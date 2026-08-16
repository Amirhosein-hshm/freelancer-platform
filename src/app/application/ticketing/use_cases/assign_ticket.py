from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import AssignTicketCommand, AssignTicketResult
from app.application.ticketing.permissions import PERMISSION_TICKET_ASSIGN
from app.domain.ticketing.entities import TicketParticipant
from app.domain.ticketing.enums import TicketParticipantRole
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


class AssignTicketUseCase(UseCase[AssignTicketCommand, AssignTicketResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AssignTicketCommand) -> AssignTicketResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_TICKET_ASSIGN)
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        now = await self._clock.now()
        async with self._uow:
            ticket.assign(request.assignee_user_id)
            if not await self._participant_repo.is_participant(ticket.id, request.assignee_user_id):
                await self._participant_repo.add(
                    TicketParticipant(
                        id=await self._id_generator.new_id(),
                        ticket_id=ticket.id,
                        user_id=request.assignee_user_id,
                        participant_role=TicketParticipantRole.ASSIGNEE,
                        joined_at=now,
                        left_at=None,
                        created_at=now,
                    )
                )
            await self._ticket_repo.update(ticket)
            await self._uow.commit()
        return AssignTicketResult(
            ticket_id=ticket.id,
            assigned_to_user_id=ticket.assigned_to_user_id or request.assignee_user_id,
        )

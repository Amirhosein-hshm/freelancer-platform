from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    ITicketCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import (
    CreateTicketOnBehalfCommand,
    CreateTicketResult,
)
from app.application.ticketing.permissions import PERMISSION_TICKET_CREATE_ON_BEHALF
from app.application.ticketing.use_cases.create_ticket import _create_ticket
from app.domain.iam.repositories import IUserRepository
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


class AdminCreateTicketOnBehalfUseCase(UseCase[CreateTicketOnBehalfCommand, CreateTicketResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        ticket_code_generator: ITicketCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._ticket_code_generator = ticket_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateTicketOnBehalfCommand) -> CreateTicketResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_TICKET_CREATE_ON_BEHALF)
        await self._user_repo.get_by_id(request.target_user_id)
        return await _create_ticket(
            requester_user_id=request.target_user_id,
            submitted_by_user_id=request.actor_id,
            related_project_id=request.related_project_id,
            related_category_id=request.related_category_id,
            subject=request.subject,
            priority=request.priority,
            ticket_repo=self._ticket_repo,
            participant_repo=self._participant_repo,
            ticket_code_generator=self._ticket_code_generator,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )

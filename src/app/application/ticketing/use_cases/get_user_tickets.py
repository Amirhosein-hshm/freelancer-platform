from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import GetUserTicketsQuery, GetUserTicketsResult
from app.application.ticketing.mapping import to_ticket_result
from app.application.ticketing.permissions import (
    PERMISSION_TICKET_READ_ANY,
    PERMISSION_TICKET_READ_OWN,
)
from app.domain.ticketing.repositories import ITicketRepository


class GetUserTicketsUseCase(UseCase[GetUserTicketsQuery, GetUserTicketsResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        ticket_repo: ITicketRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._ticket_repo = ticket_repo

    def execute(self, request: GetUserTicketsQuery) -> GetUserTicketsResult:
        authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            request.user_id,
            PERMISSION_TICKET_READ_OWN,
            PERMISSION_TICKET_READ_ANY,
        )
        tickets = self._ticket_repo.list_for_user(request.user_id)
        return GetUserTicketsResult(
            tickets=[to_ticket_result(t) for t in tickets]
        )

from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import GetUserTicketsQuery, GetUserTicketsResult
from app.application.ticketing.mapping import to_ticket_result
from app.domain.ticketing.repositories import ITicketRepository


class GetUserTicketsUseCase(UseCase[GetUserTicketsQuery, GetUserTicketsResult]):
    def __init__(self, ticket_repo: ITicketRepository) -> None:
        self._ticket_repo = ticket_repo

    def execute(self, request: GetUserTicketsQuery) -> GetUserTicketsResult:
        tickets = self._ticket_repo.list_for_user(request.user_id)
        return GetUserTicketsResult(
            tickets=[to_ticket_result(t) for t in tickets]
        )

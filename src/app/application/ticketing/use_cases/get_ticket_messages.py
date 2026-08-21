from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_party
from app.application.ticketing.dto import (
    GetTicketMessagesQuery,
    GetTicketMessagesResult,
)
from app.application.ticketing.mapping import to_message_result
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketRepository,
)


class GetTicketMessagesUseCase(UseCase[GetTicketMessagesQuery, GetTicketMessagesResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        message_repo: ITicketMessageRepository,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._message_repo = message_repo

    async def execute(self, request: GetTicketMessagesQuery) -> GetTicketMessagesResult:
        limit, offset = limit_offset(request.page, request.page_size)
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        await ensure_party(ticket, request.actor_id)
        limit, offset = limit_offset(request.page, request.page_size)
        messages = await self._message_repo.list_by_ticket(
            ticket.id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._message_repo.count_by_ticket(ticket.id)
        return GetTicketMessagesResult(
            messages=[to_message_result(m) for m in messages],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.repositories import ITicketMessageRepository
from app.infrastructure.db.models.ticketing_models import TicketMessageModel
from app.infrastructure.repositories.ticketing_mapping import to_domain_ticket_message


class SqlAlchemyTicketMessageRepository(ITicketMessageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, message: TicketMessage) -> None:
        self._session.add(
            TicketMessageModel(
                id=message.id,
                ticket_id=message.ticket_id,
                sender_user_id=message.sender_user_id,
                message_type=message.message_type.value,
                body=message.body,
                is_internal=message.is_internal,
                sent_at=message.sent_at,
                edited_at=message.edited_at,
                deleted_at=message.deleted_at,
                attachment_file_asset_ids=list(message.attachment_file_asset_ids),
                created_at=message.created_at,
            )
        )

    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]:
        result = await self._session.execute(
            select(TicketMessageModel)
            .where(TicketMessageModel.ticket_id == ticket_id)
            .order_by(TicketMessageModel.sent_at.asc())
        )
        return [to_domain_ticket_message(row) for row in result.scalars().all()]

    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[TicketMessage]:
        result = await self._session.execute(
            select(TicketMessageModel).where(TicketMessageModel.attachment_file_asset_ids.contains([file_asset_id]))
        )
        return [to_domain_ticket_message(row) for row in result.scalars().all()]

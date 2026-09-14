from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.exceptions import TicketMessageNotFoundError
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

    async def get_by_id(self, message_id: EntityId) -> TicketMessage:
        """Deliberately does NOT filter soft-deleted rows.

        Only the update/delete use cases call this; they rely on the entity guards
        (``TicketMessage.edit``/``soft_delete``) to report an already-deleted message as a
        409 conflict rather than a misleading 404. No read endpoint uses this method.
        """
        row = await self._session.get(TicketMessageModel, message_id)
        if row is None:
            raise TicketMessageNotFoundError(f"Ticket message {message_id} not found.")
        return to_domain_ticket_message(row)

    async def list_by_ticket(
        self,
        ticket_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TicketMessage]:
        stmt = (
            select(TicketMessageModel)
            .where(
                TicketMessageModel.ticket_id == ticket_id,
                TicketMessageModel.deleted_at.is_(None),
            )
            .order_by(TicketMessageModel.sent_at.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_ticket_message(row) for row in result.scalars().all()]

    async def count_by_ticket(self, ticket_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(TicketMessageModel.id)).where(
                TicketMessageModel.ticket_id == ticket_id,
                TicketMessageModel.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[TicketMessage]:
        result = await self._session.execute(
            select(TicketMessageModel).where(
                TicketMessageModel.attachment_file_asset_ids.contains([file_asset_id]),
                TicketMessageModel.deleted_at.is_(None),
            )
        )
        return [to_domain_ticket_message(row) for row in result.scalars().all()]

    async def update(self, message: TicketMessage) -> None:
        row = await self._session.get(TicketMessageModel, message.id)
        if row is None:
            raise TicketMessageNotFoundError(f"Ticket message {message.id} not found.")
        row.body = message.body
        row.edited_at = message.edited_at
        row.deleted_at = message.deleted_at

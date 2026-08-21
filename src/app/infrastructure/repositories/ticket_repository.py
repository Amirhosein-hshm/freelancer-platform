from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.exceptions import TicketNotFoundError
from app.domain.ticketing.repositories import ITicketRepository
from app.infrastructure.db.models.ticketing_models import TicketModel
from app.infrastructure.repositories.ticketing_mapping import to_domain_ticket


class SqlAlchemyTicketRepository(ITicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, ticket: Ticket) -> None:
        self._session.add(
            TicketModel(
                id=ticket.id,
                ticket_code=ticket.ticket_code,
                created_by_user_id=ticket.created_by_user_id,
                target_user_id=ticket.target_user_id,
                related_project_id=ticket.related_project_id,
                related_category_id=ticket.related_category_id,
                subject=ticket.subject,
                status=ticket.status.value,
                priority=ticket.priority.value,
                closed_by_user_id=ticket.closed_by_user_id,
                closed_at=ticket.closed_at,
                last_message_at=ticket.last_message_at,
                deleted_at=ticket.deleted_at,
                submitted_by_user_id=ticket.submitted_by_user_id,
                created_at=ticket.created_at,
            )
        )

    async def get_by_id(self, ticket_id: EntityId) -> Ticket:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id, TicketModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found.")
        return to_domain_ticket(row)

    async def get_by_code(self, ticket_code: str) -> Ticket:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.ticket_code == ticket_code, TicketModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise TicketNotFoundError(f"Ticket with code '{ticket_code}' not found.")
        return to_domain_ticket(row)

    async def list_for_user(
        self,
        user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Ticket]:
        stmt = (
            select(TicketModel)
            .where(
                TicketModel.deleted_at.is_(None),
                (TicketModel.created_by_user_id == user_id) | (TicketModel.target_user_id == user_id),
            )
            .order_by(TicketModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_ticket(row) for row in result.scalars().all()]

    async def count_for_user(self, user_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(TicketModel.id)).where(
                TicketModel.deleted_at.is_(None),
                (TicketModel.created_by_user_id == user_id) | (TicketModel.target_user_id == user_id),
            )
        )
        return int(result.scalar_one())

    async def update(self, ticket: Ticket) -> None:
        row = await self._session.get(TicketModel, ticket.id)
        if row is None:
            raise TicketNotFoundError(f"Ticket {ticket.id} not found.")
        row.ticket_code = ticket.ticket_code
        row.created_by_user_id = ticket.created_by_user_id
        row.target_user_id = ticket.target_user_id
        row.related_project_id = ticket.related_project_id
        row.related_category_id = ticket.related_category_id
        row.subject = ticket.subject
        row.status = ticket.status.value
        row.priority = ticket.priority.value
        row.closed_by_user_id = ticket.closed_by_user_id
        row.closed_at = ticket.closed_at
        row.last_message_at = ticket.last_message_at
        row.deleted_at = ticket.deleted_at
        row.submitted_by_user_id = ticket.submitted_by_user_id
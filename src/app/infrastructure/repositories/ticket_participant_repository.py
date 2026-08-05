from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketParticipant
from app.domain.ticketing.repositories import ITicketParticipantRepository
from app.infrastructure.db.models.ticketing_models import TicketParticipantModel
from app.infrastructure.repositories.ticketing_mapping import to_domain_ticket_participant


class SqlAlchemyTicketParticipantRepository(ITicketParticipantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, participant: TicketParticipant) -> None:
        self._session.add(
            TicketParticipantModel(
                id=participant.id,
                ticket_id=participant.ticket_id,
                user_id=participant.user_id,
                participant_role=participant.participant_role.value,
                joined_at=participant.joined_at,
                left_at=participant.left_at,
                created_at=participant.created_at,
            )
        )

    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketParticipant]:
        result = await self._session.execute(
            select(TicketParticipantModel)
            .where(TicketParticipantModel.ticket_id == ticket_id)
            .order_by(TicketParticipantModel.joined_at.asc())
        )
        return [to_domain_ticket_participant(row) for row in result.scalars().all()]

    async def is_participant(self, ticket_id: EntityId, user_id: EntityId) -> bool:
        result = await self._session.execute(
            select(TicketParticipantModel.id)
            .where(
                TicketParticipantModel.ticket_id == ticket_id,
                TicketParticipantModel.user_id == user_id,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

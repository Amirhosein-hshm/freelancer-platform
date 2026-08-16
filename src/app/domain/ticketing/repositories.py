from abc import ABC, abstractmethod

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket, TicketMessage, TicketParticipant


class ITicketRepository(ABC):
    @abstractmethod
    async def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    async def get_by_id(self, ticket_id: EntityId) -> Ticket:
        """Raise ``TicketNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_code(self, ticket_code: str) -> Ticket:
        """Raise ``TicketNotFoundError`` if absent."""

    @abstractmethod
    async def list_for_user(self, user_id: EntityId) -> list[Ticket]: ...

    @abstractmethod
    async def update(self, ticket: Ticket) -> None: ...


class ITicketMessageRepository(ABC):
    @abstractmethod
    async def add(self, message: TicketMessage) -> None: ...

    @abstractmethod
    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]: ...

    @abstractmethod
    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[TicketMessage]: ...


class ITicketParticipantRepository(ABC):
    @abstractmethod
    async def add(self, participant: TicketParticipant) -> None: ...

    @abstractmethod
    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketParticipant]: ...

    @abstractmethod
    async def is_participant(self, ticket_id: EntityId, user_id: EntityId) -> bool: ...

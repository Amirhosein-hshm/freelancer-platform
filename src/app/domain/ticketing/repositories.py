from abc import ABC, abstractmethod

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket, TicketMessage, TicketParticipant


class ITicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def get_by_id(self, ticket_id: EntityId) -> Ticket:
        """Raise ``TicketNotFoundError`` if absent."""

    @abstractmethod
    def get_by_code(self, ticket_code: str) -> Ticket:
        """Raise ``TicketNotFoundError`` if absent."""

    @abstractmethod
    def list_for_user(self, user_id: EntityId) -> list[Ticket]: ...

    @abstractmethod
    def update(self, ticket: Ticket) -> None: ...


class ITicketMessageRepository(ABC):
    @abstractmethod
    def add(self, message: TicketMessage) -> None: ...

    @abstractmethod
    def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]: ...


class ITicketParticipantRepository(ABC):
    @abstractmethod
    def add(self, participant: TicketParticipant) -> None: ...

    @abstractmethod
    def list_by_ticket(self, ticket_id: EntityId) -> list[TicketParticipant]: ...

    @abstractmethod
    def is_participant(self, ticket_id: EntityId, user_id: EntityId) -> bool: ...

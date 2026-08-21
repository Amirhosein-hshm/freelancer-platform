from abc import ABC, abstractmethod

from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket, TicketMessage
from app.domain.ticketing.read_models import RelatedUser


class IRelatedUsersRepository(ABC):
    """Enumerate the users an actor has an eligible ticket relationship with.

    Mirrors :class:`RelationshipEligibilityService`: users are related when they
    share a project as stakeholders (customer, assigned supervisor, selected
    freelancer) or share a category (co-supervisors, or supervisor + project
    stakeholder of an open project). Excludes the queried user and soft-deleted
    users.
    """

    @abstractmethod
    async def list_related_users(self, user_id: EntityId, limit: int, offset: int) -> list[RelatedUser]: ...

    @abstractmethod
    async def count_related_users(self, user_id: EntityId) -> int: ...


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
    async def list_for_user(
        self,
        user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Ticket]:
        """Return tickets where the user is either party (creator or target)."""

    @abstractmethod
    async def count_for_user(self, user_id: EntityId) -> int: ...

    @abstractmethod
    async def update(self, ticket: Ticket) -> None: ...


class ITicketMessageRepository(ABC):
    @abstractmethod
    async def add(self, message: TicketMessage) -> None: ...

    @abstractmethod
    async def get_by_id(self, message_id: EntityId) -> TicketMessage:
        """Raise ``TicketMessageNotFoundError`` if absent."""

    @abstractmethod
    async def list_by_ticket(
        self,
        ticket_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TicketMessage]: ...

    @abstractmethod
    async def count_by_ticket(self, ticket_id: EntityId) -> int: ...

    @abstractmethod
    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[TicketMessage]: ...

    @abstractmethod
    async def update(self, message: TicketMessage) -> None:
        """Also the persistence path for soft deletion (``TicketMessage.soft_delete``)."""

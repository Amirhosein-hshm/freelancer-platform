"""Shared service ports (hexagonal 'ports').

Every external or cross-cutting dependency is defined here as an abstract interface so
that ``infrastructure`` (Phase 2) can provide the real implementation without forcing
any change in ``domain``/``application`` (Dependency Inversion Principle).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.shared.events import DomainEvent, IEventPublisher
from app.domain.shared.types import EntityId

__all__ = [
    "AccessTokenPayload",
    "DomainEvent",
    "FileAssetMetadata",
    "IClock",
    "IEventPublisher",
    "IFileStorageService",
    "IIdGenerator",
    "INotificationService",
    "IPasswordHasher",
    "IProjectCodeGenerator",
    "IRealtimeNotifier",
    "ITicketCodeGenerator",
    "ITokenService",
    "IUnitOfWork",
]


@dataclass(frozen=True)
class AccessTokenPayload:
    user_id: EntityId
    roles: list[str]
    expires_at: datetime


@dataclass(frozen=True)
class FileAssetMetadata:
    file_asset_id: EntityId
    file_name: str
    size_bytes: int
    mime_type: str | None
    url: str | None
    uploaded_at: datetime


class IPasswordHasher(ABC):
    @abstractmethod
    async def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    async def verify(self, plain_password: str, hashed: str) -> bool: ...


class ITokenService(ABC):
    @abstractmethod
    async def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str: ...

    @abstractmethod
    async def generate_refresh_token(self) -> tuple[str, str]:
        """Return ``(raw_token, jti)``; raw is handed to the user only once."""

    @abstractmethod
    async def hash_refresh_token(self, raw_token: str) -> str: ...

    @abstractmethod
    async def decode_access_token(self, token: str) -> AccessTokenPayload:
        """Raise ``InvalidTokenError`` / ``ExpiredTokenError`` on failure."""


class IClock(ABC):
    @abstractmethod
    async def now(self) -> datetime: ...


class IIdGenerator(ABC):
    @abstractmethod
    async def new_id(self) -> EntityId: ...


class IUnitOfWork(ABC):
    """Controls transactions for use cases that change several aggregates/repositories.

    ``__aenter__``/``__aexit__`` are used via ``async with self._uow:``; on any exception
    inside the block, ``__aexit__`` must roll back. The use case itself does not need an
    explicit try/except/rollback.
    """

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class INotificationService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None: ...

    @abstractmethod
    async def send_verification_email(self, to: str, token: str) -> None: ...

    @abstractmethod
    async def send_password_reset_email(self, to: str, token: str) -> None: ...


class IRealtimeNotifier(ABC):
    """Pushes real-time notifications to a connected user (via WebSocket).

    Implemented in ``infrastructure/notifications`` (Phase 2); the implementation is the
    sole documented place allowed to import from ``presentation`` (the WebSocket
    connection manager), because connection state is inherently tied to the transport
    layer.
    """

    @abstractmethod
    async def notify_user(self, user_id: EntityId, event_type: str, payload: dict) -> None: ...


class IFileStorageService(ABC):
    @abstractmethod
    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata: ...

    @abstractmethod
    async def register_uploaded_file(
        self,
        file_name: str,
        size_bytes: int,
        mime_type: str,
        owner_user_id: EntityId,
    ) -> EntityId: ...


class IProjectCodeGenerator(ABC):
    """Generates a project business code such as ``PRJ-2026-001``.

    The real implementation (Phase 2) reads a per-year sequence from the database;
    the Phase 1 fake returns deterministic values for tests.
    """

    @abstractmethod
    async def next_code(self, year: int) -> str: ...


class ITicketCodeGenerator(ABC):
    """Generates a ticket business code such as ``TCK-2026-001``."""

    @abstractmethod
    async def next_code(self, year: int) -> str: ...
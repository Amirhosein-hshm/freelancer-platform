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
    def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    def verify(self, plain_password: str, hashed: str) -> bool: ...


class ITokenService(ABC):
    @abstractmethod
    def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str: ...

    @abstractmethod
    def generate_refresh_token(self) -> tuple[str, str]:
        """Return ``(raw_token, jti)``; raw is handed to the user only once."""

    @abstractmethod
    def hash_refresh_token(self, raw_token: str) -> str: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> AccessTokenPayload:
        """Raise ``InvalidTokenError`` / ``ExpiredTokenError`` on failure."""


class IClock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...


class IIdGenerator(ABC):
    @abstractmethod
    def new_id(self) -> EntityId: ...


class IUnitOfWork(ABC):
    """Controls transactions for use cases that change several aggregates/repositories.

    ``__enter__``/``__exit__`` are used via ``with self._uow:``; on any exception inside
    the block, ``__exit__`` must roll back. The use case itself does not need an
    explicit try/except/rollback.
    """

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


class INotificationService(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> None: ...

    @abstractmethod
    def send_verification_email(self, to: str, token: str) -> None: ...

    @abstractmethod
    def send_password_reset_email(self, to: str, token: str) -> None: ...


class IFileStorageService(ABC):
    @abstractmethod
    def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata: ...

    @abstractmethod
    def register_uploaded_file(
        self,
        file_name: str,
        size_bytes: int,
        mime_type: str,
        owner_user_id: EntityId,
    ) -> EntityId: ...


class IProjectCodeGenerator(ABC):
    """Generates a project business code such as ``PRJ-2026-001``.

    The real implementation (Phase 2) will read a per-year sequence from the database;
    the Phase 1 fake returns deterministic values for tests.
    """

    @abstractmethod
    def next_code(self, year: int) -> str: ...


class ITicketCodeGenerator(ABC):
    """Generates a ticket business code such as ``TCK-2026-001``."""

    @abstractmethod
    def next_code(self, year: int) -> str: ...

from abc import ABC, abstractmethod

from app.domain.freelancer.entities import (
    FreelancerLevelHistory,
    FreelancerProfile,
    PortfolioItem,
    Resume,
)
from app.domain.freelancer.enums import FreelancerApprovalStatus, FreelancerLevelEnum
from app.domain.shared.types import EntityId


class IFreelancerProfileRepository(ABC):
    @abstractmethod
    async def add(self, profile: FreelancerProfile) -> None: ...

    @abstractmethod
    async def get_by_id(self, profile_id: EntityId) -> FreelancerProfile:
        """Raise ``FreelancerProfileNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_user_id(self, user_id: EntityId) -> FreelancerProfile:
        """Raise ``FreelancerProfileNotFoundError`` if absent."""

    @abstractmethod
    async def update(self, profile: FreelancerProfile) -> None: ...

    @abstractmethod
    async def list_by_approval_status(
        self,
        status: FreelancerApprovalStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FreelancerProfile]: ...

    @abstractmethod
    async def count_by_approval_status(self, status: FreelancerApprovalStatus) -> int: ...

    @abstractmethod
    async def list_available_for_level(self, level: FreelancerLevelEnum) -> list[FreelancerProfile]: ...


class IFreelancerLevelHistoryRepository(ABC):
    @abstractmethod
    async def add(self, history: FreelancerLevelHistory) -> None: ...

    @abstractmethod
    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FreelancerLevelHistory]: ...

    @abstractmethod
    async def count_by_profile(self, profile_id: EntityId) -> int: ...


class IResumeRepository(ABC):
    @abstractmethod
    async def add(self, resume: Resume) -> None: ...

    @abstractmethod
    async def get_by_id(self, resume_id: EntityId) -> Resume:
        """Raise ``ResumeNotFoundError`` if absent."""

    @abstractmethod
    async def update(self, resume: Resume) -> None: ...

    @abstractmethod
    async def delete(self, resume_id: EntityId) -> None: ...

    @abstractmethod
    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Resume]: ...

    @abstractmethod
    async def count_by_profile(self, profile_id: EntityId) -> int: ...

    @abstractmethod
    async def get_current(self, profile_id: EntityId) -> Resume | None: ...

    @abstractmethod
    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> Resume | None: ...


class IPortfolioItemRepository(ABC):
    """All read methods exclude soft-deleted items (``deleted_at IS NULL``)."""

    @abstractmethod
    async def add(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    async def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        """Raise ``PortfolioItemNotFoundError`` if absent or soft-deleted."""

    @abstractmethod
    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[PortfolioItem]: ...

    @abstractmethod
    async def count_by_profile(self, profile_id: EntityId) -> int: ...

    @abstractmethod
    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> PortfolioItem | None: ...

    @abstractmethod
    async def update(self, item: PortfolioItem) -> None:
        """Also the persistence path for soft deletion (``PortfolioItem.soft_delete``)."""

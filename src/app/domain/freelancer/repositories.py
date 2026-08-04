from abc import ABC, abstractmethod

from app.domain.freelancer.entities import (
    FreelancerLevel,
    FreelancerLevelHistory,
    FreelancerProfile,
    PortfolioItem,
    Resume,
)
from app.domain.freelancer.enums import FreelancerApprovalStatus
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
    async def list_by_approval_status(self, status: FreelancerApprovalStatus) -> list[FreelancerProfile]: ...

    @abstractmethod
    async def list_available_for_level(self, level_id: EntityId) -> list[FreelancerProfile]: ...


class IFreelancerLevelRepository(ABC):
    @abstractmethod
    async def get_by_id(self, level_id: EntityId) -> FreelancerLevel:
        """Raise ``FreelancerLevelNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_key(self, level_key: str) -> FreelancerLevel:
        """Raise ``FreelancerLevelNotFoundError`` if absent."""

    @abstractmethod
    async def list_active(self) -> list[FreelancerLevel]: ...


class IFreelancerLevelHistoryRepository(ABC):
    @abstractmethod
    async def add(self, history: FreelancerLevelHistory) -> None: ...

    @abstractmethod
    async def list_by_profile(self, profile_id: EntityId) -> list[FreelancerLevelHistory]: ...


class IResumeRepository(ABC):
    @abstractmethod
    async def add(self, resume: Resume) -> None: ...

    @abstractmethod
    async def update(self, resume: Resume) -> None: ...

    @abstractmethod
    async def list_by_profile(self, profile_id: EntityId) -> list[Resume]: ...

    @abstractmethod
    async def get_current(self, profile_id: EntityId) -> Resume | None: ...


class IPortfolioItemRepository(ABC):
    @abstractmethod
    async def add(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    async def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        """Raise ``PortfolioItemNotFoundError`` if absent."""

    @abstractmethod
    async def list_by_profile(self, profile_id: EntityId) -> list[PortfolioItem]: ...

    @abstractmethod
    async def update(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    async def delete(self, item_id: EntityId) -> None: ...

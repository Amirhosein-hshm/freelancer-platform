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
    def add(self, profile: FreelancerProfile) -> None: ...

    @abstractmethod
    def get_by_id(self, profile_id: EntityId) -> FreelancerProfile:
        """Raise ``FreelancerProfileNotFoundError`` if absent."""

    @abstractmethod
    def get_by_user_id(self, user_id: EntityId) -> FreelancerProfile:
        """Raise ``FreelancerProfileNotFoundError`` if absent."""

    @abstractmethod
    def update(self, profile: FreelancerProfile) -> None: ...

    @abstractmethod
    def list_by_approval_status(self, status: FreelancerApprovalStatus) -> list[FreelancerProfile]: ...

    @abstractmethod
    def list_available_for_level(self, level_id: EntityId) -> list[FreelancerProfile]: ...


class IFreelancerLevelRepository(ABC):
    @abstractmethod
    def get_by_id(self, level_id: EntityId) -> FreelancerLevel:
        """Raise ``FreelancerLevelNotFoundError`` if absent."""

    @abstractmethod
    def get_by_key(self, level_key: str) -> FreelancerLevel:
        """Raise ``FreelancerLevelNotFoundError`` if absent."""

    @abstractmethod
    def list_active(self) -> list[FreelancerLevel]: ...


class IFreelancerLevelHistoryRepository(ABC):
    @abstractmethod
    def add(self, history: FreelancerLevelHistory) -> None: ...

    @abstractmethod
    def list_by_profile(self, profile_id: EntityId) -> list[FreelancerLevelHistory]: ...


class IResumeRepository(ABC):
    @abstractmethod
    def add(self, resume: Resume) -> None: ...

    @abstractmethod
    def update(self, resume: Resume) -> None: ...

    @abstractmethod
    def list_by_profile(self, profile_id: EntityId) -> list[Resume]: ...

    @abstractmethod
    def get_current(self, profile_id: EntityId) -> Resume | None: ...


class IPortfolioItemRepository(ABC):
    @abstractmethod
    def add(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        """Raise ``PortfolioItemNotFoundError`` if absent."""

    @abstractmethod
    def list_by_profile(self, profile_id: EntityId) -> list[PortfolioItem]: ...

    @abstractmethod
    def update(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    def delete(self, item_id: EntityId) -> None: ...

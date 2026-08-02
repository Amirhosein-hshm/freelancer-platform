from abc import ABC, abstractmethod

from app.domain.project.entities import (
    Project,
    ProjectApplication,
    ProjectDelivery,
    ProjectRevisionRequest,
    ProjectStatusHistory,
)
from app.domain.project.enums import ProjectStatus
from app.domain.project.value_objects import ProjectCode
from app.domain.shared.types import EntityId


class IProjectRepository(ABC):
    @abstractmethod
    def add(self, project: Project) -> None: ...

    @abstractmethod
    def get_by_id(self, project_id: EntityId) -> Project:
        """Raise ``ProjectNotFoundError`` if absent."""

    @abstractmethod
    def get_by_code(self, project_code: ProjectCode) -> Project:
        """Raise ``ProjectNotFoundError`` if absent."""

    @abstractmethod
    def update(self, project: Project) -> None: ...

    @abstractmethod
    def list_by_customer(
        self, customer_user_id: EntityId, status: ProjectStatus | None = None
    ) -> list[Project]: ...

    @abstractmethod
    def list_available_for_freelancer(self, level_id: EntityId) -> list[Project]: ...

    @abstractmethod
    def list_by_supervisor(self, supervisor_user_id: EntityId) -> list[Project]: ...

    @abstractmethod
    def list_by_category(self, category_id: EntityId) -> list[Project]:
        """Return the currently open (published/collecting) projects of a category."""


class IProjectApplicationRepository(ABC):
    @abstractmethod
    def add(self, application: ProjectApplication) -> None: ...

    @abstractmethod
    def get_by_id(self, application_id: EntityId) -> ProjectApplication:
        """Raise ``ApplicationNotFoundError`` if absent."""

    @abstractmethod
    def find_by_project_and_freelancer(
        self, project_id: EntityId, freelancer_profile_id: EntityId
    ) -> ProjectApplication | None: ...

    @abstractmethod
    def list_by_project(self, project_id: EntityId) -> list[ProjectApplication]: ...

    @abstractmethod
    def count_active_for_freelancer(self, freelancer_profile_id: EntityId) -> int: ...

    @abstractmethod
    def update(self, application: ProjectApplication) -> None: ...


class IProjectDeliveryRepository(ABC):
    @abstractmethod
    def add(self, delivery: ProjectDelivery) -> None: ...

    @abstractmethod
    def get_by_id(self, delivery_id: EntityId) -> ProjectDelivery:
        """Raise ``DeliveryNotFoundError`` if absent."""

    @abstractmethod
    def get_latest_for_project(self, project_id: EntityId) -> ProjectDelivery | None: ...

    @abstractmethod
    def list_by_project(self, project_id: EntityId) -> list[ProjectDelivery]: ...

    @abstractmethod
    def update(self, delivery: ProjectDelivery) -> None: ...


class IProjectRevisionRequestRepository(ABC):
    @abstractmethod
    def add(self, revision: ProjectRevisionRequest) -> None: ...

    @abstractmethod
    def list_by_project(self, project_id: EntityId) -> list[ProjectRevisionRequest]: ...

    @abstractmethod
    def count_by_project(self, project_id: EntityId) -> int: ...

    @abstractmethod
    def update(self, revision: ProjectRevisionRequest) -> None: ...


class IProjectStatusHistoryRepository(ABC):
    @abstractmethod
    def add(self, history: ProjectStatusHistory) -> None: ...

    @abstractmethod
    def list_by_project(self, project_id: EntityId) -> list[ProjectStatusHistory]: ...

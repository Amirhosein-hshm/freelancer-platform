from abc import ABC, abstractmethod

from app.domain.freelancer.enums import FreelancerLevelEnum
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
    async def add(self, project: Project) -> None: ...

    @abstractmethod
    async def get_by_id(self, project_id: EntityId) -> Project:
        """Raise ``ProjectNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_code(self, project_code: ProjectCode) -> Project:
        """Raise ``ProjectNotFoundError`` if absent."""

    @abstractmethod
    async def update(self, project: Project) -> None: ...

    @abstractmethod
    async def list_by_customer(
        self,
        customer_user_id: EntityId,
        status: ProjectStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]: ...

    @abstractmethod
    async def count_by_customer(
        self, customer_user_id: EntityId, status: ProjectStatus | None = None
    ) -> int: ...

    @abstractmethod
    async def list_available_for_freelancer(
        self,
        current_level: FreelancerLevelEnum | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        """Return open projects the freelancer may apply to.

        Hierarchical filter: a project whose ``required_level`` is set is only included
        when ``current_level`` is not None and ``current_level.rank() >= required_level.rank()``;
        projects with no ``required_level`` are always included. INVITE_ONLY excluded.
        """

    @abstractmethod
    async def count_available_for_freelancer(
        self, current_level: FreelancerLevelEnum | None
    ) -> int: ...

    @abstractmethod
    async def list_by_supervisor(
        self,
        supervisor_user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]: ...

    @abstractmethod
    async def count_by_supervisor(self, supervisor_user_id: EntityId) -> int: ...

    @abstractmethod
    async def list_by_category(
        self,
        category_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        """Return the currently open (published/collecting) projects of a category."""

    @abstractmethod
    async def count_active_by_category(self, category_id: EntityId) -> int: ...

    @abstractmethod
    async def count_open_by_category(self, category_id: EntityId) -> int: ...

    @abstractmethod
    async def count_active_by_form_template(self, form_template_id: EntityId) -> int: ...


class IProjectApplicationRepository(ABC):
    @abstractmethod
    async def add(self, application: ProjectApplication) -> None: ...

    @abstractmethod
    async def get_by_id(self, application_id: EntityId) -> ProjectApplication:
        """Raise ``ApplicationNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_project_and_freelancer(
        self, project_id: EntityId, freelancer_profile_id: EntityId
    ) -> ProjectApplication | None: ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectApplication]: ...

    @abstractmethod
    async def count_by_project(self, project_id: EntityId) -> int: ...

    @abstractmethod
    async def count_active_for_freelancer(self, freelancer_profile_id: EntityId) -> int: ...

    @abstractmethod
    async def update(self, application: ProjectApplication) -> None: ...


class IProjectDeliveryRepository(ABC):
    @abstractmethod
    async def add(self, delivery: ProjectDelivery) -> None: ...

    @abstractmethod
    async def get_by_id(self, delivery_id: EntityId) -> ProjectDelivery:
        """Raise ``DeliveryNotFoundError`` if absent."""

    @abstractmethod
    async def get_latest_for_project(self, project_id: EntityId) -> ProjectDelivery | None: ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectDelivery]: ...

    @abstractmethod
    async def count_by_project(self, project_id: EntityId) -> int: ...

    @abstractmethod
    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[ProjectDelivery]: ...

    @abstractmethod
    async def update(self, delivery: ProjectDelivery) -> None: ...


class IProjectRevisionRequestRepository(ABC):
    @abstractmethod
    async def add(self, revision: ProjectRevisionRequest) -> None: ...

    @abstractmethod
    async def get_by_id(self, revision_id: EntityId) -> ProjectRevisionRequest:
        """Raise ``RevisionRequestNotFoundError`` if absent."""

    @abstractmethod
    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectRevisionRequest]: ...

    @abstractmethod
    async def count_by_project(self, project_id: EntityId) -> int: ...

    @abstractmethod
    async def update(self, revision: ProjectRevisionRequest) -> None: ...


class IProjectStatusHistoryRepository(ABC):
    @abstractmethod
    async def add(self, history: ProjectStatusHistory) -> None: ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectStatusHistory]: ...

    @abstractmethod
    async def count_by_project(self, project_id: EntityId) -> int: ...

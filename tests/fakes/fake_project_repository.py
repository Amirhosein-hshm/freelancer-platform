from app.domain.project.entities import Project
from app.domain.project.enums import ProjectStatus
from app.domain.project.exceptions import ProjectNotFoundError
from app.domain.project.repositories import IProjectRepository
from app.domain.project.value_objects import ProjectCode
from app.domain.shared.types import EntityId

_OPEN_STATUSES = (ProjectStatus.PUBLISHED, ProjectStatus.COLLECTING_APPLICATIONS)

_TERMINAL_STATUSES = (
    ProjectStatus.COMPLETED,
    ProjectStatus.CANCELLED,
    ProjectStatus.REJECTED,
    ProjectStatus.ARCHIVED,
)


class FakeProjectRepository(IProjectRepository):
    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    async def add(self, project: Project) -> None:
        self._store[project.id] = project

    async def get_by_id(self, project_id: EntityId) -> Project:
        try:
            return self._store[project_id]
        except KeyError:
            raise ProjectNotFoundError(f"Project {project_id} not found.") from None

    async def get_by_code(self, project_code: ProjectCode) -> Project:
        for project in self._store.values():
            if project.project_code == project_code:
                return project
        raise ProjectNotFoundError(f"Project with code {project_code.value} not found.")

    async def update(self, project: Project) -> None:
        self._store[project.id] = project

    async def list_by_customer(
        self, customer_user_id: EntityId, status: ProjectStatus | None = None
    ) -> list[Project]:
        projects = [
            p
            for p in self._store.values()
            if p.customer_user_id == customer_user_id and p.deleted_at is None
        ]
        if status is not None:
            projects = [p for p in projects if p.status == status]
        return projects

    async def list_available_for_freelancer(self, level_id: EntityId) -> list[Project]:
        return [
            p
            for p in self._store.values()
            if p.status in _OPEN_STATUSES and p.deleted_at is None
        ]

    async def list_by_supervisor(self, supervisor_user_id: EntityId) -> list[Project]:
        return [
            p
            for p in self._store.values()
            if p.assigned_supervisor_user_id == supervisor_user_id and p.deleted_at is None
        ]

    async def list_by_category(self, category_id: EntityId) -> list[Project]:
        return [
            p
            for p in self._store.values()
            if p.category_id == category_id
            and p.status in _OPEN_STATUSES
            and p.deleted_at is None
        ]

    async def count_active_by_category(self, category_id: EntityId) -> int:
        return len(
            [
                p
                for p in self._store.values()
                if p.category_id == category_id
                and p.deleted_at is None
                and p.status not in _TERMINAL_STATUSES
            ]
        )

    async def count_active_by_form_template(self, form_template_id: EntityId) -> int:
        return len(
            [
                p
                for p in self._store.values()
                if p.form_template_id == form_template_id
                and p.deleted_at is None
                and p.status not in _TERMINAL_STATUSES
            ]
        )

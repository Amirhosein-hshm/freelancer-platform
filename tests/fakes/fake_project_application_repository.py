from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus
from app.domain.project.exceptions import ApplicationNotFoundError
from app.domain.project.repositories import IProjectApplicationRepository
from app.domain.shared.types import EntityId


class FakeProjectApplicationRepository(IProjectApplicationRepository):
    async def __init__(self) -> None:
        self._store: dict[str, ProjectApplication] = {}

    async def add(self, application: ProjectApplication) -> None:
        self._store[application.id] = application

    async def get_by_id(self, application_id: EntityId) -> ProjectApplication:
        try:
            return self._store[application_id]
        except KeyError:
            raise ApplicationNotFoundError(f"Application {application_id} not found.") from None

    async def find_by_project_and_freelancer(
        self, project_id: EntityId, freelancer_profile_id: EntityId
    ) -> ProjectApplication | None:
        for application in self._store.values():
            if (
                application.project_id == project_id
                and application.freelancer_profile_id == freelancer_profile_id
            ):
                return application
        return None

    async def list_by_project(self, project_id: EntityId) -> list[ProjectApplication]:
        return [a for a in self._store.values() if a.project_id == project_id]

    async def count_active_for_freelancer(self, freelancer_profile_id: EntityId) -> int:
        active = (
            ProjectApplicationStatus.APPLIED,
            ProjectApplicationStatus.SHORTLISTED,
            ProjectApplicationStatus.ACCEPTED,
        )
        return sum(
            1
            for a in self._store.values()
            if a.freelancer_profile_id == freelancer_profile_id and a.status in active
        )

    async def update(self, application: ProjectApplication) -> None:
        self._store[application.id] = application

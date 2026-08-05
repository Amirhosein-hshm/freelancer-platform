from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.repositories import IProjectRevisionRequestRepository
from app.domain.shared.types import EntityId


class FakeProjectRevisionRequestRepository(IProjectRevisionRequestRepository):
    def __init__(self) -> None:
        self._store: list[ProjectRevisionRequest] = []

    async def add(self, revision: ProjectRevisionRequest) -> None:
        self._store.append(revision)

    async def list_by_project(self, project_id: EntityId) -> list[ProjectRevisionRequest]:
        return [r for r in self._store if r.project_id == project_id]

    async def count_by_project(self, project_id: EntityId) -> int:
        return sum(1 for r in self._store if r.project_id == project_id)

    async def update(self, revision: ProjectRevisionRequest) -> None:
        for i, stored in enumerate(self._store):
            if stored.id == revision.id:
                self._store[i] = revision
                return
        self._store.append(revision)

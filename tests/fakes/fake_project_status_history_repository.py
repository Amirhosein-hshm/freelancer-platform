from app.domain.project.entities import ProjectStatusHistory
from app.domain.project.repositories import IProjectStatusHistoryRepository
from app.domain.shared.types import EntityId


class FakeProjectStatusHistoryRepository(IProjectStatusHistoryRepository):
    def __init__(self) -> None:
        self._store: list[ProjectStatusHistory] = []

    def add(self, history: ProjectStatusHistory) -> None:
        self._store.append(history)

    def list_by_project(self, project_id: EntityId) -> list[ProjectStatusHistory]:
        return [h for h in self._store if h.project_id == project_id]

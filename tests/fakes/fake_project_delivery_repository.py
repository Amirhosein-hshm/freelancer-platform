from app.domain.project.entities import ProjectDelivery
from app.domain.project.exceptions import DeliveryNotFoundError
from app.domain.project.repositories import IProjectDeliveryRepository
from app.domain.shared.types import EntityId


class FakeProjectDeliveryRepository(IProjectDeliveryRepository):
    def __init__(self) -> None:
        self._store: dict[str, ProjectDelivery] = {}

    async def add(self, delivery: ProjectDelivery) -> None:
        self._store[delivery.id] = delivery

    async def get_by_id(self, delivery_id: EntityId) -> ProjectDelivery:
        try:
            return self._store[delivery_id]
        except KeyError:
            raise DeliveryNotFoundError(f"Delivery {delivery_id} not found.") from None

    async def get_latest_for_project(self, project_id: EntityId) -> ProjectDelivery | None:
        candidates = [d for d in self._store.values() if d.project_id == project_id]
        if not candidates:
            return None
        return max(candidates, key=lambda d: d.version_no)

    async def list_by_project(self, project_id: EntityId) -> list[ProjectDelivery]:
        return sorted(
            (d for d in self._store.values() if d.project_id == project_id),
            key=lambda d: d.version_no,
        )

    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[ProjectDelivery]:
        return [d for d in self._store.values() if file_asset_id in d.file_asset_ids]

    async def update(self, delivery: ProjectDelivery) -> None:
        self._store[delivery.id] = delivery

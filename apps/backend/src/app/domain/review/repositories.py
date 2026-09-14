from abc import ABC, abstractmethod

from app.domain.review.entities import SupervisorReview
from app.domain.shared.types import EntityId


class ISupervisorReviewRepository(ABC):
    @abstractmethod
    async def add(self, review: SupervisorReview) -> None: ...

    @abstractmethod
    async def get_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview:
        """Raise ``SupervisorReviewNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview | None: ...

    @abstractmethod
    async def list_pending_for_supervisor(
        self,
        supervisor_user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SupervisorReview]: ...

    @abstractmethod
    async def count_pending_for_supervisor(self, supervisor_user_id: EntityId) -> int: ...

    @abstractmethod
    async def update(self, review: SupervisorReview) -> None: ...

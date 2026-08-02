from abc import ABC, abstractmethod

from app.domain.review.entities import SupervisorReview
from app.domain.shared.types import EntityId


class ISupervisorReviewRepository(ABC):
    @abstractmethod
    def add(self, review: SupervisorReview) -> None: ...

    @abstractmethod
    def get_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview:
        """Raise ``SupervisorReviewNotFoundError`` if absent."""

    @abstractmethod
    def find_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview | None: ...

    @abstractmethod
    def list_pending_for_supervisor(self, supervisor_user_id: EntityId) -> list[SupervisorReview]: ...

    @abstractmethod
    def update(self, review: SupervisorReview) -> None: ...

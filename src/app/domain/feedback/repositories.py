from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.shared.types import EntityId


class ICustomerReviewRepository(ABC):
    @abstractmethod
    def add(self, review: CustomerReview) -> None: ...

    @abstractmethod
    def find_by_project(self, project_id: EntityId) -> CustomerReview | None: ...


class IRatingRepository(ABC):
    @abstractmethod
    def add(self, rating: Rating) -> None: ...

    @abstractmethod
    def find_by_project(self, project_id: EntityId) -> Rating | None: ...

    @abstractmethod
    def list_by_freelancer(self, freelancer_profile_id: EntityId) -> list[Rating]: ...

    @abstractmethod
    def average_score_for_freelancer(self, freelancer_profile_id: EntityId) -> Decimal | None: ...

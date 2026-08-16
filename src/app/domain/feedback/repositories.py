from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.shared.types import EntityId


class ICustomerReviewRepository(ABC):
    @abstractmethod
    async def add(self, review: CustomerReview) -> None: ...

    @abstractmethod
    async def get_by_id(self, review_id: EntityId) -> CustomerReview:
        """Raise ``CustomerReviewNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_project(self, project_id: EntityId) -> CustomerReview | None: ...

    @abstractmethod
    async def list_by_project(self, project_id: EntityId) -> list[CustomerReview]: ...

    @abstractmethod
    async def update(self, review: CustomerReview) -> None: ...

    @abstractmethod
    async def delete(self, review_id: EntityId) -> None: ...


class IRatingRepository(ABC):
    @abstractmethod
    async def add(self, rating: Rating) -> None: ...

    @abstractmethod
    async def get_by_id(self, rating_id: EntityId) -> Rating:
        """Raise ``RatingNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_project(self, project_id: EntityId) -> Rating | None: ...

    @abstractmethod
    async def list_by_freelancer(self, freelancer_profile_id: EntityId) -> list[Rating]: ...

    @abstractmethod
    async def update(self, rating: Rating) -> None: ...

    @abstractmethod
    async def delete(self, rating_id: EntityId) -> None: ...

    @abstractmethod
    async def average_score_for_freelancer(self, freelancer_profile_id: EntityId) -> Decimal | None: ...

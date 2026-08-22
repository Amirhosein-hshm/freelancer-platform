"""Domain service for strict two-party ticket relationship eligibility."""
from app.domain.shared.types import EntityId
from app.domain.ticketing.exceptions import TicketRelationshipError
from app.domain.ticketing.repositories import IRelatedUsersRepository


class RelationshipEligibilityService:
    """Single policy entry point shared by ticket creation and recipient listing."""

    def __init__(
        self,
        related_users_repo: IRelatedUsersRepository,
    ) -> None:
        self._related_users_repo = related_users_repo

    async def ensure_related(
        self,
        *,
        user_a: EntityId,
        user_b: EntityId,
    ) -> None:
        if not await self.are_related(
            user_a=user_a,
            user_b=user_b,
        ):
            raise TicketRelationshipError(
                f"Users {user_a} and {user_b} have no eligible relationship to open a ticket."
            )

    async def are_related(
        self,
        *,
        user_a: EntityId,
        user_b: EntityId,
    ) -> bool:
        if user_a == user_b:
            return False
        return await self._related_users_repo.are_related(user_a, user_b)

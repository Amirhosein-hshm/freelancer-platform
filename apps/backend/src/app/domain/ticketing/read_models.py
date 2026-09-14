from dataclasses import dataclass

from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class RelatedUser:
    """A user the actor has an eligible ticket relationship with.

    Populated by :class:`IRelatedUsersRepository` following the same project- and
    category-anchor rules as :class:`RelationshipEligibilityService`.
    """

    user_id: EntityId
    email: str
    first_name: str
    last_name: str
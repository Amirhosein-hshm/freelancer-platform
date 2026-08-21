from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import (
    ListRelatedUsersQuery,
    ListRelatedUsersResult,
    RelatedUserResult,
)
from app.application.ticketing.permissions import (
    PERMISSION_TICKET_READ_ANY,
    PERMISSION_TICKET_READ_OWN,
)
from app.domain.ticketing.repositories import IRelatedUsersRepository


class ListRelatedUsersUseCase(UseCase[ListRelatedUsersQuery, ListRelatedUsersResult]):
    """Return the users the actor may open a two-party ticket with.

    ``user_id`` is the subject whose relationships are enumerated. Self-service
    queries (``user_id == actor_id``) need ``ticket.read_own``; on-behalf queries
    need ``ticket.read_any``.
    """

    def __init__(
        self,
        authorization_service: IAuthorizationService,
        related_users_repo: IRelatedUsersRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._related_users_repo = related_users_repo

    async def execute(self, request: ListRelatedUsersQuery) -> ListRelatedUsersResult:
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            request.user_id,
            PERMISSION_TICKET_READ_OWN,
            PERMISSION_TICKET_READ_ANY,
        )
        limit, offset = limit_offset(request.page, request.page_size)
        users = await self._related_users_repo.list_related_users(request.user_id, limit, offset)
        total_items = await self._related_users_repo.count_related_users(request.user_id)
        return ListRelatedUsersResult(
            users=[
                RelatedUserResult(
                    user_id=u.user_id,
                    email=u.email,
                    first_name=u.first_name,
                    last_name=u.last_name,
                )
                for u in users
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
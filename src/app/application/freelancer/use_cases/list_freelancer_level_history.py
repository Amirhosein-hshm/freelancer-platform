from app.application.freelancer.dto import (
    FreelancerLevelHistoryResult,
    ListFreelancerLevelHistoryQuery,
)
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerLevelHistoryRepository,
    IFreelancerProfileRepository,
)


class ListFreelancerLevelHistoryUseCase(UseCase[ListFreelancerLevelHistoryQuery, list[FreelancerLevelHistoryResult]]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        level_history_repo: IFreelancerLevelHistoryRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._level_history_repo = level_history_repo

    async def execute(self, request: ListFreelancerLevelHistoryQuery) -> list[FreelancerLevelHistoryResult]:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        history = await self._level_history_repo.list_by_profile(request.profile_id)
        return [
            FreelancerLevelHistoryResult(
                history_id=h.id,
                freelancer_profile_id=h.freelancer_profile_id,
                old_level_id=h.old_level_id,
                new_level_id=h.new_level_id,
                assigned_by_user_id=h.assigned_by_user_id,
                reason=h.reason,
                assigned_at=h.assigned_at,
            )
            for h in history
        ]

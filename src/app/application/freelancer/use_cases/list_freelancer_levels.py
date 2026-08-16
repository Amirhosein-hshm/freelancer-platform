from app.application.freelancer.dto import (
    FreelancerLevelResult,
    ListFreelancerLevelsQuery,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class ListFreelancerLevelsUseCase(UseCase[ListFreelancerLevelsQuery, list[FreelancerLevelResult]]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo

    async def execute(self, request: ListFreelancerLevelsQuery) -> list[FreelancerLevelResult]:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        levels = await self._level_repo.list_all()
        return [
            FreelancerLevelResult(
                level_id=level.id,
                level_key=level.level_key,
                name=level.name,
                rank_order=level.rank_order,
                access_type=level.access_type.value,
                min_completed_projects=level.min_completed_projects,
                min_rating=level.min_rating,
                max_active_applications=level.max_active_applications,
                can_apply_public_projects=level.can_apply_public_projects,
                can_apply_private_projects=level.can_apply_private_projects,
                is_active=level.is_active,
            )
            for level in levels
        ]

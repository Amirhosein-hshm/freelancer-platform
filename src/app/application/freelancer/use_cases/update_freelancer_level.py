from app.application.freelancer.dto import (
    UpdateFreelancerLevelCommand,
    UpdateFreelancerLevelResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.enums import FreelancerLevelAccessType
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class UpdateFreelancerLevelUseCase(UseCase[UpdateFreelancerLevelCommand, UpdateFreelancerLevelResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo

    async def execute(self, request: UpdateFreelancerLevelCommand) -> UpdateFreelancerLevelResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        level = await self._level_repo.get_by_id(request.level_id)
        if request.name is not None:
            level.name = request.name
        if request.rank_order is not None:
            level.rank_order = request.rank_order
        if request.access_type is not None:
            level.access_type = FreelancerLevelAccessType(request.access_type)
        if request.min_completed_projects is not None:
            level.min_completed_projects = request.min_completed_projects
        if request.min_rating is not None:
            level.min_rating = request.min_rating
        if request.max_active_applications is not None:
            level.max_active_applications = request.max_active_applications
        if request.can_apply_public_projects is not None:
            level.can_apply_public_projects = request.can_apply_public_projects
        if request.can_apply_private_projects is not None:
            level.can_apply_private_projects = request.can_apply_private_projects
        await self._level_repo.update(level)
        return UpdateFreelancerLevelResult(level_id=level.id)

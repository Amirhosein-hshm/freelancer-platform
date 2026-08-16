from app.application.freelancer.dto import (
    DeactivateFreelancerLevelCommand,
    DeactivateFreelancerLevelResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class DeactivateFreelancerLevelUseCase(UseCase[DeactivateFreelancerLevelCommand, DeactivateFreelancerLevelResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo

    async def execute(self, request: DeactivateFreelancerLevelCommand) -> DeactivateFreelancerLevelResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        level = await self._level_repo.get_by_id(request.level_id)
        level.deactivate()
        await self._level_repo.update(level)
        return DeactivateFreelancerLevelResult(level_id=level.id, is_active=level.is_active)

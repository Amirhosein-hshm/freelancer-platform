from app.application.freelancer.dto import (
    ActivateFreelancerLevelCommand,
    ActivateFreelancerLevelResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class ActivateFreelancerLevelUseCase(UseCase[ActivateFreelancerLevelCommand, ActivateFreelancerLevelResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo

    async def execute(self, request: ActivateFreelancerLevelCommand) -> ActivateFreelancerLevelResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        level = await self._level_repo.get_by_id(request.level_id)
        level.activate()
        await self._level_repo.update(level)
        return ActivateFreelancerLevelResult(level_id=level.id, is_active=level.is_active)

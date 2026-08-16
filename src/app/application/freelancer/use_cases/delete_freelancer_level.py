from app.application.freelancer.dto import (
    DeleteFreelancerLevelCommand,
    DeleteFreelancerLevelResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class DeleteFreelancerLevelUseCase(UseCase[DeleteFreelancerLevelCommand, DeleteFreelancerLevelResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo

    async def execute(self, request: DeleteFreelancerLevelCommand) -> DeleteFreelancerLevelResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        await self._level_repo.get_by_id(request.level_id)
        await self._level_repo.delete(request.level_id)
        return DeleteFreelancerLevelResult(level_id=request.level_id)

from app.application.freelancer.dto import (
    CreateFreelancerLevelCommand,
    CreateFreelancerLevelResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_MANAGE_LEVELS
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerLevel
from app.domain.freelancer.enums import FreelancerLevelAccessType
from app.domain.freelancer.repositories import IFreelancerLevelRepository


class CreateFreelancerLevelUseCase(UseCase[CreateFreelancerLevelCommand, CreateFreelancerLevelResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        level_repo: IFreelancerLevelRepository,
        id_generator: IIdGenerator,
        clock: IClock,
    ) -> None:
        self._authorization_service = authorization_service
        self._level_repo = level_repo
        self._id_generator = id_generator
        self._clock = clock

    async def execute(self, request: CreateFreelancerLevelCommand) -> CreateFreelancerLevelResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_MANAGE_LEVELS)
        request.validate()
        level = FreelancerLevel(
            id=await self._id_generator.new_id(),
            level_key=request.level_key,
            name=request.name,
            rank_order=request.rank_order,
            access_type=FreelancerLevelAccessType(request.access_type),
            min_completed_projects=request.min_completed_projects,
            min_rating=request.min_rating,
            max_active_applications=request.max_active_applications,
            can_apply_public_projects=request.can_apply_public_projects,
            can_apply_private_projects=request.can_apply_private_projects,
            is_active=True,
            created_at=await self._clock.now(),
        )
        await self._level_repo.add(level)
        return CreateFreelancerLevelResult(level_id=level.id)

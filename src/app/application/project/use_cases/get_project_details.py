from app.application.project.dto import (
    GetProjectDetailsQuery,
    GetProjectDetailsResult,
)
from app.application.project.mapping import (
    to_application_result,
    to_delivery_result,
    to_project_result,
)
from app.application.project.permissions import PERMISSION_PROJECT_MANAGE_ANY, PERMISSION_PROJECT_MANAGE_OWN
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
)


class GetProjectDetailsUseCase(UseCase[GetProjectDetailsQuery, GetProjectDetailsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        delivery_repo: IProjectDeliveryRepository,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._delivery_repo = delivery_repo
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo

    async def execute(self, request: GetProjectDetailsQuery) -> GetProjectDetailsResult:
        project = await self._project_repo.get_by_id(request.project_id)
        if await self._authorization_service.has_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY):
            allowed = True
        elif request.actor_id == project.customer_user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_OWN)
            allowed = True
        else:
            allowed = False
            if project.selected_application_id is not None:
                application = await self._application_repo.get_by_id(project.selected_application_id)
                profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
                allowed = profile.user_id == request.actor_id
            if not allowed and project.assigned_supervisor_user_id == request.actor_id:
                allowed = True
        if not allowed:
            raise PermissionDeniedError(f"User {request.actor_id} cannot access project {project.id}.")
        applications = await self._application_repo.list_by_project(project.id)
        deliveries = await self._delivery_repo.list_by_project(project.id)
        return GetProjectDetailsResult(
            project=to_project_result(project),
            applications=[to_application_result(a) for a in applications],
            deliveries=[to_delivery_result(d) for d in deliveries],
        )

from app.application.project.dto import (
    DeliveryResult,
    ListProjectDeliveriesQuery,
    ListProjectDeliveriesResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
)


class ListProjectDeliveriesUseCase(UseCase[ListProjectDeliveriesQuery, ListProjectDeliveriesResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        delivery_repo: IProjectDeliveryRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._delivery_repo = delivery_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo

    async def execute(self, request: ListProjectDeliveriesQuery) -> ListProjectDeliveriesResult:
        project = await self._project_repo.get_by_id(request.project_id)
        if await self._authorization_service.has_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY):
            pass
        elif request.actor_id == project.customer_user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_OWN)
        elif project.selected_application_id is not None:
            application = await self._application_repo.get_by_id(project.selected_application_id)
            profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
            if profile.user_id != request.actor_id:
                raise PermissionDeniedError("User cannot access project deliveries.")
        else:
            raise PermissionDeniedError("User cannot access project deliveries.")
        limit, offset = limit_offset(request.page, request.page_size)
        deliveries = await self._delivery_repo.list_by_project(
            request.project_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._delivery_repo.count_by_project(request.project_id)
        return ListProjectDeliveriesResult(
            deliveries=[
                DeliveryResult(
                    delivery_id=d.id,
                    project_id=d.project_id,
                    version_no=d.version_no,
                    status=d.status,
                    delivery_note=d.delivery_note,
                    submitted_at=d.submitted_at,
                    reviewed_at=d.reviewed_at,
                    reviewer_user_id=d.reviewer_user_id,
                    file_asset_ids=list(d.file_asset_ids),
                )
                for d in deliveries
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )

from app.application.project.dto import (
    DeliveryResult,
    ListProjectDeliveriesQuery,
    ListProjectDeliveriesResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectDeliveryRepository,
    IProjectRepository,
)


class ListProjectDeliveriesUseCase(UseCase[ListProjectDeliveriesQuery, ListProjectDeliveriesResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        delivery_repo: IProjectDeliveryRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._delivery_repo = delivery_repo

    async def execute(self, request: ListProjectDeliveriesQuery) -> ListProjectDeliveriesResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        deliveries = await self._delivery_repo.list_by_project(request.project_id)
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
            ]
        )

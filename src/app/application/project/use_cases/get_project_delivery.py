from app.application.project.dto import DeliveryResult, GetProjectDeliveryQuery
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


class GetProjectDeliveryUseCase(UseCase[GetProjectDeliveryQuery, DeliveryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        delivery_repo: IProjectDeliveryRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._delivery_repo = delivery_repo

    async def execute(self, request: GetProjectDeliveryQuery) -> DeliveryResult:
        delivery = await self._delivery_repo.get_by_id(request.delivery_id)
        project = await self._project_repo.get_by_id(delivery.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        return DeliveryResult(
            delivery_id=delivery.id,
            project_id=delivery.project_id,
            version_no=delivery.version_no,
            status=delivery.status,
            delivery_note=delivery.delivery_note,
            submitted_at=delivery.submitted_at,
            reviewed_at=delivery.reviewed_at,
            reviewer_user_id=delivery.reviewer_user_id,
            file_asset_ids=list(delivery.file_asset_ids),
        )

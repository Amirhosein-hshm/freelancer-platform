from fastapi import APIRouter, Depends

from app.application.project.dto import (
    CloseProjectRevisionRequestCommand,
    GetProjectRevisionRequestQuery,
    ProjectRevisionRequestResult,
)
from app.application.project.use_cases.close_project_revision_request import (
    CloseProjectRevisionRequestUseCase,
)
from app.application.project.use_cases.get_project_revision_request import (
    GetProjectRevisionRequestUseCase,
)
from app.presentation.api.v1.project.schemas import ProjectRevisionRequestResponse
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_close_project_revision_request_use_case,
    get_get_project_revision_request_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/revisions", tags=["Project"])


def _to_revision_response(
    revision: ProjectRevisionRequestResult,
) -> ProjectRevisionRequestResponse:
    return ProjectRevisionRequestResponse(
        revision_id=revision.revision_id,
        project_id=revision.project_id,
        project_delivery_id=revision.project_delivery_id,
        requested_by_user_id=revision.requested_by_user_id,
        requested_to_user_id=revision.requested_to_user_id,
        round_no=revision.round_no,
        status=revision.status,
        reason=revision.reason,
        resolved_by_user_id=revision.resolved_by_user_id,
        requested_at=revision.requested_at,
        resolved_at=revision.resolved_at,
    )


@router.get(
    "/{revision_id}",
    response_model=SuccessEnvelope[ProjectRevisionRequestResponse],
    operation_id="get_project_revision_request",
)
async def get_project_revision_request(
    revision_id: str,
    current_user=Depends(get_current_user),
    use_case: GetProjectRevisionRequestUseCase = Depends(get_get_project_revision_request_use_case),
) -> SuccessEnvelope[ProjectRevisionRequestResponse]:
    result = await use_case.execute(
        GetProjectRevisionRequestQuery(actor_id=current_user.user_id, revision_id=revision_id)
    )
    return SuccessEnvelope(
        message="Revision request details.",
        data=_to_revision_response(result),
    )


@router.post(
    "/{revision_id}/close",
    response_model=SuccessEnvelope[ProjectRevisionRequestResponse],
    operation_id="close_project_revision_request",
)
async def close_project_revision_request(
    revision_id: str,
    current_user=Depends(get_current_user),
    use_case: CloseProjectRevisionRequestUseCase = Depends(get_close_project_revision_request_use_case),
) -> SuccessEnvelope[ProjectRevisionRequestResponse]:
    result = await use_case.execute(
        CloseProjectRevisionRequestCommand(actor_id=current_user.user_id, revision_id=revision_id)
    )
    return SuccessEnvelope(
        message="Revision request closed.",
        data=ProjectRevisionRequestResponse(
            revision_id=result.revision_id,
            project_id="",
            project_delivery_id=None,
            requested_by_user_id="",
            requested_to_user_id=None,
            round_no=0,
            status=result.status,
            reason="",
            resolved_by_user_id=None,
            requested_at=None,  # type: ignore[arg-type]
            resolved_at=None,
        ),
    )

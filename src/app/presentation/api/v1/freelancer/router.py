from fastapi import APIRouter, Depends

from app.application.freelancer.dto import (
    AddPortfolioItemCommand,
    ApproveFreelancerCommand,
    AssignFreelancerLevelCommand,
    CreateFreelancerProfileCommand,
    DeletePortfolioItemCommand,
    DeleteResumeCommand,
    GetCurrentResumeQuery,
    GetFreelancerProfileQuery,
    GetPortfolioItemQuery,
    GetResumeQuery,
    ListFreelancerLevelHistoryQuery,
    ListPortfolioItemsQuery,
    ListResumeVersionsQuery,
    RejectFreelancerCommand,
    SetCurrentResumeCommand,
    SubmitFreelancerApprovalCommand,
    UpdateFreelancerProfileCommand,
    UpdatePortfolioItemCommand,
    UpdateResumeCommand,
    UploadResumeCommand,
)
from app.application.freelancer.use_cases.add_portfolio_item import AddPortfolioItemUseCase
from app.application.freelancer.use_cases.approve_freelancer import ApproveFreelancerUseCase
from app.application.freelancer.use_cases.assign_freelancer_level import (
    AssignFreelancerLevelUseCase,
)
from app.application.freelancer.use_cases.create_freelancer_profile import (
    CreateFreelancerProfileUseCase,
)
from app.application.freelancer.use_cases.delete_portfolio_item import (
    DeletePortfolioItemUseCase,
)
from app.application.freelancer.use_cases.delete_resume import DeleteResumeUseCase
from app.application.freelancer.use_cases.get_current_resume import GetCurrentResumeUseCase
from app.application.freelancer.use_cases.get_freelancer_profile import (
    GetFreelancerProfileUseCase,
)
from app.application.freelancer.use_cases.get_portfolio_item import GetPortfolioItemUseCase
from app.application.freelancer.use_cases.get_resume import GetResumeUseCase
from app.application.freelancer.use_cases.list_freelancer_level_history import (
    ListFreelancerLevelHistoryUseCase,
)
from app.application.freelancer.use_cases.list_portfolio_items import (
    ListPortfolioItemsUseCase,
)
from app.application.freelancer.use_cases.list_resume_versions import (
    ListResumeVersionsUseCase,
)
from app.application.freelancer.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.freelancer.use_cases.set_current_resume import SetCurrentResumeUseCase
from app.application.freelancer.use_cases.submit_freelancer_approval import (
    SubmitFreelancerApprovalUseCase,
)
from app.application.freelancer.use_cases.update_freelancer_profile import (
    UpdateFreelancerProfileUseCase,
)
from app.application.freelancer.use_cases.update_portfolio_item import (
    UpdatePortfolioItemUseCase,
)
from app.application.freelancer.use_cases.update_resume import UpdateResumeUseCase
from app.application.freelancer.use_cases.upload_resume import UploadResumeUseCase
from app.application.shared.pagination import total_pages
from app.presentation.api.v1.freelancer.mappers import to_profile_response
from app.presentation.api.v1.freelancer.schemas import (
    AddPortfolioItemRequest,
    AddPortfolioItemResponse,
    ApproveFreelancerRequest,
    ApproveFreelancerResponse,
    AssignFreelancerLevelRequest,
    AssignFreelancerLevelResponse,
    CreateFreelancerProfileRequest,
    CreateFreelancerProfileResponse,
    DeletePortfolioItemResponse,
    FreelancerLevelHistoryResponse,
    FreelancerProfileResponse,
    PortfolioItemResponse,
    RejectFreelancerRequest,
    RejectFreelancerResponse,
    ResumeChangeResponse,
    ResumeResponse,
    SubmitFreelancerApprovalResponse,
    UpdateFreelancerProfileRequest,
    UpdatePortfolioItemRequest,
    UpdatePortfolioItemResponse,
    UpdateResumeRequest,
    UpdateResumeResponse,
    UploadResumeRequest,
    UploadResumeResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_add_portfolio_item_use_case,
    get_approve_freelancer_use_case,
    get_assign_freelancer_level_use_case,
    get_create_freelancer_profile_use_case,
    get_delete_portfolio_item_use_case,
    get_delete_resume_use_case,
    get_get_current_resume_use_case,
    get_get_freelancer_profile_use_case,
    get_get_portfolio_item_use_case,
    get_get_resume_use_case,
    get_list_freelancer_level_history_use_case,
    get_list_portfolio_items_use_case,
    get_list_resume_versions_use_case,
    get_reject_freelancer_use_case,
    get_set_current_resume_use_case,
    get_submit_freelancer_approval_use_case,
    get_update_freelancer_profile_use_case,
    get_update_portfolio_item_use_case,
    get_update_resume_use_case,
    get_upload_resume_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/freelancers", tags=["Freelancer"], route_class=DocumentedAPIRoute)


@router.get(
    "/{profile_id}",
    response_model=SuccessEnvelope[FreelancerProfileResponse],
    operation_id="get_freelancer_profile",
)
async def get_freelancer_profile(
    profile_id: str,
    current_user=Depends(get_current_user),
    use_case: GetFreelancerProfileUseCase = Depends(get_get_freelancer_profile_use_case),
) -> SuccessEnvelope[FreelancerProfileResponse]:
    result = await use_case.execute(GetFreelancerProfileQuery(profile_id=profile_id))
    return SuccessEnvelope(message="Freelancer profile.", data=to_profile_response(result))


@router.post(
    "",
    response_model=SuccessEnvelope[CreateFreelancerProfileResponse],
    status_code=201,
    operation_id="create_freelancer_profile",
)
async def create_freelancer_profile(
    payload: CreateFreelancerProfileRequest,
    current_user=Depends(get_current_user),
    use_case: CreateFreelancerProfileUseCase = Depends(get_create_freelancer_profile_use_case),
) -> SuccessEnvelope[CreateFreelancerProfileResponse]:
    result = await use_case.execute(
        CreateFreelancerProfileCommand(
            user_id=current_user.user_id,
            display_name=payload.display_name,
            headline=payload.headline,
            bio=payload.bio,
            country_code=payload.country_code,
            city=payload.city,
            timezone=payload.timezone,
        )
    )
    return SuccessEnvelope(
        message="Freelancer profile created.",
        data=CreateFreelancerProfileResponse(profile_id=result.profile_id),
    )


@router.patch(
    "/{profile_id}",
    response_model=SuccessEnvelope[FreelancerProfileResponse],
    operation_id="update_freelancer_profile",
)
async def update_freelancer_profile(
    profile_id: str,
    payload: UpdateFreelancerProfileRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateFreelancerProfileUseCase = Depends(get_update_freelancer_profile_use_case),
) -> SuccessEnvelope[FreelancerProfileResponse]:
    result = await use_case.execute(
        UpdateFreelancerProfileCommand(
            user_id=current_user.user_id,
            display_name=payload.display_name,
            headline=payload.headline,
            bio=payload.bio,
            country_code=payload.country_code,
            city=payload.city,
            timezone=payload.timezone,
            hourly_rate_min=payload.hourly_rate_min,
            hourly_rate_max=payload.hourly_rate_max,
        )
    )
    return SuccessEnvelope(message="Freelancer profile updated.", data=to_profile_response(result))


@router.post(
    "/{profile_id}/submit-approval",
    response_model=SuccessEnvelope[SubmitFreelancerApprovalResponse],
    operation_id="submit_freelancer_approval",
)
async def submit_freelancer_approval(
    profile_id: str,
    current_user=Depends(get_current_user),
    use_case: SubmitFreelancerApprovalUseCase = Depends(get_submit_freelancer_approval_use_case),
) -> SuccessEnvelope[SubmitFreelancerApprovalResponse]:
    result = await use_case.execute(SubmitFreelancerApprovalCommand(user_id=current_user.user_id))
    return SuccessEnvelope(
        message="Approval submitted.",
        data=SubmitFreelancerApprovalResponse(
            profile_id=result.profile_id,
            approval_status=result.approval_status.value,
        ),
    )


@router.post(
    "/{profile_id}/approve",
    response_model=SuccessEnvelope[ApproveFreelancerResponse],
    operation_id="approve_freelancer",
)
async def approve_freelancer(
    profile_id: str,
    payload: ApproveFreelancerRequest,
    current_user=Depends(get_current_user),
    use_case: ApproveFreelancerUseCase = Depends(get_approve_freelancer_use_case),
) -> SuccessEnvelope[ApproveFreelancerResponse]:
    result = await use_case.execute(
        ApproveFreelancerCommand(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            note=payload.note,
        )
    )
    return SuccessEnvelope(
        message="Freelancer approved.",
        data=ApproveFreelancerResponse(
            profile_id=result.profile_id,
            approval_status=result.approval_status.value,
            current_level=result.current_level,
        ),
    )


@router.post(
    "/{profile_id}/reject",
    response_model=SuccessEnvelope[RejectFreelancerResponse],
    operation_id="reject_freelancer",
)
async def reject_freelancer(
    profile_id: str,
    payload: RejectFreelancerRequest,
    current_user=Depends(get_current_user),
    use_case: RejectFreelancerUseCase = Depends(get_reject_freelancer_use_case),
) -> SuccessEnvelope[RejectFreelancerResponse]:
    result = await use_case.execute(
        RejectFreelancerCommand(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            note=payload.note,
        )
    )
    return SuccessEnvelope(
        message="Freelancer rejected.",
        data=RejectFreelancerResponse(
            profile_id=result.profile_id,
            approval_status=result.approval_status.value,
        ),
    )


@router.post(
    "/{profile_id}/level",
    response_model=SuccessEnvelope[AssignFreelancerLevelResponse],
    operation_id="assign_freelancer_level",
)
async def assign_freelancer_level(
    profile_id: str,
    payload: AssignFreelancerLevelRequest,
    current_user=Depends(get_current_user),
    use_case: AssignFreelancerLevelUseCase = Depends(get_assign_freelancer_level_use_case),
) -> SuccessEnvelope[AssignFreelancerLevelResponse]:
    result = await use_case.execute(
        AssignFreelancerLevelCommand(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            new_level=payload.new_level,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="Level assigned.",
        data=AssignFreelancerLevelResponse(
            profile_id=result.profile_id,
            old_level=result.old_level,
            new_level=result.new_level,
        ),
    )


@router.post(
    "/{profile_id}/resume",
    response_model=SuccessEnvelope[UploadResumeResponse],
    status_code=201,
    operation_id="upload_resume",
)
async def upload_resume(
    profile_id: str,
    payload: UploadResumeRequest,
    current_user=Depends(get_current_user),
    use_case: UploadResumeUseCase = Depends(get_upload_resume_use_case),
) -> SuccessEnvelope[UploadResumeResponse]:
    result = await use_case.execute(
        UploadResumeCommand(
            user_id=current_user.user_id,
            file_asset_id=payload.file_asset_id,
            summary=payload.summary,
        )
    )
    return SuccessEnvelope(
        message="Resume uploaded.",
        data=UploadResumeResponse(
            resume_id=result.resume_id,
            version_no=result.version_no,
        ),
    )


@router.patch(
    "/{profile_id}/resume",
    response_model=SuccessEnvelope[UpdateResumeResponse],
    operation_id="update_resume",
)
async def update_resume(
    profile_id: str,
    payload: UpdateResumeRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateResumeUseCase = Depends(get_update_resume_use_case),
) -> SuccessEnvelope[UpdateResumeResponse]:
    result = await use_case.execute(UpdateResumeCommand(user_id=current_user.user_id, summary=payload.summary))
    return SuccessEnvelope(
        message="Resume updated.",
        data=UpdateResumeResponse(
            resume_id=result.resume_id,
            summary=result.summary,
        ),
    )


@router.post(
    "/{profile_id}/portfolio",
    response_model=SuccessEnvelope[AddPortfolioItemResponse],
    status_code=201,
    operation_id="add_portfolio_item",
)
async def add_portfolio_item(
    profile_id: str,
    payload: AddPortfolioItemRequest,
    current_user=Depends(get_current_user),
    use_case: AddPortfolioItemUseCase = Depends(get_add_portfolio_item_use_case),
) -> SuccessEnvelope[AddPortfolioItemResponse]:
    result = await use_case.execute(
        AddPortfolioItemCommand(
            user_id=current_user.user_id,
            title=payload.title,
            description=payload.description,
            external_url=payload.external_url,
            file_asset_id=payload.file_asset_id,
            display_order=payload.display_order,
            is_featured=payload.is_featured,
        )
    )
    return SuccessEnvelope(
        message="Portfolio item added.",
        data=AddPortfolioItemResponse(item_id=result.item_id),
    )


@router.patch(
    "/{profile_id}/portfolio/{item_id}",
    response_model=SuccessEnvelope[UpdatePortfolioItemResponse],
    operation_id="update_portfolio_item",
)
async def update_portfolio_item(
    profile_id: str,
    item_id: str,
    payload: UpdatePortfolioItemRequest,
    current_user=Depends(get_current_user),
    use_case: UpdatePortfolioItemUseCase = Depends(get_update_portfolio_item_use_case),
) -> SuccessEnvelope[UpdatePortfolioItemResponse]:
    result = await use_case.execute(
        UpdatePortfolioItemCommand(
            user_id=current_user.user_id,
            item_id=item_id,
            title=payload.title,
            description=payload.description,
            external_url=payload.external_url,
            file_asset_id=payload.file_asset_id,
            display_order=payload.display_order,
            is_featured=payload.is_featured,
        )
    )
    return SuccessEnvelope(
        message="Portfolio item updated.",
        data=UpdatePortfolioItemResponse(item_id=result.item_id),
    )


@router.delete(
    "/{profile_id}/portfolio/{item_id}",
    response_model=SuccessEnvelope[DeletePortfolioItemResponse],
    operation_id="delete_portfolio_item",
)
async def delete_portfolio_item(
    profile_id: str,
    item_id: str,
    current_user=Depends(get_current_user),
    use_case: DeletePortfolioItemUseCase = Depends(get_delete_portfolio_item_use_case),
) -> SuccessEnvelope[DeletePortfolioItemResponse]:
    result = await use_case.execute(DeletePortfolioItemCommand(user_id=current_user.user_id, item_id=item_id))
    return SuccessEnvelope(
        message="Portfolio item deleted.",
        data=DeletePortfolioItemResponse(item_id=result.item_id),
    )


def _to_resume_response(result: ResumeResponse) -> ResumeResponse:
    return ResumeResponse(
        resume_id=result.resume_id,
        freelancer_profile_id=result.freelancer_profile_id,
        file_asset_id=result.file_asset_id,
        version_no=result.version_no,
        summary=result.summary,
        is_current=result.is_current,
    )


def _to_portfolio_item_response(result: PortfolioItemResponse) -> PortfolioItemResponse:
    return PortfolioItemResponse(
        item_id=result.item_id,
        freelancer_profile_id=result.freelancer_profile_id,
        title=result.title,
        description=result.description,
        external_url=result.external_url,
        file_asset_id=result.file_asset_id,
        display_order=result.display_order,
        is_featured=result.is_featured,
    )


def _to_history_response(result: FreelancerLevelHistoryResponse) -> FreelancerLevelHistoryResponse:
    return FreelancerLevelHistoryResponse(
        history_id=result.history_id,
        freelancer_profile_id=result.freelancer_profile_id,
        old_level=result.old_level,
        new_level=result.new_level,
        assigned_by_user_id=result.assigned_by_user_id,
        reason=result.reason,
        assigned_at=result.assigned_at,
    )


@router.get(
    "/{profile_id}/resume",
    response_model=SuccessEnvelope[ResumeResponse],
    operation_id="get_current_resume",
)
async def get_current_resume(
    profile_id: str,
    current_user=Depends(get_current_user),
    use_case: GetCurrentResumeUseCase = Depends(get_get_current_resume_use_case),
) -> SuccessEnvelope[ResumeResponse]:
    result = await use_case.execute(GetCurrentResumeQuery(actor_id=current_user.user_id, profile_id=profile_id))
    return SuccessEnvelope(message="Current resume.", data=_to_resume_response(result))


@router.get(
    "/{profile_id}/resume/versions",
    response_model=SuccessEnvelope[list[ResumeResponse]],
    operation_id="list_resume_versions",
)
async def list_resume_versions(
    profile_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListResumeVersionsUseCase = Depends(get_list_resume_versions_use_case),
) -> SuccessEnvelope[list[ResumeResponse]]:
    result = await use_case.execute(
        ListResumeVersionsQuery(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    resumes = [_to_resume_response(r) for r in result.resumes]
    return SuccessEnvelope(
        message="Resume versions.",
        data=resumes,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )


@router.get(
    "/{profile_id}/resume/versions/{resume_id}",
    response_model=SuccessEnvelope[ResumeResponse],
    operation_id="get_resume",
)
async def get_resume(
    profile_id: str,
    resume_id: str,
    current_user=Depends(get_current_user),
    use_case: GetResumeUseCase = Depends(get_get_resume_use_case),
) -> SuccessEnvelope[ResumeResponse]:
    result = await use_case.execute(GetResumeQuery(actor_id=current_user.user_id, resume_id=resume_id))
    return SuccessEnvelope(message="Resume.", data=_to_resume_response(result))


@router.post(
    "/{profile_id}/resume/versions/{resume_id}/set-current",
    response_model=SuccessEnvelope[ResumeChangeResponse],
    operation_id="set_current_resume",
)
async def set_current_resume(
    profile_id: str,
    resume_id: str,
    current_user=Depends(get_current_user),
    use_case: SetCurrentResumeUseCase = Depends(get_set_current_resume_use_case),
) -> SuccessEnvelope[ResumeChangeResponse]:
    result = await use_case.execute(
        SetCurrentResumeCommand(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            resume_id=resume_id,
        )
    )
    return SuccessEnvelope(
        message="Resume version set as current.",
        data=ResumeChangeResponse(resume_id=result.resume_id),
    )


@router.delete(
    "/{profile_id}/resume/versions/{resume_id}",
    response_model=SuccessEnvelope[ResumeChangeResponse],
    operation_id="delete_resume",
)
async def delete_resume(
    profile_id: str,
    resume_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteResumeUseCase = Depends(get_delete_resume_use_case),
) -> SuccessEnvelope[ResumeChangeResponse]:
    result = await use_case.execute(
        DeleteResumeCommand(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            resume_id=resume_id,
        )
    )
    return SuccessEnvelope(
        message="Resume version deleted.",
        data=ResumeChangeResponse(resume_id=result.resume_id),
    )


@router.get(
    "/{profile_id}/portfolio",
    response_model=SuccessEnvelope[list[PortfolioItemResponse]],
    operation_id="list_portfolio_items",
)
async def list_portfolio_items(
    profile_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListPortfolioItemsUseCase = Depends(get_list_portfolio_items_use_case),
) -> SuccessEnvelope[list[PortfolioItemResponse]]:
    result = await use_case.execute(
        ListPortfolioItemsQuery(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    items = [_to_portfolio_item_response(i) for i in result.items]
    return SuccessEnvelope(
        message="Portfolio items.",
        data=items,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )


@router.get(
    "/{profile_id}/portfolio/{item_id}",
    response_model=SuccessEnvelope[PortfolioItemResponse],
    operation_id="get_portfolio_item",
)
async def get_portfolio_item(
    profile_id: str,
    item_id: str,
    current_user=Depends(get_current_user),
    use_case: GetPortfolioItemUseCase = Depends(get_get_portfolio_item_use_case),
) -> SuccessEnvelope[PortfolioItemResponse]:
    result = await use_case.execute(GetPortfolioItemQuery(actor_id=current_user.user_id, item_id=item_id))
    return SuccessEnvelope(message="Portfolio item.", data=_to_portfolio_item_response(result))


@router.get(
    "/{profile_id}/level-history",
    response_model=SuccessEnvelope[list[FreelancerLevelHistoryResponse]],
    operation_id="list_freelancer_level_history",
)
async def list_freelancer_level_history(
    profile_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListFreelancerLevelHistoryUseCase = Depends(get_list_freelancer_level_history_use_case),
) -> SuccessEnvelope[list[FreelancerLevelHistoryResponse]]:
    result = await use_case.execute(
        ListFreelancerLevelHistoryQuery(
            actor_id=current_user.user_id,
            profile_id=profile_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    history = [_to_history_response(h) for h in result.history]
    return SuccessEnvelope(
        message="Level history.",
        data=history,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )
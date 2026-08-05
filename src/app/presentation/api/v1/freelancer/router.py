from typing import Any

from fastapi import APIRouter, Depends

from app.application.freelancer.dto import (
    AddPortfolioItemCommand,
    ApproveFreelancerCommand,
    AssignFreelancerLevelCommand,
    CreateFreelancerProfileCommand,
    DeletePortfolioItemCommand,
    GetFreelancerProfileQuery,
    RejectFreelancerCommand,
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
from app.application.freelancer.use_cases.get_freelancer_profile import (
    GetFreelancerProfileUseCase,
)
from app.application.freelancer.use_cases.reject_freelancer import RejectFreelancerUseCase
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
    FreelancerProfileResponse,
    RejectFreelancerRequest,
    RejectFreelancerResponse,
    SubmitFreelancerApprovalResponse,
    UpdateFreelancerProfileRequest,
    UpdatePortfolioItemRequest,
    UpdatePortfolioItemResponse,
    UpdateResumeRequest,
    UpdateResumeResponse,
    UploadResumeRequest,
    UploadResumeResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_add_portfolio_item_use_case,
    get_approve_freelancer_use_case,
    get_assign_freelancer_level_use_case,
    get_create_freelancer_profile_use_case,
    get_delete_portfolio_item_use_case,
    get_get_freelancer_profile_use_case,
    get_reject_freelancer_use_case,
    get_submit_freelancer_approval_use_case,
    get_update_freelancer_profile_use_case,
    get_update_portfolio_item_use_case,
    get_update_resume_use_case,
    get_upload_resume_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/freelancers", tags=["Freelancer"])


def _profile_response(result: Any) -> FreelancerProfileResponse:
    return FreelancerProfileResponse(
        profile_id=result.profile_id,
        user_id=result.user_id,
        display_name=result.display_name,
        headline=result.headline,
        bio=result.bio,
        country_code=result.country_code,
        city=result.city,
        timezone=result.timezone,
        hourly_rate_min=result.hourly_rate_min,
        hourly_rate_max=result.hourly_rate_max,
        is_available=result.is_available,
        current_level_id=result.current_level_id,
        approval_status=result.approval_status.value,
        approved_at=result.approved_at.isoformat() if result.approved_at else None,
    )


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
    return SuccessEnvelope(message="Freelancer profile.", data=_profile_response(result))


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
    return SuccessEnvelope(message="Freelancer profile updated.", data=_profile_response(result))


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
    result = await use_case.execute(
        SubmitFreelancerApprovalCommand(user_id=current_user.user_id)
    )
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
            current_level_id=result.current_level_id,
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
            new_level_id=payload.new_level_id,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="Level assigned.",
        data=AssignFreelancerLevelResponse(
            profile_id=result.profile_id,
            old_level_id=result.old_level_id,
            new_level_id=result.new_level_id,
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
    result = await use_case.execute(
        UpdateResumeCommand(user_id=current_user.user_id, summary=payload.summary)
    )
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
    result = await use_case.execute(
        DeletePortfolioItemCommand(user_id=current_user.user_id, item_id=item_id)
    )
    return SuccessEnvelope(
        message="Portfolio item deleted.",
        data=DeletePortfolioItemResponse(item_id=result.item_id),
    )
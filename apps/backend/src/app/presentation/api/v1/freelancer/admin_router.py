from fastapi import APIRouter, Depends, Query

from app.application.freelancer.dto import (
    CreateFreelancerProfileOnBehalfCommand,
    ListFreelancerProfilesByApprovalStatusQuery,
    SoftDeleteFreelancerProfileCommand,
)
from app.application.freelancer.use_cases.admin_create_freelancer_profile_on_behalf import (
    AdminCreateFreelancerProfileOnBehalfUseCase,
)
from app.application.freelancer.use_cases.list_freelancer_profiles_by_approval_status import (
    ListFreelancerProfilesByApprovalStatusUseCase,
)
from app.application.freelancer.use_cases.soft_delete_freelancer_profile import (
    SoftDeleteFreelancerProfileUseCase,
)
from app.application.shared.pagination import total_pages
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.presentation.api.v1.freelancer.mappers import to_profile_response
from app.presentation.api.v1.freelancer.schemas import (
    AdminCreateFreelancerProfileRequest,
    CreateFreelancerProfileResponse,
    FreelancerProfileResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_admin_create_freelancer_profile_on_behalf_use_case,
    get_list_freelancer_profiles_by_approval_status_use_case,
    get_soft_delete_freelancer_profile_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/admin/freelancers", tags=["Admin - Freelancer"], route_class=DocumentedAPIRoute)


@router.post(
    "",
    response_model=SuccessEnvelope[CreateFreelancerProfileResponse],
    status_code=201,
    operation_id="admin_create_freelancer_profile",
)
async def admin_create_freelancer_profile(
    payload: AdminCreateFreelancerProfileRequest,
    current_user=Depends(get_current_user),
    use_case: AdminCreateFreelancerProfileOnBehalfUseCase = Depends(
        get_admin_create_freelancer_profile_on_behalf_use_case
    ),
) -> SuccessEnvelope[CreateFreelancerProfileResponse]:
    result = await use_case.execute(
        CreateFreelancerProfileOnBehalfCommand(
            actor_id=current_user.user_id,
            target_user_id=payload.target_user_id,
            display_name=payload.display_name,
            headline=payload.headline,
            bio=payload.bio,
            country_code=payload.country_code,
            city=payload.city,
            timezone=payload.timezone,
        )
    )
    return SuccessEnvelope(
        message="Freelancer profile created on behalf of user.",
        data=CreateFreelancerProfileResponse(profile_id=result.profile_id),
    )


@router.get(
    "",
    response_model=SuccessEnvelope[list[FreelancerProfileResponse]],
    operation_id="list_freelancer_profiles_by_approval_status",
)
async def list_freelancer_profiles_by_approval_status(
    status: FreelancerApprovalStatus = Query(...),
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListFreelancerProfilesByApprovalStatusUseCase = Depends(
        get_list_freelancer_profiles_by_approval_status_use_case
    ),
) -> SuccessEnvelope[list[FreelancerProfileResponse]]:
    result = await use_case.execute(
        ListFreelancerProfilesByApprovalStatusQuery(
            actor_id=current_user.user_id,
            status=status,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    profiles = [to_profile_response(p) for p in result.profiles]
    return SuccessEnvelope(
        message="Freelancer profiles.",
        data=profiles,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )


@router.delete(
    "/{profile_id}",
    response_model=SuccessEnvelope[dict],
    operation_id="soft_delete_freelancer_profile",
)
async def soft_delete_freelancer_profile(
    profile_id: str,
    current_user=Depends(get_current_user),
    use_case: SoftDeleteFreelancerProfileUseCase = Depends(get_soft_delete_freelancer_profile_use_case),
):
    result = await use_case.execute(
        SoftDeleteFreelancerProfileCommand(actor_id=current_user.user_id, profile_id=profile_id)
    )
    return SuccessEnvelope(
        message="Freelancer profile deleted.",
        data={"profile_id": result.profile_id},
    )
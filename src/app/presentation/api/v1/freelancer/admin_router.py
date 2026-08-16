from fastapi import APIRouter, Depends, Query

from app.application.freelancer.dto import (
    ActivateFreelancerLevelCommand,
    CreateFreelancerLevelCommand,
    CreateFreelancerProfileOnBehalfCommand,
    DeactivateFreelancerLevelCommand,
    DeleteFreelancerLevelCommand,
    ListFreelancerLevelsQuery,
    ListFreelancerProfilesByApprovalStatusQuery,
    SoftDeleteFreelancerProfileCommand,
    UpdateFreelancerLevelCommand,
)
from app.application.freelancer.use_cases.activate_freelancer_level import (
    ActivateFreelancerLevelUseCase,
)
from app.application.freelancer.use_cases.admin_create_freelancer_profile_on_behalf import (
    AdminCreateFreelancerProfileOnBehalfUseCase,
)
from app.application.freelancer.use_cases.create_freelancer_level import (
    CreateFreelancerLevelUseCase,
)
from app.application.freelancer.use_cases.deactivate_freelancer_level import (
    DeactivateFreelancerLevelUseCase,
)
from app.application.freelancer.use_cases.delete_freelancer_level import (
    DeleteFreelancerLevelUseCase,
)
from app.application.freelancer.use_cases.list_freelancer_levels import (
    ListFreelancerLevelsUseCase,
)
from app.application.freelancer.use_cases.list_freelancer_profiles_by_approval_status import (
    ListFreelancerProfilesByApprovalStatusUseCase,
)
from app.application.freelancer.use_cases.soft_delete_freelancer_profile import (
    SoftDeleteFreelancerProfileUseCase,
)
from app.application.freelancer.use_cases.update_freelancer_level import (
    UpdateFreelancerLevelUseCase,
)
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.presentation.api.v1.freelancer.mappers import to_profile_response
from app.presentation.api.v1.freelancer.schemas import (
    AdminCreateFreelancerProfileRequest,
    CreateFreelancerLevelRequest,
    CreateFreelancerProfileResponse,
    FreelancerLevelResponse,
    FreelancerProfileResponse,
    UpdateFreelancerLevelRequest,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.pagination import PageQuery, paginate
from app.presentation.core.providers import (
    get_activate_freelancer_level_use_case,
    get_admin_create_freelancer_profile_on_behalf_use_case,
    get_create_freelancer_level_use_case,
    get_deactivate_freelancer_level_use_case,
    get_delete_freelancer_level_use_case,
    get_list_freelancer_levels_use_case,
    get_list_freelancer_profiles_by_approval_status_use_case,
    get_soft_delete_freelancer_profile_use_case,
    get_update_freelancer_level_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/admin/freelancers", tags=["Admin - Freelancer"], route_class=DocumentedAPIRoute)
level_router = APIRouter(
    prefix="/admin/freelancer-levels", tags=["Admin - Freelancer Levels"], route_class=DocumentedAPIRoute
)


def _to_level_response(result: FreelancerLevelResponse) -> FreelancerLevelResponse:
    return FreelancerLevelResponse(
        level_id=result.level_id,
        level_key=result.level_key,
        name=result.name,
        rank_order=result.rank_order,
        access_type=result.access_type,
        min_completed_projects=result.min_completed_projects,
        min_rating=result.min_rating,
        max_active_applications=result.max_active_applications,
        can_apply_public_projects=result.can_apply_public_projects,
        can_apply_private_projects=result.can_apply_private_projects,
        is_active=result.is_active,
    )


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
        ListFreelancerProfilesByApprovalStatusQuery(actor_id=current_user.user_id, status=status)
    )
    profiles = [to_profile_response(p) for p in result]
    page_profiles, meta = paginate(profiles, pagination)
    return SuccessEnvelope(
        message="Freelancer profiles.",
        data=page_profiles,
        meta=meta,
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


@level_router.get(
    "",
    response_model=SuccessEnvelope[list[FreelancerLevelResponse]],
    operation_id="list_freelancer_levels",
)
async def list_freelancer_levels(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListFreelancerLevelsUseCase = Depends(get_list_freelancer_levels_use_case),
) -> SuccessEnvelope[list[FreelancerLevelResponse]]:
    result = await use_case.execute(ListFreelancerLevelsQuery(actor_id=current_user.user_id))
    levels = [_to_level_response(level) for level in result]
    page_levels, meta = paginate(levels, pagination)
    return SuccessEnvelope(
        message="Freelancer levels.",
        data=page_levels,
        meta=meta,
    )


@level_router.post(
    "",
    response_model=SuccessEnvelope[FreelancerLevelResponse],
    status_code=201,
    operation_id="create_freelancer_level",
)
async def create_freelancer_level(
    payload: CreateFreelancerLevelRequest,
    current_user=Depends(get_current_user),
    use_case: CreateFreelancerLevelUseCase = Depends(get_create_freelancer_level_use_case),
) -> SuccessEnvelope[FreelancerLevelResponse]:
    result = await use_case.execute(
        CreateFreelancerLevelCommand(
            actor_id=current_user.user_id,
            level_key=payload.level_key,
            name=payload.name,
            rank_order=payload.rank_order,
            access_type=payload.access_type.value,
            min_completed_projects=payload.min_completed_projects,
            min_rating=payload.min_rating,
            max_active_applications=payload.max_active_applications,
            can_apply_public_projects=payload.can_apply_public_projects,
            can_apply_private_projects=payload.can_apply_private_projects,
        )
    )
    return SuccessEnvelope(
        message="Freelancer level created.",
        data=FreelancerLevelResponse(
            level_id=result.level_id,
            level_key=payload.level_key,
            name=payload.name,
            rank_order=payload.rank_order,
            access_type=payload.access_type.value,
            min_completed_projects=payload.min_completed_projects,
            min_rating=payload.min_rating,
            max_active_applications=payload.max_active_applications,
            can_apply_public_projects=payload.can_apply_public_projects,
            can_apply_private_projects=payload.can_apply_private_projects,
            is_active=True,
        ),
    )


@level_router.patch(
    "/{level_id}",
    response_model=SuccessEnvelope[FreelancerLevelResponse],
    operation_id="update_freelancer_level",
)
async def update_freelancer_level(
    level_id: str,
    payload: UpdateFreelancerLevelRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateFreelancerLevelUseCase = Depends(get_update_freelancer_level_use_case),
) -> SuccessEnvelope[FreelancerLevelResponse]:
    result = await use_case.execute(
        UpdateFreelancerLevelCommand(
            actor_id=current_user.user_id,
            level_id=level_id,
            name=payload.name,
            rank_order=payload.rank_order,
            access_type=payload.access_type.value if payload.access_type else None,
            min_completed_projects=payload.min_completed_projects,
            min_rating=payload.min_rating,
            max_active_applications=payload.max_active_applications,
            can_apply_public_projects=payload.can_apply_public_projects,
            can_apply_private_projects=payload.can_apply_private_projects,
        )
    )
    return SuccessEnvelope(
        message="Freelancer level updated.",
        data=FreelancerLevelResponse(level_id=result.level_id),
    )


@level_router.delete(
    "/{level_id}",
    response_model=SuccessEnvelope[dict],
    operation_id="delete_freelancer_level",
)
async def delete_freelancer_level(
    level_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteFreelancerLevelUseCase = Depends(get_delete_freelancer_level_use_case),
):
    result = await use_case.execute(DeleteFreelancerLevelCommand(actor_id=current_user.user_id, level_id=level_id))
    return SuccessEnvelope(
        message="Freelancer level deleted.",
        data={"level_id": result.level_id},
    )


@level_router.post(
    "/{level_id}/activate",
    response_model=SuccessEnvelope[dict],
    operation_id="activate_freelancer_level",
)
async def activate_freelancer_level(
    level_id: str,
    current_user=Depends(get_current_user),
    use_case: ActivateFreelancerLevelUseCase = Depends(get_activate_freelancer_level_use_case),
):
    result = await use_case.execute(ActivateFreelancerLevelCommand(actor_id=current_user.user_id, level_id=level_id))
    return SuccessEnvelope(
        message="Freelancer level activated.",
        data={"level_id": result.level_id, "is_active": result.is_active},
    )


@level_router.post(
    "/{level_id}/deactivate",
    response_model=SuccessEnvelope[dict],
    operation_id="deactivate_freelancer_level",
)
async def deactivate_freelancer_level(
    level_id: str,
    current_user=Depends(get_current_user),
    use_case: DeactivateFreelancerLevelUseCase = Depends(get_deactivate_freelancer_level_use_case),
):
    result = await use_case.execute(DeactivateFreelancerLevelCommand(actor_id=current_user.user_id, level_id=level_id))
    return SuccessEnvelope(
        message="Freelancer level deactivated.",
        data={"level_id": result.level_id, "is_active": result.is_active},
    )

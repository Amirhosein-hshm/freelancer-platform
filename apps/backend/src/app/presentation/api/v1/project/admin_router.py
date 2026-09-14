from fastapi import APIRouter, Depends

from app.application.project.dto import (
    AdminApplyForProjectOnBehalfCommand,
    CreateProjectOnBehalfCommand,
    FormValueInput,
)
from app.application.project.use_cases.admin_apply_for_project_on_behalf import (
    AdminApplyForProjectOnBehalfUseCase,
)
from app.application.project.use_cases.admin_create_project_on_behalf import (
    AdminCreateProjectOnBehalfUseCase,
)
from app.presentation.api.v1.project.schemas import (
    AdminApplyForProjectRequest,
    AdminCreateProjectRequest,
    ApplyForProjectResponse,
    CreateProjectResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_admin_apply_for_project_on_behalf_use_case,
    get_admin_create_project_on_behalf_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/admin/projects", tags=["Admin - Project"], route_class=DocumentedAPIRoute)


@router.post(
    "",
    response_model=SuccessEnvelope[CreateProjectResponse],
    status_code=201,
    operation_id="admin_create_project",
)
async def admin_create_project(
    payload: AdminCreateProjectRequest,
    current_user=Depends(get_current_user),
    use_case: AdminCreateProjectOnBehalfUseCase = Depends(get_admin_create_project_on_behalf_use_case),
) -> SuccessEnvelope[CreateProjectResponse]:
    result = await use_case.execute(
        CreateProjectOnBehalfCommand(
            actor_id=current_user.user_id,
            target_customer_user_id=payload.target_customer_user_id,
            form_template_id=payload.form_template_id,
            title=payload.title,
            description=payload.description,
            visibility=payload.visibility,
            budget_type=payload.budget_type,
            currency_code=payload.currency_code,
            required_level=payload.required_level,
            fixed_budget=payload.fixed_budget,
            budget_min=payload.budget_min,
            budget_max=payload.budget_max,
            priority=payload.priority,
            application_deadline=payload.application_deadline,
            form_values=[
                FormValueInput(field_id=form_value.field_id, value=form_value.value)
                for form_value in payload.form_values
            ],
        )
    )
    return SuccessEnvelope(
        message="Project created on behalf of user.",
        data=CreateProjectResponse(
            project_id=result.project_id,
            project_code=result.project_code,
            status=result.status,
        ),
    )


@router.post(
    "/{project_id}/applications",
    response_model=SuccessEnvelope[ApplyForProjectResponse],
    status_code=201,
    operation_id="admin_apply_for_project",
)
async def admin_apply_for_project(
    project_id: str,
    payload: AdminApplyForProjectRequest,
    current_user=Depends(get_current_user),
    use_case: AdminApplyForProjectOnBehalfUseCase = Depends(get_admin_apply_for_project_on_behalf_use_case),
) -> SuccessEnvelope[ApplyForProjectResponse]:
    result = await use_case.execute(
        AdminApplyForProjectOnBehalfCommand(
            actor_id=current_user.user_id,
            target_freelancer_profile_id=payload.target_freelancer_profile_id,
            project_id=project_id,
            cover_letter=payload.cover_letter,
            proposed_amount=payload.proposed_amount,
            proposed_days=payload.proposed_days,
        )
    )
    return SuccessEnvelope(
        message="Application submitted on behalf of freelancer.",
        data=ApplyForProjectResponse(
            application_id=result.application_id,
            status=result.status,
        ),
    )

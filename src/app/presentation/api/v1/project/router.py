from fastapi import APIRouter, Depends

from app.application.project.dto import (
    AcceptFreelancerCommand,
    AdminApplyForProjectOnBehalfCommand,
    ApplicationResult,
    ApplyForProjectCommand,
    BudgetResult,
    CancelProjectCommand,
    CompleteProjectCommand,
    CreateProjectCommand,
    CreateProjectOnBehalfCommand,
    DeliveryResult,
    FormValueInput,
    GetAvailableProjectsQuery,
    GetMyProjectsQuery,
    GetProjectDetailsQuery,
    ProjectResult,
    PublishProjectCommand,
    RejectFreelancerCommand,
    RequestRevisionCommand,
    StartProjectCommand,
    SubmitDeliveryCommand,
    ViewApplicationsQuery,
    WithdrawApplicationCommand,
)
from app.application.project.use_cases.accept_freelancer import AcceptFreelancerUseCase
from app.application.project.use_cases.admin_apply_for_project_on_behalf import (
    AdminApplyForProjectOnBehalfUseCase,
)
from app.application.project.use_cases.admin_create_project_on_behalf import (
    AdminCreateProjectOnBehalfUseCase,
)
from app.application.project.use_cases.apply_for_project import ApplyForProjectUseCase
from app.application.project.use_cases.cancel_project import CancelProjectUseCase
from app.application.project.use_cases.complete_project import CompleteProjectUseCase
from app.application.project.use_cases.create_project import CreateProjectUseCase
from app.application.project.use_cases.get_available_projects import GetAvailableProjectsUseCase
from app.application.project.use_cases.get_my_projects import GetMyProjectsUseCase
from app.application.project.use_cases.get_project_details import GetProjectDetailsUseCase
from app.application.project.use_cases.publish_project import PublishProjectUseCase
from app.application.project.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.project.use_cases.request_revision import RequestRevisionUseCase
from app.application.project.use_cases.start_project import StartProjectUseCase
from app.application.project.use_cases.submit_delivery import SubmitDeliveryUseCase
from app.application.project.use_cases.view_applications import ViewApplicationsUseCase
from app.application.project.use_cases.withdraw_application import WithdrawApplicationUseCase
from app.presentation.api.v1.project.schemas import (
    AcceptFreelancerResponse,
    ApplicationResponse,
    ApplyForProjectRequest,
    ApplyForProjectResponse,
    BudgetResponse,
    CancelProjectRequest,
    CancelProjectResponse,
    CompleteProjectResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    DeliveryResponse,
    ProjectDetailsResponse,
    ProjectResponse,
    PublishProjectResponse,
    RejectFreelancerRequest,
    RejectFreelancerResponse,
    RequestRevisionRequest,
    RequestRevisionResponse,
    StartProjectResponse,
    SubmitDeliveryRequest,
    SubmitDeliveryResponse,
    WithdrawApplicationResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_accept_freelancer_use_case,
    get_admin_apply_for_project_on_behalf_use_case,
    get_admin_create_project_on_behalf_use_case,
    get_apply_for_project_use_case,
    get_cancel_project_use_case,
    get_complete_project_use_case,
    get_create_project_use_case,
    get_get_available_projects_use_case,
    get_get_my_projects_use_case,
    get_get_project_details_use_case,
    get_publish_project_use_case,
    get_reject_freelancer_use_case,
    get_request_revision_use_case,
    get_start_project_use_case,
    get_submit_delivery_use_case,
    get_view_applications_use_case,
    get_withdraw_application_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Project"])


def _to_budget_response(result: BudgetResult) -> BudgetResponse:
    return BudgetResponse(
        budget_type=result.budget_type,
        fixed_amount=result.fixed_amount,
        min_amount=result.min_amount,
        max_amount=result.max_amount,
        currency_code=result.currency_code,
    )


def _to_project_response(result: ProjectResult) -> ProjectResponse:
    return ProjectResponse(
        project_id=result.project_id,
        project_code=result.project_code,
        customer_user_id=result.customer_user_id,
        category_id=result.category_id,
        title=result.title,
        description=result.description,
        status=result.status,
        visibility=result.visibility,
        priority=result.priority,
        budget=_to_budget_response(result.budget),
        assigned_supervisor_user_id=result.assigned_supervisor_user_id,
        selected_application_id=result.selected_application_id,
        application_deadline=result.application_deadline,
        created_by_user_id=result.created_by_user_id,
        created_at=result.created_at,
    )


def _to_application_response(result: ApplicationResult) -> ApplicationResponse:
    return ApplicationResponse(
        application_id=result.application_id,
        project_id=result.project_id,
        freelancer_profile_id=result.freelancer_profile_id,
        status=result.status,
        cover_letter=result.cover_letter,
        proposed_amount=result.proposed_amount,
        proposed_days=result.proposed_days,
        applied_at=result.applied_at,
        submitted_by_user_id=result.submitted_by_user_id,
        decided_at=result.decided_at,
        decision_note=result.decision_note,
    )


def _to_delivery_response(result: DeliveryResult) -> DeliveryResponse:
    return DeliveryResponse(
        delivery_id=result.delivery_id,
        project_id=result.project_id,
        version_no=result.version_no,
        status=result.status,
        delivery_note=result.delivery_note,
        submitted_at=result.submitted_at,
        reviewed_at=result.reviewed_at,
        reviewer_user_id=result.reviewer_user_id,
        file_asset_ids=list(result.file_asset_ids),
    )


def _pagination_meta(pagination: PageQuery, total_items: int) -> PaginationMeta:
    return PaginationMeta(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
        total_pages=(total_items + pagination.page_size - 1) // pagination.page_size,
    )


@router.post(
    "",
    response_model=SuccessEnvelope[CreateProjectResponse],
    status_code=201,
    operation_id="create_project",
)
async def create_project(
    payload: CreateProjectRequest,
    current_user=Depends(get_current_user),
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),
    on_behalf_use_case: AdminCreateProjectOnBehalfUseCase = Depends(
        get_admin_create_project_on_behalf_use_case
    ),
) -> SuccessEnvelope[CreateProjectResponse]:
    create_kwargs = dict(
        actor_id=current_user.user_id,
        category_id=payload.category_id,
        title=payload.title,
        description=payload.description,
        visibility=payload.visibility,
        budget_type=payload.budget_type,
        currency_code=payload.currency_code,
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
    if payload.customer_user_id is not None:
        result = await on_behalf_use_case.execute(
            CreateProjectOnBehalfCommand(
                target_customer_user_id=payload.customer_user_id,
                **create_kwargs,
            )
        )
    else:
        result = await use_case.execute(CreateProjectCommand(**create_kwargs))
    return SuccessEnvelope(
        message="Project created.",
        data=CreateProjectResponse(
            project_id=result.project_id,
            project_code=result.project_code,
            status=result.status,
        ),
    )


@router.get(
    "",
    response_model=SuccessEnvelope[list[ProjectResponse]],
    operation_id="get_available_projects",
)
async def get_available_projects(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: GetAvailableProjectsUseCase = Depends(get_get_available_projects_use_case),
) -> SuccessEnvelope[list[ProjectResponse]]:
    result = await use_case.execute(GetAvailableProjectsQuery(actor_id=current_user.user_id))
    projects = [_to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="Available projects.",
        data=projects,
        meta=_pagination_meta(pagination, len(projects)),
    )


@router.get(
    "/my",
    response_model=SuccessEnvelope[list[ProjectResponse]],
    operation_id="get_my_projects",
)
async def get_my_projects(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: GetMyProjectsUseCase = Depends(get_get_my_projects_use_case),
) -> SuccessEnvelope[list[ProjectResponse]]:
    result = await use_case.execute(GetMyProjectsQuery(customer_user_id=current_user.user_id))
    projects = [_to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="My projects.",
        data=projects,
        meta=_pagination_meta(pagination, len(projects)),
    )


@router.get(
    "/{project_id}",
    response_model=SuccessEnvelope[ProjectDetailsResponse],
    operation_id="get_project_details",
)
async def get_project_details(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: GetProjectDetailsUseCase = Depends(get_get_project_details_use_case),
) -> SuccessEnvelope[ProjectDetailsResponse]:
    result = await use_case.execute(GetProjectDetailsQuery(project_id=project_id))
    return SuccessEnvelope(
        message="Project details.",
        data=ProjectDetailsResponse(
            project=_to_project_response(result.project),
            applications=[_to_application_response(application) for application in result.applications],
            deliveries=[_to_delivery_response(delivery) for delivery in result.deliveries],
        ),
    )


@router.post(
    "/{project_id}/publish",
    response_model=SuccessEnvelope[PublishProjectResponse],
    operation_id="publish_project",
)
async def publish_project(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: PublishProjectUseCase = Depends(get_publish_project_use_case),
) -> SuccessEnvelope[PublishProjectResponse]:
    result = await use_case.execute(
        PublishProjectCommand(actor_id=current_user.user_id, project_id=project_id)
    )
    return SuccessEnvelope(
        message="Project published.",
        data=PublishProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.post(
    "/{project_id}/cancel",
    response_model=SuccessEnvelope[CancelProjectResponse],
    operation_id="cancel_project",
)
async def cancel_project(
    project_id: str,
    payload: CancelProjectRequest,
    current_user=Depends(get_current_user),
    use_case: CancelProjectUseCase = Depends(get_cancel_project_use_case),
) -> SuccessEnvelope[CancelProjectResponse]:
    result = await use_case.execute(
        CancelProjectCommand(
            actor_id=current_user.user_id,
            project_id=project_id,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="Project cancelled.",
        data=CancelProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.post(
    "/{project_id}/complete",
    response_model=SuccessEnvelope[CompleteProjectResponse],
    operation_id="complete_project",
)
async def complete_project(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: CompleteProjectUseCase = Depends(get_complete_project_use_case),
) -> SuccessEnvelope[CompleteProjectResponse]:
    result = await use_case.execute(
        CompleteProjectCommand(actor_id=current_user.user_id, project_id=project_id)
    )
    return SuccessEnvelope(
        message="Project completed.",
        data=CompleteProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.post(
    "/{project_id}/applications",
    response_model=SuccessEnvelope[ApplyForProjectResponse],
    status_code=201,
    operation_id="apply_for_project",
)
async def apply_for_project(
    project_id: str,
    payload: ApplyForProjectRequest,
    current_user=Depends(get_current_user),
    use_case: ApplyForProjectUseCase = Depends(get_apply_for_project_use_case),
    on_behalf_use_case: AdminApplyForProjectOnBehalfUseCase = Depends(
        get_admin_apply_for_project_on_behalf_use_case
    ),
) -> SuccessEnvelope[ApplyForProjectResponse]:
    apply_kwargs = dict(
        actor_id=current_user.user_id,
        project_id=project_id,
        cover_letter=payload.cover_letter,
        proposed_amount=payload.proposed_amount,
        proposed_days=payload.proposed_days,
    )
    if payload.target_freelancer_profile_id is not None:
        result = await on_behalf_use_case.execute(
            AdminApplyForProjectOnBehalfCommand(
                target_freelancer_profile_id=payload.target_freelancer_profile_id,
                **apply_kwargs,
            )
        )
    else:
        result = await use_case.execute(ApplyForProjectCommand(**apply_kwargs))
    return SuccessEnvelope(
        message="Application submitted.",
        data=ApplyForProjectResponse(
            application_id=result.application_id,
            status=result.status,
        ),
    )


@router.get(
    "/{project_id}/applications",
    response_model=SuccessEnvelope[list[ApplicationResponse]],
    operation_id="view_applications",
)
async def view_applications(
    project_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ViewApplicationsUseCase = Depends(get_view_applications_use_case),
) -> SuccessEnvelope[list[ApplicationResponse]]:
    result = await use_case.execute(
        ViewApplicationsQuery(actor_id=current_user.user_id, project_id=project_id)
    )
    applications = [_to_application_response(application) for application in result.applications]
    return SuccessEnvelope(
        message="Project applications.",
        data=applications,
        meta=_pagination_meta(pagination, len(applications)),
    )


@router.post(
    "/{project_id}/applications/{application_id}/accept",
    response_model=SuccessEnvelope[AcceptFreelancerResponse],
    operation_id="accept_freelancer",
)
async def accept_freelancer(
    project_id: str,
    application_id: str,
    current_user=Depends(get_current_user),
    use_case: AcceptFreelancerUseCase = Depends(get_accept_freelancer_use_case),
) -> SuccessEnvelope[AcceptFreelancerResponse]:
    result = await use_case.execute(
        AcceptFreelancerCommand(actor_id=current_user.user_id, application_id=application_id)
    )
    return SuccessEnvelope(
        message="Freelancer accepted.",
        data=AcceptFreelancerResponse(
            project_id=result.project_id,
            selected_application_id=result.selected_application_id,
            status=result.status,
        ),
    )


@router.post(
    "/{project_id}/applications/{application_id}/reject",
    response_model=SuccessEnvelope[RejectFreelancerResponse],
    operation_id="reject_freelancer_application",
)
async def reject_freelancer(
    project_id: str,
    application_id: str,
    payload: RejectFreelancerRequest,
    current_user=Depends(get_current_user),
    use_case: RejectFreelancerUseCase = Depends(get_reject_freelancer_use_case),
) -> SuccessEnvelope[RejectFreelancerResponse]:
    result = await use_case.execute(
        RejectFreelancerCommand(
            actor_id=current_user.user_id,
            application_id=application_id,
            note=payload.note,
        )
    )
    return SuccessEnvelope(
        message="Freelancer rejected.",
        data=RejectFreelancerResponse(
            application_id=result.application_id,
            status=result.status,
        ),
    )


@router.post(
    "/{project_id}/applications/{application_id}/withdraw",
    response_model=SuccessEnvelope[WithdrawApplicationResponse],
    operation_id="withdraw_application",
)
async def withdraw_application(
    project_id: str,
    application_id: str,
    current_user=Depends(get_current_user),
    use_case: WithdrawApplicationUseCase = Depends(get_withdraw_application_use_case),
) -> SuccessEnvelope[WithdrawApplicationResponse]:
    result = await use_case.execute(
        WithdrawApplicationCommand(actor_id=current_user.user_id, application_id=application_id)
    )
    return SuccessEnvelope(
        message="Application withdrawn.",
        data=WithdrawApplicationResponse(
            application_id=result.application_id,
            status=result.status,
        ),
    )


@router.post(
    "/{project_id}/start",
    response_model=SuccessEnvelope[StartProjectResponse],
    operation_id="start_project",
)
async def start_project(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: StartProjectUseCase = Depends(get_start_project_use_case),
) -> SuccessEnvelope[StartProjectResponse]:
    result = await use_case.execute(
        StartProjectCommand(actor_id=current_user.user_id, project_id=project_id)
    )
    return SuccessEnvelope(
        message="Project started.",
        data=StartProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.post(
    "/{project_id}/deliveries",
    response_model=SuccessEnvelope[SubmitDeliveryResponse],
    status_code=201,
    operation_id="submit_delivery",
)
async def submit_delivery(
    project_id: str,
    payload: SubmitDeliveryRequest,
    current_user=Depends(get_current_user),
    use_case: SubmitDeliveryUseCase = Depends(get_submit_delivery_use_case),
) -> SuccessEnvelope[SubmitDeliveryResponse]:
    result = await use_case.execute(
        SubmitDeliveryCommand(
            actor_id=current_user.user_id,
            project_id=project_id,
            delivery_note=payload.delivery_note,
            file_asset_ids=list(payload.file_asset_ids),
        )
    )
    return SuccessEnvelope(
        message="Delivery submitted.",
        data=SubmitDeliveryResponse(
            delivery_id=result.delivery_id,
            version_no=result.version_no,
            project_status=result.project_status,
        ),
    )


@router.post(
    "/{project_id}/revisions",
    response_model=SuccessEnvelope[RequestRevisionResponse],
    operation_id="request_revision",
)
async def request_revision(
    project_id: str,
    payload: RequestRevisionRequest,
    current_user=Depends(get_current_user),
    use_case: RequestRevisionUseCase = Depends(get_request_revision_use_case),
) -> SuccessEnvelope[RequestRevisionResponse]:
    result = await use_case.execute(
        RequestRevisionCommand(
            actor_id=current_user.user_id,
            project_id=project_id,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="Revision requested.",
        data=RequestRevisionResponse(
            revision_id=result.revision_id,
            round_no=result.round_no,
            project_status=result.project_status,
        ),
    )

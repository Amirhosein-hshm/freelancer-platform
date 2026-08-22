from fastapi import APIRouter, Depends

from app.application.project.dto import (
    AcceptFreelancerCommand,
    ApplyForProjectCommand,
    CancelProjectCommand,
    CreateProjectCommand,
    DeleteProjectCommand,
    FormValueInput,
    GetAvailableProjectsQuery,
    GetMyProjectsQuery,
    GetProjectApplicationQuery,
    GetProjectDetailsQuery,
    ListProjectDeliveriesQuery,
    ListProjectRevisionRequestsQuery,
    ListProjectStatusHistoryQuery,
    PublishProjectCommand,
    RejectFreelancerCommand,
    StartProjectCommand,
    SubmitDeliveryCommand,
    UpdateProjectCommand,
    ViewApplicationsQuery,
    WithdrawApplicationCommand,
)
from app.application.project.use_cases.accept_freelancer import AcceptFreelancerUseCase
from app.application.project.use_cases.apply_for_project import ApplyForProjectUseCase
from app.application.project.use_cases.cancel_project import CancelProjectUseCase
from app.application.project.use_cases.create_project import CreateProjectUseCase
from app.application.project.use_cases.delete_project import DeleteProjectUseCase
from app.application.project.use_cases.get_available_projects import GetAvailableProjectsUseCase
from app.application.project.use_cases.get_my_projects import GetMyProjectsUseCase
from app.application.project.use_cases.get_project_application import (
    GetProjectApplicationUseCase,
)
from app.application.project.use_cases.get_project_details import GetProjectDetailsUseCase
from app.application.project.use_cases.list_project_deliveries import (
    ListProjectDeliveriesUseCase,
)
from app.application.project.use_cases.list_project_revision_requests import (
    ListProjectRevisionRequestsUseCase,
)
from app.application.project.use_cases.list_project_status_history import (
    ListProjectStatusHistoryUseCase,
)
from app.application.project.use_cases.publish_project import PublishProjectUseCase
from app.application.project.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.project.use_cases.start_project import StartProjectUseCase
from app.application.project.use_cases.submit_delivery import SubmitDeliveryUseCase
from app.application.project.use_cases.update_project import UpdateProjectUseCase
from app.application.project.use_cases.view_applications import ViewApplicationsUseCase
from app.application.project.use_cases.withdraw_application import WithdrawApplicationUseCase
from app.application.shared.pagination import total_pages
from app.presentation.api.v1.project.mappers import (
    to_application_response,
    to_delivery_response,
    to_project_response,
)
from app.presentation.api.v1.project.schemas import (
    AcceptFreelancerResponse,
    ApplicationResponse,
    ApplyForProjectRequest,
    ApplyForProjectResponse,
    CancelProjectRequest,
    CancelProjectResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    DeleteProjectResponse,
    DeliveryResponse,
    ProjectDetailsResponse,
    ProjectResponse,
    ProjectRevisionRequestResponse,
    ProjectStatusHistoryResponse,
    PublishProjectResponse,
    RejectFreelancerRequest,
    RejectFreelancerResponse,
    StartProjectResponse,
    SubmitDeliveryRequest,
    SubmitDeliveryResponse,
    UpdateProjectRequest,
    UpdateProjectResponse,
    WithdrawApplicationResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_accept_freelancer_use_case,
    get_apply_for_project_use_case,
    get_cancel_project_use_case,
    get_create_project_use_case,
    get_delete_project_use_case,
    get_get_available_projects_use_case,
    get_get_my_projects_use_case,
    get_get_project_application_use_case,
    get_get_project_details_use_case,
    get_list_project_deliveries_use_case,
    get_list_project_revision_requests_use_case,
    get_list_project_status_history_use_case,
    get_publish_project_use_case,
    get_reject_freelancer_use_case,
    get_start_project_use_case,
    get_submit_delivery_use_case,
    get_update_project_use_case,
    get_view_applications_use_case,
    get_withdraw_application_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Project"], route_class=DocumentedAPIRoute)


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
) -> SuccessEnvelope[CreateProjectResponse]:
    result = await use_case.execute(
        CreateProjectCommand(
            actor_id=current_user.user_id,
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
    result = await use_case.execute(
        GetAvailableProjectsQuery(
            actor_id=current_user.user_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    projects = [to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="Available projects.",
        data=projects,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
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
    result = await use_case.execute(
        GetMyProjectsQuery(
            customer_user_id=current_user.user_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    projects = [to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="My projects.",
        data=projects,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
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
    result = await use_case.execute(GetProjectDetailsQuery(actor_id=current_user.user_id, project_id=project_id))
    return SuccessEnvelope(
        message="Project details.",
        data=ProjectDetailsResponse(
            project=to_project_response(result.project),
            applications=[to_application_response(application) for application in result.applications],
            deliveries=[to_delivery_response(delivery) for delivery in result.deliveries],
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
    result = await use_case.execute(PublishProjectCommand(actor_id=current_user.user_id, project_id=project_id))
    return SuccessEnvelope(
        message="Project published.",
        data=PublishProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.patch(
    "/{project_id}",
    response_model=SuccessEnvelope[UpdateProjectResponse],
    operation_id="update_project",
)
async def update_project(
    project_id: str,
    payload: UpdateProjectRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateProjectUseCase = Depends(get_update_project_use_case),
) -> SuccessEnvelope[UpdateProjectResponse]:
    result = await use_case.execute(
        UpdateProjectCommand(
            actor_id=current_user.user_id,
            project_id=project_id,
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
        message="Project updated.",
        data=UpdateProjectResponse(project_id=result.project_id, status=result.status),
    )


@router.delete(
    "/{project_id}",
    response_model=SuccessEnvelope[DeleteProjectResponse],
    operation_id="delete_project",
)
async def delete_project(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteProjectUseCase = Depends(get_delete_project_use_case),
) -> SuccessEnvelope[DeleteProjectResponse]:
    result = await use_case.execute(
        DeleteProjectCommand(actor_id=current_user.user_id, project_id=project_id)
    )
    return SuccessEnvelope(
        message="Project deleted.",
        data=DeleteProjectResponse(project_id=result.project_id, deleted_at=result.deleted_at),
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
) -> SuccessEnvelope[ApplyForProjectResponse]:
    result = await use_case.execute(
        ApplyForProjectCommand(
            actor_id=current_user.user_id,
            project_id=project_id,
            cover_letter=payload.cover_letter,
            proposed_amount=payload.proposed_amount,
            proposed_days=payload.proposed_days,
        )
    )
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
        ViewApplicationsQuery(
            actor_id=current_user.user_id,
            project_id=project_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    applications = [to_application_response(application) for application in result.applications]
    return SuccessEnvelope(
        message="Project applications.",
        data=applications,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
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
    result = await use_case.execute(StartProjectCommand(actor_id=current_user.user_id, project_id=project_id))
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



def _to_revision_response(revision: ProjectRevisionRequestResponse) -> ProjectRevisionRequestResponse:
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


def _to_status_history_response(
    history: ProjectStatusHistoryResponse,
) -> ProjectStatusHistoryResponse:
    return ProjectStatusHistoryResponse(
        history_id=history.history_id,
        project_id=history.project_id,
        from_status=history.from_status,
        to_status=history.to_status,
        changed_by_user_id=history.changed_by_user_id,
        reason=history.reason,
        changed_at=history.changed_at,
    )


@router.get(
    "/{project_id}/applications/{application_id}",
    response_model=SuccessEnvelope[ApplicationResponse],
    operation_id="get_project_application",
)
async def get_project_application(
    project_id: str,
    application_id: str,
    current_user=Depends(get_current_user),
    use_case: GetProjectApplicationUseCase = Depends(get_get_project_application_use_case),
) -> SuccessEnvelope[ApplicationResponse]:
    result = await use_case.execute(
        GetProjectApplicationQuery(actor_id=current_user.user_id, application_id=application_id)
    )
    return SuccessEnvelope(
        message="Application details.",
        data=to_application_response(result),
    )


@router.get(
    "/{project_id}/deliveries",
    response_model=SuccessEnvelope[list[DeliveryResponse]],
    operation_id="list_project_deliveries",
)
async def list_project_deliveries(
    project_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListProjectDeliveriesUseCase = Depends(get_list_project_deliveries_use_case),
) -> SuccessEnvelope[list[DeliveryResponse]]:
    result = await use_case.execute(
        ListProjectDeliveriesQuery(
            actor_id=current_user.user_id,
            project_id=project_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    deliveries = [to_delivery_response(d) for d in result.deliveries]
    return SuccessEnvelope(
        message="Project deliveries.",
        data=deliveries,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )


@router.get(
    "/{project_id}/revisions",
    response_model=SuccessEnvelope[list[ProjectRevisionRequestResponse]],
    operation_id="list_project_revision_requests",
)
async def list_project_revision_requests(
    project_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListProjectRevisionRequestsUseCase = Depends(get_list_project_revision_requests_use_case),
) -> SuccessEnvelope[list[ProjectRevisionRequestResponse]]:
    result = await use_case.execute(
        ListProjectRevisionRequestsQuery(
            actor_id=current_user.user_id,
            project_id=project_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    revisions = [_to_revision_response(r) for r in result.revisions]
    return SuccessEnvelope(
        message="Project revision requests.",
        data=revisions,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )


@router.get(
    "/{project_id}/status-history",
    response_model=SuccessEnvelope[list[ProjectStatusHistoryResponse]],
    operation_id="list_project_status_history",
)
async def list_project_status_history(
    project_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListProjectStatusHistoryUseCase = Depends(get_list_project_status_history_use_case),
) -> SuccessEnvelope[list[ProjectStatusHistoryResponse]]:
    result = await use_case.execute(
        ListProjectStatusHistoryQuery(
            actor_id=current_user.user_id,
            project_id=project_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    history = [_to_status_history_response(h) for h in result.history]
    return SuccessEnvelope(
        message="Project status history.",
        data=history,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )

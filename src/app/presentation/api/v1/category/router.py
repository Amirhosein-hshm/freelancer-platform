from fastapi import APIRouter, Depends

from app.application.category.dto import (
    AssignSupervisorCommand,
    CreateCategoryCommand,
    DeleteCategoryCommand,
    GetCategoriesQuery,
    GetCategoryQuery,
    ListCategorySupervisorsQuery,
    RemoveSupervisorCommand,
    UpdateCategoryCommand,
)
from app.application.category.use_cases.assign_supervisor import AssignSupervisorUseCase
from app.application.category.use_cases.create_category import CreateCategoryUseCase
from app.application.category.use_cases.delete_category import DeleteCategoryUseCase
from app.application.category.use_cases.get_categories import GetCategoriesUseCase
from app.application.category.use_cases.get_category import GetCategoryUseCase
from app.application.category.use_cases.get_category_projects import (
    GetCategoryProjectsQuery,
    GetCategoryProjectsUseCase,
)
from app.application.category.use_cases.list_category_supervisors import (
    ListCategorySupervisorsUseCase,
)
from app.application.category.use_cases.remove_supervisor import RemoveSupervisorUseCase
from app.application.category.use_cases.update_category import UpdateCategoryUseCase
from app.presentation.api.v1.category.schemas import (
    AssignSupervisorRequest,
    AssignSupervisorResponse,
    CategoryResponse,
    CategorySupervisorResponse,
    CreateCategoryRequest,
    DeleteCategoryResponse,
    ListCategorySupervisorsResponse,
    RemoveSupervisorResponse,
    UpdateCategoryRequest,
)
from app.presentation.api.v1.project.schemas import ProjectResponse
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.pagination import PageQuery, paginate
from app.presentation.core.providers import (
    get_assign_supervisor_use_case,
    get_create_category_use_case,
    get_delete_category_use_case,
    get_get_categories_use_case,
    get_get_category_projects_use_case,
    get_get_category_use_case,
    get_list_category_supervisors_use_case,
    get_remove_supervisor_use_case,
    get_update_category_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/categories", tags=["Category"], route_class=DocumentedAPIRoute)


def _category_response(result) -> CategoryResponse:
    return CategoryResponse(
        category_id=result.category_id,
        category_key=result.category_key,
        name=result.name,
        slug=result.slug,
        description=result.description,
        is_active=result.is_active,
        sort_order=result.sort_order,
        parent_category_id=result.parent_category_id,
    )


def _project_response(result) -> ProjectResponse:
    return ProjectResponse(
        project_id=result.project_id,
        project_code=result.project_code,
        customer_user_id=result.customer_user_id,
        category_id=result.category_id,
        title=result.title,
        description=result.description,
        status=result.status.value,
        visibility=result.visibility.value,
        priority=result.priority.value,
        budget=result.budget,
        assigned_supervisor_user_id=result.assigned_supervisor_user_id,
        selected_application_id=result.selected_application_id,
        application_deadline=result.application_deadline,
        created_by_user_id=result.created_by_user_id,
        created_at=result.created_at,
    )


@router.get(
    "",
    response_model=SuccessEnvelope[list[CategoryResponse]],
    operation_id="get_categories",
)
async def get_categories(
    pagination: PageQuery = Depends(),
    use_case: GetCategoriesUseCase = Depends(get_get_categories_use_case),
) -> SuccessEnvelope[list[CategoryResponse]]:
    result = await use_case.execute(GetCategoriesQuery())
    categories = [_category_response(c) for c in result.categories]
    page_categories, meta = paginate(categories, pagination)
    return SuccessEnvelope(
        message="Categories.",
        data=page_categories,
        meta=meta,
    )


@router.get(
    "/{category_id}",
    response_model=SuccessEnvelope[CategoryResponse],
    operation_id="get_category",
)
async def get_category(
    category_id: str,
    use_case: GetCategoryUseCase = Depends(get_get_category_use_case),
) -> SuccessEnvelope[CategoryResponse]:
    result = await use_case.execute(GetCategoryQuery(category_id=category_id))
    return SuccessEnvelope(
        message="Category details.",
        data=_category_response(result),
    )


@router.get(
    "/{category_id}/supervisors",
    response_model=SuccessEnvelope[ListCategorySupervisorsResponse],
    operation_id="list_category_supervisors",
)
async def list_category_supervisors(
    category_id: str,
    use_case: ListCategorySupervisorsUseCase = Depends(get_list_category_supervisors_use_case),
) -> SuccessEnvelope[ListCategorySupervisorsResponse]:
    result = await use_case.execute(ListCategorySupervisorsQuery(category_id=category_id))
    return SuccessEnvelope(
        message="Category supervisors.",
        data=ListCategorySupervisorsResponse(
            supervisors=[
                CategorySupervisorResponse(
                    link_id=supervisor.link_id,
                    category_id=supervisor.category_id,
                    supervisor_user_id=supervisor.supervisor_user_id,
                    is_primary=supervisor.is_primary,
                    assigned_at=supervisor.assigned_at.isoformat(),
                )
                for supervisor in result.supervisors
            ]
        ),
    )


@router.get(
    "/{category_id}/projects",
    response_model=SuccessEnvelope[list[ProjectResponse]],
    operation_id="get_category_projects",
)
async def get_category_projects(
    category_id: str,
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: GetCategoryProjectsUseCase = Depends(get_get_category_projects_use_case),
) -> SuccessEnvelope[list[ProjectResponse]]:
    result = await use_case.execute(GetCategoryProjectsQuery(category_id=category_id))
    projects = [_project_response(p) for p in result.projects]
    page_projects, meta = paginate(projects, pagination)
    return SuccessEnvelope(
        message="Category projects.",
        data=page_projects,
        meta=meta,
    )


@router.post(
    "",
    response_model=SuccessEnvelope[CategoryResponse],
    status_code=201,
    operation_id="create_category",
)
async def create_category(
    payload: CreateCategoryRequest,
    current_user=Depends(get_current_user),
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case),
) -> SuccessEnvelope[CategoryResponse]:
    result = await use_case.execute(
        CreateCategoryCommand(
            actor_id=current_user.user_id,
            name=payload.name,
            slug=payload.slug,
            category_key=payload.category_key,
            description=payload.description,
            parent_category_id=payload.parent_category_id,
            sort_order=payload.sort_order,
        )
    )
    return SuccessEnvelope(
        message="Category created.",
        data=_category_response(result),
    )


@router.patch(
    "/{category_id}",
    response_model=SuccessEnvelope[CategoryResponse],
    operation_id="update_category",
)
async def update_category(
    category_id: str,
    payload: UpdateCategoryRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateCategoryUseCase = Depends(get_update_category_use_case),
) -> SuccessEnvelope[CategoryResponse]:
    result = await use_case.execute(
        UpdateCategoryCommand(
            actor_id=current_user.user_id,
            category_id=category_id,
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            sort_order=payload.sort_order,
        )
    )
    return SuccessEnvelope(
        message="Category updated.",
        data=_category_response(result),
    )


@router.delete(
    "/{category_id}",
    response_model=SuccessEnvelope[DeleteCategoryResponse],
    operation_id="delete_category",
)
async def delete_category(
    category_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteCategoryUseCase = Depends(get_delete_category_use_case),
) -> SuccessEnvelope[DeleteCategoryResponse]:
    result = await use_case.execute(DeleteCategoryCommand(actor_id=current_user.user_id, category_id=category_id))
    return SuccessEnvelope(
        message="Category deleted.",
        data=DeleteCategoryResponse(category_id=result.category_id),
    )


@router.post(
    "/{category_id}/supervisors",
    response_model=SuccessEnvelope[AssignSupervisorResponse],
    operation_id="assign_supervisor",
)
async def assign_supervisor(
    category_id: str,
    payload: AssignSupervisorRequest,
    current_user=Depends(get_current_user),
    use_case: AssignSupervisorUseCase = Depends(get_assign_supervisor_use_case),
) -> SuccessEnvelope[AssignSupervisorResponse]:
    result = await use_case.execute(
        AssignSupervisorCommand(
            actor_id=current_user.user_id,
            category_id=category_id,
            supervisor_user_id=payload.supervisor_user_id,
        )
    )
    return SuccessEnvelope(
        message="Supervisor assigned.",
        data=AssignSupervisorResponse(
            link_id=result.link_id,
            category_id=result.category_id,
            supervisor_user_id=result.supervisor_user_id,
        ),
    )


@router.delete(
    "/{category_id}/supervisors/{supervisor_user_id}",
    response_model=SuccessEnvelope[RemoveSupervisorResponse],
    operation_id="remove_supervisor",
)
async def remove_supervisor(
    category_id: str,
    supervisor_user_id: str,
    current_user=Depends(get_current_user),
    use_case: RemoveSupervisorUseCase = Depends(get_remove_supervisor_use_case),
) -> SuccessEnvelope[RemoveSupervisorResponse]:
    result = await use_case.execute(
        RemoveSupervisorCommand(
            actor_id=current_user.user_id,
            category_id=category_id,
            supervisor_user_id=supervisor_user_id,
        )
    )
    return SuccessEnvelope(
        message="Supervisor removed.",
        data=RemoveSupervisorResponse(
            category_id=result.category_id,
            supervisor_user_id=result.supervisor_user_id,
            revoked_at=result.revoked_at.isoformat(),
        ),
    )

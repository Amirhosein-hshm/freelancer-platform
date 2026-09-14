from fastapi import APIRouter, Depends, Query

from app.application.iam.dto import ListPermissionsQuery, ListRolesQuery
from app.application.iam.use_cases.list_permissions import ListPermissionsUseCase
from app.application.iam.use_cases.list_roles import ListRolesUseCase
from app.presentation.api.v1.iam.schemas import (
    ListPermissionsResponse,
    ListRolesResponse,
    PermissionResponse,
    RoleResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_list_permissions_use_case,
    get_list_roles_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(tags=["IAM-Admin"], route_class=DocumentedAPIRoute)


@router.get(
    "/roles",
    response_model=SuccessEnvelope[ListRolesResponse],
    operation_id="list_roles",
)
async def list_roles(
    current_user=Depends(get_current_user),
    use_case: ListRolesUseCase = Depends(get_list_roles_use_case),
) -> SuccessEnvelope[ListRolesResponse]:
    result = await use_case.execute(ListRolesQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="Roles listed.",
        data=ListRolesResponse(
            roles=[
                RoleResponse(
                    role_id=role.role_id,
                    role_key=role.role_key,
                    name=role.name,
                    description=role.description,
                    is_system=role.is_system,
                )
                for role in result.roles
            ]
        ),
    )


@router.get(
    "/permissions",
    response_model=SuccessEnvelope[ListPermissionsResponse],
    operation_id="list_permissions",
)
async def list_permissions(
    module: str | None = Query(default=None, description="Filter permissions by module."),
    current_user=Depends(get_current_user),
    use_case: ListPermissionsUseCase = Depends(get_list_permissions_use_case),
) -> SuccessEnvelope[ListPermissionsResponse]:
    result = await use_case.execute(ListPermissionsQuery(actor_id=current_user.user_id, module=module))
    return SuccessEnvelope(
        message="Permissions listed.",
        data=ListPermissionsResponse(
            permissions=[
                PermissionResponse(
                    permission_id=permission.permission_id,
                    permission_key=permission.permission_key,
                    module=permission.module,
                    action=permission.action,
                    description=permission.description,
                    is_system=permission.is_system,
                )
                for permission in result.permissions
            ]
        ),
    )

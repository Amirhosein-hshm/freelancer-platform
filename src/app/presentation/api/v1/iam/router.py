from fastapi import APIRouter, Depends

from app.application.iam.dto import (
    ActivateUserCommand,
    AdminCreateUserCommand,
    AdminDeleteUserCommand,
    AdminUpdateUserCommand,
    AssignRoleCommand,
    BlockUserCommand,
    GrantPermissionCommand,
    RemoveRoleCommand,
    RevokePermissionCommand,
)
from app.application.iam.use_cases.activate_user import ActivateUserUseCase
from app.application.iam.use_cases.admin_create_user import AdminCreateUserUseCase
from app.application.iam.use_cases.admin_delete_user import AdminDeleteUserUseCase
from app.application.iam.use_cases.admin_update_user import AdminUpdateUserUseCase
from app.application.iam.use_cases.assign_role import AssignRoleUseCase
from app.application.iam.use_cases.block_user import BlockUserUseCase
from app.application.iam.use_cases.grant_permission import GrantPermissionUseCase
from app.application.iam.use_cases.remove_role import RemoveRoleUseCase
from app.application.iam.use_cases.revoke_permission import RevokePermissionUseCase
from app.presentation.api.v1.iam.schemas import (
    ActivateUserResponse,
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminDeleteUserResponse,
    AdminUpdateUserRequest,
    AdminUpdateUserResponse,
    AssignRoleRequest,
    AssignRoleResponse,
    BlockUserRequest,
    BlockUserResponse,
    GrantPermissionRequest,
    GrantPermissionResponse,
    RemoveRoleResponse,
    RevokePermissionResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_activate_user_use_case,
    get_admin_create_user_use_case,
    get_admin_delete_user_use_case,
    get_admin_update_user_use_case,
    get_assign_role_use_case,
    get_block_user_use_case,
    get_grant_permission_use_case,
    get_remove_role_use_case,
    get_revoke_permission_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["IAM-Admin"])


@router.post(
    "",
    response_model=SuccessEnvelope[AdminCreateUserResponse],
    status_code=201,
    operation_id="admin_create_user",
)
async def admin_create_user(
    payload: AdminCreateUserRequest,
    current_user=Depends(get_current_user),
    use_case: AdminCreateUserUseCase = Depends(get_admin_create_user_use_case),
) -> SuccessEnvelope[AdminCreateUserResponse]:
    result = await use_case.execute(
        AdminCreateUserCommand(
            actor_id=current_user.user_id,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    )
    return SuccessEnvelope(
        message="User created.",
        data=AdminCreateUserResponse(
            user_id=result.user_id,
            email=result.email,
            status=result.status,
            created_at=result.created_at.isoformat(),
        ),
    )


@router.patch(
    "/{user_id}",
    response_model=SuccessEnvelope[AdminUpdateUserResponse],
    operation_id="admin_update_user",
)
async def admin_update_user(
    user_id: str,
    payload: AdminUpdateUserRequest,
    current_user=Depends(get_current_user),
    use_case: AdminUpdateUserUseCase = Depends(get_admin_update_user_use_case),
) -> SuccessEnvelope[AdminUpdateUserResponse]:
    result = await use_case.execute(
        AdminUpdateUserCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
        )
    )
    return SuccessEnvelope(
        message="User updated.",
        data=AdminUpdateUserResponse(
            user_id=result.user_id,
            first_name=result.first_name,
            last_name=result.last_name,
        ),
    )


@router.delete(
    "/{user_id}",
    response_model=SuccessEnvelope[AdminDeleteUserResponse],
    operation_id="admin_delete_user",
)
async def admin_delete_user(
    user_id: str,
    current_user=Depends(get_current_user),
    use_case: AdminDeleteUserUseCase = Depends(get_admin_delete_user_use_case),
) -> SuccessEnvelope[AdminDeleteUserResponse]:
    result = await use_case.execute(
        AdminDeleteUserCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
        )
    )
    return SuccessEnvelope(
        message="User deleted.",
        data=AdminDeleteUserResponse(
            user_id=result.user_id,
            deleted_at=result.deleted_at.isoformat(),
        ),
    )


@router.post(
    "/{user_id}/activate",
    response_model=SuccessEnvelope[ActivateUserResponse],
    operation_id="activate_user",
)
async def activate_user(
    user_id: str,
    current_user=Depends(get_current_user),
    use_case: ActivateUserUseCase = Depends(get_activate_user_use_case),
) -> SuccessEnvelope[ActivateUserResponse]:
    result = await use_case.execute(
        ActivateUserCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
        )
    )
    return SuccessEnvelope(
        message="User activated.",
        data=ActivateUserResponse(user_id=result.user_id, status=result.status),
    )


@router.post(
    "/{user_id}/block",
    response_model=SuccessEnvelope[BlockUserResponse],
    operation_id="block_user",
)
async def block_user(
    user_id: str,
    payload: BlockUserRequest,
    current_user=Depends(get_current_user),
    use_case: BlockUserUseCase = Depends(get_block_user_use_case),
) -> SuccessEnvelope[BlockUserResponse]:
    result = await use_case.execute(
        BlockUserCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="User blocked.",
        data=BlockUserResponse(user_id=result.user_id, status=result.status),
    )


@router.post(
    "/{user_id}/roles",
    response_model=SuccessEnvelope[AssignRoleResponse],
    operation_id="assign_role",
)
async def assign_role(
    user_id: str,
    payload: AssignRoleRequest,
    current_user=Depends(get_current_user),
    use_case: AssignRoleUseCase = Depends(get_assign_role_use_case),
) -> SuccessEnvelope[AssignRoleResponse]:
    result = await use_case.execute(
        AssignRoleCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
            role_key=payload.role_key,
        )
    )
    return SuccessEnvelope(
        message="Role assigned.",
        data=AssignRoleResponse(
            user_role_id=result.user_role_id,
            user_id=result.user_id,
            role_id=result.role_id,
        ),
    )


@router.delete(
    "/{user_id}/roles/{role_key}",
    response_model=SuccessEnvelope[RemoveRoleResponse],
    operation_id="remove_role",
)
async def remove_role(
    user_id: str,
    role_key: str,
    current_user=Depends(get_current_user),
    use_case: RemoveRoleUseCase = Depends(get_remove_role_use_case),
) -> SuccessEnvelope[RemoveRoleResponse]:
    result = await use_case.execute(
        RemoveRoleCommand(
            actor_id=current_user.user_id,
            target_user_id=user_id,
            role_key=role_key,
        )
    )
    return SuccessEnvelope(
        message="Role removed.",
        data=RemoveRoleResponse(
            user_id=result.user_id,
            role_id=result.role_id,
            revoked_at=result.revoked_at.isoformat(),
        ),
    )


@router.post(
    "/roles/{role_id}/permissions",
    response_model=SuccessEnvelope[GrantPermissionResponse],
    operation_id="grant_permission",
)
async def grant_permission(
    role_id: str,
    payload: GrantPermissionRequest,
    current_user=Depends(get_current_user),
    use_case: GrantPermissionUseCase = Depends(get_grant_permission_use_case),
) -> SuccessEnvelope[GrantPermissionResponse]:
    result = await use_case.execute(
        GrantPermissionCommand(
            actor_id=current_user.user_id,
            role_id=role_id,
            permission_id=payload.permission_id,
        )
    )
    return SuccessEnvelope(
        message="Permission granted.",
        data=GrantPermissionResponse(
            role_id=result.role_id,
            permission_id=result.permission_id,
        ),
    )


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=SuccessEnvelope[RevokePermissionResponse],
    operation_id="revoke_permission",
)
async def revoke_permission(
    role_id: str,
    permission_id: str,
    current_user=Depends(get_current_user),
    use_case: RevokePermissionUseCase = Depends(get_revoke_permission_use_case),
) -> SuccessEnvelope[RevokePermissionResponse]:
    result = await use_case.execute(
        RevokePermissionCommand(
            actor_id=current_user.user_id,
            role_id=role_id,
            permission_id=permission_id,
        )
    )
    return SuccessEnvelope(
        message="Permission revoked.",
        data=RevokePermissionResponse(
            role_id=result.role_id,
            permission_id=result.permission_id,
        ),
    )

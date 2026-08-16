from datetime import datetime

import pytest

from app.application.iam.dto import (
    AdminCreateUserCommand,
    AdminDeleteUserCommand,
    AdminUpdateUserCommand,
)
from app.application.iam.use_cases.admin_create_user import AdminCreateUserUseCase
from app.application.iam.use_cases.admin_delete_user import AdminDeleteUserUseCase
from app.application.iam.use_cases.admin_update_user import AdminUpdateUserUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import UserRole
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import (
    CannotDeleteSelfError,
    DuplicateEmailError,
    LastAdminCannotBeDeletedError,
    UserNotFoundError,
)

NOW = datetime(2026, 8, 2)


class TestAdminCreateUserUseCase:
    def build(self, authorization_service, user_repo, password_hasher, id_generator, clock, uow):
        return AdminCreateUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            password_hasher=password_hasher,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

    async def test_create_user_requires_permission(
        self, authorization_service, user_repo, password_hasher, id_generator, clock, uow
    ):
        use_case = self.build(authorization_service, user_repo, password_hasher, id_generator, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                AdminCreateUserCommand(
                    actor_id="admin", email="jane@example.com", password="secret", first_name="Jane", last_name="Dev"
                )
            )

    async def test_create_active_user_succeeds(
        self, authorization_service, user_repo, password_hasher, id_generator, clock, uow
    ):
        authorization_service.grant("admin", "user.create")
        use_case = self.build(authorization_service, user_repo, password_hasher, id_generator, clock, uow)

        result = await use_case.execute(
            AdminCreateUserCommand(
                actor_id="admin",
                email="jane@example.com",
                password="secret",
                first_name="Jane",
                last_name="Dev",
            )
        )

        user = await user_repo.get_by_id(result.user_id)
        assert user.status == UserStatus.ACTIVE
        assert user.email.value == "jane@example.com"
        assert uow.committed is True

    async def test_duplicate_email_raises(
        self, authorization_service, user_repo, password_hasher, id_generator, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.create")
        await make_user(user_id="u1", email="jane@example.com")
        use_case = self.build(authorization_service, user_repo, password_hasher, id_generator, clock, uow)

        with pytest.raises(DuplicateEmailError):
            await use_case.execute(
                AdminCreateUserCommand(
                    actor_id="admin",
                    email="jane@example.com",
                    password="secret",
                    first_name="Jane",
                    last_name="Dev",
                )
            )


class TestAdminUpdateUserUseCase:
    def build(self, authorization_service, user_repo, uow) -> AdminUpdateUserUseCase:
        return AdminUpdateUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            uow=uow,
        )

    async def test_update_user_requires_permission(self, authorization_service, user_repo, uow, make_user):
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AdminUpdateUserCommand(actor_id="admin", target_user_id="u1", first_name="Jane"))

    async def test_update_identity_fields_succeeds(self, authorization_service, user_repo, uow, make_user):
        authorization_service.grant("admin", "user.update_any")
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, uow)

        result = await use_case.execute(
            AdminUpdateUserCommand(
                actor_id="admin",
                target_user_id="u1",
                first_name="Jane",
                last_name="Dev",
                phone="+1-555-0100",
            )
        )

        user = await user_repo.get_by_id("u1")
        assert result.first_name == "Jane"
        assert user.first_name == "Jane"
        assert user.last_name == "Dev"
        assert user.phone.value == "+1-555-0100"
        assert uow.committed is True

    async def test_update_unknown_user_raises(self, authorization_service, user_repo, uow):
        authorization_service.grant("admin", "user.update_any")
        use_case = self.build(authorization_service, user_repo, uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(AdminUpdateUserCommand(actor_id="admin", target_user_id="ghost", first_name="Jane"))


class TestAdminDeleteUserUseCase:
    def build(self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow):
        return AdminDeleteUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            user_role_repo=user_role_repo,
            role_repo=role_repo,
            clock=clock,
            uow=uow,
        )

    async def seed_admin_role(self, user_role_repo, role_repo, user_id: str, role_id: str = "role-admin"):
        await user_role_repo.add(
            UserRole(
                id=f"{user_id}-{role_id}",
                user_id=user_id,
                role_id=role_id,
                assigned_by_user_id="admin",
                assigned_at=NOW,
                created_at=NOW,
            )
        )

    async def test_delete_user_requires_permission(
        self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow, make_user
    ):
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, user_role_repo, role_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AdminDeleteUserCommand(actor_id="admin", target_user_id="u1"))

    async def test_cannot_delete_self(
        self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.delete")
        await make_user(user_id="admin")
        use_case = self.build(authorization_service, user_repo, user_role_repo, role_repo, clock, uow)

        with pytest.raises(CannotDeleteSelfError):
            await use_case.execute(AdminDeleteUserCommand(actor_id="admin", target_user_id="admin"))

    async def test_soft_deletes_customer(
        self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.delete")
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, user_role_repo, role_repo, clock, uow)

        result = await use_case.execute(AdminDeleteUserCommand(actor_id="admin", target_user_id="u1"))

        user = await user_repo.get_by_id("u1")
        assert user.deleted_at is not None
        assert result.deleted_at == user.deleted_at
        assert uow.committed is True

    async def test_last_admin_cannot_be_deleted(
        self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin-2", "user.delete")
        await make_user(user_id="admin-1")
        await self.seed_admin_role(user_role_repo, role_repo, "admin-1")
        use_case = self.build(authorization_service, user_repo, user_role_repo, role_repo, clock, uow)

        with pytest.raises(LastAdminCannotBeDeletedError):
            await use_case.execute(AdminDeleteUserCommand(actor_id="admin-2", target_user_id="admin-1"))

    async def test_admin_can_be_deleted_when_another_admin_exists(
        self, authorization_service, user_repo, user_role_repo, role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin-2", "user.delete")
        await make_user(user_id="admin-1")
        await make_user(user_id="admin-2")
        await self.seed_admin_role(user_role_repo, role_repo, "admin-1")
        await self.seed_admin_role(user_role_repo, role_repo, "admin-2")
        use_case = self.build(authorization_service, user_repo, user_role_repo, role_repo, clock, uow)

        result = await use_case.execute(AdminDeleteUserCommand(actor_id="admin-2", target_user_id="admin-1"))

        assert (await user_repo.get_by_id("admin-1")).deleted_at is not None
        assert result.user_id == "admin-1"

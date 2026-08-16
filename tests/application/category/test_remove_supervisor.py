from datetime import UTC, datetime

import pytest

from app.application.category.dto import AssignSupervisorCommand, RemoveSupervisorCommand
from app.application.category.use_cases.assign_supervisor import AssignSupervisorUseCase
from app.application.category.use_cases.remove_supervisor import RemoveSupervisorUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.category.entities import CategorySupervisor
from app.domain.category.exceptions import SupervisorAssignmentNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_remove(authorization_service, category_supervisor_repo, clock, uow) -> RemoveSupervisorUseCase:
    return RemoveSupervisorUseCase(
        authorization_service=authorization_service,
        category_supervisor_repo=category_supervisor_repo,
        clock=clock,
        uow=uow,
    )


class TestRemoveSupervisorUseCase:
    async def test_remove_supervisor_succeeds(
        self, authorization_service, category_supervisor_repo, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.remove_supervisor")
        await category_supervisor_repo.add(
            CategorySupervisor(
                id="link-1",
                category_id="cat-1",
                supervisor_user_id="sup-1",
                assigned_by_user_id="admin",
                is_primary=True,
                is_active=True,
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        use_case = build_remove(authorization_service, category_supervisor_repo, clock, uow)

        result = await use_case.execute(
            RemoveSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )

        assert result.revoked_at == NOW
        assert (await category_supervisor_repo.is_supervisor_of("sup-1", "cat-1")) is False

    async def test_remove_supervisor_requires_permission(
        self, authorization_service, category_supervisor_repo, clock, uow
    ):
        use_case = build_remove(authorization_service, category_supervisor_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                RemoveSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
            )

    async def test_remove_inactive_supervisor_raises(self, authorization_service, category_supervisor_repo, clock, uow):
        authorization_service.grant("admin", "category.remove_supervisor")
        use_case = build_remove(authorization_service, category_supervisor_repo, clock, uow)

        with pytest.raises(SupervisorAssignmentNotFoundError):
            await use_case.execute(
                RemoveSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="ghost")
            )

    async def test_removing_primary_promotes_next_active_supervisor(
        self, authorization_service, category_supervisor_repo, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.remove_supervisor")
        await make_category(category_id="cat-1")
        await category_supervisor_repo.add(
            CategorySupervisor(
                id="link-1",
                category_id="cat-1",
                supervisor_user_id="sup-1",
                assigned_by_user_id="admin",
                is_primary=True,
                is_active=True,
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        await category_supervisor_repo.add(
            CategorySupervisor(
                id="link-2",
                category_id="cat-1",
                supervisor_user_id="sup-2",
                assigned_by_user_id="admin",
                is_primary=False,
                is_active=True,
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        use_case = build_remove(authorization_service, category_supervisor_repo, clock, uow)

        await use_case.execute(
            RemoveSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )

        remaining = await category_supervisor_repo.list_active_supervisors("cat-1")
        assert len(remaining) == 1
        assert remaining[0].supervisor_user_id == "sup-2"
        assert remaining[0].is_primary is True


class TestAssignAndRemoveFlow:
    async def test_assign_then_remove_flow(
        self,
        authorization_service,
        category_repo,
        category_supervisor_repo,
        user_repo,
        id_generator,
        clock,
        uow,
        make_category,
        make_user,
    ):
        authorization_service.grant("admin", "category.assign_supervisor")
        authorization_service.grant("admin", "category.remove_supervisor")
        await make_category(category_id="cat-1")
        await make_user(user_id="sup-1")
        assign = AssignSupervisorUseCase(
            authorization_service,
            category_repo,
            category_supervisor_repo,
            user_repo,
            id_generator,
            clock,
            uow,
        )
        remove = build_remove(authorization_service, category_supervisor_repo, clock, uow)

        assign_result = await assign.execute(
            AssignSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )
        remove_result = await remove.execute(
            RemoveSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )

        assert assign_result.supervisor_user_id == "sup-1"
        assert remove_result.revoked_at == NOW
        assert (await category_supervisor_repo.is_supervisor_of("sup-1", "cat-1")) is False

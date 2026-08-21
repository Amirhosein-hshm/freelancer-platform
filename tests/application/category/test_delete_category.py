import pytest

from app.application.category.dto import DeleteCategoryCommand
from app.application.category.use_cases.delete_category import DeleteCategoryUseCase
from app.domain.category.exceptions import (
    CategoryHasActiveReferencesError,
    CategoryNotFoundError,
)
from app.domain.project.enums import ProjectStatus


def build_use_case(authorization_service, category_repo, project_repo, clock, uow) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(
        authorization_service=authorization_service,
        category_repo=category_repo,
        project_repo=project_repo,
        clock=clock,
        uow=uow,
    )


class TestDeleteCategoryUseCase:
    async def test_delete_soft_deletes_category(
        self, authorization_service, category_repo, project_repo, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1")
        use_case = build_use_case(authorization_service, category_repo, project_repo, clock, uow)

        result = await use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="cat-1"))

        assert result.category_id == "cat-1"
        # Soft-deleted categories must no longer surface on ANY read path.
        with pytest.raises(CategoryNotFoundError):
            await category_repo.get_by_id("cat-1")
        assert await category_repo.list_active() == []

    async def test_delete_unknown_category_raises(self, authorization_service, category_repo, project_repo, clock, uow):
        authorization_service.grant("admin", "category.manage")
        use_case = build_use_case(authorization_service, category_repo, project_repo, clock, uow)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="ghost"))

    async def test_delete_category_with_children_is_blocked(
        self, authorization_service, category_repo, project_repo, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-parent")
        await make_category(category_id="cat-child", parent_category_id="cat-parent", slug="child")
        use_case = build_use_case(authorization_service, category_repo, project_repo, clock, uow)

        with pytest.raises(CategoryHasActiveReferencesError) as exc:
            await use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="cat-parent"))

        assert exc.value.children_count == 1
        assert exc.value.active_projects_count == 0

    async def test_delete_category_with_active_projects_is_blocked(
        self,
        authorization_service,
        category_repo,
        project_repo,
        clock,
        uow,
        make_category,
        make_project,
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1")
        await make_project(project_id="proj-1", category_id="cat-1", status=ProjectStatus.PUBLISHED)
        use_case = build_use_case(authorization_service, category_repo, project_repo, clock, uow)

        with pytest.raises(CategoryHasActiveReferencesError) as exc:
            await use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="cat-1"))

        assert exc.value.children_count == 0
        assert exc.value.active_projects_count == 1

    async def test_delete_category_with_terminal_project_allowed(
        self,
        authorization_service,
        category_repo,
        project_repo,
        clock,
        uow,
        make_category,
        make_project,
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1")
        await make_project(project_id="proj-1", category_id="cat-1", status=ProjectStatus.COMPLETED)
        use_case = build_use_case(authorization_service, category_repo, project_repo, clock, uow)

        result = await use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="cat-1"))

        assert result.category_id == "cat-1"

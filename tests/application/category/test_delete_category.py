import pytest

from app.application.category.dto import DeleteCategoryCommand
from app.application.category.use_cases.delete_category import DeleteCategoryUseCase
from app.domain.category.exceptions import CategoryNotFoundError


def build_use_case(authorization_service, category_repo, clock, uow) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(
        authorization_service=authorization_service,
        category_repo=category_repo,
        clock=clock,
        uow=uow,
    )


class TestDeleteCategoryUseCase:
    def test_delete_soft_deletes_category(
        self, authorization_service, category_repo, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        make_category(category_id="cat-1")
        use_case = build_use_case(authorization_service, category_repo, clock, uow)

        result = use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="cat-1"))

        assert result.category_id == "cat-1"
        category = category_repo.get_by_id("cat-1")
        assert category.deleted_at == clock.now()
        assert category_repo.list_active() == []

    def test_delete_unknown_category_raises(self, authorization_service, category_repo, clock, uow):
        authorization_service.grant("admin", "category.manage")
        use_case = build_use_case(authorization_service, category_repo, clock, uow)

        with pytest.raises(CategoryNotFoundError):
            use_case.execute(DeleteCategoryCommand(actor_id="admin", category_id="ghost"))

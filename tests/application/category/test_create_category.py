import pytest

from app.application.category.dto import CreateCategoryCommand
from app.application.category.use_cases.create_category import CreateCategoryUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.category.exceptions import DuplicateCategorySlugError


def build_use_case(
    authorization_service, category_repo, id_generator, clock, uow
) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(
        authorization_service=authorization_service,
        category_repo=category_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestCreateCategoryUseCase:
    def test_create_category_succeeds(
        self, authorization_service, category_repo, id_generator, clock, uow
    ):
        authorization_service.grant("admin", "category.manage")
        use_case = build_use_case(authorization_service, category_repo, id_generator, clock, uow)

        result = use_case.execute(
            CreateCategoryCommand(
                actor_id="admin", name="Backend", slug="backend", category_key="backend"
            )
        )

        assert result.name == "Backend"
        assert result.slug == "backend"
        assert result.is_active is True
        assert category_repo.get_by_slug("backend").id == result.category_id
        assert uow.committed is True

    def test_create_duplicate_slug_raises(
        self, authorization_service, category_repo, id_generator, clock, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        make_category(category_id="cat-1", slug="taken")
        use_case = build_use_case(authorization_service, category_repo, id_generator, clock, uow)

        with pytest.raises(DuplicateCategorySlugError):
            use_case.execute(
                CreateCategoryCommand(
                    actor_id="admin", name="Other", slug="taken", category_key="other"
                )
            )

    def test_create_missing_fields_raises_validation(
        self, authorization_service, category_repo, id_generator, clock, uow
    ):
        authorization_service.grant("admin", "category.manage")
        use_case = build_use_case(authorization_service, category_repo, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            use_case.execute(
                CreateCategoryCommand(actor_id="admin", name="", slug="", category_key="")
            )

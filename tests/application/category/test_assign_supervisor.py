import pytest

from app.application.category.dto import AssignSupervisorCommand
from app.application.category.use_cases.assign_supervisor import AssignSupervisorUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.category.exceptions import CategoryNotFoundError, SupervisorAlreadyAssignedError


def build_use_case(
    authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
) -> AssignSupervisorUseCase:
    return AssignSupervisorUseCase(
        authorization_service=authorization_service,
        category_repo=category_repo,
        category_supervisor_repo=category_supervisor_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAssignSupervisorUseCase:
    def test_assign_supervisor_succeeds(
        self,
        authorization_service,
        category_repo,
        category_supervisor_repo,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("admin", "category.assign_supervisor")
        make_category(category_id="cat-1")
        use_case = build_use_case(
            authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
        )

        result = use_case.execute(
            AssignSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )

        assert result.supervisor_user_id == "sup-1"
        assert category_supervisor_repo.is_supervisor_of("sup-1", "cat-1") is True
        assert uow.committed is True

    def test_assign_supervisor_requires_permission(
        self,
        authorization_service,
        category_repo,
        category_supervisor_repo,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        make_category(category_id="cat-1")
        use_case = build_use_case(
            authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                AssignSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
            )

    def test_assign_duplicate_supervisor_raises(
        self,
        authorization_service,
        category_repo,
        category_supervisor_repo,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("admin", "category.assign_supervisor")
        make_category(category_id="cat-1")
        first = AssignSupervisorUseCase(
            authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
        )
        first.execute(
            AssignSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
        )
        use_case = build_use_case(
            authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
        )

        with pytest.raises(SupervisorAlreadyAssignedError):
            use_case.execute(
                AssignSupervisorCommand(actor_id="admin", category_id="cat-1", supervisor_user_id="sup-1")
            )

    def test_assign_unknown_category_raises(
        self,
        authorization_service,
        category_repo,
        category_supervisor_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "category.assign_supervisor")
        use_case = build_use_case(
            authorization_service, category_repo, category_supervisor_repo, id_generator, clock, uow
        )

        with pytest.raises(CategoryNotFoundError):
            use_case.execute(
                AssignSupervisorCommand(actor_id="admin", category_id="ghost", supervisor_user_id="sup-1")
            )

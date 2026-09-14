import pytest

from app.application.project.dto import (
    CancelProjectCommand,
    PublishProjectCommand,
    StartProjectCommand,
)
from app.application.project.use_cases.cancel_project import CancelProjectUseCase
from app.application.project.use_cases.publish_project import PublishProjectUseCase
from app.application.project.use_cases.start_project import StartProjectUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.project.enums import ProjectStatus


class TestPublishProjectUseCase:
    async def test_publish_goes_straight_to_collecting(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        authorization_service.grant("customer-1", "project.manage_own")
        await make_project(project_id="project-1", customer_user_id="customer-1")
        use_case = PublishProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(PublishProjectCommand(actor_id="customer-1", project_id="project-1"))

        assert result.status == ProjectStatus.COLLECTING_APPLICATIONS
        history = await status_history_repo.list_by_project("project-1")
        assert [h.from_status.value for h in history] == ["draft", "published"]
        assert [h.to_status.value for h in history] == ["published", "collecting_applications"]
        assert uow.committed is True

    async def test_non_owner_raises(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        await make_project(project_id="project-1", customer_user_id="customer-1")
        use_case = PublishProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(PublishProjectCommand(actor_id="intruder", project_id="project-1"))


class TestCancelProjectUseCase:
    async def test_cancel_records_reason(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        authorization_service.grant("customer-1", "project.manage_own")
        await make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS)
        use_case = CancelProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(
            CancelProjectCommand(actor_id="customer-1", project_id="project-1", reason="Bailed")
        )

        assert result.status == ProjectStatus.CANCELLED
        history = (await status_history_repo.list_by_project("project-1"))[0]
        assert history.from_status == ProjectStatus.IN_PROGRESS
        assert history.to_status == ProjectStatus.CANCELLED
        assert history.reason == "Bailed"

    async def test_non_owner_raises(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        await make_project(project_id="project-1", customer_user_id="customer-1")
        use_case = CancelProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(CancelProjectCommand(actor_id="intruder", project_id="project-1", reason="x"))


class TestStartProjectUseCase:
    async def test_start_sets_in_progress(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        authorization_service.grant("customer-1", "project.manage_own")
        await make_project(project_id="project-1", status=ProjectStatus.ASSIGNED, selected_application_id="app-1")
        use_case = StartProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(StartProjectCommand(actor_id="customer-1", project_id="project-1"))

        assert result.status == ProjectStatus.IN_PROGRESS
        assert (await project_repo.get_by_id("project-1")).start_at == await clock.now()

    async def test_non_owner_raises(
        self,
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        await make_project(project_id="project-1", status=ProjectStatus.ASSIGNED, customer_user_id="customer-1")
        use_case = StartProjectUseCase(
            authorization_service=authorization_service,
            project_repo=project_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(StartProjectCommand(actor_id="intruder", project_id="project-1"))

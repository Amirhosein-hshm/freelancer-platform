import pytest

from app.application.form.dto import DeleteFormTemplateCommand
from app.application.form.use_cases.delete_form_template import DeleteFormTemplateUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateHasActiveReferencesError, FormTemplateNotFoundError
from app.domain.project.enums import ProjectStatus


def build_use_case(authorization_service, template_repo, project_repo, uow):
    return DeleteFormTemplateUseCase(
        authorization_service=authorization_service,
        template_repo=template_repo,
        project_repo=project_repo,
        uow=uow,
    )


class TestDeleteFormTemplateUseCase:
    async def test_delete_draft_template_succeeds(
        self, authorization_service, template_repo, project_repo, uow, make_template
    ):
        authorization_service.grant("admin", "form.manage")
        await make_template(template_id="template-1")
        use_case = build_use_case(
            authorization_service, template_repo, project_repo, uow
        )

        result = await use_case.execute(
            DeleteFormTemplateCommand(actor_id="admin", template_id="template-1")
        )

        assert result.template_id == "template-1"
        with pytest.raises(FormTemplateNotFoundError):
            await template_repo.get_by_id("template-1")

    async def test_delete_requires_permission(
        self, authorization_service, template_repo, project_repo, uow, make_template
    ):
        await make_template(template_id="template-1")
        use_case = build_use_case(
            authorization_service, template_repo, project_repo, uow
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                DeleteFormTemplateCommand(actor_id="admin", template_id="template-1")
            )

    async def test_delete_published_template_is_blocked(
        self, authorization_service, template_repo, project_repo, uow, make_template
    ):
        authorization_service.grant("admin", "form.manage")
        await make_template(
            template_id="template-1", status=FormTemplateStatus.PUBLISHED
        )
        use_case = build_use_case(
            authorization_service, template_repo, project_repo, uow
        )

        with pytest.raises(FormTemplateHasActiveReferencesError):
            await use_case.execute(
                DeleteFormTemplateCommand(actor_id="admin", template_id="template-1")
            )

    async def test_delete_referenced_template_is_blocked(
        self,
        authorization_service,
        template_repo,
        project_repo,
        uow,
        make_template,
        make_project,
    ):
        authorization_service.grant("admin", "form.manage")
        await make_template(template_id="template-1")
        await make_project(
            project_id="proj-1",
            form_template_id="template-1",
            status=ProjectStatus.PUBLISHED,
        )
        use_case = build_use_case(
            authorization_service, template_repo, project_repo, uow
        )

        with pytest.raises(FormTemplateHasActiveReferencesError):
            await use_case.execute(
                DeleteFormTemplateCommand(actor_id="admin", template_id="template-1")
            )

    async def test_delete_template_with_terminal_project_allowed(
        self,
        authorization_service,
        template_repo,
        project_repo,
        uow,
        make_template,
        make_project,
    ):
        authorization_service.grant("admin", "form.manage")
        await make_template(template_id="template-1")
        await make_project(
            project_id="proj-1",
            form_template_id="template-1",
            status=ProjectStatus.COMPLETED,
        )
        use_case = build_use_case(
            authorization_service, template_repo, project_repo, uow
        )

        result = await use_case.execute(
            DeleteFormTemplateCommand(actor_id="admin", template_id="template-1")
        )

        assert result.template_id == "template-1"

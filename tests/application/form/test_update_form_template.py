import pytest

from app.application.form.dto import UpdateFormTemplateCommand
from app.application.form.use_cases.update_form_template import UpdateFormTemplateUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.form.enums import FormTemplateStatus
from app.domain.shared.exceptions import InvalidStateTransitionError


def build_use_case(template_repo, authorization_service) -> UpdateFormTemplateUseCase:
    return UpdateFormTemplateUseCase(template_repo=template_repo, authorization_service=authorization_service)


class TestUpdateFormTemplateUseCase:
    async def test_update_name_of_draft(self, template_repo, make_template, authorization_service):
        await make_template(template_id="template-1")
        authorization_service.grant("admin", "form.manage")
        use_case = build_use_case(template_repo, authorization_service)

        result = await use_case.execute(
            UpdateFormTemplateCommand(actor_id="admin", template_id="template-1", name="New Name")
        )

        assert result.name == "New Name"
        assert (await template_repo.get_by_id("template-1")).name == "New Name"

    async def test_update_published_raises(self, template_repo, make_template, authorization_service):
        await make_template(template_id="template-1", status=FormTemplateStatus.PUBLISHED)
        authorization_service.grant("admin", "form.manage")
        use_case = build_use_case(template_repo, authorization_service)

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                UpdateFormTemplateCommand(actor_id="admin", template_id="template-1", name="New Name")
            )

    async def test_empty_name_raises_validation(self, template_repo, make_template, authorization_service):
        await make_template(template_id="template-1")
        authorization_service.grant("admin", "form.manage")
        use_case = build_use_case(template_repo, authorization_service)

        with pytest.raises(ValidationError):
            await use_case.execute(UpdateFormTemplateCommand(actor_id="admin", template_id="template-1", name="  "))

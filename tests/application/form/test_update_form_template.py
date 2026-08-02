import pytest

from app.application.form.dto import UpdateFormTemplateCommand
from app.application.form.use_cases.update_form_template import UpdateFormTemplateUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.form.enums import FormTemplateStatus
from app.domain.shared.exceptions import InvalidStateTransitionError


def build_use_case(template_repo) -> UpdateFormTemplateUseCase:
    return UpdateFormTemplateUseCase(template_repo=template_repo)


class TestUpdateFormTemplateUseCase:
    def test_update_name_of_draft(self, template_repo, make_template):
        make_template(template_id="template-1")
        use_case = build_use_case(template_repo)

        result = use_case.execute(
            UpdateFormTemplateCommand(template_id="template-1", name="New Name")
        )

        assert result.name == "New Name"
        assert template_repo.get_by_id("template-1").name == "New Name"

    def test_update_published_raises(self, template_repo, make_template):
        make_template(template_id="template-1", status=FormTemplateStatus.PUBLISHED)
        use_case = build_use_case(template_repo)

        with pytest.raises(InvalidStateTransitionError):
            use_case.execute(
                UpdateFormTemplateCommand(template_id="template-1", name="New Name")
            )

    def test_empty_name_raises_validation(self, template_repo, make_template):
        make_template(template_id="template-1")
        use_case = build_use_case(template_repo)

        with pytest.raises(ValidationError):
            use_case.execute(UpdateFormTemplateCommand(template_id="template-1", name="  "))

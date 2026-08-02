import pytest

from app.application.form.dto import CreateFormTemplateCommand
from app.application.form.use_cases.create_form_template import CreateFormTemplateUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.form.enums import FormTemplateStatus


def build_use_case(template_repo, id_generator, clock, uow) -> CreateFormTemplateUseCase:
    return CreateFormTemplateUseCase(
        template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
    )


class TestCreateFormTemplateUseCase:
    def test_create_draft_version_one(self, template_repo, id_generator, clock, uow):
        use_case = build_use_case(template_repo, id_generator, clock, uow)

        result = use_case.execute(
            CreateFormTemplateCommand(
                category_id="cat-1", name="Project Form", template_key="project-form"
            )
        )

        template = template_repo.get_by_id(result.template_id)
        assert result.version_no == 1
        assert result.status == FormTemplateStatus.DRAFT
        assert template.fields == []
        assert template.category_id == "cat-1"
        assert uow.committed is True

    def test_missing_fields_raises_validation(self, template_repo, id_generator, clock, uow):
        use_case = build_use_case(template_repo, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            use_case.execute(
                CreateFormTemplateCommand(category_id="cat-1", name="", template_key="")
            )

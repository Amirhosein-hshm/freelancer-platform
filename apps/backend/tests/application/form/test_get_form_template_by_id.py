import pytest

from app.application.form.use_cases.get_form_template_by_id import (
    GetFormTemplateByIdQuery,
    GetFormTemplateByIdUseCase,
)
from app.domain.form.exceptions import FormTemplateNotFoundError


class TestGetFormTemplateByIdUseCase:
    def build(self, template_repo):
        return GetFormTemplateByIdUseCase(template_repo=template_repo)

    async def test_get_template_by_id(self, template_repo, make_template):
        await make_template(template_id="template-1", name="My Form")
        use_case = self.build(template_repo)

        result = await use_case.execute(GetFormTemplateByIdQuery(template_id="template-1"))

        assert result.template_id == "template-1"
        assert result.name == "My Form"

    async def test_get_unknown_template_raises(self, template_repo):
        use_case = self.build(template_repo)

        with pytest.raises(FormTemplateNotFoundError):
            await use_case.execute(GetFormTemplateByIdQuery(template_id="ghost"))

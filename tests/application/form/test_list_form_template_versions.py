from app.application.form.use_cases.list_form_template_versions import (
    ListFormTemplateVersionsQuery,
    ListFormTemplateVersionsUseCase,
)
from app.domain.form.enums import FormTemplateStatus


class TestListFormTemplateVersionsUseCase:
    def build(self, template_repo):
        return ListFormTemplateVersionsUseCase(template_repo=template_repo)

    async def test_list_versions_for_template_key(
        self, template_repo, make_template
    ):
        await make_template(
            template_id="template-1",
            category_id="cat-1",
            template_key="project-form",
            version_no=1,
        )
        await make_template(
            template_id="template-2",
            category_id="cat-1",
            template_key="project-form",
            version_no=2,
            status=FormTemplateStatus.PUBLISHED,
        )
        await make_template(
            template_id="template-3",
            category_id="cat-1",
            template_key="other-form",
            version_no=1,
        )
        use_case = self.build(template_repo)

        result = await use_case.execute(
            ListFormTemplateVersionsQuery(template_id="template-1")
        )

        assert {v.template_id for v in result.versions} == {"template-1", "template-2"}

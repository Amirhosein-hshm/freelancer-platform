import pytest

from app.application.project.dto import FormValueInput
from app.application.project.form_validation import validate_form_values
from app.application.shared.exceptions import FormValidationError
from app.domain.form.entities import FormField, FormFieldOption, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from tests.application.project.conftest import NOW


def build_template(
    field_type: FormFieldType, *, required: bool = True, options: list[FormFieldOption] | None = None
) -> FormTemplate:
    return FormTemplate(
        id="template-1",
        category_id="cat-1",
        template_key="project-form",
        name="Project Form",
        version_no=1,
        status=FormTemplateStatus.PUBLISHED,
        is_active=True,
        published_by_user_id="admin-1",
        published_at=NOW,
        fields=[
            FormField(
                id="field-1",
                field_key="f1",
                label="Field",
                description=None,
                field_type=field_type,
                is_required=required,
                is_repeatable=False,
                is_unique=False,
                sort_order=0,
                validation_rules=None,
                options=options or [],
                created_at=NOW,
            )
        ],
        created_at=NOW,
    )


def build_values(*raw: str) -> list[FormValueInput]:
    return [FormValueInput(field_id="field-1", value=value) for value in raw]


class TestValidateFormValues:
    def test_unknown_field_id_raises(self):
        template = build_template(FormFieldType.TEXT)
        with pytest.raises(FormValidationError, match="Unknown field_id"):
            validate_form_values(template, [FormValueInput(field_id="nope", value="x")])

    def test_missing_required_field_raises(self):
        template = build_template(FormFieldType.TEXT, required=True)
        with pytest.raises(FormValidationError, match="required"):
            validate_form_values(template, [FormValueInput(field_id="field-1", value=" ")])

    def test_missing_optional_field_is_skipped(self):
        template = build_template(FormFieldType.NUMBER, required=False)
        validate_form_values(template, [])
        validate_form_values(template, [FormValueInput(field_id="field-1", value=" ")])

    @pytest.mark.parametrize("value", ["12", "-5", "0"])
    def test_number_valid(self, value):
        validate_form_values(build_template(FormFieldType.NUMBER), build_values(value))

    @pytest.mark.parametrize("value", ["abc", "1.5"])
    def test_number_invalid(self, value):
        with pytest.raises(FormValidationError, match="whole number"):
            validate_form_values(build_template(FormFieldType.NUMBER), build_values(value))

    @pytest.mark.parametrize("value", ["10.5", "-1.25", "1000"])
    def test_decimal_valid(self, value):
        validate_form_values(build_template(FormFieldType.DECIMAL), build_values(value))

    @pytest.mark.parametrize("value", ["abc", "1..5"])
    def test_decimal_invalid(self, value):
        with pytest.raises(FormValidationError, match="decimal"):
            validate_form_values(build_template(FormFieldType.DECIMAL), build_values(value))

    @pytest.mark.parametrize("value", ["true", "false", "yes", "no", "on", "off", "1", "0"])
    def test_boolean_valid(self, value):
        validate_form_values(build_template(FormFieldType.BOOLEAN), build_values(value))

    @pytest.mark.parametrize("value", ["maybe", "TRUE_FALSE", "2"])
    def test_boolean_invalid(self, value):
        with pytest.raises(FormValidationError, match="true or false"):
            validate_form_values(build_template(FormFieldType.BOOLEAN), build_values(value))

    @pytest.mark.parametrize("value", ["2026-08-02", "2000-02-29"])
    def test_date_valid(self, value):
        validate_form_values(build_template(FormFieldType.DATE), build_values(value))

    @pytest.mark.parametrize("value", ["08/02/2026", "2026-13-01", "not-a-date"])
    def test_date_invalid(self, value):
        with pytest.raises(FormValidationError, match="date"):
            validate_form_values(build_template(FormFieldType.DATE), build_values(value))

    def test_datetime_valid(self):
        validate_form_values(
            build_template(FormFieldType.DATETIME), build_values("2026-08-02T10:30:00")
        )

    @pytest.mark.parametrize("value", ["2026-13-01", "not-a-date"])
    def test_datetime_invalid(self, value):
        with pytest.raises(FormValidationError, match="datetime"):
            validate_form_values(build_template(FormFieldType.DATETIME), build_values(value))

    @pytest.mark.parametrize("value", ["user@example.com", "a.b+c@sub.example.org"])
    def test_email_valid(self, value):
        validate_form_values(build_template(FormFieldType.EMAIL), build_values(value))

    @pytest.mark.parametrize("value", ["user@", "a@b", "plainaddress"])
    def test_email_invalid(self, value):
        with pytest.raises(FormValidationError, match="email"):
            validate_form_values(build_template(FormFieldType.EMAIL), build_values(value))

    @pytest.mark.parametrize("value", ["http://example.com", "https://example.org"])
    def test_url_valid(self, value):
        validate_form_values(build_template(FormFieldType.URL), build_values(value))

    def test_url_invalid(self):
        with pytest.raises(FormValidationError, match="URL"):
            validate_form_values(build_template(FormFieldType.URL), build_values("ftp://x"))

    def _make_options(self) -> list[FormFieldOption]:
        return [
            FormFieldOption(
                id="opt-1",
                option_key="small",
                label="Small",
                value="small",
                sort_order=0,
                is_active=True,
                created_at=NOW,
            ),
            FormFieldOption(
                id="opt-2",
                option_key="large",
                label="Large",
                value="large",
                sort_order=1,
                is_active=True,
                created_at=NOW,
            ),
            FormFieldOption(
                id="opt-3",
                option_key="hidden",
                label="Hidden",
                value="hidden",
                sort_order=2,
                is_active=False,
                created_at=NOW,
            ),
        ]

    def test_select_valid(self):
        template = build_template(
            FormFieldType.SELECT, options=self._make_options()
        )
        validate_form_values(template, build_values("small"))

    def test_select_invalid_option_raises(self):
        template = build_template(
            FormFieldType.SELECT, options=self._make_options()
        )
        with pytest.raises(FormValidationError, match="available options"):
            validate_form_values(template, build_values("medium"))

    def test_select_inactive_option_raises(self):
        template = build_template(
            FormFieldType.SELECT, options=self._make_options()
        )
        with pytest.raises(FormValidationError, match="available options"):
            validate_form_values(template, build_values("hidden"))

    def test_multi_select_valid(self):
        template = build_template(
            FormFieldType.MULTI_SELECT, options=self._make_options()
        )
        validate_form_values(template, build_values("small, large"))

    def test_multi_select_invalid_item_raises(self):
        template = build_template(
            FormFieldType.MULTI_SELECT, options=self._make_options()
        )
        with pytest.raises(FormValidationError, match="not available"):
            validate_form_values(template, build_values("small, medium"))

    def test_multi_select_empty_item_raises(self):
        template = build_template(
            FormFieldType.MULTI_SELECT, options=self._make_options()
        )
        with pytest.raises(FormValidationError, match="empty option"):
            validate_form_values(template, build_values("small,,large"))

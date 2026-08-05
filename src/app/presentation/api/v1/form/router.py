from fastapi import APIRouter, Depends

from app.application.form.dto import (
    AddFieldCommand,
    AddFieldOptionCommand,
    CreateFormTemplateCommand,
    GetFormTemplateQuery,
    PublishFormTemplateCommand,
    RemoveFieldCommand,
    UpdateFieldCommand,
    UpdateFormTemplateCommand,
)
from app.application.form.use_cases.add_field import AddFieldUseCase
from app.application.form.use_cases.add_field_option import AddFieldOptionUseCase
from app.application.form.use_cases.create_form_template import CreateFormTemplateUseCase
from app.application.form.use_cases.get_form_template import GetFormTemplateUseCase
from app.application.form.use_cases.publish_form_template import PublishFormTemplateUseCase
from app.application.form.use_cases.remove_field import RemoveFieldUseCase
from app.application.form.use_cases.update_field import UpdateFieldUseCase
from app.application.form.use_cases.update_form_template import UpdateFormTemplateUseCase
from app.presentation.api.v1.form.schemas import (
    AddFieldOptionRequest,
    AddFieldOptionResponse,
    AddFieldRequest,
    AddFieldResponse,
    CreateFormTemplateRequest,
    CreateFormTemplateResponse,
    FormFieldOptionResponse,
    FormFieldResponse,
    FormTemplateResponse,
    PublishFormTemplateResponse,
    RemoveFieldResponse,
    UpdateFieldRequest,
    UpdateFieldResponse,
    UpdateFormTemplateRequest,
    UpdateFormTemplateResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_add_field_option_use_case,
    get_add_field_use_case,
    get_create_form_template_use_case,
    get_get_form_template_use_case,
    get_publish_form_template_use_case,
    get_remove_field_use_case,
    get_update_field_use_case,
    get_update_form_template_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/form-templates", tags=["Form"])


def _option_response(result) -> FormFieldOptionResponse:
    return FormFieldOptionResponse(
        option_id=result.option_id,
        option_key=result.option_key,
        label=result.label,
        value=result.value,
        sort_order=result.sort_order,
        is_active=result.is_active,
    )


def _field_response(result) -> FormFieldResponse:
    return FormFieldResponse(
        field_id=result.field_id,
        field_key=result.field_key,
        label=result.label,
        description=result.description,
        field_type=result.field_type.value,
        is_required=result.is_required,
        is_repeatable=result.is_repeatable,
        is_unique=result.is_unique,
        sort_order=result.sort_order,
        validation_rules=result.validation_rules,
        is_active=result.is_active,
        options=[_option_response(o) for o in result.options],
    )


def _template_response(result) -> FormTemplateResponse:
    return FormTemplateResponse(
        template_id=result.template_id,
        category_id=result.category_id,
        template_key=result.template_key,
        name=result.name,
        version_no=result.version_no,
        status=result.status.value,
        is_active=result.is_active,
        published_at=result.published_at.isoformat() if result.published_at else None,
        fields=[_field_response(f) for f in result.fields],
    )


@router.post(
    "",
    response_model=SuccessEnvelope[CreateFormTemplateResponse],
    status_code=201,
    operation_id="create_form_template",
)
async def create_form_template(
    payload: CreateFormTemplateRequest,
    current_user=Depends(get_current_user),
    use_case: CreateFormTemplateUseCase = Depends(get_create_form_template_use_case),
) -> SuccessEnvelope[CreateFormTemplateResponse]:
    result = await use_case.execute(
        CreateFormTemplateCommand(
            actor_id=current_user.user_id,
            category_id=payload.category_id,
            name=payload.name,
            template_key=payload.template_key,
        )
    )
    return SuccessEnvelope(
        message="Form template created.",
        data=CreateFormTemplateResponse(
            template_id=result.template_id,
            version_no=result.version_no,
            status=result.status.value,
        ),
    )


@router.get(
    "/{template_id}",
    response_model=SuccessEnvelope[FormTemplateResponse],
    operation_id="get_form_template",
)
async def get_form_template(
    template_id: str,
    current_user=Depends(get_current_user),
    use_case: GetFormTemplateUseCase = Depends(get_get_form_template_use_case),
) -> SuccessEnvelope[FormTemplateResponse]:
    result = await use_case.execute(GetFormTemplateQuery(category_id=template_id))
    return SuccessEnvelope(message="Form template.", data=_template_response(result))


@router.patch(
    "/{template_id}",
    response_model=SuccessEnvelope[UpdateFormTemplateResponse],
    operation_id="update_form_template",
)
async def update_form_template(
    template_id: str,
    payload: UpdateFormTemplateRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateFormTemplateUseCase = Depends(get_update_form_template_use_case),
) -> SuccessEnvelope[UpdateFormTemplateResponse]:
    result = await use_case.execute(
        UpdateFormTemplateCommand(
            actor_id=current_user.user_id,
            template_id=template_id,
            name=payload.name,
        )
    )
    return SuccessEnvelope(
        message="Form template updated.",
        data=UpdateFormTemplateResponse(
            template_id=result.template_id,
            name=result.name,
        ),
    )


@router.post(
    "/{template_id}/publish",
    response_model=SuccessEnvelope[PublishFormTemplateResponse],
    operation_id="publish_form_template",
)
async def publish_form_template(
    template_id: str,
    current_user=Depends(get_current_user),
    use_case: PublishFormTemplateUseCase = Depends(get_publish_form_template_use_case),
) -> SuccessEnvelope[PublishFormTemplateResponse]:
    result = await use_case.execute(
        PublishFormTemplateCommand(
            template_id=template_id,
            published_by=current_user.user_id,
        )
    )
    return SuccessEnvelope(
        message="Form template published.",
        data=PublishFormTemplateResponse(
            template_id=result.template_id,
            status=result.status.value,
            published_at=result.published_at.isoformat(),
        ),
    )


@router.post(
    "/{template_id}/fields",
    response_model=SuccessEnvelope[AddFieldResponse],
    status_code=201,
    operation_id="add_field",
)
async def add_field(
    template_id: str,
    payload: AddFieldRequest,
    current_user=Depends(get_current_user),
    use_case: AddFieldUseCase = Depends(get_add_field_use_case),
) -> SuccessEnvelope[AddFieldResponse]:
    result = await use_case.execute(
        AddFieldCommand(
            actor_id=current_user.user_id,
            template_id=template_id,
            field_key=payload.field_key,
            label=payload.label,
            field_type=payload.field_type,
            description=payload.description,
            is_required=payload.is_required,
            is_repeatable=payload.is_repeatable,
            is_unique=payload.is_unique,
            sort_order=payload.sort_order,
            validation_rules=payload.validation_rules,
        )
    )
    return SuccessEnvelope(
        message="Field added.",
        data=AddFieldResponse(field_id=result.field_id),
    )


@router.patch(
    "/{template_id}/fields/{field_id}",
    response_model=SuccessEnvelope[UpdateFieldResponse],
    operation_id="update_field",
)
async def update_field(
    template_id: str,
    field_id: str,
    payload: UpdateFieldRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateFieldUseCase = Depends(get_update_field_use_case),
) -> SuccessEnvelope[UpdateFieldResponse]:
    result = await use_case.execute(
        UpdateFieldCommand(
            actor_id=current_user.user_id,
            template_id=template_id,
            field_id=field_id,
            label=payload.label,
            description=payload.description,
            field_type=payload.field_type,
            is_required=payload.is_required,
            is_repeatable=payload.is_repeatable,
            is_unique=payload.is_unique,
            sort_order=payload.sort_order,
            validation_rules=payload.validation_rules,
            is_active=payload.is_active,
        )
    )
    return SuccessEnvelope(
        message="Field updated.",
        data=UpdateFieldResponse(field_id=result.field_id),
    )


@router.delete(
    "/{template_id}/fields/{field_id}",
    response_model=SuccessEnvelope[RemoveFieldResponse],
    operation_id="remove_field",
)
async def remove_field(
    template_id: str,
    field_id: str,
    current_user=Depends(get_current_user),
    use_case: RemoveFieldUseCase = Depends(get_remove_field_use_case),
) -> SuccessEnvelope[RemoveFieldResponse]:
    result = await use_case.execute(
        RemoveFieldCommand(
            actor_id=current_user.user_id,
            template_id=template_id,
            field_id=field_id,
        )
    )
    return SuccessEnvelope(
        message="Field removed.",
        data=RemoveFieldResponse(field_id=result.field_id),
    )


@router.post(
    "/{template_id}/fields/{field_id}/options",
    response_model=SuccessEnvelope[AddFieldOptionResponse],
    status_code=201,
    operation_id="add_field_option",
)
async def add_field_option(
    template_id: str,
    field_id: str,
    payload: AddFieldOptionRequest,
    current_user=Depends(get_current_user),
    use_case: AddFieldOptionUseCase = Depends(get_add_field_option_use_case),
) -> SuccessEnvelope[AddFieldOptionResponse]:
    result = await use_case.execute(
        AddFieldOptionCommand(
            actor_id=current_user.user_id,
            template_id=template_id,
            field_id=field_id,
            option_key=payload.option_key,
            label=payload.label,
            value=payload.value,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
    )
    return SuccessEnvelope(
        message="Field option added.",
        data=AddFieldOptionResponse(option_id=result.option_id),
    )
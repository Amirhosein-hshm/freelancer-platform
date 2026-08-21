from dataclasses import dataclass

from app.application.form.dto import FormTemplateResult
from app.application.form.use_cases.get_form_template import to_template_result
from app.application.shared.pagination import DEFAULT_PAGE_SIZE, limit_offset
from app.application.shared.use_case import UseCase
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class ListFormTemplatesQuery:
    """Browse templates across ALL categories.

    Distinct from ``ListFormTemplateVersionsQuery``, which walks the version chain of a single
    ``template_key`` inside one category. This query backs admin browsing and the
    customer-facing "pick a form, then create a project against it" flow.
    """

    category_id: EntityId | None = None
    status: FormTemplateStatus | None = None
    search: str | None = None
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class ListFormTemplatesResult:
    templates: list[FormTemplateResult]
    total_items: int
    page: int
    page_size: int


class ListFormTemplatesUseCase(UseCase[ListFormTemplatesQuery, ListFormTemplatesResult]):
    """Authenticated read; no permission gate, matching the other form-template reads
    (`GetFormTemplate`, `GetFormTemplateById`, `ListFormTemplateVersions`)."""

    def __init__(self, template_repo: IFormTemplateRepository) -> None:
        self._template_repo = template_repo

    async def execute(self, request: ListFormTemplatesQuery) -> ListFormTemplatesResult:
        limit, offset = limit_offset(request.page, request.page_size)
        templates = await self._template_repo.list_templates(
            category_id=request.category_id,
            status=request.status,
            search=request.search,
            limit=limit,
            offset=offset,
        )
        total_items = await self._template_repo.count_templates(
            category_id=request.category_id,
            status=request.status,
            search=request.search,
        )
        return ListFormTemplatesResult(
            templates=[to_template_result(template) for template in templates],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )

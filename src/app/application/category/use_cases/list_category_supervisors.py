from app.application.category.dto import (
    CategorySupervisorResult,
    ListCategorySupervisorsQuery,
    ListCategorySupervisorsResult,
)
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import (
    ICategoryRepository,
    ICategorySupervisorRepository,
)


class ListCategorySupervisorsUseCase(UseCase[ListCategorySupervisorsQuery, ListCategorySupervisorsResult]):
    def __init__(
        self,
        category_repo: ICategoryRepository,
        supervisor_repo: ICategorySupervisorRepository,
    ) -> None:
        self._category_repo = category_repo
        self._supervisor_repo = supervisor_repo

    async def execute(self, request: ListCategorySupervisorsQuery) -> ListCategorySupervisorsResult:
        await self._category_repo.get_by_id(request.category_id)
        supervisors = await self._supervisor_repo.list_active_supervisors(request.category_id)
        return ListCategorySupervisorsResult(
            supervisors=[
                CategorySupervisorResult(
                    link_id=supervisor.id,
                    category_id=supervisor.category_id,
                    supervisor_user_id=supervisor.supervisor_user_id,
                    is_primary=supervisor.is_primary,
                    assigned_at=supervisor.assigned_at,
                )
                for supervisor in supervisors
            ]
        )

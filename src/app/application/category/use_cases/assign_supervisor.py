from app.application.category.dto import AssignSupervisorCommand, AssignSupervisorResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.entities import CategorySupervisor
from app.domain.category.exceptions import SupervisorAlreadyAssignedError
from app.domain.category.repositories import ICategoryRepository, ICategorySupervisorRepository


class AssignSupervisorUseCase(UseCase[AssignSupervisorCommand, AssignSupervisorResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        category_repo: ICategoryRepository,
        category_supervisor_repo: ICategorySupervisorRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._category_repo = category_repo
        self._category_supervisor_repo = category_supervisor_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: AssignSupervisorCommand) -> AssignSupervisorResult:
        self._authorization_service.require_permission(
            request.actor_id, "category.assign_supervisor"
        )
        self._category_repo.get_by_id(request.category_id)
        active = self._category_supervisor_repo.list_active_supervisors(request.category_id)
        if any(link.supervisor_user_id == request.supervisor_user_id for link in active):
            raise SupervisorAlreadyAssignedError(
                f"User {request.supervisor_user_id} is already a supervisor of category "
                f"{request.category_id}."
            )
        now = self._clock.now()
        link = CategorySupervisor(
            id=self._id_generator.new_id(),
            category_id=request.category_id,
            supervisor_user_id=request.supervisor_user_id,
            assigned_by_user_id=request.actor_id,
            is_primary=not active,
            is_active=True,
            assigned_at=now,
            created_at=now,
        )
        with self._uow:
            self._category_supervisor_repo.add(link)
            self._uow.commit()
        return AssignSupervisorResult(
            link_id=link.id,
            category_id=link.category_id,
            supervisor_user_id=link.supervisor_user_id,
        )

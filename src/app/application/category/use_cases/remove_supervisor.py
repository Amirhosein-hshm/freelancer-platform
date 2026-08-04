from app.application.category.dto import RemoveSupervisorCommand, RemoveSupervisorResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.exceptions import SupervisorAssignmentNotFoundError
from app.domain.category.repositories import ICategorySupervisorRepository


class RemoveSupervisorUseCase(UseCase[RemoveSupervisorCommand, RemoveSupervisorResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        category_supervisor_repo: ICategorySupervisorRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._category_supervisor_repo = category_supervisor_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: RemoveSupervisorCommand) -> RemoveSupervisorResult:
        await self._authorization_service.require_permission(
            request.actor_id, "category.remove_supervisor"
        )
        active = await self._category_supervisor_repo.list_active_supervisors(request.category_id)
        link = next(
            (item for item in active if item.supervisor_user_id == request.supervisor_user_id),
            None,
        )
        if link is None:
            raise SupervisorAssignmentNotFoundError(
                f"User {request.supervisor_user_id} is not an active supervisor of "
                f"category {request.category_id}."
            )
        now = await self._clock.now()
        async with self._uow:
            was_primary = link.is_primary
            link.revoke(now)
            await self._category_supervisor_repo.update(link)
            if was_primary:
                remaining = await self._category_supervisor_repo.list_active_supervisors(
                    request.category_id
                )
                if remaining:
                    remaining[0].promote()
                    await self._category_supervisor_repo.update(remaining[0])
            await self._uow.commit()
        return RemoveSupervisorResult(
            category_id=link.category_id,
            supervisor_user_id=link.supervisor_user_id,
            revoked_at=now,
        )

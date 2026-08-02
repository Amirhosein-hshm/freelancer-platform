from app.application.iam.dto import ActivateUserCommand, ActivateUserResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository


class ActivateUserUseCase(UseCase[ActivateUserCommand, ActivateUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: ActivateUserCommand) -> ActivateUserResult:
        self._authorization_service.require_permission(request.actor_id, "user.activate")
        user = self._user_repo.get_by_id(request.target_user_id)
        with self._uow:
            user.activate()
            self._user_repo.update(user)
            self._uow.commit()
        return ActivateUserResult(user_id=user.id, status=user.status.value)

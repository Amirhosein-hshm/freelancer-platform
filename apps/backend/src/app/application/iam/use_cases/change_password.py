from app.application.iam.dto import ChangePasswordCommand, ChangePasswordResult
from app.application.shared.ports import IClock, IPasswordHasher, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import InvalidCredentialsError
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import PasswordHash


class ChangePasswordUseCase(UseCase[ChangePasswordCommand, ChangePasswordResult]):
    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._clock = clock
        self._uow = uow

    async def execute(self, request: ChangePasswordCommand) -> ChangePasswordResult:
        request.validate()
        user = await self._user_repo.get_by_id(request.user_id)
        if not await self._password_hasher.verify(request.old_password, user.password_hash.value):
            raise InvalidCredentialsError(f"Old password is incorrect for user {user.id}.")
        new_hash = PasswordHash(await self._password_hasher.hash(request.new_password))
        now = await self._clock.now()
        async with self._uow:
            user.change_password(new_hash, now)
            await self._user_repo.update(user)
            await self._uow.commit()
        return ChangePasswordResult(user_id=user.id, password_changed_at=now)

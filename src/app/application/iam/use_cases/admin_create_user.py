from app.application.iam.dto import (
    AdminCreateUserCommand,
    AdminCreateUserResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    IPasswordHasher,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import DuplicateEmailError
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import Email, PasswordHash


class AdminCreateUserUseCase(UseCase[AdminCreateUserCommand, AdminCreateUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AdminCreateUserCommand) -> AdminCreateUserResult:
        await self._authorization_service.require_permission(request.actor_id, "user.create")
        request.validate()
        email = Email(request.email)
        if await self._user_repo.exists_by_email(email):
            raise DuplicateEmailError(f"Email {email.value} is already registered.")
        password_hash = PasswordHash(await self._password_hasher.hash(request.password))
        now = await self._clock.now()
        user = User(
            id=await self._id_generator.new_id(),
            email=email,
            phone=None,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            status=UserStatus.ACTIVE,
            created_at=now,
        )
        async with self._uow:
            await self._user_repo.add(user)
            await self._uow.commit()
        return AdminCreateUserResult(
            user_id=user.id,
            email=email.value,
            status=user.status.value,
            created_at=user.created_at,
        )
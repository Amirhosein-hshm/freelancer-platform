from app.application.iam.dto import RegisterUserCommand, RegisterUserResult
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    INotificationService,
    IPasswordHasher,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import User, UserRole
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import DuplicateEmailError
from app.domain.iam.repositories import IRoleRepository, IUserRepository, IUserRoleRepository
from app.domain.iam.value_objects import Email, PasswordHash

ALLOWED_REGISTER_ROLES = frozenset({"customer", "freelancer"})


class RegisterUserUseCase(UseCase[RegisterUserCommand, RegisterUserResult]):
    def __init__(
        self,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
        role_repo: IRoleRepository,
        password_hasher: IPasswordHasher,
        id_generator: IIdGenerator,
        clock: IClock,
        notification_service: INotificationService,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo
        self._role_repo = role_repo
        self._password_hasher = password_hasher
        self._id_generator = id_generator
        self._clock = clock
        self._notification_service = notification_service
        self._uow = uow

    async def execute(self, request: RegisterUserCommand) -> RegisterUserResult:
        request.validate()
        if request.role not in ALLOWED_REGISTER_ROLES:
            raise ValidationError(f"role must be one of {sorted(ALLOWED_REGISTER_ROLES)}.")
        email = Email(request.email)
        if await self._user_repo.exists_by_email(email):
            raise DuplicateEmailError(f"Email {email.value} is already registered.")
        role = await self._role_repo.get_by_key(request.role)
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
        user_role = UserRole(
            id=await self._id_generator.new_id(),
            user_id=user.id,
            role_id=role.id,
            assigned_by_user_id=user.id,
            assigned_at=now,
            created_at=now,
        )
        # Choosing role="freelancer" at registration ONLY links the IAM UserRole; it must
        # NOT auto-create a FreelancerProfile. That remains a separate, explicit step via
        # the self-service CreateFreelancerProfileUseCase (requires display_name).
        async with self._uow:
            await self._user_repo.add(user)
            await self._user_role_repo.add(user_role)
            await self._uow.commit()
        verification_token = await self._id_generator.new_id()
        await self._notification_service.send_verification_email(email.value, verification_token)
        return RegisterUserResult(
            user_id=user.id,
            email=email.value,
            role=role.role_key,
            status=user.status.value,
            created_at=user.created_at,
        )

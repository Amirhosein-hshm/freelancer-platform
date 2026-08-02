from app.application.iam.dto import RegisterUserCommand, RegisterUserResult
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

DEFAULT_REGISTER_ROLE_KEY = "customer"


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

    def execute(self, request: RegisterUserCommand) -> RegisterUserResult:
        request.validate()
        email = Email(request.email)
        if self._user_repo.exists_by_email(email):
            raise DuplicateEmailError(f"Email {email.value} is already registered.")
        role = self._role_repo.get_by_key(DEFAULT_REGISTER_ROLE_KEY)
        password_hash = PasswordHash(self._password_hasher.hash(request.password))
        now = self._clock.now()
        user = User(
            id=self._id_generator.new_id(),
            email=email,
            phone=None,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            status=UserStatus.PENDING,
            created_at=now,
        )
        user_role = UserRole(
            id=self._id_generator.new_id(),
            user_id=user.id,
            role_id=role.id,
            assigned_by_user_id=user.id,
            assigned_at=now,
            created_at=now,
        )
        with self._uow:
            self._user_repo.add(user)
            self._user_role_repo.add(user_role)
            self._uow.commit()
        verification_token = self._id_generator.new_id()
        self._notification_service.send_verification_email(email.value, verification_token)
        return RegisterUserResult(
            user_id=user.id,
            email=email.value,
            status=user.status.value,
            created_at=user.created_at,
        )

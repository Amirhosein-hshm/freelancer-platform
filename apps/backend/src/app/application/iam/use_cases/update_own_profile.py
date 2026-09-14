from app.application.iam.dto import UpdateOwnProfileCommand, UpdateOwnProfileResult
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import PhoneNumber


class UpdateOwnProfileUseCase(UseCase[UpdateOwnProfileCommand, UpdateOwnProfileResult]):
    def __init__(self, user_repo: IUserRepository, uow: IUnitOfWork) -> None:
        self._user_repo = user_repo
        self._uow = uow

    async def execute(self, request: UpdateOwnProfileCommand) -> UpdateOwnProfileResult:
        request.validate()
        user = await self._user_repo.get_by_id(request.actor_id)
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.last_name is not None:
            user.last_name = request.last_name
        if request.phone is not None:
            user.phone = PhoneNumber(request.phone)
        async with self._uow:
            await self._user_repo.update(user)
            await self._uow.commit()
        return UpdateOwnProfileResult(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone.value if user.phone else None,
        )

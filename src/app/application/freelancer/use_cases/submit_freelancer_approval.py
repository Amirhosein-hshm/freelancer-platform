from app.application.freelancer.dto import (
    SubmitFreelancerApprovalCommand,
    SubmitFreelancerApprovalResult,
)
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class SubmitFreelancerApprovalUseCase(
    UseCase[SubmitFreelancerApprovalCommand, SubmitFreelancerApprovalResult]
):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._profile_repo = profile_repo
        self._uow = uow

    async def execute(
        self, request: SubmitFreelancerApprovalCommand
    ) -> SubmitFreelancerApprovalResult:
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        async with self._uow:
            profile.submit_for_approval()
            await self._profile_repo.update(profile)
            await self._uow.commit()
        return SubmitFreelancerApprovalResult(
            profile_id=profile.id,
            approval_status=profile.approval_status,
        )

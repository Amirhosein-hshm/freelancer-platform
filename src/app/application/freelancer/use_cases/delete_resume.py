from app.application.freelancer.dto import DeleteResumeCommand, DeleteResumeResult
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IResumeRepository,
)


class DeleteResumeUseCase(UseCase[DeleteResumeCommand, DeleteResumeResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo

    async def execute(self, request: DeleteResumeCommand) -> DeleteResumeResult:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        versions = await self._resume_repo.list_by_profile(request.profile_id)
        target = next((r for r in versions if r.id == request.resume_id), None)
        if target is None:
            from app.domain.freelancer.exceptions import ResumeNotFoundError

            raise ResumeNotFoundError(f"Resume {request.resume_id} not found.")
        was_current = target.is_current
        await self._resume_repo.delete(request.resume_id)
        if was_current:
            remaining = sorted(
                [r for r in versions if r.id != request.resume_id],
                key=lambda r: r.version_no,
                reverse=True,
            )
            if remaining:
                latest = remaining[0]
                latest.is_current = True
                await self._resume_repo.update(latest)
        return DeleteResumeResult(resume_id=request.resume_id)

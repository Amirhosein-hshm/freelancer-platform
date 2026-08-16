from app.application.freelancer.dto import SetCurrentResumeCommand, SetCurrentResumeResult
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import ResumeNotFoundError
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IResumeRepository,
)


class SetCurrentResumeUseCase(UseCase[SetCurrentResumeCommand, SetCurrentResumeResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo

    async def execute(self, request: SetCurrentResumeCommand) -> SetCurrentResumeResult:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        target = None
        versions = await self._resume_repo.list_by_profile(request.profile_id)
        for resume in versions:
            if resume.id == request.resume_id:
                target = resume
            elif resume.is_current:
                resume.is_current = False
                await self._resume_repo.update(resume)
        if target is None:
            raise ResumeNotFoundError(f"Resume {request.resume_id} not found.")
        target.is_current = True
        await self._resume_repo.update(target)
        return SetCurrentResumeResult(resume_id=target.id)

from app.application.freelancer.dto import GetResumeQuery, ResumeResult
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


class GetResumeUseCase(UseCase[GetResumeQuery, ResumeResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo

    async def execute(self, request: GetResumeQuery) -> ResumeResult:
        resume = await self._resume_repo.get_by_id(request.resume_id)
        profile = await self._profile_repo.get_by_id(resume.freelancer_profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        return ResumeResult(
            resume_id=resume.id,
            freelancer_profile_id=resume.freelancer_profile_id,
            file_asset_id=resume.file_asset_id,
            version_no=resume.version_no,
            summary=resume.summary,
            is_current=resume.is_current,
        )

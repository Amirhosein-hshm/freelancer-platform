from app.application.freelancer.dto import (
    UpdateResumeCommand,
    UpdateResumeResult,
)
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import ResumeNotFoundError
from app.domain.freelancer.repositories import IFreelancerProfileRepository, IResumeRepository


class UpdateResumeUseCase(UseCase[UpdateResumeCommand, UpdateResumeResult]):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
    ) -> None:
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo

    def execute(self, request: UpdateResumeCommand) -> UpdateResumeResult:
        profile = self._profile_repo.get_by_user_id(request.user_id)
        resume = self._resume_repo.get_current(profile.id)
        if resume is None:
            raise ResumeNotFoundError(f"No current resume for profile {profile.id}.")
        resume.summary = request.summary
        self._resume_repo.update(resume)
        return UpdateResumeResult(resume_id=resume.id, summary=resume.summary)

from app.application.freelancer.dto import (
    FreelancerProfileResult,
    GetFreelancerProfileQuery,
)
from app.application.freelancer.use_cases.update_freelancer_profile import to_profile_result
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class GetFreelancerProfileUseCase(
    UseCase[GetFreelancerProfileQuery, FreelancerProfileResult]
):
    def __init__(self, profile_repo: IFreelancerProfileRepository) -> None:
        self._profile_repo = profile_repo

    def execute(self, request: GetFreelancerProfileQuery) -> FreelancerProfileResult:
        profile = self._profile_repo.get_by_id(request.profile_id)
        return to_profile_result(profile)

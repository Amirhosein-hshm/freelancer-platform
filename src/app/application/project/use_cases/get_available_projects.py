from app.application.project.dto import (
    GetAvailableProjectsQuery,
    GetAvailableProjectsResult,
)
from app.application.project.mapping import to_project_result
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.freelancer.repositories import (
    IFreelancerLevelRepository,
    IFreelancerProfileRepository,
)
from app.domain.project.repositories import IProjectRepository


class GetAvailableProjectsUseCase(
    UseCase[GetAvailableProjectsQuery, GetAvailableProjectsResult]
):
    def __init__(
        self,
        project_repo: IProjectRepository,
        profile_repo: IFreelancerProfileRepository,
        level_repo: IFreelancerLevelRepository,
    ) -> None:
        self._project_repo = project_repo
        self._profile_repo = profile_repo
        self._level_repo = level_repo

    def execute(self, request: GetAvailableProjectsQuery) -> GetAvailableProjectsResult:
        profile = self._profile_repo.get_by_user_id(request.actor_id)
        if not profile.is_approved():
            raise FreelancerNotApprovedError(
                f"Freelancer profile {profile.id} is not approved."
            )
        if profile.current_level_id is None:
            return GetAvailableProjectsResult(projects=[])
        level = self._level_repo.get_by_id(profile.current_level_id)
        projects = self._project_repo.list_available_for_freelancer(level.id)
        return GetAvailableProjectsResult(
            projects=[to_project_result(p) for p in projects]
        )

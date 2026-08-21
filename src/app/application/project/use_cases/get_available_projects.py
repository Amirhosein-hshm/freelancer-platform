from app.application.project.dto import (
    GetAvailableProjectsQuery,
    GetAvailableProjectsResult,
)
from app.application.project.mapping import to_project_result
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import IProjectRepository


class GetAvailableProjectsUseCase(UseCase[GetAvailableProjectsQuery, GetAvailableProjectsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._project_repo = project_repo
        self._profile_repo = profile_repo

    async def execute(self, request: GetAvailableProjectsQuery) -> GetAvailableProjectsResult:
        profile = await self._profile_repo.get_by_user_id(request.actor_id)
        if not profile.is_approved():
            raise FreelancerNotApprovedError(f"Freelancer profile {profile.id} is not approved.")
        limit, offset = limit_offset(request.page, request.page_size)
        projects = await self._project_repo.list_available_for_freelancer(
            profile.current_level,
            limit=limit,
            offset=offset,
        )
        total_items = await self._project_repo.count_available_for_freelancer(profile.current_level)
        return GetAvailableProjectsResult(
            projects=[to_project_result(p) for p in projects],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
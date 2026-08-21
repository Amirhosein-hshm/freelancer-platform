from app.application.freelancer.dto import (
    ListResumeVersionsQuery,
    ListResumeVersionsResult,
    ResumeResult,
)
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IResumeRepository,
)


class ListResumeVersionsUseCase(UseCase[ListResumeVersionsQuery, ListResumeVersionsResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo

    async def execute(self, request: ListResumeVersionsQuery) -> ListResumeVersionsResult:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        limit, offset = limit_offset(request.page, request.page_size)
        resumes = await self._resume_repo.list_by_profile(
            request.profile_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._resume_repo.count_by_profile(request.profile_id)
        return ListResumeVersionsResult(
            resumes=[
                ResumeResult(
                    resume_id=r.id,
                    freelancer_profile_id=r.freelancer_profile_id,
                    file_asset_id=r.file_asset_id,
                    version_no=r.version_no,
                    summary=r.summary,
                    is_current=r.is_current,
                )
                for r in resumes
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
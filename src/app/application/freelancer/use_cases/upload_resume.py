from app.application.freelancer.dto import (
    UploadResumeCommand,
    UploadResumeResult,
)
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IFileStorageService, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import Resume
from app.domain.freelancer.repositories import IFreelancerProfileRepository, IResumeRepository


class UploadResumeUseCase(UseCase[UploadResumeCommand, UploadResumeResult]):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
        file_storage: IFileStorageService,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo
        self._file_storage = file_storage
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: UploadResumeCommand) -> UploadResumeResult:
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        try:
            await self._file_storage.get_metadata(request.file_asset_id)
        except (KeyError, FileNotFoundError) as exc:
            raise ValidationError(
                f"File asset {request.file_asset_id} does not exist."
            ) from exc
        existing = await self._resume_repo.list_by_profile(profile.id)
        version_no = max((r.version_no for r in existing), default=0) + 1
        previous = await self._resume_repo.get_current(profile.id)
        now = await self._clock.now()
        resume = Resume(
            id=await self._id_generator.new_id(),
            freelancer_profile_id=profile.id,
            file_asset_id=request.file_asset_id,
            version_no=version_no,
            summary=request.summary,
            is_current=True,
            created_at=now,
        )
        async with self._uow:
            await self._resume_repo.add(resume)
            if previous is not None and previous.id != resume.id:
                previous.is_current = False
                await self._resume_repo.update(previous)
            await self._uow.commit()
        return UploadResumeResult(resume_id=resume.id, version_no=resume.version_no)

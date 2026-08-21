from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.entities import Resume
from app.domain.freelancer.exceptions import ResumeNotFoundError
from app.domain.freelancer.repositories import IResumeRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import ResumeModel
from app.infrastructure.repositories.freelancer_mapping import to_domain_resume


class SqlAlchemyResumeRepository(IResumeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, resume: Resume) -> None:
        self._session.add(
            ResumeModel(
                id=resume.id,
                freelancer_profile_id=resume.freelancer_profile_id,
                file_asset_id=resume.file_asset_id,
                version_no=resume.version_no,
                summary=resume.summary,
                is_current=resume.is_current,
            )
        )

    async def update(self, resume: Resume) -> None:
        row = await self._session.get(ResumeModel, resume.id)
        if row is None:
            raise ResumeNotFoundError(f"Resume {resume.id} not found.")
        row.file_asset_id = resume.file_asset_id
        row.version_no = resume.version_no
        row.summary = resume.summary
        row.is_current = resume.is_current

    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Resume]:
        stmt = (
            select(ResumeModel)
            .where(ResumeModel.freelancer_profile_id == profile_id)
            .order_by(ResumeModel.version_no.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_resume(row) for row in result.scalars().all()]

    async def count_by_profile(self, profile_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(ResumeModel.id)).where(
                ResumeModel.freelancer_profile_id == profile_id,
            )
        )
        return int(result.scalar_one())

    async def get_current(self, profile_id: EntityId) -> Resume | None:
        result = await self._session.execute(
            select(ResumeModel)
            .where(
                ResumeModel.freelancer_profile_id == profile_id,
                ResumeModel.is_current.is_(True),
            )
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return to_domain_resume(row) if row is not None else None

    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> Resume | None:
        result = await self._session.execute(
            select(ResumeModel).where(ResumeModel.file_asset_id == file_asset_id).limit(1)
        )
        row = result.scalar_one_or_none()
        return to_domain_resume(row) if row is not None else None

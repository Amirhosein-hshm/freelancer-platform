from app.domain.freelancer.entities import Resume
from app.domain.freelancer.exceptions import ResumeNotFoundError
from app.domain.freelancer.repositories import IResumeRepository
from app.domain.shared.types import EntityId


class FakeResumeRepository(IResumeRepository):
    def __init__(self) -> None:
        self._store: list[Resume] = []

    async def add(self, resume: Resume) -> None:
        self._store.append(resume)

    async def get_by_id(self, resume_id: EntityId) -> Resume:
        for r in self._store:
            if r.id == resume_id:
                return r
        raise ResumeNotFoundError(f"Resume {resume_id} not found.")

    async def update(self, resume: Resume) -> None:
        for i, stored in enumerate(self._store):
            if stored.id == resume.id:
                self._store[i] = resume
                return
        self._store.append(resume)

    async def delete(self, resume_id: EntityId) -> None:
        self._store = [r for r in self._store if r.id != resume_id]

    async def list_by_profile(self, profile_id: EntityId) -> list[Resume]:
        return [r for r in self._store if r.freelancer_profile_id == profile_id]

    async def get_current(self, profile_id: EntityId) -> Resume | None:
        for r in self._store:
            if r.freelancer_profile_id == profile_id and r.is_current:
                return r
        return None

    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> Resume | None:
        for r in self._store:
            if r.file_asset_id == file_asset_id:
                return r
        return None

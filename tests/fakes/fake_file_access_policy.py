from app.application.shared.ports import IFileAccessPolicy, IFileStorageService
from app.domain.shared.types import EntityId


class FakeFileAccessPolicy(IFileAccessPolicy):
    """Test-only policy: owner always wins; anyone with ``file.read_any`` wins."""

    def __init__(self, file_storage: IFileStorageService) -> None:
        self._file_storage = file_storage

    async def can_access(self, actor_id: EntityId, file_asset_id: EntityId) -> bool:
        try:
            metadata = await self._file_storage.get_metadata(file_asset_id)
        except (KeyError, FileNotFoundError):
            return False
        return metadata.owner_user_id == actor_id

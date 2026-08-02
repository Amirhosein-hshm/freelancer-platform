from datetime import UTC, datetime

from app.application.shared.ports import FileAssetMetadata, IFileStorageService
from app.domain.shared.types import EntityId


class FakeFileStorageService(IFileStorageService):
    def __init__(self) -> None:
        self._store: dict[EntityId, FileAssetMetadata] = {}

    def add(self, metadata: FileAssetMetadata) -> None:
        self._store[metadata.file_asset_id] = metadata

    def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        try:
            return self._store[file_asset_id]
        except KeyError:
            raise FileNotFoundError(f"File asset {file_asset_id} not found.") from None

    def register_uploaded_file(
        self,
        file_name: str,
        size_bytes: int,
        mime_type: str,
        owner_user_id: EntityId,
    ) -> EntityId:
        asset_id = f"asset-{len(self._store) + 1}"
        metadata = FileAssetMetadata(
            file_asset_id=asset_id,
            file_name=file_name,
            size_bytes=size_bytes,
            mime_type=mime_type,
            url=None,
            uploaded_at=datetime.now(UTC),
        )
        self._store[asset_id] = metadata
        return asset_id

from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from app.application.shared.ports import FileAssetMetadata, IFileStorageService
from app.domain.shared.types import EntityId


class InMemoryFileStorageService(IFileStorageService):
    """In-memory file metadata registry.

    No binary blob is persisted: ``register_uploaded_file`` records metadata only and
    ``get_metadata`` raises ``KeyError`` for unknown ids, which the caller translates.
    A real S3/local-disk implementation can replace this behind the same interface.
    """

    def __init__(self) -> None:
        self._assets: dict[EntityId, FileAssetMetadata] = {}
        self._lock = Lock()

    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        with self._lock:
            try:
                return self._assets[file_asset_id]
            except KeyError as exc:
                raise KeyError(f"File asset {file_asset_id} does not exist.") from exc

    async def register_uploaded_file(
        self,
        file_name: str,
        size_bytes: int,
        mime_type: str,
        owner_user_id: EntityId,
    ) -> EntityId:
        file_asset_id = str(uuid4())
        with self._lock:
            self._assets[file_asset_id] = FileAssetMetadata(
                file_asset_id=file_asset_id,
                file_name=file_name,
                size_bytes=size_bytes,
                mime_type=mime_type,
                url=None,
                uploaded_at=datetime.now(UTC),
            )
        return file_asset_id

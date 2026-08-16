from collections.abc import AsyncIterator
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from app.application.shared.ports import FileAssetContext, FileAssetMetadata, IFileStorageService
from app.domain.file.exceptions import FileTooLargeError
from app.domain.shared.types import EntityId


class InMemoryFileStorageService(IFileStorageService):
    """In-memory file storage.

    Stores both metadata and bytes in process-local dictionaries. Useful for tests
    and lightweight local runs, but not persistent across restarts or processes.
    """

    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024) -> None:
        self._assets: dict[EntityId, FileAssetMetadata] = {}
        self._content: dict[EntityId, bytes] = {}
        self._lock = Lock()
        self._max_size_bytes = max_size_bytes

    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        with self._lock:
            try:
                return self._assets[file_asset_id]
            except KeyError as exc:
                raise KeyError(f"File asset {file_asset_id} does not exist.") from exc

    async def get_content(self, file_asset_id: EntityId) -> AsyncIterator[bytes]:
        with self._lock:
            try:
                data = self._content[file_asset_id]
            except KeyError as exc:
                raise KeyError(f"File asset {file_asset_id} does not exist.") from exc
        yield data

    async def register_uploaded_file(
        self,
        file_name: str,
        content: AsyncIterator[bytes],
        mime_type: str,
        owner_user_id: EntityId,
        context: FileAssetContext,
    ) -> EntityId:
        file_asset_id = str(uuid4())
        total = 0
        chunks: list[bytes] = []
        async for chunk in content:
            total += len(chunk)
            if total > self._max_size_bytes:
                raise FileTooLargeError(f"File exceeds maximum allowed size of {self._max_size_bytes} bytes.")
            chunks.append(chunk)
        data = b"".join(chunks)
        with self._lock:
            self._assets[file_asset_id] = FileAssetMetadata(
                file_asset_id=file_asset_id,
                file_name=file_name,
                size_bytes=total,
                mime_type=mime_type,
                url=None,
                uploaded_at=datetime.now(UTC),
                owner_user_id=owner_user_id,
                context=context,
            )
            self._content[file_asset_id] = data
        return file_asset_id

from collections.abc import AsyncIterator
from datetime import UTC, datetime

from app.application.shared.ports import FileAssetContext, FileAssetMetadata, IFileStorageService
from app.domain.file.exceptions import FileTooLargeError
from app.domain.shared.types import EntityId


class FakeFileStorageService(IFileStorageService):
    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024) -> None:
        self._store: dict[EntityId, FileAssetMetadata] = {}
        self._content: dict[EntityId, bytes] = {}
        self._max_size_bytes = max_size_bytes

    def add(self, metadata: FileAssetMetadata, content: bytes = b"") -> None:
        self._store[metadata.file_asset_id] = metadata
        self._content[metadata.file_asset_id] = content

    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        try:
            return self._store[file_asset_id]
        except KeyError:
            raise FileNotFoundError(f"File asset {file_asset_id} not found.") from None

    async def get_content(self, file_asset_id: EntityId) -> AsyncIterator[bytes]:
        try:
            data = self._content[file_asset_id]
        except KeyError:
            raise FileNotFoundError(f"File asset {file_asset_id} not found.") from None
        yield data

    async def register_uploaded_file(
        self,
        file_name: str,
        content: AsyncIterator[bytes],
        mime_type: str,
        owner_user_id: EntityId,
        context: FileAssetContext,
    ) -> EntityId:
        asset_id = f"asset-{len(self._store) + 1}"
        total = 0
        chunks: list[bytes] = []
        async for chunk in content:
            total += len(chunk)
            if total > self._max_size_bytes:
                raise FileTooLargeError(f"File exceeds maximum allowed size of {self._max_size_bytes} bytes.")
            chunks.append(chunk)
        data = b"".join(chunks)
        metadata = FileAssetMetadata(
            file_asset_id=asset_id,
            file_name=file_name,
            size_bytes=total,
            mime_type=mime_type,
            url=None,
            uploaded_at=datetime.now(UTC),
            owner_user_id=owner_user_id,
            context=context,
        )
        self._store[asset_id] = metadata
        self._content[asset_id] = data
        return asset_id

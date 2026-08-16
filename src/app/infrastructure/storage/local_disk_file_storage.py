import json
import mimetypes
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path

import aiofiles

from app.application.shared.ports import FileAssetContext, FileAssetMetadata, IFileStorageService
from app.domain.file.exceptions import FileTooLargeError
from app.domain.shared.types import EntityId


class LocalDiskFileStorageService(IFileStorageService):
    """Persistent file storage on a local filesystem path.

    Files are stored outside any web-servable static directory. The actual disk
    filename is server-generated from the asset UUID plus an extension derived from
    the validated MIME type; the original client filename is never used as a path
    component. A JSON sidecar stores metadata.

    This is the interim production backend for the current deployment stage. It can
    be swapped for an S3/MinIO implementation behind the same ``IFileStorageService``
    port without changing application code.
    """

    def __init__(self, root_dir: Path, max_size_bytes: int = 50 * 1024 * 1024) -> None:
        self._root = root_dir.resolve()
        self._max_size_bytes = max_size_bytes
        self._chunk_size = 64 * 1024
        self._root.mkdir(parents=True, exist_ok=True)

    def _binary_path(self, file_asset_id: EntityId, ext: str) -> Path:
        return self._root / f"{file_asset_id}{ext}"

    def _meta_path(self, file_asset_id: EntityId) -> Path:
        return self._root / f"{file_asset_id}.meta.json"

    @staticmethod
    def _extension(mime_type: str) -> str:
        ext = mimetypes.guess_extension(mime_type, strict=False)
        return ext or ".bin"

    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        meta_path = self._meta_path(file_asset_id)
        if not meta_path.exists():
            raise FileNotFoundError(f"File asset {file_asset_id} does not exist.")
        async with aiofiles.open(meta_path, encoding="utf-8") as f:
            raw = await f.read()
        data = json.loads(raw)
        return FileAssetMetadata(
            file_asset_id=data["file_asset_id"],
            file_name=data["file_name"],
            size_bytes=data["size_bytes"],
            mime_type=data["mime_type"],
            url=data.get("url"),
            uploaded_at=datetime.fromisoformat(data["uploaded_at"]),
            owner_user_id=data["owner_user_id"],
            context=FileAssetContext(data["context"]),
        )

    async def get_content(self, file_asset_id: EntityId) -> AsyncIterator[bytes]:
        metadata = await self.get_metadata(file_asset_id)
        binary_path = self._binary_path(file_asset_id, self._extension(metadata.mime_type or ""))
        if not binary_path.exists():
            raise FileNotFoundError(f"File asset {file_asset_id} does not exist.")
        async with aiofiles.open(binary_path, "rb") as f:
            while True:
                chunk = await f.read(self._chunk_size)
                if not chunk:
                    break
                yield chunk

    async def register_uploaded_file(
        self,
        file_name: str,
        content: AsyncIterator[bytes],
        mime_type: str,
        owner_user_id: EntityId,
        context: FileAssetContext,
    ) -> EntityId:
        file_asset_id = str(uuid.uuid4())
        ext = self._extension(mime_type)
        binary_path = self._binary_path(file_asset_id, ext)
        meta_path = self._meta_path(file_asset_id)

        total = 0
        try:
            async with aiofiles.open(binary_path, "wb") as f:
                async for chunk in content:
                    total += len(chunk)
                    if total > self._max_size_bytes:
                        raise FileTooLargeError(f"File exceeds maximum allowed size of {self._max_size_bytes} bytes.")
                    await f.write(chunk)
        except FileTooLargeError:
            if binary_path.exists():
                binary_path.unlink(missing_ok=True)
            raise

        metadata = FileAssetMetadata(
            file_asset_id=file_asset_id,
            file_name=file_name,
            size_bytes=total,
            mime_type=mime_type,
            url=None,
            uploaded_at=datetime.now(UTC),
            owner_user_id=owner_user_id,
            context=context,
        )
        async with aiofiles.open(meta_path, "w", encoding="utf-8") as f:
            await f.write(
                json.dumps(
                    {
                        "file_asset_id": metadata.file_asset_id,
                        "file_name": metadata.file_name,
                        "size_bytes": metadata.size_bytes,
                        "mime_type": metadata.mime_type,
                        "url": metadata.url,
                        "uploaded_at": metadata.uploaded_at.isoformat(),
                        "owner_user_id": metadata.owner_user_id,
                        "context": metadata.context.value,
                    },
                    indent=2,
                )
            )
        return file_asset_id

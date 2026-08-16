import json
import mimetypes
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import aioboto3

from app.application.shared.ports import FileAssetContext, FileAssetMetadata, IFileStorageService
from app.domain.file.exceptions import FileTooLargeError
from app.domain.shared.types import EntityId


class S3FileStorageService(IFileStorageService):
    """S3-compatible object storage implementation of ``IFileStorageService``.

    Works with AWS S3, MinIO, DigitalOcean Spaces, and any other S3-compatible
    service. The bucket and credentials are supplied via configuration; the storage
    key is server-generated from the asset UUID plus a content-derived extension.
    """

    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        max_size_bytes: int = 50 * 1024 * 1024,
    ) -> None:
        self._bucket = bucket
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._max_size_bytes = max_size_bytes
        self._chunk_size = 64 * 1024

    def _extension(self, mime_type: str) -> str:
        ext = mimetypes.guess_extension(mime_type, strict=False)
        return ext or ".bin"

    def _object_key(self, file_asset_id: EntityId, suffix: str = "") -> str:
        return f"{file_asset_id}{suffix}"

    def _client(self):
        session = aioboto3.Session()
        return session.client(
            "s3",
            region_name=self._region,
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        )

    async def get_metadata(self, file_asset_id: EntityId) -> FileAssetMetadata:
        async with self._client() as client:
            try:
                response = await client.get_object(
                    Bucket=self._bucket,
                    Key=self._object_key(file_asset_id, ".meta.json"),
                )
                raw = await response["Body"].read()
            except client.exceptions.NoSuchKey as exc:
                raise FileNotFoundError(f"File asset {file_asset_id} does not exist.") from exc
        data = json.loads(raw.decode("utf-8"))
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
        key = self._object_key(file_asset_id, self._extension(metadata.mime_type or ""))
        async with self._client() as client:
            try:
                response = await client.get_object(Bucket=self._bucket, Key=key)
            except client.exceptions.NoSuchKey as exc:
                raise FileNotFoundError(f"File asset {file_asset_id} does not exist.") from exc
            body = response["Body"]
            while True:
                chunk = await body.read(self._chunk_size)
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
        import uuid

        file_asset_id = str(uuid.uuid4())
        ext = self._extension(mime_type)
        binary_key = self._object_key(file_asset_id, ext)
        meta_key = self._object_key(file_asset_id, ".meta.json")

        total = 0
        chunks: list[bytes] = []
        async for chunk in content:
            total += len(chunk)
            if total > self._max_size_bytes:
                raise FileTooLargeError(f"File exceeds maximum allowed size of {self._max_size_bytes} bytes.")
            chunks.append(chunk)
        data = b"".join(chunks)

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

        async with self._client() as client:
            await client.put_object(
                Bucket=self._bucket,
                Key=binary_key,
                Body=data,
                ContentType=mime_type,
            )
            await client.put_object(
                Bucket=self._bucket,
                Key=meta_key,
                Body=json.dumps(
                    {
                        "file_asset_id": metadata.file_asset_id,
                        "file_name": metadata.file_name,
                        "size_bytes": metadata.size_bytes,
                        "mime_type": metadata.mime_type,
                        "url": metadata.url,
                        "uploaded_at": metadata.uploaded_at.isoformat(),
                        "owner_user_id": metadata.owner_user_id,
                        "context": metadata.context.value,
                    }
                ).encode("utf-8"),
                ContentType="application/json",
            )
        return file_asset_id

from dataclasses import dataclass
from datetime import datetime

from app.domain.file.enums import FileAssetContext
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class UploadFileCommand:
    actor_id: EntityId
    file_name: str
    content_bytes: bytes
    context: FileAssetContext


@dataclass(frozen=True)
class UploadFileResult:
    file_asset_id: EntityId
    file_name: str
    size_bytes: int
    mime_type: str
    uploaded_at: datetime
    context: FileAssetContext


@dataclass(frozen=True)
class GetFileAssetQuery:
    actor_id: EntityId
    file_asset_id: EntityId


@dataclass(frozen=True)
class GetFileAssetResult:
    file_asset_id: EntityId
    file_name: str
    size_bytes: int
    mime_type: str
    uploaded_at: datetime
    owner_user_id: EntityId
    context: FileAssetContext

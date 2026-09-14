from datetime import datetime

from pydantic import BaseModel

from app.domain.file.enums import FileAssetContext


class FileAssetResponse(BaseModel):
    file_asset_id: str
    file_name: str
    size_bytes: int
    mime_type: str
    uploaded_at: datetime
    context: FileAssetContext

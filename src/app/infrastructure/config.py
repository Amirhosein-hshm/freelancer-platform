from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30
    admin_email: str
    admin_password: str
    cors_allowed_origins: str = "http://localhost:3000"

    # File storage backend: "local" (default, interim production backend) or "s3".
    file_storage_backend: str = "local"
    file_storage_root: str = "/app/storage/files"
    file_storage_max_size_mb: int = 50

    # S3-compatible storage (only used when FILE_STORAGE_BACKEND=s3).
    s3_bucket: str = ""
    s3_endpoint_url: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "us-east-1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def file_storage_max_size_bytes(self) -> int:
        return self.file_storage_max_size_mb * 1024 * 1024

    @property
    def file_storage_root_path(self) -> Path:
        return Path(self.file_storage_root)


@lru_cache
def get_settings() -> Settings:
    return Settings()

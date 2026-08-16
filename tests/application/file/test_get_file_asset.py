import pytest

from app.application.file.dto import GetFileAssetQuery
from app.application.file.use_cases.get_file_asset import GetFileAssetUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import FileAssetContext, FileAssetMetadata
from app.domain.file.exceptions import FileAssetNotFoundError
from tests.fakes.fake_file_access_policy import FakeFileAccessPolicy


class TestGetFileAssetUseCase:
    async def test_owner_can_access(self, file_storage):
        file_storage.add(
            FileAssetMetadata(
                file_asset_id="asset-1",
                file_name="doc.pdf",
                size_bytes=1024,
                mime_type="application/pdf",
                url=None,
                uploaded_at=None,  # type: ignore[arg-type]
                owner_user_id="user-1",
                context=FileAssetContext.GENERIC,
            ),
            content=b"pdf-bytes",
        )
        use_case = GetFileAssetUseCase(file_storage, FakeFileAccessPolicy(file_storage))

        result = await use_case.execute(GetFileAssetQuery(actor_id="user-1", file_asset_id="asset-1"))

        assert result.file_asset_id == "asset-1"
        assert result.owner_user_id == "user-1"
        content = b"".join([chunk async for chunk in result.content])
        assert content == b"pdf-bytes"

    async def test_non_owner_denied(self, file_storage):
        file_storage.add(
            FileAssetMetadata(
                file_asset_id="asset-1",
                file_name="doc.pdf",
                size_bytes=1024,
                mime_type="application/pdf",
                url=None,
                uploaded_at=None,  # type: ignore[arg-type]
                owner_user_id="user-1",
                context=FileAssetContext.GENERIC,
            ),
            content=b"pdf-bytes",
        )
        use_case = GetFileAssetUseCase(file_storage, FakeFileAccessPolicy(file_storage))

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(GetFileAssetQuery(actor_id="user-2", file_asset_id="asset-1"))

    async def test_missing_asset_raises(self, file_storage):
        use_case = GetFileAssetUseCase(file_storage, FakeFileAccessPolicy(file_storage))

        with pytest.raises(FileAssetNotFoundError):
            await use_case.execute(GetFileAssetQuery(actor_id="user-1", file_asset_id="missing"))

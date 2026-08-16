import pytest

from app.application.file.dto import UploadFileCommand
from app.application.file.use_cases.upload_file import UploadFileUseCase
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import FileAssetContext
from app.domain.file.exceptions import InvalidFileContentError


class TestUploadFileUseCase:
    async def test_upload_pdf(self, file_storage, clock):
        use_case = UploadFileUseCase(file_storage, clock)
        content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"

        result = await use_case.execute(
            UploadFileCommand(
                actor_id="user-1",
                file_name="report.pdf",
                content_bytes=content,
                context=FileAssetContext.GENERIC,
            )
        )

        assert result.file_name == "report.pdf"
        assert result.size_bytes == len(content)
        assert result.mime_type == "application/pdf"
        assert result.context == FileAssetContext.GENERIC
        metadata = await file_storage.get_metadata(result.file_asset_id)
        assert metadata.owner_user_id == "user-1"

    async def test_upload_png(self, file_storage, clock):
        use_case = UploadFileUseCase(file_storage, clock)
        # Minimal PNG signature + IHDR-ish bytes are enough for filetype.
        content = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        result = await use_case.execute(
            UploadFileCommand(
                actor_id="user-1",
                file_name="image.png",
                content_bytes=content,
                context=FileAssetContext.PORTFOLIO,
            )
        )

        assert result.mime_type == "image/png"
        assert result.context == FileAssetContext.PORTFOLIO

    async def test_empty_file_raises(self, file_storage, clock):
        use_case = UploadFileUseCase(file_storage, clock)

        with pytest.raises(ValidationError):
            await use_case.execute(
                UploadFileCommand(
                    actor_id="user-1",
                    file_name="empty.txt",
                    content_bytes=b"",
                    context=FileAssetContext.GENERIC,
                )
            )

    async def test_unknown_content_raises(self, file_storage, clock):
        use_case = UploadFileUseCase(file_storage, clock)

        with pytest.raises(InvalidFileContentError):
            await use_case.execute(
                UploadFileCommand(
                    actor_id="user-1",
                    file_name="random.bin",
                    content_bytes=b"not a known file type content",
                    context=FileAssetContext.GENERIC,
                )
            )

    async def test_missing_file_name_raises(self, file_storage, clock):
        use_case = UploadFileUseCase(file_storage, clock)

        with pytest.raises(ValidationError):
            await use_case.execute(
                UploadFileCommand(
                    actor_id="user-1",
                    file_name="",
                    content_bytes=b"%PDF-1.4",
                    context=FileAssetContext.GENERIC,
                )
            )

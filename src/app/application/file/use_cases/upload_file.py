from collections.abc import AsyncIterator

import filetype

from app.application.file.dto import UploadFileCommand, UploadFileResult
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IFileStorageService
from app.application.shared.use_case import UseCase
from app.domain.file.exceptions import InvalidFileContentError

_DETECTION_BUFFER_SIZE = 8192


class UploadFileUseCase(UseCase[UploadFileCommand, UploadFileResult]):
    def __init__(
        self,
        file_storage: IFileStorageService,
        clock: IClock,
    ) -> None:
        self._file_storage = file_storage
        self._clock = clock

    async def execute(self, request: UploadFileCommand) -> UploadFileResult:
        if not request.file_name:
            raise ValidationError("file_name is required.")

        detection_buffer = bytearray()
        async for chunk in request.content:
            if not chunk:
                continue
            detection_buffer.extend(chunk)
            if len(detection_buffer) >= _DETECTION_BUFFER_SIZE:
                break

        if not detection_buffer:
            raise ValidationError("Uploaded file is empty.")

        guess = filetype.guess(bytes(detection_buffer))
        if guess is None:
            raise InvalidFileContentError("Could not determine MIME type from file content.")
        mime_type = guess.mime

        async def _content_with_buffer() -> AsyncIterator[bytes]:
            yield bytes(detection_buffer)
            async for chunk in request.content:
                if chunk:
                    yield chunk

        asset_id = await self._file_storage.register_uploaded_file(
            file_name=request.file_name,
            content=_content_with_buffer(),
            mime_type=mime_type,
            owner_user_id=request.actor_id,
            context=request.context,
        )
        metadata = await self._file_storage.get_metadata(asset_id)
        return UploadFileResult(
            file_asset_id=metadata.file_asset_id,
            file_name=metadata.file_name,
            size_bytes=metadata.size_bytes,
            mime_type=metadata.mime_type or "application/octet-stream",
            uploaded_at=metadata.uploaded_at,
            context=metadata.context,
        )

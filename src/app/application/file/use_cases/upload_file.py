import filetype

from app.application.file.dto import UploadFileCommand, UploadFileResult
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IFileStorageService
from app.application.shared.use_case import UseCase
from app.domain.file.exceptions import InvalidFileContentError


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
        if not request.content_bytes:
            raise ValidationError("Uploaded file is empty.")

        guess = filetype.guess(request.content_bytes)
        if guess is None:
            raise InvalidFileContentError(
                "Could not determine MIME type from file content."
            )
        mime_type = guess.mime

        asset_id = await self._file_storage.register_uploaded_file(
            file_name=request.file_name,
            size_bytes=len(request.content_bytes),
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

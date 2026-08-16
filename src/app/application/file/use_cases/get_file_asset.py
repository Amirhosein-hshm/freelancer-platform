from app.application.file.dto import GetFileAssetQuery, GetFileAssetResult
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IFileAccessPolicy, IFileStorageService
from app.application.shared.use_case import UseCase
from app.domain.file.exceptions import FileAssetNotFoundError


class GetFileAssetUseCase(UseCase[GetFileAssetQuery, GetFileAssetResult]):
    def __init__(
        self,
        file_storage: IFileStorageService,
        access_policy: IFileAccessPolicy,
    ) -> None:
        self._file_storage = file_storage
        self._access_policy = access_policy

    async def execute(self, request: GetFileAssetQuery) -> GetFileAssetResult:
        try:
            metadata = await self._file_storage.get_metadata(request.file_asset_id)
        except (KeyError, FileNotFoundError) as exc:
            raise FileAssetNotFoundError(
                f"File asset {request.file_asset_id} not found."
            ) from exc

        if not await self._access_policy.can_access(request.actor_id, request.file_asset_id):
            raise PermissionDeniedError(
                f"Access denied to file asset {request.file_asset_id}."
            )

        return GetFileAssetResult(
            file_asset_id=metadata.file_asset_id,
            file_name=metadata.file_name,
            size_bytes=metadata.size_bytes,
            mime_type=metadata.mime_type or "application/octet-stream",
            uploaded_at=metadata.uploaded_at,
            owner_user_id=metadata.owner_user_id,
            context=metadata.context,
        )

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.application.file.dto import GetFileAssetQuery, UploadFileCommand
from app.application.file.use_cases.get_file_asset import GetFileAssetUseCase
from app.application.file.use_cases.upload_file import UploadFileUseCase
from app.domain.file.enums import FileAssetContext
from app.presentation.api.v1.file.schemas import FileAssetResponse
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import get_get_file_asset_use_case, get_upload_file_use_case
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/files", tags=["File"])


@router.post(
    "",
    response_model=SuccessEnvelope[FileAssetResponse],
    status_code=201,
    operation_id="upload_file",
)
async def upload_file(
    file: UploadFile = File(...),
    context: FileAssetContext = Form(...),
    current_user=Depends(get_current_user),
    use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
) -> SuccessEnvelope[FileAssetResponse]:
    content = await file.read()
    result = await use_case.execute(
        UploadFileCommand(
            actor_id=current_user.user_id,
            file_name=file.filename or "unnamed",
            content_bytes=content,
            context=context,
        )
    )
    return SuccessEnvelope(
        message="File uploaded.",
        data=FileAssetResponse(
            file_asset_id=result.file_asset_id,
            file_name=result.file_name,
            size_bytes=result.size_bytes,
            mime_type=result.mime_type,
            uploaded_at=result.uploaded_at,
            context=result.context,
        ),
    )


@router.get(
    "/{file_asset_id}",
    response_model=SuccessEnvelope[FileAssetResponse],
    operation_id="get_file_asset",
)
async def get_file_asset(
    file_asset_id: str,
    current_user=Depends(get_current_user),
    use_case: GetFileAssetUseCase = Depends(get_get_file_asset_use_case),
) -> SuccessEnvelope[FileAssetResponse]:
    result = await use_case.execute(
        GetFileAssetQuery(
            actor_id=current_user.user_id,
            file_asset_id=file_asset_id,
        )
    )
    return SuccessEnvelope(
        message="File asset details.",
        data=FileAssetResponse(
            file_asset_id=result.file_asset_id,
            file_name=result.file_name,
            size_bytes=result.size_bytes,
            mime_type=result.mime_type,
            uploaded_at=result.uploaded_at,
            context=result.context,
        ),
    )

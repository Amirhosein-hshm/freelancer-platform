from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.shared.exceptions import ExpiredTokenError, InvalidTokenError
from app.application.shared.ports import ITokenService
from app.presentation.core.providers import get_token_service

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    token_service: ITokenService = Depends(get_token_service),
):
    try:
        return await token_service.decode_access_token(credentials.credentials)
    except (InvalidTokenError, ExpiredTokenError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

from app.application.shared.ports import ITokenService
from app.presentation.core.providers import get_token_service
from app.presentation.websocket.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def notifications_ws(
    ws: WebSocket,
    token: str = Query(...),
    token_service: ITokenService = Depends(get_token_service),
) -> None:
    payload = await token_service.decode_access_token(token)
    await manager.connect(payload.user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(payload.user_id, ws)
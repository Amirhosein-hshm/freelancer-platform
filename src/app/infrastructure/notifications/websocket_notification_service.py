import logging

from app.application.shared.ports import INotificationService, IRealtimeNotifier
from app.domain.shared.types import EntityId
from app.presentation.websocket.connection_manager import manager

logger = logging.getLogger(__name__)


class WebSocketNotificationService(INotificationService, IRealtimeNotifier):
    """Email methods are no-ops with a warning (SMTP out of scope for this phase).

    Real-time pushes go through the WebSocket connection manager — the single documented
    place where infrastructure may import from presentation (see ARCHITECTURE.md).
    """

    async def send_email(self, to: str, subject: str, body: str) -> None:
        logger.warning("Email not sent (SMTP disabled): to=%s subject=%s", to, subject)

    async def send_verification_email(self, to: str, token: str) -> None:
        logger.warning("Verification email not sent (SMTP disabled): to=%s", to)

    async def send_password_reset_email(self, to: str, token: str) -> None:
        logger.warning("Password reset email not sent (SMTP disabled): to=%s", to)

    async def notify_user(self, user_id: EntityId, event_type: str, payload: dict[str, object]) -> None:
        await manager.send_to_user(
            user_id,
            {"event_type": event_type, "payload": payload},
        )

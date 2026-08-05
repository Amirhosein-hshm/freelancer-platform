from collections import defaultdict

from fastapi import WebSocket

from app.domain.shared.types import EntityId


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[EntityId, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: EntityId, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[user_id].add(ws)

    def disconnect(self, user_id: EntityId, ws: WebSocket) -> None:
        self._connections[user_id].discard(ws)

    async def send_to_user(self, user_id: EntityId, payload: dict) -> None:
        for ws in list(self._connections.get(user_id, ())):
            await ws.send_json(payload)


manager = ConnectionManager()
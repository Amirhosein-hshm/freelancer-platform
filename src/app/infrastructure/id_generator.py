from uuid import uuid4

from app.application.shared.ports import IIdGenerator
from app.domain.shared.types import EntityId


class UuidIdGenerator(IIdGenerator):
    async def new_id(self) -> EntityId:
        return str(uuid4())
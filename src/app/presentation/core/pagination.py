from fastapi import Query
from pydantic import BaseModel


class PageQuery(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
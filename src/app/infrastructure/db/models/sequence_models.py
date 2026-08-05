from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class CodeSequenceModel(Base):
    __tablename__ = "code_sequences"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(10), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, nullable=False)
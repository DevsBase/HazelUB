from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class LocalState(Base):
    __tablename__ = "local_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installed: Mapped[bool] = mapped_column(Boolean, default=False)

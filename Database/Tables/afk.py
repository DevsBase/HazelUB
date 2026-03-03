from sqlalchemy import BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import datetime

class AFKState(Base):
    __tablename__ = "afk_state"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_afk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    time: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)

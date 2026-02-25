from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class RepeatState(Base):
    """Stores the global pause/resume state for a user's repeat messages."""
    __tablename__ = "repeat_states"

    userId: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

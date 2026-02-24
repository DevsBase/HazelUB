from sqlalchemy import Integer, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class RepeatMessage(Base):
    __tablename__ = "repeat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repeatTime: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    userId: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repeat_message_groups.id"),
        nullable=False
    )
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

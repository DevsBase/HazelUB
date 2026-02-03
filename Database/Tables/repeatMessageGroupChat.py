from sqlalchemy import Column, Integer, BigInteger, ForeignKey, UniqueConstraint
from .base import Base

class RepeatMessageGroupChat(Base):
    __tablename__ = "repeat_message_group_chats"

    id = Column(Integer, primary_key=True)
    userId = Column(BigInteger, nullable=False)
    group_id = Column(Integer, ForeignKey("repeat_message_groups.id"), nullable=False)
    chat_id = Column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint("group_id", "chat_id", name="uq_group_chat"),
    )

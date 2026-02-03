from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from .base import Base

class RepeatMessage(Base):
    __tablename__ = "repeat_messages"

    id = Column(Integer, primary_key=True)
    repeatTime = Column(Integer, default=1, nullable=False)
    userId = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    source_chat_id = Column(BigInteger, nullable=False)

    group_id = Column(
        Integer,
        ForeignKey("repeat_message_groups.id"),
        nullable=False
    )

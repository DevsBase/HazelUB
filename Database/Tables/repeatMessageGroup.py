from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, Integer, String, BigInteger
from .base import Base

class RepeatMessageGroup(Base):
    __tablename__ = "repeat_message_groups"

    id = Column(Integer, primary_key=True)
    userId = Column(BigInteger, nullable=False)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("userId", "name", name="uq_user_group_name"),
    )

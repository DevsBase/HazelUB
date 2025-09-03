from sqlalchemy import Column, String, Boolean
from ..base import Base

class AFK(Base):
  __tablename__ = "afk"
  user_id = Column(String, primary_key=True)
  reason = Column(String, nullable=True)
  is_afk = Column(Boolean, default=False, nullable=False)
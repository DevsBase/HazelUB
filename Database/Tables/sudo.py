from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Sudoers(Base):
    __tablename__ = "sudoers"

    owner_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

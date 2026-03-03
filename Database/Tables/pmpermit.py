from sqlalchemy import BigInteger, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class PMPermitSettings(Base):
    __tablename__ = "pmpermit_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    pm_message: Mapped[str] = mapped_column(String, nullable=True)


class PMPermitApproved(Base):
    __tablename__ = "pmpermit_approved"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    approved_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

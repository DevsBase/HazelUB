from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .Methods import Methods
from sqlalchemy import text
from .base import Base
from . import tables
import logging

log = logging.getLogger(__name__)

class Database(Methods):
  def __init__(self, db_url: str):
    self.engine = create_async_engine(db_url, echo=False, future=True)
    self.Session = sessionmaker(
      self.engine,
      expire_on_commit=False,
      class_=AsyncSession
    )

  async def init(self) -> None:
    log.info('Initiating Database')
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
      if "sqlite" in str(self.engine.url.drivername):
        await conn.execute(text("PRAGMA journal_mode=WAL;"))
        setattr(self, "SQLType", "sqlite")
      else: setattr(self, "SQLType", "postgresql")
    log.info(f"Database Initiated. Using {self.SQLType}.")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .base import Base
import .tables 

class Database:
  def __init__(self, db_url: str):
    self.engine = create_async_engine(db_url, echo=False, future=True)
    self.Session = sessionmaker(
      self.engine,
      expire_on_commit=False,
      class_=AsyncSession
    )

  async def init(self) -> None:
    async with self.engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
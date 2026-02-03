from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from .Tables.base import Base
from .Tables.loader import load_models
from .Tables.local import LocalState
from .Methods import Methods

class DBClient(Methods):
    def __init__(self, pg_url: str, sqlite_path="HazelUB.db"):
        self.pg_url = pg_url
        self.sqlite_url = f"sqlite+aiosqlite:///{sqlite_path}"
        
        load_models()
        
        # Engines
        self.pg_engine = create_async_engine(pg_url, echo=False)
        self.local_engine = create_async_engine(self.sqlite_url, echo=False)

        # Sessions
        self.pg_session = async_sessionmaker(
            self.pg_engine, expire_on_commit=False
        )
        self.local_session = async_sessionmaker(
            self.local_engine, expire_on_commit=False
        )

    async def init(self):
        # Create tables on both DBs
        async with self.pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self.local_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Ensure local row exists
        async with self.local_session() as session:
            res = await session.get(LocalState, 1)
            if not res:
                session.add(LocalState(id=1, installed=False))
                await session.commit()

    # ---------- Local helpers ----------

    async def is_installed(self) -> bool:
        async with self.local_session() as session:
            row = await session.get(LocalState, 1)
            return row.installed # type: ignore

    async def set_installed(self, value: bool):
        async with self.local_session() as session:
            row = await session.get(LocalState, 1)
            row.installed = value # type: ignore
            await session.commit()

    # ---------- Generic access ----------

    def get_pg(self) -> AsyncSession:
        return self.pg_session()

    def get_local(self) -> AsyncSession:
        return self.local_session()

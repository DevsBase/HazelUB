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
        # If DB_URL is not set it fallsback to sqllite
        self.db_url = pg_url if pg_url else f"sqlite+aiosqlite:///{sqlite_path}"
        
        load_models()
        
        # Main Engine
        self.engine = create_async_engine(self.db_url, echo=False)

        # Main Session
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def init(self):
        # Create tables on the DB
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Ensure local row exists in the now-unified DB
        async with self.session_factory() as session:
            res = await session.get(LocalState, 1)
            if not res:
                session.add(LocalState(id=1, installed=False))
                await session.commit()

    # ---------- Session helpers ----------

    def get_db(self) -> AsyncSession:
        """Returns the main database session."""
        return self.session_factory()

    def get_pg(self) -> AsyncSession:
        """Alias for get_db (deprecated)"""
        return self.get_db()

    def get_local(self) -> AsyncSession:
        """Alias for get_db (deprecated)"""
        return self.get_db()

    # ---------- Local helpers ----------

    async def is_installed(self) -> bool:
        async with self.get_db() as session:
            row = await session.get(LocalState, 1)
            return row.installed if row else False # type: ignore

    async def set_installed(self, value: bool):
        async with self.get_db() as session:
            row = await session.get(LocalState, 1)
            if row:
                row.installed = value # type: ignore
                await session.commit()

"""Database client module for HazelUB.

Provides the ``DBClient`` class which wraps SQLAlchemy's async engine
and session factory to manage all database operations.  It supports
both PostgreSQL and SQLite backends and exposes high-level helpers
for session management and local-state bookkeeping.
"""

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
    """Async database client that manages engine creation, session
    factories, and table initialisation for HazelUB.

    Inherits every database *method* from :class:`Methods`, keeping
    this class focused on connection setup and local-state helpers.
    """

    def __init__(self, pg_url: str, sqlite_path: str = "HazelUB.db") -> None:
        """Initialise the database client.

        Args:
            pg_url: A PostgreSQL connection URL.  If empty or falsy the
                client falls back to a local SQLite database.
            sqlite_path: Filename (or path) for the SQLite fallback
                database.  Defaults to ``"HazelUB.db"``.
        """
        # If DB_URL is not set it falls back to SQLite
        self.db_url = pg_url if pg_url else f"sqlite+aiosqlite:///{sqlite_path}"
        
        load_models()
        
        # Main Engine
        self.engine = create_async_engine(self.db_url, echo=False)

        # Main Session
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def init(self) -> None:
        """Create all tables and ensure the default local-state row exists.

        This **must** be awaited once at startup before any other
        database operations are performed.
        """
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
        """Check whether the bot has completed its first-time setup.

        Returns:
            ``True`` if the ``installed`` flag is set in the local
            state table, ``False`` otherwise.
        """
        async with self.get_db() as session:
            row = await session.get(LocalState, 1)
            return row.installed if row else False # type: ignore

    async def set_installed(self, value: bool) -> None:
        """Update the first-time setup flag in the local state table.

        Args:
            value: ``True`` to mark the bot as installed, ``False``
                to reset it.
        """
        async with self.get_db() as session:
            row = await session.get(LocalState, 1)
            if row:
                row.installed = value # type: ignore
                await session.commit()

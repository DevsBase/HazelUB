from sqlalchemy import select, delete
from Database.Tables.sudo import Sudoers

class SudoMethods:
    """Database mixin providing CRUD operations for sudo-user management.

    Sudo users are Telegram accounts that are granted elevated permissions
    to execute owner-only commands on behalf of a specific client account.
    The relationship is stored as a composite primary key
    ``(owner_id, user_id)`` in the :class:`Sudoers` table, meaning each
    owner independently maintains their own list of trusted users.

    Note:
        This class is intended to be used as a mixin.  It expects
        ``self.get_db()`` to return an async context manager yielding a
        SQLAlchemy :class:`AsyncSession`.
    """

    async def add_sudo(self, owner_id: int, user_id: int):
        """Grant sudo privileges to a user for a specific owner account.

        If the ``(owner_id, user_id)`` pair already exists the method is
        a no-op and returns ``False``, preventing duplicate rows.

        Args:
            owner_id (int): Telegram user ID of the client account that
                is granting sudo access.
            user_id (int): Telegram user ID of the user being granted
                sudo privileges.

        Returns:
            bool: ``True`` if the sudo entry was newly created, ``False``
            if the user was already a sudoer for this owner.
        """
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, {"owner_id": owner_id, "user_id": user_id})
            if not res:
                session.add(Sudoers(owner_id=owner_id, user_id=user_id))
                await session.commit()
                return True
            return False

    async def remove_sudo(self, owner_id: int, user_id: int):
        """Revoke sudo privileges from a user for a specific owner account.

        If the ``(owner_id, user_id)`` pair does not exist, the operation
        is a silent no-op.

        Args:
            owner_id (int): Telegram user ID of the client account that
                is revoking access.
            user_id (int): Telegram user ID of the user whose sudo
                privileges are being removed.
        """
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(Sudoers).where(
                    Sudoers.owner_id == owner_id,
                    Sudoers.user_id == user_id
                )
            )
            await session.commit()

    async def get_sudoers(self, owner_id: int = 0) -> list[int]:
        """Retrieve a flat list of sudo user IDs.

        When *owner_id* is provided the list is scoped to that owner's
        sudoers only.  When omitted (or ``0``), **all** sudo user IDs
        across every owner are returned (useful for pre-loading the
        in-memory ``sudoers`` cache at startup).

        Args:
            owner_id (int, optional): Telegram user ID of the owner to
                filter by. Pass ``0`` (default) to retrieve sudo user IDs
                for all owners.

        Returns:
            list[int]: A flat list of Telegram user IDs with sudo access.
        """
        async with self.get_db() as session: # type: ignore
            if owner_id:
                q = await session.execute(
                    select(Sudoers.user_id).where(Sudoers.owner_id == owner_id)
                )
            else:
                q = await session.execute(select(Sudoers.user_id))
            return [x[0] for x in q.all()]
            
    async def get_all_sudoers_map(self) -> dict[int, list[int]]:
        """Build a complete owner → sudoers mapping from the database.

        This is typically called once at startup to populate the in-memory
        ``Hazel.sudoers`` dictionary, which is then used by the
        :class:`Decorators` mixin for fast per-message authorisation
        checks.

        Returns:
            dict[int, list[int]]: A dictionary keyed by *owner_id* where
            each value is a list of *user_id* values that have sudo
            access for that owner.
        """
        async with self.get_db() as session: # type: ignore
            q = await session.execute(select(Sudoers))
            res = {}
            for row in q.scalars().all():
                if row.owner_id not in res:
                    res[row.owner_id] = []
                res[row.owner_id].append(row.user_id)
            return res

    async def is_sudo(self, owner_id: int, user_id: int) -> bool:
        """Check whether a user has sudo privileges for a given owner.

        Performs a direct primary-key lookup, making this the most
        efficient way to verify sudo status for a single user.

        Args:
            owner_id (int): Telegram user ID of the client account.
            user_id (int): Telegram user ID to check.

        Returns:
            bool: ``True`` if the user is a sudoer for *owner_id*,
            ``False`` otherwise.
        """
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, {"owner_id": owner_id, "user_id": user_id})
            return bool(res)

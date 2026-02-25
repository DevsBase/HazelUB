from sqlalchemy import select, delete
from Database.Tables.repeatMessage import RepeatMessage
from Database.Tables.repeatMessageGroup import RepeatMessageGroup
from Database.Tables.repeatMessageGroupChat import RepeatMessageGroupChat


class RepeatMethods:
    """Database mixin providing CRUD operations for the repeat-message system.

    The repeat-message system is organised around three entities:

    * **Groups** (:class:`RepeatMessageGroup`) – Named containers owned by a
      user, used to organise a set of target chats.
    * **Group Chats** (:class:`RepeatMessageGroupChat`) – Individual Telegram
      chat IDs assigned to a group. A repeated message is forwarded to every
      chat in its group.
    * **Repeat Messages** (:class:`RepeatMessage`) – Scheduled message
      records that link a source message to a group and define the repeat
      interval.

    All methods that accept a ``user_id`` enforce **ownership validation**:
    a user can only read, modify, or delete entities they own.

    Note:
        This class is intended to be used as a mixin.  It expects
        ``self.get_db()`` to return an async context manager yielding a
        SQLAlchemy :class:`AsyncSession`.
    """

    # ---------- Groups ----------

    async def create_group(self, name: str, user_id: int) -> RepeatMessageGroup:
        """Create a new repeat-message group.

        The *name* is normalised by stripping spaces and converting to
        lowercase before being persisted. Each ``(user_id, name)`` pair is
        unique (enforced by a database constraint).

        Args:
            name (str): Human-readable group name. Spaces are removed and
                the value is lowercased before storage.
            user_id (int): Telegram user ID of the group owner.

        Returns:
            RepeatMessageGroup: The newly created and committed group row,
            with its auto-generated ``id`` populated.
        """
        name = (name.replace(' ', '')).lower() # remove spaces and change to lower case
        async with self.get_db() as session: # type: ignore
            group = RepeatMessageGroup(userId=user_id, name=name)
            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    async def get_group(self, group_id: int, user_id: int):
        """Fetch a single group by its primary key, with ownership check.

        Args:
            group_id (int): Primary key of the group to retrieve.
            user_id (int): Telegram user ID of the requester. The group is
                only returned if it belongs to this user.

        Returns:
            RepeatMessageGroup | None: The group row if it exists **and**
            belongs to *user_id*, otherwise ``None``.
        """
        async with self.get_db() as session: # type: ignore
            x = await session.get(RepeatMessageGroup, group_id)
            if x.userId == user_id: # Check if the group belongs to the user.
                return x

    async def get_group_by_name(self, name: str, user_id: int):
        """Look up a group by its normalised name, with ownership check.

        The *name* is normalised (spaces stripped, lowercased) before the
        query, mirroring the normalisation applied in :meth:`create_group`.

        Args:
            name (str): Group name to search for (will be normalised).
            user_id (int): Telegram user ID of the requester.

        Returns:
            RepeatMessageGroup | None: The matching group row if found
            **and** owned by *user_id*, otherwise ``None``.
        """
        name = (name.replace(' ', '')).lower() # remove spaces and change to lower case
        async with self.get_db() as session: # type: ignore
            q = await session.execute(
                select(RepeatMessageGroup).where(
                    RepeatMessageGroup.name == name
                )
            )
            x = q.scalar_one_or_none()
            if x and x.userId == user_id: # Check if the group belongs to the user.
                return x
    
    async def get_groups(self, user_id: int):
        """Retrieve all repeat-message groups owned by a user.

        Args:
            user_id (int): Telegram user ID whose groups are requested.

        Returns:
            list[RepeatMessageGroup]: A list of all groups belonging to
            *user_id*. May be empty if the user has no groups.
        """
        async with self.get_db() as session:  # type: ignore
            q = await session.execute(
                select(RepeatMessageGroup)
                .where(RepeatMessageGroup.userId == user_id)
            )
            return q.scalars().all()

    async def delete_group(self, group_id: int, user_id: int):
        """Delete a group and all its associated chat memberships.

        Performs a **cascade delete**: all
        :class:`RepeatMessageGroupChat` rows linked to the group are
        removed first, followed by the group itself.

        Args:
            group_id (int): Primary key of the group to delete.
            user_id (int): Telegram user ID of the requester. Ownership
                is verified before deletion.

        Raises:
            Exception: If the group does not exist or does not belong to
                *user_id*.
        """
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(RepeatMessageGroupChat)
                .where(RepeatMessageGroupChat.group_id == group_id)
            )
            await session.execute(
                delete(RepeatMessageGroup)
                .where(RepeatMessageGroup.id == group_id)
            )
            await session.commit()

    # ---------- Group Chats ----------

    async def add_chat_to_group(self, group_id: int, chat_id: int, user_id: int):
        """Associate a Telegram chat with a repeat-message group.

        Each ``(group_id, chat_id)`` pair is unique (enforced by a
        database constraint), so adding the same chat twice will raise
        an integrity error.

        Args:
            group_id (int): Primary key of the target group.
            chat_id (int): Telegram chat / channel ID to add.
            user_id (int): Telegram user ID of the requester. Ownership
                of the group is verified before insertion.

        Returns:
            RepeatMessageGroupChat: The newly created association row.

        Raises:
            Exception: If the group does not exist or does not belong to
                *user_id*.
        """
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
        async with self.get_db() as session: # type: ignore
            row = RepeatMessageGroupChat(
                group_id=group_id,
                chat_id=chat_id,
                userId=user_id
            )
            session.add(row)
            await session.commit()
            return row

    async def remove_chat_from_group(self, group_id: int, chat_id: int, user_id: int):
        """Remove a Telegram chat from a repeat-message group.

        If the ``(group_id, chat_id)`` pair does not exist, the
        operation is a no-op (no error is raised).

        Args:
            group_id (int): Primary key of the target group.
            chat_id (int): Telegram chat / channel ID to remove.
            user_id (int): Telegram user ID of the requester. Ownership
                of the group is verified before deletion.

        Raises:
            Exception: If the group does not exist or does not belong to
                *user_id*.
        """
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(RepeatMessageGroupChat)
                .where(
                    RepeatMessageGroupChat.group_id == group_id,
                    RepeatMessageGroupChat.chat_id == chat_id
                )
            )
            await session.commit()

    async def get_group_chats(self, group_id: int, user_id: int) -> list[int]:
        """Return all chat IDs that belong to a group.

        Args:
            group_id (int): Primary key of the target group.
            user_id (int): Telegram user ID of the requester. Ownership
                of the group is verified first.

        Returns:
            list[int]: A flat list of Telegram chat IDs associated with
            the group.

        Raises:
            Exception: If the group does not exist or does not belong to
                *user_id*.
        """
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
        async with self.get_db() as session: # type: ignore
            q = await session.execute(
                select(RepeatMessageGroupChat.chat_id)
                .where(RepeatMessageGroupChat.group_id == group_id)
            )
            return [x[0] for x in q.all()]

    # ---------- Repeat Messages ----------

    async def create_repeat_message(
        self,
        repeatTime: int,
        userId: int,
        message_id: int,
        source_chat_id: int,
        group_id: int
    ):
        """Schedule a new repeated message.

        Creates a :class:`RepeatMessage` row linking a source message to a
        group of target chats, with a defined repeat interval.

        Args:
            repeatTime (int): Interval between repeats, in seconds.
            userId (int): Telegram user ID of the message owner.
            message_id (int): Telegram message ID of the source message
                to be forwarded / copied on each repeat.
            source_chat_id (int): Telegram chat ID where the source
                message resides.
            group_id (int): Primary key of the :class:`RepeatMessageGroup`
                whose chats will receive the repeated message.

        Returns:
            RepeatMessage: The newly created and committed row, with its
            auto-generated ``id`` populated.
        """
        async with self.get_db() as session: # type: ignore
            row = RepeatMessage(
                repeatTime=repeatTime,
                userId=userId,
                message_id=message_id,
                source_chat_id=source_chat_id,
                group_id=group_id
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return row

    async def get_repeat_messages(self) -> list[RepeatMessage]:
        """Retrieve all scheduled repeat messages across every user.

        This is typically called by the background repeater task to
        determine which messages need to be sent.

        Returns:
            list[RepeatMessage]: Every :class:`RepeatMessage` row in the
            database, regardless of owner or paused state.
        """
        async with self.get_db() as session: # type: ignore
            q = await session.execute(
                select(RepeatMessage)
            )
            return q.scalars().all()

    async def delete_repeat_message(self, repeat_id: int):
        """Delete a scheduled repeat message by its ID.

        Args:
            repeat_id (int): Primary key of the :class:`RepeatMessage`
                row to remove.
        """
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(RepeatMessage)
                .where(RepeatMessage.id == repeat_id)
            )
            await session.commit()

    async def set_repeat_state(self, user_id: int, is_paused: bool) -> None:
        """Pause or resume all repeat messages for a given user.

        Updates the ``is_paused`` flag on every :class:`RepeatMessage`
        owned by *user_id* in a single transaction.

        Args:
            user_id (int): Telegram user ID whose repeat messages should
                be updated.
            is_paused (bool): ``True`` to pause all repeats, ``False`` to
                resume them.
        """
        async with self.get_db() as session: # type: ignore
            q = await session.execute(
                select(RepeatMessage).where(RepeatMessage.userId == user_id)
            )
            rows = q.scalars().all()
            for r in rows:
                r.is_paused = is_paused
            await session.commit()
from sqlalchemy import select, delete
from Database.Tables.repeatMessage import RepeatMessage
from Database.Tables.repeatMessageGroup import RepeatMessageGroup
from Database.Tables.repeatMessageGroupChat import RepeatMessageGroupChat


class RepeatMethods:
    # ---------- Groups ----------

    async def create_group(self, name: str, user_id: int) -> RepeatMessageGroup:
        name = (name.replace(' ', '')).lower() # remove spaces and change to lower case
        async with self.get_db() as session: # type: ignore
            group = RepeatMessageGroup(userId=user_id, name=name)
            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    async def get_group(self, group_id: int, user_id: int):
        async with self.get_db() as session: # type: ignore
            x = await session.get(RepeatMessageGroup, group_id)
            if x.userId == user_id: # Check if the group belongs to the user.
                return x

    async def get_group_by_name(self, name: str, user_id: int):
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
        async with self.get_db() as session:  # type: ignore
            q = await session.execute(
                select(RepeatMessageGroup)
                .where(RepeatMessageGroup.userId == user_id)
            )
            return q.scalars().all()

    async def delete_group(self, group_id: int, user_id: int):
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
        async with self.get_db() as session: # type: ignore
            q = await session.execute(
                select(RepeatMessage)
            )
            return q.scalars().all()

    async def delete_repeat_message(self, repeat_id: int):
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(RepeatMessage)
                .where(RepeatMessage.id == repeat_id)
            )
            await session.commit()
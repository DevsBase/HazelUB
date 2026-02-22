from sqlalchemy import select, delete
from Database.Tables.sudo import Sudoers

class SudoMethods:
    async def add_sudo(self, user_id: int):
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, user_id)
            if not res:
                session.add(Sudoers(user_id=user_id))
                await session.commit()
                return True
            return False

    async def remove_sudo(self, user_id: int):
        async with self.get_db() as session: # type: ignore
            await session.execute(delete(Sudoers).where(Sudoers.user_id == user_id))
            await session.commit()

    async def get_sudoers(self) -> list[int]:
        async with self.get_db() as session: # type: ignore
            q = await session.execute(select(Sudoers.user_id))
            return [x[0] for x in q.all()]

    async def is_sudo(self, user_id: int) -> bool:
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, user_id)
            return bool(res)

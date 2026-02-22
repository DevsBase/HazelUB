from sqlalchemy import select, delete
from Database.Tables.sudo import Sudoers

class SudoMethods:
    async def add_sudo(self, owner_id: int, user_id: int):
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, {"owner_id": owner_id, "user_id": user_id})
            if not res:
                session.add(Sudoers(owner_id=owner_id, user_id=user_id))
                await session.commit()
                return True
            return False

    async def remove_sudo(self, owner_id: int, user_id: int):
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(Sudoers).where(
                    Sudoers.owner_id == owner_id,
                    Sudoers.user_id == user_id
                )
            )
            await session.commit()

    async def get_sudoers(self, owner_id: int = 0) -> list[int]:
        """Returns sudoers for a specific owner or all if owner_id is 0."""
        async with self.get_db() as session: # type: ignore
            if owner_id:
                q = await session.execute(
                    select(Sudoers.user_id).where(Sudoers.owner_id == owner_id)
                )
            else:
                q = await session.execute(select(Sudoers.user_id))
            return [x[0] for x in q.all()]
            
    async def get_all_sudoers_map(self) -> dict[int, list[int]]:
        """Returns a mapping of owner_id to list of sudoers."""
        async with self.get_db() as session: # type: ignore
            q = await session.execute(select(Sudoers))
            res = {}
            for row in q.scalars().all():
                if row.owner_id not in res:
                    res[row.owner_id] = []
                res[row.owner_id].append(row.user_id)
            return res

    async def is_sudo(self, owner_id: int, user_id: int) -> bool:
        async with self.get_db() as session: # type: ignore
            res = await session.get(Sudoers, {"owner_id": owner_id, "user_id": user_id})
            return bool(res)

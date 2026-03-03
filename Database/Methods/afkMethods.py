import datetime
from typing import Optional, Tuple
from Database.Tables.afk import AFKState
from sqlalchemy import select

class AFKMethods:
    async def get_afk(self, user_id: int) -> Tuple[bool, Optional[str], Optional[datetime.datetime]]:
        """Get AFK state for a user."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(AFKState).where(AFKState.user_id == user_id))
            state = result.scalar_one_or_none()
            if state:
                return state.is_afk, state.reason, state.time
            return False, None, None

    async def set_afk(self, user_id: int, is_afk: bool, reason: Optional[str] = None) -> None:
        """Set AFK state for a user."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(AFKState).where(AFKState.user_id == user_id))
            state = result.scalar_one_or_none()
            
            if state:
                state.is_afk = is_afk
                state.reason = reason
                state.time = datetime.datetime.utcnow()
            else:
                new_state = AFKState(
                    user_id=user_id,
                    is_afk=is_afk,
                    reason=reason,
                    time=datetime.datetime.utcnow()
                )
                session.add(new_state)
            await session.commit()

import datetime
from typing import Optional, Tuple, Dict
from Database.Tables.afk import AFKState
from sqlalchemy import select

_afk_cache: Dict[int, Tuple[bool, Optional[str], Optional[datetime.datetime]]] = {}

class AFKMethods:
    async def get_afk(self, user_id: int) -> Tuple[bool, Optional[str], Optional[datetime.datetime]]:
        """Get AFK state for a user (cached)."""
        if user_id in _afk_cache:
            return _afk_cache[user_id]
            
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(AFKState).where(AFKState.user_id == user_id))
            state = result.scalar_one_or_none()
            if state:
                _afk_cache[user_id] = (state.is_afk, state.reason, state.time)
                return _afk_cache[user_id]
            
            _afk_cache[user_id] = (False, None, None)
            return _afk_cache[user_id]

    async def set_afk(self, user_id: int, is_afk: bool, reason: Optional[str] = None) -> None:
        """Set AFK state for a user and update cache."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(AFKState).where(AFKState.user_id == user_id))
            state = result.scalar_one_or_none()
            
            time_now = datetime.datetime.utcnow()
            
            if state:
                state.is_afk = is_afk
                state.reason = reason
                state.time = time_now
            else:
                new_state = AFKState(
                    user_id=user_id,
                    is_afk=is_afk,
                    reason=reason,
                    time=time_now
                )
                session.add(new_state)
            await session.commit()
            
            _afk_cache[user_id] = (is_afk, reason, time_now)

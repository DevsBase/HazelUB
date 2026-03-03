from typing import List, Optional
from Database.Tables.pmpermit import PMPermitSettings, PMPermitApproved
from sqlalchemy import select, delete

class PMPermitMethods:
    async def is_pmpermit_enabled(self, user_id: int) -> bool:
        """Check if PMPermit is enabled for a given user client."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings.is_enabled).where(PMPermitSettings.user_id == user_id))
            state = result.scalar_one_or_none()
            return state if state is not None else False

    async def set_pmpermit(self, user_id: int, is_enabled: bool) -> None:
        """Enable or disable PMPermit for a user client."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings).where(PMPermitSettings.user_id == user_id))
            settings = result.scalar_one_or_none()
            if settings:
                settings.is_enabled = is_enabled
            else:
                settings = PMPermitSettings(user_id=user_id, is_enabled=is_enabled)
                session.add(settings)
            await session.commit()

    async def get_pmpermit_limit(self, user_id: int) -> int:
        """Get the PMPermit warning limit."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings.limit).where(PMPermitSettings.user_id == user_id))
            limit = result.scalar_one_or_none()
            return limit if limit is not None else 5

    async def set_pmpermit_limit(self, user_id: int, limit: int) -> None:
        """Set the PMPermit warning limit."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings).where(PMPermitSettings.user_id == user_id))
            settings = result.scalar_one_or_none()
            if settings:
                settings.limit = limit
            else:
                settings = PMPermitSettings(user_id=user_id, limit=limit)
                session.add(settings)
            await session.commit()

    async def get_pmpermit_message(self, user_id: int) -> Optional[str]:
        """Get the custom PMPermit warning message."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings.pm_message).where(PMPermitSettings.user_id == user_id))
            return result.scalar_one_or_none()

    async def set_pmpermit_message(self, user_id: int, message: Optional[str]) -> None:
        """Set the custom PMPermit warning message."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(select(PMPermitSettings).where(PMPermitSettings.user_id == user_id))
            settings = result.scalar_one_or_none()
            if settings:
                settings.pm_message = message
            else:
                settings = PMPermitSettings(user_id=user_id, pm_message=message) # type: ignore
                session.add(settings)
            await session.commit()

    async def is_approved(self, user_id: int, approved_user_id: int) -> bool:
        """Check if a specific user is approved to PM this user client."""
        async with self.get_db() as session: # type: ignore
            result = await session.execute(
                select(PMPermitApproved).where(
                    PMPermitApproved.user_id == user_id,
                    PMPermitApproved.approved_user_id == approved_user_id
                )
            )
            return result.scalar_one_or_none() is not None

    async def approve_user(self, user_id: int, approved_user_id: int) -> None:
        """Approve a user to PM this user client."""
        if await self.is_approved(user_id, approved_user_id):
            return
            
        async with self.get_db() as session: # type: ignore
            approved = PMPermitApproved(user_id=user_id, approved_user_id=approved_user_id)
            session.add(approved)
            await session.commit()

    async def disapprove_user(self, user_id: int, approved_user_id: int) -> None:
        """Disapprove a user from PMing this user client."""
        async with self.get_db() as session: # type: ignore
            await session.execute(
                delete(PMPermitApproved).where(
                    PMPermitApproved.user_id == user_id,
                    PMPermitApproved.approved_user_id == approved_user_id
                )
            )
            await session.commit()

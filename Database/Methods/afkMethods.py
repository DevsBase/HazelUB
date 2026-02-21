from typing import Optional, Dict, Any
import time

class AFKMethods:
    async def set_afk(self, user_id: int, reason: str):
        """Enable AFK status for a user."""
        await self.db["afk"].update_one(
            {"user_id": user_id},
            {"$set": {"reason": reason, "time": time.time()}},
            upsert=True
        )

    async def get_afk(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve AFK information for a user."""
        return await self.db["afk"].find_one({"user_id": user_id})

    async def remove_afk(self, user_id: int) -> bool:
        """Disable AFK status for a user."""
        result = await self.db["afk"].delete_one({"user_id": user_id})
        return result.deleted_count > 0

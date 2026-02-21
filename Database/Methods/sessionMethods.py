from typing import List, Optional

class SessionMethods:
    async def add_session(self, session_string: str) -> bool:
        """Add a new session string to the database if it doesn't already exist."""
        existing = await self.db["sessions"].find_one({"session": session_string})
        if not existing:
            await self.db["sessions"].insert_one({"session": session_string})
            return True
        return False

    async def get_all_sessions(self) -> List[str]:
        """Retrieve all extra session strings from the database."""
        cursor = self.db["sessions"].find({})
        sessions = await cursor.to_list(length=100)
        return [s["session"] for s in sessions]

    async def remove_session(self, session_string: str) -> bool:
        """Remove a session string from the database."""
        result = await self.db["sessions"].delete_one({"session": session_string})
        return result.deleted_count > 0

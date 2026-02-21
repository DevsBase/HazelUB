from typing import List, Optional
import logging

logger = logging.getLogger("Hazel.SudoMethods")

class SudoMethods:
    # MongoDB collections are initialized in MongoClient
    # We use Redis for fast lookup: "sudo_list" and "fsudo_list" (Sets)

    async def add_sudo(self, user_id: int, level: str = "sudo"):
        """
        level can be 'sudo' or 'fsudo'
        """
        user_id = int(user_id)
        # 1. Store in MongoDB
        collection = self.db["sudo_users"]
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {"level": level}},
            upsert=True
        )
        
        # 2. Update Redis
        from Hazel import Redis
        if Redis:
            set_name = f"{level}_list"
            await Redis.redis.sadd(set_name, str(user_id))
            
        logger.info(f"Added user {user_id} as {level}")

    async def remove_sudo(self, user_id: int):
        user_id = int(user_id)
        # 1. Remove from MongoDB
        collection = self.db["sudo_users"]
        await collection.delete_one({"user_id": user_id})
        
        # 2. Remove from Redis
        from Hazel import Redis
        if Redis:
            await Redis.redis.srem("sudo_list", str(user_id))
            await Redis.redis.srem("fsudo_list", str(user_id))
            
        logger.info(f"Removed user {user_id} from sudo list")

    async def get_all_sudo(self) -> List[dict]:
        collection = self.db["sudo_users"]
        return await collection.find({}).to_list(length=None)

    async def is_sudo(self, user_id: int) -> bool:
        user_id = int(user_id)
        from Hazel import Redis
        if Redis:
            # Check both as strings (we store them as strings in Redis)
            res1 = await Redis.redis.sismember("sudo_list", str(user_id))
            res2 = await Redis.redis.sismember("fsudo_list", str(user_id))
            is_it = bool(res1 or res2)
            return is_it
        
        collection = self.db["sudo_users"]
        res = await collection.find_one({"user_id": user_id})
        return res is not None

    async def is_fsudo(self, user_id: int) -> bool:
        user_id = int(user_id)
        from Hazel import Redis
        if Redis:
            res = await Redis.redis.sismember("fsudo_list", str(user_id))
            return bool(res)
            
        collection = self.db["sudo_users"]
        res = await collection.find_one({"user_id": user_id, "level": "fsudo"})
        return res is not None

    async def reload_sudo_cache(self):
        """Load all sudo users from Mongo into Redis."""
        from Hazel import Redis
        if not Redis: return
        
        # Clear existing
        await Redis.redis.delete("sudo_list")
        await Redis.redis.delete("fsudo_list")
        
        all_users = await self.get_all_sudo()
        for u in all_users:
            level = u.get("level", "sudo")
            await Redis.redis.sadd(f"{level}_list", str(u["user_id"]))
        
        logger.info(f"Reloaded {len(all_users)} sudo users into Redis cache")

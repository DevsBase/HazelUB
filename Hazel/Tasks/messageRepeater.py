import asyncio
import logging
from MultiSessionManagement.telegram import Telegram
from pyrogram.client import Client
from pyrogram.errors import FloodWait
from typing import TYPE_CHECKING, Dict, Any
import traceback

logger = logging.getLogger("Hazel.Tasks.messageRepeater")

if TYPE_CHECKING:
    from Database.mongo_client import MongoClient
    events: Dict[int, asyncio.Event] # int is client's user_id
else:
    MongoClient = Any
    events = {}

async def createJob(job: dict, chats: list, client: Client):
    while True:
        try:
            repeat_time = job.get("repeatTime", 1)
            await asyncio.sleep(int(repeat_time * 60)) # type: ignore # Convert sec to mins 
            
            user_id = job.get("userId")
            if user_id in events:
                await events[user_id].wait() # type: ignore
            
            for chat_id in chats:
                try:
                    await client.copy_message(
                        chat_id=chat_id,
                        from_chat_id=job.get("source_chat_id"), # type: ignore
                        message_id=job.get("message_id") # type: ignore
                    )
                    await asyncio.sleep(2.59)
                except FloodWait as e:
                    logger.critical(f"FloodWaitError: Sleeping for {e.value}.")
                    await asyncio.sleep(e.value) # type: ignore
                except Exception as e:
                    logger.error(f"Could not send repeat message for user: {client.me.id} at chat: {chat_id}. RepeatMessage ID: {job.get('_id')}. Error: {e}") # type: ignore
        except Exception as e:
            logger.error(f"Failed to do repeat task for user: {job.get('userId')}: Full Traceback: {traceback.format_exc()}")
            
async def main(Tele: Telegram, db: MongoClient):
    jobs = await db.get_repeat_messages()

    for job in jobs:
        for client in Tele._allClients:
            # client.me might be None if not started, but Tele.start (in Setup/main.py) is called before this.
            if client.me and client.me.id == job.get("userId"): # type: ignore
                user_id = job.get("userId")
                if user_id not in events:
                    events[user_id] = asyncio.Event() # type: ignore
                    events[user_id].set() # type: ignore
                
                group_id = job.get("group_id")
                chats = await db.get_group_chats(group_id, user_id=client.me.id) # type: ignore
                asyncio.create_task(createJob(job, chats, client))
                logger.info(f"Created repeat message job for user {user_id} in group {group_id}") # type: ignore
    logger.info(f"Loaded {len(jobs)} repeat message jobs.")
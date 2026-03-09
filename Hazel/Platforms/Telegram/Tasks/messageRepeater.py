import asyncio
import logging
from Hazel.Platforms.Telegram import Telegram
from pyrogram.client import Client
from Database.client import DBClient
from Database.Tables.repeatMessage import RepeatMessage
from pyrogram.errors import FloodWait
from typing import TYPE_CHECKING, Dict
import traceback

logger = logging.getLogger("Hazel.Tasks.messageRepeater")

if TYPE_CHECKING:
    events: Dict[int, asyncio.Event] # Mapping of client user ids to their pause/resume events.
else:
    events: Dict[int, asyncio.Event] = {}

async def createJob(job: RepeatMessage, chats: list[int], client: Client) -> None:
    """Run an infinite loop that periodically copies a message to target chats."""
    while True:
        try:
            await asyncio.sleep(int(job.repeatTime * 60)) # Convert sec to mins 
            if job.userId in events:
                await events[job.userId].wait()
            chat_id: int = 0
            for chat_id in chats:
                try:
                    await client.copy_message(
                        chat_id=chat_id,
                        from_chat_id=job.source_chat_id,
                        message_id=job.message_id
                    )
                    await asyncio.sleep(2.59)
                except FloodWait as e:
                    logger.critical(f"FloodWaitError: Sleeping for {e.value}.")
                    await asyncio.sleep(e.value) # type: ignore
                except Exception as e:
                    logger.error(f"Could not send repeat message for user: {client.me.id} at chat: {chat_id}. RepeatMessage ID: {job.id}. Error: {e}") # type: ignore
        except Exception as e:
            logger.error(f"Failed to do repeat task for user: {job.userId}: Full Traceback: {traceback.format_exc()}")
            
async def main(Tele: Telegram, db: DBClient) -> None:
    """Bootstrap all stored repeat-message jobs at startup."""
    jobs: list[RepeatMessage] = await db.get_repeat_messages()
    jobs_created = 0

    for job in jobs:
        for client in Tele._allClients:
            
            client_id: int = int(client.me.id) if client.me else 0
            job_user_id: int = int(job.userId)

            if client_id == job_user_id:
                if job_user_id not in events:
                    events[job_user_id] = asyncio.Event() 
                    is_paused = await db.get_repeat_state(job_user_id)
                    if not is_paused:
                        events[job_user_id].set() 
                
                chats: list[int] = await db.get_group_chats(int(job.group_id), user_id=client_id)
                asyncio.create_task(createJob(job, chats, client))
                jobs_created += 1
                logger.info(f"Created repeat message job for user {job_user_id} in group {job.group_id}")
    logger.info(f"Loaded {jobs_created} repeat message jobs.")
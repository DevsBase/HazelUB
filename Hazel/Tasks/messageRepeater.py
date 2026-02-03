import asyncio
import logging
from MultiSessionManagement.telegram import Telegram
from pyrogram.client import Client
from Database.client import DBClient
from Database.Tables.repeatMessage import RepeatMessage
from pyrogram.errors import FloodWait

logger = logging.getLogger("Hazel.Tasks.messageRepeater")

async def createJob(job: RepeatMessage, chats: list, client: Client):
    while True:
        try:
            await asyncio.sleep(int(job.repeatTime * 60)) # type: ignore # Convert sec to mins 
            chat_id: int = 0
            for chat_id in chats:
                await client.copy_message(
                    chat_id=chat_id,
                    from_chat_id=job.source_chat_id, # type: ignore
                    message_id=job.message_id # type: ignore
                )
                await asyncio.sleep(2.59)
        except FloodWait as e:
            logger.critical(f"FloodWaitError: Sleeping for {e.value}.")
            await asyncio.sleep(e.value) # type: ignore
        except Exception as e:
            logger.error(f"Could not send repeat message for user: {client.me.id} at chat: {chat_id}. RepeatMessage ID: {job.id}. Error: {e}") # type: ignore


async def main(Tele: Telegram, db: DBClient):
    jobs = await db.get_repeat_messages()

    for job in jobs:
        for client in Tele._allClients:
            if client.me.id == job.userId: # type: ignore
                chats = await db.get_group_chats(job.group_id, user_id=client.me.id) # type: ignore
                asyncio.create_task(createJob(job, chats, client))
                logger.info(f"Created repeat message job for user {job.userId} in group {job.group_id}") # type: ignore
    logger.info(f"Loaded {len(jobs)} repeat message jobs.")
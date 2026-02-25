import asyncio
import logging
from MultiSessionManagement.telegram import Telegram
from pyrogram.client import Client
from Database.client import DBClient
from Database.Tables.repeatMessage import RepeatMessage
from pyrogram.errors import FloodWait
from typing import TYPE_CHECKING, Dict
import traceback

logger = logging.getLogger("Hazel.Tasks.messageRepeater")

if TYPE_CHECKING:
    events: Dict[int, asyncio.Event] # Mapping of client user-IDs to their pause/resume events.
else:
    events: Dict[int, asyncio.Event] = {}

async def createJob(job: RepeatMessage, chats: list[int], client: Client) -> None:
    """Run an infinite loop that periodically copies a message to target chats.

    The loop sleeps for ``job.repeatTime`` minutes between iterations.
    If the owning client's :class:`asyncio.Event` is unset (paused),
    the loop blocks until it is resumed.  Individual ``FloodWait``
    errors are handled gracefully by sleeping for the required duration.

    Args:
        job: The :class:`RepeatMessage` row describing what to repeat.
        chats: List of chat IDs the message should be copied to.
        client: The Pyrogram client used to send the messages.
    """
    while True:
        try:
            await asyncio.sleep(int(job.repeatTime * 60)) # type: ignore # Convert sec to mins 
            if job.userId in events:
                await events[job.userId].wait() # type: ignore
            chat_id: int = 0
            for chat_id in chats:
                try:
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
        except Exception as e:
            logger.error(f"Failed to do repeat task for user: {job.userId}: Full Traceback: {traceback.format_exc()}")
            
async def main(Tele: Telegram, db: DBClient) -> None:
    """Bootstrap all stored repeat-message jobs at startup.

    Fetches every :class:`RepeatMessage` from the database, matches
    each job to its owning Pyrogram client, creates the corresponding
    pause/resume :class:`asyncio.Event`, and spawns background tasks
    via :func:`createJob`.

    Args:
        Tele: The multi-session manager holding all active clients.
        db: The database client used to query repeat-message data.
    """
    jobs: list[RepeatMessage] = await db.get_repeat_messages()

    for job in jobs:
        for client in Tele._allClients:
            # Type assertion to ensure IDEs understand the attribute types
            client_id: int = int(client.me.id) if client.me else 0
            job_user_id: int = int(job.userId) # type: ignore

            if client_id == job_user_id:
                if job_user_id not in events:
                    events[job_user_id] = asyncio.Event() 
                    is_paused = await db.get_repeat_state(job_user_id)
                    if not is_paused:
                        events[job_user_id].set() 
                
                chats: list[int] = await db.get_group_chats(int(job.group_id), user_id=client_id) # type: ignore
                asyncio.create_task(createJob(job, chats, client))
                logger.info(f"Created repeat message job for user {job_user_id} in group {job.group_id}") # type: ignore
    logger.info(f"Loaded {len(jobs)} repeat message jobs.")
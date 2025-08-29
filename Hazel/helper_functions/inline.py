import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Hazel import pending

async def send_button(client, user_id: int) -> bool:
  future = asyncio.get_running_loop().create_future()
    message = await BOT_CLIENT.send_message(
        chat_id=user_id,
        text=f"Please confirm the execution of the following code:\n\n```python\n{code}\n```",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Run", callback_data="run_code"),
                    InlineKeyboardButton("Cancel", callback_data="cancel_code"),
                ]
            ]
        ),
    )
    confirmation_requests[message.id] = (user_id, code, future)
    return await future

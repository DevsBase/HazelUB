import typing

if typing.TYPE_CHECKING:
    from pyrogram.types import Message

class MessageMethods:
    def __init__(self, message: Message):
        self.message = message
    
    async def delete(self) -> int | None:
        if not self.message.chat or not self.message.id:
            return False
        if self.message.business_connection_id:
            return await self.message._client.delete_business_messages(
                business_connection_id=self.message.business_connection_id,
                message_ids=[self.message.id],
            ) > 0
        
        await self.message.delete()

    async def edit(self, text: str, *args, **kwargs) -> Message | None:
        if not self.message.chat or not self.message.id or not self.message.chat.id:
            return
        if self.message.business_connection_id:
            return await self.message._client.edit_message_text(
                self.message.chat.id,
                message_id=self.message.id,
                text=text,
                business_connection_id=self.message.business_connection_id,
                *args,
                **kwargs
            )
        return await self.message._client.edit_message_text(
            self.message.chat.id,
            message_id=self.message.id,
            text=text,
            *args,
            **kwargs
        )
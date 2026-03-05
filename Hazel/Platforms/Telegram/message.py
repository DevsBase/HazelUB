from datetime import datetime
from typing import List, Optional

from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
    MessageEntity,
)

class MessageMethods:
    def __init__(self, message: Message):
        self.message = message

    async def delete(
        self, 
        business_connection_id: Optional[str] = None, 
        revoke: bool = True
    ) -> bool:
        if not self.message.chat or not self.message.id:
            return False
            
        bc_id = business_connection_id or getattr(self.message, "business_connection_id", None)
        
        if bc_id:
            result = await self.message._client.delete_business_messages(
                business_connection_id=bc_id,
                message_ids=[self.message.id],
            )
            return bool(result)
        
        return bool(await self.message.delete(revoke=revoke))

    async def edit(
        self,
        text: str,
        parse_mode: Optional[ParseMode] = None,
        entities: Optional[List[MessageEntity]] = None,
        link_preview_options: Optional[LinkPreviewOptions] = None,
        schedule_date: Optional[datetime] = None,
        business_connection_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        show_caption_above_media: Optional[bool] = None,
        disable_web_page_preview: Optional[bool] = None,
    ) -> Optional[Message]:
        
        chat_id = self.message.chat.id if self.message.chat else None
        if not chat_id or not self.message.id:
            return None

        params = {"chat_id": chat_id, "message_id": self.message.id, "text": text}

        if parse_mode is not None: params["parse_mode"] = parse_mode
        if entities is not None: params["entities"] = entities
        if link_preview_options is not None: params["link_preview_options"] = link_preview_options
        if schedule_date is not None: params["schedule_date"] = schedule_date
        if reply_markup is not None: params["reply_markup"] = reply_markup
        if show_caption_above_media is not None: params["show_caption_above_media"] = show_caption_above_media
        if disable_web_page_preview is not None: params["disable_web_page_preview"] = disable_web_page_preview

        bc_id = business_connection_id or getattr(self.message, "business_connection_id", None)
        if bc_id:
            params["business_connection_id"] = bc_id

        return await self.message._client.edit_message_text(**params)
from datetime import datetime
from typing import List, Optional, Union

from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
    MessageEntity,
    ReplyParameters
)
from pyrogram import types
from .inline import InlineMethods

class MessageMethods:
    def __init__(self, message: Message | types.InlineQuery) -> None:
        self.message = message

    async def delete(
        self, 
        business_connection_id: Optional[str] = None, 
        revoke: bool = True
    ) -> bool:
        if not isinstance(self.message, Message):
            raise ValueError("Delete method is only supported for Message objects.")
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
        
        if not isinstance(self.message, Message):
            raise ValueError("Delete method is only supported for Message objects.")
        
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
    
    async def reply(
        self,
        text: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        entities: Optional[List[MessageEntity]] = None,
        link_preview_options: Optional[LinkPreviewOptions] = None,
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        reply_parameters: Optional[ReplyParameters] = None,
        schedule_date: Optional[datetime] = None,
        repeat_period: Optional[int] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        reply_markup: Optional[
            Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply"
            ]
        ] = None,
    ) -> Optional[Message]:
        "supports replying to both messages and inline queries"
        if isinstance(self.message, Message):
            await self.message.reply(text, parse_mode, entities, link_preview_options, disable_notification, message_thread_id, direct_messages_topic_id, effect_id, show_caption_above_media, reply_parameters, schedule_date, repeat_period, protect_content, allow_paid_broadcast, paid_message_star_count, suggested_post_parameters, reply_markup)
        else:
            if isinstance(reply_markup, types.InlineKeyboardMarkup):
                await InlineMethods(self.message).answer_text(title or "No title", text, description or "", reply_markup=reply_markup, parse_mode=parse_mode, entities=entities, link_preview_options=link_preview_options)
            else:
                reply_markup = None
                await InlineMethods(self.message).answer_text(title or "No title", text, description or "", parse_mode=parse_mode, entities=entities, link_preview_options=link_preview_options)
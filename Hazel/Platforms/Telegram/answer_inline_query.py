from typing import TYPE_CHECKING, List, Any

from pyrogram.types import (
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    InlineQueryResultAudio,
    InlineQueryResultDocument,
    InputTextMessageContent,
    InlineKeyboardMarkup
)

if TYPE_CHECKING:
    from Hazel.Platforms.Telegram import Telegram


class AnswerInlineQuery:
    """Provides methods for conveniently answering Telegram inline queries with various media types."""

    def __init__(self, client: "Telegram") -> None:
        """Initialise the inline query handler with a Telegram client instance.

        Args:
            client (Telegram): The Telegram client orchestrator.
        """
        self.client = client

    async def answer_text(
        self,
        query: InlineQuery,
        title: str,
        text: str,
        description: str = "No description",
        reply_markup: InlineKeyboardMarkup | None = None,
        *content_args: Any,
        **content_kwargs: Any
    ):
        """Answer an inline query with a text article result.

        Args:
            query (InlineQuery): The incoming inline query to answer.
            title (str): The title of the result article.
            text (str): The actual message text to be sent when the result is selected.
            description (str, optional): A short description of the result. Defaults to "No description".
            *content_args: Variable positional arguments for InputTextMessageContent.
            **content_kwargs: Variable keyword arguments for InputTextMessageContent.

        Returns:
            The result of query.answer.
        """
        if reply_markup:
            results: List[InlineQueryResult] = [
                InlineQueryResultArticle(
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        text,
                        *content_args,
                        **content_kwargs
                    ),
                    reply_markup=reply_markup
                )
            ]
            return await query.answer(results=results, cache_time=0)

        results: List[InlineQueryResult] = [
            InlineQueryResultArticle(
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    text,
                    *content_args,
                    **content_kwargs
                ),
            )
        ]

        return await query.answer(results=results, cache_time=0)

    async def answer_photo(
        self,
        query: InlineQuery,
        photo_url: str,
        thumb_url: str,
        title: str,
        description: str = "",
        caption: str = "",
        *content_args: Any,
        **content_kwargs: Any
    ):
        """Answer an inline query with a photo result.

        Args:
            query (InlineQuery): The incoming inline query to answer.
            photo_url (str): A valid URL of the photo (JPEG, max 5MB).
            thumb_url (str): URL of the thumbnail for the photo.
            title (str): Title for the result.
            description (str, optional): Short description of the result. Defaults to "".
            caption (str, optional): Caption of the photo to be sent. Defaults to "".
            *content_args: Additional positional arguments for InlineQueryResultPhoto.
            **content_kwargs: Additional keyword arguments for InlineQueryResultPhoto.

        Returns:
            The result of query.answer.
        """
        results: List[InlineQueryResult] = [
            InlineQueryResultPhoto(
                photo_url=photo_url,
                thumb_url=thumb_url,
                title=title,
                description=description,
                caption=caption,
                *content_args,
                **content_kwargs
            )
        ]

        return await query.answer(results=results, cache_time=0)

    async def answer_video(
        self,
        query: InlineQuery,
        video_url: str,
        thumb_url: str,
        title: str,
        description: str = "",
        caption: str = "",
        *content_args: Any,
        **content_kwargs: Any
    ):
        """Answer an inline query with a video result.

        Args:
            query (InlineQuery): The incoming inline query to answer.
            video_url (str): A valid URL for the embedded video player or video file.
            thumb_url (str): URL of the thumbnail (JPEG or GIF) for the video.
            title (str): Title for the result.
            description (str, optional): Short description of the result. Defaults to "".
            caption (str, optional): Caption of the video to be sent. Defaults to "".
            *content_args: Additional positional arguments for InlineQueryResultVideo.
            **content_kwargs: Additional keyword arguments for InlineQueryResultVideo.

        Returns:
            The result of query.answer.
        """
        results: List[InlineQueryResult] = [
            InlineQueryResultVideo(
                video_url=video_url,
                mime_type="video/mp4",
                thumb_url=thumb_url,
                title=title,
                description=description,
                caption=caption,
                *content_args,
                **content_kwargs
            )
        ]

        return await query.answer(results=results, cache_time=0)

    async def answer_audio(
        self,
        query: InlineQuery,
        audio_url: str,
        title: str,
        caption: str = "",
        *content_args: Any,
        **content_kwargs: Any
    ):
        """Answer an inline query with an audio result.

        Args:
            query (InlineQuery): The incoming inline query to answer.
            audio_url (str): A valid URL for the audio file.
            title (str): Title for the result.
            caption (str, optional): Caption of the audio to be sent. Defaults to "".
            *content_args: Additional positional arguments for InlineQueryResultAudio.
            **content_kwargs: Additional keyword arguments for InlineQueryResultAudio.

        Returns:
            The result of query.answer.
        """
        results: List[InlineQueryResult] = [
            InlineQueryResultAudio(
                audio_url=audio_url,
                title=title,
                caption=caption,
                *content_args,
                **content_kwargs
            )
        ]

        return await query.answer(results=results, cache_time=0)

    async def answer_document(
        self,
        query: InlineQuery,
        document_url: str,
        title: str,
        mime_type: str,
        caption: str = "",
        *content_args: Any,
        **content_kwargs: Any
    ):
        """Answer an inline query with a document result.

        Args:
            query (InlineQuery): The incoming inline query to answer.
            document_url (str): A valid URL for the file to be sent.
            title (str): Title for the result.
            mime_type (str): Mime type of the content of the file, either “application/pdf” or “application/zip”.
            caption (str, optional): Caption of the document to be sent. Defaults to "".
            *content_args: Additional positional arguments for InlineQueryResultDocument.
            **content_kwargs: Additional keyword arguments for InlineQueryResultDocument.

        Returns:
            The result of query.answer.
        """
        results: List[InlineQueryResult] = [
            InlineQueryResultDocument(
                document_url=document_url,
                title=title,
                mime_type=mime_type,
                caption=caption,
                *content_args,
                **content_kwargs
            )
        ]

        return await query.answer(results=results, cache_time=0)
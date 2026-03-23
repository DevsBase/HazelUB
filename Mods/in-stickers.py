from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele

# ✅ Raw imports (Layer 222)
from pyrogram.raw.functions.stickers.create_sticker_set import CreateStickerSet
from pyrogram.raw.functions.stickers.add_sticker_to_set import AddStickerToSet
from pyrogram.raw.functions.messages.upload_media import UploadMedia

from pyrogram.raw.types.input_sticker_set_item import InputStickerSetItem
from pyrogram.raw.types.input_document import InputDocument
from pyrogram.raw.types.input_sticker_set_short_name import InputStickerSetShortName
from pyrogram.raw.types.input_media_uploaded_document import InputMediaUploadedDocument
from pyrogram.raw.types.input_user_self import InputUserSelf


PACK_SHORT_TEMPLATE = "hazel_kang_{user_id}_by_{username}"


@Tele.on_message(filters.command("kang"), sudo=True)
async def kang_cmd(c: Client, m: Message):

    # ✅ Safety checks
    if not m.from_user:
        return await m.reply_text("User not found.")

    if not m.reply_to_message or not m.reply_to_message.sticker:
        return await m.reply_text("Reply to a sticker.")

    user = m.from_user
    user_id = user.id
    username = (user.username or "hazeluser").lower()

    short_name = PACK_SHORT_TEMPLATE.format(
        user_id=user_id,
        username=username
    )
    title = f"Hazel Kang Pack {user_id}"

    # ✅ Emoji parsing
    emoji = "🔥"
    if m.text:
        parts = m.text.split(maxsplit=1)
        if len(parts) > 1:
            emoji = parts[1]

    msg = await m.reply_text("Kanging...")

    # ✅ Download (FIXED)
    file_path = await m.reply_to_message.download()
    if not file_path:
        return await msg.edit("Download failed.")

    # ✅ Prepare upload
    file = await c.save_file(file_path)
    if not file:
        return await msg.edit("Upload prep failed.")

    # ✅ Resolve peer safely
    peer = await c.resolve_peer("me")
    if peer is None:
        return await msg.edit("Peer resolve failed.")

    # ✅ Upload media
    uploaded = await c.invoke(
        UploadMedia(
            peer=peer,
            media=InputMediaUploadedDocument(
                file=file,
                mime_type="image/webp",
                attributes=[]
            )
        )
    )

    doc = getattr(uploaded, "document", None)
    if not doc:
        return await msg.edit("Upload failed.")

    # ✅ Create InputDocument
    input_doc = InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference
    )

    # ✅ Sticker item
    sticker_item = InputStickerSetItem(
        document=input_doc,
        emoji=emoji
    )

    # ✅ Correct named arg
    pack = InputStickerSetShortName(short_name=short_name)

    # ✅ Try adding (pack exists)
    try:
        await c.invoke(
            AddStickerToSet(
                stickerset=pack,
                sticker=sticker_item
            )
        )
        return await msg.edit(
            f"Sticker added!\nhttps://t.me/addstickers/{short_name}"
        )

    except Exception as e:

        # ✅ If pack doesn't exist → create
        if "STICKERSET_INVALID" in str(e):

            try:
                await c.invoke(
                    CreateStickerSet(
                        user_id=InputUserSelf(),  # ✅ FIXED
                        title=title,
                        short_name=short_name,
                        stickers=[sticker_item]
                    )
                )

                return await msg.edit(
                    f"New pack created!\nhttps://t.me/addstickers/{short_name}"
                )

            except Exception as err:
                return await msg.edit(f"Create failed:\n{err}")

        return await msg.edit(f"Error:\n{e}")


MOD_CONFIG = {
    "name": "Kang",
    "help": (
        "**Usage:**\n"
        "> .kang (reply) [emoji optional] - Kang sticker."
    ),
    "group": "Stickers",
    "works": WORKS.ALL,
    "usable": USABLE.OWNER & USABLE.SUDO
}
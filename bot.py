import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8544263942:AAFee5U8SagnKjuL6bTUcauZ_1RIRaEBE3o")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003540659050"))

pending = {}

AUTO_REPLY = (
    "✅ Xabaringiz qabul qilindi!\n\n"
    "Operatorimiz tez orada javob beradi. "
    "Iltimos, kuting 🙏"
)


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user

    if update.effective_chat.type != "private":
        return

    await msg.reply_text(AUTO_REPLY)

    name = user.full_name or "Noma'lum"
    username = f"@{user.username}" if user.username else "username yo'q"
    header = (
        f"📩 <b>Yangi murojaat</b>\n"
        f"👤 <b>{name}</b> ({username})\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"{'─' * 28}"
    )

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=header,
        parse_mode="HTML"
    )

    forwarded = await msg.forward(chat_id=CHANNEL_ID)
    pending[forwarded.message_id] = user.id


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if update.effective_chat.id != CHANNEL_ID:
        return

    if not msg.reply_to_message:
        return

    replied_id = msg.reply_to_message.message_id
    user_id = pending.get(replied_id)

    if not user_id:
        return

    try:
        if msg.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💬 <b>Operator javobi:</b>\n\n{msg.text}",
                parse_mode="HTML"
            )
        elif msg.photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=msg.photo[-1].file_id,
                caption=msg.caption or ""
            )
        elif msg.video:
            await context.bot.send_video(
                chat_id=user_id,
                video=msg.video.file_id,
                caption=msg.caption or ""
            )
        elif msg.document:
            await context.bot.send_document(
                chat_id=user_id,
                document=msg.document.file_id,
                caption=msg.caption or ""
            )
        elif msg.voice:
            await context.bot.send_voice(
                chat_id=user_id,
                voice=msg.voice.file_id
            )

        await msg.reply_text("✅ Javob mijozga yuborildi.")

    except Exception as e:
        await msg.reply_text(f"❌ Xatolik: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    user_filter = filters.ChatType.PRIVATE & (
        filters.TEXT | filters.PHOTO | filters.VIDEO |
        filters.Document.ALL | filters.VOICE
    )
    app.add_handler(MessageHandler(user_filter, handle_user_message))

    admin_filter = filters.Chat(CHANNEL_ID) & filters.REPLY
    app.add_handler(MessageHandler(admin_filter, handle_admin_reply))

    logger.info("JetCab bot ishga tushdi ✅")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

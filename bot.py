import re
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")


def extract_message_id(caption: str):
    match = re.search(r"Message ID:\s*(\d+)", caption)
    if match:
        return match.group(1)
    return None


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send media with caption containing 'Message ID:'")


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # Check caption manually
    if not msg.caption:
        return await msg.reply_text("❌ Caption missing.")

    message_id = extract_message_id(msg.caption)

    if not message_id:
        return await msg.reply_text("❌ 'Message ID:' not found in caption.")

    deep_link = f"https://t.me/{BOT_USERNAME}?start={message_id}"

    await msg.reply_text(f"✅ Deep Link Generated:\n\n🔗 {deep_link}")


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    if not BOT_USERNAME:
        print("❌ BOT_USERNAME missing!")
        return

    request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=20,
        write_timeout=20,
        pool_timeout=20
    )

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start_cmd))

    # IMPORTANT: Caption filter removed — manual caption check added
    media_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL

    app.add_handler(MessageHandler(media_filter, handle_media))

    print("🚀 Bot running without filter errors...")
    app.run_polling()


if __name__ == "__main__":
    main()

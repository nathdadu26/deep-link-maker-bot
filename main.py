import re
import os
import requests
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
VIRALBOX_API_KEY = os.getenv("VIRALBOX_API_KEY")


def extract_message_id(caption: str):
    match = re.search(r"Message ID:\s*(\d+)", caption)
    if match:
        return match.group(1)
    return None


def shorten_url(long_url):
    try:
        api = VIRALBOX_API_KEY
        url = f"https://viralbox.in/api?api={api}&url={long_url}"

        r = requests.get(url, timeout=15)
        data = r.json()

        if data.get("status") == "success":
            return data.get("shortenedUrl")

        return None
    except:
        return None


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send media with caption containing 'Message ID:'")


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg.caption:
        return await msg.reply_text("❌ Caption missing.")

    message_id = extract_message_id(msg.caption)

    if not message_id:
        return await msg.reply_text("❌ 'Message ID:' not found in caption.")

    deep_link = f"https://t.me/{BOT_USERNAME}?start={message_id}"

    # Shorten deep-link using Viralbox
    short_deeplink = shorten_url(deep_link)

    if not short_deeplink:
        short_deeplink = deep_link

    # Create caption with shortened link
    caption_text = f"🔗 **Short Deep Link:**\n{short_deeplink}"

    # Forward media with new caption
    if msg.photo:
        await msg.reply_photo(
            photo=msg.photo[-1].file_id,
            caption=caption_text,
            parse_mode="Markdown"
        )
    elif msg.video:
        await msg.reply_video(
            video=msg.video.file_id,
            caption=caption_text,
            parse_mode="Markdown"
        )
    elif msg.document:
        await msg.reply_document(
            document=msg.document.file_id,
            caption=caption_text,
            parse_mode="Markdown"
        )
    
    # Delete original message
    await msg.delete()


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    if not BOT_USERNAME:
        print("❌ BOT_USERNAME missing!")
        return
    if not VIRALBOX_API_KEY:
        print("❌ VIRALBOX_API_KEY missing!")
        return

    request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=20,
        write_timeout=20,
        pool_timeout=20
    )

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start_cmd))

    media_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL
    app.add_handler(MessageHandler(media_filter, handle_media))

    print("🚀 Bot running with ViralBox shortening...")
    app.run_polling()


if __name__ == "__main__":
    main()

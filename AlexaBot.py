import os
import requests
import logging
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutorial_text = (
        "👋 <b>Welcome to the Device Registration Bot!</b>\n\n"
        "📋 How to use: /register <DEVICE_ID>\n\n"
        "Owner: @Alexak_Only"
    )
    await update.message.reply_text(tutorial_text, parse_mode='HTML')
    video_url = "https://alexafreeinjector.onrender.com/video"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Use: /register <DEVICE_ID>")
        return

    device_id = context.args[0]
    try:
        response = requests.post(API_URL, data={'device_id': device_id})
        data = response.json()
        if data.get('status') == 'success':
            msg = data['message']
            expiry = data.get('expiry_datetime')
            if expiry:
                msg += f"\n🗓️ Expiry: {expiry}"
            await update.message.reply_text(f"✅ {msg}")
        else:
            msg = data.get('message', '❌ Registration failed.')
            await update.message.reply_text(f"❌ {msg}")
    except Exception as e:
        logging.error("Error in /register: %s", str(e))
        await update.message.reply_text("⚠️ Server error. Try again later.")

def main():
    Thread(target=keep_alive).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.run_polling()

if __name__ == '__main__':
    main()

import os
import re
import requests
import hashlib
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RINKU_API_TOKEN = 'c7f14e078e237af91d8e920159212bba25b0fd7b'
VERIFY_JSON_URL = "https://kaicodm.store/Free/Device_Registered.json"
SECRET = 'ALEXA_SECRET2025'


def get_rinku_link(device_id):
    sig = hashlib.sha256(f"{device_id}{SECRET}".encode()).hexdigest()
    long_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}&t=rinku"
    params = {
        "api": RINKU_API_TOKEN,
        "url": long_url,
        "alias": f"alexa{random.randint(1000,9999)}"
    }

    try:
        response = requests.get("https://rinku.pro/api", params=params)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl", long_url)
    except Exception as e:
        print("❌ Rinku API Error:", e)

    return long_url


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 <b>Welcome to Alexa Injector!</b>\n\n"
        "Unlock premium features by registering your device with this bot.\n"
        "It’s fast, simple, and secure.\n\n"
        "📱 <b>How to Register:</b>\n"
        "Just send your device ID using the command below:\n"
        "<code>/register YOUR_DEVICE_ID</code>\n\n"
        "💡 <b>Example:</b>\n"
        "<code>/register 9774d56d682e549c</code>\n\n"
        "📢 Need help? Watch the video tutorial sent after this message.\n\n"
        "👤 Owner: @Alexak_Only"
    )
    await update.message.reply_text(text, parse_mode='HTML')

    video_url = "https://alexafreeinjector.onrender.com/videoJuly15"
    try:
        await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")
    except:
        await update.message.reply_text("📽 Tutorial video is currently unavailable. Please check @Alexak_Only.")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /register <DEVICE_ID>")
        return

    device_id = context.args[0]
    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text("⚠️ Invalid Device ID.")
        return

    context.user_data['device_id'] = device_id
    short_link = get_rinku_link(device_id)

    await update.message.reply_text(
        f"🔗 Click the link below and complete the steps:\n{short_link}\n\n"
        f"⚠️ If the page is blank or ad-heavy, wait for the countdown then tap 'Continue'.\n"
        f"⏳ After completing all tasks, type /token"
    )

    video_url = "https://alexafreeinjector.onrender.com/videoJuly15"
    await update.message.reply_video(
        video=video_url,
        caption="📽 Tutorial Video: How to Complete the Steps"
    )


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ Please register first using /register")
        return

    try:
        response = requests.get(VERIFY_JSON_URL)
        data = response.json()

        record = data.get(device_id)
        if not record or not record.get('verified'):
            await update.message.reply_text("❌ Device not verified yet. Complete the shortlink steps first.")
            return

        expiry_str = record.get('expiry_datetime')
        expiry_dt = datetime.strptime(expiry_str, '%Y-%m-%dT%H:%M')
        now = datetime.now()

        if expiry_dt < now:
            await update.message.reply_text("❌ Your registration has expired. Please register again.")
        else:
            await update.message.reply_text(
                f"✅ Your device is verified!\n🗓️ Expiry: {expiry_str}"
            )

    except Exception as e:
        print("❌ Error checking verification:", e)
        await update.message.reply_text("❌ Failed to check verification. Try again later.")


def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("token", token))
    app.run_polling()


if __name__ == '__main__':
    main()

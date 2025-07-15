import os
import re
import requests
import hashlib
import random
from datetime import datetime
import pytz

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RINKU_API_TOKEN = 'c7f14e078e237af91d8e920159212bba25b0fd7b'
SECRET = 'ALEXA_SECRET2025'
VIDEO_URL = "https://alexafreeinjector.onrender.com/videoJuly15"
JSON_VERIFY_URL = "https://kaicodm.store/Free/Device_Registered.json"


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
        else:
            print("❌ Rinku API error:", data)
            return long_url
    except Exception as e:
        print("❌ Rinku Exception:", e)
        return long_url


async def send_tutorial(update: Update):
    try:
        await update.message.reply_video(
            video=VIDEO_URL,
            caption="📽 Tutorial Video: How to complete the verification steps."
        )
    except Exception as e:
        print("⚠️ Video error:", e)
        await update.message.reply_text("📽 Tutorial video is unavailable. Message @Alexak_Only for help.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 <b>Welcome to Alexa Injector!</b>\n\n"
        "Unlock premium features by registering your device.\n"
        "This bot is fast, secure, and now gives 2 days validity!\n\n"
        "📲 <b>Register now</b> with:\n"
        "<code>/register YOUR_DEVICE_ID</code>\n\n"
        "💡 Example:\n"
        "<code>/register 9774d56d682e549c</code>\n\n"
        "Need help? Watch the tutorial video below.\n"
        "👤 Owner: @Alexak_Only"
    )
    await update.message.reply_text(text, parse_mode='HTML')
    await send_tutorial(update)


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

    await send_tutorial(update)


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ Please register first using /register")
        return

    try:
        response = requests.get(JSON_VERIFY_URL)
        if response.status_code != 200:
            raise Exception("Verification file not found.")

        data = response.json()
        device_data = data.get(device_id)

        if not device_data:
            raise Exception("Device ID not found.")
        if not device_data.get("verified"):
            raise Exception("Device not verified.")

        expiry_str = device_data.get("expiry_datetime")
        expiry = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M")
        now = datetime.now(pytz.timezone("Asia/Manila"))

        if expiry < now:
            raise Exception("❌ Your key has expired. Please register again to renew.")

        msg = f"✅ Your device is verified!\n🗓️ Expiry: {expiry_str}"
        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Verification failed: {str(e)}\n\n"
            f"🔁 Complete the steps again to renew your key."
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ You haven’t registered. Use /register first.")
        return

    try:
        response = requests.get(JSON_VERIFY_URL)
        if response.status_code != 200:
            raise Exception("Unable to check status.")

        data = response.json()
        device_data = data.get(device_id)

        if not device_data:
            raise Exception("Device ID not found.")
        expiry_str = device_data.get("expiry_datetime")
        expiry = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M")
        now = datetime.now(pytz.timezone("Asia/Manila"))
        days_left = (expiry - now).days

        if expiry < now:
            msg = f"⛔ Your key expired on: {expiry_str}\n🔁 Re-register using /register"
        else:
            msg = f"✅ Valid\n🗓️ Expiry: {expiry_str}\n⏳ Days left: {days_left} day(s)"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to check status: {str(e)}")


def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("token", token))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()


if __name__ == '__main__':
    main()

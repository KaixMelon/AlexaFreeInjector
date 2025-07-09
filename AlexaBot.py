import os
import re
import requests
import hashlib
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'
SHRINKEARN_API_KEY = '2f865cf0ed73598943d81ab3d4174a6558fc9d37'


def get_shrinkearn_link(device_id):
    secret = 'ALEXA_SECRET2025'
    sig = hashlib.sha256(f"{device_id}{secret}".encode()).hexdigest()
    long_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}&t=shrink"

    params = {
        "api": "2f865cf0ed73598943d81ab3d4174a6558fc9d37",
        "url": long_url,
        "alias": f"alx{random.randint(1000,9999)}"
    }

    try:
        response = requests.get("https://shrinkearn.com/api", params=params)
        print("📦 ShrinkEarn API raw response:", response.text)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl", long_url)
        else:
            print("❌ ShrinkEarn returned error:", data)
            return long_url
    except Exception as e:
        print("❌ ShrinkEarn Exception:", e)
        return long_url


async def poll_verification(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    device_id = context.job.data
    url = f"https://kaicodm.store/Free/verified/{device_id}.txt"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = requests.post(API_URL, data={'device_id': device_id}).json()
            msg = result.get("message", "✅ Device verified.")
            expiry = result.get("expiry_datetime")
            if expiry:
                msg += f"\n🗓️ Expiry: {expiry}"
            await context.bot.send_message(chat_id=chat_id, text=msg)
            context.job.schedule_removal()
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Welcome to the Alexa Injector Bot!</b>\n\n"
        "This bot registers your device ID to unlock premium features.\n\n"
        "📋 <b>To register:</b>\n"
        "<code>/register YOUR_DEVICE_ID</code>\n\n"
        "🔔 <b>Example:</b>\n"
        "<code>/register 9774d56d682e549c</code>\n"
        "Owner: @Alexak_Only"
    )
    await update.message.reply_text(text, parse_mode='HTML')
    video_url = "https://alexafreeinjector.onrender.com/video2025"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /register <DEVICE_ID>")
        return

    device_id = context.args[0]
    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text("⚠️ Invalid Device ID.")
        return

    context.user_data['device_id'] = device_id
    link = get_shrinkearn_link(device_id)

    await update.message.reply_text(
        f"🔗 Click the link below and complete the steps:\n{link}\n\n"
        f"⚠️ If the page is blank or ad-heavy, wait for the countdown then tap 'Continue'.\n"
        f"⏳ After completing all tasks, type /token"
    )

    video_url = "https://alexafreeinjector.onrender.com/video2025"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")

    context.job_queue.run_repeating(
        poll_verification,
        interval=1,
        first=1,
        data=device_id,
        chat_id=update.effective_chat.id
    )


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ Please register first using /register")
        return

    check_url = f"https://kaicodm.store/Free/verified/{device_id}.txt"
    verify = requests.get(check_url)
    if verify.status_code == 200:
        try:
            response = requests.post(API_URL, data={'device_id': device_id})
            data = response.json()
            msg = data.get('message', "✅ Device registered.")
            expiry = data.get("expiry_datetime")
            if expiry:
                msg += f"\n🗓️ Expiry: {expiry}"
            await update.message.reply_text(msg)
        except:
            await update.message.reply_text("✅ Verified.")
    else:
        await update.message.reply_text("⏳ Not verified yet. Complete the tasks in the link first.")


def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("token", token))
    app.run_polling()


if __name__ == '__main__':
    main()

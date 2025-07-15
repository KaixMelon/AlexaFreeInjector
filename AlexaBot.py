import os
import re
import requests
import hashlib
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'
RINKU_API_TOKEN = 'c7f14e078e237af91d8e920159212bba25b0fd7b'


def get_rinku_link(device_id):
    secret = 'ALEXA_SECRET2025'
    sig = hashlib.sha256(f"{device_id}{secret}".encode()).hexdigest()
    long_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}"

    params = {
        "api": RINKU_API_TOKEN,
        "url": long_url,
        "alias": f"alexa{device_id[-4:]}"
    }

    try:
        response = requests.get("https://rinku.pro/api", params=params)
        data = response.json()
        print("Rinku API response:", data)
        return data.get("shortenedUrl", long_url)
    except Exception as e:
        print("Rinku error:", e)
        return long_url


# Background polling every 1s to check if verified
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
            context.job.schedule_removal()  # Stop polling
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutorial_text = (
        "👋 <b>Welcome to the Device Registration Bot!</b>\n\n"
        "This bot allows you to register your device ID to access our services.\n\n"
        "📋 <b>How to Use:</b>\n"
        "• To register your device, send the command:\n"
        "  <code>/register &lt;DEVICE_ID&gt;</code>\n"
        "  <i>Replace &lt;DEVICE_ID&gt; with your actual device identifier.</i>\n\n"
        "🔔 <b>Example:</b>\n"
        "<code>/register 9774d56d682e549c</code>\n\n"
        "Owner: @Alexak_Only"
    )
    await update.message.reply_text(tutorial_text, parse_mode='HTML')

    await update.message.reply_text("📽 Watch the tutorial here:\nhttps://www.youtube.com/watch?v=fSN0X-RElwY&t=3s")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /register <DEVICE_ID>")
        return

    device_id = context.args[0]
    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text("⚠️ Invalid Device ID. Only letters and numbers allowed.")
        return

    context.user_data['device_id'] = device_id
    link = get_rinku_link(device_id)

    await update.message.reply_text(
        f"🔗 Click this link and complete the steps in Chrome:\n{link}\n\n"
        f"<b>⚠️ If there is no link appeared just register again.</b>\n\n"
        f"⏳ I’ll auto-check every second once you click it.\n\n"
        f"📽 Tutorial video sent below.",
        parse_mode="HTML"
    )


    await update.message.reply_text("📽 Watch the tutorial here:\nhttps://www.youtube.com/watch?v=fSN0X-RElwY&t=3s")

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

            if data.get('status') == 'success':
                msg = data['message']
                expiry = data.get('expiry_datetime')
                if expiry:
                    msg += f"\n🗓️ Expiry: {expiry}"
                await update.message.reply_text(f"✅ {msg}")
            else:
                await update.message.reply_text("⚠️ Already verified or invalid request.")
        except:
            await update.message.reply_text("✅ Verified, but error on confirmation.")
    else:
        await update.message.reply_text("⏳ Not verified yet. Complete the Rinku.pro link first.")


def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("token", token))
    application.run_polling()


if __name__ == '__main__':
    main()

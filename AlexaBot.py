import os
import re
import requests
import hashlib
import asyncio
from telegram.ext import JobQueue
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'


def get_shrinkme_link(device_id):
    api_key = '8c99e33a726aaf40c081e5978ae692cd7ec6ca306b862853e368fbec93d41c4b'
    secret = 'ALEXA_SECRET2025'  # keep this private and same in PHP
    raw = f"{device_id}{secret}"
    signature = hashlib.sha256(raw.encode()).hexdigest()

    real_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={signature}"
    api_url = f"https://lootlabs.io/api?api={api_key}&url={real_url}"

    try:
        response = requests.get(api_url)
        data = response.json()
        print("ShrinkMe API response:", data)  # Debug log
        return data.get("shortenedUrl", real_url)
    except Exception as e:
        print("ShrinkMe error:", e)
        return real_url


# Background polling to check verification
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


# /start command
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
        "Thank you for using our service!\nOwner: @Alexak_Only"
    )
    await update.message.reply_text(tutorial_text, parse_mode='HTML')

    video_url = "https://alexafreeinjector.onrender.com/video2025"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")


# /register command
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /register <DEVICE_ID>")
        return

    device_id = context.args[0]

    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text("⚠️ Invalid Device ID. Only letters and numbers allowed.")
        return

    context.user_data['device_id'] = device_id
    link = get_shrinkme_link(device_id)

    await update.message.reply_text(
        f"🔗 Copy this link and paste it to Chrome. After Completing the step, comeback here and type /token:\n{link}\n\n"
        f"⏳ After completing the steps, I'll auto-confirm your device.\n\n"
        f"🗒️ Copy the link and paste it to Chrome."
    )

    # Send tutorial video
    video_url = "https://alexafreeinjector.onrender.com/video2025"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")

    # Start polling every 1 second
    context.job_queue.run_repeating(
        poll_verification,
        interval=1,
        first=1,
        data=device_id,
        chat_id=update.effective_chat.id
    )


# /token command
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
                await update.message.reply_text("✅ Verified, Your Device Id Is Successfully Registered.")
        except:
            await update.message.reply_text("✅ Verified, Your Device Id Is Successfully Registered.")
    else:
        await update.message.reply_text("⏳ Not verified yet. Complete the ShrinkMe link first.")


# Main bot launcher
def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("token", token))
    application.run_polling()


if __name__ == '__main__':
    main()

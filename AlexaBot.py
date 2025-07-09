import os
import re
import requests
import hashlib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'

# Official LootLabs API token
LOOTLABS_TOKEN = '8c99e33a726aaf40c081e5978ae692cd7ec6ca306b862853e368fbec93d41c4b'


def get_lootlabs_link(device_id):
    api_key = '8c99e33a726aaf40c081e5978ae692cd7ec6ca306b862853e368fbec93d41c4b'
    secret = 'ALEXA_SECRET2025'
    sig = hashlib.sha256(f"{device_id}{secret}".encode()).hexdigest()
    target = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}&t=loot"

  def get_lootlabs_link(device_id):
    api_token = '8c99e33a726aaf40c081e5978ae692cd7ec6ca306b862853e368fbec93d41c4b'
    sig = hashlib.sha256(f"{device_id}ALEXA_SECRET2025".encode()).hexdigest()
    target_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}"

    params = {
        "api_token": api_token,
        "title": "Alexa Injector",
        "url": target_url,
        "tier_id": "1",
        "number_of_tasks": "3",
        "theme": "5",                # 5 = Space
        "thumbnail": "",            # optional, keep blank
        "folder": "Alexa Injector"  # helps avoid missing parameter issues
    }

    resp = requests.get("https://creators.lootlabs.gg/api/public/content_locker", params=params)
    data = resp.json()
    if data.get("type") in ("created", "fetch") and "loot_url" in data.get("message", {}):
        return data["message"]["loot_url"]
    else:
        print("❌ LootLabs API error:", data)
        return target_url

    resp = requests.get("https://creators.lootlabs.gg/api/public/content_locker", params=params)
    data = resp.json()
    if data.get("type") in ("created","fetch") and "loot_url" in data.get("message",{}):
        return data["message"]["loot_url"]
    else:
        print("❌ LootLabs API error:", data)
        return target



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
    link = get_lootlabs_link(device_id)

    await update.message.reply_text(
        f"🔗 Click the link below and complete 3 steps:\n{link}\n\n"
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

import os
import re
import requests
import hashlib
import json
import random
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'
RINKU_API_TOKEN = 'c7f14e078e237af91d8e920159212bba25b0fd7b'

# Replace this with your actual Telegram video file_id
VIDEO_FILE_ID = "AAMCBQADGQECG5MHaHW9jNRlbkbNXlcSQoZ5SM_LD4cAAo8YAAIqd7FXXO-tUn_ol7IBAAdtAAM2BA"


def get_rinku_link(device_id):
    secret = 'ALEXA_SECRET2025'
    sig = hashlib.sha256(f"{device_id}{secret}".encode()).hexdigest()
    long_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={sig}&t=rinku"

    params = {
        "api": RINKU_API_TOKEN,
        "url": long_url,
        "alias": f"alexa{random.randint(1000,9999)}"
    }

    try:
        response = requests.get("https://rinku.pro/api", params=params)
        print("🔗 Rinku response:", response.text)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl", long_url)
        else:
            print("❌ Rinku API error:", data)
            return long_url
    except Exception as e:
        print("❌ Rinku Exception:", e)
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
        "📢 Need help? Watch the tutorial below.\n\n"
        "👤 Owner: @Alexak_Only"
    )

    await update.message.reply_text(text, parse_mode='HTML')

    try:
        await update.message.reply_video(
            video=VIDEO_FILE_ID,
            caption="📽 Tutorial Video: How to complete the registration steps."
        )
    except Exception as e:
        print("⚠️ Video error:", e)
        await update.message.reply_text("📽 Tutorial video is currently unavailable. Message @Alexak_Only for help.")


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

    try:
        await update.message.reply_video(
            video=VIDEO_FILE_ID,
            caption="📽 Tutorial Video: How to complete the steps"
        )
    except Exception as e:
        print("⚠️ Video error:", e)
        await update.message.reply_text("📽 Tutorial video is currently unavailable. Message @Alexak_Only for help.")


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ Please register first using /register")
        return

    # Check verification JSON file first
    verify_check_url = f"https://kaicodm.store/Free/verified/Device_Registered.json"

    try:
        verify_response = requests.get(verify_check_url)
        verify_data = verify_response.json()

        if not verify_data.get(device_id):
            await update.message.reply_text("⏳ You haven’t completed the verification steps yet.\n"
                                            "Please finish the short link and tap 'Continue', then try /token again.")
            return
    except Exception as e:
        print("❌ Error checking verification status:", e)
        await update.message.reply_text("⚠️ Could not verify your status. Try again shortly.")
        return

    # If verified, proceed to register/renew
    try:
        response = requests.post(API_URL, data={'device_id': device_id})
        data = response.json()
        msg = data.get('message', "✅ Device registered.")
        expiry = data.get("expiry_datetime")

        if "already" in msg.lower():
            msg = "✅ Your device is already registered. You're good to go!"

        if expiry:
            msg += f"\n🗓️ Expiry: {expiry}"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("❌ Registration failed. Try again later.")


def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("token", token))
    app.run_polling()


if __name__ == '__main__':
    main()

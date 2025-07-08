import os
import re
import requests
import urllib.parse
import hashlib
import urllib.parse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'


def get_shrinkme_link(device_id):
    api_key = '4dcbed541365382d5a5d325da402fb1cc9a7e651'
    secret = 'ALEXA_SECRET2025'  # keep this private and same in PHP
    raw = f"{device_id}{secret}"
    signature = hashlib.sha256(raw.encode()).hexdigest()

    real_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&sig={signature}"
    encoded_url = urllib.parse.quote(real_url, safe='')
    api_url = f"https://shrinkme.io/api?api={api_key}&url={encoded_url}"

    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("shortenedUrl", real_url)
    except Exception as e:
        print("ShrinkMe error:", e)
        return real_url


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

    video_url = "https://alexafreeinjector.onrender.com/video"
    await update.message.reply_video(video=video_url, caption="📽 Tutorial Video")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Incorrect usage.\nPlease use:\n/register <DEVICE_ID>")
        return

    device_id = context.args[0]

    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text(
            "⚠️ Invalid Device ID.\n\nOnly letters and numbers are allowed.",
            parse_mode='HTML'
        )
        return

    # Save device ID in user_data for later use in /token
    context.user_data['device_id'] = device_id

    short_link = get_shrinkme_link(device_id)

    await update.message.reply_text(
        f"🔗 To verify your device, click the link below and complete the short ad:\n\n"
        f"{short_link}\n\n"
        f"⏳ After verifying, return here and type:\n<code>/token</code>",
        parse_mode='HTML'
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
                await update.message.reply_text("✅ Verified, but no expiry info.")
        except:
            await update.message.reply_text("✅ Verified, but error fetching expiry.")
    else:
        await update.message.reply_text("⏳ Not verified yet. Complete the ShrinkMe link first.")


def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("token", token))
    application.run_polling()


if __name__ == '__main__':
    main()

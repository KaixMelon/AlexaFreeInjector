import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Starts Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = 'https://kaicodm.store/Free/api_register.php'


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
        await update.message.reply_text(
            "❌ Incorrect usage.\nPlease use:\n/register <DEVICE_ID>"
        )
        return

    device_id = context.args[0]

    # Validate Android ID (must be exactly 16-character hexadecimal)
    if not re.fullmatch(r'[a-fA-F0-9]{16}', device_id):
        await update.message.reply_text(
            "⚠️ The Device ID you provided is not valid.\n\n"
            "Please ensure your Device ID is exactly 16 characters long and only contains numbers (0–9) and letters (a–f).\n\n"
            "Example of a valid ID: <code>9774d56d682e549c</code>\n\n"
            "If you're unsure how to find your device ID, please refer to the video tutorial or contact support.",
            parse_mode='HTML'
        )
        return

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
            if 'ban' in msg.lower():
                await update.message.reply_text(
                    "🚫 Your device ID is banned.\nPlease contact @Alexak_Only."
                )
            else:
                await update.message.reply_text(f"❌ {msg}")
    except Exception as e:
        await update.message.reply_text("⚠️ Server error. Please try again later.")


def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.run_polling()


if __name__ == '__main__':
    main()

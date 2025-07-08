import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Starts Flask server

# Bot token (from environment or hardcoded)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Your API for registering device ID
API_URL = 'https://kaicodm.store/Free/api_register.php'

# 🔐 Your ShrinkMe.io API Key
SHRINKME_API_KEY = '4dcbed541365382d5a5d325da402fb1cc9a7e651'


# 📦 Generates a short link for the verify.php using ShrinkMe.io API
def get_shrinkme_link(device_id):
    api_key = '4dcbed541365382d5a5d325da402fb1cc9a7e651'
    secret_key = 'AL3X4@2025'  # MUST match PHP file
    target_url = f"https://kaicodm.store/Free/verify.php?device_id={device_id}&key={secret_key}"
    api_url = f"https://shrinkme.io/api?api={api_key}&url={target_url}"

    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("shortenedUrl", target_url)
    except Exception as e:
        print("ShrinkMe error:", e)
        return target_url


# 🎬 /start command
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


# ✅ /register command
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /register <DEVICE_ID>")
        return

    device_id = context.args[0]

    if not re.fullmatch(r'[a-zA-Z0-9]+', device_id):
        await update.message.reply_text("⚠️ Invalid Device ID (letters/numbers only)")
        return

    link = get_shrinkme_link(device_id)

    # Save for later token check
    context.user_data['device_id'] = device_id

    await update.message.reply_text(
        f"✅ Device ID saved!\n\n"
        f"🪙 Please complete this step to activate:\n"
        f"🔗 <b>{link}</b>\n\n"
        "Then return and type <code>/token</code>",
        parse_mode='HTML'
    )


# 🔍 /token command
async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    device_id = context.user_data.get('device_id')
    if not device_id:
        await update.message.reply_text("❌ Please register first using /register")
        return

    check_url = f"https://kaicodm.store/Free/verified/{device_id}.txt"
    verify = requests.get(check_url)

    if verify.status_code == 200:
        # 🔁 Now re-check the API to get expiry
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
                await update.message.reply_text("✅ Verified, but could not fetch expiry info.")
        except:
            await update.message.reply_text("✅ Verified, but error fetching expiry.")
    else:
        await update.message.reply_text("⏳ Not verified yet. Make sure you completed the ShrinkMe step.")



# 🔁 Main bot setup
def main():
    keep_alive()  # Start Flask web server (for uptime pings)

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("token", token))

    print("✅ Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()

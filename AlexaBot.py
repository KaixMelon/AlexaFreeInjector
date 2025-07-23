import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Set this in your Render environment

# Inline buttons
BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 Register", url="https://kaicodm.store/Free/register.php")],
    [InlineKeyboardButton("📽 Tutorial", url="https://youtu.be/GpgeRR6mM2A?si=Jppg066xKqcZ7oBV")]
])

# Welcome message for /start
WELCOME_TEXT = (
    "👋 <b>Welcome to the Device Registration Bot!</b>\n\n"
    "You're just a step away from unlocking access to our tools.\n\n"
    "🔐 <b>Register your device</b> using the button below.\n"
    "📽 <b>Need help?</b> A quick tutorial is also available.\n\n"
    "Please select one of the options below to proceed."
)

# Load advice from text file
def get_random_advice():
    try:
        with open("advice.txt", "r", encoding="utf-8") as file:
            tips = [line.strip() for line in file if line.strip()]
        return random.choice(tips)
    except Exception:
        return "Stay focused and keep building."

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=BUTTONS,
        parse_mode='HTML'
    )

# /register handler (any argument)
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    advice = get_random_advice()
    message = (
        "💡 <b>Please use the buttons below to continue.</b>\n\n"
        "There’s no need to type commands manually, simply tap a button for a smooth experience.\n\n"
        f"🔎 <i>Tip of the Day:</i>\n“{advice}”\n\n"
        "🛠 <i>Powered by Alexa Cutie</i>"
    )
    await update.message.reply_text(
        message,
        reply_markup=BUTTONS,
        parse_mode='HTML'
    )

# Main function
def main():
    keep_alive()  # Optional: remove if not using a Flask pinger
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.run_polling()

if __name__ == '__main__':
    main()

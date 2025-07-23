import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Optional Flask server

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Set this in your environment

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 <b>Welcome to the Device Registration Bot!</b>\n\n"
        "Please tap a button below to get started."
    )

    keyboard = [
        [InlineKeyboardButton("📝 Register", url="https://kaicodm.store/Free/register")],
        [InlineKeyboardButton("📽 Tutorial", url="https://www.youtube.com/watch?v=fSN0X-RElwY&t=3s")]
    ]

    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    main()

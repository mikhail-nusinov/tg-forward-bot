import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT_ID = int(os.getenv("DESTINATION_CHAT_ID"))
DESTINATION_THREAD_ID = os.getenv("DESTINATION_THREAD_ID")

if DESTINATION_THREAD_ID:
    DESTINATION_THREAD_ID = int(DESTINATION_THREAD_ID)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    # 1. автоответ отправителю
    await update.message.reply_text(
        "Большое спасибо, Ваше сообщение отправлено! "
        "Мы свяжемся с Вами в течение 24 часов."
    )

    # 2. пересылка админам
    await context.bot.forward_message(
        chat_id=DESTINATION_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        message_thread_id=DESTINATION_THREAD_ID
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

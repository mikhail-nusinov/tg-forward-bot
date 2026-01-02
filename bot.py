import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
THREAD_ID = int(os.getenv("THREAD_ID"))

AUTO_REPLY_TEXT = (
    "Большое спасибо, Ваше сообщение отправлено! "
    "Мы свяжемся с Вами в течение 24 часов."
)

logging.basicConfig(level=logging.INFO)

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    header = f"Сообщение от {user.full_name} (@{user.username or '—'})\n\n"

    # Пересылка сообщения администраторам
    if update.message.text:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=header + update.message.text
        )
    else:
        await update.message.copy(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID
        )

    # Автоответ отправителю
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=AUTO_REPLY_TEXT
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward_message))
app.run_polling()

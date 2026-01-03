import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- Переменные окружения ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGET_CHAT_ID = int(os.environ["TARGET_CHAT_ID"])

# --- Обработчик сообщений ---
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пересылает сообщения в целевой чат, кроме сообщений из самого целевого чата.
    """
    # Игнорируем сообщения из целевого чата, чтобы не отвечать себе
    if update.effective_chat.id == TARGET_CHAT_ID:
        return

    # Формируем текст пересылаемого сообщения
    sender_name = update.effective_user.first_name
    text = update.message.text or "<non-text message>"
    forwarded_text = f"{sender_name}: {text}"

    # Отправляем в целевой чат
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=forwarded_text
    )

# --- Основная функция ---
def main():
    # Создаём приложение бота
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик текстовых сообщений
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message)
    application.add_handler(text_handler)

    # Запуск бота (Polling) — подходит для Render
    application.run_polling()

# --- Точка входа ---
if __name__ == "__main__":
    main()

import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", 0))
TARGET_TOPIC_ID = int(os.environ.get("TARGET_TOPIC_ID", 0))  # 0 если нет тем

# Очередь сообщений
message_queue = asyncio.Queue()

async def message_worker(app):
    while True:
        update = await message_queue.get()
        try:
            # Не пересылаем сообщения из целевого чата/темы
            if update.effective_chat.id == TARGET_CHAT_ID:
                continue

            text = update.message.text
            if TARGET_TOPIC_ID:
                await app.bot.send_message(chat_id=TARGET_CHAT_ID, text=text, message_thread_id=TARGET_TOPIC_ID)
            else:
                await app.bot.send_message(chat_id=TARGET_CHAT_ID, text=text)

            # Отправляем подтверждение отправителю
            await update.message.reply_text("Ваше сообщение получено и будет переслано.")

        except Exception as e:
            print(f"Error in worker: {e}")
        finally:
            message_queue.task_done()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await message_queue.put(update)

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Хендлер на все текстовые сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем воркер очереди
    asyncio.create_task(message_worker(application))

    # Запуск polling
    await application.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

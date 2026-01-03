import os
import asyncio
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.error import RetryAfter, TelegramError

# Используем переменные окружения
BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGET_CHAT_ID = int(os.environ["TARGET_CHAT_ID"])
TOPIC_ID = int(os.environ.get("TOPIC_ID", 0))  # если нужен топик, иначе 0

# Очередь сообщений
message_queue = asyncio.Queue()

async def forward_message_safe(bot, message: Message):
    """
    Пересылает сообщение с обработкой ошибок и flood control.
    """
    try:
        if message.text:
            await bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=message.text,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        elif message.photo:
            await bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=message.caption,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        elif message.video:
            await bot.send_video(
                chat_id=TARGET_CHAT_ID,
                video=message.video.file_id,
                caption=message.caption,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        elif message.document:
            await bot.send_document(
                chat_id=TARGET_CHAT_ID,
                document=message.document.file_id,
                caption=message.caption,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        elif message.audio:
            await bot.send_audio(
                chat_id=TARGET_CHAT_ID,
                audio=message.audio.file_id,
                caption=message.caption,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=TARGET_CHAT_ID,
                voice=message.voice.file_id,
                caption=message.caption,
                message_thread_id=TOPIC_ID if TOPIC_ID else None
            )
        else:
            # Игнорируем остальные типы сообщений
            return
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await forward_message_safe(bot, message)
    except TelegramError as e:
        print(f"Ошибка Telegram API: {e}")

async def message_worker(application):
    """
    Постоянно берет сообщения из очереди и пересылает их.
    """
    while True:
        message = await message_queue.get()
        await forward_message_safe(application.bot, message)
        message_queue.task_done()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Основной обработчик входящих сообщений.
    """
    if not update.message:
        return

    # Игнорируем сообщения из целевого чата
    if update.message.chat_id == TARGET_CHAT_ID:
        return

    # Игнорируем собственные сообщения бота
    if update.message.from_user and update.message.from_user.id == context.bot.id:
        return

    # Добавляем сообщение в очередь
    await message_queue.put(update.message)

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик всех сообщений
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    # Запускаем воркер очереди сообщений
    application.create_task(message_worker(application))

    # Запускаем бота
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

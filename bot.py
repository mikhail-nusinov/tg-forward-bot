import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ====== Environment Variables ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID", 0))
TARGET_TOPIC_ID = int(os.environ.get("TARGET_TOPIC_ID", 0))
PORT = int(os.environ.get("PORT", 10000))  # Render передает порт через env

# ====== Queue для сообщений ======
message_queue = asyncio.Queue()

# ====== Worker: пересылает сообщения в целевой чат ======
async def message_worker(app):
    while True:
        update = await message_queue.get()
        try:
            # Игнорируем сообщения, уже находящиеся в целевом чате
            if update.effective_chat.id == TARGET_CHAT_ID:
                continue

            text = update.message.text or ""
            if TARGET_TOPIC_ID:
                await app.bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=text,
                    message_thread_id=TARGET_TOPIC_ID
                )
            else:
                await app.bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=text
                )

            # Подтверждаем отправителю
            await update.message.reply_text("Ваше сообщение получено и будет переслано.")
        except Exception as e:
            print(f"[Worker Error] {e}")
        finally:
            message_queue.task_done()

# ====== Хэндлер входящих сообщений ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await message_queue.put(update)

# ====== Мини HTTP-сервер для Render ======
async def handle_http(request):
    return web.Response(text="Bot is running!")

async def start_http_server():
    app_web = web.Application()
    app_web.add_routes([web.get("/", handle_http)])
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"HTTP server running on port {PORT}")

# ====== Main ======
async def main():
    # Создаем приложение Telegram
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем хэндлер сообщений
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Запускаем worker
    asyncio.create_task(message_worker(application))

    # Инициализация и запуск polling
    await application.initialize()
    await application.start_polling()
    print("Bot polling started.")

    # Запускаем HTTP сервер
    await start_http_server()

    # Держим приложение живым
    await asyncio.Event().wait()  # бесконечно

# ====== Entry Point ======
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")

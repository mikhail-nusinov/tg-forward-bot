import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======== Настройки ========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FORWARD_CHAT_ID = int(os.environ.get("FORWARD_CHAT_ID", 0))  # ID чата для пересылки
PORT = int(os.environ.get("PORT", 10000))  # порт Render Web Service

# ======== Хэндлеры ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на команду /start"""
    await update.message.reply_text("Бот запущен и готов к работе!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщение в FORWARD_CHAT_ID и отвечает отправителю"""
    sender = update.message.from_user
    text = update.message.text

    # Формируем пересылаемое сообщение
    forward_text = (
        f"От: {sender.full_name} (@{sender.username if sender.username else 'нет'})\n"
        f"ID: {sender.id}\n"
        f"Сообщение:\n{text}"
    )

    # Пересылаем в целевой чат
    await context.bot.send_message(chat_id=FORWARD_CHAT_ID, text=forward_text)

    # Отвечаем отправителю
    await update.message.reply_text("Ваше сообщение было получено и переслано.")

# ======== Запуск бота ========
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем хэндлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Инициализация и запуск polling
    await application.initialize()
    polling_task = asyncio.create_task(application.start_polling())

    return application, polling_task

# ======== Web Service для Render ========
async def handle_root(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запуск бота
    application, polling_task = await run_bot()

    # Настройка веб-сервиса
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Service running on port {PORT}")

    # Держим сервис и polling живыми
    try:
        await polling_task
    finally:
        await application.stop()
        await application.shutdown()
        await runner.cleanup()

# ======== Запуск ========
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()

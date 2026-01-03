import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# === Настройки через environment variables ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
FORWARD_CHAT_ID = int(os.environ["FORWARD_CHAT_ID"])
THREAD_ID = int(os.environ["THREAD_ID"])
PORT = int(os.environ.get("PORT", 10000))  # порт для Render

# === Обработчик входящих сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    sender_name = user.full_name
    sender_username = f"@{user.username}" if user.username else "(нет username)"
    sender_id = user.id

    forward_text = (
        f"Сообщение от {sender_name}\n"
        f"Username: {sender_username}\n"
        f"Telegram ID: {sender_id}\n\n"
        f"{update.message.text}"
    )

    # Пересылаем сообщение в указанный thread
    await context.bot.send_message(
        chat_id=FORWARD_CHAT_ID,
        text=forward_text,
        message_thread_id=THREAD_ID
    )

    # Отвечаем отправителю
    await update.message.reply_text("Спасибо за ваше сообщение")

# === Инициализация Telegram бота ===
async def init_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # Обработчик текстовых сообщений (кроме команд)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()  # важно!
    return application

# === Простейший Web Service для Render ===
async def init_web():
    async def health(request):
        return web.Response(text="Bot is alive!")

    app = web.Application()
    app.add_routes([web.get("/", health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# === Главная функция запуска ===
async def main():
    # Инициализируем Telegram bot
    application = await init_bot()

    # Запускаем web-сервер (Render будет видеть открытый порт)
    await init_web()

    # Запускаем polling (бот слушает сообщения)
    await application.run_polling()

# === Старт ===
if __name__ == "__main__":
    asyncio.run(main())

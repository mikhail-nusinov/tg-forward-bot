import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# ---------------------------
# Environment Variables
# ---------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID"))
TARGET_TOPIC_ID = os.environ.get("TARGET_TOPIC_ID")  # Если используется forum topic ID

# ---------------------------
# Telegram Bot Handlers
# ---------------------------
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пересылает сообщение в целевой чат и отвечает отправителю.
    """
    if update.effective_chat.id == TARGET_CHAT_ID:
        # Не пересылаем сообщения из целевого чата обратно
        return

    # Пересылаем текстовое сообщение
    text = update.message.text if update.message else None
    if text:
        try:
            if TARGET_TOPIC_ID:
                await context.bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=text,
                    message_thread_id=TARGET_TOPIC_ID
                )
            else:
                await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=text)
        except Exception as e:
            print("Error forwarding message:", e)

    # Отвечаем отправителю
    try:
        await update.message.reply_text("Спасибо за ваше сообщение")
    except Exception as e:
        print("Error sending reply:", e)

# ---------------------------
# Aiohttp Web Server
# ---------------------------
async def handle_health(request):
    return web.Response(text="Bot is running")

def create_web_app():
    app = web.Application()
    app.add_routes([web.get('/', handle_health)])
    return app

# ---------------------------
# Main Function
# ---------------------------
async def main():
    # Создаём Telegram Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # Запускаем polling в фоне
    polling_task = asyncio.create_task(application.run_polling())

    # Создаём и запускаем aiohttp сервер для Render
    web_app = create_web_app()
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))  # Render сам указывает PORT
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web service running on port {port}")

    # Держим приложение живым
    await polling_task

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")

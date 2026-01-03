import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# ---------------------------
# Environment Variables
# ---------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGET_CHAT_ID = int(os.environ["TARGET_CHAT_ID"])
TARGET_TOPIC_ID = os.environ.get("TARGET_TOPIC_ID")
PORT = int(os.environ.get("PORT", 10000))  # Render сам указывает PORT

# ---------------------------
# Telegram Handler
# ---------------------------
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id == TARGET_CHAT_ID:
        return  # не пересылаем из целевого чата

    text = update.message.text if update.message else None
    if text:
        try:
            if TARGET_TOPIC_ID:
                await context.bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=text,
                    message_thread_id=int(TARGET_TOPIC_ID)
                )
            else:
                await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=text)
        except Exception as e:
            print("Error forwarding message:", e)

    try:
        await update.message.reply_text("Спасибо за ваше сообщение")
    except Exception as e:
        print("Error sending reply:", e)

# ---------------------------
# Aiohttp Healthcheck
# ---------------------------
async def handle_health(request):
    return web.Response(text="Bot is running")

def create_web_app():
    app = web.Application()
    app.add_routes([web.get("/", handle_health)])
    return app

# ---------------------------
# Main
# ---------------------------
async def start_bot_and_web():
    # Telegram Application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # Запуск Telegram bot в фоне
    asyncio.create_task(application.initialize())
    asyncio.create_task(application.start())
    asyncio.create_task(application.updater.start_polling())

    # Aiohttp Web Server
    web_app = create_web_app()
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web service running on port {PORT}")

    # Держим сервис живым
    while True:
        await asyncio.sleep(3600)

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(start_bot_and_web())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")

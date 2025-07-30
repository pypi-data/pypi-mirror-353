from flask import Blueprint, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from app.handlers import start_command, help_command, echo_handler
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    raise ValueError("❌ BOT_TOKEN not set in environment!")

webhook = Blueprint("webhook", __name__)

# Create the application instance
application = ApplicationBuilder().token(bot_token).build()

# Register handlers
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))

@webhook.route("/webhook", methods=["POST"])
def handle_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))  # ✅ FIXED
    return "OK"

@webhook.route("/ping", methods=["GET"])
def ping():
    return "pong"

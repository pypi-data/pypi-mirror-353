import os
from flask import Flask
from telegram.ext import ApplicationBuilder
from app.handlers import register_handlers
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    register_routes(app)

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("❌ BOT_TOKEN is missing in environment variables")

    mode = os.getenv("MODE", "dev").lower()
    webhook_url = os.getenv("WEBHOOK_URL")

    application = ApplicationBuilder().token(bot_token).build()
    register_handlers(application)

    if mode == "dev":
        print("🛠️ Dev mode: Starting bot using polling...")
        application.run_polling()
    elif mode == "production":
        if not webhook_url:
            raise ValueError("❌ WEBHOOK_URL must be set in production mode")
        print(f"🚀 Production mode: Starting bot using webhook at {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=5000,
            url_path="/webhook",
            webhook_url=webhook_url
        )
    else:
        raise ValueError("❌ Invalid MODE. Use 'dev' or 'production'")

    return app

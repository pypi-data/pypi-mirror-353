import sys
import os

try:
    from app import create_app
    app = create_app()
except ImportError as e:
    if "Dispatcher" in str(e):
        print("❌ ERROR: Your bot code imports 'Dispatcher' from 'telegram.ext', but this was removed in python-telegram-bot v20+.")
        print("Please update your bot to use the new 'Application' API instead of 'Dispatcher'.")
        print("See the migration guide here: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html")
        sys.exit(1)
    else:
        raise

if __name__ == "__main__":
    mode = os.getenv("MODE", "dev").lower()
    debug = mode == "dev"
    app.run(debug=debug, port=5000)

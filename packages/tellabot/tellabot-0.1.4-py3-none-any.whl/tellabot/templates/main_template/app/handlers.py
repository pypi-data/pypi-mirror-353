from telegram import Update
from telegram.ext import CallbackContext

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Welcome to your TellaBot!")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("🛠 Available commands:\n/start - Greet\n/help - This message")

def echo_handler(update: Update, context: CallbackContext):
    update.message.reply_text(f"You said: {update.message.text}")

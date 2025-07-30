from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    from app.bot import webhook
    app.register_blueprint(webhook, url_prefix="/")

    return app

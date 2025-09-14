import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "google_service.json")
DB_PATH = os.getenv("DB_PATH", "db/bot.db")

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

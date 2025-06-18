import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_SHEET_KEY = os.getenv("GOOGLE_SHEET_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "google_service.json")

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

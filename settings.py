import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
RESERVE_CHAT_ID = int(os.getenv("RESERVE_CHAT_ID", "0"))
MODE = os.getenv("MODE", "webhook").lower()
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/tg-webhook")
PORT = int(os.getenv("PORT", "8080"))

# 👇 змінити ім’я файлу БД, щоб уникнути старої схеми
DB_PATH = os.getenv("DB_PATH", "keywords_v2.db")

FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "85"))

INIT_PHRASES = [x.strip() for x in os.getenv("INIT_PHRASES", "").split(";") if x.strip()]
_init_allwords_raw = [x.strip() for x in os.getenv("INIT_ALLWORDS", "").split(";") if x.strip()]
INIT_ALLWORDS = [[w.strip() for w in chunk.split(",") if w.strip()] for chunk in _init_allwords_raw]

assert BOT_TOKEN, "BOT_TOKEN is required"
assert ADMIN_CHAT_ID, "ADMIN_CHAT_ID is required"

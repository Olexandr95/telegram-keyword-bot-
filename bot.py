import asyncio
from datetime import timezone
from zoneinfo import ZoneInfo
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message, ChatMemberUpdated
from settings import (
BOT_TOKEN, ADMIN_CHAT_ID, RESERVE_CHAT_ID, MODE, WEBHOOK_HOST, WEBHOOK_PATH, PORT,
DB_PATH, FUZZY_THRESHOLD, INIT_PHRASES, INIT_ALLWORDS
)
from db import DB
from textproc import TextProc


bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
db = DB(DB_PATH)
proc = TextProc(FUZZY_THRESHOLD)
TZ = ZoneInfo("Europe/Kyiv")


# Засіваємо початкові правила, якщо БД порожня
if not db.list_rules():
for ph in INIT_PHRASES:
db.add_phrase(ph)
for words in INIT_ALLWORDS:
db.add_allwords(words)




def is_admin(msg: Message) -> bool:
return msg.from_user and msg.from_user.id == ADMIN_CHAT_ID




def chat_human(chat) -> str:
if chat.type == ChatType.PRIVATE:
return f"👤 {chat.full_name} (private)"
if chat.username:
return f"👥 @{chat.username}"
return f"👥 {chat.title} ({chat.id})"




def author_human(msg: Message) -> str:
name = (msg.from_user.full_name or "user") if msg.from_user else "user"
tag = f"@{msg.from_user.username}" if (msg.from_user and msg.from_user.username) else ""
return f"{name} {tag}".strip()




async def notify(text: str):
# надсилаємо в адмін і резерв (якщо задано)
if ADMIN_CHAT_ID:
try:
await bot.send_message(ADMIN_CHAT_ID, text)
except Exception as e:
print("admin notify failed:", e)
if RESERVE_CHAT_ID and RESERVE_CHAT_ID != ADMIN_CHAT_ID:
try:
asyncio.run(run_polling())

import asyncio
from datetime import timezone
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
from aiogram.client.default import DefaultBotProperties  # <-- важливо для aiogram 3.7+

from settings import (
    BOT_TOKEN, ADMIN_CHAT_ID, RESERVE_CHAT_ID, MODE, WEBHOOK_HOST, WEBHOOK_PATH, PORT,
    DB_PATH, FUZZY_THRESHOLD, INIT_PHRASES, INIT_ALLWORDS
)
from db import DB
from textproc import TextProc

# ✅ нова ініціалізація для aiogram 3.10
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
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
            await bot.send_message(RESERVE_CHAT_ID, text)
        except Exception as e:
            print("reserve notify failed:", e)

@dp.message(Command("ping"))
async def ping(msg: Message):
    await msg.reply("pong ✅")

@dp.message(Command("rules"))
async def rules_list(msg: Message):
    if not is_admin(msg):
        return
    rules = db.list_rules()
    if not rules:
        await msg.reply("Список правил порожній.")
        return
    lines = ["<b>Правила:</b>"]
    for r in rules:
        if r["kind"] == "PHRASE":
            lines.append(f"#{r['id']} PHRASE → \"{r['text']}\"")
        else:
            words = ", ".join(r["words"])
            lines.append(f"#{r['id']} ALLWORDS → [{words}]")
    await msg.reply("\n".join(lines))

@dp.message(Command("addphrase"))
async def add_phrase_cmd(msg: Message):
    if not is_admin(msg):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Використання: /addphrase фраза")
        return
    rid = db.add_phrase(parts[1].strip())
    await msg.reply(f"✅ Додано PHRASE з id={rid}")

@dp.message(Command("addall"))
async def add_all_cmd(msg: Message):
    if not is_admin(msg):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Використання: /addall слово1, слово2, слово3")
        return
    words = [w.strip() for w in parts[1].split(",") if w.strip()]
    rid = db.add_allwords(words)
    await msg.reply(f"✅ Додано ALLWORDS з id={rid}")

@dp.message(Command("del"))
async def del_cmd(msg: Message):
    if not is_admin(msg):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await msg.reply("Використання: /del id")
        return
    ok = db.del_rule(int(parts[1].strip()))
    await msg.reply("🗑️ Видалено" if ok else "❌ Не знайдено")

@dp.message(Command("test"))
async def test_cmd(msg: Message):
    if not is_admin(msg):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Використання: /test ваш_текст")
        return
    txt = parts[1]
    fired = match_all_rules(txt)
    if fired:
        lines = ["✅ Спрацювали правила:"] + [f"• #{r['id']} {r['kind']}" for r in fired]
        await msg.reply("\n".join(lines))
    else:
        await msg.reply("❌ Жодне правило не спрацювало")

@dp.message()
async def on_message(msg: Message):
    if not msg.text:
        return
    fired = match_all_rules(msg.text)
    if not fired:
        return

    when = (msg.date.replace(tzinfo=timezone.utc)).astimezone(TZ)
    dt = when.strftime("%Y-%m-%d %H:%M:%S %Z")

    url = None
    if msg.chat.username and msg.message_id and msg.chat.type != ChatType.PRIVATE:
        url = f"https://t.me/{msg.chat.username}/{msg.message_id}"

    preview = (msg.text[:1000] + "…") if len(msg.text) > 1000 else msg.text

    lines = [
        "🚨 <b>Співпадіння</b>",
        f"Чат: {chat_human(msg.chat)}",
        f"Автор: {author_human(msg)}",
        f"Дата/час: <code>{dt}</code>",
        "Спрацювали правила:",
    ]
    for r in fired:
        if r["kind"] == "PHRASE":
            lines.append(f"• #{r['id']} PHRASE: \"{r['text']}\"")
        else:
            words = ", ".join(r["words"])
            lines.append(f"• #{r['id']} ALLWORDS: [{words}]")
    safe_text = preview.replace("<", "&lt;").replace(">", "&gt;")
    lines.append("\n<b>Текст:</b>\n<code>" + safe_text + "</code>")
    if url:
        lines.append(f"🔗 <a href='{url}'>Відкрити повідомлення</a>")

    await notify("\n".join(lines))

@dp.chat_member()
async def on_added(event: ChatMemberUpdated):
    me = await bot.get_me()
    if event.new_chat_member.user.id == me.id and event.new_chat_member.status in {"member", "administrator"}:
        await notify(f"➕ Додано у чат: {chat_human(event.chat)}")

def match_all_rules(text: str):
    out = []
    for r in db.list_rules():
        if r["kind"] == "PHRASE":
            if proc.match_phrase(text, r["text"]):
                out.append(r)
        elif r["kind"] == "ALLWORDS":
            if proc.match_allwords(text, r["words"]):
                out.append(r)
    return out

async def run_polling():
    print("Starting polling…")
    await dp.start_polling(bot)

# ——— Вебхук через FastAPI ———
if MODE == "webhook":
    from fastapi import FastAPI, Request
    from aiogram import types
    import uvicorn

    app = FastAPI()

    @app.on_event("startup")
    async def on_startup():
        try:
            if not WEBHOOK_HOST:
                print("⚠️ WEBHOOK_HOST not set — webhook won't be set.")
            else:
                await bot.set_webhook(url=f"{WEBHOOK_HOST}{WEBHOOK_PATH}")
                print("✅ Webhook set")
        except Exception as e:
            print("❌ set_webhook failed:", e)
            # не падаємо — сервіс має лишатися живим

    @app.on_event("shutdown")
    async def on_shutdown():
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception as e:
            print("delete_webhook failed:", e)

    @app.post(WEBHOOK_PATH)
    async def webhook(request: Request):
        update = types.Update.model_validate(await request.json())
        await dp.feed_update(bot, update)
        return {"ok": True}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=PORT)
else:
    if __name__ == "__main__":
        asyncio.run(run_polling())

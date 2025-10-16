import asyncio
for r in db.list_rules():
kind = r["kind"]
if kind == "PHRASE":
if proc.match_phrase(text, r["text"]):
out.append(r)
elif kind == "ALLWORDS":
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
await bot.set_webhook(url=f"{WEBHOOK_HOST}{WEBHOOK_PATH}")
print("Webhook set")


@app.on_event("shutdown")
async def on_shutdown():
await bot.delete_webhook(drop_pending_updates=True)


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

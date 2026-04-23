import os
import time
import json
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# 🔐 CONFIG
TOKEN = os.getenv("8624104189:AAGug4bXV1Y22RvzZDWS248USG4hCq37j48")
TON_WALLET = "UQDYM7ld7G-HyC2jiFDVWOZ42qzMe93lsf6uO8pSlqAOTO4P"
ADMIN_ID = 7671435882
TOKEN_NAME = "YOR"

API_URL = "https://toncenter.com/api/v2/getTransactions"

DATA_FILE = "data.json"

# 📦 CARGAR DATOS
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {
        "balances": {},
        "last_mine": {},
        "total_tokens": 0,
        "withdraw_pool": 0,
        "owner_profit": 0,
        "event_reserve": 0,
        "user_boost": {},
        "processed": []
    }

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ⏳ EVENTO
event_duration = 15 * 24 * 60 * 60
event_end_time = time.time() + event_duration
event_finished = False

# 🚀 BOOSTS
boosts = {
    1: {"price": 0.5, "mult": 1.5, "time": 3600},
    2: {"price": 1, "mult": 2, "time": 7200},
    3: {"price": 2, "mult": 2.5, "time": 14400},
    4: {"price": 3, "mult": 3, "time": 21600},
    5: {"price": 5, "mult": 3.5, "time": 43200},
    6: {"price": 8, "mult": 4, "time": 86400},
    7: {"price": 12, "mult": 5, "time": 172800},
    8: {"price": 20, "mult": 6, "time": 259200},
    9: {"price": 30, "mult": 7, "time": 432000},
    10: {"price": 50, "mult": 10, "time": 604800},
}

# 🔍 PAGOS
async def payment_watcher(app):
    while True:
        try:
            r = requests.get(API_URL, params={"address": TON_WALLET, "limit": 20})
            txs = r.json().get("result", [])

            for tx in txs:
                try:
                    msg = tx["in_msg"]["message"]
                    value = int(tx["in_msg"]["value"]) / 1e9
                    tx_id = tx["transaction_id"]["hash"]

                    if tx_id in data["processed"]:
                        continue

                    if msg and "-" in msg:
                        uid, level = msg.split("-")
                        user_id = str(uid)
                        level = int(level)

                        if level in boosts:
                            b = boosts[level]

                            if value >= b["price"]:
                                data["processed"].append(tx_id)

                                expire = time.time() + b["time"]
                                data["user_boost"][user_id] = [b["mult"], expire]

                                data["withdraw_pool"] += value * 0.5
                                data["owner_profit"] += value * 0.3
                                data["event_reserve"] += value * 0.2

                                save()

                                await app.bot.send_message(
                                    chat_id=user_id,
                                    text=f"🚀 Boost x{b['mult']} activado"
                                )

                except:
                    continue
        except:
            pass

        await asyncio.sleep(10)

# 🏁 FINAL EVENTO
async def finish_event(app):
    global event_finished

    while True:
        if not event_finished and time.time() > event_end_time:
            event_finished = True

            for user, tokens in data["balances"].items():
                if tokens == 0:
                    continue

                share = tokens / data["total_tokens"]
                amount = data["withdraw_pool"] * share

                try:
                    await app.bot.send_message(
                        chat_id=int(user),
                        text=f"💸 Ganaste {round(amount,4)} TON"
                    )
                except:
                    pass

        await asyncio.sleep(30)

# /start
async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 EVENTO ACTIVO\n\n"
        "⛏ Mina tokens GRATIS\n"
        "💰 Gana TON real\n\n"
        "/mine /balance /shop /ranking /status"
    )

# /mine
async def mine(update: Update, context):
    user = str(update.effective_user.id)
    now = time.time()

    if event_finished:
        return await update.message.reply_text("Evento terminado")

    if user in data["last_mine"]:
        wait = 10 - (now - data["last_mine"][user])
        if wait > 0:
            return await update.message.reply_text(f"⏳ Espera {int(wait)}s")

    data["last_mine"][user] = now

    reward = 1

    if user in data["user_boost"]:
        mult, exp = data["user_boost"][user]
        if now < exp:
            reward *= mult
        else:
            del data["user_boost"][user]

    reward = min(reward, 50)

    data["balances"][user] = data["balances"].get(user, 0) + reward
    data["total_tokens"] += reward

    save()

    await update.message.reply_text(
        f"⛏ +{round(reward,2)} {TOKEN_NAME}\n⚡ Mejora en /shop"
    )

# /balance
async def balance(update: Update, context):
    user = str(update.effective_user.id)
    await update.message.reply_text(
        f"{round(data['balances'].get(user,0),2)} {TOKEN_NAME}"
    )

# /ranking
async def ranking(update: Update, context):
    top = sorted(data["balances"].items(), key=lambda x: x[1], reverse=True)[:10]

    text = "🏆 TOP\n\n"
    for i, (u, amt) in enumerate(top, 1):
        text += f"{i}. {u} → {round(amt,2)}\n"

    await update.message.reply_text(text)

# /shop
async def shop(update: Update, context):
    text = "🛒 BOOSTS\n\n"
    for k, v in boosts.items():
        text += f"{k}. x{v['mult']} → {v['price']} TON\n"

    text += "\nEnviar TON con:\nID-NIVEL"

    await update.message.reply_text(text)

# /status
async def status(update: Update, context):
    tiempo = int(event_end_time - time.time())

    await update.message.reply_text(
        f"💰 Pool: {round(data['withdraw_pool'],4)} TON\n"
        f"👤 Tus ganancias: {round(data['owner_profit'],4)}\n"
        f"🪙 Total: {round(data['total_tokens'],2)}\n"
        f"⏳ {tiempo}s"
    )

# 🚀 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mine", mine))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("ranking", ranking))
app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("status", status))

app.job_queue.run_once(lambda ctx: asyncio.create_task(payment_watcher(app)), 1)
app.job_queue.run_once(lambda ctx: asyncio.create_task(finish_event(app)), 1)

print("BOT PRO ACTIVO")
app.run_polling()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import time
import requests
import asyncio

# 🔴 CONFIG
TOKEN = "TU_TOKEN_BOT"
TON_WALLET = "UQDYM7ld7G-HyC2jiFDVWOZ42qzMe93lsf6uO8pSlqAOTO4P"
ADMIN_ID = 123456789
TOKEN_NAME = "YOR"

API_URL = "https://toncenter.com/api/v2/getTransactions"

# ⏳ EVENTO
event_duration = 15 * 24 * 60 * 60
event_end_time = time.time() + event_duration
event_finished = False

# 💾 DATA
balances = {}
last_mine = {}
processed = set()

withdraw_pool = 0
owner_profit = 0
event_reserve = 0
total_tokens = 0

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

user_boost = {}

# 🔍 PAGOS AUTOMÁTICOS
async def payment_watcher(app):
    global withdraw_pool, owner_profit, event_reserve

    while True:
        try:
            r = requests.get(API_URL, params={
                "address": TON_WALLET,
                "limit": 20
            })
            data = r.json()

            if data["ok"]:
                for tx in data["result"]:
                    try:
                        msg = tx["in_msg"]["message"]
                        value = int(tx["in_msg"]["value"]) / 1e9
                        tx_id = tx["transaction_id"]["hash"]

                        if tx_id in processed:
                            continue

                        if msg and "-" in msg:
                            uid, level = msg.split("-")
                            user_id = int(uid)
                            level = int(level)

                            if level in boosts:
                                b = boosts[level]

                                if value >= b["price"]:
                                    processed.add(tx_id)

                                    expire = time.time() + b["time"]
                                    user_boost[user_id] = (b["mult"], expire)

                                    # 💰 dividir dinero
                                    withdraw_pool += value * 0.5
                                    owner_profit += value * 0.3
                                    event_reserve += value * 0.2

                                    await app.bot.send_message(
                                        chat_id=user_id,
                                        text=f"🚀 Boost x{b['mult']} activado"
                                    )

                    except:
                        continue

        except:
            pass

        await asyncio.sleep(10)

# 🏁 FINALIZAR EVENTO
async def finish_event(app):
    global event_finished

    while True:
        if not event_finished and time.time() > event_end_time:
            event_finished = True

            for user in balances:
                user_tokens = balances.get(user, 0)

                if user_tokens == 0 or total_tokens == 0:
                    continue

                share = user_tokens / total_tokens
                amount = withdraw_pool * share

                try:
                    await app.bot.send_message(
                        chat_id=user,
                        text=f"💸 Evento finalizado\nGanancia: {round(amount,4)} TON"
                    )
                except:
                    pass

        await asyncio.sleep(20)

# /start
async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 Evento activo (15 días)\n\n"
        "⛏ Mina tokens\n"
        "💰 Gana TON al final\n\n"
        "/mine\n/balance\n/shop\n/status"
    )

# /mine
async def mine(update: Update, context):
    global total_tokens

    user = update.effective_user.id
    now = time.time()

    if event_finished:
        await update.message.reply_text("Evento terminado")
        return

    if user in last_mine and now - last_mine[user] < 10:
        await update.message.reply_text("⏳ Espera")
        return

    last_mine[user] = now

    reward = 1

    # aplicar boost
    if user in user_boost:
        mult, expire = user_boost[user]
        if now < expire:
            reward *= mult
        else:
            del user_boost[user]

    reward = min(reward, 50)

    balances[user] = balances.get(user, 0) + reward
    total_tokens += reward

    await update.message.reply_text(f"⛏ +{round(reward,2)} {TOKEN_NAME}")

# /balance
async def balance(update: Update, context):
    user = update.effective_user.id
    await update.message.reply_text(f"{round(balances.get(user,0),2)} {TOKEN_NAME}")

# /shop
async def shop(update: Update, context):
    text = "🛒 POTENCIADORES\n\n"

    for k, v in boosts.items():
        text += f"{k}. x{v['mult']} → {v['price']} TON\n"

    text += "\nEnvía TON con comentario:\nID-NIVEL\nEj: 123456-3"

    await update.message.reply_text(text)

# /status
async def status(update: Update, context):
    tiempo = int(event_end_time - time.time())

    await update.message.reply_text(
        f"📊 Estado\n\n"
        f"💰 Pool: {round(withdraw_pool,4)} TON\n"
        f"📈 Tus ganancias: {round(owner_profit,4)} TON\n"
        f"🪙 Tokens: {round(total_tokens,2)}\n"
        f"⏳ Tiempo: {tiempo} seg"
    )

# 🚀 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mine", mine))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("status", status))

# 🔥 procesos automáticos
app.job_queue.run_once(lambda ctx: asyncio.create_task(payment_watcher(app)), 1)
app.job_queue.run_once(lambda ctx: asyncio.create_task(finish_event(app)), 1)

print("Bot FINAL PRO iniciado...")
app.run_polling(timeout=30)

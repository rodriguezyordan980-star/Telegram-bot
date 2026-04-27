import os
import time
import json
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ─────────────────────────────────────────
# 🔐 CONFIG
# ─────────────────────────────────────────
TOKEN        = os.getenv("TOKEN")
TON_WALLET   = "UQDYM7ld7G-HyC2jiFDVWOZ42qzMe93lsf6uO8pSlqAOTO4P"
ADMIN_ID     = 7671435882
TOKEN_NAME   = "YOR"
CHANNEL_ID   = "@tu_canal"          # ← Cambia esto por tu canal real
CHANNEL_LINK = "https://t.me/tu_canal"  # ← Y este enlace también

API_URL   = "https://toncenter.com/api/v2/getTransactions"
DATA_FILE = "data.json"

EVENT_DURATION = 15 * 24 * 60 * 60  # 15 días en segundos

# ─────────────────────────────────────────
# 🌐 TEXTOS MULTILENGUAJE
# ─────────────────────────────────────────
T = {
    "es": {
        "choose_lang":      "🌐 Elige tu idioma / Choose your language:",
        "welcome":          (
            "👋 ¡Bienvenido a *YOR Mining Bot*!\n\n"
            "⛏ Mina tokens YOR gratis\n"
            "💰 Gana TON real al final del evento\n"
            "📈 Más tokens = mayor ganancia\n\n"
            "📌 Los retiros se realizan *solo al final del evento*\n\n"
            "Usa el menú de abajo 👇"
        ),
        "menu_title":       "📋 *Menú principal*\nElige una opción:",
        "mine_cooldown":    "⏳ Espera *{s}s* para volver a minar",
        "mine_success":     "⛏ +*{r}* {t}\n\n⚡ Compra un boost en la Tienda para ganar más",
        "mine_event_over":  "❌ El evento ya terminó",
        "balance_msg":      "🪙 *Tus tokens:* {tok} {t}\n💰 *Ganancia estimada:* {est} TON\n\n⏳ Se paga al final del evento",
        "status_msg":       "📊 *Estado del evento*\n\n💰 Pool total: {pool} TON\n🪙 Tokens minados: {total}\n⏳ Tiempo restante: {tiempo}",
        "ranking_title":    "🏆 *TOP 10 mineros*\n\n",
        "ranking_row":      "{i}. `{u}` → {a} YOR\n",
        "shop_title":       "🛒 *Tienda de Boosts*\n\nElige tu boost y paga directo desde Tonkeeper 👇",
        "tasks_title":      "📋 *Tareas disponibles*\n\nCompleta tareas para ganar YOR extra:",
        "task_channel":     "✅ Unirse al canal oficial (+{r} YOR)",
        "task_ref":         "👥 Invitar amigos (+{r} YOR por cada uno)",
        "task_done":        "✅ Ya completaste esta tarea",
        "task_channel_ok":  "🎉 ¡Tarea completada! +{r} {t} por unirte al canal",
        "task_channel_no":  "❌ Aún no estás en el canal. Únete primero y vuelve a verificar.",
        "ref_title":        "👥 *Tu enlace de referido:*\n\n`{link}`\n\n💰 Ganas *{r} YOR* por cada amigo que se una\n👤 Referidos totales: {count}",
        "ref_bonus":        "🎉 ¡{name} se unió con tu enlace! +{r} {t}",
        "event_end_msg":    "🎉 *EVENTO FINALIZADO*\n\n💰 Ganaste: *{amt} TON*\n\nGracias por participar 🚀",
        "boost_ok":         "✅ *Pago confirmado*\n\n🚀 Boost x{m} activado\n💰 Pagado: {v} TON\n\n🔥 Estás minando más rápido",
        "admin_stats":      "🛠 *Admin Stats*\n\nPool retiros: {pool} TON\nGanancia dueño: {profit} TON\nReserva evento: {res} TON\nUsuarios: {users}\nTotal tokens: {total}",
        "lang_set":         "✅ Idioma establecido: Español",
        "btn_mine":         "⛏ Minar",
        "btn_balance":      "💰 Balance",
        "btn_shop":         "🛒 Tienda",
        "btn_tasks":        "📋 Tareas",
        "btn_ranking":      "🏆 Ranking",
        "btn_status":       "📊 Estado",
        "btn_referral":     "👥 Referidos",
        "btn_verify":       "✅ Verificar",
        "btn_join":         "📢 Unirse al canal",
        "btn_back":         "🔙 Volver",
        "btn_lang":         "🌐 Idioma",
    },
    "en": {
        "choose_lang":      "🌐 Elige tu idioma / Choose your language:",
        "welcome":          (
            "👋 Welcome to *YOR Mining Bot*!\n\n"
            "⛏ Mine YOR tokens for free\n"
            "💰 Earn real TON at the end of the event\n"
            "📈 More tokens = bigger reward\n\n"
            "📌 Withdrawals happen *only at the end of the event*\n\n"
            "Use the menu below 👇"
        ),
        "menu_title":       "📋 *Main Menu*\nChoose an option:",
        "mine_cooldown":    "⏳ Wait *{s}s* to mine again",
        "mine_success":     "⛏ +*{r}* {t}\n\n⚡ Buy a boost in the Shop to earn more",
        "mine_event_over":  "❌ The event is over",
        "balance_msg":      "🪙 *Your tokens:* {tok} {t}\n💰 *Estimated earnings:* {est} TON\n\n⏳ Paid at the end of the event",
        "status_msg":       "📊 *Event Status*\n\n💰 Total pool: {pool} TON\n🪙 Mined tokens: {total}\n⏳ Time left: {tiempo}",
        "ranking_title":    "🏆 *TOP 10 Miners*\n\n",
        "ranking_row":      "{i}. `{u}` → {a} YOR\n",
        "shop_title":       "🛒 *Boost Shop*\n\nChoose your boost and pay directly from Tonkeeper 👇",
        "tasks_title":      "📋 *Available Tasks*\n\nComplete tasks to earn extra YOR:",
        "task_channel":     "✅ Join the official channel (+{r} YOR)",
        "task_ref":         "👥 Invite friends (+{r} YOR each)",
        "task_done":        "✅ Task already completed",
        "task_channel_ok":  "🎉 Task complete! +{r} {t} for joining the channel",
        "task_channel_no":  "❌ You are not in the channel yet. Join first and verify again.",
        "ref_title":        "👥 *Your referral link:*\n\n`{link}`\n\n💰 You earn *{r} YOR* per friend who joins\n👤 Total referrals: {count}",
        "ref_bonus":        "🎉 {name} joined with your link! +{r} {t}",
        "event_end_msg":    "🎉 *EVENT FINISHED*\n\n💰 You earned: *{amt} TON*\n\nThank you for participating 🚀",
        "boost_ok":         "✅ *Payment confirmed*\n\n🚀 Boost x{m} active\n💰 Paid: {v} TON\n\n🔥 You are mining faster",
        "admin_stats":      "🛠 *Admin Stats*\n\nWithdraw pool: {pool} TON\nOwner profit: {profit} TON\nEvent reserve: {res} TON\nUsers: {users}\nTotal tokens: {total}",
        "lang_set":         "✅ Language set: English",
        "btn_mine":         "⛏ Mine",
        "btn_balance":      "💰 Balance",
        "btn_shop":         "🛒 Shop",
        "btn_tasks":        "📋 Tasks",
        "btn_ranking":      "🏆 Ranking",
        "btn_status":       "📊 Status",
        "btn_referral":     "👥 Referrals",
        "btn_verify":       "✅ Verify",
        "btn_join":         "📢 Join Channel",
        "btn_back":         "🔙 Back",
        "btn_lang":         "🌐 Language",
    }
}

TASK_CHANNEL_REWARD = 50   # YOR por unirse al canal
TASK_REF_REWARD     = 20   # YOR por cada referido

# ─────────────────────────────────────────
# 📦 CARGAR / GUARDAR DATOS
# ─────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
    else:
        d = {}

    d.setdefault("balances",      {})
    d.setdefault("last_mine",     {})
    d.setdefault("withdraw_pool", 0)
    d.setdefault("owner_profit",  0)
    d.setdefault("event_reserve", 0)
    d.setdefault("user_boost",    {})
    d.setdefault("processed",     [])
    d.setdefault("referrals",     {})
    d.setdefault("ref_count",     {})
    d.setdefault("task_done",     {})
    d.setdefault("lang",          {})

    if "event_end_time" not in d:
        d["event_end_time"] = time.time() + EVENT_DURATION

    d["total_tokens"] = sum(d["balances"].values())

    return d

data = load_data()

def save():
    if len(data["processed"]) > 10000:
        data["processed"] = data["processed"][-5000:]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

event_end_time  = data["event_end_time"]
event_finished  = time.time() > event_end_time

# ─────────────────────────────────────────
# 🛠 HELPERS
# ─────────────────────────────────────────
def lang(uid: str) -> str:
    return data["lang"].get(str(uid), "es")

def t(uid, key, **kwargs) -> str:
    text = T[lang(uid)][key]
    return text.format(**kwargs) if kwargs else text

def fmt_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}h {m:02d}m {s:02d}s"

def main_menu(uid):
    l = lang(uid)
    kb = [
        [
            InlineKeyboardButton(T[l]["btn_mine"],     callback_data="mine"),
            InlineKeyboardButton(T[l]["btn_balance"],  callback_data="balance"),
        ],
        [
            InlineKeyboardButton(T[l]["btn_shop"],     callback_data="shop"),
            InlineKeyboardButton(T[l]["btn_tasks"],    callback_data="tasks"),
        ],
        [
            InlineKeyboardButton(T[l]["btn_ranking"],  callback_data="ranking"),
            InlineKeyboardButton(T[l]["btn_status"],   callback_data="status"),
        ],
        [
            InlineKeyboardButton(T[l]["btn_referral"], callback_data="referral"),
            InlineKeyboardButton(T[l]["btn_lang"],     callback_data="change_lang"),
        ],
    ]
    return InlineKeyboardMarkup(kb)

def back_btn(uid):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(uid, "btn_back"), callback_data="menu")
    ]])

# ─────────────────────────────────────────
# 🚀 BOOSTS
# ─────────────────────────────────────────
boosts = {
    1:  {"price": 0.5,  "mult": 1.5,  "time": 3600},
    2:  {"price": 1,    "mult": 2,    "time": 7200},
    3:  {"price": 2,    "mult": 2.5,  "time": 14400},
    4:  {"price": 3,    "mult": 3,    "time": 21600},
    5:  {"price": 5,    "mult": 3.5,  "time": 43200},
    6:  {"price": 8,    "mult": 4,    "time": 86400},
    7:  {"price": 12,   "mult": 5,    "time": 172800},
    8:  {"price": 20,   "mult": 6,    "time": 259200},
    9:  {"price": 30,   "mult": 7,    "time": 432000},
    10: {"price": 50,   "mult": 10,   "time": 604800},
}

# ─────────────────────────────────────────
# 📲 COMANDOS
# ─────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if context.args:
        ref_id = context.args[0]
        if (
            ref_id != uid
            and uid not in data["referrals"]
            and ref_id in data["balances"]
        ):
            data["referrals"][uid] = ref_id
            data["ref_count"][ref_id] = data["ref_count"].get(ref_id, 0) + 1
            data["balances"][ref_id] = data["balances"].get(ref_id, 0) + TASK_REF_REWARD
            data["total_tokens"] += TASK_REF_REWARD
            save()
            name = update.effective_user.first_name or uid
            try:
                await context.bot.send_message(
                    chat_id=int(ref_id),
                    text=t(ref_id, "ref_bonus", name=name, r=TASK_REF_REWARD, t=TOKEN_NAME),
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    if uid not in data["lang"]:
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]])
        await update.message.reply_text(T["es"]["choose_lang"], reply_markup=kb)
        return

    if uid not in data["balances"]:
        data["balances"][uid] = 0
        save()

    await update.message.reply_text(
        t(uid, "welcome"),
        parse_mode="Markdown",
        reply_markup=main_menu(uid)
    )

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != ADMIN_ID:
        return
    await update.message.reply_text(
        T["es"]["admin_stats"].format(
            pool   = round(data["withdraw_pool"], 4),
            profit = round(data["owner_profit"],  4),
            res    = round(data["event_reserve"], 4),
            users  = len(data["balances"]),
            total  = round(data["total_tokens"],  2),
        ),
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────
# 🎛 CALLBACKS
# ─────────────────────────────────────────
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = str(q.from_user.id)
    cd  = q.data
    await q.answer()

    if cd in ("lang_es", "lang_en"):
        chosen = cd.split("_")[1]
        data["lang"][uid] = chosen
        if uid not in data["balances"]:
            data["balances"][uid] = 0
        save()
        await q.edit_message_text(
            T[chosen]["lang_set"] + "\n\n" + T[chosen]["welcome"],
            parse_mode="Markdown",
            reply_markup=main_menu(uid)
        )
        return

    if cd == "change_lang":
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]])
        await q.edit_message_text(T["es"]["choose_lang"], reply_markup=kb)
        return

    if cd == "menu":
        await q.edit_message_text(
            t(uid, "menu_title"),
            parse_mode="Markdown",
            reply_markup=main_menu(uid)
        )
        return

    if cd == "mine":
        if event_finished:
            await q.edit_message_text(t(uid, "mine_event_over"), reply_markup=back_btn(uid))
            return

        now  = time.time()
        last = data["last_mine"].get(uid, 0)
        wait = 10 - (now - last)

        if wait > 0:
            await q.edit_message_text(
                t(uid, "mine_cooldown", s=int(wait)),
                parse_mode="Markdown",
                reply_markup=back_btn(uid)
            )
            return

        data["last_mine"][uid] = now
        reward = 1.0

        boost_info = data["user_boost"].get(uid)
        if boost_info:
            mult, exp = boost_info
            if now < exp:
                reward *= mult
            else:
                del data["user_boost"][uid]

        reward = round(min(reward, 100), 2)
        data["balances"][uid]  = round(data["balances"].get(uid, 0) + reward, 2)
        data["total_tokens"]   = round(data["total_tokens"] + reward, 2)
        save()

        await q.edit_message_text(
            t(uid, "mine_success", r=reward, t=TOKEN_NAME),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    if cd == "balance":
        tokens = data["balances"].get(uid, 0)
        total  = data["total_tokens"]
        est    = round(data["withdraw_pool"] * tokens / total, 4) if total > 0 else 0
        await q.edit_message_text(
            t(uid, "balance_msg", tok=round(tokens, 2), t=TOKEN_NAME, est=est),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    if cd == "status":
        remaining = event_end_time - time.time()
        await q.edit_message_text(
            t(uid, "status_msg",
              pool   = round(data["withdraw_pool"], 4),
              total  = round(data["total_tokens"],  2),
              tiempo = fmt_time(remaining)),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    if cd == "ranking":
        top  = sorted(data["balances"].items(), key=lambda x: x[1], reverse=True)[:10]
        text = t(uid, "ranking_title")
        for i, (u, amt) in enumerate(top, 1):
            text += t(uid, "ranking_row", i=i, u=u, a=round(amt, 2))
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_btn(uid))
        return

    if cd == "shop":
        keyboard = []
        for k, v in boosts.items():
            amount = int(v["price"] * 1e9)
            url    = (
                f"https://app.tonkeeper.com/transfer/{TON_WALLET}"
                f"?amount={amount}&text={uid}-{k}"
            )
            keyboard.append([InlineKeyboardButton(
                f"x{v['mult']} — {v['price']} TON  ({fmt_time(v['time'])})",
                url=url
            )])
        keyboard.append([InlineKeyboardButton(t(uid, "btn_back"), callback_data="menu")])
        await q.edit_message_text(
            t(uid, "shop_title"),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if cd == "tasks":
        done  = data["task_done"].get(uid, [])
        l     = lang(uid)
        ch_label  = T[l]["task_done"] if "channel" in done else T[l]["task_channel"].format(r=TASK_CHANNEL_REWARD)
        ref_label = T[l]["task_ref"].format(r=TASK_REF_REWARD)

        kb = []
        if "channel" not in done:
            kb.append([InlineKeyboardButton(T[l]["btn_join"],   url=CHANNEL_LINK)])
            kb.append([InlineKeyboardButton(T[l]["btn_verify"], callback_data="verify_channel")])
        kb.append([InlineKeyboardButton(T[l]["btn_referral"], callback_data="referral")])
        kb.append([InlineKeyboardButton(T[l]["btn_back"],     callback_data="menu")])

        text  = t(uid, "tasks_title") + "\n\n"
        text += f"1. {ch_label}\n"
        text += f"2. {ref_label}"

        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return

    if cd == "verify_channel":
        try:
            member    = await context.bot.get_chat_member(CHANNEL_ID, int(uid))
            is_member = member.status in ("member", "administrator", "creator")
        except Exception:
            is_member = False

        if is_member:
            done = data["task_done"].setdefault(uid, [])
            if "channel" not in done:
                done.append("channel")
                data["balances"][uid]  = round(data["balances"].get(uid, 0) + TASK_CHANNEL_REWARD, 2)
                data["total_tokens"]   = round(data["total_tokens"] + TASK_CHANNEL_REWARD, 2)
                save()
            await q.edit_message_text(
                t(uid, "task_channel_ok", r=TASK_CHANNEL_REWARD, t=TOKEN_NAME),
                parse_mode="Markdown",
                reply_markup=back_btn(uid)
            )
        else:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(t(uid, "btn_join"),   url=CHANNEL_LINK)],
                [InlineKeyboardButton(t(uid, "btn_verify"), callback_data="verify_channel")],
                [InlineKeyboardButton(t(uid, "btn_back"),   callback_data="tasks")],
            ])
            await q.edit_message_text(t(uid, "task_channel_no"), reply_markup=kb)
        return

    if cd == "referral":
        bot_info = await context.bot.get_me()
        link     = f"https://t.me/{bot_info.username}?start={uid}"
        count    = data["ref_count"].get(uid, 0)
        await q.edit_message_text(
            t(uid, "ref_title", link=link, r=TASK_REF_REWARD, count=count),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

# ─────────────────────────────────────────
# 🔍 WATCHER DE PAGOS TON
# ─────────────────────────────────────────
async def payment_watcher(app):
    while True:
        try:
            r   = requests.get(API_URL, params={"address": TON_WALLET, "limit": 20}, timeout=10)
            txs = r.json().get("result", [])

            for tx in txs:
                try:
                    msg   = tx["in_msg"].get("message", "")
                    value = int(tx["in_msg"]["value"]) / 1e9
                    tx_id = tx["transaction_id"]["hash"]

                    if tx_id in data["processed"]:
                        continue

                    if msg and "-" in msg:
                        parts = msg.split("-")
                        if len(parts) != 2:
                            continue
                        uid_str, lvl_str = parts
                        if not uid_str.isdigit() or not lvl_str.isdigit():
                            continue

                        user_id = uid_str
                        level   = int(lvl_str)

                        if level not in boosts:
                            continue
                        b = boosts[level]
     

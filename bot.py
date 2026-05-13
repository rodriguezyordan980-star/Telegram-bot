import os
import time
import json
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ─────────────────────────────────────────
# 🔐 CONFIG
# ─────────────────────────────────────────
TOKEN      = os.getenv("TOKEN")
TON_WALLET = "UQDYM7ld7G-HyC2jiFDVWOZ42qzMe93lsf6uO8pSlqAOTO4P"
ADMIN_ID   = 7671435882
TOKEN_NAME = "YOR"

API_URL        = "https://toncenter.com/api/v2/getTransactions"
DATA_FILE      = "data.json"
EVENT_DURATION = 15 * 24 * 60 * 60

TASK_REF_REWARD = 20  # YOR por referido

# ─────────────────────────────────────────
# 🌐 TEXTOS
# ─────────────────────────────────────────
T = {
    "es": {
        "choose_lang":     "🌐 Elige tu idioma / Choose your language:",
        "welcome":         (
            "👋 ¡Bienvenido a *YOR Mining Bot*!\n\n"
            "⛏ Mina tokens YOR gratis\n"
            "💰 Gana TON real al final del evento\n"
            "📈 Más tokens = mayor ganancia\n\n"
            "📌 Los retiros se realizan *solo al final del evento*\n\n"
            "Usa el menú de abajo 👇"
        ),
        "menu_title":      "📋 *Menú principal*\nElige una opción:",
        "mine_cooldown":   "⏳ Espera *{s}s* para volver a minar",
        "mine_success":    "⛏ +*{r}* {t}\n\n⚡ Compra un boost en la Tienda para ganar más",
        "mine_event_over": "❌ El evento ya terminó",
        "balance_msg":     "🪙 *Tus tokens:* {tok} {t}\n💰 *Ganancia estimada:* {est} TON\n\n⏳ Se paga al final del evento",
        "status_msg":      "📊 *Estado del evento*\n\n💰 Pool total: {pool} TON\n🪙 Tokens minados: {total}\n⏳ Tiempo restante: {tiempo}",
        "ranking_title":   "🏆 *TOP 10 mineros*\n\n",
        "ranking_row":     "{i}. `{u}` → {a} YOR\n",
        "shop_title":      "🛒 *Tienda de Boosts*\n\nElige tu boost y paga directo desde Tonkeeper 👇",
        "tasks_title":     "📋 *Tareas disponibles*\n\nCompleta tareas y gana YOR extra:\n\n",
        "tasks_empty":     "📋 *Tareas*\n\nNo hay tareas disponibles por ahora.\nVuelve pronto 👀",
        "task_ref":        "👥 Invitar amigos (+{r} YOR por cada uno)",
        "task_done_label": "☑️",
        "task_verify_btn": "✅ Verificar #{n}",
        "task_join_btn":   "📢 Unirse #{n}",
                "task_channel_ok": "🎉 ¡Tarea completada! +*{r} YOR* por unirte a {ch}",
        "task_channel_no": "❌ Aún no estás en el canal.\nÚnete primero y vuelve a verificar.",
        "task_already":    "✅ Ya completaste esta tarea",
        "ref_title":       "👥 *Tu enlace de referido:*\n\n`{link}`\n\n💰 Ganas *{r} YOR* por cada amigo\n👤 Referidos: {count}",
        "ref_bonus":       "🎉 ¡{name} se unió con tu enlace! +{r} {t}",
        "event_end_msg":   "🎉 *EVENTO FINALIZADO*\n\n💰 Ganaste: *{amt} TON*\n\nGracias por participar 🚀",
        "boost_ok":        "✅ *Pago confirmado*\n\n🚀 Boost x{m} activado\n💰 Pagado: {v} TON\n\n🔥 Estás minando más rápido",
        "lang_set":        "✅ Idioma: Español",
        "btn_mine":        "⛏ Minar",
        "btn_balance":     "💰 Balance",
        "btn_shop":        "🛒 Tienda",
        "btn_tasks":       "📋 Tareas",
        "btn_ranking":     "🏆 Ranking",
        "btn_status":      "📊 Estado",
        "btn_referral":    "👥 Referidos",
        "btn_back":        "🔙 Volver",
        "btn_lang":        "🌐 Idioma",
        "admin_stats":     (
            "🛠 *Admin Panel*\n\n"
            "💰 Pool retiros: {pool} TON\n"
            "💵 Ganancia tuya: {profit} TON\n"
            "🏦 Reserva evento: {res} TON\n"
            "👤 Usuarios: {users}\n"
            "🪙 Total tokens: {total}\n\n"
            "📢 *Tareas activas:* {ntasks}\n\n"
            "Comandos admin:\n"
            "/addtask @canal RECOMPENSA\n"
            "/removetask @canal\n"
            "/listtasks"
        ),
        "task_added":      "✅ Tarea añadida:\nCanal: {ch}\nRecompensa: {r} YOR",
        "task_removed":    "🗑 Tarea eliminada: {ch}",
        "task_not_found":  "❌ No se encontró tarea para {ch}",
        "task_usage":      "Uso: /addtask @canal RECOMPENSA_YOR\nEjemplo: /addtask @micanal 30",
        "no_permission":   "⛔ No tienes permiso",
    },
    "en": {
        "choose_lang":     "🌐 Elige tu idioma / Choose your language:",
        "welcome":         (
            "👋 Welcome to *YOR Mining Bot*!\n\n"
            "⛏ Mine YOR tokens for free\n"
            "💰 Earn real TON at the end of the event\n"
            "📈 More tokens = bigger reward\n\n"
            "📌 Withdrawals happen *only at the end of the event*\n\n"
            "Use the menu below 👇"
        ),
        "menu_title":      "📋 *Main Menu*\nChoose an option:",
        "mine_cooldown":   "⏳ Wait *{s}s* to mine again",
        "mine_success":    "⛏ +*{r}* {t}\n\n⚡ Buy a boost in the Shop to earn more",
        "mine_event_over": "❌ The event is over",
        "balance_msg":     "🪙 *Your tokens:* {tok} {t}\n💰 *Estimated earnings:* {est} TON\n\n⏳ Paid at the end of the event",
        "status_msg":      "📊 *Event Status*\n\n💰 Total pool: {pool} TON\n🪙 Mined tokens: {total}\n⏳ Time left: {tiempo}",
                "ranking_title":   "🏆 *TOP 10 Miners*\n\n",
        "ranking_row":     "{i}. `{u}` → {a} YOR\n",
        "shop_title":      "🛒 *Boost Shop*\n\nChoose your boost and pay directly from Tonkeeper 👇",
        "tasks_title":     "📋 *Available Tasks*\n\nComplete tasks to earn extra YOR:\n\n",
        "tasks_empty":     "📋 *Tasks*\n\nNo tasks available right now.\nCheck back soon 👀",
        "task_ref":        "👥 Invite friends (+{r} YOR each)",
        "task_done_label": "☑️",
        "task_verify_btn": "✅ Verify #{n}",
        "task_join_btn":   "📢 Join #{n}",
        "task_channel_ok": "🎉 Task complete! +*{r} YOR* for joining {ch}",
        "task_channel_no": "❌ You are not in the channel yet.\nJoin first then verify.",
        "task_already":    "✅ Task already completed",
        "ref_title":       "👥 *Your referral link:*\n\n`{link}`\n\n💰 You earn *{r} YOR* per friend\n👤 Referrals: {count}",
        "ref_bonus":       "🎉 {name} joined with your link! +{r} {t}",
        "event_end_msg":   "🎉 *EVENT FINISHED*\n\n💰 You earned: *{amt} TON*\n\nThank you for participating 🚀",
        "boost_ok":        "✅ *Payment confirmed*\n\n🚀 Boost x{m} active\n💰 Paid: {v} TON\n\n🔥 You are mining faster",
        "lang_set":        "✅ Language: English",
        "btn_mine":        "⛏ Mine",
        "btn_balance":     "💰 Balance",
        "btn_shop":        "🛒 Shop",
        "btn_tasks":       "📋 Tasks",
        "btn_ranking":     "🏆 Ranking",
        "btn_status":      "📊 Status",
        "btn_referral":    "👥 Referrals",
        "btn_back":        "🔙 Back",
        "btn_lang":        "🌐 Language",
        "admin_stats":     (
            "🛠 *Admin Panel*\n\n"
            "💰 Withdraw pool: {pool} TON\n"
            "💵 Your profit: {profit} TON\n"
            "🏦 Event reserve: {res} TON\n"
            "👤 Users: {users}\n"
            "🪙 Total tokens: {total}\n\n"
            "📢 *Active tasks:* {ntasks}\n\n"
            "Admin commands:\n"
            "/addtask @channel REWARD\n"
            "/removetask @channel\n"
            "/listtasks"
        ),
        "task_added":      "✅ Task added:\nChannel: {ch}\nReward: {r} YOR",
        "task_removed":    "🗑 Task removed: {ch}",
        "task_not_found":  "❌ Task not found for {ch}",
        "task_usage":      "Usage: /addtask @channel REWARD_YOR\nExample: /addtask @mychannel 30",
        "no_permission":   "⛔ No permission",
    }
}

# ─────────────────────────────────────────
# 📦 DATOS
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
    # Tareas de canales de pago
    # Formato: [{"channel": "@canal", "link": "https://t.me/canal", "reward": 30}, ...]
    d.setdefault("paid_tasks",    [])

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

event_end_time = data["event_end_time"]
event_finished = time.time() > event_end_time

# ─────────────────────────────────────────
# 🛠 HELPERS
# ─────────────────────────────────────────
def lang(uid: str) -> str:
    return data["lang"].get(str(uid), "es")

def tx(uid, key, **kwargs) -> str:
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
        InlineKeyboardButton(tx(uid, "btn_back"), callback_data="menu")
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
            data["balances"][ref_id]  = data["balances"].get(ref_id, 0) + TASK_REF_REWARD
            data["total_tokens"]      += TASK_REF_REWARD
            save()
            name = update.effective_user.first_name or uid
            try:
                await context.bot.send_message(
                    chat_id=int(ref_id),
                    text=tx(ref_id, "ref_bonus", name=name, r=TASK_REF_REWARD, t=TOKEN_NAME),
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
        tx(uid, "welcome"),
        parse_mode="Markdown",
        reply_markup=main_menu(uid)
    )

# ── /admin ───────────────────────────────
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        T["es"]["admin_stats"].format(
            pool   = round(data["withdraw_pool"], 4),
            profit = round(data["owner_profit"],  4),
            res    = round(data["event_reserve"], 4),
            users  = len(data["balances"]),
            total  = round(data["total_tokens"],  2),
            ntasks = len(data["paid_tasks"]),
        ),
        parse_mode="Markdown"
    )

# ── /addtask @canal RECOMPENSA ────────────
async def cmd_addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(T["es"]["no_permission"])
        return

    if len(context.args) < 2:
        await update.message.reply_text(T["es"]["task_usage"])
        return

    channel = context.args[0]
    if not channel.startswith("@"):
        channel = "@" + channel

    try:
        reward = int(context.args[1])
    except ValueError:
        await update.message.reply_text(T["es"]["task_usage"])
        return

    link = f"https://t.me/{channel.lstrip('@')}"
    
    # Si ya existe, actualizar
    for task in data["paid_tasks"]:
        if task["channel"] == channel:
            task["reward"] = reward
            task["link"]   = link
            save()
            await update.message.reply_text(
                f"✏️ Tarea actualizada:\nCanal: {channel}\nRecompensa: {reward} YOR"
            )
            return

    data["paid_tasks"].append({
        "channel": channel,
        "link":    link,
        "reward":  reward
    })
    save()
    await update.message.reply_text(
        T["es"]["task_added"].format(ch=channel, r=reward)
    )

# ── /removetask @canal ────────────────────
async def cmd_removetask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(T["es"]["no_permission"])
        return

    if not context.args:
        await update.message.reply_text("Uso: /removetask @canal")
        return

    channel = context.args[0]
    if not channel.startswith("@"):
        channel = "@" + channel

    before = len(data["paid_tasks"])
    data["paid_tasks"] = [t for t in data["paid_tasks"] if t["channel"] != channel]

    if len(data["paid_tasks"]) < before:
        save()
        await update.message.reply_text(T["es"]["task_removed"].format(ch=channel))
    else:
        await update.message.reply_text(T["es"]["task_not_found"].format(ch=channel))

# ── /listtasks ────────────────────────────
async def cmd_listtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not data["paid_tasks"]:
        await update.message.reply_text("📋 No hay tareas activas.")
        return

    text = "📋 *Tareas activas:*\n\n"
    for i, task in enumerate(data["paid_tasks"], 1):
        text += f"{i}. {task['channel']} → *{task['reward']} YOR*\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ─────────────────────────────────────────
# 🎛 CALLBACKS
# ─────────────────────────────────────────
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = str(q.from_user.id)
    cd  = q.data
    await q.answer()

    # ── Idioma ──────────────────────────
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

    # ── Menú ────────────────────────────
    if cd == "menu":
        await q.edit_message_text(
            tx(uid, "menu_title"),
            parse_mode="Markdown",
            reply_markup=main_menu(uid)
        )
        return

    # ── Minar ───────────────────────────
    if cd == "mine":
        if event_finished:
            await q.edit_message_text(tx(uid, "mine_event_over"), reply_markup=back_btn(uid))
            return

        now  = time.time()
        wait = 10 - (now - data["last_mine"].get(uid, 0))

        if wait > 0:
            await q.edit_message_text(
                tx(uid, "mine_cooldown", s=int(wait)),
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
            tx(uid, "mine_success", r=reward, t=TOKEN_NAME),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    # ── Balance ─────────────────────────
    if cd == "balance":
        tokens = data["balances"].get(uid, 0)
        total  = data["total_tokens"]
        est    = round(data["withdraw_pool"] * tokens / total, 4) if total > 0 else 0
        await q.edit_message_text(
            tx(uid, "balance_msg", tok=round(tokens, 2), t=TOKEN_NAME, est=est),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    # ── Estado ──────────────────────────
    if cd == "status":
        await q.edit_message_text(
            tx(uid, "status_msg",
               pool   = round(data["withdraw_pool"], 4),
               total  = round(data["total_tokens"],  2),
               tiempo = fmt_time(event_end_time - time.time())),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
        )
        return

    # ── Ranking ─────────────────────────
    if cd == "ranking":
        top  = sorted(data["balances"].items(), key=lambda x: x[1], reverse=True)[:10]
        text = tx(uid, "ranking_title")
        for i, (u, amt) in enumerate(top, 1):
            text += tx(uid, "ranking_row", i=i, u=u, a=round(amt, 2))
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_btn(uid))
        return

    # ── Tienda ──────────────────────────
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
        keyboard.append([InlineKeyboardButton(tx(uid, "btn_back"), callback_data="menu")])
        await q.edit_message_text(
            tx(uid, "shop_title"),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ── Tareas ──────────────────────────
    if cd == "tasks":
        tasks     = data["paid_tasks"]
        done_list = data["task_done"].get(uid, [])
        l         = lang(uid)

        if not tasks:
            await q.edit_message_text(
                T[l]["tasks_empty"],
                parse_mode="Markdown",
                reply_markup=back_btn(uid)
            )
            return

        text = T[l]["tasks_title"]
        kb   = []

        for i, task in enumerate(tasks, 1):
            ch     = task["channel"]
            reward = task["reward"]
            done   = ch in done_list
            status = T[l]["task_done_label"] if done else "🔲"
            text  += f"{status} *Tarea {i}:* Únete a {ch} → +{reward} YOR\n"

            if not done:
                kb.append([
                    InlineKeyboardButton(
                        T[l]["task_join_btn"].format(n=i),
                        url=task["link"]
                    ),
                    InlineKeyboardButton(
                        T[l]["task_verify_btn"].format(n=i),
                        callback_data=f"verify_{i-1}"
                    ),
                ])

        text += f"\n👥 *Referidos:* +{TASK_REF_REWARD} YOR por cada amigo"
        kb.append([InlineKeyboardButton(T[l]["btn_referral"], callback_data="referral")])
        kb.append([InlineKeyboardButton(T[l]["btn_back"],     callback_data="menu")])

        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
              )
        return

    # ── Verificar tarea canal ────────────
    if cd.startswith("verify_"):
        try:
            idx  = int(cd.split("_")[1])
            task = data["paid_tasks"][idx]
        except (IndexError, ValueError):
            await q.edit_message_text("❌ Tarea no encontrada.", reply_markup=back_btn(uid))
            return

        channel   = task["channel"]
        reward    = task["reward"]
        done_list = data["task_done"].get(uid, [])

        if channel in done_list:
            await q.answer(tx(uid, "task_already"), show_alert=True)
            return

        try:
            member    = await context.bot.get_chat_member(channel, int(uid))
            is_member = member.status in ("member", "administrator", "creator")
        except Exception:
            is_member = False

        if is_member:
            done_list.append(channel)
            data["task_done"][uid]  = done_list
            data["balances"][uid]   = round(data["balances"].get(uid, 0) + reward, 2)
            data["total_tokens"]    = round(data["total_tokens"] + reward, 2)
            save()
            await q.edit_message_text(
                tx(uid, "task_channel_ok", r=reward, ch=channel),
                parse_mode="Markdown",
                reply_markup=back_btn(uid)
            )
        else:
            l  = lang(uid)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(T[l]["task_join_btn"].format(n=idx+1),    url=task["link"])],
                [InlineKeyboardButton(T[l]["task_verify_btn"].format(n=idx+1),  callback_data=cd)],
                [InlineKeyboardButton(T[l]["btn_back"],                          callback_data="tasks")],
            ])
            await q.edit_message_text(tx(uid, "task_channel_no"), reply_markup=kb)
        return

    # ── Referidos ───────────────────────
    if cd == "referral":
        bot_info = await context.bot.get_me()
        link     = f"https://t.me/{bot_info.username}?start={uid}"
        count    = data["ref_count"].get(uid, 0)
        await q.edit_message_text(
            tx(uid, "ref_title", link=link, r=TASK_REF_REWARD, count=count),
            parse_mode="Markdown",
            reply_markup=back_btn(uid)
                )
        return

# ─────────────────────────────────────────
# 🔍 WATCHER DE PAGOS
# ─────────────────────────────────────────
async def payment_watcher(app):
    while True:
        try:
            r   = requests.get(API_URL, params={"address": TON_WALLET, "limit": 20}, timeout=10)
            txs = r.json().get("result", [])

            for transaction in txs:
                try:
                    msg   = transaction["in_msg"].get("message", "")
                    value = int(transaction["in_msg"]["value"]) / 1e9
                    tx_id = transaction["transaction_id"]["hash"]

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
                        if value < b["price"]:
                            continue

                        data["processed"].append(tx_id)
                        data["user_boost"][user_id] = [b["mult"], time.time() + b["time"]]
                        data["withdraw_pool"] += value * 0.5
                        data["owner_profit"]  += value * 0.3
                        data["event_reserve"] += value * 0.2
                        save()

                        await app.bot.send_message(
                            chat_id=int(user_id),
                            text=tx(user_id, "boost_ok", m=b["mult"], v=round(value, 4)),
                            parse_mode="Markdown"
                        )
                except Exception:
                    continue
        except Exception:
            pass

        await asyncio.sleep(10)

# ─────────────────────────────────────────
# 🏁 FIN DEL EVENTO
# ─────────────────────────────────────────
async def finish_event(app):
    global event_finished
    while True:
        if not event_finished and time.time() > event_end_time:
            event_finished = True
            total = data["total_tokens"]
            for user, tokens in data["balances"].items():
                if tokens == 0:
                    continue
                share  = tokens / total if total > 0 else 0
                amount = round(data["withdraw_pool"] * share, 4)
                try:
                    await app.bot.send_message(
                        chat_id=int(user),
                        text=tx(user, "event_end_msg", amt=amount),
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass
        await asyncio.sleep(30)

# ─────────────────────────────────────────
# 🚀 ARRANQUE
# ─────────────────────────────────────────
async def on_startup(app):
    asyncio.create_task(payment_watcher(app))
    asyncio.create_task(finish_event(app))

application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start",      cmd_start))
application.add_handler(CommandHandler("admin",      cmd_admin))
application.add_handler(CommandHandler("addtask",    cmd_addtask))
application.add_handler(CommandHandler("removetask", cmd_removetask))
application.add_handler(CommandHandler("listtasks",  cmd_listtasks))
application.add_handler(CallbackQueryHandler(on_callback))

application.post_init = on_startup

print("✅ YOR Mining Bot ACTIVO")
application.run_polling()

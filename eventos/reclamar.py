import sqlite3
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.logros import dar_logro

COOLDOWN = 24 * 60 * 60


def init_reclamar_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reclamaciones (
            user_id INTEGER PRIMARY KEY,
            ultima_reclamacion REAL,
            racha INTEGER DEFAULT 0,
            ultima_fecha TEXT
        )
    """)
    conn.commit()
    conn.close()


def obtener_reclamacion(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_reclamacion, racha, ultima_fecha FROM reclamaciones WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r


def set_reclamacion(user_id, timestamp, racha, fecha):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO reclamaciones (user_id, ultima_reclamacion, racha, ultima_fecha) VALUES (?, ?, ?, ?)",
        (user_id, timestamp, racha, fecha)
    )
    conn.commit()
    conn.close()


def premio_por_nivel(nivel):
    if nivel < 20:
        return 150, 100
    elif nivel < 50:
        return 250, 300
    elif nivel < 70:
        return 500, 500
    elif nivel < 100:
        return 750, 700
    else:
        return 1000, 1000


def formatear_tiempo(seg):
    horas = int(seg // 3600)
    minutos = int((seg % 3600) // 60)
    return f"{horas}h {minutos}m"


async def reclamar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    nombre, _, _, _, nivel, _ = datos
    ahora = time.time()
    fecha_hoy = time.strftime("%Y-%m-%d")

    rec = obtener_reclamacion(user_id)

    if rec is None:
        racha = 1
    else:
        ultima_rec, racha_actual, ultima_fecha = rec
        if ahora - ultima_rec < COOLDOWN:
            restante = COOLDOWN - (ahora - ultima_rec)
            await update.message.reply_text(
                f"⏳ *Ya reclamaste*\nVuelve en: *{formatear_tiempo(restante)}*\n\n"
                f"🔥 Racha actual: *{racha_actual}* días",
                parse_mode="Markdown"
            )
            return

        fecha_ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if ultima_fecha == fecha_ayer:
            racha = racha_actual + 1
        else:
            racha = 1

    es_dia_7 = (racha % 7 == 0)
    tokens_base, xp_base = premio_por_nivel(nivel)

    if es_dia_7:
        tokens_ganados = tokens_base * 2
        xp_ganados = xp_base * 2
    else:
        tokens_ganados = tokens_base
        xp_ganados = xp_base

    actualizar_tokens(user_id, tokens_ganados)
    subio = sumar_xp(user_id, xp_ganados)

    set_reclamacion(user_id, ahora, racha, fecha_hoy)

    # ─── Logros de racha ───────────────────────────────────
    if racha >= 7:
        if dar_logro(user_id, "racha_7"):
            await avisar_logro(context, user_id, "racha_7")

    if racha >= 30:
        if dar_logro(user_id, "racha_30"):
            await avisar_logro(context, user_id, "racha_30")

    texto = (
        f"🎁 *¡RECOMPENSA RECLAMADA!*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *{nombre}* (Nivel {nivel})\n\n"
        f"💰 +{tokens_ganados} tokens\n"
        f"✨ +{xp_ganados} XP\n"
    )

    if es_dia_7:
        texto += f"\n🔥 *¡BONUS DE RACHA!*\n¡Llevas *{racha}* días seguidos!\nTu premio se ha *DUPLICADO* 🎉"

    if subio:
        texto += f"\n\n⭐ *¡Subiste al nivel {subio}!*"

    texto += f"\n\n━━━━━━━━━━━━━━━━━━━\n🔥 Racha: *{racha}* días\n⏳ Vuelve en 24h"

    await update.message.reply_text(texto, parse_mode="Markdown")


async def avisar_logro(context, user_id, clave):
    from core.logros import LOGROS
    info = LOGROS.get(clave)
    if not info:
        return
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🏆 *¡LOGRO DESBLOQUEADO!*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"{info['emoji']} *{info['nombre']}*\n"
                f"_{info['descripcion']}_"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

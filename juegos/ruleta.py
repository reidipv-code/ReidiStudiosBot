import sqlite3
import random
import time
import os
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp
from core.sesiones import iniciar_partida, terminar_partida

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "usuarios.db")

COLORES_VALIDOS = ["rojo", "verde", "azul", "amarillo", "naranja", "morado", "azul claro"]

EMOJIS_COLORES = {
    "rojo": "🔴", "verde": "🟢", "azul": "🔵", "amarillo": "🟡",
    "naranja": "🟠", "morado": "🟣", "azul claro": "🔷"
}

APUESTA = 20
PREMIO_TOKENS = 50
PREMIO_XP = 30
COOLDOWN = 300


def init_juegos_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id INTEGER PRIMARY KEY,
            ultima_tirada REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_tirada FROM cooldowns WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO cooldowns (user_id, ultima_tirada) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima = get_cooldown(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


async def ruleta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado y con sesión activa.\nUsa /reg tu_nombre")
        return

    if not context.args:
        await update.message.reply_text(
            "🎰 *RULETA*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "Elige un color.\n"
            "Uso: `/ruleta rojo`\n"
            "Colores: rojo, verde, azul, amarillo, naranja, morado, azul claro\n\n"
            "• Apuesta: 20 tokens\n"
            "• Acierto: +50 tokens, +30 XP\n"
            "• Fallo: -20 tokens\n"
            "• Cooldown: 5 min",
            parse_mode="Markdown"
        )
        return

    eleccion = " ".join(context.args).lower().strip()

    if eleccion not in COLORES_VALIDOS:
        await update.message.reply_text(
            f"❌ Color no válido: *{eleccion}*\n"
            "Colores: rojo, verde, azul, amarillo, naranja, morado, azul claro",
            parse_mode="Markdown"
        )
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(
            f"⏳ Debes esperar *{formatear_tiempo(restante)}* para volver a girar.",
            parse_mode="Markdown"
        )
        return

    nombre, id_interno, tokens, xp, nivel, _ = datos

    if tokens < APUESTA:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens.\nNecesitas *{APUESTA}* y tienes *{tokens}*.",
            parse_mode="Markdown"
        )
        return

    resultado = random.choice(COLORES_VALIDOS)
    emoji_resultado = EMOJIS_COLORES[resultado]

    if resultado == eleccion:
        actualizar_tokens(user_id, PREMIO_TOKENS)
        subio = sumar_xp(user_id, PREMIO_XP)
        texto = (
            f"🎰 *RULETA*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Elegiste: {EMOJIS_COLORES[eleccion]} *{eleccion}*\n"
            f"🎲 Cayó en: {emoji_resultado} *{resultado}*\n\n"
            f"🎉 *¡GANASTE!*\n"
            f"💰 +{PREMIO_TOKENS} tokens\n"
            f"✨ +{PREMIO_XP} XP"
        )
        if subio:
            texto += f"\n\n⭐ *¡Subiste al nivel {subio}!*"
    else:
        actualizar_tokens(user_id, -APUESTA)
        texto = (
            f"🎰 *RULETA*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Elegiste: {EMOJIS_COLORES[eleccion]} *{eleccion}*\n"
            f"🎲 Cayó en: {emoji_resultado} *{resultado}*\n\n"
            f"😢 *¡Perdiste!*\n"
            f"💰 -{APUESTA} tokens"
        )

    set_cooldown(user_id)
    datos_nuevos = obtener_datos(user_id)
    texto += f"\n\n💰 Tokens actuales: *{datos_nuevos[2]}*"
    await update.message.reply_text(texto, parse_mode="Markdown")

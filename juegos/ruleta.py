import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.logros import actualizar_stat, dar_logro, obtener_stats
from core.misiones import sumar_progreso

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
        await update.message.reply_text("🔒 Debes estar registrado y con sesión activa.\nUsa /reg nombre.pais")
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

        # Logro: Fiestero
        actualizar_stat(user_id, "ruletas_ganadas", incremento=1)
        stats = obtener_stats(user_id)
        if stats[4] >= 10:
            if dar_logro(user_id, "fiestero"):
                await avisar_logro(context, user_id, "fiestero")

        # Misiones (ruleta ganada)
        completadas = sumar_progreso(user_id, "ruleta_ganada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)

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


async def avisar_mision(context, user_id, m_id):
    from core.misiones import MISIONES
    info = MISIONES.get(m_id)
    if not info:
        return
    recompensa = f"+{info['tokens']}💰"
    if info["xp"] > 0:
        recompensa += f" +{info['xp']}⭐"
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎯 *¡MISIÓN COMPLETADA!*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✅ {info['texto']}\n"
                f"🎁 {recompensa}"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

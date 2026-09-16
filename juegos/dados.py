import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.misiones import sumar_progreso

APUESTA_MIN = 10
APUESTA_MAX = 500
COOLDOWN = 300

NUMEROS_GANADORES = [7, 11]


def init_dados_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dados_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_tirada REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_tirada FROM dados_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO dados_cooldown (user_id, ultima_tirada) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima = get_cooldown(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


async def dados(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if not context.args:
        await update.message.reply_text(
            "🎲 *DADOS*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "Uso: `/dados cantidad`\n"
            f"Mínimo: {APUESTA_MIN} · Máximo: {APUESTA_MAX}\n\n"
            "• Suma 7 u 11 → x2\n"
            "• Dobles → x3\n"
            "• Otros → pierdes x2\n"
            "Cooldown: 5 min",
            parse_mode="Markdown"
        )
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número.")
        return

    if cantidad < APUESTA_MIN or cantidad > APUESTA_MAX:
        await update.message.reply_text(f"❌ La apuesta debe estar entre {APUESTA_MIN} y {APUESTA_MAX}.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        return

    nombre, _, tokens, xp, nivel, _ = datos

    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    suma = dado1 + dado2
    es_doble = (dado1 == dado2)

    if es_doble:
        multiplicador = 3
        gano = True
        razon = "¡DOBLES!"
    elif suma in NUMEROS_GANADORES:
        multiplicador = 2
        gano = True
        razon = f"Suma {suma}"
    else:
        multiplicador = -2
        gano = False
        razon = f"Suma {suma}"

    if gano:
        ganancia = cantidad * (multiplicador - 1)
        actualizar_tokens(user_id, ganancia)
        subio = sumar_xp(user_id, 10)
        texto = (
            f"🎲 *DADOS*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎲 Dado 1: *{dado1}*\n"
            f"🎲 Dado 2: *{dado2}*\n"
            f"📊 Suma: *{suma}*\n\n"
            f"🎉 *¡GANASTE!* ({razon})\n"
            f"💰 +{ganancia} tokens\n"
            f"✨ +10 XP"
        )
        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"

        # Misiones
        completadas = sumar_progreso(user_id, "dados_ganada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)
    else:
        perdida = cantidad * 2
        actualizar_tokens(user_id, -perdida)
        sumar_xp(user_id, -10)
        texto = (
            f"🎲 *DADOS*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎲 Dado 1: *{dado1}*\n"
            f"🎲 Dado 2: *{dado2}*\n"
            f"📊 Suma: *{suma}*\n\n"
            f"😢 *¡Perdiste!* ({razon})\n"
            f"💰 -{perdida} tokens\n"
            f"✨ -10 XP"
        )

    set_cooldown(user_id)
    datos_nuevos = obtener_datos(user_id)
    texto += f"\n\n💰 Tokens: *{datos_nuevos[2]}*"
    await update.message.reply_text(texto, parse_mode="Markdown")


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

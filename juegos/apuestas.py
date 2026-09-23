import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.logros import actualizar_stat, dar_logro, obtener_stats
from core.misiones import sumar_progreso

APUESTA_MIN = 5
APUESTA_MAX = 1000
COOLDOWN = 300
EXPIRACION = 180

apuestas_pendientes = {}
siguiente_id = 1


def init_apuestas_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS apuestas_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_apuesta REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_apuesta FROM apuestas_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO apuestas_cooldown (user_id, ultima_apuesta) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima = get_cooldown(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


async def apostar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global siguiente_id

    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado y con sesión activa.")
        return

    if not context.args:
        await update.message.reply_text(
            f"🎲 *APUESTAS 1v1*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Uso: `/apostar cantidad`\n"
            f"Mínimo: {APUESTA_MIN} · Máximo: {APUESTA_MAX}\n"
            f"Premio: lo que apostó el rival\n"
            f"Expira: 3 min sin rival\n"
            f"Cooldown: 5 min",
            parse_mode="Markdown"
        )
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número entero.")
        return

    if cantidad < APUESTA_MIN or cantidad > APUESTA_MAX:
        await update.message.reply_text(f"❌ La apuesta debe estar entre {APUESTA_MIN} y {APUESTA_MAX}.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(
            f"⏳ Debes esperar *{formatear_tiempo(restante)}*.",
            parse_mode="Markdown"
        )
        return

    for ap in apuestas_pendientes.values():
        if ap["creador_id"] == user_id:
            await update.message.reply_text("⚠️ Ya tienes una apuesta pendiente. Usa `/cancelar`.", parse_mode="Markdown")
            return

    if datos[2] < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens.\nNecesitas *{cantidad}* y tienes *{datos[2]}*.",
            parse_mode="Markdown"
        )
        return

    for ap_id, ap in list(apuestas_pendientes.items()):
        if ap["creador_id"] == user_id:
            continue
        if time.time() - ap["creado"] > EXPIRACION:
            del apuestas_pendientes[ap_id]
            continue

        rival_id = ap["creador_id"]
        rival_cantidad = ap["cantidad"]
        rival_datos = obtener_datos(rival_id)

        if rival_datos is None or rival_datos[2] < rival_cantidad:
            del apuestas_pendientes[ap_id]
            continue

        ganador = random.choice([user_id, rival_id])

        if ganador == user_id:
            actualizar_tokens(user_id, rival_cantidad)
            actualizar_tokens(rival_id, -rival_cantidad)
            sumar_xp(user_id, 30)

            actualizar_stat(user_id, "apuestas_ganadas", incremento=1)
            stats = obtener_stats(user_id)
            if stats[5] >= 10:
                if dar_logro(user_id, "apostador"):
                    await avisar_logro(context, user_id, "apostador")

            completadas = sumar_progreso(user_id, "apuesta_ganada")
            for m_id in completadas:
                await avisar_mision(context, user_id, m_id)

            texto = (
                f"🎲 *APUESTA RESUELTA*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🥇 Ganador: *{datos[0]}*\n"
                f"🥈 Perdedor: *{rival_datos[0]}*\n\n"
                f"💰 *{datos[0]}* ganó *{rival_cantidad}* tokens\n"
                f"✨ +30 XP\n"
                f"💸 *{rival_datos[0]}* perdió *{rival_cantidad}* tokens"
            )
        else:
            actualizar_tokens(rival_id, cantidad)
            actualizar_tokens(user_id, -cantidad)
            sumar_xp(rival_id, 30)

            actualizar_stat(rival_id, "apuestas_ganadas", incremento=1)
            stats = obtener_stats(rival_id)
            if stats[5] >= 10:
                if dar_logro(rival_id, "apostador"):
                    await avisar_logro(context, rival_id, "apostador")

            completadas = sumar_progreso(rival_id, "apuesta_ganada")
            for m_id in completadas:
                await avisar_mision(context, rival_id, m_id)

            texto = (
                f"🎲 *APUESTA RESUELTA*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🥇 Ganador: *{rival_datos[0]}*\n"
                f"🥈 Perdedor: *{datos[0]}*\n\n"
                f"💰 *{rival_datos[0]}* ganó *{cantidad}* tokens\n"
                f"✨ +30 XP\n"
                f"💸 *{datos[0]}* perdió *{cantidad}* tokens"
            )

        set_cooldown(user_id)
        set_cooldown(rival_id)
        del apuestas_pendientes[ap_id]

        try:
            await context.bot.send_message(chat_id=user_id, text=texto, parse_mode="Markdown")
        except Exception:
            pass
        try:
            await context.bot.send_message(chat_id=rival_id, text=texto, parse_mode="Markdown")
        except Exception:
            pass
        return

    apuestas_pendientes[siguiente_id] = {
        "creador_id": user_id,
        "creador_nombre": datos[0],
        "cantidad": cantidad,
        "creado": time.time()
    }

    await update.message.reply_text(
        f"🎲 *Apuesta creada*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Apostador: *{datos[0]}*\n"
        f"💰 Cantidad: *{cantidad}* tokens\n\n"
        f"⏳ Esperando rival... (expira en 3 min)\n"
        f"Para cancelar: `/cancelar`",
        parse_mode="Markdown"
    )
    siguiente_id += 1


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    for ap_id, ap in list(apuestas_pendientes.items()):
        if ap["creador_id"] == user_id:
            del apuestas_pendientes[ap_id]
            set_cooldown(user_id)
            await update.message.reply_text(
                "✅ Apuesta cancelada.\nTus tokens no fueron descontados.\n⏳ Cooldown: 5 min."
            )
            return

    await update.message.reply_text("❌ No tienes ninguna apuesta pendiente.")


async def revisar_expiradas(context) -> None:
    ahora = time.time()
    for ap_id, ap in list(apuestas_pendientes.items()):
        if ahora - ap["creado"] > EXPIRACION:
            del apuestas_pendientes[ap_id]
            try:
                await context.bot.send_message(
                    chat_id=ap["creador_id"],
                    text=(
                        f"⌛ *Apuesta expirada*\n"
                        f"👤 *{ap['creador_nombre']}* no encontró rival.\n"
                        f"💰 Tokens devueltos: *{ap['cantidad']}*\n"
                        f"✅ Sin cooldown. Puedes volver a apostar."
                    ),
                    parse_mode="Markdown"
                )
            except Exception:
                pass


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

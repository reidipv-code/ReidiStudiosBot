import sqlite3
import random
import time
import re
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, resetear_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.logros import dar_logro
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens

FRUTAS = ["🍎", "🍌", "🍇", "🍓", "🍊", "🍒", "🥝", "🍍", "🍑", "🍐",
          "🍋", "🍉", "🥭", "🫐", "🍈", "🥥", "🍅", "🥑", "🍆", "🌰"]

COOLDOWN_PERDIDA = 420
COOLDOWN_VICTORIA = 600

partidas_memoria = {}

EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E0-\U0001F1FF]"
)


def init_memoria_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memoria_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_partida FROM memoria_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO memoria_cooldown (user_id, ultima_partida) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima = get_cooldown(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN_VICTORIA - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


def tiempo_memoria(ronda):
    if ronda <= 3:
        return 10
    elif ronda <= 7:
        return 25
    elif ronda <= 14:
        return 40
    else:
        return 55


def emojis_por_ronda(ronda):
    return ronda * 2


def extraer_emojis(texto):
    return EMOJI_PATTERN.findall(texto)


async def memoria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_memoria:
        await update.message.reply_text("⚠️ Ya tienes una partida de memoria en curso.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        return

    partidas_memoria[user_id] = {
        "ronda": 1,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "emojis": [],
        "hora_inicio": time.time(),
        "message_id": None
    }
    iniciar_partida(user_id, "memoria")

    await update.message.reply_text(
        "🧠 *MEMORIA*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "Memoriza los emojis y escríbelos en el mismo orden.\n"
        "Responde con `.` seguido de los emojis.\n\n"
        "Ejemplo: `.🍎 🍌 🍇`\n"
        "También funciona pegado: `.🍎🍌🍇`\n\n"
        "⚠️ Si fallas, pierdes toda la XP de tu barra.\n\n"
        "¡Ronda 1!",
        parse_mode="Markdown"
    )
    await mostrar_secuencia(context, user_id)


async def mostrar_secuencia(context, user_id):
    partida = partidas_memoria[user_id]
    ronda = partida["ronda"]
    cantidad = emojis_por_ronda(ronda)

    emojis = [random.choice(FRUTAS) for _ in range(cantidad)]
    partida["emojis"] = emojis
    partida["hora_inicio"] = time.time()
    partida["tiempo_limite"] = tiempo_memoria(ronda) + 20

    linea = " ".join(emojis)
    tiempo = tiempo_memoria(ronda)

    mensaje = await context.bot.send_message(
        chat_id=partida["chat_id"],
        text=(
            f"🧠 *Ronda {ronda}/50*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📋 *Memoriza estos {cantidad} emojis:*\n\n"
            f"{linea}\n\n"
            f"⏱️ Tienes *{tiempo} segundos*.\n"
            f"Responde: `.🍎 🍌 🍇`"
        ),
        parse_mode="Markdown"
    )

    partida["message_id"] = mensaje.message_id

    context.job_queue.run_once(
        borrar_secuencia,
        when=tiempo,
        data={
            "chat_id": partida["chat_id"],
            "message_id": mensaje.message_id,
            "user_id": user_id
        }
    )


async def borrar_secuencia(context) -> None:
    data = context.job.data
    chat_id = data["chat_id"]
    message_id = data["message_id"]

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏱️ *¡Tiempo!*\nEscribe los emojis en el mismo orden con `.`",
            parse_mode="Markdown"
        )
    except Exception:
        pass


async def responder_memoria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in partidas_memoria:
        return

    partida = partidas_memoria[user_id]
    texto = update.message.text.strip()

    if not texto.startswith("."):
        return

    respuesta = texto[1:].strip()

    emojis_usuario = extraer_emojis(respuesta)
    emojis_correctos = partida["emojis"]

    if len(emojis_usuario) != len(emojis_correctos):
        await update.message.reply_text(
            f"❌ Escribiste *{len(emojis_usuario)}* emojis pero eran *{len(emojis_correctos)}*.",
            parse_mode="Markdown"
        )
        raise ApplicationHandlerStop

    aciertos = sum(1 for i, e in enumerate(emojis_usuario) if e == emojis_correctos[i])

    if aciertos == len(emojis_correctos):
        partida["aciertos"] += 1
        actualizar_tokens(user_id, cantidad_con_bonus_tokens(user_id, 2, "memoria"))
        aplicar_bonus_xp(user_id, 2, "memoria")

        if partida["ronda"] >= 20:
            if dar_logro(user_id, "memorion"):
                await avisar_logro(context, user_id, "memorion")

        # Misiones (memoria ronda)
        completadas = sumar_progreso(user_id, "memoria_ronda", cantidad=partida["ronda"])
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)

        if partida["ronda"] >= 50:
            await terminar_memoria(context, user_id, gano=True)
            raise ApplicationHandlerStop

        partida["ronda"] += 1
        await update.message.reply_text(
            f"✅ *¡Correcto!*\n💰 +2 tokens, ✨ +2 XP\n\n🎯 Ronda *{partida['ronda']}*...",
            parse_mode="Markdown"
        )
        await mostrar_secuencia(context, user_id)
        raise ApplicationHandlerStop
    else:
        resetear_xp(user_id)
        await update.message.reply_text(
            f"❌ *¡Incorrecto!*\nAcertaste *{aciertos}/{len(emojis_correctos)}*\n\n"
            f"💔 Has perdido *TODA* la XP de tu barra.\n📊 XP reseteada a 0.",
            parse_mode="Markdown"
        )
        await terminar_memoria(context, user_id, gano=False)
        raise ApplicationHandlerStop


async def terminar_memoria(context, user_id, gano):
    partida = partidas_memoria.pop(user_id, None)
    if partida is None:
        return
    set_cooldown(user_id)
    terminar_partida(user_id)

    if gano:
        texto = (
            f"🏆 *¡COMPLETASTE LA MEMORIA!*\n"
            f"✅ Llegaste a la ronda *50*\n"
            f"🏅 Rondas ganadas: *{partida['aciertos']}*\n\n"
            f"⏳ Cooldown: 10 min"
        )
    else:
        texto = (
            f"😢 *PARTIDA TERMINADA*\n"
            f"📊 Llegaste a la ronda *{partida['ronda']}*\n"
            f"🏅 Rondas ganadas: *{partida['aciertos']}*\n\n"
            f"⏳ Cooldown: 7 min"
        )

    try:
        await context.bot.send_message(chat_id=partida["chat_id"], text=texto, parse_mode="Markdown")
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


async def revisar_timeouts_memoria(context) -> None:
    ahora = time.time()
    for user_id, partida in list(partidas_memoria.items()):
        if ahora - partida["hora_inicio"] > partida["tiempo_limite"]:
            try:
                await context.bot.send_message(chat_id=partida["chat_id"], text="⏰ ¡Se acabó el tiempo!")
            except Exception:
                pass
            await terminar_memoria(context, user_id, gano=False)

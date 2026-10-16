import sqlite3
import random
import time

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens

COOLDOWN_PERDIDA = 195
COOLDOWN_VICTORIA = 240
TIEMPO = 40
PALABRAS_POR_PARTIDA = 5

PALABRAS = [
    "bola", "casa", "perro", "gato", "mesa", "silla", "libro", "agua",
    "fuego", "tierra", "aire", "cielo", "luna", "sol", "estrella", "nube",
    "playa", "monte", "rio", "mar", "pez", "pajaro", "leon", "tigre",
    "caballo", "vaca", "oveja", "cerdo", "gallina", "pato", "raton", "oso",
    "manzana", "platano", "naranja", "uva", "fresa", "limon", "pera", "melon",
    "coche", "moto", "avion", "barco", "tren", "bici", "camion", "taxi",
    "rojo", "azul", "verde", "amarillo", "negro", "blanco", "morado", "rosa",
    "escuela", "hospital", "parque", "tienda"
]

partidas_palabras = {}


def init_palabras_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS palabras_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT ultima_partida FROM palabras_cooldown WHERE user_id = ?",
        (user_id,)
    )
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO palabras_cooldown "
        "(user_id, ultima_partida) VALUES (?, ?)",
        (user_id, time.time())
    )
    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima = get_cooldown(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN_VICTORIA - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


def normalizar(texto):
    texto = texto.lower().strip()
    for k, v in {
        "á": "a", "é": "e", "í": "i",
        "ó": "o", "ú": "u", "ñ": "n"
    }.items():
        texto = texto.replace(k, v)
    return texto


def mezclar(palabra):
    letras = list(palabra.upper())
    random.shuffle(letras)

    intentos = 0
    while "".join(letras).lower() == palabra.lower() and intentos < 10:
        random.shuffle(letras)
        intentos += 1

    return " ".join(letras)


def cancelar_temporizador(context, user_id):
    """Cancela el temporizador anterior de este usuario."""
    if context.job_queue is None:
        return

    for job in context.job_queue.get_jobs_by_name(
        f"palabras_timeout_{user_id}"
    ):
        job.schedule_removal()


def programar_temporizador(context, user_id):
    """Programa el vencimiento exacto de la palabra actual."""
    if context.job_queue is None:
        return

    cancelar_temporizador(context, user_id)

    partida = partidas_palabras.get(user_id)
    if partida is None:
        return

    context.job_queue.run_once(
        timeout_palabras,
        when=max(0, partida["deadline"] - time.monotonic()),
        data=user_id,
        name=f"palabras_timeout_{user_id}"
    )


async def timeout_palabras(context: ContextTypes.DEFAULT_TYPE):
    """Finaliza la partida al vencer el plazo de la palabra."""
    job = context.job
    user_id = job.data if job else None

    if user_id is None:
        return

    partida = partidas_palabras.get(user_id)
    if partida is None:
        return

    restante = partida["deadline"] - time.monotonic()

    # Evita terminar antes del límite por pequeñas variaciones del scheduler.
    if restante > 0:
        programar_temporizador(context, user_id)
        return

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text="⏰ ¡Se acabó el tiempo!"
        )
    except Exception:
        pass

    await terminar_palabras(context, user_id, gano=False)


async def palabras(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_palabras:
        await update.message.reply_text(
            "⚠️ Ya tienes una partida en curso."
        )
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(
            f"⏳ Espera *{formatear_tiempo(restante)}*.",
            parse_mode="Markdown"
        )
        return

    seleccionadas = random.sample(PALABRAS, PALABRAS_POR_PARTIDA)

    partidas_palabras[user_id] = {
        "palabras": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "deadline": None
    }

    iniciar_partida(user_id, "palabras")

    await update.message.reply_text(
        "🔤 *PALABRAS DESORDENADAS*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "Forma la palabra correcta con las letras.\n"
        "Responde con `.palabra`\n\n"
        "Ejemplo: `B O L A` → `.bola`\n\n"
        f"⏱️ {TIEMPO}s por palabra. 5 palabras.\n"
        "Premio: 50 tokens + 50 XP",
        parse_mode="Markdown"
    )

    await enviar_palabra(context, user_id)


async def enviar_palabra(context, user_id):
    partida = partidas_palabras.get(user_id)
    if partida is None:
        return

    idx = partida["indice"]
    if idx >= PALABRAS_POR_PARTIDA:
        return

    palabra = partida["palabras"][idx]
    mezclada = mezclar(palabra)

    # No iniciar el reloj antes de enviar el mensaje.
    partida["deadline"] = None

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text=(
                f"🔤 *Palabra {idx + 1}/{PALABRAS_POR_PARTIDA}*\n"
                f"`{mezclada}`\n\n"
                f"⏱️ {TIEMPO}s. Responde `.palabra`"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        await terminar_palabras(context, user_id, gano=False)
        return

    # El tiempo empieza después de enviar correctamente la pregunta.
    partida_actual = partidas_palabras.get(user_id)
    if partida_actual is None:
        return

    partida_actual["deadline"] = time.monotonic() + TIEMPO
    programar_temporizador(context, user_id)


async def responder_palabras(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    partida = partidas_palabras.get(user_id)

    if partida is None:
        return

    texto = update.message.text
    if not texto:
        return

    texto = texto.strip()
    if not texto.startswith("."):
        return

    deadline = partida.get("deadline")

    # Una respuesta que llega después del plazo no cuenta.
    if deadline is None or time.monotonic() >= deadline:
        try:
            await update.message.reply_text("⏰ ¡Se acabó el tiempo!")
        except Exception:
            pass

        await terminar_palabras(context, user_id, gano=False)
        raise ApplicationHandlerStop

    respuesta = texto[1:].strip()
    correcta = partida["palabras"][partida["indice"]]

    if normalizar(respuesta) == normalizar(correcta):
        partida["aciertos"] += 1

        await update.message.reply_text(
            f"✅ ¡Correcto! Era *{correcta}*.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ Era *{correcta}*.",
            parse_mode="Markdown"
        )
        await terminar_palabras(context, user_id, gano=False)
        raise ApplicationHandlerStop

    cancelar_temporizador(context, user_id)

    # Invalidar el plazo anterior antes de pasar a la próxima palabra.
    partida["deadline"] = None
    partida["indice"] += 1

    if partida["indice"] >= PALABRAS_POR_PARTIDA:
        await terminar_palabras(context, user_id, gano=True)
    else:
        await enviar_palabra(context, user_id)

    raise ApplicationHandlerStop


async def terminar_palabras(context, user_id, gano):
    partida = partidas_palabras.pop(user_id, None)
    if partida is None:
        return

    cancelar_temporizador(context, user_id)
    set_cooldown(user_id)
    terminar_partida(user_id)

    if gano:
        actualizar_tokens(
            user_id,
            cantidad_con_bonus_tokens(user_id, 50, "palabras")
        )
        subio = aplicar_bonus_xp(user_id, 50, "palabras")

        texto = (
            "🎉 *¡PALABRAS COMPLETADAS!*\n"
            "✅ 5/5\n"
            "💰 +50 tokens\n"
            "✨ +50 XP"
        )

        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"

        texto += "\n⏳ Cooldown: 10 min"

        completadas = sumar_progreso(user_id, "palabras_completada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)

    else:
        texto = (
            "😢 *FALLIDO*\n"
            f"✅ Aciertos: {partida['aciertos']}/5\n"
            "⏳ Cooldown: 7 min"
        )

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text=texto,
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
                "🎯 *¡MISIÓN COMPLETADA!*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"✅ {info['texto']}\n"
                f"🎁 {recompensa}"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass


async def revisar_timeouts_palabras(
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Compatibilidad con el trabajo periódico ya configurado en bot_railway.py.
    El temporizador individual se encarga del vencimiento preciso.
    """
    ahora = time.monotonic()

    for user_id, partida in list(partidas_palabras.items()):
        deadline = partida.get("deadline")

        if deadline is not None and ahora >= deadline:
            try:
                await context.bot.send_message(
                    chat_id=partida["chat_id"],
                    text="⏰ ¡Se acabó el tiempo!"
                )
            except Exception:
                pass

            await terminar_palabras(context, user_id, gano=False)
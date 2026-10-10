import random
import re
import sqlite3
import time

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import (
    DB_PATH,
    obtener_datos,
    actualizar_tokens,
    resetear_xp,
)
from core.sesiones import iniciar_partida, terminar_partida
from core.logros import actualizar_stat, dar_logro
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens


# ============================================================
# CONFIGURACIÓN
# ============================================================

COOLDOWN_PERDIDA = 195
COOLDOWN_VICTORIA = 240

MAX_RONDAS = 50

FRUTAS = [
    "🍎", "🍐", "🍊", "🍋", "🍌",
    "🍉", "🍇", "🍓", "🫐", "🍒",
    "🍑", "🥭", "🍍", "🥝", "🍅",
    "🥥", "🥑", "🍆", "🥕", "🌽",
    "🍄", "🥔", "🧅", "🥦", "🥒",
]

# Cada jugador puede tener una partida activa.
partidas_memoria = {}


# ============================================================
# BASE DE DATOS
# ============================================================

def init_memoria_db():
    """Inicializa la tabla de enfriamiento del juego."""

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memoria_cooldown (
                user_id INTEGER PRIMARY KEY,
                ultima_partida REAL NOT NULL
            )
        """)

        conn.commit()
    finally:
        conn.close()


def get_cooldown(user_id):
    """Obtiene la hora de la última partida."""

    conn = sqlite3.connect(DB_PATH)

    try:
        resultado = conn.execute(
            """
            SELECT ultima_partida
            FROM memoria_cooldown
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        return resultado[0] if resultado else 0

    finally:
        conn.close()


def set_cooldown(user_id):
    """Actualiza el enfriamiento al terminar una partida."""

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO memoria_cooldown
            (user_id, ultima_partida)
            VALUES (?, ?)
            """,
            (user_id, time.time()),
        )

        conn.commit()

    finally:
        conn.close()


def tiempo_restante(user_id, gano=False):
    """Calcula el tiempo restante para volver a jugar."""

    ultima = get_cooldown(user_id)

    if not ultima:
        return 0

    cooldown = COOLDOWN_VICTORIA if gano else COOLDOWN_PERDIDA

    transcurrido = time.time() - ultima

    return max(0, int(cooldown - transcurrido))


def formatear_tiempo(segundos):
    """Convierte segundos en un texto legible."""

    segundos = max(0, int(segundos))

    minutos, segundos = divmod(segundos, 60)

    if minutos:
        return f"{minutos}m {segundos}s"

    return f"{segundos}s"


# ============================================================
# DIFICULTAD Y SECUENCIAS
# ============================================================

def emojis_por_ronda(ronda):
    """
    Aumenta progresivamente la cantidad de emojis.

    Las primeras rondas son sencillas y la dificultad aumenta
    conforme avanza la partida.
    """

    return min(3 + ((ronda - 1) // 2), 27)


def tiempo_memoria(ronda):
    """
    Tiempo para responder en cada ronda.

    El límite disminuye gradualmente para aumentar la dificultad,
    sin bajar nunca de 10 segundos.
    """

    return max(10, 25 - ((ronda - 1) // 5))


def extraer_emojis(texto):
    """
    Extrae emojis de una respuesta sin depender de espacios
    entre ellos.

    Admite emojis compuestos y selectores de variación.
    """

    patron = (
        r"[\U0001F1E6-\U0001F1FF]{2}"
        r"|[\U0001F300-\U0001FAFF]"
        r"(?:\uFE0F|\uFE0E)?"
        r"(?:\u200D[\U0001F300-\U0001FAFF]"
        r"(?:\uFE0F|\uFE0E)?)*"
        r"|[\u2600-\u27BF](?:\uFE0F|\uFE0E)?"
    )

    return re.findall(patron, texto)


# ============================================================
# TEMPORIZADORES
# ============================================================

def cancelar_timer_memoria(context, user_id):
    """Cancela los temporizadores asociados a un jugador."""

    if context.job_queue is None:
        return

    for job in context.job_queue.get_jobs_by_name(
        f"memoria_{user_id}"
    ):
        job.schedule_removal()


def programar_timer_memoria(context, user_id):
    """
    Programa un temporizador usando el deadline real de la ronda.

    Si el proceso tarda en ejecutar el trabajo, no reinicia
    los segundos del jugador.
    """

    if context.job_queue is None:
        return

    partida = partidas_memoria.get(user_id)

    if not partida:
        return

    deadline = partida.get("deadline")

    if deadline is None:
        return

    cancelar_timer_memoria(context, user_id)

    restante = max(0, deadline - time.monotonic())

    context.job_queue.run_once(
        timeout_memoria,
        when=restante,
        data={
            "user_id": user_id,
            "ronda": partida["ronda"],
            "deadline": deadline,
        },
        name=f"memoria_{user_id}",
    )


async def timeout_memoria(context):
    """Gestiona el vencimiento del temporizador."""

    if not context.job:
        return

    data = context.job.data or {}

    user_id = data.get("user_id")

    if user_id is None:
        return

    partida = partidas_memoria.get(user_id)

    if not partida:
        return

    # Evita que un temporizador antiguo cierre una ronda nueva.
    if partida["ronda"] != data.get("ronda"):
        return

    if partida.get("deadline") != data.get("deadline"):
        return

    deadline = partida.get("deadline")

    if deadline is None:
        return

    restante = deadline - time.monotonic()

    # Si el trabajo se ejecutó antes de tiempo, se vuelve
    # a programar utilizando el mismo deadline.
    if restante > 0:
        programar_timer_memoria(context, user_id)
        return

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text="⏰ ¡Se acabó el tiempo!",
        )
    except Exception:
        pass

    await terminar_memoria(
        context,
        user_id,
        gano=False,
    )


async def revisar_timeouts_memoria(context):
    """
    Comprobación adicional de seguridad.

    bot_railway.py ya puede ejecutar esta función periódicamente.
    """

    ahora = time.monotonic()

    for user_id, partida in list(partidas_memoria.items()):
        deadline = partida.get("deadline")

        if deadline is None:
            continue

        if ahora >= deadline:
            await timeout_memoria_manual(
                context,
                user_id,
            )


async def timeout_memoria_manual(context, user_id):
    """Cierra una partida cuyo tiempo haya expirado."""

    partida = partidas_memoria.get(user_id)

    if not partida:
        return

    deadline = partida.get("deadline")

    if deadline is None:
        return

    if time.monotonic() < deadline:
        return

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text="⏰ ¡Se acabó el tiempo!",
        )
    except Exception:
        pass

    await terminar_memoria(
        context,
        user_id,
        gano=False,
    )


# ============================================================
# COMANDO /MEMORIA
# ============================================================

async def memoria(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Inicia el juego de memoria."""

    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    datos = obtener_datos(user_id)

    if datos is None or datos[5] != 1:
        await update.message.reply_text(
            "🔒 Debes estar registrado."
        )
        return

    if user_id in partidas_memoria:
        await update.message.reply_text(
            "⚠️ Ya tienes una partida de memoria en curso."
        )
        return

    restante = tiempo_restante(user_id)

    if restante > 0:
        await update.message.reply_text(
            "⏳ Debes esperar "
            f"{formatear_tiempo(restante)} "
            "para volver a jugar."
        )
        return

    if context.job_queue is None:
        await update.message.reply_text(
            "⚠️ El temporizador del juego no está disponible. "
            "Inténtalo más tarde."
        )
        return

    partidas_memoria[user_id] = {
        "ronda": 1,
        "aciertos": 0,
        "emojis": [],
        "chat_id": update.effective_chat.id,
        "deadline": None,
        "tiempo_limite": 0,
        "message_id": None,
        "finalizada": False,
    }

    try:
        iniciar_partida(user_id, "memoria")

        await update.message.reply_text(
            "🧠 *JUEGO DE MEMORIA*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "Memoriza la secuencia de emojis y repítela "
            "en el mismo orden.\n\n"
            "📌 *Cómo jugar:*\n"
            "• Observa la secuencia.\n"
            "• Responde con un punto seguido de los emojis.\n"
            "• Debes acertar todos y mantener el orden.\n"
            "• Si fallas, pierdes toda la XP de tu barra.\n"
            "• Cada ronda aumenta la dificultad.\n\n"
            "💰 Recompensa por ronda: 2 tokens.\n"
            "✨ Recompensa por ronda: 2 XP.\n\n"
            "🏆 Objetivo: completar 50 rondas.\n\n"
            "Ejemplo de respuesta:\n"
            "`.🍎🍌🍇`",
            parse_mode="Markdown",
        )

        await mostrar_secuencia(
            context,
            user_id,
        )

    except Exception:
        await terminar_memoria(
            context,
            user_id,
            gano=False,
            anunciar=False,
        )
        raise


# ============================================================
# MOSTRAR SECUENCIA
# ============================================================

async def mostrar_secuencia(context, user_id):
    """Genera y muestra los emojis de la ronda actual."""

    partida = partidas_memoria.get(user_id)

    if not partida:
        return

    ronda = partida["ronda"]

    cantidad = emojis_por_ronda(ronda)

    emojis = [
        random.choice(FRUTAS)
        for _ in range(cantidad)
    ]

    partida["emojis"] = emojis

    # Durante el envío de la secuencia no se acepta respuesta.
    partida["deadline"] = None

    partida["tiempo_limite"] = tiempo_memoria(ronda)

    texto = (
        f"🧠 *Ronda {ronda}/{MAX_RONDAS}*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Memoriza estos {cantidad} emojis:*\n\n"
        f"{' '.join(emojis)}\n\n"
        f"⏱️ Tienes *{partida['tiempo_limite']} segundos*.\n"
        "Responde escribiendo un punto seguido de la secuencia.\n\n"
        "Ejemplo: `.🍎🍌🍇`"
    )

    try:
        mensaje = await context.bot.send_message(
            chat_id=partida["chat_id"],
            text=texto,
            parse_mode="Markdown",
        )

    except Exception:
        await terminar_memoria(
            context,
            user_id,
            gano=False,
            anunciar=False,
        )
        return

    # La partida pudo cancelarse mientras se enviaba el mensaje.
    partida_actual = partidas_memoria.get(user_id)

    if partida_actual is not partida:
        return

    partida["message_id"] = mensaje.message_id

    # Se inicia el tiempo después de enviar la secuencia.
    partida["deadline"] = (
        time.monotonic() + partida["tiempo_limite"]
    )

    programar_timer_memoria(
        context,
        user_id,
    )


# ============================================================
# ELIMINAR SECUENCIA ANTIGUA
# ============================================================

async def borrar_secuencia(context):
    """Compatibilidad con trabajos antiguos de eliminación."""

    if not context.job:
        return

    data = context.job.data or {}

    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    if chat_id is None or message_id is None:
        return

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except Exception:
        pass


# ============================================================
# RESPONDER
# ============================================================

async def responder_memoria(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Comprueba la respuesta del jugador."""

    if (
        not update.effective_user
        or not update.message
        or not update.message.text
    ):
        return

    user_id = update.effective_user.id

    partida = partidas_memoria.get(user_id)

    if not partida:
        return

    texto = update.message.text.strip()

    if not texto.startswith("."):
        return

    # Ignora mensajes mientras se prepara la siguiente ronda.
    deadline = partida.get("deadline")

    if deadline is None:
        return

    # Comprueba el tiempo antes de procesar la respuesta.
    if time.monotonic() >= deadline:
        await update.message.reply_text(
            "⏰ ¡Se acabó el tiempo!"
        )

        await terminar_memoria(
            context,
            user_id,
            gano=False,
        )

        raise ApplicationHandlerStop

    respuesta = texto[1:].strip()

    emojis_usuario = extraer_emojis(respuesta)

    emojis_correctos = partida["emojis"]

    if len(emojis_usuario) != len(emojis_correctos):
        await update.message.reply_text(
            f"❌ Escribiste {len(emojis_usuario)} emojis, "
            f"pero necesitabas {len(emojis_correctos)}.\n"
            "Inténtalo de nuevo antes de que termine el tiempo."
        )

        raise ApplicationHandlerStop

    aciertos = sum(
        1
        for i, emoji in enumerate(emojis_usuario)
        if emoji == emojis_correctos[i]
    )

    if aciertos != len(emojis_correctos):
        resetear_xp(user_id)

        await update.message.reply_text(
            f"❌ ¡Incorrecto! Acertaste "
            f"{aciertos}/{len(emojis_correctos)}.\n"
            "💔 Has perdido toda la XP de tu barra."
        )

        await terminar_memoria(
            context,
            user_id,
            gano=False,
        )

        raise ApplicationHandlerStop

    # Comprobación adicional para evitar procesar dos respuestas
    # válidas en la misma ronda.
    if user_id not in partidas_memoria:
        raise ApplicationHandlerStop

    cancelar_timer_memoria(
        context,
        user_id,
    )

    partida["deadline"] = None

    partida["aciertos"] += 1

    # --------------------------------------------------------
    # RECOMPENSAS
    # --------------------------------------------------------

    actualizar_tokens(
        user_id,
        cantidad_con_bonus_tokens(
            user_id,
            2,
            "memoria",
        ),
    )

    aplicar_bonus_xp(
        user_id,
        2,
        "memoria",
    )

    # --------------------------------------------------------
    # LOGRO
    # --------------------------------------------------------

    if partida["ronda"] >= 20:
        if dar_logro(user_id, "memorion"):
            await avisar_logro(
                context,
                user_id,
                "memorion",
            )

    # --------------------------------------------------------
    # MISIONES
    # --------------------------------------------------------

    for m_id in sumar_progreso(
        user_id,
        "memoria_ronda",
        cantidad=partida["ronda"],
    ):
        await avisar_mision(
            context,
            user_id,
            m_id,
        )

    # --------------------------------------------------------
    # FINAL DE PARTIDA
    # --------------------------------------------------------

    if partida["ronda"] >= MAX_RONDAS:
        await terminar_memoria(
            context,
            user_id,
            gano=True,
        )

        raise ApplicationHandlerStop

    # --------------------------------------------------------
    # SIGUIENTE RONDA
    # --------------------------------------------------------

    partida["ronda"] += 1

    await update.message.reply_text(
        "✅ ¡Correcto!\n"
        "💰 +2 tokens base\n"
        "✨ +2 XP base\n"
        f"🎯 Próxima ronda: {partida['ronda']}/{MAX_RONDAS}"
    )

    await mostrar_secuencia(
        context,
        user_id,
    )

    raise ApplicationHandlerStop


# ============================================================
# TERMINAR PARTIDA
# ============================================================

async def terminar_memoria(
    context,
    user_id,
    gano,
    anunciar=True,
):
    """
    Finaliza la partida una sola vez.

    Cancela los temporizadores, elimina la sesión y aplica
    el cooldown correspondiente.
    """

    partida = partidas_memoria.pop(
        user_id,
        None,
    )

    if partida is None:
        return

    if partida.get("finalizada"):
        return

    partida["finalizada"] = True

    cancelar_timer_memoria(
        context,
        user_id,
    )

    try:
        terminar_partida(user_id)
    except Exception:
        pass

    try:
        set_cooldown(user_id)
    except Exception:
        pass

    # Estadísticas generales.
    try:
        actualizar_stat(
            user_id,
            "partidas_jugadas",
            incremento=1,
        )
    except Exception:
        pass

    # Misión: jugar una partida.
    try:
        completadas = sumar_progreso(
            user_id,
            "partida_jugada",
        )

        for m_id in completadas:
            await avisar_mision(
                context,
                user_id,
                m_id,
            )

    except Exception:
        pass

    if gano:
        texto = (
            "🏆 *¡MEMORIA COMPLETADA!*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 Rondas completadas: {MAX_RONDAS}/{MAX_RONDAS}\n"
            f"✅ Aciertos: {partida['aciertos']}\n\n"
            "🎉 ¡Has superado todas las rondas!\n"
            "⏳ Podrás volver a jugar cuando termine "
            f"el cooldown de {formatear_tiempo(COOLDOWN_VICTORIA)}."
        )

        try:
            actualizar_stat(
                user_id,
                "memoria_ganadas",
                incremento=1,
            )
        except Exception:
            pass

    else:
        texto = (
            "💔 *PARTIDA DE MEMORIA TERMINADA*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Ronda alcanzada: {partida['ronda']}/{MAX_RONDAS}\n"
            f"✅ Rondas superadas: {partida['aciertos']}\n\n"
            "Puedes intentarlo de nuevo cuando termine "
            f"el cooldown de {formatear_tiempo(COOLDOWN_PERDIDA)}."
        )

    if anunciar:
        try:
            await context.bot.send_message(
                chat_id=partida["chat_id"],
                text=texto,
                parse_mode="Markdown",
            )
        except Exception:
            pass


# ============================================================
# NOTIFICACIONES
# ============================================================

async def avisar_logro(context, user_id, clave):
    """Notifica un logro desbloqueado."""

    from core.logros import LOGROS

    info = LOGROS.get(clave)

    if not info:
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🏆 *¡LOGRO DESBLOQUEADO!*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"{info['emoji']} *{info['nombre']}*\n"
                f"_{info['descripcion']}_"
            ),
            parse_mode="Markdown",
        )

    except Exception:
        pass


async def avisar_mision(context, user_id, m_id):
    """Notifica una misión completada."""

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
            parse_mode="Markdown",
        )

    except Exception:
        pass
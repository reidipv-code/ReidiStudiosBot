import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.misiones import sumar_progreso

COOLDOWN_PERDIDA = 420
COOLDOWN_VICTORIA = 600
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
    c.execute("SELECT ultima_partida FROM palabras_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO palabras_cooldown (user_id, ultima_partida) VALUES (?, ?)", (user_id, time.time()))
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
    for k, v in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}.items():
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


async def palabras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_palabras:
        await update.message.reply_text("⚠️ Ya tienes una partida en curso.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        return

    seleccionadas = random.sample(PALABRAS, PALABRAS_POR_PARTIDA)

    partidas_palabras[user_id] = {
        "palabras": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time()
    }
    try:
        iniciar_partida(user_id, "palabras")
    except Exception:
        partidas_palabras.pop(user_id, None)
        raise

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
    partida = partidas_palabras[user_id]
    idx = partida["indice"]
    if idx >= PALABRAS_POR_PARTIDA:
        return
    palabra = partida["palabras"][idx]
    mezclada = mezclar(palabra)
    partida["hora_inicio"] = time.time()
    await context.bot.send_message(
        chat_id=partida["chat_id"],
        text=(
            f"🔤 *Palabra {idx + 1}/{PALABRAS_POR_PARTIDA}*\n"
            f"`{mezclada}`\n\n"
            f"⏱️ {TIEMPO}s. Responde `.palabra`"
        ),
        parse_mode="Markdown"
    )


async def responder_palabras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in partidas_palabras:
        return

    partida = partidas_palabras[user_id]
    texto = update.message.text.strip()
    if not texto.startswith("."):
        return

    respuesta = texto[1:].strip()
    correcta = partida["palabras"][partida["indice"]]

    if normalizar(respuesta) == normalizar(correcta):
        partida["aciertos"] += 1
        await update.message.reply_text(f"✅ ¡Correcto! Era *{correcta}*.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Era *{correcta}*.", parse_mode="Markdown")
        await terminar_palabras(context, user_id, gano=False)
        raise ApplicationHandlerStop

    partida["indice"] += 1
    if partida["indice"] >= PALABRAS_POR_PARTIDA:
        await terminar_palabras(context, user_id, gano=True)
    else:
        await enviar_palabra(context, user_id)
    raise ApplicationHandlerStop


async def terminar_palabras(context, user_id, gano):
    # IMPORTANTE: sacar la partida de memoria PRIMERO.
    # Así, aunque falle una misión, logro, estadística, recompensa o mensaje,
    # el usuario nunca queda atrapado en la partida.
    partida = partidas_palabras.pop(user_id, None)
    if partida is None:
        try:
            terminar_partida(user_id)
        except Exception:
            pass
        return

    try:
        terminar_partida(user_id)
    except Exception:
        pass
    set_cooldown(user_id)

    if gano:
        actualizar_tokens(user_id, 50)
        subio = sumar_xp(user_id, 50)
        texto = f"🎉 *¡PALABRAS COMPLETADAS!*\n✅ 5/5\n💰 +50 tokens\n✨ +50 XP"
        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"
        texto += "\n⏳ Cooldown: 10 min"

        # Misiones
        completadas = sumar_progreso(user_id, "palabras_completada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)
    else:
        texto = f"😢 *FALLIDO*\n✅ Aciertos: {partida['aciertos']}/5\n⏳ Cooldown: 7 min"

    try:
        await context.bot.send_message(chat_id=partida["chat_id"], text=texto, parse_mode="Markdown")
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


async def revisar_timeouts_palabras(context) -> None:
    ahora = time.time()
    for user_id, partida in list(partidas_palabras.items()):
        try:
            if ahora - partida["hora_inicio"] >= TIEMPO:
                try:
                    await context.bot.send_message(
                        chat_id=partida["chat_id"],
                        text="⏰ ¡Se acabó el tiempo!"
                    )
                except Exception:
                    pass
                await terminar_palabras(context, user_id, gano=False)
        except Exception:
            try:
                partidas_palabras.pop(user_id, None)
                terminar_partida(user_id)
            except Exception:
                pass

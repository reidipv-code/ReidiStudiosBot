import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.preguntas_trivia import TRIVIA
from core.preguntas_mundo import MUNDO
from core.logros import actualizar_stat, dar_logro, obtener_stats
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens

COOLDOWN_PERDIDA = 195
COOLDOWN_VICTORIA = 240

CONFIG_DIFICULTAD = {
    "facil":   {"tiempo": 30,  "premio_tokens": 30, "premio_xp": 30},
    "normal":  {"tiempo": 50,  "premio_tokens": 50, "premio_xp": 50},
    "dificil": {"tiempo": 100, "premio_tokens": 80, "premio_xp": 80},


TODAS_CATEGORIAS = {**TRIVIA, **MUNDO}

partidas_trivia = {}


def init_trivia_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trivia_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_partida FROM trivia_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO trivia_cooldown (user_id, ultima_partida) VALUES (?, ?)", (user_id, time.time()))
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
    for signo in [".", ",", ";", ":", "!", "?", "¡", "¿", "\"", "'"]:
        texto = texto.replace(signo, "")
    texto = " ".join(texto.split())
    return texto


def es_correcta(usuario, correcta):
    return normalizar(usuario) == normalizar(correcta)


async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_trivia:
        await update.message.reply_text("⚠️ Ya tienes una partida en curso.")
        return

    if not context.args:
        paises = list(TRIVIA.keys())
        mundo = list(MUNDO.keys())

        texto = (
            "🧠 *TRIVIA DE HISTORIA*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "Preguntas de historia de Latinoamérica y del mundo.\n\n"
            "🌎 *Países disponibles:*\n"
        )
        for p in paises:
            texto += f"• `{p}`\n"

        texto += "\n🌍 *Historia Mundial:*\n"
        for m in mundo:
            texto += f"• `{m}`\n"

        texto += (
            "\n📊 *Dificultades:*\n"
            "• `facil` → 30 tokens + 30 XP (40s)\n"
            "• `normal` → 50 tokens + 50 XP (60s)\n"
            "• `dificil` → 80 tokens + 80 XP (120s)\n\n"
            "📝 *Uso:*\n"
            "`/trivia mexico facil`\n"
            "`/trivia medieval normal`\n\n"
            "📌 *Cómo jugar:*\n"
            "• 5 preguntas por partida\n"
            "• Responde con `.respuesta`\n"
            "• Si fallas 1, pierdes la partida\n\n"
            "⏳ Cooldown: 7 min si pierdes, 10 si ganas."
        )
        await update.message.reply_text(texto, parse_mode="Markdown")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso: `/trivia <categoria> <dificultad>`", parse_mode="Markdown")
        return

    categoria = context.args[0].lower().strip()
    dificultad = normalizar(context.args[1])

    if categoria not in TODAS_CATEGORIAS:
        await update.message.reply_text("❌ Categoría no válida. Usa `/trivia` para ver la lista.", parse_mode="Markdown")
        return

    if dificultad not in CONFIG_DIFICULTAD:
        await update.message.reply_text("❌ Dificultad no válida: facil, normal o dificil.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        return

    preguntas_nivel = TODAS_CATEGORIAS[categoria][dificultad]
    seleccionadas = random.sample(preguntas_nivel, 5)
    config = CONFIG_DIFICULTAD[dificultad]

    partidas_trivia[user_id] = {
        "categoria": categoria,
        "dificultad": dificultad,
        "config": config,
        "preguntas": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time(),
    }
    iniciar_partida(user_id, "trivia")

    await update.message.reply_text(
        f"🧠 *Trivia de {categoria.capitalize()} - {dificultad.capitalize()}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ {config['tiempo']}s por pregunta.\n"
        f"Responde con `.respuesta`\n\n"
        f"Pregunta 1/5:",
        parse_mode="Markdown"
    )
    await enviar_pregunta(context, user_id)


async def enviar_pregunta(context, user_id):
    partida = partidas_trivia[user_id]
    idx = partida["indice"]
    if idx >= 5:
        return
    pregunta, _ = partida["preguntas"][idx]
    partida["hora_inicio"] = time.time()
    await context.bot.send_message(
        chat_id=partida["chat_id"],
        text=f"❓ *Pregunta {idx + 1}/5:*\n{pregunta}\n\n⏱️ {partida['config']['tiempo']}s",
        parse_mode="Markdown"
    )


async def responder_trivia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in partidas_trivia:
        return

    partida = partidas_trivia[user_id]
    texto = update.message.text.strip()
    if not texto.startswith("."):
        return

    if time.time() - partida["hora_inicio"] > partida["config"]["tiempo"]:
        await update.message.reply_text("⏰ ¡Se acabó el tiempo!")
        await terminar_trivia(context, user_id, gano=False)
        raise ApplicationHandlerStop

    respuesta = texto[1:].strip()
    _, correcta = partida["preguntas"][partida["indice"]]

    if es_correcta(respuesta, correcta):
        partida["aciertos"] += 1
        await update.message.reply_text("✅ ¡Correcto!")
    else:
        await update.message.reply_text(f"❌ Era *{correcta}*.", parse_mode="Markdown")
        await terminar_trivia(context, user_id, gano=False)
        raise ApplicationHandlerStop

    partida["indice"] += 1
    if partida["indice"] >= 5:
        await terminar_trivia(context, user_id, gano=True)
    else:
        await enviar_pregunta(context, user_id)
    raise ApplicationHandlerStop


async def terminar_trivia(context, user_id, gano):
    partida = partidas_trivia.pop(user_id, None)
    if partida is None:
        return
    config = partida["config"]
    set_cooldown(user_id)
    terminar_partida(user_id)

    actualizar_stat(user_id, "partidas_jugadas", incremento=1)

    # Misiones
    completadas = sumar_progreso(user_id, "partida_jugada")
    for m_id in completadas:
        await avisar_mision(context, user_id, m_id)

    if gano:
        actualizar_tokens(user_id, cantidad_con_bonus_tokens(user_id, config["premio_tokens"], "trivia"))
        subio = aplicar_bonus_xp(user_id, config["premio_xp"], "trivia")

        actualizar_stat(user_id, "trivias_ganadas", incremento=1)
        actualizar_stat(user_id, "trivia_seguidas", incremento=1)
        actualizar_stat(user_id, "mates_seguidas", valor=0)

        stats = obtener_stats(user_id)

        if stats[3] >= 20:
            if dar_logro(user_id, "erudito"):
                await avisar_logro(context, user_id, "erudito")

        if stats[8] + stats[9] >= 10:
            if dar_logro(user_id, "cerebrito"):
                await avisar_logro(context, user_id, "cerebrito")

        # Misiones (trivia ganada)
        completadas = sumar_progreso(user_id, "trivia_ganada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)

        texto = (
            f"🎉 *¡TRIVIA COMPLETADA!*\n"
            f"🌎 {partida['categoria'].capitalize()} - {partida['dificultad'].capitalize()}\n"
            f"✅ 5/5\n\n"
            f"💰 +{config['premio_tokens']} tokens\n"
            f"✨ +{config['premio_xp']} XP"
        )
        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"
        texto += "\n⏳ Cooldown: 10 min"
    else:
        actualizar_stat(user_id, "trivia_seguidas", valor=0)
        texto = (
            f"😢 *TRIVIA FALLIDA*\n"
            f"✅ Aciertos: {partida['aciertos']}/5\n"
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


async def revisar_timeouts_trivia(context) -> None:
    ahora = time.time()
    for user_id, partida in list(partidas_trivia.items()):
        if ahora - partida["hora_inicio"] > partida["config"]["tiempo"]:
            try:
                await context.bot.send_message(chat_id=partida["chat_id"], text="⏰ ¡Se acabó el tiempo!")
            except Exception:
                pass
            await terminar_trivia(context, user_id, gano=False)

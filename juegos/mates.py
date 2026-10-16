import random
import time
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.logros import actualizar_stat, dar_logro, obtener_stats
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens

COOLDOWN_PERDIDA = 195
COOLDOWN_VICTORIA = 240

CONFIG_NIVELES = {
    "noob":    {"nombre": "Noob",    "tiempo": 25, "premio_tokens": 10,  "premio_xp": 10},
    "facil":   {"nombre": "Fácil",   "tiempo": 25, "premio_tokens": 30,  "premio_xp": 30},
    "normal":  {"nombre": "Normal",  "tiempo": 25, "premio_tokens": 50,  "premio_xp": 50},
    "dificil": {"nombre": "Difícil", "tiempo": 50, "premio_tokens": 80,  "premio_xp": 80},
    "experto": {"nombre": "Experto", "tiempo": 90, "premio_tokens": 120, "premio_xp": 120},
}

PREGUNTAS_MATES = {
    "noob": [
        ("¿Cuánto es 5 + 3?", 8), ("¿Cuánto es 12 - 7?", 5), ("¿Cuánto es 4 + 4 + 2?", 10),
        ("¿Cuánto es 9 - 3?", 6), ("¿Cuánto es 7 + 6?", 13), ("¿Cuánto es 15 - 5?", 10),
        ("¿Cuánto es 3 + 3 + 3?", 9), ("¿Cuánto es 8 + 8?", 16), ("¿Cuánto es 20 - 12?", 8),
        ("¿Cuánto es 6 + 7?", 13), ("¿Cuánto es 10 + 10 + 5?", 25), ("¿Cuánto es 14 - 4?", 10),
        ("¿Cuánto es 2 + 2 + 2 + 2?", 8), ("¿Cuánto es 9 + 9?", 18), ("¿Cuánto es 30 - 20?", 10),
        ("¿Cuánto es 5 + 5 + 5?", 15), ("¿Cuánto es 11 - 6?", 5), ("¿Cuánto es 7 + 8?", 15),
        ("¿Cuánto es 25 - 5?", 20), ("¿Cuánto es 4 + 9?", 13),
    ],
    "facil": [
        ("¿Cuánto es 25 + 37?", 62), ("¿Cuánto es 8 × 6?", 48), ("¿Cuánto es 144 ÷ 12?", 12),
        ("¿Cuánto es 9 × 7?", 63), ("¿Cuánto es 100 - 45?", 55), ("¿Cuánto es 12 × 5?", 60),
        ("¿Cuánto es 72 ÷ 8?", 9), ("¿Cuánto es 36 + 48?", 84), ("¿Cuánto es 15 × 4?", 60),
        ("¿Cuánto es 200 - 87?", 113), ("¿Cuánto es 11 × 11?", 121), ("¿Cuánto es 96 ÷ 12?", 8),
        ("¿Cuánto es 45 + 67?", 112), ("¿Cuánto es 7 × 9?", 63), ("¿Cuánto es 250 - 100?", 150),
        ("¿Cuánto es 13 × 3?", 39), ("¿Cuánto es 144 ÷ 6?", 24), ("¿Cuánto es 56 + 78?", 134),
        ("¿Cuánto es 8 × 8?", 64), ("¿Cuánto es 300 - 123?", 177),
    ],
    "normal": [
        ("Resuelve: 15 × 4 - 10 = ?", 50), ("Resuelve: 2³ + 5² = ?", 33),
        ("¿Cuál es la raíz cuadrada de 81?", 9), ("Resuelve: 3 × 8 + 7 = ?", 31),
        ("¿Cuánto es 2⁴?", 16), ("Resuelve: (5 + 5) × 3 = ?", 30),
        ("¿Cuál es la raíz cuadrada de 144?", 12), ("Resuelve: 20 ÷ 4 + 6 = ?", 11),
        ("¿Cuánto es 3³?", 27), ("Resuelve: 100 - 5 × 8 = ?", 60),
        ("Resuelve: 12 + x = 20, x = ?", 8), ("Resuelve: 2x = 18, x = ?", 9),
        ("Resuelve: x - 5 = 12, x = ?", 17), ("¿Cuánto es 5² - 3²?", 16),
        ("Resuelve: 7 × 6 - 12 = ?", 30), ("Resuelve: 45 ÷ 5 + 3 = ?", 12),
        ("¿Cuál es la raíz cuadrada de 169?", 13), ("Resuelve: x + 15 = 30, x = ?", 15),
        ("¿Cuánto es 2⁵?", 32), ("Resuelve: 4 × 4 + 4 = ?", 20),
    ],
    "dificil": [
        ("¿Cuánto es 2⁶?", 64), ("Resuelve: 3x + 6 = 18, x = ?", 4),
        ("¿Cuánto es log₁₀(1000)?", 3), ("¿Cuánto es 5³?", 125),
        ("Resuelve: 2x - 8 = 12, x = ?", 10), ("¿Cuánto es √196?", 14),
        ("¿Cuánto es 3⁴?", 81), ("Resuelve: 5x + 10 = 35, x = ?", 5),
        ("¿Cuánto es log₂(64)?", 6), ("¿Cuánto es √256?", 16),
        ("Resuelve: 4x - 6 = 22, x = ?", 7), ("¿Cuánto es 2⁷?", 128),
        ("¿Cuánto es log₁₀(10000)?", 4), ("Resuelve: 7x = 91, x = ?", 13),
        ("¿Cuánto es √400?", 20), ("¿Cuánto es 6³?", 216),
        ("Resuelve: 2x + 15 = 45, x = ?", 15), ("¿Cuánto es log₃(27)?", 3),
        ("Resuelve: 3x - 9 = 21, x = ?", 10), ("¿Cuánto es 10² + 5²?", 125),
    ],
    "experto": [
        ("¿Cuánto es 3⁵?", 243), ("Resuelve: 2x² = 50, x = ? (positivo)", 5),
        ("¿Cuánto es sen(30°) × 10?", 5), ("¿Cuánto es 4⁵?", 1024),
        ("Resuelve: x² = 144, x = ? (positivo)", 12), ("¿Cuánto es cos(60°) × 10?", 5),
        ("¿Cuánto es 2¹⁰?", 1024), ("Resuelve: x² - 25 = 0, x = ? (positivo)", 5),
        ("¿Cuánto es sen(90°) × 8?", 8), ("¿Cuánto es 5⁵?", 3125),
        ("Resuelve: x³ = 27, x = ?", 3), ("¿Cuánto es cos(0°) × 7?", 7),
        ("¿Cuánto es 6⁴?", 1296), ("Resuelve: 3x² = 75, x = ? (positivo)", 5),
        ("¿Cuánto es tan(45°) × 9?", 9), ("¿Cuánto es log₂(1024)?", 10),
        ("Resuelve: x² + 6 = 42, x = ? (positivo)", 6), ("¿Cuánto es sen(0°) + 15?", 15),
        ("¿Cuánto es 7³?", 343), ("Resuelve: 2x³ = 54, x = ?", 3),
    ],
}

partidas_mates = {}


def init_mates_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mates_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_partida FROM mates_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO mates_cooldown (user_id, ultima_partida) VALUES (?, ?)", (user_id, time.time()))
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


async def mates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_mates:
        await update.message.reply_text("⚠️ Ya tienes una partida en curso.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(
            f"⏳ Debes esperar *{formatear_tiempo(restante)}* para volver a jugar.",
            parse_mode="Markdown"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "🧮 *MATEMÁTICAS*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "Niveles: noob, facil, normal, dificil, experto\n"
            "Uso: `/mates noob`\n"
            "Respondes con: `.8`",
            parse_mode="Markdown"
        )
        return

    nivel = normalizar(context.args[0])

    if nivel not in CONFIG_NIVELES:
        await update.message.reply_text("❌ Nivel no válido. Usa: noob, facil, normal, dificil, experto.")
        return

    seleccionadas = random.sample(PREGUNTAS_MATES[nivel], 5)
    config = CONFIG_NIVELES[nivel]

    partidas_mates[user_id] = {
        "nivel": nivel,
        "config": config,
        "preguntas": seleccionadas,
        "indice": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time(),
    }
    iniciar_partida(user_id, "mates")

    await update.message.reply_text(
        f"🧮 *Mates {config['nombre']}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ {config['tiempo']}s por pregunta.\n"
        f"Responde con `.respuesta`\n\n"
        f"Pregunta 1/5:",
        parse_mode="Markdown"
    )
    await enviar_pregunta(context, user_id)


async def enviar_pregunta(context, user_id):
    partida = partidas_mates[user_id]
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


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in partidas_mates:
        return

    partida = partidas_mates[user_id]
    texto = update.message.text.strip()
    if not texto.startswith("."):
        return

    if time.time() - partida["hora_inicio"] > partida["config"]["tiempo"]:
        await update.message.reply_text("⏰ ¡Se acabó el tiempo!")
        await terminar_mates(context, user_id, gano=False)
        raise ApplicationHandlerStop

    try:
        respuesta = float(texto[1:].strip().replace(",", "."))
    except ValueError:
        return

    _, correcta = partida["preguntas"][partida["indice"]]

    if abs(respuesta - correcta) < 0.01:
        await update.message.reply_text("✅ ¡Correcto!")
    else:
        await update.message.reply_text(f"❌ Era *{correcta}*.", parse_mode="Markdown")
        await terminar_mates(context, user_id, gano=False)
        raise ApplicationHandlerStop

    partida["indice"] += 1
    if partida["indice"] >= 5:
        await terminar_mates(context, user_id, gano=True)
    else:
        await enviar_pregunta(context, user_id)

    raise ApplicationHandlerStop


async def terminar_mates(context, user_id, gano):
    partida = partidas_mates.pop(user_id, None)
    if partida is None:
        return
    config = partida["config"]
    terminar_partida(user_id)
    set_cooldown(user_id)

    # Logros
    actualizar_stat(user_id, "partidas_jugadas", incremento=1)

    # Misiones
    completadas = sumar_progreso(user_id, "partida_jugada")
    for m_id in completadas:
        await avisar_mision(context, user_id, m_id)

    if gano:
        actualizar_tokens(user_id, cantidad_con_bonus_tokens(user_id, config["premio_tokens"], "mates"))
        subio = aplicar_bonus_xp(user_id, config["premio_xp"], "mates")

        actualizar_stat(user_id, "mates_ganadas", incremento=1)
        actualizar_stat(user_id, "mates_seguidas", incremento=1)
        actualizar_stat(user_id, "trivia_seguidas", valor=0)

        stats = obtener_stats(user_id)

        if stats[2] >= 15:
            if dar_logro(user_id, "matematico"):
                await avisar_logro(context, user_id, "matematico")

        if stats[8] + stats[9] >= 10:
            if dar_logro(user_id, "cerebrito"):
                await avisar_logro(context, user_id, "cerebrito")

        # Misiones (mates ganada)
        completadas = sumar_progreso(user_id, "mates_ganada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)

        texto = (
            f"🎉 *¡Mates completadas!*\n"
            f"💰 +{config['premio_tokens']} tokens\n"
            f"✨ +{config['premio_xp']} XP"
        )
        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"
        texto += "\n⏳ Cooldown: 5 min"
    else:
        actualizar_stat(user_id, "mates_seguidas", valor=0)
        texto = f"😢 *Partida terminada*\n✅ Aciertos: {partida['indice']}/5\n⏳ Cooldown: 7 min"

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


async def revisar_timeouts(context) -> None:
    ahora = time.time()
    for user_id, partida in list(partidas_mates.items()):
        if ahora - partida["hora_inicio"] > partida["config"]["tiempo"]:
            try:
                await context.bot.send_message(chat_id=partida["chat_id"], text="⏰ ¡Se acabó el tiempo!")
            except Exception:
                pass
            await terminar_mates(context, user_id, gano=False)


async def confirmar_juego(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    return


async def verificar_comando_en_partida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    return

import sqlite3
import random
import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.misiones import sumar_progreso
from core.tienda import aplicar_bonus_xp, cantidad_con_bonus_tokens

COOLDOWN_PERDIDA = 195
COOLDOWN_VICTORIA = 240
TIEMPO = 40
CANCIONES_POR_PARTIDA = 3

FUNKS = [
    ("Na festa do fim de semana, sahur chegou", "passo bem solto", "atlxs"),
    ("Vida la vida es un carrusel", "montagem tomada", "josh gomez"),
    ("A mira la luna, lalalalalalala", "luna bala", "yb wasg'ood, ariis, mc pr"),
    ("Hay mi gatito miau miau", "montagem miau", "evelyn villabona"),
    ("Do Prada, no Prada\nDo pai da acelerada", "acelerada", "mxzi"),
    ("Clima perfeito, noite enluarada", "montagem bailao", "atlxs, mc jhey"),
    ("E-Ela desce, ela sobe, no baile e pressao", "no batidao", "zxkai"),
    ("Please, Speed, I need this, my mom", "kinda homeless", "anitor, hugeboy, vlxnor"),
    ("Quando essa tocar, tu vai se lembrar\nDe que eu era um bosta e tu nao queria me pegar", "yara yara", "mc wm, mc lan"),
    ("Uh, ah-ah, toma, toma", "esse cara", "sayfalse"),
    ("Y pensaron que me iba a caer\nPero no\nDe su mala la vibra, a mi me protegio", "funk do bounce", "ariis"),
    ("No se el dia, la-la-la, la-la-la, la\nSolo una noche\nLa-la-la, la-la-la, la-la-la, la-la-la, la", "los voltage", "sayfalse"),
    ("Olha so minha ponto 30\nTu nunca prestou atencao", "mente ma", "nakama"),
    ("Vem, vem, foder", "vem vem", "jimilton"),
    ("Ve-vem no pique", "madrugada", "ncts"),
    ("Mala fama, mala fama", "montagem coma", "adromeda"),
    ("D-D-D-D-D-D-DJ-DJ heapper, e-e-e-e-e o", "montagem vozes", "heapper, mc luizinho, dj juan"),
    ("Teus teus do funk. Manda sim, manda sim, manda, manda, manda sim.", "montagem escuro", "phonk around"),
    ("E vou 'xonar\nMas nao vou com quanta som", "montagem xonada", "dj javi"),
    ("O, novinha, taradinha, danadinha, gostosinha", "montagem supersonic", "mc jaja, khaos, jmilton"),
    ("Bailalo (y), gozalo (y)\nComo lo canto y lo siento yo (y como?)", "gozalo", "ariis"),
    ("Vento sussurra historias sem fim", "montagem rugada", "cape, sayfalse, jxndro"),
    ("Fez promessa, jurou lealdade\nMas mostrou que so viveu de falsidade", "matadora", "dj asul"),
    ("Voce fez a escolha\nAgora aguenta a consequencia", "vair vair trair", "dj asul"),
    ("Luz roja, no para, que el tiempo nos habla", "luz roja", "bxkq"),
    ("bate, bate, bate, bate\nFirme, firme, firme, firme", "montagem pegadora", "chilx, waa, rubikdice"),
    ("Tiki-tiki-tiki\nMa-te-te-ki-ta-ka-ta", "tiki-tiki", "qmiir, salima chica"),
    ("Run to me, confess your love, at least just say it", "confess your love", "jiandro"),
    ("Cheguei no baile, luzes a piscar", "voce na mira", "hwungii, dj vgk1"),
]

partidas_funks = {}


def init_funks_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS funks_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL
        )
    """)
    conn.commit()
    conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_partida FROM funks_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO funks_cooldown (user_id, ultima_partida) VALUES (?, ?)", (user_id, time.time()))
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
    for k, v in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ç": "c"}.items():
        texto = texto.replace(k, v)
    return texto


def autores_lista(autores):
    return [a.strip() for a in autores.split(",") if a.strip()]


def es_correcta(respuesta, nombre, autores):
    resp_norm = normalizar(respuesta)
    if resp_norm == normalizar(nombre):
        return True
    for a in autores_lista(autores):
        if resp_norm == normalizar(a):
            return True
    return False


async def funks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_funks:
        await update.message.reply_text("⚠️ Ya tienes una partida en curso.")
        return

    restante = tiempo_restante(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        return

    seleccionadas = random.sample(FUNKS, CANCIONES_POR_PARTIDA)

    partidas_funks[user_id] = {
        "canciones": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time()
    }
    iniciar_partida(user_id, "funks")

    await update.message.reply_text(
        "🎵 *ADIVINA LA CANCIÓN (BETA)*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Versión beta, puede tener errores.\n\n"
        "Te muestro la letra de un funk.\n"
        "Responde con `.nombre` o `.autor`\n\n"
        f"⏱️ {TIEMPO}s por canción. 3 canciones.\n"
        "Premio: 40 tokens + 45 XP",
        parse_mode="Markdown"
    )
    await enviar_cancion(context, user_id)


async def enviar_cancion(context, user_id):
    partida = partidas_funks[user_id]
    idx = partida["indice"]
    if idx >= CANCIONES_POR_PARTIDA:
        return
    letra, nombre, autores = partida["canciones"][idx]
    partida["hora_inicio"] = time.time()
    await context.bot.send_message(
        chat_id=partida["chat_id"],
        text=(
            f"🎵 *Canción {idx + 1}/{CANCIONES_POR_PARTIDA}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Letra:*\n_{letra}_\n\n"
            f"⏱️ {TIEMPO}s. `.nombre` o `.autor`"
        ),
        parse_mode="Markdown"
    )


async def responder_funks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in partidas_funks:
        return

    partida = partidas_funks[user_id]
    texto = update.message.text.strip()
    if not texto.startswith("."):
        return

    respuesta = texto[1:].strip()
    letra, nombre, autores = partida["canciones"][partida["indice"]]

    if es_correcta(respuesta, nombre, autores):
        partida["aciertos"] += 1
        await update.message.reply_text(f"✅ ¡Correcto! Era *{nombre}* ({autores}).", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Era *{nombre}* de *{autores}*.", parse_mode="Markdown")
        await terminar_funks(context, user_id, gano=False)
        raise ApplicationHandlerStop

    partida["indice"] += 1
    if partida["indice"] >= CANCIONES_POR_PARTIDA:
        await terminar_funks(context, user_id, gano=True)
    else:
        await enviar_cancion(context, user_id)
    raise ApplicationHandlerStop


async def terminar_funks(context, user_id, gano):
    partida = partidas_funks.pop(user_id, None)
    if partida is None:
        return
    set_cooldown(user_id)
    terminar_partida(user_id)

    if gano:
        actualizar_tokens(user_id, cantidad_con_bonus_tokens(user_id, 40, "funks"))
        subio = aplicar_bonus_xp(user_id, 45, "funks")
        texto = f"🎉 *¡FUNKS COMPLETADOS!*\n✅ 3/3\n💰 +40 tokens\n✨ +45 XP"
        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"
        texto += "\n⏳ Cooldown: 10 min"

        # Misiones
        completadas = sumar_progreso(user_id, "funks_completada")
        for m_id in completadas:
            await avisar_mision(context, user_id, m_id)
    else:
        texto = f"😢 *FALLIDO*\n✅ Aciertos: {partida['aciertos']}/3\n⏳ Cooldown: 7 min"

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


async def revisar_timeouts_funks(context) -> None:
    ahora = time.time()
    for user_id, partida in list(partidas_funks.items()):
        if ahora - partida["hora_inicio"] > TIEMPO:
            try:
                await context.bot.send_message(chat_id=partida["chat_id"], text="⏰ ¡Se acabó el tiempo!")
            except Exception:
                pass
            await terminar_funks(context, user_id, gano=False)

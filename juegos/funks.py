import sqlite3
import random
import time
import logging

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, actualizar_tokens, sumar_xp, DB_PATH
from core.sesiones import iniciar_partida, terminar_partida
from core.misiones import sumar_progreso


# ============================================================
# CONFIGURACIÓN
# ============================================================

COOLDOWN_PERDIDA = 420       # 7 minutos
COOLDOWN_VICTORIA = 600      # 10 minutos
TIEMPO = 40                  # 40 segundos por canción
CANCIONES_POR_PARTIDA = 3

# Si una sesión de SQLite lleva demasiado tiempo sin actualizarse
# y ya no existe la partida en RAM, se considera huérfana.
TIEMPO_SESION_HUERFANA = TIEMPO * 2 + 5

logger = logging.getLogger(__name__)


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



# ============================================================
# BASE DE DATOS
# ============================================================

def init_funks_db():
    """Crea/migra la tabla de cooldown de Funks."""
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS funks_cooldown (
                user_id INTEGER PRIMARY KEY,
                ultima_partida REAL,
                duracion INTEGER DEFAULT 600
            )
        """)

        # Migración para instalaciones que ya tenían la tabla antigua.
        c.execute("PRAGMA table_info(funks_cooldown)")
        columnas = {fila[1] for fila in c.fetchall()}

        if "duracion" not in columnas:
            c.execute(
                "ALTER TABLE funks_cooldown "
                "ADD COLUMN duracion INTEGER DEFAULT 600"
            )

        conn.commit()
    finally:
        conn.close()


def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT ultima_partida, duracion "
            "FROM funks_cooldown WHERE user_id = ?",
            (user_id,),
        )
        r = c.fetchone()

        if not r:
            return 0, COOLDOWN_VICTORIA

        ultima = r[0] or 0
        duracion = r[1] or COOLDOWN_VICTORIA
        return ultima, duracion
    finally:
        conn.close()


def set_cooldown(user_id, gano=False):
    """Guarda el cooldown correspondiente a victoria o derrota."""
    duracion = COOLDOWN_VICTORIA if gano else COOLDOWN_PERDIDA

    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute(
            """
            INSERT OR REPLACE INTO funks_cooldown
            (user_id, ultima_partida, duracion)
            VALUES (?, ?, ?)
            """,
            (user_id, time.time(), duracion),
        )
        conn.commit()
    finally:
        conn.close()


def tiempo_restante(user_id):
    ultima, duracion = get_cooldown(user_id)

    if ultima == 0:
        return 0

    return max(0, int(duracion - (time.time() - ultima)))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


# ============================================================
# UTILIDADES
# ============================================================

def normalizar(texto):
    texto = str(texto).lower().strip()

    for k, v in {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "ç": "c",
    }.items():
        texto = texto.replace(k, v)

    return texto


def autores_lista(autores):
    return [a.strip() for a in autores.split(",") if a.strip()]


def es_correcta(respuesta, nombre, autores):
    resp_norm = normalizar(respuesta)

    if resp_norm == normalizar(nombre):
        return True

    for autor in autores_lista(autores):
        if resp_norm == normalizar(autor):
            return True

    return False


async def enviar_mensaje_seguro(context, chat_id, texto, **kwargs):
    """Envía un mensaje sin dejar que un fallo de Telegram rompa la partida."""
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=texto,
            **kwargs,
        )
        return True
    except Exception:
        logger.exception(
            "Error enviando mensaje de Funks a chat_id=%s",
            chat_id,
        )
        return False


def _eliminar_sesion_directamente(user_id):
    """
    Último recurso para limpiar una sesión que haya quedado atascada.

    Normalmente se usa terminar_partida(). Esta función solo actúa
    si SQLite no pudo limpiarse por el camino normal.
    """
    for intento in range(3):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            c = conn.cursor()
            c.execute(
                "DELETE FROM sesiones WHERE user_id = ?",
                (user_id,),
            )
            conn.commit()
            return True
        except Exception:
            logger.exception(
                "Intento %s/3: no pude limpiar sesión de user_id=%s",
                intento + 1,
                user_id,
            )
            time.sleep(0.15)
        finally:
            if conn is not None:
                conn.close()

    return False


def _terminar_sesion_segura(user_id):
    """Limpia la sesión normal y usa un fallback si falla."""
    try:
        terminar_partida(user_id)
        return True
    except Exception:
        logger.exception(
            "terminar_partida() falló para user_id=%s. "
            "Intentando limpieza directa.",
            user_id,
        )
        return _eliminar_sesion_directamente(user_id)


# ============================================================
# INICIAR FUNKS
# ============================================================

async def funks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)

    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    if user_id in partidas_funks:
        await update.message.reply_text(
            "⚠️ Ya tienes una partida en curso."
        )
        return

    restante = tiempo_restante(user_id)

    if restante > 0:
        await update.message.reply_text(
            f"⏳ Espera *{formatear_tiempo(restante)}*.",
            parse_mode="Markdown",
        )
        return

    seleccionadas = random.sample(
        FUNKS,
        CANCIONES_POR_PARTIDA,
    )

    partida = {
        "canciones": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time(),
    }

    # Primero creamos la sesión persistente.
    try:
        iniciar_partida(user_id, "funks")
    except Exception:
        logger.exception(
            "No pude crear la sesión de Funks para user_id=%s",
            user_id,
        )
        await update.message.reply_text(
            "⚠️ No pude iniciar la partida. Inténtalo de nuevo."
        )
        return

    # Solo después de crear la sesión persistente guardamos la partida en RAM.
    partidas_funks[user_id] = partida

    try:
        await update.message.reply_text(
            "🎵 *ADIVINA LA CANCIÓN (BETA)*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ Versión beta, puede tener errores.\n\n"
            "Te muestro la letra de un funk.\n"
            "Responde con `.nombre` o `.autor`\n\n"
            f"⏱️ {TIEMPO}s por canción. {CANCIONES_POR_PARTIDA} canciones.\n"
            "Premio: 40 tokens + 45 XP",
            parse_mode="Markdown",
        )

        await enviar_cancion(context, user_id)

    except Exception:
        logger.exception(
            "Error iniciando la partida de Funks para user_id=%s",
            user_id,
        )

        # No dejamos al usuario bloqueado si falló el inicio.
        partidas_funks.pop(user_id, None)
        _terminar_sesion_segura(user_id)


# ============================================================
# ENVIAR CANCIÓN
# ============================================================

async def enviar_cancion(context, user_id):
    partida = partidas_funks.get(user_id)

    if partida is None:
        return False

    idx = partida["indice"]

    if idx >= CANCIONES_POR_PARTIDA:
        return False

    letra, nombre, autores = partida["canciones"][idx]

    # Este timestamp controla los 40 segundos de ESTA canción.
    ahora = time.time()
    partida["hora_inicio"] = ahora

    # Actualizamos también la sesión SQLite.
    #
    # Esto es importante si Railway tiene más de un proceso:
    # la sesión persistente refleja cuándo comenzó la canción actual.
    try:
        iniciar_partida(user_id, "funks")
    except Exception:
        logger.exception(
            "No pude actualizar la sesión de Funks para user_id=%s",
            user_id,
        )

    enviada = await enviar_mensaje_seguro(
        context,
        partida["chat_id"],
        (
            f"🎵 *Canción {idx + 1}/{CANCIONES_POR_PARTIDA}*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Letra:*\n_{letra}_\n\n"
            f"⏱️ {TIEMPO}s. `.nombre` o `.autor`"
        ),
        parse_mode="Markdown",
    )

    return enviada


# ============================================================
# RESPUESTAS
# ============================================================

async def responder_funks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user_id = update.effective_user.id

    partida = partidas_funks.get(user_id)

    if partida is None:
        return

    if not update.message or not update.message.text:
        return

    texto = update.message.text.strip()

    if not texto.startswith("."):
        return

    respuesta = texto[1:].strip()

    if not respuesta:
        raise ApplicationHandlerStop

    indice = partida.get("indice", 0)

    if indice >= CANCIONES_POR_PARTIDA:
        await terminar_funks(context, user_id, gano=False)
        raise ApplicationHandlerStop

    letra, nombre, autores = partida["canciones"][indice]

    if es_correcta(respuesta, nombre, autores):
        partida["aciertos"] += 1

        await enviar_mensaje_seguro(
            context,
            update.effective_chat.id,
            f"✅ ¡Correcto! Era *{nombre}* ({autores}).",
            parse_mode="Markdown",
        )

        partida["indice"] += 1

        if partida["indice"] >= CANCIONES_POR_PARTIDA:
            await terminar_funks(
                context,
                user_id,
                gano=True,
            )
        else:
            await enviar_cancion(
                context,
                user_id,
            )

    else:
        await enviar_mensaje_seguro(
            context,
            update.effective_chat.id,
            f"❌ Era *{nombre}* de *{autores}*.",
            parse_mode="Markdown",
        )

        await terminar_funks(
            context,
            user_id,
            gano=False,
        )

    # Evita que otros handlers de mensajes con "." procesen la respuesta.
    raise ApplicationHandlerStop


# ============================================================
# TERMINAR PARTIDA
# ============================================================

async def terminar_funks(context, user_id, gano):
    """
    Termina una partida de forma segura.

    MUY IMPORTANTE:
    la partida se elimina de RAM y la sesión SQLite se limpia
    antes de ejecutar recompensas/misiones que podrían fallar.
    Así nunca queda una partida fantasma bloqueando al usuario.
    """

    # pop() es idempotente: si otro proceso/llamada ya la eliminó,
    # simplemente no hacemos nada.
    partida = partidas_funks.pop(user_id, None)

    if partida is None:
        # Aunque no exista en RAM, limpiamos SQLite por seguridad.
        _terminar_sesion_segura(user_id)
        return

    # Guardamos el cooldown y limpiamos la sesión SIEMPRE.
    try:
        set_cooldown(user_id, gano=gano)
    except Exception:
        logger.exception(
            "No pude guardar cooldown de Funks para user_id=%s",
            user_id,
        )

    _terminar_sesion_segura(user_id)

    # A partir de aquí, aunque falle una recompensa, el usuario
    # ya no queda atrapado en la partida.

    if gano:
        try:
            actualizar_tokens(user_id, 40)
        except Exception:
            logger.exception(
                "Error dando tokens de Funks a user_id=%s",
                user_id,
            )

        try:
            subio = sumar_xp(user_id, 45)
        except Exception:
            logger.exception(
                "Error dando XP de Funks a user_id=%s",
                user_id,
            )
            subio = None

        texto = (
            f"🎉 *¡FUNKS COMPLETADOS!*\n"
            f"✅ {CANCIONES_POR_PARTIDA}/{CANCIONES_POR_PARTIDA}\n"
            "💰 +40 tokens\n"
            "✨ +45 XP"
        )

        if subio:
            texto += f"\n⭐ ¡Nivel {subio}!"

        texto += "\n⏳ Cooldown: 10 min"

        # Misiones: si una misión falla, no debe romper el final de partida.
        try:
            completadas = sumar_progreso(
                user_id,
                "funks_completada",
            )
        except Exception:
            logger.exception(
                "Error actualizando misión de Funks para user_id=%s",
                user_id,
            )
            completadas = []

        for m_id in completadas:
            try:
                await avisar_mision(
                    context,
                    user_id,
                    m_id,
                )
            except Exception:
                logger.exception(
                    "Error avisando misión %s a user_id=%s",
                    m_id,
                    user_id,
                )

    else:
        texto = (
            "😢 *FALLIDO*\n"
            f"✅ Aciertos: {partida['aciertos']}/{CANCIONES_POR_PARTIDA}\n"
            "⏳ Cooldown: 7 min"
        )

    await enviar_mensaje_seguro(
        context,
        partida["chat_id"],
        texto,
        parse_mode="Markdown",
    )


# ============================================================
# AVISO DE MISIÓN
# ============================================================

async def avisar_mision(context, user_id, m_id):
    from core.misiones import MISIONES

    info = MISIONES.get(m_id)

    if not info:
        return

    recompensa = f"+{info['tokens']}💰"

    if info["xp"] > 0:
        recompensa += f" +{info['xp']}⭐"

    await enviar_mensaje_seguro(
        context,
        user_id,
        (
            "🎯 *¡MISIÓN COMPLETADA!*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"✅ {info['texto']}\n"
            f"🎁 {recompensa}"
        ),
        parse_mode="Markdown",
    )


# ============================================================
# LIMPIEZA DE SESIONES HUÉRFANAS
# ============================================================

def limpiar_sesiones_funks_huerfanas():
    """
    Limpia sesiones de Funks que quedaron en SQLite pero ya no existen
    en partidas_funks.

    Esto sirve especialmente después de un reinicio de Railway o si
    había más de un proceso ejecutando el bot.
    """
    ahora = time.time()
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        c = conn.cursor()

        c.execute(
            """
            SELECT user_id, inicio
            FROM sesiones
            WHERE juego = ?
            """,
            ("funks",),
        )

        sesiones = c.fetchall()

        eliminadas = 0

        for user_id, inicio in sesiones:
            # Si la partida existe en este proceso, está controlada por
            # revisar_timeouts_funks y no debe tocarse aquí.
            if user_id in partidas_funks:
                continue

            if inicio is None:
                continue

            if ahora - inicio >= TIEMPO_SESION_HUERFANA:
                c.execute(
                    "DELETE FROM sesiones WHERE user_id = ?",
                    (user_id,),
                )
                eliminadas += 1

                logger.warning(
                    "Sesión huérfana de Funks eliminada: user_id=%s",
                    user_id,
                )

        conn.commit()

        if eliminadas:
            logger.info(
                "Limpieza Funks: %s sesión(es) huérfana(s) eliminada(s).",
                eliminadas,
            )

    except Exception:
        logger.exception(
            "Error limpiando sesiones huérfanas de Funks."
        )

    finally:
        if conn is not None:
            conn.close()


# ============================================================
# TIMEOUTS
# ============================================================

async def revisar_timeouts_funks(context) -> None:
    """
    Revisa cada partida activa.

    La JobQueue puede ejecutar esta función cada 10 segundos.
    El timeout real sigue siendo TIEMPO = 40 segundos.
    """
    ahora = time.time()

    try:
        for user_id, partida in list(partidas_funks.items()):

            try:
                hora_inicio = float(partida.get("hora_inicio", ahora))
            except (TypeError, ValueError):
                hora_inicio = ahora

            transcurrido = ahora - hora_inicio

            if transcurrido >= TIEMPO:
                logger.info(
                    "Timeout de Funks: user_id=%s, %.1fs transcurridos.",
                    user_id,
                    transcurrido,
                )

                await enviar_mensaje_seguro(
                    context,
                    partida["chat_id"],
                    "⏰ ¡Se acabó el tiempo!",
                )

                # terminar_funks elimina primero el estado de RAM y
                # después limpia SQLite, por lo que no queda bloqueado
                # aunque falle una recompensa o un mensaje.
                await terminar_funks(
                    context,
                    user_id,
                    gano=False,
                )

    except Exception:
        # Una partida problemática nunca debe impedir que el job vuelva
        # a ejecutarse en la siguiente ronda.
        logger.exception(
            "Error general revisando timeouts de Funks."
        )

    # Fallback para sesiones SQLite que sobrevivieron a un reinicio
    # o pertenecen a otro proceso y ya quedaron huérfanas.
    try:
        limpiar_sesiones_funks_huerfanas()
    except Exception:
        logger.exception(
            "Error en la limpieza de sesiones huérfanas de Funks."
        )

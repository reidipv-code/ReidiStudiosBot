import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ApplicationHandlerStop,
    CallbackQueryHandler,
)

# ============================================================
# CORE
# ============================================================

from core.db import (
    init_db,
    esta_registrado,
    obtener_datos,
    usuario_tiene_pais,
    actualizar_ultima_actividad,
)

from core.sesiones import (
    init_sesiones_db,
    obtener_juego,
)

from core.paises import (
    lista_paises_texto,
)

from core.logros import (
    init_logros_db,
    LOGROS,
    dar_logro,
)

from core.amigos import (
    init_amigos_db,
)

from core.misiones import (
    init_misiones_db,
)


# ============================================================
# COMANDOS
# ============================================================

from comandos.registro import (
    reg,
    unreg,
    deletereg,
    confirmar_accion,
    setpais,
)

from comandos.perfil import (
    perfil,
    tokens_cmd,
    nivel_cmd,
    rango_cmd,
    userslist,
)

from comandos.tutorial import (
    tutorial,
)

from comandos.chat import (
    chatm,
    msp,
    darTokens,
)

from comandos.top import (
    top,
)

from comandos.stats import (
    stats,
)

from comandos.sugerencia import (
    sugerencia,
)

from comandos.help import (
    help_command,
    help_botones,
)

from comandos.version import (
    version,
    setversion,
)

from comandos.logros import (
    logros,
)

from comandos.reclamarlogros import (
    reclamarlogros,
)

from comandos.amigos import (
    amigo,
    amigos,
    solicitudes,
)

from comandos.amigos_top import (
    top_amigos,
)

from comandos.amigos_invitar import (
    invitar,
    responder_invitacion,
    revisar_invitaciones_expiradas,
)

from comandos.misiones import (
    misiones,
)


# ============================================================
# ADMIN
# ============================================================

from admin import (
    anunciar,
    giveTokens,
    giveXP,
    removeTokens,
    removeXP,
)


# ============================================================
# BANCO
# ============================================================

from banco.banco import (
    init_banco_db,
    bank,
    depositar,
    retirar,
)


# ============================================================
# JUEGOS
# ============================================================

from juegos.menu import (
    actividades,
)

from juegos.ruleta import (
    init_juegos_db,
    ruleta,
)

from juegos.apuestas import (
    init_apuestas_db,
    apostar,
    cancelar,
    revisar_expiradas,
)


# ============================================================
# MATES
# ============================================================

from juegos.mates import (
    init_mates_db,
    mates,
    responder as responder_mates,
    revisar_timeouts as revisar_timeouts_mates,
)


# ============================================================
# DADOS
# ============================================================

from juegos.dados import (
    init_dados_db,
    dados,
)


# ============================================================
# MEMORIA
# ============================================================

from juegos.memoria import (
    init_memoria_db,
    memoria,
    responder_memoria,
    revisar_timeouts_memoria,
)


# ============================================================
# PALABRAS
# ============================================================
#
# IMPORTANTE:
# La función en palabras.py se llama:
#
#     revisar_timeouts_palabras
#
# NO:
#
#     revisar_timeouts
#
# ============================================================

from juegos.palabras import (
    init_palabras_db,
    palabras,
    responder_palabras,
    revisar_timeouts_palabras,
)


# ============================================================
# FUNKS
# ============================================================

from juegos.funks import (
    init_funks_db,
    funks,
    responder_funks,
    revisar_timeouts_funks,
)


# ============================================================
# TRIVIA
# ============================================================

from juegos.trivia import (
    init_trivia_db,
    trivia,
    responder_trivia,
    revisar_timeouts_trivia,
)


# ============================================================
# EVENTOS
# ============================================================

from eventos.eventos import (
    init_eventos_db,
    eventos,
    ver_evento,
    asistir,
    atras,
    comenzar,
    cancelar_evento,
    addevent,
    removeevent,
    editevent,
    revisar_eventos_expirados,
    revisar_eventos_iniciando,
    revisar_descalificados,
)

from eventos.reclamar import (
    init_reclamar_db,
    reclamar,
)


# ============================================================
# VARIABLES
# ============================================================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# COMANDOS VÁLIDOS
# ============================================================

COMANDOS_VALIDOS = [
    "/start",
    "/help",
    "/reg",
    "/unreg",
    "/deletereg",

    "/perfil",
    "/tokens",
    "/nivel",
    "/rango",

    "/actividades",
    "/juegos",
    "/ruleta",
    "/apostar",
    "/cancelar",

    "/userslist",
    "/mates",
    "/tutorial",

    "/bank",
    "/depositar",
    "/retirar",

    "/anunciar",
    "/reclamar",

    "/eventos",
    "/addevent",
    "/removeevent",
    "/editevent",

    "/giveTokens",
    "/giveXP",
    "/removeTokens",
    "/removeXP",

    "/dados",
    "/memoria",
    "/trivia",
    "/palabras",
    "/funks",

    "/setpais",

    "/chatm",
    "/msp",
    "/darTokens",

    "/top",
    "/stats",
    "/sugerencia",

    "/version",
    "/setversion",

    "/logros",
    "/reclamarlogros",

    "/amigo",
    "/amigos",
    "/solicitudes",
    "/invitar",

    "/top_amigos",
    "/topamigos",

    "/misiones",
]


COMANDOS_VALIDOS_LOWER = [
    comando.lower()
    for comando in COMANDOS_VALIDOS
]


# ============================================================
# AVISAR LOGRO
# ============================================================

async def avisar_logro(
    context,
    user_id,
    clave,
):

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


# ============================================================
# AVISAR MISIÓN
# ============================================================

async def avisar_mision(
    context,
    user_id,
    m_id,
):

    from core.misiones import MISIONES

    info = MISIONES.get(m_id)

    if not info:
        return

    recompensa = (
        f"+{info['tokens']}💰"
    )

    if info["xp"] > 0:
        recompensa += (
            f" +{info['xp']}⭐"
        )

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


# ============================================================
# RASTREAR ACTIVIDAD
# ============================================================

async def rastrear_actividad(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.effective_user:
        return

    try:

        actualizar_ultima_actividad(
            update.effective_user.id
        )

    except Exception:
        pass


# ============================================================
# COMANDOS PERMITIDOS DURANTE UNA PARTIDA
# ============================================================

COMANDOS_PERMITIDOS_EN_PARTIDA = {
    "/start",
    "/help",
    "/cancelar",

    "/perfil",
    "/tokens",
    "/nivel",
    "/rango",
    "/stats",
    "/top",

    "/logros",
    "/reclamarlogros",

    "/amigo",
    "/amigos",
    "/solicitudes",
    "/invitar",
    "/top_amigos",
    "/topamigos",

    "/misiones",

    "/sugerencia",
    "/version",
}


# ============================================================
# BLOQUEAR COMANDOS EN PARTIDA
# ============================================================

async def bloquear_comandos_en_partida(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    if not update.message.text:
        return

    if not update.effective_user:
        return

    user_id = update.effective_user.id

    try:

        juego = obtener_juego(
            user_id
        )

    except Exception:

        return

    if juego is None:
        return

    texto = update.message.text.strip()

    # --------------------------------------------------------
    # Los mensajes normales pasan.
    # Las respuestas .algo también pasan.
    # --------------------------------------------------------

    if not texto.startswith("/"):
        return

    # --------------------------------------------------------
    # Obtener comando sin @Bot
    # --------------------------------------------------------

    comando = (
        texto
        .split()[0]
        .split("@")[0]
        .lower()
    )

    # --------------------------------------------------------
    # Comandos permitidos durante una partida
    # --------------------------------------------------------

    if comando in COMANDOS_PERMITIDOS_EN_PARTIDA:
        return

    # --------------------------------------------------------
    # Bloquear el resto
    # --------------------------------------------------------

    await update.message.reply_text(
        f"⚠️ Estás en una partida de *{juego}*.\n\n"
        "Termínala primero para usar este comando.\n\n"
        "Puedes usar `/top`, `/amigos`, `/misiones`, "
        "`/sugerencia` y otros comandos permitidos.",
        parse_mode="Markdown",
    )

    raise ApplicationHandlerStop


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "¡Hola! Soy ReidiStudiosBot.\n\n"
        "Regístrate con:\n"
        "/reg nombre.pais\n\n"
        "Ejemplo: /reg Juan.cuba\n\n"
        "Usa /help para ver todos los comandos."
    )


# ============================================================
# VERIFICAR REGISTRO
# ============================================================

async def verificar_registro(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    if not update.message.text:
        return

    texto = update.message.text.strip()

    if not texto.startswith("/"):
        return

    comando = (
        texto
        .split()[0]
        .split("@")[0]
        .lower()
    )

    # --------------------------------------------------------
    # Comando no reconocido
    # --------------------------------------------------------

    if comando not in COMANDOS_VALIDOS_LOWER:

        await update.message.reply_text(
            f"❌ Comando no reconocido: `{comando}`\n\n"
            "Usa /help.",
            parse_mode="Markdown",
        )

        raise ApplicationHandlerStop

    # --------------------------------------------------------
    # Comandos que no requieren registro
    # --------------------------------------------------------

    comandos_libres = {
        "/start",
        "/help",
        "/reg",
        "/unreg",
        "/deletereg",
        "/tutorial",
        "/setpais",
        "/version",
    }

    if comando in comandos_libres:
        return

    # --------------------------------------------------------
    # Usuario
    # --------------------------------------------------------

    if not update.effective_user:
        return

    user_id = update.effective_user.id

    # --------------------------------------------------------
    # Comprobar registro
    # --------------------------------------------------------

    try:

        registrado = esta_registrado(
            user_id
        )

    except Exception as e:

        print(
            f"❌ Error comprobando registro "
            f"{user_id}: {e}"
        )

        return

    if not registrado:

        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\n"
            "Usa: /reg nombre.pais"
        )

        raise ApplicationHandlerStop

    # --------------------------------------------------------
    # Comprobar sesión
    # --------------------------------------------------------

    try:

        datos = obtener_datos(
            user_id
        )

    except Exception as e:

        print(
            f"❌ Error obteniendo datos "
            f"{user_id}: {e}"
        )

        return

    if not datos:

        await update.message.reply_text(
            "🔒 No se pudieron obtener tus datos."
        )

        raise ApplicationHandlerStop

    if datos[5] == 0:

        await update.message.reply_text(
            "🔒 Sesión cerrada. Usa /reg."
        )

        raise ApplicationHandlerStop

    # --------------------------------------------------------
    # Comprobar país
    # --------------------------------------------------------

    try:

        tiene_pais = usuario_tiene_pais(
            user_id
        )

    except Exception as e:

        print(
            f"❌ Error comprobando país "
            f"{user_id}: {e}"
        )

        return

    if not tiene_pais:

        await update.message.reply_text(
            "🌎 *Debes configurar tu país*\n\n"
            "Usa: `/setpais pais`\n\n"
            "Ejemplo: `/setpais cuba`\n\n"
            "📋 *Países disponibles:*\n"
            + lista_paises_texto(),
            parse_mode="Markdown",
        )

        raise ApplicationHandlerStop

    # --------------------------------------------------------
    # Registrar comando utilizado
    # --------------------------------------------------------

    try:

        from core.logros import (
            obtener_stats,
            actualizar_stat,
        )

        stats_usuario = obtener_stats(
            user_id
        )

        comandos_usados = (
            stats_usuario[10]
            if stats_usuario[10]
            else ""
        )

        usados = [
            x.strip()
            for x in comandos_usados.split(",")
            if x.strip()
        ]

        if comando not in usados:

            if comandos_usados:

                nuevos = (
                    comandos_usados
                    + ","
                    + comando
                )

            else:

                nuevos = comando

            actualizar_stat(
                user_id,
                "comandos_usados",
                valor=nuevos,
            )

            total_distintos = len(
                set(
                    nuevos.split(",")
                )
            )

            if total_distintos >= 15:

                try:

                    if dar_logro(
                        user_id,
                        "curioso",
                    ):

                        await avisar_logro(
                            context,
                            user_id,
                            "curioso",
                        )

                except Exception as e:

                    print(
                        f"⚠️ Error dando logro "
                        f"a {user_id}: {e}"
                    )

    except Exception as e:

        print(
            f"⚠️ Error registrando comando "
            f"{comando} de {user_id}: {e}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("🚀 Iniciando ReidiStudiosBot...")

    # ========================================================
    # INICIALIZAR BASES DE DATOS
    # ========================================================

    init_db()

    init_sesiones_db()

    init_banco_db()

    init_juegos_db()

    init_apuestas_db()

    init_mates_db()

    init_dados_db()

    init_memoria_db()

    init_trivia_db()

    init_palabras_db()

    init_funks_db()

    init_eventos_db()

    init_reclamar_db()

    init_logros_db()

    init_amigos_db()

    init_misiones_db()

    print("✅ Bases de datos inicializadas")

    # ========================================================
    # CREAR APLICACIÓN
    # ========================================================

    if not TOKEN:

        raise RuntimeError(
            "❌ No existe BOT_TOKEN en las variables de entorno."
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # ========================================================
    # JOB QUEUE
    # ========================================================

    if app.job_queue is None:

        print(
            "⚠️ ADVERTENCIA: job_queue es None.\n"
            "Revisa requirements.txt y asegúrate de tener:\n"
            "python-telegram-bot[job-queue]"
        )

    else:

        # ----------------------------------------------------
        # APUESTAS EXPIRADAS
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_expiradas,
            interval=30,
            first=10,
        )

        # ----------------------------------------------------
        # MATES
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_timeouts_mates,
            interval=10,
            first=10,
        )

        # ----------------------------------------------------
        # MEMORIA
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_timeouts_memoria,
            interval=10,
            first=10,
        )

        # ----------------------------------------------------
        # TRIVIA
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_timeouts_trivia,
            interval=10,
            first=10,
        )

        # ----------------------------------------------------
        # PALABRAS
        # ----------------------------------------------------
        #
        # IMPORTANTE:
        # usamos revisar_timeouts_palabras
        # porque así se llama realmente en palabras.py.
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_timeouts_palabras,
            interval=10,
            first=10,
        )

        # ----------------------------------------------------
        # FUNKS
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_timeouts_funks,
            interval=10,
            first=10,
        )

        # ----------------------------------------------------
        # EVENTOS EXPIRADOS
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_eventos_expirados,
            interval=60,
            first=30,
        )

        # ----------------------------------------------------
        # EVENTOS INICIANDO
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_eventos_iniciando,
            interval=30,
            first=15,
        )

        # ----------------------------------------------------
        # DESCLASIFICADOS
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_descalificados,
            interval=30,
            first=30,
        )

        # ----------------------------------------------------
        # INVITACIONES EXPIRADAS
        # ----------------------------------------------------

        app.job_queue.run_repeating(
            revisar_invitaciones_expiradas,
            interval=30,
            first=30,
        )

        print(
            "✅ JobQueue configurado con 10 tareas programadas"
        )

    # ========================================================
    # HANDLER: ACTIVIDAD
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.ALL,
            rastrear_actividad,
        ),
        group=-100,
    )

    # ========================================================
    # HANDLER: BLOQUEO DE PARTIDAS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.ALL,
            bloquear_comandos_en_partida,
        ),
        group=-10,
    )

    # ========================================================
    # CONFIRMACIONES
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[sS][iI]$|^\.[sS][íÍ]$|^\.[nN][oO]$"
            ),
            confirmar_accion,
        ),
        group=-5,
    )

    # ========================================================
    # EVENTOS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[cC][oO][mM][eE][nN][zZ][aA][rR]$"
            ),
            comenzar,
        ),
        group=-4,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[cC][aA][nN][cC][eE][lL][aA][rR]$"
            ),
            cancelar_evento,
        ),
        group=-4,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[aA][sS][iI][sS][tT][iI][rR]$"
            ),
            asistir,
        ),
        group=-3,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[aA][tT][rR][aA][sS]$"
            ),
            atras,
        ),
        group=-3,
    )

    # ========================================================
    # VERIFICAR REGISTRO
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.COMMAND,
            verificar_registro,
        ),
        group=0,
    )

    # ========================================================
    # RESPUESTAS DE JUEGOS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_mates,
        ),
        group=5,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_memoria,
        ),
        group=6,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_trivia,
        ),
        group=7,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_palabras,
        ),
        group=8,
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_funks,
        ),
        group=9,
    )

    # ========================================================
    # EVENTOS CON PUNTO
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            ver_evento,
        ),
        group=100,
    )

    # ========================================================
    # START / HELP
    # ========================================================

    app.add_handler(
        CommandHandler(
            "start",
            start,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command,
        ),
        group=10,
    )

    # ========================================================
    # BOTONES HELP
    # ========================================================

    app.add_handler(
        CallbackQueryHandler(
            help_botones,
            pattern=r"^help_",
        ),
        group=10,
    )

    # ========================================================
    # INVITACIONES
    # ========================================================

    app.add_handler(
        CallbackQueryHandler(
            responder_invitacion,
            pattern=r"^inv_",
        ),
        group=10,
    )

    # ========================================================
    # REGISTRO
    # ========================================================

    app.add_handler(
        CommandHandler(
            "tutorial",
            tutorial,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "reg",
            reg,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "unreg",
            unreg,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "deletereg",
            deletereg,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "setpais",
            setpais,
        ),
        group=10,
    )

    # ========================================================
    # PERFIL
    # ========================================================

    app.add_handler(
        CommandHandler(
            "perfil",
            perfil,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "tokens",
            tokens_cmd,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "nivel",
            nivel_cmd,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "rango",
            rango_cmd,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "userslist",
            userslist,
        ),
        group=10,
    )

    # ========================================================
    # JUEGOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "actividades",
            actividades,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "juegos",
            actividades,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "ruleta",
            ruleta,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "apostar",
            apostar,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "cancelar",
            cancelar,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "mates",
            mates,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "dados",
            dados,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "memoria",
            memoria,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "trivia",
            trivia,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "palabras",
            palabras,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "funks",
            funks,
        ),
        group=10,
    )

    # ========================================================
    # BANCO
    # ========================================================

    app.add_handler(
        CommandHandler(
            "bank",
            bank,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "depositar",
            depositar,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "retirar",
            retirar,
        ),
        group=10,
    )

    # ========================================================
    # RECLAMAR
    # ========================================================

    app.add_handler(
        CommandHandler(
            "reclamar",
            reclamar,
        ),
        group=10,
    )

    # ========================================================
    # EVENTOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "eventos",
            eventos,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "addevent",
            addevent,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "removeevent",
            removeevent,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "editevent",
            editevent,
        ),
        group=10,
    )

    # ========================================================
    # ADMIN
    # ========================================================

    app.add_handler(
        CommandHandler(
            "anunciar",
            anunciar,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "giveTokens",
            giveTokens,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "giveXP",
            giveXP,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "removeTokens",
            removeTokens,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "removeXP",
            removeXP,
        ),
        group=10,
    )

    # ========================================================
    # CHAT
    # ========================================================

    app.add_handler(
        CommandHandler(
            "chatm",
            chatm,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "msp",
            msp,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "darTokens",
            darTokens,
        ),
        group=10,
    )

    # ========================================================
    # TOP
    # ========================================================

    app.add_handler(
        CommandHandler(
            "top",
            top,
        ),
        group=10,
    )

    # ========================================================
    # STATS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "stats",
            stats,
        ),
        group=10,
    )

    # ========================================================
    # SUGERENCIAS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "sugerencia",
            sugerencia,
        ),
        group=10,
    )

    # ========================================================
    # VERSION
    # ========================================================

    app.add_handler(
        CommandHandler(
            "version",
            version,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "setversion",
            setversion,
        ),
        group=10,
    )

    # ========================================================
    # LOGROS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "logros",
            logros,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "reclamarlogros",
            reclamarlogros,
        ),
        group=10,
    )

    # ========================================================
    # AMIGOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "amigo",
            amigo,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "amigos",
            amigos,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "solicitudes",
            solicitudes,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "invitar",
            invitar,
        ),
        group=10,
    )

    # ========================================================
    # TOP AMIGOS
    # ========================================================
    #
    # Se registran las dos variantes:
    #
    # /top_amigos
    # /topamigos
    #
    # Así no perdemos la función aunque el nombre mostrado
    # en /help use una de las dos.
    # ========================================================

    app.add_handler(
        CommandHandler(
            "top_amigos",
            top_amigos,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "topamigos",
            top_amigos,
        ),
        group=10,
    )

    # ========================================================
    # MISIONES
    # ========================================================

    app.add_handler(
        CommandHandler(
            "misiones",
            misiones,
        ),
        group=10,
    )

    # ========================================================
    # INICIAR
    # ========================================================

    print("🤖 Bot corriendo...")
    print("✅ Todos los handlers registrados")
    print("✅ Top registrado")
    print("✅ Amigos registrados")
    print("✅ Top de amigos registrado")
    print("✅ Misiones registradas")
    print("✅ Sugerencias registradas")
    print("✅ Timeouts de juegos registrados")
    print("🚀 Iniciando polling...")

    app.run_polling()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()

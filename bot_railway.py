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
    CallbackQueryHandler
)

from core.db import (
    init_db,
    esta_registrado,
    obtener_datos,
    usuario_tiene_pais,
    actualizar_ultima_actividad
)

from core.sesiones import (
    init_sesiones_db,
    obtener_juego
)

from core.paises import lista_paises_texto

from core.logros import (
    init_logros_db,
    LOGROS,
    logros_de_usuario,
    dar_logro
)

from core.amigos import init_amigos_db
from core.misiones import init_misiones_db

from comandos.registro import (
    reg,
    unreg,
    deletereg,
    confirmar_accion,
    setpais
)

from comandos.perfil import (
    perfil,
    tokens_cmd,
    nivel_cmd,
    rango_cmd,
    userslist
)

from comandos.tutorial import tutorial

from comandos.chat import (
    chatm,
    msp,
    darTokens
)

from comandos.top import top
from comandos.stats import stats
from comandos.sugerencia import sugerencia
from comandos.help import help_command, help_botones
from comandos.version import version, setversion
from comandos.logros import logros
from comandos.reclamarlogros import reclamarlogros

from comandos.amigos import (
    amigo,
    amigos,
    solicitudes
)

from comandos.amigos_top import top_amigos

from comandos.amigos_invitar import (
    invitar,
    responder_invitacion,
    revisar_invitaciones_expiradas
)

from comandos.misiones import misiones

from admin import (
    anunciar,
    giveTokens,
    giveXP,
    removeTokens,
    removeXP
)

from banco.banco import (
    init_banco_db,
    bank,
    depositar,
    retirar
)

from juegos.menu import actividades
from juegos.ruleta import init_juegos_db, ruleta

from juegos.apuestas import (
    init_apuestas_db,
    apostar,
    cancelar,
    revisar_expiradas
)

from juegos.mates import (
    init_mates_db,
    mates,
    responder as responder_mates,
    revisar_timeouts as revisar_timeouts_mates
)

from juegos.dados import (
    init_dados_db,
    dados
)

from juegos.memoria import (
    init_memoria_db,
    memoria,
    responder_memoria,
    revisar_timeouts_memoria
)

from juegos.palabras import (
    init_palabras_db,
    palabras,
    responder_palabras,
    revisar_timeouts as revisar_timeouts_palabras
)

from juegos.funks import (
    init_funks_db,
    funks,
    responder_funks,
    revisar_timeouts as revisar_timeouts_funks
)

from juegos.trivia import (
    init_trivia_db,
    trivia,
    responder_trivia,
    revisar_timeouts as revisar_timeouts_trivia
)

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
    revisar_descalificados
)

from eventos.reclamar import (
    init_reclamar_db,
    reclamar
)


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
    "/misiones"
]

COMANDOS_VALIDOS_LOWER = [
    c.lower() for c in COMANDOS_VALIDOS
]


# ============================================================
# COMANDOS QUE SÍ SE PUEDEN USAR DURANTE UNA PARTIDA
# ============================================================

COMANDOS_PERMITIDOS_EN_PARTIDA = {
    "/start",
    "/cancelar",

    # Información / perfil
    "/help",
    "/perfil",
    "/tokens",
    "/nivel",
    "/rango",
    "/stats",
    "/top",

    # Logros
    "/logros",
    "/reclamarlogros",

    # Amigos
    "/amigo",
    "/amigos",
    "/solicitudes",
    "/invitar",

    # Misiones
    "/misiones",

    # Otros comandos que no inician juegos
    "/sugerencia",
    "/version"
}


# ============================================================
# AVISAR LOGRO
# ============================================================

async def avisar_logro(
    context: ContextTypes.DEFAULT_TYPE,
    user_id,
    clave
):
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


# ============================================================
# AVISAR MISIÓN
# ============================================================

async def avisar_mision(
    context: ContextTypes.DEFAULT_TYPE,
    user_id,
    m_id
):
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


# ============================================================
# RASTREAR ACTIVIDAD
# ============================================================

async def rastrear_actividad(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    if update.effective_user:

        try:
            actualizar_ultima_actividad(
                update.effective_user.id
            )

        except Exception:
            pass


# ============================================================
# BLOQUEAR COMANDOS DURANTE PARTIDA
# ============================================================

async def bloquear_comandos_en_partida(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not update.message:
        return

    if not update.message.text:
        return

    user_id = update.effective_user.id

    juego = obtener_juego(user_id)

    # No hay partida activa
    if juego is None:
        return

    texto = update.message.text.strip()

    # ========================================================
    # LOS MENSAJES NORMALES NO SE BLOQUEAN
    # Esto permite:
    #
    # .mente ma
    # .palabra
    # .respuesta
    # etc.
    # ========================================================

    if not texto.startswith("/"):
        return

    # ========================================================
    # SACAR EL COMANDO
    #
    # /top
    # /top@ReidiStudiosBot
    # /amigos
    # /amigo Juan
    #
    # Todos se convierten a:
    #
    # /top
    # /amigos
    # /amigo
    # ========================================================

    comando = texto.split()[0].split("@")[0].lower()

    # ========================================================
    # COMANDOS PERMITIDOS DURANTE PARTIDA
    # ========================================================

    if comando in COMANDOS_PERMITIDOS_EN_PARTIDA:
        return

    # ========================================================
    # CUALQUIER OTRO COMANDO SE BLOQUEA
    # ========================================================

    await update.message.reply_text(
        f"⚠️ Estás en una partida de *{juego}*.\n\n"
        f"Termínala primero para usar este comando.\n\n"
        f"Puedes usar `/top`, `/amigos`, `/misiones`, "
        f"`/sugerencia` y otros comandos informativos.",
        parse_mode="Markdown"
    )

    raise ApplicationHandlerStop


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    await update.message.reply_text(
        "¡Hola! Soy ReidiStudiosBot.\n\n"
        "Regístrate con:\n"
        "/reg nombre.pais\n\n"
        "Ejemplo:\n"
        "/reg Juan.cuba\n\n"
        "Usa /help para ver todos los comandos."
    )


# ============================================================
# VERIFICAR REGISTRO
# ============================================================

async def verificar_registro(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not update.message:
        return

    if not update.message.text:
        return

    texto = update.message.text.strip()

    if not texto.startswith("/"):
        return

    comando = texto.split()[0].split("@")[0].lower()

    # ========================================================
    # COMANDO NO RECONOCIDO
    # ========================================================

    if comando not in COMANDOS_VALIDOS_LOWER:

        await update.message.reply_text(
            f"❌ Comando no reconocido: `{comando}`\n\n"
            f"Usa /help.",
            parse_mode="Markdown"
        )

        raise ApplicationHandlerStop

    # ========================================================
    # COMANDOS LIBRES
    # ========================================================

    comandos_libres = [
        "/start",
        "/help",
        "/reg",
        "/unreg",
        "/deletereg",
        "/tutorial",
        "/setpais",
        "/version"
    ]

    if comando in comandos_libres:
        return

    user_id = update.effective_user.id

    # ========================================================
    # VERIFICAR REGISTRO
    # ========================================================

    if not esta_registrado(user_id):

        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\n"
            "Usa:\n"
            "/reg nombre.pais"
        )

        raise ApplicationHandlerStop

    # ========================================================
    # VERIFICAR SESIÓN
    # ========================================================

    datos = obtener_datos(user_id)

    if datos[5] == 0:

        await update.message.reply_text(
            "🔒 Sesión cerrada.\n\n"
            "Usa /reg."
        )

        raise ApplicationHandlerStop

    # ========================================================
    # VERIFICAR PAÍS
    # ========================================================

    if not usuario_tiene_pais(user_id):

        await update.message.reply_text(
            "🌎 *Debes configurar tu país*\n\n"
            "Usa:\n"
            "`/setpais pais`\n\n"
            "Ejemplo:\n"
            "`/setpais cuba`\n\n"
            "📋 *Países disponibles:*\n"
            + lista_paises_texto(),
            parse_mode="Markdown"
        )

        raise ApplicationHandlerStop

    # ========================================================
    # REGISTRAR COMANDO USADO PARA LOGRO
    # ========================================================

    from core.logros import (
        obtener_stats,
        actualizar_stat
    )

    stats_usuario = obtener_stats(user_id)

    comandos_usados = (
        stats_usuario[10]
        if stats_usuario[10]
        else ""
    )

    if comando not in comandos_usados.split(","):

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
            valor=nuevos
        )

        total_distintos = len(
            set(nuevos.split(","))
        )

        if total_distintos >= 15:

            if dar_logro(
                user_id,
                "curioso"
            ):

                await avisar_logro(
                    context,
                    user_id,
                    "curioso"
                )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # BASES DE DATOS
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

    # ========================================================
    # BOT
    # ========================================================

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
            "⚠️ ADVERTENCIA: job_queue es None. "
            "Revisa requirements.txt tenga "
            "[job-queue]"
        )

    else:

        app.job_queue.run_repeating(
            revisar_expiradas,
            interval=30,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_timeouts_mates,
            interval=10,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_timeouts_memoria,
            interval=10,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_timeouts_trivia,
            interval=10,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_timeouts_palabras,
            interval=10,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_timeouts_funks,
            interval=10,
            first=10
        )

        app.job_queue.run_repeating(
            revisar_eventos_expirados,
            interval=60,
            first=30
        )

        app.job_queue.run_repeating(
            revisar_eventos_iniciando,
            interval=30,
            first=15
        )

        app.job_queue.run_repeating(
            revisar_descalificados,
            interval=30,
            first=30
        )

        app.job_queue.run_repeating(
            revisar_invitaciones_expiradas,
            interval=30,
            first=30
        )

        print(
            "✅ JobQueue configurado "
            "con 10 tareas programadas"
        )

    # ========================================================
    # ACTIVIDAD
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.ALL,
            rastrear_actividad
        ),
        group=-100
    )

    # ========================================================
    # BLOQUEO DE PARTIDAS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.ALL,
            bloquear_comandos_en_partida
        ),
        group=-10
    )

    # ========================================================
    # CONFIRMACIONES
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[sS][iI]$|^\.[sS][íÍ]$|^\.[nN][oO]$"
            ),
            confirmar_accion
        ),
        group=-5
    )

    # ========================================================
    # EVENTOS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[cC][oO][mM][eE][nN][zZ][aA][rR]$"
            ),
            comenzar
        ),
        group=-4
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[cC][aA][nN][cC][eE][lL][aA][rR]$"
            ),
            cancelar_evento
        ),
        group=-4
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[aA][sS][iI][sS][tT][iI][rR]$"
            ),
            asistir
        ),
        group=-3
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^\.[aA][tT][rR][aA][sS]$"
            ),
            atras
        ),
        group=-3
    )

    # ========================================================
    # VERIFICACIÓN DE REGISTRO
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.COMMAND,
            verificar_registro
        ),
        group=0
    )

    # ========================================================
    # RESPUESTAS DE JUEGOS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_mates
        ),
        group=5
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_memoria
        ),
        group=6
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_trivia
        ),
        group=7
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_palabras
        ),
        group=8
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            responder_funks
        ),
        group=9
    )

    # ========================================================
    # EVENTOS
    # ========================================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            ver_evento
        ),
        group=100
    )

    # ========================================================
    # COMANDOS BÁSICOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        ),
        group=10
    )

    app.add_handler(
        CallbackQueryHandler(
            help_botones,
            pattern=r"^help_"
        ),
        group=10
    )

    app.add_handler(
        CallbackQueryHandler(
            responder_invitacion,
            pattern=r"^inv_"
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "tutorial",
            tutorial
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "reg",
            reg
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "unreg",
            unreg
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "deletereg",
            deletereg
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "setpais",
            setpais
        ),
        group=10
    )

    # ========================================================
    # PERFIL
    # ========================================================

    app.add_handler(
        CommandHandler(
            "perfil",
            perfil
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "tokens",
            tokens_cmd
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "nivel",
            nivel_cmd
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "rango",
            rango_cmd
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "userslist",
            userslist
        ),
        group=10
    )

    # ========================================================
    # JUEGOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "actividades",
            actividades
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "juegos",
            actividades
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "ruleta",
            ruleta
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "apostar",
            apostar
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "cancelar",
            cancelar
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "mates",
            mates
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "dados",
            dados
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "memoria",
            memoria
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "trivia",
            trivia
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "palabras",
            palabras
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "funks",
            funks
        ),
        group=10
    )

    # ========================================================
    # BANCO
    # ========================================================

    app.add_handler(
        CommandHandler(
            "bank",
            bank
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "depositar",
            depositar
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "retirar",
            retirar
        ),
        group=10
    )

    # ========================================================
    # EVENTOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "reclamar",
            reclamar
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "eventos",
            eventos
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "addevent",
            addevent
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "removeevent",
            removeevent
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "editevent",
            editevent
        ),
        group=10
    )

    # ========================================================
    # ADMIN
    # ========================================================

    app.add_handler(
        CommandHandler(
            "anunciar",
            anunciar
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "giveTokens",
            giveTokens
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "giveXP",
            giveXP
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "removeTokens",
            removeTokens
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "removeXP",
            removeXP
        ),
        group=10
    )

    # ========================================================
    # CHAT
    # ========================================================

    app.add_handler(
        CommandHandler(
            "chatm",
            chatm
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "msp",
            msp
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "darTokens",
            darTokens
        ),
        group=10
    )

    # ========================================================
    # TOP / STATS / SUGERENCIAS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "top",
            top
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "stats",
            stats
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "sugerencia",
            sugerencia
        ),
        group=10
    )

    # ========================================================
    # VERSIÓN
    # ========================================================

    app.add_handler(
        CommandHandler(
            "version",
            version
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "setversion",
            setversion
        ),
        group=10
    )

    # ========================================================
    # LOGROS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "logros",
            logros
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "reclamarlogros",
            reclamarlogros
        ),
        group=10
    )

    # ========================================================
    # AMIGOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "amigo",
            amigo
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "amigos",
            amigos
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "solicitudes",
            solicitudes
        ),
        group=10
    )

    app.add_handler(
        CommandHandler(
            "invitar",
            invitar
        ),
        group=10
    )

    # ========================================================
    # TOP DE AMIGOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "top_amigos",
            top_amigos
        ),
        group=10
    )

    # ========================================================
    # MISIONES
    # ========================================================

    app.add_handler(
        CommandHandler(
            "misiones",
            misiones
        ),
        group=10
    )

    # ========================================================
    # ARRANCAR
    # ========================================================

    print("Bot corriendo...")

    app.run_polling()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()

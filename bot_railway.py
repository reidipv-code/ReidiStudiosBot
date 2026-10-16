import os
import logging

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ApplicationHandlerStop,
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# ============================================================
# BASE DE DATOS Y SISTEMAS PRINCIPALES
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

from core.paises import lista_paises_texto
from core.idiomas import init_idiomas_db, instalar_traduccion_automatica, idioma_seleccionado

from core.razas_clases import (
    init_razas_clases_db,
    personaje_completo,
)

from core.logros import (
    init_logros_db,
    LOGROS,
    logros_de_usuario,
    dar_logro,
)

from core.amigos import init_amigos_db
from core.misiones import init_misiones_db
from core.tienda import init_tienda_db

# ============================================================
# REGISTRO RPG Y PERFIL
# ============================================================

from comandos.registro_rpg import (
    start_rpg,
    reg_rpg,
    registro_rpg_callback,
    perfil_rpg,
)

# Se mantienen los comandos antiguos que siguen siendo
# utilizados por los sistemas existentes del bot.
from comandos.registro import (
    deletereg,
    confirmar_accion,
    setpais,
)

from comandos.perfil import (
    tokens_cmd,
    nivel_cmd,
    rango_cmd,
    userslist,
)

# ============================================================
# COMANDOS GENERALES
# ============================================================

from comandos.tutorial import tutorial
from comandos.lang import lang_command, lang_callback
from comandos.menu import menu_command, menu_callback
from comandos.chat import chatm, msp, darTokens
from comandos.top import top
from comandos.stats import stats
from comandos.sugerencia import sugerencia
from comandos.help import help_command, help_botones
from comandos.version import version, setversion

from comandos.logros import logros
from comandos.reclamarlogros import reclamarlogros

# ============================================================
# AMIGOS
# ============================================================

from comandos.amigos import (
    amigo,
    amigos,
    solicitudes,
)

from comandos.amigos_top import top_amigos

from comandos.amigos_invitar import (
    invitar,
    responder_invitacion,
    revisar_invitaciones_expiradas,
)

# ============================================================
# MISIONES Y TIENDA
# ============================================================

from comandos.misiones import misiones

from comandos.tienda import (
    tienda,
    tienda_botones,
)

# ============================================================
# ADMINISTRACIÓN
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

from juegos.menu import actividades

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

from juegos.mates import (
    init_mates_db,
    mates,
    responder as responder_mates,
    revisar_timeouts as revisar_timeouts_mates,
)

from juegos.dados import (
    init_dados_db,
    dados,
)

from juegos.memoria import (
    init_memoria_db,
    memoria,
    responder_memoria,
    revisar_timeouts_memoria,
)

from juegos.palabras import (
    init_palabras_db,
    palabras,
    responder_palabras,
    revisar_timeouts_palabras,
)

from juegos.funks import (
    init_funks_db,
    funks,
    responder_funks,
    revisar_timeouts_funks,
)

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
# COMANDOS RECONOCIDOS
# ============================================================

COMANDOS_VALIDOS = [
    "/start",
    "/lang",
    "/menu",
    "/help",
    "/reg",
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
    "/givetokens",
    "/givexp",
    "/removetokens",
    "/removexp",
    "/dados",
    "/memoria",
    "/trivia",
    "/palabras",
    "/funks",
    "/setpais",
    "/chatm",
    "/msp",
    "/dartokens",
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
    "/misiones",
    "/tienda",
]

COMANDOS_VALIDOS_LOWER = {
    comando.lower()
    for comando in COMANDOS_VALIDOS
}

# Estos comandos pueden utilizarse sin haber terminado
# el registro del personaje.
COMANDOS_LIBRES = {
    "/start",
    "/help",
    "/reg",
    "/lang",
    "/menu",
    "/anunciar",
}

# ============================================================
# NOTIFICACIONES DE LOGROS
# ============================================================


async def avisar_logro(context, user_id, clave):
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

    except Exception as error:
        logger.warning(
            "No se pudo enviar el logro a %s: %s",
            user_id,
            error,
        )


# ============================================================
# NOTIFICACIONES DE MISIONES
# ============================================================


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
            parse_mode="Markdown",
        )

    except Exception as error:
        logger.warning(
            "No se pudo notificar la misión a %s: %s",
            user_id,
            error,
        )


# ============================================================
# REGISTRAR ACTIVIDAD
# ============================================================


async def rastrear_actividad(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    usuario = update.effective_user

    if usuario:
        try:
            actualizar_ultima_actividad(usuario.id)

        except Exception as error:
            logger.debug(
                "No se pudo actualizar la actividad: %s",
                error,
            )


# ============================================================
# BLOQUEAR COMANDOS DURANTE LAS PARTIDAS
# ============================================================


async def bloquear_comandos_en_partida(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message or not update.message.text:
        return

    usuario = update.effective_user

    if not usuario:
        return

    user_id = usuario.id

    juego = obtener_juego(user_id)

    if juego is None:
        return

    texto = update.message.text.strip()

    if not texto.startswith("/"):
        return

    comando = (
        texto.split()[0]
        .split("@")[0]
        .lower()
    )

    # Se permite cancelar la partida o volver a iniciar
    # el bot mientras existe un juego activo.
    if comando in {"/start", "/cancelar"}:
        return

    await update.message.reply_text(
        f"⚠️ Estás en una partida de *{juego}*.\n"
        "Termínala primero para usar otros comandos.",
        parse_mode="Markdown",
    )

    raise ApplicationHandlerStop


# ============================================================
# VERIFICAR REGISTRO COMPLETO
# ============================================================


async def verificar_registro(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message or not update.message.text:
        return

    usuario = update.effective_user

    if not usuario:
        return

    texto = update.message.text.strip()

    if not texto.startswith("/"):
        return

    comando = (
        texto.split()[0]
        .split("@")[0]
        .lower()
    )

    # Rechazar comandos que el bot no reconoce.
    if comando not in COMANDOS_VALIDOS_LOWER:

        await update.message.reply_text(
            f"❌ Comando no reconocido: {comando}\n\n"
            "Usa /help para consultar los comandos disponibles."
        )

        raise ApplicationHandlerStop

    # /start, /help, /reg, /lang, /menu y /anunciar se gestionan
    # sin exigir un personaje completo.
    #
    # El propio comando /anunciar verifica que el usuario
    # sea administrador antes de realizar cualquier acción.
    if comando in COMANDOS_LIBRES:
        return

    user_id = usuario.id

    # El usuario debe haber completado los cuatro pasos:
    # nombre y país, raza y clase.
    if not personaje_completo(user_id):

        await update.message.reply_text(
            "🔒 Todavía no tienes un personaje completo.\n\n"
            "Para entrar al MMORPG debes completar los "
            "cuatro pasos del registro:\n\n"
            "1. Seleccionar idioma: /lang español (o /lang spanish).\n"
            "2. Nombre y país: /reg Nombre.Pais\n"
            "3. Elegir una raza.\n"
            "4. Elegir una clase compatible con esa raza.\n\n"
            "Ejemplo: /reg OriGamePlay.cuba"
        )

        raise ApplicationHandlerStop

    # Comprobar que los datos de la cuenta existan.
    datos = obtener_datos(user_id)

    if not datos:

        await update.message.reply_text(
            "❌ No se pudieron cargar los datos de tu cuenta. "
            "Contacta con un administrador."
        )

        raise ApplicationHandlerStop

    # Mantener el comportamiento anterior de las sesiones.
    if datos[5] == 0:

        await update.message.reply_text(
            "🔒 Tu sesión está cerrada.\n"
            "Usa /reg si necesitas revisar tu registro."
        )

        raise ApplicationHandlerStop

    # Mantener la comprobación de país del sistema anterior.
    # El país se usa exclusivamente para las zonas horarias
    # de los eventos, no para determinar raza o clase.
    if not usuario_tiene_pais(user_id):

        await update.message.reply_text(
            "🌎 Tu cuenta no tiene un país configurado.\n\n"
            "El país solo se utiliza para ajustar la zona "
            "horaria de los eventos.\n\n"
            "Países disponibles:\n"
            + lista_paises_texto()
        )

        raise ApplicationHandlerStop

    # ========================================================
    # LOGRO: CURIOSO
    # ========================================================

    try:
        from core.logros import (
            obtener_stats,
            actualizar_stat,
        )

        stats_usuario = obtener_stats(user_id)

        comandos_usados = (
            stats_usuario[10]
            if stats_usuario and stats_usuario[10]
            else ""
        )

        lista_comandos = [
            item
            for item in comandos_usados.split(",")
            if item
        ]

        if comando not in lista_comandos:

            lista_comandos.append(comando)

            nuevos = ",".join(lista_comandos)

            actualizar_stat(
                user_id,
                "comandos_usados",
                valor=nuevos,
            )

            if len(set(lista_comandos)) >= 15:

                if dar_logro(user_id, "curioso"):
                    await avisar_logro(
                        context,
                        user_id,
                        "curioso",
                    )

    except Exception as error:
        logger.warning(
            "Error comprobando el logro Curioso: %s",
            error,
        )


# ============================================================
# INICIALIZACIÓN
# ============================================================


def main() -> None:

    if not TOKEN:
        raise RuntimeError(
            "Falta la variable de entorno BOT_TOKEN."
        )

    # Inicializar todas las bases de datos antes de registrar
    # los handlers o empezar a recibir actualizaciones.
    init_db()
    init_idiomas_db()

    # IMPORTANTE:
    # Crea las tablas de personajes y registros pendientes.
    init_razas_clases_db()

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
    init_tienda_db()

    # Crear la aplicación.
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # Traducción automática de los textos enviados en chats privados.
    # Si el servicio externo falla, los mensajes siguen enviándose en español.
    instalar_traduccion_automatica(app.bot)

    # ========================================================
    # TAREAS PROGRAMADAS
    # ========================================================

    if app.job_queue is None:

        logger.warning(
            "JobQueue no disponible. "
            "Comprueba que requirements.txt incluya "
            "python-telegram-bot[job-queue]."
        )

    else:

        app.job_queue.run_repeating(
            revisar_expiradas,
            interval=30,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_timeouts_mates,
            interval=10,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_timeouts_memoria,
            interval=10,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_timeouts_trivia,
            interval=10,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_timeouts_palabras,
            interval=10,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_timeouts_funks,
            interval=10,
            first=10,
        )

        app.job_queue.run_repeating(
            revisar_eventos_expirados,
            interval=60,
            first=30,
        )

        app.job_queue.run_repeating(
            revisar_eventos_iniciando,
            interval=30,
            first=15,
        )

        app.job_queue.run_repeating(
            revisar_descalificados,
            interval=30,
            first=30,
        )

        app.job_queue.run_repeating(
            revisar_invitaciones_expiradas,
            interval=30,
            first=30,
        )

        logger.info(
            "JobQueue configurado con 10 tareas programadas."
        )

    # ========================================================
    # HANDLERS DE PRIORIDAD ALTA
    # ========================================================

    # Actualizar actividad antes de procesar los comandos.
    app.add_handler(
        MessageHandler(
            filters.ALL,
            rastrear_actividad,
        ),
        group=-100,
    )

    # Mantener el bloqueo de comandos durante los juegos.
    app.add_handler(
        MessageHandler(
            filters.ALL,
            bloquear_comandos_en_partida,
        ),
        group=-10,
    )

    # ========================================================
    # CONFIRMACIONES Y EVENTOS
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
    # VERIFICACIÓN GLOBAL DE COMANDOS
    # ========================================================

    # Se ejecuta antes que los CommandHandler del grupo 10.
    # ApplicationHandlerStop bloquea el comando si no cumple
    # los requisitos del registro.
    app.add_handler(
        MessageHandler(
            filters.COMMAND,
            verificar_registro,
        ),
        group=0,
    )

    # ========================================================
    # RESPUESTAS DE LOS JUEGOS
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

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^\."),
            ver_evento,
        ),
        group=100,
    )

    # ========================================================
    # IDIOMA Y MENÚ PRINCIPAL
    # ========================================================

    app.add_handler(CommandHandler("lang", lang_command), group=10)
    app.add_handler(CallbackQueryHandler(lang_callback, pattern=r"^lang:"), group=10)
    app.add_handler(CommandHandler("menu", menu_command), group=10)
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu_"), group=10)

    # ========================================================
    # REGISTRO RPG: START, REGISTRO Y PERFIL
    # ========================================================

    # /start explica los cuatro pasos y la función del país.
    app.add_handler(
        CommandHandler(
            "start",
            start_rpg,
        ),
        group=10,
    )

    # /reg Nombre.Pais inicia el proceso de registro.
    app.add_handler(
        CommandHandler(
            "reg",
            reg_rpg,
        ),
        group=10,
    )

    # Atiende los botones de selección de raza y clase.
    app.add_handler(
        CallbackQueryHandler(
            registro_rpg_callback,
            pattern=r"^rpg_",
        ),
        group=10,
    )

    # /perfil muestra el personaje propio o el de otro usuario.
    app.add_handler(
        CommandHandler(
            "perfil",
            perfil_rpg,
        ),
        group=10,
    )

    # ========================================================
    # COMANDOS GENERALES
    # ========================================================

    app.add_handler(
        CommandHandler(
            "help",
            help_command,
        ),
        group=10,
    )

    app.add_handler(
        CallbackQueryHandler(
            help_botones,
            pattern=r"^help_",
        ),
        group=10,
    )

    app.add_handler(
        CallbackQueryHandler(
            tienda_botones,
            pattern=r"^shop_",
        ),
        group=10,
    )

    app.add_handler(
        CallbackQueryHandler(
            responder_invitacion,
            pattern=r"^inv_",
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "tutorial",
            tutorial,
        ),
        group=10,
    )

    # ========================================================
    # COMANDOS DE CUENTA ANTIGUOS
    # ========================================================

    # Se conservan registrados para compatibilidad con los
    # módulos antiguos. La verificación global se ejecuta antes.
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
    # ACTIVIDADES Y JUEGOS
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
    # EVENTOS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "reclamar",
            reclamar,
        ),
        group=10,
    )

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
    # ADMINISTRACIÓN
    # ========================================================

    # /anunciar puede superar la comprobación de registro.
    # La función anunciar comprueba por sí misma los permisos.
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
    # CHAT Y ECONOMÍA
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

    app.add_handler(
        CommandHandler(
            "top",
            top,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "stats",
            stats,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "sugerencia",
            sugerencia,
        ),
        group=10,
    )

    # ========================================================
    # VERSIÓN
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
    # MISIONES Y TIENDA
    # ========================================================

    app.add_handler(
        CommandHandler(
            "misiones",
            misiones,
        ),
        group=10,
    )

    app.add_handler(
        CommandHandler(
            "tienda",
            tienda,
        ),
        group=10,
    )

    # ========================================================
    # INICIAR BOT
    # ========================================================

    logger.info("ReidiStudiosBot está iniciando...")

    app.run_polling()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()
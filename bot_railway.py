import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler,
    filters, ApplicationHandlerStop, CallbackQueryHandler
)

from core.db import (
    init_db, esta_registrado, obtener_datos, usuario_tiene_pais,
    actualizar_ultima_actividad
)
from core.sesiones import init_sesiones_db, obtener_juego
from core.paises import lista_paises_texto
from core.logros import init_logros_db, LOGROS, logros_de_usuario, dar_logro

from comandos.registro import reg, unreg, deletereg, confirmar_accion, setpais
from comandos.perfil import perfil, tokens_cmd, nivel_cmd, rango_cmd, userslist
from comandos.tutorial import tutorial
from comandos.chat import chatm, msp, darTokens
from comandos.top import top
from comandos.stats import stats
from comandos.sugerencia import sugerencia
from comandos.help import help_command, help_botones
from comandos.version import version, setversion
from comandos.logros import logros
from comandos.reclamarlogros import reclamarlogros

from admin import anunciar, giveTokens, giveXP, removeTokens, removeXP

from banco.banco import init_banco_db, bank, depositar, retirar

from juegos.menu import actividades
from juegos.ruleta import init_juegos_db, ruleta
from juegos.apuestas import init_apuestas_db, apostar, cancelar, revisar_expiradas
from juegos.mates import (
    init_mates_db, mates, responder as responder_mates,
    revisar_timeouts as revisar_timeouts_mates
)
from juegos.dados import init_dados_db, dados
from juegos.memoria import init_memoria_db, memoria, responder_memoria, revisar_timeouts_memoria
from juegos.palabras import init_palabras_db, palabras, responder_palabras, revisar_timeouts_palabras
from juegos.funks import init_funks_db, funks, responder_funks, revisar_timeouts_funks
from juegos.trivia import init_trivia_db, trivia, responder_trivia, revisar_timeouts_trivia

from eventos.eventos import (
    init_eventos_db, eventos, ver_evento, asistir, atras,
    comenzar, cancelar_evento, addevent, removeevent, editevent,
    revisar_eventos_expirados, revisar_eventos_iniciando, revisar_descalificados
)
from eventos.reclamar import init_reclamar_db, reclamar

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

COMANDOS_VALIDOS = [
    "/start", "/help", "/reg", "/unreg", "/deletereg",
    "/perfil", "/tokens", "/nivel", "/rango",
    "/actividades", "/juegos", "/ruleta", "/apostar", "/cancelar",
    "/userslist", "/mates", "/tutorial",
    "/bank", "/depositar", "/retirar", "/anunciar", "/reclamar",
    "/eventos", "/addevent", "/removeevent", "/editevent",
    "/giveTokens", "/giveXP", "/removeTokens", "/removeXP",
    "/dados", "/memoria", "/trivia", "/palabras", "/funks",
    "/setpais", "/chatm", "/msp", "/darTokens", "/top", "/stats",
    "/sugerencia", "/version", "/setversion", "/logros",
    "/reclamarlogros"
]

COMANDOS_VALIDOS_LOWER = [c.lower() for c in COMANDOS_VALIDOS]


async def avisar_logro(context, user_id, clave):
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


async def rastrear_actividad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        try:
            actualizar_ultima_actividad(update.effective_user.id)
        except Exception:
            pass


async def bloquear_comandos_en_partida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    juego = obtener_juego(user_id)

    if juego is None:
        return

    texto = update.message.text.strip()

    if texto.startswith("/"):
        if texto.startswith("/start") or texto.startswith("/cancelar"):
            return
        await update.message.reply_text(
            f"⚠️ Estás en una partida de *{juego}*.\n"
            f"Termínala primero para usar otros comandos.",
            parse_mode="Markdown"
        )
        raise ApplicationHandlerStop

    return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Soy ReidiStudiosBot.\n\n"
        "Regístrate con:\n/reg nombre.pais\n\n"
        "Ejemplo: /reg Juan.cuba\n\n"
        "Usa /help para ver todos los comandos."
    )


async def verificar_registro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    texto = update.message.text.strip()
    if not texto.startswith("/"):
        return

    comando = texto.split()[0].split("@")[0].lower()
    comandos_libres = ["/start", "/help", "/reg", "/unreg", "/deletereg", "/tutorial", "/setpais", "/version"]

    if comando not in COMANDOS_VALIDOS_LOWER:
        await update.message.reply_text(
            f"❌ Comando no reconocido: `{comando}`\n\nUsa /help.",
            parse_mode="Markdown"
        )
        raise ApplicationHandlerStop

    if comando in comandos_libres:
        return

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais")
        raise ApplicationHandlerStop

    datos = obtener_datos(user_id)
    if datos[5] == 0:
        await update.message.reply_text("🔒 Sesión cerrada. Usa /reg.")
        raise ApplicationHandlerStop

    if not usuario_tiene_pais(user_id):
        await update.message.reply_text(
            "🌎 *Debes configurar tu país*\n\n"
            "Usa: `/setpais pais`\n\n"
            "Ejemplo: `/setpais cuba`\n\n"
            "📋 *Países disponibles:*\n" + lista_paises_texto(),
            parse_mode="Markdown"
        )
        raise ApplicationHandlerStop

    # ─── Logro: Curioso (15 comandos distintos) ────────────
    from core.logros import obtener_stats, actualizar_stat
    stats = obtener_stats(user_id)
    comandos_usados = stats[10] if stats[10] else ""

    if comando not in comandos_usados.split(","):
        if comandos_usados:
            nuevos = comandos_usados + "," + comando
        else:
            nuevos = comando

        actualizar_stat(user_id, "comandos_usados", valor=nuevos)
        total_distintos = len(set(nuevos.split(",")))

        if total_distintos >= 15:
            if dar_logro(user_id, "curioso"):
                await avisar_logro(context, user_id, "curioso")


def main() -> None:
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

    app = Application.builder().token(TOKEN).build()

    if app.job_queue is None:
        print("⚠️ ADVERTENCIA: job_queue es None. Revisa requirements.txt tenga [job-queue]")
    else:
        app.job_queue.run_repeating(revisar_expiradas, interval=30, first=10)
        app.job_queue.run_repeating(revisar_timeouts_mates, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_memoria, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_trivia, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_palabras, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_funks, interval=10, first=10)
        app.job_queue.run_repeating(revisar_eventos_expirados, interval=60, first=30)
        app.job_queue.run_repeating(revisar_eventos_iniciando, interval=30, first=15)
        app.job_queue.run_repeating(revisar_descalificados, interval=30, first=30)
        print("✅ JobQueue configurado con 9 tareas programadas")

    app.add_handler(
        MessageHandler(filters.ALL, rastrear_actividad),
        group=-100
    )

    app.add_handler(
        MessageHandler(filters.ALL, bloquear_comandos_en_partida),
        group=-10
    )

    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[sS][iI]$|^\.[sS][íÍ]$|^\.[nN][oO]$"), confirmar_accion),
        group=-5
    )

    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[cC][oO][mM][eE][nN][zZ][aA][rR]$"), comenzar),
        group=-4
    )
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[cC][aA][nN][cC][eE][lL][aA][rR]$"), cancelar_evento),
        group=-4
    )

    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[aA][sS][iI][sS][tT][iI][rR]$"), asistir),
        group=-3
    )
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[aA][tT][rR][aA][sS]$"), atras),
        group=-3
    )

    app.add_handler(MessageHandler(filters.COMMAND, verificar_registro), group=0)

    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_mates), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_memoria), group=6)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_trivia), group=7)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_palabras), group=8)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_funks), group=9)

    app.add_handler(MessageHandler(filters.Regex(r"^\."), ver_evento), group=100)

    app.add_handler(CommandHandler("start", start), group=10)
    app.add_handler(CommandHandler("help", help_command), group=10)
    app.add_handler(CallbackQueryHandler(help_botones, pattern=r"^help_"), group=10)
    app.add_handler(CommandHandler("tutorial", tutorial), group=10)
    app.add_handler(CommandHandler("reg", reg), group=10)
    app.add_handler(CommandHandler("unreg", unreg), group=10)
    app.add_handler(CommandHandler("deletereg", deletereg), group=10)
    app.add_handler(CommandHandler("setpais", setpais), group=10)
    app.add_handler(CommandHandler("perfil", perfil), group=10)
    app.add_handler(CommandHandler("tokens", tokens_cmd), group=10)
    app.add_handler(CommandHandler("nivel", nivel_cmd), group=10)
    app.add_handler(CommandHandler("rango", rango_cmd), group=10)
    app.add_handler(CommandHandler("userslist", userslist), group=10)

    app.add_handler(CommandHandler("actividades", actividades), group=10)
    app.add_handler(CommandHandler("juegos", actividades), group=10)
    app.add_handler(CommandHandler("ruleta", ruleta), group=10)
    app.add_handler(CommandHandler("apostar", apostar), group=10)
    app.add_handler(CommandHandler("cancelar", cancelar), group=10)
    app.add_handler(CommandHandler("mates", mates), group=10)
    app.add_handler(CommandHandler("dados", dados), group=10)
    app.add_handler(CommandHandler("memoria", memoria), group=10)
    app.add_handler(CommandHandler("trivia", trivia), group=10)
    app.add_handler(CommandHandler("palabras", palabras), group=10)
    app.add_handler(CommandHandler("funks", funks), group=10)

    app.add_handler(CommandHandler("bank", bank), group=10)
    app.add_handler(CommandHandler("depositar", depositar), group=10)
    app.add_handler(CommandHandler("retirar", retirar), group=10)

    app.add_handler(CommandHandler("reclamar", reclamar), group=10)
    app.add_handler(CommandHandler("eventos", eventos), group=10)
    app.add_handler(CommandHandler("addevent", addevent), group=10)
    app.add_handler(CommandHandler("removeevent", removeevent), group=10)
    app.add_handler(CommandHandler("editevent", editevent), group=10)

    app.add_handler(CommandHandler("anunciar", anunciar), group=10)
    app.add_handler(CommandHandler("giveTokens", giveTokens), group=10)
    app.add_handler(CommandHandler("giveXP", giveXP), group=10)
    app.add_handler(CommandHandler("removeTokens", removeTokens), group=10)
    app.add_handler(CommandHandler("removeXP", removeXP), group=10)

    app.add_handler(CommandHandler("chatm", chatm), group=10)
    app.add_handler(CommandHandler("msp", msp), group=10)
    app.add_handler(CommandHandler("darTokens", darTokens), group=10)
    app.add_handler(CommandHandler("top", top), group=10)
    app.add_handler(CommandHandler("stats", stats), group=10)
    app.add_handler(CommandHandler("sugerencia", sugerencia), group=10)
    app.add_handler(CommandHandler("version", version), group=10)
    app.add_handler(CommandHandler("setversion", setversion), group=10)
    app.add_handler(CommandHandler("logros", logros), group=10)
    app.add_handler(CommandHandler("reclamarlogros", reclamarlogros), group=10)

    print("Bot corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()

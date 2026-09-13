import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler,
    filters, ApplicationHandlerStop
)
from telegram.request import HTTPXRequest

from core.db import init_db, esta_registrado, obtener_datos
from core.sesiones import init_sesiones_db, obtener_juego

from comandos.registro import reg, unreg, deletereg, confirmar_accion
from comandos.perfil import perfil, tokens_cmd, nivel_cmd, rango_cmd, userslist
from comandos.tutorial import tutorial

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
TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXY_URL = "http://127.0.0.1:8888"

COMANDOS_VALIDOS = [
    "/start", "/help", "/reg", "/unreg", "/deletereg",
    "/perfil", "/tokens", "/nivel", "/rango",
    "/actividades", "/juegos", "/ruleta", "/apostar", "/cancelar",
    "/userslist", "/mates", "/tutorial",
    "/bank", "/depositar", "/retirar", "/anunciar", "/reclamar",
    "/eventos", "/addevent", "/removeevent", "/editevent",
    "/giveTokens", "/giveXP", "/removeTokens", "/removeXP",
    "/dados", "/memoria", "/trivia", "/palabras", "/funks"
]

# Lista en minúsculas para comparación rápida
COMANDOS_VALIDOS_LOWER = [c.lower() for c in COMANDOS_VALIDOS]


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
        "Regístrate con:\n/reg tu_nombre\n\n"
        "Comandos:\n"
        "/start - Iniciar\n"
        "/help - Ayuda\n"
        "/reg nombre - Registrarte\n"
        "/perfil - Ver tu perfil\n"
        "/bank - Ver tu banco\n"
        "/reclamar - Recompensa diaria\n"
        "/eventos - Ver eventos\n"
        "/actividades - Menú de juegos\n"
        "/tutorial - Guía completa"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 *Comandos básicos:*\n"
        "/start\n/help\n/reg\n/unreg\n/deletereg\n/perfil\n"
        "/tokens\n/nivel\n/rango\n/userslist\n/bank\n/depositar\n/retirar\n"
        "/reclamar\n/eventos\n/tutorial\n\n"
        "🎮 Juegos: /actividades",
        parse_mode="Markdown"
    )


async def verificar_registro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    texto = update.message.text.strip()
    if not texto.startswith("/"):
        return

    comando = texto.split()[0].split("@")[0].lower()
    comandos_libres = ["/start", "/help", "/reg", "/unreg", "/deletereg", "/tutorial"]

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
        await update.message.reply_text("🔒 Debes registrarte primero.\n\nUsa: /reg tu_nombre")
        raise ApplicationHandlerStop

    datos = obtener_datos(user_id)
    if datos[5] == 0:
        await update.message.reply_text("🔒 Sesión cerrada. Usa /reg.")
        raise ApplicationHandlerStop


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

    request = HTTPXRequest(proxy=PROXY_URL)

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(request)
        .build()
    )

    if app.job_queue:
        app.job_queue.run_repeating(revisar_expiradas, interval=30, first=10)
        app.job_queue.run_repeating(revisar_timeouts_mates, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_memoria, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_trivia, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_palabras, interval=10, first=10)
        app.job_queue.run_repeating(revisar_timeouts_funks, interval=10, first=10)
        app.job_queue.run_repeating(revisar_eventos_expirados, interval=60, first=30)
        app.job_queue.run_repeating(revisar_eventos_iniciando, interval=30, first=15)
        app.job_queue.run_repeating(revisar_descalificados, interval=30, first=30)

    # GRUPO -10: bloqueo de comandos en partida
    app.add_handler(
        MessageHandler(filters.ALL, bloquear_comandos_en_partida),
        group=-10
    )

    # GRUPO -5: confirmaciones .si/.no (registro)
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[sS][iI]$|^\.[sS][íÍ]$|^\.[nN][oO]$"), confirmar_accion),
        group=-5
    )

    # GRUPO -4: .comenzar y .cancelar (eventos)
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[cC][oO][mM][eE][nN][zZ][aA][rR]$"), comenzar),
        group=-4
    )
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[cC][aA][nN][cC][eE][lL][aA][rR]$"), cancelar_evento),
        group=-4
    )

    # GRUPO -3: .asistir y .atras (eventos)
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[aA][sS][iI][sS][tT][iI][rR]$"), asistir),
        group=-3
    )
    app.add_handler(
        MessageHandler(filters.Regex(r"^\.[aA][tT][rR][aA][sS]$"), atras),
        group=-3
    )

    # GRUPO 0-4: respuestas de minijuegos
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_mates), group=1)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_memoria), group=2)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_trivia), group=3)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_palabras), group=4)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), responder_funks), group=5)

    # GRUPO 100: ver evento (.nombre)
    app.add_handler(MessageHandler(filters.Regex(r"^\."), ver_evento), group=100)

    # GRUPO 200: verificar registro en comandos
    app.add_handler(MessageHandler(filters.COMMAND, verificar_registro), group=200)

    # Comandos de usuario
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tutorial", tutorial))
    app.add_handler(CommandHandler("reg", reg))
    app.add_handler(CommandHandler("unreg", unreg))
    app.add_handler(CommandHandler("deletereg", deletereg))
    app.add_handler(CommandHandler("perfil", perfil))
    app.add_handler(CommandHandler("tokens", tokens_cmd))
    app.add_handler(CommandHandler("nivel", nivel_cmd))
    app.add_handler(CommandHandler("rango", rango_cmd))
    app.add_handler(CommandHandler("userslist", userslist))

    # Comandos de juegos
    app.add_handler(CommandHandler("actividades", actividades))
    app.add_handler(CommandHandler("juegos", actividades))
    app.add_handler(CommandHandler("ruleta", ruleta))
    app.add_handler(CommandHandler("apostar", apostar))
    app.add_handler(CommandHandler("cancelar", cancelar))
    app.add_handler(CommandHandler("mates", mates))
    app.add_handler(CommandHandler("dados", dados))
    app.add_handler(CommandHandler("memoria", memoria))
    app.add_handler(CommandHandler("trivia", trivia))
    app.add_handler(CommandHandler("palabras", palabras))
    app.add_handler(CommandHandler("funks", funks))

    # Comandos de banco
    app.add_handler(CommandHandler("bank", bank))
    app.add_handler(CommandHandler("depositar", depositar))
    app.add_handler(CommandHandler("retirar", retirar))

    # Comandos de eventos
    app.add_handler(CommandHandler("reclamar", reclamar))
    app.add_handler(CommandHandler("eventos", eventos))
    app.add_handler(CommandHandler("addevent", addevent))
    app.add_handler(CommandHandler("removeevent", removeevent))
    app.add_handler(CommandHandler("editevent", editevent))

    # Comandos de admin
    app.add_handler(CommandHandler("anunciar", anunciar))
    app.add_handler(CommandHandler("giveTokens", giveTokens))
    app.add_handler(CommandHandler("giveXP", giveXP))
    app.add_handler(CommandHandler("removeTokens", removeTokens))
    app.add_handler(CommandHandler("removeXP", removeXP))

    print("Bot corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()

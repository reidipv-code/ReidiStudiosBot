from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.db import esta_registrado


MENU_PRINCIPAL = (
    "📋 *AYUDA - ReidiStudiosBot*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "Elige una categoría para ver los comandos:"
)

TEXTO_CUENTA = (
    "👤 *COMANDOS DE CUENTA*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/start` → Inicia el bot\n"
    "`/reg nombre.pais` → Regístrate\n"
    "`/setpais pais` → Configura tu país\n"
    "`/perfil` → Ver tu perfil completo\n"
    "`/perfil nombre` → Ver el perfil de otro\n"
    "`/tokens` → Ver tus tokens\n"
    "`/tienda` → Abrir la tienda\n"
    "`/nivel` → Ver tu nivel y XP\n"
    "`/rango` → Ver tu rango\n"
    "`/userslist` → Lista de usuarios\n"
    "`/unreg` → Cerrar sesión\n"
    "`/deletereg` → Eliminar tu cuenta"
)

TEXTO_JUEGOS = (
    "🎮 *COMANDOS DE JUEGOS*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/actividades` → Menú de juegos\n"
    "`/mates nivel` → 5 preguntas de mates\n"
    "`/trivia pais dificultad` → Trivia de países\n"
    "`/trivia medieval dificultad` → Historia antigua/medieval\n"
    "`/trivia moderno dificultad` → Historia moderna/contemporánea\n"
    "`/memoria` → Memoriza secuencias\n"
    "`/palabras` → Ordena las letras\n"
    "`/funks` → Adivina la canción\n"
    "`/dados cantidad` → Tira los dados\n"
    "`/ruleta color` → Elige un color\n"
    "`/apostar cantidad` → Apuesta contra otro\n"
    "`/invitar nombre cantidad` → Invita a un amigo"
)

TEXTO_ECONOMIA = (
    "💰 *COMANDOS DE ECONOMÍA*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/bank` → Ver tu cuenta bancaria\n"
    "`/depositar cantidad` → Guardar tokens\n"
    "`/retirar cantidad` → Sacar tokens\n"
    "`/reclamar` → Recompensa diaria\n"
    "`/darTokens nombre cantidad mensaje` → Transferir tokens"
)

TEXTO_EVENTOS = (
    "📅 *COMANDOS DE EVENTOS*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/eventos` → Ver eventos activos\n"
    "`.nombre` → Ver detalles de un evento\n"
    "`.asistir` → Apuntarte a un evento\n"
    "`.atras` → Volver a la lista\n"
    "`.comenzar` → Empezar el evento\n"
    "`.cancelar` → Cancelar tu participación"
)

TEXTO_SOCIAL = (
    "📢 *COMANDOS SOCIALES*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/chatm` → Ir al chat mundial\n"
    "`/msp nombre| mensaje` → Mensaje privado\n"
    "`/amigo add nombre` → Enviar solicitud de amistad\n"
    "`/amigo aceptar nombre` → Aceptar solicitud\n"
    "`/amigo rechazar nombre` → Rechazar solicitud\n"
    "`/amigo eliminar nombre` → Eliminar amigo\n"
    "`/amigos` → Ver tu lista de amigos\n"
    "`/amigos online` → Ver solo los conectados\n"
    "`/solicitudes` → Ver solicitudes pendientes\n"
    "`/invitar nombre cantidad` → Invitar a un amigo a apostar\n"
    "`/top amigos` → Ranking entre tus amigos\n"
    "`/top tokens` → Top por tokens\n"
    "`/top nivel` → Top por nivel\n"
    "`/top all` → Top global\n"
    "`/stats` → Estadísticas del bot\n"
    "`/sugerencia texto` → Enviar sugerencia al admin"
)

TEXTO_INFO = (
    "ℹ️ *INFORMACIÓN*\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "`/tutorial` → Guía completa paso a paso\n"
    "`/help` → Este menú de ayuda\n"
    "`/logros` → Ver tus logros\n"
    "`/reclamarlogros` → Reclamar logros pendientes\n"
    "`/version` → Ver la versión del bot\n"
    "`/start` → Reinicia el bot\n\n"
    "📌 *Consejos:*\n"
    "• Los comandos no distinguen mayúsculas\n"
    "• Puedes escribir `.si`, `.Si` o `.SI`\n"
    "• Mientras juegas, no puedes usar otros comandos"
)


def teclado_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Cuenta", callback_data="help_cuenta"),
            InlineKeyboardButton("🎮 Juegos", callback_data="help_juegos"),
        ],
        [
            InlineKeyboardButton("💰 Economía", callback_data="help_economia"),
            InlineKeyboardButton("📅 Eventos", callback_data="help_eventos"),
        ],
        [
            InlineKeyboardButton("📢 Social", callback_data="help_social"),
            InlineKeyboardButton("ℹ️ Info", callback_data="help_info"),
        ],
    ])


def teclado_volver():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver al menú", callback_data="help_volver")]
    ])


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        MENU_PRINCIPAL,
        parse_mode="Markdown",
        reply_markup=teclado_principal()
    )


async def help_botones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "help_cuenta":
        await query.edit_message_text(TEXTO_CUENTA, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_juegos":
        await query.edit_message_text(TEXTO_JUEGOS, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_economia":
        await query.edit_message_text(TEXTO_ECONOMIA, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_eventos":
        await query.edit_message_text(TEXTO_EVENTOS, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_social":
        await query.edit_message_text(TEXTO_SOCIAL, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_info":
        await query.edit_message_text(TEXTO_INFO, parse_mode="Markdown", reply_markup=teclado_volver())
    elif data == "help_volver":
        await query.edit_message_text(MENU_PRINCIPAL, parse_mode="Markdown", reply_markup=teclado_principal())

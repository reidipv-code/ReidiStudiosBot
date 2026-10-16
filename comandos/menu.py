from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from comandos.lang import teclado_idiomas
from core.idiomas import obtener_idioma, IDIOMAS
from core.razas_clases import personaje_completo

def teclado_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 Idioma / Language", callback_data="menu_lang"),
            InlineKeyboardButton("📖 Ayuda", callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton("🎮 Actividades", callback_data="menu_actividades"),
            InlineKeyboardButton("👤 Mi personaje", callback_data="menu_perfil"),
        ],
        [
            InlineKeyboardButton("📚 Tutorial", callback_data="menu_tutorial"),
            InlineKeyboardButton("🌎 Elegir idioma", callback_data="menu_lang"),
        ],
    ])

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.effective_message
    usuario = update.effective_user
    if not mensaje or not usuario:
        return
    idioma = obtener_idioma(usuario.id)
    nombre_idioma = IDIOMAS[idioma]["native"]
    if personaje_completo(usuario.id):
        texto = (
            "📋 MENÚ PRINCIPAL — ReidiStudiosBot\n\n"
            f"🌐 Idioma actual: {nombre_idioma}\n\n"
            "Selecciona una opción:"
        )
    else:
        texto = (
            "⚔️ MENÚ PRINCIPAL — ReidiStudiosBot\n\n"
            f"🌐 Idioma actual: {nombre_idioma}\n"
            "Para completar el registro de 4 pasos:\n"
            "1. Selecciona tu idioma con /lang.\n"
            "2. Escribe /reg Nombre.Pais.\n"
            "3. Elige una raza.\n"
            "4. Elige una clase compatible.\n\n"
            "Selecciona una opción:"
        )
    await mensaje.reply_text(texto, reply_markup=teclado_menu())

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    data = query.data or ""
    await query.answer()
    if data == "menu_lang":
        idioma = obtener_idioma(query.from_user.id)
        await query.edit_message_text(
            "🌐 Selecciona el idioma del bot.\n"
            "También puedes escribir /lang español o /lang spanish.",
            reply_markup=teclado_idiomas()
        )
    elif data == "menu_help":
        await query.edit_message_text(
            "📖 AYUDA\n\n"
            "/start — Iniciar\n"
            "/lang — Cambiar idioma\n"
            "/menu — Abrir menú\n"
            "/reg Nombre.Pais — Registro\n"
            "/help — Ayuda y comandos\n"
            "/tutorial — Tutorial\n"
            "/perfil — Perfil\n"
            "/actividades — Juegos y actividades",
            reply_markup=teclado_menu()
        )
    elif data == "menu_actividades":
        await query.edit_message_text(
            "🎮 ACTIVIDADES\n\n"
            "/ruleta — Ruleta\n"
            "/apostar cantidad — Apostar\n"
            "/mates — Matemáticas\n"
            "/dados cantidad — Dados\n"
            "/memoria — Memoria\n"
            "/trivia — Trivia\n"
            "/palabras — Palabras\n"
            "/funks — Adivina la canción\n\n"
            "Usa /actividades para abrir la lista completa.",
            reply_markup=teclado_menu()
        )
    elif data == "menu_perfil":
        if personaje_completo(query.from_user.id):
            await query.edit_message_text(
                "Para consultar tu personaje, escribe /perfil.",
                reply_markup=teclado_menu()
            )
        else:
            await query.edit_message_text(
                "Aún no tienes un personaje completo.\n"
                "Primero selecciona tu idioma con /lang y después "
                "completa /reg Nombre.Pais, elige raza y clase.",
                reply_markup=teclado_menu()
            )
    elif data == "menu_tutorial":
        await query.edit_message_text(
            "📚 TUTORIAL\n\n"
            "1. /lang español (o /lang spanish).\n"
            "2. /reg Nombre.Pais.\n"
            "3. Selecciona una raza.\n"
            "4. Selecciona una clase compatible.\n\n"
            "El país solo se usa para ajustar la zona horaria de eventos.",
            reply_markup=teclado_menu()
        )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.idiomas import (
    IDIOMAS,
    guardar_idioma,
    obtener_idioma,
    resolver_idioma,
    idioma_seleccionado,
)

def teclado_idiomas():
    filas, fila = [], []
    for codigo, info in IDIOMAS.items():
        fila.append(InlineKeyboardButton(
            info["native"], callback_data=f"lang:{codigo}"
        ))
        if len(fila) == 3:
            filas.append(fila)
            fila = []
    if fila:
        filas.append(fila)
    return InlineKeyboardMarkup(filas)

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.effective_message
    usuario = update.effective_user
    if not mensaje or not usuario:
        return

    if context.args:
        identificador = " ".join(context.args).strip()
        codigo = resolver_idioma(identificador)
        if not codigo:
            lista = ", ".join(
                f"{info['native']} ({info['aliases'][1]})"
                for info in IDIOMAS.values()
            )
            await mensaje.reply_text(
                "❌ No reconozco ese idioma.\n\n"
                "Puedes usar el nombre en inglés o en su propio idioma.\n"
                "Ejemplos: /lang español, /lang spanish, /lang 日本語.\n\n"
                "Idiomas disponibles:\n" + lista
            )
            return

        guardar_idioma(usuario.id, codigo, seleccionado=True)
        await mensaje.reply_text(
            f"✅ Idioma seleccionado: {IDIOMAS[codigo]['native']}.\n\n"
            "Paso 1/4 completado. Ahora crea tu personaje con:\n"
            "/reg Nombre.Pais\n\n"
            "Puedes cambiar el idioma cuando quieras con /lang o desde /menu."
        )
        return

    actual = obtener_idioma(usuario.id)
    estado = "completado" if idioma_seleccionado(usuario.id) else "pendiente"
    await mensaje.reply_text(
        f"🌐 Idioma actual: {IDIOMAS[actual]['native']}\n"
        f"Paso 1/4: selección de idioma ({estado}).\n"
        "Pulsa un idioma para seleccionarlo. También puedes escribir "
        "/lang español, /lang spanish, /lang English o /lang 日本語.",
        reply_markup=teclado_idiomas()
    )

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    data = query.data or ""
    if not data.startswith("lang:"):
        return
    codigo = data.split(":", 1)[1]
    if codigo not in IDIOMAS:
        await query.answer("Idioma no válido.", show_alert=True)
        return
    guardar_idioma(query.from_user.id, codigo, seleccionado=True)
    await query.answer()
    await query.edit_message_text(
        f"✅ Idioma seleccionado: {IDIOMAS[codigo]['native']}.\n\n"
        "Paso 1/4 completado. Continúa con /reg Nombre.Pais.\n"
        "Puedes cambiarlo en cualquier momento con /lang o desde /menu."
    )

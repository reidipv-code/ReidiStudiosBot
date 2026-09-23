from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_pais,
)
from core.paises import obtener_nombre as nombre_pais, obtener_bandera

# ID del admin que recibe las sugerencias
ADMIN_ID = 7669914531


async def sugerencia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/sugerencia <texto>`\n\n"
            "Ejemplo: `/sugerencia Añadir minijuego de cartas`",
            parse_mode="Markdown"
        )
        return

    texto = " ".join(context.args).strip()

    if len(texto) < 5:
        await update.message.reply_text("⚠️ La sugerencia es demasiado corta.")
        return

    # Datos del usuario que sugiere
    datos = obtener_datos(user_id)
    nombre = datos[0] if datos else "Desconocido"
    id_interno = datos[1] if datos else "?"
    pais = obtener_pais(user_id)
    bandera = obtener_bandera(pais) if pais else "🌎"
    nombre_pais_str = nombre_pais(pais) if pais else "Desconocido"

    # Mensaje que recibe el admin
    texto_admin = (
        f"📩 <b>NUEVA SUGERENCIA</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 De: <b>{nombre}</b> (#{id_interno})\n"
        f"{bandera} País: <b>{nombre_pais_str}</b>\n"
        f"🆔 Telegram: <code>{user_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Texto:</b>\n{texto}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=texto_admin,
            parse_mode="HTML"
        )
        await update.message.reply_text(
            "✅ *¡Gracias por tu sugerencia!*\n\n"
            "Ha sido enviada al admin. Si es aceptada, se implementará pronto.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ No se pudo enviar la sugerencia. Inténtalo más tarde."
        )
        print(f"[SUGERENCIA] Error al enviar al admin: {e}")

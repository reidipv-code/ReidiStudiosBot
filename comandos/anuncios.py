from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from core.db import obtener_todos_los_usuarios, obtener_user_id_por_nombre

ADMINS = [7669914531]

TIPOS_ANUNCIO = {
    "event":       ("🎉", "EVENTO ESPECIAL"),
    "update":      ("🔧", "ACTUALIZACIÓN"),
    "warning":     ("⚠️", "ADVERTENCIA"),
    "info":        ("ℹ️", "INFORMACIÓN"),
    "prize":       ("🎁", "PREMIO ESPECIAL"),
    "maintenance": ("🛠️", "MANTENIMIENTO"),
    "newgame":     ("🎮", "NUEVO MINIJUEGO"),
    "tourney":     ("🏆", "TORNEO"),
    "important":   ("🚨", "IMPORTANTE"),
    "dm":          ("📩", "MENSAJE DIRECTO"),
}


def es_admin(user_id):
    return user_id in ADMINS


def formatear_fecha():
    return datetime.now().strftime("%d/%m/%Y - %H:%M")


async def anunciar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not es_admin(user_id):
        await update.message.reply_text("❌ No tienes permiso para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Debes escribir el mensaje.\n\n"
            "📋 *Tipos disponibles:*\n"
            "`/anunciar event <mensaje>`\n"
            "`/anunciar update <mensaje>`\n"
            "`/anunciar warning <mensaje>`\n"
            "`/anunciar info <mensaje>`\n"
            "`/anunciar prize <mensaje>`\n"
            "`/anunciar maintenance <mensaje>`\n"
            "`/anunciar newgame <mensaje>`\n"
            "`/anunciar tourney <mensaje>`\n"
            "`/anunciar important <mensaje>`\n"
            "`/anunciar dm <nombre> <mensaje>`\n"
            "`/anunciar <mensaje>` (genérico)",
            parse_mode="Markdown"
        )
        return

    primer_arg = context.args[0].lower()

    if primer_arg in TIPOS_ANUNCIO:
        tipo = primer_arg
        resto = context.args[1:]
    else:
        tipo = None
        resto = context.args

    if not resto:
        await update.message.reply_text("⚠️ Debes escribir el mensaje después del tipo.")
        return

    if tipo == "dm":
        if len(resto) < 2:
            await update.message.reply_text(
                "⚠️ Uso: `/anunciar dm <nombre> <mensaje>`",
                parse_mode="Markdown"
            )
            return

        nombre_destino = resto[0]
        mensaje = " ".join(resto[1:]).strip()
        destino_id = obtener_user_id_por_nombre(nombre_destino)

        if destino_id is None:
            await update.message.reply_text(
                f"❌ No existe ningún usuario con el nombre *{nombre_destino}*.",
                parse_mode="Markdown"
            )
            return

        emoji, etiqueta = TIPOS_ANUNCIO["dm"]
        fecha = formatear_fecha()
        texto_final = (
            f"{emoji} <b>{etiqueta}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📅 {fecha}\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{mensaje}"
        )

        try:
            await context.bot.send_message(chat_id=destino_id, text=texto_final, parse_mode="HTML")
            await update.message.reply_text(f"✅ Mensaje enviado a {nombre_destino}.", parse_mode="HTML")
        except Exception:
            await update.message.reply_text("❌ No se pudo enviar el mensaje.")
        return

    if tipo is not None:
        emoji, etiqueta = TIPOS_ANUNCIO[tipo]
    else:
        emoji, etiqueta = "📢", "ANUNCIO"

    mensaje = " ".join(resto).strip()
    fecha = formatear_fecha()
    texto_final = (
        f"{emoji} <b>{etiqueta}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {fecha}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mensaje}"
    )

    ids = obtener_todos_los_usuarios()
    enviados = 0
    fallidos = 0

    for uid in ids:
        try:
            await context.bot.send_message(chat_id=uid, text=texto_final, parse_mode="HTML")
            enviados += 1
        except Exception:
            fallidos += 1

    await update.message.reply_text(
        f"✅ <b>Anuncio enviado</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📤 Enviados: <b>{enviados}</b>\n"
        f"❌ Fallidos: <b>{fallidos}</b>\n"
        f"👥 Total usuarios: <b>{len(ids)}</b>",
        parse_mode="HTML"
    )

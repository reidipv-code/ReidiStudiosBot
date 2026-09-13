import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import (
    esta_registrado, obtener_datos, obtener_todos_los_usuarios,
    registrar, eliminar_usuario, actualizar_sesion
)
from core.validacion import validar_nombre


async def notificar_a_todos(context, user_id_excluir, texto):
    ids = obtener_todos_los_usuarios()
    for uid in ids:
        if uid == user_id_excluir:
            continue
        try:
            await context.bot.send_message(chat_id=uid, text=texto, parse_mode="HTML")
        except Exception:
            pass


async def reg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin_username"

    if not context.args:
        await update.message.reply_text("⚠️ Debes poner tu nombre.\nEjemplo: /reg Juan")
        return

    if esta_registrado(user_id):
        datos = obtener_datos(user_id)
        if datos[5] == 1:
            await update.message.reply_text(
                f"⚠️ Ya estás registrado como *{datos[0]}* (ID: #{datos[1]}).",
                parse_mode="Markdown"
            )
            return
        else:
            actualizar_sesion(user_id, 1)
            await update.message.reply_text(
                f"✅ ¡Bienvenido de vuelta, *{datos[0]}*!",
                parse_mode="Markdown"
            )
            return

    nombre = " ".join(context.args).strip()
    valido, error = validar_nombre(nombre)

    if not valido:
        await update.message.reply_text(error, parse_mode="Markdown")
        return

    id_interno = registrar(user_id, username, nombre)

    await update.message.reply_text(
        f"✅ ¡Registro exitoso!\n\n"
        f"👤 *{nombre}*\n"
        f"🆔 *#{id_interno}*\n"
        f"💰 *100 tokens*\n"
        f"⭐ *Nivel 1*",
        parse_mode="Markdown"
    )

    texto_notif = f"🆕 <b>Nuevo usuario registrado</b>\n👤 <b>{nombre}</b> se ha unido al bot."
    await notificar_a_todos(context, user_id, texto_notif)


async def unreg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("❌ No tienes ninguna cuenta registrada.")
        return

    datos = obtener_datos(user_id)
    if datos[5] == 0:
        await update.message.reply_text("ℹ️ Tu sesión ya estaba cerrada.")
        return

    # Guardar confirmación pendiente en context.user_data
    context.user_data["confirmacion"] = {
        "accion": "unreg",
        "inicio": time.time()
    }

    await update.message.reply_text(
        "⚠️ *¿Cerrar sesión?*\n"
        "Responde `.si` o `.no`. Tienes 30 seg.",
        parse_mode="Markdown"
    )


async def deletereg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("❌ No tienes ninguna cuenta registrada.")
        return

    context.user_data["confirmacion"] = {
        "accion": "deletereg",
        "inicio": time.time()
    }

    await update.message.reply_text(
        "⚠️ *¿ELIMINAR tu cuenta?*\n"
        "Responde `.si` o `.no`. Tienes 30 seg.",
        parse_mode="Markdown"
    )


async def confirmar_accion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if "confirmacion" not in context.user_data:
        return

    texto = update.message.text.strip().lower()
    if texto not in [".si", ".sí", ".no"]:
        return

    accion = context.user_data["confirmacion"]["accion"]
    datos = obtener_datos(user_id)

    if texto in [".si", ".sí"]:
        if accion == "unreg":
            actualizar_sesion(user_id, 0)
            del context.user_data["confirmacion"]
            await update.message.reply_text(
                f"👋 Sesión cerrada, *{datos[0]}*.",
                parse_mode="Markdown"
            )
            await notificar_a_todos(context, user_id, f"👋 <b>{datos[0]}</b> cerró sesión.")
            raise ApplicationHandlerStop

        elif accion == "deletereg":
            nombre = datos[0]
            eliminar_usuario(user_id)
            del context.user_data["confirmacion"]
            await update.message.reply_text("🗑️ Cuenta eliminada.", parse_mode="Markdown")
            await notificar_a_todos(context, user_id, f"🗑️ <b>{nombre}</b> abandonó el bot.")
            raise ApplicationHandlerStop

    elif texto == ".no":
        del context.user_data["confirmacion"]
        await update.message.reply_text("✅ Cancelado.")
        raise ApplicationHandlerStop

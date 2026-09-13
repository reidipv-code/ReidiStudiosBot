from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    obtener_user_id_por_nombre, obtener_datos,
    actualizar_tokens, sumar_xp
)

ADMINS = [7669914531]


def es_admin(user_id):
    return user_id in ADMINS


async def _procesar_masivo(update, context, tipo, accion):
    user_id = update.effective_user.id

    if not es_admin(user_id):
        await update.message.reply_text("❌ No tienes permiso.")
        return

    if not context.args:
        await update.message.reply_text(
            f"⚠️ Uso:\n"
            f"`/{accion}{tipo.capitalize()} <nombre1>|<nombre2>|<cantidad>|<mensaje>`\n\n"
            f"Ejemplo:\n"
            f"`/{accion}{tipo.capitalize()} OriGamePlay|Diana|500|por ganar el torneo`",
            parse_mode="Markdown"
        )
        return

    texto_completo = " ".join(context.args)
    partes = texto_completo.split("|")

    if len(partes) < 3:
        await update.message.reply_text(
            "❌ Debes separar con `|`: nombre(s), cantidad y mensaje.",
            parse_mode="Markdown"
        )
        return

    mensaje = partes[-1].strip()
    cantidad_str = partes[-2].strip()
    nombres_str = "|".join(partes[:-2])

    try:
        cantidad = int(cantidad_str)
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número.")
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La cantidad debe ser mayor que 0.")
        return

    if cantidad > 9999:
        await update.message.reply_text("❌ La cantidad máxima es 9999.")
        return

    if accion == "remove":
        cantidad = -cantidad

    nombres = [n.strip() for n in nombres_str.split("|") if n.strip()]

    if not nombres:
        await update.message.reply_text("❌ Debes indicar al menos un nombre.")
        return

    usuarios = []
    for nombre in nombres:
        uid = obtener_user_id_por_nombre(nombre)
        if uid is None:
            await update.message.reply_text(
                f"❌ El usuario *{nombre}* no existe.\nNo se ha enviado nada.",
                parse_mode="Markdown"
            )
            return
        usuarios.append((nombre, uid))

    emoji = "🎁" if accion == "give" else "⚠️"
    etiqueta = "¡Has recibido una recompensa!" if accion == "give" else "Se te ha aplicado una penalización"

    for nombre, uid in usuarios:
        if tipo == "tokens":
            actualizar_tokens(uid, cantidad)
        else:
            sumar_xp(uid, cantidad)

        signo = "+" if cantidad > 0 else ""
        unidad = "tokens" if tipo == "tokens" else "XP"

        texto_usuario = (
            f"{emoji} <b>{etiqueta}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📊 {signo}{cantidad} {unidad}\n"
            f"📝 {mensaje}"
        )
        try:
            await context.bot.send_message(chat_id=uid, text=texto_usuario, parse_mode="HTML")
        except Exception:
            pass

    lineas = "✅ <b>Recompensa enviada</b>\n━━━━━━━━━━━━━━━━━━━\n"
    for nombre, uid in usuarios:
        saldos = obtener_datos(uid)
        if tipo == "tokens":
            lineas += f"👤 {nombre} → {cantidad:+d} tokens (nuevo: {saldos[2]})\n"
        else:
            lineas += f"👤 {nombre} → {cantidad:+d} XP (nivel {saldos[4]}, {saldos[3]} XP)\n"

    await update.message.reply_text(lineas, parse_mode="HTML")


async def giveTokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _procesar_masivo(update, context, "tokens", "give")


async def giveXP(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _procesar_masivo(update, context, "xp", "give")


async def removeTokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _procesar_masivo(update, context, "tokens", "remove")


async def removeXP(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _procesar_masivo(update, context, "xp", "remove")

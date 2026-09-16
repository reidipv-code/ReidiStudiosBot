import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_user_id_por_nombre,
    actualizar_tokens,
    sumar_xp,
)
from core.amigos import son_amigos

# Invitaciones pendientes: {id_invitacion: {...}}
invitaciones = {}
siguiente_id = 1

# Tiempo que dura una invitación sin respuesta
EXPIRACION = 120


async def invitar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /invitar <nombre> <cantidad>
    Invita a un amigo a una apuesta 1v1.
    """
    global siguiente_id

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Uso: `/invitar <nombre> <cantidad>`\n\n"
            "Ejemplo: `/invitar Diana 50`\n\n"
            "Solo puedes invitar a tus amigos.",
            parse_mode="Markdown"
        )
        return

    nombre_objetivo = context.args[0].strip()

    try:
        cantidad = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número.")
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La cantidad debe ser mayor que 0.")
        return

    objetivo_id = obtener_user_id_por_nombre(nombre_objetivo)

    if objetivo_id is None:
        await update.message.reply_text(
            f"❌ No existe ningún usuario con el nombre *{nombre_objetivo}*.",
            parse_mode="Markdown"
        )
        return

    if objetivo_id == user_id:
        await update.message.reply_text("❌ No puedes invitarte a ti mismo.")
        return

    if not son_amigos(user_id, objetivo_id):
        await update.message.reply_text(
            f"❌ Solo puedes invitar a tus amigos.\n"
            f"Usa `/amigo add {nombre_objetivo}` primero.",
            parse_mode="Markdown"
        )
        return

    datos_user = obtener_datos(user_id)
    datos_obj = obtener_datos(objetivo_id)

    nombre_user = datos_user[0]
    nombre_obj = datos_obj[0]
    tokens_user = datos_user[2]
    tokens_obj = datos_obj[2]

    if tokens_user < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens.\n"
            f"Tienes *{tokens_user}* y quieres apostar *{cantidad}*.",
            parse_mode="Markdown"
        )
        return

    if tokens_obj < cantidad:
        await update.message.reply_text(
            f"❌ *{nombre_obj}* no tiene suficientes tokens para aceptar.\n"
            f"Tiene *{tokens_obj}*.",
            parse_mode="Markdown"
        )
        return

    # Comprobar invitaciones ya activas
    for inv in invitaciones.values():
        if inv["de_id"] == user_id and inv["para_id"] == objetivo_id:
            await update.message.reply_text(
                f"⏳ Ya tienes una invitación activa a *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            return

    inv_id = siguiente_id
    siguiente_id += 1

    invitaciones[inv_id] = {
        "de_id": user_id,
        "de_nombre": nombre_user,
        "para_id": objetivo_id,
        "para_nombre": nombre_obj,
        "cantidad": cantidad,
        "creada": time.time(),
    }

    # Enviar la invitación al objetivo con botones
    teclado = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Aceptar", callback_data=f"inv_ok_{inv_id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"inv_no_{inv_id}"),
        ]
    ])

    try:
        await context.bot.send_message(
            chat_id=objetivo_id,
            text=(
                f"🎲 *INVITACIÓN A APUESTA*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *{nombre_user}* te invita a apostar.\n\n"
                f"💰 Cantidad: *{cantidad}* tokens\n\n"
                f"⏱️ Expira en 2 minutos."
            ),
            parse_mode="Markdown",
            reply_markup=teclado
        )
    except Exception as e:
        del invitaciones[inv_id]
        await update.message.reply_text(f"❌ No se pudo enviar la invitación: {e}")
        return

    await update.message.reply_text(
        f"✅ Invitación enviada a *{nombre_obj}* por *{cantidad}* tokens.\n"
        f"Espera a que responda (máx. 2 min).",
        parse_mode="Markdown"
    )


async def responder_invitacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja los botones de aceptar/rechazar."""
    global siguiente_id
    import random

    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # inv_ok_X o inv_no_X
    partes = data.split("_")
    if len(partes) != 3:
        return

    accion = partes[1]
    try:
        inv_id = int(partes[2])
    except ValueError:
        return

    if inv_id not in invitaciones:
        await query.edit_message_text("❌ Esta invitación ya expiró o fue cancelada.")
        return

    inv = invitaciones[inv_id]

    # Solo el destinatario puede aceptar/rechazar
    if user_id != inv["para_id"]:
        await query.answer("❌ Esta invitación no es para ti.", show_alert=True)
        return

    de_id = inv["de_id"]
    cantidad = inv["cantidad"]
    de_nombre = inv["de_nombre"]
    para_nombre = inv["para_nombre"]

    # ─── RECHAZAR ──────────────────────────────────────────
    if accion == "no":
        del invitaciones[inv_id]
        await query.edit_message_text(
            f"❌ Has rechazado la apuesta de *{de_nombre}*.",
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=de_id,
                text=f"❌ *{para_nombre}* ha rechazado tu apuesta.",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        return

    # ─── ACEPTAR ───────────────────────────────────────────
    datos_de = obtener_datos(de_id)
    datos_para = obtener_datos(user_id)

    if datos_de is None or datos_para is None:
        del invitaciones[inv_id]
        await query.edit_message_text("❌ Error: no se pudieron obtener los datos.")
        return

    if datos_de[2] < cantidad:
        del invitaciones[inv_id]
        await query.edit_message_text(f"❌ *{de_nombre}* ya no tiene suficientes tokens.")
        return

    if datos_para[2] < cantidad:
        del invitaciones[inv_id]
        await query.edit_message_text(f"❌ Ya no tienes suficientes tokens.")
        return

    # Resolver la apuesta
    ganador = random.choice([de_id, user_id])

    if ganador == de_id:
        actualizar_tokens(de_id, cantidad)
        actualizar_tokens(user_id, -cantidad)
        sumar_xp(de_id, 30)
        resultado = (
            f"🎲 *APUESTA RESUELTA*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🥇 Ganador: *{de_nombre}*\n"
            f"🥈 Perdedor: *{para_nombre}*\n\n"
            f"💰 *{de_nombre}* ganó *{cantidad}* tokens\n"
            f"✨ +30 XP"
        )
    else:
        actualizar_tokens(user_id, cantidad)
        actualizar_tokens(de_id, -cantidad)
        sumar_xp(user_id, 30)
        resultado = (
            f"🎲 *APUESTA RESUELTA*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🥇 Ganador: *{para_nombre}*\n"
            f"🥈 Perdedor: *{de_nombre}*\n\n"
            f"💰 *{para_nombre}* ganó *{cantidad}* tokens\n"
            f"✨ +30 XP"
        )

    del invitaciones[inv_id]

    await query.edit_message_text(resultado, parse_mode="Markdown")

    # Avisar también al que invitó
    try:
        await context.bot.send_message(chat_id=de_id, text=resultado, parse_mode="Markdown")
    except Exception:
        pass


async def revisar_invitaciones_expiradas(context) -> None:
    """Borra invitaciones que llevan más de 2 minutos sin respuesta."""
    ahora = time.time()
    for inv_id, inv in list(invitaciones.items()):
        if ahora - inv["creada"] > EXPIRACION:
            del invitaciones[inv_id]
            try:
                await context.bot.send_message(
                    chat_id=inv["de_id"],
                    text=f"⌛ Tu invitación a *{inv['para_nombre']}* ha expirado.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

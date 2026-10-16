from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_user_id_por_nombre,
    obtener_pais,
    esta_online,
)
from core.paises import obtener_bandera
from core.amigos import (
    son_amigos,
    enviar_solicitud,
    obtener_solicitudes,
    hay_solicitud,
    aceptar_solicitud,
    rechazar_solicitud,
    eliminar_amigo,
    lista_amigos,
    contar_amigos,
)


async def avisar_logro(context, user_id, clave):
    from core.logros import LOGROS
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


async def amigo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso:\n"
            "`/amigo add nombre` → Enviar solicitud\n"
            "`/amigo aceptar nombre` → Aceptar solicitud\n"
            "`/amigo rechazar nombre` → Rechazar solicitud\n"
            "`/amigo eliminar nombre` → Eliminar amigo\n"
            "`/amigos` → Ver tu lista",
            parse_mode="Markdown"
        )
        return

    accion = context.args[0].lower()

    if accion not in ["add", "aceptar", "rechazar", "eliminar"]:
        await update.message.reply_text(
            "❌ Acción no válida. Usa: `add`, `aceptar`, `rechazar` o `eliminar`.",
            parse_mode="Markdown"
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            f"⚠️ Uso: `/amigo {accion} <nombre>`",
            parse_mode="Markdown"
        )
        return

    nombre_objetivo = " ".join(context.args[1:]).strip()
    objetivo_id = obtener_user_id_por_nombre(nombre_objetivo)

    if objetivo_id is None:
        await update.message.reply_text(
            f"❌ No existe ningún usuario con el nombre *{nombre_objetivo}*.",
            parse_mode="Markdown"
        )
        return

    if objetivo_id == user_id:
        await update.message.reply_text("❌ No puedes hacer eso contigo mismo.")
        return

    datos_user = obtener_datos(user_id)
    nombre_user = datos_user[0]

    datos_obj = obtener_datos(objetivo_id)
    nombre_obj = datos_obj[0]

    # ─── ADD ───────────────────────────────────────────────
    if accion == "add":
        if son_amigos(user_id, objetivo_id):
            await update.message.reply_text(
                f"⚠️ Ya eres amigo de *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            return

        # ¿Ya le mandó solicitud?
        if hay_solicitud(user_id, objetivo_id):
            await update.message.reply_text(
                f"⏳ Ya le enviaste una solicitud a *{nombre_obj}*. Espera a que la acepte.",
                parse_mode="Markdown"
            )
            return

        # ¿El otro ya le mandó solicitud a él? → aceptar directamente
        if hay_solicitud(objetivo_id, user_id):
            if aceptar_solicitud(objetivo_id, user_id):
                await update.message.reply_text(
                    f"✅ ¡Ahora eres amigo de *{nombre_obj}*! (Aceptó tu solicitud pendiente)",
                    parse_mode="Markdown"
                )
                try:
                    await context.bot.send_message(
                        chat_id=objetivo_id,
                        text=f"✅ *{nombre_user}* ha aceptado tu solicitud. ¡Ya son amigos!",
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass
                return

        # Enviar solicitud
        if enviar_solicitud(user_id, objetivo_id):
            await update.message.reply_text(
                f"✅ Solicitud enviada a *{nombre_obj}*.\nEspera a que la acepte.",
                parse_mode="Markdown"
            )
            try:
                await context.bot.send_message(
                    chat_id=objetivo_id,
                    text=(
                        f"👋 *SOLICITUD DE AMISTAD*\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"*{nombre_user}* quiere ser tu amigo.\n\n"
                        f"Responde:\n"
                        f"`/amigo aceptar {nombre_user}`\n"
                        f"`/amigo rechazar {nombre_user}`"
                    ),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        return

    # ─── ACEPTAR ───────────────────────────────────────────
    if accion == "aceptar":
        if not hay_solicitud(objetivo_id, user_id):
            await update.message.reply_text(
                f"❌ No tienes solicitudes pendientes de *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            return

        if aceptar_solicitud(objetivo_id, user_id):
            await update.message.reply_text(
                f"✅ ¡Ahora eres amigo de *{nombre_obj}*!",
                parse_mode="Markdown"
            )
            try:
                await context.bot.send_message(
                    chat_id=objetivo_id,
                    text=f"✅ *{nombre_user}* ha aceptado tu solicitud. ¡Ya son amigos!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        return

    # ─── RECHAZAR ──────────────────────────────────────────
    if accion == "rechazar":
        if not hay_solicitud(objetivo_id, user_id):
            await update.message.reply_text(
                f"❌ No tienes solicitudes pendientes de *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            return

        if rechazar_solicitud(objetivo_id, user_id):
            await update.message.reply_text(
                f"✅ Has rechazado la solicitud de *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            try:
                await context.bot.send_message(
                    chat_id=objetivo_id,
                    text=f"❌ *{nombre_user}* ha rechazado tu solicitud de amistad.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        return

    # ─── ELIMINAR ──────────────────────────────────────────
    if accion == "eliminar":
        if not son_amigos(user_id, objetivo_id):
            await update.message.reply_text(
                f"❌ No eres amigo de *{nombre_obj}*.",
                parse_mode="Markdown"
            )
            return

        if eliminar_amigo(user_id, objetivo_id):
            await update.message.reply_text(
                f"✅ Has eliminado a *{nombre_obj}* de tus amigos.",
                parse_mode="Markdown"
            )
            try:
                await context.bot.send_message(
                    chat_id=objetivo_id,
                    text=f"💔 *{nombre_user}* te ha eliminado de sus amigos.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        return


async def amigos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais")
        return

    ids_amigos = lista_amigos(user_id)

    if not ids_amigos:
        await update.message.reply_text(
            "👥 *TUS AMIGOS*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "No tienes amigos todavía.\n\n"
            "Usa `/amigo add nombre` para añadir uno.",
            parse_mode="Markdown"
        )
        return

    # Si el argumento es "online", filtrar
    solo_online = context.args and context.args[0].lower() == "online"

    lineas = []
    online_count = 0

    for aid in ids_amigos:
        datos = obtener_datos(aid)
        if datos is None:
            continue
        nombre, id_interno, tokens, xp, nivel, sesion = datos
        pais = obtener_pais(aid)
        bandera = obtener_bandera(pais) if pais else "🌎"
        online = esta_online(aid)

        if online:
            online_count += 1

        if solo_online and not online:
            continue

        emoji = "🟢" if online else "⚫"
        lineas.append(f"{emoji} *{nombre}* {bandera} — Nivel {nivel}")

    if not lineas:
        await update.message.reply_text(
            "📋 No hay amigos que mostrar con ese filtro.",
            parse_mode="Markdown"
        )
        return

    titulo = "👥 *AMIGOS ONLINE*" if solo_online else "👥 *TUS AMIGOS*"
    texto = f"{titulo}\n"
    texto += f"━━━━━━━━━━━━━━━━━━━\n"
    texto += f"👥 Total: *{len(ids_amigos)}* · 🟢 Online: *{online_count}*\n\n"
    texto += "\n".join(lineas)
    texto += "\n\nUsa `/amigos online` para ver solo los conectados."

    await update.message.reply_text(texto, parse_mode="Markdown")


async def solicitudes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais")
        return

    ids = obtener_solicitudes(user_id)

    if not ids:
        await update.message.reply_text(
            "📭 No tienes solicitudes de amistad pendientes.",
            parse_mode="Markdown"
        )
        return

    texto = "📬 *SOLICITUDES PENDIENTES*\n"
    texto += "━━━━━━━━━━━━━━━━━━━\n\n"

    for de_id in ids:
        datos = obtener_datos(de_id)
        if datos is None:
            continue
        nombre = datos[0]
        pais = obtener_pais(de_id)
        bandera = obtener_bandera(pais) if pais else "🌎"
        texto += f"{bandera} *{nombre}*\n"
        texto += f"    `/amigo aceptar {nombre}`\n"
        texto += f"    `/amigo rechazar {nombre}`\n\n"

    texto += "También puedes escribir `/solicitudes` para verlas de nuevo."
    await update.message.reply_text(texto, parse_mode="Markdown")

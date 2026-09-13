# ═══════════════════════════════════════════════════════════
# admin/admin.py
# Comandos de admin centralizados + formato Markdown→HTML
# ═══════════════════════════════════════════════════════════

import sqlite3
import os
import re
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    obtener_user_id_por_nombre,
    obtener_datos,
    actualizar_tokens,
    sumar_xp,
    obtener_todos_los_usuarios,
)

DB_PATH = os.path.expanduser("~/telegram_bot/usuarios.db")

ADMINS = [7669914531]


def es_admin(user_id: int) -> bool:
    return user_id in ADMINS


# ═══════════════════════════════════════════════════════════
# FORMATO
# ═══════════════════════════════════════════════════════════
def convertir_formato(texto: str) -> str:
    texto = texto.replace("\\n", "\n")

    citas = []
    monos = []

    def guardar_cita(match):
        citas.append(match.group(1))
        return f"@@CITA{len(citas)-1}@@"

    def guardar_mono(match):
        monos.append(match.group(1))
        return f"@@MONO{len(monos)-1}@@"

    texto = re.sub(r">(.+?)<", guardar_cita, texto, flags=re.DOTALL)
    texto = re.sub(r"-(.+?)-", guardar_mono, texto, flags=re.DOTALL)
    texto = texto.replace("<", "&lt;").replace(">", "&gt;")
    texto = re.sub(r"\*(.+?)\*", r"<b>\1</b>", texto, flags=re.DOTALL)
    texto = re.sub(r"_(.+?)_", r"<i>\1</i>", texto, flags=re.DOTALL)

    for i, contenido in enumerate(citas):
        texto = texto.replace(f"@@CITA{i}@@", f"<blockquote>{contenido}</blockquote>")

    for i, contenido in enumerate(monos):
        texto = texto.replace(f"@@MONO{i}@@", f"<code>{contenido}</code>")

    return texto


def _formatear_fecha() -> str:
    return datetime.now().strftime("%d/%m/%Y - %H:%M")


# ═══════════════════════════════════════════════════════════
# /anunciar
# ═══════════════════════════════════════════════════════════
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
            "`/anunciar <mensaje>` (genérico)\n\n"
            "🎨 *Formato soportado:*\n"
            "`*negrita*` · `_cursiva_` · `-mono-` · `>cita<` · `\\n` (enter)",
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
        mensaje_fmt = convertir_formato(mensaje)
        texto_final = (
            f"{emoji} <b>{etiqueta}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📅 {_formatear_fecha()}\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{mensaje_fmt}"
        )

        try:
            await context.bot.send_message(chat_id=destino_id, text=texto_final, parse_mode="HTML")
            await update.message.reply_text(f"✅ Mensaje enviado a {nombre_destino}.")
        except Exception as e:
            await update.message.reply_text(f"❌ No se pudo enviar: {e}")
        return

    if tipo is not None:
        emoji, etiqueta = TIPOS_ANUNCIO[tipo]
    else:
        emoji, etiqueta = "📢", "ANUNCIO"

    mensaje = " ".join(resto).strip()
    mensaje_fmt = convertir_formato(mensaje)
    texto_final = (
        f"{emoji} <b>{etiqueta}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {_formatear_fecha()}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{mensaje_fmt}"
    )

    ids = obtener_todos_los_usuarios()
    enviados, fallidos = 0, 0

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


# ═══════════════════════════════════════════════════════════
# give / remove masivo (Tokens y XP) — CON FORMATO
# ═══════════════════════════════════════════════════════════
async def _procesar_masivo(update, context, tipo, accion):
    user_id = update.effective_user.id

    if not es_admin(user_id):
        await update.message.reply_text("❌ No tienes permiso.")
        return

    if not context.args:
        await update.message.reply_text(
            f"⚠️ Uso:\n"
            f"`/{accion}{tipo.capitalize()} <nombre1>|<nombre2>|<cantidad>|<mensaje>`",
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
    etiqueta = ("¡Has recibido una recompensa!" if accion == "give"
                else "Se te ha aplicado una penalización")

    mensaje_fmt = convertir_formato(mensaje)

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
            f"📝 {mensaje_fmt}"
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

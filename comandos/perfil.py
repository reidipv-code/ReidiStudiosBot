from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado, obtener_datos, obtener_lista_usuarios,
    xp_total_para_nivel, rango_por_nivel, barra_progreso
)


async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate con /reg tu_nombre")
        return

    datos = obtener_datos(user_id)
    nombre, id_interno, tokens, xp, nivel, sesion = datos
    barra = barra_progreso(xp, nivel)
    xp_siguiente = xp_total_para_nivel(nivel + 1)

    await update.message.reply_text(
        f"👤 *{nombre.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: *#{id_interno}*\n"
        f"🔑 Telegram: `{user_id}`\n"
        f"🎖️ {rango_por_nivel(nivel)}\n"
        f"⭐ Nivel: *{nivel}*\n"
        f"✨ XP: {xp}/{xp_siguiente}\n"
        f"📊 {barra}\n"
        f"💰 {tokens} tokens",
        parse_mode="Markdown"
    )


async def tokens_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    await update.message.reply_text(f"💰 *{datos[2]}* tokens", parse_mode="Markdown")


async def nivel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    nombre, _, _, xp, nivel, _ = datos
    await update.message.reply_text(
        f"⭐ *{nombre}* - Nivel {nivel}\n"
        f"✨ XP: {xp}/{xp_total_para_nivel(nivel + 1)}\n"
        f"📊 {barra_progreso(xp, nivel)}",
        parse_mode="Markdown"
    )


async def rango_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    await update.message.reply_text(
        f"🎖️ {rango_por_nivel(datos[4])}",
        parse_mode="Markdown"
    )


async def userslist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return

    lista = obtener_lista_usuarios()
    if not lista:
        await update.message.reply_text("📋 No hay usuarios registrados.")
        return

    texto = "📋 *USUARIOS*\n━━━━━━━━━━━━━━━━━━━\n"
    for id_interno, nombre in lista:
        texto += f"#{id_interno} - {nombre}\n"
    texto += f"\n👥 Total: *{len(lista)}*"
    await update.message.reply_text(texto, parse_mode="Markdown")

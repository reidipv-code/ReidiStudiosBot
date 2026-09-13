import sqlite3
import os
from telegram import Update
from telegram.ext import ContextTypes

from core.db import obtener_datos, actualizar_tokens

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "usuarios.db")

LIMITE_BANCO = 4000


def init_banco_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS banco (
            user_id INTEGER PRIMARY KEY,
            saldo INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def obtener_saldo_banco(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT saldo FROM banco WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_saldo_banco(user_id, cantidad):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO banco (user_id, saldo) VALUES (?, ?)", (user_id, cantidad))
    conn.commit()
    conn.close()


async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None:
        await update.message.reply_text("🔒 Debes estar registrado.\nUsa /reg tu_nombre")
        return

    nombre = datos[0]
    en_mano = datos[2]
    en_banco = obtener_saldo_banco(user_id)
    total = en_mano + en_banco

    await update.message.reply_text(
        f"🏦 *TU CUENTA BANCARIA*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Titular: *{nombre}*\n"
        f"💵 En mano: *{en_mano}* tokens\n"
        f"🏦 En banco: *{en_banco}* / {LIMITE_BANCO} tokens\n"
        f"💰 Total: *{total}* tokens\n\n"
        f"📌 Límite del banco: *{LIMITE_BANCO}* tokens\n\n"
        f"Usa:\n"
        f"• `/depositar cantidad`\n"
        f"• `/retirar cantidad`",
        parse_mode="Markdown"
    )


async def depositar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None:
        await update.message.reply_text("🔒 Debes estar registrado.\nUsa /reg tu_nombre")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/depositar 50`", parse_mode="Markdown")
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La cantidad debe ser mayor que 0.")
        return

    en_mano = datos[2]
    en_banco = obtener_saldo_banco(user_id)

    if en_mano < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens en mano.\nTienes: *{en_mano}*",
            parse_mode="Markdown"
        )
        return

    if en_banco + cantidad > LIMITE_BANCO:
        disponible = LIMITE_BANCO - en_banco
        await update.message.reply_text(
            f"❌ El banco tiene un límite de *{LIMITE_BANCO}* tokens.\n"
            f"Espacio disponible: *{disponible}*",
            parse_mode="Markdown"
        )
        return

    actualizar_tokens(user_id, -cantidad)
    set_saldo_banco(user_id, en_banco + cantidad)

    await update.message.reply_text(
        f"✅ *Depósito exitoso*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📥 Depositado: *{cantidad}* tokens\n\n"
        f"💵 En mano: *{en_mano - cantidad}*\n"
        f"🏦 En banco: *{en_banco + cantidad}* / {LIMITE_BANCO}",
        parse_mode="Markdown"
    )


async def retirar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    datos = obtener_datos(user_id)
    if datos is None:
        await update.message.reply_text("🔒 Debes estar registrado.\nUsa /reg tu_nombre")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/retirar 50`", parse_mode="Markdown")
        return

    try:
        cantidad = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La cantidad debe ser mayor que 0.")
        return

    en_mano = datos[2]
    en_banco = obtener_saldo_banco(user_id)

    if en_banco < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens en el banco.\nTienes: *{en_banco}*",
            parse_mode="Markdown"
        )
        return

    set_saldo_banco(user_id, en_banco - cantidad)
    actualizar_tokens(user_id, cantidad)

    await update.message.reply_text(
        f"✅ *Retiro exitoso*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📤 Retirado: *{cantidad}* tokens\n\n"
        f"💵 En mano: *{en_mano + cantidad}*\n"
        f"🏦 En banco: *{en_banco - cantidad}* / {LIMITE_BANCO}",
        parse_mode="Markdown"
    )

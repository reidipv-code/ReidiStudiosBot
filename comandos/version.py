from telegram import Update
from telegram.ext import ContextTypes

from core.db import DB_PATH
import sqlite3

ADMINS = [7669914531]


def _init_version_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bot_config (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)
    conn.commit()
    conn.close()


def _get_version() -> str:
    _init_version_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT valor FROM bot_config WHERE clave = 'version'")
    r = c.fetchone()
    if not r:
        c.execute(
            "INSERT OR REPLACE INTO bot_config (clave, valor) VALUES ('version', ?)",
            ("1.0.0",)
        )
        conn.commit()
        conn.close()
        return "1.0.0"
    conn.close()
    return r[0]


def _set_version(nueva: str) -> None:
    _init_version_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO bot_config (clave, valor) VALUES ('version', ?)",
        (nueva,)
    )
    conn.commit()
    conn.close()


async def version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    v = _get_version()
    await update.message.reply_text(
        f"🤖 *ReidiStudiosBot*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Versión actual: *{v}*",
        parse_mode="Markdown"
    )


async def setversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        await update.message.reply_text("❌ No tienes permiso.")
        return

    if not context.args:
        v = _get_version()
        await update.message.reply_text(
            f"📦 Versión actual: *{v}*\n\n"
            f"Uso: `/setversion x.x.x`\n"
            f"Ejemplo: `/setversion 1.1.0`",
            parse_mode="Markdown"
        )
        return

    nueva = context.args[0].strip()

    # Validación básica: x.x.x
    partes = nueva.split(".")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        await update.message.reply_text(
            "❌ Formato inválido. Debe ser `x.x.x`\n"
            "Ejemplo: `/setversion 1.1.0`",
            parse_mode="Markdown"
        )
        return

    _set_version(nueva)
    await update.message.reply_text(
        f"✅ Versión actualizada a *{nueva}*",
        parse_mode="Markdown"
  )

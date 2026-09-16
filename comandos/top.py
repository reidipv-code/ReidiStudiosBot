import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from core.db import DB_PATH, esta_registrado


def formatear_top(lista, valor_campo):
    """Recibe lista de tuplas y devuelve texto formateado con medallas."""
    medallas = ["🥇", "🥈", "🥉"]
    texto = ""

    for i, fila in enumerate(lista, start=1):
        nombre = fila[0]
        valor = fila[1]
        posicion = medallas[i - 1] if i <= 3 else f"{i}."

        if valor_campo == "tokens":
            texto += f"{posicion} *{nombre}* — {valor} tokens\n"
        elif valor_campo == "nivel":
            texto += f"{posicion} *{nombre}* — nivel {valor}\n"

    return texto


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/top tokens`, `/top nivel` o `/top all`",
            parse_mode="Markdown"
        )
        return

    opcion = context.args[0].lower().strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if opcion == "tokens":
        c.execute(
            "SELECT nombre, tokens FROM usuarios "
            "ORDER BY tokens DESC LIMIT 10"
        )
        lista = c.fetchall()
        conn.close()

        if not lista:
            await update.message.reply_text("📋 No hay usuarios.")
            return

        texto = "🏆 *TOP TOKENS*\n━━━━━━━━━━━━━━━━━━━\n"
        texto += formatear_top(lista, "tokens")
        await update.message.reply_text(texto, parse_mode="Markdown")

    elif opcion == "nivel":
        c.execute(
            "SELECT nombre, nivel FROM usuarios "
            "ORDER BY nivel DESC, xp DESC LIMIT 10"
        )
        lista = c.fetchall()
        conn.close()

        if not lista:
            await update.message.reply_text("📋 No hay usuarios.")
            return

        texto = "🏆 *TOP NIVEL*\n━━━━━━━━━━━━━━━━━━━\n"
        texto += formatear_top(lista, "nivel")
        await update.message.reply_text(texto, parse_mode="Markdown")

    elif opcion == "all":
        # Ranking combinado: nivel * 1000 + tokens
        c.execute(
            "SELECT nombre, nivel, tokens FROM usuarios "
            "ORDER BY (nivel * 1000 + tokens) DESC LIMIT 10"
        )
        lista = c.fetchall()
        conn.close()

        if not lista:
            await update.message.reply_text("📋 No hay usuarios.")
            return

        medallas = ["🥇", "🥈", "🥉"]
        texto = "🏆 *TOP GLOBAL*\n━━━━━━━━━━━━━━━━━━━\n"

        for i, (nombre, nivel, tokens) in enumerate(lista, start=1):
            posicion = medallas[i - 1] if i <= 3 else f"{i}."
            texto += (
                f"{posicion} *{nombre}*\n"
                f"    ⭐ Nivel {nivel} · 💰 {tokens} tokens\n"
            )

        await update.message.reply_text(texto, parse_mode="Markdown")

    else:
        conn.close()
        await update.message.reply_text(
            "⚠️ Uso: `/top tokens`, `/top nivel` o `/top all`",
            parse_mode="Markdown"
        )

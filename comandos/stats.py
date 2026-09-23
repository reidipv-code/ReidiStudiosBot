import sqlite3
import time
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from core.db import DB_PATH, esta_registrado


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Total de usuarios registrados
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = c.fetchone()[0]

    # Tokens en circulación
    c.execute("SELECT COALESCE(SUM(tokens), 0) FROM usuarios")
    total_tokens = c.fetchone()[0]

    # XP total
    c.execute("SELECT COALESCE(SUM(xp), 0) FROM usuarios")
    total_xp = c.fetchone()[0]

    # Usuarios online (últimos 5 minutos)
    hace_5_min = time.time() - (5 * 60)
    c.execute(
        "SELECT COUNT(*) FROM usuarios WHERE ultima_actividad > ?",
        (hace_5_min,)
    )
    usuarios_online = c.fetchone()[0]

    # Registrados hoy
    hoy = datetime.now().strftime("%Y-%m-%d")
    c.execute(
        "SELECT COUNT(*) FROM usuarios WHERE DATE(fecha_registro) = ?",
        (hoy,)
    )
    registrados_hoy = c.fetchone()[0]

    # Nivel más alto
    c.execute("SELECT MAX(nivel) FROM usuarios")
    nivel_max = c.fetchone()[0] or 0

    # Usuario con más tokens
    c.execute("SELECT nombre, tokens FROM usuarios ORDER BY tokens DESC LIMIT 1")
    top_tokens = c.fetchone()

    conn.close()

    texto = "📊 *ESTADÍSTICAS DEL BOT*\n"
    texto += "━━━━━━━━━━━━━━━━━━━\n\n"
    texto += f"👥 Usuarios registrados: *{total_usuarios}*\n"
    texto += f"🟢 Usuarios online: *{usuarios_online}*\n"
    texto += f"🆕 Registrados hoy: *{registrados_hoy}*\n\n"
    texto += f"💰 Tokens en circulación: *{total_tokens}*\n"
    texto += f"⭐ XP total acumulada: *{total_xp}*\n"
    texto += f"🎖️ Nivel más alto: *{nivel_max}*\n"

    if top_tokens:
        texto += f"\n🏆 *Rico del bot:* {top_tokens[0]} con {top_tokens[1]} tokens\n"

    await update.message.reply_text(texto, parse_mode="Markdown")

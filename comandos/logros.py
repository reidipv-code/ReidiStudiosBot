from telegram import Update
from telegram.ext import ContextTypes

from core.db import esta_registrado, obtener_datos
from core.logros import LOGROS, logros_de_usuario


async def logros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    datos = obtener_datos(user_id)
    nombre = datos[0]

    desbloqueados = set(logros_de_usuario(user_id))
    total = len(LOGROS)
    obtenidos = len(desbloqueados)

    texto = f"🏆 *LOGROS DE {nombre.upper()}*\n"
    texto += f"━━━━━━━━━━━━━━━━━━━\n"
    texto += f"📊 Progreso: *{obtenidos}/{total}*\n\n"

    for clave, info in LOGROS.items():
        if clave in desbloqueados:
            texto += f"✅ {info['emoji']} *{info['nombre']}*\n"
            texto += f"    _{info['descripcion']}_\n"
        else:
            texto += f"❌ {info['emoji']} {info['nombre']}\n"
            texto += f"    _{info['descripcion']}_\n"

    await update.message.reply_text(texto, parse_mode="Markdown")

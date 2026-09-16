from telegram import Update
from telegram.ext import ContextTypes

from core.db import esta_registrado
from core.misiones import (
    MISIONES,
    init_misiones_db,
    generar_misiones_dia,
    obtener_misiones,
    fecha_hoy,
)
from core.config import ahora


async def misiones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    # Generar las misiones del día si no las tiene
    generar_misiones_dia(user_id)

    lista = obtener_misiones(user_id)

    # Calcular tiempo hasta mañana
    from datetime import timedelta
    manana = (ahora() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    restante = manana - ahora()
    horas = restante.seconds // 3600
    minutos = (restante.seconds % 3600) // 60

    texto = "📋 *MISIONES DIARIAS*\n"
    texto += "━━━━━━━━━━━━━━━━━━━\n\n"

    completadas = 0
    for m_id, progreso, completada in lista:
        info = MISIONES.get(m_id)
        if not info:
            continue

        objetivo = info["objetivo"]
        recompensa = f"+{info['tokens']}💰"
        if info["xp"] > 0:
            recompensa += f" +{info['xp']}⭐"

        if completada:
            completadas += 1
            texto += f"✅ *{info['texto']}* ({objetivo}/{objetivo})\n"
            texto += f"    🎁 {recompensa} (reclamada)\n\n"
        else:
            texto += f"⏳ *{info['texto']}* ({progreso}/{objetivo})\n"
            texto += f"    🎁 {recompensa}\n\n"

    texto += f"━━━━━━━━━━━━━━━━━━━\n"
    texto += f"✅ Completadas: *{completadas}/5*\n"
    texto += f"🔄 Se reinician en: *{horas}h {minutos}m*"

    await update.message.reply_text(texto, parse_mode="Markdown")

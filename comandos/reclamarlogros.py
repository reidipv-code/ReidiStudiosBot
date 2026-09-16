from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_pais,
)
from core.logros import (
    LOGROS,
    dar_logro,
    logros_de_usuario,
)
from banco.banco import obtener_saldo_banco


async def reclamarlogros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    # Estado actual del usuario
    datos = obtener_datos(user_id)
    if datos is None:
        await update.message.reply_text("❌ No se pudieron obtener tus datos.")
        return

    nombre, id_interno, tokens, xp, nivel, sesion = datos
    saldo_banco = obtener_saldo_banco(user_id)

    desbloqueados = set(logros_de_usuario(user_id))
    nuevos = []

    # ─── Comprobaciones retroactivas ───────────────────────
    # 🌱 Primeros pasos (siempre, porque está registrado)
    if "primeros_pasos" not in desbloqueados:
        if dar_logro(user_id, "primeros_pasos"):
            nuevos.append("primeros_pasos")

    # ⭐ Nivel 5
    if nivel >= 5 and "nivel_5" not in desbloqueados:
        if dar_logro(user_id, "nivel_5"):
            nuevos.append("nivel_5")

    # 🌟 Nivel 10
    if nivel >= 10 and "nivel_10" not in desbloqueados:
        if dar_logro(user_id, "nivel_10"):
            nuevos.append("nivel_10")

    # 💫 Nivel 20
    if nivel >= 20 and "nivel_20" not in desbloqueados:
        if dar_logro(user_id, "nivel_20"):
            nuevos.append("nivel_20")

    # 💰 Rico (1000 tokens)
    if tokens >= 1000 and "rico" not in desbloqueados:
        if dar_logro(user_id, "rico"):
            nuevos.append("rico")

    # 💎 Millonario (10.000 tokens)
    if tokens >= 10000 and "millonario" not in desbloqueados:
        if dar_logro(user_id, "millonario"):
            nuevos.append("millonario")

    # 🏦 Banquero (4000 tokens en el banco)
    if saldo_banco >= 4000 and "banquero" not in desbloqueados:
        if dar_logro(user_id, "banquero"):
            nuevos.append("banquero")

    # ─── Avisar al usuario ─────────────────────────────────
    if not nuevos:
        await update.message.reply_text(
            "📋 *No tienes logros nuevos para reclamar.*\n\n"
            "Sigue jugando para desbloquear más.",
            parse_mode="Markdown"
        )
        return

    # Avisar de cada logro nuevo
    for clave in nuevos:
        info = LOGROS[clave]
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

    # Resumen final
    total = len(LOGROS)
    ahora_tiene = len(logros_de_usuario(user_id))

    await update.message.reply_text(
        f"🎉 *¡{len(nuevos)} logro(s) reclamado(s)!*\n\n"
        f"📊 Progreso actual: *{ahora_tiene}/{total}*",
        parse_mode="Markdown"
  )

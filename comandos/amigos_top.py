from telegram import Update
from telegram.ext import ContextTypes

from core.db import esta_registrado, obtener_datos
from core.amigos import lista_amigos


async def top_amigos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /top amigos → Ranking solo entre tus amigos.
    """
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    ids_amigos = lista_amigos(user_id)

    if not ids_amigos:
        await update.message.reply_text(
            "👥 *TOP AMIGOS*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "No tienes amigos todavía.\n\n"
            "Usa `/amigo add nombre` para añadir uno.",
            parse_mode="Markdown"
        )
        return

    # Incluirse a uno mismo
    ids_todos = ids_amigos + [user_id]

    # Cargar datos de cada uno
    personas = []
    for uid in ids_todos:
        datos = obtener_datos(uid)
        if datos is None:
            continue
        nombre, id_interno, tokens, xp, nivel, sesion = datos
        personas.append({
            "user_id": uid,
            "nombre": nombre,
            "tokens": tokens,
            "nivel": nivel,
            "es_tu": uid == user_id,
        })

    # Ordenar por puntuación combinada (nivel*1000 + tokens)
    personas.sort(key=lambda p: (p["nivel"] * 1000 + p["tokens"]), reverse=True)

    medallas = ["🥇", "🥈", "🥉"]
    texto = "👥 *TOP AMIGOS*\n"
    texto += "━━━━━━━━━━━━━━━━━━━\n\n"

    for i, p in enumerate(personas, start=1):
        posicion = medallas[i - 1] if i <= 3 else f"{i}."
        marca = " *(tú)*" if p["es_tu"] else ""
        texto += (
            f"{posicion} *{p['nombre']}*{marca}\n"
            f"    ⭐ Nivel {p['nivel']} · 💰 {p['tokens']} tokens\n"
        )

    await update.message.reply_text(texto, parse_mode="Markdown")

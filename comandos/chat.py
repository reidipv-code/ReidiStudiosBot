from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_user_id_por_nombre,
    obtener_pais,
    actualizar_tokens,
)
from core.paises import obtener_nombre as nombre_pais, obtener_bandera


# Enlace al grupo del chat mundial
CHAT_MUNDIAL_URL = "https://t.me/+pUmtMdKAkM8zMjFh"


async def chatm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/chatm → manda al usuario al grupo del chat mundial."""
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    await update.message.reply_text(
        "🌎 *CHAT MUNDIAL*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "Únete al grupo del chat mundial aquí:\n"
        f"{CHAT_MUNDIAL_URL}\n\n"
        "⚠️ Solo los usuarios registrados en el bot pueden entrar.\n"
        "El bot del grupo te pondrá tu etiqueta automáticamente.",
        parse_mode="Markdown"
    )


async def msp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /msp nombre| mensaje
    Envía un mensaje privado al usuario, mostrando quién lo manda.
    """
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/msp nombre| mensaje`\n\n"
            "Ejemplo: `/msp OriGamePlay| Hola, ¿cómo estás?`",
            parse_mode="Markdown"
        )
        return

    texto = " ".join(context.args)

    if "|" not in texto:
        await update.message.reply_text(
            "⚠️ Debes separar el nombre y el mensaje con `|`.\n\n"
            "Ejemplo: `/msp OriGamePlay| Hola`",
            parse_mode="Markdown"
        )
        return

    partes = texto.split("|", 1)
    nombre_destino = partes[0].strip()
    mensaje = partes[1].strip()

    if not nombre_destino or not mensaje:
        await update.message.reply_text(
            "⚠️ Debes poner el nombre y el mensaje.\n\n"
            "Ejemplo: `/msp OriGamePlay| Hola`",
            parse_mode="Markdown"
        )
        return

    destino_id = obtener_user_id_por_nombre(nombre_destino)

    if destino_id is None:
        await update.message.reply_text(
            f"❌ No existe ningún usuario con el nombre *{nombre_destino}*.",
            parse_mode="Markdown"
        )
        return

    # Datos del que envía
    datos_envia = obtener_datos(user_id)
    nombre_envia = datos_envia[0] if datos_envia else "Desconocido"
    pais_envia = obtener_pais(user_id)
    bandera_envia = obtener_bandera(pais_envia) if pais_envia else "🌎"

    # Construir el mensaje con el formato: 🇨🇺 OriGamePlay ~ Hola
    texto_final = f"{bandera_envia} {nombre_envia} ~ {mensaje}"

    try:
        await context.bot.send_message(
            chat_id=destino_id,
            text=texto_final
        )
        await update.message.reply_text(
            f"✅ Mensaje enviado a *{nombre_destino}*.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ No se pudo enviar: {e}")


async def darTokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /darTokens nombre cantidad mensaje
    Transfiere tokens del usuario que lo usa al usuario indicado,
    y le envía un mensaje tipo carta.
    """
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero.\n\nUsa: /reg nombre.pais"
        )
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ Uso: `/darTokens nombre cantidad mensaje`\n\n"
            "Ejemplo: `/darTokens Diana 10 Lo que te debía`",
            parse_mode="Markdown"
        )
        return

    nombre_destino = context.args[0].strip()

    try:
        cantidad = int(context.args[1])
    except ValueError:
        await update.message.reply_text(
            "❌ La cantidad debe ser un número entero.\n\n"
            "Ejemplo: `/darTokens Diana 10 Lo que te debía`",
            parse_mode="Markdown"
        )
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La cantidad debe ser mayor que 0.")
        return

    mensaje = " ".join(context.args[2:]).strip()

    if not mensaje:
        await update.message.reply_text(
            "⚠️ Debes escribir un mensaje.\n\n"
            "Ejemplo: `/darTokens Diana 10 Lo que te debía`",
            parse_mode="Markdown"
        )
        return

    # Datos del que envía
    datos_envia = obtener_datos(user_id)
    if datos_envia is None:
        await update.message.reply_text("❌ No se pudieron obtener tus datos.")
        return

    tokens_envia = datos_envia[2]
    nombre_envia = datos_envia[0]

    if tokens_envia < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes tokens.\n"
            f"Tienes *{tokens_envia}* y quieres dar *{cantidad}*.",
            parse_mode="Markdown"
        )
        return

    # Buscar al destinatario
    destino_id = obtener_user_id_por_nombre(nombre_destino)

    if destino_id is None:
        await update.message.reply_text(
            f"❌ No existe ningún usuario con el nombre *{nombre_destino}*.",
            parse_mode="Markdown"
        )
        return

    if destino_id == user_id:
        await update.message.reply_text("❌ No puedes enviarte tokens a ti mismo.")
        return

    # Transferir tokens
    actualizar_tokens(user_id, -cantidad)
    actualizar_tokens(destino_id, cantidad)

    # Datos del emisor para el mensaje
    pais_envia = obtener_pais(user_id)
    bandera_envia = obtener_bandera(pais_envia) if pais_envia else "🌎"

    # Enviar al destinatario
    texto_carta = (
        f"💰 *HAS RECIBIDO TOKENS*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{bandera_envia} {nombre_envia} te ha enviado *{cantidad}* tokens.\n\n"
        f"📝 *Mensaje:*\n{mensaje}"
    )

    try:
        await context.bot.send_message(
            chat_id=destino_id,
            text=texto_carta,
            parse_mode="Markdown"
        )
    except Exception as e:
        # Si falla el envío, devolvemos los tokens
        actualizar_tokens(user_id, cantidad)
        actualizar_tokens(destino_id, -cantidad)
        await update.message.reply_text(f"❌ No se pudo enviar: {e}")
        return

    # Confirmación al emisor
    await update.message.reply_text(
        f"✅ Le has enviado *{cantidad}* tokens a *{nombre_destino}*.\n\n"
        f"📝 Mensaje: _{mensaje}_",
        parse_mode="Markdown"
        )

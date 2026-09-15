import sqlite3
from dotenv import load_dotenv
import os

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    ApplicationHandlerStop
)

from core.db import DB_PATH

load_dotenv()

TOKEN = os.getenv("CHAT_BOT_TOKEN")
CHAT_MUNDIAL_ID = -1003922399103


def obtener_datos_usuario(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombre, pais FROM usuarios WHERE user_id = ?", (user_id,))
        r = c.fetchone()
        conn.close()
        return (r[0], r[1]) if r else (None, None)
    except Exception as e:
        print(f"[CHAT] Error BD: {e}")
        return (None, None)


def construir_etiqueta(nombre, pais):
    if not nombre or not pais:
        return ""
    codigo = pais.upper()[:3]
    etiqueta = f"[{codigo}] {nombre}"
    return etiqueta[:16]


async def on_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.chat_member:
        return

    chat = update.chat_member.chat
    if chat.id != CHAT_MUNDIAL_ID:
        return

    user = update.chat_member.new_chat_member.user
    user_id = user.id

    if user.is_bot:
        return

    viejo = update.chat_member.old_chat_member.status
    nuevo = update.chat_member.new_chat_member.status

    if viejo in ("left", "kicked") and nuevo in ("member", "administrator", "creator"):
        nombre, pais = obtener_datos_usuario(user_id)

        if nombre is None:
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=user_id)
                await context.bot.unban_chat_member(chat_id=chat.id, user_id=user_id)
                print(f"[CHAT] Expulsado {user_id} - no registrado")
            except Exception as e:
                print(f"[CHAT] Error al expulsar: {e}")
            raise ApplicationHandlerStop
        else:
            etiqueta = construir_etiqueta(nombre, pais)
            if etiqueta:
                try:
                    await context.bot.set_chat_member_tag(
                        chat_id=chat.id, user_id=user_id, tag=etiqueta
                    )
                    print(f"[CHAT] Etiqueta puesta a {user_id}: {etiqueta}")
                except Exception as e:
                    print(f"[CHAT] Error etiqueta: {e}")

            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"👋 Bienvenido/a *{nombre}* ({pais.upper()})",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    elif viejo in ("member", "administrator", "creator") and nuevo in ("left", "kicked"):
        try:
            await context.bot.set_chat_member_tag(
                chat_id=chat.id, user_id=user_id, tag=""
            )
        except Exception:
            pass


async def bloquear_comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    if update.effective_chat.id != CHAT_MUNDIAL_ID:
        return

    texto = update.message.text.strip()

    if texto.startswith("/"):
        await update.message.reply_text(
            "⚠️ Los comandos solo funcionan en privado con @ReidiStudiosBot.",
            parse_mode="Markdown"
        )
        raise ApplicationHandlerStop


def crear_app():
    """Crea la Application del bot del chat sin arrancarla."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        ChatMemberHandler(on_chat_member, ChatMemberHandler.CHAT_MEMBER),
        group=0
    )
    app.add_handler(
        MessageHandler(filters.ALL, bloquear_comandos),
        group=1
    )

    return app


async def iniciar_chat_bot():
    """Se llama desde start.py para arrancar el bot del chat de forma asíncrona."""
    app = crear_app()
    print("✅ Bot del chat corriendo...")
    await app.initialize()
    await app.updater.start_polling()
    await app.start()

import sqlite3
from dotenv import load_dotenv
import os

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    ApplicationHandlerStop,
    CommandHandler,
    filters
)

from core.db import DB_PATH

load_dotenv()

TOKEN = os.getenv("CHAT_BOT_TOKEN")
CHAT_MUNDIAL_ID = -1003922399103
ADMIN_ID = 7669914531


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
    return f"[{pais.upper()[:3]}] {nombre}"[:16]


async def diagnostico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"[DIAG] Update recibido:")
    print(f"[DIAG]   update_id: {update.update_id}")
    print(f"[DIAG]   message={bool(update.message)} "
          f"chat_member={bool(update.chat_member)} "
          f"my_chat_member={bool(update.my_chat_member)}")

    if update.message:
        msg = update.message
        print(f"[DIAG]   chat_id: {msg.chat.id}")
        print(f"[DIAG]   texto: {msg.text}")
        print(f"[DIAG]   new_chat_members: {msg.new_chat_members}")
        print(f"[DIAG]   left_chat_member: {msg.left_chat_member}")


async def procesar_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.message.chat
    if chat.id != CHAT_MUNDIAL_ID:
        return

    for user in update.message.new_chat_members:
        if user.is_bot:
            continue

        print(f"[CHAT] Entró: {user.id} ({user.full_name})")
        nombre, pais = obtener_datos_usuario(user.id)

        if nombre is None:
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
                await context.bot.unban_chat_member(chat_id=chat.id, user_id=user.id)
                print(f"[CHAT] Expulsado {user.id} - no registrado")
            except Exception as e:
                print(f"[CHAT] Error al expulsar: {e}")
        else:
            etiqueta = construir_etiqueta(nombre, pais)
            try:
                await context.bot.set_chat_member_tag(
                    chat_id=chat.id, user_id=user.id, tag=etiqueta
                )
                print(f"[CHAT] Etiqueta puesta a {user.id}: {etiqueta}")
            except Exception as e:
                print(f"[CHAT] Error etiqueta: {e}")


async def procesar_salida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.left_chat_member:
        return

    chat = update.message.chat
    if chat.id != CHAT_MUNDIAL_ID:
        return

    user = update.message.left_chat_member
    if user.is_bot:
        return

    print(f"[CHAT] Salió: {user.id} ({user.full_name})")
    try:
        await context.bot.set_chat_member_tag(chat_id=chat.id, user_id=user.id, tag="")
    except Exception:
        pass


async def on_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"[CHAT] on_chat_member disparado")
    if not update.chat_member:
        return

    chat = update.chat_member.chat
    if chat.id != CHAT_MUNDIAL_ID:
        return

    user = update.chat_member.new_chat_member.user
    if user.is_bot:
        return

    viejo = update.chat_member.old_chat_member.status
    nuevo = update.chat_member.new_chat_member.status
    print(f"[CHAT] Evento: user={user.id} viejo={viejo} nuevo={nuevo}")

    if viejo in ("left", "kicked") and nuevo in ("member", "administrator", "creator"):
        nombre, pais = obtener_datos_usuario(user.id)
        if nombre is None:
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
                await context.bot.unban_chat_member(chat_id=chat.id, user_id=user.id)
            except Exception as e:
                print(f"[CHAT] Error expulsar: {e}")
        else:
            etiqueta = construir_etiqueta(nombre, pais)
            try:
                await context.bot.set_chat_member_tag(
                    chat_id=chat.id, user_id=user.id, tag=etiqueta
                )
                print(f"[CHAT] Etiqueta puesta: {etiqueta}")
            except Exception as e:
                print(f"[CHAT] Error etiqueta: {e}")

    elif viejo in ("member", "administrator", "creator") and nuevo in ("left", "kicked"):
        try:
            await context.bot.set_chat_member_tag(chat_id=chat.id, user_id=user.id, tag="")
        except Exception:
            pass


async def poner_etiquetas_manual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != CHAT_MUNDIAL_ID:
        return

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo el admin.")
        return

    await update.message.reply_text("Poniendo etiquetas...")

    puestos = 0
    fallidos = 0

    try:
        admins = await context.bot.get_chat_administrators(chat_id=CHAT_MUNDIAL_ID)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    for miembro in admins:
        uid = miembro.user.id
        if miembro.user.is_bot:
            continue

        nombre, pais = obtener_datos_usuario(uid)
        if nombre is None:
            continue

        etiqueta = construir_etiqueta(nombre, pais)
        try:
            await context.bot.set_chat_member_tag(
                chat_id=CHAT_MUNDIAL_ID, user_id=uid, tag=etiqueta
            )
            puestos += 1
            print(f"[CHAT] Etiqueta manual a {uid}: {etiqueta}")
        except Exception as e:
            fallidos += 1
            print(f"[CHAT] Error manual a {uid}: {e}")

    await update.message.reply_text(f"Puestas: {puestos} Fallidas: {fallidos}")


async def bloquear_comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    if update.effective_chat.id != CHAT_MUNDIAL_ID:
        return

    texto = update.message.text.strip()

    if texto.startswith("/etiquetas"):
        return

    if texto.startswith("/"):
        await update.message.reply_text(
            "Los comandos solo funcionan en privado con @ReidiStudiosBot."
        )
        raise ApplicationHandlerStop


def crear_app():
    app = Application.builder().token(TOKEN).build()

    # DIAGNÓSTICO: se ejecuta con CUALQUIER update
    app.add_handler(MessageHandler(filters.ALL, diagnostico), group=-100)

    # Procesar entradas y salidas (eventos viejos dentro de message)
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, procesar_entrada),
        group=0
    )
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, procesar_salida),
        group=1
    )

    # Evento nuevo chat_member (por si llega)
    app.add_handler(
        ChatMemberHandler(on_chat_member, ChatMemberHandler.CHAT_MEMBER),
        group=2
    )

    # Comando /etiquetas
    app.add_handler(
        CommandHandler("etiquetas", poner_etiquetas_manual),
        group=3
    )

    # Bloquear comandos en el grupo
    app.add_handler(
        MessageHandler(filters.ALL, bloquear_comandos),
        group=4
    )

    return app


async def iniciar_chat_bot():
    app = crear_app()
    print("Bot del chat corriendo...")
    await app.initialize()
    await app.updater.start_polling(
        allowed_updates=["message", "chat_member", "my_chat_member"]
    )
    await app.start()

from telegram import Update
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado, obtener_datos, obtener_lista_usuarios,
    xp_acumulada_actual, xp_para_siguiente_nivel, rango_por_nivel, barra_progreso,
    obtener_pais, obtener_user_id_por_nombre, esta_online
)
from core.paises import obtener_nombre as nombre_pais, obtener_bandera
from core.logros import LOGROS, logros_de_usuario
from core.tienda import equipados_usuario


async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate con /reg nombre.pais")
        return

    # Si hay argumento, mostrar el perfil de OTRO usuario
    if context.args:
        nombre_buscado = " ".join(context.args).strip()
        otro_id = obtener_user_id_por_nombre(nombre_buscado)

        if otro_id is None:
            await update.message.reply_text(
                f"❌ No existe ningún usuario con el nombre *{nombre_buscado}*.",
                parse_mode="Markdown"
            )
            return

        datos = obtener_datos(otro_id)
        if datos is None:
            await update.message.reply_text("❌ No se pudo obtener el perfil.")
            return

        nombre, id_interno, tokens, xp, nivel, sesion = datos
        pais = obtener_pais(otro_id)
        if pais:
            bandera = obtener_bandera(pais)
            nombre_pais_str = nombre_pais(pais)
            linea_pais = f"{bandera} País: *{nombre_pais_str}*"
        else:
            linea_pais = "🌎 País: *No configurado*"

        estado = "🟢 Online" if esta_online(otro_id) else "⚫ Offline"

        logros_usr = logros_de_usuario(otro_id)
        total_logros = len(LOGROS)
        linea_logros = f"🏆 Logros: *{len(logros_usr)}/{total_logros}*"

        await update.message.reply_text(
            f"👤 *PERFIL DE {nombre.upper()}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: *#{id_interno}*\n"
            f"{linea_pais}\n"
            f"🎖️ Rango: {rango_por_nivel(nivel)}\n"
            f"⭐ Nivel: *{nivel}*\n"
            f"{linea_logros}\n"
            f"{estado}",
            parse_mode="Markdown"
        )
        return

    # Sin argumento: mostrar el perfil PROPIO completo
    datos = obtener_datos(user_id)
    nombre, id_interno, tokens, xp, nivel, sesion = datos
    barra = barra_progreso(xp, nivel)
    xp_actual_total = xp_acumulada_actual(xp, nivel)
    xp_siguiente = xp_para_siguiente_nivel(nivel)
    pais = obtener_pais(user_id)
    if pais:
        bandera = obtener_bandera(pais)
        nombre_pais_str = nombre_pais(pais)
        linea_pais = f"\n{bandera} País: *{nombre_pais_str}*"
    else:
        linea_pais = "\n🌎 País: *No configurado*"

    estado = "🟢 Online" if esta_online(user_id) else "⚫ Offline"

    equipados = equipados_usuario(user_id)
    cosmeticos = ""
    for tipo, etiqueta in (("titulo", "🏷️ Título"), ("marco", "🖼️ Marco"), ("efecto", "✨ Efecto"), ("marco_animado", "🔥 Marco animado"), ("fondo", "🌌 Fondo"), ("color", "🎨 Color"), ("insignia", "🏅 Insignia")):
        if tipo in equipados and equipados[tipo]:
            cosmeticos += f"\n{etiqueta}: *{equipados[tipo]['nombre']}*"

    logros_usr = logros_de_usuario(user_id)
    total_logros = len(LOGROS)

    # Mostrar los emojis de los logros desbloqueados
    emojis_logros = ""
    if logros_usr:
        emojis_logros = "\n\n🏆 *Logros:* "
        for clave in logros_usr:
            if clave in LOGROS:
                emojis_logros += LOGROS[clave]["emoji"] + " "
        emojis_logros += f"\n({len(logros_usr)}/{total_logros})"

    await update.message.reply_text(
        f"👤 *{nombre.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: *#{id_interno}*\n"
        f"🔑 Telegram: `{user_id}`\n"
        f"🎖️ {rango_por_nivel(nivel)}\n"
        f"⭐ Nivel: *{nivel}*\n"
        f"✨ XP: {xp_actual_total}/{xp_siguiente}\n"
        f"📊 {barra}\n"
        f"💰 {tokens} tokens"
        f"{cosmeticos}"
        f"{linea_pais}\n"
        f"{estado}"
        f"{emojis_logros}",
        parse_mode="Markdown"
    )


async def tokens_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    await update.message.reply_text(f"💰 *{datos[2]}* tokens", parse_mode="Markdown")


async def nivel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    nombre, _, _, xp, nivel, _ = datos
    xp_actual_total = xp_acumulada_actual(xp, nivel)
    xp_siguiente = xp_para_siguiente_nivel(nivel)
    await update.message.reply_text(
        f"⭐ *{nombre}* - Nivel {nivel}\n"
        f"✨ XP: {xp_actual_total}/{xp_siguiente}\n"
        f"📊 {barra_progreso(xp, nivel)}",
        parse_mode="Markdown"
    )


async def rango_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return
    datos = obtener_datos(user_id)
    await update.message.reply_text(
        f"🎖️ {rango_por_nivel(datos[4])}",
        parse_mode="Markdown"
    )


async def userslist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not esta_registrado(user_id):
        await update.message.reply_text("⚠️ Primero regístrate.")
        return

    lista = obtener_lista_usuarios()
    if not lista:
        await update.message.reply_text("📋 No hay usuarios registrados.")
        return

    texto = "📋 *USUARIOS*\n━━━━━━━━━━━━━━━━━━━\n"
    for id_interno, nombre in lista:
        texto += f"#{id_interno} - {nombre}\n"
    texto += f"\n👥 Total: *{len(lista)}*"
    await update.message.reply_text(texto, parse_mode="Markdown")

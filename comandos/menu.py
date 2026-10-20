# comandos/menu.py

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from comandos.lang import teclado_idiomas
from core.idiomas import obtener_idioma, IDIOMAS
from core.razas_clases import personaje_completo


# ============================================================
# TECLADOS
# ============================================================

def boton(texto: str, destino: str) -> InlineKeyboardButton:
    """Crea un botón interno del menú."""
    return InlineKeyboardButton(
        texto,
        callback_data=f"menu_{destino}",
    )


def teclado_menu():
    """Menú principal con las categorías en el orden solicitado."""

    return InlineKeyboardMarkup([
        [
            boton("👤 Mi Perfil", "perfil"),
        ],
        [
            boton("🤝 Social", "social"),
        ],
        [
            boton("✉️ Mensajes", "mensajes"),
        ],
        [
            boton("🗺️ Mapa", "mapa"),
        ],
        [
            boton("⚙️ Configuración", "configuracion"),
        ],
    ])


def teclado_perfil():
    """Opciones de Mi Perfil."""

    return InlineKeyboardMarkup([
        [
            boton("👤 Perfil", "ver_perfil"),
        ],
        [
            boton("🎒 Inventario", "inventario"),
        ],
        [
            boton("✨ Habilidades", "habilidades"),
        ],
        [
            boton("⬅️ Volver al menú", "inicio"),
        ],
    ])


def teclado_social():
    """Opciones de Social."""

    return InlineKeyboardMarkup([
        [
            boton("👥 Amigos", "amigos"),
        ],
        [
            boton("⚔️ Grupo", "grupo"),
        ],
        [
            boton("🏰 Gremio", "gremio"),
        ],
        [
            boton("⬅️ Volver al menú", "inicio"),
        ],
    ])


def teclado_configuracion():
    """Opciones de Configuración."""

    return InlineKeyboardMarkup([
        [
            boton("📖 Ayuda", "ayuda"),
        ],
        [
            boton("🌐 Idioma", "idioma"),
        ],
        [
            boton("🔌 Desconectar", "desconectar"),
        ],
        [
            boton("⬅️ Volver al menú", "inicio"),
        ],
    ])


def teclado_volver(destino: str = "inicio"):
    """Teclado sencillo para regresar."""

    return InlineKeyboardMarkup([
        [
            boton("⬅️ Volver", destino),
        ],
    ])


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

async def menu_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Muestra el menú principal."""

    mensaje = update.effective_message
    usuario = update.effective_user

    if not mensaje or not usuario:
        return

    idioma = obtener_idioma(usuario.id)

    informacion_idioma = IDIOMAS.get(
        idioma,
        {"native": "Español"},
    )

    nombre_idioma = informacion_idioma["native"]

    if personaje_completo(usuario.id):
        texto = (
            "⚔️ MENÚ PRINCIPAL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🌐 Idioma: {nombre_idioma}\n\n"
            "Selecciona una categoría:\n\n"
            "👤 Mi Perfil\n"
            "🤝 Social\n"
            "✉️ Mensajes\n"
            "🗺️ Mapa\n"
            "⚙️ Configuración"
        )

    else:
        texto = (
            "⚔️ MENÚ PRINCIPAL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🌐 Idioma: {nombre_idioma}\n\n"
            "Antes de entrar al MMORPG, completa el registro "
            "de cuatro pasos:\n\n"
            "1️⃣ Selecciona el idioma con /lang.\n"
            "2️⃣ Registra tu nombre y país con /reg Nombre.Pais.\n"
            "3️⃣ Selecciona tu raza.\n"
            "4️⃣ Selecciona una clase compatible.\n\n"
            "Después podrás acceder a las categorías del menú."
        )

    await mensaje.reply_text(
        texto,
        reply_markup=teclado_menu(),
    )


# ============================================================
# PROCESAR BOTONES DEL MENÚ
# ============================================================

async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Gestiona las categorías y las opciones del menú."""

    query = update.callback_query

    if not query:
        return

    data = query.data or ""

    await query.answer()

    usuario = query.from_user
    user_id = usuario.id

    # --------------------------------------------------------
    # VOLVER AL MENÚ PRINCIPAL
    # --------------------------------------------------------

    if data == "menu_inicio":

        idioma = obtener_idioma(user_id)

        informacion_idioma = IDIOMAS.get(
            idioma,
            {"native": "Español"},
        )

        nombre_idioma = informacion_idioma["native"]

        if personaje_completo(user_id):
            texto = (
                "⚔️ MENÚ PRINCIPAL\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"🌐 Idioma: {nombre_idioma}\n\n"
                "Selecciona una categoría:"
            )

        else:
            texto = (
                "⚔️ MENÚ PRINCIPAL\n\n"
                f"🌐 Idioma: {nombre_idioma}\n\n"
                "Completa los cuatro pasos del registro:\n\n"
                "1️⃣ /lang\n"
                "2️⃣ /reg Nombre.Pais\n"
                "3️⃣ Seleccionar raza\n"
                "4️⃣ Seleccionar clase compatible"
            )

        await query.edit_message_text(
            texto,
            reply_markup=teclado_menu(),
        )

        return

    # --------------------------------------------------------
    # MI PERFIL
    # --------------------------------------------------------

    if data == "menu_perfil":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Todavía no tienes un personaje completo.\n\n"
                "Primero selecciona tu idioma con /lang.\n"
                "Después registra tu nombre y país con:\n"
                "/reg Nombre.Pais\n\n"
                "Finalmente, selecciona una raza y una clase.",
                reply_markup=teclado_volver(),
            )
            return

        await query.edit_message_text(
            "👤 MI PERFIL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona una opción:\n\n"
            "👤 Perfil: consulta los datos de tu personaje.\n"
            "🎒 Inventario: consulta tus objetos.\n"
            "✨ Habilidades: consulta tus habilidades.",
            reply_markup=teclado_perfil(),
        )

        return

    # --------------------------------------------------------
    # PERFIL DEL PROPIO JUGADOR
    # --------------------------------------------------------

    if data == "menu_ver_perfil":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Primero debes completar el registro "
                "de tu personaje.",
                reply_markup=teclado_volver("perfil"),
            )
            return

        await query.edit_message_text(
            "👤 TU PERFIL\n\n"
            "Para consultar los datos de tu personaje, "
            "utiliza el comando:\n\n"
            "/perfil\n\n"
            "Puedes regresar a Mi Perfil con el botón inferior.",
            reply_markup=teclado_volver("perfil"),
        )

        return

    # --------------------------------------------------------
    # INVENTARIO
    # --------------------------------------------------------

    if data == "menu_inventario":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder al inventario.",
                reply_markup=teclado_volver("perfil"),
            )
            return

        await query.edit_message_text(
            "🎒 INVENTARIO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Esta opción está reservada para el sistema "
            "de inventario del MMORPG.\n\n"
            "El menú ya tiene preparada la entrada, pero "
            "necesita conectarse al módulo que administra "
            "los objetos del personaje.",
            reply_markup=teclado_volver("perfil"),
        )

        return

    # --------------------------------------------------------
    # HABILIDADES
    # --------------------------------------------------------

    if data == "menu_habilidades":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder a las habilidades.",
                reply_markup=teclado_volver("perfil"),
            )
            return

        await query.edit_message_text(
            "✨ HABILIDADES\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Esta opción está reservada para el sistema "
            "de habilidades del MMORPG.\n\n"
            "El menú ya tiene preparada la entrada, pero "
            "necesita conectarse al módulo de habilidades.",
            reply_markup=teclado_volver("perfil"),
        )

        return

    # --------------------------------------------------------
    # SOCIAL
    # --------------------------------------------------------

    if data == "menu_social":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder a las funciones sociales.",
                reply_markup=teclado_volver(),
            )
            return

        await query.edit_message_text(
            "🤝 SOCIAL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona una opción:\n\n"
            "👥 Amigos\n"
            "⚔️ Grupo\n"
            "🏰 Gremio",
            reply_markup=teclado_social(),
        )

        return

    # --------------------------------------------------------
    # AMIGOS
    # --------------------------------------------------------

    if data == "menu_amigos":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder a Amigos.",
                reply_markup=teclado_volver("social"),
            )
            return

        await query.edit_message_text(
            "👥 AMIGOS\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Utiliza /amigos para consultar tus amigos.\n\n"
            "Puedes regresar a Social con el botón inferior.",
            reply_markup=teclado_volver("social"),
        )

        return

    # --------------------------------------------------------
    # GRUPO
    # --------------------------------------------------------

    if data == "menu_grupo":

        await query.edit_message_text(
            "⚔️ GRUPO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Esta opción está reservada para el sistema "
            "de grupos del MMORPG.\n\n"
            "El menú ya tiene preparada la entrada, pero "
            "necesita conectarse al módulo de grupos.",
            reply_markup=teclado_volver("social"),
        )

        return

    # --------------------------------------------------------
    # GREMIO
    # --------------------------------------------------------

    if data == "menu_gremio":

        await query.edit_message_text(
            "🏰 GREMIO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Esta opción está reservada para el sistema "
            "de gremios del MMORPG.\n\n"
            "El menú ya tiene preparada la entrada, pero "
            "necesita conectarse al módulo de gremios.",
            reply_markup=teclado_volver("social"),
        )

        return

    # --------------------------------------------------------
    # MENSAJES
    # --------------------------------------------------------

    if data == "menu_mensajes":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder a Mensajes.",
                reply_markup=teclado_volver(),
            )
            return

        await query.edit_message_text(
            "✉️ MENSAJES\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Aquí estará tu bandeja de mensajes privados "
            "y el historial de conversaciones.\n\n"
            "Esta entrada necesita conectarse al sistema "
            "de mensajería del MMORPG.",
            reply_markup=teclado_volver(),
        )

        return

    # --------------------------------------------------------
    # MAPA
    # --------------------------------------------------------

    if data == "menu_mapa":

        if not personaje_completo(user_id):
            await query.edit_message_text(
                "🔒 Debes completar el registro antes "
                "de acceder al mapa.",
                reply_markup=teclado_volver(),
            )
            return

        await query.edit_message_text(
            "🗺️ MAPA\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Aquí estará el mapa del MMORPG.\n\n"
            "La exploración se realizará mediante botones "
            "para desplazarte entre las distintas zonas.\n\n"
            "Esta entrada necesita conectarse al sistema "
            "de mapas y exploración.",
            reply_markup=teclado_volver(),
        )

        return

    # --------------------------------------------------------
    # CONFIGURACIÓN
    # --------------------------------------------------------

    if data == "menu_configuracion":

        await query.edit_message_text(
            "⚙️ CONFIGURACIÓN\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona una opción:\n\n"
            "📖 Ayuda\n"
            "🌐 Idioma\n"
            "🔌 Desconectar",
            reply_markup=teclado_configuracion(),
        )

        return

    # --------------------------------------------------------
    # AYUDA
    # --------------------------------------------------------

    if data == "menu_ayuda":

        await query.edit_message_text(
            "📖 AYUDA\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "/start — Iniciar el bot.\n"
            "/lang — Seleccionar o cambiar idioma.\n"
            "/menu — Abrir el menú principal.\n"
            "/reg Nombre.Pais — Registrar nombre y país.\n"
            "/perfil — Consultar tu personaje.\n"
            "/amigos — Consultar tus amigos.\n"
            "/help — Consultar la ayuda general.\n\n"
            "Registro del MMORPG:\n"
            "1. Seleccionar idioma.\n"
            "2. Registrar nombre y país.\n"
            "3. Elegir raza.\n"
            "4. Elegir una clase compatible.",
            reply_markup=teclado_volver("configuracion"),
        )

        return

    # --------------------------------------------------------
    # IDIOMA
    # --------------------------------------------------------

    if data == "menu_idioma" or data == "menu_lang":

        idioma = obtener_idioma(user_id)

        informacion_idioma = IDIOMAS.get(
            idioma,
            {"native": "Español"},
        )

        nombre_idioma = informacion_idioma["native"]

        await query.edit_message_text(
            "🌐 IDIOMA DEL BOT\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"Idioma actual: {nombre_idioma}\n\n"
            "Selecciona un idioma de la lista.\n\n"
            "También puedes utilizar:\n"
            "/lang español\n"
            "/lang spanish\n"
            "/lang English\n"
            "/lang 日本語",
            reply_markup=teclado_idiomas(),
        )

        return

    # --------------------------------------------------------
    # DESCONECTAR
    # --------------------------------------------------------

    if data == "menu_desconectar":

        await query.edit_message_text(
            "🔌 DESCONECTAR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "La opción de desconexión está preparada "
            "en el menú, pero todavía necesita conectarse "
            "al sistema de sesiones del bot.\n\n"
            "Esta opción no eliminará tu registro ni "
            "tu progreso.",
            reply_markup=teclado_volver("configuracion"),
        )

        return
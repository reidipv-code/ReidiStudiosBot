# comandos/menu.py
# Menú principal de ReidiStudiosBot
# Perfil accesible desde el menú, sin utilizar /perfil.

import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from core.idiomas import (
    obtener_idioma,
    IDIOMAS,
)
from core.razas_clases import (
    personaje_completo,
    obtener_personaje,
    habilidades_de_personaje,
)

logger = logging.getLogger(__name__)


# ============================================================
# TECLADOS
# ============================================================

def boton(texto: str, destino: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=texto,
        callback_data=f"menu_{destino}",
    )


def teclado_menu():
    return InlineKeyboardMarkup([
        [boton("👤 Mi Perfil", "perfil")],
        [boton("🤝 Social", "social")],
        [boton("✉️ Mensajes", "mensajes")],
        [boton("🗺️ Mapa", "mapa")],
        [boton("⚙️ Configuración", "configuracion")],
    ])


def teclado_perfil():
    return InlineKeyboardMarkup([
        [boton("👤 Perfil", "ver_perfil")],
        [boton("🎒 Inventario", "inventario")],
        [boton("✨ Habilidades", "habilidades")],
        [boton("⬅️ Volver al menú", "inicio")],
    ])


def teclado_social():
    return InlineKeyboardMarkup([
        [boton("👥 Amigos", "amigos")],
        [boton("⚔️ Grupo", "grupo")],
        [boton("🏰 Gremio", "gremio")],
        [boton("⬅️ Volver al menú", "inicio")],
    ])


def teclado_configuracion():
    return InlineKeyboardMarkup([
        [boton("📖 Ayuda", "ayuda")],
        [boton("🌐 Idioma", "idioma")],
        [boton("🔌 Desconectar", "desconectar")],
        [boton("⬅️ Volver al menú", "inicio")],
    ])


def teclado_volver(destino="inicio"):
    return InlineKeyboardMarkup([
        [boton("⬅️ Volver", destino)],
    ])


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def nombre_idioma_usuario(user_id: int) -> str:
    codigo = obtener_idioma(user_id)
    informacion = IDIOMAS.get(codigo, IDIOMAS["es"])
    return informacion.get("native", "Español")


def texto_menu(user_id: int) -> str:
    idioma = nombre_idioma_usuario(user_id)

    if personaje_completo(user_id):
        return (
            "⚔️ MENÚ PRINCIPAL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🌐 Idioma: {idioma}\n\n"
            "Selecciona una categoría:"
        )

    return (
        "⚔️ MENÚ PRINCIPAL\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 Idioma: {idioma}\n\n"
        "Antes de entrar al MMORPG, completa el registro:\n\n"
        "1️⃣ Selecciona el idioma con /lang.\n"
        "2️⃣ Registra tu nombre y país con /reg Nombre.Pais.\n"
        "3️⃣ Selecciona tu raza.\n"
        "4️⃣ Selecciona una clase compatible.\n\n"
        "Después podrás acceder a las categorías del menú."
    )


async def editar_menu(
    query,
    texto: str,
    teclado=None,
):
    """Edita el mensaje actual y evita errores por textos idénticos."""

    try:
        await query.edit_message_text(
            texto,
            reply_markup=teclado,
        )
    except Exception as error:
        if "Message is not modified" not in str(error):
            logger.exception("No se pudo actualizar el menú: %s", error)


async def requiere_personaje(query, user_id, destino="inicio"):
    """Bloquea las secciones RPG si el registro está incompleto."""

    if personaje_completo(user_id):
        return True

    await editar_menu(
        query,
        "🔒 Todavía no tienes un personaje completo.\n\n"
        "Completa los pasos del registro:\n\n"
        "1️⃣ /lang español\n"
        "2️⃣ /reg Nombre.Pais\n"
        "3️⃣ Selecciona una raza.\n"
        "4️⃣ Selecciona una clase compatible.",
        teclado_volver(destino),
    )
    return False


# ============================================================
# PERFIL DEL JUGADOR
# ============================================================

def construir_texto_perfil(user_id: int) -> str:
    """
    Construye el perfil del jugador usando los datos existentes.

    Las estadísticas solo se muestran al propio jugador.
    """

    from core.db import obtener_datos
    from comandos.registro_rpg import (
        CLASES,
        rango_por_nivel,
        barra_progreso,
        xp_acumulada_actual,
        xp_para_siguiente_nivel,
    )

    datos = obtener_datos(user_id)
    personaje = obtener_personaje(user_id)

    if not datos or not personaje:
        return (
            "❌ No se pudieron cargar los datos del personaje.\n\n"
            "Comprueba que el registro esté completo."
        )

    nombre = datos[0]

    try:
        _, id_interno, tokens, xp, nivel, sesion = datos
    except (ValueError, TypeError):
        logger.exception("Formato inesperado de los datos del usuario.")
        return "❌ No se pudieron interpretar los datos del personaje."

    xp_actual = xp_acumulada_actual(xp, nivel)
    xp_siguiente = xp_para_siguiente_nivel(nivel)

    clase_info = CLASES.get(personaje["clase"], {})
    estado = "🟢 Online" if sesion else "⚫ Offline"

    try:
        habilidades = habilidades_de_personaje(user_id) or []
    except Exception:
        logger.exception("No se pudieron obtener las habilidades.")
        habilidades = []

    lista_habilidades = (
        "\n".join(f"• {habilidad}" for habilidad in habilidades)
        if habilidades
        else "• Todavía no tienes habilidades disponibles."
    )

    return (
        f"👤 {nombre}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Personaje: #{id_interno}\n"
        f"🧬 Raza: {personaje['raza']}\n"
        f"⚔️ Clase: {personaje['clase']}\n"
        f"🏳️ Facción: {personaje['faccion']}\n"
        f"🎖️ Rango: {rango_por_nivel(nivel)}\n"
        f"⭐ Nivel: {nivel}\n"
        f"✨ XP: {xp_actual}/{xp_siguiente}\n"
        f"📊 {barra_progreso(xp, nivel)}\n"
        f"💰 Tokens: {tokens}\n"
        f"📡 Sesión: {estado}\n\n"
        "📊 ESTADÍSTICAS\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"❤️ HP: {personaje['hp_actual']}/"
        f"{personaje['hp_max']}\n"
        f"🔷 MP: {personaje['mp_actual']}/"
        f"{personaje['mp_max']}\n"
        f"💪 Fuerza: {personaje['fuerza']}\n"
        f"🏃 Agilidad: {personaje['agilidad']}\n"
        f"🧠 Intelecto: {personaje['intelecto']}\n"
        f"🛡️ Resistencia: {personaje['resistencia']}\n"
        f"✨ Espíritu: {personaje['espiritu']}\n\n"
        f"📖 Rol: {clase_info.get('rol', 'Sin definir')}\n\n"
        "✨ HABILIDADES\n"
        f"{lista_habilidades}"
    )


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

async def menu_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    mensaje = update.effective_message
    usuario = update.effective_user

    if not mensaje or not usuario:
        return

    await mensaje.reply_text(
        texto_menu(usuario.id),
        reply_markup=teclado_menu(),
    )


# ============================================================
# CALLBACKS DEL MENÚ
# ============================================================

async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    data = query.data or ""
    user_id = query.from_user.id

    await query.answer()

    # --------------------------------------------------------
    # MENÚ PRINCIPAL
    # --------------------------------------------------------

    if data == "menu_inicio":
        await editar_menu(
            query,
            texto_menu(user_id),
            teclado_menu(),
        )
        return

    # --------------------------------------------------------
    # MI PERFIL
    # --------------------------------------------------------

    if data == "menu_perfil":
        if not await requiere_personaje(query, user_id):
            return

        await editar_menu(
            query,
            "👤 MI PERFIL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona qué quieres consultar:",
            teclado_perfil(),
        )
        return

    # --------------------------------------------------------
    # MOSTRAR PERFIL SIN /perfil
    # --------------------------------------------------------

    if data == "menu_ver_perfil":
        if not await requiere_personaje(query, user_id, "perfil"):
            return

        try:
            texto = construir_texto_perfil(user_id)
        except Exception:
            logger.exception("Error al construir el perfil.")
            texto = "❌ Ocurrió un error al cargar tu perfil."

        await editar_menu(
            query,
            texto,
            teclado_volver("perfil"),
        )
        return

    # --------------------------------------------------------
    # HABILIDADES
    # --------------------------------------------------------

    if data == "menu_habilidades":
        if not await requiere_personaje(query, user_id, "perfil"):
            return

        try:
            habilidades = habilidades_de_personaje(user_id) or []
        except Exception:
            logger.exception("Error cargando las habilidades.")
            habilidades = []

        if habilidades:
            texto_habilidades = "\n".join(
                f"✨ {habilidad}" for habilidad in habilidades
            )
        else:
            texto_habilidades = (
                "Todavía no tienes habilidades disponibles."
            )

        await editar_menu(
            query,
            "✨ HABILIDADES\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"{texto_habilidades}",
            teclado_volver("perfil"),
        )
        return

    # --------------------------------------------------------
    # INVENTARIO
    # --------------------------------------------------------

    if data == "menu_inventario":
        if not await requiere_personaje(query, user_id, "perfil"):
            return

        # El sistema de tienda existente se mantiene accesible.
        # No se inventa una segunda base de datos de inventario.
        await editar_menu(
            query,
            "🎒 INVENTARIO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Abre la tienda del bot para acceder al sistema "
            "de objetos que ya existe:\n\n"
            "/tienda",
            teclado_volver("perfil"),
        )
        return

    # --------------------------------------------------------
    # SOCIAL
    # --------------------------------------------------------

    if data == "menu_social":
        if not await requiere_personaje(query, user_id):
            return

        await editar_menu(
            query,
            "🤝 SOCIAL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona una opción:",
            teclado_social(),
        )
        return

    # --------------------------------------------------------
    # AMIGOS
    # --------------------------------------------------------

    if data == "menu_amigos":
        if not await requiere_personaje(query, user_id, "social"):
            return

        await editar_menu(
            query,
            "👥 AMIGOS\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Usa /amigos para consultar tu lista de amigos.\n"
            "Usa /solicitudes para revisar las solicitudes.\n"
            "Usa /invitar para invitar a un jugador.",
            teclado_volver("social"),
        )
        return

    # --------------------------------------------------------
    # GRUPO
    # --------------------------------------------------------

    if data == "menu_grupo":
        await editar_menu(
            query,
            "⚔️ GRUPO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "El sistema de grupos de combate necesita su "
            "propio módulo de grupos.\n"
            "Esta opción no modifica tu personaje ni tu progreso.",
            teclado_volver("social"),
        )
        return

    # --------------------------------------------------------
    # GREMIO
    # --------------------------------------------------------

    if data == "menu_gremio":
        await editar_menu(
            query,
            "🏰 GREMIO\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "El sistema de gremios todavía no está implementado "
            "en el repositorio actual.",
            teclado_volver("social"),
        )
        return

    # --------------------------------------------------------
    # MENSAJES
    # --------------------------------------------------------

    if data == "menu_mensajes":
        if not await requiere_personaje(query, user_id):
            return

        await editar_menu(
            query,
            "✉️ MENSAJES\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "El sistema de bandeja e historial de mensajes "
            "privados del MMORPG todavía necesita implementarse.",
            teclado_volver(),
        )
        return

    # --------------------------------------------------------
    # MAPA
    # --------------------------------------------------------

    if data == "menu_mapa":
        if not await requiere_personaje(query, user_id):
            return

        await editar_menu(
            query,
            "🗺️ MAPA\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "El sistema de mapa y exploración por botones "
            "todavía necesita implementarse.",
            teclado_volver(),
        )
        return

    # --------------------------------------------------------
    # CONFIGURACIÓN
    # --------------------------------------------------------

    if data == "menu_configuracion":
        await editar_menu(
            query,
            "⚙️ CONFIGURACIÓN\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Selecciona una opción:",
            teclado_configuracion(),
        )
        return

    # --------------------------------------------------------
    # AYUDA
    # --------------------------------------------------------

    if data == "menu_ayuda":
        await editar_menu(
            query,
            "📖 AYUDA\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "/start — Iniciar el bot.\n"
            "/menu — Abrir el menú principal.\n"
            "/lang — Cambiar el idioma.\n"
            "/reg Nombre.Pais — Registrar tu personaje.\n"
            "/amigos — Consultar amigos.\n"
            "/solicitudes — Consultar solicitudes.\n"
            "/tienda — Abrir la tienda.\n"
            "/help — Consultar la ayuda general.\n\n"
            "El perfil se consulta desde:\n"
            "Menú → Mi Perfil → Perfil.",
            teclado_volver("configuracion"),
        )
        return

    # --------------------------------------------------------
    # IDIOMA
    # --------------------------------------------------------

    if data in ("menu_idioma", "menu_lang"):
        from comandos.lang import teclado_idiomas

        idioma = nombre_idioma_usuario(user_id)

        await editar_menu(
            query,
            "🌐 IDIOMA DEL BOT\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"Idioma actual: {idioma}\n\n"
            "Selecciona un idioma. También puedes escribir:\n"
            "/lang español\n"
            "/lang spanish\n"
            "/lang English\n"
            "/lang 日本語",
            teclado_idiomas(),
        )
        return

    # --------------------------------------------------------
    # DESCONECTAR
    # --------------------------------------------------------

    if data == "menu_desconectar":
        await editar_menu(
            query,
            "🔌 DESCONECTAR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "La desconexión de sesiones debe conectarse "
            "al sistema de sesiones existente.\n\n"
            "Tu personaje y tu progreso no se eliminarán.",
            teclado_volver("configuracion"),
        )
        return
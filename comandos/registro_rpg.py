from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    registrar,
    obtener_user_id_por_nombre,
    obtener_datos,
    xp_acumulada_actual,
    xp_para_siguiente_nivel,
    barra_progreso,
    rango_por_nivel
)

from core.razas_clases import (
    RAZAS,
    CLASES,
    guardar_registro_pendiente,
    obtener_registro_pendiente,
    guardar_raza_pendiente,
    eliminar_registro_pendiente,
    crear_personaje,
    obtener_personaje,
    personaje_completo,
    habilidades_de_personaje
)

from core.validacion import validar_nombre
from core.paises import (
    es_pais_valido,
    obtener_nombre,
    lista_paises_texto
)


def botones_razas():
    filas = []
    fila = []

    for key, raza in RAZAS.items():
        fila.append(
            InlineKeyboardButton(
                raza["nombre"],
                callback_data=f"rpg_raza:{key}"
            )
        )

        if len(fila) == 2:
            filas.append(fila)
            fila = []

    if fila:
        filas.append(fila)

    return InlineKeyboardMarkup(filas)


def botones_clases(raza_key):
    disponibles = RAZAS[raza_key]["clases"]
    filas = []
    fila = []

    for clase in disponibles:
        fila.append(
            InlineKeyboardButton(
                clase,
                callback_data=f"rpg_clase:{clase}"
            )
        )

        if len(fila) == 2:
            filas.append(fila)
            fila = []

    if fila:
        filas.append(fila)

    filas.append([
        InlineKeyboardButton(
            "⬅️ Cambiar raza",
            callback_data="rpg_volver_razas"
        )
    ])

    return InlineKeyboardMarkup(filas)


async def start_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if personaje_completo(user_id):
        personaje = obtener_personaje(user_id)
        datos = obtener_datos(user_id)

        await update.effective_message.reply_text(
            f"¡Bienvenido de vuelta, {datos[0]}!\n"
            f"🧬 Raza: {personaje['raza']}\n"
            f"⚔️ Clase: {personaje['clase']}\n\n"
            "Usa /menu para abrir el menú del MMORPG."
        )
        return

    await update.effective_message.reply_text(
        "⚔️ ¡Bienvenido a ReidiStudiosBot MMORPG!\n\n"
        "Para entrar al juego debes completar los 3 pasos:\n\n"
        "1. Escribe tu nombre y país:\n"
        "/reg Nombre.Pais\n\n"
        "2. Elige tu raza usando los botones.\n"
        "3. Elige una clase compatible con esa raza.\n\n"
        "🌎 El país se utiliza exclusivamente para ajustar "
        "la zona horaria de los eventos. No determina tu raza, "
        "clase ni estadísticas.\n\n"
        "Ejemplo: /reg OriGamePlay.cuba\n\n"
        "Hasta completar los tres pasos no podrás utilizar "
        "los sistemas del MMORPG."
    )


async def reg_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user

    if personaje_completo(user.id):
        datos = obtener_datos(user.id)
        personaje = obtener_personaje(user.id)

        await update.effective_message.reply_text(
            f"Ya tienes un personaje completo: {datos[0]} — "
            f"{personaje['raza']} / {personaje['clase']}.\n"
            "No puedes crear otro personaje con /reg."
        )
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Uso: /reg Nombre.Pais\n"
            "Ejemplo: /reg OriGamePlay.cuba\n\n"
            "El país solo se utiliza para la zona horaria "
            "de los eventos.\n\n"
            "Países disponibles:\n" + lista_paises_texto()
        )
        return

    argumento = " ".join(context.args).strip()

    if "." not in argumento:
        await update.effective_message.reply_text(
            "Debes separar el nombre y el país con un punto.\n"
            "Ejemplo: /reg OriGamePlay.cuba\n\n"
            "Países disponibles:\n" + lista_paises_texto()
        )
        return

    nombre, pais = argumento.rsplit(".", 1)
    nombre = nombre.strip()
    pais = pais.strip().lower()

    valido, error = validar_nombre(nombre)

    if not valido:
        await update.effective_message.reply_text(error)
        return

    if not es_pais_valido(pais):
        await update.effective_message.reply_text(
            f"País no válido: {pais}\n\n"
            "Países disponibles:\n" + lista_paises_texto()
        )
        return

    otro_id = obtener_user_id_por_nombre(nombre)

    if otro_id is not None and otro_id != user.id:
        await update.effective_message.reply_text(
            "Ese nombre ya está ocupado. Elige otro."
        )
        return

    guardar_registro_pendiente(
        user.id,
        user.username or "sin_username",
        nombre,
        pais
    )

    await update.effective_message.reply_text(
        "✅ Paso 1/3 completado.\n"
        f"👤 Nombre: {nombre}\n"
        f"🌎 País: {obtener_nombre(pais)}\n\n"
        "El país solo se usa para calcular la zona horaria "
        "de los eventos.\n\n"
        "🧬 Paso 2/3: elige tu raza.\n"
        "La raza determina las clases disponibles y aporta "
        "bonificaciones raciales.",
        reply_markup=botones_razas()
    )


async def registro_rpg_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data or ""

    if data == "rpg_volver_razas":
        pending = obtener_registro_pendiente(user_id)

        if not pending:
            await query.edit_message_text(
                "No tienes un registro pendiente. "
                "Usa /reg Nombre.Pais."
            )
            return

        await query.edit_message_text(
            "🧬 Paso 2/3: elige tu raza.",
            reply_markup=botones_razas()
        )
        return

    pending = obtener_registro_pendiente(user_id)

    if not pending:
        await query.edit_message_text(
            "Este registro no está pendiente para tu cuenta. "
            "Inicia con /reg Nombre.Pais."
        )
        return

    if data.startswith("rpg_raza:"):
        raza_key = data.split(":", 1)[1]

        if raza_key not in RAZAS:
            await query.edit_message_text(
                "Raza no válida. Vuelve a usar /reg."
            )
            return

        guardar_raza_pendiente(user_id, raza_key)
        raza = RAZAS[raza_key]

        bonus = ", ".join(
            f"+{valor} {atributo}"
            for atributo, valor in raza["bonus"].items()
        )

        await query.edit_message_text(
            f"🧬 Raza elegida: {raza['nombre']}\n"
            f"🏳️ Facción: {raza['faccion']}\n"
            f"✨ Bonificaciones: {bonus}\n\n"
            "⚔️ Paso 3/3: elige una clase compatible.",
            reply_markup=botones_clases(raza_key)
        )
        return

    if data.startswith("rpg_clase:"):
        clase = data.split(":", 1)[1]
        pending = obtener_registro_pendiente(user_id)

        if not pending or not pending[4]:
            await query.edit_message_text(
                "Primero debes elegir una raza. "
                "Usa /reg Nombre.Pais."
            )
            return

        _, username, nombre, pais, raza_key = pending

        if (
            raza_key not in RAZAS
            or clase not in RAZAS[raza_key]["clases"]
        ):
            await query.answer(
                "Esa clase no está permitida para tu raza.",
                show_alert=True
            )
            return

        if esta_registrado(user_id):
            await query.edit_message_text(
                "Ya existe una cuenta registrada con tu usuario. "
                "Contacta con un administrador para revisarla."
            )
            return

        registrar(user_id, username, nombre, pais)
        crear_personaje(user_id, raza_key, clase)
        eliminar_registro_pendiente(user_id)

        personaje = obtener_personaje(user_id)
        habilidades = habilidades_de_personaje(user_id)
        clase_info = CLASES[clase]

        await query.edit_message_text(
            "🎉 ¡Personaje creado! Registro completo (3/3).\n\n"
            f"👤 Nombre: {nombre}\n"
            f"🧬 Raza: {personaje['raza']}\n"
            f"⚔️ Clase: {clase}\n"
            f"🛡️ Rol: {clase_info['rol']}\n"
            f"❤️ HP: {personaje['hp_actual']}/{personaje['hp_max']}\n"
            f"🔷 MP: {personaje['mp_actual']}/{personaje['mp_max']}\n\n"
            "✨ Habilidades iniciales:\n"
            + "\n".join(f"• {habilidad}" for habilidad in habilidades)
            + "\n\nYa puedes entrar al MMORPG. Usa /menu."
        )


async def perfil_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    viewer_id = update.effective_user.id

    if not personaje_completo(viewer_id):
        await update.effective_message.reply_text(
            "🔒 Debes completar los tres pasos del registro "
            "con /reg Nombre.Pais."
        )
        return

    if context.args:
        nombre_buscado = " ".join(context.args).strip()
        target_id = obtener_user_id_por_nombre(nombre_buscado)

        if target_id is None or not personaje_completo(target_id):
            await update.effective_message.reply_text(
                f"No existe ningún personaje completo llamado "
                f"«{nombre_buscado}»."
            )
            return

        propietario = target_id == viewer_id
    else:
        target_id = viewer_id
        propietario = True

    datos = obtener_datos(target_id)
    personaje = obtener_personaje(target_id)

    if not datos or not personaje:
        await update.effective_message.reply_text(
            "No se pudo cargar el perfil."
        )
        return

    nombre, id_interno, tokens, xp, nivel, sesion = datos
    xp_actual = xp_acumulada_actual(xp, nivel)
    xp_siguiente = xp_para_siguiente_nivel(nivel)
    estado = "🟢 Online" if sesion else "⚫ Offline"

    texto = (
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
        f"📡 Estado de sesión: {estado}"
    )

    if propietario:
        clase_info = CLASES.get(personaje["clase"], {})

        texto += (
            "\n\n📊 TUS ESTADÍSTICAS\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"❤️ HP: {personaje['hp_actual']}/{personaje['hp_max']}\n"
            f"🔷 MP: {personaje['mp_actual']}/{personaje['mp_max']}\n"
            f"💪 Fuerza: {personaje['fuerza']}\n"
            f"🏃 Agilidad: {personaje['agilidad']}\n"
            f"🧠 Intelecto: {personaje['intelecto']}\n"
            f"🛡️ Resistencia: {personaje['resistencia']}\n"
            f"✨ Espíritu: {personaje['espiritu']}\n\n"
            f"📖 Rol: {clase_info.get('rol', 'Sin definir')}\n"
            "✨ Habilidades iniciales:\n"
            + "\n".join(
                f"• {habilidad}"
                for habilidad in habilidades_de_personaje(target_id)
            )
        )

    await update.effective_message.reply_text(texto)
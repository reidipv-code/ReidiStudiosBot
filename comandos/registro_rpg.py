from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    registrar,
    obtener_user_id_por_nombre,
    obtener_datos,
    actualizar_sesion,
    eliminar_usuario,
    xp_acumulada_actual,
    xp_para_siguiente_nivel,
    barra_progreso,
    rango_por_nivel,
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
    habilidades_de_personaje,
)

from core.validacion import validar_nombre
from core.idiomas import idioma_seleccionado

from core.paises import (
    es_pais_valido,
    obtener_nombre,
    lista_paises_texto,
)


# ============================================================
# BOTONES
# ============================================================

def botones_razas():
    filas = []
    fila = []

    for key, raza in RAZAS.items():
        fila.append(
            InlineKeyboardButton(
                raza["nombre"],
                callback_data=f"rpg_raza:{key}",
            )
        )

        if len(fila) == 2:
            filas.append(fila)
            fila = []

    if fila:
        filas.append(fila)

    return InlineKeyboardMarkup(filas)


def botones_clases(raza_key):
    if raza_key not in RAZAS:
        return botones_razas()

    disponibles = RAZAS[raza_key]["clases"]
    filas = []
    fila = []

    for clase in disponibles:
        fila.append(
            InlineKeyboardButton(
                clase,
                callback_data=f"rpg_clase:{clase}",
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
            callback_data="rpg_volver_razas",
        )
    ])

    return InlineKeyboardMarkup(filas)


# ============================================================
# START
# ============================================================

async def start_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user
    mensaje = update.effective_message

    if not user or not mensaje:
        return

    user_id = user.id

    if personaje_completo(user_id):
        datos = obtener_datos(user_id)
        personaje = obtener_personaje(user_id)

        if not datos or not personaje:
            await mensaje.reply_text(
                "No se pudo cargar tu personaje. "
                "Contacta con un administrador."
            )
            return

        # Si la sesión estaba cerrada, volver a activarla.
        if not datos[5]:
            actualizar_sesion(user_id, 1)

        await mensaje.reply_text(
            f"¡Bienvenido de vuelta, {datos[0]}!\n\n"
            f"🧬 Raza: {personaje['raza']}\n"
            f"⚔️ Clase: {personaje['clase']}\n\n"
            "Usa /menu para abrir el menú del MMORPG.\n"
            "Usa /perfil para consultar tu personaje."
        )
        return

    if not idioma_seleccionado(user_id):
        await mensaje.reply_text(
            "⚔️ ¡Bienvenido a ReidiStudiosBot MMORPG!\n\n"
            "El registro ahora tiene 4 pasos y debes comenzar por el idioma:\n\n"
            "1️⃣ Selecciona tu idioma con /lang.\n"
            "   Ejemplos: /lang español o /lang spanish.\n"
            "2️⃣ Escribe tu nombre y país: /reg Nombre.Pais.\n"
            "3️⃣ Elige tu raza con los botones.\n"
            "4️⃣ Elige una clase compatible con esa raza.\n\n"
            "🌎 El país solo se utiliza para calcular la zona horaria de los eventos.\n"
            "Puedes cambiar el idioma con /lang o desde /menu."
        )
        return

    await mensaje.reply_text(
        "⚔️ ¡Bienvenido a ReidiStudiosBot MMORPG!\n\n"
        "Paso 1/4: idioma seleccionado.\n"
        "2️⃣ Escribe tu nombre y país: /reg Nombre.Pais.\n"
        "3️⃣ Elige tu raza con los botones.\n"
        "4️⃣ Elige una clase compatible con esa raza.\n\n"
        "🌎 El país se utiliza exclusivamente para calcular "
        "la zona horaria de los eventos. No determina tu raza, "
        "clase ni estadísticas.\n\n"
        "Ejemplo: /reg OriGamePlay.cuba\n\n"
        "Usa /menu para abrir el menú y cambiar el idioma."
    )


# ============================================================
# PASO 2/4: NOMBRE Y PAÍS
# ============================================================

async def reg_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user
    mensaje = update.effective_message

    if not user or not mensaje:
        return

    user_id = user.id

    # No permitir crear un segundo personaje.
    if personaje_completo(user_id):
        datos = obtener_datos(user_id)
        personaje = obtener_personaje(user_id)

        if datos and personaje:
            # /reg también permite recuperar una sesión cerrada.
            if not datos[5]:
                actualizar_sesion(user_id, 1)

                await mensaje.reply_text(
                    f"Bienvenido de vuelta, {datos[0]}.\n"
                    "Tu sesión ha sido reactivada.\n\n"
                    f"🧬 Raza: {personaje['raza']}\n"
                    f"⚔️ Clase: {personaje['clase']}\n\n"
                    "No se creó otro personaje."
                )
                return

            await mensaje.reply_text(
                f"Ya tienes un personaje completo: "
                f"{datos[0]} — {personaje['raza']} / "
                f"{personaje['clase']}.\n\n"
                "No puedes crear otro personaje con /reg."
            )
            return

    if not idioma_seleccionado(user_id):
        await mensaje.reply_text(
            "🌐 PASO 1/4: primero selecciona el idioma con /lang.\n"
            "Ejemplos: /lang español o /lang spanish.\n"
            "También puedes elegirlo desde /menu."
        )
        return

    if not context.args:
        await mensaje.reply_text(
            "PASO 2/4 — Uso: /reg Nombre.Pais\n"
            "Ejemplo: /reg OriGamePlay.cuba\n\n"
            "El país solo se utiliza para las zonas horarias "
            "de los eventos.\n\n"
            "Países disponibles:\n"
            + lista_paises_texto()
        )
        return

    argumento = " ".join(context.args).strip()

    if "." not in argumento:
        await mensaje.reply_text(
            "Debes separar el nombre y el país con un punto.\n\n"
            "Ejemplo: /reg OriGamePlay.cuba\n\n"
            "Países disponibles:\n"
            + lista_paises_texto()
        )
        return

    nombre, pais = argumento.rsplit(".", 1)

    nombre = nombre.strip()
    pais = pais.strip().lower()

    if not nombre or not pais:
        await mensaje.reply_text(
            "Debes escribir un nombre y un país.\n"
            "Ejemplo: /reg OriGamePlay.cuba"
        )
        return

    valido, error = validar_nombre(nombre)

    if not valido:
        await mensaje.reply_text(str(error))
        return

    if not es_pais_valido(pais):
        await mensaje.reply_text(
            f"País no válido: {pais}\n\n"
            "Países disponibles:\n"
            + lista_paises_texto()
        )
        return

    # Evitar que dos usuarios utilicen el mismo nombre.
    otro_id = obtener_user_id_por_nombre(nombre)

    if otro_id is not None and otro_id != user_id:
        await mensaje.reply_text(
            "Ese nombre ya está ocupado. Elige otro."
        )
        return

    # Si el usuario tiene una cuenta antigua sin personaje,
    # no sobrescribir su información ni sus estadísticas.
    if esta_registrado(user_id):
        await mensaje.reply_text(
            "Tu cuenta ya existe, pero no tiene un personaje "
            "completo asociado.\n\n"
            "Por seguridad, no se sobrescribieron tus datos. "
            "Contacta con un administrador para resolverlo."
        )
        return

    guardar_registro_pendiente(
        user_id,
        user.username or "sin_username",
        nombre,
        pais,
    )

    await mensaje.reply_text(
        "✅ PASO 2/4 COMPLETADO\n\n"
        f"👤 Nombre: {nombre}\n"
        f"🌎 País: {obtener_nombre(pais)}\n\n"
        "El país solo se usa para calcular la zona horaria "
        "de los eventos.\n\n"
        "🧬 PASO 3/4: elige tu raza.\n"
        "La raza determina las clases disponibles y aporta "
        "bonificaciones a tus estadísticas.",
        reply_markup=botones_razas(),
    )


# ============================================================
# PASOS 2 Y 3: RAZA Y CLASE
# ============================================================

async def registro_rpg_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    await query.answer()

    user_id = query.from_user.id
    data = query.data or ""

    # --------------------------------------------------------
    # VOLVER A ELEGIR RAZA
    # --------------------------------------------------------

    if data == "rpg_volver_razas":
        pending = obtener_registro_pendiente(user_id)

        if not pending:
            await query.edit_message_text(
                "No tienes un registro pendiente.\n"
                "Usa /reg Nombre.Pais para comenzar."
            )
            return

        await query.edit_message_text(
            "🧬 PASO 3/4: elige tu raza.",
            reply_markup=botones_razas(),
        )
        return

    pending = obtener_registro_pendiente(user_id)

    if not pending:
        await query.edit_message_text(
            "Este registro no está pendiente para tu cuenta.\n\n"
            "Selecciona primero el idioma con /lang y luego usa /reg Nombre.Pais."
        )
        return

    # --------------------------------------------------------
    # SELECCIONAR RAZA
    # --------------------------------------------------------

    if data.startswith("rpg_raza:"):
        raza_key = data.split(":", 1)[1]

        if raza_key not in RAZAS:
            await query.edit_message_text(
                "Raza no válida. Vuelve a iniciar el registro."
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
            "⚔️ PASO 4/4: elige una clase compatible.",
            reply_markup=botones_clases(raza_key),
        )
        return

    # --------------------------------------------------------
    # SELECCIONAR CLASE Y CREAR PERSONAJE
    # --------------------------------------------------------

    if data.startswith("rpg_clase:"):
        clase = data.split(":", 1)[1]

        pending = obtener_registro_pendiente(user_id)

        if not pending or len(pending) < 5 or not pending[4]:
            await query.edit_message_text(
                "Primero debes elegir una raza.\n"
                "Usa /reg Nombre.Pais para comenzar."
            )
            return

        _, username, nombre, pais, raza_key = pending

        if raza_key not in RAZAS:
            await query.edit_message_text(
                "La raza guardada no es válida. "
                "Vuelve a iniciar el registro."
            )
            return

        if clase not in CLASES:
            await query.edit_message_text(
                "La clase seleccionada no existe."
            )
            return

        if clase not in RAZAS[raza_key]["clases"]:
            await query.answer(
                "Esa clase no está permitida para tu raza.",
                show_alert=True,
            )
            return

        if esta_registrado(user_id):
            await query.edit_message_text(
                "Ya existe una cuenta con tu usuario. "
                "Por seguridad, no se sobrescribieron sus datos. "
                "Contacta con un administrador."
            )
            return

        # Guardar la cuenta y el personaje.
        # Si falla la creación del personaje, eliminar la cuenta
        # recién creada para evitar registros incompletos.
        try:
            registrar(
                user_id,
                username,
                nombre,
                pais,
            )

            crear_personaje(
                user_id,
                raza_key,
                clase,
            )

            if not personaje_completo(user_id):
                raise RuntimeError(
                    "El personaje no quedó registrado completamente."
                )

        except Exception:
            try:
                eliminar_usuario(user_id)
            except Exception:
                pass

            await query.edit_message_text(
                "❌ No se pudo completar el registro.\n\n"
                "No se creó un personaje incompleto. "
                "Inténtalo de nuevo con /reg Nombre.Pais."
            )
            raise

        eliminar_registro_pendiente(user_id)

        personaje = obtener_personaje(user_id)
        habilidades = habilidades_de_personaje(user_id)
        clase_info = CLASES[clase]

        await query.edit_message_text(
            "🎉 ¡PERSONAJE CREADO!\n"
            "Registro completo: 4/4.\n\n"
            f"👤 Nombre: {nombre}\n"
            f"🧬 Raza: {personaje['raza']}\n"
            f"⚔️ Clase: {clase}\n"
            f"🛡️ Rol: {clase_info['rol']}\n"
            f"❤️ HP: {personaje['hp_actual']}/"
            f"{personaje['hp_max']}\n"
            f"🔷 MP: {personaje['mp_actual']}/"
            f"{personaje['mp_max']}\n\n"
            "✨ Habilidades iniciales:\n"
            + "\n".join(
                f"• {habilidad}"
                for habilidad in habilidades
            )
            + "\n\nYa puedes entrar al MMORPG.\n"
            "Usa /menu para comenzar."
        )
        return

    await query.answer(
        "Esta opción de registro no es válida.",
        show_alert=True,
    )


# ============================================================
# PERFIL RPG
# ============================================================

async def perfil_rpg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user
    mensaje = update.effective_message

    if not user or not mensaje:
        return

    viewer_id = user.id

    if not personaje_completo(viewer_id):
        await mensaje.reply_text(
            "🔒 Debes completar los cuatro pasos del registro "
            "con /reg Nombre.Pais."
        )
        return

    # Determinar si se consulta el perfil propio o el de otro.
    if context.args:
        nombre_buscado = " ".join(context.args).strip()

        target_id = obtener_user_id_por_nombre(nombre_buscado)

        if (
            target_id is None
            or not personaje_completo(target_id)
        ):
            await mensaje.reply_text(
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
        await mensaje.reply_text(
            "No se pudo cargar el perfil."
        )
        return

    nombre = datos[0]

    # Perfil ajeno: solo información general del personaje.
    # No mostrar XP, tokens, nivel ni estadísticas detalladas.
    if not propietario:
        await mensaje.reply_text(
            f"👤 {nombre}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🧬 Raza: {personaje['raza']}\n"
            f"⚔️ Clase: {personaje['clase']}\n"
            f"🏳️ Facción: {personaje['faccion']}"
        )
        return

    # Perfil propio: mostrar las estadísticas completas.
    _, id_interno, tokens, xp, nivel, sesion = datos

    xp_actual = xp_acumulada_actual(xp, nivel)
    xp_siguiente = xp_para_siguiente_nivel(nivel)

    clase_info = CLASES.get(personaje["clase"], {})

    estado = "🟢 Online" if sesion else "⚫ Offline"

    habilidades = habilidades_de_personaje(target_id)

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
        f"📡 Estado de sesión: {estado}\n\n"
        "📊 TUS ESTADÍSTICAS\n"
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
        f"📖 Rol: {clase_info.get('rol', 'Sin definir')}\n"
        "✨ Habilidades:\n"
        + "\n".join(
            f"• {habilidad}"
            for habilidad in habilidades
        )
    )

    await mensaje.reply_text(texto)
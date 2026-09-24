import io

from telegram import Update, InputFile
from telegram.ext import ContextTypes

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_lista_usuarios,
    xp_acumulada_actual,
    xp_para_siguiente_nivel,
    rango_por_nivel,
    barra_progreso,
    obtener_pais,
    obtener_user_id_por_nombre,
    esta_online,
)

from core.paises import (
    obtener_nombre as nombre_pais,
    obtener_bandera,
)

from core.logros import (
    LOGROS,
    logros_de_usuario,
)

from core.tienda import (
    equipados_usuario,
)

from core.perfil_visual import (
    generar_perfil,
)


# ============================================================
# AVATAR DE TELEGRAM
# ============================================================

async def obtener_avatar_telegram(
    context,
    user_id,
    nombre,
):
    try:
        fotos = await context.bot.get_user_profile_photos(
            user_id=user_id,
            limit=1,
        )

        if fotos.total_count > 0:
            foto = fotos.photos[0][-1]

            archivo = await context.bot.get_file(
                foto.file_id
            )

            datos = await archivo.download_as_bytearray()

            from PIL import Image

            imagen = Image.open(
                io.BytesIO(datos)
            ).convert("RGBA")

            return imagen

    except Exception:
        pass

    # Si no se pudo obtener foto:
    from PIL import Image

    return Image.new(
        "RGBA",
        (320, 320),
        (35, 40, 55, 255),
    )


# ============================================================
# PERFIL
# ============================================================

async def perfil(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "⚠️ Primero regístrate con /reg nombre.pais"
        )
        return

    # ========================================================
    # PERFIL DE OTRO USUARIO
    # ========================================================

    if context.args:
        nombre_buscado = " ".join(
            context.args
        ).strip()

        otro_id = obtener_user_id_por_nombre(
            nombre_buscado
        )

        if otro_id is None:
            await update.message.reply_text(
                f"❌ No existe ningún usuario con el nombre "
                f"*{nombre_buscado}*.",
                parse_mode="Markdown",
            )
            return

        datos = obtener_datos(
            otro_id
        )

        if datos is None:
            await update.message.reply_text(
                "❌ No se pudo obtener el perfil."
            )
            return

        (
            nombre,
            id_interno,
            tokens,
            xp,
            nivel,
            sesion,
        ) = datos

        # ----------------------------------------------------
        # País
        # ----------------------------------------------------

        pais = obtener_pais(
            otro_id
        )

        if pais:
            bandera = obtener_bandera(
                pais
            )

            nombre_pais_str = nombre_pais(
                pais
            )

            pais_visual = (
                f"{bandera} {nombre_pais_str}"
            )

        else:
            pais_visual = "No configurado"

        # ----------------------------------------------------
        # Cosméticos
        # ----------------------------------------------------

        equipados = equipados_usuario(
            otro_id
        )

        # ----------------------------------------------------
        # Avatar
        # ----------------------------------------------------

        avatar = await obtener_avatar_telegram(
            context,
            otro_id,
            nombre,
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        xp_total = xp_acumulada_actual(
            xp,
            nivel,
        )

        xp_siguiente = xp_para_siguiente_nivel(
            nivel,
        )

        rango = rango_por_nivel(
            nivel
        )

        # ----------------------------------------------------
        # Generar imagen
        # ----------------------------------------------------

        datos_imagen = generar_perfil(
            nombre=nombre,
            nivel=nivel,
            rango=rango,
            xp_total=xp_total,
            xp_siguiente=xp_siguiente,
            tokens=tokens,
            pais=pais_visual,
            avatar=avatar,
            equipados=equipados,
        )

        contenido, mime, animado = datos_imagen

        archivo = io.BytesIO(
            contenido
        )

        archivo.seek(0)

        archivo_nombre = (
            "perfil.gif"
            if animado
            else "perfil.png"
        )

        # ----------------------------------------------------
        # Información inferior
        # ----------------------------------------------------

        estado = (
            "🟢 Online"
            if esta_online(otro_id)
            else "⚫ Offline"
        )

        logros_usr = logros_de_usuario(
            otro_id
        )

        total_logros = len(
            LOGROS
        )

        caption = (
            f"👤 *PERFIL DE {nombre.upper()}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: *#{id_interno}*\n"
            f"🏆 Logros: *{len(logros_usr)}/{total_logros}*\n"
            f"{estado}"
        )

        if animado:
            await update.message.reply_animation(
                animation=InputFile(
                    archivo,
                    filename=archivo_nombre,
                ),
                caption=caption,
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_photo(
                photo=InputFile(
                    archivo,
                    filename=archivo_nombre,
                ),
                caption=caption,
                parse_mode="Markdown",
            )

        return

    # ========================================================
    # PERFIL PROPIO
    # ========================================================

    datos = obtener_datos(
        user_id
    )

    if datos is None:
        await update.message.reply_text(
            "❌ No se pudo obtener tu perfil."
        )
        return

    (
        nombre,
        id_interno,
        tokens,
        xp,
        nivel,
        sesion,
    ) = datos

    # --------------------------------------------------------
    # XP
    # --------------------------------------------------------

    barra = barra_progreso(
        xp,
        nivel,
    )

    xp_total = xp_acumulada_actual(
        xp,
        nivel,
    )

    xp_siguiente = xp_para_siguiente_nivel(
        nivel,
    )

    # --------------------------------------------------------
    # País
    # --------------------------------------------------------

    pais = obtener_pais(
        user_id
    )

    if pais:
        bandera = obtener_bandera(
            pais
        )

        nombre_pais_str = nombre_pais(
            pais
        )

        pais_visual = (
            f"{bandera} {nombre_pais_str}"
        )

    else:
        pais_visual = "No configurado"

    # --------------------------------------------------------
    # Cosméticos
    # --------------------------------------------------------

    equipados = equipados_usuario(
        user_id
    )

    # --------------------------------------------------------
    # Avatar
    # --------------------------------------------------------

    avatar = await obtener_avatar_telegram(
        context,
        user_id,
        nombre,
    )

    # --------------------------------------------------------
    # Rango
    # --------------------------------------------------------

    rango = rango_por_nivel(
        nivel
    )

    # --------------------------------------------------------
    # Generar tarjeta visual
    # --------------------------------------------------------

    contenido, mime, animado = generar_perfil(
        nombre=nombre,
        nivel=nivel,
        rango=rango,
        xp_total=xp_total,
        xp_siguiente=xp_siguiente,
        tokens=tokens,
        pais=pais_visual,
        avatar=avatar,
        equipados=equipados,
    )

    archivo = io.BytesIO(
        contenido
    )

    archivo.seek(0)

    archivo_nombre = (
        "perfil.gif"
        if animado
        else "perfil.png"
    )

    # --------------------------------------------------------
    # Información adicional
    # --------------------------------------------------------

    estado = (
        "🟢 Online"
        if esta_online(user_id)
        else "⚫ Offline"
    )

    logros_usr = logros_de_usuario(
        user_id
    )

    total_logros = len(
        LOGROS
    )

    emojis_logros = ""

    if logros_usr:
        emojis_logros = "\n🏆 Logros: "

        for clave in logros_usr:
            if clave in LOGROS:
                emojis_logros += (
                    LOGROS[clave]["emoji"]
                    + " "
                )

        emojis_logros += (
            f"({len(logros_usr)}/{total_logros})"
        )

    caption = (
        f"👤 *{nombre.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: *#{id_interno}*\n"
        f"{estado}"
        f"{emojis_logros}"
    )

    # --------------------------------------------------------
    # ENVIAR IMAGEN/GIF
    # --------------------------------------------------------

    if animado:
        await update.message.reply_animation(
            animation=InputFile(
                archivo,
                filename=archivo_nombre,
            ),
            caption=caption,
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_photo(
            photo=InputFile(
                archivo,
                filename=archivo_nombre,
            ),
            caption=caption,
            parse_mode="Markdown",
        )


# ============================================================
# TOKENS
# ============================================================

async def tokens_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "⚠️ Primero regístrate."
        )
        return

    datos = obtener_datos(
        user_id
    )

    await update.message.reply_text(
        f"💰 *{datos[2]}* tokens",
        parse_mode="Markdown",
    )


# ============================================================
# NIVEL
# ============================================================

async def nivel_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "⚠️ Primero regístrate."
        )
        return

    datos = obtener_datos(
        user_id
    )

    (
        nombre,
        _,
        _,
        xp,
        nivel,
        _,
    ) = datos

    xp_total = xp_acumulada_actual(
        xp,
        nivel,
    )

    xp_siguiente = xp_para_siguiente_nivel(
        nivel,
    )

    await update.message.reply_text(
        f"⭐ *{nombre}* - Nivel {nivel}\n"
        f"✨ XP: {xp_total}/{xp_siguiente}\n"
        f"📊 {barra_progreso(xp, nivel)}",
        parse_mode="Markdown",
    )


# ============================================================
# RANGO
# ============================================================

async def rango_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "⚠️ Primero regístrate."
        )
        return

    datos = obtener_datos(
        user_id
    )

    await update.message.reply_text(
        f"🎖️ {rango_por_nivel(datos[4])}",
        parse_mode="Markdown",
    )


# ============================================================
# LISTA DE USUARIOS
# ============================================================

async def userslist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "⚠️ Primero regístrate."
        )
        return

    lista = obtener_lista_usuarios()

    if not lista:
        await update.message.reply_text(
            "📋 No hay usuarios registrados."
        )
        return

    texto = (
        "📋 *USUARIOS*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
    )

    for id_interno, nombre in lista:
        texto += (
            f"#{id_interno} - {nombre}\n"
        )

    texto += (
        f"\n👥 Total: *{len(lista)}*"
    )

    await update.message.reply_text(
        texto,
        parse_mode="Markdown",
    )

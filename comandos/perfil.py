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

from core.tienda import equipados_usuario
from core.perfil_visual import generar_perfil


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

            return Image.open(
                io.BytesIO(datos)
            ).convert("RGBA")

    except Exception:
        pass

    from PIL import Image

    return Image.new(
        "RGBA",
        (320, 320),
        (35, 40, 55, 255),
    )


def _pais_visual(pais):
    if not pais:
        return "No configurado"

    try:
        bandera = obtener_bandera(pais)
    except Exception:
        bandera = ""

    try:
        nombre = nombre_pais(pais)
    except Exception:
        nombre = str(pais)

    return f"{bandera} {nombre}".strip()


async def _enviar_perfil(
    update,
    nombre,
    id_interno,
    tokens,
    xp,
    nivel,
    pais,
    user_id,
    context,
    mostrar_logros=True,
):
    equipados = equipados_usuario(user_id)

    avatar = await obtener_avatar_telegram(
        context,
        user_id,
        nombre,
    )

    xp_total = xp_acumulada_actual(
        xp,
        nivel,
    )

    xp_siguiente = xp_para_siguiente_nivel(
        nivel,
    )

    rango = rango_por_nivel(nivel)

    try:
        resultado = generar_perfil(
            nombre=nombre,
            nivel=nivel,
            rango=rango,
            xp_total=xp_total,
            xp_siguiente=xp_siguiente,
            tokens=tokens,
            pais=_pais_visual(pais),
            avatar=avatar,
            equipados=equipados,
        )
    except Exception as error:
        await update.message.reply_text(
            f"❌ Error generando el perfil:\n"
            f"`{type(error).__name__}: {error}`",
            parse_mode="Markdown",
        )
        return

    contenido, mime, animado = resultado

    archivo = io.BytesIO(contenido)
    archivo.seek(0)

    archivo_nombre = (
        "perfil.gif"
        if animado
        else "perfil.png"
    )

    estado = (
        "🟢 Online"
        if esta_online(user_id)
        else "⚫ Offline"
    )

    logros_usr = logros_de_usuario(user_id)
    total_logros = len(LOGROS)

    emojis_logros = ""

    if mostrar_logros and logros_usr:
        emojis = []

        for clave in logros_usr:
            if clave in LOGROS:
                try:
                    emojis.append(
                        LOGROS[clave]["emoji"]
                    )
                except Exception:
                    pass

        if emojis:
            emojis_logros = (
                "\n🏆 Logros: "
                + " ".join(emojis)
                + f" ({len(logros_usr)}/{total_logros})"
            )

    caption = (
        f"👤 *{nombre.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: *#{id_interno}*\n"
        f"{estado}"
        f"{emojis_logros}"
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

    # /perfil nombre
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

        datos = obtener_datos(otro_id)

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

        pais = obtener_pais(otro_id)

        await _enviar_perfil(
            update=update,
            nombre=nombre,
            id_interno=id_interno,
            tokens=tokens,
            xp=xp,
            nivel=nivel,
            pais=pais,
            user_id=otro_id,
            context=context,
            mostrar_logros=True,
        )

        return

    # /perfil
    datos = obtener_datos(user_id)

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

    pais = obtener_pais(user_id)

    await _enviar_perfil(
        update=update,
        nombre=nombre,
        id_interno=id_interno,
        tokens=tokens,
        xp=xp,
        nivel=nivel,
        pais=pais,
        user_id=user_id,
        context=context,
        mostrar_logros=True,
    )


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

    datos = obtener_datos(user_id)

    if datos is None:
        await update.message.reply_text(
            "❌ No se pudo obtener tu información."
        )
        return

    await update.message.reply_text(
        f"💰 *{datos[2]}* tokens",
        parse_mode="Markdown",
    )


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

    datos = obtener_datos(user_id)

    if datos is None:
        await update.message.reply_text(
            "❌ No se pudo obtener tu información."
        )
        return

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

    datos = obtener_datos(user_id)

    if datos is None:
        await update.message.reply_text(
            "❌ No se pudo obtener tu información."
        )
        return

    await update.message.reply_text(
        f"🎖️ {rango_por_nivel(datos[4])}",
        parse_mode="Markdown",
    )


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


# Compatibilidad por si otro archivo usa userlist.
userlist = userslist

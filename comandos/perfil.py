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

    # =========================================================
    # VER PERFIL DE OTRO USUARIO
    # =========================================================

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

        if pais:
            bandera = obtener_bandera(pais)
            nombre_pais_str = nombre_pais(pais)

            pais_visual = (
                f"{bandera} {nombre_pais_str}"
            )
        else:
            pais_visual = "No configurado"

        equipados = equipados_usuario(
            otro_id
        )

        avatar = await obtener_avatar_telegram(
            context,
            otro_id,
            nombre,
        )

        xp_total = xp_acumulada_actual(
            xp,
            nivel,
        )

        xp_siguiente = xp_para_siguiente_nivel(
            nivel
        )

        rango = rango_por_nivel(
            nivel
        )

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

        estado = (
            "🟢 Online"
            if esta_online(otro_id)
            else "⚫ Offline"
        )

        logros_usr = logros_de_usuario(
            otro_id
        )

        total_logros = len(LOGROS)

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

    # =========================================================
    # PERFIL PROPIO
    # =========================================================

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

    xp_total = xp_acumulada_actual(
        xp,
        nivel,
    )

    xp_siguiente = xp_para_siguiente_nivel(
        nivel
    )

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

    equipados = equipados_usuario(
        user_id
    )

    avatar = await obtener_avatar_telegram(
        context,
        user_id,
        nombre,
    )

    rango = rango_por_nivel(
        nivel
    )

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

    estado = (
        "🟢 Online"
        if esta_online(user_id)
        else "⚫ Offline"
    )

    logros_usr = logros_de_usuario(
        user_id
    )

    total_logros = len(LOGROS)

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

    if animado:

        await update.message

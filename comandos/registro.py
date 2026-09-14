```python
import time

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import (
    esta_registrado,
    obtener_datos,
    obtener_todos_los_usuarios,
    registrar,
    eliminar_usuario,
    actualizar_sesion,
    set_pais,
    usuario_tiene_pais,
    obtener_user_id_por_nombre
)

from core.validacion import validar_nombre

from core.paises import (
    es_pais_valido,
    obtener_nombre,
    lista_paises_texto
)


async def notificar_a_todos(context, user_id_excluir, texto):
    ids = obtener_todos_los_usuarios()

    for uid in ids:
        if uid == user_id_excluir:
            continue

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=texto,
                parse_mode="HTML"
            )
        except Exception:
            pass


async def reg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Registra un usuario con:

        /reg nombre.pais

    Ejemplo:

        /reg OriGamePlay.cuba

    Esta versión incluye mensajes de diagnóstico para detectar
    exactamente dónde ocurre un posible error.
    """

    try:
        # ---------------------------------------------------------
        # DATOS DEL USUARIO
        # ---------------------------------------------------------

        user_id = update.effective_user.id
        username = update.effective_user.username or "sin_username"

        print(f"[REG] Comando recibido de user_id={user_id}")
        print(f"[REG] username={username}")
        print(f"[REG] context.args={context.args}")

        # ---------------------------------------------------------
        # COMPROBAR ARGUMENTOS
        # ---------------------------------------------------------

        if not context.args:
            await update.message.reply_text(
                "⚠️ Uso: `/reg nombre.pais`\n\n"
                "Ejemplo: `/reg Juan.cuba`\n\n"
                "📋 *Países disponibles:*\n" +
                lista_paises_texto(),
                parse_mode="Markdown"
            )
            return

        argumento = " ".join(context.args).strip()

        print(f"[REG] argumento={argumento}")

        # ---------------------------------------------------------
        # COMPROBAR PUNTO ENTRE NOMBRE Y PAÍS
        # ---------------------------------------------------------

        if "." not in argumento:
            await update.message.reply_text(
                "⚠️ Debes poner tu nombre y tu país separados por un punto.\n\n"
                "Ejemplo: `/reg Juan.cuba`\n\n"
                "📋 *Países disponibles:*\n" +
                lista_paises_texto(),
                parse_mode="Markdown"
            )
            return

        # ---------------------------------------------------------
        # SEPARAR NOMBRE Y PAÍS
        # ---------------------------------------------------------

        nombre, pais = argumento.rsplit(".", 1)

        nombre = nombre.strip()
        pais = pais.lower().strip()

        print(f"[REG] nombre={nombre}")
        print(f"[REG] pais={pais}")

        # ---------------------------------------------------------
        # VALIDAR PAÍS
        # ---------------------------------------------------------

        if not es_pais_valido(pais):
            print(f"[REG] País inválido: {pais}")

            await update.message.reply_text(
                f"❌ País no válido: *{pais}*\n\n"
                "📋 *Países disponibles:*\n" +
                lista_paises_texto(),
                parse_mode="Markdown"
            )
            return

        print("[REG] País válido")

        # ---------------------------------------------------------
        # COMPROBAR SI YA EXISTE EL USUARIO
        # ---------------------------------------------------------

        if esta_registrado(user_id):

            print("[REG] El usuario ya existe en la base de datos")

            datos = obtener_datos(user_id)

            print(f"[REG] datos={datos}")

            # Usuario con sesión activa
            if datos[5] == 1:

                await update.message.reply_text(
                    f"⚠️ Ya estás registrado como "
                    f"*{datos[0]}* (ID: #{datos[1]}).",
                    parse_mode="Markdown"
                )
                return

            # Usuario existente pero con sesión cerrada
            else:

                print("[REG] Usuario existente con sesión cerrada")

                if not usuario_tiene_pais(user_id):
                    print(f"[REG] Asignando país: {pais}")
                    set_pais(user_id, pais)

                actualizar_sesion(user_id, 1)

                await update.message.reply_text(
                    f"✅ ¡Bienvenido de vuelta, *{datos[0]}*!\n"
                    f"🌎 País: {obtener_nombre(pais)}",
                    parse_mode="Markdown"
                )

                return

        # ---------------------------------------------------------
        # VALIDAR NOMBRE
        # ---------------------------------------------------------

        print("[REG] Usuario no registrado")
        print("[REG] Validando nombre...")

        valido, error = validar_nombre(nombre)

        print(
            f"[REG] validar_nombre -> "
            f"valido={valido}, error={error}"
        )

        if not valido:
            await update.message.reply_text(
                error,
                parse_mode="Markdown"
            )
            return

        print("[REG] Nombre válido")

        # ---------------------------------------------------------
        # REGISTRAR USUARIO
        # ---------------------------------------------------------

        print("[REG] Ejecutando registrar()...")

        id_interno = registrar(
            user_id,
            username,
            nombre,
            pais
        )

        print(f"[REG] registrar() -> id={id_interno}")

        # ---------------------------------------------------------
        # OBTENER NOMBRE DEL PAÍS
        # ---------------------------------------------------------

        nombre_pais = obtener_nombre(pais)

        print(f"[REG] nombre_pais={nombre_pais}")

        # ---------------------------------------------------------
        # RESPUESTA AL USUARIO
        # ---------------------------------------------------------

        await update.message.reply_text(
            f"✅ ¡Registro exitoso!\n\n"
            f"👤 *{nombre}*\n"
            f"🆔 *#{id_interno}*\n"
            f"🌎 País: {nombre_pais}\n"
            f"💰 *100 tokens*\n"
            f"⭐ *Nivel 1*",
            parse_mode="Markdown"
        )

        print("[REG] Mensaje de registro enviado correctamente")

        # ---------------------------------------------------------
        # NOTIFICAR A LOS DEMÁS USUARIOS
        # ---------------------------------------------------------

        texto_notif = (
            f"🆕 <b>Nuevo usuario registrado</b>\n"
            f"👤 <b>{nombre}</b>\n"
            f"🌎 Se unió desde: <b>{nombre_pais}</b>"
        )

        await notificar_a_todos(
            context,
            user_id,
            texto_notif
        )

        print("[REG] Notificaciones enviadas")

    # -------------------------------------------------------------
    # CAPTURAR CUALQUIER ERROR
    # -------------------------------------------------------------

    except Exception as e:

        print(
            f"[REG ERROR] "
            f"{type(e).__name__}: {e}"
        )

        # Intentar informar al usuario
        try:
            await update.message.reply_text(
                "❌ Ocurrió un error interno durante el registro.\n\n"
                f"Tipo: `{type(e).__name__}`\n"
                f"Detalle: `{e}`",
                parse_mode="Markdown"
            )

        except Exception as e2:

            print(
                f"[REG ERROR AL RESPONDER] "
                f"{type(e2).__name__}: {e2}"
            )


async def setpais(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "❌ Debes registrarte primero con "
            "`/reg nombre.pais`.",
            parse_mode="Markdown"
        )
        return

    if usuario_tiene_pais(user_id):
        await update.message.reply_text(
            "⚠️ *Ya tienes un país configurado.*\n\n"
            "El comando `/setpais` solo se puede usar *una vez*.\n"
            "Si necesitas cambiarlo, contacta a un admin.",
            parse_mode="Markdown"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/setpais pais`\n\n"
            "Ejemplo: `/setpais mexico`\n\n"
            "📋 *Países disponibles:*\n" +
            lista_paises_texto(),
            parse_mode="Markdown"
        )
        return

    pais = context.args[0].lower().strip()

    if not es_pais_valido(pais):
        await update.message.reply_text(
            f"❌ País no válido: *{pais}*\n\n"
            "📋 *Países disponibles:*\n" +
            lista_paises_texto(),
            parse_mode="Markdown"
        )
        return

    set_pais(user_id, pais)

    await update.message.reply_text(
        f"✅ País actualizado a: {obtener_nombre(pais)}",
        parse_mode="Markdown"
    )


async def unreg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "❌ No tienes ninguna cuenta registrada."
        )
        return

    datos = obtener_datos(user_id)

    if datos[5] == 0:
        await update.message.reply_text(
            "ℹ️ Tu sesión ya estaba cerrada."
        )
        return

    context.user_data["confirmacion"] = {
        "accion": "unreg",
        "inicio": time.time()
    }

    await update.message.reply_text(
        "⚠️ *¿Cerrar sesión?*\n"
        "Responde `.si` o `.no`. Tienes 30 seg.",
        parse_mode="Markdown"
    )


async def deletereg(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "❌ No tienes ninguna cuenta registrada."
        )
        return

    context.user_data["confirmacion"] = {
        "accion": "deletereg",
        "inicio": time.time()
    }

    await update.message.reply_text(
        "⚠️ *¿ELIMINAR tu cuenta?*\n"
        "Responde `.si` o `.no`. Tienes 30 seg.",
        parse_mode="Markdown"
    )


async def confirmar_accion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user_id = update.effective_user.id

    if "confirmacion" not in context.user_data:
        return

    texto = update.message.text.strip().lower()

    if texto not in [".si", ".sí", ".no"]:
        return

    accion = context.user_data["confirmacion"]["accion"]

    datos = obtener_datos(user_id)

    # ---------------------------------------------------------
    # CONFIRMAR
    # ---------------------------------------------------------

    if texto in [".si", ".sí"]:

        # -----------------------------------------------------
        # CERRAR SESIÓN
        # -----------------------------------------------------

        if accion == "unreg":

            actualizar_sesion(user_id, 0)

            del context.user_data["confirmacion"]

            await update.message.reply_text(
                f"👋 Sesión cerrada, *{datos[0]}*.",
                parse_mode="Markdown"
            )

            await notificar_a_todos(
                context,
                user_id,
                f"👋 <b>{datos[0]}</b> cerró sesión."
            )

            raise ApplicationHandlerStop

        # -----------------------------------------------------
        # ELIMINAR CUENTA
        # -----------------------------------------------------

        elif accion == "deletereg":

            nombre = datos[0]

            eliminar_usuario(user_id)

            del context.user_data["confirmacion"]

            await update.message.reply_text(
                "🗑️ Cuenta eliminada.",
                parse_mode="Markdown"
            )

            await notificar_a_todos(
                context,
                user_id,
                f"🗑️ <b>{nombre}</b> abandonó el bot."
            )

            raise ApplicationHandlerStop

    # ---------------------------------------------------------
    # CANCELAR
    # ---------------------------------------------------------

    elif texto == ".no":

        del context.user_data["confirmacion"]

        await update.message.reply_text(
            "✅ Cancelado."
        )

        raise ApplicationHandlerStop
```

### Qué cambia esta versión

La única modificación importante está en `/reg`: ahora cualquier error queda capturado y se imprime en Railway:

```text
[REG ERROR] ...
```

y además intenta mostrarte el error directamente en Telegram.

También verás el recorrido:

```text
[REG] Comando recibido
[REG] context.args=['OriGamePlay.cuba']
[REG] argumento=OriGamePlay.cuba
[REG] nombre=OriGamePlay
[REG] pais=cuba
[REG] País válido
[REG] Usuario no registrado
[REG] Validando nombre...
[REG] Nombre válido
[REG] Ejecutando registrar()...
```

Esto nos permitirá saber exactamente dónde falla.

**Importante:** después de probar `/reg OriGamePlay.cuba`, pásame el resultado que aparezca en Railway empezando por `[REG]` o `[REG ERROR]`. Con eso podemos corregir el problema definitivo en vez de seguir cambiando archivos a ciegas.

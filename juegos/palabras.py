import sqlite3
import random
import time

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import (
    obtener_datos,
    actualizar_tokens,
    sumar_xp,
    DB_PATH
)
from core.sesiones import iniciar_partida, terminar_partida
from core.misiones import sumar_progreso


# ============================================================
# CONFIGURACIÓN
# ============================================================

COOLDOWN_PERDIDA = 420       # 7 minutos
COOLDOWN_VICTORIA = 600      # 10 minutos

TIEMPO = 40                  # 40 segundos por palabra
PALABRAS_POR_PARTIDA = 5


# ============================================================
# PALABRAS
# ============================================================

PALABRAS = [
    "bola", "casa", "perro", "gato", "mesa", "silla", "libro", "agua",
    "fuego", "tierra", "aire", "cielo", "luna", "sol", "estrella", "nube",
    "playa", "monte", "rio", "mar", "pez", "pajaro", "leon", "tigre",
    "caballo", "vaca", "oveja", "cerdo", "gallina", "pato", "raton", "oso",
    "manzana", "platano", "naranja", "uva", "fresa", "limon", "pera", "melon",
    "coche", "moto", "avion", "barco", "tren", "bici", "camion", "taxi",
    "rojo", "azul", "verde", "amarillo", "negro", "blanco", "morado", "rosa",
    "escuela", "hospital", "parque", "tienda"
]


# ============================================================
# PARTIDAS EN MEMORIA
# ============================================================

partidas_palabras = {}


# ============================================================
# BASE DE DATOS
# ============================================================

def init_palabras_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS palabras_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_partida REAL,
            duracion INTEGER DEFAULT 600
        )
    """)

    # Para instalaciones antiguas donde la tabla ya existía
    try:
        c.execute(
            "ALTER TABLE palabras_cooldown "
            "ADD COLUMN duracion INTEGER DEFAULT 600"
        )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# ============================================================
# COOLDOWN
# ============================================================

def get_cooldown(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT ultima_partida, duracion
            FROM palabras_cooldown
            WHERE user_id = ?
            """,
            (user_id,)
        )

        r = c.fetchone()

    except sqlite3.OperationalError:
        # Compatibilidad con tabla antigua
        c.execute(
            """
            SELECT ultima_partida
            FROM palabras_cooldown
            WHERE user_id = ?
            """,
            (user_id,)
        )

        r = c.fetchone()

        conn.close()

        if r:
            return r[0], COOLDOWN_VICTORIA

        return 0, COOLDOWN_VICTORIA

    conn.close()

    if not r:
        return 0, COOLDOWN_VICTORIA

    return r[0], r[1] or COOLDOWN_VICTORIA


def set_cooldown(user_id, gano=False):
    duracion = (
        COOLDOWN_VICTORIA
        if gano
        else COOLDOWN_PERDIDA
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute(
            """
            INSERT OR REPLACE INTO palabras_cooldown
            (user_id, ultima_partida, duracion)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                time.time(),
                duracion
            )
        )

    except sqlite3.OperationalError:
        # Compatibilidad extrema con una tabla antigua
        c.execute(
            """
            INSERT OR REPLACE INTO palabras_cooldown
            (user_id, ultima_partida)
            VALUES (?, ?)
            """,
            (
                user_id,
                time.time()
            )
        )

    conn.commit()
    conn.close()


def tiempo_restante(user_id):
    ultima, duracion = get_cooldown(user_id)

    if ultima == 0:
        return 0

    restante = duracion - (
        time.time() - ultima
    )

    return max(0, int(restante))


def formatear_tiempo(seg):
    return f"{seg // 60}m {seg % 60}s"


# ============================================================
# NORMALIZAR
# ============================================================

def normalizar(texto):
    texto = texto.lower().strip()

    for k, v in {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n"
    }.items():
        texto = texto.replace(k, v)

    return texto


# ============================================================
# MEZCLAR PALABRA
# ============================================================

def mezclar(palabra):
    letras = list(palabra.upper())

    random.shuffle(letras)

    intentos = 0

    while (
        "".join(letras).lower() == palabra.lower()
        and intentos < 10
    ):
        random.shuffle(letras)
        intentos += 1

    return " ".join(letras)


# ============================================================
# INICIAR PALABRAS
# ============================================================

async def palabras(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user_id = update.effective_user.id

    datos = obtener_datos(user_id)

    if datos is None or datos[5] != 1:
        await update.message.reply_text(
            "🔒 Debes estar registrado."
        )
        return

    # Evitar dos partidas simultáneas
    if user_id in partidas_palabras:
        await update.message.reply_text(
            "⚠️ Ya tienes una partida en curso."
        )
        return

    # Revisar cooldown
    restante = tiempo_restante(user_id)

    if restante > 0:
        await update.message.reply_text(
            f"⏳ Espera *{formatear_tiempo(restante)}*.",
            parse_mode="Markdown"
        )
        return

    # Seleccionar palabras
    seleccionadas = random.sample(
        PALABRAS,
        PALABRAS_POR_PARTIDA
    )

    partida = {
        "palabras": seleccionadas,
        "indice": 0,
        "aciertos": 0,
        "chat_id": update.effective_chat.id,
        "hora_inicio": time.time()
    }

    # Primero guardar la partida en memoria
    partidas_palabras[user_id] = partida

    # Crear sesión global
    try:
        iniciar_partida(
            user_id,
            "palabras"
        )
    except Exception as e:
        # Si falla la sesión, no dejar partida fantasma
        partidas_palabras.pop(user_id, None)

        print(
            f"❌ Error iniciando sesión de Palabras "
            f"{user_id}: {e}"
        )

        await update.message.reply_text(
            "❌ No se pudo iniciar la partida. "
            "Inténtalo nuevamente."
        )
        return

    # Mensaje inicial
    try:
        await update.message.reply_text(
            "🔤 *PALABRAS DESORDENADAS*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "Forma la palabra correcta con las letras.\n"
            "Responde con `.palabra`\n\n"
            "Ejemplo: `B O L A` → `.bola`\n\n"
            f"⏱️ {TIEMPO}s por palabra. "
            f"{PALABRAS_POR_PARTIDA} palabras.\n"
            "Premio: 50 tokens + 50 XP",
            parse_mode="Markdown"
        )

        await enviar_palabra(
            context,
            user_id
        )

    except Exception as e:
        print(
            f"❌ Error mostrando partida de Palabras "
            f"{user_id}: {e}"
        )

        await limpiar_partida_segura(
            user_id
        )


# ============================================================
# ENVIAR PALABRA
# ============================================================

async def enviar_palabra(
    context,
    user_id
):

    partida = partidas_palabras.get(user_id)

    if not partida:
        return

    idx = partida["indice"]

    if idx >= PALABRAS_POR_PARTIDA:
        return

    palabra = partida["palabras"][idx]

    mezclada = mezclar(palabra)

    # Reiniciar los 40 segundos para esta palabra
    partida["hora_inicio"] = time.time()

    await context.bot.send_message(
        chat_id=partida["chat_id"],
        text=(
            f"🔤 *Palabra "
            f"{idx + 1}/{PALABRAS_POR_PARTIDA}*\n"
            f"`{mezclada}`\n\n"
            f"⏱️ {TIEMPO}s. "
            f"Responde `.palabra`"
        ),
        parse_mode="Markdown"
    )


# ============================================================
# RESPONDER PALABRAS
# ============================================================

async def responder_palabras(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    partida = partidas_palabras.get(user_id)

    if not partida:
        return

    texto = update.message.text.strip()

    if not texto.startswith("."):
        return

    respuesta = texto[1:].strip()

    indice = partida["indice"]

    if indice >= PALABRAS_POR_PARTIDA:
        return

    correcta = partida["palabras"][indice]

    # ========================================================
    # RESPUESTA CORRECTA
    # ========================================================

    if normalizar(respuesta) == normalizar(correcta):

        partida["aciertos"] += 1

        try:
            await update.message.reply_text(
                f"✅ ¡Correcto! Era *{correcta}*.",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    # ========================================================
    # RESPUESTA INCORRECTA
    # ========================================================

    else:

        try:
            await update.message.reply_text(
                f"❌ Era *{correcta}*.",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        await terminar_palabras(
            context,
            user_id,
            gano=False
        )

        raise ApplicationHandlerStop

    # ========================================================
    # SIGUIENTE PALABRA
    # ========================================================

    partida = partidas_palabras.get(user_id)

    if not partida:
        raise ApplicationHandlerStop

    partida["indice"] += 1

    if partida["indice"] >= PALABRAS_POR_PARTIDA:

        await terminar_palabras(
            context,
            user_id,
            gano=True
        )

    else:

        try:
            await enviar_palabra(
                context,
                user_id
            )
        except Exception as e:
            print(
                f"❌ Error enviando siguiente palabra "
                f"{user_id}: {e}"
            )

            await terminar_palabras(
                context,
                user_id,
                gano=False
            )

    raise ApplicationHandlerStop


# ============================================================
# TERMINAR PARTIDA
# ============================================================

async def terminar_palabras(
    context,
    user_id,
    gano
):

    # IMPORTANTE:
    # sacar la partida de memoria INMEDIATAMENTE.
    # Esto evita que quede bloqueado el usuario
    # si después falla una operación.

    partida = partidas_palabras.pop(
        user_id,
        None
    )

    if not partida:
        # Intentar limpiar igualmente la sesión
        try:
            terminar_partida(user_id)
        except Exception:
            pass

        return

    # ========================================================
    # COOLDOWN
    # ========================================================

    try:
        set_cooldown(
            user_id,
            gano=gano
        )
    except Exception as e:
        print(
            f"❌ Error guardando cooldown "
            f"de Palabras {user_id}: {e}"
        )

    # ========================================================
    # SESIÓN
    # ========================================================

    try:
        terminar_partida(
            user_id
        )
    except Exception as e:

        print(
            f"⚠️ Error terminando sesión "
            f"de Palabras {user_id}: {e}"
        )

        # Limpieza directa de emergencia
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute(
                "DELETE FROM sesiones WHERE user_id = ?",
                (user_id,)
            )

            conn.commit()
            conn.close()

        except Exception as e2:
            print(
                f"❌ No se pudo limpiar sesión "
                f"de Palabras {user_id}: {e2}"
            )

    # ========================================================
    # VICTORIA
    # ========================================================

    if gano:

        try:
            actualizar_tokens(
                user_id,
                50
            )
        except Exception as e:
            print(
                f"❌ Error dando tokens "
                f"a {user_id}: {e}"
            )

        try:
            subio = sumar_xp(
                user_id,
                50
            )
        except Exception as e:
            print(
                f"❌ Error dando XP "
                f"a {user_id}: {e}"
            )
            subio = None

        texto = (
            "🎉 *¡PALABRAS COMPLETADAS!*\n"
            "✅ 5/5\n"
            "💰 +50 tokens\n"
            "✨ +50 XP"
        )

        if subio:
            texto += (
                f"\n⭐ ¡Nivel {subio}!"
            )

        texto += (
            "\n⏳ Cooldown: 10 min"
        )

        # ====================================================
        # MISIÓN
        # ====================================================

        try:
            completadas = sumar_progreso(
                user_id,
                "palabras_completada"
            )

            for m_id in completadas:
                await avisar_mision(
                    context,
                    user_id,
                    m_id
                )

        except Exception as e:
            print(
                f"⚠️ Error procesando misión "
                f"de Palabras {user_id}: {e}"
            )

    # ========================================================
    # DERROTA
    # ========================================================

    else:

        texto = (
            "😢 *FALLIDO*\n"
            f"✅ Aciertos: "
            f"{partida['aciertos']}/5\n"
            "⏳ Cooldown: 7 min"
        )

    # ========================================================
    # MENSAJE FINAL
    # ========================================================

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text=texto,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(
            f"⚠️ No se pudo enviar resultado "
            f"de Palabras {user_id}: {e}"
        )


# ============================================================
# LIMPIEZA DE EMERGENCIA
# ============================================================

async def limpiar_partida_segura(user_id):

    partidas_palabras.pop(
        user_id,
        None
    )

    try:
        terminar_partida(
            user_id
        )
    except Exception:
        pass


# ============================================================
# AVISAR MISIÓN
# ============================================================

async def avisar_mision(
    context,
    user_id,
    m_id
):

    try:
        from core.misiones import MISIONES

        info = MISIONES.get(
            m_id
        )

        if not info:
            return

        recompensa = (
            f"+{info['tokens']}💰"
        )

        if info["xp"] > 0:
            recompensa += (
                f" +{info['xp']}⭐"
            )

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎯 *¡MISIÓN COMPLETADA!*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"✅ {info['texto']}\n"
                f"🎁 {recompensa}"
            ),
            parse_mode="Markdown"
        )

    except Exception as e:
        print(
            f"⚠️ Error avisando misión "
            f"{m_id} a {user_id}: {e}"
        )


# ============================================================
# TIMEOUTS
# ============================================================

async def revisar_timeouts_palabras(
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    ahora = time.time()

    # Copia para poder modificar el diccionario
    # mientras recorremos las partidas.
    for user_id, partida in list(
        partidas_palabras.items()
    ):

        try:

            hora_inicio = partida.get(
                "hora_inicio",
                ahora
            )

            # >= evita depender de que sea exactamente
            # mayor a 40 segundos.
            if ahora - hora_inicio >= TIEMPO:

                # Sacar primero de memoria.
                partida_final = partidas_palabras.pop(
                    user_id,
                    None
                )

                if not partida_final:
                    continue

                # Limpiar sesión.
                try:
                    terminar_partida(
                        user_id
                    )
                except Exception as e:
                    print(
                        f"⚠️ Error limpiando sesión "
                        f"por timeout de Palabras "
                        f"{user_id}: {e}"
                    )

                    try:
                        conn = sqlite3.connect(
                            DB_PATH
                        )
                        c = conn.cursor()

                        c.execute(
                            "DELETE FROM sesiones "
                            "WHERE user_id = ?",
                            (user_id,)
                        )

                        conn.commit()
                        conn.close()

                    except Exception:
                        pass

                # Cooldown de derrota
                try:
                    set_cooldown(
                        user_id,
                        gano=False
                    )
                except Exception as e:
                    print(
                        f"⚠️ Error guardando cooldown "
                        f"de timeout {user_id}: {e}"
                    )

                # Avisar timeout
                try:
                    await context.bot.send_message(
                        chat_id=partida_final["chat_id"],
                        text="⏰ ¡Se acabó el tiempo!"
                    )
                except Exception:
                    pass

                # Resultado final
                texto = (
                    "😢 *FALLIDO*\n"
                    f"✅ Aciertos: "
                    f"{partida_final['aciertos']}/5\n"
                    "⏳ Cooldown: 7 min"
                )

                try:
                    await context.bot.send_message(
                        chat_id=partida_final["chat_id"],
                        text=texto,
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass

        except Exception as e:

            # MUY IMPORTANTE:
            # un usuario con un estado corrupto
            # no debe matar el JobQueue completo.

            print(
                f"❌ Error revisando timeout "
                f"de Palabras para {user_id}: {e}"
            )

            # Limpieza final de emergencia
            partidas_palabras.pop(
                user_id,
                None
            )

            try:
                terminar_partida(
                    user_id
                )
            except Exception:
                pass

import sqlite3
import time

from core.db import DB_PATH


# ============================================================
# SESIONES DE PARTIDAS
# ============================================================
#
# IMPORTANTE:
# Las partidas reales de los juegos se guardan en memoria
# (partidas_trivia, partidas_mates, partidas_funks, etc.).
#
# La tabla SQLite solo sirve como indicador para el bloqueador
# global de comandos.
#
# Si Railway reinicia el bot, los diccionarios en memoria se
# pierden. Por eso cualquier fila antigua de "sesiones" queda
# HUÉRFANA y no debe seguir bloqueando al usuario.
#
# Esta versión limpia esas sesiones al arrancar el bot.
# ============================================================


def init_sesiones_db():
    """Crea la tabla de sesiones y elimina sesiones huérfanas."""

    conn = sqlite3.connect(DB_PATH)

    try:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                user_id INTEGER PRIMARY KEY,
                juego TEXT,
                inicio REAL
            )
        """)

        # ------------------------------------------------------
        # LIMPIAR SESIONES HUÉRFANAS
        # ------------------------------------------------------
        #
        # Al arrancar/reiniciar Railway, todas las partidas que
        # estaban en memoria dejaron de existir. Por tanto, las
        # filas que quedaron en SQLite ya no representan partidas
        # reales.
        # ------------------------------------------------------

        c.execute("DELETE FROM sesiones")

        conn.commit()

        print("✅ Sesiones de partidas inicializadas")
        print("🧹 Sesiones antiguas limpiadas")

    finally:
        conn.close()


def iniciar_partida(user_id, juego):
    """Registra una partida nueva para el usuario."""

    conn = sqlite3.connect(DB_PATH)

    try:
        c = conn.cursor()

        c.execute(
            """
            INSERT OR REPLACE INTO sesiones
            (user_id, juego, inicio)
            VALUES (?, ?, ?)
            """,
            (user_id, juego, time.time())
        )

        conn.commit()

    finally:
        conn.close()


def terminar_partida(user_id):
    """Elimina la sesión de partida del usuario."""

    conn = sqlite3.connect(DB_PATH)

    try:
        c = conn.cursor()

        c.execute(
            "DELETE FROM sesiones WHERE user_id = ?",
            (user_id,)
        )

        conn.commit()

    finally:
        conn.close()


def obtener_juego(user_id):
    """Devuelve el juego activo del usuario o None."""

    conn = sqlite3.connect(DB_PATH)

    try:
        c = conn.cursor()

        c.execute(
            "SELECT juego FROM sesiones WHERE user_id = ?",
            (user_id,)
        )

        r = c.fetchone()

    finally:
        conn.close()

    return r[0] if r else None


def estas_en_partida(user_id):
    """Devuelve True si existe una sesión de partida."""

    return obtener_juego(user_id) is not None

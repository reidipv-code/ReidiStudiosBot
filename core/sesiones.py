import sqlite3
import time

from core.db import DB_PATH


def init_sesiones_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            user_id INTEGER PRIMARY KEY,
            juego TEXT,
            inicio REAL
        )
    """)
    conn.commit()
    conn.close()


def iniciar_partida(user_id, juego):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO sesiones (user_id, juego, inicio) VALUES (?, ?, ?)",
        (user_id, juego, time.time())
    )
    conn.commit()
    conn.close()


def terminar_partida(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM sesiones WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def obtener_juego(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT juego FROM sesiones WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None


def estas_en_partida(user_id):
    return obtener_juego(user_id) is not None

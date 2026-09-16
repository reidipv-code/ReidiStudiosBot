import sqlite3
import random
from datetime import datetime, date

from core.db import DB_PATH
from core.config import ahora


# ═══════════════════════════════════════════════════════════
# DEFINICIÓN DE MISIONES
# ═══════════════════════════════════════════════════════════
MISIONES = {
    "jugar_3": {
        "texto": "Juega 3 partidas",
        "objetivo": 3,
        "tokens": 100,
        "xp": 50,
        "evento": "partida_jugada",
    },
    "jugar_5": {
        "texto": "Juega 5 partidas",
        "objetivo": 5,
        "tokens": 180,
        "xp": 90,
        "evento": "partida_jugada",
    },
    "ganar_trivia": {
        "texto": "Gana 1 trivia",
        "objetivo": 1,
        "tokens": 150,
        "xp": 80,
        "evento": "trivia_ganada",
    },
    "ganar_trivia_3": {
        "texto": "Gana 3 trivias",
        "objetivo": 3,
        "tokens": 300,
        "xp": 150,
        "evento": "trivia_ganada",
    },
    "ganar_mates": {
        "texto": "Gana 1 mates",
        "objetivo": 1,
        "tokens": 150,
        "xp": 80,
        "evento": "mates_ganada",
    },
    "ganar_mates_3": {
        "texto": "Gana 3 mates",
        "objetivo": 3,
        "tokens": 300,
        "xp": 150,
        "evento": "mates_ganada",
    },
    "ganar_memoria": {
        "texto": "Llega a la ronda 10 de memoria",
        "objetivo": 10,
        "tokens": 150,
        "xp": 80,
        "evento": "memoria_ronda",
    },
    "ganar_memoria_20": {
        "texto": "Llega a la ronda 20 de memoria",
        "objetivo": 20,
        "tokens": 350,
        "xp": 180,
        "evento": "memoria_ronda",
    },
    "ganar_ruleta": {
        "texto": "Gana 1 ruleta",
        "objetivo": 1,
        "tokens": 100,
        "xp": 50,
        "evento": "ruleta_ganada",
    },
    "ganar_ruleta_3": {
        "texto": "Gana 3 ruletas",
        "objetivo": 3,
        "tokens": 250,
        "xp": 120,
        "evento": "ruleta_ganada",
    },
    "ganar_apuesta": {
        "texto": "Gana 1 apuesta",
        "objetivo": 1,
        "tokens": 200,
        "xp": 100,
        "evento": "apuesta_ganada",
    },
    "ganar_apuesta_3": {
        "texto": "Gana 3 apuestas",
        "objetivo": 3,
        "tokens": 400,
        "xp": 200,
        "evento": "apuesta_ganada",
    },
    "reclamar": {
        "texto": "Reclama tu recompensa diaria",
        "objetivo": 1,
        "tokens": 50,
        "xp": 0,
        "evento": "reclamacion",
    },
    "dar_tokens": {
        "texto": "Usa /darTokens una vez",
        "objetivo": 1,
        "tokens": 100,
        "xp": 0,
        "evento": "dar_tokens",
    },
    "ganar_palabras": {
        "texto": "Completa 1 palabras",
        "objetivo": 1,
        "tokens": 150,
        "xp": 80,
        "evento": "palabras_completada",
    },
    "ganar_funks": {
        "texto": "Completa 1 funks",
        "objetivo": 1,
        "tokens": 150,
        "xp": 80,
        "evento": "funks_completada",
    },
    "ganar_dados": {
        "texto": "Gana en /dados",
        "objetivo": 1,
        "tokens": 100,
        "xp": 50,
        "evento": "dados_ganada",
    },
    "invitar_amigo": {
        "texto": "Usa /invitar una vez",
        "objetivo": 1,
        "tokens": 80,
        "xp": 0,
        "evento": "invitacion_enviada",
    },
}


# ═══════════════════════════════════════════════════════════
# BASE DE DATOS
# ═══════════════════════════════════════════════════════════
def init_misiones_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS misiones_usuario (
            user_id INTEGER,
            fecha TEXT,
            mision TEXT,
            progreso INTEGER DEFAULT 0,
            completada INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, fecha, mision)
        )
    """)

    conn.commit()
    conn.close()


def fecha_hoy() -> str:
    return ahora().strftime("%Y-%m-%d")


def generar_misiones_dia(user_id):
    """Genera 5 misiones aleatorias para el usuario si no las tiene ya."""
    fecha = fecha_hoy()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT mision FROM misiones_usuario WHERE user_id = ? AND fecha = ?",
        (user_id, fecha)
    )
    existentes = [r[0] for r in c.fetchall()]

    if len(existentes) >= 5:
        conn.close()
        return existentes

    # Elegir 5 misiones al azar que no estén ya
    disponibles = [m for m in MISIONES.keys() if m not in existentes]
    nuevas = random.sample(disponibles, min(5 - len(existentes), len(disponibles)))

    for m in nuevas:
        c.execute(
            "INSERT OR IGNORE INTO misiones_usuario (user_id, fecha, mision, progreso, completada) "
            "VALUES (?, ?, ?, 0, 0)",
            (user_id, fecha, m)
        )

    conn.commit()
    conn.close()

    return existentes + nuevas


def obtener_misiones(user_id):
    """Devuelve lista de (mision, progreso, completada)."""
    fecha = fecha_hoy()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT mision, progreso, completada FROM misiones_usuario "
        "WHERE user_id = ? AND fecha = ?",
        (user_id, fecha)
    )
    lista = c.fetchall()
    conn.close()
    return lista


def sumar_progreso(user_id, evento, cantidad=1):
    """
    Suma progreso al usuario en las misiones que correspondan al evento.
    Devuelve lista de misiones completadas nuevas.
    """
    fecha = fecha_hoy()
    completadas = []

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Buscar misiones de hoy que escuchen este evento
    for m_id, info in MISIONES.items():
        if info["evento"] != evento:
            continue

        c.execute(
            "SELECT progreso, completada FROM misiones_usuario "
            "WHERE user_id = ? AND fecha = ? AND mision = ?",
            (user_id, fecha, m_id)
        )
        fila = c.fetchone()
        if not fila:
            continue

        progreso, completada = fila
        if completada:
            continue

        nuevo = progreso + cantidad
        hecha = 1 if nuevo >= info["objetivo"] else 0

        c.execute(
            "UPDATE misiones_usuario SET progreso = ?, completada = ? "
            "WHERE user_id = ? AND fecha = ? AND mision = ?",
            (nuevo, hecha, user_id, fecha, m_id)
        )

        if hecha:
            completadas.append(m_id)

    conn.commit()
    conn.close()
    return completadas

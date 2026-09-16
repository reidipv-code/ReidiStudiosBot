import sqlite3

from core.db import DB_PATH


# ═══════════════════════════════════════════════════════════
# DEFINICIÓN DE LOGROS
# ═══════════════════════════════════════════════════════════
LOGROS = {
    "primeros_pasos": {
        "emoji": "🌱",
        "nombre": "Primeros pasos",
        "descripcion": "Registrarse en el bot",
    },
    "nivel_5": {
        "emoji": "⭐",
        "nombre": "Nivel 5",
        "descripcion": "Llegar al nivel 5",
    },
    "nivel_10": {
        "emoji": "🌟",
        "nombre": "Nivel 10",
        "descripcion": "Llegar al nivel 10",
    },
    "nivel_20": {
        "emoji": "💫",
        "nombre": "Nivel 20",
        "descripcion": "Llegar al nivel 20",
    },
    "rico": {
        "emoji": "💰",
        "nombre": "Rico",
        "descripcion": "Tener 1000 tokens",
    },
    "millonario": {
        "emoji": "💎",
        "nombre": "Millonario",
        "descripcion": "Tener 10.000 tokens",
    },
    "jugador": {
        "emoji": "🎮",
        "nombre": "Jugador",
        "descripcion": "Jugar 10 partidas",
    },
    "veterano": {
        "emoji": "🎯",
        "nombre": "Veterano",
        "descripcion": "Jugar 100 partidas",
    },
    "racha_7": {
        "emoji": "🔥",
        "nombre": "Racha 7",
        "descripcion": "Reclamar 7 días seguidos",
    },
    "racha_30": {
        "emoji": "🌋",
        "nombre": "Racha 30",
        "descripcion": "Reclamar 30 días seguidos",
    },
    "apostador": {
        "emoji": "🎲",
        "nombre": "Apostador",
        "descripcion": "Ganar 10 apuestas",
    },
    "erudito": {
        "emoji": "📚",
        "nombre": "Erudito",
        "descripcion": "Ganar 20 trivias",
    },
    "memorion": {
        "emoji": "🧠",
        "nombre": "Memorión",
        "descripcion": "Llegar a la ronda 20 de memoria",
    },
    "banquero": {
        "emoji": "🏦",
        "nombre": "Banquero",
        "descripcion": "Tener 4000 tokens en el banco",
    },
    "social": {
        "emoji": "👥",
        "nombre": "Social",
        "descripcion": "Usar /msp 10 veces",
    },
    "matematico": {
        "emoji": "🥸",
        "nombre": "Matemático",
        "descripcion": "Ganar 15 partidas de mates",
    },
    "cerebrito": {
        "emoji": "🤓",
        "nombre": "Cerebrito",
        "descripcion": "Ganar 10 partidas seguidas de mates y trivia",
    },
    "fiestero": {
        "emoji": "🎡",
        "nombre": "Fiestero",
        "descripcion": "Ganar 10 ruletas",
    },
    "vagon_sin_destino": {
        "emoji": "🎟️",
        "nombre": "Vagón sin destino",
        "descripcion": "Participar en 5 eventos seguidos",
    },
    "curioso": {
        "emoji": "🧐",
        "nombre": "Curioso",
        "descripcion": "Usar 15 comandos distintos",
    },
}


# ═══════════════════════════════════════════════════════════
# BASE DE DATOS
# ═══════════════════════════════════════════════════════════
def init_logros_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de logros desbloqueados
    c.execute("""
        CREATE TABLE IF NOT EXISTS logros_usuario (
            user_id INTEGER,
            logro TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, logro)
        )
    """)

    # Tabla de estadísticas para los logros que necesitan contadores
    c.execute("""
        CREATE TABLE IF NOT EXISTS logros_stats (
            user_id INTEGER PRIMARY KEY,
            partidas_jugadas INTEGER DEFAULT 0,
            mates_ganadas INTEGER DEFAULT 0,
            trivias_ganadas INTEGER DEFAULT 0,
            ruletas_ganadas INTEGER DEFAULT 0,
            apuestas_ganadas INTEGER DEFAULT 0,
            msp_usados INTEGER DEFAULT 0,
            eventos_seguidos INTEGER DEFAULT 0,
            mates_seguidas INTEGER DEFAULT 0,
            trivia_seguidas INTEGER DEFAULT 0,
            comandos_usados TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


def obtener_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM logros_stats WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    if not r:
        c.execute(
            "INSERT INTO logros_stats (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()
        c.execute("SELECT * FROM logros_stats WHERE user_id = ?", (user_id,))
        r = c.fetchone()
    conn.close()
    return r


def actualizar_stat(user_id, campo, valor=None, incremento=1):
    init_logros_db()
    obtener_stats(user_id)  # asegura que existe la fila
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if valor is not None:
        c.execute(f"UPDATE logros_stats SET {campo} = ? WHERE user_id = ?", (valor, user_id))
    else:
        c.execute(f"UPDATE logros_stats SET {campo} = {campo} + ? WHERE user_id = ?", (incremento, user_id))
    conn.commit()
    conn.close()


def tiene_logro(user_id, logro) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM logros_usuario WHERE user_id = ? AND logro = ?",
        (user_id, logro)
    )
    r = c.fetchone()
    conn.close()
    return r is not None


def dar_logro(user_id, logro) -> bool:
    """Devuelve True si es la primera vez que se le da (nuevo)."""
    if tiene_logro(user_id, logro):
        return False
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO logros_usuario (user_id, logro) VALUES (?, ?)",
        (user_id, logro)
    )
    conn.commit()
    conn.close()
    return True


def logros_de_usuario(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT logro FROM logros_usuario WHERE user_id = ?", (user_id,))
    lista = [r[0] for r in c.fetchall()]
    conn.close()
    return lista


def contar_logros(user_id) -> int:
    return len(logros_de_usuario(user_id))

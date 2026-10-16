import sqlite3

from core.db import DB_PATH


def init_amigos_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de amistades confirmadas
    c.execute("""
        CREATE TABLE IF NOT EXISTS amigos (
            user_id INTEGER,
            amigo_id INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, amigo_id)
        )
    """)

    # Tabla de solicitudes pendientes
    c.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_amistad (
            de_id INTEGER,
            para_id INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (de_id, para_id)
        )
    """)

    conn.commit()
    conn.close()


def son_amigos(user_id, amigo_id) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM amigos WHERE user_id = ? AND amigo_id = ?",
        (user_id, amigo_id)
    )
    r = c.fetchone()
    conn.close()
    return r is not None


def enviar_solicitud(de_id, para_id) -> bool:
    """Devuelve True si se envía, False si ya existe."""
    if son_amigos(de_id, para_id):
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Comprobar si ya hay solicitud
    c.execute(
        "SELECT 1 FROM solicitudes_amistad WHERE de_id = ? AND para_id = ?",
        (de_id, para_id)
    )
    if c.fetchone():
        conn.close()
        return False

    c.execute(
        "INSERT INTO solicitudes_amistad (de_id, para_id) VALUES (?, ?)",
        (de_id, para_id)
    )
    conn.commit()
    conn.close()
    return True


def obtener_solicitudes(user_id):
    """Devuelve lista de (de_id) que han solicitado amistad al usuario."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT de_id FROM solicitudes_amistad WHERE para_id = ?",
        (user_id,)
    )
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids


def hay_solicitud(de_id, para_id) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM solicitudes_amistad WHERE de_id = ? AND para_id = ?",
        (de_id, para_id)
    )
    r = c.fetchone()
    conn.close()
    return r is not None


def aceptar_solicitud(de_id, para_id) -> bool:
    """Acepta la solicitud. Se crean dos entradas (bidireccional)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Comprobar que existe
    c.execute(
        "SELECT 1 FROM solicitudes_amistad WHERE de_id = ? AND para_id = ?",
        (de_id, para_id)
    )
    if not c.fetchone():
        conn.close()
        return False

    # Insertar ambos lados de la amistad
    c.execute(
        "INSERT OR IGNORE INTO amigos (user_id, amigo_id) VALUES (?, ?)",
        (de_id, para_id)
    )
    c.execute(
        "INSERT OR IGNORE INTO amigos (user_id, amigo_id) VALUES (?, ?)",
        (para_id, de_id)
    )

    # Borrar la solicitud
    c.execute(
        "DELETE FROM solicitudes_amistad WHERE de_id = ? AND para_id = ?",
        (de_id, para_id)
    )

    conn.commit()
    conn.close()
    return True


def rechazar_solicitud(de_id, para_id) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "DELETE FROM solicitudes_amistad WHERE de_id = ? AND para_id = ?",
        (de_id, para_id)
    )
    afectadas = c.rowcount
    conn.commit()
    conn.close()
    return afectadas > 0


def eliminar_amigo(user_id, amigo_id) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "DELETE FROM amigos WHERE (user_id = ? AND amigo_id = ?) OR (user_id = ? AND amigo_id = ?)",
        (user_id, amigo_id, amigo_id, user_id)
    )
    afectadas = c.rowcount
    conn.commit()
    conn.close()
    return afectadas > 0


def lista_amigos(user_id):
    """Devuelve lista de user_id de los amigos."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT amigo_id FROM amigos WHERE user_id = ?",
        (user_id,)
    )
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids


def contar_amigos(user_id) -> int:
    return len(lista_amigos(user_id))

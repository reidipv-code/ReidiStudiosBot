import sqlite3
import os
import time

RAILWAY_VOLUME_MOUNT_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")

if RAILWAY_VOLUME_MOUNT_PATH:
    DB_PATH = os.path.join(RAILWAY_VOLUME_MOUNT_PATH, "usuarios.db")
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "usuarios.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nombre TEXT NOT NULL,
            id_interno INTEGER UNIQUE,
            tokens INTEGER DEFAULT 100,
            xp INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            xp_version INTEGER DEFAULT 2,
            sesion_activa INTEGER DEFAULT 1,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN pais TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN ultima_actividad REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN xp_version INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # Migración del sistema antiguo de XP.
    c.execute("""
        SELECT user_id, xp, nivel
        FROM usuarios
        WHERE COALESCE(xp_version, 1) = 1
    """)

    filas = c.fetchall()

    for uid, xp, nivel in filas:
        xp = max(0, int(xp or 0))
        nivel = max(1, min(int(nivel or 1), 500))

        nuevo_nivel = nivel
        nuevo_xp = xp

        while nuevo_nivel < 500:
            requisito = xp_para_nivel(nuevo_nivel)

            if nuevo_xp < requisito:
                break

            nuevo_xp -= requisito
            nuevo_nivel += 1

        if nuevo_nivel >= 500:
            nuevo_nivel = 500
            nuevo_xp = min(nuevo_xp, xp_para_nivel(500))

        c.execute("""
            UPDATE usuarios
            SET xp = ?, nivel = ?, xp_version = 2
            WHERE user_id = ?
        """, (nuevo_xp, nuevo_nivel, uid))

    conn.commit()
    conn.close()


def esta_registrado(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT 1 FROM usuarios WHERE user_id = ?",
        (user_id,)
    )

    resultado = c.fetchone()

    conn.close()
    return resultado is not None


def obtener_datos(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT nombre, id_interno, tokens, xp, nivel, sesion_activa
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))

    resultado = c.fetchone()

    conn.close()
    return resultado


def obtener_todos_los_usuarios():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT user_id FROM usuarios")
    ids = [fila[0] for fila in c.fetchall()]

    conn.close()
    return ids


def obtener_lista_usuarios():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id_interno, nombre
        FROM usuarios
        ORDER BY id_interno ASC
    """)

    lista = c.fetchall()

    conn.close()
    return lista


def obtener_ids_ocupados():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id_interno
        FROM usuarios
        WHERE id_interno IS NOT NULL
    """)

    ids = [fila[0] for fila in c.fetchall()]

    conn.close()
    return ids


def siguiente_id_libre():
    ocupados = set(obtener_ids_ocupados())

    numero = 1

    while numero in ocupados:
        numero += 1

    return numero


def registrar(user_id, username, nombre, pais=None):
    id_interno = siguiente_id_libre()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO usuarios
        (
            user_id,
            username,
            nombre,
            id_interno,
            tokens,
            xp,
            nivel,
            xp_version,
            sesion_activa,
            pais,
            ultima_actividad
        )
        VALUES (?, ?, ?, ?, 100, 0, 1, 2, 1, ?, ?)
    """, (
        user_id,
        username,
        nombre,
        id_interno,
        pais,
        time.time()
    ))

    conn.commit()
    conn.close()

    return id_interno


def eliminar_usuario(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "DELETE FROM usuarios WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def actualizar_sesion(user_id, estado):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE usuarios
        SET sesion_activa = ?
        WHERE user_id = ?
    """, (estado, user_id))

    conn.commit()
    conn.close()


def actualizar_tokens(user_id, cantidad):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE usuarios
        SET tokens = tokens + ?
        WHERE user_id = ?
    """, (cantidad, user_id))

    conn.commit()
    conn.close()


def actualizar_xp(user_id, cantidad):
    return sumar_xp(user_id, cantidad)


def resetear_xp(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE usuarios
        SET xp = 0, nivel = 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def obtener_user_id_por_nombre(nombre):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT user_id
        FROM usuarios
        WHERE LOWER(nombre) = LOWER(?)
    """, (nombre,))

    resultado = c.fetchone()

    conn.close()

    return resultado[0] if resultado else None


def xp_para_nivel(nivel):
    """
    XP necesaria dentro del nivel actual.

    Nivel 1 -> 500 XP
    Nivel 2 -> 1000 XP
    Nivel 3 -> 1500 XP
    ...
    Nivel 500 -> 250000 XP
    """
    nivel = max(1, min(int(nivel), 500))
    return 500 * nivel


def xp_total_para_nivel(nivel):
    """
    Mantiene compatibilidad con código anterior.
    """
    nivel = max(1, min(int(nivel), 500))
    return 500 * nivel


def xp_acumulada_actual(xp, nivel):
    """
    Devuelve la XP que lleva el usuario DENTRO de su nivel actual.

    Ejemplo:
    nivel 1, 300 XP -> 300/500
    nivel 2, 300 XP -> 300/1000
    nivel 3, 700 XP -> 700/1500
    """
    nivel = max(1, min(int(nivel), 500))
    xp = max(0, int(xp or 0))

    requisito = xp_para_nivel(nivel)

    return min(xp, requisito)


def xp_para_siguiente_nivel(nivel):
    """
    Denominador de la barra del nivel actual.
    """
    return xp_para_nivel(nivel)


def sumar_xp(user_id, cantidad):
    """
    Añade XP respetando el requisito progresivo:

    Nivel 1 -> necesita 500
    Nivel 2 -> necesita 1000
    Nivel 3 -> necesita 1500
    ...

    Al subir de nivel, la XP vuelve a 0.
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT xp, nivel
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))

    fila = c.fetchone()

    if not fila:
        conn.close()
        return None

    xp_actual, nivel = fila

    xp_actual = max(0, int(xp_actual or 0))
    nivel = max(1, min(int(nivel or 1), 500))
    cantidad = int(cantidad)

    if cantidad <= 0:
        conn.close()
        return None

    if nivel >= 500:
        requisito = xp_para_nivel(500)

        xp_actual = min(
            requisito,
            xp_actual + cantidad
        )

        c.execute("""
            UPDATE usuarios
            SET xp = ?, nivel = 500
            WHERE user_id = ?
        """, (xp_actual, user_id))

        conn.commit()
        conn.close()

        return None

    xp_actual += cantidad
    subio = False

    while nivel < 500:
        requisito = xp_para_nivel(nivel)

        if xp_actual < requisito:
            break

        xp_actual -= requisito
        nivel += 1
        subio = True

    if nivel >= 500:
        nivel = 500
        xp_actual = min(
            xp_actual,
            xp_para_nivel(500)
        )

    c.execute("""
        UPDATE usuarios
        SET xp = ?, nivel = ?
        WHERE user_id = ?
    """, (
        xp_actual,
        nivel,
        user_id
    ))

    conn.commit()
    conn.close()

    return nivel if subio else None


def barra_progreso(xp, nivel):
    nivel = max(1, min(int(nivel), 500))

    requisito = xp_para_nivel(nivel)

    xp_actual = max(
        0,
        min(int(xp or 0), requisito)
    )

    porcentaje = int(
        (xp_actual / requisito) * 100
    )

    bloques = max(
        0,
        min(20, porcentaje // 5)
    )

    barra = (
        "█" * bloques +
        "░" * (20 - bloques)
    )

    return f"[{barra}] {porcentaje}%"


def rango_por_nivel(nivel):
    if nivel < 5:
        return "🥉 Novato"
    elif nivel < 10:
        return "🥈 Aprendiz"
    elif nivel < 20:
        return "🥇 Veterano"
    elif nivel < 35:
        return "💎 Élite"
    elif nivel < 50:
        return "👑 Maestro"
    else:
        return "🔥 Leyenda"


# ============================================================
# PAÍS
# ============================================================

def obtener_pais(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT pais FROM usuarios WHERE user_id = ?",
        (user_id,)
    )

    resultado = c.fetchone()

    conn.close()

    return resultado[0] if resultado else None


def set_pais(user_id, pais):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE usuarios
        SET pais = ?
        WHERE user_id = ?
    """, (pais, user_id))

    conn.commit()
    conn.close()


def usuario_tiene_pais(user_id):
    pais = obtener_pais(user_id)

    return pais is not None and pais != ""


# ============================================================
# ÚLTIMA ACTIVIDAD
# ============================================================

def actualizar_ultima_actividad(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE usuarios
        SET ultima_actividad = ?
        WHERE user_id = ?
    """, (
        time.time(),
        user_id
    ))

    conn.commit()
    conn.close()


def obtener_ultima_actividad(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT ultima_actividad
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))

    resultado = c.fetchone()

    conn.close()

    return resultado[0] if resultado and resultado[0] else 0


def esta_online(user_id, minutos=5):
    ultima = obtener_ultima_actividad(user_id)

    if ultima == 0:
        return False

    return (
        time.time() - ultima
    ) < (minutos * 60)

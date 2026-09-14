import sqlite3
import os

# Railway inyecta RAILWAY_VOLUME_MOUNT_PATH automáticamente cuando hay un volumen.
# Si existe, la usamos. Si no, usamos la ruta local (para Termux).
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
            sesion_activa INTEGER DEFAULT 1,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Añadir columna pais si no existe
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN pais TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def esta_registrado(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM usuarios WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r is not None


def obtener_datos(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT nombre, id_interno, tokens, xp, nivel, sesion_activa "
        "FROM usuarios WHERE user_id = ?",
        (user_id,)
    )
    r = c.fetchone()
    conn.close()
    return r


def obtener_todos_los_usuarios():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM usuarios")
    ids = [f[0] for f in c.fetchall()]
    conn.close()
    return ids


def obtener_lista_usuarios():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id_interno, nombre FROM usuarios ORDER BY id_interno ASC")
    lista = c.fetchall()
    conn.close()
    return lista


def obtener_ids_ocupados():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id_interno FROM usuarios WHERE id_interno IS NOT NULL")
    ids = [f[0] for f in c.fetchall()]
    conn.close()
    return ids


def siguiente_id_libre():
    ocupados = set(obtener_ids_ocupados())
    n = 1
    while n in ocupados:
        n += 1
    return n


def registrar(user_id, username, nombre, pais=None):
    id_interno = siguiente_id_libre()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO usuarios "
        "(user_id, username, nombre, id_interno, tokens, xp, nivel, sesion_activa, pais) "
        "VALUES (?, ?, ?, ?, 100, 0, 1, 1, ?)",
        (user_id, username, nombre, id_interno, pais)
    )
    conn.commit()
    conn.close()
    return id_interno


def eliminar_usuario(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def actualizar_sesion(user_id, estado):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET sesion_activa = ? WHERE user_id = ?", (estado, user_id))
    conn.commit()
    conn.close()


def actualizar_tokens(user_id, cantidad):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET tokens = tokens + ? WHERE user_id = ?", (cantidad, user_id))
    conn.commit()
    conn.close()


def actualizar_xp(user_id, cantidad):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET xp = xp + ? WHERE user_id = ?", (cantidad, user_id))
    conn.commit()
    conn.close()


def resetear_xp(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET xp = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def obtener_user_id_por_nombre(nombre):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM usuarios WHERE LOWER(nombre) = LOWER(?)", (nombre,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None


def xp_para_nivel(nivel):
    return 500 * nivel


def xp_total_para_nivel(nivel):
    if nivel <= 1:
        return 0
    total = 0
    for n in range(1, nivel):
        total += xp_para_nivel(n)
    return total


def sumar_xp(user_id, cantidad):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT xp, nivel FROM usuarios WHERE user_id = ?", (user_id,))
    xp_actual, nivel = c.fetchone()

    if nivel >= 500:
        conn.close()
        return None

    xp_actual += cantidad
    if xp_actual < 0:
        xp_actual = 0

    subio = False
    while nivel < 500 and xp_actual >= xp_para_nivel(nivel):
        xp_actual -= xp_para_nivel(nivel)
        nivel += 1
        subio = True

    c.execute("UPDATE usuarios SET xp = ?, nivel = ? WHERE user_id = ?", (xp_actual, nivel, user_id))
    conn.commit()
    conn.close()
    return nivel if subio else None


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


def barra_progreso(xp, nivel):
    base = xp_total_para_nivel(nivel)
    siguiente = xp_total_para_nivel(nivel + 1)
    actual = xp - base
    total = siguiente - base
    if total <= 0:
        total = 1
    porcentaje = min(int((actual / total) * 100), 100)
    bloques = int(porcentaje / 5)
    barra = "█" * bloques + "░" * (20 - bloques)
    return f"[{barra}] {porcentaje}%"


# ============================================================
# FUNCIONES DE PAÍS
# ============================================================
def obtener_pais(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT pais FROM usuarios WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None


def set_pais(user_id, pais):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET pais = ? WHERE user_id = ?", (pais, user_id))
    conn.commit()
    conn.close()


def usuario_tiene_pais(user_id):
    pais = obtener_pais(user_id)
    return pais is not None and pais != ""

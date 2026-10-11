import os
import sqlite3

RAILWAY_VOLUME_MOUNT_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")

if RAILWAY_VOLUME_MOUNT_PATH:
    DB_PATH = os.path.join(RAILWAY_VOLUME_MOUNT_PATH, "usuarios.db")
else:
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "usuarios.db"
    )


RAZAS = {
    "humano": {
        "nombre": "Humano",
        "faccion": "Alianza",
        "bonus": {"espiritu": 1},
        "clases": [
            "Guerrero", "Paladín", "Cazador", "Pícaro",
            "Sacerdote", "Mago", "Brujo", "Monje",
            "Caballero de la Muerte"
        ]
    },
    "enano": {
        "nombre": "Enano",
        "faccion": "Alianza",
        "bonus": {"resistencia": 2},
        "clases": [
            "Guerrero", "Paladín", "Cazador", "Pícaro",
            "Sacerdote", "Mago", "Chamán", "Monje",
            "Caballero de la Muerte"
        ]
    },
    "elfo_noche": {
        "nombre": "Elfo de la Noche",
        "faccion": "Alianza",
        "bonus": {"agilidad": 2},
        "clases": [
            "Guerrero", "Cazador", "Druida", "Pícaro",
            "Sacerdote", "Monje", "Caballero de la Muerte",
            "Cazador de Demonios"
        ]
    },
    "gnomo": {
        "nombre": "Gnomo",
        "faccion": "Alianza",
        "bonus": {"intelecto": 2},
        "clases": [
            "Guerrero", "Pícaro", "Sacerdote", "Mago",
            "Brujo", "Monje", "Caballero de la Muerte"
        ]
    },
    "draenei": {
        "nombre": "Draenei",
        "faccion": "Alianza",
        "bonus": {"resistencia": 1, "espiritu": 1},
        "clases": [
            "Guerrero", "Paladín", "Cazador", "Sacerdote",
            "Mago", "Chamán", "Monje", "Caballero de la Muerte"
        ]
    },
    "huargen": {
        "nombre": "Huargen",
        "faccion": "Alianza",
        "bonus": {"agilidad": 2},
        "clases": [
            "Guerrero", "Cazador", "Druida", "Pícaro",
            "Sacerdote", "Mago", "Brujo",
            "Caballero de la Muerte"
        ]
    },
    "orco": {
        "nombre": "Orco",
        "faccion": "Horda",
        "bonus": {"fuerza": 2},
        "clases": [
            "Guerrero", "Cazador", "Pícaro", "Chamán",
            "Brujo", "Monje", "Caballero de la Muerte"
        ]
    },
    "no_muerto": {
        "nombre": "No-muerto",
        "faccion": "Horda",
        "bonus": {"intelecto": 1, "espiritu": 1},
        "clases": [
            "Guerrero", "Cazador", "Pícaro", "Sacerdote",
            "Mago", "Brujo", "Monje", "Caballero de la Muerte"
        ]
    },
    "tauren": {
        "nombre": "Tauren",
        "faccion": "Horda",
        "bonus": {"resistencia": 3},
        "clases": [
            "Guerrero", "Paladín", "Cazador", "Druida",
            "Sacerdote", "Chamán", "Monje",
            "Caballero de la Muerte"
        ]
    },
    "trol": {
        "nombre": "Trol",
        "faccion": "Horda",
        "bonus": {"agilidad": 2},
        "clases": [
            "Guerrero", "Cazador", "Druida", "Pícaro",
            "Sacerdote", "Mago", "Chamán", "Brujo",
            "Monje", "Caballero de la Muerte"
        ]
    },
    "elfo_sangre": {
        "nombre": "Elfo de Sangre",
        "faccion": "Horda",
        "bonus": {"intelecto": 2},
        "clases": [
            "Guerrero", "Paladín", "Cazador", "Pícaro",
            "Sacerdote", "Mago", "Brujo", "Monje",
            "Caballero de la Muerte", "Cazador de Demonios"
        ]
    },
    "goblin": {
        "nombre": "Goblin",
        "faccion": "Horda",
        "bonus": {"agilidad": 1, "intelecto": 1},
        "clases": [
            "Guerrero", "Cazador", "Pícaro", "Sacerdote",
            "Mago", "Chamán", "Brujo",
            "Caballero de la Muerte"
        ]
    },
    "pandaren": {
        "nombre": "Pandaren",
        "faccion": "Neutral",
        "bonus": {"espiritu": 2},
        "clases": [
            "Guerrero", "Cazador", "Pícaro", "Sacerdote",
            "Mago", "Chamán", "Brujo", "Monje",
            "Caballero de la Muerte"
        ]
    },
    "dracthyr": {
        "nombre": "Dracthyr",
        "faccion": "Neutral",
        "bonus": {"intelecto": 2, "agilidad": 1},
        "clases": [
            "Evocador", "Guerrero", "Cazador", "Pícaro",
            "Sacerdote", "Mago", "Brujo",
            "Caballero de la Muerte"
        ]
    }
}


CLASES = {
    "Guerrero": {
        "rol": "Tanque / daño físico",
        "base": {
            "fuerza": 12, "agilidad": 7, "intelecto": 3,
            "resistencia": 12, "espiritu": 5,
            "hp": 150, "mp": 30
        },
        "habilidades": [
            "Golpe Heroico", "Embate", "Grito de Batalla"
        ]
    },
    "Paladín": {
        "rol": "Tanque / daño / apoyo",
        "base": {
            "fuerza": 10, "agilidad": 5, "intelecto": 8,
            "resistencia": 11, "espiritu": 8,
            "hp": 135, "mp": 80
        },
        "habilidades": [
            "Golpe de Cruzado", "Destello de Luz", "Escudo Divino"
        ]
    },
    "Cazador": {
        "rol": "Daño a distancia",
        "base": {
            "fuerza": 7, "agilidad": 12, "intelecto": 5,
            "resistencia": 8, "espiritu": 6,
            "hp": 115, "mp": 70
        },
        "habilidades": [
            "Disparo Arcano", "Disparo de Conmoción", "Llamar Mascota"
        ]
    },
    "Pícaro": {
        "rol": "Daño físico / sigilo",
        "base": {
            "fuerza": 6, "agilidad": 13, "intelecto": 4,
            "resistencia": 7, "espiritu": 5,
            "hp": 110, "mp": 40
        },
        "habilidades": ["Puñalada", "Eviscerar", "Sigilo"]
    },
    "Sacerdote": {
        "rol": "Sanación / magia",
        "base": {
            "fuerza": 3, "agilidad": 5, "intelecto": 12,
            "resistencia": 7, "espiritu": 12,
            "hp": 90, "mp": 130
        },
        "habilidades": [
            "Palabra de Poder: Escudo", "Sanación", "Punición"
        ]
    },
    "Mago": {
        "rol": "Daño mágico",
        "base": {
            "fuerza": 3, "agilidad": 6, "intelecto": 14,
            "resistencia": 6, "espiritu": 10,
            "hp": 80, "mp": 150
        },
        "habilidades": [
            "Bola de Fuego", "Descarga de Escarcha", "Traslación"
        ]
    },
    "Brujo": {
        "rol": "Daño mágico / invocación",
        "base": {
            "fuerza": 4, "agilidad": 6, "intelecto": 13,
            "resistencia": 7, "espiritu": 9,
            "hp": 90, "mp": 140
        },
        "habilidades": [
            "Descarga de las Sombras", "Corrupción", "Invocar Diablillo"
        ]
    },
    "Druida": {
        "rol": "Versátil / sanación",
        "base": {
            "fuerza": 5, "agilidad": 7, "intelecto": 11,
            "resistencia": 8, "espiritu": 10,
            "hp": 100, "mp": 120
        },
        "habilidades": [
            "Fuego Lunar", "Rejuvenecimiento", "Enredaderas"
        ]
    },
    "Chamán": {
        "rol": "Daño / sanación",
        "base": {
            "fuerza": 8, "agilidad": 7, "intelecto": 10,
            "resistencia": 9, "espiritu": 8,
            "hp": 110, "mp": 110
        },
        "habilidades": [
            "Choque de Relámpagos", "Ola de Sanación", "Tótem de Fuego"
        ]
    },
    "Monje": {
        "rol": "Movilidad / tanque / sanación",
        "base": {
            "fuerza": 7, "agilidad": 12, "intelecto": 6,
            "resistencia": 9, "espiritu": 7,
            "hp": 120, "mp": 80
        },
        "habilidades": [
            "Palma del Tigre", "Patada Oscura", "Esfera de Sanación"
        ]
    },
    "Caballero de la Muerte": {
        "rol": "Tanque / daño",
        "base": {
            "fuerza": 13, "agilidad": 7, "intelecto": 5,
            "resistencia": 13, "espiritu": 6,
            "hp": 160, "mp": 50
        },
        "habilidades": [
            "Golpe de la Plaga", "Cadenas de Hielo",
            "Caparazón Antimagia"
        ]
    },
    "Cazador de Demonios": {
        "rol": "Daño / movilidad",
        "base": {
            "fuerza": 8, "agilidad": 14, "intelecto": 5,
            "resistencia": 9, "espiritu": 6,
            "hp": 125, "mp": 70
        },
        "habilidades": [
            "Golpe de Caos", "Inmersión", "Visión Espectral"
        ]
    },
    "Evocador": {
        "rol": "Daño / apoyo",
        "base": {
            "fuerza": 4, "agilidad": 7, "intelecto": 14,
            "resistencia": 7, "espiritu": 9,
            "hp": 85, "mp": 150
        },
        "habilidades": [
            "Aliento Ígneo", "Desintegrar", "Reverberación"
        ]
    }
}


def init_razas_clases_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registro_pendiente (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                nombre TEXT NOT NULL,
                pais TEXT NOT NULL,
                raza TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS personajes (
                user_id INTEGER PRIMARY KEY,
                raza TEXT NOT NULL,
                clase TEXT NOT NULL,
                fuerza INTEGER NOT NULL,
                agilidad INTEGER NOT NULL,
                intelecto INTEGER NOT NULL,
                resistencia INTEGER NOT NULL,
                espiritu INTEGER NOT NULL,
                hp_actual INTEGER NOT NULL,
                hp_max INTEGER NOT NULL,
                mp_actual INTEGER NOT NULL,
                mp_max INTEGER NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def guardar_registro_pendiente(user_id, username, nombre, pais):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO registro_pendiente
                (user_id, username, nombre, pais, raza)
            VALUES (?, ?, ?, ?, NULL)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                nombre = excluded.nombre,
                pais = excluded.pais,
                raza = NULL
        """, (user_id, username, nombre, pais))


def obtener_registro_pendiente(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT user_id, username, nombre, pais, raza
            FROM registro_pendiente
            WHERE user_id = ?
        """, (user_id,)).fetchone()


def guardar_raza_pendiente(user_id, raza_key):
    if raza_key not in RAZAS:
        return False

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            UPDATE registro_pendiente
            SET raza = ?
            WHERE user_id = ?
        """, (raza_key, user_id))
        return cur.rowcount > 0


def eliminar_registro_pendiente(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM registro_pendiente WHERE user_id = ?",
            (user_id,)
        )


def obtener_personaje(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT raza, clase, fuerza, agilidad, intelecto,
                   resistencia, espiritu, hp_actual, hp_max,
                   mp_actual, mp_max
            FROM personajes
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    if not row:
        return None

    raza_key = row[0]
    return {
        "raza_key": raza_key,
        "clase": row[1],
        "raza": RAZAS.get(raza_key, {}).get("nombre", raza_key),
        "fuerza": row[2],
        "agilidad": row[3],
        "intelecto": row[4],
        "resistencia": row[5],
        "espiritu": row[6],
        "hp_actual": row[7],
        "hp_max": row[8],
        "mp_actual": row[9],
        "mp_max": row[10],
        "faccion": RAZAS.get(raza_key, {}).get(
            "faccion", "Desconocida"
        )
    }


def personaje_completo(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT u.user_id
            FROM usuarios u
            INNER JOIN personajes p ON p.user_id = u.user_id
            WHERE u.user_id = ?
              AND p.raza IS NOT NULL
              AND p.clase IS NOT NULL
        """, (user_id,)).fetchone()

    return row is not None


def crear_personaje(user_id, raza_key, clase):
    if raza_key not in RAZAS:
        raise ValueError("Raza no válida.")

    raza = RAZAS[raza_key]

    if clase not in raza["clases"] or clase not in CLASES:
        raise ValueError(
            "Esa clase no está disponible para la raza elegida."
        )

    stats = dict(CLASES[clase]["base"])

    for stat, bonus in raza["bonus"].items():
        stats[stat] = stats.get(stat, 0) + bonus

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO personajes (
                user_id, raza, clase, fuerza, agilidad, intelecto,
                resistencia, espiritu, hp_actual, hp_max,
                mp_actual, mp_max
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                raza = excluded.raza,
                clase = excluded.clase,
                fuerza = excluded.fuerza,
                agilidad = excluded.agilidad,
                intelecto = excluded.intelecto,
                resistencia = excluded.resistencia,
                espiritu = excluded.espiritu,
                hp_actual = excluded.hp_max,
                hp_max = excluded.hp_max,
                mp_actual = excluded.mp_max,
                mp_max = excluded.mp_max
        """, (
            user_id, raza_key, clase,
            stats["fuerza"], stats["agilidad"],
            stats["intelecto"], stats["resistencia"],
            stats["espiritu"],
            stats["hp"], stats["hp"],
            stats["mp"], stats["mp"]
        ))


def habilidades_de_personaje(user_id):
    personaje = obtener_personaje(user_id)

    if not personaje:
        return []

    return CLASES.get(
        personaje["clase"], {}
    ).get("habilidades", [])
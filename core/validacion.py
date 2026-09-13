import sqlite3
import os

DB_PATH = os.path.expanduser("~/telegram_bot/usuarios.db")

PALABRAS_PROHIBIDAS = [
    "puta", "puto", "put@", "put4", "culo", "pinga", "mierda",
    "coño", "pendejo", "cabrón", "cabron", "verga", "pija",
    "polla", "mamon", "mamón", "marica", "maricon", "maricón",
    "joto", "jota", "zorra", "perra", "malparido", "hijueputa",
    "gonorrea", "carechimba", "careverga", "pirobo", "chupame",
    "mierdero", "putita", "putito", "pendeja", "estupido",
    "estúpido", "idiota", "imbecil", "imbécil", "tarado",
    "tarada", "gilipollas", "capullo", "hostia", "joder",
    "follar", "follando", "pito", "picha", "chinga", "chingada",
    "chichis", "nalga", "nalgas", "tetas", "pene", "vagina",
    "semen", "orgasmo", "porno", "pornografia", "pornografía",
    "violacion", "violación", "violador", "nazi", "hitler",
    "matate", "suicidate", "suicídate", "muerete", "muérete"
]


def tiene_espacios(nombre):
    return " " in nombre


def tiene_caracteres_invalidos(nombre):
    for c in nombre:
        if not (c.isalpha() or c.isdigit()):
            return True
    return False


def es_palabra_prohibida(nombre):
    return nombre.lower().strip() in PALABRAS_PROHIBIDAS


def longitud_valida(nombre):
    return 2 <= len(nombre) <= 25


def nombre_ya_existe(nombre):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT user_id FROM usuarios WHERE LOWER(nombre) = LOWER(?)",
        (nombre,)
    )
    r = c.fetchone()
    conn.close()
    return r is not None


def validar_nombre(nombre):
    nombre = nombre.strip()

    if not longitud_valida(nombre):
        return False, "❌ El nombre debe tener entre *2* y *25* caracteres."

    if tiene_espacios(nombre):
        return False, "❌ El nombre no puede tener espacios.\nPrueba con algo como `OriGamePlay67`."

    if tiene_caracteres_invalidos(nombre):
        return False, "❌ El nombre solo puede tener *letras* y *números*.\nNo se permiten símbolos ni espacios."

    if es_palabra_prohibida(nombre):
        return False, "🚫 Ese nombre no está permitido.\nPor favor elige otro."

    if nombre_ya_existe(nombre):
        return False, (
            f"⚠️ El nombre *{nombre}* ya está en uso.\n\n"
            "Los nombres son únicos (no importa si usas mayúsculas o minúsculas).\n"
            f"Prueba con otro, por ejemplo: `{nombre}2` o `{nombre}X`."
        )

    return True, ""

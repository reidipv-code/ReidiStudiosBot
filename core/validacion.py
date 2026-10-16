import sqlite3

from core.db import DB_PATH

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


def validar_nombre(nombre):
    """
    Valida el nombre que el usuario quiere utilizar.

    Retorna:
        (True, None) si el nombre es válido.
        (False, mensaje) si el nombre no es válido.
    """

    if not nombre:
        return False, "❌ Debes indicar un nombre."

    nombre = nombre.strip()

    if len(nombre) < 3:
        return False, "❌ El nombre debe tener al menos 3 caracteres."

    if len(nombre) > 20:
        return False, "❌ El nombre no puede tener más de 20 caracteres."

    if " " in nombre:
        return False, "❌ El nombre no puede contener espacios."

    caracteres_permitidos = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "_-"
    )

    for caracter in nombre:
        if caracter not in caracteres_permitidos:
            return False, (
                "❌ El nombre solo puede contener letras, "
                "números, `_` y `-`."
            )

    if nombre.lower() in PALABRAS_PROHIBIDAS:
        return False, "🚫 Ese nombre no está permitido.\nPor favor elige otro."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT user_id
            FROM usuarios
            WHERE LOWER(nombre) = LOWER(?)
            """,
            (nombre,)
        )

        resultado = cursor.fetchone()

        conn.close()

        if resultado:
            return False, "❌ Ese nombre ya está registrado."

    except Exception as e:
        print(
            f"[VALIDACION ERROR] "
            f"{type(e).__name__}: {e}"
        )

        return False, (
            "❌ No se pudo comprobar el nombre "
            "en la base de datos."
        )

    return True, None

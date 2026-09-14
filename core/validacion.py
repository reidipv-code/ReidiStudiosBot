import sqlite3

from core.db import DB_PATH


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

    # Longitud mínima
    if len(nombre) < 3:
        return False, "❌ El nombre debe tener al menos 3 caracteres."

    # Longitud máxima
    if len(nombre) > 20:
        return False, "❌ El nombre no puede tener más de 20 caracteres."

    # No permitir espacios
    if " " in nombre:
        return False, "❌ El nombre no puede contener espacios."

    # Solo letras, números y algunos caracteres permitidos
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

    # Comprobar que no exista otro usuario con ese nombre
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

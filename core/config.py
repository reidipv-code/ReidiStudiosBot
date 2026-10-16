import os
from zoneinfo import ZoneInfo
from datetime import datetime

# Zona horaria leída de la variable de entorno ZONA_HORARIA
ZONA_HORARIA = os.getenv("ZONA_HORARIA", "America/Havana")
ZONA = ZoneInfo(ZONA_HORARIA)


def ahora() -> datetime:
    return datetime.now(ZONA)


def formatear_fecha() -> str:
    return ahora().strftime("%d/%m/%Y - %H:%M")

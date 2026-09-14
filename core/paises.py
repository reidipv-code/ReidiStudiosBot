# Lista de países y zonas horarias 
PAISES = {
    "mexico": {"nombre": "México", "zona": "America/Mexico_City", "bandera": "🇲🇽"},
    "cuba": {"nombre": "Cuba", "zona": "America/Havana", "bandera": "🇨🇺"},
    "salvador": {"nombre": "El Salvador", "zona": "America/El_Salvador", "bandera": "🇸🇻"},
    "ecuador": {"nombre": "Ecuador", "zona": "America/Guayaquil", "bandera": "🇪🇨"},
    "argentina": {"nombre": "Argentina", "zona": "America/Argentina/Buenos_Aires", "bandera": "🇦🇷"},
    "colombia": {"nombre": "Colombia", "zona": "America/Bogota", "bandera": "🇨🇴"},
    "peru": {"nombre": "Perú", "zona": "America/Lima", "bandera": "🇵🇪"},
    "chile": {"nombre": "Chile", "zona": "America/Santiago", "bandera": "🇨🇱"},
    "venezuela": {"nombre": "Venezuela", "zona": "America/Caracas", "bandera": "🇻🇪"},
    "guatemala": {"nombre": "Guatemala", "zona": "America/Guatemala", "bandera": "🇬🇹"},
    "honduras": {"nombre": "Honduras", "zona": "America/Tegucigalpa", "bandera": "🇭🇳"},
    "costa_rica": {"nombre": "Costa Rica", "zona": "America/Costa_Rica", "bandera": "🇨🇷"},
    "panama": {"nombre": "Panamá", "zona": "America/Panama", "bandera": "🇵🇦"},
    "bolivia": {"nombre": "Bolivia", "zona": "America/La_Paz", "bandera": "🇧🇴"},
    "paraguay": {"nombre": "Paraguay", "zona": "America/Asuncion", "bandera": "🇵🇾"},
    "uruguay": {"nombre": "Uruguay", "zona": "America/Montevideo", "bandera": "🇺🇾"},
    "rep_dominicana": {"nombre": "Rep. Dominicana", "zona": "America/Santo_Domingo", "bandera": "🇩🇴"},
    "puerto_rico": {"nombre": "Puerto Rico", "zona": "America/Puerto_Rico", "bandera": "🇵🇷"},
    "nicaragua": {"nombre": "Nicaragua", "zona": "America/Managua", "bandera": "🇳🇮"},
    "espana": {"nombre": "España", "zona": "Europe/Madrid", "bandera": "🇪🇸"},
}


def es_pais_valido(pais):
    return pais.lower().strip() in PAISES


def obtener_zona(pais):
    if pais in PAISES:
        return PAISES[pais]["zona"]
    return "America/Havana"  # Por defecto Cuba


def obtener_nombre(pais):
    if pais in PAISES:
        return PAISES[pais]["nombre"]
    return "Desconocido"


def obtener_bandera(pais):
    if pais in PAISES:
        return PAISES[pais]["bandera"]
    return "🌎"


def lista_paises():
    return list(PAISES.keys())


def lista_paises_texto():
    texto = ""
    for codigo, info in PAISES.items():
        texto += f"{info['bandera']} `{codigo}` - {info['nombre']}\n"
    return texto

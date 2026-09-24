import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================
# CONFIGURACIÓN
# ============================================================

ANCHO = 900
ALTO = 560

FPS = 10
FRAMES_ANIMADOS = 12


# ============================================================
# COLORES DEL NOMBRE
# ============================================================

COLORES_NOMBRE = {
    "color_dorado": (255, 211, 77),
    "color_rosa": (255, 105, 180),
    "color_cian": (75, 220, 255),
    "color_rojo": (255, 75, 75),
    "color_violeta": (190, 110, 255),
    "color_esmeralda": (55, 220, 135),
}


# ============================================================
# COLORES DE MARCOS
# ============================================================

COLORES_MARCO = {
    "marco_dorado": (255, 205, 65),
    "marco_diamante": (180, 240, 255),
    "marco_real": (245, 190, 70),
    "marco_glacial": (120, 220, 255),
    "marco_cosmico": (150, 100, 255),
    "marco_rosa_cristal": (255, 130, 210),
    "marco_corazones": (255, 80, 130),
    "marco_floral": (100, 220, 130),
    "marco_mariposas": (180, 110, 255),
    "marco_neon": (0, 255, 220),
    "marco_cyber": (50, 180, 255),
    "marco_samurai": (220, 70, 70),
    "marco_dark": (80, 80, 100),
    "marco_arcano": (160, 80, 255),
    "marco_esmeralda": (40, 210, 120),
    "marco_rubi": (230, 50, 70),
    "marco_ametista": (170, 80, 240),
}


# ============================================================
# COLORES DE FONDO
# ============================================================

COLORES_FONDO = {
    "fondo_noche": ((10, 12, 28), (35, 45, 85)),
    "fondo_nebulosa": ((25, 10, 50), (100, 30, 150)),
    "fondo_cyber": ((5, 20, 35), (0, 120, 150)),
    "fondo_rosa": ((45, 10, 35), (150, 40, 100)),
    "fondo_floresta": ((5, 35, 20), (30, 120, 70)),
    "fondo_abismo": ((3, 3, 10), (30, 10, 45)),
}


# ============================================================
# FUENTES
# ============================================================

def cargar_fuente(tamano, negrita=False):
    if negrita:
        posibles = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        posibles = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for ruta in posibles:
        try:
            return ImageFont.truetype(ruta, tamano)
        except Exception:
            pass

    return ImageFont.load_default()


# ============================================================
# UTILIDADES
# ============================================================

def texto_ajustado(draw, texto, fuente, max_ancho):
    texto = str(texto)

    try:
        ancho = draw.textbbox(
            (0, 0),
            texto,
            font=fuente
        )[2]

        if ancho <= max_ancho:
            return texto

        original = texto

        while len(texto) > 3:
            texto = texto[:-1]
            candidato = texto + "..."

            ancho = draw.textbbox(
                (0, 0),
                candidato,
                font=fuente
            )[2]

            if ancho <= max_ancho:
                return candidato

        return original[:1] + "..."

    except Exception:
        return texto


def crear_gradiente(color1, color2):
    imagen = Image.new(
        "RGB",
        (ANCHO, ALTO)
    )

    pixeles = imagen.load()

    for y in range(ALTO):
        t = y / max(1, ALTO - 1)

        r = int(
            color1[0] * (1 - t)
            + color2[0] * t
        )

        g = int(
            color1[1] * (1 - t)
            + color2[1] * t
        )

        b = int(
            color1[2] * (1 - t)
            + color2[2] * t
        )

        for x in range(ANCHO):
            pixeles[x, y] = (r, g, b)

    return imagen


def redimensionar_avatar(imagen):
    if imagen is None:
        return crear_avatar_iniciales("?")

    try:
        imagen = imagen.convert("RGBA")
    except Exception:
        return crear_avatar_iniciales("?")

    if imagen.width <= 0 or imagen.height <= 0:
        return crear_avatar_iniciales("?")

    lado = min(
        imagen.width,
        imagen.height
    )

    izquierda = (
        imagen.width - lado
    ) // 2

    arriba = (
        imagen.height - lado
    ) // 2

    imagen = imagen.crop(
        (
            izquierda,
            arriba,
            izquierda + lado,
            arriba + lado,
        )
    )

    return imagen.resize(
        (320, 320),
        Image.Resampling.LANCZOS
    )


def crear_avatar_iniciales(nombre):
    imagen = Image.new(
        "RGBA",
        (320, 320),
        (35, 40, 55, 255)
    )

    draw = ImageDraw.Draw(imagen)

    nombre = str(nombre or "?").strip()

    iniciales = "".join(
        parte[0]
        for parte in nombre.split()
        if parte
    )[:2].upper()

    if not iniciales:
        iniciales = "?"

    fuente = cargar_fuente(
        110,
        True
    )

    caja = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente
    )

    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    draw.text(
        (
            (320 - ancho) / 2,
            (320 - alto) / 2 - caja[1],
        ),
        iniciales,
        font=fuente,
        fill=(230, 235, 245, 255),
    )

    return imagen


def recortar_circulo(imagen):
    mascara = Image.new(
        "L",
        imagen.size,
        

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
# COLORES
# ============================================================

COLORES_NOMBRE = {
    "color_dorado": (255, 211, 77),
    "color_rosa": (255, 105, 180),
    "color_cian": (75, 220, 255),
    "color_rojo": (255, 75, 75),
    "color_violeta": (190, 110, 255),
    "color_esmeralda": (55, 220, 135),
}

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
    posibles = []

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
    """
    Acorta texto si es demasiado largo para la tarjeta.
    """
    if draw.textbbox((0, 0), texto, font=fuente)[2] <= max_ancho:
        return texto

    while len(texto) > 3:
        texto = texto[:-1]
        candidato = texto + "..."
        if draw.textbbox((0, 0), candidato, font=fuente)[2] <= max_ancho:
            return candidato

    return texto[:1] + "..."


def crear_gradiente(color1, color2):
    imagen = Image.new("RGB", (ANCHO, ALTO))
    pixeles = imagen.load()

    for y in range(ALTO):
        t = y / max(1, ALTO - 1)

        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)

        for x in range(ANCHO):
            pixeles[x, y] = (r, g, b)

    return imagen


def redimensionar_avatar(imagen):
    imagen = imagen.convert("RGBA")

    lado = min(imagen.width, imagen.height)

    izquierda = (imagen.width - lado) // 2
    arriba = (imagen.height - lado) // 2

    imagen = imagen.crop(
        (
            izquierda,
            arriba,
            izquierda + lado,
            arriba + lado,
        )
    )

    return imagen.resize((320, 320), Image.Resampling.LANCZOS)


def crear_avatar_iniciales(nombre):
    imagen = Image.new("RGBA", (320, 320), (35, 40, 55, 255))
    draw = ImageDraw.Draw(imagen)

    iniciales = "".join(
        parte[0]
        for parte in nombre.strip().split()
        if parte
    )[:2].upper()

    if not iniciales:
        iniciales = "?"

    fuente = cargar_fuente(110, True)

    caja = draw.textbbox((0, 0), iniciales, font=fuente)
    ancho = caja[2] - caja[0]
    alto = caja[3] - caja[1]

    draw.text(
        (
            (320 - ancho) / 2,
            (320 - alto) / 2 - caja[1],
        ),
        iniciales,
        font=fuente,
        fill=(230, 235, 245),
    )

    return imagen


def recortar_circulo(imagen):
    mascara = Image.new("L", imagen.size, 0)
    draw = ImageDraw.Draw(mascara)

    draw.ellipse(
        (
            0,
            0,
            imagen.width - 1,
            imagen.height - 1,
        ),
        fill=255,
    )

    resultado = Image.new("RGBA", imagen.size, (0, 0, 0, 0))
    resultado.paste(imagen, (0, 0), mascara)

    return resultado


# ============================================================
# FONDO
# ============================================================

def dibujar_fondo(imagen, fondo_id, frame):
    if fondo_id in COLORES_FONDO:
        c1, c2 = COLORES_FONDO[fondo_id]
        base = crear_gradiente(c1, c2)
        imagen.alpha_composite(base.convert("RGBA"))

    else:
        base = Image.new("RGBA", (ANCHO, ALTO), (12, 15, 25, 255))
        imagen.alpha_composite(base)

    draw = ImageDraw.Draw(imagen, "RGBA")

    # Decoración ambiental.
    random.seed(1234)

    for i in range(70):
        x = random.randint(0, ANCHO)
        y = random.randint(0, ALTO)
        radio = random.randint(1, 3)

        brillo = 90 + ((i * 17 + frame * 8) % 120)

        draw.ellipse(
            (
                x - radio,
                y - radio,
                x + radio,
                y + radio,
            ),
            fill=(255, 255, 255, brillo),
        )


# ============================================================
# AVATAR
# ============================================================

def dibujar_avatar(imagen, avatar, x=75, y=115):
    avatar = redimensionar_avatar(avatar)
    avatar = recortar_circulo(avatar)

    imagen.alpha_composite(avatar, (x, y))


# ============================================================
# MARCOS
# ============================================================

def dibujar_marco(imagen, marco_id, frame):
    draw = ImageDraw.Draw(imagen, "RGBA")

    cx = 235
    cy = 275
    radio = 175

    color = COLORES_MARCO.get(
        marco_id,
        (255, 255, 255),
    )

    # Aura.
    for grosor in range(30, 0, -5):
        alpha = int(25 * (1 - grosor / 35))

        draw.ellipse(
            (
                cx - radio - grosor,
                cy - radio - grosor,
                cx + radio + grosor,
                cy + radio + grosor,
            ),
            outline=(*color, alpha),
            width=5,
        )

    # Marco principal.
    draw.ellipse(
        (
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
        ),
        outline=(*color, 255),
        width=14,
    )

    # Segundo borde.
    draw.ellipse(
        (
            cx - radio - 10,
            cy - radio - 10,
            cx + radio + 10,
            cy + radio + 10,
        ),
        outline=(*color, 100),
        width=3,
    )

    # Decoraciones dependiendo del marco.
    if marco_id == "marco_corazones":
        _dibujar_corazones(draw, cx, cy, radio, frame)

    elif marco_id == "marco_floral":
        _dibujar_flores(draw, cx, cy, radio, frame)

    elif marco_id == "marco_mariposas":
        _dibujar_mariposas(draw, cx, cy, radio, frame)

    elif marco_id == "marco_arcano":
        _dibujar_runa(draw, cx, cy, radio, frame)

    elif marco_id == "marco_cyber":
        _dibujar_cyber(draw, cx, cy, radio)

    elif marco_id == "marco_samurai":
        _dibujar_samurai(draw, cx, cy, radio)

    elif marco_id == "marco_real":
        _dibujar_corona(draw, cx, cy, radio)

    elif marco_id == "marco_neon":
        _dibujar_neon(draw, cx, cy, radio, frame)


def _punto_circular(cx, cy, radio, angulo):
    rad = math.radians(angulo)

    return (
        cx + math.cos(rad) * radio,
        cy + math.sin(rad) * radio,
    )


def _dibujar_corazones(draw, cx, cy, radio, frame):
    color = (255, 80, 130, 230)

    for i in range(8):
        angulo = i * 45 + frame * 2
        x, y = _punto_circular(cx, cy, radio + 22, angulo)

        draw.polygon(
            [
                (x, y + 10),
                (x - 12, y - 5),
                (x - 7, y - 15),
                (x, y - 8),
                (x + 7, y - 15),
                (x + 12, y - 5),
            ],
            fill=color,
        )


def _dibujar_flores(draw, cx, cy, radio, frame):
    color = (130, 240, 160, 230)

    for i in range(8):
        angulo = i * 45
        x, y = _punto_circular(cx, cy, radio + 20, angulo)

        for petalo in range(5):
            a = math.radians(petalo * 72)

            px = x + math.cos(a) * 9
            py = y + math.sin(a) * 9

            draw.ellipse(
                (
                    px - 5,
                    py - 8,
                    px + 5,
                    py + 8,
                ),
                fill=color,
            )

        draw.ellipse(
            (
                x - 5,
                y - 5,
                x + 5,
                y + 5,
            ),
            fill=(255, 220, 70, 255),
        )


def _dibujar_mariposas(draw, cx, cy, radio, frame):
    color = (210, 130, 255, 230)

    for i in range(5):
        angulo = i * 72 + frame * 3

        x, y = _punto_circular(
            cx,
            cy,
            radio + 25,
            angulo,
        )

        draw.ellipse(
            (
                x - 13,
                y - 8,
                x - 1,
                y + 8,
            ),
            fill=color,
        )

        draw.ellipse(
            (
                x + 1,
                y - 8,
                x + 13,
                y + 8,
            ),
            fill=color,
        )

        draw.line(
            (
                x,
                y - 5,
                x,
                y + 8,
            ),
            fill=(40, 40, 60, 255),
            width=3,
        )


def _dibujar_runa(draw, cx, cy, radio, frame):
    color = (190, 100, 255, 220)

    for i in range(8):
        angulo = i * 45 + frame * 2
        x, y = _punto_circular(
            cx,
            cy,
            radio + 24,
            angulo,
        )

        draw.line(
            (
                x - 7,
                y - 7,
                x + 7,
                y + 7,
            ),
            fill=color,
            width=3,
        )

        draw.line(
            (
                x + 7,
                y - 7,
                x - 7,
                y + 7,
            ),
            fill=color,
            width=3,
        )


def _dibujar_cyber(draw, cx, cy, radio):
    color = (40, 220, 255, 230)

    for i in range(8):
        angulo = i * 45

        x, y = _punto_circular(
            cx,
            cy,
            radio + 15,
            angulo,
        )

        draw.rectangle(
            (
                x - 9,
                y - 9,
                x + 9,
                y + 9,
            ),
            outline=color,
            width=3,
        )


def _dibujar_samurai(draw, cx, cy, radio):
    color = (230, 70, 70, 240)

    draw.arc(
        (
            cx - radio - 25,
            cy - radio - 25,
            cx + radio + 25,
            cy + radio + 25,
        ),
        200,
        340,
        fill=color,
        width=9,
    )


def _dibujar_corona(draw, cx, cy, radio):
    color = (255, 215, 80, 255)

    y = cy - radio - 35

    draw.polygon(
        [
            (cx - 45, y + 35),
            (cx - 35, y),
            (cx, y + 25),
            (cx + 35, y),
            (cx + 45, y + 35),
        ],
        fill=color,
    )


def _dibujar_neon(draw, cx, cy, radio, frame):
    intensidad = 150 + int(
        100 * ((math.sin(frame / 2) + 1) / 2)
    )

    color = (
        0,
        intensidad,
        220,
        255,
    )

    draw.ellipse(
        (
            cx - radio - 18,
            cy - radio - 18,
            cx + radio + 18,
            cy + radio + 18,
        ),
        outline=color,
        width=7,
    )


# ============================================================
# EFECTOS
# ============================================================

def dibujar_efecto(imagen, efecto_id, frame):
    draw = ImageDraw.Draw(imagen, "RGBA")

    if efecto_id == "efecto_fuego":
        _efecto_fuego(draw, frame)

    elif efecto_id == "efecto_electricidad":
        _efecto_electricidad(draw, frame)

    elif efecto_id == "efecto_escarcha":
        _efecto_escarcha(draw, frame)

    elif efecto_id == "efecto_chispas":
        _efecto_chispas(draw, frame)

    elif efecto_id == "efecto_cosmico":
        _efecto_cosmico(draw, frame)

    elif efecto_id == "efecto_aura":
        _efecto_aura(imagen, frame)

    elif efecto_id == "efecto_corazones":
        _efecto_corazones(draw, frame)

    elif efecto_id == "efecto_petalo":
        _efecto_petalo(draw, frame)

    elif efecto_id == "efecto_mariposas":
        _efecto_mariposas(draw, frame)

    elif efecto_id == "efecto_burbujas":
        _efecto_burbujas(draw, frame)

    elif efecto_id == "efecto_estrellas":
        _efecto_estrellas(draw, frame)

    elif efecto_id == "efecto_arcoiris":
        _efecto_arcoiris(draw, frame)


def _efecto_fuego(draw, frame):
    random.seed(100 + frame)

    for i in range(35):
        x = random.randint(50, ANCHO - 50)
        y = random.randint(50, ALTO - 50)

        if 70 < x < 400 and 100 < y < 450:
            continue

        altura = random.randint(8, 25)

        draw.polygon(
            [
                (x, y + altura),
                (x - 7, y),
                (x, y - altura),
                (x + 7, y),
            ],
            fill=(
                255,
                random.randint(70, 190),
                30,
                random.randint(100, 230),
            ),
        )


def _efecto_electricidad(draw, frame):
    random.seed(200 + frame)

    for i in range(13):
        x = random.randint(40, ANCHO - 40)
        y = random.randint(40, ALTO - 40)

        puntos = [(x, y)]

        for _ in range(5):
            x += random.randint(-25, 25)
            y += random.randint(-25, 25)
            puntos.append((x, y))

        draw.line(
            puntos,
            fill=(100, 220, 255, 230),
            width=3,
        )


def _efecto_escarcha(draw, frame):
    random.seed(300 + frame)

    for i in range(40):
        x = random.randint(30, ANCHO - 30)
        y = random.randint(30, ALTO - 30)
        r = random.randint(2, 6)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(170, 240, 255, 180),
        )


def _efecto_chispas(draw, frame):
    random.seed(400 + frame)

    for i in range(30):
        x = random.randint(30, ANCHO - 30)
        y = random.randint(30, ALTO - 30)
        r = random.randint(2, 5)

        draw.line(
            (
                x - r * 2,
                y,
                x + r * 2,
                y,
            ),
            fill=(255, 220, 80, 230),
            width=2,
        )

        draw.line(
            (
                x,
                y - r * 2,
                x,
                y + r * 2,
            ),
            fill=(255, 220, 80, 230),
            width=2,
        )


def _efecto_cosmico(draw, frame):
    random.seed(500 + frame)

    for i in range(35):
        x = random.randint(0, ANCHO)
        y = random.randint(0, ALTO)
        r = random.randint(1, 4)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                random.randint(100, 230),
                random.randint(80, 180),
                255,
                random.randint(100, 230),
            ),
        )


def _efecto_aura(imagen, frame):
    overlay = Image.new(
        "RGBA",
        (ANCHO, ALTO),
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(overlay)

    radio = 250 + int(
        20 * math.sin(frame / 2)
    )

    draw.ellipse(
        (
            235 - radio,
            275 - radio,
            235 + radio,
            275 + radio,
        ),
        outline=(130, 80, 255, 80),
        width=30,
    )

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(15)
    )

    imagen.alpha_composite(overlay)


def _efecto_corazones(draw, frame):
    random.seed(600 + frame)

    for i in range(20):
        x = random.randint(40, ANCHO - 40)
        y = random.randint(30, ALTO - 30)

        color = (
            255,
            random.randint(70, 150),
            random.randint(120, 190),
            190,
        )

        draw.ellipse(
            (
                x - 7,
                y - 3,
                x,
                y + 7,
            ),
            fill=color,
        )

        draw.ellipse(
            (
                x,
                y - 3,
                x + 7,
                y + 7,
            ),
            fill=color,
        )

        draw.polygon(
            [
                (x - 7, y + 2),
                (x + 7, y + 2),
                (x, y + 12),
            ],
            fill=color,
        )


def _efecto_petalo(draw, frame):
    random.seed(700 + frame)

    for i in range(25):
        x = random.randint(20, ANCHO - 20)
        y = random.randint(20, ALTO - 20)

        draw.ellipse(
            (
                x - 4,
                y - 10,
                x + 4,
                y + 10,
            ),
            fill=(255, 130, 180, 170),
        )


def _efecto_mariposas(draw, frame):
    random.seed(800 + frame)

    for i in range(10):
        x = random.randint(30, ANCHO - 30)
        y = random.randint(30, ALTO - 30)

        color = (190, 100, 255, 210)

        draw.ellipse(
            (
                x - 12,
                y - 7,
                x - 1,
                y + 7,
            ),
            fill=color,
        )

        draw.ellipse(
            (
                x + 1,
                y - 7,
                x + 12,
                y + 7,
            ),
            fill=color,
        )

        draw.line(
            (x, y - 3, x, y + 8),
            fill=(30, 30, 50, 255),
            width=2,
        )


def _efecto_burbujas(draw, frame):
    random.seed(900 + frame)

    for i in range(25):
        x = random.randint(20, ANCHO - 20)
        y = random.randint(20, ALTO - 20)
        r = random.randint(3, 12)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            outline=(120, 220, 255, 170),
            width=2,
        )


def _efecto_estrellas(draw, frame):
    random.seed(1000 + frame)

    for i in range(25):
        x = random.randint(20, ANCHO - 20)
        y = random.randint(20, ALTO - 20)
        r = random.randint(4, 9)

        draw.line(
            (x - r, y, x + r, y),
            fill=(255, 255, 220, 220),
            width=2,
        )

        draw.line(
            (x, y - r, x, y + r),
            fill=(255, 255, 220, 220),
            width=2,
        )


def _efecto_arcoiris(draw, frame):
    colores = [
        (255, 70, 70, 150),
        (255, 170, 50, 150),
        (255, 240, 70, 150),
        (70, 230, 120, 150),
        (70, 180, 255, 150),
        (150, 90, 255, 150),
    ]

    for i, color in enumerate(colores):
        margen = i * 7

        draw.rounded_rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen,
            ),
            radius=35,
  

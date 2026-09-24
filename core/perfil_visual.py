import io
import math
import os

from PIL import Image, ImageDraw, ImageFont

from core.paises import PAISES


# ============================================================
# CONFIGURACIÓN
# ============================================================

ANCHO = 1920
ALTO = 1080

# ============================================================
# FUENTES
# ============================================================

FUENTE_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

FUENTE_NEGRITA = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

FUENTE_EMOJI = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/opentype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf",
]


# ============================================================
# TAMAÑOS
# ============================================================

FONT_NOMBRE = 132
FONT_PAIS = 58

FONT_ID = 46
FONT_TOKENS = 48

FONT_NIVEL = 76
FONT_XP = 68
FONT_PORCENTAJE = 56
FONT_RANGO = 62

FONT_EMOJI = 64

TAM_AVATAR = 360

FLAG_W = 82
FLAG_H = 52

X_CONTENIDO = 540

Y_NOMBRE = 100
Y_PAIS = 225

Y_ID = 325
Y_BOT_ID = 385
Y_TELEGRAM_ID = 445
Y_TOKENS = 505

Y_NIVEL = 600
Y_XP = 680
Y_BARRA = 765
Y_PORCENTAJE = 845
Y_RANGO = 925


# ============================================================
# COLORES DE NOMBRE
# ============================================================

COLORES_NOMBRE = {
    "blanco": (255, 255, 255),
    "rojo": (255, 75, 75),
    "azul": (75, 160, 255),
    "verde": (80, 225, 125),
    "amarillo": (255, 220, 70),
    "morado": (185, 100, 255),
    "rosa": (255, 105, 190),
    "cian": (70, 225, 255),
    "naranja": (255, 145, 65),
    "esmeralda": (40, 235, 155),
}


# ============================================================
# MARCOS
# ============================================================

COLORES_MARCO = {
    "normal": (100, 110, 130),
    "oro": (255, 205, 55),
    "plata": (205, 215, 230),
    "diamante": (80, 220, 255),
    "rojo": (255, 70, 70),
    "morado": (180, 85, 255),
    "esmeralda": (40, 235, 155),
    "azul": (70, 150, 255),
    "verde": (70, 225, 120),
}


# ============================================================
# FONDOS
# ============================================================

COLORES_FONDO = {
    "normal": (
        (17, 22, 37),
        (48, 60, 92),
    ),

    "azul": (
        (7, 20, 48),
        (25, 85, 155),
    ),

    "morado": (
        (25, 10, 52),
        (105, 35, 155),
    ),

    "rojo": (
        (50, 8, 18),
        (155, 30, 48),
    ),

    "verde": (
        (5, 35, 20),
        (25, 135, 78),
    ),

    "esmeralda": (
        (4, 32, 28),
        (20, 135, 100),
    ),

    "negro": (
        (5, 5, 8),
        (25, 25, 30),
    ),

    "dorado": (
        (45, 28, 5),
        (150, 95, 15),
    ),
}


# ============================================================
# ALIAS DE PRODUCTOS
# ============================================================

ALIASES_PRODUCTOS = {
    # Nombres
    "nombre_blanco": "blanco",
    "nombre_rojo": "rojo",
    "nombre_azul": "azul",
    "nombre_verde": "verde",
    "nombre_amarillo": "amarillo",
    "nombre_morado": "morado",
    "nombre_rosa": "rosa",
    "nombre_cian": "cian",
    "nombre_naranja": "naranja",
    "nombre_esmeralda": "esmeralda",

    # Marcos
    "marco_normal": "normal",
    "marco_oro": "oro",
    "marco_plata": "plata",
    "marco_diamante": "diamante",
    "marco_rojo": "rojo",
    "marco_morado": "morado",
    "marco_esmeralda": "esmeralda",
    "marco_azul": "azul",
    "marco_verde": "verde",

    # Fondos
    "fondo_normal": "normal",
    "fondo_azul": "azul",
    "fondo_morado": "morado",
    "fondo_rojo": "rojo",
    "fondo_verde": "verde",
    "fondo_esmeralda": "esmeralda",
    "fondo_negro": "negro",
    "fondo_dorado": "dorado",
}


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalizar_texto(valor):
    if valor is None:
        return ""

    return (
        str(valor)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )


def _producto_id(producto):
    if producto is None:
        return ""

    if isinstance(producto, dict):

        for clave in (
            "id",
            "producto_id",
            "nombre",
            "item",
            "slug",
            "codigo",
            "tipo",
        ):
            valor = producto.get(clave)

            if valor is not None:
                return _normalizar_texto(valor)

        return ""

    return _normalizar_texto(producto)


def normalizar_equipados(equipados):
    if equipados is None:
        return []

    if isinstance(equipados, dict):

        resultado = []

        for clave, valor in equipados.items():

            # Caso:
            # {"nombre": "esmeralda"}
            if isinstance(
                valor,
                (list, tuple, set)
            ):
                resultado.extend(
                    list(valor)
                )

            elif valor:
                resultado.append(
                    valor
                )

            else:
                resultado.append(
                    clave
                )

        return resultado

    if isinstance(
        equipados,
        (list, tuple, set)
    ):
        return list(equipados)

    return [equipados]


# ============================================================
# DETECTAR COSMÉTICOS
# ============================================================

def _buscar_cosmetico(
    equipados,
    prefijos,
    palabras=()
):
    for producto in equipados:

        pid = _producto_id(
            producto
        )

        if not pid:
            continue

        # Alias exacto.
        if pid in ALIASES_PRODUCTOS:

            for prefijo in prefijos:
                if pid.startswith(prefijo):
                    return ALIASES_PRODUCTOS[pid]

        # Prefijos.
        for prefijo in prefijos:

            if pid.startswith(prefijo):

                valor = pid[
                    len(prefijo):
                ].strip("_")

                if valor:
                    return valor

        # Palabras.
        for palabra in palabras:

            if palabra in pid:

                return pid

    return None


def detectar_color_nombre(
    equipados
):
    resultado = _buscar_cosmetico(
        equipados,
        (
            "nombre_",
            "color_nombre_",
            "color_",
        ),
        (
            "esmeralda",
            "rojo",
            "azul",
            "verde",
            "amarillo",
            "morado",
            "rosa",
            "cian",
            "naranja",
        )
    )

    if resultado in COLORES_NOMBRE:
        return resultado

    return "blanco"


def detectar_marco(
    equipados
):
    resultado = _buscar_cosmetico(
        equipados,
        (
            "marco_",
            "borde_",
        ),
        (
            "oro",
            "plata",
            "diamante",
            "esmeralda",
            "morado",
            "rojo",
            "azul",
            "verde",
        )
    )

    if resultado in COLORES_MARCO:
        return resultado

    return "normal"


def detectar_fondo(
    equipados
):
    resultado = _buscar_cosmetico(
        equipados,
        (
            "fondo_",
            "background_",
            "estilo_",
        ),
        (
            "esmeralda",
            "azul",
            "morado",
            "rojo",
            "verde",
            "negro",
            "dorado",
        )
    )

    if resultado in COLORES_FONDO:
        return resultado

    return "normal"


# ============================================================
# FUENTES
# ============================================================

def cargar_fuente(
    tamano,
    negrita=False
):
    rutas = (
        FUENTE_NEGRITA
        if negrita
        else FUENTE_NORMAL
    )

    for ruta in rutas:

        if not os.path.exists(ruta):
            continue

        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except Exception:
            pass

    try:
        return ImageFont.load_default(
            size=32
        )
    except Exception:
        return ImageFont.load_default()


def cargar_fuente_emoji(
    tamano=FONT_EMOJI
):
    for ruta in FUENTE_EMOJI:

        if not os.path.exists(ruta):
            continue

        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except Exception:
            pass

    return cargar_fuente(
        tamano
    )


# ============================================================
# TEXTO
# ============================================================

def texto_ajustado(
    draw,
    texto,
    fuente,
    max_ancho
):
    texto = str(texto)

    bbox = draw.textbbox(
        (0, 0),
        texto,
        font=fuente
    )

    if (
        bbox[2] - bbox[0]
        <= max_ancho
    ):
        return texto

    while len(texto) > 3:

        texto = texto[:-1]

        prueba = texto + "..."

        bbox = draw.textbbox(
            (0, 0),
            prueba,
            font=fuente
        )

        if (
            bbox[2] - bbox[0]
            <= max_ancho
        ):
            return prueba

    return "..."


# ============================================================
# FONDO
# ============================================================

def crear_gradiente(
    color1,
    color2
):
    imagen = Image.new(
        "RGB",
        (
            ANCHO,
            ALTO
        )
    )

    pixeles = imagen.load()

    for y in range(ALTO):

        factor = (
            y / max(
                1,
                ALTO - 1
            )
        )

        r = int(
            color1[0] * (1 - factor)
            + color2[0] * factor
        )

        g = int(
            color1[1] * (1 - factor)
            + color2[1] * factor
        )

        b = int(
            color1[2] * (1 - factor)
            + color2[2] * factor
        )

        for x in range(ANCHO):
            pixeles[x, y] = (
                r,
                g,
                b
            )

    return imagen


def dibujar_fondo(
    imagen,
    estilo="normal",
    frame=0
):
    estilo = _normalizar_texto(
        estilo
    )

    colores = COLORES_FONDO.get(
        estilo,
        COLORES_FONDO["normal"]
    )

    fondo = crear_gradiente(
        *colores
    )

    overlay = Image.new(
        "RGBA",
        (
            ANCHO,
            ALTO
        ),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # Círculos de luz.
    draw.ellipse(
        (
            1250,
            -300,
            2150,
            600
        ),
        fill=(255, 255, 255, 15)
    )

    draw.ellipse(
        (
            -400,
            650,
            650,
            1600
        ),
        fill=(0, 0, 0, 30)
    )

    # Líneas decorativas.
    for i in range(12):

        desplazamiento = (
            (frame * 2 + i * 120)
            % 500
        )

        draw.line(
            (
                1050 + desplazamiento,
                0,
                500 + desplazamiento,
                ALTO
            ),
            fill=(255, 255, 255, 8),
            width=3
        )

    # Borde.
    draw.rounded_rectangle(
        (
            20,
            20,
            ANCHO - 20,
            ALTO - 20
        ),
        radius=28,
        outline=(255, 255, 255, 35),
        width=3
    )

    fondo = Image.alpha_composite(
        fondo.convert("RGBA"),
        overlay
    )

    imagen.paste(
        fondo.convert("RGB"),
        (0, 0)
    )


# ============================================================
# AVATAR
# ============================================================

def redimensionar_avatar(
    avatar,
    tamano
):
    if avatar is None:
        return None

    return avatar.convert(
        "RGBA"
    ).resize(
        (
            tamano,
            tamano
        ),
        Image.Resampling.LANCZOS
    )


def crear_avatar_iniciales(
    nombre,
    tamano=TAM_AVATAR
):
    imagen = Image.new(
        "RGBA",
        (
            tamano,
            tamano
        ),
        (35, 40, 55, 255)
    )

    draw = ImageDraw.Draw(
        imagen
    )

    partes = str(
        nombre or "?"
    ).strip().split()

    if len(partes) >= 2:

        iniciales = (
            partes[0][0]
            + partes[1][0]
        ).upper()

    elif partes:

        iniciales = partes[0][:2].upper()

    else:

        iniciales = "?"

    fuente = cargar_fuente(
        135,
        negrita=True
    )

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente
    )

    ancho = bbox[2] - bbox[0]
    alto = bbox[3] - bbox[1]

    draw.text(
        (
            (tamano - ancho) / 2,
            (tamano - alto) / 2 - 8
        ),
        iniciales,
        font=fuente,
        fill=(245, 245, 250, 255)
    )

    return imagen


def recortar_circulo(
    imagen,
    tamano
):
    imagen = redimensionar_avatar(
        imagen,
        tamano
    )

    if imagen is None:
        return None

    mascara = Image.new(
        "L",
        (
            tamano,
            tamano
        ),
        0
    )

    draw = ImageDraw.Draw(
        mascara
    )

    draw.ellipse(
        (
            0,
            0,
            tamano - 1,
            tamano - 1
        ),
        fill=255
    )

    resultado = Image.new(
        "RGBA",
        (
            tamano,
            tamano
        ),
        (0, 0, 0, 0)
    )

    resultado.paste(
        imagen,
        (0, 0),
        mascara
    )

    return resultado


def dibujar_avatar(
    imagen,
    avatar,
    x,
    y,
    tamano,
    color_marco=None
):
    avatar = recortar_circulo(
        avatar,
        tamano
    )

    if avatar is None:
        return

    if color_marco is None:
        color_marco = (
            100,
            110,
            130
        )

    overlay = Image.new(
        "RGBA",
        imagen.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # Resplandor.
    draw.ellipse(
        (
            x - 24,
            y - 24,
            x + tamano + 24,
            y + tamano + 24
        ),
        outline=(
            *color_marco,
            70
        ),
        width=24
    )

    # Marco.
    draw.ellipse(
        (
            x - 12,
            y - 12,
            x + tamano + 12,
            y + tamano + 12
        ),
        outline=(
            *color_marco,
            255
        ),
        width=12
    )

    imagen.alpha_composite(
        overlay
    )

    imagen.alpha_composite(
        avatar,
        (
            x,
            y
        )
    )


# ============================================================
# BANDERAS
# ============================================================

def _pais_codigo(pais):
    if not pais:
        return None

    valor = str(
        pais
    ).strip().lower()

    for codigo, datos in PAISES.items():

        nombre = str(
            datos.get(
                "nombre",
                ""
            )
        ).lower()

        bandera = str(
            datos.get(
                "bandera",
                ""
            )
        )

        if valor == codigo.lower():
            return codigo

        if valor == nombre:
            return codigo

        if bandera and bandera in str(pais):
            return codigo

        if nombre and nombre in valor:
            return codigo

    return None


def _dibujar_estrella(
    draw,
    cx,
    cy,
    radio,
    color
):
    puntos = []

    for i in range(10):

        angulo = (
            -math.pi / 2
            + i * math.pi / 5
        )

        r = (
            radio
            if i % 2 == 0
            else radio * 0.42
        )

        puntos.append(
            (
                cx + math.cos(angulo) * r,
                cy + math.sin(angulo) * r
            )
        )

    draw.polygon(
        puntos,
        fill=color
    )


def dibujar_bandera(
    draw,
    pais,
    x,
    y,
    ancho=FLAG_W,
    alto=FLAG_H
):
    codigo = _pais_codigo(
        pais
    )

    if not codigo:
        return

    if codigo == "cuba":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            fill=(255, 255, 255)
        )

        h = alto / 5

        for i in range(5):

            if i % 2 == 0:

                draw.rectangle(
                    (
                        x,
                        y + i * h,
                        x + ancho,
                        y + (i + 1) * h
                    ),
                    fill=(35, 85, 170)
                )

        draw.polygon(
            [
                (x, y),
                (
                    x + ancho * 0.48,
                    y + alto / 2
                ),
                (
                    x,
                    y + alto
                )
            ],
            fill=(210, 35, 45)
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto / 2,
            alto * 0.18,
            (255, 255, 255)
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            outline=(255, 255, 255),
            width=3
        )

        return

    datos = PAISES.get(
        codigo,
        {}
    )

    bandera = datos.get(
        "bandera",
        ""
    )

    if bandera:

        fuente = cargar_fuente_emoji(
            40
        )

        draw.text(
            (
                x + ancho / 2,
                y + alto / 2
            ),
            bandera,
            font=fuente,
            anchor="mm"
        )


# ============================================================
# MARCOS
# ============================================================

def dibujar_marco(
    draw,
    x,
    y,
    tamano,
    tipo="normal"
):
    tipo = _normalizar_texto(
        tipo
    )

    color = COLORES_MARCO.get(
        tipo,
        COLORES_MARCO["normal"]
    )

    # Sombra.
    draw.ellipse(
        (
            x - 24,
            y - 24,
            x + tamano + 24,
            y + tamano + 24
        ),
        outline=(
            0,
            0,
            0,
            100
        ),
        width=28
    )

    # Marco principal.
    draw.ellipse(
        (
            x - 14,
            y - 14,
            x + tamano + 14,
            y + tamano + 14
        ),
        outline=color,
        width=14
    )

    # Marcos especiales.
    if tipo == "oro":

        draw.arc(
            (
                x - 24,
                y - 24,
                x + tamano + 24,
                y + tamano + 24
            ),
            210,
            330,
            fill=(255, 240, 130),
            width=8
        )

    elif tipo == "diamante":

        for angulo in range(
            0,
            360,
            45
        ):

            rad = math.radians(
                angulo
            )

            cx = (
                x + tamano / 2
                + math.cos(rad)
                * (tamano / 2 + 28)
            )

            cy = (
                y + tamano / 2
                + math.sin(rad)
                * (tamano / 2 + 28)
            )

            _dibujar_estrella(
                draw,
                cx,
                cy,
                10,
                color
            )

    elif tipo == "esmeralda":

        draw.arc(
            (
                x - 28,
                y - 28,
                x + tamano + 28,
                y + tamano + 28
            ),
            0,
            180,
            fill=(110, 255, 190),
            width=7
        )

        draw.arc(
            (
                x - 28,
                y - 28,
                x + tamano + 28,
                y + tamano + 28
            ),
            180,
            360,
            fill=(20, 180, 120),
            width=7
        )

    elif tipo in (
        "rojo",
        "morado",
        "azul",
        "verde"
    ):

        draw.ellipse(
            (
                x - 22,
                y - 22,
                x + tamano + 22,
                y + tamano + 22
            ),
            outline=color,
            width=5
        )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_corazon(
    draw,
    x,
    y,
    tamano=90
):
    color = (
        255,
        70,
        100
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano * 0.55,
            y + tamano * 0.55
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.45,
            y,
            x + tamano,
            y + tamano * 0.55
        ),
        fill=color
    )

    draw.polygon(
        [
            (
                x,
                y + tamano * 0.28
            ),
            (
                x + tamano,
                y + tamano * 0.28
            ),
            (
                x + tamano / 2,
                y + tamano
            )
        ],
        fill=color
    )


def _dibujar_mariposa(
    draw,
    x,
    y,
    tamano=90
):
    color = (
        190,
        100,
        255
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano * 0.48,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.52,
            y,
            x + tamano,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.42,
            y + tamano * 0.2,
            x + tamano * 0.58,
            y + tamano * 0.9
        ),
        fill=(35, 25, 50)
    )

    draw.arc(
        (
            x + tamano * 0.3,
            y - tamano * 0.2,
            x + tamano * 0.5,
            y + tamano * 0.25
        ),
        190,
        350,
        fill=color,
        width=4
    )

    draw.arc(
        (
            x + tamano * 0.5,
            y - tamano * 0.2,
            x + tamano * 0.7,
            y + tamano * 0.25
        ),
        190,
        350,
        fill=color,
        width=4
    )


def _dibujar_corona(
    draw,
    x,
    y,
    tamano=105
):
    # Corona pequeña y limpia.
    color = (
        255,
        205,
        55
    )

    borde = (
        120,
        80,
        15
    )

    puntos = [
        (x, y + tamano * 0.85),
        (x, y + tamano * 0.2),
        (
            x + tamano * 0.25,
            y + tamano * 0.48
        ),
        (
            x + tamano * 0.5,
            y
        ),
        (
            x + tamano * 0.75,
            y + tamano * 0.48
        ),
        (
            x + tamano,
            y + tamano * 0.2
        ),
        (
            x + tamano,
            y + tamano * 0.85
        ),
    ]

    draw.polygon(
        puntos,
        fill=color,
        outline=borde
    )

    draw.rectangle(
        (
            x,
            y + tamano * 0.72,
            x + tamano,
            y + tamano
        ),
        fill=color,
        outline=borde,
        width=3
    )

    # Joyas.
    for px in (
        0.25,
        0.5,
        0.75
    ):

        draw.ellipse(
            (
                x + tamano * px - 5,
                y + tamano * 0.76 - 5,
                x + tamano * px + 5,
                y + tamano * 0.76 + 5
            ),
            fill=(255, 245, 170)
        )


def _dibujar_estrellas(
    draw,
    x,
    y,
    tamano=100,
    frame=0
):
    posiciones = [
        (0, 0),
        (tamano * 0.7, -tamano * 0.3),
        (-tamano * 0.5, tamano * 0.45),
        (tamano * 0.45, tamano * 0.7),
    ]

    for i, (dx, dy) in enumerate(
        posiciones
    ):

        brillo = (
            8
            + int(
                math.sin(
                    frame * 0.4 + i
                ) * 5
            )
        )

        _dibujar_estrella(
            draw,
            x + dx,
            y + dy,
            brillo,
            (255, 235, 100)
        )


def _dibujar_accesorio(
    draw,
    accesorio,
    frame=0
):
    nombre = _producto_id(
        accesorio
    )

    if not nombre:
        return

    # ========================================================
    # CORONA
    # ========================================================

    if "corona" in nombre:

        _dibujar_corona(
            draw,
            X_CONTENIDO + 25,
            20,
            105
        )

    # ========================================================
    # CORAZÓN
    # ========================================================

    elif (
        "corazon" in nombre
        or "corazón" in nombre
        or "heart" in nombre
    ):

        _dibujar_corazon(
            draw,
            ANCHO - 180,
            90,
            90
        )

    # ========================================================
    # MARIPOSA
    # ========================================================

    elif (
        "mariposa" in nombre
        or "butterfly" in nombre
    ):

        _dibujar_mariposa(
            draw,
            ANCHO - 200,
            100,
            95
        )

    # ========================================================
    # ESTRELLAS
    # ========================================================

    elif (
        "estrella" in nombre
        or "estrellas" in nombre
        or "star" in nombre
    ):

        _dibujar_estrellas(
            draw,
            ANCHO - 170,
            110,
            100,
            frame
        )


def dibujar_efecto(
    draw,
    efecto,
    frame=0
):
    _dibujar_accesorio(
        draw,
        efecto,
        frame
    )


# ============================================================
# INSIGNIA / NIVEL
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=58
):
    color = (
        255,
        205,
        70
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=color,
        outline=(255, 240, 150),
        width=3
    )

    _dibujar_estrella(
        draw,
        x + tamano / 2,
        y + tamano / 2,
        tamano * 0.34,
        (70, 55, 15)
    )


# ============================================================
# EXPERIENCIA
# ============================================================

def dibujar_experiencia(
    draw,
    nivel,
    xp_actual,
    xp_siguiente,
    rango=None
):
    try:
        actual = float(
            xp_actual or 0
        )
    except Exception:
        actual = 0

    try:
        siguiente = float(
            xp_siguiente or 1
        )
    except Exception:
        siguiente = 1

    if siguiente <= 0:
        siguiente = 1

    porcentaje = (
        actual
        / siguiente
        * 100
    )

    porcentaje = max(
        0,
        min(
            100,
            porcentaje
        )
    )

    # ========================================================
    # NIVEL
    # ========================================================

    dibujar_icono_rango(
        draw,
        X_CONTENIDO,
        Y_NIVEL - 32,
        64
    )

    fuente_nivel = cargar_fuente(
        FONT_NIVEL,
        negrita=True
    )

    draw.text(
        (
            X_CONTENIDO + 82,
            Y_NIVEL
        ),
        f"NIVEL {nivel}",
        font=fuente_nivel,
        anchor="lm",
        fill=(255, 255, 255)
    )

    # ========================================================
    # XP
    # ========================================================

    fuente_xp = cargar_fuente(
        FONT_XP,
        negrita=True
    )

    draw.text(
        (
            X_CONTENIDO,
            Y_XP
        ),
        (
            f"XP {int(actual):,} / "
            f"{int(siguiente):,}"
        ),
        font=fuente_xp,
        anchor="lm",
        fill=(235, 240, 250)
    )

    # ========================================================
    # BARRA
    # ========================================================

    bar_x = X_CONTENIDO
    bar_y = Y_BARRA
    bar_w = 1120
    bar_h = 56

    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + bar_w,
            bar_y + bar_h
        ),
        radius=bar_h // 2,
        fill=(10, 14, 24),
        outline=(130, 140, 160),
        width=3
    )

    progreso_w = int(
        bar_w
        * porcentaje
        / 100
    )

    if progreso_w > 0:

        draw.rounded_rectangle(
            (
                bar_x,
                bar_y,
                bar_x + progreso_w,
                bar_y + bar_h
            ),
            radius=bar_h // 2,
            fill=(70, 190, 255)
        )

    # ========================================================
    # PORCENTAJE
    # ========================================================

    fuente_porcentaje = cargar_fuente(
        FONT_PORCENTAJE,
        negrita=True
    )

    draw.text(
        (
            bar_x + bar_w,
            Y_PORCENTAJE
        ),
        f"{porcentaje:.1f}%",
        font=fuente_porcentaje,
        anchor="ra",
        fill=(255, 255, 255)
    )

    # ========================================================
    # RANGO
    # ========================================================

    if rango:

        fuente_rango = cargar_fuente(
            FONT_RANGO,
            negrita=True
        )

        draw.text(
            (
                X_CONTENIDO,
                Y_RANGO
            ),
            str(rango),
            font=fuente_rango,
            anchor="lm",
            fill=(255, 210, 90)
        )


# ============================================================
# GENERADOR PRINCIPAL
# ============================================================

def generar_perfil(
    nombre,
    nivel=1,
    xp_actual=0,
    xp_siguiente=100,
    rango=None,
    pais=None,
    avatar=None,
    equipados=None,
    nombre_color="blanco",
    marco="normal",
    estilo_fondo="normal",
    id_interno=None,
    telegram_id=None,
    bot_id=None,
    propietario=False,
    tokens=None,
):
    # ========================================================
    # EQUIPADOS
    # ========================================================

    equipados_lista = normalizar_equipados(
        equipados
    )

    # ========================================================
    # DETECTAR COSMÉTICOS
    # ========================================================

    color_nombre_real = (
        detectar_color_nombre(
            equipados_lista
        )
    )

    marco_real = (
        detectar_marco(
            equipados_lista
        )
    )

    fondo_real = (
        detectar_fondo(
            equipados_lista
        )
    )

    # Si desde fuera se pasó un color explícito
    # y no hay cosmético, usarlo.
    if (
        color_nombre_real == "blanco"
        and nombre_color
        and nombre_color in COLORES_NOMBRE
    ):
        color_nombre_real = nombre_color

    # Si desde fuera se pasó un marco explícito
    # y no hay marco equipado, usarlo.
    if (
        marco_real == "normal"
        and marco
        and marco in COLORES_MARCO
    ):
        marco_real = marco

    # Si desde fuera se pasó un fondo explícito
    # y no hay fondo equipado, usarlo.
    if (
        fondo_real == "normal"
        and estilo_fondo
        and estilo_fondo in COLORES_FONDO
    ):
        fondo_real = estilo_fondo

    # ========================================================
    # IMAGEN
    # ========================================================

    imagen = Image.new(
        "RGB",
        (
            ANCHO,
            ALTO
        ),
        (20, 25, 40)
    )

    # AHORA SÍ:
    # el fondo equipado determina el fondo.
    dibujar_fondo(
        imagen,
        fondo_real
    )

    imagen = imagen.convert(
        "RGBA"
    )

    draw = ImageDraw.Draw(
        imagen
    )

    # ========================================================
    # AVATAR
    # ========================================================

    if avatar is None:

        avatar = crear_avatar_iniciales(
            nombre
        )

    avatar_x = 90
    avatar_y = 270

    color_marco = COLORES_MARCO.get(
        marco_real,
        COLORES_MARCO["normal"]
    )

    dibujar_avatar(
        imagen,
        avatar,
        avatar_x,
        avatar_y,
        TAM_AVATAR,
        color_marco
    )

    # Marco especial.
    dibujar_marco(
        draw,
        avatar_x,
        avatar_y,
        TAM_AVATAR,
        marco_real
    )

    # ========================================================
    # NOMBRE
    # ========================================================

    color_nombre = COLORES_NOMBRE.get(
        color_nombre_real,
        COLORES_NOMBRE["blanco"]
    )

    fuente_nombre = cargar_fuente(
        FONT_NOMBRE,
        negrita=True
    )

    # IMPORTANTE:
    # NO usamos .upper().
    # Se conserva exactamente como lo escribió.
    nombre_mostrado = texto_ajustado(
        draw,
        str(nombre),
        fuente_nombre,
        1280
    )

    draw.text(
        (
            X_CONTENIDO,
            Y_NOMBRE
        ),
        nombre_mostrado,
        font=fuente_nombre,
        anchor="lm",
        fill=color_nombre
    )

    # ========================================================
    # PAÍS
    # ========================================================

    codigo_pais = _pais_codigo(
        pais
    )

    nombre_pais = ""

    if codigo_pais:

        datos_pais = PAISES.get(
            codigo_pais,
            {}
        )

        nombre_pais = datos_pais.get(
            "nombre",
            codigo_pais
        )

    if nombre_pais:

        dibujar_bandera(
            draw,
            pais,
            X_CONTENIDO,
            Y_PAIS - FLAG_H // 2,
            FLAG_W,
            FLAG_H
        )

        fuente_pais = cargar_fuente(
            FONT_PAIS,
            negrita=True
        )

        draw.text(
            (
                X_CONTENIDO + 105,
                Y_PAIS
            ),
            nombre_pais,
            font=fuente_pais,
            anchor="lm",
            fill=(235, 240, 250)
        )

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    fuente_info = cargar_fuente(
        FONT_ID,
        negrita=True
    )

    if id_interno is not None:

        draw.text(
            (
                X_CONTENIDO,
                Y_ID
            ),
            f"ID INTERNO   #{id_interno}",
            font=fuente_info,
            anchor="lm",
            fill=(225, 230, 240)
        )

    if bot_id is not None:

        draw.text(
            (
                X_CONTENIDO,
                Y_BOT_ID
            ),
            f"ID DEL BOT   {bot_id}",
            font=fuente_info,
            anchor="lm",
            fill=(225, 230, 240)
        )

    # Telegram ID solamente propietario.
    if (
        propietario
        and telegram_id is not None
    ):

        draw.text(
            (
                X_CONTENIDO,
                Y_TELEGRAM_ID
            ),
            f"TELEGRAM ID   {telegram_id}",
            font=fuente_info,
            anchor="lm",
            fill=(255, 220, 120)
        )

    if tokens is not None:

        try:
            tokens_texto = (
                f"{int(tokens):,}"
            )
        except Exception:
            tokens_texto = str(tokens)

        draw.text(
            (
                X_CONTENIDO,
                Y_TOKENS
            ),
            f"TOKENS   {tokens_texto}",
            font=cargar_fuente(
                FONT_TOKENS,
                negrita=True
            ),
            anchor="lm",
            fill=(255, 215, 90)
        )

    # ========================================================
    # ACCESORIOS / EFECTOS
    # ========================================================

    for accesorio in equipados_lista:

        pid = _producto_id(
            accesorio
        )

        # No dibujar como accesorio los productos
        # que ya tienen su propia función.
        if (
            pid.startswith("nombre_")
            or pid.startswith("color_nombre_")
            or pid.startswith("color_")
            or pid.startswith("marco_")
            or pid.startswith("borde_")
            or pid.startswith("fondo_")
            or pid.startswith("background_")
            or pid.startswith("estilo_")
        ):
            continue

        _dibujar_accesorio(
            draw,
            accesorio,
            0
        )

    # ========================================================
    # EXPERIENCIA
    # ========================================================

    dibujar_experiencia(
        draw,
        nivel=nivel,
        xp_actual=xp_actual,
        xp_siguiente=xp_siguiente,
        rango=rango
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    salida = io.BytesIO()

    imagen.convert(
        "RGB"
    ).save(
        salida,
        format="PNG",
        optimize=True,
        compress_level=1
    )

    salida.seek(0)

    return (
        salida.getvalue(),
        "image/png",
        False
    )

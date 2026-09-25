import io
import math
import random

from PIL import Image, ImageDraw, ImageFont

from core.paises import PAISES


# ============================================================
# TAMAÑO
# ============================================================

ANCHO = 1920
ALTO = 1080


# ============================================================
# FUENTES DEL SISTEMA
# ============================================================

FUENTES_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

FUENTES_NEGRITA = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def cargar_fuente(tamano, negrita=False):
    rutas = (
        FUENTES_NEGRITA
        if negrita
        else FUENTES_NORMAL
    )

    for ruta in rutas:
        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except Exception:
            pass

    try:
        return ImageFont.load_default(
            size=max(16, int(tamano))
        )
    except Exception:
        return ImageFont.load_default()


# ============================================================
# TAMAÑOS
# ============================================================

FONT_NOMBRE = 128
FONT_PAIS = 58

FONT_ID = 46
FONT_TOKENS = 48

FONT_NIVEL = 72
FONT_XP = 66
FONT_PORCENTAJE = 54
FONT_RANGO = 60

TAM_AVATAR = 360

FLAG_W = 84
FLAG_H = 54

X_CONTENIDO = 540

Y_NOMBRE = 100
Y_PAIS = 225

Y_ID = 320
Y_BOT_ID = 380
Y_TELEGRAM_ID = 440
Y_TOKENS = 500

Y_NIVEL = 590
Y_XP = 670
Y_BARRA = 755
Y_PORCENTAJE = 835
Y_RANGO = 915


# ============================================================
# COLORES DEL NOMBRE
# ============================================================

COLORES_NOMBRE = {
    "blanco": (255, 255, 255),
    "dorado": (255, 210, 60),
    "amarillo": (255, 220, 60),
    "rojo": (255, 70, 70),
    "azul": (70, 160, 255),
    "verde": (70, 225, 110),
    "morado": (190, 90, 255),
    "violeta": (190, 90, 255),
    "rosa": (255, 100, 190),
    "cian": (70, 230, 255),
    "naranja": (255, 145, 55),
    "esmeralda": (40, 230, 145),
}


# ============================================================
# MARCOS
# ============================================================

COLORES_MARCO = {
    "normal": (100, 110, 130),
    "dorado": (255, 205, 55),
    "oro": (255, 205, 55),
    "plata": (205, 215, 230),
    "diamante": (90, 220, 255),
    "rojo": (255, 70, 70),
    "azul": (70, 160, 255),
    "verde": (70, 225, 110),
    "morado": (190, 90, 255),
    "rosa": (255, 100, 190),
    "cian": (70, 230, 255),
    "naranja": (255, 145, 55),
    "esmeralda": (40, 230, 145),
    "rubi": (225, 40, 55),
    "ametista": (170, 90, 255),
    "glacial": (130, 225, 255),
    "neon": (50, 255, 220),
    "cyber": (60, 220, 255),
    "dark": (25, 25, 35),
    "arcano": (170, 80, 255),
    "samurai": (190, 45, 45),
}


# ============================================================
# FONDOS
# ============================================================

COLORES_FONDO = {
    "normal": (
        (17, 22, 38),
        (48, 60, 90)
    ),

    "azul": (
        (7, 20, 48),
        (25, 85, 155)
    ),

    "rojo": (
        (45, 8, 18),
        (150, 30, 48)
    ),

    "verde": (
        (6, 35, 20),
        (25, 125, 70)
    ),

    "morado": (
        (25, 8, 48),
        (105, 30, 150)
    ),

    "rosa": (
        (45, 10, 35),
        (160, 40, 110)
    ),

    "cian": (
        (5, 30, 42),
        (20, 125, 155)
    ),

    "naranja": (
        (50, 20, 5),
        (170, 75, 20)
    ),

    "esmeralda": (
        (4, 32, 27),
        (15, 130, 95)
    ),

    "oro": (
        (40, 28, 5),
        (150, 100, 20)
    ),

    "negro": (
        (5, 5, 8),
        (28, 30, 38)
    ),
}


# ============================================================
# PRODUCTOS
# ============================================================

COLORES = (
    "blanco",
    "dorado",
    "amarillo",
    "rojo",
    "azul",
    "verde",
    "morado",
    "violeta",
    "rosa",
    "cian",
    "naranja",
    "esmeralda",
)

FONDOS = (
    "normal",
    "noche",
    "nebulosa",
    "cyber",
    "rosa",
    "floresta",
    "abismo",
    "azul",
    "rojo",
    "verde",
    "morado",
    "cian",
    "naranja",
    "esmeralda",
    "oro",
    "negro",
)

MARCOS = (
    "normal",
    "dorado",
    "oro",
    "plata",
    "diamante",
    "real",
    "glacial",
    "cosmico",
    "rosa_cristal",
    "corazones",
    "floral",
    "mariposas",
    "neon",
    "cyber",
    "samurai",
    "dark",
    "arcano",
    "esmeralda",
    "rubi",
    "ametista",
)


# ============================================================
# PRODUCTO ID
# ============================================================

def _producto_id(producto):
    if producto is None:
        return ""

    if isinstance(producto, dict):

        claves = (
            "id",
            "producto_id",
            "nombre",
            "item",
            "codigo",
            "slug",
            "tipo",
            "efecto",
            "color",
            "marco",
            "fondo",
        )

        valores = []

        for clave in claves:

            valor = producto.get(
                clave
            )

            if valor is not None:
                valores.append(
                    str(valor)
                )

        if valores:
            return " ".join(
                valores
            ).lower().strip()

    return str(
        producto
    ).lower().strip()


def normalizar_equipados(equipados):

    if equipados is None:
        return []

    if isinstance(
        equipados,
        dict
    ):

        resultado = []

        for clave, valor in equipados.items():

            if isinstance(
                valor,
                (list, tuple, set)
            ):

                resultado.extend(
                    valor
                )

            elif isinstance(
                valor,
                dict
            ):

                resultado.append(
                    valor
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

        return list(
            equipados
        )

    return [
        equipados
    ]


# ============================================================
# DETECTAR COLOR
# ============================================================

def detectar_color_nombre(
    equipados
):
    resultado = None

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        if (
            "color_" in texto
            or "nombre_" in texto
            or "nombre " in texto
            or "color " in texto
        ):

            if "dorado" in texto:
                resultado = "dorado"

            elif "rosa" in texto:
                resultado = "rosa"

            elif "cian" in texto:
                resultado = "cian"

            elif "rojo" in texto:
                resultado = "rojo"

            elif "violeta" in texto:
                resultado = "violeta"

            elif "esmeralda" in texto:
                resultado = "esmeralda"

            elif "azul" in texto:
                resultado = "azul"

            elif "verde" in texto:
                resultado = "verde"

            elif "morado" in texto:
                resultado = "morado"

            elif "naranja" in texto:
                resultado = "naranja"

            elif "amarillo" in texto:
                resultado = "amarillo"

    return resultado or "blanco"


# ============================================================
# DETECTAR MARCO
# ============================================================

def detectar_marco(
    equipados
):
    resultado = "normal"

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        if (
            "marco_" not in texto
            and "marco " not in texto
            and "frame" not in texto
            and "anim_" not in texto
        ):
            continue

        if "dorado" in texto:
            resultado = "dorado"

        elif "diamante" in texto:
            resultado = "diamante"

        elif "real" in texto:
            resultado = "real"

        elif "glacial" in texto:
            resultado = "glacial"

        elif "cosmico" in texto:
            resultado = "cosmico"

        elif "rosa_cristal" in texto:
            resultado = "rosa_cristal"

        elif "corazones" in texto:
            resultado = "corazones"

        elif "floral" in texto:
            resultado = "floral"

        elif "mariposas" in texto:
            resultado = "mariposas"

        elif "neon" in texto:
            resultado = "neon"

        elif "cyber" in texto:
            resultado = "cyber"

        elif "samurai" in texto:
            resultado = "samurai"

        elif "dark" in texto:
            resultado = "dark"

        elif "arcano" in texto:
            resultado = "arcano"

        elif "esmeralda" in texto:
            resultado = "esmeralda"

        elif "rubi" in texto:
            resultado = "rubi"

        elif "ametista" in texto:
            resultado = "ametista"

    return resultado


# ============================================================
# DETECTAR FONDO
# ============================================================

def detectar_fondo(
    equipados
):
    resultado = "normal"

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        if (
            "fondo_" not in texto
            and "fondo " not in texto
            and "background" not in texto
        ):
            continue

        if "noche" in texto:
            resultado = "noche"

        elif "nebulosa" in texto:
            resultado = "nebulosa"

        elif "cyber" in texto:
            resultado = "cyber"

        elif "rosa" in texto:
            resultado = "rosa"

        elif "floresta" in texto:
            resultado = "floresta"

        elif "abismo" in texto:
            resultado = "abismo"

    return resultado


# ============================================================
# TEXTO
# ============================================================

def texto_ajustado(
    draw,
    texto,
    fuente,
    max_ancho
):
    texto = str(
        texto
    )

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
# GRADIENTE
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


# ============================================================
# FONDO BASE
# ============================================================

def dibujar_fondo(
    imagen,
    estilo="normal",
    frame=0
):
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

    # Brillo.
    draw.ellipse(
        (
            1250,
            -300,
            2150,
            600
        ),
        fill=(
            255,
            255,
            255,
            13
        )
    )

    draw.ellipse(
        (
            -400,
            650,
            650,
            1500
        ),
        fill=(
            0,
            0,
            0,
            30
        )
    )

    # --------------------------------------------------------
    # FONDOS ESPECIALES
    # --------------------------------------------------------

    if estilo == "noche":

        random.seed(100)

        for _ in range(90):

            x = random.randint(
                0,
                ANCHO
            )

            y = random.randint(
                0,
                ALTO
            )

            r = random.choice(
                (2, 3, 4)
            )

            draw.ellipse(
                (
                    x - r,
                    y - r,
                    x + r,
                    y + r
                ),
                fill=(
                    255,
                    255,
                    255,
                    random.randint(
                        80,
                        220
                    )
                )
            )

    elif estilo == "nebulosa":

        draw.ellipse(
            (
                700,
                -100,
                1700,
                900
            ),
            fill=(
                170,
                60,
                255,
                35
            )
        )

        draw.ellipse(
            (
                1000,
                250,
                1900,
                1100
            ),
            fill=(
                40,
                140,
                255,
                28
            )
        )

    elif estilo == "cyber":

        for i in range(
            -ALTO,
            ANCHO,
            80
        ):

            draw.line(
                (
                    i,
                    ALTO,
                    i + ALTO,
                    0
                ),
                fill=(
                    0,
                    220,
                    255,
                    18
                ),
                width=3
            )

        for y in range(
            650,
            ALTO,
            60
        ):

            draw.line(
                (
                    0,
                    y,
                    ANCHO,
                    y
                ),
                fill=(
                    0,
                    220,
                    255,
                    14
                ),
                width=2
            )

    elif estilo == "floresta":

        random.seed(300)

        for _ in range(45):

            x = random.randint(
                0,
                ANCHO
            )

            y = random.randint(
                0,
                ALTO
            )

            r = random.randint(
                15,
                45
            )

            draw.ellipse(
                (
                    x - r,
                    y - r,
                    x + r,
                    y + r
                ),
                outline=(
                    100,
                    255,
                    150,
                    25
                ),
                width=3
            )

    elif estilo == "abismo":

        draw.ellipse(
            (
                850,
                100,
                1800,
                1050
            ),
            outline=(
                170,
                80,
                255,
                30
            ),
            width=40
        )

    # Líneas decorativas.
    for i in range(7):

        offset = i * 90

        draw.line(
            (
                850 + offset,
                1080,
                1350 + offset,
                0
            ),
            fill=(
                255,
                255,
                255,
                13
            ),
            width=4
        )

    draw.rounded_rectangle(
        (
            8,
            8,
            ANCHO - 8,
            ALTO - 8
        ),
        radius=25,
        outline=(
            130,
            145,
            175,
            80
        ),
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
        (
            35,
            40,
            55,
            255
        )
    )

    draw = ImageDraw.Draw(
        imagen
    )

    texto = str(
        nombre or "?"
    ).strip()

    partes = texto.split()

    if len(partes) >= 2:

        iniciales = (
            partes[0][0]
            + partes[1][0]
        ).upper()

    elif texto:

        iniciales = texto[:2].upper()

    else:

        iniciales = "?"

    fuente = cargar_fuente(
        130,
        True
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
            (tamano - alto) / 2 - 10
        ),
        iniciales,
        font=fuente,
        fill=(
            240,
            240,
            245,
            255
        )
    )

    return imagen


def recortar_circulo(
    imagen,
    tamano
):
    if imagen is None:
        return None

    imagen = imagen.convert(
        "RGBA"
    )

    imagen = imagen.resize(
        (
            tamano,
            tamano
        ),
        Image.Resampling.LANCZOS
    )

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
        (
            0,
            0,
            0,
            0
        )
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
    tamano
):
    avatar = recortar_circulo(
        avatar,
        tamano
    )

    if avatar is None:
        return

    imagen.alpha_composite(
        avatar,
        (
            x,
            y
        )
    )


# ============================================================
# BANDERA
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

        if (
            bandera
            and bandera in str(pais)
        ):
            return codigo

        if (
            nombre
            and nombre in valor
        ):
            return codigo

    return None


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

    # ========================================================
    # CUBA
    # ========================================================

    if codigo == "cuba":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            fill=(
                255,
                255,
                255
            )
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
                    fill=(
                        35,
                        90,
                        175
                    )
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
            fill=(
                215,
                40,
                50
            )
        )

        cx = (
            x
            + ancho * 0.17
        )

        cy = (
            y
            + alto / 2
        )

        radio = alto * 0.18

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
            fill=(
                255,
                255,
                255
            )
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            outline=(
                255,
                255,
                255
            ),
            width=3
        )

        return

    # ========================================================
    # RESTO DE PAÍSES
    # ========================================================

    datos = PAISES.get(
        codigo,
        {}
    )

    bandera = str(
        datos.get(
            "bandera",
            ""
        )
    )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto
        ),
        radius=7,
        fill=(
            40,
            45,
            60
        ),
        outline=(
            220,
            225,
            235
        ),
        width=2
    )

    if bandera:

        fuente = cargar_fuente(
            38
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
    color = COLORES_MARCO.get(
        tipo,
        COLORES_MARCO["normal"]
    )

    # Marco normal.
    if tipo == "normal":

        draw.ellipse(
            (
                x - 18,
                y - 18,
                x + tamano + 18,
                y + tamano + 18
            ),
            outline=color,
            width=10
        )

        return

    # ========================================================
    # DIAMANTE
    # ========================================================

    if tipo == "diamante":

        draw.ellipse(
            (
                x - 20,
                y - 20,
                x + tamano + 20,
                y + tamano + 20
            ),
            outline=color,
            width=16
        )

        draw.ellipse(
            (
                x - 8,
                y - 8,
                x + tamano + 8,
                y + tamano + 8
            ),
            outline=(210, 250, 255),
            width=4
        )

        return

    # ========================================================
    # GLACIAL
    # ========================================================

    if tipo == "glacial":

        for grosor in (
            24,
            12,
            4
        ):

            draw.ellipse(
                (
                    x - grosor,
                    y - grosor,
                    x + tamano + grosor,
                    y + tamano + grosor
                ),
                outline=(
                    100,
                    220,
                    255
                ),
                width=4
            )

        return

    # ========================================================
    # NEÓN
    # ========================================================

    if tipo == "neon":

        for grosor, alpha in (
            (35, 30),
            (25, 60),
            (15, 120),
            (8, 255)
        ):

            draw.ellipse(
                (
                    x - grosor,
                    y - grosor,
                    x + tamano + grosor,
                    y + tamano + grosor
                ),
                outline=(
                    50,
                    255,
                    220,
                    alpha
                ),
                width=5
            )

        return

    # ========================================================
    # CYBER
    # ========================================================

    if tipo == "cyber":

        draw.ellipse(
            (
                x - 25,
                y - 25,
                x + tamano + 25,
                y + tamano + 25
            ),
            outline=(
                40,
                220,
                255
            ),
            width=10
        )

        draw.arc(
            (
                x - 35,
                y - 35,
                x + tamano + 35,
                y + tamano + 35
            ),
            20,
            120,
            fill=(
                255,
                60,
                220
            ),
            width=8
        )

        draw.arc(
            (
                x - 35,
                y - 35,
                x + tamano + 35,
                y + tamano + 35
            ),
            200,
            300,
            fill=(
                60,
                255,
                240
            ),
            width=8
        )

        return

    # ========================================================
    # DARK
    # ========================================================

    if tipo == "dark":

        draw.ellipse(
            (
                x - 22,
                y - 22,
                x + tamano + 22,
                y + tamano + 22
            ),
            outline=(
                5,
                5,
                10
            ),
            width=22
        )

        draw.ellipse(
            (
                x - 10,
                y - 10,
                x + tamano + 10,
                y + tamano + 10
            ),
            outline=(
                100,
                100,
                115
            ),
            width=3
        )

        return

    # ========================================================
    # ARCANO
    # ========================================================

    if tipo == "arcano":

        draw.ellipse(
            (
                x - 24,
                y - 24,
                x + tamano + 24,
                y + tamano + 24
            ),
            outline=(
                170,
                80,
                255
            ),
            width=10
        )

        # Runas.
        for i in range(8):

            angulo = (
                math.pi * 2 * i / 8
            )

            cx = (
                x + tamano / 2
                + math.cos(angulo)
                * (tamano / 2 + 35)
            )

            cy = (
                y + tamano / 2
                + math.sin(angulo)
                * (tamano / 2 + 35)
            )

            draw.ellipse(
                (
                    cx - 7,
                    cy - 7,
                    cx + 7,
                    cy + 7
                ),
                fill=(
                    210,
                    130,
                    255
                )
            )

        return

    # ========================================================
    # SAMURAI
    # ========================================================

    if tipo == "samurai":

        draw.ellipse(
            (
                x - 20,
                y - 20,
                x + tamano + 20,
                y + tamano + 20
            ),
            outline=(
                185,
                35,
                40
            ),
            width=14
        )

        draw.arc(
            (
                x - 30,
                y - 30,
                x + tamano + 30,
                y + tamano + 30
            ),
            210,
            330,
            fill=(
                230,
                210,
                160
            ),
            width=6
        )

        return

    # ========================================================
    # CORAZONES
    # ========================================================

    if tipo == "corazones":

        dibujar_marco_corazones(
            draw,
            x,
            y,
            tamano
        )

        return

    # ========================================================
    # MARIPOSAS
    # ========================================================

    if tipo == "mariposas":

        dibujar_marco_mariposas(
            draw,
            x,
            y,
            tamano
        )

        return

    # ========================================================
    # FLORAL
    # ========================================================

    if tipo == "floral":

        dibujar_marco_floral(
            draw,
            x,
            y,
            tamano
        )

        return

    # ========================================================
    # ROSA CRISTAL
    # ========================================================

    if tipo == "rosa_cristal":

        draw.ellipse(
            (
                x - 22,
                y - 22,
                x + tamano + 22,
                y + tamano + 22
            ),
            outline=(
                255,
                120,
                210
            ),
            width=14
        )

        draw.ellipse(
            (
                x - 8,
                y - 8,
                x + tamano + 8,
                y + tamano + 8
            ),
            outline=(
                255,
                220,
                245
            ),
            width=4
        )

        return

    # ========================================================
    # MARCO REAL
    # ========================================================

    if tipo == "real":

        draw.ellipse(
            (
                x - 25,
                y - 25,
                x + tamano + 25,
                y + tamano + 25
            ),
            outline=(
                255,
                205,
                55
            ),
            width=16
        )

        # Pequeñas coronas alrededor.
        for angulo in (
            0,
            90,
            180,
            270
        ):

            rad = math.radians(
                angulo
            )

            cx = (
                x + tamano / 2
                + math.cos(rad)
                * (tamano / 2 + 35)
            )

            cy = (
                y + tamano / 2
                + math.sin(rad)
                * (tamano / 2 + 35)
            )

            dibujar_corona(
                draw,
                cx - 25,
                cy - 20,
                50
            )

        return

    # ========================================================
    # COSMICO
    # ========================================================

    if tipo == "cosmico":

        draw.ellipse(
            (
                x - 25,
                y - 25,
                x + tamano + 25,
                y + tamano + 25
            ),
            outline=(
                100,
                80,
                255
            ),
            width=12
        )

        for i in range(16):

            angulo = (
                2 * math.pi * i / 16
            )

            cx = (
                x + tamano / 2
                + math.cos(angulo)
                * (tamano / 2 + 30)
            )

            cy = (
                y + tamano / 2
                + math.sin(angulo)
                * (tamano / 2 + 30)
            )

            draw.ellipse(
                (
                    cx - 4,
                    cy - 4,
                    cx + 4,
                    cy + 4
                ),
                fill=(
                    220,
                    220,
                    255
                )
            )

        return

    # ========================================================
    # MARCO SIMPLE PARA LOS RESTANTES
    # ========================================================

    draw.ellipse(
        (
            x - 18,
            y - 18,
            x + tamano + 18,
            y + tamano + 18
        ),
        outline=color,
        width=14
    )


# ============================================================
# MARCO CORAZONES
# ============================================================

def dibujar_marco_corazones(
    draw,
    x,
    y,
    tamano
):
    for i in range(12):

        angulo = (
            2 * math.pi * i / 12
        )

        cx = (
            x + tamano / 2
            + math.cos(angulo)
            * (tamano / 2 + 28)
        )

        cy = (
            y + tamano / 2
            + math.sin(angulo)
            * (tamano / 2 + 28)
        )

        dibujar_corazon(
            draw,
            cx - 18,
            cy - 18,
            36
        )


# ============================================================
# MARCO MARIPOSAS
# ============================================================

def dibujar_marco_mariposas(
    draw,
    x,
    y,
    tamano
):
    for i in range(10):

        angulo = (
            2 * math.pi * i / 10
        )

        cx = (
            x + tamano / 2
            + math.cos(angulo)
            * (tamano / 2 + 35)
        )

        cy = (
            y + tamano / 2
            + math.sin(angulo)
            * (tamano / 2 + 35)
        )

        dibujar_mariposa(
            draw,
            cx - 22,
            cy - 22,
            44
        )


# ============================================================
# MARCO FLORAL
# ============================================================

def dibujar_marco_floral(
    draw,
    x,
    y,
    tamano
):
    draw.ellipse(
        (
            x - 14,
            y - 14,
            x + tamano + 14,
            y + tamano + 14
        ),
        outline=(
            100,
            220,
            120
        ),
        width=7
    )

    for i in range(12):

        angulo = (
            2 * math.pi * i / 12
        )

        cx = (
            x + tamano / 2
            + math.cos(angulo)
            * (tamano / 2 + 25)
        )

        cy = (
            y + tamano / 2
            + math.sin(angulo)
            * (tamano / 2 + 25)
        )

        r = 13

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r
            ),
            fill=(
                255,
                110,
                170
            )
        )


# ============================================================
# CORONA
# ============================================================

def dibujar_corona(
    draw,
    x,
    y,
    tamano=130
):
    oro = (
        255,
        205,
        45
    )

    luz = (
        255,
        240,
        130
    )

    puntos = [
        (
            x,
            y + tamano
        ),
        (
            x + tamano * 0.10,
            y + tamano * 0.15
        ),
        (
            x + tamano * 0.30,
            y + tamano * 0.55
        ),
        (
            x + tamano * 0.50,
            y
        ),
        (
            x + tamano * 0.70,
            y + tamano * 0.55
        ),
        (
            x + tamano * 0.90,
            y + tamano * 0.15
        ),
        (
            x + tamano,
            y + tamano
        ),
    ]

    draw.polygon(
        puntos,
        fill=oro,
        outline=luz
    )

    draw.rounded_rectangle(
        (
            x,
            y + tamano * 0.68,
            x + tamano,
            y + tamano
        ),
        radius=10,
        fill=oro,
        outline=luz,
        width=3
    )


# ============================================================
# CORAZÓN
# ============================================================

def dibujar_corazon(
    draw,
    x,
    y,
    tamano=100
):
    color = (
        255,
        65,
        100
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano * 0.52,
            y + tamano * 0.52
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.48,
            y,
            x + tamano,
            y + tamano * 0.52
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


# ============================================================
# MARIPOSA
# ============================================================

def dibujar_mariposa(
    draw,
    x,
    y,
    tamano=110
):
    color = (
        185,
        90,
        255
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano * 0.55,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.45,
            y,
            x + tamano,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.42,
            y + tamano * 0.25,
            x + tamano * 0.58,
            y + tamano * 0.92
        ),
        fill=(
            35,
            30,
            55
        )
    )


# ============================================================
# EFECTOS
# ============================================================

def dibujar_efecto(
    draw,
    efecto,
    frame=0
):
    texto = _producto_id(
        efecto
    )

    if not texto:
        return

    # ========================================================
    # FUEGO
    # ========================================================

    if (
        "fuego" in texto
        or "infernal" in texto
    ):

        for i in range(12):

            x = (
                30
                + i * 160
            )

            altura = (
                80
                + ((i * 37) % 90)
            )

            draw.polygon(
                [
                    (
                        x,
                        ALTO - 10
                    ),
                    (
                        x + 45,
                        ALTO - altura
                    ),
                    (
                        x + 90,
                        ALTO - 10
                    )
                ],
                fill=(
                    255,
                    80,
                    20,
                    150
                )
            )

    # ========================================================
    # ELECTRICIDAD / SOBRECARGA
    # ========================================================

    elif (
        "electricidad" in texto
        or "sobrecarga" in texto
    ):

        for i in range(10):

            x = (
                100
                + i * 190
            )

            draw.line(
                (
                    x,
                    20,
                    x + 25,
                    120,
                    x - 10,
                    220,
                    x + 25,
                    320
                ),
                fill=(
                    80,
                    220,
                    255
                ),
                width=5
            )

    # ========================================================
    # ESCARCHA / GLACIAL
    # ========================================================

    elif (
        "escarcha" in texto
        or "glacial" in texto
    ):

        for i in range(20):

            x = (
                30
                + i * 95
            )

            y = (
                (i * 73)
                % ALTO
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 12,
                    y + 12
                ),
                fill=(
                    190,
                    240,
                    255
                )
            )

    # ========================================================
    # CHISPAS
    # ========================================================

    elif "chispas" in texto:

        for i in range(20):

            x = (
                40
                + (i * 157)
                % (ANCHO - 80)
            )

            y = (
                60
                + (i * 83)
                % (ALTO - 120)
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 10,
                    y + 10
                ),
                fill=(
                    255,
                    210,
                    60
                )
            )

    # ========================================================
    # COSMICO / NEBULOSA
    # ========================================================

    elif (
        "cosmico" in texto
        or "nebulosa" in texto
    ):

        for i in range(30):

            x = (
                20
                + (i * 127)
                % (ANCHO - 40)
            )

            y = (
                20
                + (i * 71)
                % (ALTO - 40)
            )

            r = (
                3
                + i % 4
            )

            draw.ellipse(
                (
                    x - r,
                    y - r,
                    x + r,
                    y + r
                ),
                fill=(
                    210,
                    190,
                    255
                )
            )

    # ========================================================
    # AURA
    # ========================================================

    elif "aura" in texto:

        for i in range(6):

            margen = (
                20
                + i * 25
            )

            draw.rounded_rectangle(
                (
                    margen,
                    margen,
                    ANCHO - margen,
                    ALTO - margen
                ),
                radius=35,
                outline=(
                    110,
                    50,
                    220,
                    max(
                        10,
                        80 - i * 10
                    )
                ),
                width=5
            )

    # ========================================================
    # CORAZONES
    # ========================================================

    elif (
        "corazones" in texto
        or "corazon" in texto
        or "corazón" in texto
    ):

        for i in range(14):

            x = (
                40
                + (i * 139)
                % (ANCHO - 80)
            )

            y = (
                40
                + (i * 91)
                % (ALTO - 80)
            )

            dibujar_corazon(
                draw,
                x,
                y,
                35
            )

    # ========================================================
    # PÉTALOS
    # ========================================================

    elif (
        "petalo" in texto
        or "pétalo" in texto
    ):

        for i in range(25):

            x = (
                30
                + (i * 151)
                % (ANCHO - 60)
            )

            y = (
                30
                + (i * 83)
                % (ALTO - 60)
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 18,
                    y + 30
                ),
                fill=(
                    255,
                    130,
                    180
                )
            )

    # ========================================================
    # MARIPOSAS
    # ========================================================

    elif "mariposa" in texto:

        for i in range(8):

            x = (
                40
                + (i * 230)
                % (ANCHO - 100)
            )

            y = (
                50
                + (i * 137)
                % (ALTO - 120)
            )

            dibujar_mariposa(
                draw,
                x,
                y,
                55
            )

    # ========================================================
    # BURBUJAS
    # ========================================================

    elif "burbujas" in texto:

        for i in range(20):

            x = (
                30
                + (i * 113)
                % (ANCHO - 60)
            )

            y = (
                50
                + (i * 67)
                % (ALTO - 100)
            )

            r = (
                6
                + i % 8
            )

            draw.ellipse(
                (
                    x - r,
                    y - r,
                    x + r,
                    y + r
                ),
                outline=(
                    170,
                    230,
                    255
                ),
                width=3
            )

    # ========================================================
    # ESTRELLAS
    # ========================================================

    elif "estrellas" in texto:

        for i in range(25):

            x = (
                30
                + (i * 97)
                % (ANCHO - 60)
            )

            y = (
                30
                + (i * 137)
                % (ALTO - 60)
            )

            dibujar_estrella(
                draw,
                x,
                y,
                12
            )

    # ========================================================
    # ARCOIRIS
    # ========================================================

    elif "arcoiris" in texto:

        colores = (
            (255, 70, 70),
            (255, 170, 50),
            (255, 240, 70),
            (80, 230, 100),
            (70, 180, 255),
            (150, 90, 255),
        )

        for i, color in enumerate(
            colores
        ):

            draw.arc(
                (
                    600 - i * 20,
                    120 - i * 20,
                    1500 + i * 20,
                    1020 + i * 20
                ),
                200,
                340,
                fill=color,
                width=12
            )


# ============================================================
# ESTRELLA
# ============================================================

def dibujar_estrella(
    draw,
    cx,
    cy,
    radio
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
        fill=(
            255,
            230,
            80
        )
    )


# ============================================================
# INSIGNIAS
# ============================================================

def dibujar_insignia(
    draw,
    producto
):
    texto = _producto_id(
        producto
    )

    if "insignia" not in texto:
        return

    # Las insignias se colocan arriba a la derecha.
    x = ANCHO - 210
    y = 60
    tamano = 110

    # Base.
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(
            25,
            30,
            45
        ),
        outline=(
            255,
            255,
            255
        ),
        width=5
    )

    # CORONA
    if "corona" in texto:

        dibujar_corona(
            draw,
            x + 18,
            y + 22,
            74
        )

    # RAYO
    elif (
        "rayo" in texto
        or "rayo" in texto
    ):

        puntos = [
            (
                x + 60,
                y + 10
            ),
            (
                x + 30,
                y + 60
            ),
            (
                x + 55,
                y + 60
            ),
            (
                x + 40,
                y + 105
            ),
            (
                x + 85,
                y + 50
            ),
            (
                x + 60,
                y + 50
            )
        ]

        draw.polygon(
            puntos,
            fill=(
                255,
                225,
                60
            )
        )

    # CORAZÓN
    elif "corazon" in texto or "corazón" in texto:

        dibujar_corazon(
            draw,
            x + 20,
            y + 20,
            70
        )

    # ESTELAR
    elif "estelar" in texto:

        dibujar_estrella(
            draw,
            x + 55,
            y + 55,
            40
        )

    # ARCANA
    elif "arcana" in texto:

        draw.ellipse(
            (
                x + 20,
                y + 20,
                x + 90,
                y + 90
            ),
            outline=(
                190,
                100,
                255
            ),
            width=7
        )

        draw.line(
            (
                x + 30,
                y + 80,
                x + 80,
                y + 30
            ),
            fill=(
                230,
                180,
                255
            ),
            width=7
        )


# ============================================================
# INSIGNIA DE NIVEL
# ============================================================

def dibujar_insignia_rango(
    draw,
    x,
    y,
    tamano=64
):
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(
            255,
            205,
            55
        ),
        outline=(
            255,
            240,
            150
        ),
        width=3
    )

    dibujar_estrella(
        draw,
        x + tamano / 2,
        y + tamano / 2,
        tamano * 0.34
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

    # NIVEL
    dibujar_insignia_rango(
        draw,
        X_CONTENIDO,
        Y_NIVEL - 32,
        64
    )

    fuente_nivel = cargar_fuente(
        FONT_NIVEL,
        True
    )

    draw.text(
        (
            X_CONTENIDO + 84,
            Y_NIVEL
        ),
        f"NIVEL {nivel}",
        font=fuente_nivel,
        anchor="lm",
        fill=(
            255,
            255,
            255
        )
    )

    # XP
    fuente_xp = cargar_fuente(
        FONT_XP,
        True
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
        fill=(
            235,
            240,
            250
        )
    )

    # BARRA
    BAR_X = X_CONTENIDO
    BAR_Y = Y_BARRA
    BAR_W = 1120
    BAR_H = 58

    draw.rounded_rectangle(
        (
            BAR_X,
            BAR_Y,
            BAR_X + BAR_W,
            BAR_Y + BAR_H
        ),
        radius=BAR_H // 2,
        fill=(
            10,
            14,
            23
        ),
        outline=(
            145,
            155,
            175
        ),
        width=4
    )

    progreso = int(
        BAR_W
        * porcentaje
        / 100
    )

    if progreso > 0:

        draw.rounded_rectangle(
            (
                BAR_X,
                BAR_Y,
                BAR_X + progreso,
                BAR_Y + BAR_H
            ),
            radius=BAR_H // 2,
            fill=(
                70,
                190,
                255
            )
        )

    # PORCENTAJE
    fuente_porcentaje = cargar_fuente(
        FONT_PORCENTAJE,
        True
    )

    draw.text(
        (
            BAR_X + BAR_W,
            Y_PORCENTAJE
        ),
        f"{porcentaje:.1f}%",
        font=fuente_porcentaje,
        anchor="ra",
        fill=(
            255,
            255,
            255
        )
    )

    # RANGO
    if rango:

        fuente_rango = cargar_fuente(
            FONT_RANGO,
            True
        )

        draw.text(
            (
                X_CONTENIDO + 82,
                Y_RANGO
            ),
            str(rango),
            font=fuente_rango,
            anchor="lm",
            fill=(
                255,
                215,
                90
            )
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
    # COSMÉTICOS
    # ========================================================

    color_detectado = detectar_color_nombre(
        equipados_lista
    )

    marco_detectado = detectar_marco(
        equipados_lista
    )

    fondo_detectado = detectar_fondo(
        equipados_lista
    )

    color_nombre_real = (
        color_detectado
        if color_detectado != "blanco"
        else nombre_color
    )

    marco_real = (
        marco_detectado
        if marco_detectado != "normal"
        else marco
    )

    fondo_real = (
        fondo_detectado
        if fondo_detectado != "normal"
        else estilo_fondo
    )

    # ========================================================
    # IMAGEN
    # ========================================================

    imagen = Image.new(
        "RGB",
        (
            ANCHO,
            ALTO
        ),
        (
            20,
            25,
            40
        )
    )

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

    avatar_x = 85
    avatar_y = 350

    # ========================================================
    # MARCO
    # ========================================================

    dibujar_marco(
        draw,
        avatar_x,
        avatar_y,
        TAM_AVATAR,
        marco_real
    )

    # ========================================================
    # AVATAR
    # ========================================================

    dibujar_avatar(
        imagen,
        avatar,
        avatar_x,
        avatar_y,
        TAM_AVATAR
    )

    # ========================================================
    # NOMBRE
    # ========================================================

    color = COLORES_NOMBRE.get(
        color_nombre_real,
        COLORES_NOMBRE["blanco"]
    )

    fuente_nombre = cargar_fuente(
        FONT_NOMBRE,
        True
    )

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
        fill=color
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
            True
        )

        draw.text(
            (
                X_CONTENIDO + 105,
                Y_PAIS
            ),
            nombre_pais,
            font=fuente_pais,
            anchor="lm",
            fill=(
                235,
                240,
                250
            )
        )

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    fuente_id = cargar_fuente(
        FONT_ID,
        True
    )

    if id_interno is not None:

        draw.text(
            (
                X_CONTENIDO,
                Y_ID
            ),
            f"ID INTERNO   #{id_interno}",
            font=fuente_id,
            anchor="lm",
            fill=(
                225,
                230,
                240
            )
        )

    if bot_id is not None:

        draw.text(
            (
                X_CONTENIDO,
                Y_BOT_ID
            ),
            f"ID DEL BOT   {bot_id}",
            font=fuente_id,
            anchor="lm",
            fill=(
                225,
                230,
                240
            )
        )

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
            font=fuente_id,
            anchor="lm",
            fill=(
                255,
                220,
                110
            )
        )

    # ========================================================
    # TOKENS
    # ========================================================

    if tokens is not None:

        try:
            tokens_texto = (
                f"{int(tokens):,}"
            )
        except Exception:
            tokens_texto = str(
                tokens
            )

        draw.text(
            (
                X_CONTENIDO,
                Y_TOKENS
            ),
            f"TOKENS   {tokens_texto}",
            font=cargar_fuente(
                FONT_TOKENS,
                True
            ),
            anchor="lm",
            fill=(
                255,
                215,
                70
            )
        )

    # ========================================================
    # COSMÉTICOS VISUALES
    # ========================================================

    for accesorio in equipados_lista:

        texto = _producto_id(
            accesorio
        )

        if not texto:
            continue

        # ----------------------------------------------------
        # COLORES
        # ----------------------------------------------------

        if (
            "color_" in texto
            or "nombre_" in texto
            or "nombre " in texto
        ):
            continue

        # ----------------------------------------------------
        # MARCOS
        # ----------------------------------------------------

        if (
            "marco_" in texto
            or "marco " in texto
            or "frame" in texto
            or "anim_" in texto
        ):
            continue

        # ----------------------------------------------------
        # FONDOS
        # ----------------------------------------------------

        if (
            "fondo_" in texto
            or "fondo " in texto
            or "background" in texto
        ):
            continue

        # ----------------------------------------------------
        # INSIGNIAS
        # ----------------------------------------------------

        if "insignia" in texto:

            dibujar_insignia(
                draw,
                accesorio
            )

            continue

        # ----------------------------------------------------
        # EFECTOS
        # ----------------------------------------------------

        if (
            "efecto_" in texto
            or "efecto " in texto
            or "fuego" in texto
            or "electricidad" in texto
            or "escarcha" in texto
            or "chispas" in texto
            or "cosmico" in texto
            or "aura" in texto
            or "corazones" in texto
            or "petalo" in texto
            or "mariposas" in texto
            or "burbujas" in texto
            or "estrellas" in texto
            or "arcoiris" in texto
        ):

            dibujar_efecto(
                draw,
                accesorio,
                0
            )

            continue

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

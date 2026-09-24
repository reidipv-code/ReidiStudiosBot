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

TAM_AVATAR = 360

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
# TAMAÑOS DE TEXTO
# ============================================================

FONT_NOMBRE = 112
FONT_PAIS = 48

FONT_ID = 36
FONT_TOKENS = 42

FONT_NIVEL = 58
FONT_XP = 50
FONT_PORCENTAJE = 42
FONT_RANGO = 46

FONT_EMOJI = 48


# ============================================================
# POSICIONES
# ============================================================

# Avatar
AVATAR_X = 90
AVATAR_Y = 335

# Contenido
X_CONTENIDO = 540

Y_NOMBRE = 105
Y_PAIS = 205

Y_ID = 290
Y_BOT_ID = 340
Y_TELEGRAM_ID = 390
Y_TOKENS = 440

# Experiencia agrupada
Y_NIVEL = 535
Y_XP = 610
Y_BARRA = 680
Y_PORCENTAJE = 755
Y_RANGO = 820

# Decoración inferior
Y_LINEA = 895


# ============================================================
# BANDERA
# ============================================================

FLAG_W = 72
FLAG_H = 46


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
# ALIAS
# ============================================================

ALIASES_PRODUCTOS = {

    # --------------------------------------------------------
    # COLORES DE NOMBRE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # MARCOS
    # --------------------------------------------------------

    "marco_normal": "normal",
    "marco_oro": "oro",
    "marco_plata": "plata",
    "marco_diamante": "diamante",
    "marco_rojo": "rojo",
    "marco_morado": "morado",
    "marco_esmeralda": "esmeralda",
    "marco_azul": "azul",
    "marco_verde": "verde",

    # --------------------------------------------------------
    # FONDOS
    # --------------------------------------------------------

    "fondo_normal": "normal",
    "fondo_azul": "azul",
    "fondo_morado": "morado",
    "fondo_rojo": "rojo",
    "fondo_verde": "verde",
    "fondo_esmeralda": "esmeralda",
    "fondo_negro": "negro",
    "fondo_dorado": "dorado",

    # --------------------------------------------------------
    # EFECTOS
    # --------------------------------------------------------

    "efecto_corona": "corona",
    "efecto_corazon": "corazon",
    "efecto_corazón": "corazon",
    "efecto_mariposa": "mariposa",
    "efecto_estrellas": "estrellas",
    "efecto_estrellas_doradas": "estrellas",
    "efecto_brillo": "brillo",
    "efecto_fuego": "fuego",
    "efecto_hielo": "hielo",
    "efecto_rayos": "rayos",
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
            "slug",
            "codigo",
            "item",
            "tipo",
            "nombre",
        ):
            valor = producto.get(clave)

            if valor is not None:
                return _normalizar_texto(valor)

        return ""

    return _normalizar_texto(producto)


def normalizar_equipados(equipados):

    if equipados is None:
        return []

    resultado = []

    # ========================================================
    # DICCIONARIO
    # ========================================================

    if isinstance(equipados, dict):

        for clave, valor in equipados.items():

            clave_norm = _normalizar_texto(
                clave
            )

            # Si el valor es una lista.
            if isinstance(
                valor,
                (list, tuple, set)
            ):

                for elemento in valor:

                    elemento_norm = _producto_id(
                        elemento
                    )

                    if not elemento_norm:
                        continue

                    # Si la categoría es conocida,
                    # conservamos categoría + producto.
                    if clave_norm in (
                        "nombre",
                        "color_nombre",
                        "color",
                    ):

                        resultado.append(
                            f"nombre_{elemento_norm}"
                        )

                    elif clave_norm in (
                        "marco",
                        "borde",
                    ):

                        resultado.append(
                            f"marco_{elemento_norm}"
                        )

                    elif clave_norm in (
                        "fondo",
                        "background",
                        "estilo",
                    ):

                        resultado.append(
                            f"fondo_{elemento_norm}"
                        )

                    elif clave_norm in (
                        "efecto",
                        "efectos",
                        "accesorio",
                        "accesorios",
                    ):

                        resultado.append(
                            f"efecto_{elemento_norm}"
                        )

                    else:
                        resultado.append(
                            elemento_norm
                        )

                continue

            # ------------------------------------------------
            # Valor simple
            # ------------------------------------------------

            if valor is not None:

                valor_norm = _producto_id(
                    valor
                )

                if valor_norm:

                    if clave_norm in (
                        "nombre",
                        "color_nombre",
                        "color",
                    ):

                        resultado.append(
                            f"nombre_{valor_norm}"
                        )

                    elif clave_norm in (
                        "marco",
                        "borde",
                    ):

                        resultado.append(
                            f"marco_{valor_norm}"
                        )

                    elif clave_norm in (
                        "fondo",
                        "background",
                        "estilo",
                    ):

                        resultado.append(
                            f"fondo_{valor_norm}"
                        )

                    elif clave_norm in (
                        "efecto",
                        "efectos",
                        "accesorio",
                        "accesorios",
                    ):

                        resultado.append(
                            f"efecto_{valor_norm}"
                        )

                    else:

                        # Si ya viene como
                        # nombre_esmeralda,
                        # marco_oro, etc.
                        resultado.append(
                            valor_norm
                        )

                continue

            # ------------------------------------------------
            # Valor vacío
            # ------------------------------------------------

            if clave_norm:
                resultado.append(
                    clave_norm
                )

        return resultado

    # ========================================================
    # LISTA / TUPLA / SET
    # ========================================================

    if isinstance(
        equipados,
        (list, tuple, set)
    ):

        for elemento in equipados:

            if isinstance(
                elemento,
                dict
            ):

                # Puede venir:
                # {"tipo": "marco", "nombre": "oro"}

                tipo = _normalizar_texto(
                    elemento.get(
                        "tipo",
                        elemento.get(
                            "categoria",
                            ""
                        )
                    )
                )

                nombre = _producto_id(
                    elemento.get(
                        "id",
                        elemento.get(
                            "nombre",
                            elemento.get(
                                "item",
                                ""
                            )
                        )
                    )
                )

                if nombre:

                    if tipo in (
                        "nombre",
                        "color",
                        "color_nombre",
                    ):

                        resultado.append(
                            f"nombre_{nombre}"
                        )

                    elif tipo in (
                        "marco",
                        "borde",
                    ):

                        resultado.append(
                            f"marco_{nombre}"
                        )

                    elif tipo in (
                        "fondo",
                        "background",
                    ):

                        resultado.append(
                            f"fondo_{nombre}"
                        )

                    elif tipo in (
                        "efecto",
                        "accesorio",
                    ):

                        resultado.append(
                            f"efecto_{nombre}"
                        )

                    else:

                        resultado.append(
                            nombre
                        )

            else:

                pid = _producto_id(
                    elemento
                )

                if pid:
                    resultado.append(
                        pid
                    )

        return resultado

    # ========================================================
    # UN SOLO ELEMENTO
    # ========================================================

    pid = _producto_id(
        equipados
    )

    if pid:
        return [pid]

    return []


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

            return ALIASES_PRODUCTOS[
                pid
            ]

        # Prefijos.
        for prefijo in prefijos:

            if pid.startswith(
                prefijo
            ):

                valor = pid[
                    len(prefijo):
                ].strip("_")

                if valor:
                    return valor

        # Palabras.
        for palabra in palabras:

            if palabra in pid:
                return palabra

    return None


def detectar_color_nombre(
    equipados
):

    resultado = _buscar_cosmetico(
        equipados,
        (
            "nombre_",
            "color_nombre_",
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
            "blanco",
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


def detectar_efectos(
    equipados
):

    efectos = []

    for producto in equipados:

        pid = _producto_id(
            producto
        )

        if not pid:
            continue

        if pid in ALIASES_PRODUCTOS:

            efecto = ALIASES_PRODUCTOS[
                pid
            ]

            if efecto in (
                "corona",
                "corazon",
                "mariposa",
                "estrellas",
                "brillo",
                "fuego",
                "hielo",
                "rayos",
            ):

                efectos.append(
                    efecto
                )

            continue

        for palabra in (
            "corona",
            "corazon",
            "corazón",
            "mariposa",
            "estrellas",
            "brillo",
            "fuego",
            "hielo",
            "rayos",
        ):

            if palabra in pid:

                if palabra == "corazón":
                    palabra = "corazon"

                if palabra not in efectos:
                    efectos.append(
                        palabra
                    )

    return efectos


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

        if not os.path.exists(
            ruta
        ):
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

        if not os.path.exists(
            ruta
        ):
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

        prueba = (
            texto
            + "..."
        )

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

    for y in range(
        ALTO
    ):

        factor = (
            y
            / max(
                1,
                ALTO - 1
            )
        )

        r = int(
            color1[0]
            * (1 - factor)
            + color2[0]
            * factor
        )

        g = int(
            color1[1]
            * (1 - factor)
            + color2[1]
            * factor
        )

        b = int(
            color1[2]
            * (1 - factor)
            + color2[2]
            * factor
        )

        for x in range(
            ANCHO
        ):

            pixeles[
                x,
                y
            ] = (
                r,
                g,
                b
            )

    return imagen


# ============================================================
# FONDO
# ============================================================

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
        (
            0,
            0,
            0,
            0
        )
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # ========================================================
    # LUCES
    # ========================================================

    draw.ellipse(
        (
            1250,
            -350,
            2200,
            600
        ),
        fill=(
            255,
            255,
            255,
            15
        )
    )

    draw.ellipse(
        (
            -450,
            650,
            700,
            1650
        ),
        fill=(
            0,
            0,
            0,
            35
        )
    )

    # ========================================================
    # LÍNEAS DECORATIVAS
    # ========================================================

    for i in range(
        13
    ):

        desplazamiento = (
            i * 115
            + frame * 2
        )

        draw.line(
            (
                950 + desplazamiento,
                0,
                450 + desplazamiento,
                ALTO
            ),
            fill=(
                255,
                255,
                255,
                7
            ),
            width=4
        )

    # ========================================================
    # MARCO EXTERIOR
    # ========================================================

    draw.rounded_rectangle(
        (
            20,
            20,
            ANCHO - 20,
            ALTO - 20
        ),
        radius=30,
        outline=(
            255,
            255,
            255,
            35
        ),
        width=3
    )

    fondo = Image.alpha_composite(
        fondo.convert(
            "RGBA"
        ),
        overlay
    )

    imagen.paste(
        fondo.convert(
            "RGB"
        ),
        (
            0,
            0
        )
    )


# ============================================================
# EFECTOS DE FONDO
# ============================================================

def dibujar_efecto_fondo(
    draw,
    efecto,
    frame=0
):

    if efecto == "brillo":

        for i in range(
            8
        ):

            x = (
                1200
                + i * 90
                + frame * 3
            )

            y = (
                120
                + (i % 3) * 250
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 16,
                    y + 16
                ),
                fill=(
                    255,
                    255,
                    255,
                    150
                )
            )

    elif efecto == "estrellas":

        posiciones = [
            (1100, 120),
            (1500, 200),
            (1750, 400),
            (1250, 500),
            (1600, 700),
            (1050, 780),
        ]

        for i, (
            x,
            y
        ) in enumerate(
            posiciones
        ):

            radio = (
                9
                if i % 2 == 0
                else 6
            )

            _dibujar_estrella(
                draw,
                x,
                y,
                radio,
                (
                    255,
                    240,
                    120
                )
            )

    elif efecto == "fuego":

        for i in range(
            9
        ):

            x = (
                1150
                + i * 85
            )

            y = (
                930
                - (i % 3) * 35
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 45,
                    y + 70
                ),
                fill=(
                    255,
                    120,
                    35,
                    80
                )
            )

    elif efecto == "hielo":

        for i in range(
            8
        ):

            x = (
                1100
                + i * 100
            )

            y = (
                130
                + (i % 4) * 180
            )

            draw.line(
                (
                    x - 15,
                    y,
                    x + 15,
                    y
                ),
                fill=(
                    120,
                    230,
                    255,
                    120
                ),
                width=4
            )

            draw.line(
                (
                    x,
                    y - 15,
                    x,
                    y + 15
                ),
                fill=(
                    120,
                    230,
                    255,
                    120
                ),
                width=4
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

    return (
        avatar
        .convert("RGBA")
        .resize(
            (
                tamano,
                tamano
            ),
            Image.Resampling.LANCZOS
        )
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

    partes = str(
        nombre or "?"
    ).strip().split()

    if len(partes) >= 2:

        iniciales = (
            partes[0][0]
            + partes[1][0]
        ).upper()

    elif partes:

        iniciales = (
            partes[0][:2]
            .upper()
        )

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

    ancho = (
        bbox[2]
        - bbox[0]
    )

    alto = (
        bbox[3]
        - bbox[1]
    )

    draw.text(
        (
            (tamano - ancho) / 2,
            (tamano - alto) / 2 - 8
        ),
        iniciales,
        font=fuente,
        fill=(
            245,
            245,
            250,
            255
        )
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
        (
            0,
            0,
            0,
            0
        )
    )

    resultado.paste(
        imagen,
        (
            0,
            0
        ),
        mascara
    )

    return resultado


def dibujar_avatar(
    imagen,
    avatar,
    x,
    y,
    tamano,
    color_marco
):

    avatar = recortar_circulo(
        avatar,
        tamano
    )

    if avatar is None:
        return

    overlay = Image.new(
        "RGBA",
        imagen.size,
        (
            0,
            0,
            0,
            0
        )
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # Resplandor.
    draw.ellipse(
        (
            x - 28,
            y - 28,
            x + tamano + 28,
            y + tamano + 28
        ),
        outline=(
            *color_marco,
            65
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
# PAÍS
# ============================================================

def _pais_codigo(
    pais
):

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


def _dibujar_estrella(
    draw,
    cx,
    cy,
    radio,
    color
):

    puntos = []

    for i in range(
        10
    ):

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
                cx
                + math.cos(angulo)
                * r,

                cy
                + math.sin(angulo)
                * r
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

        h = (
            alto / 5
        )

        for i in range(
            5
        ):

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
                        85,
                        170
                    )
                )

        draw.polygon(
            [
                (
                    x,
                    y
                ),
                (
                    x
                    + ancho * 0.48,
                    y
                    + alto / 2
                ),
                (
                    x,
                    y + alto
                )
            ],
            fill=(
                210,
                35,
                45
            )
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto / 2,
            alto * 0.18,
            (
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
            width=2
        )

        return

    # ========================================================
    # OTROS PAÍSES
    # ========================================================

    datos = PAISES.get(
        codigo,
        {}
    )

    bandera = datos.get(
        "bandera",
        ""
    )

    if not bandera:
        return

    fuente = cargar_fuente_emoji(
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

    tipo = _normalizar_texto(
        tipo
    )

    color = COLORES_MARCO.get(
        tipo,
        COLORES_MARCO["normal"]
    )

    # ========================================================
    # SOMBRA
    # ========================================================

    draw.ellipse(
        (
            x - 25,
            y - 25,
            x + tamano + 25,
            y + tamano + 25
        ),
        outline=(
            0,
            0,
            0,
            120
        ),
        width=28
    )

    # ========================================================
    # MARCO NORMAL
    # ========================================================

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

    # ========================================================
    # ORO
    # ========================================================

    if tipo == "oro":

        draw.arc(
            (
                x - 25,
                y - 25,
                x + tamano + 25,
                y + tamano + 25
            ),
            200,
            340,
            fill=(
                255,
                240,
                120
            ),
            width=9
        )

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
                x
                + tamano / 2
                + math.cos(rad)
                * (
                    tamano / 2
                    + 30
                )
            )

            cy = (
                y
                + tamano / 2
                + math.sin(rad)
                * (
                    tamano / 2
                    + 30
                )
            )

            _dibujar_estrella(
                draw,
                cx,
                cy,
                9,
                (
                    255,
                    235,
                    100
                )
            )

    # ========================================================
    # PLATA
    # ========================================================

    elif tipo == "plata":

        draw.ellipse(
            (
                x - 25,
                y - 25,
                x + tamano + 25,
                y + tamano + 25
            ),
            outline=(
                240,
                245,
                255
            ),
            width=5
        )

    # ========================================================
    # DIAMANTE
    # ========================================================

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
                x
                + tamano / 2
                + math.cos(rad)
                * (
                    tamano / 2
                    + 32
                )
            )

            cy = (
                y
                + tamano / 2
                + math.sin(rad)
                * (
                    tamano / 2
                    + 32
                )
            )

            _dibujar_estrella(
                draw,
                cx,
                cy,
                10,
                (
                    150,
                    245,
                    255
                )
            )

    # ========================================================
    # ESMERALDA
    # ========================================================

    elif tipo == "esmeralda":

        draw.ellipse(
            (
                x - 23,
                y - 23,
                x + tamano + 23,
                y + tamano + 23
            ),
            outline=(
                90,
                255,
                190
            ),
            width=5
        )

    # ========================================================
    # MORADO
    # ========================================================

    elif tipo == "morado":

        draw.arc(
            (
                x - 23,
                y - 23,
                x + tamano + 23,
                y + tamano + 23
            ),
            0,
            180,
            fill=(
                230,
                150,
                255
            ),
            width=7
        )

    # ========================================================
    # ROJO
    # ========================================================

    elif tipo == "rojo":

        draw.arc(
            (
                x - 23,
                y - 23,
                x + tamano + 23,
                y + tamano + 23
            ),
            180,
            360,
            fill=(
                255,
                150,
                150
            ),
            width=7
        )

    # ========================================================
    # AZUL
    # ========================================================

    elif tipo == "azul":

        draw.arc(
            (
                x - 23,
                y - 23,
                x + tamano + 23,
                y + tamano + 23
            ),
            0,
            360,
            fill=(
                120,
                210,
                255
            ),
            width=6
        )

    # ========================================================
    # VERDE
    # ========================================================

    elif tipo == "verde":

        draw.arc(
            (
                x - 23,
                y - 23,
                x + tamano + 23,
                y + tamano + 23
            ),
            45,
            315,
            fill=(
                130,
                255,
                160
            ),
            width=7
        )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_corona(
    draw,
    x,
    y,
    tamano=100
):

    oro = (
        255,
        205,
        45
    )

    oro_claro = (
        255,
        235,
        100
    )

    # Base de la corona.
    draw.rounded_rectangle(
        (
            x,
            y + tamano * 0.62,
            x + tamano,
            y + tamano * 0.88
        ),
        radius=8,
        fill=oro
    )

    # Picos.
    puntos = [
        (
            x,
            y + tamano * 0.65
        ),

        (
            x + tamano * 0.08,
            y + tamano * 0.05
        ),

        (
            x + tamano * 0.30,
            y + tamano * 0.48
        ),

        (
            x + tamano * 0.50,
            y
        ),

        (
            x + tamano * 0.70,
            y + tamano * 0.48
        ),

        (
            x + tamano * 0.92,
            y + tamano * 0.05
        ),

        (
            x + tamano,
            y + tamano * 0.65
        )
    ]

    draw.polygon(
        puntos,
        fill=oro
    )

    # Joyas.
    draw.ellipse(
        (
            x + tamano * 0.10,
            y + tamano * 0.60,
            x + tamano * 0.18,
            y + tamano * 0.68
        ),
        fill=(
            255,
            70,
            70
        )
    )

    draw.ellipse(
        (
            x + tamano * 0.46,
            y + tamano * 0.60,
            x + tamano * 0.54,
            y + tamano * 0.68
        ),
        fill=(
            80,
            180,
            255
        )
    )

    draw.ellipse(
        (
            x + tamano * 0.82,
            y + tamano * 0.60,
            x + tamano * 0.90,
            y + tamano * 0.68
        ),
        fill=(
            180,
            100,
            255
        )
    )

    draw.line(
        (
            x + tamano * 0.08,
            y + tamano * 0.76,
            x + tamano * 0.92,
            y + tamano * 0.76
        ),
        fill=oro_claro,
        width=4
    )


def _dibujar_corazon(
    draw,
    x,
    y,
    tamano=85
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
            x + tamano * 0.5,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.5,
            y,
            x + tamano,
            y + tamano * 0.65
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano * 0.43,
            y + tamano * 0.25,
            x + tamano * 0.57,
            y + tamano * 0.90
        ),
        fill=(
            45,
            35,
            60
        )
    )


def _dibujar_rayos(
    draw,
    x,
    y,
    tamano=100
):

    color = (
        100,
        210,
        255
    )

    for angulo in (
        -60,
        -30,
        0,
        30,
        60,
    ):

        rad = math.radians(
            angulo
        )

        x2 = (
            x
            + math.cos(rad)
            * tamano
        )

        y2 = (
            y
            + math.sin(rad)
            * tamano
        )

        draw.line(
            (
                x,
                y,
                x2,
                y2
            ),
            fill=color,
            width=6
        )


def _dibujar_accesorio(
    draw,
    accesorio,
    frame=0
):

    nombre = _producto_id(
        accesorio
    )

    # --------------------------------------------------------
    # CORONA
    # --------------------------------------------------------

    if "corona" in nombre:

        # La corona queda ARRIBA del avatar,
        # no encima del nombre.
        _dibujar_corona(
            draw,
            AVATAR_X + 115,
            AVATAR_Y - 105,
            130
        )

    # --------------------------------------------------------
    # CORAZÓN
    # --------------------------------------------------------

    elif "corazon" in nombre:

        _dibujar_corazon(
            draw,
            ANCHO - 210,
            95,
            90
        )

    # --------------------------------------------------------
    # MARIPOSA
    # --------------------------------------------------------

    elif "mariposa" in nombre:

        _dibujar_mariposa(
            draw,
            ANCHO - 220,
            100,
            100
        )

    # --------------------------------------------------------
    # RAYOS
    # --------------------------------------------------------

    elif "rayos" in nombre:

        _dibujar_rayos(
            draw,
            ANCHO - 180,
            180,
            100
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
# INSIGNIA DE NIVEL
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=58
):

    # Círculo.
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
        )
    )

    # Estrella.
    _dibujar_estrella(
        draw,
        x + tamano / 2,
        y + tamano / 2,
        tamano * 0.34,
        (
            70,
            55,
            15
        )
    )


# ============================================================
# TOKEN
# ============================================================

def dibujar_icono_token(
    draw,
    x,
    y,
    tamano=42
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
            130
        ),
        width=3
    )

    draw.text(
        (
            x + tamano / 2,
            y + tamano / 2
        ),
        "$",
        font=cargar_fuente(
            25,
            negrita=True
        ),
        anchor="mm",
        fill=(
            100,
            70,
            10
        )
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
    ) * 100

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
        Y_NIVEL - 28,
        56
    )

    fuente_nivel = cargar_fuente(
        FONT_NIVEL,
        negrita=True
    )

    draw.text(
        (
            X_CONTENIDO + 75,
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
            f"XP {int(actual):,}"
            f" / {int(siguiente):,}"
        ),
        font=fuente_xp,
        anchor="lm",
        fill=(
            235,
            240,
            250
        )
    )

    # ========================================================
    # BARRA
    # ========================================================

    BAR_X = X_CONTENIDO
    BAR_Y = Y_BARRA

    BAR_W = 1120
    BAR_H = 48

    # Fondo.
    draw.rounded_rectangle(
        (
            BAR_X,
            BAR_Y,
            BAR_X + BAR_W,
            BAR_Y + BAR_H
        ),
        radius=24,
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
        width=3
    )

    progreso_w = int(
        BAR_W
        * porcentaje
        / 100
    )

    if progreso_w > 0:

        draw.rounded_rectangle(
            (
                BAR_X,
                BAR_Y,
                BAR_X + progreso_w,
                BAR_Y + BAR_H
            ),
            radius=24,
            fill=(
                65,
                185,
                255
            )
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
    # DETECTAR COSMÉTICOS
    # ========================================================

    color_nombre_real = detectar_color_nombre(
        equipados_lista
    )

    marco_real = detectar_marco(
        equipados_lista
    )

    fondo_real = detectar_fondo(
        equipados_lista
    )

    efectos = detectar_efectos(
        equipados_lista
    )

    # --------------------------------------------------------
    # Parámetros enviados directamente tienen prioridad
    # SOLO cuando no existe cosmético equipado.
    # --------------------------------------------------------

    if (
        not equipados_lista
        or color_nombre_real == "blanco"
    ):

        nombre_color_normalizado = _normalizar_texto(
            nombre_color
        )

        if (
            nombre_color_normalizado
            in COLORES_NOMBRE
        ):

            color_nombre_real = (
                nombre_color_normalizado
            )

    if (
        not equipados_lista
        or marco_real == "normal"
    ):

        marco_normalizado = _normalizar_texto(
            marco
        )

        if (
            marco_normalizado
            in COLORES_MARCO
        ):

            marco_real = (
                marco_normalizado
            )

    if (
        not equipados_lista
        or fondo_real == "normal"
    ):

        fondo_normalizado = _normalizar_texto(
            estilo_fondo
        )

        if (
            fondo_normalizado
            in COLORES_FONDO
        ):

            fondo_real = (
                fondo_normalizado
            )

    # ========================================================
    # IMAGEN BASE
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

    # ========================================================
    # FONDO
    # ========================================================

    dibujar_fondo(
        imagen,
        fondo_real,
        0
    )

    imagen = imagen.convert(
        "RGBA"
    )

    draw = ImageDraw.Draw(
        imagen
    )

    # ========================================================
    # EFECTOS DE FONDO
    # ========================================================

    for efecto in efectos:

        dibujar_efecto_fondo(
            draw,
            efecto,
            0
        )

    # ========================================================
    # AVATAR
    # ========================================================

    if avatar is None:

        avatar = crear_avatar_iniciales(
            nombre
        )

    color_marco = COLORES_MARCO.get(
        marco_real,
        COLORES_MARCO["normal"]
    )

    dibujar_avatar(
        imagen,
        avatar,
        AVATAR_X,
        AVATAR_Y,
        TAM_AVATAR,
        color_marco
    )

    # ========================================================
    # ACCESORIOS
    # ========================================================

    for accesorio in equipados_lista:

        pid = _producto_id(
            accesorio
        )

        # No dibujamos cosméticos que no son accesorios.
        if pid.startswith(
            "nombre_"
        ):
            continue

        if pid.startswith(
            "marco_"
        ):
            continue

        if pid.startswith(
            "fondo_"
        ):
            continue

        if (
            pid in (
                "blanco",
                "rojo",
                "azul",
                "verde",
                "amarillo",
                "morado",
                "rosa",
                "cian",
                "naranja",
                "esmeralda",
                "oro",
                "plata",
                "diamante",
            )
        ):
            continue

        _dibujar_accesorio(
            draw,
            pid,
            0
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

    nombre_mostrado = texto_ajustado(
        draw,
        str(nombre).upper(),
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
                X_CONTENIDO + 95,
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
    # ID INTERNO
    # ========================================================

    fuente_id = cargar_fuente(
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
            font=fuente_id,
            anchor="lm",
            fill=(
                225,
                230,
                240
            )
        )

    # ========================================================
    # ID DEL BOT
    # ========================================================

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

    # ========================================================
    # ID TELEGRAM
    # SOLO EN EL PROPIO PERFIL
    # ========================================================

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
                120
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

        dibujar_icono_token(
            draw,
            X_CONTENIDO,
            Y_TOKENS - 20,
            40
        )

        draw.text(
            (
                X_CONTENIDO + 55,
                Y_TOKENS
            ),
            f"TOKENS   {tokens_texto}",
            font=cargar_fuente(
                FONT_TOKENS,
                negrita=True
            ),
            anchor="lm",
            fill=(
                255,
                215,
                90
            )
        )

    # ========================================================
    # LÍNEA SEPARADORA
    # ========================================================

    draw.line(
        (
            X_CONTENIDO,
            485,
            ANCHO - 110,
            485
        ),
        fill=(
            255,
            255,
            255,
            45
        ),
        width=2
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
        optimize=False,
        compress_level=1
    )

    salida.seek(0)

    return (
        salida.getvalue(),
        "image/png",
        False
)

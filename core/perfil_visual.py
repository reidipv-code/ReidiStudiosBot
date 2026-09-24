import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================
# CONFIGURACIÓN HD
# ============================================================

ANCHO = 1800
ALTO = 1120

ESCALA = 2

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
    "marco_dorado": (255, 211, 77),
    "marco_diamante": (120, 230, 255),
    "marco_real": (170, 90, 255),
    "marco_glacial": (170, 245, 255),
    "marco_cosmico": (100, 80, 220),
    "marco_rosa_cristal": (255, 130, 210),
    "marco_corazones": (255, 80, 120),
    "marco_floral": (100, 210, 120),
    "marco_mariposas": (180, 100, 255),
    "marco_neon": (40, 255, 220),
    "marco_cyber": (50, 180, 255),
    "marco_samurai": (220, 80, 70),
    "marco_dark": (80, 80, 100),
    "marco_arcano": (150, 90, 255),
    "marco_esmeralda": (55, 220, 135),
    "marco_rubi": (230, 45, 70),
    "marco_ametista": (170, 90, 220),
}


# ============================================================
# FONDOS
# ============================================================

COLORES_FONDO = {
    "fondo_noche": (
        (12, 15, 35),
        (35, 20, 65),
    ),
    "fondo_nebulosa": (
        (15, 20, 60),
        (80, 30, 100),
    ),
    "fondo_cyber": (
        (5, 25, 40),
        (10, 70, 80),
    ),
    "fondo_rosa": (
        (55, 15, 45),
        (120, 35, 80),
    ),
    "fondo_floresta": (
        (8, 35, 25),
        (25, 80, 55),
    ),
    "fondo_abismo": (
        (3, 5, 12),
        (20, 25, 40),
    ),
}


# ============================================================
# ALIAS DE PRODUCTOS
#
# equipados_usuario() devuelve diccionarios de PRODUCTOS.
# Ejemplo:
#
# {
#   "nombre": "Nombre Esmeralda",
#   "tipo": "color",
#   ...
# }
#
# Por eso necesitamos convertir también los nombres humanos
# a sus IDs reales.
# ============================================================

ALIASES_PRODUCTOS = {
    "nombre dorado": "color_dorado",
    "nombre rosa": "color_rosa",
    "nombre cian": "color_cian",
    "nombre rojo": "color_rojo",
    "nombre violeta": "color_violeta",
    "nombre esmeralda": "color_esmeralda",

    "marco dorado": "marco_dorado",
    "marco diamante": "marco_diamante",
    "marco real": "marco_real",
    "marco glacial": "marco_glacial",
    "marco cósmico": "marco_cosmico",
    "rosa cristal": "marco_rosa_cristal",
    "corazones": "marco_corazones",
    "floral": "marco_floral",
    "mariposas": "marco_mariposas",
    "neón": "marco_neon",
    "cyber": "marco_cyber",
    "samurái": "marco_samurai",
    "dark": "marco_dark",
    "arcano": "marco_arcano",
    "esmeralda": "marco_esmeralda",
    "rubí": "marco_rubi",
    "amatista": "marco_ametista",

    "fuego": "efecto_fuego",
    "electricidad": "efecto_electricidad",
    "escarcha": "efecto_escarcha",
    "chispas doradas": "efecto_chispas",
    "partículas cósmicas": "efecto_cosmico",
    "aura oscura": "efecto_aura",
    "pétalos": "efecto_petalo",
    "burbujas": "efecto_burbujas",
    "lluvia de estrellas": "efecto_estrellas",
    "arcoíris": "efecto_arcoiris",

    "noche estrellada": "fondo_noche",
    "nebulosa": "fondo_nebulosa",
    "cyber city": "fondo_cyber",
    "sueño rosa": "fondo_rosa",
    "floresta mística": "fondo_floresta",
    "abismo": "fondo_abismo",

    "insignia corona": "insignia_corona",
    "insignia rayo": "insignia_rayo",
    "insignia corazón": "insignia_corazon",
    "insignia estelar": "insignia_estelar",
    "insignia arcana": "insignia_arcana",
}


# ============================================================
# UTILIDADES
# ============================================================

def _producto_id(producto):
    """
    Convierte cualquier representación de un producto
    en su ID real de tienda.

    Soporta:

        "color_esmeralda"

        {
            "id": "color_esmeralda"
        }

        {
            "producto_id": "color_esmeralda"
        }

        {
            "nombre": "Nombre Esmeralda",
            "tipo": "color"
        }
    """

    if producto is None:
        return None

    if isinstance(producto, str):
        valor = producto.strip()

        if not valor:
            return None

        valor_lower = valor.lower()

        if valor_lower in ALIASES_PRODUCTOS:
            return ALIASES_PRODUCTOS[valor_lower]

        return valor

    if isinstance(producto, dict):

        # Primero buscamos IDs reales.
        for clave in (
            "producto_id",
            "id",
            "codigo",
            "slug",
            "clave",
        ):
            valor = producto.get(clave)

            if valor is not None:
                valor = str(valor).strip()

                if valor:
                    valor_lower = valor.lower()

                    if valor_lower in ALIASES_PRODUCTOS:
                        return ALIASES_PRODUCTOS[
                            valor_lower
                        ]

                    return valor

        # Si no hay ID, utilizamos el nombre.
        nombre = producto.get("nombre")

        if nombre is not None:
            nombre = str(nombre).strip()
            nombre_lower = nombre.lower()

            if nombre_lower in ALIASES_PRODUCTOS:
                return ALIASES_PRODUCTOS[
                    nombre_lower
                ]

            # Intentamos reconstruir productos de color.
            if (
                str(producto.get("tipo", "")).lower()
                == "color"
            ):
                if "esmeralda" in nombre_lower:
                    return "color_esmeralda"

                if "dorado" in nombre_lower:
                    return "color_dorado"

                if "rosa" in nombre_lower:
                    return "color_rosa"

                if "cian" in nombre_lower:
                    return "color_cian"

                if "rojo" in nombre_lower:
                    return "color_rojo"

                if "violeta" in nombre_lower:
                    return "color_violeta"

            return nombre

    valor = str(producto).strip()

    if not valor:
        return None

    return valor


def normalizar_equipados(equipados):
    """
    Convierte equipamiento proveniente de la tienda
    en un formato sencillo:

        {
            "color": "color_esmeralda",
            "marco": "marco_dorado",
            "fondo": "fondo_noche",
            "efecto": "efecto_fuego",
            "insignia": "insignia_corona"
        }
    """

    if not equipados:
        return {}


    resultado = {}


    # --------------------------------------------------------
    # Diccionario:
    #
    # {
    #     "color": {...},
    #     "marco": {...}
    # }
    # --------------------------------------------------------

    if isinstance(equipados, dict):

        for clave, valor in equipados.items():

            clave_str = str(
                clave
            ).lower().strip()

            producto_id = _producto_id(
                valor
            )

            if not producto_id:
                continue

            resultado[
                clave_str
            ] = producto_id

            producto_lower = producto_id.lower()

            if producto_lower.startswith(
                "color_"
            ):
                resultado.setdefault(
                    "color",
                    producto_id,
                )

            elif producto_lower.startswith(
                "marco_"
            ):
                resultado.setdefault(
                    "marco",
                    producto_id,
                )

            elif producto_lower.startswith(
                "fondo_"
            ):
                resultado.setdefault(
                    "fondo",
                    producto_id,
                )

            elif producto_lower.startswith(
                "efecto_"
            ):
                resultado.setdefault(
                    "efecto",
                    producto_id,
                )

            elif producto_lower.startswith(
                "insignia_"
            ):
                resultado.setdefault(
                    "insignia",
                    producto_id,
                )

        return resultado


    # --------------------------------------------------------
    # Lista / tupla / set
    # --------------------------------------------------------

    if isinstance(
        equipados,
        (list, tuple, set),
    ):

        for producto in equipados:

            producto_id = _producto_id(
                producto
            )

            if not producto_id:
                continue

            producto_lower = (
                producto_id.lower()
            )

            if producto_lower.startswith(
                "color_"
            ):
                resultado.setdefault(
                    "color",
                    producto_id,
                )

            elif producto_lower.startswith(
                "marco_"
            ):
                resultado.setdefault(
                    "marco",
                    producto_id,
                )

            elif producto_lower.startswith(
                "fondo_"
            ):
                resultado.setdefault(
                    "fondo",
                    producto_id,
                )

            elif producto_lower.startswith(
                "efecto_"
            ):
                resultado.setdefault(
                    "efecto",
                    producto_id,
                )

            elif producto_lower.startswith(
                "insignia_"
            ):
                resultado.setdefault(
                    "insignia",
                    producto_id,
                )

    return resultado


# ============================================================
# FUENTES
# ============================================================

def cargar_fuente(
    tamano,
    negrita=False,
):
    rutas = []

    if negrita:
        rutas.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ])
    else:
        rutas.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ])

    for ruta in rutas:
        try:
            return ImageFont.truetype(
                ruta,
                tamano,
            )
        except OSError:
            pass

    return ImageFont.load_default()


# ============================================================
# TEXTO
# ============================================================

def texto_ajustado(
    draw,
    texto,
    fuente,
    max_ancho,
):
    texto = str(texto)

    if draw.textbbox(
        (0, 0),
        texto,
        font=fuente,
    )[2] <= max_ancho:
        return texto

    while texto and draw.textbbox(
        (0, 0),
        texto + "...",
        font=fuente,
    )[2] > max_ancho:

        texto = texto[:-1]

    return texto + "..."


# ============================================================
# GRADIENTE
# ============================================================

def crear_gradiente(
    c1,
    c2,
    ancho=ANCHO,
    alto=ALTO,
):
    imagen = Image.new(
        "RGB",
        (ancho, alto),
    )

    pixeles = imagen.load()

    for y in range(alto):

        t = y / max(
            1,
            alto - 1,
        )

        color = tuple(
            int(
                c1[i] * (1 - t)
                + c2[i] * t
            )
            for i in range(3)
        )

        for x in range(ancho):
            pixeles[x, y] = color

    return imagen.convert("RGBA")


# ============================================================
# AVATAR
# ============================================================

def redimensionar_avatar(
    imagen,
    tamano=380,
):
    imagen = imagen.convert(
        "RGBA"
    )

    lado = min(
        imagen.width,
        imagen.height,
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
        (
            tamano,
            tamano,
        ),
        Image.Resampling.LANCZOS,
    )


def crear_avatar_iniciales(
    nombre,
    tamano=380,
):
    imagen = Image.new(
        "RGBA",
        (
            tamano,
            tamano,
        ),
        (
            45,
            45,
            65,
            255,
        ),
    )

    draw = ImageDraw.Draw(
        imagen
    )

    fuente = cargar_fuente(
        max(
            64,
            tamano // 3,
        ),
        True,
    )

    partes = (
        str(nombre)
        .strip()
        .split()
    )

    iniciales = "".join(
        parte[0]
        for parte in partes[:2]
    ).upper() or "?"

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente,
    )

    ancho = (
        bbox[2] - bbox[0]
    )

    alto = (
        bbox[3] - bbox[1]
    )

    x = (
        tamano - ancho
    ) // 2

    y = (
        tamano - alto
    ) // 2 - bbox[1]

    draw.text(
        (x, y),
        iniciales,
        font=fuente,
        fill=(
            255,
            255,
            255,
            255,
        ),
    )

    return imagen


def recortar_circulo(
    imagen,
):
    imagen = imagen.convert(
        "RGBA"
    )

    mascara = Image.new(
        "L",
        imagen.size,
        0,
    )

    draw = ImageDraw.Draw(
        mascara
    )

    draw.ellipse(
        (
            0,
            0,
            imagen.width - 1,
            imagen.height - 1,
        ),
        fill=255,
    )

    resultado = Image.new(
        "RGBA",
        imagen.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    resultado.paste(
        imagen,
        (0, 0),
        mascara,
    )

    return resultado


# ============================================================
# FONDO
# ============================================================

def dibujar_fondo(
    base,
    fondo,
):
    fondo = _producto_id(
        fondo
    )

    if fondo in COLORES_FONDO:

        c1, c2 = (
            COLORES_FONDO[
                fondo
            ]
        )

        base.alpha_composite(
            crear_gradiente(
                c1,
                c2,
            )
        )

    else:

        base.alpha_composite(
            crear_gradiente(
                (
                    12,
                    15,
                    35,
                ),
                (
                    35,
                    20,
                    65,
                ),
            )
        )

    capa = Image.new(
        "RGBA",
        base.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        capa
    )

    random.seed(100)

    for _ in range(140):

        x = random.randint(
            0,
            ANCHO,
        )

        y = random.randint(
            0,
            ALTO,
        )

        r = random.choice(
            [
                2,
                2,
                3,
                4,
                5,
            ]
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                255,
                255,
                255,
                random.randint(
                    25,
                    100,
                ),
            ),
        )

    base.alpha_composite(
        capa
    )


# ============================================================
# AVATAR EN LA TARJETA
# ============================================================

def dibujar_avatar(
    base,
    avatar,
    x=140,
    y=260,
    tamano=380,
):
    if avatar is None:
        return

    avatar = redimensionar_avatar(
        avatar,
        tamano,
    )

    avatar = recortar_circulo(
        avatar
    )

    sombra = Image.new(
        "RGBA",
        (
            tamano + 40,
            tamano + 40,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )

    sombra_draw = ImageDraw.Draw(
        sombra
    )

    sombra_draw.ellipse(
        (
            10,
            10,
            tamano + 30,
            tamano + 30,
        ),
        fill=(
            0,
            0,
            0,
            150,
        ),
    )

    sombra = sombra.filter(
        ImageFilter.GaussianBlur(
            16
        )
    )

    base.alpha_composite(
        sombra,
        (
            x - 20,
            y - 20,
        ),
    )

    base.alpha_composite(
        avatar,
        (
            x,
            y,
        ),
    )


# ============================================================
# BANDERA DE CUBA
#
# Se dibuja manualmente para no depender de emoji.
# ============================================================

def dibujar_bandera_cuba(
    draw,
    x,
    y,
    ancho=90,
    alto=60,
):
    """
    Bandera cubana vectorial:
    - 3 franjas azules
    - 2 franjas blancas
    - triángulo rojo
    - estrella blanca
    """

    azul = (
        0,
        42,
        120,
        255,
    )

    blanco = (
        255,
        255,
        255,
        255,
    )

    rojo = (
        204,
        0,
        0,
        255,
    )

    # Franjas.
    altura_franja = alto / 5

    for i in range(5):

        color = (
            azul
            if i % 2 == 0
            else blanco
        )

        y1 = (
            y
            + i * altura_franja
        )

        y2 = (
            y
            + (i + 1)
            * altura_franja
        )

        draw.rectangle(
            (
                x,
                y1,
                x + ancho,
                y2,
            ),
            fill=color,
        )

    # Triángulo rojo.
    draw.polygon(
        [
            (
                x,
                y,
            ),
            (
                x
                + ancho * 0.48,
                y
                + alto / 2,
            ),
            (
                x,
                y + alto,
            ),
        ],
        fill=rojo,
    )

    # Estrella.
    cx = (
        x
        + ancho * 0.17
    )

    cy = (
        y
        + alto / 2
    )

    radio_externo = (
        alto * 0.16
    )

    radio_interno = (
        radio_externo * 0.42
    )

    puntos = []

    for i in range(10):

        angulo = (
            -math.pi / 2
            + i * math.pi / 5
        )

        radio = (
            radio_externo
            if i % 2 == 0
            else radio_interno
        )

        puntos.append(
            (
                cx
                + math.cos(
                    angulo
                ) * radio,
                cy
                + math.sin(
                    angulo
                ) * radio,
            )
        )

    draw.polygon(
        puntos,
        fill=blanco,
    )

    # Borde.
    draw.rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto,
        ),
        outline=(
            255,
            255,
            255,
            150,
        ),
        width=3,
    )


# ============================================================
# ICONO DE RANGO
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=60,
):
    """
    Insignia vectorial para representar el rango.
    No depende de emojis.
    """

    cx = (
        x
        + tamano / 2
    )

    cy = (
        y
        + tamano / 2
    )

    radio = (
        tamano * 0.42
    )

    # Sombra.
    draw.ellipse(
        (
            cx - radio - 5,
            cy - radio - 5,
            cx + radio + 5,
            cy + radio + 5,
        ),
        fill=(
            0,
            0,
            0,
            130,
        ),
    )

    # Medalla.
    draw.ellipse(
        (
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
        ),
        fill=(
            255,
            196,
            45,
            255,
        ),
        outline=(
            255,
            235,
            130,
            255,
        ),
        width=4,
    )

    # Estrella.
    puntos = []

    radio_externo = (
        radio * 0.65
    )

    radio_interno = (
        radio * 0.28
    )

    for i in range(10):

        angulo = (
            -math.pi / 2
            + i * math.pi / 5
        )

        r = (
            radio_externo
            if i % 2 == 0
            else radio_interno
        )

        puntos.append(
            (
                cx
                + math.cos(
                    angulo
                ) * r,
                cy
                + math.sin(
                    angulo
                ) * r,
            )
        )

    draw.polygon(
        puntos,
        fill=(
            255,
            255,
            255,
            255,
        ),
    )


# ============================================================
# ICONO DE TOKENS
# ============================================================

def dibujar_icono_token(
    draw,
    x,
    y,
    tamano=45,
):
    cx = (
        x
        + tamano / 2
    )

    cy = (
        y
        + tamano / 2
    )

    radio = (
        tamano / 2
    )

    draw.ellipse(
        (
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
        ),
        fill=(
            255,
            204,
            50,
            255,
        ),
        outline=(
            255,
            240,
            150,
            255,
        ),
        width=3,
    )

    fuente = cargar_fuente(
        int(
            tamano * 0.55
        ),
        True,
    )

    texto = "$"

    bbox = draw.textbbox(
        (0, 0),
        texto,
        font=fuente,
    )

    tw = (
        bbox[2]
        - bbox[0]
    )

    th = (
        bbox[3]
        - bbox[1]
    )

    draw.text(
        (
            cx - tw / 2,
            cy - th / 2 - bbox[1],
        ),
        texto,
        font=fuente,
        fill=(
            90,
            55,
            0,
            255,
        ),
    )


# ============================================================
# MARCO
# ============================================================

def dibujar_marco(
    base,
    marco,
):
    marco = _producto_id(
        marco
    )

    color = COLORES_MARCO.get(
        marco,
        (
            100,
            100,
            120,
        ),
    )

    capa = Image.new(
        "RGBA",
        base.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        capa
    )

    draw.rounded_rectangle(
        (
            24,
            24,
            ANCHO - 24,
            ALTO - 24,
        ),
        radius=60,
        outline=(
            *color,
            255,
        ),
        width=16,
    )

    draw.rounded_rectangle(
        (
            50,
            50,
            ANCHO - 50,
            ALTO - 50,
        ),
        radius=48,
        outline=(
            *color,
            90,
        ),
        width=6,
    )

    base.alpha_composite(
        capa
    )


# ============================================================
# DECORACIONES
# ============================================================

def _dibujar_corazones(
    draw,
    frame,
):
    fuente = cargar_fuente(
        44,
        True,
    )

    for i in range(9):

        x = (
            160
            + i * 200
        )

        y = (
            110
            + (
                frame * 16
                + i * 74
            ) % 900
        )

        draw.text(
            (x, y),
            "♥",
            font=fuente,
            fill=(
                255,
                90,
                130,
                150,
            ),
        )


def _dibujar_mariposas(
    draw,
    frame,
):
    for i in range(6):

        x = (
            200
            + i * 280
        )

        y = (
            140
            + (
                frame * 14
                + i * 120
            ) % 780
        )

        draw.ellipse(
            (
                x - 24,
                y - 10,
                x,
                y + 16,
            ),
            fill=(
                190,
                120,
                255,
                140,
            ),
        )

        draw.ellipse(
            (
                x,
                y - 10,
                x + 24,
                y + 16,
            ),
            fill=(
                100,
                200,
                255,
                140,
            ),
        )

        draw.line(
            (
                x,
                y,
                x,
                y + 26,
            ),
            fill=(
                255,
                255,
                255,
                160,
            ),
            width=4,
        )


def _dibujar_corona(
    draw,
    frame,
):
    # Corona vectorial para evitar problemas
    # con fuentes de emojis.
    x = ANCHO - 330
    y = 60

    puntos = [
        (
            x,
            y + 100,
        ),
        (
            x + 30,
            y + 15,
        ),
        (
            x + 95,
            y + 80,
        ),
        (
            x + 150,
            y + 15,
        ),
        (
            x + 190,
            y + 100,
        ),
    ]

    draw.polygon(
        puntos,
        fill=(
            255,
            215,
            60,
            220,
        ),
        outline=(
            255,
            240,
            150,
            255,
        ),
    )

    draw.rounded_rectangle(
        (
            x,
            y + 90,
            x + 190,
            y + 130,
        ),
        radius=12,
        fill=(
            255,
            190,
            40,
            230,
        ),
        outline=(
            255,
            240,
            150,
            255,
        ),
        width=4,
    )


def _dibujar_neon(
    draw,
    frame,
):
    color = (
        40,
        255,
        220,
        120,
    )

    for i in range(5):

        y = (
            200
            + i * 160
            + int(
                math.sin(
                    frame / 2 + i
                ) * 30
            )
        )

        draw.line(
            (
                80,
                y,
                ANCHO - 80,
                y,
            ),
            fill=color,
            width=4,
        )


# ============================================================
# EFECTOS
# ============================================================

def dibujar_efecto(
    base,
    efecto,
    frame=0,
):
    capa = Image.new(
        "RGBA",
        base.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        capa
    )

    efecto = _producto_id(
        efecto
    ) or ""

    if efecto == "efecto_fuego":
        _efecto_fuego(
            draw,
            frame,
        )

    elif efecto == "efecto_electricidad":
        _efecto_electricidad(
            draw,
            frame,
        )

    elif efecto == "efecto_escarcha":
        _efecto_escarcha(
            draw,
            frame,
        )

    elif efecto == "efecto_chispas":
        _efecto_chispas(
            draw,
            frame,
        )

    elif efecto == "efecto_cosmico":
        _efecto_cosmico(
            draw,
            frame,
        )

    elif efecto == "efecto_aura":
        _efecto_aura(
            draw,
            frame,
        )

    elif efecto == "efecto_corazones":
        _efecto_corazones(
            draw,
            frame,
        )

    elif efecto == "efecto_petalo":
        _efecto_petalo(
            draw,
            frame,
        )

    elif efecto == "efecto_mariposas":
        _efecto_mariposas(
            draw,
            frame,
        )

    elif efecto == "efecto_burbujas":
        _efecto_burbujas(
            draw,
            frame,
        )

    elif efecto == "efecto_estrellas":
        _efecto_estrellas(
            draw,
            frame,
        )

    elif efecto == "efecto_arcoiris":
        _efecto_arcoiris(
            draw,
            frame,
        )

    base.alpha_composite(
        capa
    )


def _efecto_fuego(
    draw,
    frame,
):
    random.seed(
        1000 + frame
    )

    for _ in range(90):

        x = random.randint(
            50,
            ANCHO - 50,
        )

        y = (
            ALTO
            - random.randint(
                40,
                240,
            )
        )

        r = random.randint(
            4,
            14,
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                255,
                random.randint(
                    80,
                    190,
                ),
                30,
                random.randint(
                    80,
                    180,
                ),
            ),
        )


def _efecto_electricidad(
    draw,
    frame,
):
    random.seed(
        2000 + frame
    )

    for _ in range(20):

        x = random.randint(
            80,
            ANCHO - 80,
        )

        puntos = [
            (x, 40)
        ]

        y = 40

        while y < ALTO - 40:

            y += random.randint(
                50,
                110,
            )

            x += random.randint(
                -50,
                50,
            )

            puntos.append(
                (x, y)
            )

        draw.line(
            puntos,
            fill=(
                100,
                220,
                255,
                180,
            ),
            width=4,
        )


def _efecto_escarcha(
    draw,
    frame,
):
    random.seed(
        3000 + frame
    )

    for _ in range(110):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        r = random.randint(
            4,
            10,
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                180,
                240,
                255,
                130,
            ),
        )


def _efecto_chispas(
    draw,
    frame,
):
    random.seed(
        4000 + frame
    )

    for _ in range(120):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        r = random.randint(
            2,
            7,
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                255,
                220,
                100,
                180,
            ),
        )


def _efecto_cosmico(
    draw,
    frame,
):
    random.seed(5000)

    for i in range(140):

        angulo = (
            i * 37
            + frame * 8
        ) % 360

        radio = (
            160
            + (i * 34) % 600
        )

        cx = (
            ANCHO // 2
            + math.cos(
                math.radians(
                    angulo
                )
            ) * radio
        )

        cy = (
            ALTO // 2
            + math.sin(
                math.radians(
                    angulo
                )
            ) * radio
        )

        r = 2 + i % 6

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r,
            ),
            fill=(
                190,
                150,
                255,
                140,
            ),
        )


def _efecto_aura(
    draw,
    frame,
):
    alpha = (
        70
        + int(
            40
            * math.sin(
                frame / 2
            )
        )
    )

    draw.ellipse(
        (
            200,
            120,
            ANCHO - 200,
            ALTO - 120,
        ),
        outline=(
            100,
            200,
            255,
            alpha,
        ),
        width=24,
    )


def _efecto_corazones(
    draw,
    frame,
):
    random.seed(
        6000 + frame
    )

    fuente = cargar_fuente(
        44,
        True,
    )

    for _ in range(32):

        x = random.randint(
            50,
            ANCHO - 90,
        )

        y = random.randint(
            50,
            ALTO - 90,
        )

        draw.text(
            (
                x,
                y,
            ),
            "♥",
            font=fuente,
            fill=(
                255,
                80,
                130,
                random.randint(
                    80,
                    180,
                ),
            ),
        )


def _efecto_petalo(
    draw,
    frame,
):
    random.seed(
        7000 + frame
    )

    for _ in range(60):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        draw.ellipse(
            (
                x - 8,
                y - 16,
                x + 8,
                y + 16,
            ),
            fill=(
                255,
                150,
                190,
                130,
            ),
        )


def _efecto_mariposas(
    draw,
    frame,
):
    _dibujar_mariposas(
        draw,
        frame,
    )


def _efecto_burbujas(
    draw,
    frame,
):
    for i in range(40):

        x = (
            60
            + (
                i * 146
                + frame * 8
            )
            % (
                ANCHO - 120
            )
        )

        y = (
            ALTO
            - (
                i * 94
                + frame * 16
            )
            % (
                ALTO - 80
            )
        )

        r = (
            8
            + i % 14
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            outline=(
                130,
                220,
                255,
                120,
            ),
            width=4,
        )


def _efecto_estrellas(
    draw,
    frame,
):
    random.seed(9000)

    for i in range(70):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        r = 4 + (
            (i + frame) % 6
        )

        draw.line(
            (
                x - r,
                y,
                x + r,
                y,
            ),
            fill=(
                255,
                255,
                220,
                180,
            ),
            width=2,
        )

        draw.line(
            (
                x,
                y - r,
                x,
                y + r,
            ),
            fill=(
                255,
                255,
                220,
                180,
            ),
            width=2,
        )


def _efecto_arcoiris(
    draw,
    frame,
):
    colores = [
        (
            255,
            70,
            70,
            150,
        ),
        (
            255,
            170,
            50,
            150,
        ),
        (
            255,
            240,
            70,
            150,
        ),
        (
            70,
            230,
            120,
            150,
        ),
        (
            70,
            180,
            255,
            150,
        ),
        (
            150,
            90,
            255,
            150,
        ),
    ]

    for i, color in enumerate(
        colores
    ):

        margen = i * 14

        draw.rounded_rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen,
            ),
            radius=70,
            outline=color,
            width=8,
        )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_accesorio(
    base,
    accesorio,
    frame,
):
    accesorio = _producto_id(
        accesorio
    )

    if not accesorio:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        capa
    )

    nombre = (
        accesorio.lower()
    )

    if (
        "corona" in nombre
        or nombre == "insignia_corona"
    ):
        _dibujar_corona(
            draw,
            frame,
        )

    elif "neon" in nombre:
        _dibujar_neon(
            draw,
            frame,
        )

    base.alpha_composite(
        capa
    )


# ============================================================
# INSIGNIAS
# ============================================================

def dibujar_insignia(
    base,
    insignia,
):
    insignia = _producto_id(
        insignia
    )

    if not insignia:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        capa
    )

    x = 1510
    y = 780
    tamano = 130

    color = (
        255,
        210,
        70,
        255,
    )

    if insignia == "insignia_rayo":
        color = (
            255,
            220,
            70,
            255,
        )

    elif insignia == "insignia_corazon":
        color = (
            255,
            80,
            130,
            255,
        )

    elif insignia == "insignia_estelar":
        color = (
            130,
            210,
            255,
            255,
        )

    elif insignia == "insignia_arcana":
        color = (
            190,
            110,
            255,
            255,
        )

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano,
        ),
        fill=(
            20,
            20,
            35,
            220,
        ),
        outline=color,
        width=8,
    )

    cx = (
        x + tamano / 2
    )

    cy = (
        y + tamano / 2
    )

    if insignia == "insignia_corona":

        _dibujar_corona(
            draw,
            0,
        )

    elif insignia == "insignia_corazon":

        fuente = cargar_fuente(
            70,
            True,
        )

        draw.text(
            (
                cx - 36,
                cy - 45,
            ),
            "♥",
            font=fuente,
            fill=color,
        )

    elif insignia == "insignia_rayo":

        draw.polygon(
            [
                (
                    cx + 15,
                    cy - 55,
                ),
                (
                    cx - 25,
                    cy + 5,
                ),
                (
                    cx,
                    cy + 5,
                ),
                (
                    cx - 15,
                    cy + 55,
                ),
                (
                    cx + 35,
                    cy - 15,
                ),
                (
                    cx + 8,
                    cy - 15,
                ),
            ],
            fill=color,
        )

    elif insignia in (
        "insignia_estelar",
        "insignia_arcana",
    ):

        puntos = []

        radio_externo = 42
        radio_interno = 18

        for i in range(10):

            angulo = (
                -math.pi / 2
                + i * math.pi / 5
            )

            radio = (
                radio_externo
                if i % 2 == 0
                else radio_interno
            )

            puntos.append(
                (
                    cx
                    + math.cos(
                        angulo
                    ) * radio,
                    cy
                    + math.sin(
                        angulo
                    ) * radio,
                )
            )

        draw.polygon(
            puntos,
            fill=color,
        )

    base.alpha_composite(
        capa
    )


# ============================================================
# GENERADOR PRINCIPAL
# ============================================================

def generar_perfil(
    nombre,
    nivel,
    rango,
    xp_total,
    xp_siguiente,
    tokens,
    pais=None,
    avatar=None,
    equipados=None,
):
    """
    Genera el perfil visual HD.

    Devuelve:

        bytes,
        mime,
        animado
    """

    equipados = normalizar_equipados(
        equipados
    )

    # --------------------------------------------------------
    # EQUIPAMIENTO
    # --------------------------------------------------------

    marco = _producto_id(
        equipados.get(
            "marco"
        )
    )

    fondo = _producto_id(
        equipados.get(
            "fondo"
        )
    )

    efecto = _producto_id(
        equipados.get(
            "efecto"
        )
    )

    accesorio = _producto_id(
        equipados.get(
            "accesorio"
        )
    )

    insignia = _producto_id(
        equipados.get(
            "insignia"
        )
    )

    color_nombre = _producto_id(
        equipados.get(
            "color"
        )
        or equipados.get(
            "color_nombre"
        )
    )

    # --------------------------------------------------------
    # COLOR DEL NOMBRE
    # --------------------------------------------------------

    color_texto = COLORES_NOMBRE.get(
        color_nombre,
        (
            255,
            255,
            255,
        ),
    )

    # --------------------------------------------------------
    # AVATAR
    # --------------------------------------------------------

    if avatar is None:

        avatar_img = (
            crear_avatar_iniciales(
                nombre,
                380,
            )
        )

    else:

        avatar_img = avatar

    # --------------------------------------------------------
    # ANIMACIÓN
    # --------------------------------------------------------

    animado = bool(
        efecto
    )

    cantidad_frames = (
        FRAMES_ANIMADOS
        if animado
        else 1
    )

    frames = []

    # ========================================================
    # CREACIÓN DE FRAMES
    # ========================================================

    for frame in range(
        cantidad_frames
    ):

        imagen = Image.new(
            "RGBA",
            (
                ANCHO,
                ALTO,
            ),
            (
                0,
                0,
                0,
                255,
            ),
        )

        # ----------------------------------------------------
        # FONDO
        # ----------------------------------------------------

        dibujar_fondo(
            imagen,
            fondo,
        )

        # ----------------------------------------------------
        # EFECTO
        # ----------------------------------------------------

        dibujar_efecto(
            imagen,
            efecto,
            frame,
        )

        # ----------------------------------------------------
        # ACCESORIO
        # ----------------------------------------------------

        _dibujar_accesorio(
            imagen,
            accesorio,
            frame,
        )

        # ----------------------------------------------------
        # AVATAR
        # ----------------------------------------------------

        dibujar_avatar(
            imagen,
            avatar_img,
            140,
            260,
            380,
        )

        draw = ImageDraw.Draw(
            imagen
        )

        # ----------------------------------------------------
        # FUENTES HD
        # ----------------------------------------------------

        fuente_nombre = (
            cargar_fuente(
                84,
                True,
            )
        )

        fuente_info = (
            cargar_fuente(
                50,
                False,
            )
        )

        fuente_pequena = (
            cargar_fuente(
                40,
                False,
            )
        )

        fuente_footer = (
            cargar_fuente(
                30,
                True,
            )
        )

        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        nombre_mostrado = (
            texto_ajustado(
                draw,
                nombre,
                fuente_nombre,
                1120,
            )
        )

        # Sombra del nombre.
        draw.text(
            (
                600 + 5,
                190 + 5,
            ),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                0,
                0,
                0,
                170,
            ),
        )

        # Nombre con el color equipado.
        draw.text(
            (
                600,
                190,
            ),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                *color_texto,
                255,
            ),
        )

        # ----------------------------------------------------
        # NIVEL
        # ----------------------------------------------------

        draw.text(
            (
                600,
                320,
            ),
            f"Nivel {nivel}",
            font=fuente_info,
            fill=(
                255,
                255,
                255,
                240,
            ),
        )

        # ----------------------------------------------------
        # RANGO + INSIGNIA
        # ----------------------------------------------------

        dibujar_icono_rango(
            draw,
            600,
            405,
            70,
        )

        draw.text(
            (
                690,
                412,
            ),
            f"Rango: {rango}",
            font=fuente_info,
            fill=(
                235,
                235,
                245,
                240,
            ),
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        draw.text(
            (
                600,
                500,
            ),
            f"XP: {xp_total} / {xp_siguiente}",
            font=fuente_info,
            fill=(
                225,
                225,
                235,
                240,
            ),
        )

        # ----------------------------------------------------
        # TOKENS
        # ----------------------------------------------------

        dibujar_icono_token(
            draw,
            600,
            590,
            55,
        )

        draw.text(
            (
                675,
                592,
            ),
            f"Tokens: {tokens}",
            font=fuente_info,
            fill=(
                255,
                215,
                80,
                245,
            ),
        )

        # ----------------------------------------------------
        # PAÍS
        # ----------------------------------------------------

        if pais:

            pais_texto = str(
                pais
            )

            # Si viene "🇨🇺 Cuba", eliminamos
            # el emoji porque puede no renderizarse.
            pais_limpio = (
                pais_texto
                .replace(
                    "🇨🇺",
                    "",
                )
                .strip()
            )

            dibujar_bandera_cuba(
                draw,
                600,
                700,
                90,
                60,
            )

            draw.text(
                (
                    720,
                    704,
                ),
                pais_limpio,
                font=fuente_pequena,
                fill=(
                    210,
                    225,
                    235,
                    235,
                ),
            )

        # ----------------------------------------------------
        # BARRA XP
        # ----------------------------------------------------

        try:

            xp_actual = max(
                0,
                float(
                    xp_total
                ),
            )

            xp_meta = max(
                1,
                float(
                    xp_siguiente
                ),
            )

            progreso = min(
                1.0,
                xp_actual / xp_meta,
            )

        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):

            progreso = 0.0

        barra_x = 600
        barra_y = 820

        barra_w = 1050
        barra_h = 44

        # Fondo.
        draw.rounded_rectangle(
            (
                barra_x,
                barra_y,
                barra_x + barra_w,
                barra_y + barra_h,
            ),
            radius=22,
            fill=(
                25,
                25,
                35,
                220,
            ),
            outline=(
                255,
                255,
                255,
                80,
            ),
            width=4,
        )

        # Progreso.
        if progreso > 0:

            ancho_progreso = max(
                44,
                int(
                    barra_w
                    * progreso
                ),
            )

            draw.rounded_rectangle(
                (
                    barra_x,
                    barra_y,
                    barra_x
                    + ancho_progreso,
                    barra_y
                    + barra_h,
                ),
                radius=22,
                fill=(
                    70,
                    200,
                    255,
                    235,
                ),
            )

        # ----------------------------------------------------
        # INSIGNIA EQUIPADA
        # ----------------------------------------------------

        if insignia:
            dibujar_insignia(
                imagen,
                insignia,
            )

        # ----------------------------------------------------
        # MARCO
        # ----------------------------------------------------

        if marco:

            dibujar_marco(
                imagen,
                marco,
            )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        draw.text(
            (
                110,
                ALTO - 90,
            ),
            "Reidi Studios",
            font=fuente_footer,
            fill=(
                255,
                255,
                255,
                150,
            ),
        )

        # ----------------------------------------------------
        # EXPORTACIÓN DEL FRAME
        # ----------------------------------------------------

        frames.append(
            imagen.convert(
                "RGB"
            )
        )

    # ========================================================
    # SALIDA
    # ========================================================

    salida = io.BytesIO()

    if animado:

        frames[0].save(
            salida,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=int(
                1000 / FPS
            ),
            loop=0,
            optimize=False,
        )

        mime = "image/gif"

    else:

        frames[0].save(
            salida,
            format="PNG",
            optimize=True,
        )

        mime = "image/png"

    return (
        salida.getvalue(),
        mime,
        animado,
    )

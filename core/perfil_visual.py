import io
import math

from PIL import Image, ImageDraw, ImageFont

from core.paises import PAISES


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

ANCHO = 1920
ALTO = 1080

# ============================================================
# FUENTES
# ============================================================

# DejaVu Sans es una fuente de sistema disponible normalmente
# en Linux/Railway y tiene muy buena compatibilidad Unicode.
FUENTE_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

FUENTE_NEGRITA = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

# Fuente alternativa para símbolos/emojis.
FUENTE_EMOJI = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/opentype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf",
]


# ============================================================
# TAMAÑOS DE LETRA
# ============================================================

FONT_NOMBRE = 116
FONT_PAIS = 52

FONT_ID = 42
FONT_TOKENS = 44

FONT_NIVEL = 70
FONT_XP = 62
FONT_PORCENTAJE = 52
FONT_RANGO = 56

# Emojis grandes.
FONT_EMOJI = 58


# ============================================================
# TAMAÑOS DE ELEMENTOS
# ============================================================

TAM_AVATAR = 360

TAM_ICONO = 58

# Bandera pequeña y proporcionada.
FLAG_W = 82
FLAG_H = 52


# ============================================================
# POSICIONES
# ============================================================

X_CONTENIDO = 540

Y_NOMBRE = 105
Y_PAIS = 220

Y_ID = 315
Y_BOT_ID = 370
Y_TELEGRAM_ID = 425
Y_TOKENS = 480

# XP completamente agrupado.
Y_NIVEL = 570
Y_XP = 650
Y_BARRA = 735
Y_PORCENTAJE = 815
Y_RANGO = 895


# ============================================================
# COLORES
# ============================================================

COLORES_NOMBRE = {
    "blanco": (255, 255, 255),
    "rojo": (255, 80, 80),
    "azul": (80, 170, 255),
    "verde": (90, 230, 130),
    "amarillo": (255, 220, 80),
    "morado": (190, 110, 255),
    "rosa": (255, 110, 190),
    "cian": (80, 230, 255),
    "naranja": (255, 150, 70),
    "esmeralda": (50, 220, 150),
}


COLORES_MARCO = {
    "normal": (95, 105, 125),
    "oro": (255, 205, 70),
    "plata": (200, 210, 225),
    "diamante": (100, 220, 255),
    "rojo": (255, 80, 80),
    "morado": (180, 90, 255),
    "esmeralda": (50, 220, 150),
}


COLORES_FONDO = {
    "normal": (
        (18, 23, 38),
        (48, 60, 90)
    ),

    "azul": (
        (8, 22, 50),
        (25, 85, 150)
    ),

    "morado": (
        (25, 12, 50),
        (95, 35, 145)
    ),

    "rojo": (
        (45, 10, 18),
        (145, 32, 48)
    ),

    "verde": (
        (8, 35, 22),
        (25, 125, 75)
    ),

    "esmeralda": (
        (5, 30, 27),
        (20, 125, 95)
    ),
}


ALIASES_PRODUCTOS = {
    "nombre_rojo": "rojo",
    "nombre_azul": "azul",
    "nombre_verde": "verde",
    "nombre_amarillo": "amarillo",
    "nombre_morado": "morado",
    "nombre_rosa": "rosa",
    "nombre_cian": "cian",
    "nombre_naranja": "naranja",
    "nombre_esmeralda": "esmeralda",

    "marco_oro": "oro",
    "marco_plata": "plata",
    "marco_diamante": "diamante",
    "marco_rojo": "rojo",
    "marco_morado": "morado",
    "marco_esmeralda": "esmeralda",
}


# ============================================================
# PRODUCTOS
# ============================================================

def _producto_id(producto):
    if producto is None:
        return ""

    if isinstance(producto, dict):
        for clave in (
            "id",
            "producto_id",
            "nombre",
            "item"
        ):
            if producto.get(clave) is not None:
                return str(
                    producto[clave]
                ).lower().strip()

    return str(
        producto
    ).lower().strip()


def normalizar_equipados(equipados):
    if equipados is None:
        return []

    if isinstance(equipados, dict):

        resultado = []

        for clave, valor in equipados.items():

            if isinstance(
                valor,
                (list, tuple, set)
            ):
                resultado.extend(valor)

            elif valor:
                resultado.append(valor)

            else:
                resultado.append(clave)

        return resultado

    if isinstance(
        equipados,
        (list, tuple, set)
    ):
        return list(equipados)

    return [equipados]


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
        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except Exception:
            pass

    # Fallback de Pillow.
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
# GRADIENTE
# ============================================================

def crear_gradiente(
    color1,
    color2
):
    imagen = Image.new(
        "RGB",
        (ANCHO, ALTO)
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
    colores = COLORES_FONDO.get(
        estilo,
        COLORES_FONDO["normal"]
    )

    fondo = crear_gradiente(
        *colores
    )

    overlay = Image.new(
        "RGBA",
        (ANCHO, ALTO),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # Brillo superior derecho.
    draw.ellipse(
        (
            1250,
            -300,
            2100,
            550
        ),
        fill=(255, 255, 255, 10)
    )

    # Sombra inferior.
    draw.ellipse(
        (
            -350,
            700,
            600,
            1450
        ),
        fill=(0, 0, 0, 25)
    )

    # Marco exterior.
    for i in range(16):

        margen = i * 10

        draw.rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen
            ),
            outline=(
                0,
                0,
                0,
                5 + i * 2
            ),
            width=5
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

    avatar = avatar.convert(
        "RGBA"
    )

    return avatar.resize(
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

    nombre = str(
        nombre or "?"
    ).strip()

    partes = nombre.split()

    if len(partes) >= 2:

        iniciales = (
            partes[0][0]
            + partes[1][0]
        ).upper()

    elif nombre:

        iniciales = nombre[:2].upper()

    else:

        iniciales = "?"

    fuente = cargar_fuente(
        130,
        negrita=True
    )

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente
    )

    ancho = (
        bbox[2] - bbox[0]
    )

    alto = (
        bbox[3] - bbox[1]
    )

    draw.text(
        (
            (tamano - ancho) / 2,
            (tamano - alto) / 2 - 10
        ),
        iniciales,
        font=fuente,
        fill=(240, 240, 245, 255)
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
    tamano
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
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    draw.ellipse(
        (
            x - 14,
            y - 14,
            x + tamano + 14,
            y + tamano + 14
        ),
        outline=(255, 255, 255, 190),
        width=10
    )

    imagen.alpha_composite(
        overlay
    )

    imagen.alpha_composite(
        avatar,
        (x, y)
    )


# ============================================================
# PAÍS
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
                    fill=(30, 85, 170)
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

    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto
        ),
        radius=8,
        fill=(45, 50, 65),
        outline=(255, 255, 255),
        width=2
    )

    if bandera:

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
# MARCO
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


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_corazon(
    draw,
    x,
    y,
    tamano=80
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
            x + tamano / 2,
            y + tamano / 2
        ),
        fill=color
    )

    draw.ellipse(
        (
            x + tamano / 2 - tamano * 0.25,
            y,
            x + tamano,
            y + tamano / 2
        ),
        fill=color
    )

    draw.polygon(
        [
            (
                x,
                y + tamano * 0.25
            ),
            (
                x + tamano,
                y + tamano * 0.25
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
    tamano=80
):
    color = (
        180,
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
            y + tamano * 0.9
        ),
        fill=(40, 30, 60)
    )


def _dibujar_corona(
    draw,
    x=None,
    y=None,
    tamano=80
):
    if x is None:
        x = (
            ANCHO // 2
            - tamano // 2
        )

    if y is None:
        y = 40

    color = (
        255,
        210,
        60
    )

    puntos = [
        (x, y + tamano),
        (
            x + tamano * 0.15,
            y
        ),
        (
            x + tamano * 0.45,
            y + tamano * 0.55
        ),
        (
            x + tamano * 0.7,
            y
        ),
        (
            x + tamano,
            y + tamano
        )
    ]

    draw.polygon(
        puntos,
        fill=color
    )

    draw.rectangle(
        (
            x,
            y + tamano * 0.75,
            x + tamano,
            y + tamano
        ),
        fill=color
    )


def _dibujar_accesorio(
    draw,
    accesorio,
    frame=0
):
    nombre = _producto_id(
        accesorio
    )

    if "corona" in nombre:

        _dibujar_corona(
            draw,
            x=X_CONTENIDO + 110,
            y=25,
            tamano=90
        )

    elif "corazon" in nombre:

        _dibujar_corazon(
            draw,
            ANCHO - 250,
            80,
            75
        )

    elif "mariposa" in nombre:

        _dibujar_mariposa(
            draw,
            ANCHO - 260,
            120,
            80
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
# ICONO DE NIVEL
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=58
):
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(255, 205, 70)
    )

    _dibujar_estrella(
        draw,
        x + tamano / 2,
        y + tamano / 2,
        tamano * 0.36,
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
        actual / siguiente
    ) * 100

    porcentaje = max(
        0,
        min(100, porcentaje)
    )

    # ========================================================
    # NIVEL
    # ========================================================

    dibujar_icono_rango(
        draw,
        X_CONTENIDO,
        Y_NIVEL - 32,
        TAM_ICONO
    )

    fuente_nivel = cargar_fuente(
        FONT_NIVEL,
        negrita=True
    )

    draw.text(
        (
            X_CONTENIDO + 78,
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

    BAR_X = X_CONTENIDO
    BAR_Y = Y_BARRA
    BAR_W = 1120
    BAR_H = 54

    draw.rounded_rectangle(
        (
            BAR_X,
            BAR_Y,
            BAR_X + BAR_W,
            BAR_Y + BAR_H
        ),
        radius=BAR_H // 2,
        fill=(12, 16, 25),
        outline=(130, 140, 160),
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
            radius=BAR_H // 2,
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
            BAR_X + BAR_W,
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
    # FONDO
    # ========================================================

    imagen = Image.new(
        "RGB",
        (
            ANCHO,
            ALTO
        ),
        (20, 25, 40)
    )

    dibujar_fondo(
        imagen,
        estilo_fondo
    )

    imagen = imagen.convert(
        "RGBA"
    )

    draw = ImageDraw.Draw(
        imagen
    )

    # ========================================================
    # EQUIPADOS
    # ========================================================

    equipados_lista = normalizar_equipados(
        equipados
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

    dibujar_avatar(
        imagen,
        avatar,
        avatar_x,
        avatar_y,
        TAM_AVATAR
    )

    # ========================================================
    # MARCO
    # ========================================================

    marco_real = marco or "normal"

    for producto in equipados_lista:

        pid = _producto_id(
            producto
        )

        if pid.startswith(
            "marco_"
        ):
            posible = ALIASES_PRODUCTOS.get(
                pid
            )

            if posible:
                marco_real = posible

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
        nombre_color,
        COLORES_NOMBRE["blanco"]
    )

    # Detectar color comprado.
    for producto in equipados_lista:

        pid = _producto_id(
            producto
        )

        if pid.startswith(
            "nombre_"
        ):
            color_real = ALIASES_PRODUCTOS.get(
                pid
            )

            if color_real in COLORES_NOMBRE:
                color_nombre = COLORES_NOMBRE[
                    color_real
                ]

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
    # PAÍS + BANDERA
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
            fill=(225, 230, 240)
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
            fill=(225, 230, 240)
        )

    # ========================================================
    # TELEGRAM ID
    # SOLO PROPIETARIO
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
            fill=(255, 220, 120)
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
    # ACCESORIOS
    # ========================================================

    for accesorio in equipados_lista:

        pid = _producto_id(
            accesorio
        )

        if (
            pid.startswith("nombre_")
            or pid.startswith("marco_")
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
    # LÍNEA DECORATIVA
    # ========================================================

    draw.line(
        (
            X_CONTENIDO,
            535,
            ANCHO - 120,
            535
        ),
        fill=(255, 255, 255, 40),
        width=2
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

import io
import math

from PIL import Image, ImageDraw, ImageFont

from core.paises import PAISES


# ============================================================
# TAMAÑO DEL PERFIL
# ============================================================

ANCHO = 1920
ALTO = 1080


# ============================================================
# FUENTES
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
            size=32
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
# COLORES DE NOMBRE
# ============================================================

COLORES_NOMBRE = {
    "blanco": (255, 255, 255),
    "rojo": (255, 70, 70),
    "azul": (70, 160, 255),
    "verde": (70, 225, 110),
    "amarillo": (255, 220, 60),
    "morado": (190, 90, 255),
    "rosa": (255, 100, 190),
    "cian": (70, 230, 255),
    "naranja": (255, 145, 55),
    "esmeralda": (40, 230, 145),
}


# ============================================================
# COLORES DE MARCOS
# ============================================================

COLORES_MARCO = {
    "normal": (100, 110, 130),
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
# ALIAS
# ============================================================

COLORES = (
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
)

FONDOS = (
    "normal",
    "azul",
    "rojo",
    "verde",
    "morado",
    "rosa",
    "cian",
    "naranja",
    "esmeralda",
    "oro",
    "negro",
)

MARCOS = (
    "normal",
    "oro",
    "plata",
    "diamante",
    "rojo",
    "azul",
    "verde",
    "morado",
    "rosa",
    "cian",
    "naranja",
    "esmeralda",
)


# ============================================================
# PRODUCTOS
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

            valor = producto.get(clave)

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

                for elemento in valor:
                    resultado.append(elemento)

            elif isinstance(
                valor,
                dict
            ):

                resultado.append(valor)

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
# DETECCIÓN DE COSMÉTICOS
# ============================================================

def detectar_color_nombre(equipados):
    resultado = None

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        # Debe ser un producto de nombre/color
        # o contener explícitamente un color.
        es_color = any(
            palabra in texto
            for palabra in (
                "nombre",
                "color",
                "namecolor",
                "name_color",
            )
        )

        if es_color:

            for color in COLORES:

                if color in texto:
                    resultado = color

        # Compatibilidad con productos antiguos
        # que solamente se llamaban "esmeralda",
        # "rojo", etc.
        if not es_color:

            palabras_exclusivas = (
                "marco",
                "fondo",
                "efecto",
                "corona",
                "corazon",
                "mariposa",
                "insignia",
            )

            if not any(
                p in texto
                for p in palabras_exclusivas
            ):

                for color in COLORES:

                    if texto == color:
                        resultado = color

    return resultado or "blanco"


def detectar_marco(equipados):
    resultado = "normal"

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        if (
            "marco" in texto
            or "frame" in texto
        ):

            for marco in MARCOS:

                if marco in texto:
                    resultado = marco

    return resultado


def detectar_fondo(equipados):
    resultado = "normal"

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        if not texto:
            continue

        if (
            "fondo" in texto
            or "background" in texto
            or "bg_" in texto
            or "estilo_fondo" in texto
        ):

            for fondo in FONDOS:

                if fondo in texto:
                    resultado = fondo

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

    # Brillo superior derecho.
    draw.ellipse(
        (
            1250,
            -300,
            2150,
            600
        ),
        fill=(255, 255, 255, 13)
    )

    # Decoración inferior izquierda.
    draw.ellipse(
        (
            -400,
            650,
            650,
            1500
        ),
        fill=(0, 0, 0, 30)
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
            fill=(255, 255, 255, 13),
            width=4
        )

    # Borde.
    draw.rounded_rectangle(
        (
            8,
            8,
            ANCHO - 8,
            ALTO - 8
        ),
        radius=25,
        outline=(130, 145, 175, 80),
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
        (35, 40, 55, 255)
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
        fill=(240, 240, 245, 255)
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
                    fill=(35, 90, 175)
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
            fill=(215, 40, 50)
        )

        # Estrella.
        puntos = []

        cx = x + ancho * 0.17
        cy = y + alto / 2
        radio = alto * 0.18

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
            fill=(255, 255, 255)
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

    # Intentar dibujar el emoji.
    fuente = cargar_fuente(
        40
    )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto
        ),
        radius=7,
        fill=(40, 45, 60),
        outline=(220, 225, 235),
        width=2
    )

    if bandera:

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

    # Anillo exterior.
    draw.ellipse(
        (
            x - 18,
            y - 18,
            x + tamano + 18,
            y + tamano + 18
        ),
        outline=color,
        width=12
    )

    # Segundo anillo.
    draw.ellipse(
        (
            x - 8,
            y - 8,
            x + tamano + 8,
            y + tamano + 8
        ),
        outline=color,
        width=4
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
    color_oro = (
        255,
        205,
        45
    )

    color_luz = (
        255,
        235,
        120
    )

    # Picos.
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
        fill=color_oro,
        outline=(255, 245, 170)
    )

    # Banda inferior.
    draw.rounded_rectangle(
        (
            x,
            y + tamano * 0.68,
            x + tamano,
            y + tamano
        ),
        radius=10,
        fill=color_oro,
        outline=color_luz,
        width=3
    )

    # Joyas.
    for factor in (
        0.18,
        0.50,
        0.82
    ):

        cx = (
            x
            + tamano * factor
        )

        cy = (
            y
            + tamano * 0.82
        )

        draw.ellipse(
            (
                cx - 7,
                cy - 7,
                cx + 7,
                cy + 7
            ),
            fill=(255, 80, 80)
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
        fill=(35, 30, 55)
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
    # CORONA
    # ========================================================

    if (
        "corona" in texto
        or "crown" in texto
    ):

        dibujar_corona(
            draw,
            X_CONTENIDO + 360,
            25,
            130
        )

    # ========================================================
    # CORAZÓN
    # ========================================================

    elif (
        "corazon" in texto
        or "corazón" in texto
        or "heart" in texto
    ):

        dibujar_corazon(
            draw,
            ANCHO - 270,
            80,
            100
        )

    # ========================================================
    # MARIPOSA
    # ========================================================

    elif (
        "mariposa" in texto
        or "mariposa" in texto
        or "butterfly" in texto
    ):

        dibujar_mariposa(
            draw,
            ANCHO - 280,
            90,
            110
        )

    # ========================================================
    # BRILLO
    # ========================================================

    elif (
        "brillo" in texto
        or "glow" in texto
        or "luz" in texto
    ):

        draw.ellipse(
            (
                ANCHO - 420,
                40,
                ANCHO - 80,
                380
            ),
            outline=(255, 255, 255, 80),
            width=10
        )


# ============================================================
# INSIGNIA DE RANGO
# ============================================================

def dibujar_insignia_rango(
    draw,
    x,
    y,
    tamano=64,
    rango=None
):
    # Fondo circular.
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(255, 205, 55),
        outline=(255, 240, 150),
        width=3
    )

    # Estrella visible con fuente del sistema.
    fuente = cargar_fuente(
        42,
        True
    )

    draw.text(
        (
            x + tamano / 2,
            y + tamano / 2 - 2
        ),
        "★",
        font=fuente,
        anchor="mm",
        fill=(55, 45, 10)
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

    dibujar_insignia_rango(
        draw,
        X_CONTENIDO,
        Y_NIVEL - 32,
        64,
        rango
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
        fill=(255, 255, 255)
    )

    # ========================================================
    # XP
    # ========================================================

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
        fill=(235, 240, 250)
    )

    # ========================================================
    # BARRA
    # ========================================================

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
        fill=(10, 14, 23),
        outline=(145, 155, 175),
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
            fill=(70, 190, 255)
        )

    # ========================================================
    # PORCENTAJE
    # ========================================================

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
        fill=(255, 255, 255)
    )

    # ========================================================
    # RANGO
    # ========================================================

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
            fill=(255, 215, 90)
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

    color_detectado = detectar_color_nombre(
        equipados_lista
    )

    marco_detectado = detectar_marco(
        equipados_lista
    )

    fondo_detectado = detectar_fondo(
        equipados_lista
    )

    # Si se pasó explícitamente uno,
    # respetarlo salvo que haya cosmético equipado.
    color_nombre = (
        color_detectado
        if color_detectado
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
    # CREAR IMAGEN
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
        color_nombre,
        COLORES_NOMBRE["blanco"]
    )

    fuente_nombre = cargar_fuente(
        FONT_NOMBRE,
        True
    )

    # IMPORTANTE:
    # NO usamos .upper().
    # El nombre sale exactamente como fue escrito.
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
    # BANDERA + PAÍS
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
            fill=(235, 240, 250)
        )

    # ========================================================
    # ID INTERNO
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
            fill=(225, 230, 240)
        )

    # ========================================================
    # BOT ID
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
            fill=(255, 220, 110)
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
            fill=(255, 215, 70)
        )

    # ========================================================
    # ACCESORIOS / EFECTOS
    # ========================================================

    for accesorio in equipados_lista:

        texto = _producto_id(
            accesorio
        )

        if not texto:
            continue

        # No dibujar como accesorio los productos
        # que ya fueron utilizados como color/marco/fondo.
        if (
            "nombre_" in texto
            or "color_" in texto
            or "marco_" in texto
            or "frame_" in texto
            or "fondo_" in texto
            or "background" in texto
            or "estilo_fondo" in texto
        ):
            continue

        dibujar_efecto(
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

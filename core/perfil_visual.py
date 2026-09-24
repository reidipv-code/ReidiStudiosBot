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

FUENTE_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

FUENTE_NEGRITA = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


# ============================================================
# TAMAÑOS DE LETRA
# ============================================================

FONT_NOMBRE = 128
FONT_PAIS = 58

FONT_ID = 46
FONT_TOKENS = 48

FONT_NIVEL = 76
FONT_XP = 68
FONT_PORCENTAJE = 56
FONT_RANGO = 60


# ============================================================
# POSICIONES
# ============================================================

X_CONTENIDO = 540

Y_NOMBRE = 105
Y_PAIS = 220

Y_ID = 315
Y_BOT_ID = 375
Y_TELEGRAM_ID = 435
Y_TOKENS = 495

Y_NIVEL = 585
Y_XP = 665
Y_BARRA = 750
Y_PORCENTAJE = 830
Y_RANGO = 915


# ============================================================
# AVATAR
# ============================================================

TAM_AVATAR = 360


# ============================================================
# COLORES DE NOMBRE
# ============================================================

COLORES_NOMBRE = {
    "blanco": (255, 255, 255),
    "rojo": (255, 75, 75),
    "azul": (75, 165, 255),
    "verde": (75, 225, 120),
    "amarillo": (255, 220, 70),
    "morado": (190, 105, 255),
    "rosa": (255, 105, 190),
    "cian": (70, 225, 255),
    "naranja": (255, 145, 60),
    "esmeralda": (40, 235, 150),
}


# ============================================================
# MARCOS
# ============================================================

COLORES_MARCO = {
    "normal": (100, 110, 130),
    "oro": (255, 205, 60),
    "plata": (205, 215, 230),
    "diamante": (90, 220, 255),
    "rojo": (255, 70, 70),
    "morado": (185, 85, 255),
    "esmeralda": (40, 235, 150),
    "arcoiris": None,
}


# ============================================================
# FONDOS
# ============================================================

COLORES_FONDO = {
    "normal": (
        (18, 23, 38),
        (48, 60, 90),
    ),

    "azul": (
        (7, 20, 48),
        (25, 90, 165),
    ),

    "morado": (
        (28, 10, 55),
        (105, 35, 160),
    ),

    "rojo": (
        (48, 8, 18),
        (155, 30, 48),
    ),

    "verde": (
        (5, 35, 20),
        (25, 135, 75),
    ),

    "esmeralda": (
        (3, 35, 28),
        (15, 135, 100),
    ),

    "negro": (
        (5, 5, 8),
        (25, 25, 30),
    ),

    "dorado": (
        (45, 28, 5),
        (145, 95, 20),
    ),

    "cielo": (
        (20, 65, 105),
        (70, 155, 210),
    ),
}


# ============================================================
# ALIAS DE COSMÉTICOS
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
    "marco_arcoiris": "arcoiris",

    # Fondos
    "fondo_normal": "normal",
    "fondo_azul": "azul",
    "fondo_morado": "morado",
    "fondo_rojo": "rojo",
    "fondo_verde": "verde",
    "fondo_esmeralda": "esmeralda",
    "fondo_negro": "negro",
    "fondo_dorado": "dorado",
    "fondo_cielo": "cielo",
}


# ============================================================
# OBTENER ID REAL DEL COSMÉTICO
# ============================================================

def _producto_id(producto):

    if producto is None:
        return ""

    if isinstance(producto, dict):

        posibles = (
            "id",
            "producto_id",
            "item_id",
            "nombre",
            "item",
            "producto",
            "codigo",
            "slug",
            "tipo",
        )

        valores = []

        for clave in posibles:

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


# ============================================================
# NORMALIZAR EQUIPADOS
# ============================================================

def normalizar_equipados(equipados):

    if equipados is None:
        return []

    if isinstance(
        equipados,
        dict
    ):

        resultado = []

        for clave, valor in equipados.items():

            # Si el valor contiene productos.
            if isinstance(
                valor,
                (list, tuple, set)
            ):

                for elemento in valor:
                    resultado.append(
                        elemento
                    )

                continue

            # Si es un producto individual.
            if valor:

                if isinstance(
                    valor,
                    dict
                ):
                    resultado.append(
                        valor
                    )
                else:
                    resultado.append(
                        str(valor)
                    )

                continue

            # Si la clave parece ser el producto.
            resultado.append(
                str(clave)
            )

        return resultado

    if isinstance(
        equipados,
        (list, tuple, set)
    ):
        return list(
            equipados
        )

    return [equipados]


# ============================================================
# BUSCAR SI EXISTE UN COSMÉTICO
# ============================================================

def _tiene_producto(
    equipados,
    *busquedas
):

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        for busqueda in busquedas:

            if busqueda.lower() in texto:
                return True

    return False


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

    try:
        return ImageFont.load_default(
            size=32
        )

    except Exception:
        return ImageFont.load_default()


# ============================================================
# AJUSTAR TEXTO
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
# FONDO COSMÉTICO
# ============================================================

def detectar_fondo(
    equipados,
    fondo_recibido
):

    if fondo_recibido:
        fondo = str(
            fondo_recibido
        ).lower().strip()

        if fondo in COLORES_FONDO:
            return fondo

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        # Comprobación explícita.
        for nombre in COLORES_FONDO:

            if (
                f"fondo_{nombre}"
                in texto
            ):
                return nombre

            if (
                f"background_{nombre}"
                in texto
            ):
                return nombre

        # Algunos sistemas guardan solo
        # "azul", "morado", etc.
        if (
            "fondo" in texto
            or "background" in texto
        ):

            for nombre in COLORES_FONDO:

                if nombre in texto:
                    return nombre

    return "normal"


def dibujar_fondo(
    imagen,
    estilo="normal",
    frame=0,
    equipados=None
):

    equipados = normalizar_equipados(
        equipados
    )

    estilo_real = detectar_fondo(
        equipados,
        estilo
    )

    colores = COLORES_FONDO.get(
        estilo_real,
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

    # ========================================================
    # EFECTOS DE FONDO
    # ========================================================

    if _tiene_producto(
        equipados,
        "estrellas",
        "estrellas_fondo",
        "starfield"
    ):

        for i in range(100):

            x = (
                (i * 193)
                % ANCHO
            )

            y = (
                (i * 97)
                % ALTO
            )

            radio = (
                2 + (i % 3)
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + radio,
                    y + radio
                ),
                fill=(
                    255,
                    255,
                    255,
                    150
                )
            )

    if _tiene_producto(
        equipados,
        "particulas",
        "particles"
    ):

        for i in range(45):

            x = (
                (i * 313)
                % ANCHO
            )

            y = (
                (i * 151)
                % ALTO
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 8,
                    y + 8
                ),
                fill=(
                    255,
                    255,
                    255,
                    90
                )
            )

    # Brillos.
    draw.ellipse(
        (
            1200,
            -350,
            2200,
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

    # Bordes.
    for i in range(15):

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

        iniciales = (
            nombre[:2]
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
        (0, 0),
        mascara
    )

    return resultado


# ============================================================
# MARCO
# ============================================================

def detectar_marco(
    equipados,
    marco_recibido
):

    if marco_recibido:

        marco = str(
            marco_recibido
        ).lower().strip()

        if marco in COLORES_MARCO:
            return marco

    for producto in equipados:

        texto = _producto_id(
            producto
        )

        for nombre in COLORES_MARCO:

            if (
                f"marco_{nombre}"
                in texto
            ):
                return nombre

        if (
            "marco" in texto
            or "frame" in texto
        ):

            for nombre in COLORES_MARCO:

                if nombre in texto:
                    return nombre

    return "normal"


def dibujar_marco(
    draw,
    x,
    y,
    tamano,
    tipo="normal"
):

    tipo = tipo or "normal"

    # ========================================================
    # ARCOÍRIS
    # ========================================================

    if tipo == "arcoiris":

        colores = [
            (255, 60, 60),
            (255, 170, 50),
            (255, 230, 60),
            (60, 220, 100),
            (60, 180, 255),
            (150, 80, 255),
        ]

        grosor = 12

        for i, color in enumerate(
            colores
        ):

            margen = (
                8 + i * 6
            )

            draw.ellipse(
                (
                    x - margen,
                    y - margen,
                    x + tamano + margen,
                    y + tamano + margen
                ),
                outline=color,
                width=grosor
            )

        return

    color = COLORES_MARCO.get(
        tipo,
        COLORES_MARCO["normal"]
    )

    # Aura.
    draw.ellipse(
        (
            x - 20,
            y - 20,
            x + tamano + 20,
            y + tamano + 20
        ),
        outline=(
            color[0],
            color[1],
            color[2],
            90
        ),
        width=18
    )

    # Marco principal.
    draw.ellipse(
        (
            x - 10,
            y - 10,
            x + tamano + 10,
            y + tamano + 10
        ),
        outline=color,
        width=14
    )


# ============================================================
# AVATAR + MARCO
# ============================================================

def dibujar_avatar(
    imagen,
    avatar,
    x,
    y,
    tamano,
    marco="normal"
):

    avatar = recortar_circulo(
        avatar,
        tamano
    )

    if avatar is None:
        return

    # Avatar.
    imagen.alpha_composite(
        avatar,
        (
            x,
            y
        )
    )

    # Marco por encima del avatar.
    draw = ImageDraw.Draw(
        imagen
    )

    dibujar_marco(
        draw,
        x,
        y,
        tamano,
        marco
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
    ancho=82,
    alto=52
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
         

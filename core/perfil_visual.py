import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from core.paises import PAISES


# ============================================================
# CONFIGURACIÓN VISUAL
# ============================================================

ANCHO = 1920
ALTO = 1080

FPS = 10
FRAMES_ANIMADOS = 12

COLOR_BLANCO = (255, 255, 255, 255)
COLOR_PANEL = (10, 12, 25, 205)


# ============================================================
# COLORES DE NOMBRE
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
# MARCOS
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
    "fondo_noche": ((12, 15, 35), (35, 20, 65)),
    "fondo_nebulosa": ((15, 20, 60), (80, 30, 100)),
    "fondo_cyber": ((5, 25, 40), (10, 70, 80)),
    "fondo_rosa": ((55, 15, 45), (120, 35, 80)),
    "fondo_floresta": ((8, 35, 25), (25, 80, 55)),
    "fondo_abismo": ((3, 5, 12), (20, 25, 40)),
}


# ============================================================
# ALIASES DE PRODUCTOS
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
    "marco cosmico": "marco_cosmico",
    "rosa cristal": "marco_rosa_cristal",
    "corazones": "marco_corazones",
    "floral": "marco_floral",
    "mariposas": "marco_mariposas",
    "neón": "marco_neon",
    "neon": "marco_neon",
    "cyber": "marco_cyber",
    "samurái": "marco_samurai",
    "samurai": "marco_samurai",
    "dark": "marco_dark",
    "arcano": "marco_arcano",

    # IMPORTANTE:
    # "esmeralda" como accesorio ya NO se convierte
    # automáticamente en color de nombre.
    "marco esmeralda": "marco_esmeralda",

    "rubí": "marco_rubi",
    "rubi": "marco_rubi",
    "amatista": "marco_ametista",

    "fuego": "efecto_fuego",
    "electricidad": "efecto_electricidad",
    "escarcha": "efecto_escarcha",
    "chispas doradas": "efecto_chispas",
    "partículas cósmicas": "efecto_cosmico",
    "particulas cosmicas": "efecto_cosmico",
    "aura oscura": "efecto_aura",
    "corazones animados": "efecto_corazones",
    "pétalos": "efecto_petalo",
    "petalos": "efecto_petalo",
    "mariposas animadas": "efecto_mariposas",
    "burbujas": "efecto_burbujas",
    "lluvia de estrellas": "efecto_estrellas",
    "arcoíris": "efecto_arcoiris",
    "arcoiris": "efecto_arcoiris",

    "noche estrellada": "fondo_noche",
    "nebulosa": "fondo_nebulosa",
    "cyber city": "fondo_cyber",
    "sueño rosa": "fondo_rosa",
    "sueno rosa": "fondo_rosa",
    "floresta mística": "fondo_floresta",
    "floresta mistica": "fondo_floresta",
    "abismo": "fondo_abismo",

    "insignia corona": "insignia_corona",
    "insignia rayo": "insignia_rayo",
    "insignia corazón": "insignia_corazon",
    "insignia corazon": "insignia_corazon",
    "insignia estelar": "insignia_estelar",
    "insignia arcana": "insignia_arcana",
}


# ============================================================
# PRODUCTOS
# ============================================================

def _producto_id(producto):
    if producto is None:
        return None

    if isinstance(producto, str):
        valor = producto.strip()

        if not valor:
            return None

        return ALIASES_PRODUCTOS.get(
            valor.lower(),
            valor
        )

    if isinstance(producto, dict):
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
                    return ALIASES_PRODUCTOS.get(
                        valor.lower(),
                        valor
                    )

        nombre = str(
            producto.get("nombre", "")
        ).strip()

        tipo = str(
            producto.get("tipo", "")
        ).lower().strip()

        nombre_lower = nombre.lower()

        if tipo == "color":
            colores = (
                "esmeralda",
                "dorado",
                "rosa",
                "cian",
                "rojo",
                "violeta",
            )

            for color in colores:
                if color in nombre_lower:
                    return f"color_{color}"

        if tipo in (
            "accesorio",
            "marco",
            "efecto",
            "fondo",
            "insignia",
        ):
            prefijo = {
                "accesorio": "accesorio_",
                "marco": "marco_",
                "efecto": "efecto_",
                "fondo": "fondo_",
                "insignia": "insignia_",
            }[tipo]

            if nombre_lower.startswith(prefijo):
                return nombre_lower

            return ALIASES_PRODUCTOS.get(
                nombre_lower,
                nombre
            )

        if nombre_lower in ALIASES_PRODUCTOS:
            return ALIASES_PRODUCTOS[nombre_lower]

        return nombre

    valor = str(producto).strip()

    return valor or None


def normalizar_equipados(equipados):
    if not equipados:
        return {}

    resultado = {}

    if isinstance(equipados, dict):

        for clave, valor in equipados.items():

            clave = str(clave).lower().strip()

            producto_id = _producto_id(valor)

            if not producto_id:
                continue

            producto_lower = producto_id.lower()

            resultado[clave] = producto_id

            if producto_lower.startswith("color_"):
                resultado["color"] = producto_id

            elif producto_lower.startswith("marco_"):
                resultado["marco"] = producto_id

            elif producto_lower.startswith("fondo_"):
                resultado["fondo"] = producto_id

            elif producto_lower.startswith("efecto_"):
                resultado["efecto"] = producto_id

            elif producto_lower.startswith("insignia_"):
                resultado["insignia"] = producto_id

            elif (
                producto_lower.startswith("accesorio_")
                or "accesorio" in clave
            ):
                resultado["accesorio"] = producto_id

        return resultado

    if isinstance(
        equipados,
        (list, tuple, set)
    ):
        for producto in equipados:

            producto_id = _producto_id(producto)

            if not producto_id:
                continue

            producto_lower = producto_id.lower()

            if producto_lower.startswith("color_"):
                resultado.setdefault(
                    "color",
                    producto_id
                )

            elif producto_lower.startswith("marco_"):
                resultado.setdefault(
                    "marco",
                    producto_id
                )

            elif producto_lower.startswith("fondo_"):
                resultado.setdefault(
                    "fondo",
                    producto_id
                )

            elif producto_lower.startswith("efecto_"):
                resultado.setdefault(
                    "efecto",
                    producto_id
                )

            elif producto_lower.startswith("insignia_"):
                resultado.setdefault(
                    "insignia",
                    producto_id
                )

            elif producto_lower.startswith("accesorio_"):
                resultado.setdefault(
                    "accesorio",
                    producto_id
                )

    return resultado


# ============================================================
# FUENTES
# ============================================================

def cargar_fuente(tamano, negrita=False):
    rutas = []

    if negrita:
        rutas = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        rutas = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for ruta in rutas:
        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except OSError:
            pass

    return ImageFont.load_default()


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
        font=fuente
    )[2] <= max_ancho:
        return texto

    while len(texto) > 1:

        prueba = texto[:-1] + "..."

        ancho = draw.textbbox(
            (0, 0),
            prueba,
            font=fuente
        )[2]

        if ancho <= max_ancho:
            return prueba

        texto = texto[:-1]

    return "..."


# ============================================================
# FONDO
# ============================================================

def crear_gradiente(c1, c2):
    imagen = Image.new(
        "RGBA",
        (ANCHO, ALTO)
    )

    draw = ImageDraw.Draw(imagen)

    for y in range(ALTO):

        t = y / max(
            1,
            ALTO - 1
        )

        color = tuple(
            int(
                c1[i] * (1 - t)
                + c2[i] * t
            )
            for i in range(3)
        )

        draw.line(
            (0, y, ANCHO, y),
            fill=(
                *color,
                255
            )
        )

    return imagen


def dibujar_fondo(base, fondo):
    fondo = _producto_id(fondo)

    c1, c2 = COLORES_FONDO.get(
        fondo,
        COLORES_FONDO["fondo_noche"]
    )

    base.alpha_composite(
        crear_gradiente(c1, c2)
    )

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(capa)

    random.seed(100)

    for _ in range(170):

        x = random.randint(
            20,
            ANCHO - 20
        )

        y = random.randint(
            20,
            ALTO - 20
        )

        radio = random.randint(
            1,
            4
        )

        alpha = random.randint(
            25,
            90
        )

        draw.ellipse(
            (
                x - radio,
                y - radio,
                x + radio,
                y + radio
            ),
            fill=(
                255,
                255,
                255,
                alpha
            )
        )

    base.alpha_composite(capa)


# ============================================================
# AVATAR
# ============================================================

def redimensionar_avatar(
    imagen,
    tamano=400
):
    imagen = imagen.convert("RGBA")

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
            arriba + lado
        )
    )

    return imagen.resize(
        (tamano, tamano),
        Image.Resampling.LANCZOS
    )


def crear_avatar_iniciales(
    nombre,
    tamano=400
):
    imagen = Image.new(
        "RGBA",
        (tamano, tamano),
        (35, 40, 60, 255)
    )

    draw = ImageDraw.Draw(imagen)

    fuente = cargar_fuente(
        130,
        True
    )

    partes = str(
        nombre
    ).strip().split()

    iniciales = "".join(
        parte[0]
        for parte in partes[:2]
    ).upper() or "?"

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente
    )

    ancho = bbox[2] - bbox[0]
    alto = bbox[3] - bbox[1]

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
        fill=COLOR_BLANCO
    )

    return imagen


def recortar_circulo(imagen):
    imagen = imagen.convert("RGBA")

    mascara = Image.new(
        "L",
        imagen.size,
        0
    )

    draw = ImageDraw.Draw(mascara)

    draw.ellipse(
        (
            0,
            0,
            imagen.width - 1,
            imagen.height - 1
        ),
        fill=255
    )

    resultado = Image.new(
        "RGBA",
        imagen.size,
        (0, 0, 0, 0)
    )

    resultado.paste(
        imagen,
        (0, 0),
        mascara
    )

    return resultado


def dibujar_avatar(
    base,
    avatar,
    x=110,
    y=270,
    tamano=400
):
    if avatar is None:
        return

    avatar = redimensionar_avatar(
        avatar,
        tamano
    )

    avatar = recortar_circulo(
        avatar
    )

    sombra = Image.new(
        "RGBA",
        (
            tamano + 60,
            tamano + 60
        ),
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(
        sombra
    )

    shadow_draw.ellipse(
        (
            20,
            20,
            tamano + 40,
            tamano + 40
        ),
        fill=(
            0,
            0,
            0,
            180
        )
    )

    sombra = sombra.filter(
        ImageFilter.GaussianBlur(18)
    )

    base.alpha_composite(
        sombra,
        (
            x - 30,
            y - 30
        )
    )

    base.alpha_composite(
        avatar,
        (x, y)
    )


# ============================================================
# PAÍSES
# ============================================================

def _pais_codigo(pais):
    if not pais:
        return None

    if isinstance(pais, dict):

        for clave in (
            "codigo",
            "code",
            "pais",
            "id"
        ):
            if pais.get(clave):
                return _pais_codigo(
                    pais[clave]
                )

        if pais.get("nombre"):
            return _pais_codigo(
                pais["nombre"]
            )

        return None

    valor = str(
        pais
    ).strip().lower()

    if valor in PAISES:
        return valor

    # Permite recibir "🇨🇺 Cuba",
    # "Cuba", "cuba", etc.
    for codigo, info in PAISES.items():

        if not isinstance(
            info,
            dict
        ):
            continue

        nombre = str(
            info.get(
                "nombre",
                ""
            )
        ).strip().lower()

        if nombre and (
            valor == nombre
            or nombre in valor
        ):
            return codigo

    equivalencias = {
        "méxico": "mexico",
        "mexico": "mexico",
        "el salvador": "salvador",
        "salvador": "salvador",
        "españa": "espana",
        "espana": "espana",
        "república dominicana":
            "rep_dominicana",
        "republica dominicana":
            "rep_dominicana",
        "puerto rico":
            "puerto_rico",
        "costa rica":
            "costa_rica",
    }

    return equivalencias.get(
        valor,
        valor
    )


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

        radio_actual = (
            radio
            if i % 2 == 0
            else radio * 0.42
        )

        puntos.append(
            (
                cx
                + math.cos(angulo)
                * radio_actual,
                cy
                + math.sin(angulo)
                * radio_actual
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
    ancho=68,
    alto=44
):
    codigo = _pais_codigo(
        pais
    )

    if not codigo:
        return

    blanco = (
        255,
        255,
        255,
        255
    )

    rojo = (
        210,
        30,
        45,
        255
    )

    azul = (
        30,
        80,
        175,
        255
    )

    azul_claro = (
        70,
        170,
        235,
        255
    )

    amarillo = (
        255,
        210,
        50,
        255
    )

    verde = (
        30,
        150,
        80,
        255
    )

    # ========================================================
    # CUBA
    # ========================================================

    if codigo == "cuba":

        franja = alto / 5

        for i in range(5):

            color = (
                azul
                if i % 2 == 0
                else blanco
            )

            draw.rectangle(
                (
                    x,
                    y + i * franja,
                    x + ancho,
                    y + (i + 1) * franja
                ),
                fill=color
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
            fill=rojo
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto / 2,
            alto * 0.15,
            blanco
        )

    elif codigo == "mexico":

        tercio = ancho / 3

        draw.rectangle(
            (
                x,
                y,
                x + tercio,
                y + alto
            ),
            fill=verde
        )

        draw.rectangle(
            (
                x + tercio,
                y,
                x + tercio * 2,
                y + alto
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x + tercio * 2,
                y,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "salvador":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio
            ),
            fill=azul_claro
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto
            ),
            fill=azul_claro
        )

    elif codigo == "ecuador":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2
            ),
            fill=amarillo
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto * 0.75
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "argentina":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio
            ),
            fill=azul_claro
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto
            ),
            fill=azul_claro
        )

        _dibujar_estrella(
            draw,
            x + ancho / 2,
            y + alto / 2,
            5,
            amarillo
        )

    elif codigo == "colombia":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2
            ),
            fill=amarillo
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto * 0.75
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "peru":

        tercio = ancho / 3

        draw.rectangle(
            (
                x,
                y,
                x + tercio,
                y + alto
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x + tercio,
                y,
                x + tercio * 2,
                y + alto
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x + tercio * 2,
                y,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "chile":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho * 0.33,
                y + alto / 2
            ),
            fill=azul
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.165,
            y + alto * 0.25,
            5,
            blanco
        )

    elif codigo == "venezuela":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 3
            ),
            fill=amarillo
        )

        draw.rectangle(
            (
                x,
                y + alto / 3,
                x + ancho,
                y + alto * 2 / 3
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x,
                y + alto * 2 / 3,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "guatemala":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            fill=azul_claro
        )

        draw.rectangle(
            (
                x + ancho * 0.35,
                y,
                x + ancho * 0.65,
                y + alto
            ),
            fill=blanco
        )

    elif codigo == "honduras":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio
            ),
            fill=azul_claro
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto
            ),
            fill=azul_claro
        )

    elif codigo == "nicaragua":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto
            ),
            fill=azul
        )

    elif codigo == "costa_rica":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto * 0.25
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.25,
                x + ancho,
                y + alto * 0.38
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.38,
                x + ancho,
                y + alto * 0.75
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto * 0.875
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.875,
                x + ancho,
                y + alto
            ),
            fill=azul
        )

    elif codigo == "panama":

        draw.rectangle(
            (
                x,
                y,
                x + ancho / 2,
                y + alto / 2
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x + ancho / 2,
                y,
                x + ancho,
                y + alto / 2
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho / 2,
                y + alto
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x + ancho / 2,
                y + alto / 2,
                x + ancho,
                y + alto
            ),
            fill=blanco
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.25,
            y + alto * 0.25,
            5,
            azul
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.75,
            y + alto * 0.75,
            5,
            rojo
        )

    elif codigo == "bolivia":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 3
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y + alto / 3,
                x + ancho,
                y + alto * 2 / 3
            ),
            fill=amarillo
        )

        draw.rectangle(
            (
                x,
                y + alto * 2 / 3,
                x + ancho,
                y + alto
            ),
            fill=verde
        )

    elif codigo == "paraguay":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 3
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y + alto / 3,
                x + ancho,
                y + alto * 2 / 3
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y + alto * 2 / 3,
                x + ancho,
                y + alto
            ),
            fill=azul
        )

    elif codigo == "uruguay":

        franja = alto / 9

        for i in range(9):

            draw.rectangle(
                (
                    x,
                    y + i * franja,
                    x + ancho,
                    y + (i + 1) * franja
                ),
                fill=(
                    blanco
                    if i % 2 == 0
                    else azul_claro
                )
            )

        draw.rectangle(
            (
                x,
                y,
                x + ancho * 0.35,
                y + alto * 5 / 9
            ),
            fill=blanco
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto * 0.27,
            7,
            amarillo
        )

    elif codigo == "rep_dominicana":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            fill=blanco
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho / 2 - 4,
                y + alto / 2 - 4
            ),
            fill=azul
        )

        draw.rectangle(
            (
                x + ancho / 2 + 4,
                y + alto / 2 + 4,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    elif codigo == "puerto_rico":

        franja = alto / 5

        for i in range(5):

            draw.rectangle(
                (
                    x,
                    y + i * franja,
                    x + ancho,
                    y + (i + 1) * franja
                ),
                fill=(
                    rojo
                    if i % 2 == 0
                    else blanco
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
            fill=azul
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto / 2,
            6,
            blanco
        )

    elif codigo == "espana":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto * 0.25
            ),
            fill=rojo
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.25,
                x + ancho,
                y + alto * 0.75
            ),
            fill=amarillo
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto
            ),
            fill=rojo
        )

    else:
        # Bandera genérica para países no definidos
        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto
            ),
            fill=(80, 90, 110, 255)
        )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto
        ),
        radius=6,
        outline=(255, 255, 255, 190),
        width=2
    )


# ============================================================
# ICONOS
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=44
):
    centro_x = x + tamano / 2
    centro_y = y + tamano / 2

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(30, 30, 45, 240),
        outline=(255, 215, 80, 255),
        width=3
    )

    _dibujar_estrella(
        draw,
        centro_x,
        centro_y,
        tamano * 0.32,
        (255, 215, 80, 255)
    )


def dibujar_icono_token(
    draw,
    x,
    y,
    tamano=44
):
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(255, 205, 55, 255),
        outline=(255, 245, 150, 255),
        width=3
    )

    fuente = cargar_fuente(
        27,
        True
    )

    draw.text(
        (
            x + 14,
            y + 4
        ),
        "T",
        font=fuente,
        fill=(110, 70, 10, 255)
    )


# ============================================================
# MARCO
# ============================================================

def dibujar_marco(
    base,
    marco
):
    marco = _producto_id(
        marco
    )

    color = COLORES_MARCO.get(
        marco,
        (150, 90, 255)
    )

    draw = ImageDraw.Draw(base)

    margen = 18

    draw.rounded_rectangle(
        (
            margen,
            margen,
            ANCHO - margen,
            ALTO - margen
        ),
        radius=55,
        outline=(
            *color,
            255
        ),
        width=14
    )

    draw.rounded_rectangle(
        (
            margen + 24,
            margen + 24,
            ANCHO - margen - 24,
            ALTO - margen - 24
        ),
        radius=42,
        outline=(
            *color,
            85
        ),
        width=4
    )


# ============================================================
# FORMAS
# ============================================================

def _dibujar_corazon(
    draw,
    cx,
    cy,
    tamano,
    color
):
    puntos = []

    for i in range(101):

        t = (
            2 * math.pi * i / 100
        )

        px = (
            16 * math.sin(t) ** 3
        )

        py = -(
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        puntos.append(
            (
                cx + px * tamano / 32,
                cy + py * tamano / 32
            )
        )

    draw.polygon(
        puntos,
        fill=color
    )


def _dibujar_mariposa(
    draw,
    x,
    y,
    tamano
):
    color1 = (
        190,
        100,
        255,
        180
    )

    color2 = (
        255,
        120,
        210,
        180
    )

    draw.ellipse(
        (
            x - tamano / 2,
            y - tamano / 3,
            x,
            y + tamano / 3
        ),
        fill=color1
    )

    draw.ellipse(
        (
            x,
            y - tamano / 3,
            x + tamano / 2,
            y + tamano / 3
        ),
        fill=color2
    )

    draw.rounded_rectangle(
        (
            x - 4,
            y - tamano / 4,
            x + 4,
            y + tamano / 4
        ),
        radius=4,
        fill=(40, 40, 60, 230)
    )


def _dibujar_corona(
    draw,
    x=None,
    y=None,
    tamano=80
):
    if x is None:
        x = ANCHO - 390

    if y is None:
        y = 60

    puntos = [
        (x, y + tamano),
        (x + 10, y + 12),
        (
            x + tamano / 2,
            y + 52
        ),
        (
            x + tamano - 10,
            y + 12
        ),
        (
            x + tamano,
            y + tamano
        )
    ]

    draw.polygon(
        puntos,
        fill=(255, 215, 60, 240)
    )

    draw.rounded_rectangle(
        (
            x,
            y + tamano - 17,
            x + tamano,
            y + tamano + 7
        ),
        radius=6,
        fill=(255, 190, 40, 240),
        outline=(255, 240, 150, 255),
        width=3
    )


# ============================================================
# EFECTOS
# ============================================================

def _efecto_fuego(draw, frame):
    random.seed(1000 + frame)

    for _ in range(70):

        x = random.randint(
            40,
            ANCHO - 40
        )

        y = ALTO - random.randint(
            30,
            230
        )

        r = random.randint(
            3,
            10
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
                random.randint(80, 190),
                30,
                random.randint(70, 170)
            )
        )


def _efecto_electricidad(draw, frame):
    random.seed(2000 + frame)

    for _ in range(14):

        x = random.randint(
            80,
            ANCHO - 80
        )

        puntos = [
            (x, 40)
        ]

        y = 40

        while y < ALTO - 40:

            y += random.randint(
                60,
                120
            )

            x += random.randint(
                -45,
                45
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
                170
            ),
            width=3
        )


def _efecto_escarcha(draw, frame):
    random.seed(3000 + frame)

    for _ in range(80):

        x = random.randint(
            40,
            ANCHO - 40
        )

        y = random.randint(
            40,
            ALTO - 40
        )

        r = random.randint(
            3,
            8
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            fill=(
                180,
                240,
                255,
                120
            )
        )


def _efecto_chispas(draw, frame):
    random.seed(4000 + frame)

    for _ in range(90):

        x = random.randint(
            40,
            ANCHO - 40
        )

        y = random.randint(
            40,
            ALTO - 40
        )

        r = random.randint(
            2,
            5
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
                220,
                100,
                180
            )
        )


def _efecto_cosmico(draw, frame):
    random.seed(5000)

    for i in range(100):

        angulo = (
            i * 37
            + frame * 8
        ) % 360

        radio = (
            150
            + (i * 34) % 650
        )

        cx = (
            ANCHO / 2
            + math.cos(
                math.radians(angulo)
            ) * radio
        )

        cy = (
            ALTO / 2
            + math.sin(
                math.radians(angulo)
            ) * radio
        )

        r = 2 + i % 4

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r
            ),
            fill=(
                190,
                150,
                255,
                140
            )
        )


def _efecto_aura(draw, frame):
    alpha = (
        70
        + int(
            40 * math.sin(
                frame / 2
            )
        )
    )

    draw.ellipse(
        (
            220,
            130,
            ANCHO - 220,
            ALTO - 130
        ),
        outline=(
            100,
            200,
            255,
            alpha
        ),
        width=20
    )


def _efecto_corazones(draw, frame):
    for i in range(15):

        x = (
            100
            + (
                i * 127
                + frame * 7
            ) % (ANCHO - 200)
        )

        y = (
            100
            + (
                i * 91
                + frame * 10
            ) % (ALTO - 200)
        )

        _dibujar_corazon(
            draw,
            x,
            y,
            20,
            (255, 80, 130, 140)
        )


def _efecto_petalo(draw, frame):
    random.seed(
        7000 + frame
    )

    for _ in range(45):

        x = random.randint(
            40,
            ANCHO - 40
        )

        y = random.randint(
            40,
            ALTO - 40
        )

        draw.ellipse(
            (
                x - 7,
                y - 13,
                x + 7,
                y + 13
            ),
            fill=(
                255,
                150,
                190,
                120
            )
        )


def _efecto_mariposas(draw, frame):
    for i in range(5):

        x = 180 + i * 370

        y = (
            120
            + (
                frame * 14
                + i * 120
            ) % 780
        )

        _dibujar_mariposa(
            draw,
            x,
            y,
            65
        )


def _efecto_burbujas(draw, frame):
    for i in range(30):

        x = (
            60
            + (
                i * 146
                + frame * 8
            ) % (ANCHO - 120)
        )

        y = (
            ALTO
            - (
                i * 94
                + frame * 16
            ) % (ALTO - 80)
        )

        r = 6 + i % 12

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            outline=(
                130,
                220,
                255,
                110
            ),
            width=3
        )


def _efecto_estrellas(draw, frame):
    random.seed(9000)

    for i in range(55):

        x = random.randint(
            40,
            ANCHO - 40
        )

        y = random.randint(
            40,
            ALTO - 40
        )

        r = 3 + (
            (i + frame) % 5
        )

        draw.line(
            (
                x - r,
                y,
                x + r,
                y
            ),
            fill=(
                255,
                255,
                220,
                180
            ),
            width=2
        )

        draw.line(
            (
                x,
                y - r,
                x,
                y + r
            ),
            fill=(
                255,
                255,
                220,
                180
            ),
            width=2
        )


def _efecto_arcoiris(draw, frame):
    colores = [
        (255, 70, 70, 120),
        (255, 170, 50, 120),
        (255, 240, 70, 120),
        (70, 230, 120, 120),
        (70, 180, 255, 120),
        (150, 90, 255, 120),
    ]

    for i, color in enumerate(
        colores
    ):

        margen = i * 13

        draw.rounded_rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen
            ),
            radius=60,
            outline=color,
            width=7
        )


def dibujar_efecto(
    base,
    efecto,
    frame=0
):
    efecto = _producto_id(
        efecto
    ) or ""

    funciones = {
        "efecto_fuego":
            _efecto_fuego,

        "efecto_electricidad":
            _efecto_electricidad,

        "efecto_escarcha":
            _efecto_escarcha,

        "efecto_chispas":
            _efecto_chispas,

        "efecto_cosmico":
            _efecto_cosmico,

        "efecto_aura":
            _efecto_aura,

        "efecto_corazones":
            _efecto_corazones,

        "efecto_petalo":
            _efecto_petalo,

        "efecto_mariposas":
            _efecto_mariposas,

        "efecto_burbujas":
            _efecto_burbujas,

        "efecto_estrellas":
            _efecto_estrellas,

        "efecto_arcoiris":
            _efecto_arcoiris,
    }

    funcion = funciones.get(
        efecto
    )

    if not funcion:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        capa
    )

    funcion(
        draw,
        frame
    )

    base.alpha_composite(
        capa
    )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_accesorio(
    base,
    accesorio,
    frame
):
    accesorio = _producto_id(
        accesorio
    )

    if not accesorio:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        capa
    )

    nombre = accesorio.lower()

    if (
        "corona" in nombre
        or nombre == "accesorio_corona"
    ):
        # CORREGIDO:
        # _dibujar_corona NO recibe frame.
        _dibujar_corona(
            draw,
            x=ANCHO - 390,
            y=65,
            tamano=80
        )

    elif (
        "neon" in nombre
        or "neón" in nombre
    ):
        for i in range(5):

            y = (
                200
                + i * 150
                + int(
                    math.sin(
                        frame / 2 + i
                    ) * 25
                )
            )

            draw.line(
                (
                    80,
                    y,
                    ANCHO - 80,
                    y
                ),
                fill=(
                    40,
                    255,
                    220,
                    100
                ),
                width=3
            )

    elif (
        "esmeralda" in nombre
    ):
        # Accesorio esmeralda:
        # NO cambia el color del nombre.
        draw.ellipse(
            (
                ANCHO - 390,
                55,
                ANCHO - 310,
                135
            ),
            fill=(
                35,
                220,
                135,
                180
            ),
            outline=(
                160,
                255,
                210,
                255
            ),
            width=4
        )

        _dibujar_estrella(
            draw,
            ANCHO - 350,
            95,
            25,
            (
                220,
                255,
                235,
                255
            )
        )

    base.alpha_composite(
        capa
    )


# ============================================================
# INSIGNIAS
# ============================================================

def dibujar_insignia(
    base,
    insignia
):
    insignia = _producto_id(
        insignia
    )

    if not insignia:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        capa
    )

    tamano = 48

    x = 1710
    y = 850

    colores = {
        "insignia_corona":
            (255, 210, 70, 255),

        "insignia_rayo":
            (255, 220, 70, 255),

        "insignia_corazon":
            (255, 80, 130, 255),

        "insignia_estelar":
            (130, 210, 255, 255),

        "insignia_arcana":
            (190, 110, 255, 255),
    }

    color = colores.get(
        insignia,
        (255, 210, 70, 255)
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(
            20,
            20,
            35,
            220
        ),
        outline=color,
        width=3
    )

    cx = (
        x + tamano / 2
    )

    cy = (
        y + tamano / 2
    )

    if insignia == "insignia_corazon":

        _dibujar_corazon(
            draw,
            cx,
            cy,
            22,
            color
        )

    elif insignia == "insignia_rayo":

        draw.polygon(
            [
                (cx + 6, cy - 18),
                (cx - 9, cy + 1),
                (cx, cy + 1),
                (cx - 6, cy + 18),
                (cx + 12, cy - 4),
                (cx + 2, cy - 4),
            ],
            fill=color
        )

    elif insignia in (
        "insignia_estelar",
        "insignia_arcana"
    ):

        _dibujar_estrella(
            draw,
            cx,
            cy,
            17,
            color
        )

    elif insignia == "insignia_corona":

        _dibujar_corona(
            draw,
            cx - 16,
            cy - 16,
            32
        )

    base.alpha_composite(
        capa
    )


# ============================================================
# GENERAR PERFIL
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
    equipados = normalizar_equipados(
        equipados
    )

    marco = _producto_id(
        equipados.get("marco")
    )

    fondo = _producto_id(
        equipados.get("fondo")
    )

    efecto = _producto_id(
        equipados.get("efecto")
    )

    accesorio = _producto_id(
        equipados.get("accesorio")
    )

    insignia = _producto_id(
        equipados.get("insignia")
    )

    color_nombre = _producto_id(
        equipados.get("color")
        or equipados.get("color_nombre")
    )

    color_texto = COLORES_NOMBRE.get(
        color_nombre,
        (255, 255, 255)
    )

    if avatar is None:
        avatar_img = crear_avatar_iniciales(
            nombre,
            400
        )
    else:
        avatar_img = avatar

    animado = bool(
        efecto
    )

    cantidad_frames = (
        FRAMES_ANIMADOS
        if animado
        else 1
    )

    frames = []

    for frame in range(
        cantidad_frames
    ):

        imagen = Image.new(
            "RGBA",
            (
                ANCHO,
                ALTO
            ),
            (0, 0, 0, 255)
        )

        # Fondo
        dibujar_fondo(
            imagen,
            fondo
        )

        # Efectos detrás del contenido
        dibujar_efecto(
            imagen,
            efecto,
            frame
        )

        # Accesorios
        _dibujar_accesorio(
            imagen,
            accesorio,
            frame
        )

        # Avatar
        dibujar_avatar(
            imagen,
            avatar_img,
            120,
            270,
            400
        )

        draw = ImageDraw.Draw(
            imagen
        )

        # ====================================================
        # PANEL PRINCIPAL
        # ====================================================

        draw.rounded_rectangle(
            (
                560,
                120,
                1780,
                940
            ),
            radius=40,
            fill=(
                8,
                10,
                23,
                185
            ),
            outline=(
                255,
                255,
                255,
                45
            ),
            width=2
        )

        # ====================================================
        # FUENTES
        # ====================================================

        fuente_nombre = cargar_fuente(
            96,
            True
        )

        fuente_nivel = cargar_fuente(
            58,
            True
        )

        fuente_info = cargar_fuente(
            48,
            False
        )

        fuente_pais = cargar_fuente(
            44,
            False
        )

        fuente_pequena = cargar_fuente(
            30,
            False
        )

        fuente_footer = cargar_fuente(
            26,
            True
        )

        # ====================================================
        # NOMBRE
        # ====================================================

        nombre_mostrado = texto_ajustado(
            draw,
            nombre,
            fuente_nombre,
            1120
        )

        # sombra
        draw.text(
            (
                625,
                175
            ),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                0,
                0,
                0,
                180
            )
        )

        # nombre real
        draw.text(
            (
                615,
                165
            ),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                *color_texto,
                255
            )
        )

        # ====================================================
        # NIVEL
        # ====================================================

        draw.text(
            (
                620,
                315
            ),
            f"Nivel {nivel}",
            font=fuente_nivel,
            fill=(
                255,
                255,
                255,
                245
            )
        )

        # ====================================================
        # RANGO
        # ====================================================

        dibujar_icono_rango(
            draw,
            620,
            405,
            48
        )

        draw.text(
            (
                690,
                400
            ),
            f"Rango: {rango}",
            font=fuente_info,
            fill=(
                235,
                235,
                245,
                245
            )
        )

        # ====================================================
        # XP
        # ====================================================

        draw.text(
            (
                620,
                500
            ),
            f"XP: {xp_total} / {xp_siguiente}",
            font=fuente_info,
            fill=(
                225,
                225,
                235,
                245
            )
        )

        # ====================================================
        # TOKENS
        # ====================================================

        dibujar_icono_token(
            draw,
            620,
            600,
            48
        )

        draw.text(
            (
                690,
                595
            ),
            f"Tokens: {tokens}",
            font=fuente_info,
            fill=(
                255,
                215,
                80,
                250
            )
        )

        # ====================================================
        # PAÍS
        # ====================================================

        codigo_pais = _pais_codigo(
            pais
        )

        if codigo_pais:

            info_pais = PAISES.get(
                codigo_pais,
                {}
            )

            if isinstance(
                info_pais,
                dict
            ):
                nombre_pais = info_pais.get(
                    "nombre",
                    str(pais)
                )
            else:
                nombre_pais = str(
                    pais
                )

            dibujar_bandera(
                draw,
                codigo_pais,
                620,
                700,
                72,
                46
            )

            draw.text(
                (
                    715,
                    695
                ),
                nombre_pais,
                font=fuente_pais,
                fill=(
                    220,
                    230,
                    240,
                    245
                )
            )

        # ====================================================
        # BARRA DE XP
        # ====================================================

        try:
            xp_actual = max(
                0,
                float(xp_total)
            )

            xp_meta = max(
                1,
                float(xp_siguiente)
            )

            progreso = min(
                1.0,
                xp_actual / xp_meta
            )

        except (
            TypeError,
            ValueError,
            ZeroDivisionError
        ):
            progreso = 0.0

        barra_x = 620
        barra_y = 815
        barra_w = 1060
        barra_h = 42

        draw.rounded_rectangle(
            (
                barra_x,
                barra_y,
                barra_x + barra_w,
                barra_y + barra_h
            ),
            radius=21,
            fill=(
                25,
                25,
                35,
                230
            ),
            outline=(
                255,
                255,
                255,
                70
            ),
            width=3
        )

        if progreso > 0:

            ancho_progreso = max(
                barra_h,
                int(
                    barra_w * progreso
                )
            )

            draw.rounded_rectangle(
                (
                    barra_x,
                    barra_y,
                    barra_x + ancho_progreso,
                    barra_y + barra_h
                ),
                radius=21,
                fill=(
                    70,
                    200,
                    255,
                    240
                )
            )

        # ====================================================
        # INSIGNIA
        # ====================================================

        if insignia:
            dibujar_insignia(
                imagen,
                insignia
            )

        # ====================================================
        # MARCO
        # ====================================================

        if marco:
            dibujar_marco(
                imagen,
                marco
            )

        # ====================================================
        # PIE
        # ====================================================

        draw.text(
            (
                120,
                ALTO - 65
            ),
            "Reidi Studios",
            font=fuente_footer,
            fill=(
                255,
                255,
                255,
                140
            )
        )

        draw.text(
            (
                1430,
                ALTO - 65
            ),
            "PERFIL",
            font=fuente_footer,
            fill=(
                255,
                255,
                255,
                100
            )
        )

        frames.append(
            imagen.convert("RGB")
        )

    # ========================================================
    # EXPORTACIÓN
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
            optimize=False
        )

        mime = "image/gif"

    else:

        # PNG LOSSLESS.
        # No JPEG.
        # Sin pérdida de calidad.
        frames[0].save(
            salida,
            format="PNG",
            compress_level=1,
            optimize=False
        )

        mime = "image/png"

    return (
        salida.getvalue(),
        mime,
        animado
    )

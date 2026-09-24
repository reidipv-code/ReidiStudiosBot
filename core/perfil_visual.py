import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from core.paises import PAISES


# ============================================================
# CONFIGURACIÓN HD
# ============================================================

ANCHO = 1800
ALTO = 1120

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

COLORES_FONDO = {
    "fondo_noche": ((12, 15, 35), (35, 20, 65)),
    "fondo_nebulosa": ((15, 20, 60), (80, 30, 100)),
    "fondo_cyber": ((5, 25, 40), (10, 70, 80)),
    "fondo_rosa": ((55, 15, 45), (120, 35, 80)),
    "fondo_floresta": ((8, 35, 25), (25, 80, 55)),
    "fondo_abismo": ((3, 5, 12), (20, 25, 40)),
}


# ============================================================
# ALIAS DE PRODUCTOS
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
            valor,
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
                        valor,
                    )

        nombre = producto.get("nombre")

        if nombre is not None:
            nombre = str(nombre).strip()
            nombre_lower = nombre.lower()

            if nombre_lower in ALIASES_PRODUCTOS:
                return ALIASES_PRODUCTOS[nombre_lower]

            tipo = str(
                producto.get("tipo", "")
            ).lower()

            if tipo == "color":

                for color in (
                    "esmeralda",
                    "dorado",
                    "rosa",
                    "cian",
                    "rojo",
                    "violeta",
                ):
                    if color in nombre_lower:
                        return f"color_{color}"

            return nombre

    valor = str(producto).strip()

    return valor or None


def normalizar_equipados(equipados):

    if not equipados:
        return {}

    resultado = {}

    if isinstance(equipados, dict):

        for clave, valor in equipados.items():

            producto_id = _producto_id(valor)

            if not producto_id:
                continue

            clave = str(clave).lower().strip()

            resultado[clave] = producto_id

            producto_lower = producto_id.lower()

            if producto_lower.startswith("color_"):
                resultado.setdefault("color", producto_id)

            elif producto_lower.startswith("marco_"):
                resultado.setdefault("marco", producto_id)

            elif producto_lower.startswith("fondo_"):
                resultado.setdefault("fondo", producto_id)

            elif producto_lower.startswith("efecto_"):
                resultado.setdefault("efecto", producto_id)

            elif producto_lower.startswith("insignia_"):
                resultado.setdefault("insignia", producto_id)

        return resultado

    if isinstance(equipados, (list, tuple, set)):

        for producto in equipados:

            producto_id = _producto_id(producto)

            if not producto_id:
                continue

            producto_lower = producto_id.lower()

            if producto_lower.startswith("color_"):
                resultado.setdefault("color", producto_id)

            elif producto_lower.startswith("marco_"):
                resultado.setdefault("marco", producto_id)

            elif producto_lower.startswith("fondo_"):
                resultado.setdefault("fondo", producto_id)

            elif producto_lower.startswith("efecto_"):
                resultado.setdefault("efecto", producto_id)

            elif producto_lower.startswith("insignia_"):
                resultado.setdefault("insignia", producto_id)

    return resultado


# ============================================================
# FUENTES
# ============================================================

def cargar_fuente(tamano, negrita=False):

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
                tamano,
            )
        except OSError:
            pass

    return ImageFont.load_default()


def texto_ajustado(draw, texto, fuente, max_ancho):

    texto = str(texto)

    if draw.textbbox(
        (0, 0),
        texto,
        font=fuente,
    )[2] <= max_ancho:
        return texto

    while texto:

        prueba = texto + "..."

        if draw.textbbox(
            (0, 0),
            prueba,
            font=fuente,
        )[2] <= max_ancho:
            return prueba

        texto = texto[:-1]

    return "..."


# ============================================================
# FONDO
# ============================================================

def crear_gradiente(c1, c2):

    imagen = Image.new(
        "RGB",
        (ANCHO, ALTO),
    )

    pixeles = imagen.load()

    for y in range(ALTO):

        t = y / max(
            1,
            ALTO - 1,
        )

        color = tuple(
            int(
                c1[i] * (1 - t)
                + c2[i] * t
            )
            for i in range(3)
        )

        for x in range(ANCHO):
            pixeles[x, y] = color

    return imagen.convert("RGBA")


def dibujar_fondo(base, fondo):

    fondo = _producto_id(fondo)

    if fondo in COLORES_FONDO:

        c1, c2 = COLORES_FONDO[fondo]

        base.alpha_composite(
            crear_gradiente(c1, c2)
        )

    else:

        base.alpha_composite(
            crear_gradiente(
                (12, 15, 35),
                (35, 20, 65),
            )
        )

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    random.seed(100)

    for _ in range(140):

        x = random.randint(0, ANCHO)
        y = random.randint(0, ALTO)
        r = random.choice([2, 2, 3, 4, 5])

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
                random.randint(25, 100),
            ),
        )

    base.alpha_composite(capa)


# ============================================================
# AVATAR
# ============================================================

def redimensionar_avatar(imagen, tamano=380):

    imagen = imagen.convert("RGBA")

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
        (tamano, tamano),
        Image.Resampling.LANCZOS,
    )


def crear_avatar_iniciales(nombre, tamano=380):

    imagen = Image.new(
        "RGBA",
        (tamano, tamano),
        (45, 45, 65, 255),
    )

    draw = ImageDraw.Draw(imagen)

    fuente = cargar_fuente(
        max(64, tamano // 3),
        True,
    )

    partes = str(nombre).strip().split()

    iniciales = "".join(
        parte[0]
        for parte in partes[:2]
    ).upper() or "?"

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente,
    )

    ancho = bbox[2] - bbox[0]
    alto = bbox[3] - bbox[1]

    x = (tamano - ancho) // 2
    y = (tamano - alto) // 2 - bbox[1]

    draw.text(
        (x, y),
        iniciales,
        font=fuente,
        fill=(255, 255, 255, 255),
    )

    return imagen


def recortar_circulo(imagen):

    imagen = imagen.convert("RGBA")

    mascara = Image.new(
        "L",
        imagen.size,
        0,
    )

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

    resultado = Image.new(
        "RGBA",
        imagen.size,
        (0, 0, 0, 0),
    )

    resultado.paste(
        imagen,
        (0, 0),
        mascara,
    )

    return resultado


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
        (0, 0, 0, 0),
    )

    sombra_draw = ImageDraw.Draw(sombra)

    sombra_draw.ellipse(
        (
            10,
            10,
            tamano + 30,
            tamano + 30,
        ),
        fill=(0, 0, 0, 150),
    )

    sombra = sombra.filter(
        ImageFilter.GaussianBlur(16)
    )

    base.alpha_composite(
        sombra,
        (x - 20, y - 20),
    )

    base.alpha_composite(
        avatar,
        (x, y),
    )


# ============================================================
# BANDERAS
# ============================================================

def _pais_codigo(pais):

    if not pais:
        return None

    valor = str(pais).strip().lower()

    # Si recibimos directamente el código.
    if valor in PAISES:
        return valor

    # Si recibimos el nombre completo.
    for codigo, info in PAISES.items():

        nombre = str(
            info.get("nombre", "")
        ).strip().lower()

        if valor == nombre:
            return codigo

    # Casos comunes.
    equivalencias = {
        "el salvador": "salvador",
        "salvador": "salvador",
        "méxico": "mexico",
        "mexico": "mexico",
        "españa": "espana",
        "españa": "espana",
        "república dominicana": "rep_dominicana",
        "republica dominicana": "rep_dominicana",
        "puerto rico": "puerto_rico",
        "costa rica": "costa_rica",
    }

    return equivalencias.get(valor, valor)


def _dibujar_estrella(
    draw,
    cx,
    cy,
    radio,
    color,
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
                cy + math.sin(angulo) * r,
            )
        )

    draw.polygon(
        puntos,
        fill=color,
    )


def dibujar_bandera(
    draw,
    pais,
    x,
    y,
    ancho=100,
    alto=64,
):

    codigo = _pais_codigo(pais)

    if not codigo:
        return

    # --------------------------------------------------------
    # COLORES
    # --------------------------------------------------------

    blanco = (255, 255, 255, 255)
    negro = (20, 20, 20, 255)
    rojo = (210, 30, 45, 255)
    azul = (20, 75, 170, 255)
    azul_claro = (70, 170, 235, 255)
    amarillo = (255, 210, 50, 255)
    verde = (30, 150, 80, 255)
    naranja = (240, 120, 35, 255)

    # --------------------------------------------------------
    # BASE
    # --------------------------------------------------------

    draw.rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto,
        ),
        fill=blanco,
    )

    # --------------------------------------------------------
    # CUBA
    # --------------------------------------------------------

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
                    y + (i + 1) * franja,
                ),
                fill=color,
            )

        draw.polygon(
            [
                (x, y),
                (
                    x + ancho * 0.48,
                    y + alto / 2,
                ),
                (x, y + alto),
            ],
            fill=rojo,
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.17,
            y + alto / 2,
            alto * 0.14,
            blanco,
        )

    # --------------------------------------------------------
    # EL SALVADOR
    # --------------------------------------------------------

    elif codigo == "salvador":

        franja = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + franja,
            ),
            fill=azul_claro,
        )

        draw.rectangle(
            (
                x,
                y + franja,
                x + ancho,
                y + franja * 2,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x,
                y + franja * 2,
                x + ancho,
                y + alto,
            ),
            fill=azul_claro,
        )

        # Escudo simplificado.
        cx = x + ancho / 2
        cy = y + alto / 2

        draw.ellipse(
            (
                cx - 9,
                cy - 9,
                cx + 9,
                cy + 9,
            ),
            fill=amarillo,
        )

        _dibujar_estrella(
            draw,
            cx,
            cy,
            7,
            verde,
        )

    # --------------------------------------------------------
    # MÉXICO
    # --------------------------------------------------------

    elif codigo == "mexico":

        tercio = ancho / 3

        draw.rectangle(
            (
                x,
                y,
                x + tercio,
                y + alto,
            ),
            fill=verde,
        )

        draw.rectangle(
            (
                x + tercio,
                y,
                x + tercio * 2,
                y + alto,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x + tercio * 2,
                y,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

        draw.ellipse(
            (
                x + ancho / 2 - 7,
                y + alto / 2 - 7,
                x + ancho / 2 + 7,
                y + alto / 2 + 7,
            ),
            fill=verde,
        )

    # --------------------------------------------------------
    # ECUADOR
    # --------------------------------------------------------

    elif codigo == "ecuador":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto * 0.75,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

    # --------------------------------------------------------
    # ARGENTINA
    # --------------------------------------------------------

    elif codigo == "argentina":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio,
            ),
            fill=azul_claro,
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto,
            ),
            fill=azul_claro,
        )

        _dibujar_estrella(
            draw,
            x + ancho / 2,
            y + alto / 2,
            8,
            amarillo,
        )

    # --------------------------------------------------------
    # COLOMBIA
    # --------------------------------------------------------

    elif codigo == "colombia":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto * 0.75,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

    # --------------------------------------------------------
    # PERÚ
    # --------------------------------------------------------

    elif codigo == "peru":

        tercio = ancho / 3

        draw.rectangle(
            (
                x,
                y,
                x + tercio,
                y + alto,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x + tercio,
                y,
                x + tercio * 2,
                y + alto,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x + tercio * 2,
                y,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

    # --------------------------------------------------------
    # CHILE
    # --------------------------------------------------------

    elif codigo == "chile":

        draw.rectangle(
            (
                x,
                y + alto / 2,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto / 2,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho * 0.36,
                y + alto / 2,
            ),
            fill=azul,
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.18,
            y + alto * 0.25,
            7,
            blanco,
        )

    # --------------------------------------------------------
    # VENEZUELA
    # --------------------------------------------------------

    elif codigo == "venezuela":

        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

        for i in range(7):

            angulo = (
                math.pi * 0.15
                + i * math.pi * 0.7 / 6
            )

            cx = (
                x + ancho / 2
                + math.cos(angulo) * 24
            )

            cy = (
                y + alto / 2
                + math.sin(angulo) * 10
            )

            _dibujar_estrella(
                draw,
                cx,
                cy,
                3,
                blanco,
            )

    # --------------------------------------------------------
    # CENTROAMÉRICA / OTROS
    # --------------------------------------------------------

    elif codigo in (
        "guatemala",
        "nicaragua",
        "honduras",
        "costa_rica",
        "panama",
    ):

        # Bandera simplificada basada en sus
        # franjas principales.
        if codigo == "guatemala":

            tercio = ancho / 3

            draw.rectangle(
                (
                    x,
                    y,
                    x + tercio,
                    y + alto,
                ),
                fill=azul_claro,
            )

            draw.rectangle(
                (
                    x + tercio,
                    y,
                    x + tercio * 2,
                    y + alto,
                ),
                fill=blanco,
            )

            draw.rectangle(
                (
                    x + tercio * 2,
                    y,
                    x + ancho,
                    y + alto,
                ),
                fill=azul_claro,
            )

        elif codigo == "honduras":

            franja = alto / 3

            for i, color in enumerate(
                (
                    azul_claro,
                    blanco,
                    azul_claro,
                )
            ):

                draw.rectangle(
                    (
                        x,
                        y + i * franja,
                        x + ancho,
                        y + (i + 1) * franja,
                    ),
                    fill=color,
                )

            _dibujar_estrella(
                draw,
                x + ancho / 2,
                y + alto / 2,
                4,
                azul,
            )

        elif codigo == "nicaragua":

            franja = alto / 3

            draw.rectangle(
                (
                    x,
                    y,
                    x + ancho,
                    y + franja,
                ),
                fill=azul,
            )

            draw.rectangle(
                (
                    x,
                    y + franja,
                    x + ancho,
                    y + franja * 2,
                ),
                fill=blanco,
            )

            draw.rectangle(
                (
                    x,
                    y + franja * 2,
                    x + ancho,
                    y + alto,
                ),
                fill=azul,
            )

        elif codigo == "costa_rica":

            alturas = [
                1,
                1,
                2,
                1,
                1,
            ]

            colores = [
                azul,
                blanco,
                rojo,
                blanco,
                azul,
            ]

            total = sum(alturas)
            actual = y

            for alto_rel, color in zip(
                alturas,
                colores,
            ):

                h = (
                    alto
                    * alto_rel
                    / total
                )

                draw.rectangle(
                    (
                        x,
                        actual,
                        x + ancho,
                        actual + h,
                    ),
                    fill=color,
                )

                actual += h

        elif codigo == "panama":

            draw.rectangle(
                (
                    x,
                    y,
                    x + ancho / 2,
                    y + alto / 2,
                ),
                fill=blanco,
            )

            draw.rectangle(
                (
                    x + ancho / 2,
                    y,
                    x + ancho,
                    y + alto / 2,
                ),
                fill=rojo,
            )

            draw.rectangle(
                (
                    x,
                    y + alto / 2,
                    x + ancho / 2,
                    y + alto,
                ),
                fill=azul,
            )

            draw.rectangle(
                (
                    x + ancho / 2,
                    y + alto / 2,
                    x + ancho,
                    y + alto,
                ),
                fill=blanco,
            )

            _dibujar_estrella(
                draw,
                x + ancho * 0.25,
                y + alto * 0.25,
                7,
                azul,
            )

            _dibujar_estrella(
                draw,
                x + ancho * 0.75,
                y + alto * 0.75,
                7,
                rojo,
            )

    # --------------------------------------------------------
    # RESTO: FRANJAS GENERALES
    # --------------------------------------------------------

    elif codigo in (
        "bolivia",
        "paraguay",
        "uruguay",
    ):

        if codigo == "bolivia":

            franja = alto / 3

            colores = [
                rojo,
                amarillo,
                verde,
            ]

            for i, color in enumerate(
                colores
            ):

                draw.rectangle(
                    (
                        x,
                        y + i * franja,
                        x + ancho,
                        y + (i + 1) * franja,
                    ),
                    fill=color,
                )

        elif codigo == "paraguay":

            franja = alto / 3

            colores = [
                rojo,
                blanco,
                rojo,
            ]

            for i, color in enumerate(
                colores
            ):

                draw.rectangle(
                    (
                        x,
                        y + i * franja,
                        x + ancho,
                        y + (i + 1) * franja,
                    ),
                    fill=color,
                )

        elif codigo == "uruguay":

            franja = alto / 9

            for i in range(9):

                color = (
                    blanco
                    if i % 2 == 0
                    else azul_claro
                )

                draw.rectangle(
                    (
                        x,
                        y + i * franja,
                        x + ancho,
                        y + (i + 1) * franja,
                    ),
                    fill=color,
                )

    elif codigo == "argentina":
        pass

    elif codigo == "espana":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto * 0.25,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.25,
                x + ancho,
                y + alto * 0.75,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + alto * 0.75,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

    elif codigo == "rep_dominicana":

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x,
                y,
                x + ancho / 2 - 4,
                y + alto / 2 - 4,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x + ancho / 2 + 4,
                y,
                x + ancho,
                y + alto / 2 - 4,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x,
                y + alto / 2 + 4,
                x + ancho / 2 - 4,
                y + alto,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x + ancho / 2 + 4,
                y + alto / 2 + 4,
                x + ancho,
                y + alto,
            ),
            fill=azul,
        )

    else:

        # País desconocido: bandera genérica.
        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto,
            ),
            fill=azul_claro,
        )

        draw.ellipse(
            (
                x + ancho / 2 - 10,
                y + alto / 2 - 10,
                x + ancho / 2 + 10,
                y + alto / 2 + 10,
            ),
            fill=blanco,
        )

    # Borde común.
    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto,
        ),
        radius=5,
        outline=(255, 255, 255, 170),
        width=3,
    )


# ============================================================
# ICONO DE RANGO
# MISMO TAMAÑO VISUAL QUE LAS LETRAS
# ============================================================

def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=80,
):

    cx = x + tamano / 2
    cy = y + tamano / 2

    radio = tamano * 0.38

    draw.ellipse(
        (
            cx - radio - 4,
            cy - radio - 4,
            cx + radio + 4,
            cy + radio + 4,
        ),
        fill=(0, 0, 0, 130),
    )

    draw.ellipse(
        (
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
        ),
        fill=(255, 196, 45, 255),
        outline=(255, 235, 130, 255),
        width=4,
    )

    _dibujar_estrella(
        draw,
        cx,
        cy,
        radio * 0.65,
        (255, 255, 255, 255),
    )


# ============================================================
# TOKEN
# ============================================================

def dibujar_icono_token(
    draw,
    x,
    y,
    tamano=48,
):

    cx = x + tamano / 2
    cy = y + tamano / 2

    radio = tamano / 2

    draw.ellipse(
        (
            cx - radio,
            cy - radio,
            cx + radio,
            cy + radio,
        ),
        fill=(255, 204, 50, 255),
        outline=(255, 240, 150, 255),
        width=3,
    )

    fuente = cargar_fuente(
        int(tamano * 0.42),
        True,
    )

    bbox = draw.textbbox(
        (0, 0),
        "$",
        font=fuente,
    )

    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    draw.text(
        (
            cx - tw / 2,
            cy - th / 2 - bbox[1],
        ),
        "$",
        font=fuente,
        fill=(90, 55, 0, 255),
    )


# ============================================================
# MARCO
# ============================================================

def dibujar_marco(base, marco):

    marco = _producto_id(marco)

    color = COLORES_MARCO.get(
        marco,
        (100, 100, 120),
    )

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    draw.rounded_rectangle(
        (
            24,
            24,
            ANCHO - 24,
            ALTO - 24,
        ),
        radius=60,
        outline=(*color, 255),
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
        outline=(*color, 90),
        width=6,
    )

    base.alpha_composite(capa)


# ============================================================
# CORAZONES
# ============================================================

def _dibujar_corazon(
    draw,
    cx,
    cy,
    tamano,
    color,
):

    r = tamano * 0.25

    draw.ellipse(
        (
            cx - r * 2,
            cy - r,
            cx,
            cy + r,
        ),
        fill=color,
    )

    draw.ellipse(
        (
            cx,
            cy - r,
            cx + r * 2,
            cy + r,
        ),
        fill=color,
    )

    draw.polygon(
        [
            (
                cx - r * 2,
                cy,
            ),
            (
                cx,
                cy + tamano * 0.65,
            ),
            (
                cx + r * 2,
                cy,
            ),
        ],
        fill=color,
    )


def _efecto_corazones(
    draw,
    frame,
):

    random.seed(6000 + frame)

    for _ in range(18):

        x = random.randint(
            80,
            ANCHO - 80,
        )

        y = random.randint(
            80,
            ALTO - 80,
        )

        _dibujar_corazon(
            draw,
            x,
            y,
            80,
            (
                255,
                80,
                130,
                random.randint(120, 210),
            ),
        )


# ============================================================
# MARIPOSAS
# ============================================================

def _dibujar_mariposa(
    draw,
    x,
    y,
    tamano,
):

    color1 = (
        190,
        120,
        255,
        190,
    )

    color2 = (
        100,
        200,
        255,
        190,
    )

    draw.ellipse(
        (
            x - tamano / 2,
            y - tamano / 3,
            x,
            y + tamano / 3,
        ),
        fill=color1,
    )

    draw.ellipse(
        (
            x,
            y - tamano / 3,
            x + tamano / 2,
            y + tamano / 3,
        ),
        fill=color2,
    )

    draw.rounded_rectangle(
        (
            x - 5,
            y - tamano / 4,
            x + 5,
            y + tamano / 4,
        ),
        radius=5,
        fill=(40, 40, 60, 230),
    )


def _efecto_mariposas(
    draw,
    frame,
):

    for i in range(6):

        x = 180 + i * 280

        y = (
            130
            + (
                frame * 14
                + i * 120
            ) % 780
        )

        _dibujar_mariposa(
            draw,
            x,
            y,
            80,
        )


# ============================================================
# CORONA
# ============================================================

def _dibujar_corona(
    draw,
    x=None,
    y=None,
    tamano=80,
):

    if x is None:
        x = ANCHO - 390

    if y is None:
        y = 65

    puntos = [
        (x, y + tamano),
        (x + 12, y + 12),
        (
            x + tamano / 2,
            y + 55,
        ),
        (
            x + tamano - 12,
            y + 12,
        ),
        (
            x + tamano,
            y + tamano,
        ),
    ]

    draw.polygon(
        puntos,
        fill=(255, 215, 60, 240),
    )

    draw.rounded_rectangle(
        (
            x,
            y + tamano - 18,
            x + tamano,
            y + tamano + 8,
        ),
        radius=7,
        fill=(255, 190, 40, 240),
        outline=(255, 240, 150, 255),
        width=3,
    )


# ============================================================
# EFECTOS RESTANTES
# ============================================================

def _efecto_fuego(draw, frame):

    random.seed(1000 + frame)

    for _ in range(90):

        x = random.randint(50, ANCHO - 50)
        y = ALTO - random.randint(40, 240)
        r = random.randint(4, 14)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(
                255,
                random.randint(80, 190),
                30,
                random.randint(80, 180),
            ),
        )


def _efecto_electricidad(draw, frame):

    random.seed(2000 + frame)

    for _ in range(20):

        x = random.randint(
            80,
            ANCHO - 80,
        )

        puntos = [(x, 40)]
        y = 40

        while y < ALTO - 40:

            y += random.randint(50, 110)
            x += random.randint(-50, 50)

            puntos.append(
                (x, y)
            )

        draw.line(
            puntos,
            fill=(100, 220, 255, 180),
            width=4,
        )


def _efecto_escarcha(draw, frame):

    random.seed(3000 + frame)

    for _ in range(110):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        r = random.randint(4, 10)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(180, 240, 255, 130),
        )


def _efecto_chispas(draw, frame):

    random.seed(4000 + frame)

    for _ in range(120):

        x = random.randint(
            40,
            ANCHO - 40,
        )

        y = random.randint(
            40,
            ALTO - 40,
        )

        r = random.randint(2, 7)

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=(255, 220, 100, 180),
        )


def _efecto_cosmico(draw, frame):

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
                math.radians(angulo)
            ) * radio
        )

        cy = (
            ALTO // 2
            + math.sin(
                math.radians(angulo)
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
            fill=(190, 150, 255, 140),
        )


def _efecto_aura(draw, frame):

    alpha = (
        70
        + int(
            40 * math.sin(frame / 2)
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


def _efecto_petalo(draw, frame):

    random.seed(7000 + frame)

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
            fill=(255, 150, 190, 130),
        )


def _efecto_burbujas(draw, frame):

    for i in range(40):

        x = (
            60
            + (
                i * 146
                + frame * 8
            )
            % (ANCHO - 120)
        )

        y = (
            ALTO
            - (
                i * 94
                + frame * 16
            )
            % (ALTO - 80)
        )

        r = 8 + i % 14

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            outline=(130, 220, 255, 120),
            width=4,
        )


def _efecto_estrellas(draw, frame):

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
            fill=(255, 255, 220, 180),
            width=2,
        )

        draw.line(
            (
                x,
                y - r,
                x,
                y + r,
            ),
            fill=(255, 255, 220, 180),
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


def dibujar_efecto(
    base,
    efecto,
    frame=0,
):

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    efecto = _producto_id(
        efecto
    ) or ""

    funciones = {
        "efecto_fuego": _efecto_fuego,
        "efecto_electricidad": _efecto_electricidad,
        "efecto_escarcha": _efecto_escarcha,
        "efecto_chispas": _efecto_chispas,
        "efecto_cosmico": _efecto_cosmico,
        "efecto_aura": _efecto_aura,
        "efecto_corazones": _efecto_corazones,
        "efecto_petalo": _efecto_petalo,
        "efecto_mariposas": _efecto_mariposas,
        "efecto_burbujas": _efecto_burbujas,
        "efecto_estrellas": _efecto_estrellas,
        "efecto_arcoiris": _efecto_arcoiris,
    }

    funcion = funciones.get(efecto)

    if funcion:
        funcion(draw, frame)

    base.alpha_composite(capa)


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
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    nombre = accesorio.lower()

    if "corona" in nombre:

        _dibujar_corona(
            draw,
            frame=frame,
        )

    elif (
        "neon" in nombre
        or "neón" in nombre
    ):

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
                fill=(40, 255, 220, 120),
                width=4,
            )

    base.alpha_composite(capa)


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
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    x = 1510
    y = 790
    tamano = 80

    colores = {
        "insignia_corona": (
            255,
            210,
            70,
            255,
        ),
        "insignia_rayo": (
            255,
            220,
            70,
            255,
        ),
        "insignia_corazon": (
            255,
            80,
            130,
            255,
        ),
        "insignia_estelar": (
            130,
            210,
            255,
            255,
        ),
        "insignia_arcana": (
            190,
            110,
            255,
            255,
        ),
    }

    color = colores.get(
        insignia,
        (255, 210, 70, 255),
    )

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano,
        ),
        fill=(20, 20, 35, 220),
        outline=color,
        width=6,
    )

    cx = x + tamano / 2
    cy = y + tamano / 2

    if insignia == "insignia_corazon":

        _dibujar_corazon(
            draw,
            cx,
            cy,
            40,
            color,
        )

    elif insignia == "insignia_rayo":

        draw.polygon(
            [
                (cx + 10, cy - 28),
                (cx - 16, cy + 4),
                (cx, cy + 4),
                (cx - 10, cy + 28),
                (cx + 22, cy - 8),
                (cx + 5, cy - 8),
            ],
            fill=color,
        )

    elif insignia in (
        "insignia_estelar",
        "insignia_arcana",
    ):

        _dibujar_estrella(
            draw,
            cx,
            cy,
            25,
            color,
        )

    elif insignia == "insignia_corona":

        _dibujar_corona(
            draw,
            cx - 25,
            cy - 25,
            50,
        )

    base.alpha_composite(capa)


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
        (255, 255, 255),
    )

    if avatar is None:
        avatar_img = crear_avatar_iniciales(
            nombre,
            380,
        )
    else:
        avatar_img = avatar

    animado = bool(efecto)

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
            (ANCHO, ALTO),
            (0, 0, 0, 255),
        )

        dibujar_fondo(
            imagen,
            fondo,
        )

        dibujar_efecto(
            imagen,
            efecto,
            frame,
        )

        _dibujar_accesorio(
            imagen,
            accesorio,
            frame,
        )

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

        # Letras grandes.
        fuente_nombre = cargar_fuente(
            84,
            True,
        )

        fuente_info = cargar_fuente(
            50,
            False,
        )

        fuente_pequena = cargar_fuente(
            40,
            False,
        )

        fuente_footer = cargar_fuente(
            30,
            True,
        )

        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        nombre_mostrado = texto_ajustado(
            draw,
            nombre,
            fuente_nombre,
            1120,
        )

        draw.text(
            (
                605,
                195,
            ),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(0, 0, 0, 170),
        )

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
            (600, 320),
            f"Nivel {nivel}",
            font=fuente_info,
            fill=(255, 255, 255, 240),
        )

        # ----------------------------------------------------
        # RANGO
        # ----------------------------------------------------

        dibujar_icono_rango(
            draw,
            600,
            395,
            80,
        )

        draw.text(
            (700, 412),
            f"Rango: {rango}",
            font=fuente_info,
            fill=(235, 235, 245, 240),
        )

        # ----------------------------------------------------
        # XP
        # ----------------------------------------------------

        draw.text(
            (600, 500),
            f"XP: {xp_total} / {xp_siguiente}",
            font=fuente_info,
            fill=(225, 225, 235, 240),
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
            (675, 592),
            f"Tokens: {tokens}",
            font=fuente_info,
            fill=(255, 215, 80, 245),
        )

        # ----------------------------------------------------
        # PAÍS
        # ----------------------------------------------------

        if pais:

            codigo_pais = _pais_codigo(
                pais
            )

            nombre_pais = (
                PAISES.get(
                    codigo_pais,
                    {},
                ).get(
                    "nombre",
                    str(pais),
                )
            )

            dibujar_bandera(
                draw,
                codigo_pais,
                600,
                700,
                100,
                64,
            )

            draw.text(
                (730, 704),
                nombre_pais,
                font=fuente_pequena,
                fill=(210, 225, 235, 235),
            )

        # ----------------------------------------------------
        # BARRA XP
        # ----------------------------------------------------

        try:

            xp_actual = max(
                0,
                float(xp_total),
            )

            xp_meta = max(
                1,
                float(xp_siguiente),
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

        draw.rounded_rectangle(
            (
                barra_x,
                barra_y,
                barra_x + barra_w,
                barra_y + barra_h,
            ),
            radius=22,
            fill=(25, 25, 35, 220),
            outline=(255, 255, 255, 80),
            width=4,
        )

        if progreso > 0:

            ancho_progreso = max(
                44,
                int(
                    barra_w * progreso
                ),
            )

            draw.rounded_rectangle(
                (
                    barra_x,
                    barra_y,
                    barra_x + ancho_progreso,
                    barra_y + barra_h,
                ),
                radius=22,
                fill=(70, 200, 255, 235),
            )

        # ----------------------------------------------------
        # INSIGNIA
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
            fill=(255, 255, 255, 150),
        )

        frames.append(
            imagen.convert("RGB")
        )

    # ========================================================
    # EXPORTAR
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

Ahora sí: si "pais="salvador"", la tarjeta dibuja la bandera de El Salvador; si "pais="cuba"", dibuja la de Cuba. No depende de que Telegram pueda renderizar emojis.

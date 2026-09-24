import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from core.paises import PAISES


ANCHO = 1800
ALTO = 1120

FPS = 10
FRAMES_ANIMADOS = 12


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
    "esmeralda": "marco_esmeralda",
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

            elif (
                "accesorio" in clave
                or producto_lower.startswith("accesorio_")
            ):
                resultado.setdefault("accesorio", producto_id)

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

            elif producto_lower.startswith("accesorio_"):
                resultado.setdefault("accesorio", producto_id)

    return resultado


def cargar_fuente(tamano, negrita=False):
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
            return ImageFont.truetype(ruta, tamano)
        except OSError:
            continue

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


def crear_gradiente(c1, c2):
    imagen = Image.new(
        "RGB",
        (ANCHO, ALTO),
    )

    pixeles = imagen.load()

    for y in range(ALTO):
        t = y / max(1, ALTO - 1)

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
    else:
        c1, c2 = COLORES_FONDO["fondo_noche"]

    base.alpha_composite(
        crear_gradiente(c1, c2)
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
        r = random.choice((2, 3, 4, 5))

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

    avatar = recortar_circulo(avatar)

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


def _pais_codigo(pais):
    if not pais:
        return None

    if isinstance(pais, dict):
        for clave in (
            "codigo",
            "code",
            "pais",
            "id",
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

    valor = str(pais).strip().lower()

    if valor in PAISES:
        return valor

    for codigo, info in PAISES.items():
        if isinstance(info, dict):
            nombre = str(
                info.get("nombre", "")
            ).strip().lower()

            if valor == nombre:
                return codigo

    equivalencias = {
        "el salvador": "salvador",
        "salvador": "salvador",
        "méxico": "mexico",
        "mexico": "mexico",
        "españa": "espana",
        "espana": "espana",
        "república dominicana": "rep_dominicana",
        "republica dominicana": "rep_dominicana",
        "puerto rico": "puerto_rico",
        "costa rica": "costa_rica",
    }

    return equivalencias.get(
        valor,
        valor,
    )


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
                * radio_actual,
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
    ancho=58,
    alto=38,
):
    codigo = _pais_codigo(pais)

    if not codigo:
        return

    blanco = (255, 255, 255, 255)
    rojo = (210, 30, 45, 255)
    azul = (20, 75, 170, 255)
    azul_claro = (70, 170, 235, 255)
    amarillo = (255, 210, 50, 255)
    verde = (30, 150, 80, 255)

    # Cuba
    if codigo == "cuba":
        franja = alto / 5

        for i in range(5):
            color = azul if i % 2 == 0 else blanco

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

    # El Salvador
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

        draw.ellipse(
            (
                x + ancho / 2 - 5,
                y + alto / 2 - 5,
                x + ancho / 2 + 5,
                y + alto / 2 + 5,
            ),
            fill=amarillo,
        )

    # México
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
                x + ancho / 2 - 4,
                y + alto / 2 - 4,
                x + ancho / 2 + 4,
                y + alto / 2 + 4,
            ),
            fill=verde,
        )

    # Ecuador
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

    # Argentina
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
            4,
            amarillo,
        )

    # Colombia
    elif codigo == "colombia":
        mitad = alto / 2

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + mitad,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + mitad,
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

    # Perú
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

    # Chile
    elif codigo == "chile":
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
                x + ancho * 0.33,
                y + alto / 2,
            ),
            fill=azul,
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.165,
            y + alto * 0.25,
            4,
            blanco,
        )

    # Venezuela
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
            angulo = math.radians(
                210 + i * 20
            )

            cx = (
                x + ancho * 0.50
                + math.cos(angulo) * 15
            )

            cy = (
                y + alto * 0.50
                + math.sin(angulo) * 7
            )

            _dibujar_estrella(
                draw,
                cx,
                cy,
                2.5,
                blanco,
            )

    # Guatemala
    elif codigo == "guatemala":
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

    # Nicaragua
    elif codigo == "nicaragua":
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

    # Honduras
    elif codigo == "honduras":
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

    # Costa Rica
    elif codigo == "costa_rica":
        partes = [
            azul,
            blanco,
            rojo,
            blanco,
            azul,
        ]

        altura = alto / 5

        for i, color in enumerate(partes):
            draw.rectangle(
                (
                    x,
                    y + i * altura,
                    x + ancho,
                    y + (i + 1) * altura,
                ),
                fill=color,
            )

    # Panamá
    elif codigo == "panama":
        mitad_w = ancho / 2
        mitad_h = alto / 2

        draw.rectangle(
            (
                x,
                y,
                x + mitad_w,
                y + mitad_h,
            ),
            fill=blanco,
        )

        draw.rectangle(
            (
                x + mitad_w,
                y,
                x + ancho,
                y + mitad_h,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x,
                y + mitad_h,
                x + mitad_w,
                y + alto,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x + mitad_w,
                y + mitad_h,
                x + ancho,
                y + alto,
            ),
            fill=blanco,
        )

    # Bolivia
    elif codigo == "bolivia":
        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio,
            ),
            fill=rojo,
        )

        draw.rectangle(
            (
                x,
                y + tercio,
                x + ancho,
                y + tercio * 2,
            ),
            fill=amarillo,
        )

        draw.rectangle(
            (
                x,
                y + tercio * 2,
                x + ancho,
                y + alto,
            ),
            fill=verde,
        )

    # Paraguay
    elif codigo == "paraguay":
        tercio = alto / 3

        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + tercio,
            ),
            fill=rojo,
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
            fill=azul,
        )

    # Uruguay
    elif codigo == "uruguay":
        franja = alto / 9

        for i in range(9):
            draw.rectangle(
                (
                    x,
                    y + i * franja,
                    x + ancho,
                    y + (i + 1) * franja,
                ),
                fill=blanco if i % 2 == 0 else azul,
            )

        draw.rectangle(
            (
                x,
                y,
                x + ancho * 0.38,
                y + alto * 0.55,
            ),
            fill=blanco,
        )

        _dibujar_estrella(
            draw,
            x + ancho * 0.19,
            y + alto * 0.27,
            5,
            amarillo,
        )

    # España
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

    # República Dominicana
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
                x + ancho * 0.5,
                y + alto * 0.45,
            ),
            fill=azul,
        )

        draw.rectangle(
            (
                x + ancho * 0.5,
                y + alto * 0.55,
                x + ancho,
                y + alto,
            ),
            fill=rojo,
        )

    else:
        draw.rectangle(
            (
                x,
                y,
                x + ancho,
                y + alto,
            ),
            fill=(70, 70, 90, 255),
        )

        draw.text(
            (
                x + 5,
                y + 3,
            ),
            codigo[:3].upper(),
            font=cargar_fuente(
                max(12, int(alto * 0.34)),
                True,
            ),
            fill=blanco,
        )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + ancho,
            y + alto,
        ),
        radius=5,
        outline=(255, 255, 255, 170),
        width=2,
    )


def dibujar_icono_rango(
    draw,
    x,
    y,
    tamano=52,
):
    centro_x = x + tamano / 2
    centro_y = y + tamano / 2

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano,
        ),
        fill=(35, 35, 50, 245),
        outline=(255, 215, 80, 255),
        width=3,
    )

    _dibujar_estrella(
        draw,
        centro_x,
        centro_y,
        tamano * 0.34,
        (255, 215, 80, 255),
    )


def dibujar_icono_token(
    draw,
    x,
    y,
    tamano=50,
):
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano,
        ),
        fill=(255, 205, 55, 255),
        outline=(255, 245, 150, 255),
        width=3,
    )

    fuente = cargar_fuente(
        int(tamano * 0.62),
        True,
    )

    bbox = draw.textbbox(
        (0, 0),
        "T",
        font=fuente,
    )

    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    draw.text(
        (
            x + (tamano - w) / 2,
            y + (tamano - h) / 2 - bbox[1],
        ),
        "T",
        font=fuente,
        fill=(120, 75, 10, 255),
    )


def dibujar_marco(
    base,
    marco,
):
    marco = _producto_id(marco)

    color = COLORES_MARCO.get(
        marco,
        (150, 90, 255),
    )

    draw = ImageDraw.Draw(base)

    margen = 18

    draw.rounded_rectangle(
        (
            margen,
            margen,
            ANCHO - margen,
            ALTO - margen,
        ),
        radius=60,
        outline=(
            *color,
            255,
        ),
        width=18,
    )

    draw.rounded_rectangle(
        (
            margen + 25,
            margen + 25,
            ANCHO - margen - 25,
            ALTO - margen - 25,
        ),
        radius=45,
        outline=(
            *color,
            90,
        ),
        width=5,
    )


def _dibujar_corazon(
    draw,
    cx,
    cy,
    tamano,
    color,
):
    puntos = []

    for i in range(101):
        t = (
            2 * math.pi * i / 100
        )

        x = (
            16 * math.sin(t) ** 3
        )

        y = -(
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        puntos.append(
            (
                cx + x * tamano / 32,
                cy + y * tamano / 32,
            )
        )

    draw.polygon(
        puntos,
        fill=color,
    )


def _dibujar_mariposa(
    draw,
    x,
    y,
    tamano,
):
    color1 = (
        190,
        100,
        255,
        190,
    )

    color2 = (
        255,
        120,
        210,
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
        x = random.randint(80, ANCHO - 80)
        puntos = [(x, 40)]
        y = 40

        while y < ALTO - 40:
            y += random.randint(50, 110)
            x += random.randint(-50, 50)
            puntos.append((x, y))

        draw.line(
            puntos,
            fill=(100, 220, 255, 180),
            width=4,
        )


def _efecto_escarcha(draw, frame):
    random.seed(3000 + frame)

    for _ in range(110):
        x = random.randint(40, ANCHO - 40)
        y = random.randint(40, ALTO - 40)
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
        x = random.randint(40, ANCHO - 40)
        y = random.randint(40, ALTO - 40)
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


def _efecto_corazones(draw, frame):
    for i in range(18):
        x = (
            100
            + (
                i * 113
                + frame * 7
            ) % (ANCHO - 200)
        )

        y = (
            120
            + (
                i * 91
                + frame * 10
            ) % (ALTO - 200)
        )

        _dibujar_corazon(
            draw,
            x,
            y,
            22,
            (255, 80, 130, 150),
        )


def _efecto_petalo(draw, frame):
    random.seed(7000 + frame)

    for _ in range(60):
        x = random.randint(40, ANCHO - 40)
        y = random.randint(40, ALTO - 40)

        draw.ellipse(
            (
                x - 8,
                y - 16,
                x + 8,
                y + 16,
            ),
            fill=(255, 150, 190, 130),
        )


def _efecto_mariposas(draw, frame):
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


def _efecto_burbujas(draw, frame):
    for i in range(40):
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
        x = random.randint(40, ANCHO - 40)
        y = random.randint(40, ALTO - 40)
        r = 4 + ((i + frame) % 6)

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

    efecto = _producto_id(efecto) or ""

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


def _dibujar_accesorio(
    base,
    accesorio,
    frame,
):
    accesorio = _producto_id(accesorio)

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

    elif "neon" in nombre or "neón" in nombre:
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


def dibujar_insignia(
    base,
    insignia,
):
    insignia = _producto_id(insignia)

    if not insignia:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    tamano = 56
    x = 1640
    y = 770

    colores = {
        "insignia_corona": (255, 210, 70, 255),
        "insignia_rayo": (255, 220, 70, 255),
        "insignia_corazon": (255, 80, 130, 255),
        "insignia_estelar": (130, 210, 255, 255),
        "insignia_arcana": (190, 110, 255, 255),
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
        width=4,
    )

    cx = x + tamano / 2
    cy = y + tamano / 2

    if insignia == "insignia_corazon":
        _dibujar_corazon(
            draw,
            cx,
            cy,
            25,
            color,
        )

    elif insignia == "insignia_rayo":
        draw.polygon(
            [
                (cx + 7, cy - 20),
                (cx - 10, cy + 2),
                (cx, cy + 2),
                (cx - 7, cy + 20),
                (cx + 14, cy - 5),
                (cx + 3, cy - 5),
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
            19,
            color,
        )

    elif insignia == "insignia_corona":
        _dibujar_corona(
            draw,
            cx - 18,
            cy - 18,
            36,
        )

    base.alpha_composite(capa)


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

    for frame in range(cantidad_frames):
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

        draw = ImageDraw.Draw(imagen)

        fuente_nombre = cargar_fuente(
            84,
            True,
        )

        fuente_info = cargar_fuente(
            50,
            False,
        )

        fuente_pequena = cargar_fuente(
            50,
            False,
        )

        fuente_footer = cargar_fuente(
            30,
            True,
        )

        nombre_mostrado = texto_ajustado(
            draw,
            nombre,
            fuente_nombre,
            1120,
        )

        draw.text(
            (605, 195),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(0, 0, 0, 170),
        )

        draw.text(
            (600, 190),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                *color_texto,
                255,
            ),
        )

        draw.text(
            (600, 320),
            f"Nivel {nivel}",
            font=fuente_info,
            fill=(255, 255, 255, 240),
        )

        dibujar_icono_rango(
            draw,
            600,
            395,
            50,
        )

        draw.text(
            (665, 397),
            f"Rango: {rango}",
            font=fuente_info,
            fill=(235, 235, 245, 240),
        )

        draw.text(
            (600, 500),
            f"XP: {xp_total} / {xp_siguiente}",
            font=fuente_info,
            fill=(225, 225, 235, 240),
        )

        dibujar_icono_token(
            draw,
            600,
            592,
            50,
        )

        draw.text(
            (665, 590),
            f"Tokens: {tokens}",
            font=fuente_info,
            fill=(255, 215, 80, 245),
        )

        if pais:
            codigo_pais = _pais_codigo(pais)

            info_pais = PAISES.get(
                codigo_pais,
                {},
            )

            if isinstance(info_pais, dict):
                nombre_pais = info_pais.get(
                    "nombre",
                    str(pais),
                )
            else:
                nombre_pais = str(pais)

            dibujar_bandera(
                draw,
                codigo_pais,
                600,
                700,
                58,
                38,
            )

            draw.text(
                (675, 694),
                nombre_pais,
                font=fuente_pequena,
                fill=(210, 225, 235, 235),
            )

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

        if insignia:
            dibujar_insignia(
                imagen,
                insignia,
            )

        if marco:
            dibujar_marco(
                imagen,
                marco,
            )

        draw.text(
            (110, ALTO - 90),
            "Reidi Studios",
            font=fuente_footer,
            fill=(255, 255, 255, 150),
        )

        frames.append(
            imagen.convert("RGB")
        )

    salida = io.BytesIO()

    if animado:
        frames[0].save(
            salida,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / FPS),
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

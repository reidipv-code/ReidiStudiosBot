# core/perfil_visual.py
import io
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ANCHO = 900
ALTO = 560
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


def cargar_fuente(tamano, negrita=False):
    rutas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if negrita
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for ruta in rutas:
        try:
            return ImageFont.truetype(ruta, tamano)
        except OSError:
            pass

    return ImageFont.load_default()


def texto_ajustado(draw, texto, fuente, max_ancho):
    texto = str(texto)

    if draw.textbbox((0, 0), texto, font=fuente)[2] <= max_ancho:
        return texto

    while texto and draw.textbbox(
        (0, 0),
        texto + "...",
        font=fuente,
    )[2] > max_ancho:
        texto = texto[:-1]

    return texto + "..."


def crear_gradiente(c1, c2, ancho=ANCHO, alto=ALTO):
    imagen = Image.new("RGB", (ancho, alto))
    pixeles = imagen.load()

    for y in range(alto):
        t = y / max(1, alto - 1)

        color = tuple(
            int(c1[i] * (1 - t) + c2[i] * t)
            for i in range(3)
        )

        for x in range(ancho):
            pixeles[x, y] = color

    return imagen.convert("RGBA")


def redimensionar_avatar(imagen, tamano=180):
    imagen = imagen.convert("RGBA")

    lado = min(imagen.width, imagen.height)

    izquierda = (imagen.width - lado) // 2
    arriba = (imagen.height - lado) // 2

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


def crear_avatar_iniciales(nombre, tamano=180):
    imagen = Image.new(
        "RGBA",
        (tamano, tamano),
        (45, 45, 65, 255),
    )

    draw = ImageDraw.Draw(imagen)

    fuente = cargar_fuente(
        max(32, tamano // 3),
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

    x = (
        tamano
        - (bbox[2] - bbox[0])
    ) // 2

    y = (
        tamano
        - (bbox[3] - bbox[1])
    ) // 2 - bbox[1]

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


def dibujar_fondo(base, fondo):
    if fondo in COLORES_FONDO:
        c1, c2 = COLORES_FONDO[fondo]

        gradiente = crear_gradiente(
            c1,
            c2,
        )

        base.alpha_composite(gradiente)

    else:
        base.paste(
            crear_gradiente(
                (12, 15, 35),
                (35, 20, 65),
            ),
            (0, 0),
        )

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    random.seed(100)

    for _ in range(70):
        x = random.randint(0, ANCHO)
        y = random.randint(0, ALTO)

        r = random.choice(
            [1, 1, 2, 2, 3]
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
                random.randint(25, 100),
            ),
        )

    base.alpha_composite(capa)


def dibujar_avatar(
    base,
    avatar,
    x=70,
    y=120,
    tamano=180,
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
            tamano + 20,
            tamano + 20,
        ),
        (0, 0, 0, 0),
    )

    sombra_draw = ImageDraw.Draw(
        sombra
    )

    sombra_draw.ellipse(
        (
            5,
            5,
            tamano + 15,
            tamano + 15,
        ),
        fill=(0, 0, 0, 130),
    )

    sombra = sombra.filter(
        ImageFilter.GaussianBlur(8)
    )

    base.alpha_composite(
        sombra,
        (x - 10, y - 10),
    )

    base.alpha_composite(
        avatar,
        (x, y),
    )


def dibujar_marco(base, marco):
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
            12,
            12,
            ANCHO - 12,
            ALTO - 12,
        ),
        radius=30,
        outline=(*color, 255),
        width=8,
    )

    draw.rounded_rectangle(
        (
            25,
            25,
            ANCHO - 25,
            ALTO - 25,
        ),
        radius=24,
        outline=(*color, 90),
        width=3,
    )

    base.alpha_composite(capa)


def _punto_circular(
    draw,
    cx,
    cy,
    radio,
    angulo,
    tamano,
    fill,
):
    rad = math.radians(angulo)

    x = (
        cx
        + math.cos(rad) * radio
    )

    y = (
        cy
        + math.sin(rad) * radio
    )

    draw.ellipse(
        (
            x - tamano,
            y - tamano,
            x + tamano,
            y + tamano,
        ),
        fill=fill,
    )


def _dibujar_corazones(draw, frame):
    fuente = cargar_fuente(
        22,
        True,
    )

    for i in range(9):
        x = 80 + i * 100

        y = 55 + (
            (frame * 8 + i * 37)
            % 450
        )

        draw.text(
            (x, y),
            "♥",
            font=fuente,
            fill=(255, 90, 130, 150),
        )


def _dibujar_flores(draw, frame):
    for i in range(8):
        x = 70 + i * 110

        y = 70 + (
            (frame * 5 + i * 53)
            % 420
        )

        r = 6
        color = (
            255,
            170,
            210,
            130,
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r,
            ),
            fill=color,
        )

        draw.ellipse(
            (
                x - 2 * r,
                y - r,
                x,
                y + r,
            ),
            fill=color,
        )

        draw.ellipse(
            (
                x,
                y - r,
                x + 2 * r,
                y + r,
            ),
            fill=color,
        )


def _dibujar_mariposas(draw, frame):
    for i in range(6):
        x = 100 + i * 140

        y = 70 + (
            (frame * 7 + i * 60)
            % 390
        )

        draw.ellipse(
            (
                x - 12,
                y - 5,
                x,
                y + 8,
            ),
            fill=(190, 120, 255, 120),
        )

        draw.ellipse(
            (
                x,
                y - 5,
                x + 12,
                y + 8,
            ),
            fill=(100, 200, 255, 120),
        )

        draw.line(
            (
                x,
                y,
                x,
                y + 13,
            ),
            fill=(255, 255, 255, 130),
            width=2,
        )


def _dibujar_runa(draw, frame):
    cx = ANCHO // 2
    cy = ALTO // 2

    draw.ellipse(
        (
            cx - 170,
            cy - 170,
            cx + 170,
            cy + 170,
        ),
        outline=(160, 100, 255, 100),
        width=2,
    )

    draw.ellipse(
        (
            cx - 120,
            cy - 120,
            cx + 120,
            cy + 120,
        ),
        outline=(100, 220, 255, 100),
        width=2,
    )

    for i in range(8):
        angulo = (
            frame * 3
            + i * 45
        )

        _punto_circular(
            draw,
            cx,
            cy,
            145,
            angulo,
            4,
            (190, 120, 255, 160),
        )


def _dibujar_cyber(draw, frame):
    color = (
        50,
        220,
        255,
        100,
    )

    desplazamiento = (
        frame * 8
    ) % 40

    for x in range(
        -40,
        ANCHO + 40,
        40,
    ):
        draw.line(
            (
                x + desplazamiento,
                0,
                x + desplazamiento,
                ALTO,
            ),
            fill=color,
            width=1,
        )

    for y in range(
        -40,
        ALTO + 40,
        40,
    ):
        draw.line(
            (
                0,
                y + desplazamiento,
                ANCHO,
                y + desplazamiento,
            ),
            fill=color,
            width=1,
        )


def _dibujar_samurai(draw, frame):
    color = (
        220,
        80,
        70,
        120,
    )

    for i in range(6):
        y = 80 + i * 80

        draw.line(
            (
                30,
                y,
                ANCHO - 30,
                y + 35,
            ),
            fill=color,
            width=2,
        )


def _dibujar_corona(draw, frame):
    fuente = cargar_fuente(
        70,
        True,
    )

    draw.text(
        (ANCHO - 170, 35),
        "♛",
        font=fuente,
        fill=(255, 220, 80, 180),
    )


def _dibujar_neon(draw, frame):
    color = (
        40,
        255,
        220,
        120,
    )

    for i in range(5):
        y = (
            100
            + i * 80
            + int(
                math.sin(
                    frame / 2 + i
                ) * 15
            )
        )

        draw.line(
            (
                40,
                y,
                ANCHO - 40,
                y,
            ),
            fill=color,
            width=2,
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

    efecto = efecto or ""

    if efecto == "efecto_fuego":
        _efecto_fuego(draw, frame)

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

    base.alpha_composite(capa)


def _efecto_fuego(draw, frame):
    random.seed(
        1000 + frame
    )

    for _ in range(45):
        x = random.randint(
            25,
            ANCHO - 25,
        )

        y = ALTO - random.randint(
            20,
            120,
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
                random.randint(80, 190),
                30,
                random.randint(80, 180),
            ),
        )


def _efecto_electricidad(draw, frame):
    random.seed(
        2000 + frame
    )

    for _ in range(10):
        x = random.randint(
            40,
            ANCHO - 40,
        )

        puntos = [
            (x, 20)
        ]

        y = 20

        while y < ALTO - 20:
            y += random.randint(
                25,
                55,
            )

            x += random.randint(
                -25,
                25,
            )

            puntos.append(
                (x, y)
            )

        draw.line(
            puntos,
            fill=(100, 220, 255, 170),
            width=2,
        )


def _efecto_escarcha(draw, frame):
    random.seed(
        3000 + frame
    )

    for _ in range(55):
        x = random.randint(
            20,
            ANCHO - 20,
        )

        y = random.randint(
            20,
            ALTO - 20,
        )

        r = random.randint(
            2,
            5,
        )

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
    random.seed(
        4000 + frame
    )

    for _ in range(60):
        x = random.randint(
            20,
            ANCHO - 20,
        )

        y = random.randint(
            20,
            ALTO - 20,
        )

        r = random.randint(
            1,
            3,
        )

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

    for i in range(70):
        angulo = (
            i * 37
            + frame * 8
        ) % 360

        radio = (
            80
            + (i * 17) % 300
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

        r = 1 + i % 3

        draw.ellipse(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r,
            ),
            fill=(190, 150, 255, 120),
        )


def _efecto_aura(draw, frame):
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
            100,
            60,
            ANCHO - 100,
            ALTO - 60,
        ),
        outline=(
            100,
            200,
            255,
            alpha,
        ),
        width=12,
    )


def _efecto_corazones(draw, frame):
    random.seed(
        6000 + frame
    )

    fuente = cargar_fuente(
        22,
        True,
    )

    for _ in range(16):
        x = random.randint(
            25,
            ANCHO - 45,
        )

        y = random.randint(
            25,
            ALTO - 45,
        )

        draw.text(
            (x, y),
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


def _efecto_petalo(draw, frame):
    random.seed(
        7000 + frame
    )

    for _ in range(30):
        x = random.randint(
            20,
            ANCHO - 20,
        )

        y = random.randint(
            20,
            ALTO - 20,
        )

        draw.ellipse(
            (
                x - 4,
                y - 8,
                x + 4,
                y + 8,
            ),
            fill=(255, 150, 190, 130),
        )


def _efecto_mariposas(draw, frame):
    _dibujar_mariposas(
        draw,
        frame,
    )


def _efecto_burbujas(draw, frame):
    random.seed(8000)

    for i in range(20):
        x = (
            30
            + (
                i * 73
                + frame * 4
            ) % (ANCHO - 60)
        )

        y = (
            ALTO
            - (
                i * 47
                + frame * 8
            ) % (ALTO - 40)
        )

        r = 4 + i % 7

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
            width=2,
        )


def _efecto_estrellas(draw, frame):
    random.seed(9000)

    for i in range(35):
        x = random.randint(
            20,
            ANCHO - 20,
        )

        y = random.randint(
            20,
            ALTO - 20,
        )

        r = 2 + (
            (i + frame) % 3
        )

        draw.line(
            (
                x - r,
                y,
                x + r,
                y,
            ),
            fill=(255, 255, 220, 160),
            width=1,
        )

        draw.line(
            (
                x,
                y - r,
                x,
                y + r,
            ),
            fill=(255, 255, 220, 160),
            width=1,
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
        margen = i * 7

        draw.rounded_rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen,
            ),
            radius=35,
            outline=color,
            width=4,
        )


def _dibujar_accesorio(
    base,
    accesorio,
    frame,
):
    if not accesorio:
        return

    capa = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(capa)

    nombre = str(
        accesorio
    ).lower()

    if "corona" in nombre:
        _dibujar_corona(
            draw,
            frame,
        )

    elif "neon" in nombre:
        _dibujar_neon(
            draw,
            frame,
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
    equipados = equipados or {}

    if isinstance(equipados, dict):
        marco = equipados.get("marco")
        fondo = equipados.get("fondo")
        efecto = equipados.get("efecto")
        accesorio = equipados.get("accesorio")

        color_nombre = (
            equipados.get("color")
            or equipados.get("color_nombre")
        )
    else:
        marco = None
        fondo = None
        efecto = None
        accesorio = None
        color_nombre = None

    if isinstance(equipados, dict):
        for clave, valor in equipados.items():
            valor_str = str(
                valor or ""
            ).lower()

            if not valor_str:
                continue

            clave_lower = str(
                clave
            ).lower()

            if (
                marco is None
                and (
                    "marco" in clave_lower
                    or valor_str.startswith(
                        "marco_"
                    )
                )
            ):
                marco = valor

            if (
                fondo is None
                and (
                    "fondo" in clave_lower
                    or valor_str.startswith(
                        "fondo_"
                    )
                )
            ):
                fondo = valor

            if (
                efecto is None
                and (
                    "efecto" in clave_lower
                    or valor_str.startswith(
                        "efecto_"
                    )
                )
            ):
                efecto = valor

            if (
                color_nombre is None
                and (
                    "color" in clave_lower
                    or valor_str.startswith(
                        "color_"
                    )
                )
            ):
                color_nombre = valor

    color_texto = COLORES_NOMBRE.get(
        color_nombre,
        (255, 255, 255),
    )

    if avatar is None:
        avatar_img = crear_avatar_iniciales(
            nombre,
            190,
        )
    else:
        avatar_img = avatar

    frames = []

    for frame in range(
        FRAMES_ANIMADOS
    ):
        imagen = Image.new(
            "RGBA",
            (
                ANCHO,
                ALTO,
            ),
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
            70,
            130,
            190,
        )

        draw = ImageDraw.Draw(
            imagen
        )

        fuente_nombre = cargar_fuente(
            42,
            True,
        )

        fuente_info = cargar_fuente(
            25,
            False,
        )

        fuente_pequena = cargar_fuente(
            20,
            False,
        )

        nombre_mostrado = texto_ajustado(
            draw,
            nombre,
            fuente_nombre,
            570,
        )

        draw.text(
            (300, 105),
            nombre_mostrado,
            font=fuente_nombre,
            fill=(
                *color_texto,
                255,
            ),
        )

        draw.text(
            (300, 165),
            f"Nivel {nivel}",
            font=fuente_info,
            fill=(
                255,
                255,
                255,
                235,
            ),
        )

        draw.text(
            (300, 205),
            f"Rango: {rango}",
            font=fuente_info,
            fill=(
                225,
                225,
                235,
                235,
            ),
        )

        draw.text(
            (300, 245),
            f"XP: {xp_total} / {xp_siguiente}",
            font=fuente_info,
            fill=(
                225,
                225,
                235,
                235,
            ),
        )

        draw.text(
            (300, 285),
            f"Tokens: {tokens}",
            font=fuente_info,
            fill=(
                255,
                215,
                80,
                240,
            ),
        )

        if pais:
            draw.text(
                (300, 325),
                f"País: {pais}",
                font=fuente_pequena,
                fill=(
                    210,
                    225,
                    235,
                    230,
                ),
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

        barra_x = 300
        barra_y = 375
        barra_w = 500
        barra_h = 24

        draw.rounded_rectangle(
            (
                barra_x,
                barra_y,
                barra_x + barra_w,
                barra_y + barra_h,
            ),
            radius=12,
            fill=(
                25,
                25,
                35,
                210,
            ),
            outline=(
                255,
                255,
                255,
                80,
            ),
            width=2,
        )

        if progreso > 0:
            draw.rounded_rectangle(
                (
                    barra_x,
                    barra_y,
                    barra_x
                    + int(
                        barra_w
                        * progreso
                    ),
                    barra_y
                    + barra_h,
                ),
                radius=12,
                fill=(
                    70,
                    200,
                    255,
                    230,
                ),
            )

        if marco:
            dibujar_marco(
                imagen,
                marco,
            )

        draw.text(
            (55, ALTO - 55),
            "Reidi Studios",
            font=cargar_fuente(
                18,
                True,
            ),
            fill=(
                255,
                255,
                255,
                150,
            ),
        )

        frames.append(
            imagen.convert("RGB")
        )

    animado = bool(
        efecto
        or (
            marco
            and "animado"
            in str(marco).lower()
        )
    )

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
        )

        mime = "image/png"

    return (
        salida.getvalue(),
        mime,
        animado,
    )

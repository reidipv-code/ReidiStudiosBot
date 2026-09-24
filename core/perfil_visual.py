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


# Tamaños de texto
FONT_NOMBRE = 96
FONT_PAIS = 46

FONT_NIVEL = 64
FONT_XP = 58
FONT_PORCENTAJE = 44
FONT_RANGO = 48

FONT_INFO = 42
FONT_FOOTER = 32

# Tamaños de elementos
TAM_AVATAR = 360
TAM_ICONO = 54

# Posiciones principales
X_CONTENIDO = 540

Y_NOMBRE = 100
Y_PAIS = 220

# Todo lo relacionado con XP queda agrupado aquí.
Y_NIVEL = 470
Y_XP = 550
Y_BARRA = 650
Y_PORCENTAJE = 725
Y_RANGO = 805


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
    "normal": (80, 90, 110),
    "oro": (255, 205, 70),
    "plata": (190, 200, 215),
    "diamante": (100, 220, 255),
    "rojo": (255, 80, 80),
    "morado": (180, 90, 255),
    "esmeralda": (50, 220, 150),
}

COLORES_FONDO = {
    "normal": ((20, 25, 40), (45, 55, 85)),
    "azul": ((10, 25, 55), (30, 90, 150)),
    "morado": ((30, 15, 55), (100, 40, 150)),
    "rojo": ((50, 12, 20), (150, 35, 50)),
    "verde": ((10, 40, 25), (30, 130, 80)),
    "esmeralda": ((5, 35, 30), (20, 130, 100)),
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
# UTILIDADES
# ============================================================

def _producto_id(producto):
    if producto is None:
        return ""

    if isinstance(producto, dict):
        for clave in ("id", "producto_id", "nombre", "item"):
            if producto.get(clave) is not None:
                return str(producto[clave]).lower().strip()

    return str(producto).lower().strip()


def normalizar_equipados(equipados):
    if equipados is None:
        return []

    if isinstance(equipados, dict):
        resultado = []

        for clave, valor in equipados.items():
            if isinstance(valor, (list, tuple, set)):
                resultado.extend(valor)
            elif valor:
                resultado.append(valor)
            else:
                resultado.append(clave)

        return resultado

    if isinstance(equipados, (list, tuple, set)):
        return list(equipados)

    return [equipados]


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
        except Exception:
            pass

    return ImageFont.load_default()


def texto_ajustado(draw, texto, fuente, max_ancho):
    texto = str(texto)

    if draw.textbbox((0, 0), texto, font=fuente)[2] <= max_ancho:
        return texto

    while len(texto) > 3:
        texto = texto[:-1]

        prueba = texto + "..."
        if draw.textbbox((0, 0), prueba, font=fuente)[2] <= max_ancho:
            return prueba

    return "..."


# ============================================================
# FONDO
# ============================================================

def crear_gradiente(color1, color2):
    imagen = Image.new("RGB", (ANCHO, ALTO))
    pixeles = imagen.load()

    for y in range(ALTO):
        factor = y / max(1, ALTO - 1)

        r = int(color1[0] * (1 - factor) + color2[0] * factor)
        g = int(color1[1] * (1 - factor) + color2[1] * factor)
        b = int(color1[2] * (1 - factor) + color2[2] * factor)

        for x in range(ANCHO):
            pixeles[x, y] = (r, g, b)

    return imagen


def dibujar_fondo(imagen, estilo="normal", frame=0):
    colores = COLORES_FONDO.get(
        estilo,
        COLORES_FONDO["normal"]
    )

    fondo = crear_gradiente(*colores)

    # Viñeta
    overlay = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for i in range(20):
        margen = i * 8

        alpha = int(5 + i * 2)

        draw.rectangle(
            (
                margen,
                margen,
                ANCHO - margen,
                ALTO - margen
            ),
            outline=(0, 0, 0, alpha),
            width=8
        )

    fondo = Image.alpha_composite(
        fondo.convert("RGBA"),
        overlay
    )

    imagen.paste(fondo.convert("RGB"), (0, 0))


# ============================================================
# AVATAR
# ============================================================

def redimensionar_avatar(avatar, tamano):
    if avatar is None:
        return None

    avatar = avatar.convert("RGBA")

    # Escalado de máxima calidad disponible.
    return avatar.resize(
        (tamano, tamano),
        Image.Resampling.LANCZOS
    )


def crear_avatar_iniciales(nombre, tamano=TAM_AVATAR):
    imagen = Image.new(
        "RGBA",
        (tamano, tamano),
        (35, 40, 55, 255)
    )

    draw = ImageDraw.Draw(imagen)

    nombre = str(nombre or "?").strip()

    partes = nombre.split()

    if len(partes) >= 2:
        iniciales = (
            partes[0][0] +
            partes[1][0]
        ).upper()
    elif nombre:
        iniciales = nombre[:2].upper()
    else:
        iniciales = "?"

    fuente = cargar_fuente(130, negrita=True)

    bbox = draw.textbbox(
        (0, 0),
        iniciales,
        font=fuente
    )

    x = (tamano - (bbox[2] - bbox[0])) // 2
    y = (tamano - (bbox[3] - bbox[1])) // 2 - 10

    draw.text(
        (x, y),
        iniciales,
        font=fuente,
        fill=(240, 240, 245, 255)
    )

    return imagen


def recortar_circulo(imagen, tamano):
    imagen = redimensionar_avatar(imagen, tamano)

    if imagen is None:
        return None

    mascara = Image.new(
        "L",
        (tamano, tamano),
        0
    )

    draw = ImageDraw.Draw(mascara)

    draw.ellipse(
        (0, 0, tamano - 1, tamano - 1),
        fill=255
    )

    resultado = Image.new(
        "RGBA",
        (tamano, tamano),
        (0, 0, 0, 0)
    )

    resultado.paste(
        imagen,
        (0, 0),
        mascara
    )

    return resultado


def dibujar_avatar(imagen, avatar, x, y, tamano):
    avatar = recortar_circulo(
        avatar,
        tamano
    )

    if avatar is None:
        return

    # Borde exterior.
    overlay = Image.new(
        "RGBA",
        imagen.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(overlay)

    draw.ellipse(
        (
            x - 8,
            y - 8,
            x + tamano + 8,
            y + tamano + 8
        ),
        outline=(255, 255, 255, 180),
        width=8
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

    valor = str(pais).strip().lower()

    # Si viene como "🇨🇺 Cuba".
    for codigo, datos in PAISES.items():
        nombre = str(datos.get("nombre", "")).lower()
        bandera = str(datos.get("bandera", ""))

        if valor == codigo.lower():
            return codigo

        if valor == nombre:
            return codigo

        if bandera and bandera in str(pais):
            return codigo

        if nombre and nombre in valor:
            return codigo

    return None


def _dibujar_estrella(draw, cx, cy, radio, color):
    puntos = []

    for i in range(10):
        angulo = -math.pi / 2 + i * math.pi / 5

        r = radio if i % 2 == 0 else radio * 0.42

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


def dibujar_bandera(draw, pais, x, y, ancho=90, alto=60):
    codigo = _pais_codigo(pais)

    if not codigo:
        return

    # Bandera de Cuba dibujada manualmente.
    if codigo == "cuba":
        draw.rectangle(
            (x, y, x + ancho, y + alto),
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
                (x + ancho * 0.48, y + alto / 2),
                (x, y + alto)
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
            (x, y, x + ancho, y + alto),
            outline=(255, 255, 255),
            width=3
        )

        return

    # Otras banderas: usar un bloque limpio con la bandera
    # disponible en PAISES.
    datos = PAISES.get(codigo, {})

    bandera = datos.get("bandera", "")

    draw.rounded_rectangle(
        (x, y, x + ancho, y + alto),
        radius=8,
        fill=(45, 50, 65),
        outline=(255, 255, 255),
        width=2
    )

    if bandera:
        fuente = cargar_fuente(38)

        draw.text(
            (
                x + ancho // 2,
                y + alto // 2
            ),
            bandera,
            font=fuente,
            anchor="mm"
        )


# ============================================================
# ICONOS
# ============================================================

def dibujar_icono_rango(draw, x, y, tamano=54):
    color = (255, 205, 70)

    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=color
    )

    _dibujar_estrella(
        draw,
        x + tamano / 2,
        y + tamano / 2,
        tamano * 0.36,
        (70, 55, 15)
    )


def dibujar_icono_token(draw, x, y, tamano=54):
    draw.ellipse(
        (
            x,
            y,
            x + tamano,
            y + tamano
        ),
        fill=(255, 210, 70),
        outline=(255, 245, 170),
        width=3
    )

    fuente = cargar_fuente(
        max(20, int(tamano * 0.48)),
        negrita=True
    )

    draw.text(
        (
            x + tamano / 2,
            y + tamano / 2
        ),
        "T",
        font=fuente,
        anchor="mm",
        fill=(80, 60, 10)
    )


# ============================================================
# MARCO
# ============================================================

def dibujar_marco(draw, x, y, tamano, tipo="normal"):
    color = COLORES_MARCO.get(
        tipo,
        COLORES_MARCO["normal"]
    )

    draw.ellipse(
        (
            x - 12,
            y - 12,
            x + tamano + 12,
            y + tamano + 12
        ),
        outline=color,
        width=14
    )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_corazon(draw, x, y, tamano=80):
    r = tamano * 0.25

    draw.ellipse(
        (
            x,
            y,
            x + tamano / 2,
            y + tamano / 2
        ),
        fill=(255, 70, 100)
    )

    draw.ellipse(
        (
            x + tamano / 2 - r,
            y,
            x + tamano,
            y + tamano / 2
        ),
        fill=(255, 70, 100)
    )

    draw.polygon(
        [
            (x, y + tamano * 0.25),
            (x + tamano, y + tamano * 0.25),
            (x + tamano / 2, y + tamano)
        ],
        fill=(255, 70, 100)
    )


def _dibujar_mariposa(draw, x, y, tamano=80):
    color = (180, 100, 255)

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


def _dibujar_corona(draw, x=None, y=None, tamano=80):
    if x is None:
        x = ANCHO // 2 - tamano // 2

    if y is None:
        y = 40

    color = (255, 210, 60)

    puntos = [
        (x, y + tamano),
        (x + tamano * 0.15, y),
        (x + tamano * 0.45, y + tamano * 0.55),
        (x + tamano * 0.7, y),
        (x + tamano, y + tamano),
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


# ============================================================
# EFECTOS
# ============================================================

def dibujar_efecto(draw, efecto, frame=0):
    nombre = _producto_id(efecto)

    if "corazon" in nombre:
        x = ANCHO - 240
        y = 100 + int(
            math.sin(frame * 0.6) * 12
        )

        _dibujar_corazon(
            draw,
            x,
            y,
            70
        )

    elif "mariposa" in nombre:
        x = ANCHO - 260
        y = 150 + int(
            math.sin(frame * 0.45) * 25
        )

        _dibujar_mariposa(
            draw,
            x,
            y,
            80
        )


# ============================================================
# ACCESORIOS
# ============================================================

def _dibujar_accesorio(draw, accesorio, frame=0):
    nombre = _producto_id(accesorio)

    if "corona" in nombre:
        # CORREGIDO: no pasar frame a _dibujar_corona().
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
            80 + int(
                math.sin(frame * 0.5) * 10
            ),
            75
        )

    elif "mariposa" in nombre:
        _dibujar_mariposa(
            draw,
            ANCHO - 260,
            120 + int(
                math.sin(frame * 0.5) * 15
            ),
            80
        )


def dibujar_insignia(draw, x, y, texto, color):
    draw.rounded_rectangle(
        (
            x,
            y,
            x + 220,
            y + 58
        ),
        radius=20,
        fill=(20, 25, 40),
        outline=color,
        width=3
    )

    fuente = cargar_fuente(
        30,
        negrita=True
    )

    draw.text(
        (
            x + 110,
            y + 29
        ),
        texto,
        font=fuente,
        anchor="mm",
        fill=(245, 245, 250)
    )


# ============================================================
# BLOQUE DE EXPERIENCIA
# ============================================================

def dibujar_experiencia(
    draw,
    nivel,
    xp_actual,
    xp_siguiente,
    rango=None
):
    """
    TODO el bloque de progreso queda junto:

        NIVEL
          ↓
        XP
          ↓
        BARRA
          ↓
       78.4%

    """

    # --------------------------------------------------------
    # NIVEL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # XP
    # --------------------------------------------------------

    fuente_xp = cargar_fuente(
        FONT_XP,
        negrita=True
    )

    try:
        xp_actual_num = float(xp_actual or 0)
    except Exception:
        xp_actual_num = 0

    try:
        xp_siguiente_num = float(xp_siguiente or 1)
    except Exception:
        xp_siguiente_num = 1

    if xp_siguiente_num <= 0:
        xp_siguiente_num = 1

    porcentaje = (
        xp_actual_num /
        xp_siguiente_num
    ) * 100

    porcentaje = max(
        0,
        min(100, porcentaje)
    )

    draw.text(
        (
            X_CONTENIDO,
            Y_XP
        ),
        f"XP {int(xp_actual_num):,} / {int(xp_siguiente_num):,}",
        font=fuente_xp,
        anchor="lm",
        fill=(235, 240, 250)
    )

    # --------------------------------------------------------
    # BARRA
    # --------------------------------------------------------

    BAR_X = X_CONTENIDO
    BAR_Y = Y_BARRA
    BAR_W = 1120
    BAR_H = 52

    # Fondo.
    draw.rounded_rectangle(
        (
            BAR_X,
            BAR_Y,
            BAR_X + BAR_W,
            BAR_Y + BAR_H
        ),
        radius=BAR_H // 2,
        fill=(15, 18, 28),
        outline=(120, 130, 150),
        width=3
    )

    # Progreso.
    progreso_w = int(
        BAR_W * porcentaje / 100
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

    # --------------------------------------------------------
    # PORCENTAJE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RANGO
    # --------------------------------------------------------

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
):
    """
    Genera el perfil como PNG.

    Orden visual:

        NOMBRE
        PAÍS

        NIVEL
        XP
        BARRA
        PORCENTAJE
        RANGO
    """

    equipados = normalizar_equipados(
        equipados
    )

    # --------------------------------------------------------
    # Fondo
    # --------------------------------------------------------

    imagen = Image.new(
        "RGBA",
        (ANCHO, ALTO),
        (0, 0, 0, 255)
    )

    dibujar_fondo(
        imagen,
        estilo_fondo
    )

    draw = ImageDraw.Draw(
        imagen
    )

    # --------------------------------------------------------
    # Avatar
    # --------------------------------------------------------

    if avatar is None:
        avatar = crear_avatar_iniciales(
            nombre,
            TAM_AVATAR
        )

    AVATAR_X = 100
    AVATAR_Y = 300

    dibujar_marco(
        draw,
        AVATAR_X,
        AVATAR_Y,
        TAM_AVATAR,
        marco
    )

    dibujar_avatar(
        imagen,
        avatar,
        AVATAR_X,
        AVATAR_Y,
        TAM_AVATAR
    )

    # --------------------------------------------------------
    # Nombre
    # --------------------------------------------------------

    color_nombre = COLORES_NOMBRE.get(
        str(nombre_color).lower(),
        COLORES_NOMBRE["blanco"]
    )

    fuente_nombre = cargar_fuente(
        FONT_NOMBRE,
        negrita=True
    )

    nombre_mostrado = texto_ajustado(
        draw,
        nombre or "Usuario",
        fuente_nombre,
        1250
    )

    draw.text(
        (
            X_CONTENIDO,
            Y_NOMBRE
        ),
        nombre_mostrado,
        font=fuente_nombre,
        fill=color_nombre,
        anchor="lm"
    )

    # --------------------------------------------------------
    # País
    # --------------------------------------------------------

    codigo_pais = _pais_codigo(
        pais
    )

    if codigo_pais and codigo_pais in PAISES:
        datos_pais = PAISES[
            codigo_pais
        ]

        nombre_pais = datos_pais.get(
            "nombre",
            codigo_pais
        )

        dibujar_bandera(
            draw,
            codigo_pais,
            X_CONTENIDO,
            Y_PAIS - 28,
            ancho=88,
            alto=56
        )

        fuente_pais = cargar_fuente(
            FONT_PAIS,
            negrita=True
        )

        draw.text(
            (
                X_CONTENIDO + 115,
                Y_PAIS
            ),
            nombre_pais,
            font=fuente_pais,
            anchor="lm",
            fill=(235, 240, 250)
        )

    # --------------------------------------------------------
    # EXPERIENCIA
    #
    # Todo queda JUNTO y abajo.
    # --------------------------------------------------------

    dibujar_experiencia(
        draw,
        nivel,
        xp_actual,
        xp_siguiente,
        rango
    )

    # --------------------------------------------------------
    # Accesorios
    # --------------------------------------------------------

    for accesorio in equipados:
        _dibujar_accesorio(
            draw,
            accesorio,
            frame=0
        )

    # --------------------------------------------------------
    # Efectos
    # --------------------------------------------------------

    for accesorio in equipados:
        dibujar_efecto(
            draw,
            accesorio,
            frame=0
        )

    # --------------------------------------------------------
    # Exportación PNG
    # --------------------------------------------------------

    salida = io.BytesIO()

    imagen.convert("RGB").save(
        salida,
        format="PNG",
        optimize=False,
        compress_level=1
    )

    salida.seek(0)

    return salida

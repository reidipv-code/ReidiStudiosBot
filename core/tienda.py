import sqlite3
import math

from core.db import DB_PATH


PRODUCTOS = {
    # BONUS
    "bonus_mates": {
        "nombre": "Bonus Mates",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Mates.",
        "bonus_tipo": "mates",
        "multiplicador": 1.5,
    },
    "bonus_trivia": {
        "nombre": "Bonus Trivia",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Trivia.",
        "bonus_tipo": "trivia",
        "multiplicador": 1.5,
    },
    "bonus_palabras": {
        "nombre": "Bonus Palabras",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Palabras.",
        "bonus_tipo": "palabras",
        "multiplicador": 1.5,
    },
    "bonus_funks": {
        "nombre": "Bonus Funks",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Funks.",
        "bonus_tipo": "funks",
        "multiplicador": 1.5,
    },
    "bonus_memoria": {
        "nombre": "Bonus Memoria",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Memoria.",
        "bonus_tipo": "memoria",
        "multiplicador": 1.5,
    },
    "bonus_xp": {
        "nombre": "Bonus XP",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 1800,
        "descripcion": "+25% XP en actividades con recompensa de XP.",
        "bonus_tipo": "xp",
        "multiplicador": 1.25,
    },
    "bonus_tokens": {
        "nombre": "Bonus Tokens",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 1800,
        "descripcion": "+25% tokens en recompensas de actividades.",
        "bonus_tipo": "tokens",
        "multiplicador": 1.25,
    },

    # TITULOS
    "tit_incansable": {
        "nombre": "El Incansable",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1200,
        "descripcion": "Para quien nunca deja de jugar.",
    },
    "tit_cazador": {
        "nombre": "Cazador de Tesoros",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1800,
        "descripcion": "Colecciona recompensas y secretos.",
    },
    "tit_noctambulo": {
        "nombre": "Noctámbulo",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1400,
        "descripcion": "Siempre activo cuando cae la noche.",
    },
    "tit_coleccionista": {
        "nombre": "Coleccionista",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 2200,
        "descripcion": "Nada se queda fuera de tu colección.",
    },
    "tit_afortunado": {
        "nombre": "El Afortunado",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1500,
        "descripcion": "La suerte suele acompañarte.",
    },
    "tit_sin_miedo": {
        "nombre": "Sin Miedo",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1600,
        "descripcion": "Entras a cualquier partida.",
    },
    "tit_leyenda": {
        "nombre": "Leyenda Urbana",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3000,
        "descripcion": "Un nombre que se escucha por todas partes.",
    },
    "tit_caos": {
        "nombre": "Caos Andante",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 2600,
        "descripcion": "Donde llegas, algo pasa.",
    },
    "tit_superviviente": {
        "nombre": "El Último Superviviente",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3200,
        "descripcion": "Sigues de pie cuando termina todo.",
    },
    "tit_soberano": {
        "nombre": "Soberano del Bot",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 4500,
        "descripcion": "Un título reservado para grandes coleccionistas.",
    },
    "tit_arcano": {
        "nombre": "Portador Arcano",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3800,
        "descripcion": "Misterio, magia y estilo.",
    },
    "tit_estelar": {
        "nombre": "Viajero Estelar",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3500,
        "descripcion": "Un título de otro mundo.",
    },

    # MARCOS
    "marco_dorado": {
        "nombre": "Marco Dorado",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1000,
        "descripcion": "Borde dorado elegante.",
    },
    "marco_diamante": {
        "nombre": "Marco Diamante",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 3000,
        "descripcion": "Un borde cristalino y brillante.",
    },
    "marco_real": {
        "nombre": "Marco Real",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 4200,
        "descripcion": "Estilo de corona y lujo.",
    },
    "marco_glacial": {
        "nombre": "Marco Glacial",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2200,
        "descripcion": "Cristal de hielo alrededor del perfil.",
    },
    "marco_cosmico": {
        "nombre": "Marco Cósmico",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2800,
        "descripcion": "Borde inspirado en una nebulosa.",
    },
    "marco_rosa_cristal": {
        "nombre": "Rosa Cristal",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1800,
        "descripcion": "Marco rosa brillante y delicado.",
    },
    "marco_corazones": {
        "nombre": "Corazones",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1700,
        "descripcion": "Corazones alrededor del avatar.",
    },
    "marco_floral": {
        "nombre": "Floral",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1900,
        "descripcion": "Flores decorativas alrededor del perfil.",
    },
    "marco_mariposas": {
        "nombre": "Mariposas",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2100,
        "descripcion": "Mariposas estilizadas en el borde.",
    },
    "marco_neon": {
        "nombre": "Neón",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2400,
        "descripcion": "Borde luminoso de estética cyber.",
    },
    "marco_cyber": {
        "nombre": "Cyber",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2500,
        "descripcion": "Interfaz futurista y tecnológica.",
    },
    "marco_samurai": {
        "nombre": "Samurái",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2700,
        "descripcion": "Inspiración oriental oscura.",
    },
    "marco_dark": {
        "nombre": "Dark",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2000,
        "descripcion": "Borde negro de estética oscura.",
    },
    "marco_arcano": {
        "nombre": "Arcano",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2900,
        "descripcion": "Runas y símbolos místicos.",
    },
    "marco_esmeralda": {
        "nombre": "Esmeralda",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde verde joya.",
    },
    "marco_rubi": {
        "nombre": "Rubí",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde rojo de piedra preciosa.",
    },
    "marco_ametista": {
        "nombre": "Amatista",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde violeta de cristal.",
    },

    # EFECTOS
    "efecto_fuego": {
        "nombre": "Fuego",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3500,
        "descripcion": "Llamas animadas alrededor del perfil.",
    },
    "efecto_electricidad": {
        "nombre": "Electricidad",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3200,
        "descripcion": "Descargas eléctricas animadas.",
    },
    "efecto_escarcha": {
        "nombre": "Escarcha",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2800,
        "descripcion": "Partículas de hielo en movimiento.",
    },
    "efecto_chispas": {
        "nombre": "Chispas Doradas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2600,
        "descripcion": "Destellos dorados animados.",
    },
    "efecto_cosmico": {
        "nombre": "Partículas Cósmicas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3000,
        "descripcion": "Partículas estelares en movimiento.",
    },
    "efecto_aura": {
        "nombre": "Aura Oscura",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2900,
        "descripcion": "Aura oscura animada.",
    },
    "efecto_corazones": {
        "nombre": "Corazones",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2200,
        "descripcion": "Corazones flotando alrededor del perfil.",
    },
    "efecto_petalo": {
        "nombre": "Pétalos",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2100,
        "descripcion": "Pétalos suaves en movimiento.",
    },
    "efecto_mariposas": {
        "nombre": "Mariposas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2500,
        "descripcion": "Mariposas animadas alrededor del perfil.",
    },
    "efecto_burbujas": {
        "nombre": "Burbujas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 1800,
        "descripcion": "Burbujas ascendentes y brillantes.",
    },
    "efecto_estrellas": {
        "nombre": "Lluvia de Estrellas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2700,
        "descripcion": "Pequeñas estrellas atraviesan el perfil.",
    },
    "efecto_arcoiris": {
        "nombre": "Arcoíris",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2600,
        "descripcion": "Brillo multicolor animado.",
    },

    # MARCOS ANIMADOS
    "anim_infernal": {
        "nombre": "Infernal",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6500,
        "descripcion": "Marco animado completo con fuego alrededor.",
    },
    "anim_celestial": {
        "nombre": "Celestial",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7000,
        "descripcion": "Marco animado de luz y partículas celestiales.",
    },
    "anim_neon": {
        "nombre": "Neón Pulsante",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6000,
        "descripcion": "Marco cyber con pulso luminoso.",
    },
    "anim_glacial": {
        "nombre": "Tormenta Glacial",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6800,
        "descripcion": "Hielo animado recorriendo el borde.",
    },
    "anim_rosa": {
        "nombre": "Dreamy Rosa",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6200,
        "descripcion": "Marco rosa animado con destellos y corazones.",
    },
    "anim_nebulosa": {
        "nombre": "Nebulosa",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7200,
        "descripcion": "Nebulosa en movimiento alrededor del avatar.",
    },
    "anim_sobrecarga": {
        "nombre": "Sobrecarga",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7500,
        "descripcion": "Energía eléctrica recorriendo todo el marco.",
    },
    "anim_jardin": {
        "nombre": "Jardín Encantado",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6400,
        "descripcion": "Flores, hojas y pequeñas luces animadas.",
    },

    # FONDOS
    "fondo_noche": {
        "nombre": "Noche Estrellada",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 1800,
        "descripcion": "Fondo oscuro con estrellas.",
    },
    "fondo_nebulosa": {
        "nombre": "Nebulosa",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2600,
        "descripcion": "Fondo espacial colorido.",
    },
    "fondo_cyber": {
        "nombre": "Cyber City",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2400,
        "descripcion": "Ciudad futurista nocturna.",
    },
    "fondo_rosa": {
        "nombre": "Sueño Rosa",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 1900,
        "descripcion": "Fondo pastel rosa con brillos.",
    },
    "fondo_floresta": {
        "nombre": "Floresta Mística",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2300,
        "descripcion": "Bosque mágico y luminoso.",
    },
    "fondo_abismo": {
        "nombre": "Abismo",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2500,
        "descripcion": "Fondo oscuro de fantasía.",
    },

    # COLORES
    "color_dorado": {
        "nombre": "Nombre Dorado",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1400,
        "descripcion": "Color dorado para el nombre en la tarjeta del perfil.",
    },
    "color_rosa": {
        "nombre": "Nombre Rosa",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color rosa para el nombre en la tarjeta.",
    },
    "color_cian": {
        "nombre": "Nombre Cian",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color cian para el nombre en la tarjeta.",
    },
    "color_rojo": {
        "nombre": "Nombre Rojo",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color rojo para el nombre en la tarjeta.",
    },
    "color_violeta": {
        "nombre": "Nombre Violeta",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color violeta para el nombre en la tarjeta.",
    },
    "color_esmeralda": {
        "nombre": "Nombre Esmeralda",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color esmeralda para el nombre en la tarjeta.",
    },

    # INSIGNIAS
    "insignia_corona": {
        "nombre": "Insignia Corona",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 3000,
        "descripcion": "Insignia de corona para el perfil.",
    },
    "insignia_rayo": {
        "nombre": "Insignia Rayo",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2200,
        "descripcion": "Insignia de energía.",
    },
    "insignia_corazon": {
        "nombre": "Insignia Corazón",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 1800,
        "descripcion": "Insignia de corazón.",
    },
    "insignia_estelar": {
        "nombre": "Insignia Estelar",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2500,
        "descripcion": "Insignia de estrella.",
    },
    "insignia_arcana": {
        "nombre": "Insignia Arcana",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2800,
        "descripcion": "Insignia de símbolo místico.",
    },
}


def init_tienda_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tienda_productos (
            producto_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            bonus_tipo TEXT,
            multiplicador REAL DEFAULT 1.0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventario_tienda (
            user_id INTEGER NOT NULL,
            producto_id TEXT NOT NULL,
            comprado_en REAL DEFAULT (strftime('%s','now')),
            PRIMARY KEY (user_id, producto_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS equipamiento_tienda (
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            producto_id TEXT NOT NULL,
            PRIMARY KEY (user_id, tipo)
        )
    """)

    for pid, p in PRODUCTOS.items():
        c.execute("""
            INSERT OR REPLACE INTO tienda_productos
            (
                producto_id,
                nombre,
                tipo,
                categoria,
                precio,
                descripcion,
                bonus_tipo,
                multiplicador
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid,
            p["nombre"],
            p["tipo"],
            p["categoria"],
            p["precio"],
            p["descripcion"],
            p.get("bonus_tipo"),
            p.get("multiplicador", 1.0),
        ))

    conn.commit()
    conn.close()


def producto(producto_id):
    return PRODUCTOS.get(producto_id)


def tiene_producto(user_id, producto_id):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT 1
        FROM inventario_tienda
        WHERE user_id = ?
          AND producto_id = ?
    """, (user_id, producto_id))

    resultado = c.fetchone()

    conn.close()

    return resultado is not None


def comprar_producto(user_id, producto_id):
    init_tienda_db()

    p = producto(producto_id)

    if not p:
        return False, "Producto no encontrado."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT tokens
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))

    fila = c.fetchone()

    if not fila:
        conn.close()
        return False, "Usuario no encontrado."

    tokens = int(fila[0] or 0)

    if tokens < p["precio"]:
        conn.close()
        return False, (
            f"Necesitas {p['precio']:,} tokens "
            f"y tienes {tokens:,}."
        )

    c.execute("""
        SELECT 1
        FROM inventario_tienda
        WHERE user_id = ?
          AND producto_id = ?
    """, (user_id, producto_id))

    if c.fetchone():
        conn.close()
        return False, "Ya tienes este producto."

    c.execute("""
        UPDATE usuarios
        SET tokens = tokens - ?
        WHERE user_id = ?
    """, (
        p["precio"],
        user_id
    ))

    c.execute("""
        INSERT INTO inventario_tienda
        (
            user_id,
            producto_id
        )
        VALUES (?, ?)
    """, (
        user_id,
        producto_id
    ))

    conn.commit()
    conn.close()

    return True, (
        f"Compraste {p['nombre']} "
        f"por {p['precio']:,} tokens."
    )


def equipar_producto(user_id, producto_id):
    init_tienda_db()

    p = producto(producto_id)

    if not p:
        return False, "Producto no encontrado."

    if not tiene_producto(user_id, producto_id):
        return False, "Primero debes comprarlo."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Los marcos normales y animados comparten el mismo slot visual.
    if p["tipo"] == "marco":
        c.execute("""
            DELETE FROM equipamiento_tienda
            WHERE user_id = ?
              AND tipo = 'marco_animado'
        """, (user_id,))

    elif p["tipo"] == "marco_animado":
        c.execute("""
            DELETE FROM equipamiento_tienda
            WHERE user_id = ?
              AND tipo = 'marco'
        """, (user_id,))

    c.execute("""
        INSERT OR REPLACE INTO equipamiento_tienda
        (
            user_id,
            tipo,
            producto_id
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        p["tipo"],
        producto_id
    ))

    conn.commit()
    conn.close()

    return True, f"{p['nombre']} equipado."


def desequipar_tipo(user_id, tipo):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        DELETE FROM equipamiento_tienda
        WHERE user_id = ?
          AND tipo = ?
    """, (
        user_id,
        tipo
    ))

    conn.commit()
    conn.close()


def producto_equipado(user_id, tipo):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT producto_id
        FROM equipamiento_tienda
        WHERE user_id = ?
          AND tipo = ?
    """, (
        user_id,
        tipo
    ))

    fila = c.fetchone()

    conn.close()

    if not fila:
        return None

    return PRODUCTOS.get(fila[0])


def equipados_usuario(user_id):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT tipo, producto_id
        FROM equipamiento_tienda
        WHERE user_id = ?
    """, (user_id,))

    filas = c.fetchall()

    conn.close()

    resultado = {}

    for tipo, producto_id in filas:
        if producto_id in PRODUCTOS:
            resultado[tipo] = PRODUCTOS[producto_id]

    # Unifica el slot visual de marcos.
    if "marco_animado" in resultado:
        resultado["marco"] = resultado["marco_animado"]

    return resultado


def inventario_usuario(user_id, tipo=None):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if tipo:
        c.execute("""
            SELECT i.producto_id
            FROM inventario_tienda i
            JOIN tienda_productos p
                ON p.producto_id = i.producto_id
            WHERE i.user_id = ?
              AND p.tipo = ?
            ORDER BY p.precio DESC
        """, (
            user_id,
            tipo
        ))
    else:
        c.execute("""
            SELECT producto_id
            FROM inventario_tienda
            WHERE user_id = ?
        """, (user_id,))

    filas = c.fetchall()

    conn.close()

    return [
        PRODUCTOS[pid]
        for (pid,) in filas
        if pid in PRODUCTOS
    ]


def multiplicador_recompensa(user_id, categoria, recurso):
    init_tienda_db()

    mult = 1.0

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT p.producto_id
        FROM inventario_tienda i
        JOIN tienda_productos p
            ON p.producto_id = i.producto_id
        WHERE i.user_id = ?
          AND p.tipo = 'bonus'
    """, (user_id,))

    ids = [fila[0] for fila in c.fetchall()]

    conn.close()

    for pid in ids:
        p = PRODUCTOS.get(pid)

        if not p:
            continue

        bonus_tipo = p.get("bonus_tipo")

        if recurso == "xp":
            if bonus_tipo in (categoria, "xp"):
                mult = max(
                    mult,
                    p.get("multiplicador", 1.0)
                )

        elif recurso == "tokens":
            if bonus_tipo == "tokens":
                mult = max(
                    mult,
                    p.get("multiplicador", 1.0)
                )

    return mult


def aplicar_bonus_xp(user_id, cantidad, categoria):
    from core.db import sumar_xp

    if cantidad <= 0:
        return sumar_xp(user_id, cantidad)

    multiplicador = multiplicador_recompensa(
        user_id,
        categoria,
        "xp"
    )

    cantidad_final = max(
        1,
        int(round(cantidad * multiplicador))
    )

    return sumar_xp(
        user_id,
        cantidad_final
    )


def cantidad_con_bonus_tokens(user_id, cantidad, categoria):
    if cantidad <= 0:
        return cantidad

    multiplicador = multiplicador_recompensa(
        user_id,
        categoria,
        "tokens"
    )
import sqlite3
import math

from core.db import DB_PATH


PRODUCTOS = {
    # BONUS
    "bonus_mates": {
        "nombre": "Bonus Mates",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Mates.",
        "bonus_tipo": "mates",
        "multiplicador": 1.5,
    },
    "bonus_trivia": {
        "nombre": "Bonus Trivia",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Trivia.",
        "bonus_tipo": "trivia",
        "multiplicador": 1.5,
    },
    "bonus_palabras": {
        "nombre": "Bonus Palabras",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Palabras.",
        "bonus_tipo": "palabras",
        "multiplicador": 1.5,
    },
    "bonus_funks": {
        "nombre": "Bonus Funks",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Funks.",
        "bonus_tipo": "funks",
        "multiplicador": 1.5,
    },
    "bonus_memoria": {
        "nombre": "Bonus Memoria",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 900,
        "descripcion": "+50% XP en Memoria.",
        "bonus_tipo": "memoria",
        "multiplicador": 1.5,
    },
    "bonus_xp": {
        "nombre": "Bonus XP",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 1800,
        "descripcion": "+25% XP en actividades con recompensa de XP.",
        "bonus_tipo": "xp",
        "multiplicador": 1.25,
    },
    "bonus_tokens": {
        "nombre": "Bonus Tokens",
        "tipo": "bonus",
        "categoria": "bonus",
        "precio": 1800,
        "descripcion": "+25% tokens en recompensas de actividades.",
        "bonus_tipo": "tokens",
        "multiplicador": 1.25,
    },

    # TITULOS
    "tit_incansable": {
        "nombre": "El Incansable",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1200,
        "descripcion": "Para quien nunca deja de jugar.",
    },
    "tit_cazador": {
        "nombre": "Cazador de Tesoros",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1800,
        "descripcion": "Colecciona recompensas y secretos.",
    },
    "tit_noctambulo": {
        "nombre": "Noctámbulo",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1400,
        "descripcion": "Siempre activo cuando cae la noche.",
    },
    "tit_coleccionista": {
        "nombre": "Coleccionista",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 2200,
        "descripcion": "Nada se queda fuera de tu colección.",
    },
    "tit_afortunado": {
        "nombre": "El Afortunado",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1500,
        "descripcion": "La suerte suele acompañarte.",
    },
    "tit_sin_miedo": {
        "nombre": "Sin Miedo",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 1600,
        "descripcion": "Entras a cualquier partida.",
    },
    "tit_leyenda": {
        "nombre": "Leyenda Urbana",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3000,
        "descripcion": "Un nombre que se escucha por todas partes.",
    },
    "tit_caos": {
        "nombre": "Caos Andante",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 2600,
        "descripcion": "Donde llegas, algo pasa.",
    },
    "tit_superviviente": {
        "nombre": "El Último Superviviente",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3200,
        "descripcion": "Sigues de pie cuando termina todo.",
    },
    "tit_soberano": {
        "nombre": "Soberano del Bot",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 4500,
        "descripcion": "Un título reservado para grandes coleccionistas.",
    },
    "tit_arcano": {
        "nombre": "Portador Arcano",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3800,
        "descripcion": "Misterio, magia y estilo.",
    },
    "tit_estelar": {
        "nombre": "Viajero Estelar",
        "tipo": "titulo",
        "categoria": "titulos",
        "precio": 3500,
        "descripcion": "Un título de otro mundo.",
    },

    # MARCOS
    "marco_dorado": {
        "nombre": "Marco Dorado",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1000,
        "descripcion": "Borde dorado elegante.",
    },
    "marco_diamante": {
        "nombre": "Marco Diamante",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 3000,
        "descripcion": "Un borde cristalino y brillante.",
    },
    "marco_real": {
        "nombre": "Marco Real",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 4200,
        "descripcion": "Estilo de corona y lujo.",
    },
    "marco_glacial": {
        "nombre": "Marco Glacial",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2200,
        "descripcion": "Cristal de hielo alrededor del perfil.",
    },
    "marco_cosmico": {
        "nombre": "Marco Cósmico",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2800,
        "descripcion": "Borde inspirado en una nebulosa.",
    },
    "marco_rosa_cristal": {
        "nombre": "Rosa Cristal",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1800,
        "descripcion": "Marco rosa brillante y delicado.",
    },
    "marco_corazones": {
        "nombre": "Corazones",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1700,
        "descripcion": "Corazones alrededor del avatar.",
    },
    "marco_floral": {
        "nombre": "Floral",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 1900,
        "descripcion": "Flores decorativas alrededor del perfil.",
    },
    "marco_mariposas": {
        "nombre": "Mariposas",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2100,
        "descripcion": "Mariposas estilizadas en el borde.",
    },
    "marco_neon": {
        "nombre": "Neón",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2400,
        "descripcion": "Borde luminoso de estética cyber.",
    },
    "marco_cyber": {
        "nombre": "Cyber",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2500,
        "descripcion": "Interfaz futurista y tecnológica.",
    },
    "marco_samurai": {
        "nombre": "Samurái",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2700,
        "descripcion": "Inspiración oriental oscura.",
    },
    "marco_dark": {
        "nombre": "Dark",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2000,
        "descripcion": "Borde negro de estética oscura.",
    },
    "marco_arcano": {
        "nombre": "Arcano",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2900,
        "descripcion": "Runas y símbolos místicos.",
    },
    "marco_esmeralda": {
        "nombre": "Esmeralda",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde verde joya.",
    },
    "marco_rubi": {
        "nombre": "Rubí",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde rojo de piedra preciosa.",
    },
    "marco_ametista": {
        "nombre": "Amatista",
        "tipo": "marco",
        "categoria": "marcos",
        "precio": 2300,
        "descripcion": "Borde violeta de cristal.",
    },

    # EFECTOS
    "efecto_fuego": {
        "nombre": "Fuego",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3500,
        "descripcion": "Llamas animadas alrededor del perfil.",
    },
    "efecto_electricidad": {
        "nombre": "Electricidad",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3200,
        "descripcion": "Descargas eléctricas animadas.",
    },
    "efecto_escarcha": {
        "nombre": "Escarcha",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2800,
        "descripcion": "Partículas de hielo en movimiento.",
    },
    "efecto_chispas": {
        "nombre": "Chispas Doradas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2600,
        "descripcion": "Destellos dorados animados.",
    },
    "efecto_cosmico": {
        "nombre": "Partículas Cósmicas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 3000,
        "descripcion": "Partículas estelares en movimiento.",
    },
    "efecto_aura": {
        "nombre": "Aura Oscura",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2900,
        "descripcion": "Aura oscura animada.",
    },
    "efecto_corazones": {
        "nombre": "Corazones",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2200,
        "descripcion": "Corazones flotando alrededor del perfil.",
    },
    "efecto_petalo": {
        "nombre": "Pétalos",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2100,
        "descripcion": "Pétalos suaves en movimiento.",
    },
    "efecto_mariposas": {
        "nombre": "Mariposas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2500,
        "descripcion": "Mariposas animadas alrededor del perfil.",
    },
    "efecto_burbujas": {
        "nombre": "Burbujas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 1800,
        "descripcion": "Burbujas ascendentes y brillantes.",
    },
    "efecto_estrellas": {
        "nombre": "Lluvia de Estrellas",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2700,
        "descripcion": "Pequeñas estrellas atraviesan el perfil.",
    },
    "efecto_arcoiris": {
        "nombre": "Arcoíris",
        "tipo": "efecto",
        "categoria": "efectos",
        "precio": 2600,
        "descripcion": "Brillo multicolor animado.",
    },

    # MARCOS ANIMADOS
    "anim_infernal": {
        "nombre": "Infernal",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6500,
        "descripcion": "Marco animado completo con fuego alrededor.",
    },
    "anim_celestial": {
        "nombre": "Celestial",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7000,
        "descripcion": "Marco animado de luz y partículas celestiales.",
    },
    "anim_neon": {
        "nombre": "Neón Pulsante",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6000,
        "descripcion": "Marco cyber con pulso luminoso.",
    },
    "anim_glacial": {
        "nombre": "Tormenta Glacial",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6800,
        "descripcion": "Hielo animado recorriendo el borde.",
    },
    "anim_rosa": {
        "nombre": "Dreamy Rosa",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6200,
        "descripcion": "Marco rosa animado con destellos y corazones.",
    },
    "anim_nebulosa": {
        "nombre": "Nebulosa",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7200,
        "descripcion": "Nebulosa en movimiento alrededor del avatar.",
    },
    "anim_sobrecarga": {
        "nombre": "Sobrecarga",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 7500,
        "descripcion": "Energía eléctrica recorriendo todo el marco.",
    },
    "anim_jardin": {
        "nombre": "Jardín Encantado",
        "tipo": "marco_animado",
        "categoria": "marcos",
        "precio": 6400,
        "descripcion": "Flores, hojas y pequeñas luces animadas.",
    },

    # FONDOS
    "fondo_noche": {
        "nombre": "Noche Estrellada",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 1800,
        "descripcion": "Fondo oscuro con estrellas.",
    },
    "fondo_nebulosa": {
        "nombre": "Nebulosa",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2600,
        "descripcion": "Fondo espacial colorido.",
    },
    "fondo_cyber": {
        "nombre": "Cyber City",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2400,
        "descripcion": "Ciudad futurista nocturna.",
    },
    "fondo_rosa": {
        "nombre": "Sueño Rosa",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 1900,
        "descripcion": "Fondo pastel rosa con brillos.",
    },
    "fondo_floresta": {
        "nombre": "Floresta Mística",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2300,
        "descripcion": "Bosque mágico y luminoso.",
    },
    "fondo_abismo": {
        "nombre": "Abismo",
        "tipo": "fondo",
        "categoria": "accesorios2",
        "precio": 2500,
        "descripcion": "Fondo oscuro de fantasía.",
    },

    # COLORES
    "color_dorado": {
        "nombre": "Nombre Dorado",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1400,
        "descripcion": "Color dorado para el nombre en la tarjeta del perfil.",
    },
    "color_rosa": {
        "nombre": "Nombre Rosa",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color rosa para el nombre en la tarjeta.",
    },
    "color_cian": {
        "nombre": "Nombre Cian",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color cian para el nombre en la tarjeta.",
    },
    "color_rojo": {
        "nombre": "Nombre Rojo",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color rojo para el nombre en la tarjeta.",
    },
    "color_violeta": {
        "nombre": "Nombre Violeta",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color violeta para el nombre en la tarjeta.",
    },
    "color_esmeralda": {
        "nombre": "Nombre Esmeralda",
        "tipo": "color",
        "categoria": "accesorios2",
        "precio": 1200,
        "descripcion": "Color esmeralda para el nombre en la tarjeta.",
    },

    # INSIGNIAS
    "insignia_corona": {
        "nombre": "Insignia Corona",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 3000,
        "descripcion": "Insignia de corona para el perfil.",
    },
    "insignia_rayo": {
        "nombre": "Insignia Rayo",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2200,
        "descripcion": "Insignia de energía.",
    },
    "insignia_corazon": {
        "nombre": "Insignia Corazón",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 1800,
        "descripcion": "Insignia de corazón.",
    },
    "insignia_estelar": {
        "nombre": "Insignia Estelar",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2500,
        "descripcion": "Insignia de estrella.",
    },
    "insignia_arcana": {
        "nombre": "Insignia Arcana",
        "tipo": "insignia",
        "categoria": "accesorios2",
        "precio": 2800,
        "descripcion": "Insignia de símbolo místico.",
    },
}


def init_tienda_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tienda_productos (
            producto_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            bonus_tipo TEXT,
            multiplicador REAL DEFAULT 1.0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventario_tienda (
            user_id INTEGER NOT NULL,
            producto_id TEXT NOT NULL,
            comprado_en REAL DEFAULT (strftime('%s','now')),
            PRIMARY KEY (user_id, producto_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS equipamiento_tienda (
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            producto_id TEXT NOT NULL,
            PRIMARY KEY (user_id, tipo)
        )
    """)

    for pid, p in PRODUCTOS.items():
        c.execute("""
            INSERT OR REPLACE INTO tienda_productos
            (
                producto_id,
                nombre,
                tipo,
                categoria,
                precio,
                descripcion,
                bonus_tipo,
                multiplicador
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid,
            p["nombre"],
            p["tipo"],
            p["categoria"],
            p["precio"],
            p["descripcion"],
            p.get("bonus_tipo"),
            p.get("multiplicador", 1.0),
        ))

    conn.commit()
    conn.close()


def producto(producto_id):
    return PRODUCTOS.get(producto_id)


def tiene_producto(user_id, producto_id):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT 1
        FROM inventario_tienda
        WHERE user_id = ?
          AND producto_id = ?
    """, (user_id, producto_id))

    resultado = c.fetchone()

    conn.close()

    return resultado is not None


def comprar_producto(user_id, producto_id):
    init_tienda_db()

    p = producto(producto_id)

    if not p:
        return False, "Producto no encontrado."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT tokens
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))

    fila = c.fetchone()

    if not fila:
        conn.close()
        return False, "Usuario no encontrado."

    tokens = int(fila[0] or 0)

    if tokens < p["precio"]:
        conn.close()
        return False, (
            f"Necesitas {p['precio']:,} tokens "
            f"y tienes {tokens:,}."
        )

    c.execute("""
        SELECT 1
        FROM inventario_tienda
        WHERE user_id = ?
          AND producto_id = ?
    """, (user_id, producto_id))

    if c.fetchone():
        conn.close()
        return False, "Ya tienes este producto."

    c.execute("""
        UPDATE usuarios
        SET tokens = tokens - ?
        WHERE user_id = ?
    """, (
        p["precio"],
        user_id
    ))

    c.execute("""
        INSERT INTO inventario_tienda
        (
            user_id,
            producto_id
        )
        VALUES (?, ?)
    """, (
        user_id,
        producto_id
    ))

    conn.commit()
    conn.close()

    return True, (
        f"Compraste {p['nombre']} "
        f"por {p['precio']:,} tokens."
    )


def equipar_producto(user_id, producto_id):
    init_tienda_db()

    p = producto(producto_id)

    if not p:
        return False, "Producto no encontrado."

    if not tiene_producto(user_id, producto_id):
        return False, "Primero debes comprarlo."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Los marcos normales y animados comparten el mismo slot visual.
    if p["tipo"] == "marco":
        c.execute("""
            DELETE FROM equipamiento_tienda
            WHERE user_id = ?
              AND tipo = 'marco_animado'
        """, (user_id,))

    elif p["tipo"] == "marco_animado":
        c.execute("""
            DELETE FROM equipamiento_tienda
            WHERE user_id = ?
              AND tipo = 'marco'
        """, (user_id,))

    c.execute("""
        INSERT OR REPLACE INTO equipamiento_tienda
        (
            user_id,
            tipo,
            producto_id
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        p["tipo"],
        producto_id
    ))

    conn.commit()
    conn.close()

    return True, f"{p['nombre']} equipado."


def desequipar_tipo(user_id, tipo):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        DELETE FROM equipamiento_tienda
        WHERE user_id = ?
          AND tipo = ?
    """, (
        user_id,
        tipo
    ))

    conn.commit()
    conn.close()


def producto_equipado(user_id, tipo):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT producto_id
        FROM equipamiento_tienda
        WHERE user_id = ?
          AND tipo = ?
    """, (
        user_id,
        tipo
    ))

    fila = c.fetchone()

    conn.close()

    if not fila:
        return None

    return PRODUCTOS.get(fila[0])


def equipados_usuario(user_id):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT tipo, producto_id
        FROM equipamiento_tienda
        WHERE user_id = ?
    """, (user_id,))

    filas = c.fetchall()

    conn.close()

    resultado = {}

    for tipo, producto_id in filas:
        if producto_id in PRODUCTOS:
            resultado[tipo] = PRODUCTOS[producto_id]

    # Unifica el slot visual de marcos.
    if "marco_animado" in resultado:
        resultado["marco"] = resultado["marco_animado"]

    return resultado


def inventario_usuario(user_id, tipo=None):
    init_tienda_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if tipo:
        c.execute("""
            SELECT i.producto_id
            FROM inventario_tienda i
            JOIN tienda_productos p
                ON p.producto_id = i.producto_id
            WHERE i.user_id = ?
              AND p.tipo = ?
            ORDER BY p.precio DESC
        """, (
            user_id,
            tipo
        ))
    else:
        c.execute("""
            SELECT producto_id
            FROM inventario_tienda
            WHERE user_id = ?
        """, (user_id,))

    filas = c.fetchall()

    conn.close()

    return [
        PRODUCTOS[pid]
        for (pid,) in filas
        if pid in PRODUCTOS
    ]


def multiplicador_recompensa(user_id, categoria, recurso):
    init_tienda_db()

    mult = 1.0

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT p.producto_id
        FROM inventario_tienda i
        JOIN tienda_productos p
            ON p.producto_id = i.producto_id
        WHERE i.user_id = ?
          AND p.tipo = 'bonus'
    """, (user_id,))

    ids = [fila[0] for fila in c.fetchall()]

    conn.close()

    for pid in ids:
        p = PRODUCTOS.get(pid)

        if not p:
            continue

        bonus_tipo = p.get("bonus_tipo")

        if recurso == "xp":
            if bonus_tipo in (categoria, "xp"):
                mult = max(
                    mult,
                    p.get("multiplicador", 1.0)
                )

        elif recurso == "tokens":
            if bonus_tipo == "tokens":
                mult = max(
                    mult,
                    p.get("multiplicador", 1.0)
                )

    return mult


def aplicar_bonus_xp(user_id, cantidad, categoria):
    from core.db import sumar_xp

    if cantidad <= 0:
        return sumar_xp(user_id, cantidad)

    multiplicador = multiplicador_recompensa(
        user_id,
        categoria,
        "xp"
    )

    cantidad_final = max(
        1,
        int(round(cantidad * multiplicador))
    )

    return sumar_xp(
        user_id,
        cantidad_final
    )


def cantidad_con_bonus_tokens(user_id, cantidad, categoria):
    if cantidad <= 0:
        return cantidad

    multiplicador = multiplicador_recompensa(
        user_id,
        categoria,
        "tokens"
    )

    return max(
        1,
        int(math.ceil(cantidad * multiplicador))
    )
    return max(
        1,
        int(math.ceil(cantidad * multiplicador))
    )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.db import esta_registrado, obtener_datos

from core.tienda import (
    PRODUCTOS,
    init_tienda_db,
    comprar_producto,
    equipar_producto,
    tiene_producto,
    inventario_usuario,
    equipados_usuario,
)


CATEGORIAS = {
    "bonus": "🧪 BONUS",
    "mascotas": "🐾 MASCOTAS",
    "comida": "🍖 COMIDA",
    "accesorios": "🎀 ACCESORIOS DE MASCOTA",
    "titulos": "🏷️ TÍTULOS",
    "accesorios2": "👤 ACCESORIOS 2",
    "marcos": "🖼️ MARCOS",
    "efectos": "✨ EFECTOS ANIMADOS",
    "colores": "🎨 COLORES DEL NOMBRE",
    "insignias": "🏅 INSIGNIAS",
    "fondos": "🌌 FONDOS",
}

POR_PAGINA = 7


def balance(user_id):
    datos = obtener_datos(user_id)

    return datos[2] if datos else 0


def teclado_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🧪 Bonus",
                callback_data="shop_cat_bonus"
            ),
            InlineKeyboardButton(
                "🐾 Mascotas",
                callback_data="shop_cat_mascotas"
            ),
        ],
        [
            InlineKeyboardButton(
                "🍖 Comida",
                callback_data="shop_cat_comida"
            ),
            InlineKeyboardButton(
                "🎀 Accesorios",
                callback_data="shop_cat_accesorios"
            ),
        ],
        [
            InlineKeyboardButton(
                "🏷️ Títulos",
                callback_data="shop_cat_titulos"
            ),
            InlineKeyboardButton(
                "👤 Accesorios 2",
                callback_data="shop_cat_accesorios2"
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Cerrar",
                callback_data="shop_close"
            )
        ],
    ])


def texto_principal(user_id):
    return (
        "🛒 *TIENDA REIDISTUDIOSBOT*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Saldo: *{balance(user_id):,} tokens*\n\n"
        "Elige una categoría:\n\n"
        "🧪 Bonus → mejoras para juegos\n"
        "🐾 Mascotas → próximamente\n"
        "🍖 Comida → próximamente\n"
        "🎀 Accesorios → accesorios para mascotas\n"
        "🏷️ Títulos → títulos para tu perfil\n"
        "👤 Accesorios 2 → marcos, efectos y más"
    )


def ids_categoria(categoria):
    return [
        pid
        for pid, p in PRODUCTOS.items()
        if p["categoria"] == categoria
    ]


def teclado_categoria(categoria, pagina=0):
    ids = ids_categoria(categoria)

    inicio = pagina * POR_PAGINA

    pagina_ids = ids[
        inicio:
        inicio + POR_PAGINA
    ]

    botones = []

    for pid in pagina_ids:
        p = PRODUCTOS[pid]

        botones.append([
            InlineKeyboardButton(
                f"{p['nombre']} · {p['precio']:,}💰",
                callback_data=f"shop_item_{pid}"
            )
        ])

    nav = []

    if pagina > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Anterior",
                callback_data=f"shop_page_{categoria}_{pagina - 1}"
            )
        )

    if inicio + POR_PAGINA < len(ids):
        nav.append(
            InlineKeyboardButton(
                "Siguiente ➡️",
                callback_data=f"shop_page_{categoria}_{pagina + 1}"
            )
        )

    if nav:
        botones.append(nav)

    botones.append([
        InlineKeyboardButton(
            "🎒 Mi inventario",
            callback_data=f"shop_inv_{categoria}"
        ),
        InlineKeyboardButton(
            "🔙 Tienda",
            callback_data="shop_home"
        ),
    ])

    return InlineKeyboardMarkup(botones)


def teclado_accesorios2():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🖼️ Marcos",
                callback_data="shop_sub_marcos"
            )
        ],
        [
            InlineKeyboardButton(
                "✨ Efectos",
                callback_data="shop_sub_efectos"
            )
        ],
        [
            InlineKeyboardButton(
                "🎨 Colores del nombre",
                callback_data="shop_sub_colores"
            )
        ],
        [
            InlineKeyboardButton(
                "🏅 Insignias",
                callback_data="shop_sub_insignias"
            )
        ],
        [
            InlineKeyboardButton(
                "🌌 Fondos",
                callback_data="shop_sub_fondos"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Tienda",
                callback_data="shop_home"
            )
        ],
    ])


# IMPORTANTE:
# Los tipos reales de PRODUCTOS son:
# marco
# marco_animado
# efecto
# color
# insignia
# fondo

SUBCATEGORIA_MAP = {
    "marcos": (
        "marcos",
        ("marco", "marco_animado")
    ),
    "efectos": (
        "efectos",
        ("efecto",)
    ),
    "colores": (
        "accesorios2",
        ("color",)
    ),
    "insignias": (
        "accesorios2",
        ("insignia",)
    ),
    "fondos": (
        "accesorios2",
        ("fondo",)
    ),
}


def ids_subcategoria(subcategoria):
    categoria, tipos = SUBCATEGORIA_MAP[subcategoria]

    return [
        pid
        for pid, p in PRODUCTOS.items()
        if (
            p["categoria"] == categoria
            and p["tipo"] in tipos
        )
    ]


def teclado_subcategoria(subcategoria, pagina=0):
    ids = ids_subcategoria(subcategoria)

    inicio = pagina * POR_PAGINA

    pagina_ids = ids[
        inicio:
        inicio + POR_PAGINA
    ]

    botones = []

    for pid in pagina_ids:
        p = PRODUCTOS[pid]

        botones.append([
            InlineKeyboardButton(
                f"{p['nombre']} · {p['precio']:,}💰",
                callback_data=f"shop_item_{pid}"
            )
        ])

    nav = []

    if pagina > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️ Anterior",
                callback_data=(
                    f"shop_subpage_"
                    f"{subcategoria}_"
                    f"{pagina - 1}"
                )
            )
        )

    if inicio + POR_PAGINA < len(ids):
        nav.append(
            InlineKeyboardButton(
                "Siguiente ➡️",
                callback_data=(
                    f"shop_subpage_"
                    f"{subcategoria}_"
                    f"{pagina + 1}"
                )
            )
        )

    if nav:
        botones.append(nav)

    botones.append([
        InlineKeyboardButton(
            "🎒 Inventario",
            callback_data=f"shop_invsub_{subcategoria}"
        ),
        InlineKeyboardButton(
            "🔙 Accesorios 2",
            callback_data="shop_cat_accesorios2"
        ),
    ])

    return InlineKeyboardMarkup(botones)


def texto_subcategoria(user_id, subcategoria, pagina=0):
    ids = ids_subcategoria(subcategoria)

    total = max(
        1,
        (len(ids) + POR_PAGINA - 1) // POR_PAGINA
    )

    return (
        f"{CATEGORIAS[subcategoria]}\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Saldo: *{balance(user_id):,} tokens*\n"
        f"📦 Página {pagina + 1}/{total}\n\n"
        "Pulsa un producto para verlo."
    )


def texto_categoria(user_id, categoria, pagina=0):
    if categoria == "accesorios2":
        return (
            "👤 *ACCESORIOS 2*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Saldo: *{balance(user_id):,} tokens*\n\n"
            "Elige qué parte de tu perfil quieres personalizar."
        )

    if categoria in (
        "mascotas",
        "comida",
        "accesorios"
    ):
        return (
            f"{CATEGORIAS[categoria]}\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "🚧 *En desarrollo*\n\n"
            "Esta sección todavía no está disponible.\n"
            "Próximamente habrá contenido nuevo aquí."
        )

    ids = ids_categoria(categoria)

    total_paginas = max(
        1,
        (len(ids) + POR_PAGINA - 1) // POR_PAGINA
    )

    return (
        f"{CATEGORIAS[categoria]}\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Saldo: *{balance(user_id):,} tokens*\n"
        f"📦 Página {pagina + 1}/{total_paginas}\n\n"
        "Pulsa un producto para ver sus detalles."
    )


def teclado_detalle(pid, user_id):
    p = PRODUCTOS[pid]

    comprado = tiene_producto(
        user_id,
        pid
    )

    filas = []

    if comprado:
        filas.append([
            InlineKeyboardButton(
                "✅ Comprado",
                callback_data="shop_noop"
            )
        ])

        if p["tipo"] != "bonus":
            filas.append([
                InlineKeyboardButton(
                    "⚙️ Equipar",
                    callback_data=f"shop_equip_{pid}"
                )
            ])
        else:
            filas.append([
                InlineKeyboardButton(
                    "⚡ Activar",
                    callback_data=f"shop_equip_{pid}"
                )
            ])
    else:
        filas.append([
            InlineKeyboardButton(
                "🛒 Comprar",
                callback_data=f"shop_buy_{pid}"
            )
        ])

    filas.append([
        InlineKeyboardButton(
            "🔙 Volver",
            callback_data=f"shop_back_{p['categoria']}"
        )
    ])

    return InlineKeyboardMarkup(filas)


def texto_detalle(pid, user_id):
    p = PRODUCTOS[pid]

    comprado = tiene_producto(
        user_id,
        pid
    )

    estado = (
        "\n\n✅ Ya lo tienes en tu inventario."
        if comprado
        else ""
    )

    return (
        f"{p['nombre']}\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"📖 {p['descripcion']}\n\n"
        f"💰 Precio: *{p['precio']:,} tokens*\n"
        f"💳 Tu saldo: *{balance(user_id):,} tokens*"
        f"{estado}"
    )


def teclado_confirmacion(pid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Confirmar",
                callback_data=f"shop_confirm_{pid}"
            ),
            InlineKeyboardButton(
                "❌ Cancelar",
                callback_data=f"shop_item_{pid}"
            ),
        ],
    ])


async def tienda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not esta_registrado(user_id):
        await update.message.reply_text(
            "🔒 Debes registrarte primero con /reg nombre.pais"
        )
        return

    init_tienda_db()

    await update.message.reply_text(
        texto_principal(user_id),
        parse_mode="Markdown",
        reply_markup=teclado_principal()
    )


async def tienda_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_tienda_db()

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not esta_registrado(user_id):
        await query.edit_message_text(
            "🔒 Debes registrarte primero con /reg nombre.pais"
        )
        return

    if data == "shop_close":
        await query.edit_message_text(
            "🛒 Tienda cerrada."
        )
        return

    if data == "shop_home":
        await query.edit_message_text(
            texto_principal(user_id),
            parse_mode="Markdown",
            reply_markup=teclado_principal()
        )
        return

    if data == "shop_noop":
        return

    if data.startswith("shop_cat_"):
        categoria = data[len("shop_cat_"):]

        if categoria not in CATEGORIAS:
            return

        markup = (
            teclado_accesorios2()
            if categoria == "accesorios2"
            else teclado_categoria(categoria)
        )

        await query.edit_message_text(
            texto_categoria(
                user_id,
                categoria
            ),
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    if data.startswith("shop_sub_"):
        subcategoria = data[len("shop_sub_"):]

        if subcategoria not in SUBCATEGORIA_MAP:
            return

        await query.edit_message_text(
            texto_subcategoria(
                user_id,
                subcategoria
            ),
            parse_mode="Markdown",
            reply_markup=teclado_subcategoria(
                subcategoria
            )
        )
        return

    if data.startswith("shop_subpage_"):
        partes = data.split("_", 3)

        if len(partes) != 4:
            return

        _, _, subcategoria, pagina = partes

        if subcategoria not in SUBCATEGORIA_MAP:
            return

        pagina = int(pagina)

        await query.edit_message_text(
            texto_subcategoria(
                user_id,
                subcategoria,
                pagina
            ),
            parse_mode="Markdown",
            reply_markup=teclado_subcategoria(
                subcategoria,
                pagina
            )
        )
        return

    if data.startswith("shop_page_"):
        partes = data.split("_", 3)

        if len(partes) != 4:
            return

        _, _, categoria, pagina = partes

        if categoria not in CATEGORIAS:
            return

        pagina = int(pagina)

        await query.edit_message_text(
            texto_categoria(
                user_id,
                categoria,
                pagina
            ),
            parse_mode="Markdown",
            reply_markup=teclado_categoria(
                categoria,
                pagina
            )
        )
        return

    if data.startswith("shop_item_"):
        pid = data[len("shop_item_"):]

        if pid not in PRODUCTOS:
            return

        await query.edit_message_text(
            texto_detalle(
                pid,
                user_id
            ),
            parse_mode="Markdown",
            reply_markup=teclado_detalle(
                pid,
                user_id
            )
        )
        return

    if data.startswith("shop_buy_"):
        pid = data[len("shop_buy_"):]

        if pid not in PRODUCTOS:
            return

        p = PRODUCTOS[pid]

        await query.edit_message_text(
            "🛒 *CONFIRMAR COMPRA*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 {p['nombre']}\n"
            f"💰 Precio: *{p['precio']:,} tokens*\n"
            f"💳 Saldo actual: *{balance(user_id):,} tokens*\n\n"
            "¿Quieres comprarlo?",
            parse_mode="Markdown",
            reply_markup=teclado_confirmacion(pid)
        )
        return

    if data.startswith("shop_confirm_"):
        pid = data[len("shop_confirm_"):]

        if pid not in PRODUCTOS:
            return

        ok, mensaje = comprar_producto(
            user_id,
            pid
        )

        p = PRODUCTOS[pid]

        if ok:

            if p["tipo"] == "bonus":
                equipar_producto(
                    user_id,
                    pid
                )

            await query.edit_message_text(
                "✅ *COMPRA REALIZADA*\n"
                "━━━━━━━━━━━━━━━━━━━\n\n"
                f"📦 {p['nombre']}\n"
                f"💰 {mensaje}\n\n"
                f"💳 Saldo restante: "
                f"*{balance(user_id):,} tokens*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🔙 Volver a la categoría",
                            callback_data=(
                                f"shop_back_"
                                f"{p['categoria']}"
                            )
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🏠 Tienda",
                            callback_data="shop_home"
                        )
                    ],
                ])
            )
        else:
            await query.edit_message_text(
                f"❌ {mensaje}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🔙 Volver",
                            callback_data=f"shop_item_{pid}"
                        )
                    ]
                ])
            )

        return

    if data.startswith("shop_equip_"):
        pid = data[len("shop_equip_"):]

        if pid not in PRODUCTOS:
            return

        ok, mensaje = equipar_producto(
            user_id,
            pid
        )

        await query.edit_message_text(
            f"{'✅' if ok else '❌'} {mensaje}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Volver",
                        callback_data=f"shop_item_{pid}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 Tienda",
                        callback_data="shop_home"
                    )
                ],
            ])
        )
        return

    if data.startswith("shop_back_"):
        categoria = data[len("shop_back_"):]

        if categoria in SUBCATEGORIA_MAP:
            await query.edit_message_text(
                texto_subcategoria(
                    user_id,
                    categoria
                ),
                parse_mode="Markdown",
                reply_markup=teclado_subcategoria(
                    categoria
                )
            )
        else:
            markup = (
                teclado_accesorios2()
                if categoria == "accesorios2"
                else teclado_categoria(categoria)
            )

            await query.edit_message_text(
                texto_categoria(
                    user_id,
                    categoria
                ),
                parse_mode="Markdown",
                reply_markup=markup
            )

        return

    if data.startswith("shop_invsub_"):
        subcategoria = data[len("shop_invsub_"):]

        if subcategoria not in SUBCATEGORIA_MAP:
            return

        ids = set(
            ids_subcategoria(subcategoria)
        )

        items = []

        for pid in ids:
            if tiene_producto(user_id, pid):
                items.append(PRODUCTOS[pid])

        equipados = equipados_usuario(user_id)

        ids_equipados = {
            producto["nombre"]
            for producto in equipados.values()
            if producto
        }

        if not items:
            texto = (
                "🎒 *INVENTARIO*\n"
                "━━━━━━━━━━━━━━━━━━━\n\n"
                "No tienes productos de esta sección."
            )
        else:
            lineas = [
                "🎒 *INVENTARIO*",
                "━━━━━━━━━━━━━━━━━━━",
                ""
            ]

            for item in items:
                marca = (
                    " ⚡ ACTIVO"
                    if item["nombre"] in ids_equipados
                    else ""
                )

                lineas.append(
                    f"• {item['nombre']}{marca}"
                )

            texto = "\n".join(lineas)

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Volver",
                        callback_data=(
                            f"shop_sub_{subcategoria}"
                        )
                    )
                ]
            ])
        )
        return

    if data.startswith("shop_inv_"):
        categoria = data[len("shop_inv_"):]

        if categoria == "bonus":
            items = inventario_usuario(
                user_id,
                "bonus"
            )

        elif categoria == "titulos":
            items = inventario_usuario(
                user_id,
                "titulo"
            )

        elif categoria == "accesorios2":
            items = [
                producto
                for producto in inventario_usuario(user_id)
                if producto["categoria"] == "accesorios2"
            ]

        else:
            items = []

        if not items:
            texto = (
                "🎒 *INVENTARIO*\n"
                "━━━━━━━━━━━━━━━━━━━\n\n"
                "Todavía no tienes productos "
                "de esta categoría."
            )
        else:
            equipados = equipados_usuario(
                user_id
            )

            ids_equipados = {
                producto["nombre"]
                for producto in equipados.values()
                if producto
            }

            lineas = [
                "🎒 *INVENTARIO*",
                "━━━━━━━━━━━━━━━━━━━",
                ""
            ]

            for producto in items:
                marca = (
                    " ⚡ ACTIVO"
                    if producto["nombre"] in ids_equipados
                    else ""
                )

                lineas.append(
                    f"• {producto['nombre']}{marca}"
                )

            texto = "\n".join(lineas)

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Volver",
                        callback_data=f"shop_cat_{categoria}"
                    )
                ]
            ])
        )

        return

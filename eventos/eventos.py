import sqlite3
import time
import importlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from core.db import obtener_datos, obtener_todos_los_usuarios, obtener_pais, DB_PATH
from core.paises import obtener_zona, obtener_nombre as nombre_pais

COOLDOWN_NORMAL = 10 * 60 * 60
COOLDOWN_EXPIRADO = 1 * 60 * 60
TIEMPO_CONFIRMACION = 5 * 60

ZONA_ADMIN = "America/Havana"  # Los eventos se crean en hora de Cuba

eventos_en_vista = {}
eventos_esperando_inicio = {}

ADMINS = [7669914531]


def init_eventos_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT,
            hora TEXT,
            fecha_exp TEXT,
            hora_exp TEXT,
            lv INTEGER DEFAULT 0,
            id_evento TEXT,
            archivo TEXT,
            activo INTEGER DEFAULT 1,
            notificado_inicio INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS asistentes (
            user_id INTEGER,
            evento_id INTEGER,
            PRIMARY KEY (user_id, evento_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS eventos_cooldown (
            user_id INTEGER PRIMARY KEY,
            ultima_asistencia REAL
        )
    """)
    conn.commit()
    conn.close()


def es_admin(user_id):
    return user_id in ADMINS


def parsear_fecha(fecha_str):
    partes = fecha_str.strip().split("/")
    if len(partes) != 3:
        return None
    try:
        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])
        if anio < 100:
            anio += 2000
        return datetime(anio, mes, dia)
    except ValueError:
        return None


def combinar_fecha_hora_local(fecha_str, hora_str, zona):
    dt_fecha = parsear_fecha(fecha_str)
    if dt_fecha is None:
        return None
    try:
        dt_hora = datetime.strptime(hora_str.strip(), "%H:%M")
    except ValueError:
        return None
    dt = dt_fecha.replace(hour=dt_hora.hour, minute=dt_hora.minute)
    return dt.replace(tzinfo=ZoneInfo(zona))


def combinar_fecha_hora_utc(fecha_str, hora_str, zona=ZONA_ADMIN):
    dt_local = combinar_fecha_hora_local(fecha_str, hora_str, zona)
    if dt_local is None:
        return None
    return dt_local.astimezone(timezone.utc)


def hora_para_usuario(fecha_str, hora_str, user_id):
    dt_utc = combinar_fecha_hora_utc(fecha_str, hora_str)
    if dt_utc is None:
        return fecha_str, hora_str

    pais = obtener_pais(user_id)
    zona = obtener_zona(pais) if pais else ZONA_ADMIN

    dt_local = dt_utc.astimezone(ZoneInfo(zona))
    return dt_local.strftime("%d/%m/%y"), dt_local.strftime("%H:%M")


def formatear_tiempo(seg):
    return f"{seg // 3600}h {(seg % 3600) // 60}m"


def obtener_asistentes(evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM asistentes WHERE evento_id = ?", (evento_id,))
    ids = [f[0] for f in c.fetchall()]
    conn.close()
    return ids


def esta_asistiendo(user_id, evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM asistentes WHERE user_id = ? AND evento_id = ?", (user_id, evento_id))
    r = c.fetchone()
    conn.close()
    return r is not None


def agregar_asistente(user_id, evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO asistentes (user_id, evento_id) VALUES (?, ?)", (user_id, evento_id))
    conn.commit()
    conn.close()


def get_cooldown_eventos(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ultima_asistencia FROM eventos_cooldown WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 0


def set_cooldown_eventos(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO eventos_cooldown (user_id, ultima_asistencia) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    conn.close()


def tiempo_restante_cooldown(user_id):
    ultima = get_cooldown_eventos(user_id)
    if ultima == 0:
        return 0
    return max(0, int(COOLDOWN_NORMAL - (time.time() - ultima)))


def listar_eventos_activos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre, descripcion, fecha, hora, fecha_exp, hora_exp, lv, id_evento, archivo FROM eventos WHERE activo = 1 ORDER BY fecha ASC")
    eventos = c.fetchall()
    conn.close()
    return eventos


def obtener_evento_por_nombre_o_id(busqueda):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, nombre, descripcion, fecha, hora, fecha_exp, hora_exp, lv, id_evento, archivo "
        "FROM eventos WHERE activo = 1 AND (LOWER(nombre) = LOWER(?) OR id_evento = ?)",
        (busqueda, busqueda)
    )
    r = c.fetchone()
    conn.close()
    return r


def eliminar_evento(evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM asistentes WHERE evento_id = ?", (evento_id,))
    c.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()


def marcar_evento_notificado(evento_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE eventos SET notificado_inicio = 1 WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()


async def notificar_a_todos(context, texto):
    for uid in obtener_todos_los_usuarios():
        try:
            await context.bot.send_message(chat_id=uid, text=texto, parse_mode="HTML")
        except Exception:
            pass


async def eventos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        await update.message.reply_text("🔒 Debes estar registrado.")
        return

    lista = listar_eventos_activos()
    if not lista:
        await update.message.reply_text("📅 *No hay eventos disponibles.*", parse_mode="Markdown")
        return

    pais = obtener_pais(user_id)
    zona_nombre = nombre_pais(pais) if pais else "Cuba"

    texto = f"📅 *EVENTOS DISPONIBLES*\n━━━━━━━━━━━━━━━━━━━\n"
    texto += f"🌎 Hora local: {zona_nombre}\n\n"

    for i, ev in enumerate(lista, 1):
        eid, nom, desc, fecha, hora, fecha_exp, hora_exp, lv, id_ev, archivo = ev
        fecha_local, hora_local = hora_para_usuario(fecha, hora, user_id)
        restriccion = f"🔒 Nivel mín. {lv}" if lv > 0 else "🔓 Sin restricción"
        texto += f"{i}. *{nom}*\n   🆔 ID: `{id_ev}`\n   📅 {fecha_local} - {hora_local}\n   {restriccion}\n\n"

    texto += "Usa `.nombre` o `.id` para ver los detalles."
    await update.message.reply_text(texto, parse_mode="Markdown")


async def ver_evento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    if texto.lower() in [".asistir", ".atras", ".comenzar", ".cancelar"]:
        return
    if not texto.startswith("."):
        return

    busqueda = texto[1:].strip()
    if not busqueda:
        return

    if busqueda.isdigit():
        return

    evento = obtener_evento_por_nombre_o_id(busqueda)
    if evento is None:
        return

    (eid, nom, desc, fecha, hora, fecha_exp, hora_exp, lv, id_ev, archivo) = evento
    eventos_en_vista[user_id] = eid

    datos = obtener_datos(user_id)
    nivel_usuario = datos[4]
    pais = obtener_pais(user_id)
    zona_nombre = nombre_pais(pais) if pais else "Cuba"

    fecha_local, hora_local = hora_para_usuario(fecha, hora, user_id)
    fecha_exp_local, hora_exp_local = hora_para_usuario(fecha_exp, hora_exp, user_id)

    restriccion = f"🔒 Nivel mínimo: *{lv}*" if lv > 0 else "🔓 Sin restricción"
    puede = nivel_usuario >= lv if lv > 0 else True

    texto_info = (
        f"📅 *EVENTO: {nom}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Descripción:*\n{desc}\n\n"
        f"🕐 *Inicio:* {fecha_local} a las {hora_local} ({zona_nombre})\n"
        f"🕓 *Expira:* {fecha_exp_local} a las {hora_exp_local} ({zona_nombre})\n"
        f"{restriccion}\n"
        f"🆔 ID: `{id_ev}`\n\n"
    )

    if esta_asistiendo(user_id, eid):
        texto_info += "✅ *Ya estás apuntado.*"
    elif not puede:
        texto_info += f"❌ *No cumples el nivel mínimo.*\nTu nivel: {nivel_usuario}"
    else:
        texto_info += "📌 `.asistir` para apuntarte.\n📌 `.atras` para volver."

    await update.message.reply_text(texto_info, parse_mode="Markdown")
    raise ApplicationHandlerStop


async def asistir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    evento_id = eventos_en_vista.get(user_id)

    if evento_id is None:
        await update.message.reply_text("❌ No estás viendo ningún evento. Usa `/eventos`.", parse_mode="Markdown")
        raise ApplicationHandlerStop

    datos = obtener_datos(user_id)
    if datos is None or datos[5] != 1:
        raise ApplicationHandlerStop

    restante = tiempo_restante_cooldown(user_id)
    if restante > 0:
        await update.message.reply_text(f"⏳ Espera *{formatear_tiempo(restante)}*.", parse_mode="Markdown")
        raise ApplicationHandlerStop

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nombre, lv FROM eventos WHERE id = ? AND activo = 1", (evento_id,))
    r = c.fetchone()
    conn.close()

    if r is None:
        await update.message.reply_text("❌ Evento ya no existe.")
        raise ApplicationHandlerStop

    nombre_evento, lv = r

    if esta_asistiendo(user_id, evento_id):
        await update.message.reply_text("⚠️ Ya estás apuntado.")
        raise ApplicationHandlerStop

    if lv > 0 and datos[4] < lv:
        await update.message.reply_text(f"❌ Necesitas nivel *{lv}*.", parse_mode="Markdown")
        raise ApplicationHandlerStop

    agregar_asistente(user_id, evento_id)
    await update.message.reply_text(f"✅ *¡Apuntado a {nombre_evento}!*", parse_mode="Markdown")
    raise ApplicationHandlerStop


async def atras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    eventos_en_vista.pop(user_id, None)
    await eventos(update, context)
    raise ApplicationHandlerStop


async def comenzar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    evento_id = None
    for eid, info in eventos_esperando_inicio.items():
        if user_id in info["pendientes"]:
            evento_id = eid
            break

    if evento_id is None:
        await update.message.reply_text("❌ No estás en ningún evento activo.")
        raise ApplicationHandlerStop

    info = eventos_esperando_inicio[evento_id]
    if user_id in info["pendientes"]:
        info["pendientes"].remove(user_id)
    if user_id not in info["confirmados"]:
        info["confirmados"].append(user_id)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT archivo, nombre FROM eventos WHERE id = ?", (evento_id,))
    r = c.fetchone()
    conn.close()

    if r is None:
        raise ApplicationHandlerStop

    archivo, nombre = r
    if not archivo:
        await update.message.reply_text("❌ Evento sin archivo configurado.")
        raise ApplicationHandlerStop

    try:
        modulo = importlib.import_module(archivo)
        funcion = getattr(modulo, f"iniciar_{archivo}")
        await funcion(update, context)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    raise ApplicationHandlerStop


async def cancelar_evento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    for eid, info in eventos_esperando_inicio.items():
        if user_id in info["pendientes"]:
            info["pendientes"].remove(user_id)
            await update.message.reply_text("❌ Cancelado.")
            set_cooldown_eventos(user_id)
            raise ApplicationHandlerStop
        if user_id in info["confirmados"]:
            info["confirmados"].remove(user_id)
            await update.message.reply_text("❌ Cancelado.")
            set_cooldown_eventos(user_id)
            raise ApplicationHandlerStop
    await update.message.reply_text("❌ No estás en ningún evento.")
    raise ApplicationHandlerStop


async def addevent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not es_admin(user_id):
        await update.message.reply_text("❌ Sin permiso.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/addevent nombre|desc|fecha|hora|fecha_exp|hora_exp|lv|id|archivo`\n\n"
            "⏰ *Las horas que pongas son en hora de Cuba.*",
            parse_mode="Markdown"
        )
        return

    partes = " ".join(context.args).split("|")
    if len(partes) != 9:
        await update.message.reply_text("❌ Debes separar los 9 campos con `|`.", parse_mode="Markdown")
        return

    nombre, desc, fecha, hora, fecha_exp, hora_exp, lv_str, id_evento, archivo = [p.strip() for p in partes]

    if combinar_fecha_hora_local(fecha, hora, ZONA_ADMIN) is None or combinar_fecha_hora_local(fecha_exp, hora_exp, ZONA_ADMIN) is None:
        await update.message.reply_text("❌ Fechas u horas inválidas.")
        return

    try:
        lv = int(lv_str)
    except ValueError:
        await update.message.reply_text("❌ El nivel debe ser número.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO eventos (nombre, descripcion, fecha, hora, fecha_exp, hora_exp, lv, id_evento, archivo, activo, notificado_inicio) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)",
        (nombre, desc, fecha, hora, fecha_exp, hora_exp, lv, id_evento, archivo)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Evento *{nombre}* añadido.\n⏰ Horas en zona de Cuba.",
        parse_mode="Markdown"
    )

    for uid in obtener_todos_los_usuarios():
        try:
            fecha_local, hora_local = hora_para_usuario(fecha, hora, uid)
            fecha_exp_local, hora_exp_local = hora_para_usuario(fecha_exp, hora_exp, uid)
            pais = obtener_pais(uid)
            zona_nombre = nombre_pais(pais) if pais else "Cuba"

            texto_notif = (
                f"🎉 <b>¡NUEVO EVENTO DISPONIBLE!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📅 <b>{nombre}</b>\n📝 {desc}\n\n"
                f"🕐 Inicio: <b>{fecha_local}</b> a las <b>{hora_local}</b> ({zona_nombre})\n"
                f"🕓 Expira: <b>{fecha_exp_local}</b> a las <b>{hora_exp_local}</b>\n"
                f"🆔 ID: <code>{id_evento}</code>\n\n"
                f"Consulta <code>/eventos</code>."
            )
            await context.bot.send_message(chat_id=uid, text=texto_notif, parse_mode="HTML")
        except Exception:
            pass


async def removeevent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not es_admin(user_id):
        await update.message.reply_text("❌ Sin permiso.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/removeevent <nombre>|<id>`", parse_mode="Markdown")
        return

    partes = " ".join(context.args).split("|")
    if len(partes) != 2:
        await update.message.reply_text("❌ Separa con `|`.", parse_mode="Markdown")
        return

    nombre, id_evento = [p.strip() for p in partes]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM eventos WHERE LOWER(nombre) = LOWER(?) AND id_evento = ? AND activo = 1", (nombre, id_evento))
    r = c.fetchone()
    conn.close()

    if r is None:
        await update.message.reply_text("❌ No se encontró.")
        return

    eid = r[0]
    asistentes = obtener_asistentes(eid)
    eliminar_evento(eid)

    for uid in asistentes:
        try:
            await context.bot.send_message(chat_id=uid, text=f"🗑️ <b>Evento eliminado</b>\nEl evento <b>{nombre}</b> ha sido eliminado.", parse_mode="HTML")
        except Exception:
            pass

    await update.message.reply_text(f"✅ Eliminado. Avisados: {len(asistentes)}.", parse_mode="Markdown")


async def editevent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not es_admin(user_id):
        await update.message.reply_text("❌ Sin permiso.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Uso: `/editevent nombre|id|desc|nombre_nuevo|fecha|hora|fecha_exp|hora_exp|lv|archivo`\n\n"
            "⏰ *Las horas son en hora de Cuba.*",
            parse_mode="Markdown"
        )
        return

    partes = " ".join(context.args).split("|")
    if len(partes) != 10:
        await update.message.reply_text("❌ Debes separar 10 campos con `|`.", parse_mode="Markdown")
        return

    (nombre, id_evento, desc, nombre_nuevo, fecha, hora, fecha_exp, hora_exp, lv_str, archivo) = [p.strip() for p in partes]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, nombre, descripcion, fecha, hora, fecha_exp, hora_exp, lv, id_evento, archivo "
        "FROM eventos WHERE LOWER(nombre) = LOWER(?) AND id_evento = ? AND activo = 1",
        (nombre, id_evento)
    )
    r = c.fetchone()
    conn.close()

    if r is None:
        await update.message.reply_text("❌ No se encontró.")
        return

    (eid, n_act, d_act, f_act, h_act, fe_act, he_act, lv_act, id_act, arch_act) = r

    nuevo_nombre = n_act if nombre_nuevo == "*" else ("" if nombre_nuevo == "-" else nombre_nuevo)
    nueva_desc = d_act if desc == "*" else ("" if desc == "-" else desc)
    nueva_fecha = f_act if fecha == "*" else ("" if fecha == "-" else fecha)
    nueva_hora = h_act if hora == "*" else ("" if hora == "-" else hora)
    nueva_fecha_exp = fe_act if fecha_exp == "*" else ("" if fecha_exp == "-" else fecha_exp)
    nueva_hora_exp = he_act if hora_exp == "*" else ("" if hora_exp == "-" else hora_exp)
    nuevo_archivo = arch_act if archivo == "*" else ("" if archivo == "-" else archivo)

    if lv_str == "*":
        nuevo_lv = lv_act
    elif lv_str == "-":
        nuevo_lv = 0
    else:
        try:
            nuevo_lv = int(lv_str)
        except ValueError:
            await update.message.reply_text("❌ El nivel debe ser número, `*` o `-`.")
            return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE eventos SET nombre=?, descripcion=?, fecha=?, hora=?, fecha_exp=?, hora_exp=?, lv=?, archivo=? WHERE id=?",
        (nuevo_nombre, nueva_desc, nueva_fecha, nueva_hora, nueva_fecha_exp, nueva_hora_exp, nuevo_lv, nuevo_archivo, eid)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Evento actualizado.", parse_mode="Markdown")


async def revisar_eventos_iniciando(context) -> None:
    ahora = datetime.now(timezone.utc)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre, fecha, hora, id_evento FROM eventos WHERE activo = 1 AND notificado_inicio = 0")
    lista = c.fetchall()
    conn.close()

    for eid, nombre, fecha, hora, id_ev in lista:
        dt_inicio = combinar_fecha_hora_utc(fecha, hora, ZONA_ADMIN)
        if dt_inicio is None:
            continue

        if ahora >= dt_inicio:
            marcar_evento_notificado(eid)
            asistentes = obtener_asistentes(eid)
            if not asistentes:
                continue

            eventos_esperando_inicio[eid] = {
                "confirmados": [],
                "pendientes": asistentes.copy(),
                "iniciado": False,
                "hora_aviso": time.time()
            }

            for uid in asistentes:
                try:
                    pais = obtener_pais(uid)
                    zona_nombre = nombre_pais(pais) if pais else "Cuba"
                    texto = (
                        f"🎉 <b>¡EL EVENTO VA A COMENZAR!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 <b>{nombre}</b>\n"
                        f"⏰ Hora: {zona_nombre}\n\n"
                        f"Responde <code>.comenzar</code> para participar.\n"
                        f"Responde <code>.cancelar</code> para no participar.\n\n"
                        f"⏱️ 5 minutos o serás descalificado."
                    )
                    await context.bot.send_message(chat_id=uid, text=texto, parse_mode="HTML")
                except Exception:
                    pass


async def revisar_descalificados(context) -> None:
    ahora = time.time()
    for eid, info in list(eventos_esperando_inicio.items()):
        if info["iniciado"]:
            continue
        if ahora - info["hora_aviso"] > TIEMPO_CONFIRMACION:
            pendientes = info["pendientes"].copy()
            info["pendientes"] = []
            info["iniciado"] = True

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nombre FROM eventos WHERE id = ?", (eid,))
            r = c.fetchone()
            conn.close()
            nombre_evento = r[0] if r else "Evento"

            for uid in pendientes:
                set_cooldown_eventos(uid)
                try:
                    await context.bot.send_message(chat_id=uid, text=f"⏰ <b>Descalificado</b>\nNo respondiste a tiempo.", parse_mode="HTML")
                except Exception:
                    pass


async def revisar_eventos_expirados(context) -> None:
    ahora = datetime.now(timezone.utc)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre, fecha_exp, hora_exp FROM eventos WHERE activo = 1")
    lista = c.fetchall()
    conn.close()

    for eid, nombre, fecha_exp, hora_exp in lista:
        dt_exp = combinar_fecha_hora_utc(fecha_exp, hora_exp, ZONA_ADMIN)
        if dt_exp is None:
            continue
        if ahora >= dt_exp:
            asistentes = obtener_asistentes(eid)
            eliminar_evento(eid)
            for uid in asistentes:
                set_cooldown_eventos(uid)
            texto = f"🏁 <b>EVENTO TERMINADO</b>\nEl evento <b>{nombre}</b> ha terminado."
            await notificar_a_todos(context, texto)

"""
Preferencias de idioma y traducción automática de los mensajes del bot.
La traducción utiliza MyMemory; si el servicio falla, el bot envía el texto original.
"""
import asyncio
import inspect
import logging
import re
import sqlite3
from functools import lru_cache
from urllib.parse import quote

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.db import DB_PATH

logger = logging.getLogger(__name__)
_DB_INITIALIZED = False

IDIOMAS = {
    "es": {"nombre": "Español", "native": "Español", "api": "es", "aliases": ("es", "espanol", "español", "spanish", "castellano")},
    "en": {"nombre": "English", "native": "English", "api": "en", "aliases": ("en", "english", "ingles", "inglés")},
    "ja": {"nombre": "日本語", "native": "日本語", "api": "ja", "aliases": ("ja", "japanese", "japones", "japonés", "日本語")},
    "zh": {"nombre": "中文", "native": "中文", "api": "zh-CN", "aliases": ("zh", "chinese", "chino", "中文", "mandarin")},
    "ko": {"nombre": "한국어", "native": "한국어", "api": "ko", "aliases": ("ko", "korean", "coreano", "한국어")},
    "fr": {"nombre": "Français", "native": "Français", "api": "fr", "aliases": ("fr", "french", "frances", "francés", "français")},
    "pt": {"nombre": "Português", "native": "Português", "api": "pt", "aliases": ("pt", "portuguese", "portugues", "portugués", "português")},
    "de": {"nombre": "Deutsch", "native": "Deutsch", "api": "de", "aliases": ("de", "german", "aleman", "alemán", "deutsch")},
    "it": {"nombre": "Italiano", "native": "Italiano", "api": "it", "aliases": ("it", "italian", "italiano")},
    "ru": {"nombre": "Русский", "native": "Русский", "api": "ru", "aliases": ("ru", "russian", "ruso", "русский")},
    "ar": {"nombre": "العربية", "native": "العربية", "api": "ar", "aliases": ("ar", "arabic", "arabe", "árabe", "العربية")},
    "hi": {"nombre": "हिन्दी", "native": "हिन्दी", "api": "hi", "aliases": ("hi", "hindi", "हिन्दी")},
    "nl": {"nombre": "Nederlands", "native": "Nederlands", "api": "nl", "aliases": ("nl", "dutch", "neerlandes", "neerlandés", "nederlands")},
    "pl": {"nombre": "Polski", "native": "Polski", "api": "pl", "aliases": ("pl", "polish", "polaco", "polski")},
    "tr": {"nombre": "Türkçe", "native": "Türkçe", "api": "tr", "aliases": ("tr", "turkish", "turco", "türkçe")},
    "uk": {"nombre": "Українська", "native": "Українська", "api": "uk", "aliases": ("uk", "ukrainian", "ucraniano", "українська")},
    "sv": {"nombre": "Svenska", "native": "Svenska", "api": "sv", "aliases": ("sv", "swedish", "sueco", "svenska")},
    "el": {"nombre": "Ελληνικά", "native": "Ελληνικά", "api": "el", "aliases": ("el", "greek", "griego", "ελληνικά")},
    "vi": {"nombre": "Tiếng Việt", "native": "Tiếng Việt", "api": "vi", "aliases": ("vi", "vietnamese", "vietnamita", "tiếng việt")},
    "id": {"nombre": "Bahasa Indonesia", "native": "Bahasa Indonesia", "api": "id", "aliases": ("id", "indonesian", "indonesio", "bahasa indonesia")},
    "th": {"nombre": "ไทย", "native": "ไทย", "api": "th", "aliases": ("th", "thai", "tailandés", "tailandes", "ไทย")},
}

def init_idiomas_db():
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS preferencias_idioma (
                user_id INTEGER PRIMARY KEY,
                idioma TEXT NOT NULL DEFAULT 'es',
                seleccionado INTEGER NOT NULL DEFAULT 0,
                actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    _DB_INITIALIZED = True

def normalizar_alias(texto):
    return " ".join((texto or "").strip().lower().replace("_", " ").split())

_ALIAS_A_CODIGO = {
    normalizar_alias(alias): codigo
    for codigo, info in IDIOMAS.items()
    for alias in info["aliases"]
}

def resolver_idioma(texto):
    return _ALIAS_A_CODIGO.get(normalizar_alias(texto))

def obtener_idioma(user_id):
    init_idiomas_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT idioma FROM preferencias_idioma WHERE user_id = ?",
            (int(user_id),)
        ).fetchone()
    return row[0] if row and row[0] in IDIOMAS else "es"

def idioma_seleccionado(user_id):
    init_idiomas_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT seleccionado FROM preferencias_idioma WHERE user_id = ?",
            (int(user_id),)
        ).fetchone()
    return bool(row and row[0])

def guardar_idioma(user_id, codigo, seleccionado=True):
    if codigo not in IDIOMAS:
        raise ValueError("Código de idioma no válido.")
    init_idiomas_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO preferencias_idioma(user_id, idioma, seleccionado)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                idioma = excluded.idioma,
                seleccionado = excluded.seleccionado,
                actualizado = CURRENT_TIMESTAMP
        """, (int(user_id), codigo, 1 if seleccionado else 0))

# Protege etiquetas HTML, fragmentos <code>, comandos y tokens Markdown habituales.
_PROTECTED_RE = re.compile(
    r'(<[^>]+>|`[^`]*`|/[\w@]+(?:\s+[\w.-]+)?|https?://\S+|'
    r'\*{1,2}|_{1,2}|~{2}|={2,})',
    re.UNICODE
)
_CACHE = {}
_CACHE_LOCK = asyncio.Lock()

async def _traducir_segmento(texto, destino):
    if not texto.strip() or destino == "es":
        return texto
    key = (destino, texto)
    if key in _CACHE:
        return _CACHE[key]
    url = "https://api.mymemory.translated.net/get"
    params = {"q": texto[:490], "langpair": f"es|{IDIOMAS[destino]['api']}"}
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return texto
                data = await response.json(content_type=None)
                translated = data.get("responseData", {}).get("translatedText")
                if not translated or data.get("responseStatus") not in (None, 200, "200"):
                    return texto
                translated = (translated.replace("&lt;", "<")
                              .replace("&gt;", ">").replace("&amp;", "&"))
                _CACHE[key] = translated
                return translated
    except Exception as exc:
        logger.debug("No se pudo traducir el mensaje: %s", exc)
        return texto

async def traducir_texto(texto, destino):
    if not texto or destino == "es" or destino not in IDIOMAS:
        return texto
    # El servicio gratuito limita la longitud de la consulta. Separa por segmentos
    # protegidos para conservar etiquetas, comandos, URLs y marcadores.
    partes = _PROTECTED_RE.split(str(texto))
    resultado = []
    for parte in partes:
        if not parte:
            continue
        if _PROTECTED_RE.fullmatch(parte):
            resultado.append(parte)
        else:
            # MyMemory acepta consultas cortas; divide párrafos largos por palabras.
            if len(parte) <= 480:
                resultado.append(await _traducir_segmento(parte, destino))
            else:
                palabras = parte.split(" ")
                trozo = ""
                traducidos = []
                for palabra in palabras:
                    candidato = f"{trozo} {palabra}".strip()
                    if len(candidato) > 450 and trozo:
                        traducidos.append(await _traducir_segmento(trozo, destino))
                        trozo = palabra
                    else:
                        trozo = candidato
                if trozo:
                    traducidos.append(await _traducir_segmento(trozo, destino))
                resultado.append(" ".join(traducidos))
    return "".join(resultado)

def instalar_traduccion_automatica(bot):
    """Traduce textos enviados en chats privados según el idioma del usuario."""
    # PTB methods receive chat_id for regular chats; inline-message edits without
    # chat_id are left unchanged.
    async def instalar():
        for nombre, campo in (
            ("send_message", "text"),
            ("edit_message_text", "text"),
            ("send_photo", "caption"),
            ("send_video", "caption"),
            ("send_document", "caption"),
            ("send_animation", "caption"),
        ):
            await envolver(nombre, campo)
    # This function is synchronous, wrappers are installed without awaiting.
    for nombre, campo in (
        ("send_message", "text"),
        ("edit_message_text", "text"),
        ("send_photo", "caption"),
        ("send_video", "caption"),
        ("send_document", "caption"),
        ("send_animation", "caption"),
    ):
        original = getattr(bot, nombre, None)
        if original is None:
            continue
        firma = inspect.signature(original)
        async def metodo(*args, __original=original, __firma=firma, __campo=campo, __nombre=nombre, **kwargs):
            llamada_args, llamada_kwargs = args, kwargs
            try:
                bound = __firma.bind_partial(*args, **kwargs)
                chat_id = bound.arguments.get("chat_id")
                texto = bound.arguments.get(__campo)
                # Solo se traducen chats privados, nunca grupos.
                if isinstance(chat_id, int) and chat_id > 0:
                    idioma = obtener_idioma(chat_id)
                    if idioma != "es":
                        if isinstance(texto, str):
                            bound.arguments[__campo] = await traducir_texto(texto, idioma)
                        markup = bound.arguments.get("reply_markup")
                        if isinstance(markup, InlineKeyboardMarkup):
                            filas = []
                            for fila in markup.inline_keyboard:
                                nueva_fila = []
                                for boton in fila:
                                    # Los botones para elegir idioma conservan su nombre nativo.
                                    if getattr(boton, "callback_data", None) and boton.callback_data.startswith("lang:"):
                                        nueva_fila.append(boton)
                                        continue
                                    if getattr(boton, "text", None):
                                        datos_boton = boton.to_dict()
                                        datos_boton["text"] = await traducir_texto(boton.text, idioma)
                                        nueva_fila.append(InlineKeyboardButton(**datos_boton))
                                    else:
                                        nueva_fila.append(boton)
                                filas.append(nueva_fila)
                            bound.arguments["reply_markup"] = InlineKeyboardMarkup(filas)
                llamada_args, llamada_kwargs = bound.args, bound.kwargs
            except Exception as exc:
                logger.debug("Falló la traducción automática de %s: %s", __nombre, exc)
            return await __original(*llamada_args, **llamada_kwargs)
        setattr(bot, nombre, metodo)

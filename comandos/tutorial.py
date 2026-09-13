from telegram import Update
from telegram.ext import ContextTypes


async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "📖 <b>TUTORIAL DE REIDISTUDIOSBOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "¡Bienvenido/a! 🎉\n\n"
        "1️⃣ <b>¿CÓMO EMPIEZO?</b>\n"
        "<blockquote>Lo primero es registrarte. Sin registro no puedes usar la mayoría de comandos.</blockquote>\n"
        "Escribe: <code>/reg TuNombre</code>\n\n"
        "2️⃣ <b>COMANDOS BÁSICOS</b>\n"
        "<code>/start</code> → Iniciar\n"
        "<code>/help</code> → Ayuda\n"
        "<code>/reg</code> → Registrarte\n"
        "<code>/unreg</code> → Cerrar sesión\n"
        "<code>/deletereg</code> → Eliminar cuenta\n\n"
        "3️⃣ <b>TU PERFIL</b>\n"
        "<code>/perfil</code> → Ver todo\n"
        "<code>/tokens</code> → Ver tokens\n"
        "<code>/nivel</code> → Ver nivel\n"
        "<code>/rango</code> → Ver rango\n"
        "<code>/userslist</code> → Lista de usuarios\n\n"
        "4️⃣ <b>SISTEMA DE NIVELES</b>\n"
        "<blockquote>Cada nivel cuesta 500 XP más que el anterior. Del nivel 1 al 500.</blockquote>\n\n"
        "5️⃣ <b>BANCO</b>\n"
        "<code>/bank</code> → Ver cuenta\n"
        "<code>/depositar cantidad</code> → Guardar\n"
        "<code>/retirar cantidad</code> → Sacar\n\n"
        "6️⃣ <b>RECOMPENSA DIARIA</b>\n"
        "<code>/reclamar</code> → Recompensa cada 24h\n\n"
        "7️⃣ <b>EVENTOS</b>\n"
        "<code>/eventos</code> → Ver eventos\n\n"
        "8️⃣ <b>MINIJUEGOS</b>\n"
        "<code>/actividades</code> → Ver todos\n\n"
        "9️⃣ <b>CONSEJOS</b>\n"
        "<blockquote>• Los comandos no distinguen mayúsculas.\n"
        "• Puedes escribir <code>.SI</code>, <code>.Si</code> o <code>.si</code>.\n"
        "• Mientras juegas un minijuego, no puedes usar otros comandos.</blockquote>\n\n"
        "¡Ya estás listo/a! Escribe <code>/reg TuNombre</code> y a jugar. 🚀"
    )
    await update.message.reply_text(texto, parse_mode="HTML")

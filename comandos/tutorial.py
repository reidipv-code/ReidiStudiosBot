from telegram import Update
from telegram.ext import ContextTypes


async def tutorial(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    texto = (
        "📖 <b>TUTORIAL DE REIDISTUDIOSBOT MMORPG</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "¡Bienvenido/a al MMORPG! ⚔️\n\n"

        "1️⃣ <b>CREAR TU PERSONAJE</b>\n"
        "Escribe tu nombre y país:\n"
        "<code>/reg TuNombre.cuba</code>\n\n"
        "Después elige una raza mediante los botones.\n"
        "Por último, selecciona una clase compatible.\n\n"
        "⚠️ No podrás utilizar los sistemas del MMORPG "
        "hasta completar los tres pasos.\n\n"

        "2️⃣ <b>¿PARA QUÉ SIRVE EL PAÍS?</b>\n"
        "🌎 Se utiliza exclusivamente para calcular "
        "la zona horaria de los eventos. No determina "
        "tu raza, clase ni estadísticas.\n\n"

        "3️⃣ <b>COMANDOS BÁSICOS</b>\n"
        "<code>/start</code> → Iniciar el bot\n"
        "<code>/reg Nombre.Pais</code> → Registrarte\n"
        "<code>/menu</code> → Abrir el menú del MMORPG\n"
        "<code>/help</code> → Ayuda y comandos\n"
        "<code>/tutorial</code> → Ver este tutorial\n"
        "<code>/perfil</code> → Consultar tu personaje\n"
        "<code>/perfil Nombre</code> → Consultar la raza "
        "y clase de otro personaje\n\n"

        "4️⃣ <b>PROGRESIÓN</b>\n"
        "<code>/tokens</code> → Consultar tus tokens\n"
        "<code>/nivel</code> → Consultar nivel y XP\n"
        "<code>/rango</code> → Consultar tu rango\n"
        "<code>/logros</code> → Consultar logros\n"
        "<code>/misiones</code> → Consultar misiones\n\n"

        "5️⃣ <b>BANCO Y RECOMPENSAS</b>\n"
        "<code>/bank</code> → Consultar el banco\n"
        "<code>/depositar cantidad</code> → Depositar tokens\n"
        "<code>/retirar cantidad</code> → Retirar tokens\n"
        "<code>/reclamar</code> → Reclamar recompensa diaria\n\n"

        "6️⃣ <b>JUEGOS</b>\n"
        "<code>/actividades</code> → Ver actividades\n"
        "<code>/juegos</code> → Ver juegos\n"
        "<code>/mates</code> → Matemáticas\n"
        "<code>/trivia</code> → Preguntas y respuestas\n"
        "<code>/memoria</code> → Juego de memoria\n"
        "<code>/palabras</code> → Juego de palabras\n"
        "<code>/dados</code> → Tirar los dados\n"
        "<code>/funks</code> → Adivinar canciones\n"
        "<code>/ruleta</code> → Ruleta\n\n"

        "7️⃣ <b>EVENTOS</b>\n"
        "<code>/eventos</code> → Consultar eventos\n\n"

        "8️⃣ <b>CONSEJOS</b>\n"
        "• Solo puedes crear un personaje.\n"
        "• Elige cuidadosamente tu raza y clase.\n"
        "• Tu raza proporciona bonificaciones.\n"
        "• Cada clase tiene estadísticas y habilidades.\n"
        "• Durante una partida no puedes utilizar otros "
        "comandos hasta terminarla.\n\n"

        "¡Completa tu registro y comienza tu aventura! 🚀"
    )

    mensaje = update.effective_message

    if mensaje:
        await mensaje.reply_text(
            texto,
            parse_mode="HTML",
        )
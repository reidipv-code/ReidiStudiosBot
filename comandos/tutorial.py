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
        "Después debes elegir una raza y una clase "
        "compatible con ella usando los botones.\n\n"
        "⚠️ No podrás usar los sistemas del MMORPG "
        "hasta completar los tres pasos.\n\n"

        "2️⃣ <b>¿PARA QUÉ SIRVE EL PAÍS?</b>\n"
        "🌎 El país se utiliza exclusivamente para calcular "
        "la zona horaria de los eventos. No determina tu raza, "
        "clase ni estadísticas.\n\n"

        "3️⃣ <b>COMANDOS BÁSICOS</b>\n"
        "<code>/start</code> → Iniciar el bot\n"
        "<code>/reg Nombre.Pais</code> → Registro\n"
        "<code>/menu</code> → Menú del MMORPG\n"
        "<code>/help</code> → Ayuda y comandos\n"
        "<code>/perfil</code> → Tu personaje y estadísticas\n"
        "<code>/perfil Nombre</code> → Raza y clase de otro\n\n"

        "4️⃣ <b>PROGRESIÓN</b>\n"
        "<code>/tokens</code> → Consultar tokens\n"
        "<code>/nivel</code> → Consultar nivel y XP\n"
        "<code>/rango</code> → Consultar rango\n"
        "<code>/logros</code> → Consultar logros\n"
        "<code>/misiones</code> → Misiones diarias\n\n"

        "5️⃣ <b>BANCO Y RECOMPENSAS</b>\n"
        "<code>/bank</code> → Consultar banco\n"
        "<code>/depositar cantidad</code> → Depositar tokens\n"
        "<code>/retirar cantidad</code> → Retirar tokens\n"
        "<code>/reclamar</code> → Recompensa diaria\n\n"

        "6️⃣ <b>JUEGOS</b>\n"
        "<code>/actividades</code> → Ver actividades\n"
        "<code>/mates</code> → Juego de matemáticas\n"
        "<code>/trivia</code> → Juego de preguntas\n"
        "<code>/memoria</code> → Juego de memoria\n"
        "<code>/palabras</code> → Juego de palabras\n"
        "<code>/dados</code> → Tirar los dados\n"
        "<code>/funks</code> → Adivinar canciones\n\n"

        "7️⃣ <b>EVENTOS</b>\n"
        "<code>/eventos</code> → Ver eventos disponibles\n\n"

        "8️⃣ <b>CONSEJOS</b>\n"
        "• No puedes crear más de un personaje.\n"
        "• Elige cuidadosamente tu raza y clase.\n"
        "• La raza proporciona bonificaciones.\n"
        "• Las clases tienen estadísticas y habilidades propias.\n"
        "• Mientras juegas una partida, no puedes usar "
        "otros comandos hasta terminarla.\n\n"

        "¡Completa tu registro y comienza tu aventura! 🚀"
    )

    await update.effective_message.reply_text(
        texto,
        parse_mode="HTML",
    )
import asyncio
import subprocess
import sys

from chat.chat_bot import iniciar_chat_bot


async def main():
    print("🚀 Arrancando los dos bots...")

    # Lanzamos el bot principal como subproceso
    p1 = subprocess.Popen([sys.executable, "bot_railway.py"])

    # Arrancamos el bot del chat en el bucle de eventos actual
    await iniciar_chat_bot()

    # Esperar a que el bot principal termine (nunca, salvo error)
    p1.wait()


if __name__ == "__main__":
    asyncio.run(main())

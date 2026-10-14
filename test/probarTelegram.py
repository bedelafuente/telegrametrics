import os
from pathlib import Path

import telepot
from dotenv import load_dotenv

ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ruta_env)

chat_id = int(os.environ["TELEGRAM_CHAT_ID"])

tokens = [
    os.environ[f"TELEGRAM_BOT_TOKEN_{numero}"]
    for numero in range(1, 5)
]

for numero, token in enumerate(tokens, start=1):
    bot = telepot.Bot(token)
    bot.sendMessage(
        chat_id,
        f"Monitor ambiental {numero}: conexión con Python confirmada."
    )
    print(f"Bot {numero}: mensaje enviado.")
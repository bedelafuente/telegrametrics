from getpass import getpass
import telepot

token = getpass("Token del primer bot: ")
bot = telepot.Bot(token)

actualizaciones = bot.getUpdates()

chats = {}
for actualizacion in actualizaciones:
    mensaje = actualizacion.get("message", {})
    chat = mensaje.get("chat", {})

    if chat.get("type") == "private":
        chats[chat["id"]] = chat.get("first_name", "")

if chats:
    for chat_id, nombre in chats.items():
        print(f"Chat de {nombre}: {chat_id}")
else:
    print("Envía un mensaje nuevo a tu bot y vuelve a ejecutar.")
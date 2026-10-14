"""Recibe mediciones MQTT y envía reportes al bot elegido."""

import argparse
import math
import os
from collections import deque
from pathlib import Path
from queue import Empty, Queue

import paho.mqtt.client as mqtt
import telepot
from dotenv import load_dotenv

from graficos import crear_grafico

HOST = "127.0.0.1"
PORT = 1883
CAMPOS = {
    "DATA/MP": ["MP1", "MP2.5", "MP10"],
    "DATA/MA": ["Temperatura", "Humedad"],
}


def crear_historial():
    historial = {}
    for nombres in CAMPOS.values():
        for nombre in nombres:
            historial[nombre] = deque(maxlen=10)
    return historial


def guardar_medicion(historial, tema, texto):
    """Valida todo el mensaje antes de agregar sus valores al historial."""
    nombres = CAMPOS[tema]
    partes = texto.split(",")
    if len(partes) != len(nombres):
        raise ValueError("Cantidad de valores incorrecta")

    valores = []
    for parte in partes:
        valor = float(parte)
        if not math.isfinite(valor):
            raise ValueError("La medición debe ser un número finito")
        valores.append(valor)

    for nombre, valor in zip(nombres, valores):
        historial[nombre].append(valor)


def al_conectar(cliente, mensajes, banderas, codigo, propiedades):
    if codigo.is_failure:
        print(f"Conexión rechazada: {codigo}", flush=True)
        return
    cliente.subscribe([("DATA/MP", 0), ("DATA/MA", 0)])
    print("Conectado a Mosquitto. Solicitando suscripciones…", flush=True)


def al_suscribir(cliente, mensajes, identificador, codigos, propiedades):
    if any(codigo.is_failure for codigo in codigos):
        print("No se pudieron confirmar todas las suscripciones.", flush=True)
    else:
        print("Suscripciones confirmadas. Esperando mediciones…", flush=True)


def al_recibir(cliente, mensajes, mensaje):
    if mensaje.topic not in CAMPOS:
        return
    try:
        texto = mensaje.payload.decode("utf-8").strip()
    except UnicodeDecodeError:
        print("Mensaje ignorado: no contiene texto UTF-8.", flush=True)
        return
    # MQTT sigue recibiendo mientras el programa dibuja o envía a Telegram.
    mensajes.put((mensaje.topic, texto))


def enviar_reporte(bot, chat_id, ruta, numero_bot):
    with open(ruta, "rb") as imagen:
        bot.sendPhoto(
            chat_id,
            imagen,
            caption=f"Monitor {numero_bot}: últimas 10 mediciones por variable.",
        )


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--bot", type=int, choices=[1, 2, 3, 4], default=1)
    numero_bot = argumentos.parse_args().bot

    carpeta = Path(__file__).resolve().parent
    load_dotenv(carpeta / ".env")
    token = os.getenv(f"TELEGRAM_BOT_TOKEN_{numero_bot}")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise SystemExit("Falta el token del bot o TELEGRAM_CHAT_ID en .env")
    try:
        chat_id = int(chat)
    except ValueError:
        raise SystemExit("TELEGRAM_CHAT_ID debe ser un número entero")

    bot = telepot.Bot(token)
    historial = crear_historial()
    recibidos = {"DATA/MP": 0, "DATA/MA": 0}
    mensajes = Queue()
    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"monitor-ambiental-{numero_bot}",
        userdata=mensajes,
    )
    cliente.on_connect = al_conectar
    cliente.on_subscribe = al_suscribir
    cliente.on_message = al_recibir

    try:
        cliente.connect(HOST, PORT, keepalive=60)
    except OSError:
        raise SystemExit("No se pudo conectar. Comprueba que Mosquitto esté activo.")

    cliente.loop_start()
    print(f"Monitor {numero_bot} iniciado. Detener con Ctrl+C.", flush=True)
    try:
        while True:
            try:
                tema, texto = mensajes.get(timeout=1)
            except Empty:
                continue

            try:
                guardar_medicion(historial, tema, texto)
            except ValueError:
                print(f"Mensaje inválido en {tema}; se ignora.", flush=True)
                continue

            recibidos[tema] += 1
            print(f"{tema}: {texto} | Nuevos: {recibidos}", flush=True)

            # Ambos temas deben aportar al menos 10 mensajes nuevos.
            if recibidos["DATA/MP"] < 10 or recibidos["DATA/MA"] < 10:
                continue

            ruta = carpeta / "reportes" / f"monitor_{numero_bot}.png"
            crear_grafico(historial, ruta, numero_bot)
            try:
                enviar_reporte(bot, chat_id, ruta, numero_bot)
                print(f"Reporte enviado por el bot {numero_bot}.", flush=True)
            except Exception as error:
                # No imprimir URLs de errores: podrían contener el token.
                print(
                    f"No se pudo enviar ({type(error).__name__}). "
                    f"El gráfico quedó en {ruta}. Se intentará con el próximo reporte.",
                    flush=True,
                )
            recibidos = {"DATA/MP": 0, "DATA/MA": 0}
    except KeyboardInterrupt:
        print("\nSuscriptor detenido.")
    finally:
        cliente.disconnect()
        cliente.loop_stop()


if __name__ == "__main__":
    main()

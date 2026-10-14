import random
import time

import paho.mqtt.publish as publish

HOST = "127.0.0.1"
PORT = 1883


def generar_mp():
    return f"{random.randint(4, 10)},{random.randint(10, 50)},{random.randint(10, 50)}\n"


def generar_ma():
    return f"{random.randint(10, 22)},{random.randint(60, 85)}\n"


def main():
    try:
        while True:
            tema = random.choice(["DATA/MP", "DATA/MA"])
            mensaje = generar_mp() if tema == "DATA/MP" else generar_ma()
            publish.single(tema, payload=mensaje, hostname=HOST, port=PORT)
            print(f"Publicado en {tema}: {mensaje.strip()}", flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nPublicador detenido.")
    except OSError as error:
        raise SystemExit(f"No se pudo publicar en {HOST}:{PORT}. Comprueba Mosquitto. {error}")


if __name__ == "__main__":
    main()

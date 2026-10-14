# Proyecto 2 — MQTT y reportes de Telegram

Primera etapa: comunicar un publicador y un suscriptor mediante Mosquitto.
Pendiente: historial de 10 datos por variable, gráficos con matplotlib y cuatro
suscriptores con cuatro bots de Telegram mediante telepot.

## Preparación

Desde esta carpeta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Ubuntu, instalar el broker por separado:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

Si no se usa el servicio, ejecutar `mosquitto -v` en una terminal y mantenerla
abierta. No ejecutar otra instancia si el puerto 1883 ya está ocupado.
Los scripts utilizan 127.0.0.1:1883. Mosquitto 2 sin configuración adicional
permite las pruebas locales.

## Prueba

En una terminal, activar el entorno y ejecutar:

```bash
python suscriptor.py
```

Esperar «Suscripción confirmada». En otra terminal, desde la misma carpeta:

```bash
source .venv/bin/activate
python publicador.py
```

Cada cinco segundos el publicador elige aleatoriamente uno de los temas:

- `DATA/MP`: MP1, MP2.5 y MP10, separados por comas.
- `DATA/MA`: temperatura y humedad relativa, separadas por comas.

El suscriptor debe imprimir el mismo tema y contenido. Detener con Ctrl+C.
Esta etapa no guarda mensajes publicados antes de iniciar la suscripción.

## Repositorio

Crear un repositorio privado y vacío en GitHub. Desde esta carpeta:

```bash
git init -b main
git add .
git commit -m "Inicia comunicación MQTT del proyecto 2"
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

`.gitignore` excluye el entorno virtual y archivos `.env` para configuración
privada de los bots en etapas posteriores.

Referencias: [Paho MQTT](https://eclipse.dev/paho/clients/python/docs/)
y [Mosquitto local](https://mosquitto.org/documentation/migrating-to-2-0/).

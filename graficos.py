import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def crear_grafico(historial, ruta, numero_bot):
    variables = ["MP1", "MP2.5", "MP10", "Temperatura", "Humedad"]
    unidades = ["µg/m³", "µg/m³", "µg/m³", "°C", "%"]
    colores = ["blue", "green", "red", "darkorange", "purple"]
    figura, ejes = plt.subplots(5, 1, figsize=(9, 10), sharex=True)
    try:
        for eje, nombre, unidad, color in zip(ejes, variables, unidades, colores):
            valores = list(historial[nombre])
            posiciones = range(1, len(valores) + 1)
            eje.plot(posiciones, valores, marker="o", color=color, label=nombre)
            eje.set_ylabel(unidad)
            eje.grid(True, alpha=0.3)
            eje.legend(loc="upper right")

        ejes[-1].set_xlabel("Muestra por variable (1 = más antigua)")
        ejes[-1].set_xticks(range(1, 11))
        figura.suptitle(f"Monitor ambiental {numero_bot} — últimas 10 mediciones")
        # Los temas llegan por separado: los índices no son tiempos compartidos.
        figura.tight_layout(rect=(0, 0, 1, 0.96))
        ruta.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(ruta, dpi=130)
    finally:
        plt.close(figura)

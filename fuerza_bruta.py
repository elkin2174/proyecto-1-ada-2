from itertools import permutations
from math import factorial
from pathlib import Path
import time

from f_auxiliares import (
    costo_total,
    leer_finca,
    escribir_salida,
    obtener_archivos_entrada,
)

# Límite práctico para evitar que fuerza bruta se quede ejecutando demasiado.
# Si quieren probar con más, pueden subirlo, pero no es recomendable.
MAX_N_FUERZA_BRUTA = 10


def roFB(finca):
    """
    Función principal de fuerza bruta.

    Objetivo:
        Resolver el problema de riego óptimo probando todas las posibles
        permutaciones de los tablones y escogiendo la de menor costo.

    Recibe:
        finca: lista de tablones.
            Cada tablón tiene la forma (ts, tr, p, rp).

    Retorna:
        Una pareja (mejor_orden, mejor_costo), donde:
            mejor_orden: permutación óptima encontrada.
            mejor_costo: costo mínimo encontrado.

    Observación:
        Este algoritmo siempre encuentra la solución óptima porque revisa
        todas las soluciones posibles. Sin embargo, es costoso:
        O(n · n!).
    """

    n = len(finca)

    mejor_orden = ()
    mejor_costo = float("inf")

    total_permutaciones = factorial(n)
    contador = 0
    inicio_tiempo = time.time()

    print(f"Fuerza bruta con n = {n}")
    print(f"Permutaciones totales: {total_permutaciones}")

    for orden in permutations(range(n)):
        contador += 1

        costo = costo_total(finca, orden)

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_orden = orden
            print(f"Nuevo mejor costo: {mejor_costo} con orden {list(mejor_orden)}")

        if contador % 100000 == 0:
            tiempo_actual = time.time() - inicio_tiempo
            porcentaje = (contador / total_permutaciones) * 100

            print(
                f"Procesadas {contador}/{total_permutaciones} "
                f"({porcentaje:.2f}%) - Tiempo: {tiempo_actual:.2f} s"
            )

    return list(mejor_orden), mejor_costo


def procesar_todas_las_entradas(carpeta_entrada="Tests", carpeta_salida="output_fb"):
    """
    Función auxiliar de ejecución.

    Objetivo:
        Leer todos los archivos *_in.txt de una carpeta, ejecutar fuerza bruta
        y guardar las salidas generadas.

    Recibe:
        carpeta_entrada: carpeta donde están los archivos de entrada.
        carpeta_salida: carpeta donde se guardarán las salidas.

    Retorna:
        No retorna valor. Genera archivos de salida e imprime resumen.
    """

    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(exist_ok=True)

    archivos_entrada = obtener_archivos_entrada(carpeta_entrada)

    if not archivos_entrada:
        print(f"No se encontraron archivos *_in.txt en {carpeta_entrada}.")
        return

    for ruta_entrada in archivos_entrada:
        print("------------------------------")
        print(f"Procesando: {ruta_entrada.name}")

        try:
            finca = leer_finca(ruta_entrada)
            n = len(finca)

            print(f"Número de tablones: {n}")

            if n > MAX_N_FUERZA_BRUTA:
                print(
                    f"Saltado: n = {n} es muy grande para fuerza bruta. "
                    f"Máximo permitido: {MAX_N_FUERZA_BRUTA}."
                )
                continue

            inicio = time.perf_counter()
            orden, costo = roFB(finca)
            tiempo_ms = (time.perf_counter() - inicio) * 1000

            nombre_salida = ruta_entrada.name.replace("_in.txt", "_out.txt")
            ruta_salida = carpeta_salida / nombre_salida

            escribir_salida(ruta_salida, orden, costo)

            print(f"Costo mínimo: {costo}")
            print(f"Orden óptimo: {orden}")
            print(f"Tiempo de ejecución: {tiempo_ms:.3f} ms")
            print(f"Salida generada: {ruta_salida}")

        except Exception as error:
            print(f"Error procesando {ruta_entrada.name}: {error}")


if __name__ == "__main__":
    procesar_todas_las_entradas()
"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo: Fuerza bruta (roFB).

Prueba todas las permutaciones y escoge la de menor costo: O(n · n!).
Las funciones base (costos, E/S, batch, CLI) viven en f_auxiliares.py.
"""

import sys
import time
from itertools import permutations
from math import factorial

from f_auxiliares import costo_total, ejecutar_cli

# Límite práctico para que fuerza bruta no se quede ejecutando demasiado.
MAX_N_FUERZA_BRUTA = 10


def roFB(finca, verbose=True):
    """
    Resuelve el riego óptimo probando todas las permutaciones de tablones.

    Recibe:
        finca: lista de tablones (ts, tr, p, rp).
        verbose: si True, imprime el progreso en consola.

    Retorna:
        (mejor_orden, mejor_costo). Siempre es óptimo, pero es O(n · n!).
    """
    n = len(finca)
    mejor_orden = ()
    mejor_costo = float("inf")

    total_permutaciones = factorial(n)
    contador = 0
    inicio_tiempo = time.time()

    if verbose:
        print(f"Fuerza bruta con n = {n}")
        print(f"Permutaciones totales: {total_permutaciones}")

    for orden in permutations(range(n)):
        contador += 1
        costo = costo_total(finca, orden)

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_orden = orden
            if verbose:
                print(f"Nuevo mejor costo: {mejor_costo} con orden {list(mejor_orden)}")

        if verbose and contador % 100000 == 0:
            tiempo_actual = time.time() - inicio_tiempo
            porcentaje = (contador / total_permutaciones) * 100
            print(
                f"Procesadas {contador}/{total_permutaciones} "
                f"({porcentaje:.2f}%) - Tiempo: {tiempo_actual:.2f} s"
            )

    return list(mejor_orden), mejor_costo


def main() -> int:
    return ejecutar_cli(
        sys.argv,
        lambda finca: roFB(finca, verbose=False),
        carpeta_salida="output_fb",
        etiqueta="fuerza bruta",
        nombre_script="fuerza_bruta.py",
        max_n=MAX_N_FUERZA_BRUTA,
        etiqueta_costo="Costo óptimo",
    )


if __name__ == "__main__":
    raise SystemExit(main())

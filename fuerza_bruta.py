from itertools import permutations
from math import factorial
from pathlib import Path
import sys
import time

from f_auxiliares import (
    costo_total,
    leer_finca,
    escribir_salida,
    obtener_archivos_entrada,
)

# Límite práctico para evitar que fuerza bruta se quede ejecutando demasiado.
MAX_N_FUERZA_BRUTA = 10


def roFB(finca, verbose=True):
    """
    Función principal de fuerza bruta.

    Objetivo:
        Resolver el problema de riego óptimo probando todas las posibles
        permutaciones de los tablones y escogiendo la de menor costo.

    Recibe:
        finca: lista de tablones.
            Cada tablón tiene la forma (ts, tr, p, rp).
        verbose: si True, imprime progreso en consola.

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


def procesar_todas_las_entradas(carpeta_entrada="tests", carpeta_salida="output_fb"):
    """
    Lee todos los *_in.txt, ejecuta roFB y guarda salidas en carpeta_salida.
    """
    carpeta_salida_path = Path(carpeta_salida)
    carpeta_salida_path.mkdir(exist_ok=True)

    archivos_entrada = obtener_archivos_entrada(carpeta_entrada)
    if not archivos_entrada:
        print(f"No se encontraron archivos *_in.txt en {carpeta_entrada}.")
        return

    print(f"\n{'=' * 65}")
    print(f"  Batch fuerza bruta — {len(archivos_entrada)} archivo(s)")
    print(f"  Entrada : {Path(carpeta_entrada).resolve()}")
    print(f"  Salida  : {carpeta_salida_path.resolve()}")
    print(f"{'=' * 65}")
    print(f"  {'Archivo':<18} {'n':<4} {'Costo':<10} {'Esperado':<10} {'Match':<7} {'t(ms)'}")
    print(f"  {'-' * 58}")

    coincidencias = 0
    con_esperado = 0

    for ruta_entrada in archivos_entrada:
        nombre_base = ruta_entrada.name
        try:
            finca = leer_finca(ruta_entrada)
            n = len(finca)

            if n > MAX_N_FUERZA_BRUTA:
                print(f"  {nombre_base:<18} Saltado (n={n} > {MAX_N_FUERZA_BRUTA})")
                continue

            inicio = time.perf_counter()
            orden, costo = roFB(finca, verbose=False)
            tiempo_ms = (time.perf_counter() - inicio) * 1000

            nombre_salida = nombre_base.replace("_in.txt", "_out.txt")
            ruta_salida = carpeta_salida_path / nombre_salida
            escribir_salida(ruta_salida, orden, costo)

            match = "-"
            costo_esperado = "-"
            ruta_esperado = ruta_entrada.parent / nombre_salida
            if not ruta_esperado.exists():
                ruta_esperado = Path("output") / nombre_salida
            if ruta_esperado.exists():
                lineas = [
                    ln.strip()
                    for ln in ruta_esperado.read_text(encoding="utf-8").splitlines()
                    if ln.strip()
                ]
                costo_esperado = lineas[0]
                con_esperado += 1
                if str(costo) == costo_esperado:
                    match = "✓"
                    coincidencias += 1
                else:
                    match = "✗"

            print(
                f"  {nombre_base:<18} {n:<4} {costo:<10} {costo_esperado:<10} "
                f"{match:<7} {tiempo_ms:.2f}"
            )

        except Exception as error:
            print(f"  {nombre_base:<18} ERROR: {error}")

    if con_esperado:
        print(f"  {'-' * 58}")
        print(f"  Coincidencias con esperado: {coincidencias}/{con_esperado}")
    print(f"{'=' * 65}\n")


def main() -> int:
    if len(sys.argv) == 1:
        procesar_todas_las_entradas()
        return 0

    if len(sys.argv) != 3:
        print("Uso:")
        print("  python fuerza_bruta.py")
        print("  python fuerza_bruta.py <entrada.txt> <salida.txt>")
        return 1

    finca = leer_finca(sys.argv[1])
    orden, costo = roFB(finca)

    if costo_total(finca, orden) != costo:
        print("Advertencia: el costo verificado no coincide con el reportado.")

    escribir_salida(sys.argv[2], orden, costo)
    print(f"Costo óptimo: {costo}")
    print(f"Orden: {orden}")
    print(f"Salida guardada en: {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

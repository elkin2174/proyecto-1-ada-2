"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo: Programación dinámica (roPD), versión legible.

- Estados con conjuntos (frozenset) de tablones ya regados, sin máscaras binarias.
- Clave de estado: (conjunto_regados, último_tablón_regado).
- Integrado con f_auxiliares e interfaz.py (opción 5 del menú).

Uso:
    python dinamica.py                          # procesa tests/* → output_pd/
    python dinamica.py entrada.txt salida.txt   # un solo archivo
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from f_auxiliares import (
    costo_tablon,
    costo_total,
    escribir_salida,
    leer_finca,
    obtener_archivos_entrada,
)

INF = 10**18

# DP explícita sobre subconjuntos: práctica hasta ~20 tablones.
MAX_N_DP = 25


def _suma_tiempos_regado(regados: frozenset[int], finca: list[tuple[int, int, int, int]]) -> int:
    """Día en que puede empezar el siguiente tablón (suma de tr ya regados)."""
    return sum(finca[i][1] for i in regados)


def _generar_subconjuntos(cantidad: int) -> list[frozenset[int]]:
    """Todos los subconjuntos de {0, ..., cantidad-1} sin aritmética binaria."""
    subconjuntos: list[frozenset[int]] = [frozenset()]
    for indice in range(cantidad):
        nuevos = [conjunto | {indice} for conjunto in subconjuntos]
        subconjuntos.extend(nuevos)
    return subconjuntos


def _resolver_dp(finca: list[tuple[int, int, int, int]]) -> tuple[list[int], int]:
    """
    DP con estados legibles.

      estado = (conjunto_regados, ultimo_tablon_regado)
      costo_por_estado[estado] = costo mínimo parcial
      estado_anterior[estado] = estado previo en la reconstrucción
    """
    cantidad = len(finca)
    if cantidad == 0:
        return [], 0
    if cantidad == 1:
        return [0], costo_tablon(finca, 0, 0)

    todos_regados = frozenset(range(cantidad))
    costo_por_estado: dict[tuple[frozenset[int], int], int] = {}
    estado_anterior: dict[tuple[frozenset[int], int], tuple[frozenset[int], int] | None] = {}

    for indice in range(cantidad):
        solo_este = frozenset({indice})
        estado = (solo_este, indice)
        costo_por_estado[estado] = costo_tablon(finca, indice, 0)
        estado_anterior[estado] = None

    subconjuntos_ordenados = sorted(_generar_subconjuntos(cantidad), key=len)

    for conjunto_regados in subconjuntos_ordenados:
        dia_siguiente = _suma_tiempos_regado(conjunto_regados, finca)

        for ultimo in conjunto_regados:
            estado_actual = (conjunto_regados, ultimo)
            costo_actual = costo_por_estado.get(estado_actual, INF)
            if costo_actual >= INF:
                continue

            for siguiente in range(cantidad):
                if siguiente in conjunto_regados:
                    continue

                conjunto_nuevo = conjunto_regados | {siguiente}
                estado_nuevo = (conjunto_nuevo, siguiente)
                costo_candidato = costo_actual + costo_tablon(finca, siguiente, dia_siguiente)

                if costo_candidato < costo_por_estado.get(estado_nuevo, INF):
                    costo_por_estado[estado_nuevo] = costo_candidato
                    estado_anterior[estado_nuevo] = estado_actual

    mejor_costo = INF
    mejor_ultimo = -1
    for ultimo in range(cantidad):
        costo_final = costo_por_estado.get((todos_regados, ultimo), INF)
        if costo_final < mejor_costo:
            mejor_costo = costo_final
            mejor_ultimo = ultimo

    orden_inverso: list[int] = []
    conjunto_actual = todos_regados
    ultimo_actual = mejor_ultimo

    while ultimo_actual != -1:
        orden_inverso.append(ultimo_actual)
        estado_actual = (conjunto_actual, ultimo_actual)
        estado_previo = estado_anterior[estado_actual]
        if estado_previo is None:
            break
        conjunto_actual, ultimo_actual = estado_previo

    return list(reversed(orden_inverso)), mejor_costo


def roPD(finca):
    """
    Programación dinámica para el riego óptimo.

    Recibe:
        finca: lista de tablones (ts, tr, p, rp).

    Retorna:
        (orden_optimo, costo_minimo)

    Complejidad: O(n² · 2ⁿ) en tiempo y espacio.
    """
    n = len(finca)
    if n > MAX_N_DP:
        raise ValueError(
            f"n = {n} supera el límite práctico de DP ({MAX_N_DP} tablones)."
        )
    return _resolver_dp(finca)


def procesar_todas_las_entradas(carpeta_entrada="tests", carpeta_salida="output_pd"):
    """
    Lee todos los *_in.txt, ejecuta roPD y guarda salidas en carpeta_salida.
    """
    carpeta_salida_path = Path(carpeta_salida)
    carpeta_salida_path.mkdir(exist_ok=True)

    archivos_entrada = obtener_archivos_entrada(carpeta_entrada)
    if not archivos_entrada:
        print(f"No se encontraron archivos *_in.txt en {carpeta_entrada}.")
        return

    print(f"\n{'=' * 65}")
    print(f"  Batch programación dinámica — {len(archivos_entrada)} archivo(s)")
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

            if n > MAX_N_DP:
                print(f"  {nombre_base:<18} Saltado (n={n} > {MAX_N_DP})")
                continue

            inicio = time.perf_counter()
            orden, costo = roPD(finca)
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
        print("  python dinamica.py")
        print("  python dinamica.py <entrada.txt> <salida.txt>")
        return 1

    finca = leer_finca(sys.argv[1])
    orden, costo = roPD(finca)

    if costo_total(finca, orden) != costo:
        print("Advertencia: el costo verificado no coincide con el reportado.")

    escribir_salida(sys.argv[2], orden, costo)
    print(f"Costo óptimo: {costo}")
    print(f"Orden: {orden}")
    print(f"Salida guardada en: {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

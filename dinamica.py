"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo: Programación dinámica (roPD).

- Estados (S, j): S es el conjunto de tablones ya regados y j el último regado.
- Tabulación bottom-up por tamaño creciente de S.
- Integrado con f_auxiliares e interfaz.py (opción 5 del menú).

Uso:
    python dinamica.py                          # procesa tests/* → output_pd/
    python dinamica.py entrada.txt salida.txt   # un solo archivo
"""

from __future__ import annotations

import sys

from f_auxiliares import costo_tablon, ejecutar_cli

INF = 10**18

# DP explícita sobre subconjuntos: práctica hasta ~20 tablones.
MAX_N_DP = 25


def _suma_tiempos_regado(regados: frozenset[int], finca: list[tuple[int, int, int, int]]) -> int:
    """Día en que puede empezar el siguiente tablón (suma de tr ya regados)."""
    return sum(finca[i][1] for i in regados)


def _generar_subconjuntos(cantidad: int) -> list[frozenset[int]]:
    """Todos los subconjuntos de {0, ..., cantidad-1}."""
    subconjuntos: list[frozenset[int]] = [frozenset()]
    for indice in range(cantidad):
        nuevos = [conjunto | {indice} for conjunto in subconjuntos]
        subconjuntos.extend(nuevos)
    return subconjuntos


def _resolver_dp(finca: list[tuple[int, int, int, int]]) -> tuple[list[int], int]:
    """
    Resuelve el problema por programación dinámica.

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

    Complejidad: O(n² · 2ⁿ) en tiempo, O(n · 2ⁿ) en espacio.
    """
    n = len(finca)
    if n > MAX_N_DP:
        raise ValueError(
            f"n = {n} supera el límite práctico de DP ({MAX_N_DP} tablones)."
        )
    return _resolver_dp(finca)


def main() -> int:
    return ejecutar_cli(
        sys.argv, roPD,
        carpeta_salida="output_pd",
        etiqueta="programación dinámica",
        nombre_script="dinamica.py",
        max_n=MAX_N_DP,
        etiqueta_costo="Costo óptimo",
    )


if __name__ == "__main__":
    raise SystemExit(main())

"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo: Estrategia Voraz (roV).

Fundamento teórico del criterio voraz:
  Sea i un tablón que va antes que j en la programación. Por argumento de
  intercambio se puede demostrar:

  · Caso 2-2 (ambos sin daño): i ≺ j es mejor iff tr_i < tr_j   → SJF
  · Caso 3-3 (ambos con daño): i ≺ j es mejor iff tr_i/p_i < tr_j/p_j → WSPT

  La estrategia WSPT (tr/p ascendente) unifica ambos casos y sirve como
  criterio base. Luego se refina con búsqueda local 2-opt hasta convergencia.

Las funciones base (costos, E/S, batch, CLI) viven en f_auxiliares.py.
"""

import sys

from f_auxiliares import costo_total, ejecutar_cli


# ═══════════════════════════════════════════════════════════════
#  ALGORITMO VORAZ  (roV)
# ═══════════════════════════════════════════════════════════════

def _criterio_wspt(finca, i):
    """WSPT: Weighted Shortest Processing Time = tr / p (óptimo en Caso 3-3)."""
    ts, tr, p, rp = finca[i]
    return tr / p


def _criterio_holgura(finca, i):
    """Holgura = ts - tr (deadline implícito), desempate por prioridad desc."""
    ts, tr, p, rp = finca[i]
    return (ts - tr, -p)


def _criterio_sjf(finca, i):
    """Shortest Job First: tr ascendente (óptimo para Caso 2-2)."""
    return finca[i][1]


def _criterio_edd(finca, i):
    """Earliest Due Date: ts ascendente."""
    return finca[i][0]


def _busqueda_local(finca, perm_inicial):
    """
    Mejora local 2-opt: intercambia todos los pares (i, j) con i < j.
    Acepta el intercambio si reduce el costo. Repite hasta convergencia.

    Complejidad por iteración: O(n² · n) = O(n³).
    """
    perm = list(perm_inicial)
    n = len(perm)
    mejorado = True
    while mejorado:
        mejorado = False
        costo_actual = costo_total(finca, perm)
        for i in range(n):
            for j in range(i + 1, n):
                perm[i], perm[j] = perm[j], perm[i]       # intercambio
                nuevo_costo = costo_total(finca, perm)
                if nuevo_costo < costo_actual:
                    costo_actual = nuevo_costo
                    mejorado = True                         # aceptar
                else:
                    perm[i], perm[j] = perm[j], perm[i]   # revertir
    return perm, costo_actual


def roV(finca):
    """
    Algoritmo voraz para el problema del riego óptimo.

    Estrategia:
      1. Genera cuatro permutaciones iniciales con criterios distintos
         (WSPT, SJF, holgura/EDF y EDD).
      2. Aplica búsqueda local 2-opt a cada candidato hasta convergencia.
      3. Retorna la mejor solución encontrada.

    Complejidad: O(n³). Optimalidad no garantizada, pero el multi-inicio
    + 2-opt encuentra el óptimo en la gran mayoría de instancias.
    """
    n = len(finca)

    candidatos = [
        sorted(range(n), key=lambda i: _criterio_wspt(finca, i)),
        sorted(range(n), key=lambda i: _criterio_sjf(finca, i)),
        sorted(range(n), key=lambda i: _criterio_holgura(finca, i)),
        sorted(range(n), key=lambda i: _criterio_edd(finca, i)),
    ]

    mejor_perm = None
    mejor_costo = float('inf')
    for candidato in candidatos:
        perm, costo = _busqueda_local(finca, candidato)
        if costo < mejor_costo:
            mejor_costo = costo
            mejor_perm = perm[:]

    return mejor_perm, mejor_costo


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    return ejecutar_cli(
        sys.argv, roV,
        carpeta_salida="output_v",
        etiqueta="voraz",
        nombre_script="voraz.py",
        etiqueta_costo="Costo mínimo",
    )


if __name__ == "__main__":
    raise SystemExit(main())

"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo: Estrategia Voraz (roV) + Funciones de Verificación de Rendimiento

Fundamento teórico del criterio voraz:
  Sea i un tablón que va antes que j en la programación. Por argumento de
  intercambio se puede demostrar:

  · Caso 2-2 (ambos sin daño): i ≺ j es mejor iff tr_i < tr_j   → SJF
  · Caso 3-3 (ambos con daño): i ≺ j es mejor iff tr_i/p_i < tr_j/p_j → WSPT

  La estrategia WSPT (tr/p ascendente) unifica ambos casos y sirve como
  criterio base. Luego se refina con búsqueda local 2-opt hasta convergencia.
"""

import sys
import time
import random
from itertools import permutations
from pathlib import Path

from f_auxiliares import (
    escribir_salida,
    leer_finca,
    obtener_archivos_entrada,
)

# ═══════════════════════════════════════════════════════════════
#  FUNCIONES BASE (compartidas por todos los algoritmos)
# ═══════════════════════════════════════════════════════════════

def calcular_tiempos(finca, perm):
    """
    Calcula t[i] = tiempo de inicio del tablón i dada la permutación.
    t[π₀] = 0,  t[πⱼ] = t[πⱼ₋₁] + tr[πⱼ₋₁]   (j = 1..n-1)
    """
    t = [0] * len(finca)
    for j in range(1, len(perm)):
        t[perm[j]] = t[perm[j - 1]] + finca[perm[j - 1]][1]
    return t


def costo_tablon(finca, i, ti):
    """
    CRᴾ_F[i]:
      Caso 1 (ti == rp): ts − (ti + tr)           ← riego perfecto
      Caso 2 (ts−tr ≥ ti): 2·(ts − (ti + tr))    ← sin daño
      Caso 3 (otro):  2·p·((ti + tr) − ts)        ← con daño
    """
    ts, tr, p, rp = finca[i]
    if ti == rp:
        return ts - (ti + tr)
    elif ts - tr >= ti:
        return 2 * (ts - (ti + tr))
    else:
        return 2 * p * ((ti + tr) - ts)


def costo_total(finca, perm):
    """Costo total de la programación Π para la finca F."""
    t = calcular_tiempos(finca, perm)
    return sum(costo_tablon(finca, perm[j], t[perm[j]]) for j in range(len(perm)))


# ═══════════════════════════════════════════════════════════════
#  ALGORITMO VORAZ  (roV)
# ═══════════════════════════════════════════════════════════════

def _criterio_wspt(finca, i):
    """
    WSPT: Weighted Shortest Processing Time = tr / p
    Óptimo para Caso 3-3 (argumento de intercambio), buen punto de inicio.
    Nota: SJF (solo tr) es un caso especial con p constante.
    """
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

    Complejidad por iteración: O(n² · n) = O(n³)
    Número de iteraciones: a lo sumo O(n!) pero en práctica O(n) iteraciones.
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
      1. Genera cuatro permutaciones iniciales usando criterios distintos:
         · WSPT  (tr/p ascendente) — teóricamente óptimo en Caso 3-3
         · SJF   (tr ascendente)   — teóricamente óptimo en Caso 2-2
         · EDF   (holgura asc.)    — evita rebasar deadlines
         · EDD   (ts ascendente)   — earliest due date clásico
      2. Aplica búsqueda local 2-opt a cada candidato hasta convergencia.
      3. Retorna la mejor solución encontrada.

    Complejidad:
      · Generación: O(n log n) por criterio × 4 criterios = O(n log n)
      · Local search: O(n³) por candidato × 4 = O(n³) en total
      · Total: O(n³)  — eficiente en la práctica para n razonable

    Optimalidad: no garantizada, pero el multi-inicio + 2-opt
    encuentra el óptimo en la gran mayoría de instancias.
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
#  FUERZA BRUTA  (para verificación, n ≤ 12)
# ═══════════════════════════════════════════════════════════════

def roFB(finca):
    """Fuerza bruta O(n!·n). Solo para n pequeño (verificación)."""
    mejor_perm, mejor_costo = None, float('inf')
    for perm in permutations(range(len(finca))):
        c = costo_total(finca, list(perm))
        if c < mejor_costo:
            mejor_costo = c
            mejor_perm = list(perm)
    return mejor_perm, mejor_costo


# ═══════════════════════════════════════════════════════════════
#  GENERADOR DE CASOS DE PRUEBA
# ═══════════════════════════════════════════════════════════════

def generar_finca(n, semilla=None):
    """
    Genera una finca aleatoria con n tablones válidos.

    Restricciones del enunciado:
      · ts > tr  (el tablón puede regarse antes de morir)
      · 0 ≤ rp ≤ ts - tr  (el tiempo perfecto permite completar el riego)
      · p ∈ {1, 2, 3, 4}
    """
    if semilla is not None:
        random.seed(semilla)
    finca = []
    for _ in range(n):
        tr = random.randint(1, 10)
        ts = tr + random.randint(1, 15)   # ts > tr siempre
        p  = random.randint(1, 4)
        rp = random.randint(0, ts - tr)   # 0 ≤ rp ≤ ts - tr
        finca.append((ts, tr, p, rp))
    return finca


def finca_a_texto(finca):
    """Convierte una finca a string en el formato del enunciado."""
    lineas = [str(len(finca))]
    for ts, tr, p, rp in finca:
        lineas.append(f'{ts},{tr},{p},{rp}')
    return '\n'.join(lineas)


# ═══════════════════════════════════════════════════════════════
#  FUNCIONES DE VERIFICACIÓN DE RENDIMIENTO
# ═══════════════════════════════════════════════════════════════

def verificar_instancia(finca, verbose=False):
    """
    Compara roV contra roFB en una instancia dada.
    Retorna un dict con métricas detalladas.
    """
    t0 = time.perf_counter()
    perm_v, costo_v = roV(finca)
    t_v = time.perf_counter() - t0

    t0 = time.perf_counter()
    perm_opt, costo_opt = roFB(finca)
    t_fb = time.perf_counter() - t0

    es_optimo = (costo_v == costo_opt)
    gap = ((costo_v - costo_opt) / max(abs(costo_opt), 1)) * 100 if costo_opt != 0 else 0.0

    resultado = {
        'n':          len(finca),
        'costo_v':    costo_v,
        'costo_opt':  costo_opt,
        'perm_v':     perm_v,
        'perm_opt':   perm_opt,
        'es_optimo':  es_optimo,
        'gap_%':      gap,
        'tiempo_v':   t_v,
        'tiempo_fb':  t_fb,
    }

    if verbose:
        estado = '✓ ÓPTIMO' if es_optimo else f'✗ gap={gap:.1f}%'
        print(f'  Voraz: {costo_v} {str(perm_v):<25} FB: {costo_opt} {str(perm_opt):<25} {estado}')

    return resultado


def analizar_rendimiento(num_pruebas=200, n=5, semilla_base=0):
    """
    Ejecuta `num_pruebas` instancias aleatorias de tamaño n y calcula:
      · Tasa de optimalidad (% de veces que voraz = óptimo)
      · Gap promedio y máximo
      · Tiempo promedio de voraz vs fuerza bruta

    Solo usable con n ≤ 10 (FB es O(n!)).
    """
    assert n <= 10, 'n demasiado grande para comparar con fuerza bruta'

    resultados = []
    for i in range(num_pruebas):
        finca = generar_finca(n, semilla=semilla_base + i)
        resultados.append(verificar_instancia(finca))

    optimos      = sum(1 for r in resultados if r['es_optimo'])
    tasa         = optimos / num_pruebas * 100
    gap_prom     = sum(r['gap_%'] for r in resultados) / num_pruebas
    gap_max      = max(r['gap_%'] for r in resultados)
    tiempo_v_avg = sum(r['tiempo_v'] for r in resultados) / num_pruebas * 1000
    tiempo_fb_avg= sum(r['tiempo_fb'] for r in resultados) / num_pruebas * 1000

    print(f'\n{"═"*55}')
    print(f'  Análisis de rendimiento del voraz')
    print(f'  n={n}, pruebas={num_pruebas}')
    print(f'{"═"*55}')
    print(f'  Tasa de optimalidad:  {optimos}/{num_pruebas}  ({tasa:.1f}%)')
    print(f'  Gap promedio:         {gap_prom:.2f}%')
    print(f'  Gap máximo:           {gap_max:.2f}%')
    print(f'  Tiempo voraz (prom):  {tiempo_v_avg:.3f} ms')
    print(f'  Tiempo FB   (prom):   {tiempo_fb_avg:.3f} ms')
    print(f'  Aceleración (FB/V):   {tiempo_fb_avg/max(tiempo_v_avg,1e-9):.1f}×')
    print(f'{"═"*55}\n')

    return resultados


def tabla_comparacion(casos, nombres=None):
    """
    Imprime una tabla comparando roV vs roFB para una lista de fincas.
    Ideal para el informe del proyecto.
    """
    if nombres is None:
        nombres = [f'Caso {i+1}' for i in range(len(casos))]

    print(f'\n{"─"*85}')
    print(f'  {"Caso":<12} {"n":<4} {"Costo FB":<12} {"Costo V":<12} {"Gap%":<10} {"Óptimo":<8} {"t_V(ms)":<10} {"t_FB(ms)"}')
    print(f'{"─"*85}')

    totales = {'optimos': 0, 'gaps': [], 'tv': [], 'tfb': []}

    for nombre, finca in zip(nombres, casos):
        r = verificar_instancia(finca)
        marca = '✓' if r['es_optimo'] else '✗'
        totales['optimos'] += r['es_optimo']
        totales['gaps'].append(r['gap_%'])
        totales['tv'].append(r['tiempo_v'] * 1000)
        totales['tfb'].append(r['tiempo_fb'] * 1000)
        print(f'  {nombre:<12} {r["n"]:<4} {r["costo_opt"]:<12} {r["costo_v"]:<12} '
              f'{r["gap_%"]:<10.1f} {marca:<8} {r["tiempo_v"]*1000:<10.3f} {r["tiempo_fb"]*1000:.3f}')

    n_casos = len(casos)
    print(f'{"─"*85}')
    print(f'  {"Promedio":<12} {"":4} {"":12} {"":12} '
          f'{sum(totales["gaps"])/n_casos:<10.1f} '
          f'{totales["optimos"]}/{n_casos:<4} '
          f'{sum(totales["tv"])/n_casos:<10.3f} '
          f'{sum(totales["tfb"])/n_casos:.3f}')
    print(f'{"─"*85}\n')


def analisis_por_tamano(ns=[3,4,5,6,7,8], pruebas_por_n=100):
    """
    Analiza cómo varía la calidad del voraz con el tamaño n.
    Útil para la sección de comparación del informe.
    """
    print(f'\n{"═"*65}')
    print(f'  Calidad del voraz según tamaño de la finca')
    print(f'{"═"*65}')
    print(f'  {"n":<6} {"Pruebas":<10} {"Tasa opt%":<12} {"Gap prom%":<12} {"Gap max%":<10} {"t_V(ms)"}')
    print(f'{"─"*65}')

    for n in ns:
        resultados = []
        for i in range(pruebas_por_n):
            finca = generar_finca(n, semilla=1000 * n + i)
            resultados.append(verificar_instancia(finca))
        tasa      = sum(r['es_optimo'] for r in resultados) / pruebas_por_n * 100
        gap_prom  = sum(r['gap_%'] for r in resultados) / pruebas_por_n
        gap_max   = max(r['gap_%'] for r in resultados)
        t_v_prom  = sum(r['tiempo_v'] for r in resultados) / pruebas_por_n * 1000
        print(f'  {n:<6} {pruebas_por_n:<10} {tasa:<12.1f} {gap_prom:<12.2f} {gap_max:<10.2f} {t_v_prom:.3f}')

    print(f'{"═"*65}\n')


def imprimir_solucion(finca, perm, costo, titulo='Solución'):
    """Muestra detalle completo de la solución para verificación."""
    t = calcular_tiempos(finca, perm)
    print(f'\n{"═"*60}')
    print(f'  {titulo}')
    print(f'  Permutación: {perm}')
    print(f'{"═"*60}')
    print(f'  {"Tablón":<8} {"t_ini":<8} {"rp":<6} {"ts-tr":<8} {"Caso":<6} {"Costo"}')
    print(f'  {"─"*50}')
    total_v = 0
    for j in range(len(perm)):
        i = perm[j]
        ts, tr, p, rp = finca[i]
        ti = t[i]
        if ti == rp:
            caso, c = 1, ts - (ti + tr)
        elif ts - tr >= ti:
            caso, c = 2, 2 * (ts - (ti + tr))
        else:
            caso, c = 3, 2 * p * ((ti + tr) - ts)
        total_v += c
        print(f'  T{i:<7} {ti:<8} {rp:<6} {ts - tr:<8} {caso:<6} {c}')
    print(f'  {"─"*50}')
    print(f'  {"Costo total":<30} {total_v}')
    print()

def procesar_todas_las_entradas(carpeta_entrada="tests", carpeta_salida="output_v"):
    """
    Lee todos los *_in.txt, ejecuta roV y guarda salidas en carpeta_salida.
    """
    carpeta_salida_path = Path(carpeta_salida)
    carpeta_salida_path.mkdir(exist_ok=True)

    archivos_entrada = obtener_archivos_entrada(carpeta_entrada)
    if not archivos_entrada:
        print(f"No se encontraron archivos *_in.txt en {carpeta_entrada}.")
        return

    print(f"\n{'=' * 65}")
    print(f"  Batch voraz — {len(archivos_entrada)} archivo(s)")
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

            inicio = time.perf_counter()
            orden, costo = roV(finca)
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
    if len(sys.argv) == 2 and sys.argv[1] == "benchmark":
        print("\n[Modo benchmark: análisis por tamaño de finca]")
        analisis_por_tamano(ns=[3, 4, 5, 6, 7, 8], pruebas_por_n=150)
        print("\n[Análisis con n=5, 500 pruebas]")
        analizar_rendimiento(num_pruebas=500, n=5)
        return 0

    if len(sys.argv) == 1:
        procesar_todas_las_entradas()
        return 0

    if len(sys.argv) != 3:
        print("Uso:")
        print("  python voraz.py")
        print("  python voraz.py <entrada.txt> <salida.txt>")
        print("  python voraz.py benchmark")
        return 1

    finca = leer_finca(sys.argv[1])
    orden, costo = roV(finca)

    if costo_total(finca, orden) != costo:
        print("Advertencia: el costo verificado no coincide con el reportado.")

    escribir_salida(sys.argv[2], orden, costo)
    print(f"Costo mínimo: {costo}")
    print(f"Orden: {orden}")
    print(f"Salida guardada en: {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
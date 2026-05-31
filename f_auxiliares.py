"""
Proyecto: Plan de riego óptimo de una finca
Análisis de Algoritmos II — Universidad del Valle

Módulo central de utilidades compartidas por todos los algoritmos
(fuerza bruta, voraz y programación dinámica):

  · Funciones base   : calcular_tiempos, costo_tablon, costo_total
  · Entrada/salida    : leer_finca, escribir_salida
  · Descubrimiento    : numero_test, obtener_archivos_entrada
  · Reportes          : imprimir_solucion
  · Ejecución genérica: procesar_lote (batch) y ejecutar_cli (CLI)
"""

import time
import re
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
#  FUNCIONES BASE (modelo de costo)
# ═══════════════════════════════════════════════════════════════

def calcular_tiempos(finca, perm):
    """
    Calcula t[i] = tiempo de inicio de riego del tablón i según `perm`.
    El primer tablón inicia en 0 y cada siguiente arranca cuando termina
    de regarse el anterior (suma acumulada de los tr).

    Recibe:
        finca: lista de tablones, cada uno (ts, tr, p, rp).
        perm:  orden de riego (lista/tupla de índices).

    Retorna:
        lista t, donde t[i] es el tiempo de inicio del tablón Ti.
    """
    t = [0] * len(finca)
    tiempo_actual = 0
    for indice_tablon in perm:
        t[indice_tablon] = tiempo_actual
        tiempo_actual += finca[indice_tablon][1]
    return t


def costo_tablon(finca, i, ti):
    """
    Costo individual de regar el tablón i empezando en el tiempo ti.

      Caso 1 (ti == rp):      ts - (ti + tr)          ← riego perfecto
      Caso 2 (ts - tr >= ti): 2 * (ts - (ti + tr))    ← sin daño
      Caso 3 (otro):          2 * p * ((ti + tr) - ts) ← con daño
    """
    ts, tr, p, rp = finca[i]
    fin = ti + tr
    if ti == rp:
        return ts - fin
    elif ts - tr >= ti:
        return 2 * (ts - fin)
    else:
        return 2 * p * (fin - ts)


def costo_total(finca, perm):
    """Suma de los costos individuales de todos los tablones según `perm`."""
    tiempos = calcular_tiempos(finca, perm)
    return sum(costo_tablon(finca, i, tiempos[i]) for i in perm)


# ═══════════════════════════════════════════════════════════════
#  ENTRADA / SALIDA
# ═══════════════════════════════════════════════════════════════

def leer_finca(ruta_archivo):
    """
    Lee una finca desde un archivo de texto.

    Formato esperado:
        n
        ts0,tr0,p0,rp0
        ...
        ts(n-1),tr(n-1),p(n-1),rp(n-1)

    Retorna:
        finca: lista de tablones (ts, tr, p, rp).
    """
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        lineas = [linea.strip() for linea in archivo if linea.strip()]

    if not lineas:
        raise ValueError(f"El archivo {ruta_archivo} está vacío.")

    n = int(lineas[0])
    finca = []
    for linea in lineas[1:]:
        valores = linea.replace(" ", "").split(",")
        if len(valores) != 4:
            raise ValueError(f"Línea inválida en {ruta_archivo}: {linea}")
        ts, tr, p, rp = map(int, valores)
        finca.append((ts, tr, p, rp))

    if len(finca) != n:
        raise ValueError(
            f"El archivo {ruta_archivo} dice que hay {n} tablones, "
            f"pero se leyeron {len(finca)}."
        )
    return finca


def escribir_salida(ruta_archivo, perm, costo):
    """
    Escribe la salida en el formato solicitado:
        costo
        pi0
        pi1
        ...
    """
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(f"{costo}\n")
        for indice_tablon in perm:
            archivo.write(f"{indice_tablon}\n")


# ═══════════════════════════════════════════════════════════════
#  DESCUBRIMIENTO DE CASOS DE PRUEBA
# ═══════════════════════════════════════════════════════════════

def numero_test(ruta):
    """Extrae el número N de archivos tipo testN_in.txt (999999 si no hay)."""
    coincidencia = re.search(r"test(\d+)_in\.txt", Path(ruta).name)
    return int(coincidencia.group(1)) if coincidencia else 999999


def obtener_archivos_entrada(carpeta_entrada):
    """Lista ordenada numéricamente de los *_in.txt de una carpeta."""
    return sorted(Path(carpeta_entrada).glob("*_in.txt"), key=numero_test)


# ═══════════════════════════════════════════════════════════════
#  REPORTES
# ═══════════════════════════════════════════════════════════════

def imprimir_solucion(finca, perm, costo, titulo="Solución"):
    """
    Muestra en consola el detalle de una solución (tiempos de inicio,
    fin, caso aplicado y costo individual) para verificación manual.
    """
    tiempos = calcular_tiempos(finca, perm)

    print(f"\n{'=' * 60}")
    print(f"{titulo}")
    print(f"Permutación: {perm}")
    print(f"Costo total: {costo}")
    print(f"{'=' * 60}")
    print(f"{'Tablón':<8}{'Inicio':<8}{'Fin':<8}{'rp':<8}{'ts':<8}{'Caso':<10}{'Costo'}")
    print("-" * 60)

    total_verificado = 0
    for indice_tablon in perm:
        ts, tr, p, rp = finca[indice_tablon]
        inicio = tiempos[indice_tablon]
        fin = inicio + tr
        costo_individual = costo_tablon(finca, indice_tablon, inicio)

        if inicio == rp:
            caso = "Caso 1"
        elif ts - tr >= inicio:
            caso = "Caso 2"
        else:
            caso = "Caso 3"

        total_verificado += costo_individual
        print(
            f"T{indice_tablon:<7}{inicio:<8}{fin:<8}{rp:<8}{ts:<8}"
            f"{caso:<10}{costo_individual}"
        )

    print("-" * 60)
    print(f"Total verificado: {total_verificado}\n")


# ═══════════════════════════════════════════════════════════════
#  EJECUCIÓN GENÉRICA (compartida por los tres algoritmos)
# ═══════════════════════════════════════════════════════════════

def _costo_esperado(ruta_entrada, nombre_salida):
    """Costo esperado para un test, buscando junto a la entrada o en output/."""
    candidatos = [ruta_entrada.parent / nombre_salida, Path("output") / nombre_salida]
    for ruta in candidatos:
        if ruta.exists():
            lineas = [
                ln.strip()
                for ln in ruta.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            if lineas:
                return lineas[0]
    return None


def procesar_lote(algoritmo, carpeta_salida, etiqueta,
                  max_n=None, carpeta_entrada="tests"):
    """
    Ejecuta `algoritmo` sobre todos los *_in.txt de `carpeta_entrada`,
    guarda cada salida en `carpeta_salida` y compara con el costo esperado.

    Recibe:
        algoritmo: callable finca -> (orden, costo).
        carpeta_salida: carpeta destino de los *_out.txt.
        etiqueta: nombre del algoritmo para el encabezado.
        max_n: si se da, los tests con n > max_n se saltan.
        carpeta_entrada: carpeta con los *_in.txt.
    """
    carpeta_salida_path = Path(carpeta_salida)
    carpeta_salida_path.mkdir(exist_ok=True)

    archivos_entrada = obtener_archivos_entrada(carpeta_entrada)
    if not archivos_entrada:
        print(f"No se encontraron archivos *_in.txt en {carpeta_entrada}.")
        return

    print(f"\n{'=' * 65}")
    print(f"  Batch {etiqueta} — {len(archivos_entrada)} archivo(s)")
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

            if max_n is not None and n > max_n:
                print(f"  {nombre_base:<18} Saltado (n={n} > {max_n})")
                continue

            inicio = time.perf_counter()
            orden, costo = algoritmo(finca)
            tiempo_ms = (time.perf_counter() - inicio) * 1000

            nombre_salida = nombre_base.replace("_in.txt", "_out.txt")
            escribir_salida(carpeta_salida_path / nombre_salida, orden, costo)

            match = "-"
            costo_esperado = _costo_esperado(ruta_entrada, nombre_salida)
            if costo_esperado is None:
                costo_esperado = "-"
            else:
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


def ejecutar_cli(argv, algoritmo, carpeta_salida, etiqueta, nombre_script,
                 max_n=None, etiqueta_costo="Costo"):
    """
    Punto de entrada CLI común a los tres algoritmos:

        python <script>                      → procesa todos los tests (batch)
        python <script> <entrada> <salida>   → resuelve un solo archivo

    Retorna el código de salida del proceso.
    """
    if len(argv) == 1:
        procesar_lote(algoritmo, carpeta_salida, etiqueta, max_n=max_n)
        return 0

    if len(argv) != 3:
        print("Uso:")
        print(f"  python {nombre_script}")
        print(f"  python {nombre_script} <entrada.txt> <salida.txt>")
        return 1

    finca = leer_finca(argv[1])
    orden, costo = algoritmo(finca)

    if costo_total(finca, orden) != costo:
        print("Advertencia: el costo verificado no coincide con el reportado.")

    escribir_salida(argv[2], orden, costo)
    print(f"{etiqueta_costo}: {costo}")
    print(f"Orden: {orden}")
    print(f"Salida guardada en: {argv[2]}")
    return 0

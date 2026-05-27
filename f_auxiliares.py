from pathlib import Path
import re


def calcular_tiempos(finca, perm):
    """
    Objetivo:
        Calcular el tiempo de inicio de riego de cada tablón
        según una programación o permutación dada.

    Recibe:
        finca: lista de tablones.
            Cada tablón tiene la forma (ts, tr, p, rp).

        perm: lista o tupla con el orden de riego.
            Ejemplo: [2, 1, 4, 3, 0]

    Retorna:
        Una lista t, donde t[i] es el tiempo en que inicia
        el riego del tablón Ti.
    """

    t = [0] * len(finca)
    tiempo_actual = 0

    for indice_tablon in perm:
        t[indice_tablon] = tiempo_actual
        tiempo_actual += finca[indice_tablon][1]

    return t


def costo_tablon(finca, i, ti):
    """
    Objetivo:
        Calcular el costo individual de regar el tablón i
        cuando inicia en el tiempo ti.

    Recibe:
        finca: lista de tablones.
        i: índice del tablón.
        ti: tiempo de inicio del riego del tablón i.

    Retorna:
        El costo individual del tablón i, según la función
        de costo definida en el enunciado.
    """

    ts, tr, p, rp = finca[i]
    fin = ti + tr

    # Caso 1: riego en el tiempo perfecto.
    if ti == rp:
        return ts - fin

    # Caso 2: no es riego perfecto, pero termina antes o justo
    # en el tiempo de supervivencia.
    elif ts - tr >= ti:
        return 2 * (ts - fin)

    # Caso 3: termina después del tiempo de supervivencia.
    else:
        return 2 * p * (fin - ts)


def costo_total(finca, perm):
    """
    Objetivo:
        Calcular el costo total de una programación de riego.
    Recibe:
        finca: lista de tablones.
        perm: lista o tupla con el orden de riego.
    Retorna:
        La suma de los costos individuales de todos los tablones.
    """
    tiempos = calcular_tiempos(finca, perm)
    total = 0

    for indice_tablon in perm:
        total += costo_tablon(finca, indice_tablon, tiempos[indice_tablon])

    return total

def evaluar_programacion(finca, orden):
    """
    Función auxiliar.

    Objetivo:
        Alias de costo_total. Se deja para que fuerza bruta pueda
        usar un nombre más descriptivo.

    Recibe:
        finca: lista de tablones.
        orden: orden de riego.

    Retorna:
        Costo total de esa programación.
    """

    return costo_total(finca, orden)


def leer_finca(ruta_archivo):
    """
    Función auxiliar.

    Objetivo:
        Leer una finca desde un archivo de texto.

    Recibe:
        ruta_archivo: ruta del archivo de entrada.

    Formato esperado:
        n
        ts0,tr0,p0,rp0
        ts1,tr1,p1,rp1
        ...
        ts(n-1),tr(n-1),p(n-1),rp(n-1)

    Retorna:
        finca: lista de tablones.
            Cada tablón es una tupla (ts, tr, p, rp).
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


def leer_entrada(ruta_archivo):
    """
    Función auxiliar.

    Objetivo:
        Alias de leer_finca, por compatibilidad con otros nombres
        usados en el proyecto.

    Recibe:
        ruta_archivo: ruta del archivo de entrada.

    Retorna:
        finca leída desde el archivo.
    """

    return leer_finca(ruta_archivo)


def escribir_salida(ruta_archivo, perm, costo):
    """
    Función auxiliar.

    Objetivo:
        Escribir la salida en el formato solicitado.

    Recibe:
        ruta_archivo: ruta donde se guardará la salida.
        perm: orden de riego.
        costo: costo total de la programación.

    Genera:
        Archivo de texto con el formato:
            costo
            pi0
            pi1
            ...
            pi(n-1)
    """

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(f"{costo}\n")

        for indice_tablon in perm:
            archivo.write(f"{indice_tablon}\n")


def numero_test(ruta):
    """
    Función auxiliar.

    Objetivo:
        Extraer el número de archivos tipo test1_in.txt,
        test2_in.txt, test10_in.txt, etc.

    Recibe:
        ruta: ruta del archivo.

    Retorna:
        El número del test como entero.
        Si no encuentra número, retorna un valor grande.
    """

    coincidencia = re.search(r"test(\d+)_in\.txt", Path(ruta).name)

    if coincidencia:
        return int(coincidencia.group(1))

    return 999999


def obtener_archivos_entrada(carpeta_entrada):
    """
    Función auxiliar.

    Objetivo:
        Obtener todos los archivos *_in.txt de una carpeta,
        ordenados numéricamente.

    Recibe:
        carpeta_entrada: ruta de la carpeta donde están los tests.

    Retorna:
        Lista ordenada de rutas de archivos de entrada.
    """

    carpeta = Path(carpeta_entrada)

    return sorted(
        carpeta.glob("*_in.txt"),
        key=numero_test
    )


def imprimir_solucion(finca, perm, costo, titulo="Solución"):
    """
    Función auxiliar.

    Objetivo:
        Mostrar en consola el detalle de una solución para verificar
        tiempos de inicio, caso aplicado y costo individual.

    Recibe:
        finca: lista de tablones.
        perm: orden de riego.
        costo: costo total calculado.
        titulo: título opcional para imprimir.
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
            f"T{indice_tablon:<7}"
            f"{inicio:<8}"
            f"{fin:<8}"
            f"{rp:<8}"
            f"{ts:<8}"
            f"{caso:<10}"
            f"{costo_individual}"
        )

    print("-" * 60)
    print(f"Total verificado: {total_verificado}\n")
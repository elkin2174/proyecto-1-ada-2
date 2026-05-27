from pathlib import Path

from f_auxiliares import (
    leer_finca,
    escribir_salida,
    imprimir_solucion,
    costo_total,
)

from fuerza_bruta import roFB
from voraz import roV


# Importar programación dinámica solo si ya existe el archivo dinamica.py.
# Mientras no esté lista, el programa no se cae.
try:
    from dinamica import roPD
except ImportError:
    roPD = None


def mostrar_menu():
    """
    Función auxiliar.

    Objetivo:
        Mostrar las opciones disponibles de la interfaz por consola.

    Recibe:
        No recibe parámetros.

    Retorna:
        No retorna valor. Solo imprime el menú.
    """

    print("\n=== PLAN DE RIEGO ÓPTIMO ===")
    print("1. Cargar finca desde archivo")
    print("2. Ver finca cargada")
    print("3. Ejecutar fuerza bruta")
    print("4. Ejecutar algoritmo voraz")
    print("5. Ejecutar programación dinámica")
    print("6. Ver última solución")
    print("7. Ver detalle del cálculo del costo")
    print("8. Guardar última salida en archivo")
    print("0. Salir")


def mostrar_finca(finca):
    """
    Función auxiliar.

    Objetivo:
        Mostrar en consola los tablones de la finca cargada.

    Recibe:
        finca: lista de tablones.
            Cada tablón tiene la forma (ts, tr, p, rp).

    Retorna:
        No retorna valor. Solo imprime la finca.
    """

    if finca is None:
        print("Primero debe cargar una finca.")
        return

    print("\nFinca cargada:")
    print("-" * 40)

    for i, tablon in enumerate(finca):
        ts, tr, p, rp = tablon
        print(f"T{i} = <{ts}, {tr}, {p}, {rp}>")

    print("-" * 40)


def ejecutar_algoritmo(nombre_algoritmo, funcion_algoritmo, finca):
    """
    Función auxiliar.

    Objetivo:
        Ejecutar un algoritmo de riego y mostrar su resultado.

    Recibe:
        nombre_algoritmo: nombre que se mostrará en pantalla.
        funcion_algoritmo: función que se va a ejecutar, por ejemplo roFB o roV.
        finca: finca cargada desde archivo.

    Retorna:
        Una tupla con:
            nombre_algoritmo
            orden
            costo

        Si no hay finca cargada, retorna None.
    """

    if finca is None:
        print("Primero debe cargar una finca.")
        return None

    print(f"\nEjecutando {nombre_algoritmo}...")

    orden, costo = funcion_algoritmo(finca)

    print("\nResultado:")
    print(f"Algoritmo: {nombre_algoritmo}")
    print(f"Orden: {orden}")
    print(f"Costo: {costo}")

    return nombre_algoritmo, orden, costo


def ver_ultima_solucion(ultima_solucion):
    """
    Función auxiliar.

    Objetivo:
        Mostrar la última solución calculada por alguno de los algoritmos.

    Recibe:
        ultima_solucion: tupla con:
            nombre_algoritmo
            orden
            costo

    Retorna:
        No retorna valor. Solo imprime la solución.
    """

    if ultima_solucion is None:
        print("Todavía no hay una solución calculada.")
        return

    nombre_algoritmo, orden, costo = ultima_solucion

    print("\nÚltima solución calculada:")
    print("-" * 40)
    print(f"Algoritmo: {nombre_algoritmo}")
    print(f"Costo: {costo}")
    print("Orden:")

    for indice in orden:
        print(indice)

    print("-" * 40)


def ver_detalle_costo(finca, ultima_solucion):
    """
    Función auxiliar.

    Objetivo:
        Mostrar el detalle del costo de la última solución:
        tiempos de inicio, tiempos de fin, caso aplicado y costo por tablón.

    Recibe:
        finca: finca cargada.
        ultima_solucion: última solución calculada.

    Retorna:
        No retorna valor. Solo imprime el detalle.
    """

    if finca is None:
        print("Primero debe cargar una finca.")
        return

    if ultima_solucion is None:
        print("Todavía no hay una solución calculada.")
        return

    nombre_algoritmo, orden, costo = ultima_solucion

    imprimir_solucion(
        finca,
        orden,
        costo,
        titulo=f"Detalle de costo - {nombre_algoritmo}"
    )

    costo_verificado = costo_total(finca, orden)

    if costo_verificado == costo:
        print("Verificación: el costo calculado coincide con el costo de la solución.")
    else:
        print("Advertencia: el costo verificado no coincide con el costo reportado.")
        print(f"Costo reportado: {costo}")
        print(f"Costo verificado: {costo_verificado}")


def guardar_ultima_salida(ultima_solucion):
    """
    Función auxiliar.

    Objetivo:
        Guardar la última solución calculada en un archivo de texto.

    Recibe:
        ultima_solucion: tupla con:
            nombre_algoritmo
            orden
            costo

    Retorna:
        No retorna valor. Genera un archivo de salida.
    """

    if ultima_solucion is None:
        print("Todavía no hay una solución calculada.")
        return

    nombre_algoritmo, orden, costo = ultima_solucion

    ruta_salida = input("Ingrese la ruta del archivo de salida: ").strip()

    if not ruta_salida:
        print("Ruta inválida.")
        return

    escribir_salida(ruta_salida, orden, costo)

    print(f"Salida guardada correctamente en: {ruta_salida}")


def main():
    """
    Función principal de la interfaz.

    Objetivo:
        Permitir al usuario cargar una finca, visualizarla, ejecutar los
        algoritmos disponibles, revisar la solución y guardar la salida.

    Recibe:
        No recibe parámetros.

    Retorna:
        No retorna valor. Controla el flujo del programa.
    """

    finca = None
    ultima_solucion = None

    while True:
        mostrar_menu()

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo de entrada: ").strip()

            try:
                finca = leer_finca(ruta)
                ultima_solucion = None
                print("Finca cargada correctamente.")
                mostrar_finca(finca)

            except Exception as error:
                print(f"Error al cargar la finca: {error}")

        elif opcion == "2":
            mostrar_finca(finca)

        elif opcion == "3":
            resultado = ejecutar_algoritmo("Fuerza bruta", roFB, finca)

            if resultado is not None:
                ultima_solucion = resultado

        elif opcion == "4":
            resultado = ejecutar_algoritmo("Voraz", roV, finca)

            if resultado is not None:
                ultima_solucion = resultado

        elif opcion == "5":
            if roPD is None:
                print("La función roPD todavía no está disponible.")
                print("Cuando tengan dinamica.py con roPD, esta opción funcionará.")
            else:
                resultado = ejecutar_algoritmo("Programación dinámica", roPD, finca)

                if resultado is not None:
                    ultima_solucion = resultado

        elif opcion == "6":
            ver_ultima_solucion(ultima_solucion)

        elif opcion == "7":
            ver_detalle_costo(finca, ultima_solucion)

        elif opcion == "8":
            guardar_ultima_salida(ultima_solucion)

        elif opcion == "0":
            print("Saliendo del programa.")
            break

        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()
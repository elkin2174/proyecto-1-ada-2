"""
Punto de entrada del proyecto "Plan de riego óptimo de una finca".

Lanza la interfaz interactiva por consola (menú con fuerza bruta, voraz y
programación dinámica). Es también el script que empaqueta PyInstaller para
generar el ejecutable.

Uso:
    python main.py
    (o ejecutar el .exe / ejecutar.bat generados)
"""

import sys


def _configurar_utf8():
    """
    Asegura que los acentos y símbolos (✓, ═, ó...) se muestren bien en la
    consola de Windows, tanto al correr con python como desde el .exe.
    """
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    for flujo in (sys.stdin, sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except Exception:
            pass


def main():
    _configurar_utf8()
    from interfaz import main as ejecutar_interfaz
    ejecutar_interfaz()


if __name__ == "__main__":
    main()

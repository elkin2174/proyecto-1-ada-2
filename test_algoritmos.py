"""
Pruebas de correctitud (rápidas) sobre la carpeta tests/.

Invariantes verificadas en cada *_in.txt:
  · costo_total reconstruye el costo reportado por cada algoritmo.
  · roFB y roPD coinciden (ambos son óptimos)            [n <= LIM_FB / LIM_PD].
  · roV nunca es mejor que el óptimo (roV >= óptimo).

Uso:
    python test_algoritmos.py        # ejecuta y reporta
    pytest test_algoritmos.py        # también compatible con pytest

Límites por tamaño para que las pruebas sean rápidas:
    fuerza bruta n <= 9   (n! crece muy rápido)
    dinámica     n <= 15  (2^n)
"""

from f_auxiliares import leer_finca, costo_total, obtener_archivos_entrada
from voraz import roV
from fuerza_bruta import roFB
from dinamica import roPD

LIM_FB = 9
LIM_PD = 15

CASOS = obtener_archivos_entrada("tests")


def _es_permutacion(perm, n):
    return sorted(perm) == list(range(n))


def verificar(ruta):
    """Verifica todas las invariantes para un caso; lanza AssertionError si falla."""
    finca = leer_finca(ruta)
    n = len(finca)

    perm_v, costo_v = roV(finca)
    assert _es_permutacion(perm_v, n), f"{ruta}: roV no es permutación"
    assert costo_total(finca, perm_v) == costo_v, f"{ruta}: roV costo inconsistente"

    optimo = None
    if n <= LIM_FB:
        perm_fb, costo_fb = roFB(finca, verbose=False)
        assert costo_total(finca, perm_fb) == costo_fb, f"{ruta}: roFB inconsistente"
        optimo = costo_fb
    if n <= LIM_PD:
        perm_pd, costo_pd = roPD(finca)
        assert _es_permutacion(perm_pd, n), f"{ruta}: roPD no es permutación"
        assert costo_total(finca, perm_pd) == costo_pd, f"{ruta}: roPD inconsistente"
        if optimo is None:
            optimo = costo_pd
        else:
            assert costo_pd == optimo, f"{ruta}: roPD ({costo_pd}) != roFB ({optimo})"

    if optimo is not None:
        assert costo_v >= optimo, f"{ruta}: roV ({costo_v}) < óptimo ({optimo})"

    return n, costo_v, optimo


# --- pytest: una prueba por archivo de entrada -------------------------------
try:
    import pytest

    @pytest.mark.parametrize("ruta", CASOS, ids=lambda p: p.name)
    def test_caso(ruta):
        verificar(ruta)
except ImportError:
    pass


# --- ejecución directa -------------------------------------------------------
def main():
    print(f"Verificando {len(CASOS)} casos en tests/ ...\n")
    fallos = 0
    for ruta in CASOS:
        try:
            n, costo_v, optimo = verificar(ruta)
            marca = "ÓPTIMO" if optimo is not None and costo_v == optimo else \
                    (f"opt={optimo}" if optimo is not None else "sin verificar")
            print(f"  OK  {ruta.name:<16} n={n:<3} roV={costo_v:<6} {marca}")
        except AssertionError as e:
            fallos += 1
            print(f"  XX  {e}")
    print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}  ({len(CASOS)} casos)")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())

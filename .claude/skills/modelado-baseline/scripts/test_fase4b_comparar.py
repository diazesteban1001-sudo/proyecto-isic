#!/usr/bin/env python3
"""
test_fase4b_comparar.py — control positivo de las piezas nuevas de
fase4b_comparar.py, con datos sintéticos, antes de correr ningún candidato.

  P. nadeau_bengio con confianza 0,95 coincide con evaluar_repetido._nadeau_bengio,
     y con la de Bonferroni, 1 − 0,05/3, da un intervalo con el mismo centro y más
     ancho. Debe fallar: con otra razón de pliegues ya no coincide.
  Q. cargar_predicciones acepta un archivo con su procedencia en regla y se
     detiene, cada una por su motivo, si cambia el archivo, si la procedencia
     dice que los controles no reprodujeron la Fase 4, o si las puntuaciones no
     tienen su huella aunque el SHA-256 del archivo coincida.
  R. guardada se detiene si los isic_id de un pliegue no están en el orden de la
     validación.
  S. comprobar_alineacion da bien con las columnas de con_imagen y mal con las
     columnas corridas una fila.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4b_comparar.py
Devuelve 0 si todos los casos se comportan como se espera.
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4b  # noqa: E402
import fase4b_comparar as fc  # noqa: E402
from evaluar_repetido import _nadeau_bengio  # noqa: E402

resultados = []


def caso(nombre, ok, detalle=""):
    resultados.append(bool(ok))
    print(f"[{'OK' if ok else 'FALLA'}] {nombre}{': ' + detalle if detalle else ''}")


def se_detiene(f):
    try:
        f()
        return False, "no se detuvo"
    except SystemExit as e:
        return True, str(e)


def escribir(dir_, tabla, reproducen=True, huella=None):
    ruta = os.path.join(dir_, "pred.csv.gz")
    tabla.to_csv(ruta, index=False, float_format="%.17g", compression="gzip")
    h = hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes()).hexdigest()
    with open(os.path.join(dir_, "pred.json"), "w", encoding="utf-8") as f:
        json.dump({"sha256": fc.sha256(ruta), "sha256_de_las_puntuaciones_float64": huella or h,
                   "reproducen_fase4": {"M3limpio": reproducen, "M2": True}}, f)
    return ruta


def main():
    # P
    rng = np.random.default_rng(0)
    for j in range(5):
        diffs = list(rng.normal(0.01, 0.02, size=50))
        igual = fc.nadeau_bengio(diffs, 5, 0.95) == _nadeau_bengio(diffs, 5)
        b, n = fc.nadeau_bengio(diffs, 5, fc.CONFIANZA_BONFERRONI), _nadeau_bengio(diffs, 5)
        mas_ancho = (b[0] <= n[0] and b[1] >= n[1] and (b[1] - b[0]) > (n[1] - n[0])
                     and abs((b[0] + b[1]) - (n[0] + n[1])) <= 2e-4)
        caso(f"P · 95 % igual a _nadeau_bengio y Bonferroni más ancho, serie {j}", igual and mas_ancho,
             f"NB {n}, Bonferroni {b}")
    distinto = fc.nadeau_bengio(diffs, 10, 0.95) != _nadeau_bengio(diffs, 5)
    caso("P · con otra razón de pliegues ya no coincide (debe fallar)", distinto)
    caso("P · confianza de Bonferroni", abs(fc.CONFIANZA_BONFERRONI - (1 - 0.05 / 3)) < 1e-15,
         f"{fc.CONFIANZA_BONFERRONI}")

    # Q y R
    v = rng.uniform(size=3000) ** 3
    tabla = pd.DataFrame({"modelo": np.repeat(["M3limpio", "M2"], 1500), "semilla": 0,
                          "pliegue": np.tile(np.repeat([0, 1, 2], 500), 2),
                          "isic_id": [f"ISIC_{i % 1500}" for i in range(3000)], "puntuacion": v})
    d = tempfile.mkdtemp()
    try:
        ruta = escribir(d, tabla)
        por, _ = fc.cargar_predicciones(ruta)
        ids, s = por[("M2", 0, 1)]
        exacto = np.array_equal(s, v[2000:2500]) and list(ids[:2]) == ["ISIC_500", "ISIC_501"]
        caso("Q · lee con round_trip y agrupa por modelo, semilla y pliegue", exacto and len(por) == 6)
        otra = tabla.copy()
        otra.loc[7, "puntuacion"] += 1e-12
        otra.to_csv(ruta, index=False, float_format="%.17g", compression="gzip")
        ok, m = se_detiene(lambda: fc.cargar_predicciones(ruta))
        caso("Q · archivo cambiado tras su procedencia (debe fallar)", ok and "SHA-256" in m, m[-60:])
        ruta = escribir(d, tabla, reproducen=False)
        ok, m = se_detiene(lambda: fc.cargar_predicciones(ruta))
        caso("Q · los controles no reprodujeron la Fase 4 (debe fallar)", ok and "reprodujeron" in m, m[-60:])
        ruta = escribir(d, tabla, huella="0" * 64)
        ok, m = se_detiene(lambda: fc.cargar_predicciones(ruta))
        caso("Q · huella de las puntuaciones distinta (debe fallar)", ok and "huella" in m, m[-60:])
        ruta = escribir(d, tabla)
        por, _ = fc.cargar_predicciones(ruta)
        esperado = np.array([f"ISIC_{i}" for i in range(500, 1000)])
        bien = np.array_equal(fc.guardada(por, "M2", 0, 1, esperado), v[2000:2500])
        caso("R · los isic_id en el orden de la validación", bien)
        ok, m = se_detiene(lambda: fc.guardada(por, "M2", 0, 1, esperado[::-1]))
        caso("R · los isic_id en otro orden (debe fallar)", ok and "orden" in m, m[-60:])
    finally:
        shutil.rmtree(d)

    # S
    # Menos del 0,3 % de positivos, como en los datos: el sobremuestreo de M3 limpio
    # sube la proporción hasta 0,003 y no puede bajarla.
    n = 20000
    x_tr = pd.DataFrame({"a": rng.normal(size=n), "oh": pd.Series(rng.integers(0, 2, n)).astype("category")})
    grupos = np.repeat(np.arange(400), n // 400)
    y_tr = np.zeros(n, dtype=int)
    y_tr[rng.choice(n, 30, replace=False)] = 1
    p = rng.uniform(size=n)
    ap = {"tr": {"puntuacion": p, "razon": (pd.Series(p) / pd.Series(p).groupby(grupos).transform("mean")).to_numpy()},
          "va": {"puntuacion": [], "razon": []}}
    xc_tr, _ = fase4b.con_imagen(x_tr, x_tr.iloc[:0], ap)
    r = fc.comprobar_alineacion(x_tr, xc_tr, ap, 0, y_tr, grupos)
    caso("S · alineación con las columnas de con_imagen", r["antes"] and r["razon"] and r["despues"], f"{r}")
    corrido = xc_tr.copy()
    for c in fase4b.COLUMNAS_IMAGEN:
        corrido[c] = np.roll(corrido[c].to_numpy(), 1)
    r = fc.comprobar_alineacion(x_tr, corrido, ap, 0, y_tr, grupos)
    caso("S · columnas corridas una fila (debe fallar)", not r["antes"] and not r["razon"], f"{r}")

    print(f"\n{sum(resultados)} de {len(resultados)} casos como se esperaba")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())

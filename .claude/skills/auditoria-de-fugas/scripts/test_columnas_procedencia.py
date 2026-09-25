#!/usr/bin/env python3
"""
test_columnas_procedencia.py — control positivo de la exclusión de las
columnas de procedencia (attribution, copyright_license).

La exclusión es una decisión de la persona (PLAN.md, Fase 1, 2026-09-25)
y entra por auditoria-de-fugas, como las demás: modelado-baseline la lee
del reporte, no la decide (guardarraíl 1 de CLAUDE.md). El control corre
los dos scripts de verdad sobre datos sintéticos, en un directorio
temporal, y mira las variables que usó el modelo.

Casos:
  A. El reporte de fugas trae la categoría con las dos columnas y su motivo.
  B. Ninguna de las dos aparece entre las variables del modelo.
  C. El caso discrimina: con el mismo reporte sin la categoría, las dos sí
     aparecen. La exclusión viene del reporte y de nada más.

No toca data/ ni outputs/.

Uso:
    python .claude/skills/auditoria-de-fugas/scripts/test_columnas_procedencia.py
Devuelve 0 si los tres casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

SKILLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROCEDENCIA = ["attribution", "copyright_license"]


def escribir_sinteticos(d):
    rng = np.random.default_rng(0)
    filas = []
    for i in range(160):
        centro = "Centro A" if i % 2 == 0 else "Centro B"
        licencia = "CC-BY" if centro == "Centro A" else "CC-BY-NC"
        for j in range(30):
            # Los positivos se concentran en el centro A, así que la
            # procedencia sí tiene señal: si entrara al modelo, se usaría.
            y = int(j == 0 and i % 4 == 0)
            filas.append((f"P{i:03d}", round(rng.normal(1.5 * y, 1), 1), round(rng.normal(0, 1), 1),
                          rng.choice(["torso", "pierna"]), centro, licencia, y))
    csv = os.path.join(d, "sintetico.csv")
    pd.DataFrame(filas, columns=["patient_id", "v1", "v2", "sitio", "attribution",
                                 "copyright_license", "target"]).to_csv(csv, index=False)
    holdout = os.path.join(d, "holdout.json")
    with open(holdout, "w", encoding="utf-8") as f:
        json.dump({"pacientes_reservados": [f"P{i:03d}" for i in range(0, 160, 5)]}, f)
    return csv, holdout


def correr(script, argumentos):
    r = subprocess.run([sys.executable, os.path.join(SKILLS, script)] + argumentos,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{script} terminó con código {r.returncode}:\n{r.stderr}")


def modelar(csv, holdout, reporte, out):
    correr("modelado-baseline/scripts/train_and_evaluate.py",
           ["--data", csv, "--group-col", "patient_id", "--target-col", "target",
            "--leakage-report", reporte, "--holdout", holdout, "--out", out])
    with open(f"{out}.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    with tempfile.TemporaryDirectory() as d:
        csv, holdout = escribir_sinteticos(d)
        fugas = os.path.join(d, "fugas")
        correr("auditoria-de-fugas/scripts/audit_leakage.py",
               ["--train", csv, "--group-col", "patient_id", "--target-col", "target",
                "--holdout", holdout, "--out", fugas])
        with open(f"{fugas}.json", encoding="utf-8") as f:
            reporte = json.load(f)
        con = modelar(csv, holdout, f"{fugas}.json", os.path.join(d, "con"))

        sin_categoria = {k: v for k, v in reporte.items() if k != "columnas_procedencia"}
        ruta_sin = os.path.join(d, "fugas-sin-categoria.json")
        with open(ruta_sin, "w", encoding="utf-8") as f:
            json.dump(sin_categoria, f)
        sin = modelar(csv, holdout, ruta_sin, os.path.join(d, "sin"))

    casos = [
        ("A. el reporte de fugas trae la categoría con su motivo",
         reporte.get("columnas_procedencia") == PROCEDENCIA and bool(reporte.get("motivo_columnas_procedencia")),
         f"columnas_procedencia: {reporte.get('columnas_procedencia')}"),
        ("B. ninguna columna de procedencia entre las variables del modelo",
         not set(PROCEDENCIA) & set(con["features_usadas"]) and set(PROCEDENCIA) <= set(con["columnas_excluidas"]),
         f"features_usadas: {con['features_usadas']}"),
        ("C. el caso discrimina: sin la categoría en el reporte, las dos entran",
         set(PROCEDENCIA) <= set(sin["features_usadas"]),
         f"features_usadas sin la categoría: {sin['features_usadas']}"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

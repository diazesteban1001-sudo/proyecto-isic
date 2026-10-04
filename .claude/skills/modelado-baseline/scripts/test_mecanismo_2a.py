#!/usr/bin/env python3
"""
test_mecanismo_2a.py — controles de mecanismo_2a.py, antes de correrlo sobre
los datos reales. Por el corolario de la regla 6 de CLAUDE.md, cada medida
tiene que poder fallar.

Parte 1, medir() sobre puntuaciones construidas:
  A. Satura sobre los negativos: el 1 % de los negativos con probabilidad
     1,0, por encima de todos los positivos, y los positivos abajo. Las
     medidas tienen que detectarlo: negativos >= 0,999 y en el máximo, ningún
     positivo ahí, y el rango percentil de los positivos bajo.
  B. No satura: puntuaciones continuas por debajo de 0,999, con el máximo en
     un positivo. Las mismas medidas tienen que dar cero donde A da más.
  C. Un caso de cuatro lesiones calculado a mano, con un empate, para el
     rango percentil, la mediana de los positivos y el número de valores
     distintos.
  La pAUC de medir() es la de pauc_above_tpr() en A y B.

Parte 2, de extremo a extremo sobre un CSV sintético:
  D. Con la referencia que escribe train_and_evaluate.py sobre los mismos
     datos, el control pasa y se escriben el .json y el .md.
  E. Con esa referencia alterada en un pliegue del 2a, el script se detiene
     con «CONTROL FALLIDO» y no escribe nada.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_mecanismo_2a.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
from mecanismo_2a import medir  # noqa: E402
from train_and_evaluate import pauc_above_tpr  # noqa: E402


def satura(m):
    """Lo que el caso A tiene y el B no: negativos en lo más alto y ningún
    positivo ahí."""
    return m["frac_neg_ge_0999"] > 0 and m["frac_neg_en_max"] > 0 and m["frac_pos_en_max"] == 0


def caso_a():
    rng = np.random.default_rng(1)
    neg = np.concatenate([rng.uniform(0.0, 0.01, 990), np.ones(10)])
    pos = rng.uniform(0.001, 0.005, 20)
    return np.r_[np.zeros(1000), np.ones(20)], np.r_[neg, pos]


def caso_b():
    rng = np.random.default_rng(2)
    neg = rng.uniform(0.0, 0.5, 1000)
    pos = np.r_[rng.uniform(0.3, 0.9, 19), 0.95]
    return np.r_[np.zeros(1000), np.ones(20)], np.r_[neg, pos]


def datos_sinteticos(ruta):
    rng = np.random.default_rng(7)
    filas = []
    for paciente in range(60):
        n = 50
        x1 = rng.normal(size=n)
        prob = 1 / (1 + np.exp(-(x1 * 2.0 - 4.5)))
        target = (rng.uniform(size=n) < prob).astype(int)
        if paciente % 6 == 0:
            target[0] = 1
        for i in range(n):
            filas.append({
                "isic_id": f"ISIC_{paciente:03d}_{i:03d}",
                "patient_id": f"IP_{paciente:03d}",
                "target": int(target[i]),
                "x1": x1[i],
                "x2": rng.normal(),
                "x3": rng.normal() if rng.uniform() > 0.1 else np.nan,
                "sitio": rng.choice(["a", "b", "c"]),
            })
    pd.DataFrame(filas).to_csv(ruta, index=False)


def correr(script, args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True)


def main():
    casos = []

    ya, pa = caso_a()
    yb, pb = caso_b()
    ma, mb = medir(ya, pa), medir(yb, pb)
    casos.append(("A. satura sobre los negativos: las medidas lo detectan",
                  satura(ma) and ma["frac_neg_ge_0999"] == 0.01 and ma["frac_pos_ge_0999"] == 0
                  and ma["rango_medio_pos"] < 0.5,
                  {k: ma[k] for k in ("frac_neg_ge_0999", "frac_pos_ge_0999", "frac_neg_en_max",
                                      "frac_pos_en_max", "rango_medio_pos")}))
    casos.append(("B. no satura: las mismas medidas no lo detectan",
                  not satura(mb) and mb["frac_neg_ge_0999"] == 0 and mb["frac_neg_en_max"] == 0
                  and mb["frac_pos_en_max"] == 0.05,
                  {k: mb[k] for k in ("frac_neg_ge_0999", "frac_neg_en_max", "frac_pos_en_max",
                                      "rango_medio_pos")}))
    mc = medir([0, 0, 1, 1], [0.1, 0.4, 0.4, 0.9])
    casos.append(("C. caso a mano: rango percentil 0,6875, 3 valores, ningún negativo sobre la mediana 0,65",
                  abs(mc["rango_medio_pos"] - 0.6875) < 1e-12 and mc["n_valores_distintos"] == 3
                  and mc["frac_neg_sobre_mediana_pos"] == 0.0 and mc["frac_pos_en_max"] == 0.5,
                  mc))
    casos.append(("la pAUC de medir() es la de pauc_above_tpr()",
                  ma["pauc"] == pauc_above_tpr(ya, pa) and mb["pauc"] == pauc_above_tpr(yb, pb),
                  (ma["pauc"], mb["pauc"])))

    with tempfile.TemporaryDirectory() as tmp:
        csv = os.path.join(tmp, "train.csv")
        datos_sinteticos(csv)
        fugas = os.path.join(tmp, "fugas.json")
        with open(fugas, "w") as f:
            json.dump({"columnas_solo_en_train": [], "columnas_constantes": [],
                       "columnas_identificador": ["isic_id"], "columnas_procedencia": []}, f)
        holdout = os.path.join(tmp, "holdout.json")
        with open(holdout, "w") as f:
            json.dump({"pacientes_reservados": ["IP_059"]}, f)
        comunes = ["--data", csv, "--group-col", "patient_id", "--target-col", "target", "--n-splits", "5",
                   "--seed", "42", "--leakage-report", fugas, "--holdout", holdout]
        ref = os.path.join(tmp, "referencia")
        r = correr("train_and_evaluate.py", comunes + ["--out", ref])
        if r.returncode != 0:
            print(f"[FALLA] train_and_evaluate.py no corrió sobre los datos sintéticos: {r.stderr[-400:]}")
            return 1

        sal_d = os.path.join(tmp, "mecanismo-d")
        rd = correr("mecanismo_2a.py", comunes + ["--referencia", f"{ref}.json", "--out", sal_d])
        escrito_d = os.path.exists(f"{sal_d}.json") and os.path.exists(f"{sal_d}.md")
        control_d = None
        if escrito_d:
            with open(f"{sal_d}.json") as f:
                control_d = json.load(f)["control_pauc_contra_referencia"]
            with open(f"{sal_d}.md") as f:
                lineas_md = len(f.read().splitlines())
        casos.append(("D. con la referencia correcta: el control pasa y escribe .json y .md (≤ 15 líneas)",
                      rd.returncode == 0 and escrito_d and all(c["coincide"] for c in control_d.values())
                      and lineas_md <= 15,
                      (rd.returncode, escrito_d, rd.stderr.strip()[-200:])))

        with open(f"{ref}.json") as f:
            alterada = json.load(f)
        alterada["nivel_2a_gradient_boosting_sin_balancear"]["pauc_por_fold"][0] += 0.0001
        ref_e = os.path.join(tmp, "referencia-alterada.json")
        with open(ref_e, "w") as f:
            json.dump(alterada, f)
        sal_e = os.path.join(tmp, "mecanismo-e")
        re_ = correr("mecanismo_2a.py", comunes + ["--referencia", ref_e, "--out", sal_e])
        casos.append(("E. con la referencia alterada en un pliegue del 2a: se detiene y no escribe nada",
                      re_.returncode != 0 and "CONTROL FALLIDO" in re_.stderr
                      and not os.path.exists(f"{sal_e}.json") and not os.path.exists(f"{sal_e}.md"),
                      (re_.returncode, re_.stderr.strip().splitlines()[-1:] if re_.stderr else "")))

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

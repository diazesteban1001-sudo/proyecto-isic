#!/usr/bin/env python3
"""
test_efecto_particion.py — controles de efecto_particion.py, antes de
correrlo sobre los datos reales. Por el corolario de la regla 6 de
CLAUDE.md, la medida tiene que poder dar las dos respuestas, y el control
tiene que poder fallar.

Dos conjuntos sintéticos de 80 pacientes con 40 lesiones cada uno. En los
dos, tres variables marcan al paciente: casi iguales en todas sus lesiones y
sin relación con la etiqueta de un paciente nuevo.

  A. Con efecto de sujeto: el riesgo de cada lesión depende solo de un
     efecto aleatorio de su paciente. Con la partición por filas, el modelo
     ve lesiones del mismo paciente en entrenamiento y puede aprender su
     efecto a través de esas variables; con la partición por paciente, no.
     El AUC del nivel 2b por filas tiene que superar al de por paciente en
     todas las semillas, y por más de 0,1 de media.
  B. Sin efecto de sujeto: el riesgo depende solo de una variable de la
     lesión. Las dos particiones tienen que dar un AUC parecido: menos de
     0,03 de diferencia de medias en el nivel 2b.
  C. El control: con la referencia de evaluar_repetido.py sobre los mismos
     datos, la corrida escribe; con esa referencia alterada en un pliegue,
     se detiene con «CONTROL FALLIDO» y no escribe nada.
  D. El .md tiene como mucho 15 líneas.

Para que corra en un minuto usa tres semillas, no diez.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_efecto_particion.py
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
SEMILLAS = ["0", "1", "2"]
N2B = "nivel_2b_gradient_boosting_balanceado"


def datos(ruta, efecto_de_sujeto, semilla):
    rng = np.random.default_rng(semilla)
    filas = []
    for p in range(80):
        firma = rng.normal(size=3)
        efecto = rng.normal()
        for i in range(40):
            lesion = rng.normal()
            logit = (-3.5 + 2.5 * efecto) if efecto_de_sujeto else (-3.5 + 2.0 * lesion)
            filas.append({
                "isic_id": f"ISIC_{p:03d}_{i:03d}", "patient_id": f"IP_{p:03d}",
                "target": int(rng.uniform() < 1 / (1 + np.exp(-logit))),
                "v1": firma[0] + rng.normal(scale=0.05), "v2": firma[1] + rng.normal(scale=0.05),
                "v3": firma[2] + rng.normal(scale=0.05), "lesion": lesion,
            })
    pd.DataFrame(filas).to_csv(ruta, index=False)


def correr(script, args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True)


def caso(tmp, nombre, efecto_de_sujeto):
    csv = os.path.join(tmp, f"{nombre}.csv")
    datos(csv, efecto_de_sujeto, 7 if efecto_de_sujeto else 8)
    fugas = os.path.join(tmp, "fugas.json")
    with open(fugas, "w") as f:
        json.dump({"columnas_solo_en_train": [], "columnas_constantes": [],
                   "columnas_identificador": ["isic_id"], "columnas_procedencia": []}, f)
    holdout = os.path.join(tmp, "holdout.json")
    with open(holdout, "w") as f:
        json.dump({"pacientes_reservados": ["IP_079"]}, f)
    comunes = ["--data", csv, "--group-col", "patient_id", "--target-col", "target", "--n-splits", "5",
               "--leakage-report", fugas, "--holdout", holdout, "--semillas", *SEMILLAS]
    ref = os.path.join(tmp, f"{nombre}-referencia")
    r = correr("evaluar_repetido.py", comunes + ["--out", ref])
    if r.returncode != 0:
        raise SystemExit(f"evaluar_repetido.py no corrió sobre {nombre}: {r.stderr[-400:]}")
    out = os.path.join(tmp, f"{nombre}-efecto")
    r = correr("efecto_particion.py", comunes + ["--referencia", f"{ref}.json", "--out", out])
    if r.returncode != 0:
        return None, comunes, ref, r.stderr.strip().splitlines()[-1:]
    with open(f"{out}.json") as f:
        res = json.load(f)
    with open(f"{out}.md") as f:
        n_md = len(f.read().splitlines())
    return (res, n_md), comunes, ref, ""


def main():
    casos = []
    with tempfile.TemporaryDirectory() as tmp:
        a, comunes_a, ref_a, err_a = caso(tmp, "con-sujeto", True)
        b, _, _, err_b = caso(tmp, "sin-sujeto", False)
        if a is None or b is None:
            print(f"[FALLA] efecto_particion.py no corrió: {err_a or err_b}")
            return 1
        (ra, md_a), (rb, md_b) = a, b
        da = ra["filas_menos_paciente"][N2B]["auc"]
        db = rb["filas_menos_paciente"][N2B]["auc"]
        casos.append(("A. con efecto de sujeto: el AUC del 2b por filas supera al de por paciente en todas las "
                      "semillas, por más de 0,1",
                      da["semillas_filas_mejor"] == len(SEMILLAS) and da["diferencia_de_medias"] > 0.1, da))
        casos.append(("B. sin efecto de sujeto: el AUC del 2b se parece en las dos particiones (menos de 0,03)",
                      abs(db["diferencia_de_medias"]) < 0.03, db))
        casos.append(("C1. con la referencia correcta, el control pasa",
                      all(c["coincide"] for c in ra["control_paciente_contra_referencia"].values()),
                      ra["control_paciente_contra_referencia"]))

        with open(f"{ref_a}.json") as f:
            alterada = json.load(f)
        alterada[N2B]["pauc_por_semilla_y_fold"]["0"][0] += 0.0001
        ref_e = os.path.join(tmp, "referencia-alterada.json")
        with open(ref_e, "w") as f:
            json.dump(alterada, f)
        out_e = os.path.join(tmp, "efecto-alterada")
        r = correr("efecto_particion.py", comunes_a + ["--referencia", ref_e, "--out", out_e])
        casos.append(("C2. con la referencia alterada en un pliegue del 2b: se detiene y no escribe nada",
                      r.returncode != 0 and "CONTROL FALLIDO" in r.stderr
                      and not os.path.exists(f"{out_e}.json") and not os.path.exists(f"{out_e}.md"),
                      (r.returncode, r.stderr.strip().splitlines()[-1:])))
        casos.append(("D. el .md tiene como mucho 15 líneas", md_a <= 15 and md_b <= 15, (md_a, md_b)))

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

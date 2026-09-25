#!/usr/bin/env python3
"""
test_datos_desarrollo.py — control positivo de datos_desarrollo.py.

Corolario de la regla 6 de CLAUDE.md: un chequeo que no puede fallar no
vale nada, así que se fuerza el caso que debería detectar y se comprueba
que se dispara. Todo con datos sintéticos en un directorio temporal; no
toca data/ ni outputs/.

Casos:
  A. Sin holdout-pacientes.json el cargador falla, y falla antes de leer
     el CSV (se le pasa un CSV que no existe).
  B. Con un CSV contaminado —contiene pacientes reservados— y la
     exclusión desactivada, la comprobación se dispara.
  C. Con el mismo CSV y la exclusión activa, no queda ningún paciente
     reservado y el resto de filas llega intacto.
  D. Los cinco scripts de las cuatro skills instrumento pasan por el
     cargador: sin holdout, los cinco terminan con código 1 y el mensaje
     del cargador, sin escribir nada.

Uso:
    python .claude/skills/diseno-validacion/scripts/test_datos_desarrollo.py
Devuelve 0 si los cuatro casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import datos_desarrollo  # noqa: E402

SKILLS = os.path.normpath(os.path.join(AQUI, "..", ".."))
RAIZ = os.path.normpath(os.path.join(SKILLS, "..", ".."))
RESERVADOS = ["P02", "P07"]


def escribir_sinteticos(d):
    filas = [(f"P{i:02d}", i * 10 + j, int(j == 0 and i % 3 == 0)) for i in range(1, 11) for j in range(3)]
    csv = os.path.join(d, "contaminado.csv")
    pd.DataFrame(filas, columns=["patient_id", "x", "target"]).to_csv(csv, index=False)
    holdout = os.path.join(d, "holdout-pacientes.json")
    with open(holdout, "w", encoding="utf-8") as f:
        json.dump({"semilla": 0, "pacientes_reservados": RESERVADOS}, f)
    return csv, holdout


def falla_con(fn, texto):
    try:
        fn()
    except SystemExit as e:
        return texto in str(e.code), str(e.code)
    return False, "no falló"


def caso_a(d):
    return falla_con(
        lambda: datos_desarrollo.cargar_desarrollo(
            os.path.join(d, "no-existe.csv"), ruta_holdout=os.path.join(d, "no-existe.json")
        ),
        "no existe",
    )


def caso_b(csv, holdout):
    original = datos_desarrollo.excluir_reservados
    datos_desarrollo.excluir_reservados = lambda df, reservados, group_col: df
    try:
        return falla_con(lambda: datos_desarrollo.cargar_desarrollo(csv, ruta_holdout=holdout), "2 pacientes del conjunto reservado")
    finally:
        datos_desarrollo.excluir_reservados = original


def caso_c(csv, holdout):
    df, datos = datos_desarrollo.cargar_desarrollo(csv, ruta_holdout=holdout)
    completo = pd.read_csv(csv)
    esperado = completo[~completo["patient_id"].isin(RESERVADOS)].reset_index(drop=True)
    ok = (
        not set(df["patient_id"]) & set(RESERVADOS)
        and df.equals(esperado)
        and len(df) == len(completo) - 3 * len(RESERVADOS)
        and datos["conjunto"] == "desarrollo"
    )
    return ok, f"{len(completo)} filas leídas, {len(df)} entregadas, reservados presentes: {sorted(set(df['patient_id']) & set(RESERVADOS))}"


def caso_d(csv, d):
    salida = os.path.join(d, "salidas")
    os.makedirs(salida)
    sin_holdout = os.path.join(d, "no-existe.json")
    fugas = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
    comunes = ["--group-col", "patient_id", "--target-col", "target", "--holdout", sin_holdout]
    scripts = {
        "eda-diagnostico/eda_profile.py": ["--train", csv, "--out", os.path.join(salida, "eda")] + comunes,
        "auditoria-de-fugas/audit_leakage.py": ["--train", csv, "--out", os.path.join(salida, "fugas")] + comunes,
        "diseno-validacion/build_and_audit_cv.py": ["--data", csv, "--out", os.path.join(salida, "cv")] + comunes,
        "modelado-baseline/train_and_evaluate.py": ["--data", csv, "--leakage-report", fugas, "--out", os.path.join(salida, "mb")] + comunes,
        "modelado-baseline/evaluar_repetido.py": ["--data", csv, "--leakage-report", fugas, "--out", os.path.join(salida, "vr")] + comunes,
    }
    detalle, ok = [], True
    for nombre, argumentos in scripts.items():
        skill, script = nombre.split("/")
        r = subprocess.run(
            [sys.executable, os.path.join(SKILLS, skill, "scripts", script)] + argumentos,
            capture_output=True, text=True,
        )
        bien = r.returncode == 1 and "El conjunto reservado no está sellado" in r.stderr
        ok &= bien
        detalle.append(f"{nombre}: código {r.returncode}, {'mensaje del cargador' if bien else r.stderr.strip()[-200:]}")
    escritos = os.listdir(salida)
    ok &= not escritos
    detalle.append(f"archivos escritos: {escritos or 'ninguno'}")
    return ok, "\n      ".join(detalle)


def main():
    with tempfile.TemporaryDirectory() as d:
        csv, holdout = escribir_sinteticos(d)
        casos = [
            ("A. sin holdout-pacientes.json, falla antes de leer el CSV", caso_a(d)),
            ("B. CSV contaminado con la exclusión desactivada, la comprobación se dispara", caso_b(csv, holdout)),
            ("C. CSV contaminado con la exclusión activa, no queda ningún reservado", caso_c(csv, holdout)),
            ("D. los cinco scripts instrumento pasan por el cargador", caso_d(csv, d)),
        ]
    fallos = 0
    for titulo, (ok, detalle) in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

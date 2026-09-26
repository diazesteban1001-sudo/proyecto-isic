#!/usr/bin/env python3
"""
test_contexto_paciente.py — control positivo de contexto_paciente.py.

  A. Casos calculables a mano: z-score, conteo, sumas de área (con la zona
     anatómica faltante como grupo propio) y LOF = −1 con menos de 3 lesiones.
  B. Barajar las etiquetas no cambia ninguna variable. El caso discrimina: una
     variante con fuga, que añade la media de la etiqueta del paciente, sí cambia
     y la prueba la detecta.
  C. Cada paciente solo depende de sí mismo: cambiar las lesiones de un paciente
     no cambia ninguna variable de otro, y sí las del propio.
  D. El z-score, los conteos, las sumas de área y las variables derivadas del
     LOF frente a `read_data` del ganador (celdas 3 y 7 de top-model.ipynb).
  E. El LOF frente a `get_lof_score` del ganador (celdas 10 y 11). Se comparan en
     el caso en que su estandarización global y la nuestra dentro del paciente
     coinciden: un solo paciente, sin faltantes.

D y E ejecutan el código del notebook versionado **sin modificarlo**, en un
intérprete de 2024 indicado con PYTHON_GUION_ISIC: pandas < 3, scikit-learn
< 1.6 y polars. Con el scikit-learn actual, get_lof_score falla: sus variables
del LOF traen dos columnas repetidas, y el StandardScaler de hoy las rechaza;
el de 2024 las aceptaba, así que en el ganador pesaban doble. Si falta el
intérprete, D y E salen como NO CORRIDO, a la vista.

Todo con datos sintéticos, salvo B, que además corre sobre el conjunto de
desarrollo real si existe (NO CORRIDO, a la vista, si no).

Uso:
    python .claude/skills/modelado-baseline/scripts/test_contexto_paciente.py
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import json
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import contexto_paciente as cp  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
NOTEBOOK = os.path.join(RAIZ, "referencias", "novoselskiy-2024-isic2024", "notebooks", "top-model.ipynb")
PYTHON_2024 = os.environ.get("PYTHON_GUION_ISIC")
COLUMNAS_LOF = sorted(set(cp.TOP_LOF_FEATURES) - set(cp.derivadas_lof(pd.DataFrame(
    {c: [1.0] for c in ["tbp_lv_H", "tbp_lv_Hext", "clin_size_long_diam_mm", "age_approx", "tbp_lv_color_std_mean",
                        "tbp_lv_radial_color_std_max", "tbp_lv_x", "tbp_lv_y", "tbp_lv_z", "tbp_lv_nevi_confidence",
                        "tbp_lv_deltaLBnorm", "tbp_lv_norm_color"]})).columns))
BRUTAS = sorted(set(COLUMNAS_LOF) | {"tbp_lv_H", "tbp_lv_Hext", "clin_size_long_diam_mm", "age_approx",
                                     "tbp_lv_color_std_mean", "tbp_lv_radial_color_std_max", "tbp_lv_x", "tbp_lv_y",
                                     "tbp_lv_z", "tbp_lv_nevi_confidence", "tbp_lv_deltaLBnorm", "tbp_lv_norm_color",
                                     "tbp_lv_areaMM2"})


def sintetico(semilla=0, pacientes=12):
    rng = np.random.default_rng(semilla)
    filas = []
    for p in range(pacientes):
        n = [1, 2, 5, 40, 80][p % 5]
        edad = float(rng.integers(30, 80))
        for j in range(n):
            fila = {c: float(rng.normal(10, 3)) for c in BRUTAS}
            fila.update({"patient_id": f"P{p}", "age_approx": edad, "tbp_lv_areaMM2": float(rng.uniform(1, 20)),
                         "anatom_site_general": [None, "torso", "pierna"][j % 3], "target": int(rng.random() < 0.05)})
            filas.append(fila)
    return pd.DataFrame(filas)


def iguales(a, b):
    return a.shape == b.shape and bool(((a == b) | (a.isna() & b.isna())).all().all())


def caso_a():
    df = pd.DataFrame({
        "patient_id": ["A", "A", "A", "B", "B"],
        "v": [1.0, 2.0, 3.0, 10.0, 10.0],
        "tbp_lv_areaMM2": [1.0, 2.0, 4.0, 8.0, 16.0],
        "anatom_site_general": ["torso", "torso", None, None, "pierna"],
        **{c: [1.0, 2.0, 3.0, 4.0, 5.0] for c in BRUTAS if c not in ("tbp_lv_areaMM2",)},
    })
    out = cp.variables_contexto_paciente(df, ["v"])
    # A: media 2, desviación muestral 1 → z = (x − 2) / (1 + 1e-5). B: desviación 0 → z = 0.
    z_a = [(x - 2) / (1 + cp.ERR) for x in (1, 2, 3)]
    ok = (np.allclose(out["v_patient_norm"], z_a + [0.0, 0.0])
          and out["count_per_patient"].tolist() == [3, 3, 3, 2, 2]
          and out["tbp_lv_areaMM2_patient"].tolist() == [7, 7, 7, 24, 24]
          and out["tbp_lv_areaMM2_bp"].tolist() == [3, 3, 4, 8, 16]
          and out["of"].iloc[3:].tolist() == [-1.0, -1.0] and bool((out["of"].iloc[:3] != -1).all()))
    return ok, out.round(4).to_dict("list")


def caso_b(df, numericas):
    base = cp.variables_contexto_paciente(df, numericas)
    barajado = df.copy()
    barajado["target"] = np.random.default_rng(1).permutation(df["target"].to_numpy())
    otra = cp.variables_contexto_paciente(barajado, numericas)

    def con_fuga(d, num):  # mutante: usa la etiqueta del paciente
        out = cp.variables_contexto_paciente(d, num)
        out["fuga"] = d.groupby("patient_id")["target"].transform("mean")
        return out
    fuga_ok = not iguales(con_fuga(df, numericas), con_fuga(barajado, numericas))
    return iguales(base, otra) and fuga_ok, f"iguales tras barajar: {iguales(base, otra)} · la variante con fuga cambia: {fuga_ok}"


def caso_c():
    df = sintetico()
    numericas = ["tbp_lv_H", "tbp_lv_areaMM2", "age_approx"]
    base = cp.variables_contexto_paciente(df, numericas)
    otro = df.copy()
    en_p3 = otro["patient_id"] == "P3"
    otro.loc[en_p3, BRUTAS] = otro.loc[en_p3, BRUTAS] * 3 + 7
    cambiado = cp.variables_contexto_paciente(otro, numericas)
    fuera = ~en_p3
    ok = iguales(base[fuera], cambiado[fuera]) and not iguales(base[en_p3], cambiado[en_p3])
    return ok, "los demás pacientes, iguales; P3, cambiado" if ok else "falla la localidad"


EJECUTOR = r"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, polars as pl
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
warnings.filterwarnings("ignore")
cuaderno, csv, salida, modo = sys.argv[1:5]
celdas = ["".join(c["source"]) for c in json.load(open(cuaderno, encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
def celda(marca):
    return next(c for c in celdas if marca in c)
esp = {"np": np, "pd": pd, "pl": pl, "Path": Path, "tqdm": tqdm, "StandardScaler": StandardScaler,
       "LocalOutlierFactor": LocalOutlierFactor}
for marca in ("num_cols = [", "def read_data", "def get_lof_score", "top_lof_features = ["):
    exec(celda(marca), esp)
df = esp["read_data"](csv)
if modo == "lof":
    df = esp["get_lof_score"](df, esp["top_lof_features"], output_col_name="of", lof_column="patient_id")
df.to_csv(salida)
"""

NUM_COLS_GANADOR = ["age_approx", "clin_size_long_diam_mm", "tbp_lv_A", "tbp_lv_Aext", "tbp_lv_B", "tbp_lv_Bext",
    "tbp_lv_C", "tbp_lv_Cext", "tbp_lv_H", "tbp_lv_Hext", "tbp_lv_L", "tbp_lv_Lext", "tbp_lv_areaMM2",
    "tbp_lv_area_perim_ratio", "tbp_lv_color_std_mean", "tbp_lv_deltaA", "tbp_lv_deltaB", "tbp_lv_deltaL",
    "tbp_lv_deltaLB", "tbp_lv_deltaLBnorm", "tbp_lv_eccentricity", "tbp_lv_minorAxisMM", "tbp_lv_nevi_confidence",
    "tbp_lv_norm_border", "tbp_lv_norm_color", "tbp_lv_perimeterMM", "tbp_lv_radial_color_std_max", "tbp_lv_stdL",
    "tbp_lv_stdLExt", "tbp_lv_symm_2axis", "tbp_lv_symm_2axis_angle", "tbp_lv_x", "tbp_lv_y", "tbp_lv_z"]


def esquema_completo(semilla, tamanos):
    """Datos sintéticos con todas las columnas que lee read_data, sin faltantes
    numéricos; la zona anatómica sí tiene faltantes, para el área por zona."""
    rng = np.random.default_rng(semilla)
    filas = []
    for p, n in enumerate(tamanos):
        edad = float(rng.integers(30, 80))
        for j in range(n):
            fila = {c: float(rng.uniform(1, 20)) for c in NUM_COLS_GANADOR}
            fila.update({"isic_id": f"ISIC_{p}_{j}", "patient_id": f"P{p}", "age_approx": edad, "target": 0,
                         "sex": "male", "anatom_site_general": ["torso", None, "pierna"][j % 3],
                         "tbp_tile_type": "3D: XP", "tbp_lv_location": "Torso", "tbp_lv_location_simple": "Torso",
                         "attribution": "Centro"})
            filas.append(fila)
    return pd.DataFrame(filas)


def ganador(df, modo):
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        csv, salida, ejecutor = (os.path.join(tmp, f) for f in ("datos.csv", "salida.csv", "ejecutor.py"))
        df.to_csv(csv, index=False)
        open(ejecutor, "w", encoding="utf-8").write(EJECUTOR)
        r = subprocess.run([PYTHON_2024, ejecutor, NOTEBOOK, csv, salida, modo], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"el código del ganador falló en el intérprete de 2024:\n{r.stderr[-2000:]}")
        return pd.read_csv(salida).set_index("isic_id")


def caso_d():
    df = esquema_completo(0, [1, 2, 5, 40, 120, 3])
    suyo = ganador(df, "read_data")
    nuestro = pd.concat([cp.variables_contexto_paciente(df, NUM_COLS_GANADOR), cp.derivadas_lof(df)], axis=1)
    nuestro.index = df["isic_id"]
    columnas = [f"{c}_patient_norm" for c in NUM_COLS_GANADOR] + [
        "count_per_patient", "tbp_lv_areaMM2_patient", "tbp_lv_areaMM2_bp", *cp.derivadas_lof(df.head(1)).columns]
    a, b = nuestro.loc[suyo.index, columnas].astype(float), suyo[columnas].astype(float)
    dif = ((a - b).abs() / (b.abs() + 1)).where(~(a.isna() & b.isna()), 0.0)
    mismos_nan = bool((a.isna() == b.isna()).all().all())
    peor = float(dif.max().max())
    return mismos_nan and peor < 1e-9, f"{len(columnas)} columnas · peor diferencia relativa {peor:.1e} · NaN en los mismos sitios: {mismos_nan}"


def caso_e():
    resultados = []
    for semilla, n in [(0, 12), (1, 40), (2, 200)]:
        df = esquema_completo(semilla, [n])
        suyo = ganador(df, "lof")["of"]
        propio = cp.lof_por_paciente(df).to_numpy()
        resultados.append((n, float(np.abs(suyo.loc[df["isic_id"]].to_numpy() - propio).max())))
    ok = all(d < 1e-9 for _, d in resultados)
    return ok, "max |ganador − propio| por tamaño: " + ", ".join(f"n={n}: {d:.1e}" for n, d in resultados)


def main():
    casos = [("A. valores calculados a mano", *caso_a())]
    df = sintetico(3)
    casos.append(("B. sintético: barajar las etiquetas no cambia nada", *caso_b(df, ["tbp_lv_H", "tbp_lv_areaMM2", "age_approx"])))
    csv = os.path.join(RAIZ, "data", "train-metadata.csv")
    if os.path.exists(csv):
        sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "diseno-validacion", "scripts"))
        from datos_desarrollo import cargar_desarrollo
        from train_and_evaluate import preparar_features
        dev, _ = cargar_desarrollo(csv, "patient_id", os.path.join(RAIZ, "outputs", "holdout-pacientes.json"))
        rep = json.load(open(os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json"), encoding="utf-8"))
        excl = sum((rep.get(k, []) for k in ("columnas_solo_en_train", "columnas_constantes",
                                              "columnas_identificador", "columnas_procedencia")), [])
        numericas, _ = preparar_features(dev, excl, "target", "patient_id")
        casos.append(("B. conjunto de desarrollo real: barajar las etiquetas no cambia nada", *caso_b(dev, numericas)))
    else:
        casos.append(("B. conjunto de desarrollo real", None, f"NO CORRIDO: no existe {csv}"))
    casos.append(("C. cada paciente depende solo de sí mismo", *caso_c()))
    if PYTHON_2024:
        casos.append(("D. z-score, conteos, áreas y derivadas iguales a read_data del ganador", *caso_d()))
        casos.append(("E. LOF igual a get_lof_score del ganador, con un solo paciente", *caso_e()))
    else:
        for titulo in ("D. frente a read_data del ganador", "E. frente a get_lof_score del ganador"):
            casos.append((titulo, None, "NO CORRIDO: falta PYTHON_GUION_ISIC, un intérprete de 2024"))

    fallos = corridos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'NO CORRIDO' if ok is None else ('OK' if ok else 'FALLA')}] {titulo}\n      {detalle}")
        if ok is not None:
            corridos += 1
            fallos += not ok
    print(f"\n{corridos - fallos} de {corridos} casos corridos como se esperaba; {len(casos) - corridos} no corridos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

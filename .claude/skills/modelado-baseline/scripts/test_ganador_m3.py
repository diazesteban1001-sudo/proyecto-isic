#!/usr/bin/env python3
"""
test_ganador_m3.py — control de ganador_m3.py, las variables y el ajuste de M3.

  A. Las listas leídas del notebook: recuentos, repeticiones y exclusiones.
  B. Los parámetros transcritos (CatBoost y remuestreo) están literalmente en sus
     celdas, y random_strength no llega al modelo.
  C. variables_m3 se niega a recibir la etiqueta.
  D. Frente al código del ganador, ejecutado en un intérprete de 2024 indicado con
     PYTHON_GUION_ISIC, sobre el conjunto de desarrollo: todas las variables de M3,
     columna a columna, y los conglomerados. El código del ganador corre con los
     cambios de la especificación: sin las celdas de imagen (14 a 17) ni las
     variables de la celda 19 que dependen de ellas, sin attribution, y con
     n_init=10 en el k-means, que era el valor por defecto en la corrida publicada
     (lo muestra el aviso de la celda 18) y en scikit-learn 1.5.2 ya no lo es.
     El CSV de desarrollo se escribe con las líneas originales del archivo, para
     que polars lo lea como leyó el ganador el suyo, y se comprueba que tiene las
     mismas filas que da cargar_desarrollo.
  E. Las columnas repetidas del LOF pesan doble, y la comprobación D lo ve: el LOF
     sin repeticiones y el LOF con la estandarización dentro del paciente de M2 se
     apartan del ganador. Y el scikit-learn actual rechaza el DataFrame con
     columnas repetidas, que es por qué ganador_m3 le pasa la matriz de numpy.
  F. Regla de la clase 10: el número de árboles no depende de las etiquetas de
     validación. Con ajustar_m3, barajarlas no cambia las predicciones. Con el
     ajuste publicado (eval_set = pliegue de validación) sí, y la prueba lo detecta.

D y E necesitan el intérprete de 2024 y el conjunto de desarrollo; si falta
alguno, salen como NO CORRIDO, a la vista.

Uso:
    PYTHON_GUION_ISIC=/ruta/al/python python .claude/skills/modelado-baseline/scripts/test_ganador_m3.py
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import ast
import csv
import json
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ganador_m3 as g  # noqa: E402
import contexto_paciente as cp  # noqa: E402

RAIZ = g.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HOLDOUT = os.path.join(RAIZ, "outputs", "holdout-pacientes.json")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
PYTHON_2024 = os.environ.get("PYTHON_GUION_ISIC")
warnings.filterwarnings("ignore")


def caso_a():
    L = g.listas_publicadas()
    top = L["top_lof_features"]
    repetidas = sorted({c for c in top if top.count(c) > 1})
    de_imagen = set(L["de_imagen"])
    cluster_imagen = [c for c in L["columns_for_cluster_culculations"] if c in de_imagen]
    recuentos = {k: len(L[k]) for k in ("num_cols", "new_num_cols", "cat_cols", "special_cols", "top_lof_features",
                                        "columns_for_cluster_culculations", "columns_to_drop", "de_imagen")}
    esperado = {"num_cols": 34, "new_num_cols": 42, "cat_cols": 6, "special_cols": 3, "top_lof_features": 17,
                "columns_for_cluster_culculations": 51, "columns_to_drop": 24, "de_imagen": 12}
    derivadas_ok = list(g.derivadas(pd.DataFrame({c: [1.0] for c in L["num_cols"]})).columns) == L["new_num_cols"]
    ok = (recuentos == esperado and repetidas == ["hue_contrast", "position_distance_3d"]
          and len(cluster_imagen) == 8 and "attribution" in L["cat_cols"] and derivadas_ok)
    return ok, (f"{recuentos} · repetidas en top_lof_features: {repetidas} · de la celda 19 sobre imagen: "
                f"{len(cluster_imagen)} · derivadas en el orden de new_num_cols: {derivadas_ok}")


def caso_b():
    c = g.celdas_publicadas()
    literales = [  # (celda, texto que tiene que estar)
        (24, f"'learning_rate': {g.PARAMETROS_CATBOOST['learning_rate']}"),
        (24, f"'l2_leaf_reg': {g.PARAMETROS_CATBOOST['l2_leaf_reg']}"),
        (24, f"'depth': {g.PARAMETROS_CATBOOST['depth']}"),
        (24, f"'bagging_temperature': {g.PARAMETROS_CATBOOST['bagging_temperature']}"),
        (24, f"'border_count': {g.PARAMETROS_CATBOOST['border_count']}"),
        (24, f"'grow_policy': '{g.PARAMETROS_CATBOOST['grow_policy']}'"),
        (24, f"'min_data_in_leaf': {g.PARAMETROS_CATBOOST['min_data_in_leaf']}"),
        (22, f"iterations = {g.PARAMETROS_CATBOOST['iterations']}"),
        (22, f"loss_function = \"{g.PARAMETROS_CATBOOST['loss_function']}\""),
        (22, f"eval_metric='{g.PARAMETROS_CATBOOST['eval_metric']}'"),
        (22, f"od_wait={g.PARAMETROS_CATBOOST['od_wait']}"),
        (22, "task_type='GPU'"),
        (22, f"RandomOverSampler(sampling_strategy= {g.SOBREMUESTREO} , random_state=random_seed)"),
        (22, "RandomUnderSampler(sampling_strategy=sampling_ratio , random_state=random_seed)"),
        (3, f"sampling_ratio = {g.SUBMUESTREO}"),
    ]
    faltan = [(i, t) for i, t in literales if t not in c[i]]
    campos_21 = [n.target.id for n in ast.walk(ast.parse(c[21])) if isinstance(n, ast.AnnAssign)]
    llamada = next(n for n in ast.walk(ast.parse(c[22]))
                   if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "CatBoostClassifier")
    argumentos_22 = [k.arg for k in llamada.keywords]
    sin_random_strength = ("random_strength" not in campos_21 and "random_strength" not in argumentos_22
                           and "random_strength" not in g.PARAMETROS_CATBOOST and "random_strength" in c[24])
    ok = not faltan and sin_random_strength
    return ok, (f"{len(literales) - len(faltan)} de {len(literales)} literales en su celda · random_strength en la "
                f"celda 24 pero no en ModelConfigCB (celda 21) ni en la llamada de la celda 22: {sin_random_strength}"
                + (f" · FALTAN: {faltan}" if faltan else ""))


def caso_c():
    try:
        g.variables_m3(pd.DataFrame({"target": [0], "patient_id": ["P"]}), [])
    except ValueError:
        return True, "variables_m3 rechaza un DataFrame con la columna target"
    return False, "variables_m3 aceptó la etiqueta"


# ---- D y E: frente al ganador, en el intérprete de 2024 ------------------------------

EJECUTOR = r"""
import ast, functools, json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, polars as pl
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
warnings.filterwarnings("ignore")
cuaderno, csv, destino = sys.argv[1:4]
celdas = ["".join(c["source"]) for c in json.load(open(cuaderno, encoding="utf-8"))["cells"]]
esp = {"np": np, "pd": pd, "pl": pl, "Path": Path, "tqdm": tqdm, "StandardScaler": StandardScaler,
       "OneHotEncoder": OneHotEncoder, "LocalOutlierFactor": LocalOutlierFactor,
       "KMeans": functools.partial(KMeans, n_init=10)}  # cambio: el n_init por defecto de la corrida publicada
def correr(i, saltar=None, despues_de_la_primera=None):
    cuerpo = ast.parse(celdas[i]).body
    for k, nodo in enumerate(cuerpo):
        if saltar and saltar in ast.get_source_segment(celdas[i], nodo):
            continue
        exec(compile(ast.Module([nodo], []), f"celda{i}", "exec"), esp)
        if k == 0 and despues_de_la_primera:
            despues_de_la_primera()
correr(3)
esp["cat_cols"].remove("attribution"); esp["feature_cols"].remove("attribution")  # cambio: sin procedencia
for i in (7, 8, 9, 10, 11):
    correr(i)
esp["train_path"] = esp["test_path"] = csv
correr(12, saltar="subm_path")
correr(13)
# celdas 14 a 17 (imagen): no se corren
correr(18)
de_imagen = [v for i in (14, 15, 16, 17) for n in ast.walk(ast.parse(celdas[i]))
             if isinstance(n, ast.AugAssign) and getattr(n.target, "id", "") == "feature_cols" and isinstance(n.value, ast.List)
             for v in ast.literal_eval(n.value)]
def filtrar():  # cambio: sin las variables de conglomerado calculadas sobre imagen
    esp["columns_for_cluster_culculations"] = [c for c in esp["columns_for_cluster_culculations"] if c not in de_imagen]
ids = esp["df_train"].index.to_numpy()
correr(19, despues_de_la_primera=filtrar)
esp["df_train"].index = ids  # el merge de la celda 19 descarta el índice; conserva el orden
drop = next(ast.literal_eval(n.value) for n in ast.parse(celdas[24]).body
            if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "columns_to_drop")
columnas = [c for c in esp["feature_cols"] if c not in drop]
df = esp["df_train"]
np.save(f"{destino}/x.npy", np.column_stack([df[c].astype(float).to_numpy() for c in columnas]))
np.save(f"{destino}/conglomerados.npy", np.asarray(esp["cluster_labels"]))
json.dump({"columnas": columnas, "isic_id": [str(i) for i in ids], "cat_cols": list(esp["cat_cols"])},
          open(f"{destino}/meta.json", "w"))
"""


def csv_de_desarrollo(destino):
    """Las líneas originales del CSV de los pacientes de desarrollo, sin tocar."""
    sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "diseno-validacion", "scripts"))
    from datos_desarrollo import leer_reservados
    reservados = leer_reservados(HOLDOUT)
    with open(CSV, newline="", encoding="utf-8") as f, open(destino, "w", newline="", encoding="utf-8") as h:
        cabecera = f.readline()
        h.write(cabecera)
        i = next(csv.reader([cabecera])).index("patient_id")
        for linea in f:
            if next(csv.reader([linea]))[i] not in reservados:
                h.write(linea)


def comparar_con_ganador(dev, excluidas):
    with tempfile.TemporaryDirectory() as tmp:
        ruta_csv = os.path.join(tmp, "desarrollo.csv")
        csv_de_desarrollo(ruta_csv)
        ejecutor = os.path.join(tmp, "ejecutor.py")
        open(ejecutor, "w", encoding="utf-8").write(EJECUTOR)
        r = subprocess.run([PYTHON_2024, ejecutor, g.NOTEBOOK, ruta_csv, tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"el código del ganador falló en el intérprete de 2024:\n{r.stderr[-3000:]}")
        meta = json.load(open(os.path.join(tmp, "meta.json")))
        suyo = np.load(os.path.join(tmp, "x.npy"))
        sus_conglomerados = np.load(os.path.join(tmp, "conglomerados.npy"))
    return meta, suyo, sus_conglomerados


def particiones_iguales(a, b):
    tabla = pd.crosstab(a, b)
    return bool(((tabla > 0).sum(axis=1) == 1).all() and ((tabla > 0).sum(axis=0) == 1).all())


def casos_d_y_e():
    sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "diseno-validacion", "scripts"))
    from datos_desarrollo import cargar_desarrollo
    from evaluar_repetido import cargar_columnas_excluidas
    dev, _ = cargar_desarrollo(CSV, "patient_id", HOLDOUT)
    excluidas = cargar_columnas_excluidas(FUGAS)
    sin_etiqueta = dev.drop(columns=["target"])
    nuestro, categoricas, inventario = g.variables_m3(sin_etiqueta, excluidas)
    meta, suyo, sus_conglomerados = comparar_con_ganador(dev, excluidas)

    casos = []
    mismas_filas = meta["isic_id"] == dev["isic_id"].astype(str).tolist()
    mismas_columnas = meta["columnas"] == list(nuestro.columns)
    a = nuestro.astype(float).to_numpy()
    detalle = f"{len(meta['columnas'])} columnas y {len(meta['isic_id'])} filas · mismas filas y orden: {mismas_filas} · mismas columnas y orden: {mismas_columnas}"
    if mismas_filas and mismas_columnas:
        nan_a, nan_b = np.isnan(a), np.isnan(suyo)
        mismos_nan = bool((nan_a == nan_b).all())
        dif = np.where(nan_a | nan_b, 0.0, np.abs(a - suyo) / (np.abs(suyo) + 1))
        peor = dif.max(axis=0)
        j = int(np.argmax(peor))
        detalle += (f" · NaN en los mismos sitios: {mismos_nan} · peor diferencia relativa {peor.max():.1e}"
                    f" ({meta['columnas'][j]})")
        casos.append(("D. todas las variables de M3 iguales a las del código del ganador",
                      mismos_nan and peor.max() < 1e-9, detalle))
    else:
        casos.append(("D. todas las variables de M3 iguales a las del código del ganador", False, detalle))

    L = g.listas_publicadas()
    base = g.variables_lectura(sin_etiqueta, L)
    escalada = g.matriz_lof(base, L["top_lof_features"])
    nuestros_conglomerados = g.conglomerados(escalada)
    iguales = particiones_iguales(nuestros_conglomerados, sus_conglomerados)
    casos.append(("D. los 29 conglomerados del k-means, la misma partición", iguales,
                  f"etiquetas idénticas: {bool((nuestros_conglomerados == sus_conglomerados).all())}"))

    # E. Lo que ve la comprobación: las repeticiones y la estandarización global.
    col_of = meta["columnas"].index("of")
    of_ganador = suyo[:, col_of]
    of_nuestro = a[:, col_of]
    rng = np.random.default_rng(0)
    tamanos = dev.groupby("patient_id").size()
    muestra = rng.choice(tamanos[tamanos >= 3].index.to_numpy(), size=60, replace=False)
    en_muestra = dev["patient_id"].isin(muestra).to_numpy()
    unicas = list(dict.fromkeys(L["top_lof_features"]))
    # El estandarizado, sobre todas las filas, como el publicado; el LOF, solo en la muestra.
    sin_repeticion = g.lof_publicado(g.matriz_lof(base, unicas)[en_muestra], dev["patient_id"].to_numpy()[en_muestra])
    m2 = cp.lof_por_paciente(dev[en_muestra].reset_index(drop=True)).to_numpy()
    dif_propio = float(np.abs(of_nuestro - of_ganador).max())
    dif_sin_rep = float(np.abs(sin_repeticion - of_ganador[en_muestra]).max())
    dif_m2 = float(np.abs(m2 - of_ganador[en_muestra]).max())
    casos.append(("E. el LOF de M3 igual al del ganador (columnas repetidas, estandarizado global)",
                  dif_propio < 1e-9, f"max |ganador − M3| = {dif_propio:.1e}, sobre {len(dev)} filas"))
    casos.append(("E. control: sin las repeticiones, el LOF se aparta del ganador",
                  dif_sin_rep > 1e-3, f"max |ganador − sin repeticiones| = {dif_sin_rep:.3g}, en 60 pacientes"))
    casos.append(("E. control: con la estandarización dentro del paciente de M2, también",
                  dif_m2 > 1e-3, f"max |ganador − LOF de M2| = {dif_m2:.3g}, en los mismos 60 pacientes"))
    try:
        from sklearn.preprocessing import StandardScaler
        StandardScaler().fit(base[L["top_lof_features"]])
        rechaza = False
    except Exception as e:  # noqa: BLE001
        rechaza, motivo = True, type(e).__name__
    casos.append(("E. el scikit-learn actual rechaza el DataFrame con columnas repetidas", rechaza,
                  f"StandardScaler().fit(df[top_lof_features]): {motivo if rechaza else 'lo aceptó'}"))
    return casos, inventario


# ---- F: el número de árboles, sin las etiquetas de validación -----------------------------

def caso_f():
    from catboost import CatBoostClassifier, Pool
    from sklearn.model_selection import StratifiedGroupKFold
    # Prevalencia de alrededor del 0,1 %, como en los datos: el sobremuestreo publicado
    # (hasta 0,003) falla si los positivos ya pasan de esa razón.
    rng = np.random.default_rng(0)
    grupos = np.repeat([f"P{i}" for i in range(600)], 100)
    n = len(grupos)
    y = (rng.random(n) < 0.0012).astype(int)
    x = pd.DataFrame(rng.normal(size=(n, 8)) + y[:, None] * 0.6, columns=[f"v{i}" for i in range(8)])
    x["onehot_0"] = pd.Series(rng.integers(0, 2, n).astype(np.int32)).astype("category")
    tr, va = next(StratifiedGroupKFold(5, shuffle=True, random_state=0).split(x, y, groups=grupos))
    y_barajada = y.copy()
    y_barajada[va] = rng.permutation(y[va])

    def publicado(yy):  # la celda 22: el pliegue de validación como eval_set
        params = {**g.PARAMETROS_CATBOOST, **g.PARCHE_CPU, "random_state": 0, "verbose": False, "allow_writing_files": False}
        x_fit, y_fit = g.remuestrear(x.iloc[tr], yy[tr], 0)
        m = CatBoostClassifier(**params).fit(Pool(x_fit, y_fit, cat_features=["onehot_0"]),
                                             eval_set=Pool(x.iloc[va], yy[va], cat_features=["onehot_0"]))
        return m.predict_proba(x.iloc[va])[:, 1], m.tree_count_

    def propio(yy):
        m = g.ajustar_m3(x.iloc[tr], yy[tr], grupos[tr], ["onehot_0"], 0)
        return m.predict_proba(x.iloc[va])[:, 1], m.tree_count_

    p1, a1 = propio(y)
    p2, a2 = propio(y_barajada)
    q1, b1 = publicado(y)
    q2, b2 = publicado(y_barajada)
    propio_ok = bool(np.array_equal(p1, p2))
    publicado_cambia = not np.array_equal(q1, q2)
    return [("F. ajustar_m3: barajar las etiquetas de validación no cambia nada", propio_ok,
             f"árboles {a1} y {a2}; predicciones idénticas: {propio_ok}"),
            ("F. control: con el ajuste publicado sí cambian", publicado_cambia,
             f"árboles {b1} con las etiquetas y {b2} barajadas; predicciones distintas: {publicado_cambia}")]


def main():
    casos = [("A. las listas del notebook", *caso_a()),
             ("B. los parámetros transcritos, en su celda", *caso_b()),
             ("C. sin etiqueta", *caso_c())]
    casos += caso_f()
    inventario = None
    if PYTHON_2024 and os.path.exists(CSV):
        de, inventario = casos_d_y_e()
        casos += de
    else:
        falta = "PYTHON_GUION_ISIC, un intérprete de 2024" if not PYTHON_2024 else CSV
        casos.append(("D y E. frente al código del ganador", None, f"NO CORRIDO: falta {falta}"))

    fallos = corridos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'NO CORRIDO' if ok is None else ('OK' if ok else 'FALLA')}] {titulo}\n      {detalle}")
        if ok is not None:
            corridos += 1
            fallos += not ok
    if inventario:
        print("\nVariables de M3:", inventario["n_variables"], "· categóricas:", inventario["n_categoricas"],
              "· por familia:", {k: len(v) for k, v in inventario["entran"].items()})
    print(f"\n{corridos - fallos} de {corridos} casos corridos como se esperaba; {len(casos) - corridos} no corridos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

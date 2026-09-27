#!/usr/bin/env python3
"""
ganador_m3.py — M3 (PLAN.md, Fase 4): la parte tabular de la solución ganadora
de ISIC 2024, reproducida en el entorno actual desde su notebook versionado,
referencias/novoselskiy-2024-isic2024/notebooks/top-model.ipynb.

Las listas de variables no se transcriben: se leen del notebook con `ast`, y
antes se comprueba que su SHA-256 es el que registra
referencias/novoselskiy-2024-isic2024.md.

Qué se reproduce, celda a celda:
- **Celda 7, `read_data`.** La edad faltante (el texto 'NA' del CSV, que la
  celda convierte en NaN) se rellena con la mediana de la columna sobre todas las
  filas.
  Después vienen las 42 variables derivadas de `new_num_cols`, con sus fórmulas,
  el z-score dentro del paciente de las 76 numéricas y derivadas, con la
  desviación muestral de polars más `err`, y los tres conteos y sumas de
  `special_cols`. Las agregaciones de polars propagan los NaN, y aquí también.
  La zona anatómica faltante es su propio grupo.
- **Celda 8, `preprocess`.** One-hot de las categóricas ajustado sobre todas las
  filas, con los faltantes como categoría propia (polars los lee como texto
  vacío).
- **Celdas 10, 11 y 13, el LOF.** Un `StandardScaler` ajustado sobre todas las
  filas y las 17 columnas de `top_lof_features`. `hue_contrast` y
  `position_distance_3d` están dos veces, así que pesan doble en la distancia.
  Después, `LocalOutlierFactor(n_neighbors=min(n, 30))` paciente por paciente,
  y −1 si el paciente tiene menos de 3 lesiones. El scikit-learn actual rechaza
  un DataFrame con columnas repetidas; con la matriz de numpy salen las mismas
  17 columnas.
- **Celda 18, el k-means.** 29 conglomerados con `random_state=42` sobre la misma
  matriz estandarizada. `n_init=10` va explícito porque era el valor por defecto
  en la corrida publicada: la salida de la celda avisa de que cambiaría a 'auto'.
- **Celda 19.** Cada variable de `columns_for_cluster_culculations` menos la media
  de su conglomerado, dividida por la desviación del conglomerado, con pandas,
  como en el notebook.
- **Celda 24.** Se quitan las columnas de `columns_to_drop`.

Qué no se reproduce, con su motivo (parches declarados en PLAN.md, Fase 4):
- **Las celdas 14 a 17**, que añaden las 12 variables de los modelos de imagen, y
  las 8 variables de la celda 19 calculadas sobre ellas. El conglomerado en sí no
  depende de la imagen: se ajusta sobre `top_lof_features`.
- **Las columnas que excluye `auditoria-de-fugas`.** De las publicadas solo cae
  `attribution`, una columna de procedencia. `copyright_license` no aparece en el
  notebook.

**Sin etiquetas, pero no local.** Ninguna función de variables lee la etiqueta.
A diferencia de las de M2, estas variables sí dependen de otros pacientes: la
mediana, el one-hot, el estandarizado, el k-means y sus medias se ajustan sobre
todas las filas del conjunto de desarrollo, como el notebook lo hace sobre todo el
CSV de entrenamiento (decisión de la persona del 2026-09-26). Nunca entra el
conjunto reservado.

El ajuste, `ajustar_m3`, sigue la especificación de PLAN.md, Fase 4: los
parámetros publicados, el remuestreo publicado, CPU en lugar de GPU y el número
de árboles elegido dentro del pliegue de entrenamiento.

Dependencias en `.venv`, instaladas desde PyPI el 2026-09-26: catboost 1.2.8 (la
1.2.5 que fija el ganador no importa con numpy 2) e imbalanced-learn 0.14.2.
El control es test_ganador_m3.py.
"""

import ast
import hashlib
import json
import os
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import OneHotEncoder, StandardScaler

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
NOTEBOOK = os.path.join(RAIZ, "referencias", "novoselskiy-2024-isic2024", "notebooks", "top-model.ipynb")
SHA256_NOTEBOOK = "0c39e7526dc7017b334a01d71a02a4a6f7e63d50f221011b8eee3f89e663362f"

ERR = 1e-5  # celda 3: err = 1e-5
VECINOS_MAX, MIN_LESIONES_LOF = 30, 3  # celda 10
N_CONGLOMERADOS, SEMILLA_KMEANS, N_INIT_KMEANS = 29, 42, 10  # celda 18; n_init, de su salida
CELDAS_DE_IMAGEN = (14, 15, 16, 17)

# Lo que llega al CatBoostClassifier en la corrida publicada: la celda 25 llama a
# optimise_catboost (celda 22) con la configuración de la celda 24. random_strength
# figura en la celda 24 pero no llega: ModelConfigCB (celda 21) no tiene ese campo y
# pydantic lo descarta, y la celda 22 tampoco lo pasa.
PARAMETROS_CATBOOST = {
    "loss_function": "Logloss",
    "eval_metric": "AUC",
    "learning_rate": 0.02606161517843435,
    "od_wait": 100,
    "depth": 6,
    "l2_leaf_reg": 18.04422276698195,
    "min_data_in_leaf": 38,
    "bagging_temperature": 0.8735940473548339,
    "border_count": 256,
    "grow_policy": "Lossguide",
    "iterations": 2000,
}
SOBREMUESTREO = 0.003  # celda 22: RandomOverSampler(sampling_strategy= 0.003 , ...)
SUBMUESTREO = 0.01  # celda 3: sampling_ratio = 0.01, el RandomUnderSampler de la celda 22
# Parche de dispositivo. La celda 22 entrena en GPU (task_type='GPU', devices='0').
# En CPU, CatBoost usa por defecto el bootstrap MVS e ignora bagging_temperature; el
# bayesiano es el de GPU. En GPU evaluó el AUC cada 5 iteraciones (salida de la celda
# 25); en CPU, con el detector de sobreajuste activo, lo evalúa en cada una e ignora
# metric_period (aviso de CatBoost 1.2.8), así que eso no se reproduce.
PARCHE_CPU = {"task_type": "CPU", "bootstrap_type": "Bayesian"}
PLIEGUES_INTERNOS = 5


def celdas_publicadas(ruta=NOTEBOOK):
    """Fuente de cada celda del notebook, por su índice. Falla si el archivo no
    es la versión registrada."""
    with open(ruta, "rb") as f:
        contenido = f.read()
    sha = hashlib.sha256(contenido).hexdigest()
    if sha != SHA256_NOTEBOOK:
        raise SystemExit(f"ERROR: {ruta} no es la versión registrada (SHA-256 {sha}, se esperaba {SHA256_NOTEBOOK}).")
    return ["".join(c["source"]) for c in json.loads(contenido)["cells"]]


def _literal_asignado(fuente, nombre):
    for nodo in ast.parse(fuente).body:
        if isinstance(nodo, ast.Assign) and any(isinstance(t, ast.Name) and t.id == nombre for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise KeyError(nombre)


def _anadidas_a_feature_cols(fuente):
    """Las listas literales que una celda suma a feature_cols (`feature_cols += [...]`)."""
    salida = []
    for nodo in ast.walk(ast.parse(fuente)):
        if (isinstance(nodo, ast.AugAssign) and isinstance(nodo.target, ast.Name)
                and nodo.target.id == "feature_cols" and isinstance(nodo.value, ast.List)):
            salida += ast.literal_eval(nodo.value)
    return salida


def listas_publicadas(ruta=NOTEBOOK):
    c = celdas_publicadas(ruta)
    listas = {k: _literal_asignado(c[3], k) for k in ("num_cols", "new_num_cols", "cat_cols", "special_cols")}
    listas["top_lof_features"] = _literal_asignado(c[11], "top_lof_features")
    listas["columns_for_cluster_culculations"] = _literal_asignado(c[19], "columns_for_cluster_culculations")
    listas["columns_to_drop"] = _literal_asignado(c[24], "columns_to_drop")
    listas["de_imagen"] = [v for i in CELDAS_DE_IMAGEN for v in _anadidas_a_feature_cols(c[i])]
    return listas


def mediana_como_polars(v):
    """Mediana de una columna con NaN, como `pl.col(...).median()` en la celda 7:
    polars ordena los NaN como los valores más altos y no los descarta."""
    v = np.asarray(v, dtype=float)
    return float(np.median(np.where(np.isnan(v), np.inf, v)))


def derivadas(df):
    """Las 42 variables de new_num_cols, con las fórmulas de la celda 7, en su orden."""
    c = df
    d = {}
    d["lesion_size_ratio"] = c["tbp_lv_minorAxisMM"] / c["clin_size_long_diam_mm"]
    d["lesion_shape_index"] = c["tbp_lv_areaMM2"] / (c["tbp_lv_perimeterMM"] ** 2)
    d["hue_contrast"] = (c["tbp_lv_H"] - c["tbp_lv_Hext"]).abs()
    d["luminance_contrast"] = (c["tbp_lv_L"] - c["tbp_lv_Lext"]).abs()
    d["lesion_color_difference"] = np.sqrt(c["tbp_lv_deltaA"] ** 2 + c["tbp_lv_deltaB"] ** 2 + c["tbp_lv_deltaL"] ** 2)
    d["border_complexity"] = c["tbp_lv_norm_border"] + c["tbp_lv_symm_2axis"]
    d["color_uniformity"] = c["tbp_lv_color_std_mean"] / (c["tbp_lv_radial_color_std_max"] + ERR)

    d["position_distance_3d"] = np.sqrt(c["tbp_lv_x"] ** 2 + c["tbp_lv_y"] ** 2 + c["tbp_lv_z"] ** 2)
    d["perimeter_to_area_ratio"] = c["tbp_lv_perimeterMM"] / c["tbp_lv_areaMM2"]
    d["area_to_perimeter_ratio"] = c["tbp_lv_areaMM2"] / c["tbp_lv_perimeterMM"]
    d["lesion_visibility_score"] = c["tbp_lv_deltaLBnorm"] + c["tbp_lv_norm_color"]
    d["symmetry_border_consistency"] = c["tbp_lv_symm_2axis"] * c["tbp_lv_norm_border"]
    d["consistency_symmetry_border"] = (c["tbp_lv_symm_2axis"] * c["tbp_lv_norm_border"]
                                        / (c["tbp_lv_symm_2axis"] + c["tbp_lv_norm_border"]))

    d["color_consistency"] = c["tbp_lv_stdL"] / c["tbp_lv_Lext"]
    d["consistency_color"] = c["tbp_lv_stdL"] * c["tbp_lv_Lext"] / (c["tbp_lv_stdL"] + c["tbp_lv_Lext"])
    d["size_age_interaction"] = c["clin_size_long_diam_mm"] * c["age_approx"]
    d["hue_color_std_interaction"] = c["tbp_lv_H"] * c["tbp_lv_color_std_mean"]
    d["lesion_severity_index"] = (c["tbp_lv_norm_border"] + c["tbp_lv_norm_color"] + c["tbp_lv_eccentricity"]) / 3
    d["shape_complexity_index"] = d["border_complexity"] + d["lesion_shape_index"]
    d["color_contrast_index"] = c["tbp_lv_deltaA"] + c["tbp_lv_deltaB"] + c["tbp_lv_deltaL"] + c["tbp_lv_deltaLBnorm"]

    d["log_lesion_area"] = np.log(c["tbp_lv_areaMM2"] + 1)
    d["normalized_lesion_size"] = c["clin_size_long_diam_mm"] / c["age_approx"]
    d["mean_hue_difference"] = (c["tbp_lv_H"] + c["tbp_lv_Hext"]) / 2
    d["std_dev_contrast"] = np.sqrt((c["tbp_lv_deltaA"] ** 2 + c["tbp_lv_deltaB"] ** 2 + c["tbp_lv_deltaL"] ** 2) / 3)
    d["color_shape_composite_index"] = (c["tbp_lv_color_std_mean"] + c["tbp_lv_area_perim_ratio"] + c["tbp_lv_symm_2axis"]) / 3
    d["lesion_orientation_3d"] = np.arctan2(c["tbp_lv_y"], c["tbp_lv_x"])
    d["overall_color_difference"] = (c["tbp_lv_deltaA"] + c["tbp_lv_deltaB"] + c["tbp_lv_deltaL"]) / 3

    d["symmetry_perimeter_interaction"] = c["tbp_lv_symm_2axis"] * c["tbp_lv_perimeterMM"]
    d["comprehensive_lesion_index"] = (c["tbp_lv_area_perim_ratio"] + c["tbp_lv_eccentricity"] + c["tbp_lv_norm_color"]
                                       + c["tbp_lv_symm_2axis"]) / 4
    d["color_variance_ratio"] = c["tbp_lv_color_std_mean"] / c["tbp_lv_stdLExt"]
    d["border_color_interaction"] = c["tbp_lv_norm_border"] * c["tbp_lv_norm_color"]
    d["border_color_interaction_2"] = (c["tbp_lv_norm_border"] * c["tbp_lv_norm_color"]
                                       / (c["tbp_lv_norm_border"] + c["tbp_lv_norm_color"]))
    d["size_color_contrast_ratio"] = c["clin_size_long_diam_mm"] / c["tbp_lv_deltaLBnorm"]
    d["age_normalized_nevi_confidence"] = c["tbp_lv_nevi_confidence"] / c["age_approx"]
    d["age_normalized_nevi_confidence_2"] = np.sqrt(c["clin_size_long_diam_mm"] ** 2 + c["age_approx"] ** 2)
    d["color_asymmetry_index"] = c["tbp_lv_radial_color_std_max"] * c["tbp_lv_symm_2axis"]

    d["volume_approximation_3d"] = c["tbp_lv_areaMM2"] * np.sqrt(c["tbp_lv_x"] ** 2 + c["tbp_lv_y"] ** 2 + c["tbp_lv_z"] ** 2)
    d["color_range"] = ((c["tbp_lv_L"] - c["tbp_lv_Lext"]).abs() + (c["tbp_lv_A"] - c["tbp_lv_Aext"]).abs()
                        + (c["tbp_lv_B"] - c["tbp_lv_Bext"]).abs())
    d["shape_color_consistency"] = c["tbp_lv_eccentricity"] * c["tbp_lv_color_std_mean"]
    d["border_length_ratio"] = c["tbp_lv_perimeterMM"] / (2 * np.pi * np.sqrt(c["tbp_lv_areaMM2"] / np.pi))
    d["age_size_symmetry_index"] = c["age_approx"] * c["clin_size_long_diam_mm"] * c["tbp_lv_symm_2axis"]
    d["index_age_size_symmetry"] = c["age_approx"] * c["tbp_lv_areaMM2"] * c["tbp_lv_symm_2axis"]
    return pd.DataFrame(d, index=df.index)


def _media_y_desviacion_como_polars(x, grupos):
    """Media y desviación muestral dentro de cada grupo; un NaN en el grupo lo
    vuelve NaN, como en las agregaciones `.over()` de polars."""
    g = x.groupby(grupos, sort=False)
    media, sd = g.transform("mean"), g.transform("std")
    con_nan = x.isna().groupby(grupos, sort=False).transform("any").to_numpy()
    media[con_nan] = np.nan
    sd[con_nan] = np.nan
    return media, sd


def variables_lectura(df, listas, group_col="patient_id"):
    """La celda 7 (read_data) sobre un DataFrame de pandas: las 34 numéricas con la
    edad imputada, las 42 derivadas, sus 76 z-scores dentro del paciente y los tres
    conteos y sumas por paciente. No lee la etiqueta."""
    base = df[listas["num_cols"]].astype(float).copy()
    for col in listas["num_cols"]:  # fill_nan(median) de la celda 7: en estos datos, solo la edad tiene NaN
        if base[col].isna().any():
            base[col] = base[col].fillna(mediana_como_polars(base[col]))
    base = pd.concat([base, derivadas(base)], axis=1)
    grupos = df[group_col]
    normas = {}
    for col in listas["num_cols"] + listas["new_num_cols"]:
        media, sd = _media_y_desviacion_como_polars(base[col], grupos)
        normas[f"{col}_patient_norm"] = (base[col] - media) / (sd + ERR)
    base = pd.concat([base, pd.DataFrame(normas, index=df.index)], axis=1)
    g = base.groupby(grupos, sort=False)
    base["count_per_patient"] = grupos.groupby(grupos, sort=False).transform("size").astype(float)
    base["tbp_lv_areaMM2_patient"] = g["tbp_lv_areaMM2"].transform("sum")
    zona = df["anatom_site_general"].fillna("")
    base["tbp_lv_areaMM2_bp"] = base["tbp_lv_areaMM2"].groupby([grupos, zona], sort=False).transform("sum")
    return base


def one_hot(df, categoricas):
    """La celda 8: OneHotEncoder ajustado sobre todas las filas; los faltantes, como
    texto vacío (así los lee polars). Columnas onehot_0, onehot_1…, de tipo category."""
    x = df[categoricas].astype(object).where(df[categoricas].notna(), "").astype(str)
    enc = OneHotEncoder(sparse_output=False, dtype=np.int32, handle_unknown="ignore").fit(x)
    nombres = [f"onehot_{i}" for i in range(len(enc.get_feature_names_out()))]
    salida = pd.DataFrame(enc.transform(x), index=df.index, columns=nombres).astype("category")
    return salida, dict(zip(nombres, enc.get_feature_names_out()))


def matriz_lof(base, top_lof_features):
    """La matriz de las celdas 10 y 18: StandardScaler sobre todas las filas y las 17
    columnas de top_lof_features, repeticiones incluidas."""
    return StandardScaler().fit_transform(base[top_lof_features].to_numpy(dtype=float))


def lof_publicado(escalada, grupos):
    """La celda 10: LOF paciente por paciente sobre la matriz estandarizada global."""
    grupos = np.asarray(grupos)
    of = np.full(len(grupos), np.nan)
    for p in pd.unique(grupos):
        mascara = grupos == p
        n = int(mascara.sum())
        if n < MIN_LESIONES_LOF:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # n_neighbors >= n: sklearn lo baja a n − 1 y avisa
            clf = LocalOutlierFactor(n_neighbors=min(n, VECINOS_MAX))
            clf.fit_predict(escalada[mascara])
        of[mascara] = clf.negative_outlier_factor_
    return np.where(np.isnan(of), -1.0, of)


def conglomerados(escalada):
    """La celda 18."""
    return KMeans(n_clusters=N_CONGLOMERADOS, random_state=SEMILLA_KMEANS, n_init=N_INIT_KMEANS).fit_predict(escalada)


def variables_conglomerado(base, etiquetas, columnas):
    """La celda 19: (x − media del conglomerado) / desviación del conglomerado, con pandas."""
    g = base[columnas].groupby(etiquetas, sort=False)
    media, sd = g.transform("mean"), g.transform("std")
    salida = (base[columnas] - media) / sd
    salida.columns = [f"{c}__cluster" for c in columnas]
    return salida


def variables_m3(df, columnas_excluidas, group_col="patient_id", ruta=NOTEBOOK):
    """Todas las variables de M3 sobre df (el conjunto de desarrollo, sin la
    etiqueta). Devuelve (DataFrame de variables en el orden de feature_cols
    publicado, nombres de las categóricas, inventario de qué entra y qué sale)."""
    if "target" in df.columns:
        raise ValueError("variables_m3 no recibe la etiqueta.")
    listas = listas_publicadas(ruta)
    excluidas = set(columnas_excluidas)
    categoricas = [c for c in listas["cat_cols"] if c not in excluidas]
    brutas_excluidas = [c for c in listas["num_cols"] + listas["cat_cols"] if c in excluidas]

    segundos = {}
    t0 = time.perf_counter()
    base = variables_lectura(df, listas, group_col)
    codificadas, nombres_onehot = one_hot(df, categoricas)
    segundos["lectura_y_one_hot"] = round(time.perf_counter() - t0, 1)
    t0 = time.perf_counter()
    escalada = matriz_lof(base, listas["top_lof_features"])
    base["of"] = lof_publicado(escalada, df[group_col])
    segundos["lof"] = round(time.perf_counter() - t0, 1)
    t0 = time.perf_counter()
    etiquetas = conglomerados(escalada)
    de_imagen = set(listas["de_imagen"])
    para_conglomerado = [c for c in listas["columns_for_cluster_culculations"] if c not in de_imagen]
    cluster = variables_conglomerado(base, etiquetas, para_conglomerado)
    segundos["kmeans_y_conglomerado"] = round(time.perf_counter() - t0, 1)

    # Orden de feature_cols publicado: celda 3, sin las categóricas (la celda 8 las
    # cambia por el one-hot, al final), 'of' (celda 13), las de conglomerado (celda 19).
    norm_cols = [f"{c}_patient_norm" for c in listas["num_cols"] + listas["new_num_cols"]]
    orden = (listas["num_cols"] + listas["new_num_cols"] + norm_cols + listas["special_cols"]
             + list(codificadas.columns) + ["of"] + list(cluster.columns))
    quitadas = [c for c in orden if c in set(listas["columns_to_drop"])]
    finales = [c for c in orden if c not in set(listas["columns_to_drop"])]
    todo = pd.concat([base, codificadas, cluster], axis=1)
    inventario = {
        "entran": {
            "numericas_brutas": [c for c in listas["num_cols"] if c in finales],
            "derivadas": [c for c in listas["new_num_cols"] if c in finales],
            "z_score_dentro_del_paciente": [c for c in norm_cols if c in finales],
            "conteos_y_sumas_por_paciente": [c for c in listas["special_cols"] if c in finales],
            "one_hot": {c: nombres_onehot[c] for c in codificadas.columns if c in finales},
            "lof": ["of"],
            "conglomerado": [c for c in cluster.columns if c in finales],
        },
        "salen": {
            "de_imagen_celdas_14_a_17": listas["de_imagen"],
            "conglomerado_sobre_imagen_celda_19": [f"{c}__cluster" for c in listas["columns_for_cluster_culculations"]
                                                   if c in de_imagen],
            "excluidas_por_auditoria_de_fugas": brutas_excluidas,
            "columns_to_drop_celda_24": quitadas,
        },
        "n_variables": len(finales),
        "n_categoricas": len([c for c in finales if c in set(codificadas.columns)]),
        "segundos": segundos,
    }
    return todo[finales], [c for c in finales if c in set(codificadas.columns)], inventario


def remuestrear(x, y, semilla):
    """La celda 22: sobremuestreo de positivos hasta 0,003 y submuestreo de negativos
    hasta 0,01, con la semilla del pliegue."""
    from imblearn.over_sampling import RandomOverSampler
    from imblearn.pipeline import Pipeline
    from imblearn.under_sampling import RandomUnderSampler
    return Pipeline([
        ("sampler_1", RandomOverSampler(sampling_strategy=SOBREMUESTREO, random_state=semilla)),
        ("sampler_2", RandomUnderSampler(sampling_strategy=SUBMUESTREO, random_state=semilla)),
    ]).fit_resample(x, y)


def ajustar_m3(x_tr, y_tr, grupos_tr, categoricas, semilla):
    """CatBoost de M3 sobre el pliegue de entrenamiento. El publicado elige el número
    de árboles con el pliegue de validación (eval_set, use_best_model y od_wait);
    aquí nunca lo ve (parche 4, decisión de la persona del 2026-09-26). La parada
    temprana del publicado se hace sobre un 20 % del pliegue de entrenamiento: el
    primer pliegue de un StratifiedGroupKFold de 5, agrupado por paciente,
    estratificado y con la semilla externa. El remuestreo va solo en el resto, como
    el publicado remuestrea el entrenamiento y no la evaluación."""
    from catboost import CatBoostClassifier, Pool
    parametros = {**PARAMETROS_CATBOOST, **PARCHE_CPU, "random_state": semilla,
                  "verbose": False, "allow_writing_files": False}
    interna = StratifiedGroupKFold(n_splits=PLIEGUES_INTERNOS, shuffle=True, random_state=semilla)
    itr, iva = next(interna.split(x_tr, y_tr, groups=grupos_tr))
    x_fit, y_fit = remuestrear(x_tr.iloc[itr], y_tr[itr], semilla)
    evaluacion = Pool(x_tr.iloc[iva], y_tr[iva], cat_features=categoricas)
    modelo = CatBoostClassifier(**parametros)
    modelo.fit(Pool(x_fit, y_fit, cat_features=categoricas), eval_set=evaluacion)
    return modelo

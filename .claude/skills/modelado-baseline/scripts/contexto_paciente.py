#!/usr/bin/env python3
"""
contexto_paciente.py — las variables de contexto de paciente del modelo M2
(PLAN.md, Fase 4): cada lesión comparada con las demás de su mismo paciente.

Sigue la solución ganadora (referencias/novoselskiy-2024-isic2024/notebooks/top-model.ipynb):

- **z-score dentro del paciente** de cada variable numérica de M1:
  (x − media del paciente) / (desviación del paciente + 1e-5). Celda 7:
  `((pl.col(col) - pl.col(col).mean().over('patient_id')) / (pl.col(col).std().over('patient_id') + err))`,
  con `err = 1e-5` (celda 3). La desviación es la muestral (ddof = 1), como la de
  polars; en un paciente de una sola lesión sale NaN.
- **Conteos y sumas de área por paciente**, celda 7: `count_per_patient` (lesiones
  del paciente), `tbp_lv_areaMM2_patient` (área total del paciente) y
  `tbp_lv_areaMM2_bp` (área del paciente en la misma zona anatómica,
  `anatom_site_general`; los faltantes de la zona cuentan como un grupo, como en
  polars).
- **LOF por paciente**, celdas 10 y 11: `LocalOutlierFactor(n_neighbors=min(n, 30))`
  sobre las 17 variables de `top_lof_features`, repeticiones incluidas
  (`hue_contrast` y `position_distance_3d` aparecen dos veces, y así pesan doble
  en la distancia). El valor es `negative_outlier_factor_`. Los pacientes con
  menos de 3 lesiones reciben −1. Las variables derivadas se calculan con las
  fórmulas de la celda 7.

**Una desviación, declarada.** El ganador estandariza las variables del LOF con un
`StandardScaler` ajustado sobre todas las filas (celda 10) e imputa los faltantes
con la mediana global (celda 7). Aquí se estandariza y se imputa **dentro de cada
paciente**: faltante con la mediana del paciente; si el paciente no tiene ningún
valor, o la variable no varía en él, la columna vale 0 tras estandarizar. Así
ninguna variable de un paciente depende de otro.

**Sin etiquetas y sin fuga entre pliegues.** Ninguna función lee la etiqueta.
Todas se calculan con las lesiones de un solo paciente, y los pliegues agrupan por
paciente, así que las variables de una lesión de validación no dependen de
ninguna lesión de entrenamiento. Por eso se calculan una vez, sobre el conjunto de
desarrollo, y valen para todos los pliegues y semillas. El control positivo,
test_contexto_paciente.py, comprueba las dos cosas: barajar las etiquetas no
cambia ninguna variable, y cambiar un paciente no cambia las de otro.
"""

import warnings

import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

ERR = 1e-5  # celda 3: err = 1e-5
VECINOS_MAX = 30  # celda 10: n_neighbors=min(sum(mask), 30)
MIN_LESIONES_LOF = 3  # celda 10: if sum(mask) < 3: continue; fillna(-1)
# Celda 11, tal cual, con sus repeticiones.
TOP_LOF_FEATURES = [
    'tbp_lv_H', 'hue_contrast',
    'age_normalized_nevi_confidence_2', 'tbp_lv_deltaB',
    'color_uniformity', 'tbp_lv_z',
    'clin_size_long_diam_mm', 'tbp_lv_y',
    'position_distance_3d', 'hue_contrast',
    'tbp_lv_stdLExt', 'mean_hue_difference',
    'age_normalized_nevi_confidence',
    'lesion_visibility_score',
    'position_distance_3d',
    'tbp_lv_minorAxisMM', 'tbp_lv_Hext',
]


def derivadas_lof(df):
    """Las siete variables derivadas que usa el LOF, con las fórmulas de la celda 7."""
    return pd.DataFrame({
        "hue_contrast": (df["tbp_lv_H"] - df["tbp_lv_Hext"]).abs(),
        "age_normalized_nevi_confidence_2": np.sqrt(df["clin_size_long_diam_mm"] ** 2 + df["age_approx"] ** 2),
        "color_uniformity": df["tbp_lv_color_std_mean"] / (df["tbp_lv_radial_color_std_max"] + ERR),
        "position_distance_3d": np.sqrt(df["tbp_lv_x"] ** 2 + df["tbp_lv_y"] ** 2 + df["tbp_lv_z"] ** 2),
        "mean_hue_difference": (df["tbp_lv_H"] + df["tbp_lv_Hext"]) / 2,
        "age_normalized_nevi_confidence": df["tbp_lv_nevi_confidence"] / df["age_approx"],
        "lesion_visibility_score": df["tbp_lv_deltaLBnorm"] + df["tbp_lv_norm_color"],
    }, index=df.index)


def _estandarizar_en_paciente(x):
    """Imputación y estandarización dentro de un paciente, columna a columna."""
    x = x.astype(float).copy()
    for j in range(x.shape[1]):
        col = x[:, j]
        if np.isnan(col).all():
            x[:, j] = 0.0
            continue
        col = np.where(np.isnan(col), np.nanmedian(col), col)
        sd = col.std()
        x[:, j] = (col - col.mean()) / sd if sd > 0 else 0.0
    return x


def lof_por_paciente(df, group_col="patient_id"):
    base = pd.concat([df, derivadas_lof(df)], axis=1)
    base = base.loc[:, ~base.columns.duplicated()]
    x_todo = base[TOP_LOF_FEATURES].to_numpy()
    of = np.full(len(df), -1.0)
    for _, pos in df.groupby(group_col, sort=False).indices.items():
        if len(pos) < MIN_LESIONES_LOF:
            continue
        x = _estandarizar_en_paciente(x_todo[pos])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # sklearn avisa cuando n_neighbors >= n y lo baja a n - 1
            clf = LocalOutlierFactor(n_neighbors=min(len(pos), VECINOS_MAX))
            clf.fit_predict(x)
        of[pos] = clf.negative_outlier_factor_
    return pd.Series(of, index=df.index, name="of")


def variables_contexto_paciente(df, numericas, group_col="patient_id", sitio_col="anatom_site_general"):
    """Devuelve un DataFrame, con el índice de df, con las variables de contexto:
    {col}_patient_norm por cada numérica, count_per_patient,
    tbp_lv_areaMM2_patient, tbp_lv_areaMM2_bp y of. No lee la etiqueta."""
    g = df.groupby(group_col, sort=False)
    salida = {}
    for col in numericas:
        media = g[col].transform("mean")
        sd = g[col].transform("std")  # muestral, ddof = 1, como polars
        salida[f"{col}_patient_norm"] = (df[col] - media) / (sd + ERR)
    salida["count_per_patient"] = g[group_col].transform("size").astype(float)
    salida["tbp_lv_areaMM2_patient"] = g["tbp_lv_areaMM2"].transform("sum")
    salida["tbp_lv_areaMM2_bp"] = df.groupby([group_col, sitio_col], sort=False, dropna=False)["tbp_lv_areaMM2"].transform("sum")
    out = pd.DataFrame(salida, index=df.index)
    out["of"] = lof_por_paciente(df, group_col)
    return out

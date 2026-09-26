#!/usr/bin/env python3
"""
metricas_triaje.py — las dos métricas de triaje del cliente: SEtop-15 y
NNT80% SE. Complementan al pAUC (train_and_evaluate.py > pauc_above_tpr).

SEtop-15 — verificada contra el guion del organizador.
    Media, sobre los pacientes con al menos una lesión maligna, de la fracción
    de sus malignas que caen entre sus 15 lesiones de mayor puntuación. Es
    `raw_average_rank` de SecondaryMetric-TopNSensitivity.py (líneas 85, 90,
    114 y 129; ficha en referencias/isic-secondary-metric-topn.py.md), y es la
    que Kurtansky et al. 2025 describen como la que "weighed each diseased
    patient equally". En los empates del borde se queda con las que aparecen
    antes, como `nlargest(keep="first")` del guion. La verificación ejecuta el
    guion sin modificarlo: test_metricas_triaje.py.

NNT80% SE — según la definición de Kurtansky et al. 2025.
    "NNTx% SE defined the average number of lesions needed to triage to undergo
    expert evaluation to detect a single malignancy, using a threshold
    corresponding to a given sensitivity" (métodos;
    referencias/kurtansky-2025-triaje-automatizado-tbp.md). No hay guion del
    organizador para esta métrica. La lectura operativa es nuestra: el umbral es
    el más alto con el que la sensibilidad llega al 80 %, y el NNT es el número
    de lesiones con puntuación igual o mayor que el umbral entre las malignas
    que capturan, es decir, 1 / VPP en ese umbral. Con empates en el umbral
    entran todas las lesiones empatadas.
"""

import numpy as np
import pandas as pd

TOP_N = 15
SENSIBILIDAD_NNT = 0.80


def setop_n(y_true, y_score, grupos, n=TOP_N):
    """SEtop-n: media por paciente enfermo de la fracción de sus malignas que
    caen entre sus n lesiones de mayor puntuación."""
    df = pd.DataFrame({"y": np.asarray(y_true), "s": np.asarray(y_score, dtype=float),
                       "g": np.asarray(grupos)})
    malignas = df.groupby("g", sort=False)["y"].transform("sum")
    df = df[malignas > 0]
    if df.empty:
        raise ValueError("Ningún paciente tiene lesiones malignas; SEtop-n no está definida.")
    # Orden estable por puntuación descendente: entre empates conserva el orden
    # de aparición, que es lo que hace nlargest(keep="first").
    df = df.iloc[np.argsort(-df["s"].to_numpy(), kind="stable")]
    en_top = df.groupby("g", sort=False).cumcount() < n
    por_paciente = df[en_top].groupby("g")["y"].sum() / df.groupby("g")["y"].sum()
    por_paciente = por_paciente.reindex(df["g"].unique(), fill_value=0.0)
    return float(por_paciente.mean())


def nnt_a_sensibilidad(y_true, y_score, sensibilidad=SENSIBILIDAD_NNT):
    """NNTx% SE: lesiones con puntuación >= umbral entre malignas capturadas,
    con el umbral más alto que alcanza la sensibilidad pedida."""
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(y_score, dtype=float)
    n_pos = int(y.sum())
    if n_pos == 0:
        raise ValueError("No hay lesiones malignas; el NNT no está definido.")
    k = int(np.ceil(sensibilidad * n_pos - 1e-9))  # malignas que hay que capturar
    umbral = np.sort(s[y])[::-1][k - 1]
    marcadas = s >= umbral
    return float(marcadas.sum() / (marcadas & y).sum())

#!/usr/bin/env python3
"""
test_nivel0_en_entrenamiento.py — control positivo del nivel 0.

Comprueba que el nivel 0 elige la columna y la orientación con las
etiquetas del fold de entrenamiento y no con las de validación (clase
décima del registro de incidentes de CLAUDE.md). Por el corolario de la
regla 6, el caso se fuerza: datos sintéticos en los que entrenamiento y
validación eligen distinto, y primero se comprueba que de verdad eligen
distinto. Si no, el control no probaría nada.

Un fold, con índices explícitos:
  - columna "a": en entrenamiento, asociada al target en sentido positivo
    y con fuerza; en validación, asociada en sentido NEGATIVO;
  - columna "b": en entrenamiento, asociación débil; en validación, casi
    perfecta;
  - columna "cat": categórica y perfecta en los dos lados. No es candidata,
    porque el nivel 0 usa la variable cruda.

Con etiquetas de entrenamiento se elige "a" con orientación +1. Con
etiquetas de validación se elegiría "b", y "a" se orientaría con -1.

No toca data/ ni outputs/.

Uso:
    python .claude/skills/modelado-baseline/scripts/test_nivel0_en_entrenamiento.py
Devuelve 0 si todos los casos se comportan como se espera.
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import (  # noqa: E402
    elegir_columna_sola,
    evaluar_columna_sola,
    pauc_above_tpr,
    preparar_features,
)


def datos_sinteticos(seed=0, n_train=4000, n_val=2000, tasa=0.05):
    rng = np.random.default_rng(seed)
    y_tr = (rng.random(n_train) < tasa).astype(int)
    y_va = (rng.random(n_val) < tasa).astype(int)
    df = pd.DataFrame({
        "patient_id": [f"P{i}" for i in range(n_train + n_val)],
        "a": np.r_[1.8 * y_tr, -1.8 * y_va] + rng.normal(0, 1, n_train + n_val),
        "b": np.r_[0.5 * y_tr, 4.0 * y_va] + rng.normal(0, 1, n_train + n_val),
        "cat": np.where(np.r_[y_tr, y_va] == 1, "m", "n"),
        "target": np.r_[y_tr, y_va],
    })
    train_idx = np.arange(n_train)
    val_idx = np.arange(n_train, n_train + n_val)
    return df, train_idx, val_idx


def fuerza(y, s):
    a = roc_auc_score(y, s)
    return max(a, 1 - a)


def main():
    df, tr, va = datos_sinteticos()
    y = df["target"].values
    numericas, categoricas = preparar_features(df, ["patient_id"], "target", "patient_id")

    # Lo que se elegiría con etiquetas de validación: el procedimiento viejo.
    col_val = max(numericas, key=lambda c: fuerza(y[va], df[c].values[va]))
    a_va = df["a"].values[va]
    signo_val_a = 1 if pauc_above_tpr(y[va], a_va) >= pauc_above_tpr(y[va], -a_va) else -1

    col, signo = elegir_columna_sola(df, numericas, "target", tr)
    fold = evaluar_columna_sola(df, numericas, "target", [(tr, va)])[0]

    # Las elecciones no pueden cambiar si se barajan las etiquetas de validación.
    df_barajado = df.copy()
    df_barajado.loc[va, "target"] = np.random.default_rng(1).permutation(y[va])
    col_b, signo_b = elegir_columna_sola(df_barajado, numericas, "target", tr)

    reportado_viejo = max(pauc_above_tpr(y[va], a_va), pauc_above_tpr(y[va], -a_va))
    casos = [
        ("el caso discrimina: con validación se elegiría otra columna",
         col_val != col, f"validación elegiría {col_val!r}; entrenamiento elige {col!r}"),
        ("el caso discrimina: con validación, 'a' se orientaría al revés",
         signo_val_a == -1, f"orientación de 'a' con validación: {signo_val_a}"),
        ("la categórica perfecta no es candidata",
         "cat" in categoricas and "cat" not in numericas, f"numéricas {numericas}, categóricas {categoricas}"),
        ("se elige la columna de entrenamiento",
         col == "a" and fold["columna"] == "a", f"elegir_columna_sola: {col!r}; evaluar_columna_sola: {fold['columna']!r}"),
        ("se usa la orientación de entrenamiento",
         signo == 1 and fold["orientacion"] == 1, f"orientación elegida: {signo}; en el fold: {fold['orientacion']}"),
        ("el pAUC reportado es el de la orientación de entrenamiento",
         np.isclose(fold["pauc"], pauc_above_tpr(y[va], a_va)) and fold["pauc"] < reportado_viejo,
         f"reportado {fold['pauc']:.4f}; con max() sobre validación habría sido {reportado_viejo:.4f}"),
        ("barajar las etiquetas de validación no cambia la elección",
         (col_b, signo_b) == (col, signo), f"con etiquetas barajadas: {col_b!r}, {signo_b}"),
    ]

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

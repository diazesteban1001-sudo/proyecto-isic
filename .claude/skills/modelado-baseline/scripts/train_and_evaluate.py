#!/usr/bin/env python3
"""
train_and_evaluate.py — instrumento de medición para la skill modelado-baseline.

Entrena tres niveles de baseline sobre la partición agrupada auditada,
evaluados con pAUC sobre 80% TPR. No decide cuál nivel es "el mejor" —
mide y reporta. No optimiza hiperparámetros.

ADVERTENCIA: la implementación de pauc_above_tpr() NO ha sido
contrastada línea por línea contra el notebook oficial de Kaggle
(isic-pauc-abovetpr). Ver SKILL.md, sección "Sobre la métrica".

Uso:
    python train_and_evaluate.py --data data/train-metadata.csv \
                                  --group-col patient_id \
                                  --target-col target \
                                  --n-splits 5 \
                                  --seed 42 \
                                  --leakage-report outputs/auditoria-de-fugas.json \
                                  --out outputs/modelado-baseline
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import auc, roc_curve
from sklearn.preprocessing import StandardScaler

try:
    from sklearn.model_selection import StratifiedGroupKFold
    HAS_STRATIFIED_GROUP = True
except ImportError:
    HAS_STRATIFIED_GROUP = False
from sklearn.model_selection import GroupKFold


def pauc_above_tpr(y_true, y_score, min_tpr=0.80):
    """pAUC sobre min_tpr. Transcripción del algoritmo oficial del
    organizador (`p_auc_tpr`), copia versionada en
    `referencias/isic-primary-metric-pauc.py.md`. Verificado el 2026-08-11.

    El oficial NO usa el AUC parcial corregido de McClish: invierte las
    etiquetas, trunca la curva ROC en max_fpr = 1 - min_tpr interpolando
    el último punto, e integra el área cruda. Rango [0, 1 - min_tpr],
    es decir [0, 0.2] para min_tpr = 0.80.
    """
    if len(np.unique(y_true)) != 2:
        raise ValueError(
            "Solo hay una clase en y_true; el pAUC no está definido. "
            "Revisa la estratificación de los folds."
        )

    v_gt = np.abs(np.asarray(y_true) - 1)
    v_pred = -1.0 * np.asarray(y_score)
    max_fpr = abs(1 - min_tpr)

    fpr, tpr, _ = roc_curve(v_gt, v_pred)

    stop = np.searchsorted(fpr, max_fpr, "right")
    x_interp = [fpr[stop - 1], fpr[stop]]
    y_interp = [tpr[stop - 1], tpr[stop]]
    tpr = np.append(tpr[:stop], np.interp(max_fpr, x_interp, y_interp))
    fpr = np.append(fpr[:stop], max_fpr)
    return auc(fpr, tpr)


def construir_folds(df, group_col, target_col, n_splits, seed):
    if HAS_STRATIFIED_GROUP:
        n_grupos_positivos = df.loc[df[target_col] == 1, group_col].nunique()
        if n_grupos_positivos >= n_splits:
            splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
            return list(splitter.split(df, df[target_col], groups=df[group_col]))
    splitter = GroupKFold(n_splits=n_splits)
    return list(splitter.split(df, df[target_col], groups=df[group_col]))


def preparar_features(df, columnas_excluidas, target_col, group_col):
    excluir = set(columnas_excluidas) | {target_col, group_col}
    cols = [c for c in df.columns if c not in excluir]
    numericas = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    categoricas = [c for c in cols if c not in numericas]
    return numericas, categoricas


def codificar_fold(df, numericas, categoricas, target_col, train_idx, val_idx):
    """Codifica dentro de cada fold: numéricas se imputan con la mediana
    de train; categóricas se codifican por media de target, ajustada
    solo con train. Nunca se usa información de val para codificar."""
    X_train = pd.DataFrame(index=train_idx)
    X_val = pd.DataFrame(index=val_idx)

    for c in numericas:
        mediana = df[c].iloc[train_idx].median()
        X_train[c] = df[c].iloc[train_idx].fillna(mediana).values
        X_val[c] = df[c].iloc[val_idx].fillna(mediana).values

    for c in categoricas:
        medias = df.iloc[train_idx].groupby(c)[target_col].mean()
        media_global = df[target_col].iloc[train_idx].mean()
        X_train[c] = df[c].iloc[train_idx].map(medias).fillna(media_global).values
        X_val[c] = df[c].iloc[val_idx].map(medias).fillna(media_global).values

    return X_train.values, X_val.values


def evaluar_modelo(df, target_col, folds, numericas, categoricas, modelo_fn, escalar=False):
    y = df[target_col].values
    paucs = []
    for train_idx, val_idx in folds:
        X_train, X_val = codificar_fold(df, numericas, categoricas, target_col, train_idx, val_idx)
        y_train, y_val = y[train_idx], y[val_idx]

        if escalar:
            # Las features van de std 0.12 a std 408; sin escalar, la
            # logistica no converge en max_iter y su pAUC no es el del
            # modelo sino el del optimizador a medio camino.
            scaler = StandardScaler().fit(X_train)
            X_train, X_val = scaler.transform(X_train), scaler.transform(X_val)

        modelo = modelo_fn()
        modelo.fit(X_train, y_train)
        y_score = modelo.predict_proba(X_val)[:, 1]

        paucs.append(pauc_above_tpr(y_val, y_score))
    return paucs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not os.path.exists(args.leakage_report):
        print(
            f"ERROR: no existe {args.leakage_report}. Esta skill no decide "
            f"qué columnas excluir por su cuenta — corre auditoria-de-fugas primero.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(args.leakage_report, encoding="utf-8") as f:
        reporte_fugas = json.load(f)

    columnas_excluidas = (
        reporte_fugas.get("columnas_solo_en_train", [])
        + reporte_fugas.get("columnas_constantes", [])
        + reporte_fugas.get("columnas_identificador", [])
    )

    df = pd.read_csv(args.data, low_memory=False)

    for col in (args.group_col, args.target_col):
        if col not in df.columns:
            print(f"ERROR: la columna '{col}' no existe en {args.data}", file=sys.stderr)
            sys.exit(1)

    numericas, categoricas = preparar_features(df, columnas_excluidas, args.target_col, args.group_col)
    folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, args.seed)

    # Nivel 0: referencia univariada, tomada del reporte de fugas, sin re-entrenar.
    univariado = reporte_fugas.get("univariado", [])
    if univariado:
        mejor = max(univariado, key=lambda u: u["auc_oof"])
        nivel_0 = {
            "columna": mejor["columna"],
            "auc_estandar": mejor["auc_oof"],
            "nota": "AUC estándar, NO pAUC — no comparable directamente con niveles 1 y 2",
        }
    else:
        nivel_0 = {"columna": None, "auc_estandar": None, "nota": "sin datos univariados en el reporte de fugas"}

    # Nivel 1: regresión logística balanceada.
    def modelo_logreg():
        return LogisticRegression(class_weight="balanced", max_iter=1000)

    paucs_1 = evaluar_modelo(df, args.target_col, folds, numericas, categoricas, modelo_logreg, escalar=True)

    # Nivel 2: gradient boosting.
    def modelo_gb():
        return HistGradientBoostingClassifier(random_state=args.seed)

    paucs_2 = evaluar_modelo(df, args.target_col, folds, numericas, categoricas, modelo_gb)

    resultado = {
        "esquema_cv": {"group_col": args.group_col, "n_splits": args.n_splits, "seed": args.seed},
        "metrica": "pAUC sobre 80% TPR, rango [0, 0.2]",
        "metrica_verificada_contra_fuente_oficial": True,
        "metrica_fuente": "referencias/isic-primary-metric-pauc.py.md (p_auc_tpr, ISIC/MSKCC), verificado 2026-08-11",
        "columnas_excluidas": columnas_excluidas,
        "n_features_usadas": len(numericas) + len(categoricas),
        "nivel_0_referencia_univariada": nivel_0,
        "nivel_1_regresion_logistica": {
            "pauc_por_fold": [round(float(p), 4) for p in paucs_1],
            "pauc_media": round(float(np.mean(paucs_1)), 4),
            "pauc_std": round(float(np.std(paucs_1)), 4),
        },
        "nivel_2_gradient_boosting": {
            "modelo": "HistGradientBoostingClassifier",
            "pauc_por_fold": [round(float(p), 4) for p in paucs_2],
            "pauc_media": round(float(np.mean(paucs_2)), 4),
            "pauc_std": round(float(np.std(paucs_2)), 4),
        },
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    lineas = []
    lineas.append(f"# Modelado baseline — {args.data}")
    lineas.append("Métrica: pAUC sobre 80% TPR [0, 0.2] · verificada contra el script oficial (2026-08-11)")
    lineas.append(f"Esquema CV: {args.n_splits} folds agrupados por {args.group_col}, seed {args.seed}")
    lineas.append(f"Columnas excluidas: {len(columnas_excluidas)} · features usadas: {resultado['n_features_usadas']}")
    lineas.append(
        f"Nivel 0 (univariado, AUC estándar no pAUC): {nivel_0['columna']} = {nivel_0['auc_estandar']}"
    )
    lineas.append(
        f"Nivel 1 (regresión logística balanceada): pAUC media {resultado['nivel_1_regresion_logistica']['pauc_media']} "
        f"± {resultado['nivel_1_regresion_logistica']['pauc_std']}"
    )
    lineas.append(
        f"Nivel 2 (gradient boosting): pAUC media {resultado['nivel_2_gradient_boosting']['pauc_media']} "
        f"± {resultado['nivel_2_gradient_boosting']['pauc_std']}"
    )
    lineas.append("Detalle por fold: outputs/modelado-baseline.json")

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

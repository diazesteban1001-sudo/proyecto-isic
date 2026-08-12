#!/usr/bin/env python3
"""
audit_leakage.py — instrumento de medición para la skill auditoria-de-fugas.

Chequeos estructurales + escaneo univariado de AUC fuera de muestra con
partición agrupada. No combina columnas, no ajusta hiperparámetros, no
es un baseline. No decide nada — mide y deja preguntas abiertas cuando
no puede resolver algo por sí solo.

Uso:
    python audit_leakage.py --train data/train-metadata.csv \
                             --test data/test-metadata.csv \
                             --group-col patient_id \
                             --target-col target \
                             --n-splits 5 \
                             --seed 42 \
                             --auc-threshold 0.90 \
                             --out outputs/auditoria-de-fugas
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

try:
    from sklearn.model_selection import StratifiedGroupKFold
    HAS_STRATIFIED_GROUP = True
except ImportError:
    HAS_STRATIFIED_GROUP = False
from sklearn.model_selection import GroupKFold

NOMBRES_SOSPECHOSOS = ["confidence", "score", "pred", "diagnos", "iddx", "mel_"]


def columnas_estructurales(train, test, target_col, group_col):
    cols_train = set(train.columns)
    cols_test = set(test.columns) if test is not None else set()

    solo_train = sorted(cols_train - cols_test) if test is not None else []

    constantes = [c for c in train.columns if train[c].nunique(dropna=False) <= 1]

    n = len(train)
    identificador = [
        c for c in train.columns
        if train[c].nunique(dropna=False) == n and c not in (target_col, group_col)
    ]

    nombre_sospechoso = [
        c for c in train.columns
        if any(patron in c.lower() for patron in NOMBRES_SOSPECHOSOS)
        and c not in (target_col,)
    ]

    return solo_train, constantes, identificador, nombre_sospechoso


def construir_folds(train, group_col, target_col, n_splits, seed):
    if HAS_STRATIFIED_GROUP:
        n_grupos_positivos = train.loc[train[target_col] == 1, group_col].nunique()
        if n_grupos_positivos >= n_splits:
            splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
            return list(splitter.split(train, train[target_col], groups=train[group_col]))
    splitter = GroupKFold(n_splits=n_splits)
    return list(splitter.split(train, train[target_col], groups=train[group_col]))


def auc_oof_columna(train, col, target_col, folds):
    """AUC fuera de muestra para una sola columna, ajustando cualquier
    codificación necesaria SOLO dentro de cada fold de entrenamiento."""
    y = train[target_col].values
    oof_scores = np.full(len(train), np.nan)
    es_numerica = pd.api.types.is_numeric_dtype(train[col])

    for train_idx, val_idx in folds:
        col_train = train[col].iloc[train_idx]
        col_val = train[col].iloc[val_idx]

        if es_numerica:
            mediana = col_train.median()
            scores_val = col_val.fillna(mediana).values
        else:
            # codificación de medias, ajustada solo con el fold de entrenamiento
            medias = train.iloc[train_idx].groupby(col)[target_col].mean()
            media_global = y[train_idx].mean()
            scores_val = col_val.map(medias).fillna(media_global).values

        oof_scores[val_idx] = scores_val

    mask = ~np.isnan(oof_scores)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None

    auc = roc_auc_score(y[mask], oof_scores[mask])
    # una columna puede predecir bien "al revés"; nos interesa la fuerza
    # de la señal, no la dirección
    return max(auc, 1 - auc), es_numerica


def preguntas_abiertas(nombre_sospechoso, solo_train, univariado_por_col, target_col):
    preguntas = []
    for c in nombre_sospechoso:
        es_post_evento_obvio = c in solo_train and c != target_col
        nunca_evaluada = c not in univariado_por_col
        if c == target_col:
            continue
        if es_post_evento_obvio and nunca_evaluada:
            # está en solo_train (nunca se evaluó univariado, es excluida
            # de entrada) — igual dejamos constancia de por qué.
            preguntas.append({
                "columna": c,
                "pregunta": (
                    f"'{c}' tiene nombre sugerente de derivación posterior y no "
                    f"está en test. ¿Es post-evento (excluir sin discusión) o "
                    f"una señal derivada que tampoco estaría disponible en "
                    f"inferencia real (excluir igual, pero por otra razón)?"
                ),
            })
        elif not es_post_evento_obvio:
            preguntas.append({
                "columna": c,
                "pregunta": (
                    f"'{c}' tiene nombre sugerente pero SÍ está en test. "
                    f"¿Por qué existiría en ambos conjuntos si fuera derivada "
                    f"del diagnóstico? Investigar el origen antes de usarla."
                ),
            })
    return preguntas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--test", required=False, default=None)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--auc-threshold", type=float, default=0.90)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    train = pd.read_csv(args.train, low_memory=False)
    test = pd.read_csv(args.test, low_memory=False) if args.test and os.path.exists(args.test) else None

    for col in (args.group_col, args.target_col):
        if col not in train.columns:
            print(f"ERROR: la columna '{col}' no existe en {args.train}", file=sys.stderr)
            sys.exit(1)

    solo_train, constantes, identificador, nombre_sospechoso = columnas_estructurales(
        train, test, args.target_col, args.group_col
    )

    excluir_del_univariado = set(solo_train) | set(constantes) | set(identificador) | {
        args.group_col, args.target_col
    }
    candidatas = [c for c in train.columns if c not in excluir_del_univariado]

    folds = construir_folds(train, args.group_col, args.target_col, args.n_splits, args.seed)

    univariado = []
    univariado_por_col = {}
    for c in candidatas:
        resultado = auc_oof_columna(train, c, args.target_col, folds)
        if resultado is None:
            continue
        auc, es_numerica = resultado
        entrada = {
            "columna": c,
            "tipo": "numerica" if es_numerica else "categorica",
            "auc_oof": round(float(auc), 4),
            "n_faltantes": int(train[c].isna().sum()),
            "sospechosa": bool(auc >= args.auc_threshold),
        }
        univariado.append(entrada)
        univariado_por_col[c] = entrada

    preguntas = preguntas_abiertas(nombre_sospechoso, solo_train, univariado_por_col, args.target_col)

    resultado = {
        "esquema_cv": {"group_col": args.group_col, "n_splits": args.n_splits, "seed": args.seed},
        "columnas_solo_en_train": solo_train,
        "columnas_constantes": constantes,
        "columnas_identificador": identificador,
        "columnas_nombre_sospechoso": nombre_sospechoso,
        "umbral_auc_sospechoso": args.auc_threshold,
        "univariado": sorted(univariado, key=lambda x: x["auc_oof"], reverse=True),
        "preguntas_abiertas": preguntas,
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    sospechosas = [u for u in univariado if u["sospechosa"]]
    # El .md debe caber en 15 lineas con cualquier numero de hallazgos: cada
    # bloque de detalle esta acotado y el resto vive en el .json.
    MAX_DETALLE = 3
    lineas = []
    lineas.append(f"# Auditoría de fugas — {args.train}")
    lineas.append(f"Columnas solo en train (excluidas de entrada): {len(solo_train)}")
    lineas.append(f"Columnas constantes: {len(constantes)} · identificador: {len(identificador)}")
    lineas.append(f"Columnas evaluadas univariadamente: {len(univariado)} · umbral AUC >= {args.auc_threshold}")
    lineas.append(f"Columnas sospechosas por AUC alto: {len(sospechosas)}")
    for u in sospechosas[:MAX_DETALLE]:
        lineas.append(f"  - {u['columna']}: AUC {u['auc_oof']} ({u['tipo']})")
    if len(sospechosas) > MAX_DETALLE:
        lineas.append(f"  ... y {len(sospechosas) - MAX_DETALLE} más")
    lineas.append(f"Preguntas abiertas sin resolver por el script: {len(preguntas)}")
    for p in preguntas[:MAX_DETALLE]:
        lineas.append(f"  - {p['columna']}: {p['pregunta']}")
    if len(preguntas) > MAX_DETALLE:
        lineas.append(f"  ... y {len(preguntas) - MAX_DETALLE} más")
    lineas.append(f"Detalle completo: {args.out}.json")

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

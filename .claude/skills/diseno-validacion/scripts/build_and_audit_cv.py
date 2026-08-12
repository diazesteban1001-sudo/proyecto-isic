#!/usr/bin/env python3
"""
build_and_audit_cv.py — instrumento de medición para la skill diseno-validacion.

Construye un esquema de validación cruzada agrupado, lo audita
estructuralmente, y cuantifica cuánta fuga produciría ignorar la
agrupación. No entrena ningún modelo. No decide nada — solo mide.

Uso:
    python build_and_audit_cv.py --data data/train-metadata.csv \
                                  --group-col patient_id \
                                  --target-col target \
                                  --n-splits 5 \
                                  --seed 42 \
                                  --out outputs/diseno-validacion
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

try:
    from sklearn.model_selection import StratifiedGroupKFold
    HAS_STRATIFIED_GROUP = True
except ImportError:
    HAS_STRATIFIED_GROUP = False


def elegir_metodo(df, target_col, group_col, n_splits):
    """StratifiedGroupKFold si está disponible y hay suficientes grupos
    positivos para estratificar en n_splits; si no, GroupKFold plano."""
    if not HAS_STRATIFIED_GROUP:
        return "GroupKFold"
    n_grupos_positivos = df.loc[df[target_col] == 1, group_col].nunique()
    if n_grupos_positivos < n_splits:
        return "GroupKFold"
    return "StratifiedGroupKFold"


def auditar_fuga_de_grupo(df, group_col, fold_assignments, n_splits):
    """Verifica, de forma independiente a la construcción, que ningún
    grupo aparezca en más de un fold."""
    grupo_a_folds = df.groupby(group_col).apply(
        lambda g: set(fold_assignments[g.index])
    )
    grupos_en_mas_de_un_fold = grupo_a_folds[grupo_a_folds.apply(len) > 1]
    return len(grupos_en_mas_de_un_fold) > 0


def comparacion_naive(df, group_col, seed, val_frac=0.2):
    """Partición aleatoria simple a nivel de fila, ignorando group_col.
    Cuenta cuántos grupos quedan repartidos entre train y validación."""
    rng = np.random.RandomState(seed)
    n = len(df)
    idx_val = rng.choice(n, size=int(n * val_frac), replace=False)
    es_val = np.zeros(n, dtype=bool)
    es_val[idx_val] = True

    grupos = df[group_col].values
    grupo_a_lados = {}
    for g, v in zip(grupos, es_val):
        lados = grupo_a_lados.setdefault(g, set())
        lados.add("val" if v else "train")

    n_con_fuga = sum(1 for lados in grupo_a_lados.values() if len(lados) > 1)
    n_grupos_total = len(grupo_a_lados)
    return {
        "descripcion": "partición aleatoria 80/20 a nivel de fila, misma semilla, ignorando group_col",
        "n_grupos_con_fuga": int(n_con_fuga),
        "pct_grupos_con_fuga": round(100 * n_con_fuga / n_grupos_total, 2) if n_grupos_total else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.data, low_memory=False)

    for col in (args.group_col, args.target_col):
        if col not in df.columns:
            print(f"ERROR: la columna '{col}' no existe en {args.data}", file=sys.stderr)
            sys.exit(1)

    df = df.reset_index(drop=True)

    metodo = elegir_metodo(df, args.target_col, args.group_col, args.n_splits)

    fold_assignments = np.full(len(df), -1, dtype=int)

    if metodo == "StratifiedGroupKFold":
        splitter = StratifiedGroupKFold(n_splits=args.n_splits, shuffle=True, random_state=args.seed)
        splits = splitter.split(df, df[args.target_col], groups=df[args.group_col])
    else:
        splitter = GroupKFold(n_splits=args.n_splits)
        splits = splitter.split(df, df[args.target_col], groups=df[args.group_col])

    por_fold = []
    for fold_i, (train_idx, val_idx) in enumerate(splits):
        fold_assignments[val_idx] = fold_i
        n_val_pos = int(df.iloc[val_idx][args.target_col].sum())
        por_fold.append({
            "fold": fold_i,
            "n_train_grupos": int(df.iloc[train_idx][args.group_col].nunique()),
            "n_val_grupos": int(df.iloc[val_idx][args.group_col].nunique()),
            "n_train_filas": int(len(train_idx)),
            "n_val_filas": int(len(val_idx)),
            "n_val_positivos": n_val_pos,
            "pct_val_positivos": round(100 * n_val_pos / len(val_idx), 4) if len(val_idx) else 0.0,
        })

    fuga_detectada = auditar_fuga_de_grupo(df, args.group_col, fold_assignments, args.n_splits)
    comparacion = comparacion_naive(df, args.group_col, args.seed)

    resultado = {
        "esquema": {
            "metodo": metodo,
            "n_splits": args.n_splits,
            "group_col": args.group_col,
            "target_col": args.target_col,
            "seed": args.seed,
        },
        "n_grupos_total": int(df[args.group_col].nunique()),
        "n_grupos_positivos": int(df.loc[df[args.target_col] == 1, args.group_col].nunique()),
        "por_fold": por_fold,
        "fuga_de_grupo_detectada": bool(fuga_detectada),
        "comparacion_particion_naive": comparacion,
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    lineas = []
    lineas.append(f"# Diseño de validación — {args.data}")
    lineas.append(f"Método: {metodo} · n_splits={args.n_splits} · seed={args.seed}")
    lineas.append(f"Grupos totales: {resultado['n_grupos_total']} · grupos con al menos un positivo: {resultado['n_grupos_positivos']}")
    lineas.append(f"Fuga de grupo detectada en el esquema construido: {fuga_detectada}")
    # Resumen en lineas fijas: el .md debe caber en 15 lineas con cualquier
    # n_splits. El detalle fold a fold vive en el .json.
    pos = [f["n_val_positivos"] for f in por_fold]
    filas = [f["n_val_filas"] for f in por_fold]
    grupos = [f["n_val_grupos"] for f in por_fold]
    lineas.append(
        f"Positivos en validación por fold: min {min(pos)}, max {max(pos)}, "
        f"promedio {round(sum(pos) / len(pos), 1)}, total {sum(pos)}"
    )
    lineas.append(
        f"Filas en validación por fold: min {min(filas)}, max {max(filas)} · "
        f"grupos por fold: min {min(grupos)}, max {max(grupos)}"
    )
    lineas.append("Detalle fold a fold: outputs/diseno-validacion.json campo `por_fold`.")
    lineas.append(
        f"Partición naive (ignora grupo): {comparacion['n_grupos_con_fuga']} de "
        f"{resultado['n_grupos_total']} grupos ({comparacion['pct_grupos_con_fuga']}%) "
        f"quedarían repartidos entre train y validación."
    )

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

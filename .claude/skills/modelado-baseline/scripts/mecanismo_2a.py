#!/usr/bin/env python3
"""
mecanismo_2a.py — instrumento de medición para la skill modelado-baseline.

Mide cómo se distribuyen, sobre validación, las probabilidades que predice el
nivel 2a (gradient boosting sin balancear) y, como control, el 2b (el mismo
modelo con class_weight="balanced"). Mide y reporta; no interpreta ni dice
por qué la pAUC del 2a queda donde queda (CLAUDE.md, Pendientes,
«Por qué el nivel 2a hunde a una parte de los positivos está sin medir»).

Usa la misma partición y los mismos modelos que train_and_evaluate.py: el
conjunto de desarrollo, la partición de la semilla 42, las mismas columnas
excluidas, la misma codificación por pliegue y los mismos constructores de
HistGradientBoostingClassifier. Las funciones se importan de ese script, no
se copian.

Por pliegue y en total, sobre validación (medir()):
  - n_valores_distintos: número de valores distintos de la probabilidad
    predicha.
  - frac_neg_ge_0999 y frac_pos_ge_0999: fracción de negativos y de
    positivos con probabilidad >= 0,999.
  - frac_neg_en_max y frac_pos_en_max: fracción de negativos y de positivos
    con la probabilidad máxima del pliegue.
  - rango_medio_pos: el rango percentil medio de los positivos, en escala
    0–1: media, sobre los positivos, de su rango entre todas las lesiones de
    validación, con rango medio en los empates: (n de puntuaciones menores +
    0,5 · n de iguales) / n. 0 es la más baja; 1, la más alta. El nombre del
    campo no lleva «percentil» a propósito: verificar_trazabilidad.py trata
    como porcentaje todo campo cuyo nombre empieza por «percent», y este
    valor es una fracción.
  - frac_neg_sobre_mediana_pos: fracción de negativos con probabilidad
    estrictamente mayor que la mediana de las de los positivos.
  - pauc: la pAUC sobre 80% TPR, con pauc_above_tpr() de
    train_and_evaluate.py.
La cola baja de los positivos (añadido el 2026-10-04, sin cambiar lo de
arriba):
  - p20_neg y frac_pos_bajo_p20_neg: el percentil 20 de las probabilidades
    de los negativos del pliegue (np.percentile, interpolación lineal) y la
    fracción de positivos con probabilidad menor o igual que él.
  - minimo_predicho, n_neg_en_el_minimo y n_pos_en_el_minimo: el valor
    mínimo predicho en el pliegue y cuántos negativos y cuántos positivos
    comparten ese valor.
  - deciles_rango_pos: los deciles (10, 20, …, 90) del rango percentil de
    los positivos, el mismo rango cuya media es rango_medio_pos.
«En total» es lo mismo sobre las predicciones de validación de los cinco
pliegues juntas: cada lesión de desarrollo aparece una vez, con la
probabilidad del modelo del pliegue en que fue validación. La pAUC total se
da además como media de los pliegues, que es lo que reporta
modelado-baseline.json.

Control: la pAUC de cada pliegue, del 2a y del 2b, tiene que coincidir con
outputs/modelado-baseline.json (pauc_por_fold, a 4 decimales). Si no
coincide, el script se detiene antes de escribir nada.

Uso:
    python mecanismo_2a.py --data data/train-metadata.csv \\
                           --group-col patient_id \\
                           --target-col target \\
                           --n-splits 5 \\
                           --seed 42 \\
                           --leakage-report outputs/auditoria-de-fugas.json \\
                           --referencia outputs/modelado-baseline.json \\
                           --out outputs/mecanismo-2a
"""

import argparse
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import (  # noqa: E402
    RUTA_HOLDOUT,
    cargar_desarrollo,
    codificar_fold,
    construir_folds,
    pauc_above_tpr,
    preparar_features,
)

UMBRAL_ALTO = 0.999
NIVELES = {
    "nivel_2a_gradient_boosting_sin_balancear": {},
    "nivel_2b_gradient_boosting_balanceado": {"class_weight": "balanced"},
}


def medir(y, p):
    """Las medidas de un conjunto de validación: etiquetas y (0/1) y
    probabilidades predichas p. Función pura, para poder forzarla con datos
    sintéticos (test_mecanismo_2a.py)."""
    y = np.asarray(y).astype(int)
    p = np.asarray(p, dtype=float)
    neg, pos = p[y == 0], p[y == 1]
    maximo = p.max()
    orden = np.sort(p)
    menores = np.searchsorted(orden, pos, side="left")
    iguales = np.searchsorted(orden, pos, side="right") - menores
    rango_pos = (menores + 0.5 * iguales) / len(p)
    return {
        "n_lesiones": int(len(p)),
        "n_negativos": int(len(neg)),
        "n_positivos": int(len(pos)),
        "n_valores_distintos": int(len(np.unique(p))),
        "probabilidad_maxima": float(maximo),
        "frac_neg_ge_0999": float(np.mean(neg >= UMBRAL_ALTO)),
        "frac_pos_ge_0999": float(np.mean(pos >= UMBRAL_ALTO)),
        "frac_neg_en_max": float(np.mean(neg == maximo)),
        "frac_pos_en_max": float(np.mean(pos == maximo)),
        "rango_medio_pos": float(np.mean(rango_pos)),
        "frac_neg_sobre_mediana_pos": float(np.mean(neg > np.median(pos))),
        "pauc": float(pauc_above_tpr(y, p)),
        "p20_neg": float(np.percentile(neg, 20)),
        "frac_pos_bajo_p20_neg": float(np.mean(pos <= np.percentile(neg, 20))),
        "minimo_predicho": float(p.min()),
        "n_neg_en_el_minimo": int(np.sum(neg == p.min())),
        "n_pos_en_el_minimo": int(np.sum(pos == p.min())),
        "deciles_rango_pos": [float(v) for v in np.percentile(rango_pos, list(range(10, 100, 10)))],
    }


# Valores que pueden ser muy pequeños: con seis decimales, el mínimo del 2a
# saldría 0,0 sin serlo. Se guardan con seis cifras significativas.
SIGNIFICATIVAS = {"p20_neg", "minimo_predicho"}


def redondear(d):
    def r(v):
        if isinstance(v, float):
            return round(v, 6)
        if isinstance(v, list):
            return [r(x) for x in v]
        return v
    return {k: (float(f"{v:.6g}") if k in SIGNIFICATIVAS else r(v)) for k, v in d.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--referencia", default="outputs/modelado-baseline.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if os.path.basename(args.out) == "modelado-baseline":
        raise SystemExit("ERROR: mecanismo_2a.py no escribe outputs/modelado-baseline.")
    for ruta in (args.leakage_report, args.referencia):
        if not os.path.exists(ruta):
            raise SystemExit(f"ERROR: no existe {ruta}.")

    with open(args.leakage_report, encoding="utf-8") as f:
        reporte_fugas = json.load(f)
    with open(args.referencia, encoding="utf-8") as f:
        referencia = json.load(f)

    # Las mismas columnas excluidas que la corrida principal de
    # train_and_evaluate.py, procedencia incluida.
    columnas_excluidas = (
        reporte_fugas.get("columnas_solo_en_train", [])
        + reporte_fugas.get("columnas_constantes", [])
        + reporte_fugas.get("columnas_identificador", [])
        + reporte_fugas.get("columnas_procedencia", [])
    )
    if sorted(columnas_excluidas) != sorted(referencia["columnas_excluidas"]):
        raise SystemExit("ERROR: las columnas excluidas no son las de la referencia.")
    esquema = referencia["esquema_cv"]
    if (esquema["n_splits"], esquema["seed"], esquema["group_col"]) != (args.n_splits, args.seed, args.group_col):
        raise SystemExit(f"ERROR: el esquema de la referencia es {esquema}, no el pedido.")

    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    numericas, categoricas = preparar_features(df, columnas_excluidas, args.target_col, args.group_col)
    folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, args.seed)
    y = df[args.target_col].values

    resultado_niveles, control = {}, {}
    for nivel, extra in NIVELES.items():
        por_fold, y_todo, p_todo = [], [], []
        for train_idx, val_idx in folds:
            X_train, X_val = codificar_fold(df, numericas, categoricas, args.target_col, train_idx, val_idx)
            modelo = HistGradientBoostingClassifier(random_state=args.seed, **extra)
            modelo.fit(X_train, y[train_idx])
            p = modelo.predict_proba(X_val)[:, 1]
            por_fold.append(medir(y[val_idx], p))
            y_todo.append(y[val_idx])
            p_todo.append(p)

        obtenido = [round(f["pauc"], 4) for f in por_fold]
        esperado = referencia[nivel]["pauc_por_fold"]
        control[nivel] = {"pauc_por_fold_obtenido": obtenido, "pauc_por_fold_referencia": esperado,
                          "coincide": obtenido == esperado}
        if obtenido != esperado:
            raise SystemExit(
                f"CONTROL FALLIDO en {nivel}: pAUC por pliegue {obtenido}, la referencia "
                f"{args.referencia} dice {esperado}. No se escribe nada."
            )

        total = medir(np.concatenate(y_todo), np.concatenate(p_todo))
        total["pauc_media_de_pliegues"] = float(np.mean([f["pauc"] for f in por_fold]))
        resultado_niveles[nivel] = {
            "modelo": f"HistGradientBoostingClassifier(random_state={args.seed}"
                      + (", class_weight='balanced')" if extra else ")"),
            "por_pliegue": [redondear(f) for f in por_fold],
            "total": redondear(total),
        }

    resultado = {
        "datos": datos,
        "esquema_cv": {"group_col": args.group_col, "n_splits": args.n_splits, "seed": args.seed},
        "referencia": args.referencia,
        "control_pauc_contra_referencia": control,
        "umbral_alto": UMBRAL_ALTO,
        "definiciones": {
            "n_valores_distintos": "valores distintos de la probabilidad predicha en validación",
            "frac_neg_ge_0999 / frac_pos_ge_0999": "fracción de negativos / positivos con probabilidad >= umbral_alto",
            "frac_neg_en_max / frac_pos_en_max": "fracción de negativos / positivos con la probabilidad máxima del conjunto",
            "rango_medio_pos": "rango percentil medio de los positivos, en escala 0–1: media sobre los positivos de (n menores + 0,5 · n iguales) / n, entre todas las lesiones del conjunto; 0 la más baja, 1 la más alta",
            "frac_neg_sobre_mediana_pos": "fracción de negativos con probabilidad estrictamente mayor que la mediana de las de los positivos",
            "pauc": "pAUC sobre 80% TPR, pauc_above_tpr() de train_and_evaluate.py",
            "total": "las mismas medidas sobre las predicciones de validación de todos los pliegues juntas; pauc_media_de_pliegues es la media de las pAUC por pliegue",
            "p20_neg / frac_pos_bajo_p20_neg": "percentil 20 de las probabilidades de los negativos del conjunto (np.percentile, interpolación lineal) y fracción de positivos con probabilidad menor o igual que él",
            "minimo_predicho / n_neg_en_el_minimo / n_pos_en_el_minimo": "valor mínimo predicho en el conjunto y cuántos negativos y positivos lo comparten",
            "deciles_rango_pos": "deciles 10 a 90 del rango percentil de los positivos (el de rango_medio_pos), en escala 0–1",
        },
        "niveles": resultado_niveles,
    }

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    def linea(etiqueta, t):
        return (
            f"{etiqueta}: {t['n_valores_distintos']} valores distintos · máx {t['probabilidad_maxima']:.6f} · "
            f"≥{UMBRAL_ALTO}: neg {t['frac_neg_ge_0999']:.4f}, pos {t['frac_pos_ge_0999']:.4f} · "
            f"en el máx: neg {t['frac_neg_en_max']:.4f}, pos {t['frac_pos_en_max']:.4f} · "
            f"rango percentil medio pos {t['rango_medio_pos']:.4f} · "
            f"neg sobre la mediana pos {t['frac_neg_sobre_mediana_pos']:.4f}"
        )

    def cola(etiqueta, t):
        deciles = ", ".join(f"{x:.3f}" for x in t["deciles_rango_pos"])
        return (
            f"{etiqueta}, total: pos ≤ p20 de neg {t['frac_pos_bajo_p20_neg']:.4f} · en el mínimo "
            f"({t['minimo_predicho']:.3g}): neg {t['n_neg_en_el_minimo']}, pos {t['n_pos_en_el_minimo']} · "
            f"deciles del rango pos {deciles}"
        )

    n2a = resultado_niveles["nivel_2a_gradient_boosting_sin_balancear"]
    n2b = resultado_niveles["nivel_2b_gradient_boosting_balanceado"]
    lineas = [
        f"# Mecanismo del 2a — {args.data}, conjunto de desarrollo",
        f"Partición: {args.n_splits} folds agrupados por {args.group_col}, seed {args.seed}; validación de cada pliegue",
        f"Control: pAUC por pliegue igual a {args.referencia} en 2a y 2b",
        f"Total = validación de los {args.n_splits} pliegues juntos ({n2a['total']['n_lesiones']} lesiones, "
        f"{n2a['total']['n_positivos']} positivas)",
        linea("2a, total", n2a["total"]),
        linea("2b, total", n2b["total"]),
        f"pAUC media de pliegues: 2a {n2a['total']['pauc_media_de_pliegues']:.4f} · 2b {n2b['total']['pauc_media_de_pliegues']:.4f}",
        "2a por pliegue, valores distintos: " + ", ".join(str(f["n_valores_distintos"]) for f in n2a["por_pliegue"]),
        "2a por pliegue, neg ≥0.999: " + ", ".join(f"{f['frac_neg_ge_0999']:.4f}" for f in n2a["por_pliegue"]),
        "2a por pliegue, rango percentil medio pos: " + ", ".join(f"{f['rango_medio_pos']:.4f}" for f in n2a["por_pliegue"]),
        "2b por pliegue, rango percentil medio pos: " + ", ".join(f"{f['rango_medio_pos']:.4f}" for f in n2b["por_pliegue"]),
        cola("2a", n2a["total"]),
        cola("2b", n2b["total"]),
        f"Definiciones y detalle por pliegue: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

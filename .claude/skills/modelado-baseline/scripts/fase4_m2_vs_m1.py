#!/usr/bin/env python3
"""
fase4_m2_vs_m1.py — Fase 4, primera comparación principal: M2 − M1 (PLAN.md).

  M1 = el nivel 2b actual: HistGradientBoostingClassifier(class_weight="balanced",
       random_state=semilla), con las variables de desarrollo de modelado-baseline.
  M2 = M1 más el contexto de paciente de contexto_paciente.py, con los mismos
       hiperparámetros.

Validación repetida con las semillas dadas y los mismos folds de desarrollo que
outputs/validacion-repetida.json. Por modelo: pAUC, AUC, SEtop-15 y NNT80% SE en
cada (semilla, fold). Para cada métrica, M2 − M1 pareado fold a fold, con
intervalo t ingenuo y corregido por Nadeau y Bengio y victorias por fold y por
semilla. La principal es la del pAUC, la métrica del cliente; las otras tres se
reportan como secundarias. En el NNT, menos es mejor, y las victorias se cuentan
en esa dirección.

NO reimplementa nada verificado: importa los folds, la codificación y el pAUC de
train_and_evaluate.py, la corrección de Nadeau y Bengio de evaluar_repetido.py,
las métricas de triaje de metricas_triaje.py y el contexto de contexto_paciente.py.
Comprueba que su M1 reproduce fold a fold el nivel 2b de la referencia.

No interpreta: mide y escribe outputs/fase4-m2-vs-m1.json y su .md.

Uso:
    python fase4_m2_vs_m1.py --data data/train-metadata.csv \
                             --group-col patient_id --target-col target \
                             --n-splits 5 \
                             --leakage-report outputs/auditoria-de-fugas.json \
                             --referencia outputs/validacion-repetida.json \
                             --out outputs/fase4-m2-vs-m1 \
                             --semillas 0 1 2 3 4 5 6 7 8 9
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import codificar_fold, construir_folds, pauc_above_tpr, preparar_features  # noqa: E402
from evaluar_repetido import _nadeau_bengio, _semillas_a_favor_de_2b, cargar_columnas_excluidas  # noqa: E402
from metricas_triaje import nnt_a_sensibilidad, setop_n  # noqa: E402
from contexto_paciente import variables_contexto_paciente  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402  (ruta añadida por train_and_evaluate)

METRICAS = {  # nombre: (mayor es mejor)
    "pauc": True,
    "auc": True,
    "setop15": True,
    "nnt80": False,
}


def huella_folds(folds, n):
    asignacion = np.full(n, -1, dtype=np.int64)
    for i, (_, val_idx) in enumerate(folds):
        asignacion[val_idx] = i
    return hashlib.sha256(asignacion.tobytes()).hexdigest()


def medir(y, s, grupos):
    return {
        "pauc": float(pauc_above_tpr(y, s)),
        "auc": float(roc_auc_score(y, s)),
        "setop15": setop_n(y, s, grupos),
        "nnt80": nnt_a_sensibilidad(y, s),
    }


def comparacion(diffs, n_splits, semillas, mayor_es_mejor):
    """Media, intervalo t ingenuo y corregido por Nadeau y Bengio, y victorias
    de M2 por fold y por semilla, en la dirección de la métrica."""
    n = len(diffs)
    media = float(np.mean(diffs))
    desviacion = float(np.std(diffs, ddof=1))
    t = float(stats.t.ppf(0.975, df=n - 1))
    ee = desviacion / np.sqrt(n)
    a_favor = diffs if mayor_es_mejor else [-d for d in diffs]
    return {
        "diferencias_m2_menos_m1": [round(d, 4) for d in diffs],
        "n_diferencias": n,
        "media": round(media, 4),
        "desviacion": round(desviacion, 4),
        "intervalo_t_95": [round(float(media - t * ee), 4), round(float(media + t * ee), 4)],
        "intervalo_t_95_nadeau_bengio": _nadeau_bengio(diffs, n_splits),
        "mayor_es_mejor": mayor_es_mejor,
        "m2_mejor_en_folds": sum(1 for d in a_favor if d > 0),
        "de_folds": n,
        "m2_mejor_en_semillas": _semillas_a_favor_de_2b(a_favor, n_splits, semillas),
        "de_semillas": len(semillas),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--referencia", default=None, help="outputs/validacion-repetida.json, para comprobar M1")
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()

    t_total = time.perf_counter()
    excluidas = cargar_columnas_excluidas(args.leakage_report)
    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    numericas, categoricas = preparar_features(df, excluidas, args.target_col, args.group_col)

    t0 = time.perf_counter()
    contexto = variables_contexto_paciente(df.drop(columns=[args.target_col]), numericas, args.group_col)
    t_contexto = time.perf_counter() - t0
    for c in contexto.columns:
        df[c] = contexto[c]
    modelos = {
        "M1": (numericas, categoricas),
        "M2": (numericas + list(contexto.columns), categoricas),
    }

    y = df[args.target_col].to_numpy()
    grupos = df[args.group_col].to_numpy()
    semillas = list(args.semillas)
    por = {m: {k: {} for k in METRICAS} for m in modelos}
    huellas, t_semilla = {}, {}
    for seed in semillas:
        inicio = time.perf_counter()
        folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, seed)
        huellas[str(seed)] = huella_folds(folds, len(df))
        for m, (num, cat) in modelos.items():
            valores = {k: [] for k in METRICAS}
            for tr, va in folds:
                x_tr, x_va = codificar_fold(df, num, cat, args.target_col, tr, va)
                modelo = HistGradientBoostingClassifier(random_state=seed, class_weight="balanced")
                modelo.fit(x_tr, y[tr])
                s = modelo.predict_proba(x_va)[:, 1]
                for k, v in medir(y[va], s, grupos[va]).items():
                    valores[k].append(v)
            for k in METRICAS:
                por[m][k][str(seed)] = valores[k]
        t_semilla[str(seed)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {seed}: {t_semilla[str(seed)]} s", flush=True)

    reproduccion = None
    if args.referencia:
        with open(args.referencia, encoding="utf-8") as f:
            ref = json.load(f)["nivel_2b_gradient_boosting_balanceado"]["pauc_por_semilla_y_fold"]
        discrepancias = [s for s in semillas
                         if [round(v, 4) for v in por["M1"]["pauc"][str(s)]] != ref.get(str(s))]
        reproduccion = {"referencia": args.referencia, "m1_reproduce_nivel_2b_fold_a_fold": not discrepancias,
                        "semillas_con_discrepancia": discrepancias}

    def resumen(m, k):
        todos = [v for s in semillas for v in por[m][k][str(s)]]
        medias = [float(np.mean(por[m][k][str(s)])) for s in semillas]
        return {
            "por_semilla_y_fold": {str(s): [round(v, 4) for v in por[m][k][str(s)]] for s in semillas},
            "media_global": round(float(np.mean(todos)), 4),
            "std_entre_folds": round(float(np.std(todos)), 4),
            "std_entre_semillas": round(float(np.std(medias)), 4),
        }

    comparaciones = {}
    for k, mayor in METRICAS.items():
        diffs = [float(b - a) for s in semillas for a, b in zip(por["M1"][k][str(s)], por["M2"][k][str(s)])]
        comparaciones[k] = {**comparacion(diffs, args.n_splits, semillas, mayor),
                            "papel": "principal" if k == "pauc" else "secundaria"}

    resultado = {
        "datos": datos,
        "semillas_corridas": semillas,
        "n_splits": args.n_splits,
        "modelos": {
            "M1": {"descripcion": "nivel 2b actual", "n_variables": len(numericas) + len(categoricas)},
            "M2": {"descripcion": "M1 + contexto de paciente (contexto_paciente.py)",
                   "n_variables": len(numericas) + len(contexto.columns) + len(categoricas),
                   "variables_de_contexto": list(contexto.columns)},
        },
        "hiperparametros": "los del nivel 2b: HistGradientBoostingClassifier(class_weight='balanced', "
                           "random_state=semilla), el resto por defecto; sin ajuste",
        "folds": {"sha256_por_semilla": huellas,
                  "como_se_construyen": "construir_folds de train_and_evaluate.py, los mismos de validacion-repetida"},
        "reproduccion_de_m1": reproduccion,
        "metricas": {m: {k: resumen(m, k) for k in METRICAS} for m in modelos},
        "comparaciones_m2_menos_m1": comparaciones,
        "segundos": {"contexto_de_paciente": round(t_contexto, 1), "por_semilla": t_semilla,
                     "total": round(time.perf_counter() - t_total, 1)},
        "nota": (
            "Las diferencias fold a fold no son independientes: los entrenamientos se solapan. "
            "El intervalo corregido por Nadeau y Bengio tiene en cuenta ese solape; el ingenuo, no. "
            "En el NNT80% SE menos es mejor: las victorias de M2 cuentan las diferencias negativas."
        ),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    lineas = [
        f"# Fase 4 — M2 − M1, {len(semillas)} semillas × {args.n_splits} folds, conjunto de desarrollo",
        f"M1 = nivel 2b ({resultado['modelos']['M1']['n_variables']} variables) · "
        f"M2 = M1 + contexto de paciente ({resultado['modelos']['M2']['n_variables']} variables) · hiperparámetros de 2b",
    ]
    if reproduccion:
        lineas.append(f"M1 reproduce fold a fold el nivel 2b de {args.referencia}: {reproduccion['m1_reproduce_nivel_2b_fold_a_fold']}")
    for k in METRICAS:
        a, b = resultado["metricas"]["M1"][k]["media_global"], resultado["metricas"]["M2"][k]["media_global"]
        lineas.append(f"{nombres[k]}: M1 {a} · M2 {b}")
    for k in METRICAS:
        c = comparaciones[k]
        lineas.append(
            f"M2 − M1, {nombres[k]} ({c['papel']}): media {c['media']} · ingenuo {c['intervalo_t_95']} · "
            f"corregido {c['intervalo_t_95_nadeau_bengio']} · M2 mejor en {c['m2_mejor_en_folds']}/{c['de_folds']} "
            f"folds y {c['m2_mejor_en_semillas']}/{c['de_semillas']} semillas"
        )
    lineas.append("En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.")
    lineas.append(f"Detalle por semilla y fold: {args.out}.json")
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
sensibilidad_repetida.py — análisis de sensibilidad de las columnas de
procedencia (attribution, copyright_license) con validación repetida.

Corre, sobre los mismos folds, las dos configuraciones: sin las columnas de
procedencia (la de outputs/validacion-repetida.json) y con ellas. Los folds
se construyen una vez por semilla y se usan para las dos, así que son
idénticos por construcción; además se guarda su huella (SHA-256 de la
asignación de folds) y se comprueba que la configuración sin procedencia
reproduce fold a fold los pAUC de outputs/validacion-repetida.json.

Comparaciones pareadas, una diferencia por (semilla, fold):
  (a) 2b − 1 con procedencia, junto a 2b − 1 sin procedencia;
  (b) 2b con procedencia − 2b sin procedencia;
  (c) 1 con procedencia − 1 sin procedencia.
Cada una con intervalo t ingenuo y corregido por Nadeau y Bengio, y
victorias del primer término por fold y por semilla.

NO reimplementa nada verificado: importa la métrica, los folds, la
codificación, los modelos y la corrección de Nadeau y Bengio de
train_and_evaluate.py y evaluar_repetido.py.

REGLA DURA: nunca escribe outputs/validacion-repetida.* ni
outputs/modelado-baseline.*. Es una sensibilidad: no sustituye a la
corrida principal ni se usa para elegir nada.

Uso:
    python sensibilidad_repetida.py --data data/train-metadata.csv \
                                    --group-col patient_id \
                                    --target-col target \
                                    --n-splits 5 \
                                    --leakage-report outputs/auditoria-de-fugas.json \
                                    --referencia outputs/validacion-repetida.json \
                                    --out outputs/sensibilidad-procedencia-repetida \
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import construir_folds, evaluar_modelo, preparar_features  # noqa: E402
from evaluar_repetido import (  # noqa: E402
    ETIQUETAS,
    _nadeau_bengio,
    _semillas_a_favor_de_2b,
    cargar_columnas_excluidas,
    modelos_de,
)
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402  (ruta añadida por train_and_evaluate)

SALIDAS_PROHIBIDAS = {"validacion-repetida", "modelado-baseline"}


def huella_folds(folds, n):
    asignacion = np.full(n, -1, dtype=np.int64)
    for i, (_, val_idx) in enumerate(folds):
        asignacion[val_idx] = i
    return hashlib.sha256(asignacion.tobytes()).hexdigest()


def comparacion(diffs, n_splits, semillas):
    """Mismos cálculos que la comparación 2b − 1 de evaluar_repetido.py:
    media, desviación, intervalo t ingenuo, intervalo corregido por Nadeau
    y Bengio, y victorias del primer término por fold y por semilla. La
    igualdad con aquella se comprueba en la salida (control_2b_menos_1)."""
    n = len(diffs)
    media = float(np.mean(diffs))
    desviacion = float(np.std(diffs, ddof=1))
    t = float(stats.t.ppf(0.975, df=n - 1))
    ee = desviacion / np.sqrt(n)
    return {
        "diferencias": [round(d, 4) for d in diffs],
        "n_diferencias": n,
        "media": round(media, 4),
        "desviacion": round(desviacion, 4),
        "intervalo_t_95": [round(float(media - t * ee), 4), round(float(media + t * ee), 4)],
        "intervalo_t_95_nadeau_bengio": _nadeau_bengio(diffs, n_splits),
        "gana_primer_termino_en_folds": sum(1 for d in diffs if d > 0),
        "de_folds": n,
        "gana_primer_termino_en_semillas": _semillas_a_favor_de_2b(diffs, n_splits, semillas),
        "de_semillas": len(semillas),
    }


def diferencias(por_semilla_a, nivel_a, por_semilla_b, nivel_b, semillas):
    return [float(x - y) for s in semillas for x, y in zip(por_semilla_a[s][nivel_a], por_semilla_b[s][nivel_b])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--referencia", required=True, help="outputs/validacion-repetida.json de la corrida principal")
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()

    if os.path.basename(args.out) in SALIDAS_PROHIBIDAS:
        print(f"ERROR: esta sensibilidad no escribe {args.out}. Usa otra salida.", file=sys.stderr)
        sys.exit(1)

    excluidas_sin = cargar_columnas_excluidas(args.leakage_report)
    with open(args.leakage_report, encoding="utf-8") as f:
        procedencia = json.load(f).get("columnas_procedencia", [])
    if not procedencia:
        print("ERROR: el reporte de fugas no declara columnas de procedencia.", file=sys.stderr)
        sys.exit(1)
    excluidas_con = [c for c in excluidas_sin if c not in procedencia]

    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    configuraciones = {
        "sin_procedencia": preparar_features(df, excluidas_sin, args.target_col, args.group_col),
        "con_procedencia": preparar_features(df, excluidas_con, args.target_col, args.group_col),
    }

    por_config = {c: {} for c in configuraciones}
    huellas = {}
    tiempos = {}
    for seed in args.semillas:
        inicio = time.time()
        folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, seed)
        huellas[str(seed)] = huella_folds(folds, len(df))
        for config, (numericas, categoricas) in configuraciones.items():
            por_config[config][seed] = {
                nivel: evaluar_modelo(df, args.target_col, folds, numericas, categoricas, fn, escalar=escalar)
                for nivel, (fn, escalar) in modelos_de(seed).items()
            }
        tiempos[str(seed)] = round(time.time() - inicio, 1)
        print(f"Semilla {seed}: {tiempos[str(seed)]}s")

    semillas = list(args.semillas)
    sin, con = por_config["sin_procedencia"], por_config["con_procedencia"]

    # Control: la configuración sin procedencia debe reproducir fold a fold la
    # corrida principal. Si no, los folds o los modelos no son los mismos.
    with open(args.referencia, encoding="utf-8") as f:
        ref = json.load(f)
    discrepancias = []
    for nivel, etiqueta in ETIQUETAS.items():
        for s in semillas:
            propio = [round(float(p), 4) for p in sin[s][nivel]]
            if propio != ref[etiqueta]["pauc_por_semilla_y_fold"][str(s)]:
                discrepancias.append(f"{nivel}, semilla {s}")
    control_2b_menos_1 = comparacion(diferencias(sin, "nivel_2b", sin, "nivel_1", semillas), args.n_splits, semillas)
    ref_comp = ref["comparacion_pareada_2b_menos_1"]
    igual_a_referencia = all(
        control_2b_menos_1[k] == ref_comp[k2] for k, k2 in [
            ("media", "media"), ("intervalo_t_95", "intervalo_t_95"),
            ("intervalo_t_95_nadeau_bengio", "intervalo_t_95_nadeau_bengio"),
            ("gana_primer_termino_en_folds", "gana_2b_en"),
            ("gana_primer_termino_en_semillas", "semillas_a_favor_de_2b"),
        ]
    )

    resultado = {
        "datos": datos,
        "semillas_corridas": semillas,
        "n_splits": args.n_splits,
        "sensibilidad": {
            "columnas_procedencia_incluidas": procedencia,
            "nota": (
                "Análisis de sensibilidad: los mismos folds de desarrollo que "
                "outputs/validacion-repetida.json, con y sin las columnas de procedencia. "
                "No sustituye a la corrida principal ni se usa para elegir nada."
            ),
        },
        "folds": {
            "sha256_por_semilla": huellas,
            "mismos_folds_en_las_dos_configuraciones": True,
            "como_se_garantiza": "se construyen una vez por semilla y se usan para las dos configuraciones",
            "sin_procedencia_reproduce_la_referencia_fold_a_fold": not discrepancias,
            "discrepancias_con_la_referencia": discrepancias,
            "referencia": args.referencia,
        },
        "pauc_por_semilla_y_fold": {
            config: {ETIQUETAS[n]: {str(s): [round(float(p), 4) for p in por_config[config][s][n]] for s in semillas}
                     for n in ETIQUETAS}
            for config in por_config
        },
        "pauc_media_global": {
            config: {ETIQUETAS[n]: round(float(np.mean([p for s in semillas for p in por_config[config][s][n]])), 4)
                     for n in ETIQUETAS}
            for config in por_config
        },
        "comparaciones": {
            "a_2b_menos_1_con_procedencia": comparacion(
                diferencias(con, "nivel_2b", con, "nivel_1", semillas), args.n_splits, semillas),
            "a_2b_menos_1_sin_procedencia": control_2b_menos_1,
            "b_2b_con_menos_2b_sin": comparacion(
                diferencias(con, "nivel_2b", sin, "nivel_2b", semillas), args.n_splits, semillas),
            "c_1_con_menos_1_sin": comparacion(
                diferencias(con, "nivel_1", sin, "nivel_1", semillas), args.n_splits, semillas),
        },
        "control_2b_menos_1": {
            "igual_a_la_referencia": igual_a_referencia,
            "nota": "a_2b_menos_1_sin_procedencia, recalculado aquí, contra comparacion_pareada_2b_menos_1 de la referencia",
        },
        "segundos_por_semilla": tiempos,
        "nota": (
            "Las diferencias de cada comparación NO son independientes: los conjuntos de "
            "entrenamiento se solapan entre folds. El intervalo corregido por Nadeau y Bengio "
            "tiene en cuenta ese solape; el ingenuo, no."
        ),
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    def linea(etiqueta, c):
        return (
            f"{etiqueta}: media {c['media']} · ingenuo {c['intervalo_t_95']} · "
            f"corregido {c['intervalo_t_95_nadeau_bengio']} · gana el primer término en "
            f"{c['gana_primer_termino_en_folds']}/{c['de_folds']} folds y "
            f"{c['gana_primer_termino_en_semillas']}/{c['de_semillas']} semillas"
        )

    comp = resultado["comparaciones"]
    medias = resultado["pauc_media_global"]
    lineas = [
        f"# Sensibilidad de procedencia, validación repetida — {len(semillas)} semillas, conjunto de desarrollo",
        f"SENSIBILIDAD: {procedencia} dentro del modelo. No sustituye a {args.referencia} ni se usa para elegir nada.",
        f"Folds: los mismos en las dos configuraciones; sin procedencia reproduce la referencia fold a fold: "
        f"{not discrepancias} · 2b − 1 sin procedencia igual al de la referencia: {igual_a_referencia}",
        "pAUC media global, sin / con procedencia: " + " · ".join(
            f"{n} {medias['sin_procedencia'][ETIQUETAS[n]]} / {medias['con_procedencia'][ETIQUETAS[n]]}"
            for n in ETIQUETAS),
        linea("(a) 2b − 1, con procedencia", comp["a_2b_menos_1_con_procedencia"]),
        linea("(a) 2b − 1, sin procedencia", comp["a_2b_menos_1_sin_procedencia"]),
        linea("(b) 2b con − 2b sin procedencia", comp["b_2b_con_menos_2b_sin"]),
        linea("(c) 1 con − 1 sin procedencia", comp["c_1_con_menos_1_sin"]),
        "Nota: el intervalo ingenuo supone diferencias independientes; los folds se solapan. Ver .json.",
        f"Detalle por semilla y fold: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

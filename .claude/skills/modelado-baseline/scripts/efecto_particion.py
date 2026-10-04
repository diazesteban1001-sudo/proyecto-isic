#!/usr/bin/env python3
"""
efecto_particion.py — instrumento de medición para la skill modelado-baseline.

Mide cuánto cambian las métricas del nivel 1 (logística balanceada) y del
nivel 2b (gradient boosting balanceado, = M1) según la partición de la
validación cruzada: la de siempre, agrupada por paciente, y una por filas,
sin agrupar. Mide y reporta; no interpreta. La especificación y la regla de
lectura las fijó la persona antes de correr (PLAN.md, Fase 6, «El efecto de
la partición», 2026-10-04); la regla la aplica el agente, no este script.

Configuración de evaluar_repetido.py, importada y no copiada: el cargador
del conjunto de desarrollo, que se niega a entregar pacientes reservados; las
columnas excluidas del reporte de fugas; preparar_features y codificar_fold;
los modelos de modelos_de(semilla), con el escalado de la logística; y la
corrección de Nadeau y Bengio. Las métricas son las del proyecto:
pauc_above_tpr, roc_auc_score, setop_n y nnt_a_sensibilidad.

Particiones, 5 pliegues y semillas de la 0 a la 9:
  - paciente: construir_folds de train_and_evaluate.py, StratifiedGroupKFold
    por patient_id con shuffle y random_state = semilla;
  - filas: StratifiedKFold con shuffle y random_state = semilla, sin agrupar.

Control: la partición por paciente tiene que reproducir
outputs/validacion-repetida.json pliegue a pliegue (pAUC a 4 decimales) en
los niveles 1 y 2b. Se comprueba antes de correr la partición por filas; si
no coincide, el script se detiene sin escribir nada.

Uso:
    python efecto_particion.py --data data/train-metadata.csv \\
                               --group-col patient_id \\
                               --target-col target \\
                               --leakage-report outputs/auditoria-de-fugas.json \\
                               --referencia outputs/validacion-repetida.json \\
                               --out outputs/efecto-particion
"""

import argparse
import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evaluar_repetido import (  # noqa: E402
    ETIQUETAS,
    RUTA_HOLDOUT,
    _nadeau_bengio,
    cargar_columnas_excluidas,
    cargar_desarrollo,
    modelos_de,
)
from metricas_triaje import nnt_a_sensibilidad, setop_n  # noqa: E402
from train_and_evaluate import (  # noqa: E402
    codificar_fold,
    construir_folds,
    pauc_above_tpr,
    preparar_features,
)

NIVELES = ("nivel_1", "nivel_2b")
METRICAS = ("pauc", "auc", "setop15", "nnt80")
# En el NNT80% SE menos es mejor; en las demás, más.
MAYOR_ES_MEJOR = {"pauc": True, "auc": True, "setop15": True, "nnt80": False}
PARTICIONES = ("paciente", "filas")


def folds_de(particion, df, group_col, target_col, n_splits, seed):
    if particion == "paciente":
        return construir_folds(df, group_col, target_col, n_splits, seed)
    return list(StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed).split(df, df[target_col]))


def evaluar(df, target_col, group_col, folds, numericas, categoricas, modelo_fn, escalar):
    """Los mismos pasos que evaluar_modelo() de train_and_evaluate.py
    —codificar dentro del pliegue, escalar si toca, ajustar, predecir—, pero
    devuelve las cuatro métricas de cada pliegue, no solo la pAUC."""
    y = df[target_col].values
    grupos = df[group_col].values
    por_fold = []
    for train_idx, val_idx in folds:
        X_train, X_val = codificar_fold(df, numericas, categoricas, target_col, train_idx, val_idx)
        if escalar:
            scaler = StandardScaler().fit(X_train)
            X_train, X_val = scaler.transform(X_train), scaler.transform(X_val)
        modelo = modelo_fn()
        modelo.fit(X_train, y[train_idx])
        s = modelo.predict_proba(X_val)[:, 1]
        por_fold.append({
            "pauc": float(pauc_above_tpr(y[val_idx], s)),
            "auc": float(roc_auc_score(y[val_idx], s)),
            "setop15": float(setop_n(y[val_idx], s, grupos[val_idx])),
            "nnt80": float(nnt_a_sensibilidad(y[val_idx], s)),
        })
    return por_fold


def resumen_nivel(por_semilla, semillas):
    """Por métrica: los valores por semilla y pliegue, la media de cada
    semilla y la media global."""
    out = {}
    for m in METRICAS:
        valores = {str(s): [round(f[m], 4) for f in por_semilla[s]] for s in semillas}
        medias = [float(np.mean([f[m] for f in por_semilla[s]])) for s in semillas]
        todos = [f[m] for s in semillas for f in por_semilla[s]]
        out[m] = {
            "por_semilla_y_fold": valores,
            "media_por_semilla": [round(v, 4) for v in medias],
            "media_global": round(float(np.mean(todos)), 4),
        }
    return out


def comparacion_2b_menos_1(res, semillas, n_splits):
    """Por métrica, las diferencias pareadas 2b − 1, una por (semilla,
    pliegue), con el intervalo corregido de Nadeau y Bengio, como en
    validacion-repetida.json. «Mejor» respeta la dirección de cada métrica."""
    out = {}
    for m in METRICAS:
        diffs = [b[m] - a[m] for s in semillas for a, b in zip(res["nivel_1"][s], res["nivel_2b"][s])]
        signo = 1 if MAYOR_ES_MEJOR[m] else -1
        por_semilla = [float(np.mean(diffs[i * n_splits:(i + 1) * n_splits])) for i in range(len(semillas))]
        ic = _nadeau_bengio(diffs, n_splits)
        out[m] = {
            "diferencias": [round(d, 4) for d in diffs],
            "n_diferencias": len(diffs),
            "media": round(float(np.mean(diffs)), 4),
            "intervalo_t_95_nadeau_bengio": ic,
            "intervalo_excluye_cero": bool(ic[0] > 0 or ic[1] < 0),
            "nivel_2b_mejor_en_pliegues": int(sum(1 for d in diffs if signo * d > 0)),
            "nivel_2b_mejor_en_semillas": int(sum(1 for d in por_semilla if signo * d > 0)),
            "de_pliegues": len(diffs),
            "de_semillas": len(semillas),
        }
    return out


def comprobar_control(res_paciente, referencia, semillas):
    """La partición por paciente tiene que reproducir validacion-repetida.json
    pliegue a pliegue en la pAUC. Devuelve el detalle; se detiene si no."""
    detalle = {}
    for nivel in NIVELES:
        clave = ETIQUETAS[nivel]
        esperado = referencia[clave]["pauc_por_semilla_y_fold"]
        obtenido = {str(s): [round(f["pauc"], 4) for f in res_paciente[nivel][s]] for s in semillas}
        distintos = [s for s in obtenido if obtenido[s] != esperado.get(s)]
        detalle[clave] = {"coincide": not distintos, "semillas_distintas": distintos}
        if distintos:
            raise SystemExit(
                f"CONTROL FALLIDO en {clave}: la partición por paciente no reproduce la referencia en las "
                f"semillas {distintos}. No se escribe nada.")
    return detalle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--referencia", default="outputs/validacion-repetida.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()

    if os.path.basename(args.out) in ("validacion-repetida", "modelado-baseline"):
        raise SystemExit(f"ERROR: efecto_particion.py no escribe outputs/{os.path.basename(args.out)}.")
    if not os.path.exists(args.referencia):
        raise SystemExit(f"ERROR: no existe {args.referencia}.")
    with open(args.referencia, encoding="utf-8") as f:
        referencia = json.load(f)
    if referencia.get("n_splits") != args.n_splits or sorted(map(int, referencia.get("semillas_corridas", []))) != sorted(args.semillas):
        raise SystemExit("ERROR: la referencia no tiene los mismos pliegues y semillas que se piden.")

    columnas_excluidas = cargar_columnas_excluidas(args.leakage_report)
    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    numericas, categoricas = preparar_features(df, columnas_excluidas, args.target_col, args.group_col)

    res = {}
    control = None
    for particion in PARTICIONES:
        res[particion] = {nivel: {} for nivel in NIVELES}
        for seed in args.semillas:
            folds = folds_de(particion, df, args.group_col, args.target_col, args.n_splits, seed)
            modelos = modelos_de(seed)
            for nivel in NIVELES:
                modelo_fn, escalar = modelos[nivel]
                res[particion][nivel][seed] = evaluar(df, args.target_col, args.group_col, folds,
                                                      numericas, categoricas, modelo_fn, escalar)
            print(f"{particion}, semilla {seed}: hecho", flush=True)
        if particion == "paciente":
            control = comprobar_control(res["paciente"], referencia, args.semillas)

    salida_particiones = {}
    for particion in PARTICIONES:
        salida_particiones[particion] = {
            **{ETIQUETAS[n]: resumen_nivel(res[particion][n], args.semillas) for n in NIVELES},
            "comparacion_2b_menos_1": comparacion_2b_menos_1(res[particion], args.semillas, args.n_splits),
        }

    filas_menos_paciente = {}
    for nivel in NIVELES:
        clave = ETIQUETAS[nivel]
        filas_menos_paciente[clave] = {}
        for m in METRICAS:
            mf = salida_particiones["filas"][clave][m]
            mp = salida_particiones["paciente"][clave][m]
            medias_f = [float(np.mean([f[m] for f in res["filas"][nivel][s]])) for s in args.semillas]
            medias_p = [float(np.mean([f[m] for f in res["paciente"][nivel][s]])) for s in args.semillas]
            signo = 1 if MAYOR_ES_MEJOR[m] else -1
            filas_menos_paciente[clave][m] = {
                "diferencia_de_medias": round(mf["media_global"] - mp["media_global"], 4),
                "semillas_filas_mayor": int(sum(1 for a, b in zip(medias_f, medias_p) if a > b)),
                "semillas_filas_mejor": int(sum(1 for a, b in zip(medias_f, medias_p) if signo * (a - b) > 0)),
                "de_semillas": len(args.semillas),
                "mayor_es_mejor": MAYOR_ES_MEJOR[m],
            }

    resultado = {
        "datos": datos,
        "esquema": {
            "group_col": args.group_col,
            "n_splits": args.n_splits,
            "semillas": list(args.semillas),
            "particiones": {
                "paciente": "construir_folds de train_and_evaluate.py: StratifiedGroupKFold por group_col, "
                            "shuffle, random_state = semilla",
                "filas": "StratifiedKFold, shuffle, random_state = semilla, sin agrupar",
            },
            "niveles": {ETIQUETAS[n]: n for n in NIVELES},
        },
        "referencia": args.referencia,
        "control_paciente_contra_referencia": control,
        "metricas": {
            "pauc": "pauc_above_tpr de train_and_evaluate.py (sobre 80% TPR)",
            "auc": "roc_auc_score",
            "setop15": "setop_n de metricas_triaje.py, con los pacientes del pliegue de validación",
            "nnt80": "nnt_a_sensibilidad de metricas_triaje.py; menos es mejor",
        },
        "particiones": salida_particiones,
        "filas_menos_paciente": filas_menos_paciente,
        "nota": (
            "semillas_filas_mayor cuenta las semillas en que la media por filas es numéricamente mayor; "
            "semillas_filas_mejor, aquellas en que es mejor según mayor_es_mejor (en el NNT80% SE, menor). "
            "Con la partición por filas, cada paciente tiene en validación solo una parte de sus lesiones, "
            "así que la sensibilidad top-15 no mide lo mismo en las dos particiones."
        ),
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    def fila(particion, clave):
        r = salida_particiones[particion][clave]
        return " · ".join(f"{m} {r[m]['media_global']}" for m in METRICAS)

    def dif(clave):
        d = filas_menos_paciente[clave]
        return " · ".join(f"{m} {d[m]['diferencia_de_medias']:+} (filas mejor en {d[m]['semillas_filas_mejor']}/"
                          f"{d[m]['de_semillas']})" for m in METRICAS)

    def comp(particion):
        c = salida_particiones[particion]["comparacion_2b_menos_1"]
        return " · ".join(f"{m} {c[m]['media']:+} {c[m]['intervalo_t_95_nadeau_bengio']}" for m in METRICAS)

    n1, n2b = ETIQUETAS["nivel_1"], ETIQUETAS["nivel_2b"]
    lineas = [
        f"# Efecto de la partición — {args.data}, conjunto de desarrollo",
        f"Niveles 1 y 2b, {args.n_splits} pliegues, semillas {args.semillas[0]}–{args.semillas[-1]}; "
        "por paciente (StratifiedGroupKFold) y por filas (StratifiedKFold)",
        f"Control: la partición por paciente reproduce {args.referencia} pliegue a pliegue en 1 y 2b",
        "Medias globales (pauc · auc · setop15 · nnt80):",
        f"  Nivel 1, por paciente: {fila('paciente', n1)}",
        f"  Nivel 1, por filas: {fila('filas', n1)}",
        f"  Nivel 2b, por paciente: {fila('paciente', n2b)}",
        f"  Nivel 2b, por filas: {fila('filas', n2b)}",
        f"Filas − paciente, nivel 1: {dif(n1)}",
        f"Filas − paciente, nivel 2b: {dif(n2b)}",
        f"2b − 1 por paciente, media e intervalo corregido: {comp('paciente')}",
        f"2b − 1 por filas, media e intervalo corregido: {comp('filas')}",
        "En el NNT80% SE menos es mejor. La sensibilidad top-15 no mide lo mismo en las dos particiones.",
        f"Detalle por semilla y pliegue: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
evaluar_repetido.py — validación cruzada repetida con varias semillas.

Repite la partición y evaluación de los niveles 1 (logística balanceada),
2a (HistGB sin ajustar) y 2b (HistGB balanceado) con varias semillas, para
separar qué tanto depende cada resultado de una asignación de folds
concreta frente a la variación semilla a semilla.

NO reimplementa nada verificado: importa de train_and_evaluate.py las
funciones ya contrastadas contra la fuente oficial —pauc_above_tpr,
construir_folds, codificar_fold, preparar_features, evaluar_modelo—.
Reimplementar la métrica es exactamente el error que ya se cometió una
vez (ver SKILL.md, "Sobre la métrica"); este script existe para correr
esas mismas funciones muchas veces, no para escribir otras nuevas.

REGLA DURA: este script nunca escribe outputs/modelado-baseline.json. Ese
archivo alimenta la demo, el borrador y la verificación de trazabilidad
ya existentes. La salida de este script es outputs/validacion-repetida.json
y outputs/validacion-repetida.md — archivos nuevos, independientes.

Uso:
    python evaluar_repetido.py --data data/train-metadata.csv \
                                --group-col patient_id \
                                --target-col target \
                                --n-splits 5 \
                                --leakage-report outputs/auditoria-de-fugas.json \
                                --out outputs/validacion-repetida \
                                --semillas 0 1 2 3 4 5 6 7 8 9
"""

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

# train_and_evaluate.py vive en el mismo directorio que este script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import (  # noqa: E402  (import tras el sys.path.insert, a propósito)
    construir_folds,
    codificar_fold,  # no se llama directo aquí: evaluar_modelo ya lo usa internamente.
    preparar_features,
    evaluar_modelo,
    pauc_above_tpr,  # idem: usada dentro de evaluar_modelo. Se importa para dejar constancia
                      # explícita de que este script no define su propia métrica.
)


# Nombres largos para que las claves de salida sean comparables a simple
# vista con outputs/modelado-baseline.json.
ETIQUETAS = {
    "nivel_1": "nivel_1_regresion_logistica",
    "nivel_2a": "nivel_2a_gradient_boosting_sin_balancear",
    "nivel_2b": "nivel_2b_gradient_boosting_balanceado",
}


def cargar_columnas_excluidas(leakage_report_path):
    """Misma regla que train_and_evaluate.py: sin el reporte de fugas, no
    hay columnas que excluir, y este script tampoco decide por su cuenta."""
    if not os.path.exists(leakage_report_path):
        print(
            f"ERROR: no existe {leakage_report_path}. Este script tampoco decide "
            f"qué columnas excluir por su cuenta — corre auditoria-de-fugas primero.",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(leakage_report_path, encoding="utf-8") as f:
        reporte_fugas = json.load(f)
    return (
        reporte_fugas.get("columnas_solo_en_train", [])
        + reporte_fugas.get("columnas_constantes", [])
        + reporte_fugas.get("columnas_identificador", [])
    )


def modelos_de(seed):
    """Misma definición que train_and_evaluate.py, nivel por nivel: nivel 1
    logística balanceada con escalado; nivel 2a HistGB sin ajustar; nivel 2b
    HistGB balanceado. Única diferencia entre 2a y 2b es class_weight.
    Devuelve {nivel: (constructor_del_modelo, necesita_escalar)}."""
    return {
        "nivel_1": (lambda: LogisticRegression(class_weight="balanced", max_iter=1000), True),
        "nivel_2a": (lambda: HistGradientBoostingClassifier(random_state=seed), False),
        "nivel_2b": (
            lambda: HistGradientBoostingClassifier(random_state=seed, class_weight="balanced"),
            False,
        ),
    }


def _nadeau_bengio(diffs, n_splits):
    """Corrección de Nadeau y Bengio (2003) sobre las diferencias pareadas
    ya calculadas en `diffs`. El intervalo t ingenuo trata esas n
    diferencias como independientes; no lo son, porque los conjuntos de
    entrenamiento se solapan entre folds de la misma semilla. La
    corrección ajusta la varianza multiplicándola por
    (1/n + n_test/n_train), con n_test/n_train = 1/(n_splits - 1) para
    k-fold. Mismo t de n-1 grados de libertad que el intervalo ingenuo."""
    n = len(diffs)
    media = float(np.mean(diffs))
    varianza = float(np.var(diffs, ddof=1))
    t_critico = float(stats.t.ppf(0.975, df=n - 1))
    razon_test_train = 1.0 / (n_splits - 1)
    varianza_corregida = varianza * (1.0 / n + razon_test_train)
    error_estandar_corregido = float(np.sqrt(varianza_corregida))
    return [
        round(media - t_critico * error_estandar_corregido, 4),
        round(media + t_critico * error_estandar_corregido, 4),
    ]


def _semillas_a_favor_de_2b(diffs, n_splits, semillas_corridas):
    """Cuenta en cuántas semillas la media de sus n_splits diferencias
    (2b − 1) fue positiva. Asume que `diffs` se construyó recorriendo
    semillas_corridas en orden y añadiendo n_splits valores por semilla
    —el mismo orden en que se arma esa lista más abajo—, así que el
    bloque i-ésimo de tamaño n_splits corresponde a la semilla i-ésima."""
    conteo = 0
    for i in range(len(semillas_corridas)):
        bloque = diffs[i * n_splits: (i + 1) * n_splits]
        if bloque and float(np.mean(bloque)) > 0:
            conteo += 1
    return conteo


def calcular_resultado(por_semilla, n_splits, semillas_corridas):
    """Reconstruye el bloque de salida completo a partir de lo acumulado
    hasta ahora. Se llama después de cada semilla, así que tiene que
    funcionar igual con 1 semilla que con 10."""
    resultado_niveles = {}

    for nivel, etiqueta in ETIQUETAS.items():
        pauc_por_semilla_y_fold = {
            str(seed): [round(float(p), 4) for p in por_semilla[seed][nivel]]
            for seed in semillas_corridas
        }
        todos = [p for seed in semillas_corridas for p in por_semilla[seed][nivel]]
        medias_por_semilla = [float(np.mean(por_semilla[seed][nivel])) for seed in semillas_corridas]

        resultado_niveles[etiqueta] = {
            "pauc_por_semilla_y_fold": pauc_por_semilla_y_fold,
            "pauc_media_global": round(float(np.mean(todos)), 4),
            "pauc_std_entre_folds": round(float(np.std(todos)), 4),
            "pauc_std_entre_semillas": round(float(np.std(medias_por_semilla)), 4),
        }

    # Comparación pareada 2b − 1: una diferencia por (semilla, fold), nunca
    # entre semillas ni folds distintos — cada par compara el mismo fold,
    # de la misma semilla, para los dos modelos.
    diffs = []
    for seed in semillas_corridas:
        p1 = por_semilla[seed]["nivel_1"]
        p2b = por_semilla[seed]["nivel_2b"]
        diffs.extend(float(b - a) for a, b in zip(p1, p2b))

    n = len(diffs)
    if n > 1:
        media_diff = float(np.mean(diffs))
        std_diff = float(np.std(diffs, ddof=1))
        error_estandar = float(std_diff / np.sqrt(n))
        t_critico = float(stats.t.ppf(0.975, df=n - 1))
        intervalo_t_95 = [
            round(float(media_diff - t_critico * error_estandar), 4),
            round(float(media_diff + t_critico * error_estandar), 4),
        ]
        # Corrección de Nadeau-Bengio: se calcula a partir de `diffs`
        # directamente (las diferencias reales), nunca de std_diff ya
        # redondeado.
        intervalo_t_95_nadeau_bengio = _nadeau_bengio(diffs, n_splits)
        media_diff = round(media_diff, 4)
        std_diff = round(std_diff, 4)
    elif n == 1:
        media_diff = round(float(diffs[0]), 4)
        std_diff = None
        intervalo_t_95 = None
        intervalo_t_95_nadeau_bengio = None
    else:
        media_diff = None
        std_diff = None
        intervalo_t_95 = None
        intervalo_t_95_nadeau_bengio = None

    gana_2b_en = sum(1 for d in diffs if d > 0)
    semillas_a_favor_de_2b = _semillas_a_favor_de_2b(diffs, n_splits, semillas_corridas)

    comparacion_pareada_2b_menos_1 = {
        "diferencias": [round(d, 4) for d in diffs],
        "n_diferencias": n,
        "media": media_diff,
        "desviacion": std_diff,
        "intervalo_t_95": intervalo_t_95,
        "intervalo_t_95_nadeau_bengio": intervalo_t_95_nadeau_bengio,
        "gana_2b_en": gana_2b_en,
        "de": n,
        "semillas_a_favor_de_2b": semillas_a_favor_de_2b,
    }

    return {
        "semillas_corridas": list(semillas_corridas),
        "n_splits": n_splits,
        **resultado_niveles,
        "comparacion_pareada_2b_menos_1": comparacion_pareada_2b_menos_1,
        "nota": (
            "Las diferencias fold a fold que alimentan comparacion_pareada_2b_menos_1 "
            "NO son independientes: los conjuntos de entrenamiento se solapan entre "
            "folds (cada fold deja fuera solo una fracción de los datos, el resto se "
            "comparte con los demás folds de la misma semilla), así que el intervalo t "
            "de arriba subestima la varianza real. Repetir con distintas semillas "
            "elimina la dependencia de una asignación concreta de folds, pero no "
            "elimina ese solape dentro de cada semilla. El intervalo_t_95 ingenuo "
            "supone que las 50 diferencias son independientes entre sí, supuesto que "
            "no se cumple por ese mismo solape; la corrección de Nadeau y Bengio "
            "(2003) ajusta la varianza para tenerlo en cuenta, y es "
            "intervalo_t_95_nadeau_bengio —más ancho— el que sostiene una conclusión "
            "defendible, no el ingenuo."
        ),
    }


def escribir_md(resultado, out_path):
    n1 = resultado["nivel_1_regresion_logistica"]
    n2a = resultado["nivel_2a_gradient_boosting_sin_balancear"]
    n2b = resultado["nivel_2b_gradient_boosting_balanceado"]
    comp = resultado["comparacion_pareada_2b_menos_1"]

    lineas = []
    lineas.append(f"# Validación repetida — {len(resultado['semillas_corridas'])} semillas")
    lineas.append("Métrica: pAUC sobre 80% TPR [0, 0.2], funciones de train_and_evaluate.py (no reimplementada)")
    lineas.append(f"Semillas corridas: {resultado['semillas_corridas']}")
    lineas.append(f"Folds por semilla: {resultado['n_splits']}")
    lineas.append(
        f"Nivel 1 (logística balanceada): media global {n1['pauc_media_global']} · "
        f"std entre folds {n1['pauc_std_entre_folds']} · std entre semillas {n1['pauc_std_entre_semillas']}"
    )
    lineas.append(
        f"Nivel 2a (GB sin balancear): media global {n2a['pauc_media_global']} · "
        f"std entre folds {n2a['pauc_std_entre_folds']} · std entre semillas {n2a['pauc_std_entre_semillas']}"
    )
    lineas.append(
        f"Nivel 2b (GB balanceado): media global {n2b['pauc_media_global']} · "
        f"std entre folds {n2b['pauc_std_entre_folds']} · std entre semillas {n2b['pauc_std_entre_semillas']}"
    )
    lineas.append(
        f"Comparación pareada 2b − 1 (n={comp['n_diferencias']}): media {comp['media']} · "
        f"desviación {comp['desviacion']} · intervalo t 95% ingenuo {comp['intervalo_t_95']} · "
        f"2b gana en {comp['gana_2b_en']}/{comp['de']} folds"
    )
    lineas.append(
        f"Corrección Nadeau-Bengio (2003), varianza ajustada por solape entre folds: "
        f"intervalo t 95% corregido {comp['intervalo_t_95_nadeau_bengio']} · "
        f"2b gana en {comp['semillas_a_favor_de_2b']}/{len(resultado['semillas_corridas'])} semillas"
    )
    lineas.append("Nota: el intervalo ingenuo subestima la varianza real — folds con entrenamientos solapados. Ver .json.")
    lineas.append("Detalle por semilla y fold: outputs/validacion-repetida.json")

    with open(f"{out_path}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def escribir_salida(resultado, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(f"{out_path}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    escribir_md(resultado, out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--semillas",
        type=int,
        nargs="+",
        default=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    args = ap.parse_args()

    columnas_excluidas = cargar_columnas_excluidas(args.leakage_report)

    df = pd.read_csv(args.data, low_memory=False)
    for col in (args.group_col, args.target_col):
        if col not in df.columns:
            print(f"ERROR: la columna '{col}' no existe en {args.data}", file=sys.stderr)
            sys.exit(1)

    numericas, categoricas = preparar_features(df, columnas_excluidas, args.target_col, args.group_col)

    por_semilla = {}
    semillas_corridas = []

    for seed in args.semillas:
        inicio = time.time()

        folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, seed)
        modelos = modelos_de(seed)

        resultados_seed = {}
        for nivel, (modelo_fn, escalar) in modelos.items():
            resultados_seed[nivel] = evaluar_modelo(
                df, args.target_col, folds, numericas, categoricas, modelo_fn, escalar=escalar
            )

        por_semilla[seed] = resultados_seed
        semillas_corridas.append(seed)

        # Se guarda después de CADA semilla, no al final: si esto se
        # interrumpe, el archivo en outputs/ refleja las semillas que
        # alcanzaron a correr, no nada.
        resultado = calcular_resultado(por_semilla, args.n_splits, semillas_corridas)
        escribir_salida(resultado, args.out)

        duracion = time.time() - inicio
        print(f"Semilla {seed}: {duracion:.1f}s — escrito {args.out}.json con {len(semillas_corridas)} semilla(s)")

    print(f"Terminado. Semillas corridas: {semillas_corridas}. Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

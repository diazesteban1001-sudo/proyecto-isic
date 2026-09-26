#!/usr/bin/env python3
"""
fase4_comparar.py — Fase 4: una comparación principal entre dos modelos
(PLAN.md), nuevo − base, con validación repetida.

  M1 = el nivel 2b actual: HistGradientBoostingClassifier(class_weight="balanced",
       random_state=semilla), con las variables de desarrollo de modelado-baseline.
  M2 = M1 más el contexto de paciente de contexto_paciente.py.
  M4 = M2 más las 384 variables de DINOv2 ViT-S/14 (token CLS) del conjunto de
       desarrollo, tal cual. Se leen con el cargador protegido
       (datos_desarrollo.cargar_caracteristicas_desarrollo), se alinean por
       isic_id y se comprueba la alineación y el hash del archivo.
  M4b = variante secundaria: M2 más dos variables de imagen apiladas, la
       puntuación de una logística balanceada sobre esas 384 variables y su
       razón a la media del paciente (apilado_imagen.py). Se calculan dentro de
       cada fold: fuera de pliegue en entrenamiento, con el modelo del fold en
       validación. Su control de fuga es test_apilado_imagen.py.
Todos con los mismos hiperparámetros, los de 2b, sin ajuste.

Validación repetida con las semillas dadas y los mismos folds de desarrollo que
outputs/validacion-repetida.json. Por modelo: pAUC, AUC, SEtop-15 y NNT80% SE en
cada (semilla, fold), y el tiempo de entrenamiento de cada fold. Para cada
métrica, nuevo − base pareado fold a fold, con intervalo t ingenuo y corregido
por Nadeau y Bengio y victorias por fold y por semilla. La principal es la del
pAUC; las otras tres, secundarias. En el NNT, menos es mejor, y las victorias se
cuentan en esa dirección.

NO reimplementa nada verificado: importa los folds, la codificación y el pAUC de
train_and_evaluate.py, la corrección de Nadeau y Bengio de evaluar_repetido.py,
las métricas de triaje de metricas_triaje.py y el contexto de contexto_paciente.py.
Con --referencia comprueba que el modelo base reproduce fold a fold el pAUC de
una corrida anterior: el nivel 2b de validacion-repetida.json, o el modelo del
mismo nombre de una salida anterior de este script.

Hasta el 2026-09-25 se llamaba fase4_m2_vs_m1.py y solo hacía M2 − M1.

No interpreta: mide y escribe --out.json y su .md.

Uso:
    python fase4_comparar.py --base M1 --nuevo M2 \
        --data data/train-metadata.csv --group-col patient_id --target-col target \
        --leakage-report outputs/auditoria-de-fugas.json \
        --referencia outputs/validacion-repetida.json \
        --out outputs/fase4-m2-vs-m1 --semillas 0 1 2 3 4 5 6 7 8 9

    python fase4_comparar.py --base M2 --nuevo M4 \
        --imagen data/dinov2-vits14-desarrollo.h5 \
        --extraccion outputs/extraccion-imagen.json \
        ... --referencia outputs/fase4-m2-vs-m1.json --out outputs/fase4-m4-vs-m2
"""

import argparse
import hashlib
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_and_evaluate import codificar_fold, construir_folds, pauc_above_tpr, preparar_features  # noqa: E402
from evaluar_repetido import _nadeau_bengio, _semillas_a_favor_de_2b, cargar_columnas_excluidas  # noqa: E402
from metricas_triaje import nnt_a_sensibilidad, setop_n  # noqa: E402
from contexto_paciente import variables_contexto_paciente  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_caracteristicas_desarrollo, cargar_desarrollo  # noqa: E402
from apilado_imagen import puntuaciones_imagen  # noqa: E402

# codificar_fold (train_and_evaluate.py, verificado) inserta las columnas de una en una;
# con cientos de columnas pandas avisa de fragmentación. Es rendimiento, no resultado.
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

METRICAS = {  # nombre: mayor es mejor
    "pauc": True,
    "auc": True,
    "setop15": True,
    "nnt80": False,
}
DESCRIPCION = {
    "M1": "nivel 2b actual",
    "M2": "M1 + contexto de paciente (contexto_paciente.py)",
    "M4": "M2 + las 384 variables de DINOv2 ViT-S/14 (token CLS), tal cual",
    "M4b": "M2 + 2 variables de imagen apiladas: puntuación de una logística balanceada sobre las 384 "
           "de DINOv2, fuera de pliegue, y su razón a la media del paciente (apilado_imagen.py)",
}
APILADAS = ["img_lr_puntuacion", "img_lr_razon_paciente"]


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


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
    del modelo nuevo por fold y por semilla, en la dirección de la métrica."""
    n = len(diffs)
    media = float(np.mean(diffs))
    desviacion = float(np.std(diffs, ddof=1))
    t = float(stats.t.ppf(0.975, df=n - 1))
    ee = desviacion / np.sqrt(n)
    a_favor = diffs if mayor_es_mejor else [-d for d in diffs]
    return {
        "diferencias_nuevo_menos_base": [round(d, 4) for d in diffs],
        "n_diferencias": n,
        "media": round(media, 4),
        "desviacion": round(desviacion, 4),
        "intervalo_t_95": [round(float(media - t * ee), 4), round(float(media + t * ee), 4)],
        "intervalo_t_95_nadeau_bengio": _nadeau_bengio(diffs, n_splits),
        "mayor_es_mejor": mayor_es_mejor,
        "nuevo_mejor_en_folds": sum(1 for d in a_favor if d > 0),
        "de_folds": n,
        "nuevo_mejor_en_semillas": _semillas_a_favor_de_2b(a_favor, n_splits, semillas),
        "de_semillas": len(semillas),
    }


def cargar_imagen(df, ruta_h5, ruta_csv, ruta_holdout, extraccion):
    """Lee las características de desarrollo con el cargador protegido, las
    alinea por isic_id con df y devuelve (DataFrame alineado, comprobaciones)."""
    ids, cls, decodificada = cargar_caracteristicas_desarrollo(ruta_h5, ruta_csv, ruta_holdout=ruta_holdout)
    columnas = [f"dinov2_{i:03d}" for i in range(cls.shape[1])]
    tabla = pd.DataFrame(cls, index=pd.Index(ids, name="isic_id"), columns=columnas)
    en_df, en_h5 = set(df["isic_id"]), set(ids)
    alineada = tabla.reindex(df["isic_id"].to_numpy())
    # Comprobación independiente de la alineación: unas filas al azar, buscadas
    # por su posición en el archivo, tienen que ser idénticas a las alineadas.
    posicion = {i: k for k, i in enumerate(ids)}
    rng = np.random.default_rng(0)
    muestra = rng.choice(len(df), size=min(1000, len(df)), replace=False)
    filas_iguales = all(np.array_equal(cls[posicion[df["isic_id"].iat[j]]], alineada.iloc[j].to_numpy()) for j in muestra)
    comprobaciones = {
        "archivo": ruta_h5,
        "sha256": sha256(ruta_h5),
        "isic_id_en_datos": len(en_df),
        "isic_id_en_archivo": len(en_h5),
        "en_datos_sin_caracteristicas": len(en_df - en_h5),
        "en_archivo_sin_fila_en_datos": len(en_h5 - en_df),
        "imagenes_no_decodificadas": int((~decodificada).sum()),
        "nan_tras_alinear": int(alineada.isna().to_numpy().sum()),
        "mismo_orden_que_los_datos": bool(list(ids) == df["isic_id"].tolist()),
        "filas_comprobadas_al_azar": int(len(muestra)),
        "filas_comprobadas_identicas": bool(filas_iguales),
    }
    if extraccion:
        with open(extraccion, encoding="utf-8") as f:
            esperado = json.load(f)["conjuntos"]["desarrollo"]["archivo"]["sha256"]
        comprobaciones["sha256_igual_al_de_la_extraccion"] = comprobaciones["sha256"] == esperado
    fallos = [k for k in ("en_datos_sin_caracteristicas", "en_archivo_sin_fila_en_datos",
                          "imagenes_no_decodificadas", "nan_tras_alinear") if comprobaciones[k]]
    if fallos or not filas_iguales or comprobaciones.get("sha256_igual_al_de_la_extraccion") is False:
        raise SystemExit(f"ERROR: las características de imagen no se alinean con los datos: {comprobaciones}")
    return alineada.set_index(df.index), comprobaciones


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, choices=sorted(DESCRIPCION))
    ap.add_argument("--nuevo", required=True, choices=sorted(DESCRIPCION))
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--imagen", default=None, help="características de desarrollo, para M4")
    ap.add_argument("--extraccion", default=None, help="outputs/extraccion-imagen.json, para comprobar el hash")
    ap.add_argument("--referencia", default=None)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()
    if {"M4", "M4b"} & {args.base, args.nuevo} and not args.imagen:
        raise SystemExit("ERROR: M4 y M4b necesitan --imagen.")

    t_total = time.perf_counter()
    excluidas = cargar_columnas_excluidas(args.leakage_report)
    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    numericas, categoricas = preparar_features(df, excluidas, args.target_col, args.group_col)

    t0 = time.perf_counter()
    contexto = variables_contexto_paciente(df.drop(columns=[args.target_col]), numericas, args.group_col)
    t_contexto = time.perf_counter() - t0
    extra = [contexto]
    imagen, comprobacion_imagen, t_imagen = None, None, None
    if args.imagen:
        t0 = time.perf_counter()
        imagen, comprobacion_imagen = cargar_imagen(df, args.imagen, args.data, args.holdout, args.extraccion)
        t_imagen = time.perf_counter() - t0
        extra.append(imagen)
    df = pd.concat([df, *extra], axis=1)
    variables = {
        "M1": numericas,
        "M2": numericas + list(contexto.columns),
        "M4": numericas + list(contexto.columns) + (list(imagen.columns) if imagen is not None else []),
        "M4b": numericas + list(contexto.columns) + APILADAS,
    }
    x_imagen = imagen.to_numpy() if imagen is not None else None
    avisos_apilado, t_apilado = {}, {}
    modelos = {m: variables[m] for m in (args.base, args.nuevo)}

    y = df[args.target_col].to_numpy()
    grupos = df[args.group_col].to_numpy()
    semillas = list(args.semillas)
    por = {m: {k: {} for k in METRICAS} for m in modelos}
    t_fit = {m: {} for m in modelos}
    huellas, t_semilla = {}, {}
    for seed in semillas:
        inicio = time.perf_counter()
        folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, seed)
        huellas[str(seed)] = huella_folds(folds, len(df))
        for m, num in modelos.items():
            valores, tiempos = {k: [] for k in METRICAS}, []
            for tr, va in folds:
                if m == "M4b":
                    # Las variables apiladas dependen de las etiquetas: se rehacen en cada fold.
                    t0 = time.perf_counter()
                    ap = puntuaciones_imagen(x_imagen, y, grupos, tr, va, seed)
                    for col, clave in zip(APILADAS, ("puntuacion", "razon")):
                        valores_col = np.full(len(df), np.nan)
                        valores_col[tr] = ap["tr"][clave]
                        valores_col[va] = ap["va"][clave]
                        df[col] = valores_col
                    avisos_apilado.setdefault(str(seed), []).append(ap["avisos_no_convergencia"])
                    t_apilado.setdefault(str(seed), []).append(round(time.perf_counter() - t0, 2))
                x_tr, x_va = codificar_fold(df, num, categoricas, args.target_col, tr, va)
                modelo = HistGradientBoostingClassifier(random_state=seed, class_weight="balanced")
                t0 = time.perf_counter()
                modelo.fit(x_tr, y[tr])
                tiempos.append(round(time.perf_counter() - t0, 2))
                s = modelo.predict_proba(x_va)[:, 1]
                for k, v in medir(y[va], s, grupos[va]).items():
                    valores[k].append(v)
            for k in METRICAS:
                por[m][k][str(seed)] = valores[k]
            t_fit[m][str(seed)] = tiempos
        t_semilla[str(seed)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {seed}: {t_semilla[str(seed)]} s", flush=True)

    reproduccion = None
    if args.referencia:
        with open(args.referencia, encoding="utf-8") as f:
            ref = json.load(f)
        if "nivel_2b_gradient_boosting_balanceado" in ref and args.base == "M1":
            esperado = ref["nivel_2b_gradient_boosting_balanceado"]["pauc_por_semilla_y_fold"]
            que = "el nivel 2b"
        else:
            esperado = ref["metricas"][args.base]["pauc"]["por_semilla_y_fold"]
            que = f"{args.base}"
        discrepancias = [s for s in semillas
                         if [round(v, 4) for v in por[args.base]["pauc"][str(s)]] != esperado.get(str(s))]
        reproduccion = {"referencia": args.referencia, "que_se_compara": f"{args.base} frente a {que} de la referencia",
                        "reproduce_fold_a_fold": not discrepancias, "semillas_con_discrepancia": discrepancias}

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
        diffs = [float(b - a) for s in semillas
                 for a, b in zip(por[args.base][k][str(s)], por[args.nuevo][k][str(s)])]
        comparaciones[k] = {**comparacion(diffs, args.n_splits, semillas, mayor),
                            "papel": "principal" if k == "pauc" else "secundaria"}

    def resumen_tiempo(m):
        todos = [t for s in semillas for t in t_fit[m][str(s)]]
        return {"por_semilla_y_fold": t_fit[m], "mediana": round(float(np.median(todos)), 2),
                "media": round(float(np.mean(todos)), 2), "minimo": min(todos), "maximo": max(todos)}

    resultado = {
        "datos": datos,
        "comparacion": {"nuevo": args.nuevo, "base": args.base},
        "semillas_corridas": semillas,
        "n_splits": args.n_splits,
        "modelos": {m: {"descripcion": DESCRIPCION[m], "n_variables": len(num) + len(categoricas)}
                    for m, num in modelos.items()},
        "variables_de_contexto": list(contexto.columns),
        "caracteristicas_de_imagen": comprobacion_imagen,
        "hiperparametros": "los del nivel 2b: HistGradientBoostingClassifier(class_weight='balanced', "
                           "random_state=semilla), el resto por defecto; sin ajuste",
        "folds": {"sha256_por_semilla": huellas,
                  "como_se_construyen": "construir_folds de train_and_evaluate.py, los mismos de validacion-repetida"},
        "reproduccion_del_base": reproduccion,
        "metricas": {m: {k: resumen(m, k) for k in METRICAS} for m in modelos},
        "comparaciones_nuevo_menos_base": comparaciones,
        "segundos_de_entrenamiento_por_fold": {m: resumen_tiempo(m) for m in modelos},
        **({"apilado_imagen": {
            "logistica": "pipeline StandardScaler + LogisticRegression(class_weight='balanced', max_iter=2000), C por defecto",
            "validacion_interna": "StratifiedGroupKFold(5, shuffle=True, random_state=semilla externa), por patient_id",
            "avisos_no_convergencia_por_semilla_y_fold": avisos_apilado,
            "avisos_no_convergencia_total": int(sum(sum(v) for v in avisos_apilado.values())),
            "segundos_por_fold": t_apilado,
            "nota": "6 logísticas por fold: 5 de la validación interna y 1 sobre todo el fold de entrenamiento.",
        }} if avisos_apilado else {}),
        "segundos": {"contexto_de_paciente": round(t_contexto, 1),
                     "carga_de_caracteristicas_de_imagen": round(t_imagen, 1) if t_imagen is not None else None,
                     "por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
        "nota": (
            "Las diferencias fold a fold no son independientes: los entrenamientos se solapan. "
            "El intervalo corregido por Nadeau y Bengio tiene en cuenta ese solape; el ingenuo, no. "
            "En el NNT80% SE menos es mejor: las victorias del modelo nuevo cuentan las diferencias "
            "negativas. El tiempo de entrenamiento es el de fit, sin codificación ni predicción."
        ),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    b, n = args.base, args.nuevo
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    lineas = [
        f"# Fase 4 — {n} − {b}, {len(semillas)} semillas × {args.n_splits} folds, conjunto de desarrollo",
        " · ".join(f"{m} = {DESCRIPCION[m]} ({resultado['modelos'][m]['n_variables']} variables)" for m in (b, n))
        + " · hiperparámetros de 2b",
    ]
    if reproduccion:
        lineas.append(f"{reproduccion['que_se_compara']} ({args.referencia}), fold a fold: {reproduccion['reproduce_fold_a_fold']}")
    if comprobacion_imagen:
        lineas.append(
            f"Imagen: {comprobacion_imagen['isic_id_en_archivo']} filas alineadas por isic_id, sin faltantes · "
            f"hash igual al de la extracción: {comprobacion_imagen.get('sha256_igual_al_de_la_extraccion')}"
        )
    lineas.append(" · ".join(f"{nombres[k]}: {b} {resultado['metricas'][b][k]['media_global']}, "
                             f"{n} {resultado['metricas'][n][k]['media_global']}" for k in METRICAS))
    for k in METRICAS:
        c = comparaciones[k]
        lineas.append(
            f"{n} − {b}, {nombres[k]} ({c['papel']}): media {c['media']} · ingenuo {c['intervalo_t_95']} · "
            f"corregido {c['intervalo_t_95_nadeau_bengio']} · {n} mejor en {c['nuevo_mejor_en_folds']}/{c['de_folds']} "
            f"folds y {c['nuevo_mejor_en_semillas']}/{c['de_semillas']} semillas"
        )
    if avisos_apilado:
        a = resultado["apilado_imagen"]
        todos = [s for v in t_apilado.values() for s in v]
        lineas.append(f"Apilado de imagen: {a['avisos_no_convergencia_total']} avisos de no convergencia · "
                      f"{float(np.median(todos))} s por fold de mediana (6 logísticas)")
    tf = resultado["segundos_de_entrenamiento_por_fold"]
    lineas.append("Entrenamiento por fold (fit), mediana: " + " · ".join(f"{m} {tf[m]['mediana']} s" for m in (b, n)))
    lineas.append("En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.")
    lineas.append(f"Detalle por semilla y fold: {args.out}.json")
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

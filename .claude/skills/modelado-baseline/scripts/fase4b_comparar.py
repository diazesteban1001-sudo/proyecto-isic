#!/usr/bin/env python3
"""
fase4b_comparar.py — Fase 4b (PLAN.md, decisión de la persona del 2026-10-22): un
candidato contra M3 limpio, candidato − M3 limpio, con validación repetida y los
pliegues de la Fase 4 (construir_folds, 5 pliegues, semillas 0 a 9).

  C1 = fase4b.rango_promedio(M3 limpio, M2), sobre las predicciones que guardaron
       los controles (test_fase4b_controles.py) en
       data/fase4b-predicciones-m3limpio-m2.csv.gz. Se leen con
       float_precision="round_trip" y, antes de usarlas, se comprueban el SHA-256
       del archivo, la huella de las puntuaciones en float64 y que los controles
       reprodujeron la Fase 4 con ellas.
  C2 = M3 limpio más las dos variables de imagen de M4b (fase4b.con_imagen),
       ajustado con la parada y el remuestreo de M3 limpio. En cada pliegue se
       comprueba la alineación: las dos columnas son las de puntuaciones_imagen
       fila a fila, la razón sale de la puntuación con los grupos de esas filas, y
       tras el remuestreo cada fila lleva los valores de su fila de origen. Si
       falla en un pliegue, el guion se detiene.
  C3 = fase4b.rango_promedio(M3 limpio, nivel 2b), con el nivel 2b de
       fase4b.ajustar_nivel_2b sobre las variables de M3 limpio de cada pliegue;
       ese ajuste se detiene si el modelo trata alguna variable como categórica.

La base, M3 limpio, son en los tres casos sus puntuaciones guardadas, con las
mismas comprobaciones que C1; en cada pliegue, sus isic_id tienen que ser los de
la validación de construir_folds, en el mismo orden.

Por métrica (pAUC, AUC, SEtop-15 y NNT80% SE): candidato − M3 limpio, pareado
pliegue a pliegue, con la función de fase4_comparar.py (intervalo t ingenuo,
corregido por Nadeau y Bengio al 95 % y victorias por pliegue y por semilla) y,
para la regla de PLAN.md, el intervalo corregido por Nadeau y Bengio con la
confianza de Bonferroni, 1 − 0,05/3. En el NNT, menos es mejor.

No aplica la regla ni interpreta: mide y escribe --out.json y su .md.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4b_comparar.py \\
        --candidato C1 --out outputs/fase4b-c1-vs-m3limpio
(lo mismo con C2 y C3).
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

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import ganador_m3  # noqa: E402
from apilado_imagen import puntuaciones_imagen  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import _nadeau_bengio, cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
H5 = os.path.join(RAIZ, "data", "dinov2-vits14-desarrollo.h5")
EXTRACCION = os.path.join(RAIZ, "outputs", "extraccion-imagen.json")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
PREDICCIONES = os.path.join(RAIZ, "data", "fase4b-predicciones-m3limpio-m2.csv.gz")
REFERENCIA = os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json")
G, Y = "patient_id", "target"
N_CANDIDATOS = 3
CONFIANZA_BONFERRONI = 1 - 0.05 / N_CANDIDATOS
DESCRIPCION = {
    "M3limpio": f4.DESCRIPCION["M3limpio"],
    "C1": "promedio simple de los rangos de M3 limpio y M2, pesos 1/2 y 1/2, empates con el rango promedio "
          "(fase4b.rango_promedio), sobre sus predicciones guardadas",
    "C2": "M3 limpio más las dos variables de imagen de M4b (apilado_imagen.puntuaciones_imagen), calculadas sobre "
          "todo el pliegue de entrenamiento antes del remuestreo; todo lo demás de M3 limpio, igual (fase4b.con_imagen)",
    "C3": "promedio simple de los rangos de M3 limpio y del nivel 2b sin cambios sobre las variables de M3 limpio de "
          "cada pliegue, con las one-hot como números y sin remuestreo (fase4b.ajustar_nivel_2b)",
}


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def nadeau_bengio(diffs, n_splits, confianza):
    """El intervalo de evaluar_repetido._nadeau_bengio con otra confianza: la misma
    varianza corregida por (1/n + 1/(n_splits − 1)) y el t de n − 1 grados de libertad
    en el cuantil 1 − (1 − confianza)/2."""
    n = len(diffs)
    media = float(np.mean(diffs))
    varianza = float(np.var(diffs, ddof=1))
    t = float(stats.t.ppf(1 - (1 - confianza) / 2, df=n - 1))
    ee = float(np.sqrt(varianza * (1.0 / n + 1.0 / (n_splits - 1))))
    return [round(media - t * ee, 4), round(media + t * ee, 4)]


def cargar_predicciones(ruta):
    """Las predicciones guardadas por los controles, comprobadas. Devuelve
    {(modelo, semilla, pliegue): (isic_id, puntuacion)} y su procedencia."""
    ruta_json = os.path.splitext(os.path.splitext(ruta)[0])[0] + ".json"
    with open(ruta_json, encoding="utf-8") as f:
        procedencia = json.load(f)
    if sha256(ruta) != procedencia["sha256"]:
        raise SystemExit(f"ERROR: {ruta} no tiene el SHA-256 de su procedencia.")
    if not all(procedencia["reproducen_fase4"].values()):
        raise SystemExit(f"ERROR: los controles no reprodujeron la Fase 4 con {ruta}: {procedencia['reproducen_fase4']}")
    tabla = pd.read_csv(ruta, float_precision="round_trip")
    huella = hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes()).hexdigest()
    if huella != procedencia["sha256_de_las_puntuaciones_float64"]:
        raise SystemExit(f"ERROR: las puntuaciones leídas de {ruta} no tienen la huella de su procedencia.")
    por = {}
    for (m, s, i), bloque in tabla.groupby(["modelo", "semilla", "pliegue"], sort=False):
        por[(m, int(s), int(i))] = (bloque["isic_id"].to_numpy(), bloque["puntuacion"].to_numpy(np.float64))
    return por, procedencia


def guardada(predicciones, modelo, semilla, i, isic_va):
    ids, s = predicciones[(modelo, semilla, i)]
    if not np.array_equal(ids, isic_va):
        raise SystemExit(f"ERROR: las predicciones de {modelo}, semilla {semilla}, pliegue {i}, no están en el orden "
                         "de la validación de construir_folds.")
    return s


def comprobar_alineacion(x_tr, xc_tr, ap, semilla, y_tr, grupos_tr):
    """La de test_fase4b_controles.py (caso M), en cada pliegue de C2."""
    cols = fase4b.COLUMNAS_IMAGEN
    antes = (np.array_equal(xc_tr[cols[0]].to_numpy(), ap["tr"]["puntuacion"])
             and np.array_equal(xc_tr[cols[1]].to_numpy(), ap["tr"]["razon"])
             and list(xc_tr.columns[:-2]) == list(x_tr.columns))
    p = pd.Series(xc_tr[cols[0]].to_numpy())
    razon = np.allclose(xc_tr[cols[1]].to_numpy(), (p / p.groupby(grupos_tr).transform("mean")).to_numpy(),
                        rtol=0, atol=1e-12)
    interna = ganador_m3.StratifiedGroupKFold(n_splits=ganador_m3.PLIEGUES_INTERNOS, shuffle=True,
                                              random_state=semilla)
    itr, _ = next(interna.split(xc_tr, y_tr, groups=grupos_tr))
    marcada = xc_tr.iloc[itr].copy()
    marcada["_fila"] = np.arange(len(marcada))
    xr, _ = ganador_m3.remuestrear(marcada, y_tr[itr], semilla)
    origen = marcada.iloc[xr["_fila"].to_numpy()]
    despues = all(np.array_equal(xr[c].to_numpy(), origen[c].to_numpy()) for c in cols)
    return {"antes": bool(antes), "razon": bool(razon), "despues": bool(despues), "filas_remuestreadas": int(len(xr))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidato", required=True, choices=["C1", "C2", "C3"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--predicciones", default=PREDICCIONES)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--n-splits", type=int, default=5)
    args = ap.parse_args()
    t_total = time.perf_counter()
    c = args.candidato

    predicciones, procedencia = cargar_predicciones(args.predicciones)
    excluidas = cargar_columnas_excluidas(FUGAS)
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    df_sin_etiqueta = df.drop(columns=[Y])
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    x_imagen, comprobacion_imagen = None, None
    if c == "C2":
        imagen, comprobacion_imagen = f4.cargar_imagen(df, H5, CSV, RUTA_HOLDOUT, EXTRACCION)
        x_imagen = imagen.to_numpy()
    with open(REFERENCIA, encoding="utf-8") as f:
        referencia = json.load(f)

    modelos = ("M3limpio", c)
    por = {m: {k: {} for k in f4.METRICAS} for m in modelos}
    t_fit, bloque, huellas, t_semilla = {}, {}, {}, {}
    for semilla in args.semillas:
        inicio = time.perf_counter()
        folds = construir_folds(df, G, Y, args.n_splits, semilla)
        huellas[str(semilla)] = f4.huella_folds(folds, len(df))
        if huellas[str(semilla)] != referencia["folds"]["sha256_por_semilla"][str(semilla)]:
            raise SystemExit(f"ERROR: los pliegues de la semilla {semilla} no son los de {REFERENCIA}.")
        valores = {m: {k: [] for k in f4.METRICAS} for m in modelos}
        tiempos = []
        for i, (tr, va) in enumerate(folds):
            base = guardada(predicciones, "M3limpio", semilla, i, isic[va])
            t0 = time.perf_counter()
            if c == "C1":
                s = fase4b.rango_promedio(base, guardada(predicciones, "M2", semilla, i, isic[va]))
            else:
                x_tr, x_va, cats, inv = ganador_m3.variables_m3_en_pliegue(df_sin_etiqueta, tr, va, excluidas, G)
                if c == "C2":
                    t1 = time.perf_counter()
                    a = puntuaciones_imagen(x_imagen, y, grupos, tr, va, semilla)
                    t_apilado = round(time.perf_counter() - t1, 2)
                    xc_tr, xc_va = fase4b.con_imagen(x_tr, x_va, a)
                    alin = comprobar_alineacion(x_tr, xc_tr, a, semilla, y[tr], grupos[tr])
                    if not all(alin[k] for k in ("antes", "razon", "despues")):
                        raise SystemExit(f"ERROR: alineación de C2, semilla {semilla}, pliegue {i}: {alin}")
                    t1 = time.perf_counter()
                    modelo = ganador_m3.ajustar_m3(xc_tr, y[tr], grupos[tr], cats, semilla,
                                                   parametros=ganador_m3.PARAMETROS_LIMPIO)
                    t_ajuste = round(time.perf_counter() - t1, 2)
                    s = modelo.predict_proba(xc_va)[:, 1]
                    bloque.setdefault(str(semilla), []).append({
                        "n_variables": int(xc_tr.shape[1]), "alineacion": alin, "segundos_apilado": t_apilado,
                        "segundos_ajuste": t_ajuste, "avisos_no_convergencia": a["avisos_no_convergencia"],
                        "arboles": int(modelo.tree_count_),
                        "iteraciones_corridas": len(modelo.get_evals_result()["validation"]["AUC"])})
                else:
                    t1 = time.perf_counter()
                    segundo = fase4b.ajustar_nivel_2b(x_tr, y[tr], semilla)  # se detiene si hay categóricas
                    t_ajuste = round(time.perf_counter() - t1, 2)
                    s = fase4b.rango_promedio(base, fase4b.puntuar_nivel_2b(segundo, x_va))
                    bloque.setdefault(str(semilla), []).append({
                        "n_variables": int(x_tr.shape[1]), "n_one_hot_como_numeros": len(cats),
                        "categoricas_para_el_modelo": 0 if segundo.is_categorical_ is None
                        else int(np.sum(segundo.is_categorical_)),
                        "iteraciones_del_nivel_2b": int(segundo.n_iter_), "segundos_ajuste": t_ajuste})
            tiempos.append(round(time.perf_counter() - t0, 2))
            for m, sc in (("M3limpio", base), (c, s)):
                for k, v in f4.medir(y[va], sc, grupos[va]).items():
                    valores[m][k].append(v)
        for m in modelos:
            for k in f4.METRICAS:
                por[m][k][str(semilla)] = valores[m][k]
        t_fit[str(semilla)] = tiempos
        t_semilla[str(semilla)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {semilla}: {t_semilla[str(semilla)]} s", flush=True)

    # La base reproduce la Fase 4 pliegue a pliegue en las cuatro métricas.
    discrepancias = [(k, s_) for k in f4.METRICAS for s_ in args.semillas
                     if [round(v, 4) for v in por["M3limpio"][k][str(s_)]]
                     != referencia["metricas"]["M3limpio"][k]["por_semilla_y_fold"][str(s_)]]
    if discrepancias:
        raise SystemExit(f"ERROR: M3 limpio no reproduce {REFERENCIA}: {discrepancias}")

    def resumen(m, k):
        todos = [v for s_ in args.semillas for v in por[m][k][str(s_)]]
        medias = [float(np.mean(por[m][k][str(s_)])) for s_ in args.semillas]
        return {"por_semilla_y_fold": {str(s_): [round(v, 4) for v in por[m][k][str(s_)]] for s_ in args.semillas},
                "media_global": round(float(np.mean(todos)), 4), "std_entre_folds": round(float(np.std(todos)), 4),
                "std_entre_semillas": round(float(np.std(medias)), 4)}

    comparaciones = {}
    for k, mayor in f4.METRICAS.items():
        diffs = [float(b - a) for s_ in args.semillas for a, b in zip(por["M3limpio"][k][str(s_)], por[c][k][str(s_)])]
        comp = f4.comparacion(diffs, args.n_splits, args.semillas, mayor)
        if nadeau_bengio(diffs, args.n_splits, 0.95) != _nadeau_bengio(diffs, args.n_splits):
            raise SystemExit("ERROR: nadeau_bengio al 95 % no coincide con el de evaluar_repetido.py.")
        comp["intervalo_bonferroni_nadeau_bengio"] = nadeau_bengio(diffs, args.n_splits, CONFIANZA_BONFERRONI)
        comp["confianza_bonferroni"] = round(CONFIANZA_BONFERRONI, 6)
        comp["papel"] = "principal" if k == "pauc" else "secundaria"
        comparaciones[k] = comp

    todos_t = [t for s_ in args.semillas for t in t_fit[str(s_)]]
    resultado = {
        "datos": datos,
        "comparacion": {"nuevo": c, "base": "M3limpio"},
        "semillas_corridas": args.semillas,
        "n_splits": args.n_splits,
        "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in modelos},
        "caracteristicas_de_imagen": comprobacion_imagen,
        "hiperparametros": "M3 limpio: los de la Fase 4 (ganador_m3.PARAMETROS_LIMPIO). C3, segundo modelo: "
                           "HistGradientBoostingClassifier(class_weight='balanced', random_state=semilla), el resto "
                           "por defecto. Sin ajuste.",
        "folds": {"sha256_por_semilla": huellas, "iguales_a": os.path.relpath(REFERENCIA, RAIZ)},
        "reproduccion_del_base": {"referencia": os.path.relpath(REFERENCIA, RAIZ),
                                  "que_se_compara": "las cuatro métricas de M3 limpio, pliegue a pliegue",
                                  "reproduce_fold_a_fold": True},
        "predicciones_guardadas": {"archivo": os.path.relpath(args.predicciones, RAIZ),
                                   "sha256": procedencia["sha256"],
                                   "huella_de_las_puntuaciones": procedencia["sha256_de_las_puntuaciones_float64"],
                                   "usadas_para": "M3 limpio" + (" y M2" if c == "C1" else "")},
        "metricas": {m: {k: resumen(m, k) for k in f4.METRICAS} for m in modelos},
        "comparaciones_nuevo_menos_base": comparaciones,
        "segundos_por_fold": {"por_semilla_y_fold": t_fit, "mediana": round(float(np.median(todos_t)), 2),
                              "media": round(float(np.mean(todos_t)), 2)},
        c.lower(): {"por_semilla_y_fold": bloque} if bloque else {"pesos": [0.5, 0.5],
                                                                  "empates": "rankdata(method='average')"},
        "segundos": {"por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
        "nota": "Candidato − M3 limpio, pareado pliegue a pliegue. intervalo_bonferroni_nadeau_bengio: el corregido "
                f"por Nadeau y Bengio con confianza 1 − 0,05/{N_CANDIDATOS}, el de la regla de PLAN.md, Fase 4b. En el "
                "NNT80% SE menos es mejor, y las victorias se cuentan en esa dirección. No aplica la regla ni "
                "interpreta.",
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    lineas = [f"# Fase 4b: {c} − M3 limpio", "",
              f"Conjunto de desarrollo, semillas {args.semillas[0]} a {args.semillas[-1]} × {args.n_splits} pliegues; "
              "M3 limpio reproduce la Fase 4.", ""]
    for k, comp in comparaciones.items():
        lineas.append(f"- {nombres[k]}: {c} {resultado['metricas'][c][k]['media_global']}, M3 limpio "
                      f"{resultado['metricas']['M3limpio'][k]['media_global']}; diferencia {comp['media']}, "
                      f"NB 95 % {comp['intervalo_t_95_nadeau_bengio']}, Bonferroni "
                      f"{comp['intervalo_bonferroni_nadeau_bengio']}; mejor en {comp['nuevo_mejor_en_folds']} de "
                      f"{comp['de_folds']} pliegues y {comp['nuevo_mejor_en_semillas']} de {comp['de_semillas']} semillas")
    lineas += ["", f"Tiempo por pliegue: mediana {resultado['segundos_por_fold']['mediana']} s; total "
                   f"{resultado['segundos']['total']} s.", "", "No aplica la regla ni interpreta."]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md")


if __name__ == "__main__":
    main()

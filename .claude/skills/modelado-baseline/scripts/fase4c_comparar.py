#!/usr/bin/env python3
"""
fase4c_comparar.py — Fase 4c (PLAN.md, decisión de la persona del 2026-10-22):
las dos preguntas, y el control del atajo, sobre las puntuaciones que guardó
fase4c_redes.py. Validación repetida con los pliegues de la Fase 4
(construir_folds, 5 pliegues, semillas 0 a 9).

  --pregunta 1: «Red sola» − «Imagen». La red sola es la puntuación de la red en
       el pliegue de validación. «Imagen» son las métricas por pliegue de
       outputs/imagen-sola.json, guardadas a 4 decimales; antes se comprueba que
       los pliegues tienen la huella de outputs/fase4-m2-vs-m1.json, la misma con
       que imagen_sola.py comprobó los suyos.
  --pregunta 2: C4 − M3 limpio. C4 es M3 limpio más las dos variables de la red
       (fase4c.variables_red, con fase4b.con_imagen: las columnas llevan los
       nombres de C2, img_lr_puntuacion e img_lr_razon_paciente, pero salen de la
       red), calculadas antes del remuestreo y ajustadas con la parada y el
       remuestreo de M3 limpio. En las filas de entrenamiento, la puntuación sale
       de las redes de los otros pliegues: el atajo declarado en PLAN.md. En cada
       pliegue se comprueba la alineación de C2
       (fase4b_comparar.comprobar_alineacion) y, si falla, se detiene. M3 limpio
       son sus predicciones guardadas de la Fase 4b, con sus comprobaciones, y
       tiene que reproducir outputs/fase4-m3limpio-vs-m2.json.
  --atajo: el control del atajo, descriptivo. En la semilla 0, C4 con las
       puntuaciones de la validación interna de M4b en las filas de
       entrenamiento (fase4c_redes.py --internos), frente a C4 con el atajo,
       recalculado y comprobado contra outputs/fase4c-c4-vs-m3limpio.json; la
       diferencia de pAUC por pliegue.

Por métrica (pAUC, AUC, SEtop-15 y NNT80% SE): la diferencia pareada pliegue a
pliegue, con fase4_comparar.comparacion (intervalo t ingenuo, corregido por
Nadeau y Bengio al 95 % y victorias) y, para la regla, el corregido por Nadeau y
Bengio con la confianza de Bonferroni, 1 − 0,05/2. En el NNT, menos es mejor.

Antes de usar las puntuaciones de la red se comprueban el SHA-256 del archivo,
la huella de las puntuaciones en float64, que la probabilidad es la sigmoide del
logit guardado, la alineación registrada por semilla y que los controles
completos tuvieron 0 fallos.

No aplica la regla ni interpreta: mide y escribe --out.json y su .md.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4c_comparar.py \\
        --pregunta 1 --out outputs/fase4c-red-sola-vs-imagen
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4c_comparar.py \\
        --pregunta 2 --out outputs/fase4c-c4-vs-m3limpio
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4c_comparar.py \\
        --atajo --out outputs/fase4c-control-atajo
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

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import _nadeau_bengio, cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
RED = os.path.join(RAIZ, "data", "fase4c-puntuaciones-red.csv.gz")
RED_INTERNAS = os.path.join(RAIZ, "data", "fase4c-puntuaciones-red-internas.csv.gz")
IMAGEN_SOLA = os.path.join(RAIZ, "outputs", "imagen-sola.json")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
REF_M3L = os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json")
SALIDA_C4 = os.path.join(RAIZ, "outputs", "fase4c-c4-vs-m3limpio.json")
G, Y = "patient_id", "target"
N_PREGUNTAS = 2
CONFIANZA_BONFERRONI = 1 - 0.05 / N_PREGUNTAS
DESCRIPCION = {
    "Red": "EfficientNet-B0 de torchvision con los pesos de ImageNet, entrenada de punta a punta en el pliegue de "
           "entrenamiento (fase4c.entrenar_y_puntuar); su probabilidad, la sigmoide del logit en float64",
    "Imagen": "«Imagen» de outputs/imagen-sola.json: modelo_imagen() de apilado_imagen.py sobre las 384 variables de "
              "DINOv2, métricas por pliegue a 4 decimales",
    "M3limpio": f4.DESCRIPCION["M3limpio"],
    "C4": "M3 limpio más las dos variables de la red (fase4c.variables_red con fase4b.con_imagen; los nombres de "
          "columna son los de C2), calculadas antes del remuestreo; en las filas de entrenamiento, de las redes de "
          "los otros pliegues (el atajo); todo lo demás de M3 limpio, igual",
}


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar_red(ruta, internos):
    """Las puntuaciones guardadas por fase4c_redes.py, comprobadas. Devuelve la tabla
    y su procedencia."""
    ruta_json = os.path.splitext(os.path.splitext(ruta)[0])[0] + ".json"
    with open(ruta_json, encoding="utf-8") as f:
        procedencia = json.load(f)
    if sha256(ruta) != procedencia["sha256"]:
        raise SystemExit(f"ERROR: {ruta} no tiene el SHA-256 de su procedencia.")
    if procedencia["internos"] != internos:
        raise SystemExit(f"ERROR: {ruta} es de la corrida con internos={procedencia['internos']}.")
    if procedencia["controles"]["fallos"] != 0:
        raise SystemExit(f"ERROR: las redes de {ruta} se entrenaron con controles fallidos.")
    if not all(a["una_puntuacion_por_fila"] for a in procedencia["alineacion"].values()):
        raise SystemExit(f"ERROR: la alineación registrada en {ruta_json} no se cumplió.")
    tabla = pd.read_csv(ruta, float_precision="round_trip")
    p = tabla["puntuacion"].to_numpy(np.float64)
    if hashlib.sha256(p.tobytes()).hexdigest() != procedencia["sha256_de_las_puntuaciones_float64"]:
        raise SystemExit(f"ERROR: las puntuaciones leídas de {ruta} no tienen la huella de su procedencia.")
    if p.tobytes() != fase4c.probabilidad(tabla["logit"].to_numpy()).tobytes():
        raise SystemExit(f"ERROR: en {ruta}, la puntuación no es la sigmoide del logit guardado.")
    return tabla, procedencia


def de_semilla(tabla, semilla, isic):
    """La puntuación de cada fila del desarrollo en una semilla, unida por isic_id."""
    t = tabla[tabla["semilla"] == semilla]
    p = pd.Series(t["puntuacion"].to_numpy(np.float64), index=t["isic_id"].to_numpy())
    if not p.index.is_unique or len(p) != len(isic) or not p.index.isin(isic).all():
        raise SystemExit(f"ERROR: la semilla {semilla} no tiene exactamente una puntuación por fila del desarrollo.")
    return p.loc[isic].to_numpy()


def huellas_iguales(df, semillas, n_splits):
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        ref = json.load(f)["folds"]["sha256_por_semilla"]
    huellas, folds = {}, {}
    for s in semillas:
        folds[s] = construir_folds(df, G, Y, n_splits, s)
        huellas[str(s)] = f4.huella_folds(folds[s], len(df))
        if huellas[str(s)] != ref[str(s)]:
            raise SystemExit(f"ERROR: los pliegues de la semilla {s} no son los de {REF_PLIEGUES}.")
    return folds, huellas


def resumen(por, semillas):
    todos = [v for s in semillas for v in por[str(s)]]
    medias = [float(np.mean(por[str(s)])) for s in semillas]
    return {"por_semilla_y_fold": {str(s): [round(v, 4) for v in por[str(s)]] for s in semillas},
            "media_global": round(float(np.mean(todos)), 4), "std_entre_folds": round(float(np.std(todos)), 4),
            "std_entre_semillas": round(float(np.std(medias)), 4)}


def comparar(por_nuevo, por_base, semillas, n_splits):
    comparaciones = {}
    for k, mayor in f4.METRICAS.items():
        diffs = [float(b - a) for s in semillas for a, b in zip(por_base[k][str(s)], por_nuevo[k][str(s)])]
        comp = f4.comparacion(diffs, n_splits, semillas, mayor)
        if f4b.nadeau_bengio(diffs, n_splits, 0.95) != _nadeau_bengio(diffs, n_splits):
            raise SystemExit("ERROR: nadeau_bengio al 95 % no coincide con el de evaluar_repetido.py.")
        comp["intervalo_bonferroni_nadeau_bengio"] = f4b.nadeau_bengio(diffs, n_splits, CONFIANZA_BONFERRONI)
        comp["confianza_bonferroni"] = round(CONFIANZA_BONFERRONI, 6)
        comp["papel"] = "principal" if k == "pauc" else "secundaria"
        comparaciones[k] = comp
    return comparaciones


def c4_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p_tr_va, tr, va, semilla):
    """C4 en un pliegue: devuelve (puntuación de validación, registro). p_tr_va es
    un vector sobre todo el desarrollo con la puntuación de la red que recibe cada
    fila de tr y de va."""
    x_tr, x_va, cats, _ = ganador_m3.variables_m3_en_pliegue(df_sin_etiqueta, tr, va, excluidas, G)
    a = fase4c.variables_red(p_tr_va, tr, va, grupos)
    xc_tr, xc_va = fase4b.con_imagen(x_tr, x_va, a)
    alin = f4b.comprobar_alineacion(x_tr, xc_tr, a, semilla, y[tr], grupos[tr])
    if not all(alin[k] for k in ("antes", "razon", "despues")):
        raise SystemExit(f"ERROR: alineación de C4, semilla {semilla}: {alin}")
    t1 = time.perf_counter()
    modelo = ganador_m3.ajustar_m3(xc_tr, y[tr], grupos[tr], cats, semilla, parametros=ganador_m3.PARAMETROS_LIMPIO)
    t_ajuste = round(time.perf_counter() - t1, 2)
    s = modelo.predict_proba(xc_va)[:, 1]
    return s, {"n_variables": int(xc_tr.shape[1]), "alineacion": alin, "segundos_ajuste": t_ajuste,
               "arboles": int(modelo.tree_count_),
               "iteraciones_corridas": len(modelo.get_evals_result()["validation"]["AUC"])}


def escribir(out, resultado, titulo, nuevo, base, nombres_modelo):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    s = resultado["semillas_corridas"]
    lineas = [f"# Fase 4c: {titulo}", "",
              f"Conjunto de desarrollo, semillas {s[0]} a {s[-1]} × {resultado['n_splits']} pliegues.", ""]
    for k, comp in resultado["comparaciones_nuevo_menos_base"].items():
        lineas.append(f"- {nombres[k]}: {nombres_modelo[0]} {resultado['metricas'][nuevo][k]['media_global']}, "
                      f"{nombres_modelo[1]} {resultado['metricas'][base][k]['media_global']}; diferencia "
                      f"{comp['media']}, NB 95 % {comp['intervalo_t_95_nadeau_bengio']}, Bonferroni "
                      f"{comp['intervalo_bonferroni_nadeau_bengio']}; mejor en {comp['nuevo_mejor_en_folds']} de "
                      f"{comp['de_folds']} pliegues y {comp['nuevo_mejor_en_semillas']} de {comp['de_semillas']} "
                      "semillas")
    lineas += ["", f"Total: {resultado['segundos']['total']} s.", "", "No aplica la regla ni interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--pregunta", type=int, choices=[1, 2])
    grupo.add_argument("--atajo", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--red", default=RED)
    ap.add_argument("--red-internas", default=RED_INTERNAS)
    ap.add_argument("--salida-c4", default=SALIDA_C4, help="la de --pregunta 2, que --atajo reproduce")
    args = ap.parse_args()
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    red_tabla, red_proc = cargar_red(args.red, internos=False)
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    semillas = [0] if args.atajo else args.semillas
    folds, huellas = huellas_iguales(df, semillas, args.n_splits)
    comun = {
        "datos": datos, "semillas_corridas": semillas, "n_splits": args.n_splits,
        "folds": {"sha256_por_semilla": huellas, "iguales_a": os.path.relpath(REF_PLIEGUES, RAIZ)},
        "puntuaciones_de_la_red": {"archivo": red_proc["archivo"], "sha256": red_proc["sha256"],
                                   "huella_de_las_puntuaciones": red_proc["sha256_de_las_puntuaciones_float64"],
                                   "controles": red_proc["controles"],
                                   "segundos_por_red": red_proc["segundos_por_red"]},
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
    }

    if args.pregunta == 1:
        with open(IMAGEN_SOLA, encoding="utf-8") as f:
            sola = json.load(f)
        if not sola["control_m1_contra_referencia"]["huellas_de_pliegues_iguales"]:
            raise SystemExit(f"ERROR: {IMAGEN_SOLA} no registra los pliegues de {REF_PLIEGUES}.")
        imagen = {k: sola["metricas"]["Imagen"][k]["por_semilla_y_fold"] for k in f4.METRICAS}
        red = {k: {} for k in f4.METRICAS}
        for s in semillas:
            p = de_semilla(red_tabla, s, isic)
            valores = {k: [] for k in f4.METRICAS}
            for tr, va in folds[s]:
                for k, v in f4.medir(y[va], p[va], grupos[va]).items():
                    valores[k].append(v)
            for k in f4.METRICAS:
                red[k][str(s)] = valores[k]
            print(f"Semilla {s}: métricas de la red sola", flush=True)
        resultado = {
            **comun, "comparacion": {"nuevo": "Red", "base": "Imagen"},
            "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in ("Red", "Imagen")},
            "referencia_imagen": {"archivo": os.path.relpath(IMAGEN_SOLA, RAIZ), "precision": "4 decimales",
                                  "pliegues_comprobados_contra": os.path.relpath(REF_PLIEGUES, RAIZ)},
            "metricas": {"Red": {k: resumen(red[k], semillas) for k in f4.METRICAS},
                         "Imagen": {k: resumen(imagen[k], semillas) for k in f4.METRICAS}},
            "comparaciones_nuevo_menos_base": comparar(red, imagen, semillas, args.n_splits),
            "segundos": {"total": round(time.perf_counter() - t_total, 1)},
            "nota": ("Red − Imagen, pareado pliegue a pliegue; Imagen a 4 decimales, como está guardada. "
                     "intervalo_bonferroni_nadeau_bengio: el corregido por Nadeau y Bengio con confianza 1 − 0,05/2, "
                     "el de la regla de PLAN.md, Fase 4c. En el NNT80% SE menos es mejor. No aplica la regla ni "
                     "interpreta."),
        }
        escribir(args.out, resultado, "Red sola − Imagen", "Red", "Imagen", ("Red", "Imagen"))
        return

    predicciones, procedencia_m3l = f4b.cargar_predicciones(f4b.PREDICCIONES)
    excluidas = cargar_columnas_excluidas(FUGAS)
    df_sin_etiqueta = df.drop(columns=[Y])
    with open(REF_M3L, encoding="utf-8") as f:
        ref_m3l = json.load(f)

    if args.pregunta == 2:
        por = {m: {k: {} for k in f4.METRICAS} for m in ("M3limpio", "C4")}
        bloque, t_semilla = {}, {}
        for s in semillas:
            inicio = time.perf_counter()
            p = de_semilla(red_tabla, s, isic)
            valores = {m: {k: [] for k in f4.METRICAS} for m in por}
            for i, (tr, va) in enumerate(folds[s]):
                base = f4b.guardada(predicciones, "M3limpio", s, i, isic[va])
                sc, reg = c4_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p, tr, va, s)
                bloque.setdefault(str(s), []).append(reg)
                for m, puntuacion in (("M3limpio", base), ("C4", sc)):
                    for k, v in f4.medir(y[va], puntuacion, grupos[va]).items():
                        valores[m][k].append(v)
            for m in por:
                for k in f4.METRICAS:
                    por[m][k][str(s)] = valores[m][k]
            t_semilla[str(s)] = round(time.perf_counter() - inicio, 1)
            print(f"Semilla {s}: {t_semilla[str(s)]} s", flush=True)
        fuera = [(k, s) for k in f4.METRICAS for s in semillas
                 if [round(v, 4) for v in por["M3limpio"][k][str(s)]]
                 != ref_m3l["metricas"]["M3limpio"][k]["por_semilla_y_fold"][str(s)]]
        if fuera:
            raise SystemExit(f"ERROR: M3 limpio no reproduce {REF_M3L}: {fuera}")
        resultado = {
            **comun, "comparacion": {"nuevo": "C4", "base": "M3limpio"},
            "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in ("M3limpio", "C4")},
            "hiperparametros": "M3 limpio: los de la Fase 4 (ganador_m3.PARAMETROS_LIMPIO). Sin ajuste.",
            "reproduccion_del_base": {"referencia": os.path.relpath(REF_M3L, RAIZ),
                                      "que_se_compara": "las cuatro métricas de M3 limpio, pliegue a pliegue",
                                      "reproduce_fold_a_fold": True},
            "predicciones_guardadas": {"archivo": os.path.relpath(f4b.PREDICCIONES, RAIZ),
                                       "sha256": procedencia_m3l["sha256"],
                                       "huella_de_las_puntuaciones": procedencia_m3l["sha256_de_las_puntuaciones_float64"],
                                       "usadas_para": "M3 limpio"},
            "metricas": {m: {k: resumen(por[m][k], semillas) for k in f4.METRICAS} for m in por},
            "comparaciones_nuevo_menos_base": comparar(por["C4"], por["M3limpio"], semillas, args.n_splits),
            "c4": {"por_semilla_y_fold": bloque},
            "segundos": {"por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
            "nota": ("C4 − M3 limpio, pareado pliegue a pliegue. intervalo_bonferroni_nadeau_bengio: el corregido por "
                     "Nadeau y Bengio con confianza 1 − 0,05/2, el de la regla de PLAN.md, Fase 4c. En el NNT80% SE "
                     "menos es mejor. No aplica la regla ni interpreta."),
        }
        escribir(args.out, resultado, "C4 − M3 limpio", "C4", "M3limpio", ("C4", "M3 limpio"))
        return

    # --atajo: semilla 0, C4 con la validación interna frente a C4 con el atajo.
    internas, proc_int = cargar_red(args.red_internas, internos=True)
    with open(args.salida_c4, encoding="utf-8") as f:
        c4_guardada = json.load(f)["metricas"]["C4"]
    p_atajo = de_semilla(red_tabla, 0, isic)
    filas, pliegues = [], []
    for i, (tr, va) in enumerate(folds[0]):
        t = internas[(internas["semilla"] == 0) & (internas["pliegue"] == i)]
        q = pd.Series(t["puntuacion"].to_numpy(np.float64), index=t["isic_id"].to_numpy())
        if not q.index.is_unique or len(q) != len(tr) or not q.index.isin(isic[tr]).all():
            raise SystemExit(f"ERROR: las puntuaciones internas del pliegue {i} no cubren su entrenamiento una vez.")
        p_interna = np.full(len(df), np.nan)
        p_interna[tr] = q.loc[isic[tr]].to_numpy()
        p_interna[va] = p_atajo[va]  # la validación, de la red externa en los dos casos
        s_atajo, reg_a = c4_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p_atajo, tr, va, 0)
        s_int, reg_i = c4_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p_interna, tr, va, 0)
        m_a, m_i = f4.medir(y[va], s_atajo, grupos[va]), f4.medir(y[va], s_int, grupos[va])
        if round(m_a["pauc"], 4) != c4_guardada["pauc"]["por_semilla_y_fold"]["0"][i]:
            raise SystemExit(f"ERROR: C4 con el atajo no reproduce {args.salida_c4} en el pliegue {i}.")
        pliegues.append({"pliegue": i, "pauc_atajo": round(m_a["pauc"], 4), "pauc_validacion_interna": round(m_i["pauc"], 4),
                         "diferencia_interna_menos_atajo": round(m_i["pauc"] - m_a["pauc"], 4),
                         "metricas_atajo": {k: round(v, 4) for k, v in m_a.items()},
                         "metricas_validacion_interna": {k: round(v, 4) for k, v in m_i.items()},
                         "ajuste_atajo": reg_a, "ajuste_validacion_interna": reg_i})
        filas.append(m_i["pauc"] - m_a["pauc"])
        print(f"Pliegue {i}: pAUC con el atajo {m_a['pauc']:.4f}, con la validación interna {m_i['pauc']:.4f}",
              flush=True)
    resultado = {
        **comun,
        "que_es": ("Control del atajo de la Fase 4c (PLAN.md), descriptivo: no cambia la regla. Semilla 0: C4 con las "
                   "puntuaciones de la validación interna de M4b en las filas de entrenamiento, frente a C4 con el "
                   "atajo; en validación, las dos con la red externa."),
        "puntuaciones_internas": {"archivo": proc_int["archivo"], "sha256": proc_int["sha256"],
                                  "huella_de_las_puntuaciones": proc_int["sha256_de_las_puntuaciones_float64"],
                                  "segundos_por_red": proc_int["segundos_por_red"]},
        "c4_con_el_atajo_reproduce": os.path.relpath(args.salida_c4, RAIZ),
        "por_pliegue": pliegues,
        "diferencia_de_pauc_interna_menos_atajo": {"por_pliegue": [round(d, 4) for d in filas],
                                                   "media": round(float(np.mean(filas)), 4),
                                                   "minima": round(float(np.min(filas)), 4),
                                                   "maxima": round(float(np.max(filas)), 4)},
        "segundos": {"total": round(time.perf_counter() - t_total, 1)},
        "nota": "Descriptivo, sin intervalo: cinco pliegues de una semilla. No aplica la regla ni interpreta.",
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    d = resultado["diferencia_de_pauc_interna_menos_atajo"]
    lineas = ["# Fase 4c: control del atajo (semilla 0)", "",
              "C4 con la validación interna de M4b en las filas de entrenamiento, frente a C4 con el atajo. "
              "Descriptivo: no cambia la regla.", ""]
    lineas += [f"- Pliegue {q['pliegue']}: pAUC {q['pauc_atajo']} con el atajo, {q['pauc_validacion_interna']} con la "
               f"validación interna; diferencia {q['diferencia_interna_menos_atajo']}" for q in pliegues]
    lineas += ["", f"Diferencia media {d['media']} (de {d['minima']} a {d['maxima']}).", "",
               "No aplica la regla ni interpreta."]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md", flush=True)


if __name__ == "__main__":
    main()

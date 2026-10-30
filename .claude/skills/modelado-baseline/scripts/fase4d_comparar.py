#!/usr/bin/env python3
"""
fase4d_comparar.py — Fase 4d (PLAN.md, decisión de la persona del 2026-10-30):
las tres preguntas. Validación repetida con los pliegues de la Fase 4
(construir_folds, 5 pliegues).

  --pregunta 1: C5 − M3 limpio, semillas 0 a 9. C5 es C4 con las seis variables de
       la red de fase4d.variables_c5 (la puntuación y su razón, como C4; la
       estandarizada por zona y edad, con ruido en el entrenamiento; y las tres
       estandarizadas por conglomerado), sobre las puntuaciones de la red de la
       Fase 4c, con el atajo declarado. En el mismo pliegue se recalcula C4, que
       tiene que reproducir outputs/fase4c-c4-vs-m3limpio.json, y M3 limpio son
       sus predicciones guardadas de la Fase 4b, que tienen que reproducir
       outputs/fase4-m3limpio-vs-m2.json.
  --pregunta 2: la red mejorada − la red de la Fase 4c, semillas 0 a 4: la
       puntuación de cada red en el pliegue de validación. La red de la 4c tiene
       que reproducir sus métricas de outputs/fase4c-red-sola-vs-imagen.json.
  --pregunta 3: C6 − M3 limpio, semillas 0 a 4. C6 es C5 con las puntuaciones de
       la red mejorada.

En cada pliegue de C5 y C6 se detiene si falla la alineación de las seis
variables, antes o después del remuestreo (fase4d.comprobar_alineacion), o si el
ruido no va solo al entrenamiento (fase4d.comprobar_ruido).

Por métrica (pAUC, AUC, SEtop-15 y NNT80% SE): la diferencia pareada pliegue a
pliegue, con fase4_comparar.comparacion (intervalo t ingenuo, corregido por
Nadeau y Bengio al 95 % y victorias), el valor p bilateral de Nadeau y Bengio
(fase4d.valor_p) y, en la pAUC, la media y el intervalo divididos por 0,2, en
especificidad media. En el NNT, menos es mejor.

Antes de empezar se comprueba que las dos corridas completas de controles tienen
0 fallos: outputs/fase4d-controles-comparacion.json y data/fase4d-controles.json.
Las puntuaciones de las redes se leen con fase4c_comparar.cargar_red, con sus
comprobaciones.

No aplica la regla ni interpreta: mide y escribe --out.json y su .md. La regla la
aplica fase4d_holm.py sobre las tres salidas.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4d_comparar.py \\
        --pregunta 1 --out outputs/fase4d-c5-vs-m3limpio
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4d_comparar.py \\
        --pregunta 2 --out outputs/fase4d-red-mejorada-vs-red
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4d_comparar.py \\
        --pregunta 3 --out outputs/fase4d-c6-vs-m3limpio
"""

import argparse
import json
import os
import sys
import time
import warnings

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import fase4c_comparar as f4cc  # noqa: E402
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import _nadeau_bengio, cargar_columnas_excluidas  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
RED_MEJORADA = os.path.join(RAIZ, "data", "fase4d-puntuaciones-red-mejorada.csv.gz")
CONTROLES = os.path.join(RAIZ, "data", "fase4d-controles.json")
CONTROLES_COMPARACION = os.path.join(RAIZ, "outputs", "fase4d-controles-comparacion.json")
REF_M3L = os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json")
REF_C4 = os.path.join(RAIZ, "outputs", "fase4c-c4-vs-m3limpio.json")
REF_RED = os.path.join(RAIZ, "outputs", "fase4c-red-sola-vs-imagen.json")
G, Y = "patient_id", "target"
SEMILLAS = {1: list(range(10)), 2: list(range(5)), 3: list(range(5))}
DESCRIPCION = {
    "M3limpio": f4.DESCRIPCION["M3limpio"],
    "C4": f4cc.DESCRIPCION["C4"],
    "C5": ("C4 con las seis variables de la red de fase4d.variables_c5: la puntuación y su razón a la media del "
           "paciente (como C4), la puntuación estandarizada por tbp_lv_location × age_approx (celda 17 sin el "
           "hospital) con ruido normal de desviación 0,1 en las filas de entrenamiento, y las tres estandarizadas por "
           "conglomerado (celda 19); red de la Fase 4c, con el atajo; todo lo demás de M3 limpio, igual"),
    "C6": "C5 con las puntuaciones de la red mejorada en lugar de las de la red de la Fase 4c",
    "Red": f4cc.DESCRIPCION["Red"] + " (Fase 4c: 3 épocas, una submuestra nueva de negativos en cada época)",
    "RedMejorada": ("la misma red con 15 épocas y los negativos en bloques de 20 por positivo, uno distinto en cada "
                    "época (fase4d.entrenar_y_puntuar); su probabilidad, la sigmoide del logit en float64"),
}


def leer_controles():
    salida = {}
    for nombre, ruta in (("comparacion", CONTROLES_COMPARACION), ("redes_y_c5", CONTROLES)):
        with open(ruta, encoding="utf-8") as f:
            c = json.load(f)
        if c.get("rapido") or c.get("fallos") != 0:
            raise SystemExit(f"ERROR: {ruta} no es la corrida completa de los controles con 0 fallos.")
        salida[nombre] = {"archivo": os.path.relpath(ruta, RAIZ), "sha256": f4cc.sha256(ruta),
                          "casos": len(c["casos"]), "fallos": c["fallos"]}
    return salida


def resumen(por, semillas, k):
    r = f4cc.resumen(por, semillas)
    if k == "pauc":
        r["media_global_sobre_0_2"] = round(float(np.mean([v for s in semillas for v in por[str(s)]])) / 0.2, 4)
    return r


def comparar(por_nuevo, por_base, semillas, n_splits):
    comparaciones = {}
    for k, mayor in f4.METRICAS.items():
        diffs = [float(b - a) for s in semillas for a, b in zip(por_base[k][str(s)], por_nuevo[k][str(s)])]
        comp = f4.comparacion(diffs, n_splits, semillas, mayor)
        if f4b.nadeau_bengio(diffs, n_splits, 0.95) != _nadeau_bengio(diffs, n_splits):
            raise SystemExit("ERROR: nadeau_bengio al 95 % no coincide con el de evaluar_repetido.py.")
        comp["media_sin_redondear"] = float(np.mean(diffs))
        comp["valor_p_nadeau_bengio"] = fase4d.valor_p(diffs, n_splits)
        if k == "pauc":
            comp["en_especificidad_media"] = {
                "media": round(float(np.mean(diffs)) / 0.2, 4),
                "intervalo_t_95_nadeau_bengio": _nadeau_bengio([d / 0.2 for d in diffs], n_splits)}
        comp["papel"] = "principal" if k == "pauc" else "secundaria"
        comparaciones[k] = comp
    return comparaciones


def m3_y_red_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p, tr, va, semilla, con_c4):
    """C5 (o C6) en un pliegue, y C4 si con_c4, con las mismas variables de M3 limpio.
    p: la puntuación de la red para cada fila del desarrollo. Devuelve (puntuación de
    C4 o None, puntuación de C5, registro)."""
    t0 = time.perf_counter()
    x_tr, x_va, cats, _, aj = ganador_m3.variables_m3_en_pliegue(df_sin_etiqueta, tr, va, excluidas, G,
                                                                 devolver_ajuste=True)
    registro = {"segundos_variables_m3": round(time.perf_counter() - t0, 1)}
    s4 = None
    if con_c4:
        a4 = fase4c.variables_red(p, tr, va, grupos)
        x4_tr, x4_va = fase4b.con_imagen(x_tr, x_va, a4)
        alin4 = f4b.comprobar_alineacion(x_tr, x4_tr, a4, semilla, y[tr], grupos[tr])
        if not all(alin4[k] for k in ("antes", "razon", "despues")):
            raise SystemExit(f"ERROR: alineación de C4, semilla {semilla}: {alin4}")
        t1 = time.perf_counter()
        m4 = ganador_m3.ajustar_m3(x4_tr, y[tr], grupos[tr], cats, semilla, parametros=ganador_m3.PARAMETROS_LIMPIO)
        s4 = m4.predict_proba(x4_va)[:, 1]
        registro["c4"] = {"n_variables": int(x4_tr.shape[1]), "alineacion": alin4,
                          "segundos_ajuste": round(time.perf_counter() - t1, 2), "arboles": int(m4.tree_count_)}
    claves_tr = fase4d.claves_zona_edad(df_sin_etiqueta, tr, x_tr)
    claves_va = fase4d.claves_zona_edad(df_sin_etiqueta, va, x_va)
    et_tr, et_va = fase4d.etiquetas_conglomerado(aj, x_tr, x_va)
    a = fase4d.variables_c5(p, tr, va, grupos, claves_tr, claves_va, et_tr, et_va, semilla)
    _, z_va_sin = fase4d.estandarizar(p[tr], claves_tr, p[va], claves_va)
    ruido = fase4d.comprobar_ruido(a, semilla, z_va_sin)
    if not (ruido["validacion_sin_ruido"] and ruido["entrenamiento_con_el_sorteo_de_la_semilla"]):
        raise SystemExit(f"ERROR: el ruido de la semilla {semilla} no va solo al entrenamiento: {ruido}")
    xc_tr, xc_va = fase4d.con_red(x_tr, x_va, a)
    alin = fase4d.comprobar_alineacion(x_tr, xc_tr, a, semilla, y[tr], grupos[tr])
    if not all(alin[k] for k in ("antes", "razon", "despues")):
        raise SystemExit(f"ERROR: alineación de las seis variables, semilla {semilla}: {alin}")
    t1 = time.perf_counter()
    modelo = ganador_m3.ajustar_m3(xc_tr, y[tr], grupos[tr], cats, semilla, parametros=ganador_m3.PARAMETROS_LIMPIO)
    s5 = modelo.predict_proba(xc_va)[:, 1]
    registro.update({
        "n_variables": int(xc_tr.shape[1]), "alineacion": alin, "ruido": ruido,
        "nan_por_variable": {c: {"tr": int(np.isnan(a["tr"][c]).sum()), "va": int(np.isnan(a["va"][c]).sum())}
                             for c in fase4d.COLUMNAS_C5},
        "segundos_ajuste": round(time.perf_counter() - t1, 2), "arboles": int(modelo.tree_count_),
        "iteraciones_corridas": len(modelo.get_evals_result()["validation"]["AUC"])})
    return s4, s5, registro


def reproduce(por, ref, semillas, que):
    fuera = [(k, s) for k in f4.METRICAS for s in semillas
             if [round(v, 4) for v in por[k][str(s)]] != ref[k]["por_semilla_y_fold"][str(s)]]
    if fuera:
        raise SystemExit(f"ERROR: {que}: {fuera}")


def escribir(out, resultado, titulo, nuevo, base, nombres_modelo):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    s = resultado["semillas_corridas"]
    lineas = [f"# Fase 4d: {titulo}", "",
              f"Conjunto de desarrollo, semillas {s[0]} a {s[-1]} × {resultado['n_splits']} pliegues.", ""]
    for k, comp in resultado["comparaciones_nuevo_menos_base"].items():
        lineas.append(f"- {nombres[k]}: {nombres_modelo[0]} {resultado['metricas'][nuevo][k]['media_global']}, "
                      f"{nombres_modelo[1]} {resultado['metricas'][base][k]['media_global']}; diferencia "
                      f"{comp['media']}, NB 95 % {comp['intervalo_t_95_nadeau_bengio']}, valor p "
                      f"{comp['valor_p_nadeau_bengio']:.4g}; mejor en {comp['nuevo_mejor_en_folds']} de "
                      f"{comp['de_folds']} pliegues y {comp['nuevo_mejor_en_semillas']} de {comp['de_semillas']} "
                      "semillas")
    e = resultado["comparaciones_nuevo_menos_base"]["pauc"]["en_especificidad_media"]
    lineas += ["", f"En especificidad media (pAUC/0,2): diferencia {e['media']}, NB 95 % "
               f"{e['intervalo_t_95_nadeau_bengio']}.", "",
               f"Total: {resultado['segundos']['total']} s.", "",
               "No aplica la regla ni interpreta: la aplica fase4d_holm.py."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pregunta", type=int, choices=[1, 2, 3], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+")
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--red-mejorada", default=RED_MEJORADA)
    args = ap.parse_args()
    semillas = args.semillas if args.semillas is not None else SEMILLAS[args.pregunta]
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()
    controles = leer_controles()

    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    folds, huellas = f4cc.huellas_iguales(df, semillas, args.n_splits)
    red_4c, proc_4c = f4cc.cargar_red(f4cc.RED, internos=False)
    redes = {"Fase 4c": proc_4c}
    if args.pregunta in (2, 3):
        red_4d, proc_4d = f4cc.cargar_red(args.red_mejorada, internos=False)
        if not set(semillas) <= set(proc_4d["semillas"]):
            raise SystemExit(f"ERROR: {args.red_mejorada} no tiene las semillas {semillas}.")
        redes["Fase 4d"] = proc_4d

    def de_la_red(proc):
        return {"archivo": proc["archivo"], "sha256": proc["sha256"],
                "huella_de_las_puntuaciones": proc["sha256_de_las_puntuaciones_float64"],
                "controles": proc["controles"], "segundos_por_red": proc["segundos_por_red"]}
    comun = {
        "datos": datos, "semillas_corridas": semillas, "n_splits": args.n_splits,
        "folds": {"sha256_por_semilla": huellas, "iguales_a": os.path.relpath(f4cc.REF_PLIEGUES, RAIZ)},
        "puntuaciones_de_las_redes": {k: de_la_red(v) for k, v in redes.items()},
        "controles": controles,
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
    }

    if args.pregunta == 2:
        por = {m: {k: {} for k in f4.METRICAS} for m in ("Red", "RedMejorada")}
        for s in semillas:
            p = {"Red": f4cc.de_semilla(red_4c, s, isic), "RedMejorada": f4cc.de_semilla(red_4d, s, isic)}
            valores = {m: {k: [] for k in f4.METRICAS} for m in por}
            for tr, va in folds[s]:
                for m in por:
                    for k, v in f4.medir(y[va], p[m][va], grupos[va]).items():
                        valores[m][k].append(v)
            for m in por:
                for k in f4.METRICAS:
                    por[m][k][str(s)] = valores[m][k]
            print(f"Semilla {s}: métricas de las dos redes", flush=True)
        with open(REF_RED, encoding="utf-8") as f:
            reproduce(por["Red"], json.load(f)["metricas"]["Red"], semillas,
                      f"la red de la Fase 4c no reproduce {REF_RED}")
        resultado = {
            **comun, "comparacion": {"nuevo": "RedMejorada", "base": "Red"},
            "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in ("RedMejorada", "Red")},
            "reproduccion_del_base": {"referencia": os.path.relpath(REF_RED, RAIZ),
                                      "que_se_compara": "las cuatro métricas de la red de la Fase 4c, pliegue a pliegue",
                                      "reproduce_fold_a_fold": True},
            "metricas": {m: {k: resumen(por[m][k], semillas, k) for k in f4.METRICAS} for m in por},
            "comparaciones_nuevo_menos_base": comparar(por["RedMejorada"], por["Red"], semillas, args.n_splits),
            "segundos": {"total": round(time.perf_counter() - t_total, 1)},
            "nota": ("Red mejorada − red de la Fase 4c, pareado pliegue a pliegue. valor_p_nadeau_bengio: bilateral, "
                     "el que usa la regla de Holm de PLAN.md, Fase 4d. En el NNT80% SE menos es mejor. No aplica la "
                     "regla ni interpreta."),
        }
        escribir(args.out, resultado, "red mejorada − red de la Fase 4c", "RedMejorada", "Red",
                 ("Red mejorada", "Red de la 4c"))
        return

    nuevo = "C5" if args.pregunta == 1 else "C6"
    con_c4 = args.pregunta == 1
    red = red_4c if args.pregunta == 1 else red_4d
    predicciones, procedencia_m3l = f4b.cargar_predicciones(f4b.PREDICCIONES)
    excluidas = cargar_columnas_excluidas(FUGAS)
    df_sin_etiqueta = df.drop(columns=[Y])
    modelos = ("M3limpio", nuevo) + (("C4",) if con_c4 else ())
    por = {m: {k: {} for k in f4.METRICAS} for m in modelos}
    bloque, t_semilla = {}, {}
    for s in semillas:
        inicio = time.perf_counter()
        p = f4cc.de_semilla(red, s, isic)
        valores = {m: {k: [] for k in f4.METRICAS} for m in por}
        for i, (tr, va) in enumerate(folds[s]):
            base = f4b.guardada(predicciones, "M3limpio", s, i, isic[va])
            s4, s5, reg = m3_y_red_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p, tr, va, s, con_c4)
            bloque.setdefault(str(s), []).append(reg)
            for m, puntuacion in (("M3limpio", base), (nuevo, s5), ("C4", s4)):
                if m in por:
                    for k, v in f4.medir(y[va], puntuacion, grupos[va]).items():
                        valores[m][k].append(v)
        for m in por:
            for k in f4.METRICAS:
                por[m][k][str(s)] = valores[m][k]
        t_semilla[str(s)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {s}: {t_semilla[str(s)]} s", flush=True)
    with open(REF_M3L, encoding="utf-8") as f:
        reproduce(por["M3limpio"], json.load(f)["metricas"]["M3limpio"], semillas,
                  f"M3 limpio no reproduce {REF_M3L}")
    extra = {}
    if con_c4:
        with open(REF_C4, encoding="utf-8") as f:
            reproduce(por["C4"], json.load(f)["metricas"]["C4"], semillas, f"C4 no reproduce {REF_C4}")
        extra["reproduccion_de_c4"] = {"referencia": os.path.relpath(REF_C4, RAIZ),
                                       "que_se_compara": "las cuatro métricas de C4, pliegue a pliegue",
                                       "reproduce_fold_a_fold": True,
                                       "metricas": {k: resumen(por["C4"][k], semillas, k) for k in f4.METRICAS}}
    resultado = {
        **comun, "comparacion": {"nuevo": nuevo, "base": "M3limpio"},
        "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in modelos},
        "hiperparametros": "M3 limpio: los de la Fase 4 (ganador_m3.PARAMETROS_LIMPIO). Sin ajuste.",
        "reproduccion_del_base": {"referencia": os.path.relpath(REF_M3L, RAIZ),
                                  "que_se_compara": "las cuatro métricas de M3 limpio, pliegue a pliegue",
                                  "reproduce_fold_a_fold": True},
        **extra,
        "predicciones_guardadas": {"archivo": os.path.relpath(f4b.PREDICCIONES, RAIZ),
                                   "sha256": procedencia_m3l["sha256"],
                                   "huella_de_las_puntuaciones": procedencia_m3l["sha256_de_las_puntuaciones_float64"],
                                   "usadas_para": "M3 limpio"},
        "ruido": {"variable": fase4d.Z_ZONA_EDAD, "desviacion": fase4d.RUIDO,
                  "donde": "solo en las filas de entrenamiento, con numpy.random.default_rng(semilla)"},
        "metricas": {m: {k: resumen(por[m][k], semillas, k) for k in f4.METRICAS} for m in ("M3limpio", nuevo)},
        "comparaciones_nuevo_menos_base": comparar(por[nuevo], por["M3limpio"], semillas, args.n_splits),
        nuevo.lower(): {"por_semilla_y_fold": bloque},
        "segundos": {"por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
        "nota": (f"{nuevo} − M3 limpio, pareado pliegue a pliegue. valor_p_nadeau_bengio: bilateral, el que usa la "
                 "regla de Holm de PLAN.md, Fase 4d. En el NNT80% SE menos es mejor. No aplica la regla ni "
                 "interpreta."),
    }
    escribir(args.out, resultado, f"{nuevo} − M3 limpio", nuevo, "M3limpio", (nuevo, "M3 limpio"))


if __name__ == "__main__":
    main()

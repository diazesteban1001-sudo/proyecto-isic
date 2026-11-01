#!/usr/bin/env python3
"""
fase4e_comparar.py — Fase 4e de PLAN.md (decisión de la persona del 2026-10-31):
la exploración y las dos preguntas de la confirmación. Validación repetida con
los pliegues de la Fase 4 (construir_folds, 5 pliegues).

  --exploracion: semilla 0, descriptiva. Paso 1: la red de la 4e frente a la red
       de la Fase 4c, pliegue a pliegue. Con --red-ajustada, paso 2: la red
       ajustada frente a la red de la 4e sin ajustar. Para cada paso, en cuántos
       pliegues gana la nueva en la pAUC (estrictamente, sin redondear) y si llega
       al umbral de la regla, 4 de 5. La red de la 4c tiene que reproducir sus
       métricas de outputs/fase4c-red-sola-vs-imagen.json.
  --pregunta 1: la red elegida − la red de la Fase 4c, en las semillas de
       confirmación: la puntuación de cada red en el pliegue de validación.
  --pregunta 2: C7 − M3 limpio, en las semillas de confirmación. C7 es C4 con la
       red elegida: las dos variables de fase4c.variables_red, la puntuación y su
       razón a la media del paciente, con el atajo declarado, y todo lo demás de M3
       limpio (ganador_m3.PARAMETROS_LIMPIO). M3 limpio son sus predicciones
       guardadas de la Fase 4b, que tienen que reproducir
       outputs/fase4-m3limpio-vs-m2.json. En cada pliegue se detiene si falla la
       alineación de las dos variables, antes o después del remuestreo.

Las preguntas usan las mismas medidas que la Fase 4d (fase4d_comparar.comparar):
por métrica, la diferencia pareada pliegue a pliegue, el intervalo corregido por
Nadeau y Bengio al 95 %, el valor p bilateral de la misma prueba y las victorias.

Antes de empezar se comprueba que los controles completos tienen 0 fallos:
outputs/fase4e-controles-comparacion.json, data/fase4e-controles.json y, con la
red ajustada, data/fase4e-controles-ajuste.json. Las puntuaciones de la 4e se
leen con cargar_red_4e, con las comprobaciones de fase4c_comparar.cargar_red.

No aplica la regla de las preguntas ni interpreta: mide y escribe --out.json y su
.md. La de Holm la aplica fase4e_holm.py.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4e_comparar.py --exploracion \\
        --red-4e data/fase4e-puntuaciones-red-exploracion.csv.gz --out outputs/fase4e-exploracion
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4e_comparar.py --pregunta 1 \\
        --semillas 5 6 7 8 9 --red-4e data/….csv.gz --out outputs/fase4e-red-vs-red4c
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4e_comparar.py --pregunta 2 \\
        --semillas 5 6 7 8 9 --red-4e data/….csv.gz --out outputs/fase4e-c7-vs-m3limpio
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
import fase4c_comparar as f4cc  # noqa: E402
import fase4d_comparar as f4dc  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
CONTROLES = {"comparacion": os.path.join(RAIZ, "outputs", "fase4e-controles-comparacion.json"),
             "redes": os.path.join(RAIZ, "data", "fase4e-controles.json")}
CONTROLES_AJUSTE = os.path.join(RAIZ, "data", "fase4e-controles-ajuste.json")
REF_M3L = f4dc.REF_M3L
REF_RED = f4dc.REF_RED
G, Y = "patient_id", "target"
UMBRAL_EXPLORACION = 4
DESCRIPCION = {
    "M3limpio": f4.DESCRIPCION["M3limpio"],
    "Red": f4dc.DESCRIPCION["Red"],
    "Red4e": ("EfficientNet-B0 con la receta de imagen del 10.º puesto (fase4e.entrenar_y_puntuar): 20 épocas, cada "
              "una con todos los positivos y un conjunto distinto de los 20 en que se reparten los negativos, los "
              "aumentos del patrón 2, AdamW y OneCycle; su probabilidad, la sigmoide del logit en float64"),
    "Red4eAjustada": ("la red de la 4e tras el ajuste fino del paso 2 (fase4e_ajuste.ajustar_y_puntuar): 2 épocas con "
                      "pAUC_CVaR_Loss y SOPA sobre las clases invertidas, con la capa de salida reinicializada"),
    "C7": ("C4 con la red de la 4e elegida en lugar de la red de la Fase 4c: la puntuación y su razón a la media "
           "del paciente (fase4c.variables_red), con el atajo; todo lo demás de M3 limpio, igual"),
}


def cargar_red_4e(ruta, ajuste_fino):
    """Las puntuaciones de fase4e_redes.py o fase4e_ajuste.py, con las comprobaciones
    de fase4c_comparar.cargar_red; en lugar de «internos», «ajuste_fino»."""
    ruta_json = os.path.splitext(os.path.splitext(ruta)[0])[0] + ".json"
    with open(ruta_json, encoding="utf-8") as f:
        procedencia = json.load(f)
    if f4cc.sha256(ruta) != procedencia["sha256"]:
        raise SystemExit(f"ERROR: {ruta} no tiene el SHA-256 de su procedencia.")
    if procedencia["ajuste_fino"] != ajuste_fino:
        raise SystemExit(f"ERROR: {ruta} es de la corrida con ajuste_fino={procedencia['ajuste_fino']}.")
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


def leer_controles(con_ajuste):
    rutas = dict(CONTROLES, **({"ajuste": CONTROLES_AJUSTE} if con_ajuste else {}))
    salida = {}
    for nombre, ruta in rutas.items():
        with open(ruta, encoding="utf-8") as f:
            c = json.load(f)
        if c.get("rapido") or c.get("fallos") != 0:
            raise SystemExit(f"ERROR: {ruta} no es la corrida completa de los controles con 0 fallos.")
        salida[nombre] = {"archivo": os.path.relpath(ruta, RAIZ), "sha256": f4cc.sha256(ruta),
                          "casos": len(c["casos"]), "fallos": c["fallos"]}
    return salida


def de_la_red(proc):
    return {"archivo": proc["archivo"], "sha256": proc["sha256"],
            "huella_de_las_puntuaciones": proc["sha256_de_las_puntuaciones_float64"],
            "controles": proc["controles"], "segundos_por_red": proc["segundos_por_red"]}


def metricas_por_pliegue(y, grupos, folds, semillas, puntuaciones):
    """{modelo: {métrica: {semilla: [valor por pliegue]}}} para {modelo: {semilla: p}}."""
    por = {m: {k: {} for k in f4.METRICAS} for m in puntuaciones}
    for s in semillas:
        for m, p in puntuaciones.items():
            valores = {k: [] for k in f4.METRICAS}
            for _tr, va in folds[s]:
                for k, v in f4.medir(y[va], p[s][va], grupos[va]).items():
                    valores[k].append(v)
            for k in f4.METRICAS:
                por[m][k][str(s)] = valores[k]
    return por


def paso(por, nuevo, base, semilla):
    nuevos, bases = por[nuevo]["pauc"][str(semilla)], por[base]["pauc"][str(semilla)]
    gana = [bool(a > b) for a, b in zip(nuevos, bases)]
    return {"nuevo": nuevo, "base": base, "semilla": semilla,
            "pauc_por_pliegue": {nuevo: [round(v, 4) for v in nuevos], base: [round(v, 4) for v in bases]},
            "diferencia_por_pliegue": [round(a - b, 4) for a, b in zip(nuevos, bases)],
            "diferencia_media": round(float(np.mean([a - b for a, b in zip(nuevos, bases)])), 4),
            "nuevo_mejor_en_pliegue": gana, "nuevo_mejor_en_pliegues": int(sum(gana)), "de_pliegues": len(gana),
            "umbral_de_la_regla": UMBRAL_EXPLORACION, "llega_al_umbral": bool(sum(gana) >= UMBRAL_EXPLORACION),
            "otras_metricas": {k: {nuevo: [round(v, 4) for v in por[nuevo][k][str(semilla)]],
                                   base: [round(v, 4) for v in por[base][k][str(semilla)]]}
                               for k in f4.METRICAS if k != "pauc"}}


def c7_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p, tr, va, semilla):
    """C7 en un pliegue: C4 de f4dc.m3_y_red_en_pliegue con la puntuación p."""
    t0 = time.perf_counter()
    x_tr, x_va, cats, _ = ganador_m3.variables_m3_en_pliegue(df_sin_etiqueta, tr, va, excluidas, G)
    registro = {"segundos_variables_m3": round(time.perf_counter() - t0, 1)}
    a = fase4c.variables_red(p, tr, va, grupos)
    xc_tr, xc_va = fase4b.con_imagen(x_tr, x_va, a)
    alin = f4b.comprobar_alineacion(x_tr, xc_tr, a, semilla, y[tr], grupos[tr])
    if not all(alin[k] for k in ("antes", "razon", "despues")):
        raise SystemExit(f"ERROR: alineación de C7, semilla {semilla}: {alin}")
    t1 = time.perf_counter()
    modelo = ganador_m3.ajustar_m3(xc_tr, y[tr], grupos[tr], cats, semilla, parametros=ganador_m3.PARAMETROS_LIMPIO)
    s7 = modelo.predict_proba(xc_va)[:, 1]
    registro.update({"n_variables": int(xc_tr.shape[1]), "alineacion": alin,
                     "segundos_ajuste": round(time.perf_counter() - t1, 2), "arboles": int(modelo.tree_count_),
                     "iteraciones_corridas": len(modelo.get_evals_result()["validation"]["AUC"])})
    return s7, registro


def escribir_pregunta(out, resultado, titulo, nuevo, base, nombres_modelo):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    s = resultado["semillas_corridas"]
    lineas = [f"# Fase 4e: {titulo}", "",
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
               "No aplica la regla ni interpreta: la aplica fase4e_holm.py."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def escribir_exploracion(out, resultado):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"Red4e": "red de la 4e", "Red": "red de la 4c", "Red4eAjustada": "red ajustada"}
    lineas = ["# Fase 4e: la exploración, semilla 0", "", "Descriptiva. pAUC por pliegue, y en cuántos gana la nueva.",
              ""]
    for clave in ("paso_1", "paso_2"):
        p = resultado.get(clave)
        if not p:
            continue
        lineas.append(f"- {clave.replace('_', ' ').capitalize()}, {nombres[p['nuevo']]} frente a "
                      f"{nombres[p['base']]}: {p['pauc_por_pliegue'][p['nuevo']]} frente a "
                      f"{p['pauc_por_pliegue'][p['base']]}; gana en {p['nuevo_mejor_en_pliegues']} de "
                      f"{p['de_pliegues']} (umbral {p['umbral_de_la_regla']}); llega al umbral: "
                      f"{'sí' if p['llega_al_umbral'] else 'no'}")
    lineas += ["", "Las demás métricas, en el .json. Mide; la regla la aplica PLAN.md."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--exploracion", action="store_true")
    modo.add_argument("--pregunta", type=int, choices=[1, 2])
    ap.add_argument("--semillas", type=int, nargs="+")
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--red-4e", required=True, help="las puntuaciones de la red de la 4e (la elegida, en las preguntas)")
    ap.add_argument("--ajustada", action="store_true", help="en las preguntas: --red-4e es la red ajustada")
    ap.add_argument("--red-ajustada", help="en la exploración: las puntuaciones de la red ajustada, para el paso 2")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    semillas = [0] if args.exploracion else args.semillas
    if args.exploracion and args.semillas not in (None, [0]):
        raise SystemExit("ERROR: la exploración es la semilla 0.")
    if not semillas:
        raise SystemExit("ERROR: las preguntas necesitan --semillas, las de la confirmación.")
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()
    con_ajuste = bool(args.red_ajustada) or args.ajustada
    controles = leer_controles(con_ajuste)

    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    folds, huellas = f4cc.huellas_iguales(df, semillas, args.n_splits)
    red_4c, proc_4c = f4cc.cargar_red(f4cc.RED, internos=False)
    elegida = "Red4eAjustada" if args.ajustada else "Red4e"
    red_4e, proc_4e = cargar_red_4e(args.red_4e, ajuste_fino=args.ajustada)
    if not set(semillas) <= set(proc_4e["semillas"]):
        raise SystemExit(f"ERROR: {args.red_4e} no tiene las semillas {semillas}.")
    redes = {"Fase 4c": proc_4c, elegida: proc_4e}
    if args.red_ajustada:
        red_aj, proc_aj = cargar_red_4e(args.red_ajustada, ajuste_fino=True)
        if 0 not in proc_aj["semillas"]:
            raise SystemExit(f"ERROR: {args.red_ajustada} no tiene la semilla 0.")
        redes["Red4eAjustada"] = proc_aj
    comun = {
        "datos": datos, "semillas_corridas": semillas, "n_splits": args.n_splits,
        "folds": {"sha256_por_semilla": huellas, "iguales_a": os.path.relpath(f4cc.REF_PLIEGUES, RAIZ)},
        "puntuaciones_de_las_redes": {k: de_la_red(v) for k, v in redes.items()},
        "controles": controles,
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
    }

    def de(tabla):
        return {s: f4cc.de_semilla(tabla, s, isic) for s in semillas}

    if args.exploracion or args.pregunta == 1:
        puntuaciones = {"Red": de(red_4c), elegida: de(red_4e)}
        if args.red_ajustada:
            puntuaciones["Red4eAjustada"] = de(red_aj)
        por = metricas_por_pliegue(y, grupos, folds, semillas, puntuaciones)
        with open(REF_RED, encoding="utf-8") as f:
            f4dc.reproduce(por["Red"], json.load(f)["metricas"]["Red"], semillas,
                           f"la red de la Fase 4c no reproduce {REF_RED}")
        reproduccion = {"referencia": os.path.relpath(REF_RED, RAIZ),
                        "que_se_compara": "las cuatro métricas de la red de la Fase 4c, pliegue a pliegue",
                        "reproduce_fold_a_fold": True}
        if args.exploracion:
            resultado = {
                **comun, "que_es": "La exploración de la Fase 4e de PLAN.md, semilla 0. Descriptiva.",
                "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in puntuaciones},
                "reproduccion_del_base": reproduccion,
                "metricas": {m: {k: f4dc.resumen(por[m][k], semillas, k) for k in f4.METRICAS} for m in por},
                "paso_1": paso(por, "Red4e", "Red", 0),
                "paso_2": paso(por, "Red4eAjustada", "Red4e", 0) if args.red_ajustada else None,
                "segundos": {"total": round(time.perf_counter() - t_total, 1)},
                "nota": ("Gana la nueva en un pliegue si su pAUC, sin redondear, es estrictamente mayor. El umbral es "
                         "el de PLAN.md, Fase 4e: 4 de los 5 pliegues. Descriptiva: sus filas entran a la bitácora "
                         "como descriptivas."),
            }
            escribir_exploracion(args.out, resultado)
            return
        resultado = {
            **comun, "comparacion": {"nuevo": elegida, "base": "Red"},
            "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in (elegida, "Red")},
            "reproduccion_del_base": reproduccion,
            "metricas": {m: {k: f4dc.resumen(por[m][k], semillas, k) for k in f4.METRICAS} for m in por},
            "comparaciones_nuevo_menos_base": f4dc.comparar(por[elegida], por["Red"], semillas, args.n_splits),
            "segundos": {"total": round(time.perf_counter() - t_total, 1)},
            "nota": ("La red de la 4e elegida − la red de la Fase 4c, pareado pliegue a pliegue. valor_p_nadeau_bengio: "
                     "bilateral, el que usa la regla de Holm de PLAN.md, Fase 4e. En el NNT80% SE menos es mejor. No "
                     "aplica la regla ni interpreta."),
        }
        escribir_pregunta(args.out, resultado, "la red de la 4e − la red de la Fase 4c", elegida, "Red",
                          ("Red de la 4e", "Red de la 4c"))
        return

    predicciones, procedencia_m3l = f4b.cargar_predicciones(f4b.PREDICCIONES)
    excluidas = cargar_columnas_excluidas(FUGAS)
    df_sin_etiqueta = df.drop(columns=[Y])
    por = {m: {k: {} for k in f4.METRICAS} for m in ("M3limpio", "C7")}
    bloque, t_semilla = {}, {}
    for s in semillas:
        inicio = time.perf_counter()
        p = f4cc.de_semilla(red_4e, s, isic)
        valores = {m: {k: [] for k in f4.METRICAS} for m in por}
        for i, (tr, va) in enumerate(folds[s]):
            base = f4b.guardada(predicciones, "M3limpio", s, i, isic[va])
            s7, reg = c7_en_pliegue(df_sin_etiqueta, excluidas, y, grupos, p, tr, va, s)
            bloque.setdefault(str(s), []).append(reg)
            for m, puntuacion in (("M3limpio", base), ("C7", s7)):
                for k, v in f4.medir(y[va], puntuacion, grupos[va]).items():
                    valores[m][k].append(v)
        for m in por:
            for k in f4.METRICAS:
                por[m][k][str(s)] = valores[m][k]
        t_semilla[str(s)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {s}: {t_semilla[str(s)]} s", flush=True)
    with open(REF_M3L, encoding="utf-8") as f:
        f4dc.reproduce(por["M3limpio"], json.load(f)["metricas"]["M3limpio"], semillas,
                       f"M3 limpio no reproduce {REF_M3L}")
    resultado = {
        **comun, "comparacion": {"nuevo": "C7", "base": "M3limpio"},
        "red_de_c7": elegida,
        "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in ("M3limpio", "C7")},
        "hiperparametros": "M3 limpio: los de la Fase 4 (ganador_m3.PARAMETROS_LIMPIO). Sin ajuste.",
        "reproduccion_del_base": {"referencia": os.path.relpath(REF_M3L, RAIZ),
                                  "que_se_compara": "las cuatro métricas de M3 limpio, pliegue a pliegue",
                                  "reproduce_fold_a_fold": True},
        "predicciones_guardadas": {"archivo": os.path.relpath(f4b.PREDICCIONES, RAIZ),
                                   "sha256": procedencia_m3l["sha256"],
                                   "huella_de_las_puntuaciones": procedencia_m3l["sha256_de_las_puntuaciones_float64"],
                                   "usadas_para": "M3 limpio"},
        "metricas": {m: {k: f4dc.resumen(por[m][k], semillas, k) for k in f4.METRICAS} for m in por},
        "comparaciones_nuevo_menos_base": f4dc.comparar(por["C7"], por["M3limpio"], semillas, args.n_splits),
        "c7": {"por_semilla_y_fold": bloque},
        "segundos": {"por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
        "nota": ("C7 − M3 limpio, pareado pliegue a pliegue. valor_p_nadeau_bengio: bilateral, el que usa la regla de "
                 "Holm de PLAN.md, Fase 4e. En el NNT80% SE menos es mejor. No aplica la regla ni interpreta."),
    }
    escribir_pregunta(args.out, resultado, "C7 − M3 limpio", "C7", "M3limpio", ("C7", "M3 limpio"))


if __name__ == "__main__":
    main()

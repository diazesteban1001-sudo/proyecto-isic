#!/usr/bin/env python3
"""
curva_aprendizaje.py — la curva de aprendizaje de «Imagen + básicos» y de la red
de la 4e, solo con el desarrollo. Análisis descriptivo, declarado como posterior
a la apertura del reservado (PLAN.md, Fase 5, «Curva de aprendizaje»; decisión
de la persona del 2026-11-04). No toca el reservado, no cambia ningún modelo ni
ninguna recomendación y no suma a la bitácora.

La pregunta de la persona: ¿sube «Imagen + básicos» con más datos más que la red?

«Imagen + básicos» es el de imagen_sola.py: modelo_imagen() sobre las 384
variables de DINOv2 más edad, sexo y zona del cuerpo (codificar_fold). En cada
pliegue k de la semilla 0, se entrena con 2, 3 o 4 de los otros cuatro pliegues
—2/5, 3/5 y 4/5 del desarrollo— y se puntúa el pliegue k. *Elegido por el
agente, declarado:* cada tamaño usa todas las combinaciones de pliegues, 6 de
2/5, 4 de 3/5 y 1 de 4/5, para no elegir un subconjunto a mano.

La red de la 4e: solo lo que ya está medido, sin entrenar redes nuevas. Todas sus
redes de desarrollo se entrenaron con 4/5 del desarrollo, así que hay un solo
tamaño: el de los pliegues de la semilla 0, en outputs/fase4e-exploracion.json >
paso_2.

Controles, cada uno con su caso que debe fallar:
  - los pliegues de la semilla 0 tienen la huella de outputs/fase4-m2-vs-m1.json,
    la misma que registra fase4e-exploracion.json;
  - con 4/5, el entrenamiento es el pliegue de entrenamiento de la Fase 4 y las
    cuatro métricas reproducen las de imagen-sola.json, semilla 0, a 4 decimales;
  - ningún paciente a los dos lados en ningún ajuste.
Si uno falla, no se escribe nada.

No interpreta: mide y escribe --out.json y su .md.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/curva_aprendizaje.py --out outputs/curva-aprendizaje
"""

import argparse
import datetime
import itertools
import json
import os
import platform
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402
import fase5  # noqa: E402
import imagen_sola  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds, preparar_features  # noqa: E402

RAIZ = fase5.RAIZ
G, Y = "patient_id", "target"
SEMILLA = 0
N_SPLITS = 5
TAMANOS = (2, 3, 4)  # pliegues de entrenamiento, de cinco


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return json.load(f)


def disjuntos(grupos, tr, va):
    return not (set(grupos[tr]) & set(grupos[va]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = time.perf_counter()
    casos = []
    csv = os.path.join(RAIZ, "data", "train-metadata.csv")
    excluidas = cargar_columnas_excluidas(os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json"))
    df, datos = cargar_desarrollo(csv, G, RUTA_HOLDOUT)
    numericas, categoricas = preparar_features(df, excluidas, Y, G)
    imagen, comprobacion = f4.cargar_imagen(df, os.path.join(RAIZ, "data", "dinov2-vits14-desarrollo.h5"), csv,
                                            RUTA_HOLDOUT, os.path.join(RAIZ, "outputs", "extraccion-imagen.json"))
    x_img, y, grupos = imagen.to_numpy(), df[Y].to_numpy(), df[G].astype(str).to_numpy()

    folds = construir_folds(df, G, Y, N_SPLITS, SEMILLA)
    ref = leer("outputs/fase4-m2-vs-m1.json")["folds"]["sha256_por_semilla"]
    huella = f4.huella_folds(folds, len(df))
    expl = leer("outputs/fase4e-exploracion.json")
    casos.append(fase5.caso("pliegues", "los de la semilla 0 tienen la huella de fase4-m2-vs-m1.json y de "
                            "fase4e-exploracion.json", huella == ref["0"] == expl["folds"]["sha256_por_semilla"]["0"],
                            False, huella[:12] + "…"))
    casos.append(fase5.caso("pliegues", "frente a la huella de la semilla 1", huella != ref["1"], True, "distintas"))
    if huella != ref["0"]:
        raise SystemExit("ERROR: los pliegues de la semilla 0 no son los de la Fase 4.")

    sola = leer("outputs/imagen-sola.json")["metricas"]["Imagen + básicos"]
    ajustes, avisos = [], 0
    for k, (tr_k, va) in enumerate(folds):
        otros = [j for j in range(N_SPLITS) if j != k]
        for t in TAMANOS:
            for combinacion in itertools.combinations(otros, t):
                tr = np.sort(np.concatenate([folds[j][1] for j in combinacion]))
                if not disjuntos(grupos, tr, va):
                    raise SystemExit(f"ERROR: un paciente a los dos lados en el pliegue {k}, {combinacion}.")
                b_tr, b_va = codificar_fold(df, imagen_sola.BASICOS_NUMERICAS, imagen_sola.BASICOS_CATEGORICAS, Y, tr, va)
                p, n = imagen_sola._ajustar_imagen(np.hstack([x_img[tr], b_tr]), y[tr], np.hstack([x_img[va], b_va]))
                avisos += n
                m = f4.medir(y[va], p, grupos[va])
                ajustes.append({"pliegue": k, "pliegues_de_entrenamiento": list(combinacion), "quintos": t,
                                "pacientes": int(len(set(grupos[tr]))), "lesiones": int(len(tr)),
                                "malignas": int(y[tr].sum()), **{q: round(v, 4) for q, v in m.items()}})
                if t == 4:
                    iguales = np.array_equal(tr, tr_k)
                    reproduce = all(round(m[q], 4) == sola[q]["por_semilla_y_fold"]["0"][k] for q in f4.METRICAS)
                    otra = all(round(m[q], 4) == sola[q]["por_semilla_y_fold"]["1"][k] for q in f4.METRICAS)
                    casos.append(fase5.caso("reproduccion", f"pliegue {k}, 4/5: el entrenamiento de la Fase 4 y las cuatro "
                                            "métricas de imagen-sola.json, semilla 0", iguales and reproduce, False,
                                            {q: round(m[q], 4) for q in f4.METRICAS}))
                    casos.append(fase5.caso("reproduccion", f"pliegue {k}, 4/5: frente a la semilla 1 de imagen-sola.json",
                                            not otra, True, f"iguales: {otra}"))
        print(f"Pliegue {k}: hecho ({round(time.perf_counter() - t0, 1)} s)", flush=True)
    malo = np.concatenate([folds[0][0], folds[0][1][:1]])
    casos.append(fase5.caso("pacientes", "en los 55 ajustes, ningún paciente a los dos lados", True, False,
                            f"{len(ajustes)} ajustes"))
    casos.append(fase5.caso("pacientes", "con una fila de validación en el entrenamiento",
                            not disjuntos(grupos, malo, folds[0][1]), True, "se detecta"))

    curva = {}
    for t in TAMANOS:
        filas = [a for a in ajustes if a["quintos"] == t]
        por_pliegue = {k: {q: round(float(np.mean([a[q] for a in filas if a["pliegue"] == k])), 4) for q in f4.METRICAS}
                       for k in range(N_SPLITS)}
        curva[f"{t}/5"] = {
            "ajustes": len(filas), "combinaciones_por_pliegue": len(filas) // N_SPLITS,
            "pacientes_medios": round(float(np.mean([a["pacientes"] for a in filas])), 1),
            "malignas_medias": round(float(np.mean([a["malignas"] for a in filas])), 1),
            "media_por_pliegue": por_pliegue,
            "media": {q: round(float(np.mean([por_pliegue[k][q] for k in range(N_SPLITS)])), 4) for q in f4.METRICAS},
            "minimo_y_maximo_de_los_ajustes": {q: [min(a[q] for a in filas), max(a[q] for a in filas)]
                                               for q in f4.METRICAS},
        }
    p2 = expl["paso_2"]
    if p2.get("semilla") != SEMILLA or p2.get("nuevo") != "Red4eAjustada":
        raise SystemExit("ERROR: fase4e-exploracion.json > paso_2 no es la red ajustada de la semilla 0.")
    red_por_pliegue = {k: {"pauc": p2["pauc_por_pliegue"]["Red4eAjustada"][k],
                           **{q: p2["otras_metricas"][q]["Red4eAjustada"][k] for q in ("auc", "setop15", "nnt80")}}
                       for k in range(N_SPLITS)}
    red = {"4/5": {"fuente": "outputs/fase4e-exploracion.json > paso_2 (Red4eAjustada), semilla 0",
                   "media_por_pliegue": red_por_pliegue,
                   "media": {q: round(float(np.mean([red_por_pliegue[k][q] for k in range(N_SPLITS)])), 4)
                             for q in f4.METRICAS}},
           "tamanos_medidos": ["4/5"], "tamanos_sin_medir": ["2/5", "3/5"],
           "por_que": ("todas las redes de la 4e de desarrollo, en data/fase4e-redes y data/fase4e-ajuste, se entrenaron "
                       "con el pliegue de entrenamiento: 4/5 del desarrollo, una por semilla y pliegue")}
    ib = {q: curva["4/5"]["media"][q] - curva["2/5"]["media"][q] for q in f4.METRICAS}
    fallos = [f"{c['control']}: {c['caso']}" for c in casos if not c["ok"]]
    if fallos:
        raise SystemExit("ERROR: fallaron controles; no se escribe nada:\n  " + "\n  ".join(fallos))
    resultado = {
        "que_es": ("curva de aprendizaje de «Imagen + básicos» y de la red de la 4e, solo con el desarrollo; análisis "
                   "descriptivo posterior a la apertura del reservado (PLAN.md, Fase 5, decisión de la persona del "
                   "2026-11-04); no toca el reservado"),
        "datos": datos,
        "pliegues": {"semilla": SEMILLA, "n_splits": N_SPLITS, "sha256": huella,
                     "como": "construir_folds de train_and_evaluate.py, los de la Fase 4"},
        "imagen_basicos": {"modelo": "imagen_sola._ajustar_imagen sobre DINOv2 + age_approx, sex y anatom_site_general",
                           "combinaciones": "todas las de 2, 3 y 4 de los otros cuatro pliegues",
                           "curva": curva, "ajustes": ajustes, "avisos_no_convergencia": avisos,
                           "caracteristicas_de_imagen": {"archivo": os.path.relpath(comprobacion["archivo"], RAIZ),
                                                         "sha256": comprobacion["sha256"]}},
        "red4e": red,
        "pregunta": {
            "texto": "¿sube «Imagen + básicos» con más datos más que la red?",
            "imagen_basicos_de_2_a_4_quintos": {q: round(v, 4) for q, v in ib.items()},
            "red4e_de_2_a_4_quintos": None,
            "se_puede_responder_con_lo_medido": False,
            "por_que": "la red tiene un solo tamaño de entrenamiento medido en desarrollo, 4/5; su curva no está medida",
        },
        "controles": {"casos": casos, "de_casos": len(casos), "fallos": 0,
                      "deben_fallar": sum(c["debe_fallar"] for c in casos)},
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "segundos": round(time.perf_counter() - t0, 1),
        "nota": "No interpreta. Posterior a la apertura; solo desarrollo.",
    }
    out = args.out if os.path.isabs(args.out) else os.path.join(RAIZ, args.out)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    c = resultado["controles"]
    lineas = ["# Curva de aprendizaje, solo desarrollo (posterior a la apertura, descriptivo)",
              f"Pliegues de la semilla 0; «Imagen + básicos» con todas las combinaciones de 2, 3 y 4 de los otros "
              f"cuatro pliegues; la red de la 4e, solo lo ya medido.",
              "| Tamaño | Pacientes (media) | «Imagen + básicos», pAUC | AUC | SEtop-15 | NNT80% SE | Red de la 4e, pAUC |",
              "|---|---|---|---|---|---|---|"]
    for t in TAMANOS:
        cv = curva[f"{t}/5"]
        r = red["4/5"]["media"]["pauc"] if t == 4 else "sin medir"
        lineas.append(f"| {t}/5 | {cv['pacientes_medios']} | {cv['media']['pauc']} | {cv['media']['auc']} | "
                      f"{cv['media']['setop15']} | {cv['media']['nnt80']} | {r} |")
    lineas += [f"«Imagen + básicos», de 2/5 a 4/5: pAUC {resultado['pregunta']['imagen_basicos_de_2_a_4_quintos']['pauc']:+}. "
               "La red tiene un solo tamaño medido (4/5): la pregunta no se puede responder con lo medido.",
               f"Controles: {c['de_casos']} de {c['de_casos']} bien, {c['deben_fallar']} de ellos casos que deben fallar; "
               f"{resultado['segundos']} s. No interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']} s", flush=True)


if __name__ == "__main__":
    main()

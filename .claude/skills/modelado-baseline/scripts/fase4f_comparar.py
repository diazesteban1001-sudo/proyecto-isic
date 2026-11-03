#!/usr/bin/env python3
"""
fase4f_comparar.py — Fase 4f de PLAN.md (decisión de la persona del 2026-11-02):
una sola pregunta, la red de la 4e ajustada − «Imagen + básicos», en las semillas
de la confirmación de la 4e y sus pliegues (construir_folds, con la huella de
outputs/fase4-m2-vs-m1.json).

  - La red: las puntuaciones de la confirmación (fase4e_ajuste.py), leídas con
    fase4e_comparar.cargar_red_4e. Tiene que reproducir sus cuatro métricas de
    outputs/fase4e-red-vs-red4c.json pliegue a pliegue.
  - «Imagen + básicos»: se recalcula como en imagen_sola.py —modelo_imagen() sobre
    las 384 variables de DINOv2 más age_approx, sex y anatom_site_general, pasadas
    por codificar_fold—, ajustado con el pliegue de entrenamiento. Tiene que
    reproducir sus cuatro métricas de outputs/imagen-sola.json pliegue a pliegue, a
    4 decimales. Caso que debe fallar: cada semilla, frente a lo guardado para la
    siguiente (la última, frente a la primera), no coincide.

Si un control falla, se detiene sin escribir nada. La comparación es la de la
Fase 4d (fase4d_comparar.comparar), con los valores sin redondear. La regla de la
Fase 4f va en el mismo archivo, en «regla»: a favor si el valor p bilateral de
Nadeau y Bengio de la pAUC es menor que 0,05 y la diferencia media es positiva.
Las métricas secundarias no deciden. No interpreta.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4f_comparar.py \\
        --semillas 5 6 7 8 9 --out outputs/fase4f-red4e-vs-imagen-basicos
"""

import argparse
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4c  # noqa: E402
import fase4c_comparar as f4cc  # noqa: E402
import fase4d  # noqa: E402
import fase4d_comparar as f4dc  # noqa: E402
import fase4e_comparar as fec  # noqa: E402
import ganador_m3  # noqa: E402
import imagen_sola  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, preparar_features  # noqa: E402

RAIZ = ganador_m3.RAIZ
RED_4E = os.path.join(RAIZ, "data", "fase4e-puntuaciones-red-ajustada-confirmacion.csv.gz")
REF_RED_4E = os.path.join(RAIZ, "outputs", "fase4e-red-vs-red4c.json")
IMAGEN_SOLA = f4cc.IMAGEN_SOLA
DINOV2 = os.path.join(RAIZ, "data", "dinov2-vits14-desarrollo.h5")
EXTRACCION = os.path.join(RAIZ, "outputs", "extraccion-imagen.json")
G, Y = "patient_id", "target"
NUEVO, BASE = "Red4eAjustada", "ImagenBasicos"
DESCRIPCION = {
    NUEVO: fec.DESCRIPCION["Red4eAjustada"] + "; las puntuaciones de la confirmación de la Fase 4e",
    BASE: ("«Imagen + básicos» de outputs/imagen-sola.json, recalculado: modelo_imagen() de apilado_imagen.py sobre "
           "las 384 variables de DINOv2 más age_approx, sex y anatom_site_general (codificar_fold), estandarizadas "
           "juntas, ajustado con el pliegue de entrenamiento"),
}


def imagen_basicos(df, x_img, y, grupos, folds, semillas):
    """Las cuatro métricas de «Imagen + básicos» por pliegue, como en
    imagen_sola.puntuar_fold, y los avisos de no convergencia y segundos por semilla."""
    por = {k: {} for k in f4.METRICAS}
    avisos, segundos = 0, {}
    for s in semillas:
        inicio = time.perf_counter()
        valores = {k: [] for k in f4.METRICAS}
        for tr, va in folds[s]:
            b_tr, b_va = codificar_fold(df, imagen_sola.BASICOS_NUMERICAS, imagen_sola.BASICOS_CATEGORICAS, Y, tr, va)
            p, n = imagen_sola._ajustar_imagen(np.hstack([x_img[tr], b_tr]), y[tr], np.hstack([x_img[va], b_va]))
            avisos += n
            for k, v in f4.medir(y[va], p, grupos[va]).items():
                valores[k].append(v)
        for k in f4.METRICAS:
            por[k][str(s)] = valores[k]
        segundos[str(s)] = round(time.perf_counter() - inicio, 1)
        print(f"Semilla {s}: «Imagen + básicos» en {segundos[str(s)]} s", flush=True)
    return por, avisos, segundos


def caso_que_debe_fallar(por, ref, semillas):
    """Cada semilla recalculada frente a lo guardado para la siguiente: devuelve las
    semillas en que, aun así, coinciden las cuatro métricas (tiene que ser ninguna)."""
    coinciden = []
    for i, s in enumerate(semillas):
        otra = str(semillas[(i + 1) % len(semillas)])
        if all([round(v, 4) for v in por[k][str(s)]] == ref[k]["por_semilla_y_fold"][otra] for k in f4.METRICAS):
            coinciden.append(s)
    return coinciden


def escribir(out, resultado):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    s, r = resultado["semillas_corridas"], resultado["regla"]
    lineas = ["# Fase 4f: la red de la 4e − «Imagen + básicos»", "",
              f"Conjunto de desarrollo, semillas {s[0]} a {s[-1]} × {resultado['n_splits']} pliegues. «Imagen + "
              "básicos» reproduce outputs/imagen-sola.json y la red outputs/fase4e-red-vs-red4c.json, pliegue a "
              "pliegue.", ""]
    for k, comp in resultado["comparaciones_nuevo_menos_base"].items():
        lineas.append(f"- {nombres[k]}: red de la 4e {resultado['metricas'][NUEVO][k]['media_global']}, Imagen + "
                      f"básicos {resultado['metricas'][BASE][k]['media_global']}; diferencia {comp['media']}, NB 95 % "
                      f"{comp['intervalo_t_95_nadeau_bengio']}, valor p {comp['valor_p_nadeau_bengio']:.4g}; mejor en "
                      f"{comp['nuevo_mejor_en_folds']} de {comp['de_folds']} pliegues y "
                      f"{comp['nuevo_mejor_en_semillas']} de {comp['de_semillas']} semillas")
    e = resultado["comparaciones_nuevo_menos_base"]["pauc"]["en_especificidad_media"]
    lineas += ["", f"En especificidad media (pAUC/0,2): diferencia {e['media']}, NB 95 % "
               f"{e['intervalo_t_95_nadeau_bengio']}.", "",
               f"Regla de PLAN.md, Fase 4f: valor p {r['valor_p']:.4g} frente a {r['alfa']}; diferencia media "
               f"{'positiva' if r['media_sin_redondear'] > 0 else 'no positiva'}; a favor: "
               f"{'sí' if r['a_favor'] else 'no'}.", "",
               f"Total: {resultado['segundos']['total']} s. Aplica la regla tal como la fija PLAN.md; no interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, nargs="+", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--red-4e", default=RED_4E)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    semillas = args.semillas
    if len(semillas) < 2:
        raise SystemExit("ERROR: el caso que debe fallar necesita al menos dos semillas.")
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()
    controles = fec.leer_controles(con_ajuste=True)

    df, datos = cargar_desarrollo(fec.CSV, G, RUTA_HOLDOUT)
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    folds, huellas = f4cc.huellas_iguales(df, semillas, args.n_splits)

    red, proc = fec.cargar_red_4e(args.red_4e, ajuste_fino=True)
    if not set(semillas) <= set(proc["semillas"]):
        raise SystemExit(f"ERROR: {args.red_4e} no tiene las semillas {semillas}.")
    with open(REF_RED_4E, encoding="utf-8") as f:
        ref_red = json.load(f)
    if ref_red["comparacion"]["nuevo"] != NUEVO or ref_red["puntuaciones_de_las_redes"][NUEVO]["sha256"] != proc["sha256"]:
        raise SystemExit(f"ERROR: {REF_RED_4E} no es la pregunta 1 de la 4e con estas puntuaciones.")
    p_red = {s: f4cc.de_semilla(red, s, isic) for s in semillas}
    por_red = fec.metricas_por_pliegue(y, grupos, folds, semillas, {NUEVO: p_red})[NUEVO]
    f4dc.reproduce(por_red, ref_red["metricas"][NUEVO], semillas, f"la red de la 4e no reproduce {REF_RED_4E}")
    print("La red de la 4e reproduce su pregunta 1 pliegue a pliegue", flush=True)

    with open(IMAGEN_SOLA, encoding="utf-8") as f:
        sola = json.load(f)
    if not sola["control_m1_contra_referencia"]["huellas_de_pliegues_iguales"]:
        raise SystemExit(f"ERROR: {IMAGEN_SOLA} no registra los pliegues de {f4cc.REF_PLIEGUES}.")
    ref_ib = sola["metricas"]["Imagen + básicos"]
    excluidas = cargar_columnas_excluidas(fec.FUGAS)
    numericas, categoricas = preparar_features(df, excluidas, Y, G)
    faltan = [c for c in imagen_sola.BASICOS_NUMERICAS if c not in numericas] + \
             [c for c in imagen_sola.BASICOS_CATEGORICAS if c not in categoricas]
    if faltan:
        raise SystemExit(f"ERROR: {faltan} no son variables de M1 con el tipo esperado.")
    imagen, comprobacion_imagen = f4.cargar_imagen(df, DINOV2, fec.CSV, RUTA_HOLDOUT, EXTRACCION)
    comprobacion_imagen["archivo"] = os.path.relpath(DINOV2, RAIZ)
    por_ib, avisos, t_semilla = imagen_basicos(df, imagen.to_numpy(), y, grupos, folds, semillas)
    f4dc.reproduce(por_ib, ref_ib, semillas, f"«Imagen + básicos» no reproduce {IMAGEN_SOLA}")
    coinciden = caso_que_debe_fallar(por_ib, ref_ib, semillas)
    if coinciden:
        raise SystemExit(f"ERROR: el caso que debe fallar no falla: las semillas {coinciden} coinciden con otra.")
    print("«Imagen + básicos» reproduce outputs/imagen-sola.json, y el caso que debe fallar falla", flush=True)

    comparaciones = f4dc.comparar(por_red, por_ib, semillas, args.n_splits)
    c = comparaciones["pauc"]
    regla = {"que_es": ("La regla de PLAN.md, Fase 4f: a favor si el valor p bilateral de Nadeau y Bengio de la pAUC "
                        "es menor que alfa y la diferencia media es positiva. Una sola pregunta, sin corrección por "
                        "multiplicidad."),
             "alfa": fase4d.ALFA, "valor_p": c["valor_p_nadeau_bengio"], "media_sin_redondear": c["media_sin_redondear"],
             "valor_p_menor_que_alfa": bool(c["valor_p_nadeau_bengio"] < fase4d.ALFA),
             "media_positiva": bool(c["media_sin_redondear"] > 0)}
    regla["a_favor"] = regla["valor_p_menor_que_alfa"] and regla["media_positiva"]
    resultado = {
        "datos": datos, "semillas_corridas": semillas, "n_splits": args.n_splits,
        "folds": {"sha256_por_semilla": huellas, "iguales_a": os.path.relpath(f4cc.REF_PLIEGUES, RAIZ)},
        "puntuaciones_de_las_redes": {NUEVO: fec.de_la_red(proc)},
        "controles": controles,
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
        "comparacion": {"nuevo": NUEVO, "base": BASE},
        "modelos": {m: {"descripcion": DESCRIPCION[m]} for m in (NUEVO, BASE)},
        "comprobacion_imagen": comprobacion_imagen,
        "reproduccion_de_la_red": {"referencia": os.path.relpath(REF_RED_4E, RAIZ),
                                   "que_se_compara": "las cuatro métricas de la red ajustada, pliegue a pliegue",
                                   "reproduce_fold_a_fold": True},
        "reproduccion_del_base": {
            "referencia": os.path.relpath(IMAGEN_SOLA, RAIZ), "modelo_en_la_referencia": "Imagen + básicos",
            "que_se_compara": "las cuatro métricas, pliegue a pliegue, a 4 decimales",
            "reproduce_fold_a_fold": True,
            "caso_que_debe_fallar": {"que_es": ("cada semilla recalculada frente a lo guardado para la siguiente; la "
                                                "última, frente a la primera"),
                                     "semillas_que_coinciden": coinciden, "falla_como_se_esperaba": True}},
        "avisos_no_convergencia": {BASE: avisos},
        "metricas": {NUEVO: {k: f4dc.resumen(por_red[k], semillas, k) for k in f4.METRICAS},
                     BASE: {k: f4dc.resumen(por_ib[k], semillas, k) for k in f4.METRICAS}},
        "comparaciones_nuevo_menos_base": comparaciones,
        "regla": regla,
        "segundos": {"imagen_basicos_por_semilla": t_semilla, "total": round(time.perf_counter() - t_total, 1)},
        "nota": ("La red de la 4e ajustada − «Imagen + básicos», pareado pliegue a pliegue, con los valores sin "
                 "redondear. En el NNT80% SE menos es mejor. Las métricas secundarias no deciden. Aplica la regla tal "
                 "como la fija PLAN.md; no interpreta."),
    }
    escribir(args.out, resultado)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
fase4d_holm.py — la regla de la Fase 4d (PLAN.md, «Regla, fijada antes de
correr»), sobre las tres salidas de fase4d_comparar.py. Holm con los valores p
bilaterales de Nadeau y Bengio de la pAUC (fase4d.holm): ordenados de menor a
mayor, se comparan con 0,05/3, 0,05/2 y 0,05, y una pregunta se acepta solo si se
aceptaron las anteriores. Una pregunta da su resultado a favor si Holm la acepta
y su diferencia media en la pAUC es positiva.

Comprueba antes que cada salida es la pregunta que dice ser (los modelos y las
semillas de PLAN.md) y que las tres usaron los mismos controles. Si C5 y C6 dan
su resultado a favor, registra cuál tiene mayor diferencia media en la pAUC en
las semillas 0 a 4, las que tienen los dos.

Escribe --out.json y su .md. No interpreta.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4d_holm.py --out outputs/fase4d-holm
"""

import argparse
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4c_comparar as f4cc  # noqa: E402
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402

RAIZ = ganador_m3.RAIZ
PREGUNTAS = [
    {"pregunta": 1, "archivo": "outputs/fase4d-c5-vs-m3limpio.json", "nuevo": "C5", "base": "M3limpio",
     "semillas": list(range(10))},
    {"pregunta": 2, "archivo": "outputs/fase4d-red-mejorada-vs-red.json", "nuevo": "RedMejorada", "base": "Red",
     "semillas": list(range(5))},
    {"pregunta": 3, "archivo": "outputs/fase4d-c6-vs-m3limpio.json", "nuevo": "C6", "base": "M3limpio",
     "semillas": list(range(5))},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    entradas, salidas, controles = [], {}, set()
    for q in PREGUNTAS:
        ruta = os.path.join(RAIZ, q["archivo"])
        with open(ruta, encoding="utf-8") as f:
            r = json.load(f)
        if r["comparacion"] != {"nuevo": q["nuevo"], "base": q["base"]} or r["semillas_corridas"] != q["semillas"]:
            raise SystemExit(f"ERROR: {q['archivo']} no es la pregunta {q['pregunta']}: {r['comparacion']}, semillas "
                             f"{r['semillas_corridas']}.")
        controles.add(json.dumps(r["controles"], sort_keys=True))
        c = r["comparaciones_nuevo_menos_base"]["pauc"]
        # Las diferencias guardadas van a 4 decimales: el valor p recalculado con ellas tiene que quedar cerca.
        p, pg = fase4d.valor_p(c["diferencias_nuevo_menos_base"], r["n_splits"]), c["valor_p_nadeau_bengio"]
        if not (p < 1e-12 and pg < 1e-12) and abs(np.log10(max(p, 1e-300)) - np.log10(max(pg, 1e-300))) > 0.1:
            raise SystemExit(f"ERROR: el valor p de {q['archivo']} no corresponde a sus diferencias guardadas.")
        entradas.append({"pregunta": q["pregunta"], "valor_p": c["valor_p_nadeau_bengio"],
                         "media": c["media_sin_redondear"]})
        salidas[q["pregunta"]] = {"archivo": q["archivo"], "sha256": f4cc.sha256(ruta), "comparacion": r["comparacion"],
                                  "semillas": r["semillas_corridas"], "media_redondeada": c["media"],
                                  "intervalo_t_95_nadeau_bengio": c["intervalo_t_95_nadeau_bengio"],
                                  "en_especificidad_media": c["en_especificidad_media"]}
    if len(controles) != 1:
        raise SystemExit("ERROR: las tres salidas no usaron los mismos controles.")
    decision = fase4d.holm(entradas)
    for d in decision:
        d.update(salidas[d["pregunta"]])
    a_favor = {d["pregunta"]: d["a_favor"] for d in decision}
    eleccion = None
    if a_favor[1] and a_favor[3]:
        with open(os.path.join(RAIZ, PREGUNTAS[0]["archivo"]), encoding="utf-8") as f:
            c5 = json.load(f)["comparaciones_nuevo_menos_base"]["pauc"]["diferencias_nuevo_menos_base"]
        with open(os.path.join(RAIZ, PREGUNTAS[2]["archivo"]), encoding="utf-8") as f:
            c6 = json.load(f)["comparaciones_nuevo_menos_base"]["pauc"]["diferencias_nuevo_menos_base"]
        medias = {"C5": float(np.mean(c5[:25])), "C6": float(np.mean(c6))}
        eleccion = {"medias_en_las_semillas_0_a_4": {k: round(v, 4) for k, v in medias.items()},
                    "mayor": max(medias, key=medias.get)}
    resultado = {
        "que_es": ("La regla de la Fase 4d de PLAN.md: Holm sobre los valores p bilaterales de Nadeau y Bengio de la "
                   "pAUC de las tres preguntas; a favor si Holm la acepta y la diferencia media es positiva."),
        "alfa": fase4d.ALFA, "preguntas": decision, "a_favor": a_favor,
        "si_c5_y_c6_dan_su_resultado_a_favor": eleccion,
        "controles": json.loads(controles.pop()),
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "nota": "Aplica la regla tal como la fija PLAN.md. No interpreta.",
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {1: "C5 − M3 limpio", 2: "Red mejorada − red de la 4c", 3: "C6 − M3 limpio"}
    lineas = ["# Fase 4d: la regla de Holm", "",
              "Valores p bilaterales de Nadeau y Bengio de la pAUC, ordenados; a favor si Holm acepta y la diferencia "
              "media es positiva.", ""]
    for d in sorted(decision, key=lambda d: d["orden_holm"]):
        lineas.append(f"- {d['orden_holm']}. Pregunta {d['pregunta']}, {nombres[d['pregunta']]}: valor p "
                      f"{d['valor_p']:.4g} frente a {d['umbral_holm']:.4g}; diferencia {d['media_redondeada']}; "
                      f"aceptada {'sí' if d['aceptada_por_holm'] else 'no'}; a favor "
                      f"{'sí' if d['a_favor'] else 'no'}")
    if eleccion:
        lineas += ["", f"C5 y C6 a favor; mayor diferencia en las semillas 0 a 4: {eleccion['mayor']}."]
    lineas += ["", "Aplica la regla tal como la fija PLAN.md. No interpreta."]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md", flush=True)


if __name__ == "__main__":
    main()

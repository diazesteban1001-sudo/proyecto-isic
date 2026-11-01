#!/usr/bin/env python3
"""
fase4e_holm.py — la regla de la Fase 4e (PLAN.md, «Regla, fijada antes de
correr»), sobre las dos salidas de fase4e_comparar.py: la de la Fase 4d con dos
preguntas. Holm con los valores p bilaterales de Nadeau y Bengio de la pAUC
(fase4d.holm): ordenados de menor a mayor, se comparan con 0,05/2 y 0,05, y una
pregunta se acepta solo si se aceptó la anterior. Una pregunta da su resultado a
favor si Holm la acepta y su diferencia media en la pAUC es positiva.

Comprueba antes que cada salida es la pregunta que dice ser, que las dos usan las
semillas de --semillas, la misma red de la 4e y los mismos controles.

Escribe --out.json y su .md. No interpreta.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4e_holm.py \\
        --semillas 5 6 7 8 9 --out outputs/fase4e-holm
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
    {"pregunta": 1, "archivo": "outputs/fase4e-red-vs-red4c.json", "nuevo": ("Red4e", "Red4eAjustada"),
     "base": "Red"},
    {"pregunta": 2, "archivo": "outputs/fase4e-c7-vs-m3limpio.json", "nuevo": ("C7",), "base": "M3limpio"},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    entradas, salidas, controles, redes = [], {}, set(), set()
    for q in PREGUNTAS:
        ruta = os.path.join(RAIZ, q["archivo"])
        with open(ruta, encoding="utf-8") as f:
            r = json.load(f)
        if r["comparacion"]["nuevo"] not in q["nuevo"] or r["comparacion"]["base"] != q["base"] \
                or r["semillas_corridas"] != args.semillas:
            raise SystemExit(f"ERROR: {q['archivo']} no es la pregunta {q['pregunta']}: {r['comparacion']}, semillas "
                             f"{r['semillas_corridas']}.")
        controles.add(json.dumps(r["controles"], sort_keys=True))
        red = r["comparacion"]["nuevo"] if q["pregunta"] == 1 else r["red_de_c7"]
        redes.add((red, r["puntuaciones_de_las_redes"][red]["sha256"]))
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
        raise SystemExit("ERROR: las dos salidas no usaron los mismos controles.")
    if len(redes) != 1:
        raise SystemExit(f"ERROR: las dos preguntas no usaron la misma red de la 4e: {sorted(redes)}.")
    decision = fase4d.holm(entradas)
    for d in decision:
        d.update(salidas[d["pregunta"]])
    a_favor = {d["pregunta"]: d["a_favor"] for d in decision}
    red, sha = redes.pop()
    resultado = {
        "que_es": ("La regla de la Fase 4e de PLAN.md: Holm sobre los valores p bilaterales de Nadeau y Bengio de la "
                   "pAUC de las dos preguntas; a favor si Holm la acepta y la diferencia media es positiva."),
        "alfa": fase4d.ALFA, "semillas": args.semillas, "red_de_la_4e": {"modelo": red, "sha256": sha},
        "preguntas": decision, "a_favor": a_favor,
        "controles": json.loads(controles.pop()),
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "nota": "Aplica la regla tal como la fija PLAN.md. No interpreta.",
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    nombres = {1: "red de la 4e − red de la 4c", 2: "C7 − M3 limpio"}
    lineas = ["# Fase 4e: la regla de Holm", "",
              f"Semillas {args.semillas[0]} a {args.semillas[-1]}; red de la 4e: {red}. Valores p bilaterales de Nadeau "
              "y Bengio de la pAUC, ordenados; a favor si Holm acepta y la diferencia media es positiva.", ""]
    for d in sorted(decision, key=lambda d: d["orden_holm"]):
        lineas.append(f"- {d['orden_holm']}. Pregunta {d['pregunta']}, {nombres[d['pregunta']]}: valor p "
                      f"{d['valor_p']:.4g} frente a {d['umbral_holm']:.4g}; diferencia {d['media_redondeada']}; "
                      f"aceptada {'sí' if d['aceptada_por_holm'] else 'no'}; a favor "
                      f"{'sí' if d['a_favor'] else 'no'}")
    lineas += ["", "Aplica la regla tal como la fija PLAN.md. No interpreta."]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
test_fase4e_comparar.py — controles de fase4e_comparar.py antes de leer la
exploración: se le pasa, como si fuera la red de la 4e, la red de la Fase 4c
(data/fase4c-puntuaciones-red.csv.gz), con el formato de fase4e_redes.py.

  - exploración: con dos redes idénticas, la 4e no gana en ningún pliegue y no
    llega al umbral; y una red que tiene que ganar en todos, la de la 4c con 1
    sumado al logit de cada lesión maligna, se detecta como ganadora en los 5;
  - pregunta 1: con la red de la 4c contra sí misma, las diferencias son todas 0;
  - pregunta 2: C7 con la red de la 4c en la semilla 5 reproduce C4,
    outputs/fase4c-c4-vs-m3limpio.json, pliegue a pliegue en las cuatro métricas;
    caso que debe fallar: frente a C4 de la semilla 6, no coincide.

No lee ninguna puntuación de la 4e. Escribe en --dir, fuera de outputs/.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_comparar.py \\
        --dir data/fase4e-test-comparar --out data/fase4e-controles-comparar.json
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4c  # noqa: E402
import fase4c_comparar as f4cc  # noqa: E402
import fase4e_comparar as fec  # noqa: E402
import ganador_m3  # noqa: E402

RAIZ = ganador_m3.RAIZ
REF_C4 = os.path.join(RAIZ, "outputs", "fase4c-c4-vs-m3limpio.json")
CASOS = []


def registrar(grupo, nombre, ok, detalle):
    CASOS.append({"grupo": grupo, "caso": nombre, "como_se_esperaba": bool(ok), "detalle": str(detalle)})
    print(f"[{'OK' if ok else 'FALLA'}] {grupo} · {nombre}: {detalle}", flush=True)


def disfrazar(tabla, semillas, destino, sumar_a_malignos=0.0, etiquetas=None):
    """La red de la 4c en esas semillas, con la procedencia de fase4e_redes.py."""
    t = tabla[tabla["semilla"].isin(semillas)].copy().reset_index(drop=True)
    if sumar_a_malignos:
        t["logit"] = t["logit"].to_numpy(np.float64) + sumar_a_malignos * t["isic_id"].map(etiquetas).to_numpy()
    t["puntuacion"] = fase4c.probabilidad(t["logit"].to_numpy())
    t.to_csv(destino, index=False, float_format="%.17g", compression="gzip")
    leida = pd.read_csv(destino, float_precision="round_trip")
    proc = {"archivo": os.path.relpath(destino, RAIZ), "sha256": f4cc.sha256(destino), "ajuste_fino": False,
            "sha256_de_las_puntuaciones_float64": hashlib.sha256(leida["puntuacion"].to_numpy(np.float64).tobytes())
            .hexdigest(),
            "semillas": semillas, "controles": {"fallos": 0},
            "alineacion": {str(s): {"una_puntuacion_por_fila": True} for s in semillas},
            "segundos_por_red": None}
    with open(os.path.splitext(os.path.splitext(destino)[0])[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(proc, f)
    return destino


def correr(argumentos):
    sys.argv = ["fase4e_comparar.py"] + argumentos
    fec.main()
    with open(argumentos[argumentos.index("--out") + 1] + ".json", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    argv = list(sys.argv)
    t0 = time.perf_counter()
    os.makedirs(args.dir, exist_ok=True)
    tabla, _ = f4cc.cargar_red(f4cc.RED, internos=False)
    df = pd.read_csv(fec.CSV, usecols=["isic_id", "target"])
    etiquetas = pd.Series(df["target"].to_numpy(), index=df["isic_id"].to_numpy())

    igual = disfrazar(tabla, [0, 5], os.path.join(args.dir, "red4c-como-4e.csv.gz"))
    e = correr(["--exploracion", "--red-4e", igual, "--out", os.path.join(args.dir, "exploracion-igual")])["paso_1"]
    registrar("exploracion", "dos redes idénticas: no gana en ningún pliegue ni llega al umbral",
              e["nuevo_mejor_en_pliegues"] == 0 and not e["llega_al_umbral"],
              f"gana en {e['nuevo_mejor_en_pliegues']} de {e['de_pliegues']}; llega: {e['llega_al_umbral']}")
    mejor = disfrazar(tabla, [0], os.path.join(args.dir, "red4c-mas-1-en-malignos.csv.gz"), 1.0, etiquetas)
    e = correr(["--exploracion", "--red-4e", mejor, "--out", os.path.join(args.dir, "exploracion-mejor")])["paso_1"]
    registrar("exploracion", "sumando 1 al logit de los malignos (debe detectarse como ganadora)",
              e["nuevo_mejor_en_pliegues"] == 5 and e["llega_al_umbral"],
              f"gana en {e['nuevo_mejor_en_pliegues']} de {e['de_pliegues']}; llega: {e['llega_al_umbral']}")

    r = correr(["--pregunta", "1", "--semillas", "5", "--red-4e", igual, "--out", os.path.join(args.dir, "p1")])
    d = r["comparaciones_nuevo_menos_base"]["pauc"]["diferencias_nuevo_menos_base"]
    registrar("pregunta_1", "la red de la 4c contra sí misma: diferencias 0", all(v == 0 for v in d), f"{d}")

    r = correr(["--pregunta", "2", "--semillas", "5", "--red-4e", igual, "--out", os.path.join(args.dir, "p2")])
    with open(REF_C4, encoding="utf-8") as f:
        c4 = json.load(f)["metricas"]["C4"]
    c7 = r["metricas"]["C7"]
    iguales = {k: c7[k]["por_semilla_y_fold"]["5"] == c4[k]["por_semilla_y_fold"]["5"] for k in c4}
    registrar("pregunta_2", "C7 con la red de la 4c reproduce C4 en la semilla 5, en las cuatro métricas",
              all(iguales.values()), f"{iguales}; pAUC {c7['pauc']['por_semilla_y_fold']['5']}")
    otra = c7["pauc"]["por_semilla_y_fold"]["5"] == c4["pauc"]["por_semilla_y_fold"]["6"]
    registrar("pregunta_2", "frente a C4 de la semilla 6 (debe fallar)", not otra, f"iguales: {otra}")

    fallos = sum(not c["como_se_esperaba"] for c in CASOS)
    informe = {"casos": CASOS, "fallos": fallos, "rapido": False, "segundos": round(time.perf_counter() - t0, 1),
               "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": argv}}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(f"\n{len(CASOS) - fallos} de {len(CASOS)} casos como se esperaba; {informe['segundos']} s.", flush=True)
    if fallos:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
test_fase4e_ajuste.py — los controles de fase4e_ajuste.py, el ajuste fino del
paso 2 de la Fase 4e, antes de correrlo. Cada uno con su caso que debe fallar.
No calcula ninguna métrica.

  - lotes: con los tamaños de un pliegue real (253 positivos y 254.330
    negativos), cada lote trae 32 casos de cada clase, cada época tiene 397
    lotes, cada benigno entra una vez como mucho y las etiquetas invertidas son
    las de sus filas; caso que debe fallar: las mismas posiciones barajadas sin
    DualSampler.
  - capa: capa_nueva() cambia solo la capa de salida, y con la misma semilla da
    la misma capa; casos que deben fallar: sin capa_nueva(), y con otra semilla.
  - ajuste: ajustar_y_puntuar() corre de punta a punta sobre la red de los
    controles de la red (data/fase4e-controles-red-real.pt, semilla 1, pliegue 0,
    que no usan ni la exploración ni la confirmación), con max_lotes lotes por
    época y unas pocas filas de validación, y da el mismo logit dos veces; caso
    que debe fallar: un logit cambiado en 1e-6.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_ajuste.py \\
        --out data/fase4e-controles-ajuste.json
"""

import argparse
import copy
import json
import os
import sys
import time

import numpy as np
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4e  # noqa: E402
import fase4e_ajuste as fa  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from prueba_tiempo_red_imagen import red  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = ganador_m3.RAIZ
PESOS_CONTROL = os.path.join(RAIZ, "data", "fase4e-controles-red-real.pt")
CASOS = []


def registrar(grupo, nombre, ok, detalle):
    CASOS.append({"grupo": grupo, "caso": nombre, "como_se_esperaba": bool(ok), "detalle": str(detalle)})
    print(f"[{'OK' if ok else 'FALLA'}] {grupo} · {nombre}: {detalle}", flush=True)


def control_lotes():
    etiquetas = np.zeros(253 + 254330, dtype=np.int64)
    etiquetas[:253] = 1
    filas = np.random.default_rng(5).permutation(len(etiquetas))
    universo, invertidas, por_epoca = fa.orden_de_los_lotes(etiquetas, filas, semilla=1)
    bien, detalle = fa.comprobar_lotes(invertidas, por_epoca)
    lotes = [len(o) // fase4e.LOTE for o in por_epoca]
    veces = fa.actualizaciones_duales(invertidas, por_epoca)
    etiquetas_bien = bool(np.array_equal(invertidas, 1 - etiquetas[universo]))
    malignos = np.bincount(np.concatenate(por_epoca)[invertidas[np.concatenate(por_epoca)] == 0],
                           minlength=len(universo))[invertidas == 0]
    registrar("lotes", "32 de cada clase por lote, 397 lotes por época, cada benigno una vez como mucho",
              bien and lotes == [397, 397] and set(veces) <= {"0", "1"} and etiquetas_bien,
              f"{detalle}; lotes {lotes}; veces por benigno {veces}; etiquetas invertidas de sus filas: "
              f"{etiquetas_bien}; cada maligno entre {malignos.min()} y {malignos.max()} veces")
    rng = np.random.default_rng(0)
    barajadas = [rng.permutation(o) for o in por_epoca]
    mal, detalle_mal = fa.comprobar_lotes(invertidas, barajadas)
    registrar("lotes", "las mismas posiciones barajadas sin DualSampler (debe fallar)", not mal, detalle_mal)
    return {"lotes_por_epoca": lotes, "veces_por_benigno": veces,
            "veces_por_maligno": [int(malignos.min()), int(malignos.max())]}


def control_capa():
    cpu = torch.device("cpu")
    modelo, _ = red(cpu)
    modelo.load_state_dict(torch.load(PESOS_CONTROL, map_location=cpu))
    antes = copy.deepcopy(modelo.state_dict())

    def diferencias(m):
        d = m.state_dict()
        return sorted(k for k in d if not torch.equal(d[k], antes[k]))
    a = fa.capa_nueva(copy.deepcopy(modelo), 1)
    b = fa.capa_nueva(copy.deepcopy(modelo), 1)
    c = fa.capa_nueva(copy.deepcopy(modelo), 2)
    cambiadas = diferencias(a)
    misma = all(torch.equal(a.state_dict()[k], b.state_dict()[k]) for k in a.state_dict())
    registrar("capa", "capa_nueva() cambia solo la capa de salida, igual con la misma semilla",
              cambiadas == ["classifier.1.bias", "classifier.1.weight"] and misma,
              f"cambian {cambiadas}; con la misma semilla, igual: {misma}")
    registrar("capa", "sin capa_nueva() (debe fallar)", diferencias(modelo) != cambiadas,
              f"cambian {diferencias(modelo)}")
    otra = torch.equal(a.state_dict()["classifier.1.weight"], c.state_dict()["classifier.1.weight"])
    registrar("capa", "con otra semilla (debe fallar)", not otra, f"igual a la de la semilla 1: {otra}")


def control_ajuste(dispositivo, filas_validacion, max_lotes):
    df, _ = cargar_desarrollo(fa.CSV, fa.G, RUTA_HOLDOUT)
    isic, y = df["isic_id"].to_numpy(), df[fa.Y].to_numpy()
    tr, va = construir_folds(df, fa.G, fa.Y, 5, 1)[0]
    va = va[:filas_validacion]
    salidas = []
    for _ in range(2):
        logit, reg = fa.ajustar_y_puntuar(fa.HDF5, isic, y, tr, va, 1, dispositivo, PESOS_CONTROL,
                                          trabajadores=2, max_lotes=max_lotes)
        salidas.append(logit)
    iguales = bool(np.array_equal(salidas[0], salidas[1]))
    registrar("ajuste", f"corre de punta a punta y da el mismo logit dos veces ({dispositivo.type})",
              iguales and np.isfinite(salidas[0]).all() and len(np.unique(salidas[0])) > 1
              and reg["lotes_corridos"] == [max_lotes, max_lotes],
              f"idénticos: {iguales}; {len(np.unique(salidas[0]))} logits distintos en {len(va)} filas; lotes "
              f"{reg['lotes_corridos']} de {reg['lotes_por_epoca']}; pérdida por época "
              f"{reg['perdida_media_por_epoca']}")
    otro = salidas[1].copy()
    otro[0] += 1e-6
    registrar("ajuste", "un logit cambiado en 1e-6 (debe fallar)", not np.array_equal(salidas[0], otro),
              f"idénticos: {np.array_equal(salidas[0], otro)}")
    return {k: reg[k] for k in ("universo", "benignos_en_el_universo", "malignos", "lotes_por_epoca",
                                "actualizaciones_por_variable_dual", "segundos_por_epoca")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dispositivo", default="cpu", choices=["cpu", "mps"])
    ap.add_argument("--filas-validacion", type=int, default=256)
    ap.add_argument("--max-lotes", type=int, default=2)
    args = ap.parse_args()
    t0 = time.perf_counter()
    informe = {"lotes": control_lotes()}
    control_capa()
    informe["ajuste"] = control_ajuste(torch.device(args.dispositivo), args.filas_validacion, args.max_lotes)
    fallos = sum(not c["como_se_esperaba"] for c in CASOS)
    informe.update({"casos": CASOS, "fallos": fallos, "rapido": False, "segundos": round(time.perf_counter() - t0, 1),
                    "ajustes": fa.ajustes(), "comando": {"interprete": os.path.relpath(sys.executable, RAIZ),
                                                         "argumentos": sys.argv}})
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(f"\n{len(CASOS) - fallos} de {len(CASOS)} casos como se esperaba; {informe['segundos']} s. "
          f"Escrito: {args.out}", flush=True)
    if fallos:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

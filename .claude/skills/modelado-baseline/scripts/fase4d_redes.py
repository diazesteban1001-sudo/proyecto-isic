#!/usr/bin/env python3
"""
fase4d_redes.py — la red mejorada de la Fase 4d, pregunta 2 (PLAN.md, decisión
de la persona del 2026-10-30). No calcula ninguna métrica: entrena y guarda
puntuaciones.

Una red por semilla y pliegue de construir_folds (5 pliegues, semillas 0 a 4, los
de la Fase 4), entrenada con el pliegue de entrenamiento y puntuando el de
validación (fase4d.entrenar_y_puntuar, con los negativos en bloques y 15 épocas).
Cada lesión recibe, en cada semilla, el logit de la red en cuya validación está.

Antes de entrenar:
  - los ajustes de la Fase 4c siguen siendo los de la prueba de tiempo
    (fase4c.comprobar_ajustes) y las épocas son 15;
  - los controles completos (test_fase4d_controles.py, sin --rapido) están en
    --controles con 0 fallos;
  - los pliegues tienen la huella de outputs/fase4-m2-vs-m1.json.
Después de cada red, se detiene si alguna época repitió negativos.

Como fase4c_redes.py: cada red se guarda en una parte de --partes-dir con el
SHA-256 del código que la produjo, y la corrida se reanuda con las partes de ese
mismo código; al terminar, fase4c.ensamblar une las partes por isic_id y se
escribe --out (en data/, que no se versiona) con su procedencia al lado.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4d_redes.py \\
        --controles data/fase4d-controles.json --partes-dir data/fase4d-redes \\
        --out data/fase4d-puntuaciones-red-mejorada.csv.gz
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import sys
import time

import h5py
import numpy as np
import pandas as pd
import torch
import torchvision

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4c  # noqa: E402
import fase4c_redes as f4cr  # noqa: E402
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
CODIGO = ["fase4d.py", "fase4d_redes.py", "fase4c.py", "prueba_tiempo_red_imagen.py", "train_and_evaluate.py"]
G, Y = "patient_id", "target"


def huella_codigo():
    return {c: f4cr.sha256(os.path.join(AQUI, c)) for c in CODIGO}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(5)))
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--controles", required=True)
    ap.add_argument("--partes-dir", required=True)
    ap.add_argument("--out", required=True, help="data/….csv.gz")
    args = ap.parse_args()
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    with open(fase4c.PRUEBA_DE_TIEMPO, encoding="utf-8") as f:
        diferencias = fase4c.comprobar_ajustes(json.load(f))
    if diferencias or fase4d.EPOCAS != 15:
        raise SystemExit(f"ERROR: los ajustes no son los de la Fase 4d: {diferencias}, épocas {fase4d.EPOCAS}")
    controles = f4cr.leer_controles(args.controles)
    destino = f4cr.en_data(args.out)
    partes_dir = f4cr.en_data(args.partes_dir)
    os.makedirs(partes_dir, exist_ok=True)
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")
    codigo = huella_codigo()

    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    isic, y = df["isic_id"].to_numpy(), df[Y].to_numpy()
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        ref_huellas = json.load(f)["folds"]["sha256_por_semilla"]

    filas, registros, alineacion, huellas = [], [], {}, {}
    with h5py.File(HDF5, "r") as h5:
        for semilla in args.semillas:
            folds = construir_folds(df, G, Y, args.n_splits, semilla)
            huellas[str(semilla)] = f4.huella_folds(folds, len(df))
            if huellas[str(semilla)] != ref_huellas[str(semilla)]:
                raise SystemExit(f"ERROR: los pliegues de la semilla {semilla} no son los de {REF_PLIEGUES}.")
            asignacion = np.full(len(df), -1)
            partes = {}
            for k, (tr, va) in enumerate(folds):
                asignacion[va] = k

                def entrenar(tr=tr, va=va):
                    logit, reg = fase4d.entrenar_y_puntuar(h5, isic, y, tr, va, semilla, dispositivo)
                    return isic[va], logit, reg
                ids, logit, reg, leida = f4cr.parte(partes_dir, semilla, k, None, codigo, entrenar)
                if reg["negativos"] != "bloques" or reg["negativos_en_mas_de_una_epoca"] != 0 \
                        or reg["epocas"] != fase4d.EPOCAS:
                    raise SystemExit(f"ERROR: la red s{semilla}-p{k} no usó un bloque de negativos distinto en cada "
                                     f"una de sus {fase4d.EPOCAS} épocas: {reg['negativos']}, "
                                     f"{reg['negativos_en_mas_de_una_epoca']} repetidos, {reg['epocas']} épocas.")
                registros.append(reg)
                estado = "leída" if leida else f"{reg['segundos_total']} s · épocas {reg['segundos_por_epoca']}"
                print(f"Semilla {semilla}, pliegue {k}: {estado}", flush=True)
                partes[k] = (ids, logit)
            unido = fase4c.ensamblar(partes, isic, asignacion)
            alineacion[str(semilla)] = {"filas": int(len(df)), "una_puntuacion_por_fila": True}
            filas.append(pd.DataFrame({"semilla": semilla, "pliegue": asignacion, "isic_id": isic, "logit": unido}))

    tabla = pd.concat(filas, ignore_index=True)
    tabla["puntuacion"] = fase4c.probabilidad(tabla["logit"].to_numpy())
    tabla.to_csv(destino, index=False, float_format="%.17g", compression="gzip")
    leida = pd.read_csv(destino, float_precision="round_trip")
    for c in ("logit", "puntuacion"):
        if leida[c].to_numpy(np.float64).tobytes() != tabla[c].to_numpy(np.float64).tobytes():
            raise SystemExit(f"ERROR: {destino} no se relee igual que se escribió ({c}).")

    import sklearn
    tiempos = [r["segundos_total"] for r in registros]
    procedencia = {
        "archivo": os.path.relpath(destino, RAIZ),
        "sha256": f4cr.sha256(destino),
        "como_leerlo": "pd.read_csv(archivo, float_precision='round_trip')",
        "sha256_de_las_puntuaciones_float64": hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes())
        .hexdigest(),
        "filas": int(len(tabla)),
        "columnas": list(tabla.columns),
        "que_es": ("logit y probabilidad (sigmoide en float64) de la red mejorada de la Fase 4d de PLAN.md, "
                   "EfficientNet-B0 con 15 épocas y los negativos en bloques; en cada semilla, cada lesión con la "
                   "puntuación de la red de su pliegue de validación"),
        "internos": False,
        "semillas": args.semillas,
        "pliegues": args.n_splits,
        "pliegues_con_la_huella_de": os.path.relpath(REF_PLIEGUES, RAIZ),
        "huellas_de_pliegues": huellas,
        "alineacion": alineacion,
        "datos": datos,
        "controles": controles,
        "ajustes": {"lado_px": fase4c.LADO, "tasa": fase4c.TASA, "lote": fase4c.LOTE, "epocas": fase4d.EPOCAS,
                    "negativos_por_positivo": fase4c.NEGATIVOS_POR_POSITIVO,
                    "iguales_a": os.path.relpath(fase4c.PRUEBA_DE_TIEMPO, RAIZ) + ", salvo las épocas",
                    "aumento_de_datos": "volteos horizontales y verticales al azar, solo al entrenar",
                    "negativos": ("en bloques de 20 por positivo, barajados una vez con la semilla externa; cada "
                                  "época, un bloque distinto")},
        "redes": registros,
        "segundos_por_red": {"mediana": round(float(np.median(tiempos)), 1), "minimo": round(float(min(tiempos)), 1),
                             "maximo": round(float(max(tiempos)), 1)},
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sha256_del_codigo": codigo,
        "versiones": {"python": platform.python_version(), "torch": torch.__version__,
                      "torchvision": torchvision.__version__, "numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "h5py": h5py.__version__},
        "segundos_total": round(time.perf_counter() - t_total, 1),
    }
    with open(os.path.splitext(os.path.splitext(destino)[0])[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(procedencia, f, ensure_ascii=False, indent=2)
    print(f"Escrito: {procedencia['archivo']}, {procedencia['filas']} filas, {len(registros)} redes; "
          f"{procedencia['segundos_total']} s", flush=True)


if __name__ == "__main__":
    main()

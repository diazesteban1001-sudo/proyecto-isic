#!/usr/bin/env python3
"""
fase4c_redes.py — las redes de la Fase 4c (PLAN.md, decisión de la persona del
2026-10-22). No calcula ninguna métrica: entrena y guarda puntuaciones.

Sin --internos: una red por semilla y pliegue de construir_folds (5 pliegues,
semillas 0 a 9, los de la Fase 4), entrenada con el pliegue de entrenamiento y
puntuando el de validación (fase4c.entrenar_y_puntuar). Cada lesión recibe, en
cada semilla, el logit de la red en cuya validación está.

Con --internos (el control del atajo, semilla 0): en cada pliegue externo, la
validación interna de M4b (apilado_imagen.py: StratifiedGroupKFold de 5 pliegues
por paciente, con la semilla externa) sobre el pliegue de entrenamiento; una red
por pliegue interno, que puntúa su parte de validación. Juntas cubren el pliegue
de entrenamiento externo, una vez cada fila.

Antes de entrenar:
  - los ajustes coinciden con outputs/prueba-tiempo-red-imagen.json
    (fase4c.comprobar_ajustes);
  - los controles completos (test_fase4c_controles.py, sin --rapido) están en
    --controles con 0 fallos;
  - los pliegues tienen la huella de outputs/fase4-m2-vs-m1.json.

Cada red se guarda en una parte de --partes-dir con el SHA-256 del código que la
produjo; si la corrida se corta, se reanuda con las partes de ese mismo código y
se detiene si alguna es de otro. Al terminar, fase4c.ensamblar une las partes por
isic_id —cada fila exactamente una vez, de su red— y se escribe --out (en data/,
que no se versiona) con su procedencia al lado: el SHA-256 del archivo y de las
puntuaciones en float64, la alineación por semilla, el registro de cada red con
sus tiempos, los controles, el código, la orden y las versiones.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4c_redes.py \\
        --controles data/fase4c-controles.json --partes-dir data/fase4c-redes \\
        --out data/fase4c-puntuaciones-red.csv.gz
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4c_redes.py --internos \\
        --semillas 0 --controles data/fase4c-controles.json --partes-dir data/fase4c-redes-internas \\
        --out data/fase4c-puntuaciones-red-internas.csv.gz
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
import ganador_m3  # noqa: E402
from apilado_imagen import PLIEGUES_INTERNOS  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
CODIGO = ["fase4c.py", "fase4c_redes.py", "prueba_tiempo_red_imagen.py", "apilado_imagen.py", "train_and_evaluate.py"]
G, Y = "patient_id", "target"


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def huella_codigo():
    return {c: sha256(os.path.join(AQUI, c)) for c in CODIGO}


def en_data(ruta):
    destino = os.path.realpath(ruta)
    if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "data")) + os.sep):
        raise SystemExit(f"ERROR: {ruta} tiene que estar en data/, que no se versiona.")
    return destino


def leer_controles(ruta):
    with open(ruta, encoding="utf-8") as f:
        c = json.load(f)
    if c.get("rapido") or c.get("fallos") != 0:
        raise SystemExit(f"ERROR: {ruta} no es la corrida completa de los controles con 0 fallos "
                         f"(rapido={c.get('rapido')}, fallos={c.get('fallos')}).")
    return {"archivo": os.path.relpath(ruta, RAIZ), "sha256": sha256(ruta), "casos": len(c["casos"]),
            "fallos": c["fallos"]}


def parte(directorio, semilla, k, j, codigo, entrenar):
    """La red (semilla, k[, j]): la lee si ya está, con el mismo código; si no, la
    entrena con entrenar() y la guarda."""
    nombre = f"s{semilla}-p{k}" + ("" if j is None else f"-i{j}")
    ruta_npz, ruta_json = os.path.join(directorio, nombre + ".npz"), os.path.join(directorio, nombre + ".json")
    if os.path.exists(ruta_npz) and os.path.exists(ruta_json):
        with open(ruta_json, encoding="utf-8") as f:
            reg = json.load(f)
        if reg["sha256_del_codigo"] != codigo or reg["sha256_npz"] != sha256(ruta_npz):
            raise SystemExit(f"ERROR: la parte {nombre} es de otro código o cambió; borre {directorio} para rehacerla.")
        z = np.load(ruta_npz)
        return z["isic_id"], z["logit"], reg, True
    ids, logit, reg = entrenar()
    np.savez(ruta_npz, isic_id=np.asarray(ids, dtype=str), logit=logit)
    reg = {**reg, "red": nombre, "pliegue": int(k), "pliegue_interno": None if j is None else int(j),
           "sha256_del_codigo": codigo, "sha256_npz": sha256(ruta_npz),
           "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    return ids, logit, reg, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--internos", action="store_true")
    ap.add_argument("--controles", required=True)
    ap.add_argument("--partes-dir", required=True)
    ap.add_argument("--out", required=True, help="data/….csv.gz")
    args = ap.parse_args()
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    with open(fase4c.PRUEBA_DE_TIEMPO, encoding="utf-8") as f:
        diferencias = fase4c.comprobar_ajustes(json.load(f))
    if diferencias:
        raise SystemExit(f"ERROR: los ajustes no son los de la prueba de tiempo: {diferencias}")
    controles = leer_controles(args.controles)
    destino = en_data(args.out)
    partes_dir = en_data(args.partes_dir)
    os.makedirs(partes_dir, exist_ok=True)
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")
    codigo = huella_codigo()

    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    isic, y, grupos = df["isic_id"].to_numpy(), df[Y].to_numpy(), df[G].to_numpy()
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        ref_huellas = json.load(f)["folds"]["sha256_por_semilla"]

    tablas, registros, alineacion, huellas = [], [], {}, {}
    with h5py.File(HDF5, "r") as h5:
        for semilla in args.semillas:
            folds = construir_folds(df, G, Y, args.n_splits, semilla)
            huellas[str(semilla)] = f4.huella_folds(folds, len(df))
            if huellas[str(semilla)] != ref_huellas[str(semilla)]:
                raise SystemExit(f"ERROR: los pliegues de la semilla {semilla} no son los de {REF_PLIEGUES}.")
            for k, (tr, va) in enumerate(folds):
                if not args.internos:
                    def entrenar(tr=tr, va=va):
                        logit, reg = fase4c.entrenar_y_puntuar(h5, isic, y, tr, va, semilla, dispositivo)
                        return isic[va], logit, reg
                    ids, logit, reg, leida = parte(partes_dir, semilla, k, None, codigo, entrenar)
                    registros.append(reg)
                    estado = "leída" if leida else f"{reg['segundos_total']} s · épocas {reg['segundos_por_epoca']}"
                    print(f"Semilla {semilla}, pliegue {k}: {estado}", flush=True)
                    tablas.append((semilla, k, ids, logit))
                    continue
                interna = StratifiedGroupKFold(n_splits=PLIEGUES_INTERNOS, shuffle=True, random_state=semilla)
                asign = np.full(len(tr), -1)
                partes = {}
                for j, (itr, iva) in enumerate(interna.split(tr, y[tr], groups=grupos[tr])):
                    asign[iva] = j

                    def entrenar(itr=itr, iva=iva):
                        logit, reg = fase4c.entrenar_y_puntuar(h5, isic, y, tr[itr], tr[iva], semilla, dispositivo)
                        return isic[tr[iva]], logit, reg
                    ids, logit, reg, leida = parte(partes_dir, semilla, k, j, codigo, entrenar)
                    registros.append(reg)
                    partes[j] = (ids, logit)
                    print(f"Semilla {semilla}, pliegue {k}, interno {j}: "
                          f"{'leída' if leida else str(reg['segundos_total']) + ' s'}", flush=True)
                unido = fase4c.ensamblar(partes, isic[tr], asign)
                alineacion[f"{semilla}-{k}"] = {"filas": int(len(tr)), "una_puntuacion_por_fila": True}
                tablas.append((semilla, k, isic[tr], unido))

    # Ensamblado y alineación: sin --internos, por semilla sobre todo el desarrollo.
    filas = []
    if not args.internos:
        for semilla in args.semillas:
            folds = construir_folds(df, G, Y, args.n_splits, semilla)
            asignacion = np.full(len(df), -1)
            for k, (_, va) in enumerate(folds):
                asignacion[va] = k
            partes = {k: (ids, logit) for s_, k, ids, logit in tablas if s_ == semilla}
            unido = fase4c.ensamblar(partes, isic, asignacion)
            alineacion[str(semilla)] = {"filas": int(len(df)), "una_puntuacion_por_fila": True}
            filas.append(pd.DataFrame({"semilla": semilla, "pliegue": asignacion, "isic_id": isic, "logit": unido}))
    else:
        for semilla, k, ids, unido in tablas:
            filas.append(pd.DataFrame({"semilla": semilla, "pliegue": k, "isic_id": ids, "logit": unido}))
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
        "sha256": sha256(destino),
        "como_leerlo": "pd.read_csv(archivo, float_precision='round_trip')",
        "sha256_de_las_puntuaciones_float64": hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes())
        .hexdigest(),
        "filas": int(len(tabla)),
        "columnas": list(tabla.columns),
        "que_es": ("logit y probabilidad (sigmoide en float64) de EfficientNet-B0 entrenada sobre los recortes, "
                   "Fase 4c de PLAN.md; " + ("en cada pliegue externo de la semilla, puntuaciones fuera de pliegue "
                                            "de la validación interna de M4b sobre su pliegue de entrenamiento"
                                            if args.internos else "en cada semilla, cada lesión con la puntuación "
                                            "de la red de su pliegue de validación")),
        "internos": args.internos,
        "semillas": args.semillas,
        "pliegues": args.n_splits,
        "pliegues_con_la_huella_de": os.path.relpath(REF_PLIEGUES, RAIZ),
        "huellas_de_pliegues": huellas,
        "alineacion": alineacion,
        "datos": datos,
        "controles": controles,
        "ajustes": {"lado_px": fase4c.LADO, "tasa": fase4c.TASA, "lote": fase4c.LOTE, "epocas": fase4c.EPOCAS,
                    "negativos_por_positivo": fase4c.NEGATIVOS_POR_POSITIVO,
                    "iguales_a": os.path.relpath(fase4c.PRUEBA_DE_TIEMPO, RAIZ),
                    "aumento_de_datos": "volteos horizontales y verticales al azar, solo al entrenar",
                    "submuestra_de_negativos": "nueva en cada época, con la semilla externa"},
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

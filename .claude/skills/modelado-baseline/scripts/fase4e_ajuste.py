#!/usr/bin/env python3
"""
fase4e_ajuste.py — el paso 2 de la Fase 4e de PLAN.md: el ajuste fino de cada
red de la 4e con la pérdida de pAUC unilateral de LibAUC, sobre las clases
invertidas. No calcula ninguna métrica: ajusta y guarda puntuaciones.

Los ajustes son los de PLAN.md, Fase 4e, «Los ajustes del paso 2», fijados el
2026-11-01 por la regla de la persona (Zhu et al. 2022, después la documentación
de SOPA en LibAUC 2.0.1, después el criterio más simple):
  - parte de los pesos de la red de la 4e del mismo pliegue (fase4e_redes.py),
    reinicializa la capa de salida con la inicialización por defecto de PyTorch,
    tras fijar la semilla de la red, y ajusta todas las capas;
  - EPOCAS_AJUSTE épocas; la época e usa todos los positivos y el conjunto e del
    mismo reparto de negativos del entrenamiento (fase4e.conjuntos_de_negativos
    con la semilla externa);
  - los lotes los arma DualSampler, con sampling_rate PROPORCION y su random_seed
    por defecto, sobre las clases invertidas: la benigna lleva la etiqueta 1;
  - pAUC_CVaR_Loss con BETA, MARGEN, ETA y la bisagra cuadrada, una sola para las
    dos épocas, con una variable dual por imagen; recibe el logit negado;
  - SOPA en modo 'adam', TASA_AJUSTE constante y DECAIMIENTO_AJUSTE; los demás
    argumentos, los de su documentación; clip_value, el de la librería;
  - los aumentos, los procesos de datos y la predicción, los de fase4e.

ajustar_y_puntuar() devuelve el logit de la red ajustada para filas_pred y un
registro con cuántas veces se actualizó cada variable dual. max_lotes corta
cada época tras esos lotes: solo para la prueba de test_fase4e_ajuste.py.

Como fase4e_redes.py: cada red ajustada se guarda en una parte de --partes-dir
con el SHA-256 del código que la produjo, y la corrida se reanuda con las
partes de ese mismo código; al terminar se escribe --out (en data/) con su
procedencia al lado. Antes de cada red se comprueba el SHA-256 de los pesos de
partida contra su parte de --redes-dir.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase4e_ajuste.py \\
        --semillas 0 --controles data/fase4e-controles.json --redes-dir data/fase4e-redes \\
        --partes-dir data/fase4e-ajuste --out data/fase4e-puntuaciones-red-ajustada-exploracion.csv.gz
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import platform
import sys
import time

import numpy as np
import pandas as pd
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4c  # noqa: E402
import fase4c_redes as f4cr  # noqa: E402
import fase4e  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from prueba_tiempo_red_imagen import red, sincronizar  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
CODIGO = ["fase4e.py", "fase4e_ajuste.py", "prueba_tiempo_red_imagen.py", "train_and_evaluate.py"]
G, Y = "patient_id", "target"

EPOCAS_AJUSTE = 2
TASA_AJUSTE = 1e-3
DECAIMIENTO_AJUSTE = 2e-4
MARGEN = 1.0
BETA = 0.2
ETA = 0.1
PROPORCION = 0.5
SEMILLA_MUESTREO = 2023  # random_seed por defecto de DualSampler


class RecortesConIndice(fase4e.Recortes):
    """Como fase4e.Recortes, con la posición del caso: pAUC_CVaR_Loss la necesita
    para su variable dual."""

    def __getitem__(self, i):
        x, y = super().__getitem__(i)
        return x, y, i


class LotesPorEpoca(torch.utils.data.Sampler):
    """Las posiciones de la época vigente, en el orden que dio DualSampler."""

    def __init__(self, por_epoca):
        self.por_epoca, self.epoca = por_epoca, 0

    def __iter__(self):
        return iter(self.por_epoca[self.epoca].tolist())

    def __len__(self):
        return len(self.por_epoca[self.epoca])


def orden_de_los_lotes(etiquetas, filas_ent, semilla, lote=fase4e.LOTE):
    """El universo del ajuste (filas: todos los positivos y los conjuntos de las
    épocas), sus etiquetas invertidas y, por época, las posiciones en el universo
    en el orden de DualSampler."""
    from libauc.sampler import DualSampler
    filas_ent = np.asarray(filas_ent)
    y_ent = etiquetas[filas_ent]
    pos, neg = filas_ent[y_ent == 1], filas_ent[y_ent == 0]
    grupos = fase4e.conjuntos_de_negativos(neg, fase4e.CONJUNTOS, np.random.default_rng(semilla))
    universo = np.concatenate([pos] + [grupos[e] for e in range(EPOCAS_AJUSTE)])
    invertidas = (1 - etiquetas[universo]).astype(np.int64)
    pos_en_universo = np.arange(len(pos))
    inicio, por_epoca = len(pos), []
    for e in range(EPOCAS_AJUSTE):
        en_universo = np.concatenate([pos_en_universo, inicio + np.arange(len(grupos[e]))])
        inicio += len(grupos[e])
        muestreo = DualSampler(None, lote, labels=invertidas[en_universo], shuffle=True,
                               sampling_rate=PROPORCION, random_seed=SEMILLA_MUESTREO)
        por_epoca.append(en_universo[np.fromiter(iter(muestreo), dtype=np.int64)])
    return universo, invertidas, por_epoca


def comprobar_lotes(invertidas, por_epoca, lote=fase4e.LOTE):
    """Que cada lote tiene la mitad de cada clase. Devuelve (bien, detalle)."""
    malos = 0
    for orden in por_epoca:
        n = len(orden) // lote
        if len(orden) % lote:
            return False, f"una época de {len(orden)} posiciones no se reparte en lotes de {lote}"
        unos = invertidas[orden[:n * lote]].reshape(n, lote).sum(axis=1)
        malos += int((unos != lote // 2).sum())
    return malos == 0, f"{malos} lotes sin {lote // 2} casos de cada clase"


def actualizaciones_duales(invertidas, por_epoca):
    """Cuántas veces entra cada benigno del universo (una variable dual cada uno)."""
    veces = np.bincount(np.concatenate(por_epoca), minlength=len(invertidas))[invertidas == 1]
    return {str(v): int(c) for v, c in zip(*np.unique(veces, return_counts=True))}


def capa_nueva(modelo, semilla):
    """La capa de salida con la inicialización por defecto de PyTorch, creada en CPU
    tras fijar la semilla de la red."""
    vieja = modelo.classifier[1]
    torch.manual_seed(semilla)
    modelo.classifier[1] = torch.nn.Linear(vieja.in_features, vieja.out_features).to(vieja.weight.device)
    return modelo


def ajustar_y_puntuar(hdf5, isic, etiquetas, filas_ent, filas_pred, semilla, dispositivo, pesos,
                      trabajadores=fase4e.TRABAJADORES, max_lotes=None):
    from libauc.losses import pAUC_CVaR_Loss
    from libauc.optimizers import SOPA
    t_inicio = time.perf_counter()
    filas_ent, filas_pred = np.asarray(filas_ent), np.asarray(filas_pred)
    if np.intersect1d(filas_ent, filas_pred).size:
        raise SystemExit("ERROR: la red puntuaría filas con las que se ajusta.")
    universo, invertidas, por_epoca = orden_de_los_lotes(etiquetas, filas_ent, semilla)
    bien, detalle = comprobar_lotes(invertidas, por_epoca)
    if not bien:
        raise SystemExit(f"ERROR: los lotes del ajuste no traen las dos clases por mitades: {detalle}.")
    ds = RecortesConIndice(hdf5, isic[universo], invertidas, fase4e.aumentos_entrenamiento())
    muestreo = LotesPorEpoca(por_epoca)
    carga = fase4e.cargador(ds, fase4e.LOTE, trabajadores, semilla=semilla, muestreo=muestreo,
                            persistente=trabajadores > 0)

    modelo, pesos_imagenet = red(dispositivo)
    modelo.load_state_dict(torch.load(pesos, map_location=dispositivo))
    capa_nueva(modelo, semilla)
    perdida = pAUC_CVaR_Loss(data_len=len(universo), pos_len=int(invertidas.sum()), margin=MARGEN, beta=BETA,
                             eta=ETA, surr_loss="squared_hinge", device=dispositivo)
    opt = SOPA(modelo.parameters(), mode="adam", lr=TASA_AJUSTE, weight_decay=DECAIMIENTO_AJUSTE,
               betas=(0.9, 0.999), eps=1e-8, amsgrad=False, epoch_decay=0, device=dispositivo)

    s_epoca, perdida_media, lotes_corridos = [], [], []
    modelo.train()
    for e in range(EPOCAS_AJUSTE):
        muestreo.epoca = e
        t0, suma, n = time.perf_counter(), 0.0, 0
        for xb, yb, ib in carga:
            xb, yb, ib = xb.to(dispositivo), yb.to(dispositivo), ib.to(dispositivo)
            loss = perdida(-modelo(xb), yb.view(-1, 1), ib)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            suma, n = suma + float(loss.detach()), n + 1
            if max_lotes is not None and n >= max_lotes:
                break
        sincronizar()
        s_epoca.append(round(time.perf_counter() - t0, 3))
        perdida_media.append(round(suma / n, 6))
        lotes_corridos.append(n)
    del carga
    duales = perdida.u_pos.detach().cpu().numpy().ravel()[invertidas == 1]

    t0 = time.perf_counter()
    logit = fase4e.predecir(modelo, hdf5, isic[filas_pred], dispositivo, trabajadores=trabajadores)
    s_pred = round(time.perf_counter() - t0, 3)
    del modelo, opt
    if dispositivo.type == "mps":
        torch.mps.empty_cache()
    registro = {
        "semilla": int(semilla), "ajuste_fino": True, "pesos_de_partida": os.path.relpath(pesos, RAIZ),
        "sha256_pesos_de_partida": f4cr.sha256(pesos), "sha256_pesos_imagenet": pesos_imagenet["sha256"],
        "universo": int(len(universo)), "benignos_en_el_universo": int(invertidas.sum()),
        "malignos": int((invertidas == 0).sum()), "epocas": EPOCAS_AJUSTE,
        "lotes_por_epoca": [int(math.ceil(len(o) / fase4e.LOTE)) for o in por_epoca],
        "lotes_corridos": lotes_corridos, "imagenes_por_epoca": [int(len(o)) for o in por_epoca],
        "lotes_con_las_dos_clases_por_mitades": True,
        "actualizaciones_por_variable_dual": actualizaciones_duales(invertidas, por_epoca),
        "variables_duales_de_los_benignos": {"media": round(float(duales.mean()), 6),
                                             "minimo": round(float(duales.min()), 6),
                                             "maximo": round(float(duales.max()), 6)},
        "perdida_media_por_epoca": perdida_media, "filas_puntuadas": int(len(filas_pred)),
        "segundos_por_epoca": s_epoca, "segundos_prediccion": s_pred,
        "segundos_total": round(time.perf_counter() - t_inicio, 3),
    }
    return logit, registro


def ajustes():
    import libauc
    import importlib.metadata as md
    return {"epocas": EPOCAS_AJUSTE, "conjuntos_por_epoca": list(range(EPOCAS_AJUSTE)), "lote": fase4e.LOTE,
            "optimizador": {"nombre": "libauc.optimizers.SOPA", "mode": "adam", "lr": TASA_AJUSTE,
                            "weight_decay": DECAIMIENTO_AJUSTE, "betas": [0.9, 0.999], "eps": 1e-8,
                            "amsgrad": False, "epoch_decay": 0, "clip_value": "el de la librería, no se pasa",
                            "calendario": "tasa constante"},
            "perdida": {"nombre": "libauc.losses.pAUC_CVaR_Loss", "beta": BETA, "margin": MARGEN, "eta": ETA,
                        "surr_loss": "squared_hinge", "entrada": "el logit negado; etiqueta 1 la benigna"},
            "muestreo": {"nombre": "libauc.sampler.DualSampler", "sampling_rate": PROPORCION,
                         "random_seed": SEMILLA_MUESTREO, "shuffle": True},
            "capa_de_salida": "reinicializada: torch.nn.Linear nueva tras torch.manual_seed(semilla)",
            "libauc": {"version": md.version("libauc"), "licencia": "MIT",
                       "archivo": os.path.relpath(libauc.__file__, RAIZ)},
            "fuente": "PLAN.md, Fase 4e, «Los ajustes del paso 2» (2026-11-01)"}


def huella_codigo():
    return {c: f4cr.sha256(os.path.join(AQUI, c)) for c in CODIGO}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, nargs="+", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--controles", required=True)
    ap.add_argument("--redes-dir", required=True, help="las partes de fase4e_redes.py, con sus pesos")
    ap.add_argument("--partes-dir", required=True)
    ap.add_argument("--out", required=True, help="data/….csv.gz")
    args = ap.parse_args()
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()
    controles = f4cr.leer_controles(args.controles)
    destino = f4cr.en_data(args.out)
    redes_dir = f4cr.en_data(args.redes_dir)
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
    for semilla in args.semillas:
        folds = construir_folds(df, G, Y, args.n_splits, semilla)
        huellas[str(semilla)] = f4.huella_folds(folds, len(df))
        if huellas[str(semilla)] != ref_huellas[str(semilla)]:
            raise SystemExit(f"ERROR: los pliegues de la semilla {semilla} no son los de {REF_PLIEGUES}.")
        asignacion = np.full(len(df), -1)
        partes = {}
        for k, (tr, va) in enumerate(folds):
            asignacion[va] = k
            nombre = f"s{semilla}-p{k}"
            with open(os.path.join(redes_dir, nombre + ".json"), encoding="utf-8") as f:
                de_partida = json.load(f)
            pesos = os.path.join(redes_dir, nombre + ".pt")
            if f4cr.sha256(pesos) != de_partida["sha256_pesos_guardados"]:
                raise SystemExit(f"ERROR: los pesos de {pesos} no son los de su parte.")

            def entrenar(tr=tr, va=va, pesos=pesos):
                logit, reg = ajustar_y_puntuar(HDF5, isic, y, tr, va, semilla, dispositivo, pesos)
                return isic[va], logit, reg
            ids, logit, reg, leida = f4cr.parte(partes_dir, semilla, k, None, codigo, entrenar)
            if reg["sha256_pesos_de_partida"] != de_partida["sha256_pesos_guardados"] \
                    or reg["lotes_corridos"] != reg["lotes_por_epoca"]:
                raise SystemExit(f"ERROR: la red ajustada {nombre} no partió de sus pesos o no corrió todos sus "
                                 f"lotes: {reg['lotes_corridos']} de {reg['lotes_por_epoca']}.")
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

    import h5py
    import sklearn
    import torchvision
    tiempos = [r["segundos_total"] for r in registros]
    procedencia = {
        "archivo": os.path.relpath(destino, RAIZ),
        "sha256": f4cr.sha256(destino),
        "como_leerlo": "pd.read_csv(archivo, float_precision='round_trip')",
        "sha256_de_las_puntuaciones_float64": hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes())
        .hexdigest(),
        "filas": int(len(tabla)),
        "columnas": list(tabla.columns),
        "que_es": ("logit y probabilidad (sigmoide en float64) de la red de la Fase 4e de PLAN.md tras el ajuste "
                   "fino del paso 2 con pAUC_CVaR_Loss sobre las clases invertidas; en cada semilla, cada lesión con "
                   "la puntuación de la red de su pliegue de validación"),
        "ajuste_fino": True,
        "internos": False,
        "redes_de_partida": os.path.relpath(redes_dir, RAIZ),
        "semillas": args.semillas,
        "pliegues": args.n_splits,
        "pliegues_con_la_huella_de": os.path.relpath(REF_PLIEGUES, RAIZ),
        "huellas_de_pliegues": huellas,
        "alineacion": alineacion,
        "datos": datos,
        "controles": controles,
        "ajustes": ajustes(),
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

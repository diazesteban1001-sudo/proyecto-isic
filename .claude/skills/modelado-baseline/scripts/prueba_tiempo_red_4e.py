#!/usr/bin/env python3
"""
prueba_tiempo_red_4e.py — prueba de tiempo de la red de la Fase 4e (PLAN.md,
«Presupuesto de cómputo»), antes de la exploración. **No calcula ninguna métrica.**

En la semilla 0, pliegue 0 de construir_folds (los pliegues de la Fase 4, con la
huella de outputs/fase4-m2-vs-m1.json), entrena la red de la 4e con su receta
completa (fase4e.entrenar_y_puntuar, calendario de EPOCAS épocas) durante
--epocas-medidas épocas, y cronometra cada una en MPS. Después cronometra la pasada
hacia adelante sobre todo el pliegue de validación y descarta los logits en cuanto
salen: no los guarda ni calcula nada con ellos. Las etiquetas de validación no se
leen. Los datos salen de cargar_desarrollo, que se detiene si aparece un paciente
reservado.

Con esos tiempos proyecta el total de la fase, con 5 semillas de confirmación (de
la 5 a la 9) y con 3 (de la 5 a la 7), y aplica la regla de las semillas fijada en
PLAN.md: 5 si caben en LIMITE_HORAS, 3 si no; si tampoco con 3, la fase no arranca.
Los supuestos de la proyección van en la salida.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/prueba_tiempo_red_4e.py \\
        --epocas-medidas 2 --out outputs/prueba-tiempo-red-4e
"""

import argparse
import datetime
import json
import os
import platform
import statistics
import subprocess
import sys
import time

import numpy as np
import PIL
import torch
import torchvision

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4c  # noqa: E402
import fase4e  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
REF_C6 = os.path.join(RAIZ, "outputs", "fase4d-c6-vs-m3limpio.json")
G, Y = "patient_id", "target"
LIMITE_HORAS = 45
EPOCAS_AJUSTE = 2  # el ajuste fino del paso 2
# Redes de control (PLAN.md, Fase 4e, «Controles»): dos completas (etiquetas
# barajadas y red real), dos de EPOCAS_REPRODUCIBILIDAD épocas para la
# reproducibilidad, y dos predicciones más de un pliegue (los aumentos al predecir).
CONTROL_COMPLETAS = 2
CONTROL_CORTAS = 2
EPOCAS_REPRODUCIBILIDAD = 2
CONTROL_PREDICCIONES = 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epocas-medidas", type=int, default=2)
    ap.add_argument("--out", required=True, help="ruta sin extensión, en outputs/")
    args = ap.parse_args()
    t_total = time.perf_counter()
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")
    bajo_caffeinate = fase4c.caffeinate()

    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    isic, y = df["isic_id"].to_numpy(), df[Y].to_numpy()
    folds = construir_folds(df, G, Y, 5, 0)
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        if f4.huella_folds(folds, len(df)) != json.load(f)["folds"]["sha256_por_semilla"]["0"]:
            raise SystemExit(f"ERROR: los pliegues de la semilla 0 no son los de {REF_PLIEGUES}.")
    tr, va = folds[0]

    # Entrenamiento: solo las etiquetas del pliegue de entrenamiento; sin predecir.
    _, reg = fase4e.entrenar_y_puntuar(HDF5, isic, y, tr, va, 0, dispositivo, parar_tras=args.epocas_medidas,
                                       predecir_filas=False)
    memoria_entrenando = torch.mps.driver_allocated_memory()

    # Predicción: una red nueva con los pesos de ImageNet, sobre todo el pliegue de
    # validación; los logits se descartan. El tiempo no depende de los pesos.
    torch.manual_seed(0)
    modelo, _ = fase4e.red(dispositivo)
    t0 = time.perf_counter()
    logit = fase4e.predecir(modelo, HDF5, isic[va], dispositivo)
    s_pred = time.perf_counter() - t0
    n_pred = int(len(logit))
    del logit, modelo
    memoria_prediciendo = torch.mps.driver_allocated_memory()

    epocas = reg["segundos_por_epoca"]
    t_epoca = statistics.median(epocas[1:]) if len(epocas) > 1 else epocas[0]
    arranque = max(0.0, epocas[0] - t_epoca)  # el arranque de los procesos y la primera época
    por_red = arranque + fase4e.EPOCAS * t_epoca + s_pred
    por_ajuste = EPOCAS_AJUSTE * t_epoca + s_pred
    controles = (CONTROL_COMPLETAS * por_red + CONTROL_CORTAS * (arranque + EPOCAS_REPRODUCIBILIDAD * t_epoca + s_pred)
                 + CONTROL_PREDICCIONES * s_pred)
    with open(REF_C6, encoding="utf-8") as f:
        s_c7_por_semilla = statistics.median(json.load(f)["segundos"]["por_semilla"].values())

    def total(n_semillas):
        partes = {
            "controles_de_la_red": controles,
            "exploracion_5_redes": 5 * por_red,
            "ajuste_fino_de_la_exploracion": 5 * por_ajuste,
            f"confirmacion_{5 * n_semillas}_redes": 5 * n_semillas * por_red,
            f"ajuste_fino_de_la_confirmacion_{5 * n_semillas}_redes": 5 * n_semillas * por_ajuste,
            "c7_y_comparaciones": n_semillas * s_c7_por_semilla,
        }
        return {"horas": round(sum(partes.values()) / 3600, 2),
                "partes_en_horas": {k: round(v / 3600, 2) for k, v in partes.items()}}

    con5, con3 = total(5), total(3)
    if con5["horas"] <= LIMITE_HORAS:
        regla = {"semillas_de_confirmacion": [5, 6, 7, 8, 9], "arranca": True}
    elif con3["horas"] <= LIMITE_HORAS:
        regla = {"semillas_de_confirmacion": [5, 6, 7], "arranca": True}
    else:
        regla = {"semillas_de_confirmacion": None, "arranca": False}
    regla["motivo"] = (f"PLAN.md, Fase 4e, «Regla de las semillas de confirmación»: 5 si la proyección cabe en "
                       f"{LIMITE_HORAS} horas, 3 si no; si tampoco con 3, la fase no arranca y decide la persona.")

    try:
        chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
        memoria = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
        nucleos = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True).stdout.strip())
    except Exception:
        chip, memoria, nucleos = None, None, None
    salida = {
        "que_es": ("Prueba de tiempo de la red de la Fase 4e de PLAN.md, en la semilla 0, pliegue 0, y proyección "
                   "del total de la fase. No calcula ninguna métrica: los logits de validación se descartan y sus "
                   "etiquetas no se leen."),
        "datos": datos,
        "pliegues": {"semilla": 0, "pliegue": 0, "huella_de": os.path.relpath(REF_PLIEGUES, RAIZ),
                     "filas_entrenamiento": int(len(tr)), "filas_validacion": int(len(va))},
        "receta": {"epocas": fase4e.EPOCAS, "conjuntos_de_negativos": fase4e.CONJUNTOS, "lote": fase4e.LOTE,
                   "tasa": fase4e.TASA, "decaimiento": fase4e.DECAIMIENTO, "pct_inicio": fase4e.PCT_INICIO,
                   "lado_px": fase4e.LADO, "lado_previo_px": fase4e.LADO_PREVIO,
                   "aumentos": fase4e.describir(fase4e.aumentos_entrenamiento()),
                   "prediccion": fase4e.describir(fase4e.preprocesado_prediccion()),
                   "trabajadores": fase4e.TRABAJADORES, "precision": "float32"},
        "entrenamiento": reg,
        "prediccion": {"filas": n_pred, "segundos": round(s_pred, 3),
                       "segundos_por_1000": round(1000 * s_pred / n_pred, 3), "lote": fase4e.LOTE_PREDICCION},
        "memoria_mps_bytes": {"entrenando": int(memoria_entrenando), "prediciendo": int(memoria_prediciendo)},
        "proyeccion": {
            "supuestos": [
                f"cada época de las {fase4e.EPOCAS} tarda la mediana de las medidas sin la primera, "
                f"{round(t_epoca, 3)} s; la primera incluye el arranque de los procesos, {round(arranque, 3)} s, "
                "que se suma una vez por red",
                "los pliegues de las otras semillas tienen el tamaño de este; la predicción de cada red, la "
                "medida aquí",
                f"el ajuste fino son {EPOCAS_AJUSTE} épocas del tamaño de una de entrenamiento y una predicción, "
                "por red, en la exploración y, si se elige, en la confirmación: es el caso más caro",
                f"controles de la red: {CONTROL_COMPLETAS} redes completas, {CONTROL_CORTAS} de "
                f"{EPOCAS_REPRODUCIBILIDAD} épocas y {CONTROL_PREDICCIONES} predicciones más",
                f"C7 y las comparaciones, la mediana por semilla de C6 en {os.path.relpath(REF_C6, RAIZ)}, "
                f"{s_c7_por_semilla} s",
            ],
            "segundos_por_red": round(por_red, 1), "segundos_por_ajuste_fino": round(por_ajuste, 1),
            "con_5_semillas": con5, "con_3_semillas": con3, "limite_horas": LIMITE_HORAS,
        },
        "regla_de_las_semillas": regla,
        "equipo": {"chip": chip, "memoria_bytes": memoria, "nucleos": nucleos, "dispositivo": "mps"},
        "software": {"python": platform.python_version(), "torch": torch.__version__,
                     "torchvision": torchvision.__version__, "numpy": np.__version__, "pillow": PIL.__version__},
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "segundos_corrida_total": round(time.perf_counter() - t_total, 1),
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    p = salida["proyeccion"]
    lineas = [
        "# Prueba de tiempo: la red de la Fase 4e, MPS", "",
        "Sin métricas: los logits de validación se descartan y sus etiquetas no se leen.",
        f"Equipo: {chip} · torch {torch.__version__} · torchvision {torchvision.__version__}",
        f"Entrenamiento (semilla 0, pliegue 0): {reg['positivos']} positivos + un conjunto de negativos de "
        f"{reg['tamano_de_los_conjuntos']['minimo']} a {reg['tamano_de_los_conjuntos']['maximo']} por época, "
        f"lote {fase4e.LOTE}, {fase4e.TRABAJADORES} procesos de datos",
        f"Segundos por época, {len(epocas)} medidas: {', '.join(str(e) for e in epocas)} · esperando datos "
        f"{', '.join(str(e) for e in reg['segundos_esperando_datos_por_epoca'])}",
        f"Predicción sobre {n_pred:,} imágenes: {salida['prediccion']['segundos_por_1000']} s por 1.000",
        f"Por red, {fase4e.EPOCAS} épocas y su predicción: {p['segundos_por_red']} s · ajuste fino "
        f"{p['segundos_por_ajuste_fino']} s",
        f"Proyección de la fase: {p['con_5_semillas']['horas']} h con 5 semillas de confirmación · "
        f"{p['con_3_semillas']['horas']} h con 3 (límite {LIMITE_HORAS} h)",
        f"Regla de las semillas: {regla['semillas_de_confirmacion']}; arranca: {'sí' if regla['arranca'] else 'no'}",
        "", f"Detalle y supuestos: {args.out}.json",
    ]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print("\n".join(lineas), flush=True)


if __name__ == "__main__":
    main()

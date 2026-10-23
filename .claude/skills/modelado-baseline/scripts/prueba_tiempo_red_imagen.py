#!/usr/bin/env python3
"""
prueba_tiempo_red_imagen.py — prueba de tiempo de una red de imagen entrenada
sobre los recortes, antes de decidir si cabe una fase así (2026-10-22).

Red: EfficientNet-B0 de torchvision, con los pesos IMAGENET1K_V1 y la última
capa cambiada por una salida. El preentrenamiento se comprobó contra la regla de
la Fase 2 de `PLAN.md` antes de descargar los pesos
(`referencias/efficientnet-b0-preentrenamiento.md`).

Qué hace, en este orden:
  1. Mide el lado de los recortes de todas las filas de desarrollo, leyendo la
     cabecera del JPEG, sin decodificarlo.
  2. En la semilla 0, pliegue 0 de construir_folds (train_and_evaluate.py, los
     mismos pliegues de la validación repetida), entrena la red con todos los
     positivos del pliegue de entrenamiento y NEGATIVOS_POR_POSITIVO negativos
     por cada uno, sorteados con la semilla. Cronometra cada época en MPS,
     sincronizando el dispositivo antes de parar el reloj.
  3. Cronometra la pasada hacia adelante sobre las imágenes del pliegue de
     validación y descarta las puntuaciones en cuanto salen: no las guarda ni
     calcula nada con ellas. Las etiquetas de validación no se leen.
  4. Extrapola tres escenarios con los tamaños reales de los pliegues.

**No calcula ninguna métrica** y no lee el conjunto reservado: los datos salen
de cargar_desarrollo, que se detiene si aparece un paciente reservado.

Los parámetros de entrenamiento (proporción de negativos, épocas, lote, tasa de
aprendizaje) son de la prueba, no de una fase. No hay aumento de datos.

Los pesos se leen de la caché de torch. Si torchvision no puede descargarlos
(el Python del .venv no encontró los certificados raíz el 2026-10-22), se bajan
con curl a la caché, con el nombre del archivo de la URL: el script comprueba el
prefijo del SHA-256 de todos modos.

Uso:
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/prueba_tiempo_red_imagen.py \
        --hdf5 data/train-image.hdf5 --data data/train-metadata.csv \
        --lado 128 --epocas 3 --out outputs/prueba-tiempo-red-imagen
"""

import argparse
import hashlib
import io
import json
import os
import platform
import re
import resource
import statistics
import subprocess
import sys
import time

import h5py
import numpy as np
import PIL
import torch
import torchvision
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "diseno-validacion", "scripts"))
from apilado_imagen import PLIEGUES_INTERNOS  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

PREFIJO_SHA256 = "7f5810bc"  # el que lleva el nombre del archivo de pesos en torchvision
MEDIA = [0.485, 0.456, 0.406]  # normalización de ImageNet,
DESV = [0.229, 0.224, 0.225]   # la de los pesos IMAGENET1K_V1
_NORMA = {}


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def sincronizar():
    torch.mps.synchronize()


def decodificar(f, ids, lado):
    """uint8, N × lado × lado × 3: RGB y redimensión bicúbica."""
    return np.stack([
        np.asarray(Image.open(io.BytesIO(bytes(f[i][()]))).convert("RGB").resize((lado, lado), Image.BICUBIC))
        for i in ids
    ])


def a_tensor(lote_uint8, dispositivo):
    if dispositivo not in _NORMA:
        _NORMA[dispositivo] = tuple(torch.tensor(v, device=dispositivo).view(1, 3, 1, 1) for v in (MEDIA, DESV))
    media, desv = _NORMA[dispositivo]
    x = torch.from_numpy(lote_uint8).to(dispositivo).permute(0, 3, 1, 2).float().div_(255.0)
    return (x - media) / desv


def tamanos(f, ids, lado):
    lados = []
    for i in ids:
        im = Image.open(io.BytesIO(bytes(f[i][()])))
        if im.size[0] != im.size[1]:
            raise SystemExit(f"ERROR: {i} no es cuadrada ({im.size}); la medida supone recortes cuadrados.")
        lados.append(im.size[0])
    v = np.array(lados)
    return {
        "n_imagenes": len(v),
        "todas_cuadradas": True,
        "lado_px": {"minimo": int(v.min()), "p5": float(np.percentile(v, 5)), "p25": float(np.percentile(v, 25)),
                    "mediana": float(np.median(v)), "p75": float(np.percentile(v, 75)),
                    "p95": float(np.percentile(v, 95)), "maximo": int(v.max()), "media": round(float(v.mean()), 1)},
        "fraccion_con_lado_mayor_o_igual_al_de_entrada": round(float((v >= lado).mean()), 4),
    }


def caffeinate():
    """Si caffeinate mantiene despierto el equipo por este proceso. caffeinate no
    queda en la cadena de procesos padre: se separa y deja una aserción de energía
    a nombre del PID del programa que lanzó, que es lo que se busca aquí."""
    lineas = subprocess.run(["pmset", "-g", "assertions"], capture_output=True, text=True).stdout.splitlines()
    for previa, linea in zip(lineas, lineas[1:]):
        if "caffeinate asserting on behalf of" in linea and f"(pid {os.getpid()})" in linea:
            tipo = re.search(r"\(caffeinate\): \[[^\]]*\] \S+ (\w+) named", previa)
            return {"activo": True, "asercion": tipo.group(1) if tipo else None}
    return {"activo": False, "asercion": None}


def memoria_mps():
    return torch.mps.driver_allocated_memory()


def red(dispositivo):
    pesos = EfficientNet_B0_Weights.IMAGENET1K_V1
    # torchvision comprueba el prefijo del SHA-256 solo al descargar; con el archivo
    # ya en la caché no lo hace, así que se comprueba aquí, sobre el archivo completo.
    modelo = efficientnet_b0(weights=pesos)
    modelo.classifier[1] = torch.nn.Linear(modelo.classifier[1].in_features, 1)
    ruta = os.path.join(torch.hub.get_dir(), "checkpoints", os.path.basename(pesos.url))
    h = sha256(ruta)
    if not h.startswith(PREFIJO_SHA256):
        raise SystemExit(f"ERROR: el SHA-256 de {ruta} no empieza por {PREFIJO_SHA256}: {h}")
    return modelo.to(dispositivo), {"url": pesos.url, "archivo": os.path.basename(ruta),
                                    "bytes": os.path.getsize(ruta), "sha256": h,
                                    "comprobacion": f"SHA-256 del archivo en la caché, empieza por {PREFIJO_SHA256}"}


def submuestra(tr, y, negativos_por_positivo, rng):
    pos = tr[y[tr] == 1]
    neg = tr[y[tr] == 0]
    return np.sort(np.concatenate([pos, rng.choice(neg, size=negativos_por_positivo * len(pos), replace=False)])), len(pos)


def entrenar(modelo, x_uint8, etiquetas, args, dispositivo):
    opt = torch.optim.AdamW(modelo.parameters(), lr=args.tasa)
    perdida = torch.nn.BCEWithLogitsLoss()
    yt = torch.from_numpy(etiquetas.astype(np.float32))
    g = torch.Generator().manual_seed(args.semilla)
    tiempos, pico = [], 0
    modelo.train()
    for _e in range(args.epocas):
        orden = torch.randperm(len(yt), generator=g).numpy()
        t0 = time.perf_counter()
        for i in range(0, len(orden), args.lote):
            b = orden[i: i + args.lote]
            opt.zero_grad(set_to_none=True)
            loss = perdida(modelo(a_tensor(x_uint8[b], dispositivo)).squeeze(1), yt[b].to(dispositivo))
            loss.backward()
            opt.step()
            pico = max(pico, memoria_mps())
        sincronizar()
        tiempos.append(time.perf_counter() - t0)
        pico = max(pico, memoria_mps())
    return tiempos, pico


def predecir_y_descartar(modelo, f, ids, args, dispositivo):
    """Pasada hacia adelante por bloques; cada salida se descarta en cuanto sale."""
    modelo.eval()
    t_dec = t_mod = 0.0
    pico = 0
    with torch.no_grad():
        # Calentamiento fuera del reloj: la primera tanda en eval y sin gradiente
        _ = modelo(a_tensor(decodificar(f, ids[: args.lote_prediccion], args.lado), dispositivo))
        sincronizar()
        del _
        for i in range(0, len(ids), args.bloque):
            t0 = time.perf_counter()
            bloque = decodificar(f, ids[i: i + args.bloque], args.lado)
            t_dec += time.perf_counter() - t0
            t0 = time.perf_counter()
            for j in range(0, len(bloque), args.lote_prediccion):
                salida = modelo(a_tensor(bloque[j: j + args.lote_prediccion], dispositivo))
                del salida  # no se guarda nada
            sincronizar()
            t_mod += time.perf_counter() - t0
            pico = max(pico, memoria_mps())
    return t_dec, t_mod, pico


def tamanos_de_pliegues(df, y, grupos, semillas, n_splits, con_internos):
    """Por semilla y pliegue: positivos del entrenamiento y filas de validación; y,
    si se piden, los mismos tamaños en la validación interna de apilado_imagen.py."""
    filas = []
    for s in semillas:
        for k, (tr, va) in enumerate(construir_folds(df, "patient_id", "target", n_splits, s)):
            fila = {"semilla": s, "pliegue": k, "positivos_entrenamiento": int(y[tr].sum()), "filas_validacion": len(va)}
            if con_internos:
                interna = StratifiedGroupKFold(n_splits=PLIEGUES_INTERNOS, shuffle=True, random_state=s)
                fila["internos"] = [{"positivos_entrenamiento": int(y[tr[itr]].sum()), "filas_validacion": len(iva)}
                                    for itr, iva in interna.split(tr, y[tr], groups=grupos[tr])]
            filas.append(fila)
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hdf5", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--lado", type=int, default=128)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--pliegue", type=int, default=0)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--negativos-por-positivo", type=int, default=20)
    ap.add_argument("--epocas", type=int, default=3)
    ap.add_argument("--lote", type=int, default=64)
    ap.add_argument("--tasa", type=float, default=1e-4)
    ap.add_argument("--lote-prediccion", type=int, default=256)
    ap.add_argument("--bloque", type=int, default=4096, help="imágenes que se decodifican de una vez al predecir")
    ap.add_argument("--semillas-escenario-c", type=int, default=10)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible; la prueba es en MPS.")
    dispositivo = torch.device("mps")
    torch.manual_seed(args.semilla)
    t_inicio = time.perf_counter()
    bajo_caffeinate = caffeinate()

    df, datos = cargar_desarrollo(args.data, "patient_id", args.holdout)
    ids = df["isic_id"].to_numpy()
    y = df["target"].to_numpy()
    grupos = df["patient_id"].to_numpy()

    folds = construir_folds(df, "patient_id", "target", args.n_splits, args.semilla)
    tr, va = folds[args.pliegue]
    if set(grupos[tr]) & set(grupos[va]):
        raise SystemExit("ERROR: el pliegue comparte pacientes entre entrenamiento y validación.")
    filas_ent, n_pos = submuestra(tr, y, args.negativos_por_positivo, np.random.default_rng(args.semilla))

    modelo, pesos = red(dispositivo)
    n_param = sum(p.numel() for p in modelo.parameters())

    with h5py.File(args.hdf5, "r") as f:
        t0 = time.perf_counter()
        medida = tamanos(f, ids, args.lado)
        t_tamanos = time.perf_counter() - t0

        t0 = time.perf_counter()
        x_ent = decodificar(f, ids[filas_ent], args.lado)
        t_dec_ent = time.perf_counter() - t0
        tiempos_epoca, pico_ent = entrenar(modelo, x_ent, y[filas_ent], args, dispositivo)
        del x_ent

        t_dec_val, t_mod_val, pico_val = predecir_y_descartar(modelo, f, ids[va], args, dispositivo)

    # Ritmos por imagen, de esta corrida
    n_epoca = len(filas_ent)
    s_epoca_img = statistics.median(tiempos_epoca) / n_epoca
    s_pred_img = t_mod_val / len(va)
    s_dec_img = t_dec_val / len(va)

    def horas(n_ent_lista, n_pred_lista):
        n_ent, n_pred = sum(n_ent_lista), sum(n_pred_lista)
        modelo_s = args.epocas * n_ent * s_epoca_img + n_pred * s_pred_img
        dec_s = (n_ent + n_pred) * s_dec_img
        return {"entrenamientos": len(n_ent_lista), "imagenes_por_epoca_sumadas": n_ent,
                "imagenes_predichas": n_pred, "horas_solo_modelo": round(modelo_s / 3600, 2),
                "horas_con_lectura_y_decodificacion": round((modelo_s + dec_s) / 3600, 2)}

    k = 1 + args.negativos_por_positivo
    pl_a = tamanos_de_pliegues(df, y, grupos, [args.semilla], args.n_splits, con_internos=True)
    pl_c = tamanos_de_pliegues(df, y, grupos, list(range(args.semillas_escenario_c)), args.n_splits, False)
    esc_a = horas([k * p["positivos_entrenamiento"] for p in pl_a], [p["filas_validacion"] for p in pl_a])
    ent_b = [k * p["positivos_entrenamiento"] for p in pl_a] + [k * i["positivos_entrenamiento"]
                                                                for p in pl_a for i in p["internos"]]
    pred_b = [p["filas_validacion"] for p in pl_a] + [i["filas_validacion"] for p in pl_a for i in p["internos"]]
    esc_b = horas(ent_b, pred_b)
    esc_c = horas([k * p["positivos_entrenamiento"] for p in pl_c], [p["filas_validacion"] for p in pl_c])

    chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
    memoria = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
    gb = 2 ** 30
    resultado = {
        "datos": datos,
        "que_es": ("Prueba de tiempo de una red de imagen entrenada sobre los recortes. No calcula ninguna "
                   "métrica: las puntuaciones de validación se descartan en cuanto salen y sus etiquetas no se leen."),
        "comando": {"interprete": os.path.relpath(sys.executable), "argumentos": sys.argv,
                    "caffeinate": bajo_caffeinate},
        "red": {"nombre": "EfficientNet-B0 (torchvision)", "pesos": pesos, "parametros": n_param,
                "salida": "la última capa lineal cambiada por una salida, con BCEWithLogitsLoss",
                "verificacion_del_preentrenamiento": "referencias/efficientnet-b0-preentrenamiento.md"},
        "tamanos_de_los_recortes_desarrollo": medida,
        "entrada": {"lado_px": args.lado, "preprocesado": (f"RGB, redimensión bicúbica a {args.lado}x{args.lado}, "
                                                           "normalización de ImageNet"),
                    "aumento_de_datos": "ninguno"},
        "entrenamiento": {
            "semilla": args.semilla, "pliegue": args.pliegue, "n_splits": args.n_splits,
            "pliegues": "construir_folds de train_and_evaluate.py, los mismos de validacion-repetida",
            "positivos": n_pos, "negativos_por_positivo": args.negativos_por_positivo,
            "imagenes_por_epoca": n_epoca, "epocas": args.epocas, "lote": args.lote,
            "optimizador": f"AdamW, tasa {args.tasa}, el resto por defecto", "precision": "float32",
            "segundos_lectura_y_decodificacion": round(t_dec_ent, 3),
            "segundos_por_epoca": [round(t, 3) for t in tiempos_epoca],
            "segundos_por_epoca_mediana": round(statistics.median(tiempos_epoca), 3),
        },
        "prediccion": {
            "imagenes": len(va), "lote": args.lote_prediccion, "bloque_de_decodificacion": args.bloque,
            "segundos_solo_modelo": round(t_mod_val, 3),
            "segundos_lectura_y_decodificacion": round(t_dec_val, 3),
            "segundos_por_1000_imagenes_solo_modelo": round(1000 * s_pred_img, 3),
            "segundos_por_1000_imagenes_con_lectura_y_decodificacion": round(1000 * (s_pred_img + s_dec_img), 3),
            "calentamiento": "una tanda de un lote, fuera del reloj",
        },
        "memoria": {
            "mps_pico_entrenamiento_gb": round(pico_ent / gb, 2),
            "mps_pico_prediccion_gb": round(pico_val / gb, 2),
            "mps_recomendada_maxima_gb": round(torch.mps.recommended_max_memory() / gb, 2),
            "proceso_rss_pico_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / gb, 2),
            "como_se_mide": ("MPS: torch.mps.driver_allocated_memory, el máximo de las lecturas tras cada paso de "
                             "entrenamiento y cada bloque de predicción. Proceso: ru_maxrss de getrusage."),
        },
        "equipo": {"chip": chip, "memoria_gb": round(memoria / gb, 1), "macos": platform.mac_ver()[0],
                   "dispositivo": "mps"},
        "software": {"python": platform.python_version(), "torch": torch.__version__,
                     "torchvision": torchvision.__version__, "h5py": h5py.__version__, "numpy": np.__version__,
                     "pillow": PIL.__version__},
        "segundos_medida_de_tamanos": round(t_tamanos, 3),
        "extrapolacion": {
            "ritmos_de_esta_corrida": {
                "segundos_por_imagen_y_epoca_entrenando": s_epoca_img,
                "segundos_por_imagen_prediciendo_solo_modelo": s_pred_img,
                "segundos_por_imagen_lectura_y_decodificacion": s_dec_img,
            },
            "a_1_semilla_x_5_pliegues": esc_a,
            "b_1_semilla_x_5_pliegues_con_validacion_interna": esc_b,
            "c_10_semillas_x_5_pliegues": esc_c,
            "como_se_calcula": (
                "Cada entrenamiento usa todos los positivos de su conjunto de entrenamiento y "
                f"{args.negativos_por_positivo} negativos por positivo, {args.epocas} épocas, al ritmo de la "
                "mediana de las épocas medidas; cada predicción, al ritmo de la de validación. La lectura y "
                "decodificación se cuenta una vez por imagen de cada entrenamiento y de cada predicción, al ritmo "
                "de la de validación. (a) y (c): por pliegue, un entrenamiento sobre el pliegue de entrenamiento y "
                "una predicción sobre el de validación. (b): además, la validación interna de apilado_imagen.py "
                f"({PLIEGUES_INTERNOS} pliegues StratifiedGroupKFold por paciente, con la semilla externa): por "
                "pliegue interno, un entrenamiento y una predicción sobre su parte de validación, que juntas "
                "cubren el pliegue de entrenamiento externo."
            ),
            "tamanos_de_pliegues_a_y_b": pl_a,
            "tamanos_de_pliegues_c": pl_c,
            "que_no_incluye": ("El ajuste de M3 limpio y de cualquier modelo tabular, el aumento de datos, la "
                               "elección de hiperparámetros y el efecto de solapar decodificación y modelo. Supone "
                               "el mismo ritmo por imagen sea cual sea el tamaño del conjunto."),
        },
        "segundos_corrida_total": round(time.perf_counter() - t_inicio, 1),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    e, p, m = resultado["entrenamiento"], resultado["prediccion"], resultado["memoria"]
    lad = medida["lado_px"]

    def linea(nombre, esc):
        return (f"{nombre}: {esc['horas_solo_modelo']} h solo modelo · "
                f"{esc['horas_con_lectura_y_decodificacion']} h con lectura y decodificación "
                f"({esc['entrenamientos']} entrenamientos)")

    lineas = [
        f"# Prueba de tiempo: EfficientNet-B0 entrenada sobre los recortes, MPS",
        "Sin métricas: las puntuaciones de validación se descartan y sus etiquetas no se leen.",
        f"Equipo: {chip}, {resultado['equipo']['memoria_gb']} GB · torch {torch.__version__} · "
        f"torchvision {torchvision.__version__}",
        f"Recortes de desarrollo ({medida['n_imagenes']:,}, cuadrados): lado mediano {lad['mediana']} px, "
        f"p5 {lad['p5']}, p95 {lad['p95']} · entrada {args.lado}x{args.lado}",
        f"Entrenamiento (semilla {args.semilla}, pliegue {args.pliegue}): {e['positivos']} positivos + "
        f"{args.negativos_por_positivo} negativos por positivo = {n_epoca:,} imágenes, lote {args.lote}",
        f"Segundos por época: {', '.join(str(t) for t in e['segundos_por_epoca'])} · decodificación "
        f"{e['segundos_lectura_y_decodificacion']} s",
        f"Predicción sobre {p['imagenes']:,} imágenes: {p['segundos_por_1000_imagenes_solo_modelo']} s por 1.000 "
        f"solo modelo · {p['segundos_por_1000_imagenes_con_lectura_y_decodificacion']} s con lectura y decodificación",
        f"Memoria MPS, pico: {m['mps_pico_entrenamiento_gb']} GB entrenando · {m['mps_pico_prediccion_gb']} GB "
        f"prediciendo · proceso {m['proceso_rss_pico_gb']} GB",
        f"Extrapolación, {args.epocas} épocas y {args.negativos_por_positivo} negativos por positivo:",
        "  " + linea("(a) 1 semilla × 5 pliegues", esc_a),
        "  " + linea("(b) (a) con la validación interna de 5 pliegues", esc_b),
        "  " + linea("(c) 10 semillas × 5 pliegues", esc_c),
        f"Detalle y supuestos: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md ({resultado['segundos_corrida_total']} s)")


if __name__ == "__main__":
    main()

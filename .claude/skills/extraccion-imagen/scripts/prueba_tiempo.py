#!/usr/bin/env python3
"""
prueba_tiempo.py — prueba de tiempo de la extracción de imagen, antes de la
Fase 3. Primer script de la futura skill extraccion-imagen, que todavía no
tiene SKILL.md.

Mide cuánto tarda una pasada hacia adelante congelada de cada punto de control
de DINOv2 sobre una muestra de imágenes del conjunto de desarrollo, en MPS, y
estima el tiempo para todas las imágenes del reto. **No guarda características
ni calcula ninguna métrica**: la salida del modelo se descarta en cuanto se
produce. Sirve para decidir el orden de la Fase 3 (M4 si cabe en 8 horas, si no
Kaggle; `PLAN.md`) y para que la persona elija entre ViT-S/14 y ViT-B/14 sin ver
ningún resultado de desempeño.

Los puntos de control son los del repositorio oficial, en el commit versionado
en `referencias/dinov2-repositorio.md`, cuya documentación da LVD-142M como
datos de entrenamiento (condición de la decisión de la Fase 2). El código del
modelo se importa de una copia local de ese commit, no se descarga al vuelo.

Qué se cronometra, por separado:
  - lectura del HDF5, decodificación JPEG y preprocesado, en CPU;
  - la pasada hacia adelante en MPS, con torch.no_grad, sincronizando el
    dispositivo antes de parar el reloj. Se repite y se reporta la mediana.
Una tanda previa, fuera del reloj, calienta el dispositivo.

Uso:
    python prueba_tiempo.py --hdf5 data/train-image.hdf5 \
                            --data data/train-metadata.csv \
                            --repo data/dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8 \
                            --modelos dinov2_vits14 dinov2_vitb14 \
                            --n 1000 --semilla 0 --lote 64 --repeticiones 3 \
                            --total 401059 \
                            --out outputs/prueba-tiempo-dinov2
"""

import argparse
import hashlib
import io
import json
import os
import platform
import statistics
import subprocess
import sys
import time

import h5py
import numpy as np
import torch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "diseno-validacion", "scripts"))
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402

LADO = 224  # 16 × 16 parches de 14 píxeles
MEDIA = np.array([0.485, 0.456, 0.406], dtype=np.float32)  # normalización de ImageNet,
DESV = np.array([0.229, 0.224, 0.225], dtype=np.float32)   # la de las transformaciones de DINOv2


def preprocesar(crudo):
    img = Image.open(io.BytesIO(crudo)).convert("RGB").resize((LADO, LADO), Image.BICUBIC)
    x = (np.asarray(img, dtype=np.float32) / 255.0 - MEDIA) / DESV
    return x.transpose(2, 0, 1)


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def sincronizar(dispositivo):
    if dispositivo.type == "mps":
        torch.mps.synchronize()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hdf5", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--repo", required=True, help="copia local del repositorio dinov2 en el commit versionado")
    ap.add_argument("--modelos", nargs="+", default=["dinov2_vits14", "dinov2_vitb14"])
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--lote", type=int, default=64)
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--total", type=int, required=True, help="imágenes a extraer en la Fase 3, para la estimación")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible; la prueba es en MPS.")
    dispositivo = torch.device("mps")

    sys.path.insert(0, args.repo)
    from dinov2.hub import backbones  # noqa: E402

    df, datos = cargar_desarrollo(args.data, "patient_id", args.holdout)
    rng = np.random.default_rng(args.semilla)
    ids = sorted(rng.choice(df["isic_id"].to_numpy(), size=args.n, replace=False).tolist())

    # Lectura, decodificación y preprocesado: CPU, una vez, fuera del reloj del modelo.
    t0 = time.perf_counter()
    with h5py.File(args.hdf5, "r") as f:
        crudos = [bytes(f[i][()]) for i in ids]
    t_lectura = time.perf_counter() - t0
    t0 = time.perf_counter()
    lote_total = np.stack([preprocesar(c) for c in crudos])
    t_preproceso = time.perf_counter() - t0
    tensores = torch.from_numpy(lote_total)

    cache = torch.hub.get_dir()
    resultados = {}
    for nombre in args.modelos:
        modelo = getattr(backbones, nombre)(pretrained=True).eval().to(dispositivo)
        pesos = os.path.join(cache, "checkpoints", f"{nombre}_pretrain.pth")
        n_param = sum(p.numel() for p in modelo.parameters())

        with torch.no_grad():
            _ = modelo(tensores[: args.lote].to(dispositivo))  # calentamiento, fuera del reloj
            sincronizar(dispositivo)
            del _
            tiempos = []
            for _r in range(args.repeticiones):
                t0 = time.perf_counter()
                for i in range(0, args.n, args.lote):
                    salida = modelo(tensores[i: i + args.lote].to(dispositivo))
                    del salida  # no se guarda nada
                sincronizar(dispositivo)
                tiempos.append(time.perf_counter() - t0)

        mediana = statistics.median(tiempos)
        ips_modelo = args.n / mediana
        ips_total = args.n / (mediana + t_lectura + t_preproceso)
        resultados[nombre] = {
            "pesos": {"archivo": os.path.basename(pesos), "bytes": os.path.getsize(pesos), "sha256": sha256(pesos)},
            "parametros": n_param,
            "segundos_pasada_por_repeticion": [round(t, 3) for t in tiempos],
            "segundos_pasada_mediana": round(mediana, 3),
            "imagenes_por_segundo_solo_modelo": round(ips_modelo, 1),
            "imagenes_por_segundo_con_lectura_y_preproceso": round(ips_total, 1),
            "horas_estimadas_total_solo_modelo": round(args.total / ips_modelo / 3600, 2),
            "horas_estimadas_total_con_lectura_y_preproceso": round(args.total / ips_total / 3600, 2),
        }
        del modelo
        torch.mps.empty_cache()

    chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
    memoria = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
    resultado = {
        "datos": datos,
        "que_es": (
            "Prueba de tiempo de la pasada hacia adelante congelada. No guarda características "
            "ni calcula ninguna métrica de desempeño."
        ),
        "muestra": {"n_imagenes": args.n, "semilla": args.semilla, "de": "conjunto de desarrollo (isic_id)"},
        "preprocesado": f"RGB, redimensión bicúbica a {LADO}x{LADO}, normalización de ImageNet",
        "lote": args.lote,
        "repeticiones": args.repeticiones,
        "dispositivo": "mps",
        "equipo": {"chip": chip, "memoria_gb": round(memoria / 2**30, 1), "macos": platform.mac_ver()[0]},
        "software": {"python": platform.python_version(), "torch": torch.__version__, "h5py": h5py.__version__},
        "repositorio_dinov2": os.path.basename(os.path.normpath(args.repo)),
        "segundos_lectura_hdf5": round(t_lectura, 3),
        "segundos_decodificacion_y_preproceso": round(t_preproceso, 3),
        "total_para_la_estimacion": args.total,
        "modelos": resultados,
        "nota": (
            "La estimación supone el mismo ritmo para todas las imágenes y que lectura, "
            "preprocesado y modelo van uno detrás de otro; no mide el efecto de solaparlos "
            "ni de otro tamaño de lote."
        ),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    lineas = [
        f"# Prueba de tiempo DINOv2 — {args.n} imágenes del conjunto de desarrollo, MPS",
        "Pasada hacia adelante congelada. No guarda características ni calcula métricas.",
        f"Equipo: {chip}, {resultado['equipo']['memoria_gb']} GB · torch {torch.__version__} · lote {args.lote} · {args.repeticiones} repeticiones",
        f"Lectura del HDF5: {resultado['segundos_lectura_hdf5']} s · decodificación y preprocesado: {resultado['segundos_decodificacion_y_preproceso']} s",
    ]
    for nombre, r in resultados.items():
        lineas.append(
            f"{nombre} ({r['parametros']:,} parámetros): {r['imagenes_por_segundo_solo_modelo']} img/s solo modelo · "
            f"{r['imagenes_por_segundo_con_lectura_y_preproceso']} img/s con lectura y preprocesado"
        )
        lineas.append(
            f"  estimado para {args.total:,} imágenes: {r['horas_estimadas_total_solo_modelo']} h solo modelo · "
            f"{r['horas_estimadas_total_con_lectura_y_preproceso']} h con lectura y preprocesado"
        )
    lineas.append(f"Detalle: {args.out}.json")
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
extraer.py — instrumento de medición para la skill extraccion-imagen.

Extrae el token CLS de DINOv2 ViT-S/14 de cada imagen de SLICE-3D y mide la
cobertura. Lo que se fija antes de correr —modelo, pesos, preprocesado,
característica— está en SKILL.md; este script lo aplica y no lo cambia.

No lee la etiqueta: del CSV solo toma isic_id y patient_id. No calcula ninguna
métrica. Separa desarrollo y reservado con la lista sellada, y escribe cada uno
en su propio archivo de data/. El reservado se extrae para la Fase 5; el
cargador de desarrollo se niega a leerlo.

Se niega a correr si el código de la skill o el cargador tienen cambios sin
commitear, porque el JSON graba el commit que lo produjo; y si el hash de los
pesos no es el fijado en SKILL.md.

Uso:
    python extraer.py --hdf5 data/train-image.hdf5 \
                      --data data/train-metadata.csv \
                      --repo data/dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8 \
                      --salida-dir data \
                      --out outputs/extraccion-imagen
"""

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import h5py
import numpy as np
import pandas as pd
import PIL
import torch
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "diseno-validacion", "scripts"))
from datos_desarrollo import RUTA_HOLDOUT, exigir_sin_reservados, leer_reservados  # noqa: E402

MODELO = "dinov2_vits14"
PESOS = "dinov2_vits14_pretrain.pth"
PESOS_SHA256 = "b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9"
DIMENSION = 384
LADO = 224
# IMAGENET_DEFAULT_MEAN y IMAGENET_DEFAULT_STD de dinov2/data/transforms.py.
MEDIA = np.array([0.485, 0.456, 0.406], dtype=np.float32)
DESV = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PREPROCESADO = (
    "JPEG a RGB; redimensionado bicúbico a 224 x 224, sin recorte central; "
    "normalización por defecto de DINOv2 (media 0.485, 0.456, 0.406; desviación 0.229, 0.224, 0.225)"
)
CARACTERISTICA = "token CLS tras la normalización final (x_norm_clstoken), 384 dimensiones"
# Archivos cuyo estado en git debe estar limpio: son el código que produce la salida.
CODIGO = [
    ".claude/skills/extraccion-imagen",
    ".claude/skills/diseno-validacion/scripts/datos_desarrollo.py",
]


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def commit_del_codigo():
    raiz = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    sucio = subprocess.run(["git", "status", "--porcelain", "--", *CODIGO], capture_output=True, text=True, cwd=raiz, check=True).stdout.strip()
    if sucio:
        raise SystemExit(
            "ERROR: el código de la extracción tiene cambios sin commitear. El JSON graba el "
            f"commit que lo produjo, así que hay que commitear antes de correr:\n{sucio}"
        )
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=raiz, check=True).stdout.strip()


def preprocesar(crudo):
    img = Image.open(io.BytesIO(crudo)).convert("RGB")
    cuadrada = img.size[0] == img.size[1]
    img = img.resize((LADO, LADO), Image.BICUBIC)
    x = (np.asarray(img, dtype=np.float32) / 255.0 - MEDIA) / DESV
    return x.transpose(2, 0, 1), cuadrada


def extraer_conjunto(nombre, ids, imagenes, modelo, dispositivo, lote):
    n = len(ids)
    cls = np.full((n, DIMENSION), np.nan, dtype=np.float32)
    decodificada = np.zeros(n, dtype=bool)
    fallidas, no_cuadradas = [], 0
    t = {"lectura_hdf5": 0.0, "decodificacion_y_preproceso": 0.0, "modelo": 0.0}
    inicio = time.perf_counter()
    with torch.no_grad():
        for desde in range(0, n, lote):
            posiciones = range(desde, min(desde + lote, n))
            t0 = time.perf_counter()
            crudos = [bytes(imagenes[ids[i]][()]) for i in posiciones]
            t["lectura_hdf5"] += time.perf_counter() - t0

            t0 = time.perf_counter()
            buenas, tensores = [], []
            for i, crudo in zip(posiciones, crudos):
                try:
                    x, cuadrada = preprocesar(crudo)
                except Exception as e:  # noqa: BLE001 — cualquier fallo de decodificación cuenta como fallida
                    fallidas.append({"isic_id": ids[i], "error": f"{type(e).__name__}: {e}"})
                    continue
                no_cuadradas += not cuadrada
                buenas.append(i)
                tensores.append(x)
            t["decodificacion_y_preproceso"] += time.perf_counter() - t0

            if buenas:
                t0 = time.perf_counter()
                salida = modelo(torch.from_numpy(np.stack(tensores)).to(dispositivo)).cpu().numpy()
                t["modelo"] += time.perf_counter() - t0
                cls[buenas] = salida
                decodificada[buenas] = True

            hechas = posiciones.stop
            if hechas % (lote * 200) < lote or hechas == n:
                transcurrido = time.perf_counter() - inicio
                print(f"[{nombre}] {hechas}/{n} · {transcurrido / 60:.1f} min · "
                      f"quedan ~{transcurrido / hechas * (n - hechas) / 60:.1f} min", flush=True)
    return cls, decodificada, fallidas, no_cuadradas, t


def escribir(ruta, nombre, ids, cls, decodificada, commit):
    t0 = time.perf_counter()
    with h5py.File(ruta, "w") as f:
        f.create_dataset("cls", data=cls)
        f.create_dataset("isic_id", data=np.array(ids, dtype=object), dtype=h5py.string_dtype("utf-8"))
        f.create_dataset("decodificada", data=decodificada)
        f.attrs["conjunto"] = nombre
        f.attrs["modelo"] = MODELO
        f.attrs["pesos_sha256"] = PESOS_SHA256
        f.attrs["preprocesado"] = PREPROCESADO
        f.attrs["caracteristica"] = CARACTERISTICA
        f.attrs["codigo_commit"] = commit
    return time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hdf5", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--repo", required=True, help="copia local del repositorio dinov2 en el commit de SKILL.md")
    ap.add_argument("--salida-dir", required=True)
    ap.add_argument("--lote", type=int, default=64)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t_total = time.perf_counter()
    commit = commit_del_codigo()
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")

    ruta_pesos = os.path.join(torch.hub.get_dir(), "checkpoints", PESOS)
    if not os.path.exists(ruta_pesos) or sha256(ruta_pesos) != PESOS_SHA256:
        raise SystemExit(f"ERROR: {ruta_pesos} no existe o su SHA-256 no es el fijado en SKILL.md.")

    # Solo isic_id y patient_id: la etiqueta no se lee.
    columnas = ["isic_id", "patient_id"]
    df = pd.read_csv(args.data, usecols=columnas)
    assert list(df.columns) == columnas
    reservados = leer_reservados(args.holdout)
    es_reservado = df["patient_id"].astype(str).isin(reservados).to_numpy()
    conjuntos = {
        "desarrollo": df.loc[~es_reservado].reset_index(drop=True),
        "reservado": df.loc[es_reservado].reset_index(drop=True),
    }
    exigir_sin_reservados(conjuntos["desarrollo"], reservados, "patient_id", "el conjunto de desarrollo de la extracción")

    sys.path.insert(0, args.repo)
    from dinov2.hub import backbones  # noqa: E402

    t0 = time.perf_counter()
    modelo = getattr(backbones, MODELO)(pretrained=True).eval().to(dispositivo)
    t_carga = time.perf_counter() - t0

    resultado_conjuntos, archivos = {}, {}
    with h5py.File(args.hdf5, "r") as imagenes:
        for nombre, sub in conjuntos.items():
            ids = sub["isic_id"].tolist()
            cls, decodificada, fallidas, no_cuadradas, t = extraer_conjunto(
                nombre, ids, imagenes, modelo, dispositivo, args.lote)
            ruta = os.path.join(args.salida_dir, f"dinov2-vits14-{nombre}.h5")
            t["escritura"] = escribir(ruta, nombre, ids, cls, decodificada, commit)
            archivos[nombre] = {"archivo": ruta, "bytes": os.path.getsize(ruta), "sha256": sha256(ruta)}
            resultado_conjuntos[nombre] = {
                "cobertura": {
                    "imagenes": len(ids),
                    "pacientes": int(sub["patient_id"].nunique()),
                    "decodificadas": int(decodificada.sum()),
                    "fallidas": len(fallidas),
                    "no_cuadradas": int(no_cuadradas),
                },
                "fallidas": fallidas,
                "segundos_por_fase": {k: round(v, 1) for k, v in t.items()},
                "segundos_total": round(sum(t.values()), 1),
                "archivo": archivos[nombre],
            }

    chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
    memoria = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
    resultado = {
        "datos": {
            "archivo": args.data,
            "columnas_leidas": columnas,
            "imagenes": args.hdf5,
            "reparto": f"desarrollo y reservado según {args.holdout}",
        },
        "modelo": {
            "nombre": MODELO,
            "repositorio": "facebookresearch/dinov2",
            "repositorio_commit": os.path.basename(os.path.normpath(args.repo)).removeprefix("dinov2-"),
            "pesos": {"archivo": PESOS, "sha256": PESOS_SHA256},
        },
        "preprocesado": PREPROCESADO,
        "caracteristica": CARACTERISTICA,
        "lote": args.lote,
        "dispositivo": "mps",
        "equipo": {"chip": chip, "memoria_gb": round(memoria / 2**30, 1), "macos": platform.mac_ver()[0]},
        "software": {
            "python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__,
            "h5py": h5py.__version__, "pillow": PIL.__version__, "pandas": pd.__version__,
        },
        "codigo_commit": commit,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "segundos_carga_del_modelo": round(t_carga, 1),
        "conjuntos": resultado_conjuntos,
        "segundos_total": round(time.perf_counter() - t_total, 1),
        "nota": (
            "No se leyó ninguna etiqueta ni se calculó ninguna métrica. Las filas de una "
            "imagen fallida van en NaN y con decodificada = false."
        ),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    lineas = [
        "# Extracción de imagen — DINOv2 ViT-S/14, token CLS (384 dimensiones)",
        "Sin etiquetas leídas ni métricas calculadas. Preprocesado y modelo fijados en SKILL.md.",
        f"Equipo: {chip}, {resultado['equipo']['memoria_gb']} GB · MPS · torch {torch.__version__} · lote {args.lote}",
    ]
    for nombre, r in resultado_conjuntos.items():
        c = r["cobertura"]
        lineas.append(
            f"{nombre.capitalize()}: {c['decodificadas']} de {c['imagenes']} imágenes decodificadas "
            f"({c['fallidas']} fallidas) · {c['pacientes']} pacientes · {r['segundos_total'] / 60:.1f} min"
        )
        lineas.append(f"  archivo: {r['archivo']['archivo']} · SHA-256 {r['archivo']['sha256'][:16]}…")
    lineas.append(f"Tiempo total: {resultado['segundos_total'] / 60:.1f} min · código en el commit {commit[:12]}")
    lineas.append(f"Detalle, tiempos por fase y hashes completos: {args.out}.json")
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

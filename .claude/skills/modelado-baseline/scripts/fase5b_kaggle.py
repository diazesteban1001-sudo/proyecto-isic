#!/usr/bin/env python3
"""
fase5b_kaggle.py — arma el notebook de Kaggle de la Fase 5b (PLAN.md) desde
fase5b_notebook.py, con su kernel-metadata.json, y lo ensaya en local. No envía
nada a Kaggle: subir el conjunto de datos y el notebook se hace aparte, con la
CLI de Kaggle, y enviar, todavía más aparte.

  construir: el .ipynb con MODO fijado (una celda por cada «# %%» de
      fase5b_notebook.py) y kernel-metadata.json: privado, sin internet, con GPU,
      con la competición y el conjunto de datos de fase5b_paquete.py como entradas.
  --local: ensaya el notebook en el Mac sobre una entrada que imita la de Kaggle:
      la competición con train-metadata.csv y train-image.hdf5 reales, y una
      prueba hecha con tres filas de entrenamiento con las columnas de
      data/test-metadata.csv; y el conjunto de datos armado. En el Mac, sin procesos
      de datos (TRABAJADORES=0): con spawn volverían a importar el script.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --modo medicion \\
        --destino data/fase5b/kernel-medicion [--local]
"""

import argparse
import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
FUENTE = os.path.join(AQUI, "fase5b_notebook.py")
USUARIO = "estebandazz"
CONJUNTO = f"{USUARIO}/isic2024-fase5b-modelos"
COMPETICION = "isic-2024-challenge"
MODOS = ("medicion", "M3limpio", "C7", "Red4e", "ImagenBasicos")


def slug(modo):
    return f"isic2024-fase5b-{modo.lower()}"


def celdas(texto):
    bloques, actual, tipo = [], [], None
    for linea in texto.splitlines(keepends=True):
        if linea.startswith("# %%"):
            if tipo is not None:
                bloques.append((tipo, actual))
            tipo, actual = ("markdown" if "[markdown]" in linea else "code"), []
            continue
        actual.append(linea[2:] if tipo == "markdown" and linea.startswith("# ") else
                      ("\n" if tipo == "markdown" and linea.strip() == "#" else linea))
    bloques.append((tipo, actual))
    salida = []
    for i, (tipo, lineas) in enumerate(bloques):
        while lineas and not lineas[-1].strip():
            lineas.pop()
        celda = {"cell_type": tipo, "id": f"celda-{i}", "metadata": {}, "source": lineas}
        if tipo == "code":
            celda.update(outputs=[], execution_count=None)
        salida.append(celda)
    return salida


def construir(modo, destino):
    texto = open(FUENTE, encoding="utf-8").read()
    if texto.count('MODO = "medicion"\n') != 1:
        raise SystemExit("ERROR: fase5b_notebook.py no tiene una sola línea MODO = \"medicion\".")
    texto = texto.replace('MODO = "medicion"\n', f'MODO = "{modo}"\n')
    os.makedirs(destino, exist_ok=True)
    nombre = slug(modo)
    cuaderno = {"cells": celdas(texto), "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                                                     "name": "python3"},
                                                      "language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 5}
    with open(os.path.join(destino, f"{nombre}.ipynb"), "w", encoding="utf-8") as f:
        json.dump(cuaderno, f, ensure_ascii=False, indent=1)
    with open(os.path.join(destino, f"{nombre}.py"), "w", encoding="utf-8") as f:
        f.write(texto)
    metadata = {"id": f"{USUARIO}/{nombre}", "title": nombre, "code_file": f"{nombre}.ipynb", "language": "python",
                "kernel_type": "notebook", "is_private": True, "enable_gpu": True, "enable_internet": False,
                "dataset_sources": [CONJUNTO], "competition_sources": [COMPETICION], "kernel_sources": []}
    with open(os.path.join(destino, "kernel-metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    return os.path.join(destino, f"{nombre}.py")


def entrada_local(base, conjunto):
    """La entrada que imita la de Kaggle, en base."""
    import h5py
    import pandas as pd
    comp = os.path.join(base, COMPETICION)
    os.makedirs(comp, exist_ok=True)
    for f in ("train-metadata.csv", "train-image.hdf5"):
        destino = os.path.join(comp, f)
        if not os.path.exists(destino):
            os.symlink(os.path.join(RAIZ, "data", f), destino)
    columnas = pd.read_csv(os.path.join(RAIZ, "data", "test-metadata.csv"), nrows=0).columns
    meta = pd.read_csv(os.path.join(RAIZ, "data", "train-metadata.csv"), low_memory=False)
    filas = meta.groupby("patient_id").head(1).iloc[:3][list(columnas)]
    filas.to_csv(os.path.join(comp, "test-metadata.csv"), index=False)
    with h5py.File(os.path.join(RAIZ, "data", "train-image.hdf5"), "r") as h, \
            h5py.File(os.path.join(comp, "test-image.hdf5"), "w") as p:
        for i in filas["isic_id"]:
            p.create_dataset(i, data=h[i][()])
    enlace = os.path.join(base, "isic2024-fase5b-modelos")
    if os.path.lexists(enlace):
        os.remove(enlace)
    os.symlink(os.path.abspath(conjunto), enlace)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", required=True, choices=MODOS)
    ap.add_argument("--destino", required=True)
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--conjunto", default=os.path.join(RAIZ, "data", "fase5b", "kaggle-dataset"))
    args = ap.parse_args()
    script = construir(args.modo, args.destino)
    print(f"Escrito: {args.destino}/{slug(args.modo)}.ipynb y kernel-metadata.json", flush=True)
    if args.local:
        base = os.path.join(args.destino, "entrada-local")
        salida = os.path.join(args.destino, "salida-local")
        os.makedirs(salida, exist_ok=True)
        entrada_local(base, args.conjunto)
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, script], env={**os.environ, "RAIZ_ENTRADA": base, "RAIZ_SALIDA": salida,
                                                  "TRABAJADORES": "0"})
        print(f"Ensayo local: salida {r.returncode}, {round(time.perf_counter() - t0, 1)} s", flush=True)
        if r.returncode:
            raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()

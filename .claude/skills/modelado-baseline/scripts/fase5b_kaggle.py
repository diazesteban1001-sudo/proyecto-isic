#!/usr/bin/env python3
"""
fase5b_kaggle.py — arma el notebook de Kaggle de la Fase 5b (PLAN.md) desde
fase5b_notebook.py, con su kernel-metadata.json, y lo ensaya en local. No envía
nada a Kaggle: subir el conjunto de datos y el notebook se hace aparte, con la
CLI de Kaggle, y enviar, todavía más aparte.

  construir: el .ipynb con MODO fijado (una celda por cada «# %%» de
      fase5b_notebook.py) y kernel-metadata.json: privado, sin internet, con GPU,
      con la competición y el conjunto de datos de fase5b_paquete.py como entradas.
  --registrar: copia a outputs/ la salida que el notebook escribió en Kaggle, ya
      descargada, sin tocarla, con su procedencia; con --anterior, pone al lado el
      control de otra versión del mismo notebook.
  --local: ensaya el notebook en el Mac sobre una entrada que imita la de Kaggle:
      la competición con train-metadata.csv y train-image.hdf5 reales, y una
      prueba hecha con tres filas de entrenamiento con las columnas de
      data/test-metadata.csv; y el conjunto de datos armado. En el Mac, sin procesos
      de datos (TRABAJADORES=0): con spawn volverían a importar el script.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --modo medicion \\
        --destino data/fase5b/kernel-medicion [--local]
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --modo medicion \\
        --destino data/fase5b-kernel-medicion --registrar data/fase5b-kaggle-salida-3 --version 3 \\
        --anterior data/fase5b-kaggle-salida-2 --out outputs/fase5b-kaggle-medicion
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


def sha256(ruta):
    import hashlib
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def registrar(modo, destino, salida, version, out, anterior=None):
    """Copia a outputs/ la salida que el notebook escribió en Kaggle, sin tocarla, con
    su procedencia. Con anterior (la salida de otra versión del mismo notebook), pone
    al lado las diferencias del control de las dos, caso por caso."""
    nombre = slug(modo)
    ruta = os.path.join(salida, f"fase5b-{modo}.json")
    with open(ruta, encoding="utf-8") as f:
        notebook = json.load(f)
    if notebook.get("modo") != modo:
        raise SystemExit(f"ERROR: {ruta} es del modo {notebook.get('modo')!r}, no de {modo!r}.")
    archivos = {os.path.basename(p): {"bytes": os.path.getsize(p), "sha256": sha256(p)}
                for p in (ruta, os.path.join(salida, "submission.csv"), os.path.join(destino, f"{nombre}.ipynb"))}
    registro = {"que_es": "la salida del notebook de la Fase 5b en Kaggle, copiada sin tocar, con su procedencia "
                          "(PLAN.md, Fase 5b); no es un envío a la competición",
                "kernel": {"id": f"{USUARIO}/{nombre}", "version": version, "privado": True, "internet": False},
                "conjunto_de_datos": CONJUNTO, "competicion": COMPETICION, "archivos": archivos,
                "salida_del_notebook": notebook}
    if anterior:
        with open(os.path.join(anterior, f"fase5b-{modo}.json"), encoding="utf-8") as f:
            previa = json.load(f)
        pares = list(zip(previa["control"]["casos"], notebook["control"]["casos"], strict=True))
        if any(a["caso"] != b["caso"] for a, b in pares):
            raise SystemExit("ERROR: los casos del control no son los mismos en las dos versiones.")
        registro["control_frente_a_la_version_anterior"] = {
            "que_es": "la diferencia máxima de cada caso del control en esta versión y en la anterior del mismo "
                      "notebook; los modelos que no cambiaron entre las dos versiones del conjunto de datos tienen "
                      "que repetirla",
            "anterior": {"archivo": f"fase5b-{modo}.json", "sha256": sha256(os.path.join(anterior, f"fase5b-{modo}.json"))},
            "casos": [{"caso": a["caso"], "anterior": a["diferencia_maxima"], "esta": b["diferencia_maxima"],
                       "igual": a["diferencia_maxima"] == b["diferencia_maxima"]}
                      for a, b in pares]}
    with open(f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    c, t = notebook["control"], notebook.get("tiempo")
    lineas = [f"# Fase 5b — el notebook en Kaggle, modo {modo}",
              f"Kernel {USUARIO}/{nombre}, versión {version}, privado y sin internet; {notebook['gpu']}, "
              f"{notebook['trabajadores']} procesos de datos. No es un envío a la competición.",
              f"Control: {len(c['casos']) - c['fallos']} de {len(c['casos'])} bien, "
              f"{sum(x['debe_fallar'] for x in c['casos'])} de ellos casos que deben fallar "
              f"(tolerancias: logit {c['tolerancias']['logit']}, DINOv2 {c['tolerancias']['dinov2']}, "
              f"probabilidad {c['tolerancias']['probabilidad']})."]
    if t:
        lineas.append(f"Proyección a {t['lesiones_de_prueba_supuestas']} lesiones, frente al límite de "
                      f"{t['limite_horas']} h: " + ", ".join(f"{k} {v['horas_proyectadas']} h"
                                                             for k, v in t["proyeccion"].items()) + ".")
    if anterior:
        casos = registro["control_frente_a_la_version_anterior"]["casos"]
        lineas.append(f"Frente a la versión anterior: {sum(x['igual'] for x in casos)} de {len(casos)} casos del "
                      "control repiten su diferencia máxima.")
    lineas.append(f"Tiempo total en Kaggle: {notebook['segundos_total']} s.")
    with open(f"{out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", required=True, choices=MODOS)
    ap.add_argument("--destino", required=True)
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--conjunto", default=os.path.join(RAIZ, "data", "fase5b", "kaggle-dataset"))
    ap.add_argument("--registrar", metavar="SALIDA", help="la salida descargada de Kaggle; no construye nada")
    ap.add_argument("--version", type=int, help="con --registrar: la versión del kernel que la escribió")
    ap.add_argument("--anterior", metavar="SALIDA", help="con --registrar: la salida de la versión anterior")
    ap.add_argument("--out", help="con --registrar: outputs/<nombre>, sin extensión")
    args = ap.parse_args()
    if args.registrar:
        if args.version is None or not args.out:
            raise SystemExit("ERROR: --registrar necesita --version y --out.")
        registrar(args.modo, args.destino, args.registrar, args.version, args.out, args.anterior)
        return
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

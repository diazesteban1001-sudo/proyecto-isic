#!/usr/bin/env python3
"""
fase5b_kaggle.py — arma el notebook de Kaggle de la Fase 5b (PLAN.md) desde
fase5b_notebook.py, con su kernel-metadata.json, lo ensaya en local, fija la
huella de lo que se envía y hace los envíos. Subir el conjunto de datos y el
notebook se hace aparte, con la CLI de Kaggle.

  construir: el .ipynb con MODO fijado (una celda por cada «# %%» de
      fase5b_notebook.py) y kernel-metadata.json: privado, sin internet, con GPU,
      con la competición y el conjunto de datos de fase5b_paquete.py como entradas.
  --registrar: copia a outputs/ la salida que el notebook escribió en Kaggle, ya
      descargada, sin tocarla, con su procedencia; con --anterior, pone al lado el
      control de otra versión del mismo notebook.
  --huella: construye los cuatro notebooks de envío, descarga el conjunto de datos
      tal como lo sirve Kaggle y escribe outputs/fase5b-huella: el SHA-256 de cada
      archivo servido y del conjunto, su versión, su comparación con lo subido y el
      SHA-256 de cada notebook. Se escribe una sola vez, antes del primer envío.
      Con --comprobar, lo vuelve a calcular y se detiene si algo no coincide.
  --enviar: comprueba la huella y envía a la competición la versión --version del
      kernel del modelo. Se niega si el modelo ya tiene un envío con puntuación o
      uno pendiente (PLAN.md, Fase 5b, «Los envíos»).
  --puntuacion: copia a outputs/ los envíos del modelo tal como los devuelve la
      API de Kaggle; sale con código 3, sin escribir nada, si alguno sigue
      pendiente.
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
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --huella [--comprobar]
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --modo M3limpio --enviar --version 1
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_kaggle.py --modo M3limpio --puntuacion \\
        --version 1 --out outputs/fase5b-envio-m3limpio
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
FUENTE = os.path.join(AQUI, "fase5b_notebook.py")
USUARIO = "estebandazz"
CONJUNTO = f"{USUARIO}/isic2024-fase5b-modelos"
COMPETICION = "isic-2024-challenge"
MODOS = ("medicion", "M3limpio", "C7", "Red4e", "ImagenBasicos")
ENVIOS = ("M3limpio", "Red4e", "C7", "ImagenBasicos")  # el orden de envío que fijó la persona (PLAN.md, Fase 5b)
HUELLA = os.path.join(RAIZ, "outputs", "fase5b-huella")
SUBIDO = os.path.join(RAIZ, "data", "fase5b", "kaggle-dataset")


def slug(modo):
    return f"isic2024-fase5b-{modo.lower()}"


def directorio_kernel(modo):
    return os.path.join(RAIZ, "data", f"fase5b-kernel-{modo.lower()}")


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


def sha256_flujo(f):
    h = hashlib.sha256()
    for bloque in iter(lambda: f.read(1 << 20), b""):
        h.update(bloque)
    return h.hexdigest()


def sha256(ruta):
    with open(ruta, "rb") as f:
        return sha256_flujo(f)


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


# ---- la huella y los envíos ------------------------------------------------------------------

def api():
    from kaggle.api.kaggle_api_extended import KaggleApi
    a = KaggleApi()
    a.authenticate()
    return a


def huella_conjunto(archivos):
    """El SHA-256 de las líneas «sha256  ruta» de cada archivo, ordenadas por ruta: el formato de sha256sum."""
    return hashlib.sha256("".join(f"{archivos[r]}  {r}\n" for r in sorted(archivos)).encode()).hexdigest()


def archivos_del_zip(ruta, prefijo=""):
    with zipfile.ZipFile(ruta) as z:
        return {prefijo + n: sha256_flujo(z.open(n)) for n in z.namelist() if not n.endswith("/")}


def lo_subido(conjunto):
    """Lo que Kaggle tiene que servir del directorio subido, con el SHA-256 de cada archivo: todo salvo
    dataset-metadata.json, que no sirve; dinov2.zip, descomprimido en dinov2/; y sin los .DS_Store, que
    tampoco sirve."""
    archivos = {}
    for n in sorted(os.listdir(conjunto)):
        ruta = os.path.join(conjunto, n)
        if n == "dataset-metadata.json":
            continue
        archivos.update(archivos_del_zip(ruta, "dinov2/") if n == "dinov2.zip" else {n: sha256(ruta)})
    return {r: h for r, h in archivos.items() if os.path.basename(r) != ".DS_Store"}


def diferencias(servido, subido):
    return [{"ruta": r, "servido": servido.get(r), "subido": subido.get(r)}
            for r in sorted(set(servido) | set(subido)) if servido.get(r) != subido.get(r)]


def mensaje(modo, version):
    return f"Fase 5b: {modo}, kernel {USUARIO}/{slug(modo)} v{version}"


def del_modelo(envios, modo):
    """Los envíos a la competición que son de este modelo, por el mensaje con que se enviaron."""
    return [e for e in envios if (e.get("description") or "").startswith(f"Fase 5b: {modo},")]


def ya_puntuado(envios, modo):
    """Si el modelo tiene un envío con puntuación: entonces no se vuelve a enviar nunca (PLAN.md, Fase 5b)."""
    return any(e.get("status") == "COMPLETE" for e in del_modelo(envios, modo))


def envios_en_kaggle(a):
    return [s.to_dict(ignore_defaults=False) for s in (a.competition_submissions(COMPETICION, page_size=200) or [])
            if s is not None]


def calcular_huella(conjunto):
    a = api()
    with tempfile.TemporaryDirectory(dir=os.path.join(RAIZ, "data")) as d:
        antes = next(x for x in a.dataset_list(mine=True) if x.ref == CONJUNTO)
        a.dataset_download_files(CONJUNTO, path=d, quiet=True)
        despues = next(x for x in a.dataset_list(mine=True) if x.ref == CONJUNTO)
        if antes.current_version_number != despues.current_version_number:
            raise SystemExit("ERROR: la versión del conjunto de datos cambió durante la descarga.")
        servido = archivos_del_zip(os.path.join(d, f"{CONJUNTO.split('/')[1]}.zip"))
    subido = lo_subido(conjunto)
    notebooks = {}
    for modo in ENVIOS:
        destino = directorio_kernel(modo)
        construir(modo, destino)
        notebooks[modo] = {"kernel": f"{USUARIO}/{slug(modo)}", "directorio": os.path.relpath(destino, RAIZ),
                           "archivos": {n: {"bytes": os.path.getsize(os.path.join(destino, n)),
                                            "sha256": sha256(os.path.join(destino, n))}
                                        for n in (f"{slug(modo)}.ipynb", "kernel-metadata.json")}}
    huella = {"conjunto_de_datos": {"id": CONJUNTO, "version": antes.current_version_number,
                                    "ultima_actualizacion": str(antes.last_updated), "archivos_servidos": len(servido),
                                    "huella_sha256": huella_conjunto(servido), "archivos": servido},
              "lo_subido": {"directorio": os.path.relpath(conjunto, RAIZ), "archivos_esperados": len(subido),
                            "huella_sha256": huella_conjunto(subido)},
              "diferencias_con_lo_subido": diferencias(servido, subido), "notebooks": notebooks}
    return huella, subido


def controles_huella(huella, subido):
    servido = huella["conjunto_de_datos"]["archivos"]
    alterado = dict(subido)
    alterado[sorted(alterado)[0]] = "0" * 64
    puntuado = [{"description": mensaje(ENVIOS[0], 1), "status": "COMPLETE"}]
    con_error = [{"description": mensaje(ENVIOS[0], 1), "status": "ERROR"}]
    casos = [
        {"caso": "lo que sirve Kaggle es lo subido", "ok": not diferencias(servido, subido), "debe_fallar": False},
        {"caso": "con un archivo subido alterado, una diferencia", "ok": len(diferencias(servido, alterado)) == 1,
         "debe_fallar": True},
        {"caso": "con un archivo alterado, la huella cambia",
         "ok": huella_conjunto(alterado) != huella_conjunto(subido), "debe_fallar": True},
        {"caso": "un modelo con un envío puntuado no se vuelve a enviar", "ok": ya_puntuado(puntuado, ENVIOS[0]),
         "debe_fallar": True},
        {"caso": "un envío con error no cuenta como puntuado", "ok": not ya_puntuado(con_error, ENVIOS[0]),
         "debe_fallar": False},
        {"caso": "el envío puntuado de otro modelo no cuenta", "ok": not ya_puntuado(puntuado, ENVIOS[1]),
         "debe_fallar": False},
    ]
    return {"casos": casos, "fallos": sum(not c["ok"] for c in casos)}


def fijar_huella(conjunto):
    if os.path.exists(f"{HUELLA}.json"):
        raise SystemExit(f"ERROR: {HUELLA}.json ya existe; la huella se fija una sola vez. Usa --comprobar.")
    huella, subido = calcular_huella(conjunto)
    huella["controles"] = controles_huella(huella, subido)
    if huella["controles"]["fallos"] or huella["diferencias_con_lo_subido"]:
        print(json.dumps({k: huella[k] for k in ("diferencias_con_lo_subido", "controles")}, indent=1), flush=True)
        raise SystemExit("ERROR: la huella no pasa sus controles; no se escribe.")
    registro = {"que_es": "la huella de lo que se envía en la Fase 5b, fijada antes del primer envío (PLAN.md, Fase "
                          "5b): el conjunto de datos tal como lo sirve Kaggle y los cuatro notebooks de envío",
                "orden_de_envio": list(ENVIOS), **huella,
                "fecha": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with open(f"{HUELLA}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    c, s = huella["conjunto_de_datos"], huella["controles"]
    lineas = ["# Fase 5b — la huella de lo que se envía",
              f"Conjunto de datos {c['id']}, versión {c['version']}: {c['archivos_servidos']} archivos servidos, "
              f"huella SHA-256 {c['huella_sha256']}; 0 diferencias con lo subido.",
              f"Controles: {len(s['casos']) - s['fallos']} de {len(s['casos'])} bien, "
              f"{sum(x['debe_fallar'] for x in s['casos'])} de ellos casos que deben fallar.",
              "Notebooks de envío, en el orden de envío:"]
    for modo in ENVIOS:
        n = huella["notebooks"][modo]
        lineas.append(f"- {modo}: {n['kernel']}, " + ", ".join(f"{k} {v['sha256']}" for k, v in n["archivos"].items()))
    with open(f"{HUELLA}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {HUELLA}.json y .md", flush=True)


def comprobar_huella(conjunto):
    """Vuelve a calcular la huella y se detiene si no es la fijada."""
    with open(f"{HUELLA}.json", encoding="utf-8") as f:
        fijada = json.load(f)
    actual, _ = calcular_huella(conjunto)
    problemas = [f"conjunto de datos, {k}: {fijada['conjunto_de_datos'][k]} fijado, {actual['conjunto_de_datos'][k]} "
                 "ahora" for k in ("version", "huella_sha256")
                 if actual["conjunto_de_datos"][k] != fijada["conjunto_de_datos"][k]]
    problemas += [f"{modo}, {n}" for modo in ENVIOS for n, v in fijada["notebooks"][modo]["archivos"].items()
                  if actual["notebooks"][modo]["archivos"][n]["sha256"] != v["sha256"]]
    if problemas:
        raise SystemExit("ERROR: la huella no es la fijada: " + "; ".join(problemas))
    comprobacion = {"fecha": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "conjunto_de_datos": {k: actual["conjunto_de_datos"][k] for k in ("version", "huella_sha256")},
                    "notebooks": {modo: {n: v["sha256"] for n, v in actual["notebooks"][modo]["archivos"].items()}
                                  for modo in ENVIOS}}
    print("La huella es la fijada:", json.dumps(comprobacion, indent=1), flush=True)
    return comprobacion


def ruta_respuesta(modo):
    return os.path.join(RAIZ, "data", f"fase5b-envio-{modo.lower()}-respuesta.json")


def enviar(modo, version, conjunto):
    comprobacion = comprobar_huella(conjunto)
    a = api()
    previos = del_modelo(envios_en_kaggle(a), modo)
    if ya_puntuado(previos, modo):
        raise SystemExit(f"ERROR: {modo} ya tiene un envío con puntuación; no se vuelve a enviar (PLAN.md, Fase 5b).")
    if any(e.get("status") == "PENDING" for e in previos):
        raise SystemExit(f"ERROR: {modo} tiene un envío pendiente.")
    with open(os.path.join(RAIZ, "outputs", f"fase5b-kaggle-{modo.lower()}.json"), encoding="utf-8") as f:
        corrida = json.load(f)
    if corrida["kernel"]["version"] != version:
        raise SystemExit(f"ERROR: la corrida registrada es de la versión {corrida['kernel']['version']}, no de la {version}.")
    if corrida["salida_del_notebook"]["control"]["fallos"]:
        raise SystemExit("ERROR: el control de la corrida registrada tiene fallos.")
    if corrida["archivos"][f"{slug(modo)}.ipynb"]["sha256"] != comprobacion["notebooks"][modo][f"{slug(modo)}.ipynb"]:
        raise SystemExit("ERROR: el notebook de la corrida registrada no es el fijado en la huella.")
    texto = mensaje(modo, version)
    respuesta = a.competition_submit_code("submission.csv", texto, COMPETICION, kernel=f"{USUARIO}/{slug(modo)}",
                                          kernel_version=version, quiet=True)
    registro = {"mensaje": texto, "respuesta": respuesta.to_dict(ignore_defaults=False),
                "comprobado_antes_de_enviar": comprobacion, "envios_previos_del_modelo": previos}
    with open(ruta_respuesta(modo), "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    print(json.dumps(registro["respuesta"], ensure_ascii=False), flush=True)


def puntuacion(modo, version, out):
    envios = del_modelo(envios_en_kaggle(api()), modo)
    if not envios:
        raise SystemExit(f"ERROR: no hay envíos de {modo} en la competición.")
    if any(e.get("status") == "PENDING" for e in envios):
        print(f"{modo}: pendiente", flush=True)
        raise SystemExit(3)
    with open(f"{HUELLA}.json", encoding="utf-8") as f:
        huella = json.load(f)
    respuesta = None
    if os.path.exists(ruta_respuesta(modo)):
        with open(ruta_respuesta(modo), encoding="utf-8") as f:
            respuesta = json.load(f)
    registro = {"que_es": "los envíos de este modelo a la competición, tal como los devuelve la API de Kaggle, sin "
                          "tocar (PLAN.md, Fase 5b)",
                "modelo": modo, "kernel": {"id": f"{USUARIO}/{slug(modo)}", "version": version},
                "huella_fijada": {"archivo": "outputs/fase5b-huella.json",
                                  "conjunto_de_datos": {k: huella["conjunto_de_datos"][k]
                                                        for k in ("version", "huella_sha256")},
                                  "notebook": {n: v["sha256"] for n, v in huella["notebooks"][modo]["archivos"].items()}},
                "al_enviar": respuesta, "envios": envios}
    with open(f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    lineas = [f"# Fase 5b — los envíos de {modo} a la competición",
              f"Kernel {USUARIO}/{slug(modo)}, versión {version}. Tal como los devuelve la API de Kaggle:"]
    lineas += [f"- {e.get('date')}: {e.get('status')}; puntuación pública {e.get('publicScore')}, privada "
               f"{e.get('privateScore')}" + (f"; error: {e.get('errorDescription')}" if e.get("errorDescription") else "")
               + f" («{e.get('description')}»)" for e in envios]
    with open(f"{out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=MODOS)
    ap.add_argument("--destino")
    ap.add_argument("--huella", action="store_true", help="fija la huella de lo que se envía; no construye otra cosa")
    ap.add_argument("--comprobar", action="store_true", help="con --huella: comprueba la fijada en vez de fijarla")
    ap.add_argument("--enviar", action="store_true", help="envía a la competición la versión --version del kernel")
    ap.add_argument("--puntuacion", action="store_true", help="copia a outputs/ los envíos del modelo")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--conjunto", default=SUBIDO)
    ap.add_argument("--registrar", metavar="SALIDA", help="la salida descargada de Kaggle; no construye nada")
    ap.add_argument("--version", type=int, help="con --registrar, --enviar o --puntuacion: la versión del kernel")
    ap.add_argument("--anterior", metavar="SALIDA", help="con --registrar: la salida de la versión anterior")
    ap.add_argument("--out", help="con --registrar o --puntuacion: outputs/<nombre>, sin extensión")
    args = ap.parse_args()
    if args.huella:
        (comprobar_huella if args.comprobar else fijar_huella)(args.conjunto)
        return
    if not args.modo:
        raise SystemExit("ERROR: falta --modo.")
    if args.enviar or args.puntuacion:
        if args.modo not in ENVIOS or args.version is None or (args.puntuacion and not args.out):
            raise SystemExit("ERROR: --enviar y --puntuacion necesitan un modo de envío y --version; "
                             "--puntuacion, también --out.")
        if args.enviar:
            enviar(args.modo, args.version, args.conjunto)
        else:
            puntuacion(args.modo, args.version, args.out)
        return
    if not args.destino:
        raise SystemExit("ERROR: falta --destino.")
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

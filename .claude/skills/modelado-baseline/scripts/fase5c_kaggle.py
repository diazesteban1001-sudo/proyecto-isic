#!/usr/bin/env python3
"""
fase5c_kaggle.py — lo de fase5b_kaggle.py para la Fase 5c (PLAN.md): arma el
notebook de Kaggle desde fase5c_notebook.py, con su kernel-metadata.json, lo
ensaya en local, registra sus corridas, fija la huella de lo que se envía y hace
los envíos. Usa las piezas de fase5b_kaggle.py que no dependen de la fase, sin
cambiarlas; las que sí, con los nombres de la 5c. Subir el conjunto de datos y el
notebook se hace aparte, con la CLI de Kaggle.

  construir: el .ipynb con MODO fijado y kernel-metadata.json: privado, sin
      internet, con GPU, con la competición y el conjunto de datos de
      fase5c_paquete.py como entradas.
  --registrar: copia a outputs/ la salida que el notebook escribió en Kaggle, ya
      descargada, sin tocarla, con su procedencia.
  --huella: construye los cuatro notebooks de envío, descarga el conjunto de datos
      tal como lo sirve Kaggle y escribe outputs/fase5c-huella, una sola vez, antes
      del primer envío. Con --comprobar, lo vuelve a calcular y se detiene si algo
      no coincide.
  --enviar: comprueba la huella y envía a la competición la versión --version del
      kernel del modelo. Solo envía los cuatro modelos de la 5c, y se niega si el
      modelo ya tiene un envío con puntuación o uno pendiente (PLAN.md, Fase 5c).
  --puntuacion: copia a outputs/ los envíos del modelo tal como los devuelve la
      API de Kaggle; sale con código 3, sin escribir nada, si alguno sigue
      pendiente.
  --local: ensaya el notebook en el Mac sobre una entrada que imita la de Kaggle,
      como en la 5b (fase5b_kaggle.py, --local).

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_kaggle.py --modo medicion \\
        --destino data/fase5c-kernel-medicion [--local]
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_kaggle.py --modo medicion \\
        --destino data/fase5c-kernel-medicion --registrar data/fase5c-kaggle-salida-medicion --version 1 \\
        --out outputs/fase5c-kaggle-medicion
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_kaggle.py --huella [--comprobar]
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_kaggle.py --modo M3limpioProm --enviar --version 1
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_kaggle.py --modo M3limpioProm --puntuacion \\
        --version 1 --out outputs/fase5c-envio-m3limpioprom
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase5b_kaggle as k5b  # noqa: E402

RAIZ = k5b.RAIZ
FUENTE = os.path.join(AQUI, "fase5c_notebook.py")
USUARIO = k5b.USUARIO
NOMBRE_CONJUNTO = "isic2024-fase5c-modelos"
CONJUNTO = f"{USUARIO}/{NOMBRE_CONJUNTO}"
COMPETICION = k5b.COMPETICION
MODOS = ("medicion", "M3limpioProm", "M3limpioPromHosp", "C7Prom", "C7PromHosp")
ENVIOS = ("M3limpioProm", "M3limpioPromHosp", "C7Prom", "C7PromHosp")  # el orden de envío (PLAN.md, Fase 5c)
HUELLA = os.path.join(RAIZ, "outputs", "fase5c-huella")
SUBIDO = os.path.join(RAIZ, "data", "fase5c", "kaggle-dataset")


def slug(modo):
    return f"isic2024-fase5c-{modo.lower()}"


def directorio_kernel(modo):
    return os.path.join(RAIZ, "data", f"fase5c-kernel-{modo.lower()}")


def construir(modo, destino):
    texto = open(FUENTE, encoding="utf-8").read()
    if texto.count('MODO = "medicion"\n') != 1:
        raise SystemExit("ERROR: fase5c_notebook.py no tiene una sola línea MODO = \"medicion\".")
    texto = texto.replace('MODO = "medicion"\n', f'MODO = "{modo}"\n')
    os.makedirs(destino, exist_ok=True)
    nombre = slug(modo)
    cuaderno = {"cells": k5b.celdas(texto), "metadata": {"kernelspec": {"display_name": "Python 3",
                                                                         "language": "python", "name": "python3"},
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
    """La de fase5b_kaggle.entrada_local, con el conjunto de datos de la 5c."""
    k5b.entrada_local(base, conjunto)
    viejo = os.path.join(base, "isic2024-fase5b-modelos")
    if os.path.lexists(viejo):
        os.remove(viejo)
    enlace = os.path.join(base, NOMBRE_CONJUNTO)
    if os.path.lexists(enlace):
        os.remove(enlace)
    os.symlink(os.path.abspath(conjunto), enlace)


def registrar(modo, destino, salida, version, out):
    """Copia a outputs/ la salida que el notebook escribió en Kaggle, sin tocarla, con su procedencia."""
    nombre = slug(modo)
    ruta = os.path.join(salida, f"fase5c-{modo}.json")
    with open(ruta, encoding="utf-8") as f:
        notebook = json.load(f)
    if notebook.get("modo") != modo:
        raise SystemExit(f"ERROR: {ruta} es del modo {notebook.get('modo')!r}, no de {modo!r}.")
    archivos = {os.path.basename(p): {"bytes": os.path.getsize(p), "sha256": k5b.sha256(p)}
                for p in (ruta, os.path.join(salida, "submission.csv"), os.path.join(destino, f"{nombre}.ipynb"))}
    registro = {"que_es": "la salida del notebook de la Fase 5c en Kaggle, copiada sin tocar, con su procedencia "
                          "(PLAN.md, Fase 5c); no es un envío a la competición",
                "kernel": {"id": f"{USUARIO}/{nombre}", "version": version, "privado": True, "internet": False},
                "conjunto_de_datos": CONJUNTO, "competicion": COMPETICION, "archivos": archivos,
                "salida_del_notebook": notebook}
    with open(f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    c, t = notebook["control"], notebook.get("tiempo")
    lineas = [f"# Fase 5c — el notebook en Kaggle, modo {modo}",
              f"Kernel {USUARIO}/{nombre}, versión {version}, privado y sin internet; {notebook['gpu']}, "
              f"{notebook['trabajadores']} procesos de datos. No es un envío a la competición.",
              f"Control: {len(c['casos']) - c['fallos']} de {len(c['casos'])} bien, "
              f"{sum(x['debe_fallar'] for x in c['casos'])} de ellos casos que deben fallar "
              f"(tolerancias: logit {c['tolerancias']['logit']}, probabilidad {c['tolerancias']['probabilidad']}, "
              f"celda 17 {c['tolerancias']['z']})."]
    if t:
        lineas.append(f"Proyección a {t['lesiones_de_prueba_supuestas']} lesiones, frente al límite de "
                      f"{t['limite_horas']} h: " + ", ".join(f"{k} {v['horas_proyectadas']} h"
                                                             for k, v in t["proyeccion"].items()) + ".")
    lineas.append(f"Tiempo total en Kaggle: {notebook['segundos_total']} s.")
    with open(f"{out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md", flush=True)


# ---- la huella y los envíos ------------------------------------------------------------------

def mensaje(modo, version):
    return f"Fase 5c: {modo}, kernel {USUARIO}/{slug(modo)} v{version}"


def del_modelo(envios, modo):
    """Los envíos a la competición que son de este modelo, por el mensaje con que se enviaron."""
    return [e for e in envios if (e.get("description") or "").startswith(f"Fase 5c: {modo},")]


def ya_puntuado(envios, modo):
    """Si el modelo tiene un envío con puntuación: entonces no se vuelve a enviar nunca (PLAN.md, Fase 5c)."""
    return any(e.get("status") == "COMPLETE" for e in del_modelo(envios, modo))


def calcular_huella(conjunto):
    a = k5b.api()
    with tempfile.TemporaryDirectory(dir=os.path.join(RAIZ, "data")) as d:
        antes = next(x for x in a.dataset_list(mine=True) if x.ref == CONJUNTO)
        a.dataset_download_files(CONJUNTO, path=d, quiet=True)
        despues = next(x for x in a.dataset_list(mine=True) if x.ref == CONJUNTO)
        if antes.current_version_number != despues.current_version_number:
            raise SystemExit("ERROR: la versión del conjunto de datos cambió durante la descarga.")
        servido = k5b.archivos_del_zip(os.path.join(d, f"{NOMBRE_CONJUNTO}.zip"))
    subido = k5b.lo_subido(conjunto)
    notebooks = {}
    for modo in ENVIOS:
        destino = directorio_kernel(modo)
        construir(modo, destino)
        notebooks[modo] = {"kernel": f"{USUARIO}/{slug(modo)}", "directorio": os.path.relpath(destino, RAIZ),
                           "archivos": {n: {"bytes": os.path.getsize(os.path.join(destino, n)),
                                            "sha256": k5b.sha256(os.path.join(destino, n))}
                                        for n in (f"{slug(modo)}.ipynb", "kernel-metadata.json")}}
    huella = {"conjunto_de_datos": {"id": CONJUNTO, "version": antes.current_version_number,
                                    "ultima_actualizacion": str(antes.last_updated), "archivos_servidos": len(servido),
                                    "huella_sha256": k5b.huella_conjunto(servido), "archivos": servido},
              "lo_subido": {"directorio": os.path.relpath(conjunto, RAIZ), "archivos_esperados": len(subido),
                            "huella_sha256": k5b.huella_conjunto(subido)},
              "diferencias_con_lo_subido": k5b.diferencias(servido, subido), "notebooks": notebooks}
    return huella, subido


def controles_huella(huella, subido):
    servido = huella["conjunto_de_datos"]["archivos"]
    alterado = dict(subido)
    alterado[sorted(alterado)[0]] = "0" * 64
    puntuado = [{"description": mensaje(ENVIOS[0], 1), "status": "COMPLETE"}]
    con_error = [{"description": mensaje(ENVIOS[0], 1), "status": "ERROR"}]
    de_la_5b = [{"description": k5b.mensaje("M3limpio", 1), "status": "COMPLETE"}]
    casos = [
        {"caso": "lo que sirve Kaggle es lo subido", "ok": not k5b.diferencias(servido, subido), "debe_fallar": False},
        {"caso": "con un archivo subido alterado, una diferencia", "ok": len(k5b.diferencias(servido, alterado)) == 1,
         "debe_fallar": True},
        {"caso": "con un archivo alterado, la huella cambia",
         "ok": k5b.huella_conjunto(alterado) != k5b.huella_conjunto(subido), "debe_fallar": True},
        {"caso": "un modelo con un envío puntuado no se vuelve a enviar", "ok": ya_puntuado(puntuado, ENVIOS[0]),
         "debe_fallar": True},
        {"caso": "un envío con error no cuenta como puntuado", "ok": not ya_puntuado(con_error, ENVIOS[0]),
         "debe_fallar": False},
        {"caso": "el envío puntuado de otro modelo no cuenta", "ok": not ya_puntuado(puntuado, ENVIOS[1]),
         "debe_fallar": False},
        {"caso": "«M3limpioProm» no se confunde con «M3limpioPromHosp»",
         "ok": not ya_puntuado([{"description": mensaje("M3limpioPromHosp", 1), "status": "COMPLETE"}], ENVIOS[0]),
         "debe_fallar": False},
        {"caso": "un envío de la 5b no cuenta como de la 5c", "ok": not ya_puntuado(de_la_5b, ENVIOS[0]),
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
    registro = {"que_es": "la huella de lo que se envía en la Fase 5c, fijada antes del primer envío (PLAN.md, Fase "
                          "5c): el conjunto de datos tal como lo sirve Kaggle y los cuatro notebooks de envío",
                "orden_de_envio": list(ENVIOS), **huella,
                "fecha": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with open(f"{HUELLA}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    c, s = huella["conjunto_de_datos"], huella["controles"]
    lineas = ["# Fase 5c — la huella de lo que se envía",
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
    return os.path.join(RAIZ, "data", f"fase5c-envio-{modo.lower()}-respuesta.json")


def enviar(modo, version, conjunto):
    if modo not in ENVIOS:
        raise SystemExit(f"ERROR: {modo} no es uno de los cuatro envíos de la Fase 5c.")
    comprobacion = comprobar_huella(conjunto)
    a = k5b.api()
    previos = del_modelo(k5b.envios_en_kaggle(a), modo)
    if ya_puntuado(previos, modo):
        raise SystemExit(f"ERROR: {modo} ya tiene un envío con puntuación; no se vuelve a enviar (PLAN.md, Fase 5c).")
    if any(e.get("status") == "PENDING" for e in previos):
        raise SystemExit(f"ERROR: {modo} tiene un envío pendiente.")
    with open(os.path.join(RAIZ, "outputs", f"fase5c-kaggle-{modo.lower()}.json"), encoding="utf-8") as f:
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
    envios = del_modelo(k5b.envios_en_kaggle(k5b.api()), modo)
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
                          "tocar (PLAN.md, Fase 5c)",
                "modelo": modo, "kernel": {"id": f"{USUARIO}/{slug(modo)}", "version": version},
                "huella_fijada": {"archivo": "outputs/fase5c-huella.json",
                                  "conjunto_de_datos": {k: huella["conjunto_de_datos"][k]
                                                        for k in ("version", "huella_sha256")},
                                  "notebook": {n: v["sha256"] for n, v in huella["notebooks"][modo]["archivos"].items()}},
                "al_enviar": respuesta, "envios": envios}
    with open(f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    lineas = [f"# Fase 5c — los envíos de {modo} a la competición",
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
        registrar(args.modo, args.destino, args.registrar, args.version, args.out)
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

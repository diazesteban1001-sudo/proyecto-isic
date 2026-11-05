#!/usr/bin/env python3
"""
fase5b_paquete.py — comprueba en el Mac que inferencia_5b.py reproduce las
referencias de fase5b_entrenar.py y arma el conjunto de datos privado que usará
el notebook de Kaggle de la Fase 5b (PLAN.md). No envía nada.

Sobre el conjunto de control, puntuado por el entrenamiento con el código
verificado, la inferencia portátil tiene que dar:
  - las variables de M3 limpio y su puntuación, idénticas;
  - el conglomerado del k-means en números igual al de scikit-learn en todas las
    filas de entrenamiento;
  - los logits de las seis redes con los pesos ajustados guardados, a TOL_RED;
  - las variables de DINOv2 recalculadas, a TOL_DINOV2 de las del archivo;
  - «Imagen + básicos» y C7 desde esas variables, a TOL_PROBABILIDAD.
Cada comprobación tiene su caso que debe fallar. Si una falla, no se arma nada.

El conjunto de datos, plano, lleva: inferencia_5b.py y ganador_m3.py sin cambios;
el paquete dinov2 del repositorio de la extracción, en dinov2.zip, y su licencia;
los pesos públicos
de DINOv2 ViT-S/14; los modelos de la Fase 5b; y el control, para que el notebook
repita la comprobación en Kaggle. Cada archivo, con su SHA-256 en la salida.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_paquete.py --out outputs/fase5b-paquete
"""

import argparse
import datetime
import json
import os
import platform
import shutil
import sys
import time

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "extraccion-imagen", "scripts"))
import fase5  # noqa: E402
import ganador_m3  # noqa: E402
import inferencia_5b as inf  # noqa: E402
import extraer  # noqa: E402

RAIZ = fase5.RAIZ
G = "patient_id"
TOL_RED = 1e-4
TOL_DINOV2 = 1e-3
TOL_PROBABILIDAD = 1e-6
USUARIO = "estebandazz"
SLUG = "isic2024-fase5b-modelos"
REDES = ["sola", *inf.REDES_DE_C7]


def sha(ruta):
    return fase5.sha256(ruta)


def caso(control, que, ok, debe_fallar, detalle):
    return fase5.caso(control, que, ok, debe_fallar, detalle)


def maxima(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return float("inf")
    iguales_nan = np.isnan(a) & np.isnan(b)
    d = np.where(iguales_nan, 0.0, np.abs(a - b))
    return float(np.nanmax(np.where(np.isnan(d), np.inf, d))) if d.size else 0.0


def comprobar(d, csv, hdf5, dispositivo, casos):
    import torch
    c = dict(np.load(os.path.join(d, "control.npz")))
    ids = list(c["isic_id"])
    meta = pd.read_csv(csv, low_memory=False)
    filas = meta.set_index("isic_id").loc[ids].reset_index().drop(columns=["target"])
    aj = inf.cargar_ajuste_m3(d)

    x, et = inf.variables_m3(filas, aj)
    columnas = list(c["x_m3_columnas"])
    dif = maxima(x.astype(float).to_numpy(), c["x_m3"])
    casos.append(caso("m3limpio", "las variables de M3 limpio del control, idénticas", list(x.columns) == columnas
                      and dif == 0.0, False, f"diferencia máxima {dif:.1e}"))
    s = inf.puntuar_cbm(os.path.join(d, "m3limpio.cbm"), x)
    dif = maxima(s, c["m3limpio"])
    casos.append(caso("m3limpio", "la puntuación de M3 limpio, idéntica", dif == 0.0, False, f"diferencia máxima {dif:.1e}"))
    casos.append(caso("m3limpio", "frente a la de C7", maxima(s, c["c7"]) > TOL_PROBABILIDAD, True, "distintas"))

    base = ganador_m3.variables_lectura(meta, aj[0]["listas"], G, aj[0]["medianas"])
    escalada = (base[aj[0]["listas"]["top_lof_features"]].to_numpy(dtype=float) - aj[1]["escala_media"]) \
        / aj[1]["escala_escala"]
    del base
    et_tr = inf.conglomerado(escalada, aj[1]["centros"])
    distintas = int((et_tr != c["etiquetas_kmeans_entrenamiento"]).sum())
    casos.append(caso("m3limpio", "el k-means en números asigna como scikit-learn las filas de entrenamiento",
                      distintas == 0, False, f"{distintas} de {len(et_tr)} distintas"))
    otras = int((inf.conglomerado(escalada, aj[1]["centros"][::-1]) != c["etiquetas_kmeans_entrenamiento"]).sum())
    casos.append(caso("m3limpio", "con los centros en orden inverso", otras > 0, True, f"{otras} distintas"))

    redes = {k: inf.red(os.path.join(d, "redes", f"{k}.pt"), dispositivo) for k in REDES}
    modelo_d = inf.dinov2(os.path.join(d, "dinov2_vits14_pretrain.pth"), dispositivo)
    logits, dino = inf.recorrer(hdf5, ids, redes, modelo_d, dispositivo)
    refs = {"sola": c["logit_sola"], **{k: c["logit_pliegues"][i] for i, k in enumerate(inf.REDES_DE_C7)}}
    difs = {k: maxima(logits[k], refs[k]) for k in REDES}
    casos.append(caso("redes", f"los logits de las seis redes ajustadas, a {TOL_RED}", max(difs.values()) <= TOL_RED,
                      False, {k: f"{v:.1e}" for k, v in difs.items()}))
    base_sola, _ = inf.recorrer(hdf5, ids[:256], {"base": inf.red(os.path.join(d, "redes", "sola-base.pt"), dispositivo)},
                                None, dispositivo)
    dif = maxima(base_sola["base"], refs["sola"][:256])
    casos.append(caso("redes", "con los pesos de la red sin ajustar", dif > TOL_RED, True, f"diferencia máxima {dif:.1e}"))
    dif = maxima(dino, c["dinov2"])
    casos.append(caso("dinov2", f"las variables de DINOv2 recalculadas, a {TOL_DINOV2} de las del archivo",
                      dif <= TOL_DINOV2, False, f"diferencia máxima {dif:.1e}"))
    dif = maxima(np.roll(dino, 1, axis=0), c["dinov2"])
    casos.append(caso("dinov2", "con las filas corridas una", dif > TOL_DINOV2, True, f"diferencia máxima {dif:.1e}"))

    aj_ib = inf.leer_json(os.path.join(d, "imagen-basicos.json"))
    dif = maxima(inf.basicos(filas, aj_ib), c["basicos"])
    casos.append(caso("imagen_basicos", "los tres básicos codificados, idénticos", dif == 0.0, False,
                      f"diferencia máxima {dif:.1e}"))
    s = inf.puntuar_imagen_basicos(filas, dino, d)
    dif = maxima(s, c["imagen_basicos"])
    casos.append(caso("imagen_basicos", f"la puntuación, a {TOL_PROBABILIDAD}", dif <= TOL_PROBABILIDAD, False,
                      f"diferencia máxima {dif:.1e}"))
    s_mal = inf.puntuar_imagen_basicos(filas.assign(sex=np.nan), dino, d)
    dif = maxima(s_mal, c["imagen_basicos"])
    casos.append(caso("imagen_basicos", "con el sexo borrado", dif > TOL_PROBABILIDAD, True, f"diferencia máxima {dif:.1e}"))

    p = np.mean([inf.probabilidad(logits[k]) for k in inf.REDES_DE_C7], axis=0)
    s = inf.puntuar_cbm(os.path.join(d, "c7.cbm"), inf.variables_c7(x, p, filas[G].astype(str).to_numpy()))
    dif = maxima(s, c["c7"])
    casos.append(caso("c7", f"la puntuación de C7 con la media de las cinco redes, a {TOL_PROBABILIDAD}",
                      dif <= TOL_PROBABILIDAD, False, f"diferencia máxima {dif:.1e}"))
    s_mal = inf.puntuar_cbm(os.path.join(d, "c7.cbm"),
                            inf.variables_c7(x, inf.probabilidad(logits["sola"]), filas[G].astype(str).to_numpy()))
    dif = maxima(s_mal, c["c7"])
    casos.append(caso("c7", "con la red sola en lugar de las cinco", dif > TOL_PROBABILIDAD, True,
                      f"diferencia máxima {dif:.1e}"))
    del redes, modelo_d
    if dispositivo.type == "mps":
        torch.mps.empty_cache()


def armar(d, destino):
    """El directorio del conjunto de datos de Kaggle, plano, con su metadata. El paquete
    dinov2 va en dinov2.zip, que el notebook descomprime: así no hay subcarpetas."""
    import zipfile
    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.makedirs(destino)
    for f in ("inferencia_5b.py", "ganador_m3.py"):
        shutil.copy2(os.path.join(AQUI, f), os.path.join(destino, f))
    repo = os.path.join(RAIZ, "data", "dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8")
    with zipfile.ZipFile(os.path.join(destino, "dinov2.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dns, fs in os.walk(os.path.join(repo, "dinov2")):
            dns[:] = sorted(x for x in dns if x != "__pycache__")
            for f in sorted(fs):
                z.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), repo))
    shutil.copy2(os.path.join(repo, "LICENSE"), os.path.join(destino, "dinov2-LICENSE"))
    for f in ("m3limpio.cbm", "c7.cbm", "m3limpio-ajuste.json", "m3limpio-ajuste.npz", "imagen-basicos.json",
              "imagen-basicos.npz", "control.npz", "dinov2_vits14_pretrain.pth"):
        shutil.copy2(os.path.join(d, f), os.path.join(destino, f))
    for k in REDES:
        shutil.copy2(os.path.join(d, "redes", f"{k}.pt"), os.path.join(destino, f"red-{k}.pt"))
    with open(os.path.join(destino, "dataset-metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"title": SLUG, "id": f"{USUARIO}/{SLUG}", "licenses": [{"name": "unknown"}]}, f, indent=2)
    return sorted(os.path.join(destino, f) for f in os.listdir(destino))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dir", default=os.path.join(RAIZ, "data", "fase5b"), help="los artefactos del entrenamiento")
    ap.add_argument("--registro", default=os.path.join(RAIZ, "outputs", "fase5b-entrenamiento.json"))
    args = ap.parse_args()
    import torch
    t0 = time.perf_counter()
    with open(args.registro, encoding="utf-8") as f:
        registro = json.load(f)
    cambiados = [a for a, v in registro["archivos"].items() if sha(os.path.normpath(os.path.join(RAIZ, a))) != v["sha256"]]
    if cambiados:
        raise SystemExit(f"ERROR: archivos distintos de los del entrenamiento: {cambiados}")
    pesos = os.path.join(torch.hub.get_dir(), "checkpoints", extraer.PESOS)
    if extraer.sha256(pesos) != extraer.PESOS_SHA256:
        raise SystemExit("ERROR: los pesos de DINOv2 no son los de la extracción.")
    shutil.copy2(pesos, os.path.join(args.dir, "dinov2_vits14_pretrain.pth"))
    sys.path.insert(0, os.path.join(RAIZ, "data", "dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8"))
    r = fase5.rutas(RAIZ)
    casos = []
    comprobar(args.dir, r["csv"], r["hdf5"], torch.device("mps"), casos)
    fallos = [f"{c['control']}: {c['caso']}" for c in casos if not c["ok"]]
    if fallos:
        print(json.dumps(casos, ensure_ascii=False, indent=2))
        raise SystemExit("ERROR: fallaron controles; no se arma el conjunto de datos:\n  " + "\n  ".join(fallos))
    destino = os.path.join(args.dir, "kaggle-dataset")
    archivos = armar(args.dir, destino)
    resultado = {
        "que_es": ("la comprobación en el Mac de inferencia_5b.py frente a las referencias del entrenamiento de la Fase "
                   "5b, y el conjunto de datos privado para el notebook de Kaggle (PLAN.md, Fase 5b); no envía nada"),
        "tolerancias": {"redes_logit": TOL_RED, "dinov2": TOL_DINOV2, "probabilidades": TOL_PROBABILIDAD},
        "controles": {"casos": casos, "de_casos": len(casos), "fallos": 0,
                      "deben_fallar": sum(c["debe_fallar"] for c in casos)},
        "conjunto_de_datos": {"id": f"{USUARIO}/{SLUG}", "directorio": os.path.relpath(destino, RAIZ),
                              "archivos": {os.path.relpath(a, destino): {"bytes": os.path.getsize(a), "sha256": sha(a)}
                                           for a in archivos},
                              "pesos_dinov2": {"sha256": extraer.PESOS_SHA256, "licencia": "Apache 2.0, codigo/dinov2-LICENSE"}},
        "registro_del_entrenamiento": os.path.relpath(args.registro, RAIZ),
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                      "torch": torch.__version__},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "segundos": round(time.perf_counter() - t0, 1),
    }
    out = args.out if os.path.isabs(args.out) else os.path.join(RAIZ, args.out)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    c = resultado["controles"]
    total = sum(v["bytes"] for v in resultado["conjunto_de_datos"]["archivos"].values())
    lineas = ["# Fase 5b — la inferencia portátil y el conjunto de datos para Kaggle",
              f"Controles en el Mac: {c['de_casos']} de {c['de_casos']} bien, {c['deben_fallar']} de ellos casos que "
              f"deben fallar (tolerancias: logits {TOL_RED}, DINOv2 {TOL_DINOV2}, probabilidades {TOL_PROBABILIDAD}).",
              f"Conjunto de datos {USUARIO}/{SLUG}: {len(archivos)} archivos, {total / 2**20:.1f} MiB. No envía nada."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']} s", flush=True)


if __name__ == "__main__":
    main()

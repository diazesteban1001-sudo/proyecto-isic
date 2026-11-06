#!/usr/bin/env python3
"""
fase5c_paquete.py — comprueba en el Mac que inferencia_5c.py reproduce las
referencias de fase5c_entrenar.py y arma el conjunto de datos privado que usará
el notebook de Kaggle de la Fase 5c (PLAN.md). No envía nada.

Sobre el conjunto de control, puntuado por el entrenamiento con el código
verificado, la inferencia portátil tiene que dar:
  - las variables de M3 limpio, sin hospital y con hospital, idénticas;
  - el conglomerado del k-means en números igual al de scikit-learn en todas las
    filas de entrenamiento, con los dos ajustes;
  - los logits de las cinco redes de los pliegues, a TOL_RED, y la media de sus
    probabilidades, a TOL_PROBABILIDAD de la que guardó la Fase 5b;
  - la variable de la celda 17, idéntica con la media guardada de las redes;
  - la puntuación de cada envío, la media de sus 45 CatBoost: idéntica con la
    media guardada de las redes, y a TOL_PROBABILIDAD con la recalculada.
Cada comprobación tiene su caso que debe fallar. Si una falla, no se arma nada.

El conjunto de datos, plano, lleva: inferencia_5c.py, inferencia_5b.py y
ganador_m3.py sin cambios; los dos ajustes de M3 limpio y la tabla de la celda 17;
los 180 CatBoost; las cinco redes de los pliegues de la Fase 5b; y el control,
para que el notebook repita la comprobación en Kaggle. Cada archivo, con su
SHA-256 en la salida.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_paquete.py --out outputs/fase5c-paquete
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
import fase5  # noqa: E402
import fase5b_paquete as p5b  # noqa: E402
import ganador_m3  # noqa: E402
import inferencia_5b as inf5b  # noqa: E402
import inferencia_5c as inf  # noqa: E402

RAIZ = fase5.RAIZ
G = "patient_id"
TOL_RED = p5b.TOL_RED
TOL_PROBABILIDAD = p5b.TOL_PROBABILIDAD
USUARIO = "estebandazz"
SLUG = "isic2024-fase5c-modelos"
DIR_5B = os.path.join(RAIZ, "data", "fase5b")


def sha(ruta):
    return fase5.sha256(ruta)


def caso(control, que, ok, debe_fallar, detalle):
    return fase5.caso(control, que, ok, debe_fallar, detalle)


maxima = p5b.maxima  # diferencia máxima; un NaN en el mismo lugar de los dos lados cuenta como igual


def comprobar(d, csv, hdf5, dispositivo, casos):
    import torch
    c = dict(np.load(os.path.join(d, "control.npz")))
    ids = list(c["isic_id"])
    meta = pd.read_csv(csv, low_memory=False)
    filas = meta.set_index("isic_id").loc[ids].reset_index().drop(columns=["target"])
    ajustes = {h: inf.cargar_ajuste(d, h) for h in (False, True)}
    tabla = inf5b.leer_json(os.path.join(d, "celda17.json"))

    xs = {}
    for h, sufijo, nombre in ((False, "", "sin hospital"), (True, "_hospital", "con hospital")):
        x, _ = inf5b.variables_m3(filas, ajustes[h])
        dif = maxima(x.astype(float).to_numpy(), c[f"x_m3{sufijo}"])
        casos.append(caso("variables", f"las variables de M3 limpio {nombre} del control, idénticas",
                          list(x.columns) == list(c[f"x_m3{sufijo}_columnas"]) and dif == 0.0, False,
                          f"diferencia máxima {dif:.1e}"))
        xs[h] = x
    hospital = [n for n in ajustes[True][0]["categoricas_brutas"] if n not in ajustes[False][0]["categoricas_brutas"]]
    casos.append(caso("variables", "el ajuste con hospital solo añade attribution a las categóricas",
                      hospital == ["attribution"], False, hospital))
    casos.append(caso("variables", "las variables con hospital frente a las de sin hospital",
                      list(xs[True].columns) != list(c["x_m3_columnas"]), True,
                      f"{xs[True].shape[1]} frente a {len(c['x_m3_columnas'])} columnas"))

    for h, sufijo in ((False, ""), (True, "_hospital")):
        aj, nz = ajustes[h]
        base = ganador_m3.variables_lectura(meta, aj["listas"], G, aj["medianas"])
        escalada = (base[aj["listas"]["top_lof_features"]].to_numpy(dtype=float) - nz["escala_media"]) / nz["escala_escala"]
        del base
        distintas = int((inf5b.conglomerado(escalada, nz["centros"]) != c[f"etiquetas_kmeans_entrenamiento{sufijo}"]).sum())
        casos.append(caso("variables", f"el k-means en números{' con hospital' if h else ''} asigna como scikit-learn "
                          "las filas de entrenamiento", distintas == 0, False, f"{distintas} de {len(escalada)} distintas"))
    otras = int((inf5b.conglomerado(escalada, nz["centros"][::-1]) != c["etiquetas_kmeans_entrenamiento_hospital"]).sum())
    casos.append(caso("variables", "con los centros en orden inverso", otras > 0, True, f"{otras} distintas"))
    del escalada

    redes = {k: inf5b.red(os.path.join(DIR_5B, "redes", f"{k}.pt"), dispositivo) for k in inf5b.REDES_DE_C7}
    logits, _ = inf5b.recorrer(hdf5, ids, redes, None, dispositivo)
    difs = {k: maxima(logits[k], c["logit_pliegues"][i]) for i, k in enumerate(inf5b.REDES_DE_C7)}
    casos.append(caso("redes", f"los logits de las cinco redes de los pliegues, a {TOL_RED}",
                      max(difs.values()) <= TOL_RED, False, {k: f"{v:.1e}" for k, v in difs.items()}))
    dif = maxima(logits["pliegue-1"], c["logit_pliegues"][0])
    casos.append(caso("redes", "la red del pliegue 1 frente a la referencia del pliegue 0", dif > TOL_RED, True,
                      f"diferencia máxima {dif:.1e}"))
    p = np.mean([inf5b.probabilidad(logits[k]) for k in inf5b.REDES_DE_C7], axis=0)
    dif = maxima(p, c["p_red_media"])
    casos.append(caso("redes", f"la media de las cinco redes, a {TOL_PROBABILIDAD} de la de la Fase 5b",
                      dif <= TOL_PROBABILIDAD, False, f"diferencia máxima {dif:.1e}"))
    del redes
    if dispositivo.type == "mps":
        torch.mps.empty_cache()

    p_guardada = c["p_red_media"]
    edad = xs[True]["age_approx"].to_numpy(np.float64)
    z = inf.z_celda_17(p_guardada, filas, edad, tabla)
    dif = maxima(z, c["z_celda17"])
    casos.append(caso("celda_17", "la variable de la celda 17 con la media guardada de las redes, idéntica",
                      dif == 0.0 and bool(np.array_equal(np.isnan(z), np.isnan(c["z_celda17"]))), False,
                      f"diferencia máxima {dif:.1e}; {int(np.isnan(z).sum())} NaN"))
    un_hospital = filas.assign(attribution=filas["attribution"].mode().iloc[0])
    dif = maxima(inf.z_celda_17(p_guardada, un_hospital, edad, tabla), c["z_celda17"])
    casos.append(caso("celda_17", "con todas las lesiones en un mismo hospital", dif > TOL_PROBABILIDAD, True,
                      f"diferencia máxima {dif:.1e}"))

    for modo in inf.MODOS:
        h = inf.CON_HOSPITAL[modo]
        x = inf.variables(modo, filas, ajustes[h], p_guardada, tabla)
        s, todas = inf.puntuar_promedio(os.path.join(d, "modelos"), modo, x)
        dif = maxima(s, c[modo])
        casos.append(caso(modo, "la media de los 45 modelos" + (" con la media guardada de las redes" if inf.CON_RED[modo]
                                                                 else "") + ", idéntica",
                          dif == 0.0 and todas.shape == c[f"{modo}_por_modelo"].shape, False,
                          f"diferencia máxima {dif:.1e}; {todas.shape[0]} modelos"))
        dif = maxima(todas[0], c[modo])
        casos.append(caso(modo, "con el primer modelo solo", dif > TOL_PROBABILIDAD, True, f"diferencia máxima {dif:.1e}"))
        if inf.CON_RED[modo]:
            s_r, _ = inf.puntuar_promedio(os.path.join(d, "modelos"), modo, inf.variables(modo, filas, ajustes[h], p, tabla))
            dif = maxima(s_r, c[modo])
            casos.append(caso(modo, f"con la media recalculada de las redes, a {TOL_PROBABILIDAD}",
                              dif <= TOL_PROBABILIDAD, False, f"diferencia máxima {dif:.1e}"))


def armar(d, destino):
    """El directorio del conjunto de datos de Kaggle, plano, con su metadata."""
    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.makedirs(destino)
    for f in ("inferencia_5c.py", "inferencia_5b.py", "ganador_m3.py"):
        shutil.copy2(os.path.join(AQUI, f), os.path.join(destino, f))
    for f in ("m3limpio-ajuste.json", "m3limpio-ajuste.npz", "m3limpio-hospital-ajuste.json",
              "m3limpio-hospital-ajuste.npz", "celda17.json", "control.npz"):
        shutil.copy2(os.path.join(d, f), os.path.join(destino, f))
    for modo in inf.MODOS:
        for n in inf.modelos(modo):
            shutil.copy2(os.path.join(d, "modelos", n), os.path.join(destino, n))
    for k in inf5b.REDES_DE_C7:
        shutil.copy2(os.path.join(DIR_5B, "redes", f"{k}.pt"), os.path.join(destino, f"red-{k}.pt"))
    with open(os.path.join(destino, "dataset-metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"title": SLUG, "id": f"{USUARIO}/{SLUG}", "licenses": [{"name": "unknown"}]}, f, indent=2)
    return sorted(os.path.join(destino, f) for f in os.listdir(destino))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dir", default=os.path.join(RAIZ, "data", "fase5c"), help="los artefactos del entrenamiento")
    ap.add_argument("--registro", default=os.path.join(RAIZ, "outputs", "fase5c-entrenamiento.json"))
    args = ap.parse_args()
    import torch
    t0 = time.perf_counter()
    with open(args.registro, encoding="utf-8") as f:
        registro = json.load(f)
    cambiados = [a for a, v in registro["archivos"].items() if sha(os.path.normpath(os.path.join(RAIZ, a))) != v["sha256"]]
    cambiados += [a for a, h in registro["de_la_fase_5b"]["archivos_sha256"].items() if sha(os.path.join(DIR_5B, a)) != h]
    if cambiados:
        raise SystemExit(f"ERROR: archivos distintos de los del entrenamiento: {cambiados}")
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
        "que_es": ("la comprobación en el Mac de inferencia_5c.py frente a las referencias del entrenamiento de la Fase "
                   "5c, y el conjunto de datos privado para el notebook de Kaggle (PLAN.md, Fase 5c); no envía nada"),
        "tolerancias": {"redes_logit": TOL_RED, "probabilidades": TOL_PROBABILIDAD},
        "controles": {"casos": casos, "de_casos": len(casos), "fallos": 0,
                      "deben_fallar": sum(c["debe_fallar"] for c in casos)},
        "conjunto_de_datos": {"id": f"{USUARIO}/{SLUG}", "directorio": os.path.relpath(destino, RAIZ),
                              "archivos": {os.path.relpath(a, destino): {"bytes": os.path.getsize(a), "sha256": sha(a)}
                                           for a in archivos}},
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
    lineas = ["# Fase 5c — la inferencia portátil y el conjunto de datos para Kaggle",
              f"Controles en el Mac: {c['de_casos']} de {c['de_casos']} bien, {c['deben_fallar']} de ellos casos que "
              f"deben fallar (tolerancias: logits {TOL_RED}, probabilidades {TOL_PROBABILIDAD}).",
              f"Conjunto de datos {USUARIO}/{SLUG}: {len(archivos)} archivos, {total / 2**20:.1f} MiB. No envía nada."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']} s", flush=True)


if __name__ == "__main__":
    main()

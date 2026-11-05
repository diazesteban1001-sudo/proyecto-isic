#!/usr/bin/env python3
"""
fase5_posterior.py — dos comprobaciones descriptivas hechas después de abrir el
reservado (PLAN.md, Fase 5, «Análisis posterior a la apertura»; decisión de la
persona del 2026-11-04). No cambian ningún modelo ni ninguna recomendación, no
entrenan nada y no vuelven a correr la apertura: leen sus archivos.

1. La procedencia de las características de DINOv2 del reservado frente a las
   del desarrollo, y la identidad de «Imagen + básicos»:
   - los atributos de los dos archivos —modelo, pesos, preprocesado,
     característica y commit del código— son iguales, salvo el conjunto, y son
     los de outputs/extraccion-imagen.json, una sola corrida; los dos SHA-256
     son los que esa corrida registró;
   - recalculadas con DINOv2 desde las imágenes, con el preprocesado de
     extraer.py y la función de tiempo_inferencia.py, MUESTRA recortes al azar
     de cada archivo difieren del archivo en TOLERANCIA como máximo, la de
     tiempo_inferencia.py. Caso que debe fallar: sin la normalización;
   - «Imagen + básicos» de la Fase 5 es el de outputs/imagen-sola.json: el
     ensayo reprodujo su pliegue 0 de la semilla 0 a 4 decimales, con la misma
     huella de código que la apertura, y el archivo de desarrollo que leyó
     imagen-sola.json es el de la extracción.
2. Con las remuestras guardadas de la apertura, la diferencia red de la 4e −
   «Imagen + básicos» en el reservado, con las mismas remuestras, y una tabla de
   cada modelo en desarrollo y en el reservado.

Antes de calcular, las remuestras y las puntuaciones guardadas tienen que
reproducir lo que escribió la apertura: los puntos, a 4 decimales, desde las
puntuaciones y las etiquetas; los intervalos de cada modelo y el de M3 limpio −
M2, desde las remuestras. Cada comprobación tiene su caso que debe fallar. Si
una falla, no se escribe nada.

No interpreta: mide y escribe --out.json y su .md.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5_posterior.py --out outputs/fase5-posterior
"""

import argparse
import datetime
import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "extraccion-imagen", "scripts"))
import fase4_comparar as f4  # noqa: E402
import fase5  # noqa: E402
import extraer  # noqa: E402

RAIZ = fase5.RAIZ
MUESTRA = 256
SEMILLA_MUESTRA = 0
TOLERANCIA = 1e-3  # la de tiempo_inferencia.py
ATRIBUTOS = ("modelo", "pesos_sha256", "preprocesado", "caracteristica", "codigo_commit")
NOMBRES = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return json.load(f)


def atributos(ruta):
    import h5py
    with h5py.File(os.path.join(RAIZ, ruta), "r") as h:
        return {k: (v if isinstance(v, str) else str(v)) for k, v in h.attrs.items()}


def procedencia(casos):
    """Atributos y SHA-256 de los dos archivos frente a la extracción."""
    ext = leer("outputs/extraccion-imagen.json")
    archivos = {c: ext["conjuntos"][c]["archivo"] for c in ("desarrollo", "reservado")}
    attrs = {c: atributos(archivos[c]["archivo"]) for c in archivos}
    esperado = {"modelo": ext["modelo"]["nombre"], "pesos_sha256": ext["modelo"]["pesos"]["sha256"],
                "preprocesado": ext["preprocesado"], "caracteristica": ext["caracteristica"],
                "codigo_commit": ext["codigo_commit"]}
    iguales = all(attrs["desarrollo"][k] == attrs["reservado"][k] == esperado[k] for k in ATRIBUTOS)
    casos.append(fase5.caso("procedencia", "los dos archivos tienen los atributos de la extracción, salvo el conjunto",
                            iguales and attrs["desarrollo"]["conjunto"] == "desarrollo"
                            and attrs["reservado"]["conjunto"] == "reservado", False,
                            {k: esperado[k] for k in ATRIBUTOS}))
    otro = {**attrs["reservado"], "preprocesado": extraer.PREPROCESADO.replace("bicúbico", "bilineal")}
    casos.append(fase5.caso("procedencia", "con otro preprocesado en el del reservado",
                            any(otro[k] != esperado[k] for k in ATRIBUTOS), True, "se detecta"))
    actual = {"modelo": extraer.MODELO, "pesos_sha256": extraer.PESOS_SHA256, "preprocesado": extraer.PREPROCESADO,
              "caracteristica": extraer.CARACTERISTICA}
    casos.append(fase5.caso("procedencia", "extraer.py declara hoy el mismo modelo, pesos, preprocesado y característica",
                            all(actual[k] == esperado[k] for k in actual), False, "iguales"))
    shas = {c: fase5.sha256(os.path.join(RAIZ, archivos[c]["archivo"])) for c in archivos}
    casos.append(fase5.caso("procedencia", "los dos SHA-256 son los que registró la extracción",
                            all(shas[c] == archivos[c]["sha256"] for c in archivos), False,
                            {c: s[:12] + "…" for c, s in shas.items()}))
    casos.append(fase5.caso("procedencia", "el del reservado frente al registrado para el desarrollo",
                            shas["reservado"] != archivos["desarrollo"]["sha256"], True, "distintos"))
    return {"extraccion": {"fecha": ext["fecha"], "una_sola_corrida": True, "lote": ext["lote"],
                           "dispositivo": ext["dispositivo"], "repositorio_commit": ext["modelo"]["repositorio_commit"]},
            "atributos_comunes": {k: esperado[k] for k in ATRIBUTOS},
            "archivos": {c: {"archivo": archivos[c]["archivo"], "sha256": shas[c]} for c in archivos}}, archivos


def recalculo(archivos, casos):
    """DINOv2 recalculado desde las imágenes para MUESTRA recortes de cada archivo."""
    import h5py
    import torch
    import tiempo_inferencia as ti
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible; la extracción se hizo en MPS.")
    ruta_pesos = os.path.join(torch.hub.get_dir(), "checkpoints", extraer.PESOS)
    if extraer.sha256(ruta_pesos) != extraer.PESOS_SHA256:
        raise SystemExit("ERROR: los pesos de DINOv2 no son los de la extracción.")
    repo = os.path.join(RAIZ, "data", "dinov2-" + leer("outputs/extraccion-imagen.json")["modelo"]["repositorio_commit"])
    sys.path.insert(0, repo)
    from dinov2.hub import backbones  # noqa: E402
    dispositivo = torch.device("mps")
    modelo = getattr(backbones, extraer.MODELO)(pretrained=True).eval().to(dispositivo)
    hdf5 = os.path.join(RAIZ, "data", "train-image.hdf5")
    salida = {}
    for c, a in archivos.items():
        with h5py.File(os.path.join(RAIZ, a["archivo"]), "r") as h:
            n = h["isic_id"].shape[0]
            pos = np.sort(np.random.default_rng(SEMILLA_MUESTRA).choice(n, size=MUESTRA, replace=False))
            ids = list(h["isic_id"].asstr()[pos])
            guardadas = h["cls"][pos]
        nuevas = ti.caracteristicas_dinov2(ids, hdf5, modelo, dispositivo)
        sin_normalizar = ti.caracteristicas_dinov2(ids, hdf5, modelo, dispositivo, {"preprocesado"})
        d, d_mal = float(np.abs(nuevas - guardadas).max()), float(np.abs(sin_normalizar - guardadas).max())
        casos.append(fase5.caso("recalculo", f"{c}: DINOv2 recalculado en {MUESTRA} recortes, a {TOLERANCIA} o menos",
                                d <= TOLERANCIA, False, f"diferencia máxima {d:.2e}"))
        casos.append(fase5.caso("recalculo", f"{c}: sin la normalización del preprocesado", d_mal > TOLERANCIA, True,
                                f"diferencia máxima {d_mal:.2e}"))
        salida[c] = {"recortes": MUESTRA, "diferencia_maxima": d, "diferencia_maxima_sin_normalizar": d_mal}
    return {"muestra": MUESTRA, "semilla": SEMILLA_MUESTRA, "tolerancia": TOLERANCIA,
            "funcion": "tiempo_inferencia.caracteristicas_dinov2, con extraer.preprocesar, lote 64, MPS",
            "por_archivo": salida}


def identidad_imagen_basicos(casos):
    ensayo, apertura = leer("outputs/fase5-ensayo.json"), leer("outputs/fase5-reservado.json")
    rep = [c for c in ensayo["controles"]["casos"]
           if c["control"] == "reproduccion" and c["caso"].startswith("«Imagen + básicos»")]
    casos.append(fase5.caso("imagen_basicos", "el ensayo reprodujo su pliegue 0 de imagen-sola.json, y su caso que debe "
                            "fallar se disparó", len(rep) == 2 and all(c["ok"] for c in rep), False,
                            [c["caso"] for c in rep]))
    casos.append(fase5.caso("imagen_basicos", "la apertura corrió con la huella de código del ensayo",
                            apertura["sha256_del_codigo"] == ensayo["sha256_del_codigo"], False,
                            {k: apertura["sha256_del_codigo"][k][:12] + "…" for k in ("imagen_sola.py", "apilado_imagen.py",
                                                                                     "fase5.py")}))
    sola = leer("outputs/imagen-sola.json")
    ext = leer("outputs/extraccion-imagen.json")["conjuntos"]
    casos.append(fase5.caso("imagen_basicos", "imagen-sola.json leyó el archivo de desarrollo de la extracción",
                            sola["comprobacion_imagen"]["sha256"] == ext["desarrollo"]["archivo"]["sha256"], False,
                            sola["comprobacion_imagen"]["sha256"][:12] + "…"))
    casos.append(fase5.caso("imagen_basicos", "frente al SHA-256 del reservado",
                            sola["comprobacion_imagen"]["sha256"] != ext["reservado"]["archivo"]["sha256"], True,
                            "distintos"))
    return {"modelo": apertura["modelos"]["ImagenBasicos"]["descripcion"],
            "n_variables": {"fase5": apertura["entrenamiento"]["ImagenBasicos"]["n_variables"]},
            "diferencia": ("en imagen-sola.json se ajusta con el pliegue de entrenamiento (cuatro quintos del "
                           "desarrollo); en la Fase 5, con todo el desarrollo")}


def guardados(casos):
    """Las puntuaciones y las remuestras de la apertura, comprobadas contra su salida."""
    ap = leer("outputs/fase5-reservado.json")
    tablas = {}
    for k in ("puntuaciones", "remuestras"):
        a = ap["archivos"][k]
        ruta = os.path.join(RAIZ, a["archivo"])
        bien = fase5.sha256(ruta) == a["sha256"]
        casos.append(fase5.caso("guardados", f"{a['archivo']} tiene el SHA-256 de la salida de la apertura", bien, False,
                                a["sha256"][:12] + "…"))
        if not bien:
            raise SystemExit(f"ERROR: {a['archivo']} no es el que escribió la apertura.")
        tablas[k] = pd.read_csv(ruta, float_precision="round_trip")
    p, rem = tablas["puntuaciones"], tablas["remuestras"]
    r = fase5.rutas(RAIZ)
    y = fase5.etiquetas_de(r["csv"], p["isic_id"].to_numpy(), "apertura", r["holdout"])
    g = p[fase5.G].astype(str).to_numpy()
    puntos = {m: f4.medir(y, p[m].to_numpy(np.float64), g) for m in fase5.MODELOS}
    bien = all(round(puntos[m][k], 4) == ap["metricas"][m][k]["punto"] for m in fase5.MODELOS for k in f4.METRICAS)
    casos.append(fase5.caso("guardados", "los puntos de los cuatro modelos, recalculados, a 4 decimales", bien, False,
                            f"{len(y)} lesiones, {int(y.sum())} malignas"))
    casos.append(fase5.caso("guardados", "los de la red frente a los guardados de «Imagen + básicos»",
                            not all(round(puntos["Red4e"][k], 4) == ap["metricas"]["ImagenBasicos"][k]["punto"]
                                    for k in f4.METRICAS), True, "distintos"))
    valores = {}
    for m in fase5.MODELOS:
        t = rem[rem["modelo"] == m].sort_values("remuestra")
        if list(t["remuestra"]) != list(range(fase5.REMUESTRAS)):
            raise SystemExit(f"ERROR: las remuestras de {m} no son 0 a {fase5.REMUESTRAS - 1}.")
        valores[m] = {k: t[k].to_numpy(np.float64) for k in f4.METRICAS}
    bien = all(fase5.intervalo(valores[m][k]) == ap["metricas"][m][k]["intervalo_95"]
               for m in fase5.MODELOS for k in f4.METRICAS)
    casos.append(fase5.caso("guardados", "los intervalos de los cuatro modelos, desde las remuestras", bien, False,
                            f"{fase5.REMUESTRAS} remuestras por modelo"))
    casos.append(fase5.caso("guardados", "los de la red frente a los guardados de «Imagen + básicos»",
                            not all(fase5.intervalo(valores["Red4e"][k]) == ap["metricas"]["ImagenBasicos"][k]["intervalo_95"]
                                    for k in f4.METRICAS), True, "distintos"))
    pareada = all(fase5.intervalo(valores["M3limpio"][k] - valores["M2"][k]) ==
                  ap["diferencia_m3limpio_menos_m2"][k]["intervalo_95"] for k in f4.METRICAS)
    casos.append(fase5.caso("guardados", "M3 limpio − M2, remuestra a remuestra, da los intervalos de la apertura",
                            pareada, False, "las remuestras están pareadas"))
    barajada = np.random.default_rng(0).permutation(fase5.REMUESTRAS)
    casos.append(fase5.caso("guardados", "con las remuestras de M2 barajadas",
                            not all(fase5.intervalo(valores["M3limpio"][k] - valores["M2"][k][barajada]) ==
                                    ap["diferencia_m3limpio_menos_m2"][k]["intervalo_95"] for k in f4.METRICAS), True,
                            "distintos"))
    return ap, puntos, valores


def tabla(ap, red_menos_ib):
    """Cada modelo en desarrollo, con sus semillas y su fuente, y en el reservado."""
    def medias(archivo, modelo):
        d = leer(f"outputs/{archivo}")
        return {"fuente": f"outputs/{archivo} > metricas.{modelo}.*.media_global",
                "semillas": d.get("semillas_corridas") or d["esquema"]["semillas"], "pliegues": 5,
                **{k: d["metricas"][modelo][k]["media_global"] for k in f4.METRICAS}}

    def diferencias(archivo):
        d = leer(f"outputs/{archivo}")
        c = d["comparaciones_nuevo_menos_base"]
        return {"fuente": f"outputs/{archivo} > comparaciones_nuevo_menos_base.*", "semillas": d["semillas_corridas"],
                "pliegues": 5, "intervalo": "t al 95 % con la corrección de Nadeau y Bengio",
                **{k: {"media": c[k]["media"], "intervalo_95": c[k]["intervalo_t_95_nadeau_bengio"]} for k in f4.METRICAS}}

    def reservado(m):
        return {k: ap["metricas"][m][k] for k in f4.METRICAS}
    filas = {
        "M3limpio": {"desarrollo": [medias("fase4-m3limpio-vs-m2.json", "M3limpio")], "reservado": reservado("M3limpio")},
        "M2": {"desarrollo": [medias("fase4-m2-vs-m1.json", "M2")], "reservado": reservado("M2")},
        "Red4e": {"desarrollo": [medias("fase4f-red4e-vs-imagen-basicos.json", "Red4eAjustada")],
                  "reservado": reservado("Red4e")},
        "ImagenBasicos": {"desarrollo": [medias("imagen-sola.json", "Imagen + básicos"),
                                         medias("fase4f-red4e-vs-imagen-basicos.json", "ImagenBasicos")],
                          "reservado": reservado("ImagenBasicos")},
    }
    difs = {
        "m3limpio_menos_m2": {"desarrollo": diferencias("fase4-m3limpio-vs-m2.json"),
                              "reservado": ap["diferencia_m3limpio_menos_m2"]},
        "red4e_menos_imagen_basicos": {"desarrollo": diferencias("fase4f-red4e-vs-imagen-basicos.json"),
                                       "reservado": red_menos_ib},
    }
    return filas, difs


def escribir_md(out, res):
    f, d = res["tabla"]["modelos"], res["tabla"]["diferencias"]
    rc = res["recalculo"]["por_archivo"]

    def sem(s):
        return f"{s[0]} a {s[-1]}"

    def iv(v):
        return f"{v['punto']} [{v['intervalo_95'][0]}; {v['intervalo_95'][1]}]"
    nombres = {"M3limpio": "M3 limpio", "M2": "M2", "Red4e": "Red de la 4e", "ImagenBasicos": "Imagen + básicos"}
    lineas = ["# Fase 5 — análisis posterior a la apertura (descriptivo)",
              f"DINOv2: los dos archivos, de una sola extracción, con los mismos atributos y los SHA-256 registrados; "
              f"recalculado en {res['recalculo']['muestra']} recortes de cada uno, diferencia máxima "
              f"{rc['desarrollo']['diferencia_maxima']:.1e} y {rc['reservado']['diferencia_maxima']:.1e} "
              f"(tolerancia {TOLERANCIA}). «Imagen + básicos»: el de imagen-sola.json, con todo el desarrollo.",
              "Red de la 4e − «Imagen + básicos» en el reservado, mismas remuestras: "
              + " · ".join(f"{NOMBRES[k]} {iv(res['red4e_menos_imagen_basicos'][k])}" for k in f4.METRICAS),
              "| pAUC | desarrollo (semillas) | reservado [95 %] |", "|---|---|---|"]
    for m, fila in f.items():
        dev = "; ".join(f"{x['pauc']} ({sem(x['semillas'])})" for x in fila["desarrollo"])
        lineas.append(f"| {nombres[m]} | {dev} | {iv(fila['reservado']['pauc'])} |")
    for k, nombre in (("m3limpio_menos_m2", "M3 limpio − M2"), ("red4e_menos_imagen_basicos", "Red − Imagen + básicos")):
        x = d[k]["desarrollo"]
        nb = x["pauc"]["intervalo_95"]
        lineas.append(f"| {nombre} | {x['pauc']['media']} [{nb[0]}; {nb[1]}] ({sem(x['semillas'])}, NB) | "
                      f"{iv(d[k]['reservado']['pauc'])} |")
    c = res["controles"]
    lineas += [f"Controles: {c['de_casos'] - c['fallos']} de {c['de_casos']} bien, {c['deben_fallar']} de ellos casos que "
               "deben fallar. Las cuatro métricas, en el .json. Posterior a la apertura; no interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas) + "\n")
    if len(lineas) > 15:
        raise SystemExit(f"ERROR: el .md tiene {len(lineas)} líneas; el contrato pide 15 como máximo.")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--out", required=True)
    args = ap_.parse_args()
    t0 = time.perf_counter()
    if not os.path.exists(os.path.join(RAIZ, "outputs", "fase5-reservado.json")):
        raise SystemExit("ERROR: este análisis es posterior a la apertura, y falta outputs/fase5-reservado.json.")
    casos = []
    pr, archivos = procedencia(casos)
    rc = recalculo(archivos, casos)
    ib = identidad_imagen_basicos(casos)
    ap, puntos, valores = guardados(casos)
    red_menos_ib = {}
    for k in f4.METRICAS:
        dif = valores["Red4e"][k] - valores["ImagenBasicos"][k]
        iv = fase5.intervalo(dif)
        red_menos_ib[k] = {"punto": round(puntos["Red4e"][k] - puntos["ImagenBasicos"][k], 4), "intervalo_95": iv,
                           "intervalo_excluye_el_cero": bool(np.percentile(dif, fase5.PERCENTILES[0]) > 0
                                                             or np.percentile(dif, fase5.PERCENTILES[1]) < 0)}
    filas, difs = tabla(ap, red_menos_ib)
    fallos = [f"{c['control']}: {c['caso']}" for c in casos if not c["ok"]]
    if fallos:
        raise SystemExit("ERROR: fallaron controles; no se escribe nada:\n  " + "\n  ".join(fallos))
    resultado = {
        "que_es": ("análisis descriptivo posterior a la apertura del reservado (PLAN.md, Fase 5, «Análisis posterior a "
                   "la apertura», decisión de la persona del 2026-11-04); no cambia ningún modelo ni ninguna "
                   "recomendación, y no entrena nada"),
        "procedencia": pr,
        "recalculo": rc,
        "imagen_basicos": ib,
        "red4e_menos_imagen_basicos": red_menos_ib,
        "bootstrap": {"remuestras": fase5.REMUESTRAS, "semilla": fase5.SEMILLA_BOOTSTRAP,
                      "de": ap["archivos"]["remuestras"]["archivo"],
                      "pareo": "la misma remuestra para los dos modelos, como M3 limpio − M2 en la apertura"},
        "tabla": {"modelos": filas, "diferencias": difs,
                  "como_leerla": ("en desarrollo, la media de las métricas por pliegue sobre las semillas indicadas, "
                                  "cada pliegue con un modelo entrenado con cuatro quintos del desarrollo, y en las "
                                  "diferencias el intervalo de Nadeau y Bengio; en el reservado, un solo modelo "
                                  "entrenado con todo el desarrollo, con el intervalo del bootstrap por paciente. Los "
                                  "dos intervalos no miden lo mismo")},
        "controles": {"casos": casos, "de_casos": len(casos), "fallos": 0,
                      "deben_fallar": sum(c["debe_fallar"] for c in casos)},
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "segundos": round(time.perf_counter() - t0, 1),
        "nota": "No interpreta. Posterior a la apertura: no vuelve a abrir el reservado ni a entrenar.",
    }
    out = os.path.join(RAIZ, args.out) if not os.path.isabs(args.out) else args.out
    with open(out + ".json", "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=2)
    escribir_md(out, resultado)
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']} s", flush=True)


if __name__ == "__main__":
    main()

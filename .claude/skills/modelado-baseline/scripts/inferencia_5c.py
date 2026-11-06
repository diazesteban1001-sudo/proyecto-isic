#!/usr/bin/env python3
"""
inferencia_5c.py — la inferencia de los envíos de la Fase 5c (PLAN.md), la misma
en el Mac y en el notebook de Kaggle, que corre sin internet. Usa la de la Fase
5b, inferencia_5b.py, que viaja con ella, sin cambiarla:

- las variables de M3 limpio, con o sin hospital, son inferencia_5b.variables_m3
  con el ajuste que corresponde; el hospital solo cambia el one-hot;
- las cinco redes de los pliegues y su media, inferencia_5b.red, .recorrer y
  .probabilidad; las dos variables de imagen de C7, inferencia_5b.variables_c7.

Lo que añade:
- puntuar_promedio: la media de las probabilidades de los 45 CatBoost de un
  envío, en el orden de SEMILLAS y de los pliegues, como fase5c_entrenar.py;
- z_celda_17: la puntuación estandarizada por hospital, zona y edad con la tabla
  del entrenamiento, como fase4d.estandarizar.

No lee etiquetas ni calcula métricas.
"""

import os

import numpy as np
import pandas as pd

import inferencia_5b as inf5b

SEMILLAS = list(range(1, 10))
N_SPLITS = 5
MODOS = ("M3limpioProm", "M3limpioPromHosp", "C7Prom", "C7PromHosp")
CON_HOSPITAL = {"M3limpioProm": False, "M3limpioPromHosp": True, "C7Prom": False, "C7PromHosp": True}
CON_RED = {"M3limpioProm": False, "M3limpioPromHosp": False, "C7Prom": True, "C7PromHosp": True}
Z_CELDA_17 = "red_z_hospital_zona_edad"


def nombre_modelo(modo, semilla, pliegue):
    """fase5c_entrenar.nombre_modelo."""
    return f"cbm-{modo}-s{semilla}-p{pliegue}.cbm"


def modelos(modo):
    return [nombre_modelo(modo, s, k) for s in SEMILLAS for k in range(N_SPLITS)]


def cargar_ajuste(directorio, hospital):
    nombre = "m3limpio-hospital-ajuste" if hospital else "m3limpio-ajuste"
    return inf5b.leer_json(os.path.join(directorio, f"{nombre}.json")), \
        dict(np.load(os.path.join(directorio, f"{nombre}.npz")))


def puntuar_promedio(directorio, modo, x):
    """(media de las 45 probabilidades, las 45 por separado)."""
    todas = np.stack([inf5b.puntuar_cbm(os.path.join(directorio, n), x) for n in modelos(modo)])
    return todas.mean(axis=0), todas


def z_celda_17(p, filas, edad, tabla):
    """(p − media del grupo)/desviación del grupo, con la media y la desviación del
    entrenamiento por attribution, tbp_lv_location y la edad imputada; NaN si el grupo
    no está en la tabla, si tiene una sola lesión o si su desviación es 0."""
    claves = tabla["claves"]
    agg = pd.DataFrame([f[:5] for f in tabla["filas"]], columns=[*claves, "mean", "std"])
    izq = pd.DataFrame({claves[0]: filas[claves[0]].to_numpy(), claves[1]: filas[claves[1]].to_numpy(),
                        claves[2]: np.asarray(edad, dtype=np.float64)})
    m = izq.merge(agg, how="left", on=claves)
    if len(m) != len(izq):
        raise SystemExit("ERROR: la estandarización duplicó filas al unir por grupo.")
    sd = m["std"].to_numpy(np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (np.asarray(p, dtype=np.float64) - m["mean"].to_numpy(np.float64)) / sd
    z[~(sd > 0)] = np.nan
    return z


def variables(modo, filas, ajuste, p_media=None, tabla=None):
    """Las variables de un envío para filas nuevas (sin etiqueta): las de M3 limpio con
    su ajuste y, en C7, las dos de la red con la media de las cinco y, con hospital, la
    de la celda 17 al final."""
    x, _ = inf5b.variables_m3(filas, ajuste)
    if not CON_RED[modo]:
        return x
    x = inf5b.variables_c7(x, p_media, filas[inf5b.G].astype(str).to_numpy())
    if CON_HOSPITAL[modo]:
        x[Z_CELDA_17] = z_celda_17(p_media, filas, x["age_approx"].to_numpy(np.float64), tabla)
    return x

#!/usr/bin/env python3
"""
fase4c.py — las piezas de la Fase 4c (PLAN.md, decisión de la persona del
2026-10-22): una red de imagen entrenada sobre los recortes. No corre la fase:
test_fase4c_controles.py controla estas piezas antes, fase4c_redes.py entrena las
redes y fase4c_comparar.py responde las dos preguntas.

- Los ajustes de la red son los de la prueba de tiempo
  (outputs/prueba-tiempo-red-imagen.json): entrada de LADO × LADO con la
  normalización de ImageNet, AdamW con tasa TASA y lo demás por defecto, lote
  LOTE, EPOCAS épocas y NEGATIVOS_POR_POSITIVO negativos por positivo. La
  decodificación, la normalización y la carga de EfficientNet-B0 con la
  comprobación de su SHA-256 se importan de prueba_tiempo_red_imagen.py, así que
  son las mismas por construcción; comprobar_ajustes() compara las constantes con
  lo que la prueba registró.
- entrenar_y_puntuar(): entrena una red de punta a punta y devuelve su logit
  sobre otras filas. En cada época, todos los positivos y una submuestra nueva de
  negativos, sorteada con la semilla externa; volteos horizontales y verticales
  al azar, solo al entrenar. No lee las etiquetas de las filas que puntúa.
- probabilidad(): la sigmoide del logit, en float64. Es la puntuación de la fase.
- variables_red(): las dos variables de C4, la puntuación y su razón contra la
  media del paciente, con apilado_imagen.razon_paciente, como M4b y C2.
- ensamblar(): une por isic_id las puntuaciones de cada red y comprueba que cada
  fila recibe exactamente una, la de la red en cuya validación está.
- caffeinate(): si caffeinate mantiene despierto el equipo por este proceso o por
  uno de sus padres.
"""

import os
import re
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import torch
from scipy.special import expit

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from apilado_imagen import razon_paciente  # noqa: E402
from prueba_tiempo_red_imagen import a_tensor, decodificar, red, sincronizar  # noqa: E402

LADO = 128
TASA = 1e-4
LOTE = 64
EPOCAS = 3
NEGATIVOS_POR_POSITIVO = 20
LOTE_PREDICCION = 256  # el de la prueba de tiempo al predecir; no cambia el modelo
BLOQUE = 4096  # imágenes que se decodifican de una vez al predecir
PRUEBA_DE_TIEMPO = os.path.normpath(os.path.join(AQUI, "..", "..", "..", "..", "outputs",
                                                 "prueba-tiempo-red-imagen.json"))


def comprobar_ajustes(prueba):
    """Las diferencias entre las constantes de esta fase y lo que registró la prueba
    de tiempo (su JSON ya leído). Lista vacía si coinciden."""
    e, n = prueba["entrenamiento"], prueba["entrada"]
    esperado = [
        ("entrada.lado_px", n["lado_px"], LADO),
        ("entrada.preprocesado incluye la normalización de ImageNet",
         "normalización de ImageNet" in n["preprocesado"], True),
        ("entrenamiento.optimizador", e["optimizador"], f"AdamW, tasa {TASA}, el resto por defecto"),
        ("entrenamiento.lote", e["lote"], LOTE),
        ("entrenamiento.epocas", e["epocas"], EPOCAS),
        ("entrenamiento.negativos_por_positivo", e["negativos_por_positivo"], NEGATIVOS_POR_POSITIVO),
        ("entrenamiento.precision", e["precision"], "float32"),
    ]
    return [{"campo": c, "prueba": a, "fase4c": b} for c, a, b in esperado if a != b]


def entrenar_y_puntuar(f, isic, etiquetas, filas_ent, filas_pred, semilla, dispositivo, epocas=EPOCAS):
    """Entrena una red con las filas filas_ent (índices sobre isic y etiquetas) y
    devuelve (logit en float32 para filas_pred, en ese orden; registro). Solo se
    leen las etiquetas de filas_ent."""
    t_inicio = time.perf_counter()
    filas_ent, filas_pred = np.asarray(filas_ent), np.asarray(filas_pred)
    if np.intersect1d(filas_ent, filas_pred).size:
        raise SystemExit("ERROR: la red puntuaría filas con las que se entrena.")
    y_ent = etiquetas[filas_ent]
    pos, neg = filas_ent[y_ent == 1], filas_ent[y_ent == 0]
    n_neg = NEGATIVOS_POR_POSITIVO * len(pos)
    if len(pos) == 0 or n_neg > len(neg):
        raise SystemExit(f"ERROR: {len(pos)} positivos y {len(neg)} negativos no alcanzan para "
                         f"{NEGATIVOS_POR_POSITIVO} negativos por positivo.")
    rng = np.random.default_rng(semilla)  # las submuestras de negativos
    g = torch.Generator().manual_seed(semilla)  # el orden de los lotes y los volteos
    torch.manual_seed(semilla)  # la capa de salida nueva
    modelo, pesos = red(dispositivo)
    opt = torch.optim.AdamW(modelo.parameters(), lr=TASA)
    perdida = torch.nn.BCEWithLogitsLoss()

    s_dec, s_epoca = [], []
    modelo.train()
    for _e in range(epocas):
        filas = np.sort(np.concatenate([pos, rng.choice(neg, size=n_neg, replace=False)]))
        t0 = time.perf_counter()
        x = decodificar(f, isic[filas], LADO)
        s_dec.append(round(time.perf_counter() - t0, 3))
        yt = torch.from_numpy(etiquetas[filas].astype(np.float32))
        orden = torch.randperm(len(filas), generator=g).numpy()
        t0 = time.perf_counter()
        for i in range(0, len(orden), LOTE):
            b = orden[i: i + LOTE]
            xb = a_tensor(x[b], dispositivo)
            h = (torch.rand(len(b), generator=g) < 0.5).view(-1, 1, 1, 1).to(dispositivo)
            v = (torch.rand(len(b), generator=g) < 0.5).view(-1, 1, 1, 1).to(dispositivo)
            xb = torch.where(h, xb.flip(3), xb)
            xb = torch.where(v, xb.flip(2), xb)
            opt.zero_grad(set_to_none=True)
            loss = perdida(modelo(xb).squeeze(1), yt[b].to(dispositivo))
            loss.backward()
            opt.step()
        sincronizar()
        s_epoca.append(round(time.perf_counter() - t0, 3))
        del x

    modelo.eval()
    logit = np.empty(len(filas_pred), dtype=np.float32)
    t_dec_p = t_mod_p = 0.0
    with torch.no_grad():
        for i in range(0, len(filas_pred), BLOQUE):
            t0 = time.perf_counter()
            bloque = decodificar(f, isic[filas_pred[i: i + BLOQUE]], LADO)
            t_dec_p += time.perf_counter() - t0
            t0 = time.perf_counter()
            salidas = [modelo(a_tensor(bloque[j: j + LOTE_PREDICCION], dispositivo)).squeeze(1).float().cpu()
                       for j in range(0, len(bloque), LOTE_PREDICCION)]
            sincronizar()
            logit[i: i + len(bloque)] = torch.cat(salidas).numpy()
            t_mod_p += time.perf_counter() - t0
    del modelo, opt
    torch.mps.empty_cache()
    registro = {
        "semilla": int(semilla), "positivos": int(len(pos)), "negativos_por_epoca": int(n_neg),
        "imagenes_por_epoca": int(len(pos) + n_neg), "epocas": int(epocas), "filas_puntuadas": int(len(filas_pred)),
        "segundos_decodificacion_por_epoca": s_dec, "segundos_por_epoca": s_epoca,
        "segundos_prediccion_modelo": round(t_mod_p, 3), "segundos_prediccion_decodificacion": round(t_dec_p, 3),
        "segundos_total": round(time.perf_counter() - t_inicio, 3), "sha256_pesos": pesos["sha256"],
    }
    return logit, registro


def probabilidad(logit):
    """La puntuación de la fase: la sigmoide del logit, calculada en float64."""
    return expit(np.asarray(logit, dtype=np.float64))


def variables_red(p, tr, va, grupos):
    """Las dos variables de C4 en un pliegue, con la forma que recibe
    fase4b.con_imagen: la puntuación de la red y su razón contra la media del
    paciente, a cada lado con sus propias filas, como en M4b y C2."""
    p = np.asarray(p, dtype=np.float64)
    if not np.all(p[np.concatenate([tr, va])] > 0):
        raise SystemExit("ERROR: hay puntuaciones de la red que no son positivas; la razón por paciente no se puede "
                         "calcular.")
    return {"tr": {"puntuacion": p[tr], "razon": razon_paciente(p[tr], grupos[tr])},
            "va": {"puntuacion": p[va], "razon": razon_paciente(p[va], grupos[va])}}


def ensamblar(partes, isic, asignacion):
    """partes: {k: (isic_id, logit)} de cada red k. isic: los isic_id del universo, y
    asignacion[r]: la red en cuya validación está la fila r. Une por isic_id y se
    detiene si un isic_id no es del universo, si una fila recibe la puntuación de
    otra red, si se repite o si falta. Devuelve el logit en el orden de isic."""
    indice = pd.Index(isic)
    if not indice.is_unique:
        raise SystemExit("ERROR: el universo tiene isic_id repetidos.")
    logit = np.full(len(isic), np.nan, dtype=np.float64)
    veces = np.zeros(len(isic), dtype=np.int64)
    for k, (ids, valores) in partes.items():
        filas = indice.get_indexer(ids)
        if (filas < 0).any():
            raise SystemExit(f"ERROR: la red {k} puntúa {int((filas < 0).sum())} isic_id que no son del universo.")
        if (asignacion[filas] != k).any():
            raise SystemExit(f"ERROR: la red {k} puntúa {int((asignacion[filas] != k).sum())} filas que no están en su "
                             "validación.")
        np.add.at(veces, filas, 1)
        logit[filas] = np.asarray(valores, dtype=np.float64)
    if (veces != 1).any():
        raise SystemExit(f"ERROR: {int((veces == 0).sum())} filas sin puntuación y {int((veces > 1).sum())} con más "
                         "de una.")
    return logit


def caffeinate():
    """Si caffeinate mantiene despierto el equipo por este proceso o por uno de sus
    padres. caffeinate no queda en la cadena de procesos: se separa y deja una
    aserción de energía a nombre del PID del programa que lanzó."""
    pids, p = [], os.getpid()
    while p > 1 and len(pids) < 10:
        pids.append(p)
        salida = subprocess.run(["ps", "-o", "ppid=", "-p", str(p)], capture_output=True, text=True).stdout.strip()
        p = int(salida) if salida else 1
    lineas = subprocess.run(["pmset", "-g", "assertions"], capture_output=True, text=True).stdout.splitlines()
    for previa, linea in zip(lineas, lineas[1:]):
        m = re.search(r"caffeinate asserting on behalf of .* \(pid (\d+)\)", linea)
        if m and int(m.group(1)) in pids:
            tipo = re.search(r"\(caffeinate\): \[[^\]]*\] \S+ (\w+) named", previa)
            return {"activo": True, "asercion": tipo.group(1) if tipo else None,
                    "a_nombre_de": "este proceso" if int(m.group(1)) == pids[0] else "un proceso padre"}
    return {"activo": False, "asercion": None, "a_nombre_de": None}

#!/usr/bin/env python3
"""
fase4d.py — las piezas de la Fase 4d (PLAN.md, decisión de la persona del
2026-10-30): acercarse al ganador con estadística y con el equipo propio. No
corre la fase: test_fase4d_comparacion.py y test_fase4d_controles.py controlan
estas piezas antes, fase4d_redes.py entrena la red mejorada, fase4d_comparar.py
responde las tres preguntas y fase4d_holm.py aplica la regla.

- La comparación: valor_p() es el valor p bilateral de la t corregida de Nadeau y
  Bengio, con la misma varianza y los mismos grados de libertad que los
  intervalos de las fases anteriores (fase4b_comparar.nadeau_bengio); holm() es
  el procedimiento de Holm sobre los valores p de las tres preguntas, y una
  pregunta da su resultado a favor si Holm la acepta y su diferencia media es
  positiva (decisión 3).
- C5 (pregunta 1) y C6 (pregunta 3): variables_c5() construye las seis
  variables de la red, copiando las celdas 15, 17 y 19 de top-model.ipynb sin el
  hospital (decisiones 5 y 6), y suma el ruido de la decisión 4.
  - estandarizar(): (x − media del grupo)/desviación del grupo, con la media y la
    desviación de pandas (ddof=1) de las filas de entrenamiento; NaN si el grupo
    no tiene filas de entrenamiento, si tiene una sola o si su desviación es 0.
  - etiquetas_conglomerado(): las etiquetas del k-means que M3 limpio ajusta en
    el pliegue (ganador_m3.variables_m3_en_pliegue con devolver_ajuste).
- La red mejorada (pregunta 2): entrenar_y_puntuar() es el de la Fase 4c
  (fase4c.entrenar_y_puntuar), línea por línea, salvo la elección de los
  negativos: con negativos="bloques", los negativos del pliegue de entrenamiento
  se reparten al azar, con la semilla externa, en bloques de
  NEGATIVOS_POR_POSITIVO por cada positivo, y cada época usa un bloque distinto
  (bloques_de_negativos). Con negativos="4c", los sorteos de la Fase 4c: es el
  control de que lo demás no cambió.
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import torch
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4b  # noqa: E402
import fase4c  # noqa: E402
import ganador_m3  # noqa: E402
from prueba_tiempo_red_imagen import a_tensor, decodificar, red, sincronizar  # noqa: E402

EPOCAS = 15
RUIDO = 0.1
ALFA = 0.05
N_PREGUNTAS = 3
ZONA_EDAD = ["tbp_lv_location", "age_approx"]  # celda 17, sin "attribution"
COLUMNAS_C4 = list(fase4b.COLUMNAS_IMAGEN)  # la puntuación y su razón, con los nombres de C2 y C4
Z_ZONA_EDAD = "red_z_zona_edad"
COLUMNAS_C5 = COLUMNAS_C4 + [Z_ZONA_EDAD] + [f"{c}__cluster" for c in COLUMNAS_C4 + [Z_ZONA_EDAD]]


# ---- la comparación --------------------------------------------------------------------------

def valor_p(diffs, n_splits):
    """Valor p bilateral de la t corregida de Nadeau y Bengio: la varianza de las
    diferencias por (1/n + 1/(n_splits − 1)) y n − 1 grados de libertad, como
    fase4b_comparar.nadeau_bengio."""
    d = np.asarray(diffs, dtype=np.float64)
    n = len(d)
    ee = float(np.sqrt(np.var(d, ddof=1) * (1.0 / n + 1.0 / (n_splits - 1))))
    media = float(np.mean(d))
    if ee == 0:
        return 1.0 if media == 0 else 0.0
    return float(2 * stats.t.sf(abs(media / ee), df=n - 1))


def valor_p_ingenuo(diffs):
    """El de la t sin corregir, que trata las diferencias como independientes. Solo
    para el caso que debe fallar del control negativo."""
    d = np.asarray(diffs, dtype=np.float64)
    n = len(d)
    t = float(np.mean(d)) / float(np.sqrt(np.var(d, ddof=1) / n))
    return float(2 * stats.t.sf(abs(t), df=n - 1))


def holm(preguntas, alfa=ALFA):
    """Holm sobre [{"pregunta", "valor_p", "media"}]: ordenados de menor a mayor
    valor p, el i-ésimo (desde 0) se compara con alfa/(m − i), y se acepta solo si
    se aceptaron todos los anteriores. a_favor: aceptada y media > 0. Devuelve las
    preguntas en su orden de entrada, con su orden, su umbral y su decisión."""
    m = len(preguntas)
    orden = sorted(range(m), key=lambda i: preguntas[i]["valor_p"])
    salida = [dict(q) for q in preguntas]
    sigue = True
    for rango, i in enumerate(orden):
        umbral = alfa / (m - rango)
        pasa = sigue and preguntas[i]["valor_p"] <= umbral
        sigue = pasa
        salida[i].update({"orden_holm": rango + 1, "umbral_holm": umbral, "aceptada_por_holm": bool(pasa),
                          "media_positiva": bool(preguntas[i]["media"] > 0),
                          "a_favor": bool(pasa and preguntas[i]["media"] > 0)})
    return salida


# ---- C5 y C6 ---------------------------------------------------------------------------------

def estandarizar(v_tr, claves_tr, v_otros, claves_otros):
    """Celdas 17 y 19 del ganador, ajustadas con el entrenamiento: para cada lado,
    (x − media)/desviación de su grupo, con la media y la desviación de pandas
    (ddof=1) de v_tr agrupado por claves_tr. claves_*: {nombre: array}. NaN si el
    grupo no está en el entrenamiento, si tiene una sola fila (desviación NaN) o si
    su desviación es 0. Devuelve (para v_tr, para v_otros)."""
    nombres = list(claves_tr)
    d = pd.DataFrame({k: np.asarray(claves_tr[k]) for k in nombres})
    d["_v"] = np.asarray(v_tr, dtype=np.float64)
    agg = d.groupby(nombres, sort=False)["_v"].agg(["mean", "std"]).reset_index()

    def aplicar(v, claves):
        izq = pd.DataFrame({k: np.asarray(claves[k]) for k in nombres})
        m = izq.merge(agg, how="left", on=nombres)
        if len(m) != len(izq):
            raise SystemExit("ERROR: la estandarización duplicó filas al unir por grupo.")
        sd = m["std"].to_numpy(np.float64)
        with np.errstate(divide="ignore", invalid="ignore"):
            z = (np.asarray(v, dtype=np.float64) - m["mean"].to_numpy(np.float64)) / sd
        z[~(sd > 0)] = np.nan
        return z
    return aplicar(v_tr, claves_tr), aplicar(v_otros, claves_otros)


def etiquetas_conglomerado(ajuste, x_tr, x_va):
    """Las etiquetas del k-means de M3 limpio en el pliegue: las del ajuste para el
    entrenamiento y su predicción para la validación, sobre las mismas variables
    estandarizadas del LOF."""
    top = ajuste["listas"]["top_lof_features"]
    km, escala = ajuste["kmeans"], ajuste["escala"]
    return km.labels_.copy(), km.predict(escala.transform(x_va[top].to_numpy(dtype=float)))


def claves_zona_edad(df_sin_etiqueta, filas, x):
    """tbp_lv_location del CSV y la edad imputada de M3 limpio (x, en el orden de
    filas)."""
    return {"tbp_lv_location": df_sin_etiqueta["tbp_lv_location"].to_numpy()[filas],
            "age_approx": x["age_approx"].to_numpy(np.float64)}


def variables_c5(p, tr, va, grupos, claves_tr, claves_va, et_tr, et_va, semilla, ruido=True):
    """Las seis variables de la red de C5 en un pliegue: la puntuación y su razón a
    la media del paciente (fase4c.variables_red, como C4), la puntuación
    estandarizada por zona y edad (celda 17 sin el hospital) y las tres
    estandarizadas por conglomerado (celda 19). Con ruido, en las filas de
    entrenamiento se suma a la estandarizada por zona y edad un ruido normal de
    media 0 y desviación RUIDO, con default_rng(semilla), en el orden de tr; las
    estandarizadas por conglomerado salen de la variable sin ruido. Devuelve
    {"tr": {columna: array}, "va": {...}, "sin_ruido_tr": array}."""
    a4 = fase4c.variables_red(p, tr, va, grupos)
    a = {"tr": {COLUMNAS_C4[0]: a4["tr"]["puntuacion"], COLUMNAS_C4[1]: a4["tr"]["razon"]},
         "va": {COLUMNAS_C4[0]: a4["va"]["puntuacion"], COLUMNAS_C4[1]: a4["va"]["razon"]}}
    a["tr"][Z_ZONA_EDAD], a["va"][Z_ZONA_EDAD] = estandarizar(a4["tr"]["puntuacion"], claves_tr,
                                                              a4["va"]["puntuacion"], claves_va)
    for c in COLUMNAS_C4 + [Z_ZONA_EDAD]:
        a["tr"][f"{c}__cluster"], a["va"][f"{c}__cluster"] = estandarizar(
            a["tr"][c], {"conglomerado": et_tr}, a["va"][c], {"conglomerado": et_va})
    a["sin_ruido_tr"] = a["tr"][Z_ZONA_EDAD].copy()
    if ruido:
        a["tr"][Z_ZONA_EDAD] = a["sin_ruido_tr"] + np.random.default_rng(semilla).normal(0.0, RUIDO, size=len(tr))
    return a


def con_red(x_tr, x_va, a, columnas=COLUMNAS_C5):
    """Las variables de M3 limpio de un pliegue más las de la red, al final y en el
    orden de columnas."""
    salida = []
    for x, lado in ((x_tr, "tr"), (x_va, "va")):
        x = x.copy()
        for c in columnas:
            if len(a[lado][c]) != len(x):
                raise ValueError(f"La variable {c} no tiene el largo de las de M3 limpio.")
            x[c] = np.asarray(a[lado][c], dtype=float)
        salida.append(x)
    return tuple(salida)


def comprobar_alineacion(x_tr, xc_tr, a, semilla, y_tr, grupos_tr, columnas=COLUMNAS_C5):
    """La de C2 y C4 (fase4b_comparar.comprobar_alineacion), extendida a las seis
    variables: antes del remuestreo, cada columna es la calculada y las de M3
    limpio no cambian; la razón es la puntuación entre la media del paciente; y
    después del remuestreo, cada fila remuestreada lleva las de su fila de origen."""
    iguales = (lambda u, v: np.array_equal(np.asarray(u, dtype=float), np.asarray(v, dtype=float), equal_nan=True))
    antes = (all(iguales(xc_tr[c].to_numpy(), a["tr"][c]) for c in columnas)
             and list(xc_tr.columns[:-len(columnas)]) == list(x_tr.columns))
    q = pd.Series(xc_tr[columnas[0]].to_numpy())
    razon = np.allclose(xc_tr[columnas[1]].to_numpy(), (q / q.groupby(grupos_tr).transform("mean")).to_numpy(),
                        rtol=0, atol=1e-12)
    interna = ganador_m3.StratifiedGroupKFold(n_splits=ganador_m3.PLIEGUES_INTERNOS, shuffle=True,
                                              random_state=semilla)
    itr, _ = next(interna.split(xc_tr, y_tr, groups=grupos_tr))
    marcada = xc_tr.iloc[itr].copy()
    marcada["_fila"] = np.arange(len(marcada))
    xr, _ = ganador_m3.remuestrear(marcada, y_tr[itr], semilla)
    origen = marcada.iloc[xr["_fila"].to_numpy()]
    despues = all(iguales(xr[c].to_numpy(), origen[c].to_numpy()) for c in columnas)
    return {"antes": bool(antes), "razon": bool(razon), "despues": bool(despues), "filas_remuestreadas": int(len(xr))}


def comprobar_ruido(a, semilla, z_va_sin_ruido):
    """Que el ruido vaya solo al entrenamiento: en validación, la estandarizada por
    zona y edad es z_va_sin_ruido, la que quien llama calcula aparte con
    estandarizar(); en entrenamiento, la diferencia con la sin ruido es
    exactamente el sorteo de default_rng(semilla). Devuelve también la desviación
    del ruido sumado."""
    esperado = np.random.default_rng(semilla).normal(0.0, RUIDO, size=len(a["sin_ruido_tr"]))
    sumado = a["tr"][Z_ZONA_EDAD] - a["sin_ruido_tr"]
    finito = np.isfinite(a["sin_ruido_tr"])
    return {"validacion_sin_ruido": bool(np.array_equal(a["va"][Z_ZONA_EDAD], z_va_sin_ruido, equal_nan=True)),
            "entrenamiento_con_el_sorteo_de_la_semilla": bool(np.allclose(sumado[finito], esperado[finito], rtol=0,
                                                                          atol=1e-12)),
            "desviacion_del_ruido": float(np.std(sumado[finito])), "filas_con_ruido": int(finito.sum()),
            "filas_en_nan": int((~finito).sum())}


# ---- la red mejorada -------------------------------------------------------------------------

def bloques_de_negativos(neg, n_por_bloque, epocas, rng):
    """Los negativos de cada época: neg barajado una vez con rng y cortado en
    bloques de n_por_bloque; la época e usa el bloque e, y solo repite cuando ya
    usó todos. Los que no llenan un bloque no se usan. Devuelve (lista de arrays,
    número de bloques)."""
    n_bloques = len(neg) // n_por_bloque
    if n_bloques == 0:
        raise SystemExit(f"ERROR: {len(neg)} negativos no llenan un bloque de {n_por_bloque}.")
    bloques = rng.permutation(neg)[: n_bloques * n_por_bloque].reshape(n_bloques, n_por_bloque)
    return [bloques[e % n_bloques] for e in range(epocas)], n_bloques


def repetidos_entre_epocas(por_epoca):
    """Cuántos negativos aparecen en más de una época."""
    valores, veces = np.unique(np.concatenate(por_epoca), return_counts=True)
    return int((veces > 1).sum())


def entrenar_y_puntuar(f, isic, etiquetas, filas_ent, filas_pred, semilla, dispositivo, epocas=EPOCAS,
                       negativos="bloques"):
    """fase4c.entrenar_y_puntuar con la elección de negativos de la Fase 4d.
    negativos="bloques": los de bloques_de_negativos con default_rng(semilla);
    "4c": un sorteo nuevo en cada época con ese mismo generador, como la Fase 4c.
    Devuelve (logit en float32 para filas_pred, en ese orden; registro)."""
    if negativos not in ("bloques", "4c"):
        raise ValueError(f"negativos: {negativos}")
    t_inicio = time.perf_counter()
    filas_ent, filas_pred = np.asarray(filas_ent), np.asarray(filas_pred)
    if np.intersect1d(filas_ent, filas_pred).size:
        raise SystemExit("ERROR: la red puntuaría filas con las que se entrena.")
    y_ent = etiquetas[filas_ent]
    pos, neg = filas_ent[y_ent == 1], filas_ent[y_ent == 0]
    n_neg = fase4c.NEGATIVOS_POR_POSITIVO * len(pos)
    if len(pos) == 0 or n_neg > len(neg):
        raise SystemExit(f"ERROR: {len(pos)} positivos y {len(neg)} negativos no alcanzan para "
                         f"{fase4c.NEGATIVOS_POR_POSITIVO} negativos por positivo.")
    rng = np.random.default_rng(semilla)  # los negativos
    g = torch.Generator().manual_seed(semilla)  # el orden de los lotes y los volteos
    torch.manual_seed(semilla)  # la capa de salida nueva
    modelo, pesos = red(dispositivo)
    opt = torch.optim.AdamW(modelo.parameters(), lr=fase4c.TASA)
    perdida = torch.nn.BCEWithLogitsLoss()
    if negativos == "bloques":
        por_epoca, n_bloques = bloques_de_negativos(neg, n_neg, epocas, rng)
    else:
        por_epoca, n_bloques = None, None

    s_dec, s_epoca, usados = [], [], []
    modelo.train()
    for e in range(epocas):
        elegidos = por_epoca[e] if negativos == "bloques" else rng.choice(neg, size=n_neg, replace=False)
        usados.append(elegidos)
        filas = np.sort(np.concatenate([pos, elegidos]))
        t0 = time.perf_counter()
        x = decodificar(f, isic[filas], fase4c.LADO)
        s_dec.append(round(time.perf_counter() - t0, 3))
        yt = torch.from_numpy(etiquetas[filas].astype(np.float32))
        orden = torch.randperm(len(filas), generator=g).numpy()
        t0 = time.perf_counter()
        for i in range(0, len(orden), fase4c.LOTE):
            b = orden[i: i + fase4c.LOTE]
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
        for i in range(0, len(filas_pred), fase4c.BLOQUE):
            t0 = time.perf_counter()
            bloque = decodificar(f, isic[filas_pred[i: i + fase4c.BLOQUE]], fase4c.LADO)
            t_dec_p += time.perf_counter() - t0
            t0 = time.perf_counter()
            salidas = [modelo(a_tensor(bloque[j: j + fase4c.LOTE_PREDICCION], dispositivo)).squeeze(1).float().cpu()
                       for j in range(0, len(bloque), fase4c.LOTE_PREDICCION)]
            sincronizar()
            logit[i: i + len(bloque)] = torch.cat(salidas).numpy()
            t_mod_p += time.perf_counter() - t0
    del modelo, opt
    torch.mps.empty_cache()
    registro = {
        "semilla": int(semilla), "positivos": int(len(pos)), "negativos_por_epoca": int(n_neg),
        "imagenes_por_epoca": int(len(pos) + n_neg), "epocas": int(epocas), "filas_puntuadas": int(len(filas_pred)),
        "negativos": negativos, "bloques_disponibles": n_bloques,
        "negativos_del_pliegue": int(len(neg)),
        "negativos_en_mas_de_una_epoca": repetidos_entre_epocas(usados),
        "negativos_distintos_vistos": int(np.unique(np.concatenate(usados)).size),
        "segundos_decodificacion_por_epoca": s_dec, "segundos_por_epoca": s_epoca,
        "segundos_prediccion_modelo": round(t_mod_p, 3), "segundos_prediccion_decodificacion": round(t_dec_p, 3),
        "segundos_total": round(time.perf_counter() - t_inicio, 3), "sha256_pesos": pesos["sha256"],
    }
    return logit, registro

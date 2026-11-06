#!/usr/bin/env python3
"""
fase5c_entrenar.py — la Fase 5c de PLAN.md: entrena con todos los datos de
entrenamiento (1.042 pacientes) los cuatro modelos de sus envíos, {M3 limpio,
C7} promediados × {sin hospital, con hospital}. No envía nada y no calcula
ninguna métrica.

- «Promediado»: un CatBoost por cada pliegue de construir_folds con las semillas
  1 a 9, un StratifiedGroupKFold de 5 agrupado por paciente, como en las celdas 22
  y 25 del ganador. Cada uno se ajusta sobre su pliegue de entrenamiento con
  ganador_m3.ajustar_m3, PARAMETROS_LIMPIO y la semilla del pliegue, y la
  puntuación es la media de las 45 probabilidades.
- Las variables de M3 limpio se calculan una vez, con todas las filas de
  entrenamiento (ganador_m3.variables_m3_en_pliegue), como en la Fase 5b. «Con
  hospital», sin excluir attribution, que entra en el one-hot (celdas 3 y 8).
- C7: las variables de M3 limpio más la puntuación de la red de la 4e y su razón
  a la media del paciente (fase4c.variables_red, fase4b.con_imagen), con las
  puntuaciones fuera de pliegue de la Fase 5b y, en el control, la media de las
  cinco redes que guardó la 5b. «Con hospital», además, la puntuación
  estandarizada por hospital, zona y edad (celda 17, con fase4d.estandarizar).

Antes de entrenar se comprueba que, sin hospital, las variables son las de la 5b:
los CatBoost de M3 limpio y de C7 de la 5b, sobre las variables del control
calculadas aquí, dan las puntuaciones que guardó la 5b, sin diferencia.

Conjunto de control: el de la Fase 5b (fase5b_entrenar.elegir_control). Sus filas
se añaden al final como filas nuevas, sin etiqueta, y cada uno de los 45 modelos
de cada envío las puntúa: son las referencias que la inferencia portátil
(inferencia_5c.py) tiene que reproducir en el Mac y en Kaggle.

Cada CatBoost se guarda en data/fase5c/modelos/ con su registro, y la corrida se
reanuda con los del mismo código, las mismas variables y los mismos pliegues.
Todo va a data/fase5c/, que no se versiona; el registro, a --out (.json y .md).

Uso (con caffeinate, en segundo plano):
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_entrenar.py \\
        --out outputs/fase5c-entrenamiento
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import fase4d  # noqa: E402
import fase5  # noqa: E402
import fase5b_entrenar as f5b  # noqa: E402
import ganador_m3  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import construir_folds  # noqa: E402

RAIZ = fase5.RAIZ
G, Y = "patient_id", "target"
SEMILLAS = list(range(1, 10))  # celda 22: for random_seed in range(1, n_rounds), con n_rounds=10
N_SPLITS = 5
HOSPITAL = "attribution"
CLAVES_CELDA_17 = [HOSPITAL, "tbp_lv_location", "age_approx"]  # celda 17
Z_CELDA_17 = "red_z_hospital_zona_edad"
COLUMNAS_C7_HOSPITAL = list(fase4b.COLUMNAS_IMAGEN) + [Z_CELDA_17]
MODOS = ("M3limpioProm", "M3limpioPromHosp", "C7Prom", "C7PromHosp")  # el orden de envío (PLAN.md, Fase 5c)
DIR = os.path.join(RAIZ, "data", "fase5c")
DIR_5B = os.path.join(RAIZ, "data", "fase5b")
REGISTRO_5B = os.path.join(RAIZ, "outputs", "fase5b-entrenamiento.json")
CODIGO = ["fase5c_entrenar.py", "fase5b_entrenar.py", "fase4_comparar.py", "fase4b.py", "fase4b_comparar.py",
          "fase4c.py", "fase4d.py", "fase5.py", "ganador_m3.py", "evaluar_repetido.py", "train_and_evaluate.py"]


def sha(ruta):
    return fase5.sha256(ruta)


def sha_matriz(x):
    """El SHA-256 de las columnas y los valores de un DataFrame, en float64."""
    h = hashlib.sha256("\n".join(map(str, x.columns)).encode())
    h.update(np.ascontiguousarray(x.astype(float).to_numpy()).tobytes())
    return h.hexdigest()


def nombre_modelo(modo, semilla, pliegue):
    return f"cbm-{modo}-s{semilla}-p{pliegue}.cbm"


# ---- lo que viene de la Fase 5b -----------------------------------------------------------

def leer_5b(df, ids_control):
    """Las puntuaciones fuera de pliegue de la red, en el orden de df, y el control de la
    Fase 5b, comprobados contra el registro de su entrenamiento."""
    with open(REGISTRO_5B, encoding="utf-8") as f:
        archivos = json.load(f)["archivos"]
    usados = ["puntuaciones-fuera-de-pliegue.csv.gz", "control.npz", "m3limpio.cbm", "c7.cbm",
              *[f"redes/pliegue-{k}.pt" for k in range(N_SPLITS)]]
    for a in usados:
        clave = f"data/fase5b/{a}"
        if sha(os.path.join(DIR_5B, a)) != archivos[clave]["sha256"]:
            raise SystemExit(f"ERROR: {clave} no es el del entrenamiento de la Fase 5b.")
    oof = pd.read_csv(os.path.join(DIR_5B, "puntuaciones-fuera-de-pliegue.csv.gz"))
    if not np.array_equal(oof["isic_id"].to_numpy(), df["isic_id"].to_numpy()) or (oof["pliegue"] < 0).any():
        raise SystemExit("ERROR: las puntuaciones fuera de pliegue no están en el orden de los datos o les falta pliegue.")
    control = dict(np.load(os.path.join(DIR_5B, "control.npz")))
    if list(control["isic_id"]) != list(ids_control):
        raise SystemExit("ERROR: el control no es el de la Fase 5b.")
    return oof["puntuacion"].to_numpy(dtype=np.float64), control, {a: archivos[f"data/fase5b/{a}"]["sha256"]
                                                                  for a in usados}


def claves_celda_17(ext, filas, x):
    """attribution y tbp_lv_location del CSV y la edad imputada de M3 limpio (x, en el
    orden de filas), como fase4d.claves_zona_edad con el hospital."""
    return {HOSPITAL: ext[HOSPITAL].to_numpy()[filas], "tbp_lv_location": ext["tbp_lv_location"].to_numpy()[filas],
            "age_approx": x["age_approx"].to_numpy(np.float64)}


def tabla_celda_17(p_tr, claves_tr):
    """La media y la desviación (ddof=1) de cada grupo, en el formato que lee inferencia_5c.py."""
    d = pd.DataFrame({k: np.asarray(v) for k, v in claves_tr.items()})
    d["_v"] = np.asarray(p_tr, dtype=np.float64)
    agg = d.groupby(CLAVES_CELDA_17, sort=False)["_v"].agg(["mean", "std", "size"]).reset_index()
    return {"claves": CLAVES_CELDA_17,
            "filas": [[str(r[HOSPITAL]), str(r["tbp_lv_location"]), float(r["age_approx"]), float(r["mean"]),
                       float(r["std"]), int(r["size"])] for _, r in agg.iterrows()],
            "columnas_de_cada_fila": [*CLAVES_CELDA_17, "media", "desviacion", "lesiones"]}


# ---- los 45 modelos -----------------------------------------------------------------------

def promediado(modo, x, x_c, y, g, cats, pliegues, meta, codigo):
    """Los 45 CatBoost de un envío y sus puntuaciones del control (45 × m), en el orden de
    SEMILLAS y de los pliegues. Cada uno se guarda en DIR/modelos con su registro, y se
    lee si ya está con el mismo código, las mismas variables y los mismos pliegues."""
    from catboost import CatBoostClassifier
    d = os.path.join(DIR, "modelos")
    os.makedirs(d, exist_ok=True)
    puntuaciones, registros = [], []
    for s in SEMILLAS:
        for k, (ftr, _) in enumerate(pliegues[s]["folds"]):
            ruta = os.path.join(d, nombre_modelo(modo, s, k))
            ruta_json = ruta[:-4] + ".json"
            esperado = {**meta, "semilla": s, "pliegue": k, "sha256_pliegues": pliegues[s]["sha256"],
                        "sha256_del_codigo": codigo}
            if os.path.exists(ruta) and os.path.exists(ruta_json):
                with open(ruta_json, encoding="utf-8") as f:
                    reg = json.load(f)
                if {c: reg.get(c) for c in esperado} != esperado or reg["sha256_cbm"] != sha(ruta):
                    raise SystemExit(f"ERROR: {rel(ruta)} es de otro código, otras variables u otros pliegues; "
                                     "bórrelo para rehacerlo.")
                modelo = CatBoostClassifier()
                modelo.load_model(ruta)
                leido = True
            else:
                t0 = time.perf_counter()
                modelo = ganador_m3.ajustar_m3(x.iloc[ftr], y[ftr], g[ftr], cats, s,
                                               parametros=ganador_m3.PARAMETROS_LIMPIO)
                modelo.save_model(ruta)
                reg = {**esperado, "arboles": int(modelo.tree_count_),
                       "iteraciones_corridas": len(modelo.get_evals_result()["validation"]["AUC"]),
                       "lesiones_del_pliegue_de_entrenamiento": int(len(ftr)),
                       "segundos": round(time.perf_counter() - t0, 1), "sha256_cbm": sha(ruta), "fecha": f5b.ahora()}
                with open(ruta_json, "w", encoding="utf-8") as f:
                    json.dump(reg, f, ensure_ascii=False, indent=2)
                leido = False
            puntuaciones.append(modelo.predict_proba(x_c)[:, 1])
            registros.append({c: reg[c] for c in ("semilla", "pliegue", "arboles", "iteraciones_corridas",
                                                  "lesiones_del_pliegue_de_entrenamiento", "segundos", "sha256_cbm")})
            print(f"{modo} s{s} p{k}: {reg['arboles']} árboles, "
                  f"{'leído' if leido else str(reg['segundos']) + ' s'}", flush=True)
    return np.stack(puntuaciones), registros


def rel(ruta):
    return os.path.relpath(ruta, RAIZ)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    import catboost
    import sklearn
    r = fase5.rutas(RAIZ)
    for previo in ("fase5b-envio-m3limpio", "fase5b-envio-c7"):
        if not os.path.exists(os.path.join(RAIZ, "outputs", f"{previo}.json")):
            raise SystemExit(f"ERROR: la Fase 5c va después de la 5b, y falta outputs/{previo}.json.")
    bajo_caffeinate = fase4c.caffeinate()
    if not bajo_caffeinate["activo"]:
        raise SystemExit("ERROR: el programa corre bajo caffeinate (caffeinate -i …).")
    os.makedirs(DIR, exist_ok=True)
    t_total, segundos = time.perf_counter(), {}

    t0 = time.perf_counter()
    df, datos = f5b.cargar_todo(r)
    excluidas = cargar_columnas_excluidas(r["fugas"])
    if HOSPITAL not in excluidas:
        raise SystemExit(f"ERROR: {HOSPITAL} no está entre las columnas que excluye auditoria-de-fugas.")
    excluidas_hospital = [c for c in excluidas if c != HOSPITAL]
    control = f5b.elegir_control(df)
    filas_c = np.flatnonzero(df[G].astype(str).isin(control).to_numpy())
    n, m = len(df), len(filas_c)
    ext = pd.concat([df, df.iloc[filas_c].assign(**{Y: np.nan})], ignore_index=True)
    tr, va_c = np.arange(n), np.arange(n, n + m)
    y, g = df[Y].to_numpy().astype(np.int64), df[G].astype(str).to_numpy()
    g_c = g[filas_c]
    ids_c = ext["isic_id"].to_numpy()[va_c]
    p_oof, control_5b, sha_5b = leer_5b(df, ids_c)
    p_c = control_5b["p_red_media"].astype(np.float64)
    segundos["carga"] = round(time.perf_counter() - t0, 1)
    print(f"Datos: {datos['pacientes']} pacientes, {n} lesiones; control: {len(control)} pacientes, {m} lesiones",
          flush=True)

    t0 = time.perf_counter()
    sin_etiqueta = ext.drop(columns=[Y])
    x_tr, x_c, cats, inv, aj = ganador_m3.variables_m3_en_pliegue(sin_etiqueta, tr, va_c, excluidas, G,
                                                                  devolver_ajuste=True)
    xh_tr, xh_c, cats_h, inv_h, aj_h = ganador_m3.variables_m3_en_pliegue(sin_etiqueta, tr, va_c, excluidas_hospital,
                                                                          G, devolver_ajuste=True)
    one_hot_hospital = {c: n_ for c, n_ in zip(aj_h["nombres_one_hot"],
                                                [f"{cat}={v}" for cat, cs in zip(aj_h["categoricas_brutas"],
                                                                                  aj_h["one_hot"].categories_)
                                                 for v in cs])
                        if n_.startswith(f"{HOSPITAL}=")}
    if HOSPITAL in aj["categoricas_brutas"] or HOSPITAL not in aj_h["categoricas_brutas"] or not one_hot_hospital:
        raise SystemExit("ERROR: el hospital no entra solo en las variables «con hospital».")
    a7 = fase4c.variables_red(np.concatenate([p_oof, p_c]), tr, va_c, np.concatenate([g, g_c]))
    xc_tr, xc_c = fase4b.con_imagen(x_tr, x_c, a7)
    xch_tr, xch_c = fase4b.con_imagen(xh_tr, xh_c, a7)
    claves_tr, claves_c = claves_celda_17(ext, tr, xh_tr), claves_celda_17(ext, va_c, xh_c)
    z_tr, z_c = fase4d.estandarizar(p_oof, claves_tr, p_c, claves_c)
    xch_tr[Z_CELDA_17], xch_c[Z_CELDA_17] = z_tr, z_c
    tabla_17 = tabla_celda_17(p_oof, claves_tr)
    a7h = {"tr": {fase4b.COLUMNAS_IMAGEN[0]: a7["tr"]["puntuacion"], fase4b.COLUMNAS_IMAGEN[1]: a7["tr"]["razon"],
                  Z_CELDA_17: z_tr}}
    alineacion = {"C7Prom": f4b.comprobar_alineacion(x_tr, xc_tr, a7, SEMILLAS[0], y, g),
                  "C7PromHosp": fase4d.comprobar_alineacion(xh_tr, xch_tr, a7h, SEMILLAS[0], y, g,
                                                            columnas=COLUMNAS_C7_HOSPITAL)}
    if not all(v[k] for v in alineacion.values() for k in ("antes", "razon", "despues")):
        raise SystemExit(f"ERROR: alineación de las variables de imagen: {alineacion}")
    segundos["variables"] = round(time.perf_counter() - t0, 1)

    # Sin hospital, las variables son las de la Fase 5b: sus dos CatBoost dan, sobre las del control calculadas
    # aquí, las puntuaciones que guardó.
    from catboost import CatBoostClassifier

    def cbm_5b(nombre, x):
        modelo = CatBoostClassifier()
        modelo.load_model(os.path.join(DIR_5B, nombre))
        return modelo.predict_proba(x)[:, 1]
    iguales_5b = {
        "variables_de_m3_limpio": bool(list(x_c.columns) == list(control_5b["x_m3_columnas"])
                                       and np.array_equal(x_c.astype(float).to_numpy(), control_5b["x_m3"],
                                                          equal_nan=True)),
        "m3limpio_5b_sobre_estas_variables": float(np.max(np.abs(cbm_5b("m3limpio.cbm", x_c) - control_5b["m3limpio"]))),
        "c7_5b_sobre_estas_variables": float(np.max(np.abs(cbm_5b("c7.cbm", xc_c) - control_5b["c7"]))),
    }
    if not (iguales_5b["variables_de_m3_limpio"] and iguales_5b["m3limpio_5b_sobre_estas_variables"] == 0
            and iguales_5b["c7_5b_sobre_estas_variables"] == 0):
        raise SystemExit(f"ERROR: sin hospital, las variables no son las de la Fase 5b: {iguales_5b}")
    print(f"Variables: M3 limpio {x_tr.shape[1]}, con hospital {xh_tr.shape[1]}; iguales a las de la 5b: {iguales_5b}",
          flush=True)

    pliegues = {}
    for s in SEMILLAS:
        folds = construir_folds(df, G, Y, N_SPLITS, s)
        asignacion = np.full(n, -1)
        for k, (_, fva) in enumerate(folds):
            asignacion[fva] = k
        if (asignacion < 0).any() or any(y[fva].sum() == 0 for _, fva in folds) \
                or any(set(g[ftr]) & set(g[fva]) for ftr, fva in folds):
            raise SystemExit(f"ERROR: los pliegues de la semilla {s} no reparten a todos, les faltan positivos o "
                             "comparten pacientes.")
        pliegues[s] = {"folds": folds, "sha256": f4.huella_folds(folds, n)}

    variantes = {"M3limpioProm": (x_tr, x_c, cats), "M3limpioPromHosp": (xh_tr, xh_c, cats_h),
                 "C7Prom": (xc_tr, xc_c, cats), "C7PromHosp": (xch_tr, xch_c, cats_h)}
    codigo = f5b.huella(CODIGO)
    puntuaciones, info = {}, {}
    for modo in MODOS:
        x, xc, cs = variantes[modo]
        t0 = time.perf_counter()
        meta = {"modo": modo, "n_variables": int(x.shape[1]), "sha256_variables": sha_matriz(x)}
        puntuaciones[modo], registros = promediado(modo, x, xc, y, g, cs, pliegues, meta, codigo)
        segundos[modo] = round(time.perf_counter() - t0, 1)
        info[modo] = {"n_variables": int(x.shape[1]), "categoricas": len(cs), "sha256_variables": meta["sha256_variables"],
                      "modelos": registros,
                      "arboles": {"mediana": float(np.median([v["arboles"] for v in registros])),
                                  "minimo": min(v["arboles"] for v in registros),
                                  "maximo": max(v["arboles"] for v in registros)},
                      "puntuacion": "la media de las probabilidades de los 45 modelos"}
        print(f"{modo}: 45 modelos ({segundos[modo]} s)", flush=True)

    aj_json, aj_npz = f5b.ajuste_m3_en_numeros(aj, cats)
    ajh_json, ajh_npz = f5b.ajuste_m3_en_numeros(aj_h, cats_h)
    for nombre, (j, z) in {"m3limpio-ajuste": (aj_json, aj_npz), "m3limpio-hospital-ajuste": (ajh_json, ajh_npz)}.items():
        with open(os.path.join(DIR, f"{nombre}.json"), "w", encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False)
        np.savez(os.path.join(DIR, f"{nombre}.npz"), **z)
    with open(os.path.join(DIR, "celda17.json"), "w", encoding="utf-8") as f:
        json.dump(tabla_17, f, ensure_ascii=False)
    np.savez(os.path.join(DIR, "control.npz"), isic_id=np.asarray(ids_c, dtype=str), patient_id=np.asarray(g_c, dtype=str),
             **{modo: puntuaciones[modo].mean(axis=0) for modo in MODOS},
             **{f"{modo}_por_modelo": puntuaciones[modo] for modo in MODOS},
             x_m3=x_c.astype(float).to_numpy(), x_m3_columnas=np.asarray(list(x_c.columns), dtype=str),
             x_m3_hospital=xh_c.astype(float).to_numpy(),
             x_m3_hospital_columnas=np.asarray(list(xh_c.columns), dtype=str),
             z_celda17=z_c, p_red_media=p_c, logit_pliegues=control_5b["logit_pliegues"],
             etiquetas_kmeans_entrenamiento=aj["kmeans"].labels_,
             etiquetas_kmeans_entrenamiento_hospital=aj_h["kmeans"].labels_)

    archivos = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(DIR) for f in fs)
    resultado = {
        "que_es": ("los cuatro modelos de los envíos de la Fase 5c, {M3 limpio, C7} promediados × {sin hospital, con "
                   "hospital}, entrenados con todos los datos de entrenamiento (PLAN.md, Fase 5c); no envía nada y no "
                   "calcula ninguna métrica"),
        "datos": datos,
        "control": {"pacientes": control, "lesiones": int(m),
                    "sha256_isic_id": hashlib.sha256("\n".join(ids_c).encode()).hexdigest(),
                    "que_es": "el de la Fase 5b: filas de entrenamiento puntuadas como nuevas, referencias para "
                              "inferencia_5c.py"},
        "de_la_fase_5b": {"archivos_sha256": sha_5b, "iguales_sin_hospital": iguales_5b},
        "pliegues": {"semillas": SEMILLAS, "n_splits": N_SPLITS,
                     "como": "construir_folds: StratifiedGroupKFold(5, shuffle=True, random_state=semilla) sobre las "
                             "filas de train-metadata.csv, con la etiqueta y agrupado por paciente",
                     "sha256_por_semilla": {str(s): pliegues[s]["sha256"] for s in SEMILLAS}},
        "hospital": {"columna": HOSPITAL, "one_hot": one_hot_hospital,
                     "excluidas_sin_hospital": excluidas, "excluidas_con_hospital": excluidas_hospital,
                     "celda_17": {"variable": Z_CELDA_17, "claves": CLAVES_CELDA_17, "grupos": len(tabla_17["filas"]),
                                  "nan_en_el_entrenamiento": int(np.isnan(z_tr).sum()),
                                  "nan_en_el_control": int(np.isnan(z_c).sum()),
                                  "que_es": "la puntuación fuera de pliegue de la red de la 4e menos la media de su "
                                            "grupo, dividida por su desviación (ddof=1), con las del entrenamiento; "
                                            "NaN si el grupo no está, tiene una lesión o su desviación es 0"}},
        "alineacion_de_las_variables_de_imagen": alineacion,
        "modelos": info,
        "archivos": {rel(a): {"bytes": os.path.getsize(a), "sha256": sha(a)} for a in archivos},
        "sha256_del_codigo": codigo,
        "comando": {"interprete": rel(sys.executable), "argumentos": sys.argv, "caffeinate": bajo_caffeinate},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "catboost": catboost.__version__},
        "fecha": f5b.ahora(),
        "segundos": {**segundos, "total": round(time.perf_counter() - t_total, 1)},
        "nota": "No envía nada y no calcula ninguna métrica.",
    }
    out = args.out if os.path.isabs(args.out) else os.path.join(RAIZ, args.out)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    lineas = ["# Fase 5c — entrenamiento con todos los datos",
              f"Datos: {datos['pacientes']} pacientes, {datos['filas']} lesiones, {datos['lesiones_malignas']} malignas. "
              f"Control: {len(control)} pacientes, {m} lesiones, puntuados como filas nuevas.",
              f"Cuatro envíos de 45 CatBoost cada uno (semillas 1 a 9 × 5 pliegues): "
              + "; ".join(f"{k} {v['n_variables']} variables, mediana de {v['arboles']['mediana']:g} árboles"
                          for k, v in info.items()) + ".",
              f"Sin hospital, las variables y los CatBoost de la 5b reproducen su control sin diferencia. "
              f"Hospital: {len(one_hot_hospital)} columnas de one-hot; celda 17 con {len(tabla_17['filas'])} grupos.",
              f"Tiempo: {resultado['segundos']['total']} s. No envía nada y no calcula ninguna métrica."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']['total']} s", flush=True)


if __name__ == "__main__":
    main()

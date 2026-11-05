#!/usr/bin/env python3
"""
fase5b_entrenar.py — la Fase 5b de PLAN.md: entrena con todos los datos de
entrenamiento, desarrollo y reservado (1.042 pacientes), los modelos de los
envíos tardíos a Kaggle, con su especificación fija y semilla 0. No envía nada y
no calcula ninguna métrica.

  - M3 limpio: ganador_m3.variables_m3_en_pliegue y ajustar_m3 con
    PARAMETROS_LIMPIO, la parada sobre el 20 % interno, agrupado por paciente.
  - «Imagen + básicos»: imagen_sola, sobre las variables de DINOv2 de los dos
    archivos de la extracción, unidos por isic_id.
  - La red de la 4e sola: fase4e.entrenar_y_puntuar y
    fase4e_ajuste.ajustar_y_puntuar, sobre los 1.042 pacientes.
  - C7: cinco redes de la 4e, una por pliegue de construir_folds con semilla 0
    sobre los 1.042 pacientes, dan a cada lesión su puntuación fuera de pliegue;
    con ellas, la puntuación y su razón a la media del paciente
    (fase4c.variables_red, fase4b.con_imagen) se apilan sobre las variables de
    M3 limpio, y el CatBoost se ajusta como el de M3 limpio. Es la propuesta
    aprobada el 2026-11-04 (PLAN.md, Fase 5b).

Conjunto de control: pacientes completos de entrenamiento, elegidos como en
tiempo_inferencia.py (patient_id ordenados, barajados con la semilla
SEMILLA_CONTROL, hasta MINIMO_CONTROL lesiones). Sus filas se añaden al final
como filas nuevas, sin etiqueta, y cada modelo las puntúa con el código
verificado: son las referencias que la inferencia portátil
(inferencia_5b.py) tiene que reproducir en el Mac y en Kaggle.

fase4e_ajuste.ajustar_y_puntuar no guarda los pesos de la red ajustada. Para
guardarlos sin tocar el código de la 4e, se envuelve fase4e.predecir, que recibe
la red ajustada justo antes de puntuar: guarda su state_dict y después predice.
fase5b_paquete.py comprueba que esos pesos reproducen los logits.

Cada red se guarda en data/fase5b/redes/ con el SHA-256 del código de la red, y
la corrida se reanuda con las redes de ese mismo código. Todo lo demás va a
data/fase5b/, que no se versiona; el registro, a --out (.json y .md).

Uso (con caffeinate, en segundo plano):
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_entrenar.py \\
        --out outputs/fase5b-entrenamiento
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import sys
import time
import warnings

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase5  # noqa: E402
import ganador_m3  # noqa: E402
import imagen_sola  # noqa: E402
from apilado_imagen import modelo_imagen  # noqa: E402
from datos_desarrollo import leer_reservados  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds  # noqa: E402

RAIZ = fase5.RAIZ
G, Y = "patient_id", "target"
SEMILLA = 0
N_SPLITS = 5
SEMILLA_CONTROL = 7
MINIMO_CONTROL = 1000
DIR = os.path.join(RAIZ, "data", "fase5b")
CODIGO_RED = ["fase4e.py", "fase4e_ajuste.py", "prueba_tiempo_red_imagen.py"]
CODIGO = ["fase5b_entrenar.py", "fase4_comparar.py", "fase4b.py", "fase4b_comparar.py", "fase4c.py", "fase5.py",
          "ganador_m3.py", "imagen_sola.py", "apilado_imagen.py", "train_and_evaluate.py", *CODIGO_RED]


def sha(ruta):
    return fase5.sha256(ruta)


def huella(archivos):
    return {c: sha(os.path.join(AQUI, c)) for c in archivos}


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def rel(ruta):
    return os.path.relpath(ruta, RAIZ)


# ---- los datos ----------------------------------------------------------------------------

def cargar_todo(r):
    """Todo train-metadata.csv, con sus recuentos frente a holdout-pacientes.json."""
    df = pd.read_csv(r["csv"], low_memory=False)
    with open(r["holdout"], encoding="utf-8") as f:
        rec = json.load(f)["recuentos"]
    esperado = {k: rec["desarrollo"][k] + rec["reservado"][k] for k in ("pacientes", "lesiones_malignas")}
    obtenido = {"pacientes": int(df[G].nunique()), "lesiones_malignas": int(df[Y].sum())}
    reservados = leer_reservados(r["holdout"])
    if obtenido != esperado or not reservados <= set(df[G].astype(str)):
        raise SystemExit(f"ERROR: los datos no son los de holdout-pacientes.json: {obtenido} frente a {esperado}.")
    return df, {"archivo": rel(r["csv"]), "conjunto": "todos: desarrollo y reservado", "filas": int(len(df)),
                **obtenido, "pacientes_del_reservado": len(reservados)}


def cargar_dinov2(df, r):
    """Las variables de DINOv2 de los dos archivos de la extracción, alineadas con df."""
    import h5py
    with open(r["extraccion"], encoding="utf-8") as f:
        conjuntos = json.load(f)["conjuntos"]
    partes, comprobacion = [], {}
    for c in ("desarrollo", "reservado"):
        ruta = os.path.join(RAIZ, conjuntos[c]["archivo"]["archivo"])
        if sha(ruta) != conjuntos[c]["archivo"]["sha256"]:
            raise SystemExit(f"ERROR: {rel(ruta)} no tiene el SHA-256 de la extracción.")
        with h5py.File(ruta, "r") as h:
            if h.attrs["conjunto"] != c or not h["decodificada"][:].all():
                raise SystemExit(f"ERROR: {rel(ruta)} no es el conjunto {c} entero y decodificado.")
            partes.append(pd.DataFrame(h["cls"][:], index=pd.Index(h["isic_id"].asstr()[:], name="isic_id")))
        comprobacion[c] = {"archivo": rel(ruta), "sha256": conjuntos[c]["archivo"]["sha256"],
                           "filas": int(len(partes[-1]))}
    tabla = pd.concat(partes)
    if not tabla.index.is_unique or set(tabla.index) != set(df["isic_id"]):
        raise SystemExit("ERROR: los isic_id de DINOv2 no son exactamente los de los datos.")
    x = tabla.reindex(df["isic_id"].to_numpy()).to_numpy()
    if np.isnan(x).any():
        raise SystemExit("ERROR: hay variables de DINOv2 vacías tras alinear.")
    return x, comprobacion


def elegir_control(df):
    pacientes = np.array(sorted(df[G].astype(str).unique()))
    orden = np.random.default_rng(SEMILLA_CONTROL).permutation(pacientes)
    tamanos = df[G].astype(str).value_counts()
    elegidos, total = [], 0
    for p in orden:
        elegidos.append(str(p))
        total += int(tamanos[p])
        if total >= MINIMO_CONTROL:
            break
    return elegidos


# ---- las redes ----------------------------------------------------------------------------

def red_de_la_4e(nombre, r, isic, etiquetas, filas_ent, filas_pred, dispositivo, meta):
    """Una red de la 4e con su ajuste fino: (logit de filas_pred, registro). Se guarda en
    DIR/redes con los pesos base y los ajustados, y se reanuda si ya está con el mismo
    código y los mismos datos."""
    import torch
    import fase4e
    import fase4e_ajuste
    d = os.path.join(DIR, "redes")
    os.makedirs(d, exist_ok=True)
    base, ajustados = os.path.join(d, f"{nombre}-base.pt"), os.path.join(d, f"{nombre}.pt")
    ruta_npz, ruta_json = os.path.join(d, f"{nombre}.npz"), os.path.join(d, f"{nombre}.json")
    codigo = huella(CODIGO_RED)
    if os.path.exists(ruta_npz) and os.path.exists(ruta_json):
        with open(ruta_json, encoding="utf-8") as f:
            reg = json.load(f)
        if reg["sha256_del_codigo"] != codigo or reg["meta"] != meta or reg["sha256_npz"] != sha(ruta_npz) \
                or reg["sha256_pesos_ajustados"] != sha(ajustados):
            raise SystemExit(f"ERROR: la red {nombre} guardada es de otro código o de otros datos; bórrela para rehacerla.")
        z = np.load(ruta_npz, allow_pickle=False)
        return z["logit"].astype(np.float64), reg, True
    _, reg_base = fase4e.entrenar_y_puntuar(r["hdf5"], isic, etiquetas, filas_ent, filas_pred, SEMILLA, dispositivo,
                                            pesos_en=base, predecir_filas=False)
    if reg_base["negativos"] != "conjuntos" or reg_base["negativos_en_mas_de_una_epoca"] != 0 \
            or reg_base["epocas_corridas"] != fase4e.EPOCAS or reg_base["conjuntos"] != fase4e.CONJUNTOS:
        raise SystemExit(f"ERROR: la red {nombre} no corrió sus {fase4e.EPOCAS} épocas con un conjunto de negativos "
                         "distinto en cada una.")
    original = fase4e.predecir
    llamadas = []

    def predecir_y_guardar(modelo, *a, **k):
        torch.save(modelo.state_dict(), ajustados)
        llamadas.append(1)
        return original(modelo, *a, **k)
    fase4e.predecir = predecir_y_guardar
    try:
        logit, reg_ajuste = fase4e_ajuste.ajustar_y_puntuar(r["hdf5"], isic, etiquetas, filas_ent, filas_pred, SEMILLA,
                                                            dispositivo, base)
    finally:
        fase4e.predecir = original
    if len(llamadas) != 1 or reg_ajuste["lotes_corridos"] != reg_ajuste["lotes_por_epoca"] \
            or reg_ajuste["sha256_pesos_de_partida"] != sha(base):
        raise SystemExit(f"ERROR: el ajuste de la red {nombre} no partió de sus pesos, no corrió todos sus lotes o no "
                         "guardó los pesos ajustados una sola vez.")
    logit = np.asarray(logit, dtype=np.float32)
    np.savez(ruta_npz, isic_id=np.asarray(isic[filas_pred], dtype=str), logit=logit)
    reg = {"red": nombre, "meta": meta, "base": reg_base, "ajuste": reg_ajuste, "sha256_del_codigo": codigo,
           "sha256_pesos_base": sha(base), "sha256_pesos_ajustados": sha(ajustados), "sha256_npz": sha(ruta_npz),
           "fecha": ahora()}
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    return logit.astype(np.float64), reg, False


# ---- los ajustes, en números --------------------------------------------------------------

def ajuste_m3_en_numeros(aj, cats):
    """Lo que inferencia_5b.py necesita del ajuste de M3 limpio, sin objetos de
    scikit-learn: categorías del one-hot, media y escala, centros del k-means y medias
    y desviaciones de cada conglomerado."""
    etiquetas = list(range(aj["kmeans"].n_clusters))
    media = aj["media_conglomerado"].reindex(etiquetas)
    sd = aj["desviacion_conglomerado"].reindex(etiquetas)
    json_ = {"listas": aj["listas"], "categoricas_brutas": aj["categoricas_brutas"], "medianas": aj["medianas"],
             "categorias_one_hot": [[str(v) for v in c] for c in aj["one_hot"].categories_],
             "nombres_one_hot": aj["nombres_one_hot"], "columnas_conglomerado": aj["columnas_conglomerado"],
             "finales": aj["finales"], "categoricas_catboost": cats}
    npz = {"escala_media": aj["escala"].mean_, "escala_escala": aj["escala"].scale_,
           "centros": aj["kmeans"].cluster_centers_, "media_conglomerado": media.to_numpy(dtype=float),
           "desviacion_conglomerado": sd.to_numpy(dtype=float)}
    return json_, npz


def ajuste_ib_en_numeros(df, tr, modelo):
    """La codificación de codificar_fold para los tres básicos, y el estandarizado y la
    logística del pipeline, en números."""
    medianas = {c: float(df[c].iloc[tr].median()) for c in imagen_sola.BASICOS_NUMERICAS}
    medias = {c: {str(k): float(v) for k, v in df.iloc[tr].groupby(c)[Y].mean().items()}
              for c in imagen_sola.BASICOS_CATEGORICAS}
    escala, logistica = modelo.steps[0][1], modelo.steps[1][1]
    json_ = {"numericas": imagen_sola.BASICOS_NUMERICAS, "categoricas": imagen_sola.BASICOS_CATEGORICAS,
             "medianas": medianas, "medias": medias, "media_global": float(df[Y].iloc[tr].mean())}
    npz = {"escala_media": escala.mean_, "escala_escala": escala.scale_, "coef": logistica.coef_.ravel(),
           "intercepto": logistica.intercept_}
    return json_, npz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    import fase4c
    import torch
    r = fase5.rutas(RAIZ)
    if not os.path.exists(r["salida"]["apertura"] + ".json"):
        raise SystemExit("ERROR: la Fase 5b va después de la Fase 5, y falta outputs/fase5-reservado.json.")
    bajo_caffeinate = fase4c.caffeinate()
    if not bajo_caffeinate["activo"]:
        raise SystemExit("ERROR: el programa corre bajo caffeinate (caffeinate -i …).")
    controles_4e = fase5.comprobar_red_antes(r)
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")
    os.makedirs(DIR, exist_ok=True)
    t_total, segundos = time.perf_counter(), {}

    t0 = time.perf_counter()
    df, datos = cargar_todo(r)
    excluidas = cargar_columnas_excluidas(r["fugas"])
    x_dino, comprobacion_dino = cargar_dinov2(df, r)
    control = elegir_control(df)
    en_control = df[G].astype(str).isin(control).to_numpy()
    filas_c = np.flatnonzero(en_control)
    n, m = len(df), len(filas_c)
    ext = pd.concat([df, df.iloc[filas_c].assign(**{Y: np.nan})], ignore_index=True)
    tr, va_c = np.arange(n), np.arange(n, n + m)
    y, g = df[Y].to_numpy().astype(np.int64), df[G].astype(str).to_numpy()
    g_c = g[filas_c]
    segundos["carga"] = round(time.perf_counter() - t0, 1)
    print(f"Datos: {datos['pacientes']} pacientes, {n} lesiones; control: {len(control)} pacientes, {m} lesiones",
          flush=True)

    t0 = time.perf_counter()
    x_tr, x_c, cats, inv, aj = ganador_m3.variables_m3_en_pliegue(ext.drop(columns=[Y]), tr, va_c, excluidas, G,
                                                                  devolver_ajuste=True)
    m3 = ganador_m3.ajustar_m3(x_tr, y, g, cats, SEMILLA, parametros=ganador_m3.PARAMETROS_LIMPIO)
    s_m3_c = m3.predict_proba(x_c)[:, 1]
    m3.save_model(os.path.join(DIR, "m3limpio.cbm"))
    aj_json, aj_npz = ajuste_m3_en_numeros(aj, cats)
    with open(os.path.join(DIR, "m3limpio-ajuste.json"), "w", encoding="utf-8") as f:
        json.dump(aj_json, f, ensure_ascii=False)
    np.savez(os.path.join(DIR, "m3limpio-ajuste.npz"), **aj_npz)
    info = {"M3limpio": {"n_variables": inv["n_variables"], "arboles": int(m3.tree_count_),
                         "iteraciones_corridas": len(m3.get_evals_result()["validation"]["AUC"])}}
    segundos["M3limpio"] = round(time.perf_counter() - t0, 1)
    print(f"M3 limpio: {info['M3limpio']} ({segundos['M3limpio']} s)", flush=True)

    t0 = time.perf_counter()
    b_tr, b_c = codificar_fold(ext, imagen_sola.BASICOS_NUMERICAS, imagen_sola.BASICOS_CATEGORICAS, Y, tr, va_c)
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        ib = modelo_imagen().fit(np.hstack([x_dino, b_tr]), y)
    s_ib_c = ib.predict_proba(np.hstack([x_dino[filas_c], b_c]))[:, 1]
    ib_json, ib_npz = ajuste_ib_en_numeros(ext, tr, ib)
    with open(os.path.join(DIR, "imagen-basicos.json"), "w", encoding="utf-8") as f:
        json.dump(ib_json, f, ensure_ascii=False)
    np.savez(os.path.join(DIR, "imagen-basicos.npz"), **ib_npz)
    info["ImagenBasicos"] = {"n_variables": int(x_dino.shape[1] + b_tr.shape[1]),
                             "avisos": sorted({str(a.category.__name__) for a in avisos})}
    segundos["ImagenBasicos"] = round(time.perf_counter() - t0, 1)
    print(f"«Imagen + básicos»: {info['ImagenBasicos']} ({segundos['ImagenBasicos']} s)", flush=True)

    isic_ext = ext["isic_id"].to_numpy()
    y_ext = np.concatenate([y, np.full(m, -1, dtype=np.int64)])
    folds = construir_folds(df, G, Y, N_SPLITS, SEMILLA)
    huella_folds = f4.huella_folds(folds, n)
    sha_control = hashlib.sha256("\n".join(isic_ext[va_c]).encode()).hexdigest()
    logits_c, oof, registros = {}, {}, {}
    asignacion = np.full(n, -1)
    for k, (ftr, fva) in enumerate(folds):
        asignacion[fva] = k
        t0 = time.perf_counter()
        meta = {"filas_de_entrenamiento": f"pliegue de entrenamiento {k} de construir_folds, semilla 0",
                "sha256_pliegues": huella_folds, "sha256_control": sha_control, "n_puntuadas": int(len(fva) + m)}
        logit, reg, leida = red_de_la_4e(f"pliegue-{k}", r, isic_ext, y_ext, ftr, np.concatenate([fva, va_c]),
                                         dispositivo, meta)
        oof[k] = (isic_ext[fva], logit[:len(fva)])
        logits_c[f"pliegue-{k}"] = logit[len(fva):]
        registros[f"pliegue-{k}"] = reg
        segundos[f"red-pliegue-{k}"] = round(time.perf_counter() - t0, 1)
        print(f"Red del pliegue {k}: {'leída' if leida else str(segundos[f'red-pliegue-{k}']) + ' s'}", flush=True)
    t0 = time.perf_counter()
    meta = {"filas_de_entrenamiento": "los 1.042 pacientes", "sha256_control": sha_control, "n_puntuadas": int(m)}
    logit, reg, leida = red_de_la_4e("sola", r, isic_ext, y_ext, tr, va_c, dispositivo, meta)
    logits_c["sola"], registros["sola"] = logit, reg
    segundos["red-sola"] = round(time.perf_counter() - t0, 1)
    print(f"Red sola: {'leída' if leida else str(segundos['red-sola']) + ' s'}", flush=True)

    t0 = time.perf_counter()
    logit_oof = fase4c.ensamblar(oof, df["isic_id"].to_numpy(), asignacion)
    p_oof = fase4c.probabilidad(logit_oof)
    p_c = np.mean([fase4c.probabilidad(logits_c[f"pliegue-{k}"]) for k in range(N_SPLITS)], axis=0)
    a = fase4c.variables_red(np.concatenate([p_oof, p_c]), tr, va_c, np.concatenate([g, g_c]))
    xc_tr, xc_c = fase4b.con_imagen(x_tr, x_c, a)
    alin = f4b.comprobar_alineacion(x_tr, xc_tr, a, SEMILLA, y, g)
    if not all(alin[k] for k in ("antes", "razon", "despues")):
        raise SystemExit(f"ERROR: alineación de C7: {alin}")
    c7 = ganador_m3.ajustar_m3(xc_tr, y, g, cats, SEMILLA, parametros=ganador_m3.PARAMETROS_LIMPIO)
    s_c7_c = c7.predict_proba(xc_c)[:, 1]
    c7.save_model(os.path.join(DIR, "c7.cbm"))
    info["C7"] = {"n_variables": int(xc_tr.shape[1]), "arboles": int(c7.tree_count_),
                  "iteraciones_corridas": len(c7.get_evals_result()["validation"]["AUC"]), "alineacion": alin,
                  "puntuacion_al_predecir": "la media de las puntuaciones (sigmoide del logit) de las cinco redes"}
    segundos["C7"] = round(time.perf_counter() - t0, 1)
    print(f"C7: {info['C7']['arboles']} árboles ({segundos['C7']} s)", flush=True)

    np.savez(os.path.join(DIR, "control.npz"), isic_id=np.asarray(isic_ext[va_c], dtype=str),
             patient_id=np.asarray(g_c, dtype=str), m3limpio=s_m3_c, imagen_basicos=s_ib_c, c7=s_c7_c,
             logit_sola=logits_c["sola"], logit_pliegues=np.stack([logits_c[f"pliegue-{k}"] for k in range(N_SPLITS)]),
             p_red_media=p_c, dinov2=x_dino[filas_c], basicos=b_c, x_m3=x_c.astype(float).to_numpy(),
             x_m3_columnas=np.asarray(list(x_c.columns), dtype=str), etiquetas_kmeans_entrenamiento=aj["kmeans"].labels_)
    pd.DataFrame({"isic_id": df["isic_id"], "pliegue": asignacion, "logit": logit_oof, "puntuacion": p_oof}).to_csv(
        os.path.join(DIR, "puntuaciones-fuera-de-pliegue.csv.gz"), index=False, float_format="%.17g", compression="gzip")

    archivos = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(DIR) for f in fs)
    import catboost
    import sklearn
    import torchvision
    resultado = {
        "que_es": ("los modelos de los envíos tardíos de la Fase 5b, entrenados con todos los datos de entrenamiento "
                   "(PLAN.md, Fase 5b); no envía nada y no calcula ninguna métrica"),
        "datos": datos, "dinov2": comprobacion_dino,
        "control": {"semilla": SEMILLA_CONTROL, "minimo_de_lesiones": MINIMO_CONTROL, "pacientes": control,
                    "lesiones": int(m), "sha256_isic_id": sha_control,
                    "que_es": "filas de entrenamiento puntuadas como nuevas, referencias para inferencia_5b.py"},
        "pliegues_de_c7": {"semilla": SEMILLA, "n_splits": N_SPLITS, "sha256": huella_folds,
                           "lesiones_por_pliegue": [int(len(v)) for _, v in folds]},
        "modelos": info,
        "redes": {k: {"epocas": v["base"]["epocas_corridas"], "positivos": v["base"]["positivos"],
                      "negativos_en_mas_de_una_epoca": v["base"]["negativos_en_mas_de_una_epoca"],
                      "lotes_del_ajuste": v["ajuste"]["lotes_corridos"], "segundos_base": v["base"]["segundos_total"],
                      "segundos_ajuste": v["ajuste"]["segundos_total"], "sha256_pesos_ajustados": v["sha256_pesos_ajustados"]}
                  for k, v in registros.items()},
        "controles_de_la_red_4e": controles_4e,
        "archivos": {rel(a): {"bytes": os.path.getsize(a), "sha256": sha(a)} for a in archivos
                     if not a.endswith("-base.pt")},
        "sha256_del_codigo": huella(CODIGO),
        "comando": {"interprete": rel(sys.executable), "argumentos": sys.argv, "caffeinate": bajo_caffeinate},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "catboost": catboost.__version__,
                      "torch": torch.__version__, "torchvision": torchvision.__version__},
        "fecha": ahora(),
        "segundos": {**segundos, "total": round(time.perf_counter() - t_total, 1)},
        "nota": "No envía nada y no calcula ninguna métrica.",
    }
    out = args.out if os.path.isabs(args.out) else os.path.join(RAIZ, args.out)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    lineas = ["# Fase 5b — entrenamiento con todos los datos",
              f"Datos: {datos['pacientes']} pacientes, {datos['filas']} lesiones, {datos['lesiones_malignas']} malignas; "
              f"semilla 0. Control: {len(control)} pacientes, {m} lesiones, puntuados como filas nuevas.",
              f"M3 limpio: {info['M3limpio']['arboles']} árboles · C7: {info['C7']['arboles']} árboles · "
              f"«Imagen + básicos»: {info['ImagenBasicos']['n_variables']} variables",
              f"Redes de la 4e: {len(registros)} (cinco de pliegue para C7 y la sola), "
              f"{sum(v['base']['epocas_corridas'] for v in registros.values())} épocas en total",
              f"Tiempo: {resultado['segundos']['total']} s. No envía nada y no calcula ninguna métrica."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md; {resultado['segundos']['total']} s", flush=True)


if __name__ == "__main__":
    main()

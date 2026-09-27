#!/usr/bin/env python3
"""
tiempo_inferencia.py — el tiempo de inferencia de la Fase 4, con la
especificación fijada en PLAN.md («Tiempo de inferencia», 2026-09-26) antes de
medir.

Los modelos son M1, M2, M3 limpio, M4 y M4b, y cada uno se entrena una vez con
los pacientes de desarrollo que no están en el subconjunto, con su
especificación de la Fase 4 y semilla 0. El subconjunto son pacientes completos
de desarrollo: sus patient_id ordenados, barajados con numpy.random.default_rng(7),
se añaden en ese orden hasta sumar 5.000 lesiones o más.

El camino cronometrado va desde las filas de metadatos del subconjunto, ya en
memoria y sin la etiqueta, hasta la puntuación de cada lesión. En M4 y M4b parte
también de las imágenes de data/train-image.hdf5. Calcula todo lo que el modelo
necesita al predecir:
- las variables por paciente, el LOF y los conglomerados;
- las transformaciones ya ajustadas en el entrenamiento;
- la lectura, la decodificación y el preprocesado de la imagen y DINOv2 ViT-S/14,
  en MPS, con el lote de 64 y el preprocesado de la extracción (extraer.py);
- la predicción.
Cargar los modelos y los pesos de DINOv2 queda fuera.

Antes de cronometrar, un control compara el camino cronometrado con el normal,
que es el de la Fase 4 con el mismo modelo entrenado. En M1, M2 y M3 limpio las
puntuaciones tienen que ser idénticas. En M4 y M4b se comprueba:
- (a) que las variables de DINOv2 difieren de las del archivo de la extracción
  en 1e-3 como máximo;
- (b) que, con las del archivo, las puntuaciones son idénticas;
- (c) cuánto difieren las puntuaciones con las recalculadas. Se reporta sin
  umbral.
Después se quita cada paso, uno por vez, y la comprobación tiene que fallar cada
vez. Si el camino sin el paso no llega a puntuar, porque algo se niega a correr,
también cuenta como fallo, y se registra el error. Esa parte corre sobre una
copia del subconjunto con la edad de todos sus pacientes borrada en los dos
caminos, para que la imputación tenga efecto. Para el paso de imputación se
compara además la matriz que entra al modelo, que es la que tiene que cambiar:
que una puntuación no cambie no prueba que el paso se ejecutó. Es la enmienda
del 2026-09-27 en PLAN.md. Los pasos de imagen son los mismos en M4 y M4b y se
comprueban una vez. Si algo falla, no se cronometra.

No interpreta: mide y escribe --out.json y su .md.

Uso (con caffeinate, en segundo plano):
    python tiempo_inferencia.py --data data/train-metadata.csv \
        --leakage-report outputs/auditoria-de-fugas.json \
        --imagen data/dinov2-vits14-desarrollo.h5 --extraccion outputs/extraccion-imagen.json \
        --hdf5 data/train-image.hdf5 --repo data/dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8 \
        --out outputs/tiempo-inferencia
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import warnings

import h5py
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "extraccion-imagen", "scripts"))
import fase4_comparar as f4  # noqa: E402  (también fija el filtro de PerformanceWarning)
import ganador_m3  # noqa: E402
import extraer  # noqa: E402
from apilado_imagen import puntuaciones_imagen, razon_paciente  # noqa: E402
from contexto_paciente import variables_contexto_paciente  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, preparar_features  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

SEMILLA_SUBCONJUNTO = 7
MINIMO_DE_LESIONES = 5000
SEMILLA = 0
REPETICIONES = 5
TOLERANCIA_DINOV2 = 1e-3
LOTE = 64
MODELOS = ["M1", "M2", "M3limpio", "M4", "M4b"]
PASOS_M2 = ["imputacion", "codificacion_categoricas", "variables_por_paciente", "lof"]
PASOS_DE_IMAGEN = ["lectura_y_decodificacion", "preprocesado", "dinov2"]
PASOS = {
    "M1": ["imputacion", "codificacion_categoricas"],
    "M2": PASOS_M2,
    "M3limpio": ["imputacion_edad", "variables_por_paciente", "one_hot", "estandarizado_y_lof", "conglomerado",
                 "medias_por_conglomerado"],
    "M4": PASOS_M2 + PASOS_DE_IMAGEN,
    "M4b": PASOS_M2 + PASOS_DE_IMAGEN + ["logistica_imagen", "razon_paciente"],
}


def elegir_subconjunto(df, group_col, minimo=MINIMO_DE_LESIONES):
    pacientes = np.array(sorted(df[group_col].astype(str).unique()))
    orden = np.random.default_rng(SEMILLA_SUBCONJUNTO).permutation(pacientes)
    tamanos = df[group_col].astype(str).value_counts()
    elegidos, total = [], 0
    for p in orden:
        elegidos.append(str(p))
        total += int(tamanos[p])
        if total >= minimo:
            break
    return elegidos, total


# ---- DINOv2 en el camino cronometrado ---------------------------------------------------

def _sin_normalizar(crudo):
    """El paso de preprocesado quitado: la imagen redimensionada, sin la
    normalización. El redimensionado se deja, porque sin él no se forma el lote."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(crudo)).convert("RGB").resize((extraer.LADO, extraer.LADO), Image.BICUBIC)
    return (np.asarray(img, dtype=np.float32) / 255.0).transpose(2, 0, 1)


def caracteristicas_dinov2(ids, ruta_hdf5, modelo, dispositivo, saltar=frozenset()):
    import torch
    salida = np.empty((len(ids), extraer.DIMENSION), dtype=np.float32)
    with h5py.File(ruta_hdf5, "r") as imagenes, torch.no_grad():
        for desde in range(0, len(ids), LOTE):
            lote = ids[desde:desde + LOTE]
            if "lectura_y_decodificacion" in saltar:
                x = np.zeros((len(lote), 3, extraer.LADO, extraer.LADO), dtype=np.float32)
            else:
                crudos = [bytes(imagenes[i][()]) for i in lote]
                if "preprocesado" in saltar:
                    x = np.stack([_sin_normalizar(c) for c in crudos])
                else:
                    x = np.stack([extraer.preprocesar(c)[0] for c in crudos])
            if "dinov2" in saltar:
                salida[desde:desde + len(lote)] = 0.0
            else:
                salida[desde:desde + len(lote)] = modelo(torch.from_numpy(x).to(dispositivo)).cpu().numpy()
    return salida


# ---- el camino cronometrado -------------------------------------------------------------

def puntuar(m, filas, ctx, saltar=frozenset(), caracteristicas=None, devolver_matriz=False):
    """Puntuaciones del modelo m para las filas (metadatos sin etiqueta). En M4 y
    M4b, si no se dan `caracteristicas`, se calculan con DINOv2 desde las imágenes.
    Con `devolver_matriz`, devuelve también la matriz que entra al modelo."""
    g = ctx["group_col"]
    if m == "M3limpio":
        return _puntuar_m3limpio(filas, ctx, saltar, devolver_matriz)
    e = ctx["entrenados"][m]
    columnas = {}
    base = ctx["numericas"]
    for c in base:
        columnas[c] = filas[c]
    if m in ("M2", "M4", "M4b"):
        contexto = variables_contexto_paciente(filas, base, g)
        if "variables_por_paciente" in saltar:
            contexto.loc[:, [c for c in contexto.columns if c != "of"]] = np.nan
        if "lof" in saltar:
            contexto["of"] = np.nan
        for c in contexto.columns:
            columnas[c] = contexto[c]
    if m in ("M4", "M4b"):
        if caracteristicas is None:
            caracteristicas = caracteristicas_dinov2(filas["isic_id"].tolist(), ctx["hdf5"], ctx["dinov2"],
                                                     ctx["dispositivo"], saltar)
        if m == "M4":
            for j, c in enumerate(ctx["columnas_imagen"]):
                columnas[c] = pd.Series(caracteristicas[:, j], index=filas.index)
        else:
            if "logistica_imagen" in saltar:
                puntuacion = np.full(len(filas), np.nan)
            else:
                puntuacion = ctx["logistica_imagen"].predict_proba(caracteristicas)[:, 1]
            razon = (np.full(len(filas), np.nan) if "razon_paciente" in saltar
                     else razon_paciente(puntuacion, filas[g].to_numpy()))
            columnas[f4.APILADAS[0]] = pd.Series(puntuacion, index=filas.index)
            columnas[f4.APILADAS[1]] = pd.Series(razon, index=filas.index)
    # Las transformaciones ya ajustadas, como codificar_fold las aplica a validación.
    x = pd.DataFrame(index=range(len(filas)))
    for c in e["numericas"]:
        valores = columnas[c]
        x[c] = (valores if "imputacion" in saltar else valores.fillna(e["medianas"][c])).values
    for c in ctx["categoricas"]:
        if "codificacion_categoricas" in saltar:
            x[c] = np.full(len(filas), e["media_global"])
        else:
            x[c] = filas[c].map(e["medias"][c]).fillna(e["media_global"]).values
    puntuaciones = e["modelo"].predict_proba(x.values)[:, 1]
    return (puntuaciones, x.values) if devolver_matriz else puntuaciones


def _puntuar_m3limpio(filas, ctx, saltar, devolver_matriz=False):
    a, g = ctx["ajuste_m3limpio"], ctx["group_col"]
    L = a["listas"]
    medianas = {c: np.nan for c in a["medianas"]} if "imputacion_edad" in saltar else a["medianas"]
    b = ganador_m3.variables_lectura(filas, L, g, medianas)
    if "variables_por_paciente" in saltar:
        por_paciente = [f"{c}_patient_norm" for c in L["num_cols"] + L["new_num_cols"]] + L["special_cols"]
        b.loc[:, por_paciente] = np.nan
    cat = a["categoricas_brutas"]
    texto = filas[cat].astype(object).where(filas[cat].notna(), "").astype(str)
    codificadas = (np.zeros((len(filas), len(a["nombres_one_hot"])), dtype=np.int32) if "one_hot" in saltar
                   else a["one_hot"].transform(texto))
    oh = pd.DataFrame(codificadas, index=filas.index, columns=a["nombres_one_hot"]).astype("category")
    top = L["top_lof_features"]
    escalada = a["escala"].transform(b[top].to_numpy(dtype=float))
    b["of"] = (np.full(len(filas), -1.0) if "estandarizado_y_lof" in saltar
               else ganador_m3.lof_publicado(escalada, filas[g]))
    et = np.zeros(len(filas), dtype=int) if "conglomerado" in saltar else a["kmeans"].predict(escalada)
    cols = a["columnas_conglomerado"]
    if "medias_por_conglomerado" in saltar:
        valores = np.full((len(filas), len(cols)), np.nan)
    else:
        valores = ((b[cols].to_numpy() - a["media_conglomerado"].loc[et].to_numpy())
                   / a["desviacion_conglomerado"].loc[et].to_numpy())
    cl = pd.DataFrame(valores, index=filas.index, columns=[f"{c}__cluster" for c in cols])
    x = pd.concat([b, oh, cl], axis=1)[a["finales"]]
    puntuaciones = ctx["modelo_m3limpio"].predict_proba(x)[:, 1]
    return (puntuaciones, x.astype(float).to_numpy()) if devolver_matriz else puntuaciones


# ---- el camino normal: el de la Fase 4 ----------------------------------------------------

def preparar(df_crudo, args, excluidas, cargar):
    """Las variables de la Fase 4 sobre todo el desarrollo (contexto e imagen)."""
    numericas, categoricas = preparar_features(df_crudo, excluidas, args.target_col, args.group_col)
    contexto = variables_contexto_paciente(df_crudo.drop(columns=[args.target_col]), numericas, args.group_col)
    imagen, comprobacion = cargar
    return pd.concat([df_crudo, contexto, imagen], axis=1), numericas, categoricas, list(contexto.columns), comprobacion


def columnas_de(m, numericas, contexto, imagen):
    return {"M1": numericas, "M2": numericas + contexto, "M4": numericas + contexto + imagen,
            "M4b": numericas + contexto + f4.APILADAS}[m]


def poner_apiladas(d, apilado, tr, va):
    """Las dos variables apiladas de M4b, como las pone fase4_comparar.py. Ningún otro
    modelo las usa."""
    for col, clave in zip(f4.APILADAS, ("puntuacion", "razon")):
        v = np.full(len(d), np.nan)
        v[tr], v[va] = apilado["tr"][clave], apilado["va"][clave]
        d[col] = v


def camino_normal(df, cols_por_modelo, categoricas, args, tr, va, entrenados, df_crudo, excluidas, ctx):
    """Puntuaciones de la Fase 4 para las filas va, con los modelos ya entrenados, y
    las matrices que entran a cada modelo."""
    salida, matrices = {}, {}
    for m in ("M1", "M2", "M4", "M4b"):
        _, x_va = codificar_fold(df, cols_por_modelo[m], categoricas, args.target_col, tr, va)
        salida[m], matrices[m] = entrenados[m]["modelo"].predict_proba(x_va)[:, 1], x_va
    _, x_va, _, _ = ganador_m3.variables_m3_en_pliegue(df_crudo.drop(columns=[args.target_col]), tr, va, excluidas,
                                                        args.group_col)
    salida["M3limpio"] = ctx["modelo_m3limpio"].predict_proba(x_va)[:, 1]
    matrices["M3limpio"] = x_va.astype(float).to_numpy()
    return salida, matrices


def declaraciones(ctx):
    import catboost
    import imblearn
    import PIL
    import scipy
    import sklearn
    import threadpoolctl
    import torch

    def sysctl(clave):
        return subprocess.run(["sysctl", "-n", clave], capture_output=True, text=True).stdout.strip()
    hilos_openmp = sorted({i["num_threads"] for i in threadpoolctl.threadpool_info() if i.get("user_api") == "openmp"})
    comunes = {"numpy": np.__version__, "pandas": pd.__version__}
    return {
        "equipo": {"chip": sysctl("machdep.cpu.brand_string"), "memoria_gb": int(sysctl("hw.memsize")) / 2**30,
                   "nucleos": os.cpu_count()},
        "sistema": {"macos": platform.mac_ver()[0], "plataforma": platform.platform()},
        "interprete": {"python": platform.python_version(), "ejecutable": sys.executable},
        "versiones_por_modelo": {
            "M1": {**comunes, "scikit_learn": sklearn.__version__},
            "M2": {**comunes, "scikit_learn": sklearn.__version__},
            "M3limpio": {**comunes, "scikit_learn": sklearn.__version__, "catboost": catboost.__version__},
            "M4": {**comunes, "scikit_learn": sklearn.__version__, "torch": torch.__version__,
                   "pillow": PIL.__version__, "h5py": h5py.__version__},
            "M4b": {**comunes, "scikit_learn": sklearn.__version__, "torch": torch.__version__,
                    "pillow": PIL.__version__, "h5py": h5py.__version__},
        },
        "solo_en_el_entrenamiento": {"imbalanced_learn": imblearn.__version__, "scipy": scipy.__version__},
        "dinov2": {"modelo": extraer.MODELO, "pesos_sha256": extraer.PESOS_SHA256, "dispositivo": str(ctx["dispositivo"]),
                   "lote": LOTE, "preprocesado": extraer.PREPROCESADO},
        "hilos": {"torch_cpu": torch.get_num_threads(), "openmp_scikit_learn": hilos_openmp,
                  "catboost": "thread_count por defecto (todos los núcleos)"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", default="patient_id")
    ap.add_argument("--target-col", default="target")
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--imagen", required=True, help="características de desarrollo de la extracción")
    ap.add_argument("--extraccion", required=True)
    ap.add_argument("--hdf5", required=True, help="las imágenes, data/train-image.hdf5")
    ap.add_argument("--repo", required=True, help="copia local del repositorio dinov2 del commit de la extracción")
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--out", required=True)
    # Solo para pruebas de humo; la corrida de la especificación usa los valores fijados.
    ap.add_argument("--minimo-lesiones", type=int, default=MINIMO_DE_LESIONES)
    ap.add_argument("--repeticiones", type=int, default=REPETICIONES)
    args = ap.parse_args()
    import torch
    t_total = time.perf_counter()

    # Datos, subconjunto y entrenamiento: no se cronometran.
    excluidas = cargar_columnas_excluidas(args.leakage_report)
    df_crudo, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    elegidos, n_lesiones = elegir_subconjunto(df_crudo, args.group_col, args.minimo_lesiones)
    en_sub = df_crudo[args.group_col].astype(str).isin(elegidos).to_numpy()
    tr, va = np.flatnonzero(~en_sub), np.flatnonzero(en_sub)
    cargar = f4.cargar_imagen(df_crudo, args.imagen, args.data, args.holdout, args.extraccion)
    df, numericas, categoricas, cols_contexto, comprobacion_imagen = preparar(df_crudo, args, excluidas, cargar)
    cols_imagen = list(cargar[0].columns)
    y, grupos = df[args.target_col].to_numpy(), df[args.group_col].to_numpy()
    cols_por_modelo = {m: columnas_de(m, numericas, cols_contexto, cols_imagen) for m in ("M1", "M2", "M4", "M4b")}

    t0 = time.perf_counter()
    apilado = puntuaciones_imagen(cargar[0].to_numpy(), y, grupos, tr, va, SEMILLA)
    poner_apiladas(df, apilado, tr, va)
    entrenados = {}
    for m in ("M1", "M2", "M4", "M4b"):
        d = df
        x_tr, _ = codificar_fold(d, cols_por_modelo[m], categoricas, args.target_col, tr, va)
        modelo = HistGradientBoostingClassifier(random_state=SEMILLA, class_weight="balanced").fit(x_tr, y[tr])
        entrenados[m] = {
            "modelo": modelo, "numericas": cols_por_modelo[m],
            "medianas": {c: d[c].iloc[tr].median() for c in cols_por_modelo[m]},
            "medias": {c: d.iloc[tr].groupby(c)[args.target_col].mean() for c in categoricas},
            "media_global": d[args.target_col].iloc[tr].mean(),
        }
    sin_etiqueta = df_crudo.drop(columns=[args.target_col])
    x3_tr, _, cats3, inv3, ajuste3 = ganador_m3.variables_m3_en_pliegue(sin_etiqueta, tr, va, excluidas,
                                                                        args.group_col, devolver_ajuste=True)
    modelo3 = ganador_m3.ajustar_m3(x3_tr, y[tr], grupos[tr], cats3, SEMILLA, parametros=ganador_m3.PARAMETROS_LIMPIO)
    t_entrenamiento = time.perf_counter() - t0

    # DINOv2, cargado una vez, fuera del cronómetro: los mismos pesos y código que la extracción.
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible; la extracción se hizo en MPS.")
    ruta_pesos = os.path.join(torch.hub.get_dir(), "checkpoints", extraer.PESOS)
    if extraer.sha256(ruta_pesos) != extraer.PESOS_SHA256:
        raise SystemExit("ERROR: los pesos de DINOv2 no son los de la extracción.")
    sys.path.insert(0, args.repo)
    from dinov2.hub import backbones  # noqa: E402
    dispositivo = torch.device("mps")
    dinov2 = getattr(backbones, extraer.MODELO)(pretrained=True).eval().to(dispositivo)

    ctx = {"group_col": args.group_col, "numericas": numericas, "categoricas": categoricas,
           "columnas_imagen": cols_imagen, "entrenados": entrenados, "logistica_imagen": apilado["modelo_completo"],
           "ajuste_m3limpio": ajuste3, "modelo_m3limpio": modelo3, "hdf5": args.hdf5, "dinov2": dinov2,
           "dispositivo": dispositivo}
    filas = df_crudo.iloc[va].drop(columns=[args.target_col]).reset_index(drop=True)
    del_archivo = cargar[0].to_numpy()[va]

    # ---- control ----
    t0 = time.perf_counter()
    normal, _ = camino_normal(df, cols_por_modelo, categoricas, args, tr, va, entrenados, df_crudo, excluidas, ctx)
    recalculadas = caracteristicas_dinov2(filas["isic_id"].tolist(), args.hdf5, dinov2, dispositivo)
    dif_dinov2 = float(np.abs(recalculadas - del_archivo).max())
    control = {"igualdad": {}, "pasos_quitados": {}}
    for m in MODELOS:
        if m in ("M4", "M4b"):
            con_archivo = puntuar(m, filas, ctx, caracteristicas=del_archivo)
            con_recalculadas = puntuar(m, filas, ctx, caracteristicas=recalculadas)
            dif = np.abs(con_recalculadas - normal[m])
            control["igualdad"][m] = {
                "a_dinov2_diferencia_maxima": dif_dinov2, "a_dentro_de_la_tolerancia": dif_dinov2 <= TOLERANCIA_DINOV2,
                "b_identicas_con_las_variables_del_archivo": bool(np.array_equal(con_archivo, normal[m])),
                "c_puntuacion_diferencia_maxima_con_las_recalculadas": float(dif.max()),
                "c_lesiones_con_diferencia_mayor_que_1e-6": int((dif > 1e-6).sum()),
            }
        else:
            control["igualdad"][m] = {"identicas": bool(np.array_equal(puntuar(m, filas, ctx), normal[m]))}

    # La copia con la edad borrada a todos los pacientes del subconjunto, en los dos caminos.
    crudo_mod = df_crudo.copy()
    edades_presentes = int(crudo_mod.loc[en_sub, "age_approx"].notna().sum())
    crudo_mod.loc[en_sub, "age_approx"] = np.nan
    del df
    df_mod, *_ = preparar(crudo_mod, args, excluidas, cargar)
    poner_apiladas(df_mod, apilado, tr, va)
    normal_mod, matrices_mod = camino_normal(df_mod, cols_por_modelo, categoricas, args, tr, va, entrenados, crudo_mod,
                                             excluidas, ctx)
    del df_mod
    filas_mod = crudo_mod.iloc[va].drop(columns=[args.target_col]).reset_index(drop=True)
    for m in MODELOS:
        caract = del_archivo if m in ("M4", "M4b") else None
        s, x = puntuar(m, filas_mod, ctx, caracteristicas=caract, devolver_matriz=True)
        control["igualdad"][m]["identicas_en_la_copia_con_la_edad_borrada"] = bool(np.array_equal(s, normal_mod[m]))
        control["igualdad"][m]["matriz_identica_en_la_copia_con_la_edad_borrada"] = bool(
            np.array_equal(x, matrices_mod[m], equal_nan=True))
    detectados_imagen = {}
    for paso in PASOS_DE_IMAGEN:
        mutadas = caracteristicas_dinov2(filas_mod["isic_id"].tolist(), args.hdf5, dinov2, dispositivo, {paso})
        d = float(np.abs(mutadas - del_archivo).max())
        detectados_imagen[paso] = {"diferencia_maxima_en_dinov2": d, "detectado": d > TOLERANCIA_DINOV2}
    for m in MODELOS:
        control["pasos_quitados"][m] = {}
        for paso in PASOS[m]:
            if paso in PASOS_DE_IMAGEN:
                control["pasos_quitados"][m][paso] = detectados_imagen[paso]
                continue
            caract = del_archivo if m in ("M4", "M4b") else None
            try:
                s, x = puntuar(m, filas_mod, ctx, saltar={paso}, caracteristicas=caract, devolver_matriz=True)
            except Exception as e:  # noqa: BLE001 — sin el paso el camino no llega a puntuar: tampoco coincide
                control["pasos_quitados"][m][paso] = {"detectado": True, "error": type(e).__name__}
                continue
            puntuaciones_distintas = not np.array_equal(s, normal_mod[m])
            if paso in ("imputacion", "imputacion_edad"):
                # Para la imputación manda la matriz (enmienda del 2026-09-27).
                matriz_distinta = not np.array_equal(x, matrices_mod[m], equal_nan=True)
                control["pasos_quitados"][m][paso] = {"detectado": matriz_distinta, "matriz_distinta": matriz_distinta,
                                                      "puntuaciones_distintas": puntuaciones_distintas}
            else:
                control["pasos_quitados"][m][paso] = {"detectado": puntuaciones_distintas}
    control["copia_con_la_edad_borrada"] = {"pacientes": len(elegidos), "lesiones": int(en_sub.sum()),
                                           "edades_presentes_que_se_borraron": edades_presentes}
    control["tolerancia_dinov2"] = TOLERANCIA_DINOV2
    t_control = time.perf_counter() - t0

    fallos = []
    for m, r in control["igualdad"].items():
        for k, v in r.items():
            if isinstance(v, bool) and not v:
                fallos.append(f"{m}: {k}")
    for m, r in control["pasos_quitados"].items():
        fallos += [f"{m}: quitar {p} no se detecta" for p, v in r.items() if not v["detectado"]]
    if fallos:
        print(json.dumps(control, ensure_ascii=False, indent=2))
        raise SystemExit("ERROR: el control falló; no se cronometra:\n  " + "\n  ".join(fallos))

    # ---- cronómetro ----
    tiempos = {}
    for m in MODELOS:
        segundos, primeras, iguales = [], None, True
        for _ in range(args.repeticiones):
            t0 = time.perf_counter()
            s = puntuar(m, filas, ctx)
            segundos.append(time.perf_counter() - t0)
            primeras = s if primeras is None else primeras
            iguales &= bool(np.array_equal(s, primeras))
        por_mil = [t / len(filas) * 1000 for t in segundos]
        tiempos[m] = {"segundos_por_repeticion": [round(t, 3) for t in segundos],
                      "segundos_por_1000_lesiones": [round(t, 4) for t in por_mil],
                      "mediana_segundos_por_1000_lesiones": round(float(np.median(por_mil)), 4),
                      "puntuaciones_identicas_en_las_repeticiones": iguales}
        print(f"{m}: mediana {tiempos[m]['mediana_segundos_por_1000_lesiones']} s por 1.000 lesiones", flush=True)

    resultado = {
        "especificacion": "PLAN.md, Fase 4, «Tiempo de inferencia», fijada el 2026-09-26 antes de medir",
        "datos": datos,
        "subconjunto": {"semilla": SEMILLA_SUBCONJUNTO, "minimo_de_lesiones": args.minimo_lesiones,
                        "orden": "patient_id de desarrollo ordenados, permutados con numpy.random.default_rng(7)",
                        "pacientes": elegidos, "n_pacientes": len(elegidos), "n_lesiones": int(len(filas))},
        "entrenamiento": {"pacientes": int(pd.Series(grupos[tr]).nunique()), "lesiones": int(len(tr)),
                          "semilla": SEMILLA, "no_se_cronometra": True,
                          "m3limpio_variables": inv3["n_variables"], "m3limpio_arboles": int(modelo3.tree_count_)},
        "caracteristicas_de_imagen": comprobacion_imagen,
        "control": control,
        "tiempos": tiempos,
        "repeticiones": args.repeticiones,
        "es_la_corrida_de_la_especificacion": (args.minimo_lesiones == MINIMO_DE_LESIONES
                                               and args.repeticiones == REPETICIONES),
        "que_se_cronometra": ("desde las filas de metadatos del subconjunto, en memoria y sin la etiqueta (y en M4 y "
                              "M4b desde las imágenes de data/train-image.hdf5) hasta la puntuación de cada lesión; "
                              "fuera, la carga de los modelos y de los pesos de DINOv2"),
        "declaraciones": declaraciones(ctx),
        "segundos": {"entrenamiento": round(t_entrenamiento, 1), "control": round(t_control, 1),
                     "total": round(time.perf_counter() - t_total, 1)},
        "nota": "Los tiempos solo comparan estos modelos entre sí. Son tiempos de pared, en el mismo proceso.",
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    dec = resultado["declaraciones"]
    ig = control["igualdad"]
    n_pasos = sum(len(v) for v in control["pasos_quitados"].values())
    nombres = {"M1": "M1", "M2": "M2", "M3limpio": "M3 limpio", "M4": "M4", "M4b": "M4b"}
    lineas = [
        "# Tiempo de inferencia — Fase 4, conjunto de desarrollo",
        f"Subconjunto: {len(elegidos)} pacientes completos, {len(filas)} lesiones (semilla 7) · entrenamiento: "
        f"{resultado['entrenamiento']['pacientes']} pacientes, semilla 0, sin cronometrar",
        f"Control: M1, M2 y M3 limpio idénticos al camino normal · M4 y M4b: DINOv2 a {dif_dinov2:.1e} del archivo "
        f"(tolerancia {TOLERANCIA_DINOV2}), idénticos con las variables del archivo; con las recalculadas, diferencia "
        f"máxima {ig['M4']['c_puntuacion_diferencia_maxima_con_las_recalculadas']:.1e} (M4) y "
        f"{ig['M4b']['c_puntuacion_diferencia_maxima_con_las_recalculadas']:.1e} (M4b) · "
        f"{n_pasos} de {n_pasos} pasos quitados detectados",
    ]
    imputacion = {m: r.get("imputacion") or r.get("imputacion_edad") for m, r in control["pasos_quitados"].items()}
    con_error = [nombres[m] for m, v in imputacion.items() if v.get("error")]
    sin_cambio = [nombres[m] for m, v in imputacion.items() if v.get("puntuaciones_distintas") is False]
    lineas.append("Imputación quitada: la matriz que entra al modelo cambia en "
                  + ", ".join(nombres[m] for m, v in imputacion.items() if v.get("matriz_distinta"))
                  + (f"; en {', '.join(con_error)} el camino no llega a formarla (el LOF no acepta NaN)" if con_error else "")
                  + (f" · puntuaciones sin cambio en {', '.join(sin_cambio)}: ese paso lo cubren las matrices"
                     if sin_cambio else " · las puntuaciones cambian en todos"))
    for m in MODELOS:
        t = tiempos[m]
        lineas.append(f"{nombres[m]}: mediana {t['mediana_segundos_por_1000_lesiones']} s por 1.000 lesiones · "
                      f"las cinco: {t['segundos_por_1000_lesiones']}")
    lineas += [
        f"Equipo: {dec['equipo']['chip']}, {dec['equipo']['nucleos']} núcleos, {dec['equipo']['memoria_gb']:.0f} GB · "
        f"macOS {dec['sistema']['macos']} · Python {dec['interprete']['python']} · DINOv2 en "
        f"{dec['dinov2']['dispositivo']}, lote {LOTE} · hilos: torch {dec['hilos']['torch_cpu']}, OpenMP "
        f"{dec['hilos']['openmp_scikit_learn']}, CatBoost por defecto",
        "Desde los metadatos (y las imágenes en M4 y M4b) hasta la puntuación; sin cargar modelos ni pesos.",
        "Los tiempos solo comparan estos modelos entre sí.",
        f"Detalle, versiones y lista de pacientes: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    main()

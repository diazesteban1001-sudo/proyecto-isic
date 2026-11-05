#!/usr/bin/env python3
"""
fase5.py — la Fase 5 de PLAN.md: abrir el conjunto reservado, una sola vez.

Especificación: PLAN.md, Fase 5, fijada por la persona el 2026-09-26 y ampliada
el 2026-11-02, antes de abrir el reservado. Se entrenan una sola vez sobre los
pacientes de desarrollo, con semilla 0:
  - M3 limpio, el modelo recomendado y el resultado principal (ganador_m3.py),
    con la parada temprana sobre el 20 % interno, agrupado por paciente;
  - M2, de referencia (el de fase4_comparar.py);
  - la red de la 4e, con su receta y su ajuste fino (fase4e.entrenar_y_puntuar
    y fase4e_ajuste.ajustar_y_puntuar), como resultado descriptivo;
  - «Imagen + básicos» (imagen_sola.py), como resultado descriptivo.
Todo lo que se ajusta se ajusta con el entrenamiento y se aplica a la
evaluación; lo que se calcula dentro del paciente se calcula a cada lado con
sus propias filas. Métricas: pAUC, AUC, SEtop-15 y NNT80% SE
(fase4_comparar.medir). Intervalos: bootstrap por paciente sobre la evaluación,
REMUESTRAS remuestras con semilla SEMILLA_BOOTSTRAP, percentiles 2,5 y 97,5 de
numpy.percentile, con su interpolación lineal por defecto. Las mismas remuestras
sirven para los cuatro modelos y para la diferencia M3 limpio − M2. Un paciente
que sale dos veces en una remuestra cuenta como dos pacientes en SEtop-15.

Dos modos, con el mismo código de punta a punta:
  --modo ensayo    el pliegue 0 de la semilla 0 del desarrollo hace de reservado
                   de mentira, y los otros cuatro, de desarrollo. No lee el
                   reservado. Como son los pliegues de la Fase 4, cada modelo
                   tiene que reproducir lo que ya dio en ese pliegue:
                     - M2 y M3 limpio, sus puntuaciones de
                       data/fase4b-predicciones-m3limpio-m2.csv.gz;
                     - la red, los pesos de data/fase4e-redes/s0-p0.pt y el
                       logit ajustado de data/fase4e-ajuste/s0-p0.npz;
                     - los cuatro, sus métricas de ese pliegue en outputs/, a 4
                       decimales.
                   Cada comprobación tiene su caso que debe fallar.
  --modo apertura  el reservado. Se niega a correr si falta el ensayo completo
                   con este mismo código, o si el código o el ensayo no están en
                   el último commit.

En los dos modos se niega a correr, antes de leer nada, si ya existe la salida
del reservado (outputs/fase5-reservado.json o .md) o la marca de que la
apertura empezó (data/fase5-apertura-iniciada.json). La marca se escribe antes
de leer el reservado, para que una apertura que se corte no se repita sin que
la persona lo decida.

Las etiquetas de la evaluación no se leen hasta que las cuatro puntuaciones
están escritas en data/: la evaluación se carga sin la columna de la etiqueta,
y la etiqueta se lee después del CSV, con etiquetas_de().

No interpreta: mide y escribe outputs/fase5-ensayo o outputs/fase5-reservado,
.json y .md. Las puntuaciones y las métricas de cada remuestra van a data/, que
no se versiona, con su SHA-256 en la salida. El control es test_fase5.py.

Uso (con caffeinate, en segundo plano):
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5.py --modo ensayo
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5.py --modo apertura
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import ganador_m3  # noqa: E402
import imagen_sola  # noqa: E402
from contexto_paciente import variables_contexto_paciente  # noqa: E402
from datos_desarrollo import cargar_desarrollo, exigir_sin_reservados, leer_reservados  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds, preparar_features  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

RAIZ = ganador_m3.RAIZ
G, Y = "patient_id", "target"
SEMILLA = 0
N_SPLITS = 5
PLIEGUE_DEL_ENSAYO = 0
REMUESTRAS = 2000
SEMILLA_BOOTSTRAP = 2026
PERCENTILES = (2.5, 97.5)
MODOS = ("ensayo", "apertura")
MODELOS = ("M3limpio", "M2", "Red4e", "ImagenBasicos")
NOMBRES = {"M3limpio": "M3 limpio", "M2": "M2", "Red4e": "red de la 4e", "ImagenBasicos": "«Imagen + básicos»"}
PAPEL = {"M3limpio": "principal", "M2": "referencia", "Red4e": "descriptivo", "ImagenBasicos": "descriptivo"}
DESCRIPCION = {
    "M3limpio": f4.DESCRIPCION["M3limpio"] + "; semilla 0, parada sobre el 20 % interno del entrenamiento",
    "M2": f4.DESCRIPCION["M2"] + "; HistGradientBoostingClassifier(class_weight='balanced', random_state=0)",
    "Red4e": ("EfficientNet-B0 con la receta de la Fase 4e y su ajuste fino con pAUC_CVaR_Loss (fase4e.py y "
              "fase4e_ajuste.py), semilla 0; solo la imagen; la puntuación es la sigmoide del logit en float64"),
    "ImagenBasicos": ("modelo_imagen() de apilado_imagen.py sobre las 384 variables de DINOv2 más age_approx, sex y "
                      "anatom_site_general (codificar_fold), estandarizadas juntas, como en imagen_sola.py"),
}
CODIGO = ["fase5.py", "fase4_comparar.py", "ganador_m3.py", "contexto_paciente.py", "train_and_evaluate.py",
          "evaluar_repetido.py", "metricas_triaje.py", "apilado_imagen.py", "imagen_sola.py", "fase4c.py",
          "fase4c_redes.py", "fase4e.py", "fase4e_ajuste.py", "fase4e_redes.py", "prueba_tiempo_red_imagen.py",
          os.path.join("..", "..", "diseno-validacion", "scripts", "datos_desarrollo.py")]


def rutas(raiz):
    def r(*p):
        return os.path.join(raiz, *p)
    return {
        "raiz": raiz,
        "csv": r("data", "train-metadata.csv"),
        "hdf5": r("data", "train-image.hdf5"),
        "holdout": r("outputs", "holdout-pacientes.json"),
        "fugas": r("outputs", "auditoria-de-fugas.json"),
        "extraccion": r("outputs", "extraccion-imagen.json"),
        "dinov2_desarrollo": r("data", "dinov2-vits14-desarrollo.h5"),
        "dinov2_reservado": r("data", "dinov2-vits14-reservado.h5"),
        "controles_4e": r("data", "fase4e-controles.json"),
        "prueba_tiempo_4e": r("outputs", "prueba-tiempo-red-4e.json"),
        "ref_pliegues": r("outputs", "fase4-m2-vs-m1.json"),
        "ref_m3limpio": r("outputs", "fase4-m3limpio-vs-m2.json"),
        "ref_imagen_sola": r("outputs", "imagen-sola.json"),
        "ref_red": r("outputs", "fase4e-exploracion.json"),
        "pred_fase4b": r("data", "fase4b-predicciones-m3limpio-m2.csv.gz"),
        "red_base_ref": r("data", "fase4e-redes", f"s{SEMILLA}-p{PLIEGUE_DEL_ENSAYO}"),
        "red_base_otra": r("data", "fase4e-redes", f"s{SEMILLA}-p{PLIEGUE_DEL_ENSAYO + 1}"),
        "red_ajuste_ref": r("data", "fase4e-ajuste", f"s{SEMILLA}-p{PLIEGUE_DEL_ENSAYO}"),
        "salida": {"ensayo": r("outputs", "fase5-ensayo"), "apertura": r("outputs", "fase5-reservado")},
        "datos": {"ensayo": r("data", "fase5-ensayo"), "apertura": r("data", "fase5-reservado")},
        "marca": r("data", "fase5-apertura-iniciada.json"),
    }


def sha256(ruta):
    return f4.sha256(ruta)


def huella_codigo():
    return {os.path.basename(c): sha256(os.path.normpath(os.path.join(AQUI, c))) for c in CODIGO}


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def rel(ruta, raiz):
    return os.path.relpath(ruta, raiz)


# ---- las negativas a correr ---------------------------------------------------------------

def negarse_si_ya_se_abrio(r):
    """Antes de leer nada: si existe la salida del reservado o la marca de la apertura."""
    salida = r["salida"]["apertura"]
    for ruta in (salida + ".json", salida + ".md", r["marca"]):
        if os.path.exists(ruta):
            raise SystemExit(f"ERROR: ya existe {rel(ruta, r['raiz'])}. El reservado se abre una sola vez; "
                             "este programa no vuelve a correr.")


def exigir_apertura(modo, que):
    if modo != "apertura":
        raise SystemExit(f"ERROR: el modo {modo!r} no lee el reservado ({que}); solo lo lee la apertura.")


def comprobar_ensayo(r, codigo):
    """El ensayo completo, con todos sus controles bien y con este mismo código."""
    ruta = r["salida"]["ensayo"] + ".json"
    if not os.path.exists(ruta) or not os.path.exists(r["salida"]["ensayo"] + ".md"):
        raise SystemExit(f"ERROR: falta {rel(ruta, r['raiz'])} o su .md. La apertura corre después de un ensayo "
                         "completo.")
    with open(ruta, encoding="utf-8") as f:
        e = json.load(f)
    if e.get("modo") != "ensayo" or not e.get("completo") or e.get("controles", {}).get("fallos") != 0:
        raise SystemExit(f"ERROR: {rel(ruta, r['raiz'])} no es un ensayo completo con 0 controles fallidos.")
    if e.get("sha256_del_codigo") != codigo:
        distintos = sorted(k for k in set(codigo) | set(e.get("sha256_del_codigo", {}))
                           if codigo.get(k) != e.get("sha256_del_codigo", {}).get(k))
        raise SystemExit(f"ERROR: el ensayo se corrió con otro código ({distintos}); hay que repetir el ensayo.")
    return {"archivo": rel(ruta, r["raiz"]), "sha256": sha256(ruta), "completo": True,
            "controles": e["controles"]["de_casos"], "mismo_codigo": True}


def exigir_versionado(raiz, archivos):
    """Que cada archivo esté versionado y sea idéntico al del último commit."""
    for a in archivos:
        if subprocess.run(["git", "-C", raiz, "ls-files", "--error-unmatch", a], capture_output=True).returncode:
            raise SystemExit(f"ERROR: {a} no está versionado; la apertura corre con el código y el ensayo en un "
                             "commit anterior.")
    if subprocess.run(["git", "-C", raiz, "diff", "--quiet", "HEAD", "--", *archivos]).returncode:
        raise SystemExit("ERROR: el código o el ensayo tienen cambios sin commit; la apertura corre con lo que está "
                         "en el último commit.")


# ---- los datos ----------------------------------------------------------------------------

def cargar_reservado_sin_etiqueta(csv, holdout, modo):
    """Las filas de los pacientes reservados, sin la columna de la etiqueta."""
    exigir_apertura(modo, "sus filas")
    reservados = leer_reservados(holdout)
    df = pd.read_csv(csv, usecols=lambda c: c != Y, low_memory=False)
    df = df[df[G].astype(str).isin(reservados)].reset_index(drop=True)
    if set(df[G].astype(str)) != reservados:
        raise SystemExit("ERROR: las filas leídas no son exactamente las de los pacientes reservados.")
    return df


def cargar_caracteristicas_reservado(df_eval, ruta_h5, extraccion, modo):
    """Las variables de DINOv2 del reservado, alineadas por isic_id con df_eval, con
    las comprobaciones de fase4_comparar.cargar_imagen: el atributo del archivo, su
    SHA-256 frente al de la extracción, ningún isic_id de más ni de menos, todas
    decodificadas y ningún NaN tras alinear."""
    exigir_apertura(modo, "sus características de imagen")
    import h5py
    with h5py.File(ruta_h5, "r") as f:
        conjunto = f.attrs.get("conjunto")
        if conjunto != "reservado":
            raise SystemExit(f"ERROR: {ruta_h5} declara el conjunto {conjunto!r}, no 'reservado'.")
        ids = f["isic_id"].asstr()[:]
        cls = f["cls"][:]
        decodificada = f["decodificada"][:]
    with open(extraccion, encoding="utf-8") as f:
        esperado = json.load(f)["conjuntos"]["reservado"]["archivo"]["sha256"]
    tabla = pd.DataFrame(cls, index=pd.Index(ids, name="isic_id"), columns=[f"dinov2_{i:03d}" for i in range(cls.shape[1])])
    alineada = tabla.reindex(df_eval["isic_id"].to_numpy())
    comprobaciones = {
        "archivo": ruta_h5, "sha256": sha256(ruta_h5), "isic_id_en_datos": int(df_eval["isic_id"].nunique()),
        "isic_id_en_archivo": int(len(set(ids))),
        "en_datos_sin_caracteristicas": len(set(df_eval["isic_id"]) - set(ids)),
        "en_archivo_sin_fila_en_datos": len(set(ids) - set(df_eval["isic_id"])),
        "imagenes_no_decodificadas": int((~decodificada).sum()), "nan_tras_alinear": int(alineada.isna().to_numpy().sum()),
    }
    comprobaciones["sha256_igual_al_de_la_extraccion"] = comprobaciones["sha256"] == esperado
    if any(comprobaciones[k] for k in ("en_datos_sin_caracteristicas", "en_archivo_sin_fila_en_datos",
                                        "imagenes_no_decodificadas", "nan_tras_alinear")) \
            or not comprobaciones["sha256_igual_al_de_la_extraccion"]:
        raise SystemExit(f"ERROR: las características del reservado no se alinean con los datos: {comprobaciones}")
    return alineada.to_numpy(), comprobaciones


def etiquetas_de(csv, ids, modo, holdout):
    """Las etiquetas de las filas de evaluación, leídas del CSV por isic_id, en el
    orden de ids. Se llama solo cuando las puntuaciones ya están escritas. En el
    ensayo, ninguna puede ser de un paciente reservado; en la apertura, todas."""
    t = pd.read_csv(csv, usecols=["isic_id", G, Y], low_memory=False).set_index("isic_id")
    filas = t.reindex(pd.Index(ids))
    if filas[Y].isna().any():
        raise SystemExit("ERROR: hay filas de evaluación sin etiqueta en el CSV.")
    reservados = leer_reservados(holdout)
    if modo == "ensayo":
        exigir_sin_reservados(filas.reset_index(), reservados, G, "la evaluación del ensayo")
    elif not set(filas[G].astype(str)) <= reservados:
        raise SystemExit("ERROR: la evaluación de la apertura tiene filas de pacientes no reservados.")
    return filas[Y].to_numpy().astype(np.int64)


def exigir_disjuntos(g_ent, g_eval):
    comunes = sorted(set(map(str, g_ent)) & set(map(str, g_eval)))
    if comunes:
        raise SystemExit(f"ERROR: {len(comunes)} pacientes están en el entrenamiento y en la evaluación "
                         f"(p. ej. {comunes[:3]}).")


# ---- los cuatro modelos -------------------------------------------------------------------

def unir(df_ent, df_eval):
    """Entrenamiento (con la etiqueta) y evaluación (sin ella) en un solo DataFrame,
    con el entrenamiento primero y en su orden: (unido, tr, va). La etiqueta de la
    evaluación queda vacía."""
    if Y in df_eval.columns:
        raise SystemExit("ERROR: la evaluación llega con la etiqueta; se lee después de puntuar.")
    unido = pd.concat([df_ent, df_eval], ignore_index=True)
    tr, va = np.arange(len(df_ent)), np.arange(len(df_ent), len(unido))
    if unido[Y].iloc[va].notna().any():
        raise SystemExit("ERROR: la evaluación tiene etiquetas en el DataFrame unido.")
    return unido, tr, va


def puntuar_tabulares(df_ent, df_eval, x_img_ent, x_img_eval, numericas, categoricas, excluidas):
    """M2, M3 limpio e «Imagen + básicos», entrenados con df_ent y puntuando df_eval."""
    y_ent = df_ent[Y].to_numpy()
    g_ent = df_ent[G].to_numpy()
    segundos, info = {}, {}
    crudo, tr, va = unir(df_ent, df_eval)

    t0 = time.perf_counter()
    ctx_ent = variables_contexto_paciente(df_ent.drop(columns=[Y]), numericas, G)
    ctx_eval = variables_contexto_paciente(df_eval, numericas, G)
    con_ctx, _, _ = unir(pd.concat([df_ent, ctx_ent], axis=1), pd.concat([df_eval, ctx_eval], axis=1))
    x_tr, x_va = codificar_fold(con_ctx, numericas + list(ctx_ent.columns), categoricas, Y, tr, va)
    m2 = HistGradientBoostingClassifier(random_state=SEMILLA, class_weight="balanced").fit(x_tr, y_ent)
    p_m2 = m2.predict_proba(x_va)[:, 1]
    segundos["M2"] = round(time.perf_counter() - t0, 1)
    info["M2"] = {"n_variables": int(x_tr.shape[1])}

    t0 = time.perf_counter()
    x3_tr, x3_va, cats3, inv3 = ganador_m3.variables_m3_en_pliegue(crudo.drop(columns=[Y]), tr, va, excluidas, G)
    m3 = ganador_m3.ajustar_m3(x3_tr, y_ent, g_ent, cats3, SEMILLA, parametros=ganador_m3.PARAMETROS_LIMPIO)
    p_m3 = m3.predict_proba(x3_va)[:, 1]
    segundos["M3limpio"] = round(time.perf_counter() - t0, 1)
    info["M3limpio"] = {"n_variables": inv3["n_variables"], "arboles": int(m3.tree_count_),
                        "iteraciones_corridas": len(m3.get_evals_result()["validation"]["AUC"])}

    t0 = time.perf_counter()
    b_tr, b_va = codificar_fold(crudo, imagen_sola.BASICOS_NUMERICAS, imagen_sola.BASICOS_CATEGORICAS, Y, tr, va)
    p_ib, avisos = imagen_sola._ajustar_imagen(np.hstack([x_img_ent, b_tr]), y_ent, np.hstack([x_img_eval, b_va]))
    segundos["ImagenBasicos"] = round(time.perf_counter() - t0, 1)
    info["ImagenBasicos"] = {"n_variables": int(x_img_ent.shape[1] + b_tr.shape[1]), "avisos_no_convergencia": avisos}
    return {"M2": p_m2, "M3limpio": p_m3, "ImagenBasicos": p_ib}, info, segundos


def comprobar_red_antes(r):
    """La receta cronometrada y los controles completos de la 4e, como fase4e_redes.py."""
    import fase4c_redes as f4cr
    import fase4e_redes
    with open(r["prueba_tiempo_4e"], encoding="utf-8") as f:
        diferencias = fase4e_redes.comprobar_receta(json.load(f))
    if diferencias:
        raise SystemExit(f"ERROR: la receta no es la de {rel(r['prueba_tiempo_4e'], r['raiz'])}: {diferencias}")
    return f4cr.leer_controles(r["controles_4e"])


def puntuar_red(r, df_ent, df_eval, dispositivo, dir_datos):
    """La red de la 4e entrenada con df_ent y ajustada, puntuando df_eval: (logit,
    registro). Las etiquetas de la evaluación entran como −1 y nunca se leen: las dos
    funciones solo leen las de filas_ent."""
    import fase4e
    import fase4e_ajuste
    isic = np.concatenate([df_ent["isic_id"].to_numpy(), df_eval["isic_id"].to_numpy()])
    etiquetas = np.concatenate([df_ent[Y].to_numpy().astype(np.int64), np.full(len(df_eval), -1, dtype=np.int64)])
    tr, va = np.arange(len(df_ent)), np.arange(len(df_ent), len(isic))
    if (etiquetas[va] != -1).any():
        raise SystemExit("ERROR: la red recibiría etiquetas de la evaluación.")
    pesos = os.path.join(dir_datos, "red-base.pt")
    t0 = time.perf_counter()
    _, base = fase4e.entrenar_y_puntuar(r["hdf5"], isic, etiquetas, tr, va, SEMILLA, dispositivo, pesos_en=pesos,
                                        predecir_filas=False)
    s_base = round(time.perf_counter() - t0, 1)
    if base["negativos"] != "conjuntos" or base["negativos_en_mas_de_una_epoca"] != 0 \
            or base["epocas"] != fase4e.EPOCAS or base["epocas_corridas"] != fase4e.EPOCAS \
            or base["conjuntos"] != fase4e.CONJUNTOS or sha256(pesos) != base["sha256_pesos_guardados"]:
        raise SystemExit(f"ERROR: la red no corrió sus {fase4e.EPOCAS} épocas con un conjunto de negativos distinto "
                         "en cada una, o sus pesos no son los guardados.")
    t0 = time.perf_counter()
    logit, ajuste = fase4e_ajuste.ajustar_y_puntuar(r["hdf5"], isic, etiquetas, tr, va, SEMILLA, dispositivo, pesos)
    s_ajuste = round(time.perf_counter() - t0, 1)
    if ajuste["lotes_corridos"] != ajuste["lotes_por_epoca"] or ajuste["sha256_pesos_de_partida"] != sha256(pesos):
        raise SystemExit("ERROR: el ajuste fino no partió de los pesos de la red o no corrió todos sus lotes.")
    with open(os.path.join(dir_datos, "red.json"), "w", encoding="utf-8") as f:
        json.dump({"base": base, "ajuste": ajuste}, f, ensure_ascii=False, indent=2)
    resumen = {"epocas": base["epocas_corridas"], "negativos_en_mas_de_una_epoca": base["negativos_en_mas_de_una_epoca"],
               "positivos": base["positivos"], "lotes_del_ajuste_corridos": ajuste["lotes_corridos"],
               "pesos_base": rel(pesos, r["raiz"]), "sha256_pesos_base": base["sha256_pesos_guardados"],
               "registro_completo": rel(os.path.join(dir_datos, "red.json"), r["raiz"])}
    return np.asarray(logit, dtype=np.float64), resumen, {"Red4e_entrenamiento": s_base,
                                                          "Red4e_ajuste_y_prediccion": s_ajuste}


# ---- el bootstrap por paciente ------------------------------------------------------------

def remuestras_por_paciente(grupos, n_remuestras, semilla):
    """Los pacientes de la evaluación, ordenados, y una matriz de sorteos: en la fila
    b, los índices (con repetición) de los pacientes de la remuestra b."""
    pacientes = np.array(sorted(pd.unique(pd.Series(grupos).astype(str))))
    sorteos = np.random.default_rng(semilla).integers(0, len(pacientes), size=(n_remuestras, len(pacientes)))
    return pacientes, sorteos


def posiciones_por_paciente(grupos, pacientes):
    indices = pd.Series(np.arange(len(grupos))).groupby(pd.Series(grupos).astype(str).to_numpy()).indices
    return [np.asarray(indices[p]) for p in pacientes]


def filas_de_la_remuestra(posiciones, sorteo):
    """Las filas de una remuestra y su grupo: cada sorteo es un grupo nuevo, así que un
    paciente que sale dos veces cuenta como dos pacientes."""
    filas = np.concatenate([posiciones[j] for j in sorteo])
    grupo = np.repeat(np.arange(len(sorteo)), [len(posiciones[j]) for j in sorteo])
    return filas, grupo


def es_remuestra_por_paciente(filas, sorteo, posiciones):
    """Que cada fila de cada paciente aparece tantas veces como salió su paciente, y
    ninguna de un paciente que no salió."""
    veces_fila = np.bincount(filas, minlength=sum(len(p) for p in posiciones))
    veces_paciente = np.bincount(sorteo, minlength=len(posiciones))
    return all(np.all(veces_fila[p] == veces_paciente[j]) for j, p in enumerate(posiciones))


def bootstrap(y, puntuaciones, grupos, n_remuestras=REMUESTRAS, semilla=SEMILLA_BOOTSTRAP):
    """Las cuatro métricas de cada modelo en cada remuestra: {modelo: {métrica:
    array}}, con las mismas remuestras para todos. Se detiene si una remuestra no
    tiene las dos clases."""
    pacientes, sorteos = remuestras_por_paciente(grupos, n_remuestras, semilla)
    posiciones = posiciones_por_paciente(grupos, pacientes)
    valores = {m: {k: np.empty(n_remuestras) for k in f4.METRICAS} for m in puntuaciones}
    for b in range(n_remuestras):
        filas, grupo = filas_de_la_remuestra(posiciones, sorteos[b])
        yb = y[filas]
        if yb.min() == yb.max():
            raise SystemExit(f"ERROR: la remuestra {b} tiene una sola clase; las métricas no están definidas.")
        for m, s in puntuaciones.items():
            for k, v in f4.medir(yb, s[filas], grupo).items():
                valores[m][k][b] = v
    return pacientes, sorteos, posiciones, valores


def intervalo(v):
    lo, hi = np.percentile(v, PERCENTILES)
    return [round(float(lo), 4), round(float(hi), 4)]


def resumir(puntos, valores):
    metricas = {m: {k: {"punto": round(puntos[m][k], 4), "intervalo_95": intervalo(valores[m][k])}
                    for k in f4.METRICAS} for m in puntos}
    diferencia = {}
    for k in f4.METRICAS:
        d = valores["M3limpio"][k] - valores["M2"][k]
        iv = intervalo(d)
        diferencia[k] = {"punto": round(puntos["M3limpio"][k] - puntos["M2"][k], 4), "intervalo_95": iv,
                         "intervalo_entero_por_debajo_de_cero": bool(np.percentile(d, PERCENTILES[1]) < 0)}
    return metricas, diferencia


# ---- controles ----------------------------------------------------------------------------

def caso(control, que, ok, debe_fallar, detalle):
    return {"control": control, "caso": que, "ok": bool(ok), "debe_fallar": bool(debe_fallar), "detalle": detalle}


def metricas_de_referencia(r):
    """Las métricas del pliegue 0 y del pliegue 1 de la semilla 0 en la Fase 4 y la 4e,
    por modelo: {modelo: {pliegue: {métrica: valor}}}."""
    def leer(ruta):
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    s = str(SEMILLA)
    m2 = leer(r["ref_pliegues"])["metricas"]["M2"]
    m3 = leer(r["ref_m3limpio"])["metricas"]["M3limpio"]
    ib = leer(r["ref_imagen_sola"])["metricas"]["Imagen + básicos"]
    p2 = leer(r["ref_red"])["paso_2"]
    if p2.get("semilla") != SEMILLA or p2.get("nuevo") != "Red4eAjustada":
        raise SystemExit(f"ERROR: {rel(r['ref_red'], r['raiz'])} no es el paso 2 de la semilla 0 con la red ajustada.")
    red = {"pauc": p2["pauc_por_pliegue"]["Red4eAjustada"],
           **{k: p2["otras_metricas"][k]["Red4eAjustada"] for k in ("auc", "setop15", "nnt80")}}
    salida = {}
    for p in (PLIEGUE_DEL_ENSAYO, PLIEGUE_DEL_ENSAYO + 1):
        salida.setdefault("M2", {})[p] = {k: m2[k]["por_semilla_y_fold"][s][p] for k in f4.METRICAS}
        salida.setdefault("M3limpio", {})[p] = {k: m3[k]["por_semilla_y_fold"][s][p] for k in f4.METRICAS}
        salida.setdefault("ImagenBasicos", {})[p] = {k: ib[k]["por_semilla_y_fold"][s][p] for k in f4.METRICAS}
        salida.setdefault("Red4e", {})[p] = {k: red[k][p] for k in f4.METRICAS}
    return salida


def misma_metrica(obtenidas, referencia):
    return all(round(obtenidas[k], 4) == referencia[k] for k in f4.METRICAS)


def leer_pred_fase4b(r):
    with open(os.path.splitext(os.path.splitext(r["pred_fase4b"])[0])[0] + ".json", encoding="utf-8") as f:
        proc = json.load(f)
    if sha256(r["pred_fase4b"]) != proc["sha256"]:
        raise SystemExit(f"ERROR: {rel(r['pred_fase4b'], r['raiz'])} no tiene el SHA-256 de su procedencia.")
    t = pd.read_csv(r["pred_fase4b"], float_precision="round_trip")
    t = t[(t["semilla"] == SEMILLA) & (t["pliegue"] == PLIEGUE_DEL_ENSAYO)]
    return {m: t[t["modelo"] == m].set_index("isic_id")["puntuacion"] for m in ("M2", "M3limpio")}


def leer_parte(base):
    """El .npz de una parte de la 4e, comprobado contra el SHA-256 de su .json."""
    with open(base + ".json", encoding="utf-8") as f:
        reg = json.load(f)
    if sha256(base + ".npz") != reg["sha256_npz"]:
        raise SystemExit(f"ERROR: {base}.npz no tiene el SHA-256 de su parte.")
    z = np.load(base + ".npz")
    return z["isic_id"], z["logit"].astype(np.float64), reg


def pesos_iguales(a, b):
    import torch
    x, y = torch.load(a, map_location="cpu"), torch.load(b, map_location="cpu")
    return set(x) == set(y) and all(torch.equal(x[k], y[k]) for k in x)


def controles_del_ensayo(r, ids_eval, puntuaciones, logit_red, pesos_base, obtenidas, huella, huella_otra, ref_huella):
    """Que cada modelo reproduce su pliegue de la Fase 4 y la 4e, con un caso que
    debe fallar por comprobación."""
    casos = [
        caso("pliegues", "los pliegues de la semilla 0 tienen la huella de fase4-m2-vs-m1.json", huella == ref_huella,
             False, f"{huella[:12]}…"),
        caso("pliegues", "los pliegues de la semilla 1 frente a esa huella", huella_otra != ref_huella, True,
             f"iguales: {huella_otra == ref_huella}"),
    ]
    pred = leer_pred_fase4b(r)
    for m in ("M2", "M3limpio"):
        ref = pred[m].reindex(ids_eval).to_numpy()
        iguales = bool(np.array_equal(puntuaciones[m], ref))
        casos.append(caso("reproduccion", f"{NOMBRES[m]}: las puntuaciones de data/fase4b-predicciones, semilla 0, "
                          "pliegue 0", iguales, False, f"idénticas: {iguales}"))
    otra = pred["M3limpio"].reindex(ids_eval).to_numpy()
    casos.append(caso("reproduccion", "M2 frente a las puntuaciones de M3 limpio", not np.array_equal(puntuaciones["M2"],
                      otra), True, f"idénticas: {bool(np.array_equal(puntuaciones['M2'], otra))}"))
    with open(r["red_base_ref"] + ".json", encoding="utf-8") as f:
        sha_ref = json.load(f)["sha256_pesos_guardados"]
    if sha256(r["red_base_ref"] + ".pt") != sha_ref:
        raise SystemExit(f"ERROR: {r['red_base_ref']}.pt no tiene el SHA-256 de su parte.")
    iguales = pesos_iguales(pesos_base, r["red_base_ref"] + ".pt")
    casos.append(caso("reproduccion", "red de la 4e: los pesos de data/fase4e-redes/s0-p0.pt, tensor a tensor",
                      iguales, False, f"idénticos: {iguales}"))
    otros = pesos_iguales(pesos_base, r["red_base_otra"] + ".pt")
    casos.append(caso("reproduccion", "red de la 4e: los pesos de s0-p1.pt", not otros, True, f"idénticos: {otros}"))
    ids_ref, logit_ref, _ = leer_parte(r["red_ajuste_ref"])
    iguales = list(ids_ref) == list(ids_eval) and bool(np.array_equal(logit_red, logit_ref))
    casos.append(caso("reproduccion", "red de la 4e: el logit ajustado de data/fase4e-ajuste/s0-p0.npz", iguales,
                      False, f"mismo orden e idénticos: {iguales}"))
    ids_base, logit_base, _ = leer_parte(r["red_base_ref"])
    sin_ajuste = list(ids_base) == list(ids_eval) and bool(np.array_equal(logit_red, logit_base))
    casos.append(caso("reproduccion", "red de la 4e: el logit de la red sin ajustar, s0-p0.npz de fase4e-redes",
                      not sin_ajuste, True, f"idénticos: {sin_ajuste}"))
    ref = metricas_de_referencia(r)
    for m in MODELOS:
        bien = misma_metrica(obtenidas[m], ref[m][PLIEGUE_DEL_ENSAYO])
        casos.append(caso("reproduccion", f"{NOMBRES[m]}: las cuatro métricas de su pliegue 0, a 4 decimales", bien,
                          False, {k: round(obtenidas[m][k], 4) for k in f4.METRICAS}))
        otra = misma_metrica(obtenidas[m], ref[m][PLIEGUE_DEL_ENSAYO + 1])
        casos.append(caso("reproduccion", f"{NOMBRES[m]}: frente a las de su pliegue 1", not otra, True,
                          f"iguales: {otra}"))
    return casos


def controles_comunes(g_ent, g_eval, puntuaciones, y, grupos, posiciones, sorteos):
    casos = []
    try:
        exigir_disjuntos(g_ent, g_eval)
        casos.append(caso("pacientes", "ningún paciente en el entrenamiento y en la evaluación", True, False, "0"))
    except SystemExit as e:
        casos.append(caso("pacientes", "ningún paciente en el entrenamiento y en la evaluación", False, False, str(e)))
    try:
        exigir_disjuntos(np.append(np.asarray(g_ent, dtype=object), str(g_eval[0])), g_eval)
        casos.append(caso("pacientes", "con un paciente de la evaluación añadido al entrenamiento", False, True,
                          "no se detecta"))
    except SystemExit as e:
        casos.append(caso("pacientes", "con un paciente de la evaluación añadido al entrenamiento", True, True, str(e)))
    finitas = all(len(s) == len(y) and np.all(np.isfinite(s)) for s in puntuaciones.values())
    casos.append(caso("puntuaciones", "una puntuación finita por fila de evaluación en los cuatro modelos", finitas,
                      False, {m: int(len(s)) for m, s in puntuaciones.items()}))
    con_nan = np.array(puntuaciones["M3limpio"], dtype=float)
    con_nan[0] = np.nan
    casos.append(caso("puntuaciones", "con un NaN en M3 limpio", not np.all(np.isfinite(con_nan)), True, "se detecta"))
    bien = all(es_remuestra_por_paciente(filas_de_la_remuestra(posiciones, sorteos[b])[0], sorteos[b], posiciones)
               for b in range(min(20, len(sorteos))))
    casos.append(caso("bootstrap", "en las 20 primeras remuestras, cada paciente entra con todas sus lesiones",
                      bien, False, f"{len(posiciones)} pacientes"))
    filas = np.random.default_rng(0).integers(0, len(y), size=len(y))
    casos.append(caso("bootstrap", "una remuestra por lesiones, del mismo tamaño",
                      not es_remuestra_por_paciente(filas, sorteos[0], posiciones), True, "se detecta"))
    return casos


def recuentos(y, grupos):
    s = pd.Series(np.asarray(y)).groupby(np.asarray(grupos).astype(str)).max()
    return {"pacientes": int(len(s)), "pacientes_portadores": int(s.sum()), "lesiones_malignas": int(np.sum(y))}


def controles_de_recuentos(r, modo, y_ent, g_ent, y_eval, g_eval):
    """Los recuentos frente a los de holdout-pacientes.json: en la apertura, el
    reservado y el desarrollo; en el ensayo, entrenamiento y evaluación juntos frente
    al desarrollo. El caso que debe fallar los compara con los del otro conjunto."""
    with open(r["holdout"], encoding="utf-8") as f:
        sellado = {k: {c: v[c] for c in ("pacientes", "pacientes_portadores", "lesiones_malignas")}
                   for k, v in json.load(f)["recuentos"].items()}
    ent, ev = recuentos(y_ent, g_ent), recuentos(y_eval, g_eval)
    if modo == "apertura":
        pares = [("la evaluación", ev, "reservado"), ("el entrenamiento", ent, "desarrollo")]
    else:
        pares = [("entrenamiento y evaluación juntos", {k: ent[k] + ev[k] for k in ent}, "desarrollo")]
    casos = []
    for que, obtenidos, conjunto in pares:
        otro = "desarrollo" if conjunto == "reservado" else "reservado"
        casos.append(caso("recuentos", f"{que}: los de {conjunto} en holdout-pacientes.json",
                          obtenidos == sellado[conjunto], False, obtenidos))
        casos.append(caso("recuentos", f"{que} frente a los de {otro}", obtenidos != sellado[otro], True,
                          f"iguales: {obtenidos == sellado[otro]}"))
    return casos


def comprobar_salida(resultado):
    """Lo que tiene que estar en la salida: punto e intervalo de las cuatro métricas
    de los cuatro modelos y de la diferencia, finitos y ordenados. Devuelve las faltas."""
    faltas = []
    for m in MODELOS:
        for k in f4.METRICAS:
            v = resultado.get("metricas", {}).get(m, {}).get(k)
            if not v or not np.isfinite(v.get("punto", np.nan)) or len(v.get("intervalo_95", [])) != 2 \
                    or not all(np.isfinite(v["intervalo_95"])) or v["intervalo_95"][0] > v["intervalo_95"][1]:
                faltas.append(f"metricas.{m}.{k}")
    for k in f4.METRICAS:
        v = resultado.get("diferencia_m3limpio_menos_m2", {}).get(k)
        if not v or not np.isfinite(v.get("punto", np.nan)) or len(v.get("intervalo_95", [])) != 2 \
                or "intervalo_entero_por_debajo_de_cero" not in v:
            faltas.append(f"diferencia_m3limpio_menos_m2.{k}")
    b = resultado.get("bootstrap", {})
    if b.get("remuestras") != REMUESTRAS or b.get("semilla") != SEMILLA_BOOTSTRAP:
        faltas.append("bootstrap")
    return faltas


# ---- la salida ----------------------------------------------------------------------------

def escribir_tabla(ruta, tabla):
    tabla.to_csv(ruta, index=False, float_format="%.17g", compression="gzip")
    leida = pd.read_csv(ruta, float_precision="round_trip")
    for c in tabla.columns:
        if pd.api.types.is_float_dtype(tabla[c]) and \
                leida[c].to_numpy(np.float64).tobytes() != tabla[c].to_numpy(np.float64).tobytes():
            raise SystemExit(f"ERROR: {ruta} no se relee igual que se escribió ({c}).")
    return sha256(ruta)


def escribir_md(salida, res):
    nombres = {"pauc": "pAUC", "auc": "AUC", "setop15": "SEtop-15", "nnt80": "NNT80% SE"}
    e, d = res["datos"]["entrenamiento"], res["datos"]["evaluacion"]

    def fila(v):
        return " · ".join(f"{nombres[k]} {v[k]['punto']} [{v[k]['intervalo_95'][0]}; {v[k]['intervalo_95'][1]}]"
                          for k in f4.METRICAS)
    titulo = ("el conjunto reservado" if res["modo"] == "apertura"
              else "ensayo: el pliegue 0 de la semilla 0 del desarrollo como reservado de mentira")
    c = res["controles"]
    lineas = [f"# Fase 5 — {titulo}", "",
              f"Entrenamiento: {e['pacientes']} pacientes, {e['lesiones']} lesiones · evaluación: {d['pacientes']} "
              f"pacientes, {d['lesiones']} lesiones, {d['malignas']} malignas · semilla 0",
              f"Bootstrap por paciente: {REMUESTRAS} remuestras, semilla {SEMILLA_BOOTSTRAP}, percentiles 2,5 y 97,5", ""]
    for m in MODELOS:
        lineas.append(f"- {NOMBRES[m]} ({PAPEL[m]}): {fila(res['metricas'][m])}")
    lineas.append(f"- M3 limpio − M2: {fila(res['diferencia_m3limpio_menos_m2'])}")
    lineas += ["", f"Controles: {c['de_casos'] - c['fallos']} de {c['de_casos']} bien, {c['deben_fallar']} de ellos "
               f"casos que deben fallar · tiempo total {res['segundos']['total']} s", "No interpreta."]
    with open(salida + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def main(argv=None, raiz=RAIZ):
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", required=True, choices=MODOS)
    args = ap.parse_args(argv)
    r = rutas(raiz)
    negarse_si_ya_se_abrio(r)
    modo, salida, dir_datos = args.modo, r["salida"][args.modo], r["datos"][args.modo]
    codigo = huella_codigo()
    ensayo = None
    if modo == "ensayo":
        for ruta in (salida + ".json", salida + ".md"):
            if os.path.exists(ruta):
                raise SystemExit(f"ERROR: ya existe {rel(ruta, raiz)}; bórrelo para repetir el ensayo.")
    else:
        ensayo = comprobar_ensayo(r, codigo)
        exigir_versionado(raiz, [rel(os.path.normpath(os.path.join(AQUI, c)), raiz) for c in CODIGO]
                          + [rel(salida_e, raiz) for salida_e in (r["salida"]["ensayo"] + ".json",
                                                                  r["salida"]["ensayo"] + ".md")])
    import fase4c
    bajo_caffeinate = fase4c.caffeinate()
    if not bajo_caffeinate["activo"]:
        raise SystemExit("ERROR: el programa corre bajo caffeinate (caffeinate -i …).")
    controles_4e = comprobar_red_antes(r)
    import torch
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    dispositivo = torch.device("mps")
    if modo == "apertura":
        if os.path.exists(dir_datos):
            raise SystemExit(f"ERROR: ya existe {rel(dir_datos, raiz)}.")
        with open(r["marca"], "w", encoding="utf-8") as f:
            json.dump({"fecha": ahora(), "sha256_del_codigo": codigo, "pid": os.getpid()}, f, ensure_ascii=False,
                      indent=2)
    os.makedirs(dir_datos, exist_ok=True)

    t_total = time.perf_counter()
    segundos = {}
    t0 = time.perf_counter()
    excluidas = cargar_columnas_excluidas(r["fugas"])
    df_dev, datos_dev = cargar_desarrollo(r["csv"], G, r["holdout"])
    numericas, categoricas = preparar_features(df_dev, excluidas, Y, G)
    faltan = [c for c in imagen_sola.BASICOS_NUMERICAS if c not in numericas] + \
             [c for c in imagen_sola.BASICOS_CATEGORICAS if c not in categoricas]
    if faltan:
        raise SystemExit(f"ERROR: {faltan} no son variables de M1 con el tipo esperado.")
    imagen_dev, comprobacion_dev = f4.cargar_imagen(df_dev, r["dinov2_desarrollo"], r["csv"], r["holdout"],
                                                    r["extraccion"])
    x_img_dev = imagen_dev.to_numpy()
    huellas = None
    if modo == "ensayo":
        folds = construir_folds(df_dev, G, Y, N_SPLITS, SEMILLA)
        with open(r["ref_pliegues"], encoding="utf-8") as f:
            ref_huella = json.load(f)["folds"]["sha256_por_semilla"][str(SEMILLA)]
        huellas = (f4.huella_folds(folds, len(df_dev)),
                   f4.huella_folds(construir_folds(df_dev, G, Y, N_SPLITS, SEMILLA + 1), len(df_dev)), ref_huella)
        if huellas[0] != ref_huella:
            raise SystemExit("ERROR: los pliegues de la semilla 0 no son los de la Fase 4.")
        tr, va = folds[PLIEGUE_DEL_ENSAYO]
        df_ent = df_dev.iloc[tr].reset_index(drop=True)
        df_eval = df_dev.iloc[va].drop(columns=[Y]).reset_index(drop=True)
        x_img_ent, x_img_eval = x_img_dev[tr], x_img_dev[va]
        comprobacion_eval = {"archivo": comprobacion_dev["archivo"], "sha256": comprobacion_dev["sha256"],
                             "filas": "las del pliegue 0, del archivo de desarrollo"}
        que_es_eval = "el pliegue 0 de construir_folds con semilla 0 sobre el desarrollo: un reservado de mentira"
    else:
        df_ent, x_img_ent = df_dev, x_img_dev
        df_eval = cargar_reservado_sin_etiqueta(r["csv"], r["holdout"], modo)
        x_img_eval, comprobacion_eval = cargar_caracteristicas_reservado(df_eval, r["dinov2_reservado"],
                                                                         r["extraccion"], modo)
        que_es_eval = f"los pacientes de {rel(r['holdout'], raiz)}"
    del df_dev
    exigir_disjuntos(df_ent[G], df_eval[G])
    segundos["carga"] = round(time.perf_counter() - t0, 1)
    print(f"Datos: {df_ent[G].nunique()} pacientes de entrenamiento, {df_eval[G].nunique()} de evaluación "
          f"({segundos['carga']} s)", flush=True)

    puntuaciones, info, s_tab = puntuar_tabulares(df_ent, df_eval, x_img_ent, x_img_eval, numericas, categoricas,
                                                  excluidas)
    segundos.update(s_tab)
    print(f"Tabulares: {s_tab}", flush=True)
    logit_red, info["Red4e"], s_red = puntuar_red(r, df_ent, df_eval, dispositivo, dir_datos)
    segundos.update(s_red)
    puntuaciones["Red4e"] = fase4c.probabilidad(logit_red)
    print(f"Red: {s_red}", flush=True)
    if not all(len(puntuaciones[m]) == len(df_eval) and np.all(np.isfinite(puntuaciones[m])) for m in MODELOS):
        raise SystemExit("ERROR: falta una puntuación o no es finita; no se leen las etiquetas.")

    ids_eval = df_eval["isic_id"].to_numpy()
    g_eval = df_eval[G].astype(str).to_numpy()
    tabla = pd.DataFrame({"isic_id": ids_eval, G: g_eval, "Red4e_logit": logit_red,
                          **{m: np.asarray(puntuaciones[m], dtype=np.float64) for m in MODELOS}})
    ruta_punt = os.path.join(dir_datos, "puntuaciones.csv.gz")
    sha_punt = escribir_tabla(ruta_punt, tabla)
    orden = {"puntuaciones_escritas": ahora()}

    # Hasta aquí, ninguna etiqueta de la evaluación.
    y = etiquetas_de(r["csv"], ids_eval, modo, r["holdout"])
    orden["etiquetas_leidas"] = ahora()
    puntos = {m: f4.medir(y, puntuaciones[m], g_eval) for m in MODELOS}

    t0 = time.perf_counter()
    pacientes, sorteos, posiciones, valores = bootstrap(y, puntuaciones, g_eval)
    segundos["bootstrap"] = round(time.perf_counter() - t0, 1)
    print(f"Bootstrap: {segundos['bootstrap']} s", flush=True)
    metricas, diferencia = resumir(puntos, valores)
    remuestras = pd.DataFrame([{"remuestra": b, "modelo": m, **{k: valores[m][k][b] for k in f4.METRICAS}}
                               for m in MODELOS for b in range(REMUESTRAS)])
    ruta_rem = os.path.join(dir_datos, "remuestras.csv.gz")
    sha_rem = escribir_tabla(ruta_rem, remuestras)

    casos = controles_comunes(df_ent[G].astype(str).to_numpy(), g_eval, puntuaciones, y, g_eval, posiciones, sorteos)
    casos += controles_de_recuentos(r, modo, df_ent[Y].to_numpy(), df_ent[G].to_numpy(), y, g_eval)
    if modo == "ensayo":
        casos += controles_del_ensayo(r, ids_eval, puntuaciones, logit_red,
                                      os.path.join(raiz, info["Red4e"]["pesos_base"]), puntos, *huellas)

    import catboost
    import sklearn
    import torchvision
    resultado = {
        "especificacion": "PLAN.md, Fase 5, fijada el 2026-09-26 y ampliada el 2026-11-02, antes de abrir el reservado",
        "modo": modo,
        "datos": {
            "entrenamiento": {"conjunto": datos_dev["conjunto"], "archivo": rel(r["csv"], raiz),
                              "sin_los_pacientes_de": rel(r["holdout"], raiz),
                              "filas": "todo el desarrollo" if modo == "apertura" else "los pliegues 1 a 4 de la semilla 0",
                              "pacientes": int(df_ent[G].nunique()), "lesiones": int(len(df_ent)),
                              "malignas": int(df_ent[Y].sum())},
            "evaluacion": {"que_es": que_es_eval, "pacientes": int(len(pacientes)), "lesiones": int(len(y)),
                           "malignas": int(y.sum()), "pacientes_con_malignas": int(pd.Series(y).groupby(g_eval).max().sum()),
                           "caracteristicas_de_imagen": {k: (rel(v, raiz) if k == "archivo" else v)
                                                         for k, v in comprobacion_eval.items()}},
        },
        "modelos": {m: {"nombre": NOMBRES[m], "papel": PAPEL[m], "descripcion": DESCRIPCION[m]} for m in MODELOS},
        "metricas": metricas,
        "diferencia_m3limpio_menos_m2": diferencia,
        "bootstrap": {"unidad": "paciente", "remuestras": REMUESTRAS, "semilla": SEMILLA_BOOTSTRAP,
                      "percentiles": list(PERCENTILES), "metodo_de_percentil": "numpy.percentile, interpolación lineal",
                      "sorteo": "numpy.random.default_rng(semilla).integers(0, pacientes, (remuestras, pacientes)), "
                                "sobre los patient_id de la evaluación ordenados",
                      "mismas_remuestras_para_los_cuatro_modelos_y_la_diferencia": True,
                      "paciente_repetido": "cada vez que sale un paciente es un grupo nuevo en SEtop-15",
                      "sha256_de_los_sorteos": hashlib.sha256(sorteos.tobytes()).hexdigest()},
        "entrenamiento": info,
        "controles": {"casos": casos, "de_casos": len(casos), "fallos": sum(not c["ok"] for c in casos),
                      "deben_fallar": sum(c["debe_fallar"] for c in casos), "controles_de_la_red_4e": controles_4e},
        "orden": {**orden, "nota": "las etiquetas de la evaluación se leen del CSV después de escribir las "
                                   "puntuaciones de los cuatro modelos"},
        "archivos": {"puntuaciones": {"archivo": rel(ruta_punt, raiz), "sha256": sha_punt},
                     "remuestras": {"archivo": rel(ruta_rem, raiz), "sha256": sha_rem},
                     "como_leerlos": "pd.read_csv(archivo, float_precision='round_trip')"},
        **({"ensayo": ensayo} if ensayo else {}),
        "sha256_del_codigo": codigo,
        "comando": {"interprete": rel(sys.executable, raiz), "argumentos": sys.argv, "caffeinate": bajo_caffeinate},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "catboost": catboost.__version__,
                      "torch": torch.__version__, "torchvision": torchvision.__version__},
        "fecha": ahora(),
    }
    faltas = comprobar_salida(resultado)
    incompleta = json.loads(json.dumps(resultado))
    del incompleta["metricas"]["Red4e"]["setop15"]
    casos.append(caso("salida", "la salida tiene punto e intervalo de todo lo que pide la especificación", not faltas,
                      False, faltas or "completa"))
    casos.append(caso("salida", "sin la SEtop-15 de la red", bool(comprobar_salida(incompleta)), True,
                      comprobar_salida(incompleta)))
    resultado["controles"].update(de_casos=len(casos), fallos=sum(not c["ok"] for c in casos),
                                  deben_fallar=sum(c["debe_fallar"] for c in casos))
    segundos["total"] = round(time.perf_counter() - t_total, 1)
    resultado["segundos"] = segundos
    resultado["completo"] = resultado["controles"]["fallos"] == 0
    if not resultado["completo"]:
        with open(os.path.join(dir_datos, "controles-fallidos.json"), "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        malos = [f"{c['control']}: {c['caso']}" for c in casos if not c["ok"]]
        raise SystemExit("ERROR: fallaron controles; no se escribe la salida (el detalle, en "
                         f"{rel(dir_datos, raiz)}/controles-fallidos.json):\n  " + "\n  ".join(malos))
    resultado["nota"] = ("No interpreta. El resultado principal es M3 limpio; M2 es la referencia; la red de la 4e e "
                         "«Imagen + básicos» son descriptivos.")
    with open(salida + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    escribir_md(salida, resultado)
    print(f"Escrito: {rel(salida, raiz)}.json y .md; {segundos['total']} s", flush=True)


if __name__ == "__main__":
    main()

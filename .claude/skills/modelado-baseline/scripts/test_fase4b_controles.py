#!/usr/bin/env python3
"""
test_fase4b_controles.py — los controles de la Fase 4b (PLAN.md, «Controles,
antes de leer cualquier resultado»), antes de correr ningún candidato. No corre
C1, C2 ni C3: comprueba las piezas de fase4b.py y que el código de la Fase 4
sigue dando lo que registró.

  K. M3 limpio y M2, con el código de la Fase 4, reproducen pliegue a pliegue las
     cuatro métricas de outputs/fase4-m3limpio-vs-m2.json, con los mismos pliegues
     (huella por semilla).
  L. C2 de punta a punta: M4b, con puntuaciones_imagen, reproduce pliegue a
     pliegue las cuatro métricas de outputs/fase4-m4b-vs-m2.json.
  M. C2, alineación: en un pliegue, las dos columnas de imagen de
     fase4b.con_imagen coinciden fila a fila con lo que devuelve
     puntuaciones_imagen, antes y después del remuestreo de M3 limpio.
  N. C3: fase4b.ajustar_nivel_2b, con las 39 variables y la codificación de M1
     (codificar_fold), reproduce pliegue a pliegue las cuatro métricas de M1 en
     outputs/fase4-m2-vs-m1.json. Con las variables de M3 limpio, ninguna entra
     como categórica, y las one-hot conservan sus valores al pasar a enteros.
  O. fase4b.rango_promedio: un modelo mezclado consigo mismo da su misma pAUC, y
     mezclado con ruido aleatorio, una pAUC menor, en cada pliegue.

Cada control tiene un caso que debe fallar, por el corolario de la regla 6 de
CLAUDE.md (un chequeo que no puede fallar no vale nada):
  K: la referencia con un valor alterado en 0,0001, y M3 limpio con otra semilla;
  L: M4b con otra semilla en su validación interna;
  M: las columnas de imagen corridas una fila;
  N: el nivel 2b sin class_weight, y las one-hot sin pasar a enteros;
  O: un rango invertido, y una mezcla que ignora el segundo modelo.

Con --rapido corre el pliegue 0 de la semilla 0 de K, L y N, los casos que deben
fallar, M y O sobre datos sintéticos. Sin --rapido, además las reproducciones
completas, 10 semillas × 5 pliegues, y O sobre las puntuaciones reales de M3
limpio.

Con --guardar-predicciones RUTA.csv.gz (solo en la corrida completa) guarda, para
que C1 las reutilice, las puntuaciones de M3 limpio y M2 de cada pliegue de
validación: modelo, semilla, pliegue, isic_id y puntuación. Al lado escribe
RUTA.json con su procedencia: el SHA-256 del archivo y del código que lo produjo,
la orden, las versiones y si K reprodujo la Fase 4. No calcula ninguna mezcla ni
ninguna métrica de candidatos. La ruta tiene que estar en data/, que no se
versiona.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4b_controles.py --rapido --out RUTA.json
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4b_controles.py --out RUTA.json \
        --guardar-predicciones data/fase4b-predicciones-m3limpio-m2.csv.gz
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import ganador_m3  # noqa: E402
from apilado_imagen import puntuaciones_imagen  # noqa: E402
from contexto_paciente import variables_contexto_paciente  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds, pauc_above_tpr, preparar_features  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
H5 = os.path.join(RAIZ, "data", "dinov2-vits14-desarrollo.h5")
EXTRACCION = os.path.join(RAIZ, "outputs", "extraccion-imagen.json")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
REF = {
    "M3limpio": os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json"),
    "M2": os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json"),
    "M4b": os.path.join(RAIZ, "outputs", "fase4-m4b-vs-m2.json"),
    "M1": os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json"),
}
G, Y = "patient_id", "target"

resultados = []


def registrar(control, caso, ok, detalle, debe_fallar=False):
    """ok: el caso se comportó como se esperaba (si debe_fallar, que la comprobación falló)."""
    resultados.append({"control": control, "caso": caso, "ok": bool(ok), "debe_fallar": debe_fallar,
                       "detalle": detalle})
    print(f"[{'OK' if ok else 'FALLA'}] {control} · {caso}{' (debe fallar)' if debe_fallar else ''}: {detalle}",
          flush=True)


def leer_referencias():
    ref = {}
    for m, ruta in REF.items():
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
        ref[m] = {"metricas": {k: d["metricas"][m][k]["por_semilla_y_fold"] for k in f4.METRICAS},
                  "huellas": d["folds"]["sha256_por_semilla"], "archivo": os.path.relpath(ruta, RAIZ)}
    return ref


def discrepancias(calculadas, ref_metricas, semilla, pliegues):
    """Métricas calculadas {k: [valores por pliegue]} frente a las registradas, con el
    redondeo de 4 decimales con que se guardaron. Devuelve la lista de diferencias."""
    fuera = []
    for k, valores in calculadas.items():
        guardadas = ref_metricas[k][str(semilla)]
        for i, v in zip(pliegues, valores):
            if round(float(v), 4) != guardadas[i]:
                fuera.append({"metrica": k, "semilla": semilla, "pliegue": i, "calculada": round(float(v), 4),
                              "registrada": guardadas[i]})
    return fuera


def preparar():
    t0 = time.perf_counter()
    excluidas = cargar_columnas_excluidas(FUGAS)
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    numericas, categoricas = preparar_features(df, excluidas, Y, G)
    contexto = variables_contexto_paciente(df.drop(columns=[Y]), numericas, G)
    imagen, _ = f4.cargar_imagen(df, H5, CSV, RUTA_HOLDOUT, EXTRACCION)
    df_sin_etiqueta = df.drop(columns=[Y])  # como en fase4_comparar: antes de añadir contexto e imagen
    df = pd.concat([df, contexto, imagen], axis=1)
    return {"df": df, "df_sin_etiqueta": df_sin_etiqueta, "excluidas": excluidas, "numericas": numericas,
            "categoricas": categoricas, "contexto": list(contexto.columns), "x_imagen": imagen.to_numpy(),
            "y": df[Y].to_numpy(), "grupos": df[G].to_numpy(), "datos": datos,
            "segundos_de_carga": round(time.perf_counter() - t0, 1)}


# ---- los modelos de la Fase 4, como los ajusta fase4_comparar.py ------------------------------

def hgb_fase4(d, variables, tr, va, semilla, class_weight="balanced"):
    x_tr, x_va = codificar_fold(d["df"], variables, d["categoricas"], Y, tr, va)
    m = HistGradientBoostingClassifier(random_state=semilla, class_weight=class_weight).fit(x_tr, d["y"][tr])
    return m.predict_proba(x_va)[:, 1]


def m3limpio(d, tr, va, semilla, variables=None):
    if variables is None:
        variables = ganador_m3.variables_m3_en_pliegue(d["df_sin_etiqueta"], tr, va, d["excluidas"], G)
    x_tr, x_va, cats, _ = variables
    modelo = ganador_m3.ajustar_m3(x_tr, d["y"][tr], d["grupos"][tr], cats, semilla,
                                   parametros=ganador_m3.PARAMETROS_LIMPIO)
    return modelo.predict_proba(x_va)[:, 1]


def m4b(d, tr, va, semilla, semilla_interna=None, ap=None):
    if ap is None:
        ap = puntuaciones_imagen(d["x_imagen"], d["y"], d["grupos"], tr, va,
                                 semilla if semilla_interna is None else semilla_interna)
    df = d["df"]
    for col, clave in zip(f4.APILADAS, ("puntuacion", "razon")):
        valores = np.full(len(df), np.nan)
        valores[tr] = ap["tr"][clave]
        valores[va] = ap["va"][clave]
        df[col] = valores
    return hgb_fase4(d, d["numericas"] + d["contexto"] + f4.APILADAS, tr, va, semilla)


def m1_con_c3(d, tr, va, semilla):
    """El segundo modelo de C3 (fase4b.ajustar_nivel_2b) con las 39 variables y la
    codificación de M1."""
    x_tr, x_va = codificar_fold(d["df"], d["numericas"], d["categoricas"], Y, tr, va)
    modelo = fase4b.ajustar_nivel_2b(x_tr, d["y"][tr], semilla)
    return fase4b.puntuar_nivel_2b(modelo, x_va)


def medir(d, va, s):
    return f4.medir(d["y"][va], s, d["grupos"][va])


# ---- K, L y N: reproducciones -------------------------------------------------------------

def reproducir(d, ref, semillas, pliegues_por_semilla):
    """Corre M3 limpio, M2, M4b y M1 (con el código de C3) y compara. Devuelve las
    puntuaciones de M3 limpio por (semilla, pliegue) para O."""
    puntuaciones_m3l, tiempos = {}, {}
    guardadas = []  # (modelo, semilla, pliegue, isic_id, puntuación) de M3 limpio y M2
    por = {m: [] for m in ("M3limpio", "M2", "M4b", "M1")}
    for semilla in semillas:
        folds = construir_folds(d["df"], G, Y, 5, semilla)
        huella = f4.huella_folds(folds, len(d["df"]))
        for m in por:
            if huella != ref[m]["huellas"][str(semilla)]:
                por[m].append({"huella": f"semilla {semilla}: pliegues distintos de {ref[m]['archivo']}"})
        calc = {m: {k: [] for k in f4.METRICAS} for m in por}
        pliegues = pliegues_por_semilla(semilla)
        inicio = time.perf_counter()
        for i in pliegues:
            tr, va = folds[i]
            s = {"M3limpio": m3limpio(d, tr, va, semilla), "M2": hgb_fase4(d, d["numericas"] + d["contexto"], tr, va,
                                                                           semilla),
                 "M4b": m4b(d, tr, va, semilla), "M1": m1_con_c3(d, tr, va, semilla)}
            puntuaciones_m3l[(semilla, i)] = (s["M3limpio"], va)
            for m in ("M3limpio", "M2"):
                guardadas.append(pd.DataFrame({"modelo": m, "semilla": semilla, "pliegue": i,
                                               "isic_id": d["df"]["isic_id"].to_numpy()[va],
                                               "puntuacion": s[m]}))
            for m in por:
                for k, v in medir(d, va, s[m]).items():
                    calc[m][k].append(v)
        tiempos[str(semilla)] = round(time.perf_counter() - inicio, 1)
        for m in por:
            por[m].extend(discrepancias(calc[m], ref[m]["metricas"], semilla, pliegues))
        print(f"  semilla {semilla}: {tiempos[str(semilla)]} s", flush=True)
    return por, puntuaciones_m3l, tiempos, guardadas


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def guardar_predicciones(ruta, guardadas, d, reproduce, semillas):
    """Las puntuaciones de M3 limpio y M2, y su procedencia al lado. Solo en data/."""
    destino = os.path.realpath(ruta)
    if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "data")) + os.sep):
        raise SystemExit(f"ERROR: las predicciones van en data/, que no se versiona; se pidió {ruta}.")
    tabla = pd.concat(guardadas, ignore_index=True)
    tabla.to_csv(destino, index=False, float_format="%.17g", compression="gzip")
    # El lector por defecto de pandas no recupera el mismo float64 desde "%.17g";
    # float_precision="round_trip" sí. Se comprueba antes de dar el archivo por bueno.
    leida = pd.read_csv(destino, float_precision="round_trip")
    huella = hashlib.sha256(tabla["puntuacion"].to_numpy(np.float64).tobytes()).hexdigest()
    if (not leida["puntuacion"].to_numpy(np.float64).tobytes() == tabla["puntuacion"].to_numpy(np.float64).tobytes()
            or not (leida["isic_id"].to_numpy() == tabla["isic_id"].to_numpy()).all()):
        raise SystemExit(f"ERROR: {destino} no se relee igual que se escribió.")
    import catboost
    import sklearn
    codigo = ["fase4b.py", "test_fase4b_controles.py", "fase4_comparar.py", "ganador_m3.py", "apilado_imagen.py",
              "contexto_paciente.py", "train_and_evaluate.py"]
    procedencia = {
        "archivo": os.path.relpath(destino, RAIZ),
        "sha256": sha256(destino),
        "como_leerlo": "pd.read_csv(archivo, float_precision='round_trip'): con el lector por defecto no se recupera "
                       "el mismo float64",
        "sha256_de_las_puntuaciones_float64": huella,
        "filas": int(len(tabla)),
        "columnas": list(tabla.columns),
        "modelos": ["M3limpio", "M2"],
        "semillas": semillas,
        "pliegues": 5,
        "datos": d["datos"],
        "que_es": "puntuaciones de validación de M3 limpio y M2, de los controles de la Fase 4b (PLAN.md), "
                  "para que C1 las reutilice; sin mezclas ni métricas de candidatos",
        "reproducen_fase4": reproduce,
        "comando": " ".join([os.path.relpath(sys.executable, RAIZ)] + [os.path.relpath(a, RAIZ) if os.path.exists(a)
                                                                        else a for a in sys.argv]),
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sha256_del_codigo": {c: sha256(os.path.join(AQUI, c)) for c in codigo},
        "versiones": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "catboost": catboost.__version__},
    }
    with open(os.path.splitext(os.path.splitext(destino)[0])[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(procedencia, f, ensure_ascii=False, indent=2)
    return procedencia


def casos_que_deben_fallar_k_l_n(d, ref, variables_m3l):
    folds = construir_folds(d["df"], G, Y, 5, 0)
    tr, va = folds[0]
    # K: el comparador detecta un cambio de 0,0001 en la referencia.
    s = m3limpio(d, tr, va, 0, variables=variables_m3l)
    calc = {k: [v] for k, v in medir(d, va, s).items()}
    alterada = {k: {s_: list(v) for s_, v in vs.items()} for k, vs in ref["M3limpio"]["metricas"].items()}
    alterada["pauc"]["0"][0] = round(alterada["pauc"]["0"][0] + 0.0001, 4)
    fuera = discrepancias(calc, alterada, 0, [0])
    registrar("K", "referencia alterada en 0,0001", len(fuera) == 1 and fuera[0]["metrica"] == "pauc",
              f"{len(fuera)} discrepancia(s): {fuera}", debe_fallar=True)
    # K: M3 limpio con otra semilla no reproduce el pliegue.
    s_otra = m3limpio(d, tr, va, 1, variables=variables_m3l)
    fuera = discrepancias({k: [v] for k, v in medir(d, va, s_otra).items()}, ref["M3limpio"]["metricas"], 0, [0])
    registrar("K", "M3 limpio con semilla 1 en el pliegue 0 de la semilla 0", len(fuera) > 0,
              f"{len(fuera)} de 4 métricas distintas", debe_fallar=True)
    # L: M4b con otra semilla en la validación interna.
    s_m4b = m4b(d, tr, va, 0, semilla_interna=1)
    fuera = discrepancias({k: [v] for k, v in medir(d, va, s_m4b).items()}, ref["M4b"]["metricas"], 0, [0])
    registrar("L", "M4b con semilla interna 1", len(fuera) > 0, f"{len(fuera)} de 4 métricas distintas",
              debe_fallar=True)
    # N: el nivel 2b sin class_weight.
    s_m1 = hgb_fase4(d, d["numericas"], tr, va, 0, class_weight=None)
    fuera = discrepancias({k: [v] for k, v in medir(d, va, s_m1).items()}, ref["M1"]["metricas"], 0, [0])
    registrar("N", "M1 sin class_weight", len(fuera) > 0, f"{len(fuera)} de 4 métricas distintas",
              debe_fallar=True)


# ---- M: alineación de C2 -------------------------------------------------------------------

def alineacion(x_tr, ap, semilla, y_tr, grupos_tr, con_imagen=fase4b.con_imagen):
    """Antes del remuestreo: las dos columnas son las de ap, fila a fila, y la razón
    sale de la puntuación con los grupos de esas filas. Después: cada fila
    remuestreada lleva los valores de su fila de origen (una columna marcadora
    viaja con ella)."""
    xc_tr, _ = con_imagen(x_tr, x_tr.iloc[:0], {"tr": ap["tr"], "va": {"puntuacion": [], "razon": []}})
    cols = fase4b.COLUMNAS_IMAGEN
    antes = (np.array_equal(xc_tr[cols[0]].to_numpy(), ap["tr"]["puntuacion"])
             and np.array_equal(xc_tr[cols[1]].to_numpy(), ap["tr"]["razon"]))
    p = pd.Series(xc_tr[cols[0]].to_numpy())
    razon_indep = (p / p.groupby(grupos_tr).transform("mean")).to_numpy()
    razon_ok = np.allclose(xc_tr[cols[1]].to_numpy(), razon_indep, rtol=0, atol=1e-12)
    interna = ganador_m3.StratifiedGroupKFold(n_splits=ganador_m3.PLIEGUES_INTERNOS, shuffle=True,
                                              random_state=semilla)
    itr, _ = next(interna.split(xc_tr, y_tr, groups=grupos_tr))
    marcada = xc_tr.iloc[itr].copy()
    marcada["_fila"] = np.arange(len(marcada))
    xr, _ = ganador_m3.remuestrear(marcada, y_tr[itr], semilla)
    origen = marcada.iloc[xr["_fila"].to_numpy()]
    despues = all(np.array_equal(xr[c].to_numpy(), origen[c].to_numpy()) for c in cols)
    return antes, razon_ok, despues, len(xr)


# ---- N: las one-hot entran como números ----------------------------------------------------

def one_hot_como_numeros(variables_m3l, y_tr, semilla):
    x_tr, _, cats, _ = variables_m3l
    convertidas = fase4b.a_numeros(x_tr)
    valores_ok = all(np.array_equal(convertidas[c].to_numpy(), np.asarray(x_tr[c].tolist(), dtype=np.int64))
                     for c in cats)
    modelo = fase4b.ajustar_nivel_2b(x_tr, y_tr, semilla)
    ninguna = modelo.is_categorical_ is None or not np.any(modelo.is_categorical_)
    registrar("N", "las one-hot de M3 limpio entran como números",
              valores_ok and ninguna and len(cats) > 0,
              f"{len(cats)} one-hot en {x_tr.shape[1]} variables; valores conservados: {valores_ok}; "
              f"categóricas para el modelo: {0 if modelo.is_categorical_ is None else int(np.sum(modelo.is_categorical_))}")
    # Debe fallar: sin pasar a enteros, el modelo las toma como categóricas y el guardián se dispara.
    original = fase4b.a_numeros
    fase4b.a_numeros = lambda x: x
    try:
        fase4b.ajustar_nivel_2b(x_tr, y_tr, semilla)
        disparado, mensaje = False, "el ajuste no se detuvo"
    except SystemExit as e:
        disparado, mensaje = True, str(e)
    finally:
        fase4b.a_numeros = original
    registrar("N", "las one-hot sin pasar a enteros", disparado, mensaje, debe_fallar=True)


# ---- O: el promedio de rangos ---------------------------------------------------------------

def control_rangos(pares, mezcla=fase4b.rango_promedio):
    """pares: lista de (y, s). Devuelve (consigo mismo da la misma pAUC en todos,
    con ruido da menos en todos)."""
    iguales = menores = 0
    for j, (y, s) in enumerate(pares):
        propia = pauc_above_tpr(y, s)
        if abs(pauc_above_tpr(y, mezcla(s, s)) - propia) <= 1e-12:
            iguales += 1
        ruido = np.random.default_rng(1000 + j).uniform(size=len(s))
        if pauc_above_tpr(y, mezcla(s, ruido)) < propia:
            menores += 1
    return iguales, menores, len(pares)


def pares_sinteticos():
    pares = []
    for j in range(10):
        rng = np.random.default_rng(j)
        y = (rng.uniform(size=20000) < 0.01).astype(int)
        s = np.round(1.5 * y + rng.normal(size=len(y)), 1)  # redondeada: con empates
        pares.append((y, s))
    return pares


def casos_o(pares, origen):
    iguales, menores, n = control_rangos(pares)
    registrar("O", f"consigo mismo, misma pAUC ({origen})", iguales == n, f"{iguales} de {n}")
    registrar("O", f"con ruido, pAUC menor ({origen})", menores == n, f"{menores} de {n}")
    invertido = lambda a, b: 0.5 * rankdata(-np.asarray(a), method="average") + 0.5 * rankdata(-np.asarray(b), method="average")
    iguales, _, n = control_rangos(pares, invertido)
    registrar("O", f"rango invertido, consigo mismo ({origen})", iguales < n, f"misma pAUC en {iguales} de {n}",
              debe_fallar=True)
    ignora = lambda a, b: rankdata(np.asarray(a), method="average")
    _, menores, n = control_rangos(pares, ignora)
    registrar("O", f"mezcla que ignora el segundo, con ruido ({origen})", menores < n,
              f"pAUC menor en {menores} de {n}", debe_fallar=True)
    # Los empates reciben el rango promedio.
    r = fase4b.rango_promedio(np.array([0.2, 0.5, 0.5, 0.9]), np.array([0.2, 0.5, 0.5, 0.9]))
    registrar("O", "empates con el rango promedio", list(r) == [1.0, 2.5, 2.5, 4.0], f"rangos {list(r)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--out", required=True, help="JSON con el resultado de cada caso")
    ap.add_argument("--guardar-predicciones", default=None, help="data/….csv.gz, solo en la corrida completa")
    args = ap.parse_args()
    if args.guardar_predicciones and args.rapido:
        raise SystemExit("ERROR: --guardar-predicciones es para la corrida completa, no para --rapido.")
    t_total = time.perf_counter()

    registrar("M", "COLUMNAS_IMAGEN = fase4_comparar.APILADAS", fase4b.COLUMNAS_IMAGEN == f4.APILADAS,
              f"{fase4b.COLUMNAS_IMAGEN}")
    casos_o(pares_sinteticos(), "sintético")

    d = preparar()
    ref = leer_referencias()
    print(f"Datos de desarrollo: {len(d['df'])} filas, {len(d['numericas'])} numéricas y {len(d['categoricas'])} "
          f"categóricas de M1; carga en {d['segundos_de_carga']} s", flush=True)

    # Lo de un pliegue: semilla 0, pliegue 0.
    folds = construir_folds(d["df"], G, Y, 5, 0)
    tr, va = folds[0]
    variables_m3l = ganador_m3.variables_m3_en_pliegue(d["df_sin_etiqueta"], tr, va, d["excluidas"], G)
    ap_img = puntuaciones_imagen(d["x_imagen"], d["y"], d["grupos"], tr, va, 0)
    antes, razon_ok, despues, n_rem = alineacion(variables_m3l[0], ap_img, 0, d["y"][tr], d["grupos"][tr])
    registrar("M", "antes del remuestreo, fila a fila", antes and razon_ok,
              f"columnas iguales a puntuaciones_imagen: {antes}; razón recalculada por paciente: {razon_ok}")
    registrar("M", "después del remuestreo, cada fila con la de su origen", despues, f"{n_rem} filas remuestreadas")

    def corrida(x_tr, x_va, a):
        rodado = {"puntuacion": np.roll(a["tr"]["puntuacion"], 1), "razon": np.roll(a["tr"]["razon"], 1)}
        return fase4b.con_imagen(x_tr, x_va, {"tr": rodado, "va": a["va"]})
    antes_m, _, _, _ = alineacion(variables_m3l[0], ap_img, 0, d["y"][tr], d["grupos"][tr], con_imagen=corrida)
    registrar("M", "columnas corridas una fila", not antes_m, f"coinciden: {antes_m}", debe_fallar=True)

    one_hot_como_numeros(variables_m3l, d["y"][tr], 0)
    casos_que_deben_fallar_k_l_n(d, ref, variables_m3l)

    if args.rapido:
        por, puntuaciones, tiempos, _ = reproducir(d, ref, [0], lambda s: [0])
        alcance = "semilla 0, pliegue 0"
    else:
        por, puntuaciones, tiempos, guardadas = reproducir(d, ref, args.semillas, lambda s: list(range(5)))
        alcance = f"semillas {args.semillas[0]} a {args.semillas[-1]}, 5 pliegues"
    nombres = {"M3limpio": ("K", "M3 limpio"), "M2": ("K", "M2"), "M4b": ("L", "M4b (C2 de punta a punta)"),
               "M1": ("N", "M1 con el ajuste de C3")}
    for m, fuera in por.items():
        control, nombre = nombres[m]
        registrar(control, f"{nombre} reproduce {REF[m].split('/')[-1]} ({alcance})", not fuera,
                  "las cuatro métricas iguales" if not fuera else f"{len(fuera)} discrepancias: {fuera[:3]}")
    if not args.rapido:
        pares = [(d["y"][va], s) for (s, va) in puntuaciones.values()]
        casos_o(pares, "M3 limpio, 50 pliegues")
    if args.guardar_predicciones:
        reproduce = {m: not por[m] for m in ("M3limpio", "M2")}
        p = guardar_predicciones(args.guardar_predicciones, guardadas, d, reproduce, args.semillas)
        print(f"Predicciones guardadas: {p['archivo']}, {p['filas']} filas, SHA-256 {p['sha256']}", flush=True)

    total = round(time.perf_counter() - t_total, 1)
    malos = [r for r in resultados if not r["ok"]]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"rapido": args.rapido, "alcance": alcance, "segundos": total, "segundos_por_semilla": tiempos,
                   "casos": resultados, "fallos": len(malos)}, f, ensure_ascii=False, indent=2)
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; {total} s. Escrito: {args.out}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

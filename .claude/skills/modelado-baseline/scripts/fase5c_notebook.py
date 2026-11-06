# %% [markdown]
# # ISIC 2024 — Fase 5c: descomponer la distancia al ganador
#
# Notebook de la Fase 5c de `PLAN.md` del proyecto «Agente consultor estadístico — ISIC 2024». Solo predice: los
# modelos se entrenaron fuera de Kaggle con todos los datos de entrenamiento y llegan en un conjunto de datos privado,
# con el código de inferencia (`inferencia_5c.py`, que usa `inferencia_5b.py`). Corre sin internet.
#
# `MODO` elige qué hace:
# - `"medicion"`: la comprobación del control, el tiempo de los cuatro modelos sobre recortes de entrenamiento,
#   proyectado al tamaño de la prueba, y las cuatro puntuaciones de la prueba visible. No es un envío.
# - `"M3limpioProm"`, `"M3limpioPromHosp"`, `"C7Prom"` o `"C7PromHosp"`: la comprobación del control y
#   `submission.csv` de ese modelo, la media de las probabilidades de sus 45 CatBoost.
#
# Si la comprobación del control falla, se detiene sin escribir `submission.csv`.

# %%
MODO = "medicion"

import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd
import torch

T0 = time.perf_counter()
ENTRADA = os.environ.get("RAIZ_ENTRADA", "/kaggle/input")
SALIDA = os.environ.get("RAIZ_SALIDA", "/kaggle/working")
MODOS = ("medicion", "M3limpioProm", "M3limpioPromHosp", "C7Prom", "C7PromHosp")
if MODO not in MODOS:
    raise SystemExit(f"MODO tiene que ser uno de {MODOS}")


def buscar(nombre, profundidad=4):
    """La carpeta que contiene `nombre` bajo ENTRADA, sin entrar en train-image/."""
    def recorrer(d, nivel):
        if os.path.exists(os.path.join(d, nombre)):
            return d
        if nivel == profundidad:
            return None
        for h in sorted(os.listdir(d)):
            ruta = os.path.join(d, h)
            if os.path.isdir(ruta) and h != "train-image":
                encontrada = recorrer(ruta, nivel + 1)
                if encontrada:
                    return encontrada
        return None
    d = recorrer(ENTRADA, 0)
    if d is None:
        raise SystemExit(f"No está {nombre} bajo {ENTRADA}.")
    return d


COMPETICION = buscar("train-metadata.csv")
MODELOS = buscar("inferencia_5c.py")
sys.path.insert(0, MODELOS)
import inferencia_5b as inf5b  # noqa: E402
import inferencia_5c as inf  # noqa: E402

if torch.cuda.is_available():
    DISPOSITIVO = torch.device("cuda")
elif torch.backends.mps.is_available():
    DISPOSITIVO = torch.device("mps")
else:
    DISPOSITIVO = torch.device("cpu")
TRABAJADORES = int(os.environ.get("TRABAJADORES", min(4, os.cpu_count() or 1)))
TRAIN_HDF5 = os.path.join(COMPETICION, "train-image.hdf5")
TOL = {"logit": 1e-2, "probabilidad": 1e-3, "z": 1e-2}
N_PRUEBA = 500_000  # "Test data comprised about 500,000 lesion tiles" (Kurtansky et al. 2025, métodos)
N_MUESTRA_IMAGENES = 4096
N_MUESTRA_TABULAR = 20_000
LIMITE_HORAS = 12  # "CPU Notebook <= 12 hours run-time", "GPU Notebook <= 12 hours run-time"
ENVIOS = MODOS[1:]
resultado = {"modo": MODO, "dispositivo": str(DISPOSITIVO),
             "gpu": torch.cuda.get_device_name(0) if DISPOSITIVO.type == "cuda" else None,
             "trabajadores": TRABAJADORES, "entrada": {"competicion": COMPETICION, "modelos": MODELOS}}
print(resultado, flush=True)

# %%
# Los modelos: las cinco redes solo si el modo usa C7; los CatBoost se cargan al puntuar, uno a uno.
a_correr = ENVIOS if MODO == "medicion" else [MODO]
con_redes = any(inf.CON_RED[m] for m in a_correr)
t = time.perf_counter()
REDES = {k: inf5b.red(os.path.join(MODELOS, f"red-{k}.pt"), DISPOSITIVO) for k in inf5b.REDES_DE_C7} \
    if con_redes else {}
AJUSTES = {h: inf.cargar_ajuste(MODELOS, h) for h in (False, True)}
TABLA_17 = inf5b.leer_json(os.path.join(MODELOS, "celda17.json"))
resultado["segundos_carga_de_modelos"] = round(time.perf_counter() - t, 1)
META = pd.read_csv(os.path.join(COMPETICION, "train-metadata.csv"), low_memory=False)


def media_de_las_redes(filas, hdf5):
    """Los logits de las cinco redes y la media de sus probabilidades, en el orden de filas."""
    logits, _ = inf5b.recorrer(hdf5, filas["isic_id"].tolist(), REDES, None, DISPOSITIVO, TRABAJADORES)
    return logits, np.mean([inf5b.probabilidad(logits[k]) for k in inf5b.REDES_DE_C7], axis=0)


def puntuar(modelo, filas, hdf5, red=None):
    """La puntuación de un envío para filas (sin etiqueta) y lo intermedio que se compara en
    el control. red: (logits, media) ya calculados para estas filas, si los hay."""
    intermedio, p = {}, None
    if inf.CON_RED[modelo]:
        logits, p = red if red is not None else media_de_las_redes(filas, hdf5)
        intermedio["logits"] = logits
    x = inf.variables(modelo, filas, AJUSTES[inf.CON_HOSPITAL[modelo]], p, TABLA_17)
    if inf.Z_CELDA_17 in x.columns:
        intermedio["z"] = x[inf.Z_CELDA_17].to_numpy(np.float64)
    s, _ = inf.puntuar_promedio(MODELOS, modelo, x)
    return s, intermedio


def maxima(a, b):
    """Diferencia máxima; un NaN en el mismo lugar de los dos lados cuenta como igual, y en uno solo, como infinita."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return float("inf")
    d = np.where(np.isnan(a) & np.isnan(b), 0.0, np.abs(a - b))
    return float(np.max(np.where(np.isnan(d), np.inf, d))) if d.size else 0.0


# %%
# El control: filas de entrenamiento que el Mac puntuó con el código verificado del proyecto.
t = time.perf_counter()
CONTROL = dict(np.load(os.path.join(MODELOS, "control.npz")))
filas_c = META.set_index("isic_id").loc[list(CONTROL["isic_id"])].reset_index().drop(columns=["target"])
red_c = media_de_las_redes(filas_c, TRAIN_HDF5) if con_redes else None
casos = []
if con_redes:
    for i, k in enumerate(inf5b.REDES_DE_C7):
        d = maxima(red_c[0][k], CONTROL["logit_pliegues"][i])
        casos.append({"caso": f"red {k}: logits del control", "ok": d <= TOL["logit"], "debe_fallar": False,
                      "diferencia_maxima": d})
for modelo in a_correr:
    s, intermedio = puntuar(modelo, filas_c, TRAIN_HDF5, red_c)
    d = maxima(s, CONTROL[modelo])
    casos.append({"caso": f"{modelo}: puntuación del control", "ok": d <= TOL["probabilidad"], "debe_fallar": False,
                  "diferencia_maxima": d})
    d_mal = maxima(np.roll(s, 1), CONTROL[modelo])
    casos.append({"caso": f"{modelo}: con las filas corridas una", "ok": d_mal > TOL["probabilidad"],
                  "debe_fallar": True, "diferencia_maxima": d_mal})
    if "z" in intermedio:
        d = maxima(intermedio["z"], CONTROL["z_celda17"])
        casos.append({"caso": f"{modelo}: la variable de la celda 17 del control", "ok": d <= TOL["z"],
                      "debe_fallar": False, "diferencia_maxima": d})
resultado["control"] = {"lesiones": int(len(filas_c)), "tolerancias": TOL, "casos": casos,
                        "fallos": sum(not c["ok"] for c in casos), "segundos": round(time.perf_counter() - t, 1)}
print(json.dumps(resultado["control"], indent=1), flush=True)
if resultado["control"]["fallos"]:
    with open(os.path.join(SALIDA, f"fase5c-{MODO}.json"), "w") as f:
        json.dump(resultado, f, indent=2)
    raise SystemExit("La comprobación del control falló; no se escribe submission.csv.")

# %%
# El tiempo, solo en la medición: las cinco redes sobre recortes de entrenamiento y las variables tabulares con los 45
# CatBoost de cada envío sobre lesiones de entrenamiento, proyectado a N_PRUEBA lesiones.
if MODO == "medicion":
    rng = np.random.default_rng(0)
    muestra = rng.choice(META["isic_id"].to_numpy(), size=N_MUESTRA_IMAGENES, replace=False).tolist()
    t = time.perf_counter()
    inf5b.recorrer(TRAIN_HDF5, muestra, REDES, None, DISPOSITIVO, TRABAJADORES)
    por_imagen = (time.perf_counter() - t) / N_MUESTRA_IMAGENES
    pacientes = rng.permutation(np.array(sorted(META[inf5b.G].astype(str).unique())))
    tamanos = META[inf5b.G].astype(str).value_counts()
    elegidos, total = [], 0
    for p_ in pacientes:
        elegidos.append(p_)
        total += int(tamanos[p_])
        if total >= N_MUESTRA_TABULAR:
            break
    filas_t = META[META[inf5b.G].astype(str).isin(elegidos)].drop(columns=["target"]).reset_index(drop=True)
    p_t = rng.random(len(filas_t))
    tabular = {}
    for modelo in ENVIOS:
        t = time.perf_counter()
        x = inf.variables(modelo, filas_t, AJUSTES[inf.CON_HOSPITAL[modelo]], p_t, TABLA_17)
        inf.puntuar_promedio(MODELOS, modelo, x)
        tabular[modelo] = (time.perf_counter() - t) / len(filas_t)
    fijo = time.perf_counter() - T0
    proyeccion = {}
    for modelo in ENVIOS:
        imagenes = por_imagen if inf.CON_RED[modelo] else 0.0
        horas = (fijo + (imagenes + tabular[modelo]) * N_PRUEBA) / 3600
        proyeccion[modelo] = {"segundos_por_1000_lesiones_imagenes": round(imagenes * 1000, 3),
                              "segundos_por_1000_lesiones_tabular": round(tabular[modelo] * 1000, 3),
                              "horas_proyectadas": round(horas, 2), "cabe_en_el_limite": horas < LIMITE_HORAS}
    resultado["tiempo"] = {"muestra_de_imagenes": N_MUESTRA_IMAGENES, "muestra_tabular": int(len(filas_t)),
                           "lesiones_de_prueba_supuestas": N_PRUEBA, "segundos_fijos_hasta_aqui": round(fijo, 1),
                           "limite_horas": LIMITE_HORAS, "proyeccion": proyeccion,
                           "nota": ("proyección lineal: lo fijo medido en esta corrida más el costo por lesión por "
                                    "N_PRUEBA; la carga de los modelos va en lo fijo")}
    print(json.dumps(resultado["tiempo"], indent=1), flush=True)

# %%
# La prueba.
t = time.perf_counter()
prueba = pd.read_csv(os.path.join(COMPETICION, "test-metadata.csv"), low_memory=False)
hdf5_prueba = os.path.join(COMPETICION, "test-image.hdf5")
red_p = media_de_las_redes(prueba, hdf5_prueba) if con_redes else None
salidas = {}
for modelo in a_correr:
    s, _ = puntuar(modelo, prueba, hdf5_prueba, red_p)
    if len(s) != len(prueba) or not np.all(np.isfinite(s)):
        raise SystemExit(f"{modelo}: puntuaciones faltantes o no finitas en la prueba.")
    salidas[modelo] = s
elegido = ENVIOS[0] if MODO == "medicion" else MODO
pd.DataFrame({"isic_id": prueba["isic_id"], "target": salidas[elegido]}).to_csv(
    os.path.join(SALIDA, "submission.csv"), index=False)
resultado["prueba"] = {"filas": int(len(prueba)), "modelo_en_submission": elegido,
                       "segundos": round(time.perf_counter() - t, 1)}
import catboost  # noqa: E402
import PIL  # noqa: E402
import sklearn  # noqa: E402
import torchvision  # noqa: E402
resultado["versiones"] = {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                          "scikit_learn": sklearn.__version__, "catboost": catboost.__version__,
                          "torch": torch.__version__, "torchvision": torchvision.__version__, "pillow": PIL.__version__}
resultado["segundos_total"] = round(time.perf_counter() - T0, 1)
with open(os.path.join(SALIDA, f"fase5c-{MODO}.json"), "w") as f:
    json.dump(resultado, f, indent=2)
print(json.dumps({k: resultado[k] for k in ("prueba", "versiones", "segundos_total")}, indent=1), flush=True)

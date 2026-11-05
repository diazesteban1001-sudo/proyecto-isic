# %% [markdown]
# # ISIC 2024 — Fase 5b: envío tardío
#
# Notebook de la Fase 5b de `PLAN.md` del proyecto «Agente consultor estadístico — ISIC 2024». Solo predice: los
# modelos se entrenaron fuera de Kaggle con todos los datos de entrenamiento y llegan en un conjunto de datos privado,
# con el código de inferencia (`inferencia_5b.py`). Corre sin internet.
#
# `MODO` elige qué hace:
# - `"medicion"`: la comprobación del control, el tiempo de los cuatro modelos sobre recortes de entrenamiento,
#   proyectado al tamaño de la prueba, y las cuatro puntuaciones de la prueba visible. No es un envío.
# - `"M3limpio"`, `"C7"`, `"Red4e"` o `"ImagenBasicos"`: la comprobación del control y `submission.csv` de ese modelo.
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
MODOS = ("medicion", "M3limpio", "C7", "Red4e", "ImagenBasicos")
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
MODELOS = buscar("inferencia_5b.py")
# El paquete dinov2 viaja en dinov2.zip. Kaggle descomprime los zip de un conjunto de datos al procesarlo y lo deja
# en dinov2/dinov2/; en local, el zip sigue entero y se descomprime en un directorio temporal.
if os.path.isdir(os.path.join(MODELOS, "dinov2", "dinov2")):
    DINOV2_CODIGO = os.path.join(MODELOS, "dinov2")
else:
    import tempfile  # noqa: E402
    import zipfile  # noqa: E402
    DINOV2_CODIGO = os.path.join(tempfile.gettempdir(), "dinov2-codigo")
    with zipfile.ZipFile(os.path.join(MODELOS, "dinov2.zip")) as z:
        z.extractall(DINOV2_CODIGO)
sys.path.insert(0, MODELOS)
sys.path.insert(0, DINOV2_CODIGO)
import inferencia_5b as inf  # noqa: E402

if torch.cuda.is_available():
    DISPOSITIVO = torch.device("cuda")
elif torch.backends.mps.is_available():
    DISPOSITIVO = torch.device("mps")
else:
    DISPOSITIVO = torch.device("cpu")
TRABAJADORES = int(os.environ.get("TRABAJADORES", min(4, os.cpu_count() or 1)))
TRAIN_HDF5 = os.path.join(COMPETICION, "train-image.hdf5")
TOL = {"logit": 1e-2, "dinov2": 1e-2, "probabilidad": 1e-3}
N_PRUEBA = 500_000  # "Test data comprised about 500,000 lesion tiles" (Kurtansky et al. 2025, métodos)
N_MUESTRA_IMAGENES = 4096
N_MUESTRA_TABULAR = 20_000
LIMITE_HORAS = 12  # "CPU Notebook <= 12 hours run-time", "GPU Notebook <= 12 hours run-time"
NECESITA = {"M3limpio": ([], False), "C7": (inf.REDES_DE_C7, False), "Red4e": (["sola"], False),
            "ImagenBasicos": ([], True)}
resultado = {"modo": MODO, "dispositivo": str(DISPOSITIVO),
             "gpu": torch.cuda.get_device_name(0) if DISPOSITIVO.type == "cuda" else None,
             "trabajadores": TRABAJADORES, "entrada": {"competicion": COMPETICION, "modelos": MODELOS}}
print(resultado, flush=True)

# %%
# Los modelos: solo los que el modo necesita.
necesarios = sorted({r for m in (NECESITA if MODO == "medicion" else [MODO]) for r in NECESITA[m][0]})
con_dinov2 = MODO in ("medicion", "ImagenBasicos")
t = time.perf_counter()
REDES = {k: inf.red(os.path.join(MODELOS, f"red-{k}.pt"), DISPOSITIVO) for k in necesarios}
DINOV2 = inf.dinov2(os.path.join(MODELOS, "dinov2_vits14_pretrain.pth"), DISPOSITIVO) if con_dinov2 else None
AJUSTE_M3 = inf.cargar_ajuste_m3(MODELOS)
resultado["segundos_carga_de_modelos"] = round(time.perf_counter() - t, 1)
META = pd.read_csv(os.path.join(COMPETICION, "train-metadata.csv"), low_memory=False)


def puntuar(modelo, filas, hdf5, redes, dino):
    """Las puntuaciones de un modelo para filas (sin etiqueta) y sus imágenes, y lo
    intermedio que se compara en el control."""
    ids = filas["isic_id"].tolist()
    grupos = filas[inf.G].astype(str).to_numpy()
    nombres, con_d = NECESITA[modelo]
    logits, caracteristicas = inf.recorrer(hdf5, ids, {k: redes[k] for k in nombres},
                                           dino if con_d else None, DISPOSITIVO, TRABAJADORES) \
        if (nombres or con_d) else ({}, None)
    if modelo == "M3limpio":
        x, _ = inf.variables_m3(filas, AJUSTE_M3)
        return inf.puntuar_cbm(os.path.join(MODELOS, "m3limpio.cbm"), x), {}
    if modelo == "C7":
        x, _ = inf.variables_m3(filas, AJUSTE_M3)
        p = np.mean([inf.probabilidad(logits[k]) for k in inf.REDES_DE_C7], axis=0)
        return inf.puntuar_cbm(os.path.join(MODELOS, "c7.cbm"), inf.variables_c7(x, p, grupos)), logits
    if modelo == "Red4e":
        return inf.probabilidad(logits["sola"]), logits
    return inf.puntuar_imagen_basicos(filas, caracteristicas, MODELOS), {"dinov2": caracteristicas}


def maxima(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.max(np.abs(a - b))) if a.shape == b.shape else float("inf")


# %%
# El control: filas de entrenamiento que el Mac puntuó con el código verificado del proyecto.
t = time.perf_counter()
CONTROL = dict(np.load(os.path.join(MODELOS, "control.npz")))
filas_c = META.set_index("isic_id").loc[list(CONTROL["isic_id"])].reset_index().drop(columns=["target"])
casos = []
referencia = {"M3limpio": CONTROL["m3limpio"], "C7": CONTROL["c7"], "Red4e": inf.probabilidad(CONTROL["logit_sola"]),
              "ImagenBasicos": CONTROL["imagen_basicos"]}
for modelo in (NECESITA if MODO == "medicion" else [MODO]):
    s, intermedio = puntuar(modelo, filas_c, TRAIN_HDF5, REDES, DINOV2)
    d = maxima(s, referencia[modelo])
    casos.append({"caso": f"{modelo}: puntuación del control", "ok": d <= TOL["probabilidad"], "debe_fallar": False,
                  "diferencia_maxima": d})
    d_mal = maxima(np.roll(s, 1), referencia[modelo])
    casos.append({"caso": f"{modelo}: con las filas corridas una", "ok": d_mal > TOL["probabilidad"],
                  "debe_fallar": True, "diferencia_maxima": d_mal})
    for k, v in intermedio.items():
        if k == "dinov2":
            d = maxima(v, CONTROL["dinov2"])
            casos.append({"caso": "DINOv2: variables del control", "ok": d <= TOL["dinov2"], "debe_fallar": False,
                          "diferencia_maxima": d})
        else:
            ref = CONTROL["logit_sola"] if k == "sola" else CONTROL["logit_pliegues"][inf.REDES_DE_C7.index(k)]
            d = maxima(v, ref)
            casos.append({"caso": f"red {k}: logits del control", "ok": d <= TOL["logit"], "debe_fallar": False,
                          "diferencia_maxima": d})
resultado["control"] = {"lesiones": int(len(filas_c)), "tolerancias": TOL, "casos": casos,
                        "fallos": sum(not c["ok"] for c in casos), "segundos": round(time.perf_counter() - t, 1)}
print(json.dumps(resultado["control"], indent=1), flush=True)
if resultado["control"]["fallos"]:
    with open(os.path.join(SALIDA, f"fase5b-{MODO}.json"), "w") as f:
        json.dump(resultado, f, indent=2)
    raise SystemExit("La comprobación del control falló; no se escribe submission.csv.")

# %%
# El tiempo, solo en la medición: imágenes y variables tabulares de entrenamiento, proyectado a N_PRUEBA lesiones.
if MODO == "medicion":
    rng = np.random.default_rng(0)
    muestra = rng.choice(META["isic_id"].to_numpy(), size=N_MUESTRA_IMAGENES, replace=False).tolist()
    imagenes = {}
    for modelo, (nombres, con_d) in NECESITA.items():
        if not (nombres or con_d):
            continue
        t = time.perf_counter()
        inf.recorrer(TRAIN_HDF5, muestra, {k: REDES[k] for k in nombres}, DINOV2 if con_d else None, DISPOSITIVO,
                     TRABAJADORES)
        imagenes[modelo] = (time.perf_counter() - t) / N_MUESTRA_IMAGENES
    pacientes = rng.permutation(np.array(sorted(META[inf.G].astype(str).unique())))
    tamanos = META[inf.G].astype(str).value_counts()
    elegidos, total = [], 0
    for p in pacientes:
        elegidos.append(p)
        total += int(tamanos[p])
        if total >= N_MUESTRA_TABULAR:
            break
    filas_t = META[META[inf.G].astype(str).isin(elegidos)].drop(columns=["target"]).reset_index(drop=True)
    tabular = {}
    t = time.perf_counter()
    x, _ = inf.variables_m3(filas_t, AJUSTE_M3)
    t_x = time.perf_counter() - t
    t = time.perf_counter()
    inf.puntuar_cbm(os.path.join(MODELOS, "m3limpio.cbm"), x)
    tabular["M3limpio"] = (t_x + time.perf_counter() - t) / len(filas_t)
    t = time.perf_counter()
    p = rng.random(len(filas_t))
    inf.puntuar_cbm(os.path.join(MODELOS, "c7.cbm"), inf.variables_c7(x, p, filas_t[inf.G].astype(str).to_numpy()))
    tabular["C7"] = (t_x + time.perf_counter() - t) / len(filas_t)
    t = time.perf_counter()
    inf.basicos(filas_t, inf.leer_json(os.path.join(MODELOS, "imagen-basicos.json")))
    tabular["ImagenBasicos"] = (time.perf_counter() - t) / len(filas_t)
    tabular["Red4e"] = 0.0
    fijo = time.perf_counter() - T0
    proyeccion = {}
    for modelo in NECESITA:
        por_lesion = imagenes.get(modelo, 0.0) + tabular[modelo]
        horas = (fijo + por_lesion * N_PRUEBA) / 3600
        proyeccion[modelo] = {"segundos_por_1000_lesiones_imagenes": round(imagenes.get(modelo, 0.0) * 1000, 3),
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
salidas = {}
for modelo in (NECESITA if MODO == "medicion" else [MODO]):
    s, _ = puntuar(modelo, prueba, hdf5_prueba, REDES, DINOV2)
    if len(s) != len(prueba) or not np.all(np.isfinite(s)):
        raise SystemExit(f"{modelo}: puntuaciones faltantes o no finitas en la prueba.")
    salidas[modelo] = s
elegido = "M3limpio" if MODO == "medicion" else MODO
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
with open(os.path.join(SALIDA, f"fase5b-{MODO}.json"), "w") as f:
    json.dump(resultado, f, indent=2)
print(json.dumps({k: resultado[k] for k in ("prueba", "versiones", "segundos_total")}, indent=1), flush=True)

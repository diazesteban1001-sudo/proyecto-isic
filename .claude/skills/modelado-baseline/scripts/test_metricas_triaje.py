#!/usr/bin/env python3
"""
test_metricas_triaje.py — pruebas de SEtop-15 y NNT80% SE (metricas_triaje.py).

Tres partes.

1. Casos sintéticos con el valor calculado a mano, escrito en el propio caso.
2. Control positivo: las pruebas pueden fallar. Cada métrica se sustituye por
   versiones mutadas —cada una, un error plausible— y se comprueba que al menos
   un caso de la parte 1 detecta cada mutante. Un mutante que ninguna prueba
   detecta dejaría ese error sin vigilar.
3. SEtop-15 frente al guion del organizador, SecondaryMetric-TopNSensitivity.py,
   ejecutado sin modificar sobre seis conjuntos sintéticos con empates. Necesita
   la copia local del guion (referencias/_texto-completo/, que no se versiona) y
   un intérprete con pandas < 3: el guion es de 2024, y con pandas 3 su
   groupby(...).apply ya no conserva la columna de agrupación y la línea 125
   falla. El intérprete se indica con la variable de entorno PYTHON_GUION_ISIC.
   Si falta el guion o el intérprete, la parte sale como NO CORRIDA, a la vista.

Uso:
    python .claude/skills/modelado-baseline/scripts/test_metricas_triaje.py
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import metricas_triaje as mt  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
GUION = os.path.join(RAIZ, "referencias", "_texto-completo", "upstream-SecondaryMetric-TopNSensitivity.py")
PYTHON_GUION = os.environ.get("PYTHON_GUION_ISIC")


# ---- 1. Casos calculables a mano ----------------------------------------------

def caso_setop_pesos_por_paciente():
    """Paciente A: 20 lesiones, 2 malignas, una en el puesto 1 y otra en el 16:
    encuentra 1 de 2. Paciente B: 5 lesiones, 1 maligna: 1 de 1. Paciente C:
    sin malignas, no cuenta. SEtop-15 = (1/2 + 1) / 2 = 0,75. Con peso por
    lesión saldría 2/3."""
    y, s, g = [], [], []
    for i in range(20):
        g.append("A"); s.append(100 - i); y.append(int(i in (0, 15)))
    for i in range(5):
        g.append("B"); s.append(50 - i); y.append(int(i == 4))
    for i in range(30):
        g.append("C"); s.append(10 - i / 10); y.append(0)
    return mt.setop_n(y, s, g), 0.75


def caso_setop_puesto_15():
    """Paciente A: 20 lesiones con puntuaciones distintas y la maligna en el
    puesto 15, dentro: 1. Paciente B: igual, con la maligna en el puesto 16,
    fuera: 0. SEtop-15 = 0,5."""
    y, s, g = [], [], []
    for paciente, puesto in (("A", 15), ("B", 16)):
        for i in range(20):
            g.append(paciente); s.append(100 - i); y.append(int(i == puesto - 1))
    return mt.setop_n(y, s, g), 0.5


def caso_setop_empates_en_el_borde():
    """Paciente A: 16 lesiones con la misma puntuación y la maligna en el puesto
    16; con keep="first" queda fuera: 0. Paciente B: puntuaciones distintas y la
    maligna en el puesto 1: 1. SEtop-15 = 0,5. Si en el empate se quedara con
    las últimas, A daría 1 y la media, 1."""
    y, s, g = [], [], []
    for i in range(16):
        g.append("A"); s.append(0.5); y.append(int(i == 15))
    for i in range(16):
        g.append("B"); s.append(1 - i / 100); y.append(int(i == 0))
    return mt.setop_n(y, s, g), 0.5


def caso_nnt_basico():
    """5 malignas con puntuaciones 0,9, 0,8, 0,7, 0,6 y 0,1; negativas 0,95,
    0,65, 0,5 y 0,2. Para el 80 % hay que capturar 4: umbral 0,6. Marcadas:
    4 malignas y 2 negativas (0,95 y 0,65). NNT = 6 / 4 = 1,5."""
    y = [1, 1, 1, 1, 1, 0, 0, 0, 0]
    s = [0.9, 0.8, 0.7, 0.6, 0.1, 0.95, 0.65, 0.5, 0.2]
    return mt.nnt_a_sensibilidad(y, s), 1.5


def caso_nnt_redondeo_hacia_arriba():
    """4 malignas: el 80 % son 3,2, así que hay que capturar 4, todas. Umbral:
    la maligna más baja, 0,3. Marcadas: 4 malignas y las 3 negativas por encima
    (0,9, 0,5 y 0,4). NNT = 7 / 4 = 1,75."""
    y = [1, 1, 1, 1, 0, 0, 0, 0]
    s = [0.8, 0.7, 0.6, 0.3, 0.9, 0.5, 0.4, 0.1]
    return mt.nnt_a_sensibilidad(y, s), 1.75


def caso_nnt_empate_en_el_umbral():
    """Como el básico, pero una negativa empata con el umbral, 0,6: entra.
    Marcadas: 4 malignas y 3 negativas. NNT = 7 / 4 = 1,75."""
    y = [1, 1, 1, 1, 1, 0, 0, 0]
    s = [0.9, 0.8, 0.7, 0.6, 0.1, 0.95, 0.65, 0.6]
    return mt.nnt_a_sensibilidad(y, s), 1.75


CASOS_SETOP = [caso_setop_pesos_por_paciente, caso_setop_puesto_15, caso_setop_empates_en_el_borde]
CASOS_NNT = [caso_nnt_basico, caso_nnt_redondeo_hacia_arriba, caso_nnt_empate_en_el_umbral]


def correr(casos):
    return {c.__name__: (lambda r: abs(r[0] - r[1]) < 1e-12)(c()) for c in casos}


# ---- 2. Mutantes ----------------------------------------------------------------

def setop_por_lesion(y_true, y_score, grupos, n=mt.TOP_N):
    df = pd.DataFrame({"y": np.asarray(y_true), "s": np.asarray(y_score, float), "g": np.asarray(grupos)})
    df = df[df.groupby("g")["y"].transform("sum") > 0]
    df = df.iloc[np.argsort(-df["s"].to_numpy(), kind="stable")]
    return float(df[df.groupby("g").cumcount() < n]["y"].sum() / df["y"].sum())


def setop_top14(y_true, y_score, grupos, n=mt.TOP_N):
    return ORIGINAL_SETOP(y_true, y_score, grupos, n=14)


def setop_ultimos_en_empate(y_true, y_score, grupos, n=mt.TOP_N):
    # Invierte el orden de aparición: en un empate se queda con las últimas.
    y, s, g = (np.asarray(v)[::-1] for v in (y_true, y_score, grupos))
    return ORIGINAL_SETOP(y, s, g, n=n)


def nnt_redondeo_abajo(y_true, y_score, sensibilidad=mt.SENSIBILIDAD_NNT):
    y = np.asarray(y_true).astype(bool); s = np.asarray(y_score, float)
    k = max(1, int(np.floor(sensibilidad * y.sum())))
    umbral = np.sort(s[y])[::-1][k - 1]
    m = s >= umbral
    return float(m.sum() / (m & y).sum())


def nnt_falsos_sobre_verdaderos(y_true, y_score, sensibilidad=mt.SENSIBILIDAD_NNT):
    y = np.asarray(y_true).astype(bool); s = np.asarray(y_score, float)
    k = int(np.ceil(sensibilidad * y.sum() - 1e-9))
    umbral = np.sort(s[y])[::-1][k - 1]
    m = s >= umbral
    return float((m & ~y).sum() / (m & y).sum())


def nnt_umbral_estricto(y_true, y_score, sensibilidad=mt.SENSIBILIDAD_NNT):
    y = np.asarray(y_true).astype(bool); s = np.asarray(y_score, float)
    k = int(np.ceil(sensibilidad * y.sum() - 1e-9))
    umbral = np.sort(s[y])[::-1][k - 1]
    m = (s > umbral) | ((s == umbral) & y)  # los empates negativos no entran
    return float(m.sum() / (m & y).sum())


ORIGINAL_SETOP, ORIGINAL_NNT = mt.setop_n, mt.nnt_a_sensibilidad


def detectado(mutante, nombre_funcion, casos):
    original = getattr(mt, nombre_funcion)
    setattr(mt, nombre_funcion, mutante)
    try:
        return [n for n, ok in correr(casos).items() if not ok]
    finally:
        setattr(mt, nombre_funcion, original)


# ---- 3. SEtop-15 frente al guion oficial ---------------------------------------

def datos_aleatorios(semilla):
    rng = np.random.default_rng(semilla)
    filas = []
    for p in range(40):
        n = int(rng.integers(1, 45))
        for j in range(n):
            filas.append((f"ISIC_{semilla}_{p}_{j}", f"P{p}", int(rng.random() < 0.08),
                          round(float(rng.random()), 2)))  # dos decimales: fuerza empates
    return pd.DataFrame(filas, columns=["isic_id", "patient_id", "target", "score"])


def guion_oficial(df, tmp):
    carpeta = os.path.join(tmp, "metrica")
    os.makedirs(carpeta, exist_ok=True)
    shutil.copy(GUION, os.path.join(carpeta, "guion.py"))
    df.assign(split="private")[["isic_id", "patient_id", "target", "split"]].to_csv(
        os.path.join(carpeta, "test-gt.csv"), index=False)
    # El guion busca los envíos con directory + "\\*.csv", un patrón de Windows. En
    # macOS casa con archivos del directorio padre cuyo nombre empieza por
    # "envios\"; así se ejecuta sin cambiarle una línea.
    envios = os.path.join(tmp, "envios")
    os.makedirs(envios, exist_ok=True)
    df.rename(columns={"isic_id": "filenames", "score": "Predictions"})[["filenames", "Predictions"]].to_csv(
        os.path.join(tmp, "envios\\envio.csv"), index=False)
    salida = os.path.join(tmp, "clasificacion.csv")
    subprocess.run([PYTHON_GUION, os.path.join(carpeta, "guion.py"), "--directory", envios, "-l", salida],
                   check=True, capture_output=True, cwd=tmp)
    return float(pd.read_csv(salida)["average ranks"].iloc[0])


def main():
    fallos = 0
    print("1. Casos calculables a mano")
    for c in CASOS_SETOP + CASOS_NNT:
        valor, esperado = c()
        ok = abs(valor - esperado) < 1e-12
        fallos += not ok
        print(f"   [{'OK' if ok else 'FALLA'}] {c.__name__}: {valor} (a mano: {esperado})")

    print("2. Control positivo: cada mutante lo detecta al menos un caso")
    for mutante, funcion, casos in [
        (setop_por_lesion, "setop_n", CASOS_SETOP),
        (setop_top14, "setop_n", CASOS_SETOP),
        (setop_ultimos_en_empate, "setop_n", CASOS_SETOP),
        (nnt_redondeo_abajo, "nnt_a_sensibilidad", CASOS_NNT),
        (nnt_falsos_sobre_verdaderos, "nnt_a_sensibilidad", CASOS_NNT),
        (nnt_umbral_estricto, "nnt_a_sensibilidad", CASOS_NNT),
    ]:
        quien = detectado(mutante, funcion, casos)
        fallos += not quien
        print(f"   [{'OK' if quien else 'FALLA'}] {mutante.__name__}: detectado por {quien or 'ningún caso'}")

    print("3. SEtop-15 frente al guion oficial, sin modificar")
    if not os.path.exists(GUION):
        print(f"   [NO CORRIDA] no existe {GUION}")
    elif not PYTHON_GUION:
        print("   [NO CORRIDA] falta PYTHON_GUION_ISIC, un intérprete con pandas < 3 para el guion")
    else:
        version = subprocess.run([PYTHON_GUION, "-c", "import pandas; print(pandas.__version__)"],
                                 capture_output=True, text=True, check=True).stdout.strip()
        print(f"   intérprete del guion: {PYTHON_GUION} (pandas {version})")
        for semilla in range(6):
            df = datos_aleatorios(semilla)
            with tempfile.TemporaryDirectory() as tmp:
                oficial = guion_oficial(df, tmp)
            propio = mt.setop_n(df["target"], df["score"], df["patient_id"])
            # La comparación discrimina: la versión con peso por lesión no coincide.
            por_lesion = setop_por_lesion(df["target"], df["score"], df["patient_id"])
            ok = abs(oficial - propio) < 1e-12 and abs(oficial - por_lesion) > 1e-6
            fallos += not ok
            print(f"   [{'OK' if ok else 'FALLA'}] semilla {semilla}: oficial {oficial:.15f} · propio {propio:.15f}"
                  f" · con peso por lesión {por_lesion:.6f}")

    print(f"\n{'Todo como se esperaba.' if not fallos else f'{fallos} fallos.'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

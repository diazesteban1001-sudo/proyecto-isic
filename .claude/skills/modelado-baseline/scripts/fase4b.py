#!/usr/bin/env python3
"""
fase4b.py — las piezas de la Fase 4b (PLAN.md, decisión de la persona del
2026-10-22) que comparten los tres candidatos y sus controles. No corre ningún
candidato: test_fase4b_controles.py las controla antes.

- rango_promedio(a, b): la mezcla de C1 y C3. El promedio simple de los rangos de
  dos puntuaciones del mismo pliegue de validación, con pesos 1/2 y 1/2 fijos.
  Los empates reciben el rango promedio, scipy.stats.rankdata(method="average").
  No lee etiquetas.
- con_imagen(x_tr, x_va, ap): las variables de C2. Añade a las de M3 limpio de un
  pliegue las dos de imagen de M4b, tal como las devuelve
  apilado_imagen.puntuaciones_imagen para ese pliegue: calculadas sobre todas las
  filas del pliegue de entrenamiento, antes del remuestreo de M3 limpio, que las
  arrastra como dos columnas más.
- ajustar_nivel_2b(x_tr, y_tr, semilla) y puntuar_nivel_2b(modelo, x): el segundo
  modelo de C3, el del nivel 2b sin cambios. Las columnas `category` —las one-hot
  de M3 limpio, que CatBoost recibe como categóricas— pasan antes a enteros, y el
  ajuste se detiene si el modelo trata alguna variable como categórica.
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

# Los mismos nombres que fase4_comparar.APILADAS, para que C2 y M4b llamen igual a
# sus dos variables de imagen. test_fase4b_controles.py comprueba que coinciden.
COLUMNAS_IMAGEN = ["img_lr_puntuacion", "img_lr_razon_paciente"]


def rango_promedio(a, b):
    """0,5 · rango(a) + 0,5 · rango(b), con los empates en su rango promedio."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError(f"rango_promedio necesita dos vectores del mismo largo: {a.shape} y {b.shape}.")
    if np.isnan(a).any() or np.isnan(b).any():
        raise ValueError("rango_promedio recibió puntuaciones faltantes.")
    return 0.5 * rankdata(a, method="average") + 0.5 * rankdata(b, method="average")


def con_imagen(x_tr, x_va, ap):
    """Las variables de M3 limpio de un pliegue más las dos de imagen de M4b. x_tr y
    x_va están en el orden de tr y de va, el mismo de los arrays de ap."""
    pares = ((x_tr, ap["tr"]), (x_va, ap["va"]))
    salida = []
    for x, a in pares:
        if len(x) != len(a["puntuacion"]) or len(x) != len(a["razon"]):
            raise ValueError("Las variables de imagen no tienen el largo de las de M3 limpio.")
        x = x.copy()
        x[COLUMNAS_IMAGEN[0]] = np.asarray(a["puntuacion"], dtype=float)
        x[COLUMNAS_IMAGEN[1]] = np.asarray(a["razon"], dtype=float)
        salida.append(x)
    return tuple(salida)


def a_numeros(x):
    """Las columnas `category` de un DataFrame, como enteros con sus mismos valores.
    Un array de numpy pasa sin cambios."""
    if not isinstance(x, pd.DataFrame):
        return x
    x = x.copy()
    for c in x.columns:
        if isinstance(x[c].dtype, pd.CategoricalDtype):
            x[c] = pd.to_numeric(x[c].astype(object), errors="raise").astype("int64")
    return x


def ajustar_nivel_2b(x_tr, y_tr, semilla):
    """El nivel 2b sin cambios: HistGradientBoostingClassifier(class_weight="balanced",
    random_state=semilla), con todo lo demás por defecto, incluida su parada temprana.
    Ninguna variable entra como categórica."""
    modelo = HistGradientBoostingClassifier(class_weight="balanced", random_state=semilla)
    modelo.fit(a_numeros(x_tr), y_tr)
    categoricas = modelo.is_categorical_
    if categoricas is not None and np.any(categoricas):
        raise SystemExit(f"ERROR: el nivel 2b de C3 trata {int(np.sum(categoricas))} variables como categóricas; "
                         "tienen que entrar como números.")
    return modelo


def puntuar_nivel_2b(modelo, x):
    return modelo.predict_proba(a_numeros(x))[:, 1]

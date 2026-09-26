#!/usr/bin/env python3
"""
apilado_imagen.py — las dos variables de imagen de la variante secundaria M4b
(PLAN.md, Fase 4; especificación y detalles fijados el 2026-09-25 antes de
correr).

Dentro de cada fold externo (tr, va):
- una regresión logística con pesos balanceados, C por defecto y max_iter=2000,
  en un pipeline con el estandarizado, sobre las 384 variables de DINOv2;
- la puntuación es predict_proba[:, 1]. En las filas de entrenamiento sale fuera
  de pliegue, de una validación interna StratifiedGroupKFold de 5 pliegues
  agrupada por paciente, estratificada y con la semilla externa. En las de
  validación sale del modelo ajustado sobre todo el fold de entrenamiento;
- la segunda variable es esa puntuación dividida por su media dentro del
  paciente, sobre puntuaciones del mismo tipo: las de entrenamiento, contra las
  del mismo paciente en entrenamiento; las de validación, contra las del mismo
  paciente en validación. Los pacientes no se reparten entre los dos lados.

Devuelve además qué modelo puntuó cada fila de entrenamiento y con qué filas se
ajustó cada modelo, para que el control positivo (test_apilado_imagen.py) pueda
comprobar que ninguna fila recibe una puntuación de un modelo que la vio.
"""

import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PLIEGUES_INTERNOS = 5


def modelo_imagen():
    return make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000))


def razon_paciente(p, grupos):
    """p dividida por la media de p dentro de cada paciente."""
    s = pd.Series(p)
    return (s / s.groupby(np.asarray(grupos)).transform("mean")).to_numpy()


def puntuaciones_imagen(x, y, grupos, tr, va, semilla):
    """Puntuaciones y razones de imagen para las filas tr (fuera de pliegue) y va
    (del modelo del fold). Índices tr y va sobre x, y y grupos."""
    oof = np.full(len(tr), np.nan)
    modelo_de_fila = np.full(len(tr), -1)
    filas_de_modelo = []
    interna = StratifiedGroupKFold(n_splits=PLIEGUES_INTERNOS, shuffle=True, random_state=semilla)
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always", ConvergenceWarning)
        for k, (itr, iva) in enumerate(interna.split(x[tr], y[tr], groups=grupos[tr])):
            m = modelo_imagen().fit(x[tr[itr]], y[tr[itr]])
            oof[iva] = m.predict_proba(x[tr[iva]])[:, 1]
            modelo_de_fila[iva] = k
            filas_de_modelo.append(tr[itr])
        completo = modelo_imagen().fit(x[tr], y[tr])
        val = completo.predict_proba(x[va])[:, 1]
        filas_de_modelo.append(tr)  # el último modelo, el completo, solo puntúa validación
    n_avisos = sum(1 for a in avisos if issubclass(a.category, ConvergenceWarning))
    return {
        "tr": {"puntuacion": oof, "razon": razon_paciente(oof, grupos[tr])},
        "va": {"puntuacion": val, "razon": razon_paciente(val, grupos[va])},
        "modelo_de_fila_tr": modelo_de_fila,
        "filas_de_modelo": filas_de_modelo,
        "avisos_no_convergencia": n_avisos,
    }

#!/usr/bin/env python3
"""
test_apilado_imagen.py — control positivo de fuga del apilado de imagen de M4b
(apilado_imagen.py). Con datos sintéticos, antes de la corrida real.

  (a) Barajar las etiquetas del fold de validación no cambia sus puntuaciones de
      imagen, ni las de entrenamiento.
  (b) Ninguna fila de entrenamiento recibe una puntuación de un modelo que la
      vio. Se comprueba también por paciente, que es más estricto: ningún
      paciente se puntúa con un modelo ajustado con alguna de sus lesiones.

Cada comprobación puede fallar, y se demuestra: se aplica a una versión mutada,
hecha para incumplirla, y tiene que detectarla.
  - mutante de (a): el modelo de validación se ajusta con el fold de validación
    incluido;
  - mutante de (b): las filas de entrenamiento se puntúan con el modelo completo,
    que las vio;
  - mutante de (b) por paciente: la validación interna no agrupa por paciente.
    Por fila no hay fuga, así que la comprobación por fila no lo ve; por
    paciente sí.

Uso:
    python .claude/skills/modelado-baseline/scripts/test_apilado_imagen.py
Devuelve 0 si todos los casos se comportan como se espera.
"""

import os
import sys
import warnings

import numpy as np
from sklearn.model_selection import KFold, StratifiedGroupKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apilado_imagen as ai  # noqa: E402

warnings.filterwarnings("ignore")


def sintetico(semilla=0):
    rng = np.random.default_rng(semilla)
    grupos, filas = [], []
    for p in range(80):
        n = int(rng.integers(5, 40))
        grupos += [f"P{p}"] * n
    n = len(grupos)
    y = (rng.random(n) < 0.08).astype(int)
    x = rng.normal(size=(n, 12)) + y[:, None] * 0.8
    grupos = np.array(grupos)
    tr, va = next(StratifiedGroupKFold(5, shuffle=True, random_state=semilla).split(x, y, groups=grupos))
    return x, y, grupos, tr, va


# ---- mutantes ----------------------------------------------------------------

def mutante_valida_con_su_fold(x, y, grupos, tr, va, semilla):
    r = ai.puntuaciones_imagen(x, y, grupos, tr, va, semilla)
    todo = np.concatenate([tr, va])
    m = ai.modelo_imagen().fit(x[todo], y[todo])  # fuga: ve las etiquetas de validación
    r["va"]["puntuacion"] = m.predict_proba(x[va])[:, 1]
    return r


def mutante_entrena_dentro_de_muestra(x, y, grupos, tr, va, semilla):
    r = ai.puntuaciones_imagen(x, y, grupos, tr, va, semilla)
    completo = ai.modelo_imagen().fit(x[tr], y[tr])
    r["tr"]["puntuacion"] = completo.predict_proba(x[tr])[:, 1]
    r["modelo_de_fila_tr"] = np.full(len(tr), len(r["filas_de_modelo"]) - 1)  # el completo, que vio todo tr
    return r


def mutante_interna_sin_agrupar(x, y, grupos, tr, va, semilla):
    oof = np.full(len(tr), np.nan)
    modelo_de_fila = np.full(len(tr), -1)
    filas_de_modelo = []
    for k, (itr, iva) in enumerate(KFold(5, shuffle=True, random_state=semilla).split(x[tr])):
        m = ai.modelo_imagen().fit(x[tr[itr]], y[tr[itr]])
        oof[iva] = m.predict_proba(x[tr[iva]])[:, 1]
        modelo_de_fila[iva] = k
        filas_de_modelo.append(tr[itr])
    filas_de_modelo.append(tr)
    return {"tr": {"puntuacion": oof}, "modelo_de_fila_tr": modelo_de_fila, "filas_de_modelo": filas_de_modelo}


# ---- comprobaciones ------------------------------------------------------------

def comprobacion_a(funcion, x, y, grupos, tr, va, semilla):
    """True si barajar las etiquetas de validación no cambia ninguna puntuación."""
    r1 = funcion(x, y, grupos, tr, va, semilla)
    y2 = y.copy()
    y2[va] = np.random.default_rng(99).permutation(y[va])
    r2 = funcion(x, y2, grupos, tr, va, semilla)
    return (np.array_equal(r1["va"]["puntuacion"], r2["va"]["puntuacion"])
            and np.array_equal(r1["tr"]["puntuacion"], r2["tr"]["puntuacion"]))


def comprobacion_b(r, tr, grupos, por_paciente):
    """True si ninguna fila de entrenamiento (o ningún paciente, si por_paciente)
    se puntúa con un modelo ajustado con ella."""
    if (r["modelo_de_fila_tr"] < 0).any() or np.isnan(r["tr"]["puntuacion"]).any():
        return False
    for k, filas in enumerate(r["filas_de_modelo"]):
        puntuadas = tr[r["modelo_de_fila_tr"] == k]
        if por_paciente:
            if set(grupos[puntuadas]) & set(grupos[filas]):
                return False
        elif set(puntuadas) & set(filas):
            return False
    return True


def main():
    casos = []
    for semilla in (0, 1, 2):
        x, y, g, tr, va = sintetico(semilla)
        r = ai.puntuaciones_imagen(x, y, g, tr, va, semilla)
        casos += [
            (f"semilla {semilla} · (a) barajar la validación no cambia las puntuaciones",
             comprobacion_a(ai.puntuaciones_imagen, x, y, g, tr, va, semilla)),
            (f"semilla {semilla} · (b) ninguna fila, puntuada por un modelo que la vio",
             comprobacion_b(r, tr, g, por_paciente=False)),
            (f"semilla {semilla} · (b) ningún paciente, puntuado por un modelo que lo vio",
             comprobacion_b(r, tr, g, por_paciente=True)),
            (f"semilla {semilla} · control: (a) detecta el mutante que valida con su fold",
             not comprobacion_a(mutante_valida_con_su_fold, x, y, g, tr, va, semilla)),
            (f"semilla {semilla} · control: (b) detecta el mutante dentro de muestra",
             not comprobacion_b(mutante_entrena_dentro_de_muestra(x, y, g, tr, va, semilla), tr, g, por_paciente=False)),
        ]
        sin_agrupar = mutante_interna_sin_agrupar(x, y, g, tr, va, semilla)
        casos += [
            (f"semilla {semilla} · control: el mutante sin agrupar pasa (b) por fila",
             comprobacion_b(sin_agrupar, tr, g, por_paciente=False)),
            (f"semilla {semilla} · control: (b) por paciente sí lo detecta",
             not comprobacion_b(sin_agrupar, tr, g, por_paciente=True)),
        ]
        razones_ok = np.allclose(r["tr"]["razon"], ai.razon_paciente(r["tr"]["puntuacion"], g[tr]))
        casos.append((f"semilla {semilla} · la razón de entrenamiento usa las puntuaciones fuera de pliegue", razones_ok))

    fallos = 0
    for titulo, ok in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

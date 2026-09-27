#!/usr/bin/env python3
"""
test_m3_limpio.py — control positivo de M3 limpio (PLAN.md, Fase 4): las
variables de variables_m3_en_pliegue y el ajuste con PARAMETROS_LIMPIO, de
ganador_m3.py. Antes de la corrida.

  G. Las transformaciones de validación no dependen de sus propias filas. Con
     datos sintéticos, se cambian todas las filas de validación salvo las de un
     paciente P: no cambia ninguna variable de entrenamiento ni ninguna de P. La
     comprobación puede fallar, y se demuestra: con las variables de M3, que
     ajustan las transformaciones sobre todas las filas, P sí cambia.
  H. Con las filas de validación fuera, el lado de entrenamiento es el M3 ya
     verificado: sus variables coinciden con las de variables_m3 sobre esas
     mismas filas.
  I. Las 22 columnas de la celda 24, que M3 limpio no descarta, no están entre
     las que excluye auditoria-de-fugas. Tampoco dependen de ellas: en una
     muestra del conjunto de desarrollo real se alteran todas las columnas
     excluidas, y ninguna variable cambia.
  J. El ajuste de M3 limpio usa la parada de M3 y los valores por defecto de
     CatBoost en todo lo demás, sin pesos de clase. Barajar las etiquetas de
     validación no lo cambia.

Uso:
    python .claude/skills/modelado-baseline/scripts/test_m3_limpio.py
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ganador_m3 as g  # noqa: E402

RAIZ = g.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HOLDOUT = os.path.join(RAIZ, "outputs", "holdout-pacientes.json")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
warnings.filterwarnings("ignore")
L = g.listas_publicadas()


def sintetico(semilla=0, pacientes=60):
    rng = np.random.default_rng(semilla)
    filas = []
    for p in range(pacientes):
        n = 2 if p % 7 == 0 else int(rng.integers(3, 60))
        edad = np.nan if p % 9 == 0 else float(rng.integers(30, 80))
        for j in range(n):
            fila = {c: float(rng.uniform(1, 20)) for c in L["num_cols"]}
            fila.update({"patient_id": f"P{p}", "age_approx": edad, "sex": ["male", "female", None][p % 3],
                         "anatom_site_general": ["torso", None, "pierna", "brazo"][j % 4],
                         "tbp_tile_type": ["3D: XP", "3D: white"][j % 2],
                         "tbp_lv_location": ["Torso", "Pierna", "Brazo"][j % 3],
                         "tbp_lv_location_simple": ["Torso", "Pierna"][j % 2],
                         "attribution": f"Centro {p % 4}"})
            filas.append(fila)
    return pd.DataFrame(filas)


def iguales(a, b):
    a, b = a.astype(float).to_numpy(), b.astype(float).to_numpy()
    return a.shape == b.shape and bool(((a == b) | (np.isnan(a) & np.isnan(b))).all())


def particion(df):
    """Validación: los pacientes cuyo número es múltiplo de 5."""
    en_va = df["patient_id"].str[1:].astype(int) % 5 == 0
    return np.flatnonzero(~en_va.to_numpy()), np.flatnonzero(en_va.to_numpy())


def perturbar_validacion_salvo(df, va, paciente):
    otro = df.copy()
    filas = otro.index[va][otro.iloc[va]["patient_id"].to_numpy() != paciente]
    otro.loc[filas, L["num_cols"]] = otro.loc[filas, L["num_cols"]] * 3 + 7
    otro.loc[filas[::3], "age_approx"] = np.nan
    otro.loc[filas, "sex"] = "otro"
    otro.loc[filas, "tbp_lv_location"] = "Cabeza"  # categoría que el entrenamiento no ha visto
    return otro


def caso_g():
    df = sintetico()
    tr, va = particion(df)
    tamanos = df.iloc[va].groupby("patient_id").size()
    p = tamanos[tamanos >= 3].index[0]
    otro = perturbar_validacion_salvo(df, va, p)
    excl = ["attribution"]
    x_tr, x_va, _, _ = g.variables_m3_en_pliegue(df, tr, va, excl)
    y_tr, y_va, _, _ = g.variables_m3_en_pliegue(otro, tr, va, excl)
    de_p = (df.iloc[va]["patient_id"] == p).to_numpy()
    entrenamiento_igual = iguales(x_tr, y_tr)
    p_igual = iguales(x_va[de_p], y_va[de_p])
    # Mutante: M3, que ajusta las transformaciones con todas las filas.
    a, _, _ = g.variables_m3(df, excl)
    b, _, _ = g.variables_m3(otro, excl)
    fila_p = (df["patient_id"] == p).to_numpy()
    mutante_detectado = not iguales(a[fila_p], b[fila_p]) and not iguales(a.iloc[tr], b.iloc[tr])
    return [
        ("G. cambiar las demás filas de validación no cambia el entrenamiento", entrenamiento_igual,
         f"{len(tr)} filas de entrenamiento idénticas: {entrenamiento_igual}"),
        ("G. ni las variables del paciente de validación que no se tocó", p_igual,
         f"paciente {p}, {int(de_p.sum())} filas idénticas: {p_igual}"),
        ("G. control: con las transformaciones de M3, sobre todas las filas, sí cambian", mutante_detectado,
         f"el paciente {p} y el entrenamiento cambian con M3: {mutante_detectado}"),
    ]


def caso_h():
    df = sintetico(1)
    tr, va = particion(df)
    x_tr, _, _, inv = g.variables_m3_en_pliegue(df, tr, va, ["attribution"])
    m3, _, _ = g.variables_m3(df.iloc[tr], ["attribution"])
    a, b = x_tr[m3.columns].astype(float).to_numpy(), m3.astype(float).to_numpy()
    mismos_nan = bool((np.isnan(a) == np.isnan(b)).all())
    peor = float(np.nanmax(np.where(np.isnan(a) | np.isnan(b), 0.0, np.abs(a - b) / (np.abs(b) + 1))))
    ok = mismos_nan and peor < 1e-12 and inv["n_variables"] == m3.shape[1] + 22
    return ok, (f"{m3.shape[1]} columnas comunes, peor diferencia relativa {peor:.1e}, NaN en los mismos sitios: "
                f"{mismos_nan} · M3 limpio: {inv['n_variables']} variables, 22 más que M3")


def caso_i():
    sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "diseno-validacion", "scripts"))
    from evaluar_repetido import cargar_columnas_excluidas
    excluidas = cargar_columnas_excluidas(FUGAS)
    de_imagen = set(L["de_imagen"])
    veintidos = [c for c in L["columns_to_drop"]
                 if not (c in de_imagen or (c.endswith("__cluster") and c[:-len("__cluster")] in de_imagen))]
    fuera = [c for c in veintidos if c in excluidas]
    casos = [("I. ninguna de las 22 columnas está entre las que excluye el proyecto", len(veintidos) == 22 and not fuera,
              f"{len(veintidos)} columnas; entre las {len(excluidas)} excluidas: {fuera}")]
    if not os.path.exists(CSV):
        casos.append(("I. las variables no dependen de las columnas excluidas", None, f"NO CORRIDO: no existe {CSV}"))
        return casos
    from datos_desarrollo import cargar_desarrollo
    dev, _ = cargar_desarrollo(CSV, "patient_id", HOLDOUT)
    pacientes = dev["patient_id"].drop_duplicates().sample(80, random_state=0)
    muestra = dev[dev["patient_id"].isin(pacientes)].drop(columns=["target"]).reset_index(drop=True)
    grupos = muestra["patient_id"].map({p: i for i, p in enumerate(pacientes)}).to_numpy()
    tr, va = np.flatnonzero(grupos % 5 != 0), np.flatnonzero(grupos % 5 == 0)
    alterada = muestra.copy()
    for c in excluidas:
        if c in alterada.columns:
            alterada[c] = ("x" + alterada[c].astype(str)) if not pd.api.types.is_numeric_dtype(alterada[c]) \
                else alterada[c] * -3 + 11
    x_tr, x_va, _, inv = g.variables_m3_en_pliegue(muestra, tr, va, excluidas)
    y_tr, y_va, _, _ = g.variables_m3_en_pliegue(alterada, tr, va, excluidas)
    ok = iguales(x_tr, y_tr) and iguales(x_va, y_va) and set(veintidos) <= set(x_tr.columns)
    alteradas = [c for c in excluidas if c in muestra.columns]
    casos.append(("I. alterar las columnas excluidas no cambia ninguna variable", ok,
                  f"{len(muestra)} filas de {len(pacientes)} pacientes de desarrollo · {len(alteradas)} columnas "
                  f"alteradas · {inv['n_variables']} variables idénticas (menos de 239: la muestra no tiene todas "
                  f"las categorías del one-hot): {ok}"))
    return casos


def caso_j():
    from catboost import CatBoostClassifier, Pool  # noqa: F401
    from sklearn.model_selection import StratifiedGroupKFold
    rng = np.random.default_rng(0)
    grupos = np.repeat([f"P{i}" for i in range(600)], 100)
    n = len(grupos)
    y = (rng.random(n) < 0.0012).astype(int)
    x = pd.DataFrame(rng.normal(size=(n, 8)) + y[:, None] * 0.6, columns=[f"v{i}" for i in range(8)])
    x["onehot_0"] = pd.Series(rng.integers(0, 2, n).astype(np.int32)).astype("category")
    tr, va = next(StratifiedGroupKFold(5, shuffle=True, random_state=0).split(x, y, groups=grupos))
    y_barajada = y.copy()
    y_barajada[va] = rng.permutation(y[va])
    m1 = g.ajustar_m3(x.iloc[tr], y[tr], grupos[tr], ["onehot_0"], 0, parametros=g.PARAMETROS_LIMPIO)
    m2 = g.ajustar_m3(x.iloc[tr], y_barajada[tr], grupos[tr], ["onehot_0"], 0, parametros=g.PARAMETROS_LIMPIO)
    p = m1.get_all_params()
    esperado = {"iterations": 1000, "l2_leaf_reg": 3, "depth": 6, "grow_policy": "SymmetricTree", "min_data_in_leaf": 1,
                "border_count": 254, "bootstrap_type": "MVS", "loss_function": "Logloss", "eval_metric": "AUC",
                "od_wait": 100, "od_type": "Iter", "use_best_model": True, "auto_class_weights": "None",
                "class_weights": None, "scale_pos_weight": None}
    distintos = {k: p.get(k) for k, v in esperado.items() if p.get(k) != v}
    lr_propia = p.get("learning_rate") != g.PARAMETROS_CATBOOST["learning_rate"]
    iguales_pred = bool(np.array_equal(m1.predict_proba(x.iloc[va])[:, 1], m2.predict_proba(x.iloc[va])[:, 1]))
    return [
        ("J. parada de M3 y valores por defecto en lo demás, sin pesos de clase", not distintos and lr_propia,
         f"distintos de lo esperado: {distintos} · tasa de aprendizaje automática {p.get('learning_rate'):.4f}"),
        ("J. barajar las etiquetas de validación no cambia el ajuste", iguales_pred,
         f"árboles {m1.tree_count_} y {m2.tree_count_}; predicciones idénticas: {iguales_pred}"),
    ]


def main():
    casos = caso_g()
    casos.append(("H. el lado de entrenamiento es el M3 verificado", *caso_h()))
    casos += caso_i()
    casos += caso_j()
    fallos = corridos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'NO CORRIDO' if ok is None else ('OK' if ok else 'FALLA')}] {titulo}\n      {detalle}")
        if ok is not None:
            corridos += 1
            fallos += not ok
    print(f"\n{corridos - fallos} de {corridos} casos corridos como se esperaba; {len(casos) - corridos} no corridos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

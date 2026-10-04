#!/usr/bin/env python3
"""
test_imagen_sola.py — prueba sintética de imagen_sola.py, antes de la corrida
real (PLAN.md, Fase 6, «La imagen sola»).

  A. Con una referencia que M1 reproduce, corre y escribe el .json y el .md; el
     .md tiene como mucho 15 líneas, y las métricas de M1 que escribe son las
     de la referencia.
  B. Con un valor de M1 alterado en la referencia, se detiene y no escribe nada.
  C. Con la huella de los pliegues alterada en la referencia, se detiene y no
     escribe nada.
  D. Con el archivo de características del conjunto reservado, el cargador se
     niega a leerlo y no se escribe nada.
  E. Barajar las etiquetas del pliegue de validación no cambia las puntuaciones
     de ninguno de los tres modelos. Puede fallar, y se demuestra: una versión
     mutada que ajusta la logística de imagen con el pliegue de validación
     incluido tiene que detectarse.
  F. «Imagen + básicos» usa las tres variables básicas e «Imagen» no: permutar
     age_approx cambia las puntuaciones del primero y no las del segundo.
  G. El campo «comando» registra el intérprete real, el script y las rutas de
     los argumentos, relativos a la raíz del repositorio.

La referencia de A se construye aquí con las piezas de train_and_evaluate.py,
del mismo modo que fase4_comparar.py construye M1. Con datos sintéticos; no
lee data/ ni outputs/.

Uso:
    python .claude/skills/modelado-baseline/scripts/test_imagen_sola.py
Devuelve 0 si todos los casos se comportan como se espera.
"""

import copy
import hashlib
import json
import os
import sys
import tempfile
import warnings

import h5py
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imagen_sola as isola  # noqa: E402
from fase4_comparar import METRICAS, huella_folds, medir  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds, preparar_features  # noqa: E402

warnings.filterwarnings("ignore")
SEMILLAS = [0, 1, 2]
N_SPLITS = 5
DIM = 8


def sinteticos(d):
    rng = np.random.default_rng(0)
    filas = []
    for p in range(70):
        for _ in range(int(rng.integers(10, 40))):
            filas.append({"patient_id": f"P{p:03d}"})
    df = pd.DataFrame(filas)
    n = len(df)
    df.insert(0, "isic_id", [f"ISIC_{i:06d}" for i in range(n)])
    y = (rng.random(n) < 0.05).astype(int)
    df["target"] = y
    df["age_approx"] = np.where(rng.random(n) < 0.05, np.nan, 50 + 10 * rng.normal(size=n) + 12 * y)
    df["sex"] = np.where(rng.random(n) < 0.05, None, rng.choice(["male", "female"], size=n))
    df["anatom_site_general"] = rng.choice(["torso", "head/neck", "lower extremity"], size=n)
    df["tbp_lv_a"] = rng.normal(size=n) + 0.7 * y
    df["tbp_lv_b"] = rng.normal(size=n)
    csv = os.path.join(d, "metadata.csv")
    df.to_csv(csv, index=False)
    x = rng.normal(size=(n, DIM)) + 0.6 * y[:, None]

    reservados = [f"P{p:03d}" for p in range(0, 70, 7)]
    holdout = os.path.join(d, "holdout.json")
    with open(holdout, "w", encoding="utf-8") as f:
        json.dump({"pacientes_reservados": reservados}, f)
    es_res = df["patient_id"].isin(reservados).to_numpy()

    def h5(ruta, mascara, conjunto):
        with h5py.File(ruta, "w") as f:
            f.create_dataset("cls", data=x[mascara].astype(np.float32))
            f.create_dataset("isic_id", data=np.array(df["isic_id"][mascara], dtype=object),
                             dtype=h5py.string_dtype("utf-8"))
            f.create_dataset("decodificada", data=np.ones(int(mascara.sum()), dtype=bool))
            f.attrs["conjunto"] = conjunto

    h5_des, h5_res = os.path.join(d, "des.h5"), os.path.join(d, "res.h5")
    h5(h5_des, ~es_res, "desarrollo")
    h5(h5_res, es_res, "reservado")
    extraccion = os.path.join(d, "extraccion.json")
    with open(h5_des, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    with open(extraccion, "w", encoding="utf-8") as f:
        json.dump({"conjuntos": {"desarrollo": {"archivo": {"sha256": sha}}}}, f)
    fugas = os.path.join(d, "fugas.json")
    with open(fugas, "w", encoding="utf-8") as f:
        json.dump({"columnas_identificador": ["isic_id"]}, f)
    return {"csv": csv, "holdout": holdout, "h5_des": h5_des, "h5_res": h5_res,
            "extraccion": extraccion, "fugas": fugas}


def referencia_m1(rutas, ruta_salida):
    """M1 como lo construye fase4_comparar.py, en el formato de su salida."""
    df = pd.read_csv(rutas["csv"])
    with open(rutas["holdout"], encoding="utf-8") as f:
        reservados = set(json.load(f)["pacientes_reservados"])
    df = df[~df["patient_id"].isin(reservados)].reset_index(drop=True)
    numericas, categoricas = preparar_features(df, ["isic_id"], "target", "patient_id")
    y, grupos = df["target"].to_numpy(), df["patient_id"].to_numpy()
    metricas = {k: {"por_semilla_y_fold": {}} for k in METRICAS}
    huellas = {}
    for seed in SEMILLAS:
        folds = construir_folds(df, "patient_id", "target", N_SPLITS, seed)
        huellas[str(seed)] = huella_folds(folds, len(df))
        valores = {k: [] for k in METRICAS}
        for tr, va in folds:
            x_tr, x_va = codificar_fold(df, numericas, categoricas, "target", tr, va)
            m = HistGradientBoostingClassifier(random_state=seed, class_weight="balanced").fit(x_tr, y[tr])
            for k, v in medir(y[va], m.predict_proba(x_va)[:, 1], grupos[va]).items():
                valores[k].append(v)
        for k in METRICAS:
            metricas[k]["por_semilla_y_fold"][str(seed)] = [round(v, 4) for v in valores[k]]
    ref = {"metricas": {"M1": metricas}, "folds": {"sha256_por_semilla": huellas}}
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(ref, f)
    return ref


def correr(rutas, referencia, out, imagen=None):
    """Corre main() con estos argumentos; devuelve (mensaje de parada o None, archivos escritos)."""
    sys.argv = [isola.__file__, "--data", rutas["csv"], "--group-col", "patient_id", "--target-col", "target",
                "--leakage-report", rutas["fugas"], "--imagen", imagen or rutas["h5_des"],
                "--extraccion", rutas["extraccion"], "--referencia", referencia, "--holdout", rutas["holdout"],
                "--out", out, "--semillas", *map(str, SEMILLAS)]
    parada = None
    try:
        isola.main()
    except SystemExit as e:
        parada = str(e.code)
    escritos = [s for s in (".json", ".md") if os.path.exists(out + s)]
    return parada, escritos


def mutante_ve_validacion(df, x_img, numericas, categoricas, target_col, tr, va, seed):
    p, n = isola.puntuar_fold(df, x_img, numericas, categoricas, target_col, tr, va, seed)
    todo = np.concatenate([tr, va])
    y = df[target_col].to_numpy()
    p["Imagen"] = isola.modelo_imagen().fit(x_img[todo], y[todo]).predict_proba(x_img[va])[:, 1]  # fuga
    return p, n


def main():
    casos = []
    with tempfile.TemporaryDirectory() as d:
        rutas = sinteticos(d)
        ref_path = os.path.join(d, "ref.json")
        ref = referencia_m1(rutas, ref_path)

        out = os.path.join(d, "a", "imagen-sola")
        parada, escritos = correr(rutas, ref_path, out)
        ok = parada is None and escritos == [".json", ".md"]
        detalle = f"parada {parada!r}, escritos {escritos}"
        if ok:
            r = json.load(open(out + ".json", encoding="utf-8"))
            lineas = open(out + ".md", encoding="utf-8").read().splitlines()
            m1_igual = all(r["metricas"]["M1"][k]["por_semilla_y_fold"] == ref["metricas"]["M1"][k]["por_semilla_y_fold"]
                           for k in METRICAS)
            control = r["control_m1_contra_referencia"]
            ok = (len(lineas) <= 15 and m1_igual and control["m1_reproduce_fold_a_fold"]
                  and control["semillas_comprobadas"] == SEMILLAS
                  and set(r["comparaciones_nuevo_menos_base"]) == set(isola.COMPARACIONES))
            detalle = (f"{len(lineas)} líneas en el .md; M1 igual a la referencia: {m1_igual}; "
                       f"semillas comprobadas {control['semillas_comprobadas']}")
        casos.append(("A. referencia que M1 reproduce: corre, escribe, .md ≤ 15 líneas", ok, detalle))
        if parada is None:
            partes = r["comando"].split(" ")
            interprete = os.path.relpath(sys.executable, isola.RAIZ)
            script = os.path.join(".claude", "skills", "modelado-baseline", "scripts", "imagen_sola.py")
            data = os.path.relpath(rutas["csv"], isola.RAIZ)
            casos.append(("G. el comando registra el intérprete, el script y las rutas, relativos al repositorio",
                          partes[:2] == [interprete, script] and data in partes and "patient_id" in partes,
                          f"{r['comando'][:110]}…"))

        alterada = copy.deepcopy(ref)
        alterada["metricas"]["M1"]["nnt80"]["por_semilla_y_fold"]["1"][3] += 0.0001
        ruta_b = os.path.join(d, "ref-b.json")
        json.dump(alterada, open(ruta_b, "w", encoding="utf-8"))
        out = os.path.join(d, "b", "imagen-sola")
        parada, escritos = correr(rutas, ruta_b, out)
        casos.append(("B. un valor de M1 alterado en 0,0001: se detiene sin escribir",
                      bool(parada) and "M1 no reproduce" in parada and "semilla 1" in parada and not escritos,
                      f"parada {parada!r}, escritos {escritos}"))

        alterada = copy.deepcopy(ref)
        alterada["folds"]["sha256_por_semilla"]["2"] = "0" * 64
        ruta_c = os.path.join(d, "ref-c.json")
        json.dump(alterada, open(ruta_c, "w", encoding="utf-8"))
        out = os.path.join(d, "c", "imagen-sola")
        parada, escritos = correr(rutas, ruta_c, out)
        casos.append(("C. huella de pliegues alterada: se detiene sin escribir",
                      bool(parada) and "los pliegues de la semilla 2" in parada and not escritos,
                      f"parada {parada!r}, escritos {escritos}"))

        out = os.path.join(d, "d", "imagen-sola")
        parada, escritos = correr(rutas, ref_path, out, imagen=rutas["h5_res"])
        casos.append(("D. archivo del conjunto reservado: el cargador se niega, no se escribe nada",
                      bool(parada) and "declara el conjunto 'reservado'" in parada and not escritos,
                      f"parada {parada!r}, escritos {escritos}"))

        # E y F, sobre un pliegue del conjunto de desarrollo sintético.
        from datos_desarrollo import cargar_desarrollo
        df, _ = cargar_desarrollo(rutas["csv"], "patient_id", rutas["holdout"])
        numericas, categoricas = preparar_features(df, ["isic_id"], "target", "patient_id")
        img, _ = isola.cargar_imagen(df, rutas["h5_des"], rutas["csv"], rutas["holdout"], None)
        x_img = img.to_numpy()
        tr, va = construir_folds(df, "patient_id", "target", N_SPLITS, 0)[0]
        barajado = df.copy()
        t = barajado["target"].to_numpy().copy()
        t[va] = np.random.default_rng(1).permutation(t[va])
        barajado["target"] = t
        assert (t[va] != df["target"].to_numpy()[va]).any()

        def cambia(fn, a, b):
            pa, _ = fn(a, x_img, numericas, categoricas, "target", tr, va, 0)
            pb, _ = fn(b, x_img, numericas, categoricas, "target", tr, va, 0)
            return [m for m in isola.MODELOS if not np.array_equal(pa[m], pb[m])]

        cambiados = cambia(isola.puntuar_fold, df, barajado)
        casos.append(("E. barajar las etiquetas de validación no cambia ninguna puntuación",
                      cambiados == [], f"modelos que cambian: {cambiados}"))
        cambiados = cambia(mutante_ve_validacion, df, barajado)
        casos.append(("E'. mutante que ajusta con la validación: se detecta",
                      cambiados == ["Imagen"], f"modelos que cambian: {cambiados}"))

        edad = df.copy()
        edad["age_approx"] = np.random.default_rng(2).permutation(edad["age_approx"].to_numpy())
        cambiados = cambia(isola.puntuar_fold, df, edad)
        casos.append(("F. permutar age_approx cambia «Imagen + básicos» (y M1) y no «Imagen»",
                      "Imagen + básicos" in cambiados and "Imagen" not in cambiados,
                      f"modelos que cambian: {cambiados}"))

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

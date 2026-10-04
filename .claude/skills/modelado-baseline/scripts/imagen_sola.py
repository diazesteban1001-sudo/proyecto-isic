#!/usr/bin/env python3
"""
imagen_sola.py — instrumento de medición para la skill modelado-baseline.

Mide qué rinde la imagen sin las mediciones del equipo de fotografía corporal
total: dos modelos sobre los recortes de SLICE-3D del conjunto de desarrollo,
en los mismos pliegues de M1 de la validación repetida. Especificación y regla
de lectura fijadas por la persona antes de correr (PLAN.md, Fase 6, «La imagen
sola», 2026-10-04). Mide y reporta; no interpreta.

  «Imagen»: modelo_imagen() de apilado_imagen.py —estandarizado y regresión
      logística balanceada— sobre las variables de DINOv2 del archivo de
      desarrollo, ajustado con el pliegue de entrenamiento y puntuando la
      validación. Es la primera etapa de M4b.
  «Imagen + básicos»: lo mismo, con age_approx, sex y anatom_site_general
      codificadas como en M1 (codificar_fold) y después estandarizadas con las
      de imagen.
  M1: el nivel 2b, como en fase4_comparar.py, de referencia y como control.

Importa, no copia: el cargador del conjunto de desarrollo y el de las
características, que se niega a leer el archivo del conjunto reservado
(datos_desarrollo.py, vía fase4_comparar.cargar_imagen, que además comprueba
la alineación por isic_id y el hash); los pliegues y la codificación de
train_and_evaluate.py; las métricas y la comparación de fase4_comparar.py.

Control: M1 tiene que reproducir pliegue a pliegue sus cuatro métricas de
outputs/fase4-m2-vs-m1.json (a 4 decimales), y la huella de los pliegues de
cada semilla tiene que ser la de ese archivo. Se comprueba al terminar cada
semilla; si no coincide, el script se detiene sin escribir nada.

No se mide tiempo: el costo de la imagen ya está medido en M4
(outputs/tiempo-inferencia.json).

La salida guarda el comando con que se corrió: el intérprete y los argumentos
reales (sys.executable y sys.argv), con rutas relativas al repositorio.

Uso:
    python imagen_sola.py --data data/train-metadata.csv \\
        --group-col patient_id --target-col target \\
        --leakage-report outputs/auditoria-de-fugas.json \\
        --imagen data/dinov2-vits14-desarrollo.h5 \\
        --extraccion outputs/extraccion-imagen.json \\
        --referencia outputs/fase4-m2-vs-m1.json \\
        --out outputs/imagen-sola
"""

import argparse
import json
import os
import sys
import warnings

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fase4_comparar import METRICAS, cargar_imagen, comparacion, huella_folds, medir  # noqa: E402
from apilado_imagen import modelo_imagen  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import codificar_fold, construir_folds, preparar_features  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
BASICOS_NUMERICAS = ["age_approx"]
BASICOS_CATEGORICAS = ["sex", "anatom_site_general"]
MODELOS = ("M1", "Imagen", "Imagen + básicos")
COMPARACIONES = {  # nombre: (nuevo, base)
    "imagen_menos_m1": ("Imagen", "M1"),
    "imagen_basicos_menos_imagen": ("Imagen + básicos", "Imagen"),
}


def _ajustar_imagen(x_tr, y_tr, x_va):
    """modelo_imagen() ajustado con el pliegue de entrenamiento; devuelve las
    puntuaciones de validación y cuántos avisos de no convergencia dio."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", ConvergenceWarning)
        p = modelo_imagen().fit(x_tr, y_tr).predict_proba(x_va)[:, 1]
    return p, sum(1 for a in w if issubclass(a.category, ConvergenceWarning))


def puntuar_fold(df, x_img, numericas, categoricas, target_col, tr, va, seed):
    """Puntuaciones de validación de los tres modelos en un pliegue, ajustados
    solo con tr, y los avisos de no convergencia de las dos logísticas."""
    y = df[target_col].to_numpy()
    x_tr, x_va = codificar_fold(df, numericas, categoricas, target_col, tr, va)
    m1 = HistGradientBoostingClassifier(random_state=seed, class_weight="balanced").fit(x_tr, y[tr])
    b_tr, b_va = codificar_fold(df, BASICOS_NUMERICAS, BASICOS_CATEGORICAS, target_col, tr, va)
    solo, n_solo = _ajustar_imagen(x_img[tr], y[tr], x_img[va])
    con, n_con = _ajustar_imagen(np.hstack([x_img[tr], b_tr]), y[tr], np.hstack([x_img[va], b_va]))
    puntuaciones = {"M1": m1.predict_proba(x_va)[:, 1], "Imagen": solo, "Imagen + básicos": con}
    return puntuaciones, {"Imagen": n_solo, "Imagen + básicos": n_con}


def comando_real():
    """El intérprete y los argumentos con que se corrió (sys.executable y
    sys.argv), con las rutas relativas a la raíz del repositorio. Se toma
    como ruta el script y todo argumento que contenga un separador."""
    def relativa(ruta):
        return os.path.relpath(os.path.abspath(ruta), RAIZ)
    argumentos = [relativa(sys.argv[0])] + [relativa(a) if os.sep in a and not a.startswith("-") else a
                                            for a in sys.argv[1:]]
    return " ".join([relativa(sys.executable), *argumentos])


def resumen(por_semilla, semillas):
    """El mismo resumen que fase4_comparar.py, más la media de cada semilla."""
    todos = [v for s in semillas for v in por_semilla[str(s)]]
    medias = [float(np.mean(por_semilla[str(s)])) for s in semillas]
    return {
        "por_semilla_y_fold": {str(s): [round(v, 4) for v in por_semilla[str(s)]] for s in semillas},
        "media_por_semilla": [round(m, 4) for m in medias],
        "media_global": round(float(np.mean(todos)), 4),
        "std_entre_folds": round(float(np.std(todos)), 4),
        "std_entre_semillas": round(float(np.std(medias)), 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--leakage-report", required=True)
    ap.add_argument("--imagen", required=True, help="características de DINOv2 del conjunto de desarrollo")
    ap.add_argument("--extraccion", default=None, help="outputs/extraccion-imagen.json, para comprobar el hash")
    ap.add_argument("--referencia", default="outputs/fase4-m2-vs-m1.json")
    ap.add_argument("--holdout", default=RUTA_HOLDOUT)
    ap.add_argument("--out", required=True)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(10)))
    args = ap.parse_args()

    if os.path.basename(args.out).startswith("fase4-"):
        raise SystemExit("ERROR: imagen_sola.py no escribe las salidas de la Fase 4.")
    with open(args.referencia, encoding="utf-8") as f:
        referencia = json.load(f)
    ref_m1 = referencia["metricas"]["M1"]
    ref_huellas = referencia["folds"]["sha256_por_semilla"]

    excluidas = cargar_columnas_excluidas(args.leakage_report)
    df, datos = cargar_desarrollo(args.data, args.group_col, args.holdout)
    numericas, categoricas = preparar_features(df, excluidas, args.target_col, args.group_col)
    faltan = [c for c in BASICOS_NUMERICAS if c not in numericas] + [c for c in BASICOS_CATEGORICAS if c not in categoricas]
    if faltan:
        raise SystemExit(f"ERROR: {faltan} no son variables de M1 con el tipo esperado.")
    imagen, comprobacion_imagen = cargar_imagen(df, args.imagen, args.data, args.holdout, args.extraccion)
    x_img = imagen.to_numpy()
    y = df[args.target_col].to_numpy()
    grupos = df[args.group_col].to_numpy()
    semillas = list(args.semillas)

    por = {m: {k: {} for k in METRICAS} for m in MODELOS}
    avisos = {m: 0 for m in ("Imagen", "Imagen + básicos")}
    control = {"referencia": args.referencia, "semillas_comprobadas": []}
    for seed in semillas:
        folds = construir_folds(df, args.group_col, args.target_col, args.n_splits, seed)
        if huella_folds(folds, len(df)) != ref_huellas.get(str(seed)):
            raise SystemExit(f"CONTROL FALLIDO: los pliegues de la semilla {seed} no son los de {args.referencia}. "
                             "No se escribe nada.")
        valores = {m: {k: [] for k in METRICAS} for m in MODELOS}
        for tr, va in folds:
            puntuaciones, n_avisos = puntuar_fold(df, x_img, numericas, categoricas, args.target_col, tr, va, seed)
            for m, n in n_avisos.items():
                avisos[m] += n
            for m in MODELOS:
                for k, v in medir(y[va], puntuaciones[m], grupos[va]).items():
                    valores[m][k].append(v)
        distintas = [k for k in METRICAS
                     if [round(v, 4) for v in valores["M1"][k]] != ref_m1[k]["por_semilla_y_fold"].get(str(seed))]
        if distintas:
            raise SystemExit(f"CONTROL FALLIDO: M1 no reproduce {args.referencia} en la semilla {seed} "
                             f"(métricas {distintas}). No se escribe nada.")
        control["semillas_comprobadas"].append(seed)
        for m in MODELOS:
            for k in METRICAS:
                por[m][k][str(seed)] = valores[m][k]
        print(f"Semilla {seed}: hecho", flush=True)
    control["m1_reproduce_fold_a_fold"] = True
    control["huellas_de_pliegues_iguales"] = True

    comparaciones = {}
    for nombre, (nuevo, base) in COMPARACIONES.items():
        comparaciones[nombre] = {"nuevo": nuevo, "base": base}
        for k, mayor in METRICAS.items():
            diffs = [n - b for s in semillas for n, b in zip(por[nuevo][k][str(s)], por[base][k][str(s)])]
            comparaciones[nombre][k] = comparacion(diffs, args.n_splits, semillas, mayor)

    resultado = {
        "comando": comando_real(),
        "datos": datos,
        "esquema": {
            "group_col": args.group_col, "n_splits": args.n_splits, "semillas": semillas,
            "pliegues": "construir_folds de train_and_evaluate.py, los de M1 en outputs/fase4-m2-vs-m1.json",
        },
        "modelos": {
            "M1": "nivel 2b: HistGradientBoostingClassifier(class_weight='balanced'), variables de modelado-baseline",
            "Imagen": f"modelo_imagen() de apilado_imagen.py sobre las {x_img.shape[1]} variables de DINOv2",
            "Imagen + básicos": "lo mismo, más " + ", ".join(BASICOS_NUMERICAS + BASICOS_CATEGORICAS)
                                + " codificadas con codificar_fold y estandarizadas con las de imagen",
        },
        "comprobacion_imagen": comprobacion_imagen,
        "control_m1_contra_referencia": control,
        "avisos_no_convergencia": avisos,
        "metricas": {m: {k: resumen(por[m][k], semillas) for k in METRICAS} for m in MODELOS},
        "comparaciones_nuevo_menos_base": comparaciones,
        "nota": "En el NNT80% SE menos es mejor; las victorias se cuentan en esa dirección. No se mide tiempo.",
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    def medias(m):
        r = resultado["metricas"][m]
        return " · ".join(f"{k} {r[k]['media_global']}" for k in METRICAS)

    def comp(nombre):
        c = comparaciones[nombre]
        return " · ".join(f"{k} {c[k]['media']:+} {c[k]['intervalo_t_95_nadeau_bengio']}" for k in METRICAS)

    lineas = [
        f"# Imagen sola — {args.data}, conjunto de desarrollo",
        f"Pliegues de M1 en la validación repetida: {args.n_splits} agrupados por {args.group_col}, "
        f"semillas {semillas[0]}–{semillas[-1]}",
        f"Control: M1 reproduce {args.referencia} pliegue a pliegue en las cuatro métricas, con los mismos pliegues",
        f"Imagen: logística balanceada sobre las {x_img.shape[1]} variables de DINOv2, estandarizadas en el pliegue",
        "Imagen + básicos: lo mismo, más " + ", ".join(BASICOS_NUMERICAS + BASICOS_CATEGORICAS) + ", codificadas como en M1",
        "Medias globales (pauc · auc · setop15 · nnt80):",
        f"  M1: {medias('M1')}",
        f"  Imagen: {medias('Imagen')}",
        f"  Imagen + básicos: {medias('Imagen + básicos')}",
        f"Imagen − M1, media e intervalo corregido: {comp('imagen_menos_m1')}",
        f"(Imagen + básicos) − Imagen, media e intervalo corregido: {comp('imagen_basicos_menos_imagen')}",
        f"Avisos de no convergencia de la logística: Imagen {avisos['Imagen']} · Imagen + básicos {avisos['Imagen + básicos']}",
        "En el NNT80% SE menos es mejor. No se mide tiempo: el costo de la imagen está en tiempo-inferencia.json (M4).",
        f"Detalle por semilla y pliegue: {args.out}.json",
    ]
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

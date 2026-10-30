#!/usr/bin/env python3
"""
test_fase4d_controles.py — los controles de la red mejorada y de C5 de la Fase 4d
(PLAN.md, «Controles, antes de leer cualquier resultado»), antes de entrenar las
25 redes y de responder ninguna pregunta. No calcula la métrica de C5, de la red
mejorada ni de C6.

  ajustes          Las constantes de la Fase 4c siguen siendo las de la prueba de
                   tiempo (fase4c.comprobar_ajustes), y la red mejorada cambia solo
                   las épocas, a 15.
  bloques          En el pliegue 0 de la semilla 0, los negativos de 15 épocas
                   (fase4d.bloques_de_negativos): ninguno en dos épocas, cada época
                   con 20 por positivo, todos del pliegue de entrenamiento.
  igual_que_4c     Fuera de la elección de los negativos, el entrenamiento es el de
                   la Fase 4c: con los sorteos de la 4c, una época de
                   fase4d.entrenar_y_puntuar da los mismos logits que
                   fase4c.entrenar_y_puntuar, sobre los positivos de la validación
                   y 4.000 de sus negativos.
  barajadas        Los de la Fase 4c con la red mejorada: con las etiquetas del
                   pliegue de entrenamiento barajadas (semilla 0), su pAUC cae en el
                   99 % central de 1.000 puntuaciones aleatorias; la red con las
                   etiquetas reales queda por encima de ese rango con logits que
                   varían, y sus épocas no repiten negativos.
  reproducibilidad La misma red, semilla 0, pliegue 0, dos veces.
  alineacion       fase4c.ensamblar, que también une las puntuaciones de la red
                   mejorada: cada lesión, una vez, la de su pliegue.
  referencias      Las predicciones de M3 limpio de la Fase 4b y las puntuaciones de
                   la red de la Fase 4c pasan sus comprobaciones; los pliegues de las
                   semillas 0 a 9 tienen la huella de outputs/fase4-m2-vs-m1.json.
  c5               En el pliegue 0 de la semilla 0, con las puntuaciones de la red
                   de la Fase 4c:
                   - C4 reproduce las cuatro métricas de ese pliegue en
                     outputs/fase4c-c4-vs-m3limpio.json;
                   - la estandarización por zona y edad es la de la celda 17 sin el
                     hospital, con pandas sobre las filas de entrenamiento;
                   - las etiquetas de conglomerado, con fase4d.estandarizar,
                     reproducen las variables por conglomerado de M3 limpio;
                   - el ruido va solo al entrenamiento, es el sorteo de la semilla,
                     con desviación cercana a 0,1, y se repite igual;
                   - la alineación de las seis variables, antes y después del
                     remuestreo;
                   - C5 se ajusta y puntúa la validación de punta a punta: se
                     comprueba que da una probabilidad por fila, sin calcular su
                     métrica.

Casos que deben fallar: la prueba de tiempo con lote 32; los sorteos de la Fase
4c repiten negativos entre épocas; con los bloques, una época no da los logits
de la 4c; una puntuación sintética de las etiquetas con ruido queda fuera del
rango y una constante no pasa por red real; un logit cambiado en 1e-6; una fila
que falta, una repetida, una en la red de otro pliegue y un isic_id ajeno; los
pliegues de la semilla 0 frente a la huella de la 1; la estandarización por
zona y edad calculada con el entrenamiento y la validación juntos; las
etiquetas de conglomerado barajadas; ruido también en validación; las columnas
de la red corridas una fila.

Con --rapido, las redes de barajadas y reproducibilidad entrenan 2 épocas y
puntúan solo los positivos de la validación y 4.000 de sus negativos. Sin
--rapido, entrenan las 15 épocas y puntúan toda la validación, y --out tiene que
ir en data/: fase4d_redes.py y fase4d_comparar.py lo exigen con 0 fallos.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4d_controles.py --rapido --out RUTA.json
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4d_controles.py \\
        --out data/fase4d-controles.json
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import argparse
import copy
import json
import os
import sys
import time
import warnings

import h5py
import numpy as np
import pandas as pd
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import fase4c_comparar as f4cc  # noqa: E402
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402
import test_fase4c_controles as t4c  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import construir_folds, pauc_above_tpr  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
REF_C4 = os.path.join(RAIZ, "outputs", "fase4c-c4-vs-m3limpio.json")
G, Y = "patient_id", "target"
NEGATIVOS_RAPIDO = 4000
EPOCAS_RAPIDO = 2

# Los casos se registran en la lista de test_fase4c_controles, para reusar sus
# controles de alineación y de referencias tal cual.
resultados = t4c.resultados
registrar = t4c.registrar
se_detiene = t4c.se_detiene


def iguales(u, v):
    return bool(np.array_equal(np.asarray(u, dtype=float), np.asarray(v, dtype=float), equal_nan=True))


# ---- ajustes y bloques -----------------------------------------------------------------------

def control_ajustes():
    with open(fase4c.PRUEBA_DE_TIEMPO, encoding="utf-8") as f:
        prueba = json.load(f)
    diferencias = fase4c.comprobar_ajustes(prueba)
    registrar("ajustes", "las constantes de la 4c son las de la prueba de tiempo y la red mejorada cambia solo las "
              "épocas", not diferencias and fase4d.EPOCAS == 15 and fase4c.EPOCAS == 3,
              f"lado {fase4c.LADO}, tasa {fase4c.TASA}, lote {fase4c.LOTE}, {fase4c.NEGATIVOS_POR_POSITIVO} negativos "
              f"por positivo; épocas {fase4c.EPOCAS} en la 4c y {fase4d.EPOCAS} aquí; diferencias: {diferencias}")
    otra = copy.deepcopy(prueba)
    otra["entrenamiento"]["lote"] = 32
    registrar("ajustes", "la prueba de tiempo con lote 32", len(fase4c.comprobar_ajustes(otra)) == 1,
              f"{fase4c.comprobar_ajustes(otra)}", debe_fallar=True)


def control_bloques(d):
    tr, _ = construir_folds(d["df"], G, Y, 5, 0)[0]
    pos, neg = tr[d["y"][tr] == 1], tr[d["y"][tr] == 0]
    n_neg = fase4c.NEGATIVOS_POR_POSITIVO * len(pos)
    por_epoca, n_bloques = fase4d.bloques_de_negativos(neg, n_neg, fase4d.EPOCAS, np.random.default_rng(0))
    ok = (fase4d.repetidos_entre_epocas(por_epoca) == 0 and all(len(b) == n_neg for b in por_epoca)
          and np.isin(np.concatenate(por_epoca), neg).all() and n_bloques >= fase4d.EPOCAS)
    registrar("bloques", "15 épocas sin ningún negativo en dos, 20 por positivo, todos del entrenamiento", ok,
              f"{len(pos)} positivos, {len(neg)} negativos, {n_bloques} bloques de {n_neg}; repetidos "
              f"{fase4d.repetidos_entre_epocas(por_epoca)}")
    rng = np.random.default_rng(0)
    sorteos = [rng.choice(neg, size=n_neg, replace=False) for _ in range(fase4d.EPOCAS)]
    rep = fase4d.repetidos_entre_epocas(sorteos)
    registrar("bloques", "los sorteos de la Fase 4c, 15 épocas", rep > 0, f"{rep} negativos en más de una época",
              debe_fallar=True)
    return {"positivos": int(len(pos)), "negativos": int(len(neg)), "bloques": int(n_bloques),
            "repetidos_con_los_sorteos_de_la_4c": rep}


# ---- redes -----------------------------------------------------------------------------------

def subconjunto_de_validacion(d, va):
    rng = np.random.default_rng(0)
    pos, neg = va[d["y"][va] == 1], va[d["y"][va] == 0]
    return np.sort(np.concatenate([pos, rng.choice(neg, size=NEGATIVOS_RAPIDO, replace=False)]))


def control_igual_que_4c(d, h5, dispositivo):
    tr, va = construir_folds(d["df"], G, Y, 5, 0)[0]
    va_eval = subconjunto_de_validacion(d, va)
    l_4c, _ = fase4c.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, 1)
    l_igual, r_igual = fase4d.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, 1, negativos="4c")
    l_bloq, _ = fase4d.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, 1)
    c_igual, c_bloq = t4c.coinciden(l_4c, l_igual), t4c.coinciden(l_4c, l_bloq)
    registrar("igual_que_4c", "con los sorteos de la 4c, una época da los logits de fase4c.entrenar_y_puntuar",
              c_igual["identicos"], f"idénticos: {c_igual['identicos']}; mayor diferencia "
              f"{c_igual['maxima_diferencia']:.3g} en {c_igual['filas']} filas")
    registrar("igual_que_4c", "con los bloques, una época", not c_bloq["identicos"],
              f"idénticos: {c_bloq['identicos']}; mayor diferencia {c_bloq['maxima_diferencia']:.3g}",
              debe_fallar=True)
    return {"con_los_sorteos_de_la_4c": c_igual, "con_los_bloques": c_bloq, "red": r_igual}


def controles_con_red(d, h5, dispositivo, rapido):
    tr, va = construir_folds(d["df"], G, Y, 5, 0)[0]
    va_eval, epocas = (subconjunto_de_validacion(d, va), EPOCAS_RAPIDO) if rapido else (va, fase4d.EPOCAS)
    y_va = d["y"][va_eval]
    barajadas = d["y"].copy()
    barajadas[tr] = np.random.default_rng(0).permutation(d["y"][tr])
    logit_b, reg_b = fase4d.entrenar_y_puntuar(h5, d["isic"], barajadas, tr, va_eval, 0, dispositivo, epocas)
    logit_1, reg_1 = fase4d.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, epocas)
    logit_2, reg_2 = fase4d.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, epocas)
    banda, media = t4c.banda_aleatoria(y_va)
    pauc_b = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit_b)))
    disp = {"barajada": t4c.dispersion(logit_b), "primera": t4c.dispersion(logit_1), "segunda": t4c.dispersion(logit_2)}
    registrar("barajadas", "la red con las etiquetas barajadas, dentro del 99 % central del azar",
              t4c.dentro(pauc_b, banda),
              f"pAUC {pauc_b:.4f}; rango [{banda[0]:.4f}; {banda[1]:.4f}], media {media:.4f}; {len(va_eval)} filas, "
              f"{int(y_va.sum())} positivos, {epocas} épocas; {disp['barajada']['logits_distintos']} logits distintos")
    sintetica = y_va + 0.1 * np.random.default_rng(2).normal(size=len(y_va))
    pauc_s = float(pauc_above_tpr(y_va, sintetica))
    registrar("barajadas", "las etiquetas más un poco de ruido", not t4c.dentro(pauc_s, banda), f"pAUC {pauc_s:.4f}",
              debe_fallar=True)
    reales = []
    for nombre, logit, reg in (("primera", logit_1, reg_1), ("segunda", logit_2, reg_2)):
        pauc_r = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit)))
        dis = t4c.dispersion(logit)
        ok = (pauc_r > banda[1] and dis["logits_distintos"] > 1 and dis["desviacion_del_logit"] > 0
              and reg["negativos_en_mas_de_una_epoca"] == 0)
        reales.append({"red": nombre, "pauc": round(pauc_r, 4), **dis})
        registrar("barajadas", f"la red con las etiquetas reales ({nombre}), por encima del rango, con logits que "
                  "varían y sin negativos repetidos", ok,
                  f"pAUC {pauc_r:.4f} frente al límite {banda[1]:.4f}; {dis['logits_distintos']} logits distintos, "
                  f"desviación {dis['desviacion_del_logit']:.3g}; {reg['negativos_en_mas_de_una_epoca']} negativos en "
                  f"más de una época, {reg['negativos_distintos_vistos']} vistos")
    constante = np.zeros(len(y_va), dtype=np.float32)
    pauc_c = float(pauc_above_tpr(y_va, fase4c.probabilidad(constante)))
    registrar("barajadas", "una puntuación constante como red real", not (pauc_c > banda[1]),
              f"pAUC {pauc_c:.4f}; 1 logit distinto", debe_fallar=True)
    rep = t4c.coinciden(logit_1, logit_2)
    registrar("reproducibilidad", "la misma red dos veces, semilla 0, pliegue 0", True,
              f"idénticos: {rep['identicos']}; mayor diferencia de logit {rep['maxima_diferencia']:.3g} en "
              f"{rep['filas']} filas")
    tocado = np.array(logit_1, dtype=np.float64)
    tocado[0] += 1e-6
    registrar("reproducibilidad", "un logit cambiado en 1e-6", not t4c.coinciden(logit_1, tocado)["identicos"],
              "idénticos: False", debe_fallar=True)
    return {"barajadas": {"pauc": round(pauc_b, 4), "rango_99": [round(b, 4) for b in banda],
                          "media_aleatoria": round(media, 4), "filas": int(len(va_eval)), "positivos": int(y_va.sum()),
                          "redes_con_las_etiquetas_reales": reales, "red": reg_b},
            "reproducibilidad": {**rep, "redes": [reg_1, reg_2]}, "dispersion_de_los_logits": disp}


# ---- referencias -----------------------------------------------------------------------------

def control_red_4c(d):
    tabla, proc = f4cc.cargar_red(f4cc.RED, internos=False)
    ok = all(len(f4cc.de_semilla(tabla, s, d["isic"])) == len(d["isic"]) for s in range(10))
    registrar("referencias", "las puntuaciones de la red de la 4c pasan sus comprobaciones y cubren cada semilla", ok,
              f"{os.path.relpath(f4cc.RED, RAIZ)}, SHA-256 {proc['sha256'][:12]}…")
    return tabla


# ---- c5 --------------------------------------------------------------------------------------

def control_c5(d, red_4c):
    tr, va = construir_folds(d["df"], G, Y, 5, 0)[0]
    p = f4cc.de_semilla(red_4c, 0, d["isic"])
    x_tr, x_va, cats, _, aj = ganador_m3.variables_m3_en_pliegue(d["df_sin_etiqueta"], tr, va, d["excluidas"], G,
                                                                 devolver_ajuste=True)
    informe = {}

    # C4 reproduce su pliegue.
    s4, reg4 = f4cc.c4_en_pliegue(d["df_sin_etiqueta"], d["excluidas"], d["y"], d["grupos"], p, tr, va, 0)
    with open(REF_C4, encoding="utf-8") as f:
        ref = json.load(f)["metricas"]["C4"]
    calc = {k: round(v, 4) for k, v in f4.medir(d["y"][va], s4, d["grupos"][va]).items()}
    registrar("c5", "C4 reproduce las cuatro métricas de su pliegue en fase4c-c4-vs-m3limpio.json",
              all(calc[k] == ref[k]["por_semilla_y_fold"]["0"][0] for k in f4.METRICAS), f"semilla 0, pliegue 0: {calc}")

    # Zona y edad: la celda 17 sin el hospital, con pandas.
    claves_tr = fase4d.claves_zona_edad(d["df_sin_etiqueta"], tr, x_tr)
    claves_va = fase4d.claves_zona_edad(d["df_sin_etiqueta"], va, x_va)
    et_tr, et_va = fase4d.etiquetas_conglomerado(aj, x_tr, x_va)
    a = fase4d.variables_c5(p, tr, va, d["grupos"], claves_tr, claves_va, et_tr, et_va, 0)
    celda = pd.DataFrame({**claves_tr, "s": p[tr]})
    agg = celda.groupby(fase4d.ZONA_EDAD).agg(m=("s", "mean"), sd=("s", "std")).reset_index()
    ganador_tr = celda.merge(agg, how="left", on=fase4d.ZONA_EDAD)
    z_ganador_tr = ((ganador_tr["s"] - ganador_tr["m"]) / ganador_tr["sd"]).to_numpy()
    lado_va = pd.DataFrame({**claves_va, "s": p[va]}).merge(agg, how="left", on=fase4d.ZONA_EDAD)
    z_ganador_va = ((lado_va["s"] - lado_va["m"]) / lado_va["sd"]).to_numpy()
    defin = lado_va["sd"].to_numpy() > 0
    ok_tr = iguales(np.where(np.isfinite(z_ganador_tr), z_ganador_tr, np.nan), a["sin_ruido_tr"])
    ok_va = iguales(z_ganador_va[defin], a["va"][fase4d.Z_ZONA_EDAD][defin]) and np.isnan(
        a["va"][fase4d.Z_ZONA_EDAD][~defin]).all()
    registrar("c5", "la estandarización por zona y edad es la de la celda 17 sin el hospital", ok_tr and ok_va,
              f"{agg.shape[0]} grupos en el entrenamiento; NaN en {int(np.isnan(a['sin_ruido_tr']).sum())} filas de "
              f"entrenamiento y {int(np.isnan(a['va'][fase4d.Z_ZONA_EDAD]).sum())} de validación")
    juntas = pd.DataFrame({k: np.concatenate([claves_tr[k], claves_va[k]]) for k in claves_tr})
    juntas["s"] = np.concatenate([p[tr], p[va]])
    agg_j = juntas.groupby(fase4d.ZONA_EDAD).agg(m=("s", "mean"), sd=("s", "std")).reset_index()
    lado_j = pd.DataFrame({**claves_va, "s": p[va]}).merge(agg_j, how="left", on=fase4d.ZONA_EDAD)
    z_juntas = ((lado_j["s"] - lado_j["m"]) / lado_j["sd"]).to_numpy()
    registrar("c5", "la estandarización con el entrenamiento y la validación juntos, como el ganador",
              not iguales(z_juntas[defin], a["va"][fase4d.Z_ZONA_EDAD][defin]),
              f"mayor diferencia en validación {np.nanmax(np.abs(z_juntas[defin] - a['va'][fase4d.Z_ZONA_EDAD][defin])):.3g}",
              debe_fallar=True)

    # Conglomerados: reproducen las variables por conglomerado de M3 limpio.
    cols = [c for c in aj["columnas_conglomerado"] if c in x_tr.columns and f"{c}__cluster" in x_tr.columns]

    def reproduce(e_tr, e_va):
        dif = 0.0
        for c in cols:
            z_tr, z_va = fase4d.estandarizar(x_tr[c].to_numpy(float), {"conglomerado": e_tr}, x_va[c].to_numpy(float),
                                             {"conglomerado": e_va})
            for z, x in ((z_tr, x_tr), (z_va, x_va)):
                ref_c = x[f"{c}__cluster"].to_numpy(float)
                fin = np.isfinite(ref_c) & np.isfinite(z)
                if (np.isfinite(ref_c) != np.isfinite(z)).any():
                    return float("inf")
                dif = max(dif, float(np.max(np.abs(z[fin] - ref_c[fin]))) if fin.any() else 0.0)
        return dif
    dif = reproduce(et_tr, et_va)
    registrar("c5", "las etiquetas de conglomerado reproducen las variables por conglomerado de M3 limpio",
              dif <= 1e-9, f"{len(cols)} variables; mayor diferencia {dif:.3g}")
    dif_b = reproduce(et_tr, np.random.default_rng(0).permutation(et_va))
    registrar("c5", "con las etiquetas de validación barajadas", dif_b > 1e-9, f"mayor diferencia {dif_b:.3g}",
              debe_fallar=True)

    # Ruido.
    _, z_va_sin = fase4d.estandarizar(p[tr], claves_tr, p[va], claves_va)
    r = fase4d.comprobar_ruido(a, 0, z_va_sin)
    otra = fase4d.variables_c5(p, tr, va, d["grupos"], claves_tr, claves_va, et_tr, et_va, 0)
    repite = all(iguales(a[l][c], otra[l][c]) for l in ("tr", "va") for c in fase4d.COLUMNAS_C5)
    registrar("c5", "el ruido va solo al entrenamiento, es el sorteo de la semilla, con desviación cercana a 0,1, y "
              "se repite igual", r["validacion_sin_ruido"] and r["entrenamiento_con_el_sorteo_de_la_semilla"]
              and abs(r["desviacion_del_ruido"] - fase4d.RUIDO) < 0.002 and repite,
              f"{r}; se repite igual: {repite}")
    mal = {"tr": dict(a["tr"]), "va": dict(a["va"]), "sin_ruido_tr": a["sin_ruido_tr"]}
    mal["va"][fase4d.Z_ZONA_EDAD] = a["va"][fase4d.Z_ZONA_EDAD] + np.random.default_rng(9).normal(0, 0.1, len(va))
    r_mal = fase4d.comprobar_ruido(mal, 0, z_va_sin)
    registrar("c5", "ruido también en validación", not r_mal["validacion_sin_ruido"], f"{r_mal['validacion_sin_ruido']}",
              debe_fallar=True)

    # Alineación de las seis variables.
    xc_tr, xc_va = fase4d.con_red(x_tr, x_va, a)
    alin = fase4d.comprobar_alineacion(x_tr, xc_tr, a, 0, d["y"][tr], d["grupos"][tr])
    registrar("c5", "alineación de las seis variables de la red, antes y después del remuestreo",
              all(alin[k] for k in ("antes", "razon", "despues")), f"{alin}")
    rodado = {"tr": {c: np.roll(v, 1) for c, v in a["tr"].items()}, "va": a["va"]}
    xr_tr, _ = fase4d.con_red(x_tr, x_va, rodado)
    alin_r = fase4d.comprobar_alineacion(x_tr, xr_tr, a, 0, d["y"][tr], d["grupos"][tr])
    registrar("c5", "las columnas de la red corridas una fila", not alin_r["antes"], f"{alin_r}", debe_fallar=True)

    # C5 de punta a punta, sin su métrica.
    modelo = ganador_m3.ajustar_m3(xc_tr, d["y"][tr], d["grupos"][tr], cats, 0, parametros=ganador_m3.PARAMETROS_LIMPIO)
    s5 = modelo.predict_proba(xc_va)[:, 1]
    registrar("c5", "C5 se ajusta y da una probabilidad por fila de validación, sin calcular su métrica",
              len(s5) == len(va) and np.all(np.isfinite(s5)) and np.all((s5 >= 0) & (s5 <= 1)),
              f"{len(s5)} filas; {xc_tr.shape[1]} variables, {xc_tr.shape[1] - x_tr.shape[1]} de la red; "
              f"{int(modelo.tree_count_)} árboles")
    informe.update({"c4_reproducido": calc, "ajuste_c4": reg4, "grupos_zona_edad": int(agg.shape[0]), "ruido": r,
                    "alineacion": alin, "variables": int(xc_tr.shape[1]), "arboles_c5": int(modelo.tree_count_)})
    return informe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--out", required=True, help="JSON con el resultado de cada caso")
    args = ap.parse_args()
    if not args.rapido:
        destino = os.path.realpath(args.out)
        if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "data")) + os.sep):
            raise SystemExit("ERROR: la corrida completa de los controles va en data/, donde la leen fase4d_redes.py y "
                             "fase4d_comparar.py.")
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    control_ajustes()
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    d = {"df": df, "df_sin_etiqueta": df.drop(columns=[Y]), "excluidas": cargar_columnas_excluidas(FUGAS),
         "y": df[Y].to_numpy(), "grupos": df[G].to_numpy(), "isic": df["isic_id"].to_numpy()}
    print(f"Datos de desarrollo: {len(df)} filas", flush=True)
    informe = {"bloques": control_bloques(d)}
    t4c.control_alineacion(d)
    t4c.control_referencias(d)
    red_4c = control_red_4c(d)
    informe["c5"] = control_c5(d, red_4c)
    dispositivo = torch.device("mps")
    with h5py.File(HDF5, "r") as h5:
        informe["igual_que_4c"] = control_igual_que_4c(d, h5, dispositivo)
        informe.update(controles_con_red(d, h5, dispositivo, args.rapido))

    total = round(time.perf_counter() - t_total, 1)
    malos = [r for r in resultados if not r["ok"]]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"rapido": args.rapido, "datos": datos,
                   "alcance": (f"redes de {EPOCAS_RAPIDO} épocas sobre los positivos de la validación y 4.000 negativos"
                               if args.rapido else "redes con los ajustes de la fase, sobre toda la validación"),
                   "segundos": total, "casos": resultados, "fallos": len(malos), **informe,
                   "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                               "caffeinate": bajo_caffeinate}}, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; {total} s. Escrito: {args.out}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

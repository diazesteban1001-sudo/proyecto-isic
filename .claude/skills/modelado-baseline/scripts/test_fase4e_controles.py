#!/usr/bin/env python3
"""
test_fase4e_controles.py — los controles de la red de la Fase 4e, de su ajuste
fino y de C7 (PLAN.md, Fase 4e, «Controles, antes de leer cualquier resultado»),
antes de la exploración. Las redes de control se entrenan en la semilla 1, pliegue
0, que no usan ni la exploración (semilla 0) ni la confirmación (semillas 5 a 9):
ningún control calcula la pAUC de un pliegue que después decide.

  aumentos         El patrón 2 de fase4e coincide con el train_transform_p2 del
                   autor, reconstruido desde la cita de su código en la ficha; la
                   predicción, con su valid_transform_p2.
  conjuntos        Los 20 conjuntos reparten todos los negativos del pliegue de
                   entrenamiento, cada uno en uno solo, con tamaños que difieren a
                   lo sumo en 1.
  barajadas        Con las etiquetas del pliegue de entrenamiento barajadas, la pAUC
                   de la red cae en el 99 % central de 1.000 puntuaciones
                   aleatorias; con las etiquetas reales queda por encima de ese
                   rango, con logits que varían y sin negativos repetidos.
  calendario       La tasa registrada en cada paso de la red real sigue OneCycle:
                   empieza en TASA/25, llega a TASA en el 10 % de los pasos, sube
                   antes y baja después, y termina en TASA/25/10⁴.
  reproducibilidad Dos redes de 2 épocas con la misma semilla dan logits idénticos.
  prediccion       Sin aumentos, predecir dos veces la misma validación con los
                   pesos de la red real da el mismo logit.
  alineacion       fase4c.ensamblar, que también une las puntuaciones de la 4e.
  referencias      Las predicciones de M3 limpio y las puntuaciones de la red de la
                   4c pasan sus comprobaciones; los pliegues de las semillas 0 a 9
                   tienen la huella de outputs/fase4-m2-vs-m1.json.
  c7               La alineación de C4 con la puntuación de la red de la 4e en la
                   validación de la semilla 1, pliegue 0.
  ajuste_fino      LibAUC importa y su pAUC_CVaR_Loss corre en MPS igual que en
                   CPU; con datos sintéticos, la métrica oficial es la pAUC
                   unilateral con FPR ≤ 0,2 de las clases invertidas, y la pérdida,
                   con las clases invertidas, responde a subir los positivos de
                   menor puntuación y no a subir los de mayor puntuación.

Casos que deben fallar: quitar un aumento; predecir con la interpolación
bicúbica de la 4c; los sorteos de la 4c repiten negativos entre épocas; una
puntuación sintética de las etiquetas con ruido queda fuera del rango y una
constante no pasa por red real; una tasa fija; un logit cambiado en 1e-6; con
los aumentos activos al predecir, el logit cambia; los de alineación y
referencias de la 4c; las columnas de C7 corridas una fila; sin invertir las
clases, ni la pAUC coincide con la métrica oficial ni la pérdida responde solo a
los positivos de menor puntuación.

Con --rapido, las redes entrenan 2 épocas y puntúan los positivos de la
validación y 4.000 de sus negativos. Sin --rapido, la barajada y la real entrenan
las 20 épocas y puntúan toda la validación, y --out tiene que ir en data/.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_controles.py --rapido --out RUTA.json
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_controles.py \\
        --out data/fase4e-controles.json
Devuelve 0 si todo se comporta como se espera.
"""

import argparse
import copy
import importlib.util
import json
import math
import os
import sys
import time
import warnings

import numpy as np
import torch
from sklearn.metrics import roc_curve
from torchvision import transforms

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import fase4c_comparar as f4cc  # noqa: E402
import fase4e  # noqa: E402
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
OFICIAL = os.path.join(RAIZ, "referencias", "_texto-completo", "upstream-PrimaryMetric-pAUC.py")
G, Y = "patient_id", "target"
SEMILLA, PLIEGUE = 1, 0
NEGATIVOS_RAPIDO = 4000
EPOCAS_RAPIDO = 2
EPOCAS_REPRODUCIBILIDAD = 2
BETA = 0.2

# Los casos se registran en la lista de test_fase4c_controles, para reusar sus
# controles de alineación y de referencias tal cual.
resultados = t4c.resultados
registrar = t4c.registrar
se_detiene = t4c.se_detiene


def pliegue(d):
    return construir_folds(d["df"], G, Y, 5, SEMILLA)[PLIEGUE]


# ---- aumentos y conjuntos ---------------------------------------------------------------------

def control_aumentos():
    nuestro, autor = fase4e.describir(fase4e.aumentos_entrenamiento()), fase4e.describir(fase4e.autor_p2())
    registrar("aumentos", "el patrón 2 coincide con train_transform_p2 del autor, tal como lo cita la ficha",
              nuestro == autor, f"{len(nuestro)} pasos: {', '.join(p['nombre'] for p in nuestro)}")
    sin_uno = transforms.Compose(fase4e.aumentos_entrenamiento().transforms[:6]
                                 + fase4e.aumentos_entrenamiento().transforms[7:])
    registrar("aumentos", "quitando el desenfoque gaussiano", fase4e.describir(sin_uno) != autor,
              "se detecta", debe_fallar=True)
    pred, pred_autor = (fase4e.describir(fase4e.preprocesado_prediccion()),
                        fase4e.describir(fase4e.autor_p2("valid_transform_p2")))
    registrar("aumentos", "la predicción coincide con valid_transform_p2 del autor", pred == pred_autor,
              f"{', '.join(p['nombre'] for p in pred)}; interpolación {pred[0]['interpolation']}")
    bicubica = transforms.Compose([transforms.Resize((fase4e.LADO, fase4e.LADO),
                                                     interpolation=transforms.InterpolationMode.BICUBIC),
                                   *fase4e.preprocesado_prediccion().transforms[1:]])
    registrar("aumentos", "la predicción con la interpolación bicúbica de la 4c", fase4e.describir(bicubica) != pred_autor,
              "se detecta", debe_fallar=True)
    return {"entrenamiento": nuestro, "prediccion": pred}


def control_conjuntos(d):
    tr, _ = pliegue(d)
    pos, neg = tr[d["y"][tr] == 1], tr[d["y"][tr] == 0]
    grupos = fase4e.conjuntos_de_negativos(neg, fase4e.CONJUNTOS, np.random.default_rng(SEMILLA))
    todos = np.concatenate(grupos)
    tam = [len(g) for g in grupos]
    ok = (len(grupos) == fase4e.CONJUNTOS and len(todos) == len(neg) and np.array_equal(np.sort(todos), np.sort(neg))
          and max(tam) - min(tam) <= 1)
    registrar("conjuntos", f"los {fase4e.CONJUNTOS} conjuntos reparten todos los negativos, cada uno en uno solo", ok,
              f"{len(pos)} positivos, {len(neg)} negativos; conjuntos de {min(tam)} a {max(tam)}")
    rng = np.random.default_rng(SEMILLA)
    sorteos = [rng.choice(neg, size=fase4c.NEGATIVOS_POR_POSITIVO * len(pos), replace=False)
               for _ in range(fase4e.EPOCAS)]
    unidos = np.concatenate(sorteos)
    rep = int(len(unidos) - len(np.unique(unidos)))
    registrar("conjuntos", f"los sorteos de la Fase 4c, {fase4e.EPOCAS} épocas", rep > 0,
              f"{rep} negativos en más de una época", debe_fallar=True)
    return {"positivos": int(len(pos)), "negativos": int(len(neg)), "tamanos": [min(tam), max(tam)],
            "repetidos_con_los_sorteos_de_la_4c": rep}


def one_cycle(pasos):
    """La tasa de cada paso de OneCycle con dos fases y descenso en coseno, escrita
    desde su definición y no con torch: de TASA/25 a TASA hasta el paso
    PCT_INICIO·pasos − 1, y de TASA a TASA/25/10⁴ hasta el último. El pico cae
    entre dos pasos cuando PCT_INICIO·pasos no es entero."""
    inicio, maximo = fase4e.TASA / 25, fase4e.TASA
    fin = inicio / 1e4
    fin_1, fin_2 = fase4e.PCT_INICIO * pasos - 1, pasos - 1

    def coseno(a, b, x):
        return b + (a - b) / 2 * (math.cos(math.pi * x) + 1)
    return np.array([coseno(inicio, maximo, k / fin_1) if k <= fin_1 else
                     coseno(maximo, fin, (k - fin_1) / (fin_2 - fin_1)) for k in range(pasos)])


def calendario_ok(tasas, pasos):
    t = np.asarray(tasas, dtype=np.float64)
    if len(t) != pasos or len(t) < 20:
        return False, f"{len(t)} tasas para {pasos} pasos"
    esperado = one_cycle(pasos)
    dif = float(np.max(np.abs(t - esperado) / esperado))
    pico = int(np.argmax(t))
    ok = dif <= 1e-9 and abs(pico - (fase4e.PCT_INICIO * pasos - 1)) <= 1
    return ok, (f"{pasos} pasos; mayor diferencia relativa con OneCycle {dif:.3g}; empieza en {t[0]:.3g}, máximo "
                f"{t.max():.6g} en el paso {pico} ({pico / pasos:.3f} de los pasos), termina en {t[-1]:.3g}")


# ---- redes -----------------------------------------------------------------------------------

def subconjunto_de_validacion(d, va):
    rng = np.random.default_rng(SEMILLA)
    pos, neg = va[d["y"][va] == 1], va[d["y"][va] == 0]
    return np.sort(np.concatenate([pos, rng.choice(neg, size=NEGATIVOS_RAPIDO, replace=False)]))


def controles_con_red(d, dispositivo, rapido):
    tr, va = pliegue(d)
    va_eval, epocas = (subconjunto_de_validacion(d, va), EPOCAS_RAPIDO) if rapido else (va, fase4e.EPOCAS)
    y_va = d["y"][va_eval]
    pesos = os.path.join(RAIZ, "data", "fase4e-controles-red-real" + ("-rapido" if rapido else "") + ".pt")

    barajadas = d["y"].copy()
    barajadas[tr] = np.random.default_rng(SEMILLA).permutation(d["y"][tr])
    logit_b, reg_b = fase4e.entrenar_y_puntuar(HDF5, d["isic"], barajadas, tr, va_eval, SEMILLA, dispositivo,
                                               epocas=epocas)
    logit_r, reg_r = fase4e.entrenar_y_puntuar(HDF5, d["isic"], d["y"], tr, va_eval, SEMILLA, dispositivo,
                                               epocas=epocas, tasas=True, pesos_en=pesos)
    banda, media = t4c.banda_aleatoria(y_va)
    pauc_b = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit_b)))
    dis_b, dis_r = t4c.dispersion(logit_b), t4c.dispersion(logit_r)
    registrar("barajadas", "la red con las etiquetas barajadas, dentro del 99 % central del azar",
              t4c.dentro(pauc_b, banda),
              f"pAUC {pauc_b:.4f}; rango [{banda[0]:.4f}; {banda[1]:.4f}], media {media:.4f}; {len(va_eval)} filas, "
              f"{int(y_va.sum())} positivos, {epocas} épocas; {dis_b['logits_distintos']} logits distintos")
    sintetica = y_va + 0.1 * np.random.default_rng(2).normal(size=len(y_va))
    pauc_s = float(pauc_above_tpr(y_va, sintetica))
    registrar("barajadas", "las etiquetas más un poco de ruido", not t4c.dentro(pauc_s, banda), f"pAUC {pauc_s:.4f}",
              debe_fallar=True)
    pauc_r = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit_r)))
    ok = (pauc_r > banda[1] and dis_r["logits_distintos"] > 1 and dis_r["desviacion_del_logit"] > 0
          and reg_r["negativos_en_mas_de_una_epoca"] == 0)
    registrar("barajadas", "la red con las etiquetas reales, por encima del rango, con logits que varían y sin "
              "negativos repetidos", ok,
              f"pAUC {pauc_r:.4f} frente al límite {banda[1]:.4f}; {dis_r['logits_distintos']} logits distintos, "
              f"desviación {dis_r['desviacion_del_logit']:.3g}; {reg_r['negativos_en_mas_de_una_epoca']} negativos "
              "en más de una época")
    constante = np.zeros(len(y_va), dtype=np.float32)
    pauc_c = float(pauc_above_tpr(y_va, fase4c.probabilidad(constante)))
    registrar("barajadas", "una puntuación constante como red real", not (pauc_c > banda[1]),
              f"pAUC {pauc_c:.4f}; 1 logit distinto", debe_fallar=True)

    ok_cal, det_cal = calendario_ok(reg_r["tasas"], reg_r["pasos_del_calendario"])
    registrar("calendario", "la tasa de cada paso de la red real sigue OneCycle", ok_cal, det_cal)
    fija = [fase4e.TASA] * reg_r["pasos_del_calendario"]
    ok_fija, det_fija = calendario_ok(fija, reg_r["pasos_del_calendario"])
    registrar("calendario", "una tasa fija", not ok_fija, det_fija, debe_fallar=True)

    l1, r1 = fase4e.entrenar_y_puntuar(HDF5, d["isic"], d["y"], tr, va_eval, SEMILLA, dispositivo,
                                       epocas=EPOCAS_REPRODUCIBILIDAD)
    l2, r2 = fase4e.entrenar_y_puntuar(HDF5, d["isic"], d["y"], tr, va_eval, SEMILLA, dispositivo,
                                       epocas=EPOCAS_REPRODUCIBILIDAD)
    rep = t4c.coinciden(l1, l2)
    registrar("reproducibilidad", f"la misma red de {EPOCAS_REPRODUCIBILIDAD} épocas dos veces", rep["identicos"],
              f"idénticos: {rep['identicos']}; mayor diferencia de logit {rep['maxima_diferencia']:.3g} en "
              f"{rep['filas']} filas")
    tocado = np.array(l1, dtype=np.float64)
    tocado[0] += 1e-6
    registrar("reproducibilidad", "un logit cambiado en 1e-6", not t4c.coinciden(l1, tocado)["identicos"],
              "idénticos: False", debe_fallar=True)

    modelo, _ = fase4e.red(dispositivo)
    modelo.load_state_dict(torch.load(pesos, map_location=dispositivo))
    p1 = fase4e.predecir(modelo, HDF5, d["isic"][va_eval], dispositivo)
    p2 = fase4e.predecir(modelo, HDF5, d["isic"][va_eval], dispositivo)
    pa = fase4e.predecir(modelo, HDF5, d["isic"][va_eval], dispositivo,
                         transformacion=fase4e.aumentos_entrenamiento(), semilla=SEMILLA)
    c12, c1a, c1r = t4c.coinciden(p1, p2), t4c.coinciden(p1, pa), t4c.coinciden(p1, logit_r)
    registrar("prediccion", "sin aumentos, predecir dos veces la misma validación da el mismo logit, el de la red",
              c12["identicos"] and c1r["identicos"],
              f"idénticos entre sí: {c12['identicos']}; con el logit del entrenamiento: {c1r['identicos']}")
    registrar("prediccion", "con los aumentos activos al predecir", not c1a["identicos"],
              f"mayor diferencia de logit {c1a['maxima_diferencia']:.3g}", debe_fallar=True)
    del modelo
    torch.mps.empty_cache()
    return logit_r, {
        "pliegue": {"semilla": SEMILLA, "pliegue": PLIEGUE, "filas_validacion": int(len(va_eval)),
                    "positivos_validacion": int(y_va.sum())},
        "barajadas": {"pauc": round(pauc_b, 4), "rango_99": [round(b, 4) for b in banda],
                      "media_aleatoria": round(media, 4), "red": reg_b},
        "real": {"pauc": round(pauc_r, 4), **dis_r, "red": {k: v for k, v in reg_r.items() if k != "tasas"},
                 "pesos": os.path.relpath(pesos, RAIZ)},
        "calendario": det_cal, "reproducibilidad": {**rep, "redes": [r1, r2]},
        "prediccion": {"sin_aumentos": c12, "con_aumentos": c1a},
    }, va_eval


# ---- c7 --------------------------------------------------------------------------------------

def control_c7(d, logit_4e, va_eval, red_4c):
    """La alineación de C4 con una puntuación en la que la validación de la semilla 1,
    pliegue 0, lleva el logit de la red de la 4e; el resto, el de la red de la 4c
    en esa semilla. Es la misma ruta de código que seguirá C7."""
    tr, va = pliegue(d)
    p = f4cc.de_semilla(red_4c, SEMILLA, d["isic"]).copy()
    p[va_eval] = fase4c.probabilidad(logit_4e)
    x_tr, x_va, _, _ = ganador_m3.variables_m3_en_pliegue(d["df_sin_etiqueta"], tr, va, d["excluidas"], G)
    a = fase4c.variables_red(p, tr, va, d["grupos"])
    xc_tr, _ = fase4b.con_imagen(x_tr, x_va, a)
    alin = f4b.comprobar_alineacion(x_tr, xc_tr, a, SEMILLA, d["y"][tr], d["grupos"][tr])
    posicion = {int(r): i for i, r in enumerate(va)}
    en_va = bool(np.array_equal(a["va"]["puntuacion"][[posicion[int(r)] for r in va_eval]],
                                fase4c.probabilidad(logit_4e)))
    registrar("c7", "alineación de C4 con la puntuación de la red de la 4e, antes y después del remuestreo",
              all(alin[k] for k in ("antes", "razon", "despues")) and en_va, f"{alin}; la validación lleva la 4e: {en_va}")
    rodado = {"tr": {"puntuacion": np.roll(a["tr"]["puntuacion"], 1), "razon": np.roll(a["tr"]["razon"], 1)},
              "va": a["va"]}
    xr_tr, _ = fase4b.con_imagen(x_tr, x_va, rodado)
    alin_r = f4b.comprobar_alineacion(x_tr, xr_tr, a, SEMILLA, d["y"][tr], d["grupos"][tr])
    registrar("c7", "las columnas corridas una fila", not alin_r["antes"], f"{alin_r}", debe_fallar=True)
    return {"alineacion": alin}


# ---- ajuste fino -----------------------------------------------------------------------------

def pauc_unilateral(y, s, max_fpr=BETA):
    """El área bajo la ROC de (y, s) con FPR entre 0 y max_fpr, sin normalizar, con la
    curva interpolada linealmente en max_fpr."""
    fpr, tpr, _ = roc_curve(y, s)
    corte = np.interp(max_fpr, fpr, tpr)
    dentro_ = fpr <= max_fpr
    x, z = np.r_[fpr[dentro_], max_fpr], np.r_[tpr[dentro_], corte]
    return float(np.trapezoid(z, x))


def respuesta_de_la_perdida(libauc_losses, y, p, invertir, n_mover=10, subida=0.2, iteraciones=3000):
    """La pérdida de pAUC_CVaR_Loss, con sus variables duales llevadas al equilibrio
    sobre (y, p), y cuánto baja al subir los n_mover positivos de menor y de mayor
    puntuación. Con invertir, la clase positiva es la benigna y la puntuación 1 − p."""
    y_t, s_t = (1 - y, 1 - p) if invertir else (y, p)
    n = len(y)
    perdida = libauc_losses.pAUC_CVaR_Loss(data_len=n, pos_len=int(y_t.sum()), beta=BETA,
                                           device=torch.device("cpu"))
    yt, idx = torch.tensor(y_t, dtype=torch.float32), torch.arange(n)
    with torch.no_grad():
        for _ in range(iteraciones):
            perdida(torch.tensor(s_t, dtype=torch.float32), yt, idx)

    def valor(pp):
        ss = 1 - pp if invertir else pp
        with torch.no_grad():
            return float(copy.deepcopy(perdida)(torch.tensor(ss, dtype=torch.float32), yt, idx))
    malignos = np.flatnonzero(y == 1)
    orden = malignos[np.argsort(p[malignos])]
    base = valor(p)
    bajos, altos = p.copy(), p.copy()
    bajos[orden[:n_mover]] = np.minimum(bajos[orden[:n_mover]] + subida, 1.0)
    altos[orden[-n_mover:]] = np.minimum(altos[orden[-n_mover:]] + subida, 1.0)
    caida_bajos, caida_altos = base - valor(bajos), base - valor(altos)
    return {"perdida": round(base, 6), "caida_subiendo_los_de_menor_puntuacion": round(caida_bajos, 6),
            "caida_subiendo_los_de_mayor_puntuacion": round(caida_altos, 6),
            "cociente": round(abs(caida_altos) / caida_bajos, 6) if caida_bajos > 0 else None}


def control_ajuste_fino():
    try:
        import libauc
        from libauc import losses as libauc_losses
    except ImportError as e:
        registrar("ajuste_fino", "LibAUC importa", False, f"{e}")
        return {"libauc": None}
    import importlib.metadata as md
    informe = {"libauc": {"version": md.version("libauc"), "archivo": os.path.relpath(libauc.__file__, RAIZ),
                          "licencia": "MIT"}}

    # Corre en MPS como en CPU: un paso con los mismos pesos.
    torch.manual_seed(0)
    n = 512
    y = (torch.rand(n) < 0.2).float()
    x = torch.randn(n, 8)
    base = torch.nn.Linear(8, 1)
    pasos = {}
    for dev in ("cpu", "mps"):
        dd = torch.device(dev)
        w = copy.deepcopy(base).to(dd)
        lf = libauc_losses.pAUC_CVaR_Loss(data_len=n, pos_len=int(y.sum()), beta=BETA, device=dd)
        valor = lf(torch.sigmoid(w(x.to(dd))), y.to(dd), torch.arange(n).to(dd))
        valor.backward()
        pasos[dev] = (float(valor), w.weight.grad.cpu().clone(), lf.u_pos.cpu().clone())
    d_grad = float((pasos["cpu"][1] - pasos["mps"][1]).abs().max())
    d_u = float((pasos["cpu"][2] - pasos["mps"][2]).abs().max())
    registrar("ajuste_fino", f"LibAUC {informe['libauc']['version']}: pAUC_CVaR_Loss corre en MPS como en CPU",
              pasos["cpu"][0] == pasos["mps"][0] and d_grad <= 1e-6 and d_u == 0.0,
              f"pérdida {pasos['cpu'][0]:.6f} y {pasos['mps'][0]:.6f}; mayor diferencia del gradiente {d_grad:.3g}, "
              f"de la variable dual {d_u:.3g}")

    # La región: la métrica oficial es la pAUC unilateral de las clases invertidas.
    if not os.path.exists(OFICIAL):
        registrar("ajuste_fino", "la copia local del script oficial", False,
                  f"no está {os.path.relpath(OFICIAL, RAIZ)}")
        return informe
    spec = importlib.util.spec_from_file_location("oficial", OFICIAL)
    oficial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oficial)
    rng = np.random.default_rng(0)
    casos = []
    for k in range(40):
        m = int(rng.integers(200, 5000))
        yy = (rng.random(m) < float(rng.uniform(0.01, 0.3))).astype(int)
        if yy.sum() < 2:
            continue
        s = rng.normal(0, 1, m) + rng.uniform(0, 3) * yy
        if k % 3 == 0:
            s = np.round(s, 1)
        s = 1 / (1 + np.exp(-s))
        casos.append((oficial.p_auc_tpr(yy, s, min_tpr=0.80), pauc_unilateral(1 - yy, -s), pauc_unilateral(yy, s)))
    c = np.array(casos)
    d_inv, d_sin = float(np.abs(c[:, 0] - c[:, 1]).max()), float(np.abs(c[:, 0] - c[:, 2]).max())
    registrar("ajuste_fino", "la métrica oficial es la pAUC unilateral con FPR ≤ 0,2 de las clases invertidas",
              d_inv <= 1e-12, f"{len(c)} casos sintéticos con empates; mayor diferencia {d_inv:.3g}")
    registrar("ajuste_fino", "sin invertir las clases", d_sin > 1e-3, f"mayor diferencia {d_sin:.3g}",
              debe_fallar=True)

    # La pérdida responde a los positivos de menor puntuación.
    yy = np.r_[np.ones(50), np.zeros(1000)].astype(int)
    p = 1 / (1 + np.exp(-(rng.normal(0, 1, len(yy)) + 1.5 * yy)))
    inv = respuesta_de_la_perdida(libauc_losses, yy, p, invertir=True)
    sin = respuesta_de_la_perdida(libauc_losses, yy, p, invertir=False)
    registrar("ajuste_fino", "con las clases invertidas, la pérdida responde a subir los 10 malignos de menor "
              "puntuación y no a subir los 10 de mayor",
              inv["cociente"] is not None and inv["cociente"] < 0.05, f"{inv}")
    registrar("ajuste_fino", "sin invertir las clases", sin["cociente"] is None or sin["cociente"] >= 0.05, f"{sin}",
              debe_fallar=True)
    informe.update({"mps_frente_a_cpu": {"diferencia_gradiente": d_grad, "diferencia_dual": d_u},
                    "region": {"casos": len(c), "diferencia_invertidas": d_inv, "diferencia_sin_invertir": d_sin},
                    "respuesta": {"invertidas": inv, "sin_invertir": sin}})
    return informe


def control_red_4c(d):
    tabla, proc = f4cc.cargar_red(f4cc.RED, internos=False)
    ok = all(len(f4cc.de_semilla(tabla, s, d["isic"])) == len(d["isic"]) for s in range(10))
    registrar("referencias", "las puntuaciones de la red de la 4c pasan sus comprobaciones y cubren cada semilla", ok,
              f"{os.path.relpath(f4cc.RED, RAIZ)}, SHA-256 {proc['sha256'][:12]}…")
    return tabla


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--out", required=True, help="JSON con el resultado de cada caso")
    args = ap.parse_args()
    if not args.rapido:
        destino = os.path.realpath(args.out)
        if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "data")) + os.sep):
            raise SystemExit("ERROR: la corrida completa de los controles va en data/.")
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    informe = {"aumentos": control_aumentos(), "ajuste_fino": control_ajuste_fino()}
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    d = {"df": df, "df_sin_etiqueta": df.drop(columns=[Y]), "excluidas": cargar_columnas_excluidas(FUGAS),
         "y": df[Y].to_numpy(), "grupos": df[G].to_numpy(), "isic": df["isic_id"].to_numpy()}
    print(f"Datos de desarrollo: {len(df)} filas", flush=True)
    informe["conjuntos"] = control_conjuntos(d)
    t4c.control_alineacion(d)
    t4c.control_referencias(d)
    red_4c = control_red_4c(d)
    logit_4e, informe["redes"], va_eval = controles_con_red(d, torch.device("mps"), args.rapido)
    informe["c7"] = control_c7(d, logit_4e, va_eval, red_4c)

    total = round(time.perf_counter() - t_total, 1)
    malos = [r for r in resultados if not r["ok"]]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"rapido": args.rapido, "datos": datos,
                   "alcance": (f"redes de {EPOCAS_RAPIDO} épocas sobre los positivos de la validación y "
                               f"{NEGATIVOS_RAPIDO} negativos" if args.rapido else
                               "redes con la receta de la fase, sobre toda la validación"),
                   "semilla_y_pliegue_de_las_redes": [SEMILLA, PLIEGUE],
                   "segundos": total, "casos": resultados, "fallos": len(malos), **informe,
                   "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                               "caffeinate": bajo_caffeinate}}, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; {total} s. Escrito: {args.out}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

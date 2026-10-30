#!/usr/bin/env python3
"""
test_fase4d_comparacion.py — los controles de la comparación de la Fase 4d
(PLAN.md, «Lo que cambia en la forma de comparar» y decisiones 1 a 3), antes de
leer cualquier resultado. No entrena ningún modelo ni responde ninguna pregunta.

  equivalencia  pAUC/0,2 es la especificidad media cuando la sensibilidad recorre
                de 0,8 a 1: en 40 casos sintéticos con empates, el script oficial
                (copia local, referencias/_texto-completo/upstream-PrimaryMetric-pAUC.py)
                coincide con pauc_above_tpr y con 0,2 veces esa especificidad
                media; un clasificador perfecto da 0,2.
  negativo      1.000 juegos sintéticos de 50 y de 25 diferencias con media 0 y
                correlación 0,2 entre ellas, la que la corrección supone: la prueba
                corregida (fase4d.valor_p) rechaza al 5 % a lo sumo el 5 % de las
                veces, con el error de Monte Carlo (a lo sumo el cuantil 0,95 de
                una binomial de 1.000 y 0,05: 62).
  positivo      Sobre las predicciones guardadas de M3 limpio, las puntuaciones
                de los positivos de cada pliegue de validación se suben en la
                escala del logit con el mismo desplazamiento, buscado por bisección
                hasta una diferencia media de pAUC de +0,02 (±0,002): en las 10
                semillas y en las semillas 0 a 4, el valor p queda por debajo de
                0,05/3 y Holm da el resultado a favor.
  holm          Con valores p sintéticos: acepta en orden, se detiene en la
                primera que no pasa, una diferencia negativa no da resultado a
                favor, y acepta más que Bonferroni cuando debe.
  coherencia    El valor p es el de los intervalos: a la confianza 1 − p, un
                extremo del intervalo de fase4b_comparar.nadeau_bengio es 0.

Casos que deben fallar: la especificidad media sobre toda la curva no da
pAUC/0,2; la t sin corregir rechaza más del límite en el control negativo; el
desplazamiento con el signo contrario no da resultado a favor; un Holm que no se
detuviera aceptaría la tercera pregunta del caso b; con el valor p sin corregir,
el extremo del intervalo no es 0.

Descriptivo, sin caso: el control negativo que proponía el borrador, intercambiar
dentro de cada pliegue las puntuaciones de los dos modelos, sobre las 50
diferencias guardadas de C4 − M3 limpio, y el valor p de esas diferencias
(PLAN.md, Fase 4d, «Lectura declarada» y decisión 1).

Con --rapido, 200 juegos en vez de 1.000 en los controles sintéticos, con su
propio límite binomial. Sin --rapido, --out va en outputs/.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4d_comparacion.py --rapido --out RUTA
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4d_comparacion.py \\
        --out outputs/fase4d-controles-comparacion
Escribe RUTA.json y RUTA.md. Devuelve 0 si todo se comporta como se espera.
"""

import argparse
import importlib.util
import json
import os
import sys
import time
import warnings

import numpy as np
from scipy import stats
from scipy.special import expit, logit
from sklearn.metrics import roc_curve

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b_comparar as f4b  # noqa: E402
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from train_and_evaluate import construir_folds, pauc_above_tpr  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
OFICIAL = os.path.join(RAIZ, "referencias", "_texto-completo", "upstream-PrimaryMetric-pAUC.py")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
REF_M3L = os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json")
C4 = os.path.join(RAIZ, "outputs", "fase4c-c4-vs-m3limpio.json")
G, Y = "patient_id", "target"
RHO = 0.2  # n_prueba/(n_entrenamiento + n_prueba) con 5 pliegues: la que supone 1/(k − 1) = 0,25
OBJETIVO, MARGEN = 0.02, 0.002
N_SPLITS = 5

resultados = []


def registrar(control, caso, ok, detalle, debe_fallar=False):
    resultados.append({"control": control, "caso": caso, "ok": bool(ok), "debe_fallar": debe_fallar,
                       "detalle": detalle})
    print(f"[{'OK' if ok else 'FALLA'}] {control} · {caso}{' (debe fallar)' if debe_fallar else ''}: {detalle}",
          flush=True)


# ---- equivalencia ----------------------------------------------------------------------------

def especificidad_media(y, s, desde=0.8, hasta=1.0, n=200001):
    """La especificidad, 1 − FPR, sobre la curva ROC original interpolada linealmente,
    promediada cuando la sensibilidad recorre de `desde` a `hasta`."""
    fpr, tpr, _ = roc_curve(y, s)
    g = np.linspace(desde, hasta, n)
    return float(np.trapezoid(1 - np.interp(g, tpr, fpr), g) / (hasta - desde))


def control_equivalencia():
    if not os.path.exists(OFICIAL):
        registrar("equivalencia", "la copia local del script oficial", False,
                  f"no está {os.path.relpath(OFICIAL, RAIZ)}: hay que volver a obtenerla desde la URL de su ficha")
        return {}
    spec = importlib.util.spec_from_file_location("oficial", OFICIAL)
    oficial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oficial)
    rng = np.random.default_rng(0)
    casos = []
    for k in range(40):
        n = int(rng.integers(200, 5000))
        prev = float(rng.uniform(0.01, 0.3))
        y = (rng.random(n) < prev).astype(int)
        if y.sum() < 2:
            continue
        separacion = rng.uniform(0, 3)
        s = rng.normal(0, 1, n) + separacion * y
        if k % 3 == 0:
            s = np.round(s, 1)  # empates
        s = 1 / (1 + np.exp(-s))
        casos.append((oficial.p_auc_tpr(y, s, min_tpr=0.80), pauc_above_tpr(y, s), 0.2 * especificidad_media(y, s),
                      especificidad_media(y, s, desde=0.0)))
    c = np.array(casos)
    d_proyecto = float(np.abs(c[:, 0] - c[:, 1]).max())
    d_espec = float(np.abs(c[:, 0] - c[:, 2]).max())
    d_toda = float(np.abs(c[:, 0] / 0.2 - c[:, 3]).max())
    y = np.r_[np.zeros(1000), np.ones(100)].astype(int)
    perfecto = float(oficial.p_auc_tpr(y, y.astype(float), min_tpr=0.80))
    registrar("equivalencia", "el script oficial y pauc_above_tpr", d_proyecto == 0.0,
              f"{len(c)} casos; máxima diferencia {d_proyecto:.3g}")
    registrar("equivalencia", "pAUC = 0,2 × especificidad media con sensibilidad de 0,8 a 1", d_espec <= 1e-6,
              f"máxima diferencia {d_espec:.3g}, el error de la integración numérica")
    registrar("equivalencia", "un clasificador perfecto da 0,2", abs(perfecto - 0.2) < 1e-12, f"{perfecto!r}")
    registrar("equivalencia", "la especificidad media sobre toda la curva como pAUC/0,2", d_toda > 1e-3,
              f"máxima diferencia {d_toda:.3g}", debe_fallar=True)
    return {"casos": len(c), "maxima_diferencia_oficial_vs_proyecto": d_proyecto,
            "maxima_diferencia_oficial_vs_0_2_por_especificidad_media": d_espec, "perfecto": perfecto,
            "maxima_diferencia_con_toda_la_curva": d_toda}


# ---- negativo --------------------------------------------------------------------------------

def correlacionadas(rng, juegos, n, rho):
    """juegos × n diferencias normales de media 0 con correlación rho entre todas."""
    comun = rng.standard_normal((juegos, 1))
    return np.sqrt(rho) * comun + np.sqrt(1 - rho) * rng.standard_normal((juegos, n))


def control_negativo(juegos):
    limite = int(stats.binom.ppf(0.95, juegos, fase4d.ALFA))
    rng = np.random.default_rng(2026)
    informe = {"juegos": juegos, "correlacion": RHO, "limite_de_rechazos": limite,
               "probabilidad_de_pasar_el_limite_con_tasa_real_del_5": float(stats.binom.sf(limite, juegos, fase4d.ALFA))}
    for n in (50, 25):
        z = correlacionadas(rng, juegos, n, RHO)
        corregida = int(sum(fase4d.valor_p(x, N_SPLITS) < fase4d.ALFA for x in z))
        ingenua = int(sum(fase4d.valor_p_ingenuo(x) < fase4d.ALFA for x in z))
        informe[f"{n}_diferencias"] = {"rechazos_corregida": corregida, "rechazos_sin_corregir": ingenua}
        registrar("negativo", f"{n} diferencias: la prueba corregida rechaza a lo sumo el 5 %", corregida <= limite,
                  f"{corregida} de {juegos}; límite {limite}")
        registrar("negativo", f"{n} diferencias: la t sin corregir", ingenua > limite, f"{ingenua} de {juegos}",
                  debe_fallar=True)
    return informe


def descartado_del_borrador(juegos):
    """El intercambio por pliegue del borrador, sobre C4 − M3 limpio: descriptivo."""
    with open(C4, encoding="utf-8") as f:
        m = json.load(f)["metricas"]
    c4, m3 = m["C4"]["pauc"]["por_semilla_y_fold"], m["M3limpio"]["pauc"]["por_semilla_y_fold"]
    diffs = np.array([b - a for s in sorted(c4, key=int) for a, b in zip(m3[s], c4[s])])
    signos = np.random.default_rng(0).choice([-1, 1], size=(juegos, len(diffs)))
    corregida = int(sum(fase4d.valor_p(diffs * s, N_SPLITS) < fase4d.ALFA for s in signos))
    ingenua = int(sum(fase4d.valor_p_ingenuo(diffs * s) < fase4d.ALFA for s in signos))
    p = fase4d.valor_p(diffs, N_SPLITS)
    print(f"[descriptivo] intercambio por pliegue sobre C4 − M3 limpio: {corregida} y {ingenua} rechazos de {juegos}; "
          f"valor p de C4 − M3 limpio {p:.4f}", flush=True)
    return {"que_es": ("El control negativo del borrador: intercambiar al azar, dentro de cada pliegue, las "
                       "puntuaciones de C4 y de M3 limpio, que invierte el signo de la diferencia de ese pliegue. "
                       "Descartado por la decisión 1: ninguna de las dos pruebas puede fallarlo."),
            "diferencias": f"{os.path.relpath(C4, RAIZ)} > metricas.*.pauc.por_semilla_y_fold, a 4 decimales",
            "juegos": juegos, "rechazos_corregida": corregida, "rechazos_sin_corregir": ingenua,
            "valor_p_c4_menos_m3limpio": round(p, 4)}


# ---- positivo --------------------------------------------------------------------------------

def control_positivo():
    predicciones, procedencia = f4b.cargar_predicciones(f4b.PREDICCIONES)
    df, _ = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    y, grupos, isic = df[Y].to_numpy(), df[G].to_numpy(), df["isic_id"].to_numpy()
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        huellas = json.load(f)["folds"]["sha256_por_semilla"]
    with open(REF_M3L, encoding="utf-8") as f:
        ref = json.load(f)["metricas"]["M3limpio"]["pauc"]["por_semilla_y_fold"]
    pliegues = []
    for s in range(10):
        folds = construir_folds(df, G, Y, N_SPLITS, s)
        if f4.huella_folds(folds, len(df)) != huellas[str(s)]:
            raise SystemExit(f"ERROR: los pliegues de la semilla {s} no son los de {REF_PLIEGUES}.")
        for i, (_, va) in enumerate(folds):
            base = f4b.guardada(predicciones, "M3limpio", s, i, isic[va])
            pauc = float(pauc_above_tpr(y[va], base))
            if round(pauc, 4) != ref[str(s)][i]:
                raise SystemExit(f"ERROR: M3 limpio no reproduce {REF_M3L} en la semilla {s}, pliegue {i}.")
            pliegues.append((s, y[va], base, pauc))

    def diferencias(c, semillas):
        salida = []
        for s, yv, base, pauc in pliegues:
            if s not in semillas:
                continue
            sub = base.copy()
            pos = yv == 1
            sub[pos] = expit(logit(base[pos]) + c)
            salida.append(float(pauc_above_tpr(yv, sub)) - pauc)
        return np.array(salida)

    informe = {"predicciones": os.path.relpath(f4b.PREDICCIONES, RAIZ), "sha256": procedencia["sha256"],
               "reproduce": os.path.relpath(REF_M3L, RAIZ), "objetivo": OBJETIVO, "margen": MARGEN}
    otras = [{"pregunta": "relleno 1", "valor_p": 1.0, "media": 0.0}, {"pregunta": "relleno 2", "valor_p": 1.0,
                                                                        "media": 0.0}]
    for nombre, semillas in (("10 semillas", set(range(10))), ("semillas 0 a 4", set(range(5)))):
        lo, hi = 0.0, 8.0
        for _ in range(40):
            c = (lo + hi) / 2
            media = diferencias(c, semillas).mean()
            if abs(media - OBJETIVO) <= MARGEN / 4:
                break
            lo, hi = (c, hi) if media < OBJETIVO else (lo, c)
        d = diferencias(c, semillas)
        p = fase4d.valor_p(d, N_SPLITS)
        h = fase4d.holm([{"pregunta": "desplazada", "valor_p": p, "media": float(d.mean())}] + otras)[0]
        registrar("positivo", f"{nombre}: +{OBJETIVO} en la pAUC, valor p por debajo de 0,05/3 y a favor",
                  abs(d.mean() - OBJETIVO) <= MARGEN and p < fase4d.ALFA / fase4d.N_PREGUNTAS and h["a_favor"],
                  f"desplazamiento {c:.4f} en el logit; diferencia media {d.mean():.4f} en {len(d)} pliegues; "
                  f"valor p {p:.3g}")
        d_neg = diferencias(-c, semillas)
        p_neg = fase4d.valor_p(d_neg, N_SPLITS)
        h_neg = fase4d.holm([{"pregunta": "desplazada al revés", "valor_p": p_neg, "media": float(d_neg.mean())}]
                            + otras)[0]
        registrar("positivo", f"{nombre}: el mismo desplazamiento con el signo contrario da resultado a favor",
                  not h_neg["a_favor"], f"diferencia media {d_neg.mean():.4f}; valor p {p_neg:.3g}; aceptada por "
                  f"Holm {h_neg['aceptada_por_holm']}, a favor {h_neg['a_favor']}", debe_fallar=True)
        informe[nombre] = {"desplazamiento_en_el_logit": round(c, 6), "pliegues": int(len(d)),
                           "diferencia_media": round(float(d.mean()), 4), "valor_p": p,
                           "signo_contrario": {"diferencia_media": round(float(d_neg.mean()), 4), "valor_p": p_neg,
                                               "a_favor": h_neg["a_favor"]}}
    return informe


# ---- holm y coherencia -----------------------------------------------------------------------

def control_holm():
    def decide(ps, medias=None):
        medias = medias or [0.01] * len(ps)
        return fase4d.holm([{"pregunta": f"q{i + 1}", "valor_p": p, "media": m} for i, (p, m) in
                            enumerate(zip(ps, medias))])
    a = decide([0.04, 0.001, 0.02])
    registrar("holm", "a. 0,001, 0,02 y 0,04: las tres", [q["a_favor"] for q in a] == [True, True, True],
              f"umbrales {[round(q['umbral_holm'], 4) for q in a]}")
    b = decide([0.001, 0.03, 0.04])
    registrar("holm", "b. 0,001, 0,03 y 0,04: solo la primera", [q["a_favor"] for q in b] == [True, False, False],
              f"{[q['aceptada_por_holm'] for q in b]}")
    sin_parar = [q["valor_p"] <= q["umbral_holm"] for q in b]
    registrar("holm", "b sin detenerse en la primera que no pasa", sin_parar != [q["a_favor"] for q in b],
              f"aceptaría {sin_parar}", debe_fallar=True)
    c = decide([0.001, 0.5, 0.5], medias=[-0.01, 0.01, 0.01])
    registrar("holm", "c. una diferencia negativa con valor p 0,001: aceptada, pero no a favor",
              c[0]["aceptada_por_holm"] and not c[0]["a_favor"], f"{c[0]}")
    d = decide([0.01, 0.02, 0.2])
    bonferroni = [p <= fase4d.ALFA / 3 for p in (0.01, 0.02, 0.2)]
    registrar("holm", "d. 0,01, 0,02 y 0,2: Holm acepta dos, Bonferroni una",
              [q["a_favor"] for q in d] == [True, True, False] and bonferroni == [True, False, False],
              f"Holm {[q['a_favor'] for q in d]}; Bonferroni {bonferroni}")


def control_coherencia():
    with open(C4, encoding="utf-8") as f:
        m = json.load(f)["metricas"]
    c4, m3 = m["C4"]["pauc"]["por_semilla_y_fold"], m["M3limpio"]["pauc"]["por_semilla_y_fold"]
    diffs = [b - a for s in sorted(c4, key=int) for a, b in zip(m3[s], c4[s])]
    p = fase4d.valor_p(diffs, N_SPLITS)
    extremo = min(abs(v) for v in f4b.nadeau_bengio(diffs, N_SPLITS, 1 - p))
    registrar("coherencia", "a la confianza 1 − p, un extremo del intervalo corregido es 0", extremo <= 1e-4,
              f"extremo más cercano a 0: {extremo:.4g}, con los 4 decimales del intervalo")
    p_ing = fase4d.valor_p_ingenuo(diffs)
    extremo_ing = min(abs(v) for v in f4b.nadeau_bengio(diffs, N_SPLITS, 1 - p_ing))
    registrar("coherencia", "con el valor p sin corregir", extremo_ing > 1e-4, f"extremo más cercano a 0: "
              f"{extremo_ing:.4g}", debe_fallar=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--out", required=True, help="ruta sin extensión")
    args = ap.parse_args()
    if not args.rapido:
        destino = os.path.realpath(args.out)
        if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "outputs")) + os.sep):
            raise SystemExit("ERROR: la corrida completa de los controles de la comparación va en outputs/.")
    juegos = 200 if args.rapido else 1000
    t0 = time.perf_counter()
    informe = {"equivalencia": control_equivalencia(), "negativo": control_negativo(juegos)}
    control_holm()
    control_coherencia()
    informe["positivo"] = control_positivo()
    informe["descartado_del_borrador"] = descartado_del_borrador(juegos)
    malos = [r for r in resultados if not r["ok"]]
    salida = {"rapido": args.rapido, "que_es": ("Controles de la comparación de la Fase 4d (PLAN.md): la unidad de "
                                                "lectura, el control negativo, el positivo, Holm y la coherencia del "
                                                "valor p con los intervalos. No responde ninguna pregunta."),
              "casos": resultados, "fallos": len(malos), **informe,
              "segundos": round(time.perf_counter() - t0, 1),
              "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv}}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    n, pos, eq = informe["negativo"], informe["positivo"], informe["equivalencia"]
    lineas = [
        "# Fase 4d: controles de la comparación", "",
        f"{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba, incluidos los que debían fallar.",
        "",
        f"- Equivalencia: {eq.get('casos')} casos; pAUC frente a 0,2 × especificidad media, máxima diferencia "
        f"{eq.get('maxima_diferencia_oficial_vs_0_2_por_especificidad_media', float('nan')):.3g}.",
        f"- Negativo ({juegos} juegos, correlación {RHO}, límite {n['limite_de_rechazos']}): corregida "
        f"{n['50_diferencias']['rechazos_corregida']} y {n['25_diferencias']['rechazos_corregida']}; sin corregir "
        f"{n['50_diferencias']['rechazos_sin_corregir']} y {n['25_diferencias']['rechazos_sin_corregir']} "
        "(50 y 25 diferencias).",
        f"- Positivo: diferencia media {pos['10 semillas']['diferencia_media']} con valor p "
        f"{pos['10 semillas']['valor_p']:.3g} (10 semillas); {pos['semillas 0 a 4']['diferencia_media']} con "
        f"{pos['semillas 0 a 4']['valor_p']:.3g} (semillas 0 a 4).",
        f"- Descartado del borrador, descriptivo: {informe['descartado_del_borrador']['rechazos_corregida']} y "
        f"{informe['descartado_del_borrador']['rechazos_sin_corregir']} rechazos de {juegos}.",
        "", "No responde ninguna pregunta.",
    ]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; "
          f"{salida['segundos']} s. Escrito: {args.out}.json y .md")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
test_fase4e_comparacion.py — los controles de la comparación de la Fase 4e
(PLAN.md, Fase 4e, «Controles»): los de la Fase 4d, rehechos para juegos de 25 y
de 15 diferencias y para Holm con dos preguntas. No entrena ningún modelo ni
responde ninguna pregunta.

  equivalencia  El de la Fase 4d, tal cual (test_fase4d_comparacion).
  negativo      1.000 juegos sintéticos de 25 y de 15 diferencias, las de 5 y de 3
                semillas de confirmación, con media 0 y correlación 0,2: la prueba
                corregida rechaza al 5 % a lo sumo el 5 % de las veces, con el
                error de Monte Carlo (el cuantil 0,95 de una binomial de 1.000 y
                0,05).
  positivo      Sobre las predicciones guardadas de M3 limpio en las semillas de
                confirmación, 5 a 9 y 5 a 7, las puntuaciones de los positivos se
                suben en el logit hasta una diferencia media de pAUC de +0,02
                (±0,002): el valor p queda por debajo de 0,05/2 y Holm, con dos
                preguntas, da el resultado a favor. Son M3 limpio contra sí mismo
                desplazado: no mira ninguna red de la 4e.
  holm          Con dos preguntas y valores p sintéticos.
  coherencia    El de la Fase 4d, tal cual.

Casos que deben fallar: los de la 4d en equivalencia y coherencia; la t sin
corregir rechaza más del límite; el desplazamiento con el signo contrario no da
resultado a favor; un Holm que no se detuviera aceptaría la segunda pregunta del
caso b.

Con --rapido, 200 juegos en vez de 1.000. Sin --rapido, --out va en outputs/.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_comparacion.py --rapido --out RUTA
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4e_comparacion.py \\
        --out outputs/fase4e-controles-comparacion
Escribe RUTA.json y RUTA.md. Devuelve 0 si todo se comporta como se espera.
"""

import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
from scipy import stats
from scipy.special import expit, logit

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b_comparar as f4b  # noqa: E402
import fase4d  # noqa: E402
import test_fase4d_comparacion as t4d  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from train_and_evaluate import construir_folds, pauc_above_tpr  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = t4d.RAIZ
G, Y = t4d.G, t4d.Y
N_SPLITS = t4d.N_SPLITS
N_PREGUNTAS = 2
CONFIRMACION = {"semillas 5 a 9": [5, 6, 7, 8, 9], "semillas 5 a 7": [5, 6, 7]}

# Los casos se registran en la lista de test_fase4d_comparacion, para reusar sus
# controles de equivalencia y de coherencia tal cual.
resultados = t4d.resultados
registrar = t4d.registrar


def control_negativo(juegos):
    limite = int(stats.binom.ppf(0.95, juegos, fase4d.ALFA))
    rng = np.random.default_rng(2026)
    informe = {"juegos": juegos, "correlacion": t4d.RHO, "limite_de_rechazos": limite,
               "probabilidad_de_pasar_el_limite_con_tasa_real_del_5": float(stats.binom.sf(limite, juegos, fase4d.ALFA))}
    for n in (25, 15):
        z = t4d.correlacionadas(rng, juegos, n, t4d.RHO)
        corregida = int(sum(fase4d.valor_p(x, N_SPLITS) < fase4d.ALFA for x in z))
        ingenua = int(sum(fase4d.valor_p_ingenuo(x) < fase4d.ALFA for x in z))
        informe[f"{n}_diferencias"] = {"rechazos_corregida": corregida, "rechazos_sin_corregir": ingenua}
        registrar("negativo", f"{n} diferencias: la prueba corregida rechaza a lo sumo el 5 %", corregida <= limite,
                  f"{corregida} de {juegos}; límite {limite}")
        registrar("negativo", f"{n} diferencias: la t sin corregir", ingenua > limite, f"{ingenua} de {juegos}",
                  debe_fallar=True)
    return informe


def control_positivo():
    predicciones, procedencia = f4b.cargar_predicciones(f4b.PREDICCIONES)
    df, _ = cargar_desarrollo(t4d.CSV, G, RUTA_HOLDOUT)
    y, isic = df[Y].to_numpy(), df["isic_id"].to_numpy()
    with open(t4d.REF_PLIEGUES, encoding="utf-8") as f:
        huellas = json.load(f)["folds"]["sha256_por_semilla"]
    with open(t4d.REF_M3L, encoding="utf-8") as f:
        ref = json.load(f)["metricas"]["M3limpio"]["pauc"]["por_semilla_y_fold"]
    pliegues = []
    for s in sorted(set().union(*CONFIRMACION.values())):
        folds = construir_folds(df, G, Y, N_SPLITS, s)
        if f4.huella_folds(folds, len(df)) != huellas[str(s)]:
            raise SystemExit(f"ERROR: los pliegues de la semilla {s} no son los de {t4d.REF_PLIEGUES}.")
        for i, (_, va) in enumerate(folds):
            base = f4b.guardada(predicciones, "M3limpio", s, i, isic[va])
            pauc = float(pauc_above_tpr(y[va], base))
            if round(pauc, 4) != ref[str(s)][i]:
                raise SystemExit(f"ERROR: M3 limpio no reproduce {t4d.REF_M3L} en la semilla {s}, pliegue {i}.")
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
               "reproduce": os.path.relpath(t4d.REF_M3L, RAIZ), "objetivo": t4d.OBJETIVO, "margen": t4d.MARGEN}
    otra = [{"pregunta": "relleno", "valor_p": 1.0, "media": 0.0}]
    for nombre, semillas in CONFIRMACION.items():
        lo, hi = 0.0, 8.0
        for _ in range(40):
            c = (lo + hi) / 2
            media = diferencias(c, semillas).mean()
            if abs(media - t4d.OBJETIVO) <= t4d.MARGEN / 4:
                break
            lo, hi = (c, hi) if media < t4d.OBJETIVO else (lo, c)
        d = diferencias(c, semillas)
        p = fase4d.valor_p(d, N_SPLITS)
        h = fase4d.holm([{"pregunta": "desplazada", "valor_p": p, "media": float(d.mean())}] + otra)[0]
        registrar("positivo", f"{nombre}: +{t4d.OBJETIVO} en la pAUC, valor p por debajo de 0,05/2 y a favor",
                  abs(d.mean() - t4d.OBJETIVO) <= t4d.MARGEN and p < fase4d.ALFA / N_PREGUNTAS and h["a_favor"],
                  f"desplazamiento {c:.4f} en el logit; diferencia media {d.mean():.4f} en {len(d)} pliegues; "
                  f"valor p {p:.3g}")
        d_neg = diferencias(-c, semillas)
        p_neg = fase4d.valor_p(d_neg, N_SPLITS)
        h_neg = fase4d.holm([{"pregunta": "desplazada al revés", "valor_p": p_neg, "media": float(d_neg.mean())}]
                            + otra)[0]
        registrar("positivo", f"{nombre}: el mismo desplazamiento con el signo contrario da resultado a favor",
                  not h_neg["a_favor"], f"diferencia media {d_neg.mean():.4f}; valor p {p_neg:.3g}; aceptada por "
                  f"Holm {h_neg['aceptada_por_holm']}, a favor {h_neg['a_favor']}", debe_fallar=True)
        informe[nombre] = {"desplazamiento_en_el_logit": round(c, 6), "pliegues": int(len(d)),
                           "diferencia_media": round(float(d.mean()), 4), "valor_p": p,
                           "signo_contrario": {"diferencia_media": round(float(d_neg.mean()), 4), "valor_p": p_neg,
                                               "a_favor": h_neg["a_favor"]}}
    return informe


def control_holm():
    def decide(ps, medias=None):
        medias = medias or [0.01] * len(ps)
        return fase4d.holm([{"pregunta": f"q{i + 1}", "valor_p": p, "media": m} for i, (p, m) in
                            enumerate(zip(ps, medias))])
    a = decide([0.04, 0.001])
    registrar("holm", "a. 0,001 y 0,04: las dos", [q["a_favor"] for q in a] == [True, True],
              f"umbrales {[round(q['umbral_holm'], 4) for q in a]}")
    b = decide([0.03, 0.04])
    registrar("holm", "b. 0,03 y 0,04: ninguna, la primera no pasa 0,025", [q["a_favor"] for q in b] == [False, False],
              f"{[q['aceptada_por_holm'] for q in b]}")
    sin_parar = [q["valor_p"] <= q["umbral_holm"] for q in b]
    registrar("holm", "b sin detenerse en la primera que no pasa", sin_parar != [q["a_favor"] for q in b],
              f"aceptaría {sin_parar}", debe_fallar=True)
    c = decide([0.001, 0.5], medias=[-0.01, 0.01])
    registrar("holm", "c. una diferencia negativa con valor p 0,001: aceptada, pero no a favor",
              c[0]["aceptada_por_holm"] and not c[0]["a_favor"], f"{c[0]}")
    d = decide([0.02, 0.04])
    bonferroni = [p <= fase4d.ALFA / 2 for p in (0.02, 0.04)]
    registrar("holm", "d. 0,02 y 0,04: Holm acepta las dos, Bonferroni una",
              [q["a_favor"] for q in d] == [True, True] and bonferroni == [True, False],
              f"Holm {[q['a_favor'] for q in d]}; Bonferroni {bonferroni}")


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
    informe = {"equivalencia": t4d.control_equivalencia(), "negativo": control_negativo(juegos)}
    control_holm()
    t4d.control_coherencia()
    informe["positivo"] = control_positivo()
    malos = [r for r in resultados if not r["ok"]]
    salida = {"rapido": args.rapido, "que_es": ("Controles de la comparación de la Fase 4e (PLAN.md): la unidad de "
                                                "lectura, el control negativo con 25 y 15 diferencias, el positivo en "
                                                "las semillas de confirmación, Holm con dos preguntas y la coherencia "
                                                "del valor p con los intervalos. No responde ninguna pregunta."),
              "casos": resultados, "fallos": len(malos), **informe,
              "segundos": round(time.perf_counter() - t0, 1),
              "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv}}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    n, pos, eq = informe["negativo"], informe["positivo"], informe["equivalencia"]
    lineas = [
        "# Fase 4e: controles de la comparación", "",
        f"{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba, incluidos los que debían fallar.",
        "",
        f"- Equivalencia: {eq.get('casos')} casos; pAUC frente a 0,2 × especificidad media, máxima diferencia "
        f"{eq.get('maxima_diferencia_oficial_vs_0_2_por_especificidad_media', float('nan')):.3g}.",
        f"- Negativo ({juegos} juegos, correlación {t4d.RHO}, límite {n['limite_de_rechazos']}): corregida "
        f"{n['25_diferencias']['rechazos_corregida']} y {n['15_diferencias']['rechazos_corregida']}; sin corregir "
        f"{n['25_diferencias']['rechazos_sin_corregir']} y {n['15_diferencias']['rechazos_sin_corregir']} "
        "(25 y 15 diferencias).",
        f"- Positivo: diferencia media {pos['semillas 5 a 9']['diferencia_media']} con valor p "
        f"{pos['semillas 5 a 9']['valor_p']:.3g} (semillas 5 a 9); {pos['semillas 5 a 7']['diferencia_media']} con "
        f"{pos['semillas 5 a 7']['valor_p']:.3g} (semillas 5 a 7).",
        "", "No responde ninguna pregunta.",
    ]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; "
          f"{salida['segundos']} s. Escrito: {args.out}.json y .md")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

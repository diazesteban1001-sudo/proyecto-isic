#!/usr/bin/env python3
"""
potencia_nadeau_bengio.py — la potencia de la prueba de las fases 4d a 4f frente a
M3 limpio (PLAN.md, Fase 6, «La potencia de la prueba: especificación», decisión de
la persona del 2026-11-04). Descriptivo: no compara ningún modelo ni cambia ninguna
recomendación. Solo lee cuatro archivos de outputs/: ni data/ ni el reservado.

  - Curva analítica. Con la desviación s de las diferencias pliegue a pliegue de la
    pAUC de C4, C5, C6 y C7 − M3 limpio, cada una por separado, y n = 25 y 50, la
    probabilidad de «a favor» (fase4d.valor_p < 0,05 y media > 0) es la de que una t
    no central de n − 1 grados de libertad y no centralidad δ / (s·√(1/n + 1/4))
    pase t(0,975; n − 1). δ de 0,002 a 0,02 en pasos de 0,001, y el δ con el 50 % y
    con el 80 % de potencia, buscado sobre la curva continua.
  - Controles previos, sobre las diferencias guardadas: la prueba es la nuestra
    (media, desviación, intervalo y valor p guardados); los bloques son semillas (la
    lista coincide con candidato − M3 limpio desde metricas.*.pauc.por_semilla_y_fold);
    el valor p vectorizado de la simulación es fase4d.valor_p.
  - Control por simulación. El generador del control negativo de la 4d
    (test_fase4d_comparacion.correlacionadas, ρ = 0,2), multiplicado por s/√(1 − ρ),
    para que la desviación esperada dentro de un juego sea s, más δ. 20.000 juegos
    por comparación y n, los mismos para todos los δ, semilla 2026. (a) Las tasas a
    favor y bilateral coinciden con las analíticas dentro de 4 errores de Monte
    Carlo; (b) con δ = 0, a favor a lo sumo 0,05 y bilateral a lo sumo 0,05 más 4
    errores de Monte Carlo; (c) con δ = 0,05, a favor al menos 0,99.
  - Una línea entre semillas: el error estándar de la media entre semillas frente al
    de la prueba, con el n de cada comparación.

Casos que deben fallar: la t sin corregir en la reproducción y en (b), la lista
desplazada una semilla, el valor p vectorizado sin corregir, el generador con ρ = 0
en (a) y δ = −0,05 en (c). Si un control falla, se detiene sin escribir nada. No
interpreta.

Salida: <out>.json, el resumen (los δ al 50 % y al 80 %, los errores estándar y los
controles); <out>-curva.json, la curva completa, analítica y simulada, que está en
FUERA_DEL_CORPUS de verificar_trazabilidad.py porque sus tasas respaldaban por
coincidencia cifras del borrador (decisión de la persona del 2026-11-04); y <out>.md.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/potencia_nadeau_bengio.py \\
        --out outputs/potencia-nadeau-bengio
"""

import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
from scipy import optimize, stats

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4d  # noqa: E402
import ganador_m3  # noqa: E402
from evaluar_repetido import _nadeau_bengio  # noqa: E402

_filtros = list(warnings.filters)
import test_fase4d_comparacion as t4d  # noqa: E402  (el generador del control negativo de la 4d)
warnings.filters[:] = _filtros  # ese módulo silencia todos los avisos al importarse

RAIZ = ganador_m3.RAIZ
COMPARACIONES = {
    "C4": "outputs/fase4c-c4-vs-m3limpio.json",
    "C5": "outputs/fase4d-c5-vs-m3limpio.json",
    "C6": "outputs/fase4d-c6-vs-m3limpio.json",
    "C7": "outputs/fase4e-c7-vs-m3limpio.json",
}
CAMPO = "comparaciones_nuevo_menos_base.pauc.diferencias_nuevo_menos_base"
BASE = "M3limpio"
N_SPLITS = 5
RHO = t4d.RHO  # 0,2: n_prueba/(n_entrenamiento + n_prueba) con 5 pliegues
RAZON = 1.0 / (N_SPLITS - 1)  # el 1/4 de fase4d.valor_p, que es ρ/(1 − ρ)
NS = (25, 50)
DELTAS = [round(0.002 + 0.001 * i, 3) for i in range(19)]
DELTA_GRANDE = 0.05
JUEGOS = 20000
SEMILLA = 2026  # la del control negativo de la 4d
Z_MC = 4
JUEGOS_COMPROBADOS = 2000
DELTA_COMPROBACION = 0.01
TOL_P_GUARDADO = 0.002  # las diferencias están guardadas con 4 decimales
TOL_BLOQUES = 0.00015  # dos valores redondeados a 4 decimales
TOL_VECTORIZADO = 1e-12
OBJETIVOS = {"delta_50": 0.5, "delta_80": 0.8}

casos = []


def registrar(control, caso, ok, detalle, debe_fallar=False):
    casos.append({"control": control, "caso": caso, "ok": bool(ok), "debe_fallar": debe_fallar,
                  "detalle": detalle})
    print(f"[{'OK' if ok else 'FALLA'}] {control} · {caso}{' (debe fallar)' if debe_fallar else ''}: {detalle}",
          flush=True)


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        d = json.load(f)
    nuevo = [k for k in d["metricas"] if k != BASE]
    if len(nuevo) != 1 or d["n_splits"] != N_SPLITS:
        raise SystemExit(f"ERROR: {ruta} no es una comparación de un modelo contra {BASE} con {N_SPLITS} pliegues.")
    guardado = d["comparaciones_nuevo_menos_base"]["pauc"]
    x = np.asarray(guardado["diferencias_nuevo_menos_base"], dtype=np.float64)
    if len(x) != N_SPLITS * len(d["semillas_corridas"]):
        raise SystemExit(f"ERROR: {ruta} no trae {N_SPLITS} diferencias por semilla.")
    return {"archivo": ruta, "semillas": d["semillas_corridas"], "nuevo": nuevo[0], "metricas": d["metricas"],
            "guardado": guardado, "x": x}


# ---- la prueba ---------------------------------------------------------------------------------

def ee_prueba(s, n):
    return s * np.sqrt(1.0 / n + RAZON)


def tasas_analiticas(delta, s, n):
    """Tasa a favor y rechazo bilateral de fase4d.valor_p al 5 %, con n diferencias
    normales de correlación ρ, desviación esperada s dentro del juego y media δ: el
    estadístico es una t no central de n − 1 grados de libertad."""
    tc = stats.t.ppf(1 - fase4d.ALFA / 2, df=n - 1)
    nc = delta / ee_prueba(s, n)
    a_favor = float(stats.nct.sf(tc, n - 1, nc))
    en_contra = cola_inferior(tc, n - 1, nc)
    if not (np.isfinite(a_favor) and np.isfinite(en_contra)):
        raise SystemExit(f"ERROR: la t no central no da un valor finito con δ = {delta}, s = {s}, n = {n}.")
    return a_favor, a_favor + en_contra


def cola_inferior(tc, gl, nc):
    """P(T < −tc) para una t no central, por simetría: −T(gl, nc) es T(gl, −nc).
    stats.nct.cdf(−tc, gl, nc) da nan con no centralidad grande (scipy 1.17.1: con
    nc = 10,95 y 24 grados de libertad)."""
    return float(stats.nct.sf(tc, gl, -nc))


def control_cola_inferior(datos):
    """La cola inferior por simetría coincide con stats.nct.cdf donde este da un valor
    finito, en todas las comparaciones, n y δ de la simulación."""
    d_sim, d_signo, sin_valor, total = 0.0, 0.0, 0, 0
    for c in datos.values():
        s = float(np.std(c["x"], ddof=1))
        for n in NS:
            tc = stats.t.ppf(1 - fase4d.ALFA / 2, df=n - 1)
            for delta in [0.0] + DELTAS + [DELTA_GRANDE]:
                nc = delta / ee_prueba(s, n)
                ref = float(stats.nct.cdf(-tc, n - 1, nc))
                total += 1
                if not np.isfinite(ref):
                    sin_valor += 1
                    continue
                d_sim = max(d_sim, abs(cola_inferior(tc, n - 1, nc) - ref))
                d_signo = max(d_signo, abs(float(stats.nct.sf(tc, n - 1, nc)) - ref))
    registrar("cola inferior por simetría", "frente a stats.nct.cdf", d_sim <= 1e-10,
              f"máxima diferencia {d_sim:.2g} en {total - sin_valor} de {total}; stats.nct.cdf da nan en {sin_valor}")
    registrar("cola inferior por simetría", "sin cambiar el signo de la no centralidad", d_signo > 1e-10,
              f"máxima diferencia {d_signo:.2g}", debe_fallar=True)


def delta_con_potencia(objetivo, s, n):
    return float(optimize.brentq(lambda d: tasas_analiticas(d, s, n)[0] - objetivo, 0.0, 1.0, xtol=1e-12))


def valores_p(x, corregida=True):
    """fase4d.valor_p fila a fila (o, con corregida=False, la t sin corregir), y la media."""
    n = x.shape[1]
    media = x.mean(axis=1)
    factor = (1.0 / n + RAZON) if corregida else 1.0 / n
    ee = np.sqrt(x.var(axis=1, ddof=1) * factor)
    return 2 * stats.t.sf(np.abs(media / ee), df=n - 1), media


def tasas_simuladas(z, s, delta, rho, corregida=True):
    x = delta + z * (s / np.sqrt(1 - rho))
    p, media = valores_p(x, corregida)
    rechaza = p < fase4d.ALFA
    return float(np.mean(rechaza & (media > 0))), float(np.mean(rechaza))


def tolerancia(p):
    return float(Z_MC * np.sqrt(max(p * (1 - p), 1.0 / JUEGOS) / JUEGOS))


def coincide(sim, ana):
    return all(abs(a - b) <= tolerancia(b) for a, b in zip(sim, ana))


def control_b(a_favor, bilateral):
    return a_favor <= fase4d.ALFA and bilateral <= fase4d.ALFA + tolerancia(fase4d.ALFA)


# ---- controles previos -------------------------------------------------------------------------

def intervalo_ingenuo(x):
    n = len(x)
    t = float(stats.t.ppf(0.975, df=n - 1))
    ee = float(np.std(x, ddof=1)) / np.sqrt(n)
    media = float(np.mean(x))
    return [round(float(media - t * ee), 4), round(float(media + t * ee), 4)]


def controles_previos(c, nombre):
    x, g = c["x"], c["guardado"]
    ok = (round(float(np.mean(x)), 4) == g["media"] and round(float(np.std(x, ddof=1)), 4) == g["desviacion"]
          and _nadeau_bengio(list(x), N_SPLITS) == g["intervalo_t_95_nadeau_bengio"])
    detalle = f"media {g['media']}, desviación {g['desviacion']}, intervalo {g['intervalo_t_95_nadeau_bengio']}"
    if "valor_p_nadeau_bengio" in g:
        dp = abs(fase4d.valor_p(x, N_SPLITS) - g["valor_p_nadeau_bengio"])
        ok = ok and dp <= TOL_P_GUARDADO
        detalle += f"; valor p a {dp:.2g} del guardado"
    else:
        detalle += "; no guarda valor p"
    registrar("la prueba es la nuestra", nombre, ok, detalle)
    ingenuo = intervalo_ingenuo(x)
    falla = ingenuo != g["intervalo_t_95_nadeau_bengio"]
    detalle = f"intervalo sin corregir {ingenuo}"
    if "valor_p_nadeau_bengio" in g:
        dp = abs(fase4d.valor_p_ingenuo(x) - g["valor_p_nadeau_bengio"])
        falla = falla and dp > TOL_P_GUARDADO
        detalle += f"; valor p sin corregir a {dp:.2g} del guardado"
    registrar("la prueba es la nuestra", f"{nombre}, con la t sin corregir", falla, detalle, debe_fallar=True)

    m = c["metricas"]
    rehecha = np.concatenate([np.asarray(m[c["nuevo"]]["pauc"]["por_semilla_y_fold"][str(s)])
                              - np.asarray(m[BASE]["pauc"]["por_semilla_y_fold"][str(s)]) for s in c["semillas"]])
    d = float(np.abs(rehecha - x).max())
    registrar("los bloques son semillas", nombre, d <= TOL_BLOQUES, f"máxima diferencia {d:.2g}")
    d = float(np.abs(np.roll(rehecha, N_SPLITS) - x).max())
    registrar("los bloques son semillas", f"{nombre}, desplazada una semilla", d > TOL_BLOQUES,
              f"máxima diferencia {d:.2g}", debe_fallar=True)


def entre_semillas(c, s):
    medias = c["x"].reshape(len(c["semillas"]), N_SPLITS).mean(axis=1)
    sd = float(np.std(medias, ddof=1))
    ee_sem = sd / np.sqrt(len(medias))
    ee = float(ee_prueba(s, len(c["x"])))
    return {"semillas": len(medias), "n": len(c["x"]), "desviacion_medias_por_semilla": round(sd, 6),
            "ee_entre_semillas": round(ee_sem, 6), "ee_de_la_prueba": round(ee, 6),
            "ee_prueba_sobre_ee_semillas": round(ee / ee_sem, 2)}


# ---- simulación --------------------------------------------------------------------------------

def simular(nombre, s, n, rng):
    z = t4d.correlacionadas(rng, JUEGOS, n, RHO)
    z0 = t4d.correlacionadas(rng, JUEGOS, n, 0.0)
    celda = f"{nombre}, n = {n}"

    x = DELTA_COMPROBACION + z[:JUEGOS_COMPROBADOS] * (s / np.sqrt(1 - RHO))
    uno_a_uno = np.array([fase4d.valor_p(fila, N_SPLITS) for fila in x])
    d = float(np.abs(valores_p(x)[0] - uno_a_uno).max())
    registrar("valor p vectorizado", celda, d <= TOL_VECTORIZADO, f"máxima diferencia {d:.2g}")
    d = float(np.abs(valores_p(x, corregida=False)[0] - uno_a_uno).max())
    registrar("valor p vectorizado", f"{celda}, sin corregir", d > TOL_VECTORIZADO, f"máxima diferencia {d:.2g}",
              debe_fallar=True)

    filas, fuera, fuera_rho0 = [], 0, 0
    for delta in [0.0] + DELTAS + [DELTA_GRANDE]:
        sim, ana = tasas_simuladas(z, s, delta, RHO), tasas_analiticas(delta, s, n)
        fuera += not coincide(sim, ana)
        fuera_rho0 += not coincide(tasas_simuladas(z0, s, delta, 0.0), ana)
        filas.append({"delta": delta, "a_favor": round(sim[0], 4), "rechazo_bilateral": round(sim[1], 4),
                      "a_favor_analitica": round(ana[0], 4), "rechazo_bilateral_analitico": round(ana[1], 4),
                      "tolerancia_a_favor": round(tolerancia(ana[0]), 4),
                      "tolerancia_bilateral": round(tolerancia(ana[1]), 4)})
    registrar("(a) coincide con la analítica", celda, fuera == 0, f"{fuera} de {len(filas)} δ fuera de tolerancia")
    registrar("(a) coincide con la analítica", f"{celda}, generador con ρ = 0", fuera_rho0 > 0,
              f"{fuera_rho0} de {len(filas)} δ fuera de tolerancia", debe_fallar=True)

    a, b = tasas_simuladas(z, s, 0.0, RHO)
    registrar("(b) δ = 0, a lo sumo el 5 %", celda, control_b(a, b),
              f"a favor {a:.4f}, bilateral {b:.4f}; límite bilateral {fase4d.ALFA + tolerancia(fase4d.ALFA):.4f}")
    a, b = tasas_simuladas(z, s, 0.0, RHO, corregida=False)
    registrar("(b) δ = 0, a lo sumo el 5 %", f"{celda}, t sin corregir", not control_b(a, b),
              f"a favor {a:.4f}, bilateral {b:.4f}", debe_fallar=True)

    a = tasas_simuladas(z, s, DELTA_GRANDE, RHO)[0]
    registrar("(c) δ = 0,05, al menos el 99 %", celda, a >= 0.99, f"a favor {a:.4f}")
    a = tasas_simuladas(z, s, -DELTA_GRANDE, RHO)[0]
    registrar("(c) δ = 0,05, al menos el 99 %", f"{celda}, δ = −0,05", a < 0.99, f"a favor {a:.4f}",
              debe_fallar=True)
    return filas


# ---- salida ------------------------------------------------------------------------------------

def escribir(out, resultado, curva):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    with open(out + "-curva.json", "w", encoding="utf-8") as f:
        json.dump(curva, f, ensure_ascii=False, indent=2)
    comp, sim = resultado["comparaciones"], resultado["simulacion"]
    lineas = ["# Potencia de la prueba de Nadeau y Bengio frente a M3 limpio (descriptivo)", "",
              "Diferencias pliegue a pliegue de la pAUC de C4 a C7 − M3 limpio, cada una por separado. «A favor»: "
              "valor p bilateral < 0.05 y media > 0. Potencia con la t no central, bajo el modelo de varianza de la "
              "prueba (ρ = 1/5), con la s de cada comparación.", "",
              "| Comparación | s | δ al 50 %, n = 25 | δ al 80 %, n = 25 | δ al 50 %, n = 50 | δ al 80 %, n = 50 |",
              "|---|---|---|---|---|---|"]
    for nombre, c in comp.items():
        sem = c["semillas"]
        lineas.append(f"| {nombre} (semillas {sem[0]} a {sem[-1]}) | {c['s']:.4f} | {c['delta_50']['25']:.4f} | "
                      f"{c['delta_80']['25']:.4f} | {c['delta_50']['50']:.4f} | {c['delta_80']['50']:.4f} |")
    lineas += ["", "Entre semillas, error estándar de la media frente al de la prueba: " + "; ".join(
        f"{nombre} {c['entre_semillas']['ee_entre_semillas']:.4f} frente a {c['entre_semillas']['ee_de_la_prueba']:.4f}"
        for nombre, c in comp.items()) + ".", "",
        f"Controles: {sum(k['ok'] for k in resultado['controles'])} de {len(resultado['controles'])} casos como se "
        f"esperaba ({sum(k['debe_fallar'] for k in resultado['controles'])} deben fallar y fallan). Simulación con el "
        f"generador de la 4d: {sim['juegos']} juegos por comparación y n, semilla {sim['semilla']}. La curva completa "
        f"está en {resultado['curva']}, fuera del corpus del verificador. No interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json, {out}-curva.json y {out}.md", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="ruta sin extensión de la salida")
    args = ap.parse_args()
    inicio = time.perf_counter()
    if abs(RAZON - RHO / (1 - RHO)) > 1e-12:
        raise SystemExit("ERROR: el término de fase4d.valor_p no es ρ/(1 − ρ) con el ρ del generador.")

    datos = {nombre: leer(ruta) for nombre, ruta in COMPARACIONES.items()}
    for nombre, c in datos.items():
        controles_previos(c, nombre)
    control_cola_inferior(datos)

    rng = np.random.default_rng(SEMILLA)
    comparaciones, curvas, simulacion = {}, {}, {}
    for nombre, c in datos.items():
        s = float(np.std(c["x"], ddof=1))
        curvas[nombre] = {str(n): [dict(zip(("delta", "a_favor", "rechazo_bilateral"),
                                            (d, *(round(v, 4) for v in tasas_analiticas(d, s, n)))))
                                   for d in DELTAS] for n in NS}
        comparaciones[nombre] = {
            "archivo": c["archivo"], "campo": CAMPO, "nuevo": c["nuevo"], "semillas": c["semillas"],
            "n_diferencias": len(c["x"]), "s": s, "media_observada": c["guardado"]["media"],
            **{k: {str(n): round(delta_con_potencia(p, s, n), 4) for n in NS} for k, p in OBJETIVOS.items()},
            "entre_semillas": entre_semillas(c, s),
        }
        simulacion[nombre] = {str(n): simular(nombre, s, n, rng) for n in NS}

    if not all(k["ok"] for k in casos):
        raise SystemExit("ERROR: algún control no da lo esperado; no se escribe nada.")

    ruta_curva = os.path.relpath(os.path.abspath(args.out + "-curva.json"), RAIZ)
    curva = {
        "que_es": ("La curva completa del análisis de potencia: las tasas analíticas y las simuladas en cada δ. El "
                   f"resumen, con los δ al 50 % y al 80 %, los errores estándar y los controles, está en "
                   f"{os.path.relpath(os.path.abspath(args.out + '.json'), RAIZ)}. Fuera del corpus del verificador "
                   "de trazabilidad (FUERA_DEL_CORPUS)."),
        "deltas": DELTAS,
        "curva_analitica": curvas,
        "simulacion": {"deltas": [0.0] + DELTAS + [DELTA_GRANDE], "por_comparacion": simulacion},
    }
    resultado = {
        "que_es": ("Potencia descriptiva de la prueba de las fases 4d a 4f frente a M3 limpio (PLAN.md, Fase 6, «La "
                   "potencia de la prueba»). No compara ningún modelo, no cambia ninguna recomendación y no suma a la "
                   "bitácora."),
        "prueba": {"funcion": "fase4d.valor_p", "alfa": fase4d.ALFA, "n_splits": N_SPLITS,
                   "error_estandar": "s·√(1/n + 1/(n_splits − 1))", "termino_de_correccion": RAZON, "rho": RHO,
                   "a_favor": "valor p bilateral < alfa y media > 0", "grados_de_libertad": "n − 1",
                   "potencia": "t no central de n − 1 grados de libertad, no centralidad δ / (s·√(1/n + 1/4))"},
        "rejilla_de_delta": "de 0,002 a 0,02 en pasos de 0,001; más 0 y 0,05 en la simulación",
        "curva": ruta_curva, "ns": list(NS), "objetivos": OBJETIVOS,
        "comparaciones": comparaciones,
        "simulacion": {"generador": "test_fase4d_comparacion.correlacionadas", "rho": RHO,
                       "escala": "s/√(1 − ρ)", "juegos": JUEGOS, "semilla": SEMILLA, "z_monte_carlo": Z_MC,
                       "tolerancia": "4·√(max(p(1 − p), 1/juegos)/juegos), con p la tasa analítica"},
        "controles": casos,
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "segundos": round(time.perf_counter() - inicio, 1),
        "nota": ("s se toma como la dispersión verdadera, sin propagar su incertidumbre; un modelo de verdad δ mejor "
                 "tendría las diferencias de C4 a C7 desplazadas en δ. El modelo de varianza, ρ = 1/5, es el que la "
                 "prueba ya supone. «entre_semillas» mide la variación con los mismos pacientes. Sin interpretación."),
    }
    escribir(args.out, resultado, curva)


if __name__ == "__main__":
    main()

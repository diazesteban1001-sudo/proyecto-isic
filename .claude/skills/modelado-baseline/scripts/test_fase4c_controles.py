#!/usr/bin/env python3
"""
test_fase4c_controles.py — los controles de la Fase 4c (PLAN.md, «Controles,
antes de leer cualquier resultado»), antes de entrenar las 50 redes. No entrena
ninguna red de la fase ni responde ninguna pregunta.

  ajustes          Las constantes de fase4c.py son las de la prueba de tiempo
                   (outputs/prueba-tiempo-red-imagen.json).
  barajadas        La red puede fallar: en la semilla 0, pliegue 0, se barajan
                   las etiquetas de todo el pliegue de entrenamiento, con la
                   semilla 0, antes de elegir positivos y negativos, y se entrena
                   la red. Pasa si su pAUC en validación cae dentro del 99 %
                   central de la pAUC de 1.000 puntuaciones aleatorias sobre ese
                   mismo pliegue de validación. El control solo vale si la red
                   con las etiquetas reales (la de reproducibilidad) queda
                   claramente por encima: su pAUC por encima de ese rango, con
                   más de un logit distinto y desviación mayor que cero
                   (decisión de la persona, 2026-10-22).
  reproducibilidad La misma red, semilla 0, pliegue 0, dos veces: se reporta si
                   los logits coinciden y, si no, la mayor diferencia.
  alineacion       fase4c.ensamblar: cada lesión recibe exactamente una
                   puntuación, la de su pliegue de validación, unida por isic_id.
  referencias      Las predicciones de M3 limpio de la Fase 4b pasan sus
                   comprobaciones y reproducen su pliegue; los pliegues tienen la
                   huella de outputs/fase4-m2-vs-m1.json, la que imagen_sola.py
                   comprobó para los suyos.
  c4               La alineación de C2 (fase4b_comparar.comprobar_alineacion)
                   con las variables de la red (fase4c.variables_red), antes y
                   después del remuestreo; la puntuación es una probabilidad, y
                   una puntuación 0 dentro de un paciente da razón 0.

Cada control tiene un caso que debe fallar, por el corolario de la regla 6 de
CLAUDE.md:
  ajustes: la prueba de tiempo con otro lote;
  barajadas: una puntuación sintética hecha de las etiquetas más un poco de
             ruido queda fuera del rango, y una puntuación constante no pasa
             por red con las etiquetas reales;
  reproducibilidad: un logit cambiado en 1e-6 se detecta como distinto;
  alineacion: una fila que falta, una repetida, una en la red de otro pliegue y
              un isic_id ajeno;
  referencias: el archivo de predicciones con un byte más, y los pliegues de la
               semilla 0 frente a la huella de la semilla 1;
  c4: las columnas corridas una fila; una puntuación negativa, una faltante y
      un paciente con todas sus puntuaciones en 0.

Con --rapido, las tres redes (barajadas y las dos de reproducibilidad) entrenan
una época y puntúan solo los positivos de la validación y 4.000 de sus
negativos; el rango de barajadas se calcula sobre ese mismo subconjunto. Sin
--rapido, las redes tienen los ajustes de la fase y puntúan toda la validación,
y --out tiene que ir en data/: fase4c_redes.py lo exige con 0 fallos.

Lee el conjunto de desarrollo con el cargador protegido; el reservado no entra.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4c_controles.py --rapido --out RUTA.json
    caffeinate -i .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase4c_controles.py \\
        --out data/fase4c-controles.json
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import argparse
import copy
import json
import os
import shutil
import sys
import tempfile
import time
import warnings

import h5py
import numpy as np
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402  (añade también la ruta de diseno-validacion)
import fase4b  # noqa: E402
import fase4b_comparar as f4b  # noqa: E402
import fase4c  # noqa: E402
import ganador_m3  # noqa: E402
from datos_desarrollo import RUTA_HOLDOUT, cargar_desarrollo  # noqa: E402
from evaluar_repetido import cargar_columnas_excluidas  # noqa: E402
from train_and_evaluate import construir_folds, pauc_above_tpr  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = ganador_m3.RAIZ
CSV = os.path.join(RAIZ, "data", "train-metadata.csv")
HDF5 = os.path.join(RAIZ, "data", "train-image.hdf5")
FUGAS = os.path.join(RAIZ, "outputs", "auditoria-de-fugas.json")
REF_PLIEGUES = os.path.join(RAIZ, "outputs", "fase4-m2-vs-m1.json")
REF_M3L = os.path.join(RAIZ, "outputs", "fase4-m3limpio-vs-m2.json")
IMAGEN_SOLA = os.path.join(RAIZ, "outputs", "imagen-sola.json")
G, Y = "patient_id", "target"
N_ALEATORIAS = 1000
NEGATIVOS_RAPIDO = 4000

resultados = []


def registrar(control, caso, ok, detalle, debe_fallar=False):
    """ok: el caso se comportó como se esperaba (si debe_fallar, que la comprobación falló)."""
    resultados.append({"control": control, "caso": caso, "ok": bool(ok), "debe_fallar": debe_fallar,
                       "detalle": detalle})
    print(f"[{'OK' if ok else 'FALLA'}] {control} · {caso}{' (debe fallar)' if debe_fallar else ''}: {detalle}",
          flush=True)


def se_detiene(f):
    try:
        f()
        return False, "no se detuvo"
    except SystemExit as e:
        return True, str(e)


# ---- ajustes ---------------------------------------------------------------------------------

def control_ajustes():
    with open(fase4c.PRUEBA_DE_TIEMPO, encoding="utf-8") as f:
        prueba = json.load(f)
    diferencias = fase4c.comprobar_ajustes(prueba)
    registrar("ajustes", "las constantes son las de la prueba de tiempo", not diferencias,
              f"lado {fase4c.LADO}, tasa {fase4c.TASA}, lote {fase4c.LOTE}, épocas {fase4c.EPOCAS}, "
              f"{fase4c.NEGATIVOS_POR_POSITIVO} negativos por positivo; diferencias: {diferencias}")
    otra = copy.deepcopy(prueba)
    otra["entrenamiento"]["lote"] = 32
    diferencias = fase4c.comprobar_ajustes(otra)
    registrar("ajustes", "la prueba de tiempo con lote 32", len(diferencias) == 1, f"{diferencias}",
              debe_fallar=True)


# ---- barajadas y reproducibilidad ------------------------------------------------------------

def banda_aleatoria(y_va, semilla=1):
    rng = np.random.default_rng(semilla)
    valores = [pauc_above_tpr(y_va, rng.uniform(size=len(y_va))) for _ in range(N_ALEATORIAS)]
    return [float(np.quantile(valores, 0.005)), float(np.quantile(valores, 0.995))], float(np.mean(valores))


def dispersion(logit):
    """Cuántos logits distintos da una red y su desviación: que no puntúe igual a
    todas las lesiones. No es una métrica de desempeño."""
    logit = np.asarray(logit, dtype=np.float64)
    return {"logits_distintos": int(np.unique(logit).size), "desviacion_del_logit": float(np.std(logit))}


def dentro(v, banda):
    return banda[0] <= v <= banda[1]


def coinciden(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return {"identicos": bool(a.tobytes() == b.tobytes()), "maxima_diferencia": float(np.max(np.abs(a - b))),
            "filas": int(len(a))}


def controles_con_red(d, rapido, informe):
    folds = construir_folds(d["df"], G, Y, 5, 0)
    tr, va = folds[0]
    if rapido:
        rng = np.random.default_rng(0)
        pos, neg = va[d["y"][va] == 1], va[d["y"][va] == 0]
        va_eval = np.sort(np.concatenate([pos, rng.choice(neg, size=NEGATIVOS_RAPIDO, replace=False)]))
        epocas = 1
    else:
        va_eval, epocas = va, fase4c.EPOCAS
    y_va = d["y"][va_eval]
    dispositivo = torch.device("mps")
    with h5py.File(HDF5, "r") as h5:
        barajadas = d["y"].copy()
        barajadas[tr] = np.random.default_rng(0).permutation(d["y"][tr])
        logit_b, reg_b = fase4c.entrenar_y_puntuar(h5, d["isic"], barajadas, tr, va_eval, 0, dispositivo, epocas)
        logit_1, reg_1 = fase4c.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, epocas)
        logit_2, reg_2 = fase4c.entrenar_y_puntuar(h5, d["isic"], d["y"], tr, va_eval, 0, dispositivo, epocas)
    banda, media = banda_aleatoria(y_va)
    pauc_b = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit_b)))
    disp = {"barajada": dispersion(logit_b), "primera": dispersion(logit_1), "segunda": dispersion(logit_2)}
    registrar("barajadas", "la red con las etiquetas barajadas, dentro del 99 % central del azar", dentro(pauc_b, banda),
              f"pAUC {pauc_b:.4f}; rango [{banda[0]:.4f}; {banda[1]:.4f}] de {N_ALEATORIAS} puntuaciones aleatorias, "
              f"media {media:.4f}; {len(va_eval)} filas, {int(y_va.sum())} positivos, {epocas} época(s); "
              f"{disp['barajada']['logits_distintos']} logits distintos, desviación "
              f"{disp['barajada']['desviacion_del_logit']:.3g}")
    sintetica = y_va + 0.1 * np.random.default_rng(2).normal(size=len(y_va))
    pauc_s = float(pauc_above_tpr(y_va, sintetica))
    registrar("barajadas", "las etiquetas más un poco de ruido", not dentro(pauc_s, banda), f"pAUC {pauc_s:.4f}",
              debe_fallar=True)

    def por_encima(logit):
        pauc = float(pauc_above_tpr(y_va, fase4c.probabilidad(logit)))
        dis = dispersion(logit)
        return pauc, dis, pauc > banda[1] and dis["logits_distintos"] > 1 and dis["desviacion_del_logit"] > 0
    reales = []
    for nombre, logit in (("primera", logit_1), ("segunda", logit_2)):
        pauc_r, dis, ok = por_encima(logit)
        reales.append({"red": nombre, "pauc": round(pauc_r, 4), **dis})
        registrar("barajadas", f"la red con las etiquetas reales ({nombre}), por encima del rango y con puntuaciones "
                  "que varían", ok, f"pAUC {pauc_r:.4f} frente al límite {banda[1]:.4f}; {dis['logits_distintos']} "
                  f"logits distintos, desviación {dis['desviacion_del_logit']:.3g}")
    pauc_c, dis_c, ok_c = por_encima(np.zeros(len(y_va), dtype=np.float32))
    registrar("barajadas", "una puntuación constante como red real", not ok_c,
              f"pAUC {pauc_c:.4f}; {dis_c['logits_distintos']} logit distinto", debe_fallar=True)
    rep = coinciden(logit_1, logit_2)
    registrar("reproducibilidad", "la misma red dos veces, semilla 0, pliegue 0", True,
              f"idénticos: {rep['identicos']}; mayor diferencia de logit {rep['maxima_diferencia']:.3g} en "
              f"{rep['filas']} filas; {disp['primera']['logits_distintos']} logits distintos, desviación "
              f"{disp['primera']['desviacion_del_logit']:.3g}")
    tocado = np.array(logit_1, dtype=np.float64)
    tocado[0] += 1e-6
    rep_t = coinciden(logit_1, tocado)
    registrar("reproducibilidad", "un logit cambiado en 1e-6", not rep_t["identicos"],
              f"idénticos: {rep_t['identicos']}", debe_fallar=True)
    informe.update({"barajadas": {"pauc": round(pauc_b, 4), "rango_99": [round(b, 4) for b in banda],
                                  "redes_con_las_etiquetas_reales": reales,
                                  "media_aleatoria": round(media, 4), "filas": int(len(va_eval)),
                                  "positivos": int(y_va.sum()), "red": reg_b},
                    "reproducibilidad": {**rep, "redes": [reg_1, reg_2]}, "dispersion_de_los_logits": disp})


# ---- alineacion ------------------------------------------------------------------------------

def control_alineacion(d):
    rng = np.random.default_rng(0)
    isic = np.array([f"ISIC_{i:05d}" for i in range(1000)])
    asign = rng.integers(0, 5, size=1000)
    partes = {k: (isic[asign == k][::-1], np.flatnonzero(asign == k)[::-1].astype(float)) for k in range(5)}
    unido = fase4c.ensamblar(partes, isic, asign)
    registrar("alineacion", "partes correctas, en otro orden, unidas por isic_id", np.array_equal(unido, np.arange(1000)),
              "cada fila con su valor")

    def caso(nombre, cambiar):
        p = {k: (ids.copy(), v.copy()) for k, (ids, v) in partes.items()}
        cambiar(p)
        ok, m = se_detiene(lambda: fase4c.ensamblar(p, isic, asign))
        registrar("alineacion", nombre, ok, m[:110], debe_fallar=True)
    caso("una fila que falta", lambda p: p.__setitem__(0, (p[0][0][1:], p[0][1][1:])))
    caso("una fila repetida", lambda p: p.__setitem__(1, (np.append(p[1][0], p[1][0][0]), np.append(p[1][1], 0.0))))
    otra = int(np.flatnonzero(asign == 2)[0])

    def mover(p):
        p[2] = (p[2][0][p[2][0] != isic[otra]], p[2][1][p[2][0] != isic[otra]])
        p[3] = (np.append(p[3][0], isic[otra]), np.append(p[3][1], 0.0))
    caso("una fila en la red de otro pliegue", mover)
    caso("un isic_id ajeno", lambda p: p.__setitem__(4, (np.append(p[4][0][1:], "ISIC_99999"), p[4][1])))
    # Sobre los pliegues reales de la semilla 0: cada fila de desarrollo, una vez.
    folds = construir_folds(d["df"], G, Y, 5, 0)
    asignacion = np.full(len(d["isic"]), -1)
    for k, (_, va) in enumerate(folds):
        asignacion[va] = k
    reales = {k: (d["isic"][va], va.astype(float)) for k, (_, va) in enumerate(folds)}
    unido = fase4c.ensamblar(reales, d["isic"], asignacion)
    registrar("alineacion", "los pliegues reales de la semilla 0", np.array_equal(unido, np.arange(len(d["isic"]))),
              f"{len(d['isic'])} filas, cada una con la de su pliegue de validación")


# ---- referencias -----------------------------------------------------------------------------

def control_referencias(d):
    predicciones, procedencia = f4b.cargar_predicciones(f4b.PREDICCIONES)
    folds = construir_folds(d["df"], G, Y, 5, 0)
    _, va = folds[0]
    base = f4b.guardada(predicciones, "M3limpio", 0, 0, d["isic"][va])
    with open(REF_M3L, encoding="utf-8") as f:
        ref = json.load(f)["metricas"]["M3limpio"]
    calc = {k: round(v, 4) for k, v in f4.medir(d["y"][va], base, d["grupos"][va]).items()}
    iguales = all(calc[k] == ref[k]["por_semilla_y_fold"]["0"][0] for k in f4.METRICAS)
    registrar("referencias", "las predicciones de M3 limpio pasan sus comprobaciones y reproducen su pliegue", iguales,
              f"semilla 0, pliegue 0: {calc}")
    with tempfile.TemporaryDirectory() as tmp:
        copia = os.path.join(tmp, os.path.basename(f4b.PREDICCIONES))
        shutil.copy(f4b.PREDICCIONES, copia)
        shutil.copy(os.path.splitext(os.path.splitext(f4b.PREDICCIONES)[0])[0] + ".json",
                    os.path.splitext(os.path.splitext(copia)[0])[0] + ".json")
        with open(copia, "ab") as f:
            f.write(b"\0")
        ok, m = se_detiene(lambda: f4b.cargar_predicciones(copia))
    registrar("referencias", "el archivo de predicciones con un byte más", ok and "SHA-256" in m, m[-70:],
              debe_fallar=True)
    with open(REF_PLIEGUES, encoding="utf-8") as f:
        huellas_ref = json.load(f)["folds"]["sha256_por_semilla"]
    with open(IMAGEN_SOLA, encoding="utf-8") as f:
        sola = json.load(f)
    calc = {s: f4.huella_folds(folds if s == 0 else construir_folds(d["df"], G, Y, 5, s), len(d["df"]))
            for s in range(10)}
    iguales = all(calc[s] == huellas_ref[str(s)] for s in range(10))
    registrada = (sola["control_m1_contra_referencia"]["huellas_de_pliegues_iguales"]
                  and sola["control_m1_contra_referencia"]["referencia"] == os.path.relpath(REF_PLIEGUES, RAIZ)
                  and sola["esquema"]["semillas"] == list(range(10)))
    registrar("referencias", "los pliegues de las semillas 0 a 9 tienen la huella de fase4-m2-vs-m1.json, la de "
              "imagen-sola.json", iguales and registrada, f"huellas iguales: {iguales}; imagen-sola las registra: "
              f"{registrada}")
    registrar("referencias", "los pliegues de la semilla 0 frente a la huella de la semilla 1",
              calc[0] != huellas_ref["1"], f"iguales: {calc[0] == huellas_ref['1']}", debe_fallar=True)


# ---- c4 --------------------------------------------------------------------------------------

def control_c4(d):
    folds = construir_folds(d["df"], G, Y, 5, 0)
    tr, va = folds[0]
    x_tr, x_va, _, _ = ganador_m3.variables_m3_en_pliegue(d["df_sin_etiqueta"], tr, va, d["excluidas"], G)
    logit = np.random.default_rng(3).normal(-4, 2, size=len(d["isic"])).astype(np.float32)
    p = fase4c.probabilidad(logit)
    prob = bool(p.dtype == np.float64 and np.all((p > 0) & (p < 1)) and np.all(np.diff(p[np.argsort(logit)]) >= 0))
    registrar("c4", "la puntuación es una probabilidad: sigmoide en float64, entre 0 y 1, en el orden del logit", prob,
              f"dtype {p.dtype}, de {p.min():.3g} a {p.max():.3g}")
    a = fase4c.variables_red(p, tr, va, d["grupos"])
    xc_tr, _ = fase4b.con_imagen(x_tr, x_va, a)
    alin = f4b.comprobar_alineacion(x_tr, xc_tr, a, 0, d["y"][tr], d["grupos"][tr])
    registrar("c4", "alineación de C2 con las variables de la red, antes y después del remuestreo",
              all(alin[k] for k in ("antes", "razon", "despues")), f"{alin}")
    rodado = {"tr": {"puntuacion": np.roll(a["tr"]["puntuacion"], 1), "razon": np.roll(a["tr"]["razon"], 1)},
              "va": a["va"]}
    xr_tr, _ = fase4b.con_imagen(x_tr, x_va, rodado)
    alin_r = f4b.comprobar_alineacion(x_tr, xr_tr, a, 0, d["y"][tr], d["grupos"][tr])
    registrar("c4", "las columnas corridas una fila", not alin_r["antes"], f"{alin_r}", debe_fallar=True)
    cero = p.copy()
    cero[tr[0]] = 0.0
    a_cero = fase4c.variables_red(cero, tr, va, d["grupos"])
    registrar("c4", "una puntuación 0 dentro de un paciente con otras positivas: razón 0",
              a_cero["tr"]["razon"][0] == 0.0 and np.all(np.isfinite(a_cero["tr"]["razon"])),
              f"razón de esa fila: {a_cero['tr']['razon'][0]}")
    for nombre, valor in (("una puntuación negativa", -0.1), ("una puntuación faltante", np.nan)):
        malo = p.copy()
        malo[tr[0]] = valor
        ok, m = se_detiene(lambda: fase4c.variables_red(malo, tr, va, d["grupos"]))
        registrar("c4", nombre, ok, m[:90], debe_fallar=True)
    todo_cero = p.copy()
    todo_cero[tr[d["grupos"][tr] == d["grupos"][tr[0]]]] = 0.0
    ok, m = se_detiene(lambda: fase4c.variables_red(todo_cero, tr, va, d["grupos"]))
    registrar("c4", "un paciente con todas sus puntuaciones en 0", ok, m[:90], debe_fallar=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--out", required=True, help="JSON con el resultado de cada caso")
    args = ap.parse_args()
    if not args.rapido:
        destino = os.path.realpath(args.out)
        if not destino.startswith(os.path.realpath(os.path.join(RAIZ, "data")) + os.sep):
            raise SystemExit("ERROR: la corrida completa de los controles va en data/, donde la lee fase4c_redes.py.")
    if not torch.backends.mps.is_available():
        raise SystemExit("ERROR: MPS no está disponible.")
    t_total = time.perf_counter()
    bajo_caffeinate = fase4c.caffeinate()

    control_ajustes()
    df, datos = cargar_desarrollo(CSV, G, RUTA_HOLDOUT)
    d = {"df": df, "df_sin_etiqueta": df.drop(columns=[Y]), "excluidas": cargar_columnas_excluidas(FUGAS),
         "y": df[Y].to_numpy(), "grupos": df[G].to_numpy(), "isic": df["isic_id"].to_numpy()}
    print(f"Datos de desarrollo: {len(df)} filas", flush=True)
    control_alineacion(d)
    control_referencias(d)
    control_c4(d)
    informe = {}
    controles_con_red(d, args.rapido, informe)

    total = round(time.perf_counter() - t_total, 1)
    malos = [r for r in resultados if not r["ok"]]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"rapido": args.rapido, "datos": datos,
                   "alcance": ("redes de una época sobre los positivos de la validación y 4.000 negativos"
                               if args.rapido else "redes con los ajustes de la fase, sobre toda la validación"),
                   "segundos": total, "casos": resultados, "fallos": len(malos), **informe,
                   "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv,
                               "caffeinate": bajo_caffeinate}}, f, ensure_ascii=False, indent=2)
    print(f"\n{len(resultados) - len(malos)} de {len(resultados)} casos como se esperaba; {total} s. Escrito: {args.out}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())

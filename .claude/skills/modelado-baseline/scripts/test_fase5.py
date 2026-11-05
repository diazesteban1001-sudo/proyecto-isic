#!/usr/bin/env python3
"""
test_fase5.py — controles de fase5.py que no necesitan entrenar nada. Lo que sí
entrena lo controla el ensayo (fase5.py --modo ensayo), que reproduce el pliegue
0 de la semilla 0 de las fases 4 y 4e.

  - las negativas a correr: con la salida del reservado (.json o .md) o la marca
    de la apertura, el programa se detiene antes de leer nada, en los dos modos;
    sin ellas, pasa de ese punto (caso que debe fallar: la negativa no salta);
  - la apertura exige el ensayo completo con el mismo código, y el código y el
    ensayo en el último commit;
  - las funciones que leen el reservado se niegan a hacerlo fuera de la apertura;
  - la evaluación no puede llegar con la etiqueta, la red no recibe etiquetas de
    la evaluación y ningún paciente puede estar a los dos lados;
  - el bootstrap: por paciente, un paciente repetido cuenta como dos en SEtop-15,
    las mismas remuestras para la diferencia, la semilla y la negativa ante una
    remuestra con una sola clase;
  - los recuentos frente a holdout-pacientes.json, en los dos modos;
  - la salida completa, con sus casos que deben fallar;
  - las constantes de la especificación.

No lee el reservado: trabaja con datos sintéticos y directorios temporales.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/test_fase5.py
"""

import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase4_comparar as f4  # noqa: E402
import fase5  # noqa: E402
from metricas_triaje import setop_n  # noqa: E402

CASOS = []


def registrar(grupo, nombre, ok, detalle):
    CASOS.append({"grupo": grupo, "caso": nombre, "como_se_esperaba": bool(ok), "detalle": str(detalle)})
    print(f"[{'OK' if ok else 'FALLA'}] {grupo} · {nombre}: {detalle}", flush=True)


def mensaje(f, *a, **k):
    """El mensaje de SystemExit de f, o None si no se detiene."""
    try:
        f(*a, **k)
    except SystemExit as e:
        return str(e)
    return None


def leyo(*a, **k):
    raise RuntimeError("leyó datos")


def raiz_temporal(con=()):
    d = tempfile.mkdtemp()
    for sub in ("outputs", "data"):
        os.makedirs(os.path.join(d, sub))
    for ruta in con:
        with open(os.path.join(d, ruta), "w") as f:
            f.write("{}")
    return d


def negativas():
    originales = (fase5.cargar_desarrollo, fase5.huella_codigo)
    fase5.cargar_desarrollo = fase5.huella_codigo = leyo  # si llegara a leer, no sería un SystemExit
    try:
        for modo in fase5.MODOS:
            for ruta in ("outputs/fase5-reservado.json", "outputs/fase5-reservado.md", "data/fase5-apertura-iniciada.json"):
                m = mensaje(fase5.main, ["--modo", modo], raiz=raiz_temporal([ruta]))
                registrar("negativas", f"{modo}: con {ruta}, se niega antes de leer nada",
                          m is not None and "ya existe" in m and ruta in m, m)
        fase5.huella_codigo = originales[1]
        try:
            m = mensaje(fase5.main, ["--modo", "apertura"], raiz=raiz_temporal())
        except RuntimeError as e:
            m = str(e)
        registrar("negativas", "apertura sin salida ni marca: la negativa no salta (debe fallar) y pide el ensayo",
                  m is not None and "ya existe" not in m and "fase5-ensayo.json" in m, m)
    finally:
        fase5.cargar_desarrollo, fase5.huella_codigo = originales


def ensayo_previo():
    codigo = fase5.huella_codigo()
    base = {"modo": "ensayo", "completo": True, "controles": {"fallos": 0, "de_casos": 3}, "sha256_del_codigo": codigo}
    variantes = {
        "completo y con el mismo código": (base, True),
        "con otro código": ({**base, "sha256_del_codigo": {**codigo, "fase5.py": "0" * 64}}, False),
        "con un control fallido": ({**base, "controles": {"fallos": 1, "de_casos": 3}}, False),
        "incompleto": ({**base, "completo": False}, False),
        "de la apertura": ({**base, "modo": "apertura"}, False),
    }
    for nombre, (contenido, pasa) in variantes.items():
        d = raiz_temporal()
        r = fase5.rutas(d)
        with open(r["salida"]["ensayo"] + ".json", "w", encoding="utf-8") as f:
            json.dump(contenido, f)
        with open(r["salida"]["ensayo"] + ".md", "w", encoding="utf-8") as f:
            f.write("# ensayo\n")
        m = mensaje(fase5.comprobar_ensayo, r, codigo)
        registrar("ensayo_previo", f"ensayo {nombre}" + ("" if pasa else " (debe fallar)"),
                  (m is None) == pasa, m or "pasa")
    m = mensaje(fase5.comprobar_ensayo, fase5.rutas(raiz_temporal()), codigo)
    registrar("ensayo_previo", "sin ensayo (debe fallar)", m is not None and "falta" in m, m)


def versionado():
    d = tempfile.mkdtemp()

    def git(*a):
        return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True)
    git("init", "-q")
    git("config", "user.email", "prueba@example.com")
    git("config", "user.name", "prueba")
    for nombre in ("a.py", "b.py"):
        with open(os.path.join(d, nombre), "w") as f:
            f.write("x = 1\n")
    m = mensaje(fase5.exigir_versionado, d, ["a.py", "b.py"])
    registrar("versionado", "archivos sin versionar (debe fallar)", m is not None and "no está versionado" in m, m)
    git("add", "a.py", "b.py")
    git("commit", "-q", "-m", "c")
    m = mensaje(fase5.exigir_versionado, d, ["a.py", "b.py"])
    registrar("versionado", "archivos en el último commit", m is None, m or "pasa")
    with open(os.path.join(d, "b.py"), "a") as f:
        f.write("y = 2\n")
    m = mensaje(fase5.exigir_versionado, d, ["a.py", "b.py"])
    registrar("versionado", "un archivo con cambios sin commit (debe fallar)", m is not None and "sin commit" in m, m)


def lectores_del_reservado():
    falso = "/no/existe.csv"
    m = mensaje(fase5.cargar_reservado_sin_etiqueta, falso, falso, "ensayo")
    registrar("reservado", "el ensayo no lee las filas del reservado", m is not None and "no lee el reservado" in m, m)
    m = mensaje(fase5.cargar_caracteristicas_reservado, pd.DataFrame({"isic_id": []}), falso, falso, "ensayo")
    registrar("reservado", "el ensayo no lee las características del reservado", m is not None and "no lee el reservado" in m, m)
    m = mensaje(fase5.cargar_reservado_sin_etiqueta, falso, falso, "apertura")
    registrar("reservado", "en la apertura sí intenta leerlas (debe fallar la negativa)",
              m is not None and "no lee el reservado" not in m, m)

    d = tempfile.mkdtemp()
    csv, holdout = os.path.join(d, "m.csv"), os.path.join(d, "h.json")
    pd.DataFrame({"isic_id": ["a", "b", "c"], fase5.G: ["P1", "P2", "P3"], fase5.Y: [0, 1, 0]}).to_csv(csv, index=False)
    with open(holdout, "w", encoding="utf-8") as f:
        json.dump({"pacientes_reservados": ["P3"]}, f)
    y = fase5.etiquetas_de(csv, ["b", "a"], "ensayo", holdout)
    registrar("reservado", "etiquetas del ensayo, en el orden pedido", list(y) == [1, 0], list(y))
    m = mensaje(fase5.etiquetas_de, csv, ["a", "c"], "ensayo", holdout)
    registrar("reservado", "etiquetas del ensayo con un paciente reservado (debe fallar)", m is not None, m)
    m = mensaje(fase5.etiquetas_de, csv, ["a", "c"], "apertura", holdout)
    registrar("reservado", "etiquetas de la apertura con un paciente no reservado (debe fallar)", m is not None, m)


def separacion():
    ent = pd.DataFrame({"isic_id": ["a", "b"], fase5.G: ["P1", "P1"], fase5.Y: [0, 1], "x": [1.0, 2.0]})
    ev = pd.DataFrame({"isic_id": ["c"], fase5.G: ["P2"], "x": [3.0]})
    unido, tr, va = fase5.unir(ent, ev)
    registrar("separacion", "la evaluación sin etiqueta: el entrenamiento primero y la etiqueta vacía en la evaluación",
              list(tr) == [0, 1] and list(va) == [2] and unido[fase5.Y].iloc[va].isna().all(), f"tr {list(tr)}, va {list(va)}")
    m = mensaje(fase5.unir, ent, ev.assign(**{fase5.Y: [1]}))
    registrar("separacion", "la evaluación con la etiqueta (debe fallar)", m is not None, m)
    m = mensaje(fase5.exigir_disjuntos, ["P1", "P1"], ["P2"])
    registrar("separacion", "pacientes distintos a cada lado", m is None, m or "pasa")
    m = mensaje(fase5.exigir_disjuntos, ["P1", "P2"], ["P2"])
    registrar("separacion", "un paciente a los dos lados (debe fallar)", m is not None, m)

    # La red recibe −1 en las etiquetas de la evaluación: se sustituyen las dos funciones de la 4e.
    import fase4e
    import fase4e_ajuste
    recibidas = {}
    originales = (fase4e.entrenar_y_puntuar, fase4e_ajuste.ajustar_y_puntuar)

    def entrenar(hdf5, isic, etiquetas, tr, va, semilla, dispositivo, pesos_en=None, predecir_filas=True):
        recibidas["entrenar"] = (etiquetas.copy(), tr, va)
        with open(pesos_en, "wb") as f:
            f.write(b"pesos")
        return None, {"negativos": "conjuntos", "negativos_en_mas_de_una_epoca": 0, "epocas": fase4e.EPOCAS,
                      "epocas_corridas": fase4e.EPOCAS, "conjuntos": fase4e.CONJUNTOS, "positivos": 1,
                      "sha256_pesos_guardados": fase5.sha256(pesos_en)}

    def ajustar(hdf5, isic, etiquetas, tr, va, semilla, dispositivo, pesos):
        recibidas["ajustar"] = (etiquetas.copy(), tr, va)
        return np.zeros(len(va), dtype=np.float32), {"lotes_corridos": [1], "lotes_por_epoca": [1],
                                                      "sha256_pesos_de_partida": fase5.sha256(pesos)}
    fase4e.entrenar_y_puntuar, fase4e_ajuste.ajustar_y_puntuar = entrenar, ajustar
    try:
        d = raiz_temporal()
        fase5.puntuar_red(fase5.rutas(d), ent, ev, None, os.path.join(d, "data"))
    finally:
        fase4e.entrenar_y_puntuar, fase4e_ajuste.ajustar_y_puntuar = originales
    bien = all(list(e[va]) == [-1] and list(e[tr]) == [0, 1] for e, tr, va in recibidas.values())
    registrar("separacion", "la red y su ajuste reciben −1 como etiqueta de cada fila de evaluación",
              bien and len(recibidas) == 2, {k: list(v[0]) for k, v in recibidas.items()})


def datos_sinteticos(n_pacientes=40, semilla=0):
    rng = np.random.default_rng(semilla)
    filas = []
    for p in range(n_pacientes):
        n = int(rng.integers(3, 30))
        y = (rng.random(n) < 0.15).astype(int)
        if p % 3 == 0:
            y[0] = 1
        for i in range(n):
            filas.append((f"P{p:03d}", y[i], y[i] * 1.0 + rng.normal(), y[i] * 0.5 + rng.normal()))
    t = pd.DataFrame(filas, columns=["g", "y", "a", "b"])
    return t["y"].to_numpy(), {"M3limpio": t["a"].to_numpy(), "M2": t["b"].to_numpy()}, t["g"].to_numpy()


def bootstrap():
    y, punt, g = datos_sinteticos()
    pacientes, sorteos = fase5.remuestras_por_paciente(g, 50, 2026)
    posiciones = fase5.posiciones_por_paciente(g, pacientes)
    filas, _ = fase5.filas_de_la_remuestra(posiciones, sorteos[0])
    registrar("bootstrap", "la remuestra entra por pacientes completos",
              fase5.es_remuestra_por_paciente(filas, sorteos[0], posiciones), f"{len(pacientes)} pacientes")
    por_lesion = np.random.default_rng(1).integers(0, len(y), size=len(y))
    registrar("bootstrap", "una remuestra por lesiones (debe fallar)",
              not fase5.es_remuestra_por_paciente(por_lesion, sorteos[0], posiciones), "se detecta")
    _, otros = fase5.remuestras_por_paciente(g, 50, 2026)
    _, distintos = fase5.remuestras_por_paciente(g, 50, 2027)
    registrar("bootstrap", "la misma semilla da los mismos sorteos; otra semilla, otros (debe fallar el segundo)",
              np.array_equal(sorteos, otros) and not np.array_equal(sorteos, distintos), "")

    # Un paciente repetido cuenta como dos: A con 20 lesiones y 2 malignas, una en su top-15 y otra no; B con una.
    ya = np.zeros(20, dtype=int)
    ya[[0, 19]] = 1
    sa = -np.arange(20, dtype=float)
    y2 = np.concatenate([ya, [1]])
    s2 = np.concatenate([sa, [5.0]])
    g2 = np.array(["A"] * 20 + ["B"])
    pac, _ = fase5.remuestras_por_paciente(g2, 1, 0)
    pos = fase5.posiciones_por_paciente(g2, pac)
    sorteo = np.array([0, 0, 1])  # A dos veces y B
    filas, grupo = fase5.filas_de_la_remuestra(pos, sorteo)
    nuevo = setop_n(y2[filas], s2[filas], grupo)
    fundido = setop_n(y2[filas], s2[filas], g2[filas])
    registrar("bootstrap", "un paciente repetido cuenta como dos en SEtop-15: (0,5 + 0,5 + 1) / 3",
              abs(nuevo - 2 / 3) < 1e-12, round(nuevo, 6))
    registrar("bootstrap", "con el patient_id original, las dos copias se funden (debe fallar)",
              abs(fundido - 2 / 3) > 1e-6, round(fundido, 6))

    pac, sorteos, pos, valores = fase5.bootstrap(y, punt, g, n_remuestras=200, semilla=2026)
    puntos = {m: f4.medir(y, s, g) for m, s in punt.items()}
    metricas, diferencia = fase5.resumir(puntos, valores)
    d = valores["M3limpio"]["pauc"] - valores["M2"]["pauc"]
    propio = fase5.intervalo(d)
    registrar("bootstrap", "la diferencia sale de las mismas remuestras", diferencia["pauc"]["intervalo_95"] == propio,
              propio)
    barajada = valores["M3limpio"]["pauc"] - np.random.default_rng(0).permutation(valores["M2"]["pauc"])
    registrar("bootstrap", "con las remuestras de M2 barajadas, otro intervalo (debe fallar)",
              fase5.intervalo(barajada) != propio, fase5.intervalo(barajada))
    registrar("bootstrap", "percentiles 2,5 y 97,5 con la interpolación lineal de numpy",
              fase5.intervalo(np.arange(1, 1001, dtype=float)) == [25.975, 975.025],
              fase5.intervalo(np.arange(1, 1001, dtype=float)))

    # Con un solo paciente con malignas entre 40, alguna remuestra no tiene ninguna.
    y1 = np.zeros(len(y), dtype=int)
    y1[np.flatnonzero(g == g[0])[0]] = 1
    m = mensaje(fase5.bootstrap, y1, punt, g, n_remuestras=200, semilla=2026)
    registrar("bootstrap", "una remuestra con una sola clase detiene el programa (debe fallar)",
              m is not None and "una sola clase" in m, m)


def recuentos():
    """El control de recuentos en los dos modos, con un holdout-pacientes.json sintético."""
    d = raiz_temporal()
    r = fase5.rutas(d)
    with open(r["holdout"], "w", encoding="utf-8") as f:
        json.dump({"recuentos": {"reservado": {"pacientes": 2, "pacientes_portadores": 1, "lesiones_malignas": 2},
                                 "desarrollo": {"pacientes": 3, "pacientes_portadores": 2, "lesiones_malignas": 2}}}, f)
    y_ent, g_ent = np.array([1, 0, 1, 0]), np.array(["A", "A", "B", "C"])
    y_ev, g_ev = np.array([1, 1, 0]), np.array(["D", "D", "E"])
    casos = fase5.controles_de_recuentos(r, "apertura", y_ent, g_ent, y_ev, g_ev)
    registrar("recuentos", "apertura: los dos conjuntos cuadran y sus casos que deben fallar se disparan",
              len(casos) == 4 and all(c["ok"] for c in casos), [(c["caso"], c["ok"]) for c in casos])
    casos = fase5.controles_de_recuentos(r, "apertura", y_ent, g_ent, np.array([1, 0, 0]), g_ev)
    registrar("recuentos", "apertura con una maligna de menos en la evaluación (debe fallar)",
              not casos[0]["ok"], casos[0]["detalle"])
    casos = fase5.controles_de_recuentos(r, "ensayo", y_ent[:2], g_ent[:2], y_ent[2:], g_ent[2:])
    registrar("recuentos", "ensayo: entrenamiento y evaluación juntos cuadran con el desarrollo",
              len(casos) == 2 and all(c["ok"] for c in casos), [(c["caso"], c["ok"]) for c in casos])


def salida():
    def completa():
        return {"metricas": {m: {k: {"punto": 0.1, "intervalo_95": [0.05, 0.15]} for k in f4.METRICAS}
                             for m in fase5.MODELOS},
                "diferencia_m3limpio_menos_m2": {k: {"punto": 0.0, "intervalo_95": [-0.01, 0.01],
                                                     "intervalo_entero_por_debajo_de_cero": False} for k in f4.METRICAS},
                "bootstrap": {"remuestras": fase5.REMUESTRAS, "semilla": fase5.SEMILLA_BOOTSTRAP}}
    registrar("salida", "completa", fase5.comprobar_salida(completa()) == [], "sin faltas")
    variantes = {}
    r = completa()
    del r["metricas"]["Red4e"]["nnt80"]
    variantes["sin el NNT de la red"] = r
    r = completa()
    r["metricas"]["M2"]["auc"]["punto"] = float("nan")
    variantes["un punto NaN"] = r
    r = completa()
    r["metricas"]["M3limpio"]["pauc"]["intervalo_95"] = [0.2, 0.1]
    variantes["un intervalo al revés"] = r
    r = completa()
    del r["diferencia_m3limpio_menos_m2"]["setop15"]["intervalo_entero_por_debajo_de_cero"]
    variantes["la diferencia sin su marca"] = r
    r = completa()
    r["bootstrap"]["remuestras"] = 1000
    variantes["1.000 remuestras"] = r
    for nombre, r in variantes.items():
        faltas = fase5.comprobar_salida(r)
        registrar("salida", f"{nombre} (debe fallar)", bool(faltas), faltas)


def constantes():
    esperadas = {"REMUESTRAS": 2000, "SEMILLA_BOOTSTRAP": 2026, "PERCENTILES": (2.5, 97.5), "SEMILLA": 0,
                 "PLIEGUE_DEL_ENSAYO": 0, "N_SPLITS": 5}
    distintas = {k: getattr(fase5, k) for k, v in esperadas.items() if getattr(fase5, k) != v}
    registrar("constantes", "las de PLAN.md, Fase 5", not distintas, distintas or esperadas)
    r = fase5.rutas("/r")
    registrar("constantes", "la salida del reservado y la marca",
              r["salida"]["apertura"] == "/r/outputs/fase5-reservado" and r["marca"] == "/r/data/fase5-apertura-iniciada.json",
              (r["salida"]["apertura"], r["marca"]))


def main():
    negativas()
    ensayo_previo()
    versionado()
    lectores_del_reservado()
    separacion()
    bootstrap()
    recuentos()
    salida()
    constantes()
    fallos = sum(not c["como_se_esperaba"] for c in CASOS)
    print(f"\n{len(CASOS) - fallos} de {len(CASOS)} casos como se esperaba.", flush=True)
    if fallos:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

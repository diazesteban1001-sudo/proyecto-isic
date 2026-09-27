#!/usr/bin/env python3
"""
test_hojas_y_analisis.py — pruebas de preparar_hojas.py y analizar.py con datos
sintéticos. Ningún dato real del experimento: todo se escribe en un directorio
temporal.

1. preparar_hojas.py: la hoja sale sin tratamiento y con las columnas de
   clasificación vacías, conserva el resto tal cual, y la pasada 2 no depende de
   la pasada 1. Controles positivos, cada uno un rechazo que tiene que
   dispararse: sobrescribir una hoja, id que delatan el tratamiento, una columna
   de más, respuestas.csv cambiado entre pasadas.
2. analizar.py: dos pasadas sintéticas que discrepan en exactamente 3
   referencias, con todos los resultados esperados calculados a mano y escritos
   en el caso. Sin tercera lectura, se detiene antes de abrir la llave. Control:
   dos pasadas iguales dan 0 discrepancias y kappa 1.
3. Intervalo de Wilson de 7 de 10 frente a statsmodels, y kappa frente a
   scikit-learn. El valor de statsmodels está además escrito como literal,
   tomado de statsmodels 0.15.0 el 2026-09-27, así que la comparación con el
   literal corre siempre; la comparación en vivo sale como NO CORRIDA, a la
   vista, si el intérprete no tiene statsmodels o scikit-learn.

Uso:
    python actividad-fuentes/test_hojas_y_analisis.py
Devuelve 0 si todo lo corrido se comporta como se espera.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from analizar import kappa_cohen, wilson  # noqa: E402

# Escrita aquí, no importada: el valor esperado no sale del código que se prueba.
COLUMNAS_HOJA = ["id", "orden", "referencia", "doi", "afirmacion",
                 "categoria", "ubicacion", "solo_resumen", "doi_erroneo", "nota"]

# statsmodels 0.15.0, proportion_confint(7, 10, alpha=0.05, method="wilson"),
# 2026-09-27.
WILSON_7_DE_10_STATSMODELS = (0.39677814746114537, 0.8922087325936989)

# 13 referencias: A y B dan 5, C da 3. Los id son opacos a propósito.
IDS = {
    "A": ["417", "082", "936", "251", "770"],
    "B": ["608", "145", "399", "527", "013"],
    "C": ["864", "302", "691"],
}
# Texto con comas, comillas, tildes y un salto de línea: tiene que cruzar el
# CSV sin cambios.
def respuesta(t, j, id_):
    return {
        "id": id_, "tratamiento": t, "orden": str(j + 1),
        "referencia": f'Autor{t}{j}, "Título, con coma" ({2015 + j}). Revista ñ.',
        "doi": f"10.{1000 + j}/{t.lower()}{j}" if j != 2 else "",
        "afirmacion": f"Afirmación {t}{j}: la partición por imagen\nsobreestima el AUC.",
    }

RESPUESTAS = [respuesta(t, j, i) for t, ids in IDS.items() for j, i in enumerate(ids)]

# Clasificación sintética de la pasada 1, y los tres cambios de la pasada 2.
P1 = {
    "417": "no_existe", "082": "no_existe", "936": "no_existe", "251": "no_dice_eso", "770": "utilizable",
    "608": "no_dice_eso", "145": "no_dice_eso", "399": "utilizable", "527": "utilizable", "013": "utilizable",
    "864": "utilizable", "302": "utilizable", "691": "utilizable",
}
CAMBIOS_P2 = {"082": "no_dice_eso", "527": "no_dice_eso", "691": "no_dice_eso"}
TERCERA = {"082": ("no_existe", "motivo sintético 1"), "527": ("utilizable", "motivo sintético 2"),
           "691": ("no_dice_eso", "motivo sintético 3")}
SOLO_RESUMEN = {1: {"417", "399"}, 2: {"399"}}
DOI_ERRONEO = {1: {"864"}, 2: {"864"}}
SIN_UBICACION = {2: {"013"}}  # una utilizable sin ubicación en la pasada 2: un aviso


def escribir_csv(ruta, columnas, filas, separador=","):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, delimiter=separador, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def bytes_de(ruta):
    with open(ruta, "rb") as f:
        return f.read()


def correr(guion, *args):
    return subprocess.run([sys.executable, os.path.join(AQUI, guion), *args],
                          capture_output=True, text=True)


def nuevo_dir(base, nombre, filas=RESPUESTAS, columnas=None, separador=","):
    d = os.path.join(base, nombre)
    os.makedirs(d)
    escribir_csv(os.path.join(d, "respuestas.csv"),
                 columnas or ["id", "tratamiento", "orden", "referencia", "doi", "afirmacion"],
                 filas, separador)
    return d


def clasificar(d, n, categorias):
    """Llena la hoja como lo haría la persona."""
    ruta = os.path.join(d, f"pasada-{n}.csv")
    cols, filas = leer(ruta)
    for f in filas:
        i = f["id"]
        f["categoria"] = categorias[i]
        f["ubicacion"] = "p. 3" if categorias[i] == "utilizable" and i not in SIN_UBICACION.get(n, ()) else ""
        f["solo_resumen"] = "sí" if i in SOLO_RESUMEN[n] else "no"
        f["doi_erroneo"] = "Si" if i in DOI_ERRONEO[n] else ""
    # Un alias del protocolo en vez del código, para probar que se acepta.
    for f in filas:
        if f["categoria"] == "no_dice_eso":
            f["categoria"] = "Existe pero no dice eso"
            break
    escribir_csv(ruta, cols, filas)


def escribir_tercera(d, tercera):
    escribir_csv(os.path.join(d, "tercera-lectura.csv"), ["id", "categoria", "motivo"],
                 [{"id": i, "categoria": c, "motivo": m} for i, (c, m) in tercera.items()])


def parte_1(tmp):
    casos = []
    d = nuevo_dir(tmp, "normal")
    r = correr("preparar_hojas.py", "--pasada", "1", "--dir", d)
    casos.append(("1a. la pasada 1 se escribe", r.returncode == 0, r.stderr.strip()))

    cols, hoja1 = leer(os.path.join(d, "pasada-1.csv"))
    originales = {f["id"]: f for f in RESPUESTAS}
    casos.append(("1b. columnas de la hoja: sin tratamiento, con las de clasificación",
                  cols == COLUMNAS_HOJA and "tratamiento" not in cols, str(cols)))
    casos.append(("1c. las 13 referencias, cada una una vez",
                  sorted(f["id"] for f in hoja1) == sorted(originales), ""))
    intactas = all(f[c] == originales[f["id"]][c] for f in hoja1
                   for c in ("orden", "referencia", "doi", "afirmacion"))
    vacias = all(f[c] == "" for f in hoja1 for c in ("categoria", "ubicacion", "solo_resumen", "doi_erroneo", "nota"))
    casos.append(("1d. el texto cruza el CSV sin cambios (comas, comillas, tildes, salto de línea)", intactas, ""))
    casos.append(("1e. columnas de clasificación vacías", vacias, ""))
    orden_respuestas = [f["id"] for f in RESPUESTAS]
    orden1 = [f["id"] for f in hoja1]
    casos.append(("1f. la hoja está mezclada", orden1 != orden_respuestas
                  and orden1 != sorted(orden_respuestas), " ".join(orden1)))
    _, llave = leer(os.path.join(d, "llave.csv"))
    esperada = {i: t for t, ids in IDS.items() for i in ids}
    casos.append(("1g. llave.csv es id -> tratamiento", {f["id"]: f["tratamiento"] for f in llave} == esperada, ""))

    antes = bytes_de(os.path.join(d, "pasada-1.csv"))
    r = correr("preparar_hojas.py", "--pasada", "1", "--dir", d)
    casos.append(("1h. control: se niega a sobrescribir la pasada 1",
                  r.returncode == 1 and "ya existe" in r.stderr
                  and bytes_de(os.path.join(d, "pasada-1.csv")) == antes, r.stderr.strip()))

    r = correr("preparar_hojas.py", "--pasada", "2", "--dir", d)
    _, hoja2 = leer(os.path.join(d, "pasada-2.csv"))
    orden2 = [f["id"] for f in hoja2]
    casos.append(("1i. la pasada 2 se escribe con otro orden y el mismo contenido",
                  r.returncode == 0 and orden2 != orden1
                  and sorted(map(json.dumps, (sorted(f.items()) for f in hoja2)))
                  == sorted(map(json.dumps, (sorted(f.items()) for f in hoja1))), " ".join(orden2)))

    # La pasada 2 no depende de la pasada 1: la misma hoja sale sin pasada 1, y
    # con una pasada 1 ya clasificada al lado.
    d_sin = nuevo_dir(tmp, "sin-pasada-1")
    correr("preparar_hojas.py", "--pasada", "2", "--dir", d_sin)
    clasificar(d, 1, P1)
    os.remove(os.path.join(d, "pasada-2.csv"))
    correr("preparar_hojas.py", "--pasada", "2", "--dir", d)
    casos.append(("1j. la pasada 2 sale igual sin pasada 1 y con la pasada 1 clasificada al lado",
                  bytes_de(os.path.join(d_sin, "pasada-2.csv")) == bytes_de(os.path.join(d, "pasada-2.csv")), ""))

    d_otro = nuevo_dir(tmp, "otro-orden", filas=list(reversed(RESPUESTAS)), separador=";")
    correr("preparar_hojas.py", "--pasada", "1", "--dir", d_otro)
    d_ref = nuevo_dir(tmp, "referencia-1")
    correr("preparar_hojas.py", "--pasada", "1", "--dir", d_ref)
    casos.append(("1k. la hoja no depende del orden de las filas ni del separador (;)",
                  bytes_de(os.path.join(d_otro, "pasada-1.csv")) == bytes_de(os.path.join(d_ref, "pasada-1.csv")), ""))

    # Controles positivos de los rechazos: nada se escribe.
    secuenciales = [dict(f, id=str(k + 1)) for k, f in enumerate(RESPUESTAS)]
    con_letra = [dict(f, id=f"{f['tratamiento']}{f['orden']}") for f in RESPUESTAS]
    columna_de_mas = [dict(f, herramienta="x") for f in RESPUESTAS]
    for nombre, filas, cols, texto in (
        ("id numerados por tratamiento (1-5 A, 6-10 B, 11-13 C)", secuenciales, None, "deduce de los id"),
        ("id con el tratamiento delante (A1, B3)", con_letra, None, "deduce de los id"),
        ("una columna de más", columna_de_mas,
         ["id", "tratamiento", "orden", "referencia", "doi", "afirmacion", "herramienta"], "exactamente las columnas"),
    ):
        dd = nuevo_dir(tmp, nombre.replace(" ", "_")[:20] + str(len(os.listdir(tmp))), filas=filas, columnas=cols)
        r = correr("preparar_hojas.py", "--pasada", "1", "--dir", dd)
        casos.append((f"1l. control: rechaza {nombre}",
                      r.returncode == 1 and texto in r.stderr and os.listdir(dd) == ["respuestas.csv"],
                      r.stderr.strip()))

    d_cambio = nuevo_dir(tmp, "cambio-entre-pasadas")
    correr("preparar_hojas.py", "--pasada", "1", "--dir", d_cambio)
    cambiadas = [dict(f, tratamiento="B") if f["id"] == "417" else f for f in RESPUESTAS]
    escribir_csv(os.path.join(d_cambio, "respuestas.csv"),
                 ["id", "tratamiento", "orden", "referencia", "doi", "afirmacion"], cambiadas)
    r = correr("preparar_hojas.py", "--pasada", "2", "--dir", d_cambio)
    casos.append(("1m. control: rechaza la pasada 2 si respuestas.csv cambió desde la llave",
                  r.returncode == 1 and not os.path.exists(os.path.join(d_cambio, "pasada-2.csv")),
                  r.stderr.strip()))
    return casos, d


def esperado_a_mano():
    """Lo que analizar.py tiene que dar con P1, CAMBIOS_P2 y TERCERA. Contado a
    mano, no con el código que se prueba."""
    return {
        "no_coinciden": 3,
        "discrepantes": {"082", "527", "691"},
        "tabla": {"no_existe": {"no_existe": 2, "no_dice_eso": 1, "utilizable": 0},
                  "no_dice_eso": {"no_existe": 0, "no_dice_eso": 3, "utilizable": 0},
                  "utilizable": {"no_existe": 0, "no_dice_eso": 2, "utilizable": 5}},
        "celdas": {"no_existe -> no_dice_eso": 1, "utilizable -> no_dice_eso": 2},
        # po = 10/13; pe = (3*2 + 3*6 + 7*5)/169 = 59/169; kappa = 71/110.
        "kappa": round(71 / 110, 4),
        "A": {"entregadas": 5, "faltaron": 0, "p1": [3, 1, 1], "p2": [2, 2, 1], "final": [3, 1, 1], "k": 1,
              "solo_resumen": [1, 0], "doi_erroneo": [0, 0]},
        "B": {"entregadas": 5, "faltaron": 0, "p1": [0, 2, 3], "p2": [0, 3, 2], "final": [0, 2, 3], "k": 3,
              "solo_resumen": [1, 1], "doi_erroneo": [0, 0]},
        "C": {"entregadas": 3, "faltaron": 2, "p1": [0, 0, 3], "p2": [0, 1, 2], "final": [0, 1, 2], "k": 2,
              "solo_resumen": [0, 0], "doi_erroneo": [1, 1]},
        "avisos": 1,
    }


def parte_2(tmp, d):
    casos = []
    p2 = dict(P1, **CAMBIOS_P2)
    clasificar(d, 2, p2)

    # Sin tercera lectura: se detiene, lista las 3, y no ha leído la llave.
    shutil.move(os.path.join(d, "llave.csv"), os.path.join(tmp, "llave-apartada.csv"))
    r = correr("analizar.py", "--dir", d)
    listadas = {i for i in P1 if f"  {i}: pasada 1" in r.stderr}
    casos.append(("2a. sin tercera lectura se detiene antes de abrir la llave y lista las 3",
                  r.returncode == 1 and "La llave no se abrió" in r.stderr
                  and listadas == set(CAMBIOS_P2) and not os.path.exists(os.path.join(d, "resultados.json")),
                  r.stderr.strip().splitlines()[0][:120]))
    shutil.move(os.path.join(tmp, "llave-apartada.csv"), os.path.join(d, "llave.csv"))

    for nombre, tercera, texto in (
        ("una referencia de más", dict(TERCERA, **{"417": ("no_existe", "m")}), "Sobran: ['417']"),
        ("una que falta", {k: v for k, v in TERCERA.items() if k != "691"}, "Faltan: ['691']"),
        ("un motivo vacío", dict(TERCERA, **{"082": ("no_existe", "")}), "sin motivo"),
    ):
        escribir_tercera(d, tercera)
        r = correr("analizar.py", "--dir", d)
        casos.append((f"2b. control: rechaza la tercera lectura con {nombre}",
                      r.returncode == 1 and texto in r.stderr, r.stderr.strip()))

    escribir_tercera(d, TERCERA)
    r = correr("analizar.py", "--dir", d)
    casos.append(("2c. con la tercera lectura, escribe resultados.json y .md",
                  r.returncode == 0 and os.path.exists(os.path.join(d, "resultados.md")), r.stderr.strip()))
    if r.returncode != 0:
        return casos, None, p2
    with open(os.path.join(d, "resultados.json"), encoding="utf-8") as f:
        res = json.load(f)
    e = esperado_a_mano()
    c = res["consistencia"]
    casos.append(("2d. no coinciden exactamente las 3 sembradas",
                  c["no_coinciden"] == e["no_coinciden"]
                  and {x["id"] for x in c["discrepancias"]} == e["discrepantes"], str(c["no_coinciden"])))
    casos.append(("2e. tabla 3 x 3 y celdas de las discrepancias",
                  c["tabla_filas_pasada_1_columnas_pasada_2"] == e["tabla"]
                  and c["no_coinciden_por_celda"] == e["celdas"], json.dumps(c["no_coinciden_por_celda"])))
    casos.append(("2f. kappa = 71/110, calculado a mano", c["kappa_cohen"] == e["kappa"], str(c["kappa_cohen"])))
    motivos = {x["id"]: (x["final"], x["motivo"]) for x in c["discrepancias"]}
    casos.append(("2g. la clasificación final de las discrepantes sale de la tercera lectura",
                  motivos == TERCERA, ""))
    cats = ("no_existe", "no_dice_eso", "utilizable")
    bien = True
    for t in ("A", "B", "C"):
        d_t, e_t = res["por_tratamiento"][t], e[t]
        bien &= (d_t["entregadas"] == e_t["entregadas"] and d_t["faltaron"] == e_t["faltaron"]
                 and [d_t["pasada_1"][x] for x in cats] == e_t["p1"]
                 and [d_t["pasada_2"][x] for x in cats] == e_t["p2"]
                 and [d_t["final"][x] for x in cats] == e_t["final"]
                 and d_t["utilizables_final"]["k"] == e_t["k"]
                 and d_t["utilizables_final"]["n"] == e_t["entregadas"]
                 and [d_t["solo_resumen"]["pasada_1"], d_t["solo_resumen"]["pasada_2"]] == e_t["solo_resumen"]
                 and [d_t["doi_erroneo"]["pasada_1"], d_t["doi_erroneo"]["pasada_2"]] == e_t["doi_erroneo"])
        ic = wilson(e_t["k"], e_t["entregadas"])
        bien &= d_t["utilizables_final"]["wilson_95"] == [round(ic[0], 4), round(ic[1], 4)]
    casos.append(("2h. por tratamiento: entregadas, faltaron, conteos P1/P2/final, marcas, Wilson", bien, ""))
    casos.append(("2i. un aviso: la utilizable sin ubicación de la pasada 2",
                  len(res["avisos_de_protocolo"]) == e["avisos"] and "013" in res["avisos_de_protocolo"][0],
                  str(res["avisos_de_protocolo"])))

    # Control: dos pasadas iguales.
    d_igual = nuevo_dir(tmp, "pasadas-iguales")
    correr("preparar_hojas.py", "--pasada", "1", "--dir", d_igual)
    correr("preparar_hojas.py", "--pasada", "2", "--dir", d_igual)
    clasificar(d_igual, 1, P1)
    clasificar(d_igual, 2, P1)
    r = correr("analizar.py", "--dir", d_igual)
    c0 = {}
    if r.returncode == 0:
        with open(os.path.join(d_igual, "resultados.json"), encoding="utf-8") as f:
            c0 = json.load(f)["consistencia"]
    casos.append(("2j. control: pasadas iguales, 0 discrepancias y kappa 1, sin tercera lectura",
                  r.returncode == 0 and c0["no_coinciden"] == 0 and c0["kappa_cohen"] == 1.0, r.stderr.strip()))
    return casos, res, p2


def parte_3(p2):
    casos, no_corridas = [], []
    casos.append(("3a. Wilson 7 de 10 igual al literal de statsmodels 0.15.0",
                  wilson(7, 10) == WILSON_7_DE_10_STATSMODELS, repr(wilson(7, 10))))
    try:
        from statsmodels.stats.proportion import proportion_confint
    except ImportError:
        no_corridas.append("3b. Wilson frente a statsmodels en vivo: el intérprete no tiene statsmodels")
    else:
        pares = [(7, 10), (0, 5), (5, 5), (1, 5), (3, 5), (2, 3), (0, 1)]
        dif = max(abs(a - b) for k, n in pares
                  for a, b in zip(wilson(k, n), proportion_confint(k, n, alpha=0.05, method="wilson")))
        casos.append((f"3b. Wilson frente a statsmodels en vivo, {len(pares)} casos con 0 y n incluidos",
                      dif <= 1e-12, f"diferencia máxima {dif:.1e}; 7 de 10: "
                      f"{proportion_confint(7, 10, alpha=0.05, method='wilson')}"))
    try:
        from sklearn.metrics import cohen_kappa_score
    except ImportError:
        no_corridas.append("3c. kappa frente a scikit-learn: el intérprete no tiene scikit-learn")
    else:
        ids = sorted(P1)
        k_sk = cohen_kappa_score([P1[i] for i in ids], [p2[i] for i in ids])
        k_nuestro = kappa_cohen([P1[i] for i in ids], [p2[i] for i in ids])
        casos.append(("3c. kappa frente a scikit-learn", abs(k_sk - k_nuestro) <= 1e-12,
                      f"scikit-learn {k_sk!r}, nuestro {k_nuestro!r}"))
    return casos, no_corridas


def main():
    tmp = tempfile.mkdtemp(prefix="actividad-fuentes-")
    try:
        c1, d = parte_1(tmp)
        c2, _, p2 = parte_2(tmp, d)
        c3, no_corridas = parte_3(p2)
        ruta_md = os.path.join(d, "resultados.md")
        md = open(ruta_md, encoding="utf-8").read() if os.path.exists(ruta_md) else "(no se escribió)"
    finally:
        shutil.rmtree(tmp)
    ok = True
    for nombre, bien, detalle in c1 + c2 + c3:
        ok &= bool(bien)
        print(f"{'OK   ' if bien else 'FALLA'} {nombre}" + (f"\n      {detalle}" if detalle and not bien else ""))
        if bien and nombre.startswith(("3b", "3c")):
            print(f"      {detalle}")
    for n in no_corridas:
        print(f"NO CORRIDA {n}")
    if "--md" in sys.argv:
        print("\n----- resultados.md sintético -----\n" + md)
    print(f"\n{'Todo lo corrido pasa.' if ok else 'HAY FALLAS.'} "
          f"{sum(1 for _ in c1 + c2 + c3)} casos, {len(no_corridas)} sin correr.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

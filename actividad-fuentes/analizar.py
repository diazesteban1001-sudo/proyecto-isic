#!/usr/bin/env python3
"""
analizar.py — la sección «Análisis» de protocolo-experimento-v1.md.

Lee, de la misma carpeta:
- pasada-1.csv y pasada-2.csv, clasificadas: las hojas de preparar_hojas.py
  con la columna categoria llena;
- tercera-lectura.csv, con las columnas id, categoria y motivo, una fila por
  cada referencia en que las dos pasadas no coinciden, y solo esas. Si hay
  discrepancias y falta este archivo, el guion lista las referencias que hay
  que leer una tercera vez y se detiene **antes de abrir la llave**;
- llave.csv, id -> tratamiento;
- tratamientos.csv, una fila por tratamiento, con las columnas tratamiento,
  entregadas, se_abstuvo y texto_abstencion. Registra lo que el protocolo pide
  en «Qué se extrae de cada respuesta»: si la respuesta se abstuvo de forma
  explícita («no está en las fuentes»), con el texto literal de la abstención.
  entregadas tiene que coincidir con las referencias de ese tratamiento en la
  llave; se_abstuvo es si o no; con si, texto_abstencion es obligatorio, y con
  no, va vacío. Un tratamiento que no entregó ninguna referencia va con
  entregadas 0.

Escribe resultados.json y resultados.md:
- por tratamiento: cuántas referencias entregó de las 5 pedidas, si se abstuvo
  de forma explícita y con qué texto, y el conteo de cada categoría en la
  pasada 1, en la pasada 2 y en la clasificación final;
- por tratamiento: la proporción de utilizables en la clasificación final, con
  el intervalo de Wilson al 95 %, sobre las referencias que entregó;
- por tratamiento y pasada: cuántas llevan las marcas solo_resumen y doi_erroneo;
- consistencia: la tabla de 3 x 3 de la pasada 1 contra la pasada 2, cuántas
  referencias no coinciden, en qué celdas y con qué motivo; el kappa de Cohen
  como dato secundario, sin intervalo ni prueba;
- ninguna prueba de hipótesis entre tratamientos, por el protocolo.

Categorías, en la columna categoria: no_existe, no_dice_eso, utilizable. Se
aceptan también los nombres del protocolo («no existe», «existe pero no dice
eso»). Marcas, en solo_resumen y doi_erroneo: si o no; vacío cuenta como no.

Solo usa la biblioteca estándar.

Uso:
    python actividad-fuentes/analizar.py
Opción --dir: carpeta de las hojas. Por defecto, la de este guion.
"""

import argparse
import json
import math
import os
import sys
from statistics import NormalDist

from preparar_hojas import PEDIDAS, TRATAMIENTOS, Rechazo, clave_natural, leer_csv

CATEGORIAS = ("no_existe", "no_dice_eso", "utilizable")
NOMBRES = {"no_existe": "No existe", "no_dice_eso": "Existe pero no dice eso", "utilizable": "Utilizable"}
ALIAS = {
    "no_existe": "no_existe", "no existe": "no_existe",
    "no_dice_eso": "no_dice_eso", "existe pero no dice eso": "no_dice_eso",
    "existe_pero_no_dice_eso": "no_dice_eso",
    "utilizable": "utilizable",
}
SI = {"si", "sí"}
NO = {"no", ""}
MARCAS = ("solo_resumen", "doi_erroneo")
CONFIANZA = 0.95


def wilson(k, n, confianza=CONFIANZA):
    """Intervalo de Wilson para k éxitos en n. None si n es 0."""
    if n == 0:
        return None
    z = NormalDist().inv_cdf(0.5 + confianza / 2)
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    medio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centro - medio), min(1.0, centro + medio)


def kappa_cohen(a, b, categorias=CATEGORIAS):
    """Kappa de Cohen sin ponderar. None si no está definido: cuando las dos
    pasadas ponen todas las referencias en una misma y única categoría, el
    acuerdo esperado por azar es 1 y el cociente es 0/0."""
    n = len(a)
    acuerdo = sum(x == y for x, y in zip(a, b)) / n
    esperado = sum((a.count(c) / n) * (b.count(c) / n) for c in categorias)
    if esperado == 1:
        return None
    return (acuerdo - esperado) / (1 - esperado)


def categoria(valor, donde):
    c = ALIAS.get(" ".join(valor.strip().lower().split()))
    if c is None:
        raise Rechazo(f"{donde}: categoría {valor!r}; tiene que ser una de {list(CATEGORIAS)}.")
    return c


def marca(valor, donde):
    v = valor.strip().lower()
    if v in SI:
        return True
    if v in NO:
        return False
    raise Rechazo(f"{donde}: marca {valor!r}; tiene que ser si, no o vacío.")


def leer_pasada(directorio, n):
    ruta = os.path.join(directorio, f"pasada-{n}.csv")
    if not os.path.exists(ruta):
        raise Rechazo(f"no existe {ruta}.")
    columnas, filas = leer_csv(ruta)
    faltan = [c for c in ("id", "categoria", "ubicacion") + MARCAS if c not in columnas]
    if faltan:
        raise Rechazo(f"pasada-{n}.csv: faltan las columnas {faltan}.")
    if "tratamiento" in columnas:
        raise Rechazo(f"pasada-{n}.csv tiene columna de tratamiento: no es una hoja ciega.")
    pasada = {}
    for i, f in enumerate(filas, start=2):
        id_ = f["id"].strip()
        donde = f"pasada-{n}.csv, línea {i} (id {id_})"
        if id_ in pasada:
            raise Rechazo(f"{donde}: id repetido.")
        pasada[id_] = {
            "categoria": categoria(f["categoria"], donde),
            "ubicacion": f["ubicacion"].strip(),
            **{m: marca(f[m], donde) for m in MARCAS},
        }
    return pasada


def leer_tercera(directorio, discrepantes):
    ruta = os.path.join(directorio, "tercera-lectura.csv")
    if not os.path.exists(ruta):
        return None
    columnas, filas = leer_csv(ruta)
    faltan = [c for c in ("id", "categoria", "motivo") if c not in columnas]
    if faltan:
        raise Rechazo(f"tercera-lectura.csv: faltan las columnas {faltan}.")
    tercera = {}
    for i, f in enumerate(filas, start=2):
        id_ = f["id"].strip()
        donde = f"tercera-lectura.csv, línea {i} (id {id_})"
        if id_ in tercera:
            raise Rechazo(f"{donde}: id repetido.")
        if not f["motivo"].strip():
            raise Rechazo(f"{donde}: sin motivo; el protocolo pide el motivo escrito.")
        tercera[id_] = {"categoria": categoria(f["categoria"], donde), "motivo": f["motivo"].strip()}
    if set(tercera) != set(discrepantes):
        sobran = sorted(set(tercera) - set(discrepantes), key=clave_natural)
        faltan = sorted(set(discrepantes) - set(tercera), key=clave_natural)
        raise Rechazo(
            "tercera-lectura.csv tiene que tener exactamente las referencias en que las dos "
            f"pasadas no coinciden. Sobran: {sobran}. Faltan: {faltan}."
        )
    return tercera


def leer_llave(directorio, ids):
    ruta = os.path.join(directorio, "llave.csv")
    if not os.path.exists(ruta):
        raise Rechazo(f"no existe {ruta}.")
    _, filas = leer_csv(ruta)
    llave = {f["id"].strip(): f["tratamiento"].strip() for f in filas}
    if set(llave) != set(ids):
        raise Rechazo("llave.csv y las hojas no tienen los mismos id.")
    otros = sorted(set(llave.values()) - set(TRATAMIENTOS))
    if otros:
        raise Rechazo(f"llave.csv tiene tratamientos fuera del protocolo: {otros}.")
    return llave


def leer_tratamientos(directorio, llave):
    ruta = os.path.join(directorio, "tratamientos.csv")
    if not os.path.exists(ruta):
        raise Rechazo(f"no existe {ruta}.")
    columnas, filas = leer_csv(ruta)
    faltan = [c for c in ("tratamiento", "entregadas", "se_abstuvo", "texto_abstencion") if c not in columnas]
    if faltan:
        raise Rechazo(f"tratamientos.csv: faltan las columnas {faltan}.")
    tratamientos = {}
    for i, f in enumerate(filas, start=2):
        t = f["tratamiento"].strip()
        donde = f"tratamientos.csv, línea {i} (tratamiento {t})"
        if t not in TRATAMIENTOS:
            raise Rechazo(f"{donde}: tratamiento fuera del protocolo.")
        if t in tratamientos:
            raise Rechazo(f"{donde}: tratamiento repetido.")
        try:
            entregadas = int(f["entregadas"])
        except ValueError:
            raise Rechazo(f"{donde}: entregadas {f['entregadas']!r} no es un entero.")
        en_llave = sum(1 for x in llave.values() if x == t)
        if entregadas != en_llave:
            raise Rechazo(f"{donde}: entregadas {entregadas}, pero la llave tiene {en_llave} referencias "
                          "de ese tratamiento.")
        v = f["se_abstuvo"].strip().lower()
        if v not in SI and v != "no":
            raise Rechazo(f"{donde}: se_abstuvo {f['se_abstuvo']!r}; tiene que ser si o no.")
        abstuvo, texto = v in SI, f["texto_abstencion"].strip()
        if abstuvo and not texto:
            raise Rechazo(f"{donde}: se abstuvo, pero falta el texto literal de la abstención.")
        if not abstuvo and texto:
            raise Rechazo(f"{donde}: dice que no se abstuvo y trae texto de abstención.")
        tratamientos[t] = {"entregadas": entregadas, "se_abstuvo": abstuvo, "texto_abstencion": texto or None}
    ausentes = [t for t in TRATAMIENTOS if t not in tratamientos]
    if ausentes:
        raise Rechazo(f"tratamientos.csv: faltan los tratamientos {ausentes}.")
    return tratamientos


def contar(ids, clasif):
    return {c: sum(clasif[i] == c for i in ids) for c in CATEGORIAS}


def analizar(directorio):
    p1 = leer_pasada(directorio, 1)
    p2 = leer_pasada(directorio, 2)
    if set(p1) != set(p2):
        raise Rechazo("pasada-1.csv y pasada-2.csv no tienen los mismos id.")
    ids = sorted(p1, key=clave_natural)
    discrepantes = [i for i in ids if p1[i]["categoria"] != p2[i]["categoria"]]

    # La tercera lectura va antes que la llave: si falta, el guion se detiene
    # sin haber leído ningún tratamiento.
    tercera = leer_tercera(directorio, discrepantes)
    if discrepantes and tercera is None:
        lineas = [f"  {i}: pasada 1 {p1[i]['categoria']}, pasada 2 {p2[i]['categoria']}" for i in discrepantes]
        raise Rechazo(
            f"las dos pasadas no coinciden en {len(discrepantes)} referencias y no existe "
            "tercera-lectura.csv (columnas id, categoria, motivo). La llave no se abrió. "
            "Referencias para la tercera lectura:\n" + "\n".join(lineas)
        )
    tercera = tercera or {}

    llave = leer_llave(directorio, ids)
    tratamientos = leer_tratamientos(directorio, llave)

    c1 = {i: p1[i]["categoria"] for i in ids}
    c2 = {i: p2[i]["categoria"] for i in ids}
    final = {i: tercera[i]["categoria"] if i in tercera else c1[i] for i in ids}

    por_tratamiento = {}
    for t in TRATAMIENTOS:
        suyos = [i for i in ids if llave[i] == t]
        n = len(suyos)
        k = sum(final[i] == "utilizable" for i in suyos)
        ic = wilson(k, n)
        por_tratamiento[t] = {
            "pedidas": PEDIDAS,
            "entregadas": n,
            "faltaron": PEDIDAS - n,
            "se_abstuvo": tratamientos[t]["se_abstuvo"],
            "texto_abstencion": tratamientos[t]["texto_abstencion"],
            "pasada_1": contar(suyos, c1),
            "pasada_2": contar(suyos, c2),
            "final": contar(suyos, final),
            "utilizables_final": {
                "k": k,
                "n": n,
                "proporcion": round(k / n, 4) if n else None,
                "wilson_95": [round(ic[0], 4), round(ic[1], 4)] if ic else None,
            },
            **{m: {"pasada_1": sum(p1[i][m] for i in suyos), "pasada_2": sum(p2[i][m] for i in suyos)}
               for m in MARCAS},
        }

    tabla = {a: {b: sum(c1[i] == a and c2[i] == b for i in ids) for b in CATEGORIAS} for a in CATEGORIAS}
    celdas = {f"{a} -> {b}": tabla[a][b] for a in CATEGORIAS for b in CATEGORIAS if a != b and tabla[a][b]}
    kappa = kappa_cohen([c1[i] for i in ids], [c2[i] for i in ids])

    avisos = [
        f"pasada {n}: id {i} es utilizable y no tiene ubicación (página, sección o cita)"
        for n, p in ((1, p1), (2, p2)) for i in ids
        if p[i]["categoria"] == "utilizable" and not p[i]["ubicacion"]
    ]

    return {
        "protocolo": "protocolo-experimento-v1.md",
        "categorias": list(CATEGORIAS),
        "n_referencias": len(ids),
        "por_tratamiento": por_tratamiento,
        "consistencia": {
            "tabla_filas_pasada_1_columnas_pasada_2": tabla,
            "coinciden": len(ids) - len(discrepantes),
            "no_coinciden": len(discrepantes),
            "no_coinciden_por_celda": celdas,
            "discrepancias": [
                {"id": i, "tratamiento": llave[i], "pasada_1": c1[i], "pasada_2": c2[i],
                 "final": final[i], "motivo": tercera[i]["motivo"]}
                for i in discrepantes
            ],
            "kappa_cohen": round(kappa, 4) if kappa is not None else None,
            "kappa_nota": (
                "Dato secundario, sin intervalo ni prueba: con 15 referencias o menos es inestable."
                if kappa is not None else
                "No definido: las dos pasadas ponen todas las referencias en una misma categoría."
            ),
        },
        "entre_tratamientos": (
            "Sin pruebas de hipótesis, por el protocolo: las referencias de un tratamiento salen "
            "de una sola respuesta y no son independientes. Los intervalos valen para esta "
            "consulta, no para la herramienta en general."
        ),
        "avisos_de_protocolo": avisos,
    }


def fmt(x):
    return "—" if x is None else f"{x:.4f}".replace(".", ",")


def markdown(r):
    L = ["# Experimento de la semana 1: resultados", ""]
    L.append(f"Protocolo: `{r['protocolo']}`. Referencias clasificadas: {r['n_referencias']}.")
    L += ["", "## Por tratamiento", ""]
    L.append("| | Entregadas de 5 | Faltaron | Se abstuvo | " + " | ".join(
        f"{NOMBRES[c]} (P1 / P2 / final)" for c in CATEGORIAS) + " | Solo resumen (P1 / P2) | DOI erróneo (P1 / P2) |")
    L.append("|---" * (6 + len(CATEGORIAS)) + "|")
    for t, d in r["por_tratamiento"].items():
        celdas = [f"{d['pasada_1'][c]} / {d['pasada_2'][c]} / {d['final'][c]}" for c in CATEGORIAS]
        L.append(f"| {t} | {d['entregadas']} | {d['faltaron']} | {'sí' if d['se_abstuvo'] else 'no'} | "
                 + " | ".join(celdas)
                 + f" | {d['solo_resumen']['pasada_1']} / {d['solo_resumen']['pasada_2']}"
                 + f" | {d['doi_erroneo']['pasada_1']} / {d['doi_erroneo']['pasada_2']} |")
    abstenciones = [(t, d["texto_abstencion"]) for t, d in r["por_tratamiento"].items() if d["se_abstuvo"]]
    if abstenciones:
        L += ["", "Abstenciones explícitas, texto literal:", ""]
        L += [f"- {t}: «{texto}»" for t, texto in abstenciones]
    L += ["", "Proporción de utilizables en la clasificación final, sobre las que entregó, "
          "con intervalo de Wilson al 95 %:", ""]
    for t, d in r["por_tratamiento"].items():
        u = d["utilizables_final"]
        ic = u["wilson_95"]
        L.append(f"- {t}: {u['k']} de {u['n']}, {fmt(u['proporcion'])}, "
                 + (f"[{fmt(ic[0])}; {fmt(ic[1])}]" if ic else "sin intervalo (no entregó ninguna)"))
    c = r["consistencia"]
    L += ["", "## Consistencia", "", "Filas: pasada 1. Columnas: pasada 2.", ""]
    L.append("| | " + " | ".join(NOMBRES[x] for x in CATEGORIAS) + " |")
    L.append("|---" * (1 + len(CATEGORIAS)) + "|")
    for a in CATEGORIAS:
        L.append(f"| {NOMBRES[a]} | " + " | ".join(str(c["tabla_filas_pasada_1_columnas_pasada_2"][a][b])
                                                   for b in CATEGORIAS) + " |")
    L += ["", f"No coinciden: {c['no_coinciden']} de {r['n_referencias']}."]
    for d in c["discrepancias"]:
        L.append(f"- {d['id']} ({d['tratamiento']}): {d['pasada_1']} -> {d['pasada_2']}; "
                 f"final {d['final']}. Motivo: {d['motivo']}")
    L += ["", f"Kappa de Cohen: {fmt(c['kappa_cohen'])}. {c['kappa_nota']}"]
    L += ["", "## Entre tratamientos", "", r["entre_tratamientos"]]
    if r["avisos_de_protocolo"]:
        L += ["", "## Avisos de protocolo", ""] + [f"- {a}" for a in r["avisos_de_protocolo"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    try:
        r = analizar(args.dir)
    except Rechazo as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    with open(os.path.join(args.dir, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(os.path.join(args.dir, "resultados.md"), "w", encoding="utf-8") as f:
        f.write(markdown(r))
    print("Escrito resultados.json y resultados.md.")


if __name__ == "__main__":
    main()

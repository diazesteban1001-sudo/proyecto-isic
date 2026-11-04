#!/usr/bin/env python3
"""
por_campo.py — la verificación por campo (PLAN.md, Fase 6, «La verificación por
campo», paso 4, y las dos reglas añadidas antes de él). Cada número del cuerpo
del borrador se busca en lo que cita su comentario F:, no en todo el corpus.
verificar_trazabilidad.py lo llama y escribe el resultado en el grupo
`por_campo` de su salida.

  - Los campos citados: los subárboles que designan sus rutas, con
    comentarios_f.resolver. Un campo citado cuenta aunque su archivo esté en
    FUERA_DEL_CORPUS: la exclusión solo gobierna la búsqueda en todo el corpus.
    n(ruta) aporta el número de elementos de la lista.
  - Las líneas citadas de referencias/: solo cuentan las del texto original.
    Todas las líneas en referencias/_texto-completo/ y en las carpetas con los
    originales intactos; ninguna en un .md que se declara «obra del proyecto»; en
    cualquier otro .md, las líneas de cita («>») y, si tiene «## Texto original»,
    todas las que van después. Lo demás es nuestro: cuenta como documento del
    proyecto.
  - La tolerancia es la de verificar_trazabilidad.tiene_respaldo. Los números de
    las fuentes se leen con verificar_trazabilidad.candidatos, que da las dos
    lecturas del punto y de la coma: «0.94» y «0,94» son 0,94, y «57,000», 57.000.

Cada número cae en una sola clase, y si la suma no da el total, se detiene. Si
algún comentario no entra en la gramática, también se detiene.

Con --medir-azar, mide la tasa de coincidencias por azar dentro del ámbito de cada
comentario, con los rangos del límite del SKILL.md, y la imprime; no escribe nada.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/por_campo.py \\
        --borrador informe/borrador-v2.md --outputs-dir outputs/ --medir-azar
"""

import argparse
import collections
import json
import os
import re
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comentarios_f as cf  # noqa: E402
import verificar_trazabilidad as vt  # noqa: E402

RAIZ = cf.RAIZ
CLASES = ["respaldada_por_su_campo", "respaldada_por_su_referencia", "no_esta_en_sus_campos",
          "fuera_de_las_lineas_citadas", "no_comprobable_aqui", "cita_un_documento_del_proyecto",
          "sin_comentario", "declarada_sin_fuente"]
SENALADAS = {"no_esta_en_sus_campos", "fuera_de_las_lineas_citadas", "cita_un_documento_del_proyecto",
             "sin_comentario"}
TEXTO_ORIGINAL = re.compile(r"^## Texto original")
OBRA_DEL_PROYECTO = re.compile(r"LICENCIA:\**\s*obra del proyecto")
RANGOS = {
    "enteros del 1 al 200": [str(n) for n in range(1, 201)],
    "4 decimales, 0,0001 a 0,0499": [f"0,{k:04d}" for k in range(1, 500)],
    "4 decimales, 0,0500 a 0,2000": [f"0,{k:04d}" for k in range(500, 2001)],
    "3 decimales, 0,500 a 1,000": [f"0,{k:03d}" for k in range(500, 1000)] + ["1,000"],
}


# ---- las líneas originales de referencias/ -------------------------------------------------------

def lineas_originales(archivo, raiz=RAIZ, regla="propia"):
    """(número de líneas, conjunto de líneas originales) de un archivo de referencias/.
    regla="todas" y regla="solo_texto_original" son los clasificadores que deben
    fallar en el control."""
    ruta = os.path.join(raiz, archivo)
    with open(ruta, encoding="utf-8", errors="replace") as f:
        lineas = f.read().split("\n")
    n = len(lineas)
    todas = set(range(1, n + 1))
    if regla == "todas":
        return n, todas
    partes = archivo.split("/")
    if "_texto-completo" in partes or (len(partes) > 2 and partes[0] == "referencias"):
        return n, todas
    if any(OBRA_DEL_PROYECTO.search(l) for l in lineas[:40]):
        return n, set()
    inicio = next((i + 1 for i, l in enumerate(lineas) if TEXTO_ORIGINAL.match(l)), None)
    originales = set() if regla == "solo_texto_original" else \
        {i + 1 for i, l in enumerate(lineas) if re.match(r"\s*>", l)}
    if inicio is not None:
        originales |= set(range(inicio + 1, n + 1))
    return n, originales


def valores_de_lineas(archivo, numeros, raiz=RAIZ):
    """(valores, valores de porcentaje) de los números escritos en esas líneas."""
    with open(os.path.join(raiz, archivo), encoding="utf-8", errors="replace") as f:
        lineas = f.read().split("\n")
    valores, pct = set(), set()
    for n in numeros:
        if not 1 <= n <= len(lineas):
            continue
        for m in vt.NUM_PATTERN.finditer(lineas[n - 1]):
            tok = m.group()
            lecturas = {v for v, _ in vt.candidatos(tok)}
            valores |= lecturas
            if tok.endswith("%"):
                pct |= lecturas
    return valores, pct


# ---- los ámbitos de cada comentario --------------------------------------------------------------

def ambito(c, outputs_dir, raiz=RAIZ, regla="propia", cache=None):
    """Los valores que respaldan una cifra bajo este comentario: de sus campos, de
    sus líneas originales y de sus líneas nuestras, y las citas de referencias."""
    cache = {} if cache is None else cache
    campos, campos_pct = set(), set()
    for r in c["rutas"]:
        if r["archivo"] not in cache:
            with open(os.path.join(outputs_dir, os.path.basename(r["archivo"])), encoding="utf-8") as f:
                cache[r["archivo"]] = json.load(f)
        for nodo in cf.resolver(cache[r["archivo"]], r["ruta"]):
            if r["cuenta"]:
                campos.add(float(len(nodo)))
            else:
                vt.extraer_valores_numericos(nodo, campos, r["ruta"], campos_pct)
    orig, orig_pct, nuestro, nuestro_pct, citas, ausente = set(), set(), set(), set(), [], False
    for ref in c["referencias"]:
        if ref["ausente"]:
            ausente = True
            citas.append({"archivo": ref["archivo"], "lineas": ref["lineas"], "originales": None, "nuestras": None})
            continue
        _, originales = lineas_originales(ref["archivo"], raiz, regla)
        o = [n for n in ref["lineas"] if n in originales]
        u = [n for n in ref["lineas"] if n not in originales]
        v, p = valores_de_lineas(ref["archivo"], o, raiz)
        orig |= v; orig_pct |= p
        v, p = valores_de_lineas(ref["archivo"], u, raiz)
        nuestro |= v; nuestro_pct |= p
        citas.append({"archivo": ref["archivo"], "lineas": ref["lineas"], "originales": len(o), "nuestras": len(u)})
    return {"campos": (campos, campos_pct), "originales": (orig, orig_pct), "nuestras": (nuestro, nuestro_pct),
            "citas": citas, "ausente": ausente}


def clase_de(crudo, c, a, tolerancia_fija=None):
    lecturas = vt.candidatos(crudo)
    pct = crudo.rstrip(".,").endswith("%")

    def en(par):
        return vt.tiene_respaldo(lecturas, pct, par[0], par[1], tolerancia_fija)

    if c["clase"] == "sin fuente":
        return "declarada_sin_fuente"
    if en(a["campos"]):
        return "respaldada_por_su_campo"
    if en(a["originales"]):
        return "respaldada_por_su_referencia"
    if a["ausente"]:
        return "no_comprobable_aqui"
    if en(a["nuestras"]) or (not c["rutas"] and not c["referencias"]):
        return "cita_un_documento_del_proyecto"
    return "no_esta_en_sus_campos" if c["rutas"] else "fuera_de_las_lineas_citadas"


# ---- la clasificación ----------------------------------------------------------------------------

def clasificar(texto, outputs_dir, raiz=RAIZ, tolerancia_fija=None, regla="propia"):
    comentarios, sin_comentario, _ = cf.analizar(texto, outputs_dir, raiz=raiz)
    fuera = [c for c in comentarios if c["clase"] == "no entra"]
    if fuera:
        rota = any(m.startswith(("ruta que no existe", "no existe")) for c in fuera for m in c["motivos"])
        raise SystemExit(("ERROR: cita rota. " if rota else "ERROR: ")
                         + "Comentarios F: fuera de la gramática; no se verifica por campo: "
                         + "; ".join(f"línea {c['linea']}: {', '.join(c['motivos'])}" for c in fuera))
    cache, por_clase = {}, collections.defaultdict(list)
    citas_por_tipo = {"solo_lineas_nuestras": [], "mezcla": [], "solo_lineas_originales": 0, "no_comprobables": 0}
    for c in comentarios:
        a = ambito(c, outputs_dir, raiz, regla, cache)
        for cita in a["citas"]:
            if cita["originales"] is None:
                citas_por_tipo["no_comprobables"] += 1
            elif cita["originales"] == 0:
                citas_por_tipo["solo_lineas_nuestras"].append({"comentario_en_linea": c["linea"], **cita})
            elif cita["nuestras"]:
                citas_por_tipo["mezcla"].append({"comentario_en_linea": c["linea"], **cita})
            else:
                citas_por_tipo["solo_lineas_originales"] += 1
        for n in c["numeros"]:
            k = clase_de(n["valor"], c, a, tolerancia_fija)
            por_clase[k].append({"valor": n["valor"], "linea": n["linea"], "comentario_en_linea": c["linea"],
                                 "campos": [f"{r['archivo']} > {'n(' + r['ruta'] + ')' if r['cuenta'] else r['ruta']}"
                                            for r in c["rutas"]],
                                 "referencias": [f"{x['archivo']}, líneas {x['lineas']}" for x in c["referencias"]]})
    for n in sin_comentario:
        por_clase["sin_comentario"].append({"valor": n["valor"], "linea": n["linea"]})
    total = len(cf.segun_el_verificador(texto))
    if sum(len(v) for v in por_clase.values()) != total:
        raise SystemExit(f"ERROR: las clases por campo suman {sum(len(v) for v in por_clase.values())}, "
                         f"no los {total} números del cuerpo.")
    marcas = [{"comentario_en_linea": c["linea"], "motivo": c["sin_fuente"],
               "numeros": [n["valor"] for n in c["numeros"]]} for c in comentarios if c["clase"] == "sin fuente"]
    return {
        "que_es": ("Cada número del cuerpo, buscado en lo que cita su comentario F: (PLAN.md, Fase 6, «La "
                   "verificación por campo»). Las clases señaladas van con su comentario y lo que cita."),
        "numeros_del_cuerpo": total,
        "por_clase": {k: len(por_clase.get(k, [])) for k in CLASES},
        "senaladas": sum(len(por_clase.get(k, [])) for k in SENALADAS),
        "detalle": {k: por_clase[k] for k in CLASES if k in por_clase and k not in
                    {"respaldada_por_su_campo", "respaldada_por_su_referencia"}},
        "marcas_sin_fuente": marcas,
        "citas_de_referencias": {"solo_lineas_originales": citas_por_tipo["solo_lineas_originales"],
                                 "mezcla": len(citas_por_tipo["mezcla"]),
                                 "solo_lineas_nuestras": len(citas_por_tipo["solo_lineas_nuestras"]),
                                 "no_comprobables_aqui": citas_por_tipo["no_comprobables"],
                                 "lista_solo_lineas_nuestras": citas_por_tipo["solo_lineas_nuestras"],
                                 "lista_mezcla": citas_por_tipo["mezcla"]},
    }


def medir_azar(texto, outputs_dir, raiz=RAIZ):
    """Por rango, la fracción de valores que el ámbito de cada comentario respaldaría
    por azar: mediana y máximo sobre los comentarios con alguna fuente, y la media
    ponderada por los números que cubre cada uno."""
    comentarios, _, _ = cf.analizar(texto, outputs_dir, raiz=raiz)
    cache, filas = {}, []
    for c in comentarios:
        if c["clase"] != "entra":
            continue
        a = ambito(c, outputs_dir, raiz, cache=cache)
        P = a["campos"][0] | a["originales"][0]
        Q = a["campos"][1] | a["originales"][1]
        filas.append((len(c["numeros"]), {k: sum(vt.tiene_respaldo(vt.candidatos(t), False, P, Q) for t in ts) / len(ts)
                                          for k, ts in RANGOS.items()}))
    salida = {}
    peso = sum(w for w, _ in filas)
    for k in RANGOS:
        tasas = [f[k] for _, f in filas]
        salida[k] = {"mediana": statistics.median(tasas), "maximo": max(tasas),
                     "ponderada_por_numeros": sum(w * f[k] for w, f in filas) / peso if peso else None}
    return {"comentarios_con_fuente": len(filas), "rangos": salida}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--borrador", required=True)
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument("--medir-azar", action="store_true")
    args = ap.parse_args()
    with open(args.borrador, encoding="utf-8") as f:
        texto = f.read()
    if args.medir_azar:
        print(json.dumps(medir_azar(texto, args.outputs_dir), ensure_ascii=False, indent=1))
    else:
        r = clasificar(texto, args.outputs_dir)
        print(json.dumps({k: r[k] for k in ("numeros_del_cuerpo", "por_clase", "senaladas")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
comentarios_f.py — el analizador de los comentarios <!-- F: … --> del borrador,
solo en modo informe (PLAN.md, Fase 6, «La verificación por campo:
especificación», paso 2). No verifica ninguna cifra ni toca el borrador: dice
qué comentarios entran en la gramática de las citas y cuáles no, y por qué.

La gramática (la de la especificación):
  - Un comentario F: se parte por «;» fuera de paréntesis y de «…».
  - Parte de outputs/: FUENTE > ruta[, ruta][ y ruta]. FUENTE es outputs/x.json
    o una abreviatura de archivo declarada en un comentario «Abreviaturas de los
    comentarios:» anterior; varias se unen con comas e «y», sin comodines. Las
    rutas son claves separadas por «.», con [i] o [*] y «*» como comodín; una
    abreviatura de tramo (C, IC) sustituye a su tramo; una ruta que empieza por
    «.» sustituye los últimos tramos de la anterior, tantos como tenga; n(ruta)
    cuenta elementos. Lo que va entre paréntesis se ignora. Cada ruta tiene que
    existir en cada fuente.
  - Parte de referencias/: el archivo y sus líneas («línea N», «líneas N y M»).
    Una cita LOCAL (referencias/_texto-completo/, o marcada «LOCAL») cuyo archivo
    no está en esta máquina se lista aparte; no es un fallo de la gramática.
  - Parte con «sin fuente: <motivo>»: una marca «sin fuente».
  - Lo demás es un documento del proyecto: PLAN.md, CLAUDE.md, un SKILL.md, un
    script, el README, otro documento de informe/, una sección del propio
    informe («…») o texto libre.

Cada comentario cae en una clase: entra, no entra, solo documentos del proyecto
(agrupados por tipo) o sin fuente. Los números del cuerpo son los que cuenta
verificar_trazabilidad.py; un comentario cubre los que hay entre el comentario F:
anterior, o el encabezado anterior, y él mismo. Precisiones de la gramática,
declaradas: «e» vale como «y» (C.*.media e IC), y las fuentes se pueden listar
con comas.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/comentarios_f.py \\
        --borrador informe/borrador-v2.md --outputs-dir outputs/ \\
        --out outputs/sintesis-comentarios-f
"""

import argparse
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import verificar_trazabilidad as vt  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
COMENTARIO_F = re.compile(r"<!--\s*F:(.*?)-->", re.DOTALL)
ABREVIATURAS = re.compile(r"Abreviaturas de los comentarios:(.*?)-->", re.DOTALL)
ENCABEZADO = re.compile(r"^#{1,6} ", re.MULTILINE)

SEG = r"(?:[A-Za-z0-9_*]+(?:\[(?:\d+|\*)\])*)"
RUTA = rf"(?:\.?{SEG}(?:\.{SEG})*|n\(\.?{SEG}(?:\.{SEG})*\))"
SEP = r"(?:\s*,\s*|\s+(?:y|e)\s+)"
LISTA_DE_RUTAS = re.compile(rf"^{RUTA}(?:{SEP}{RUTA})*$")
FUENTE_OUTPUTS = re.compile(r"^outputs/[\w.-]+\.json$")
ARCHIVO_REFERENCIAS = re.compile(r"referencias/[^\s,;()«»]+")
LINEAS = re.compile(r"l[ií]neas?\s+\d")


# ---- lectura del comentario ---------------------------------------------------------------------

def partir(texto):
    """Parte por «;» fuera de paréntesis y de «…»."""
    partes, actual, nivel = [], [], 0
    for ch in texto:
        if ch in "(«":
            nivel += 1
        elif ch in ")»":
            nivel = max(0, nivel - 1)
        if ch == ";" and nivel == 0:
            partes.append("".join(actual).strip())
            actual = []
        else:
            actual.append(ch)
    partes.append("".join(actual).strip())
    return [p for p in partes if p]


def sin_parentesis(texto):
    """Quita lo que va entre paréntesis, salvo la llamada n(ruta)."""
    texto = re.sub(r"\bn\(([^()]*)\)", "n\u27e6\\1\u27e7", texto)
    anterior = None
    while anterior != texto:
        anterior, texto = texto, re.sub(r"\s*\([^()]*\)", "", texto)
    return texto.replace("\u27e6", "(").replace("\u27e7", ")").strip()


def leer_abreviaturas(texto):
    """[(posición, {abreviatura: valor})] de cada comentario «Abreviaturas»."""
    bloques = []
    for m in ABREVIATURAS.finditer(texto):
        tabla = {}
        for par in re.split(r";", " ".join(m.group(1).split())):
            if "=" in par:
                k, v = (x.strip() for x in par.split("=", 1))
                tabla[k] = v.rstrip(".").strip()
        bloques.append((m.start(), tabla))
    return bloques


def abreviaturas_en(bloques, posicion):
    tabla = {}
    for inicio, t in bloques:
        if inicio < posicion:
            tabla.update(t)
    return tabla


# ---- rutas ---------------------------------------------------------------------------------------

def tramos(ruta):
    """'por_fold[*].n_val' -> [('por_fold', ['*']), ('n_val', [])]."""
    salida = []
    for t in ruta.split("."):
        nombre = t.split("[", 1)[0]
        indices = re.findall(r"\[(\d+|\*)\]", t)
        salida.append((nombre, indices))
    return salida


def expandir(tokens, abreviaturas, relativas=True):
    """Las rutas absolutas de una lista de tokens, con las abreviaturas de tramo
    sustituidas. Con relativas=False, una ruta que empieza por «.» se toma tal cual,
    sin la anterior (el resolvedor que debe fallar)."""
    absolutas, previa = [], None
    for tok in tokens:
        cuenta = tok.startswith("n(")
        cuerpo = tok[2:-1] if cuenta else tok
        if cuerpo.startswith(".") and relativas:
            nuevos = cuerpo[1:].split(".")
            if previa is None or len(nuevos) > len(previa):
                raise ValueError(f"ruta relativa sin ruta anterior que alcance: {tok}")
            partes = previa[: len(previa) - len(nuevos)] + nuevos
        else:
            partes = cuerpo.lstrip(".").split(".")
        previa = partes
        sustituidas = []
        for p in partes:
            nombre, resto = (p.split("[", 1) + [""])[:2]
            valor = abreviaturas.get(nombre)
            if valor is not None and not valor.endswith(".json"):
                sustituidas.append(valor + ("[" + resto if resto else ""))
            else:
                sustituidas.append(p)
        absolutas.append(("n" if cuenta else "", ".".join(sustituidas)))
    return absolutas


def resolver(obj, ruta):
    """Los nodos que designa la ruta; lista vacía si no existe."""
    nodos = [obj]
    for nombre, indices in tramos(ruta):
        siguientes = []
        for nodo in nodos:
            if nombre == "*":
                if isinstance(nodo, dict):
                    siguientes.extend(nodo.values())
                elif isinstance(nodo, list):
                    siguientes.extend(nodo)
            elif isinstance(nodo, dict) and nombre in nodo:
                siguientes.append(nodo[nombre])
            elif isinstance(nodo, list) and nombre.isdigit() and int(nombre) < len(nodo):
                siguientes.append(nodo[int(nombre)])
        for i in indices:
            siguientes = [x for n in siguientes if isinstance(n, list)
                          for x in (n if i == "*" else ([n[int(i)]] if int(i) < len(n) else []))]
        nodos = siguientes
        if not nodos:
            return []
    return nodos


# ---- clasificación de cada parte -----------------------------------------------------------------

def tipo_de_documento(parte):
    for clave, tipo in (("PLAN.md", "PLAN.md"), ("CLAUDE.md", "CLAUDE.md"), ("SKILL.md", "SKILL.md"),
                        (".py", "script"), ("README", "README"), ("informe/", "otro documento de informe/"),
                        ("«", "sección del informe")):
        if clave in parte:
            return tipo
    return "texto libre"


def parte_de_outputs(parte, abreviaturas, cargar, relativas=True):
    """(motivos, rutas resueltas): motivos vacío si la parte entra en la gramática."""
    s = sin_parentesis(parte)
    if s.count(" > ") != 1:
        return ([f"{'ninguna' if ' > ' not in s else 'más de una'} «FUENTE > ruta» en la parte"], [])
    izquierda, derecha = (x.strip() for x in s.split(" > "))
    motivos, archivos = [], []
    for f in re.split(r"\s*,\s*|\s+y\s+", izquierda):
        destino = abreviaturas.get(f, f)
        if "*" in f:
            motivos.append(f"comodín en la fuente: {f}")
        elif FUENTE_OUTPUTS.match(destino):
            archivos.append(destino)
        else:
            motivos.append(f"fuente no reconocida: {f}")
    if not LISTA_DE_RUTAS.match(derecha):
        return (motivos + [f"rutas fuera de la gramática: {derecha}"], [])
    try:
        rutas = expandir(re.split(SEP, derecha), abreviaturas, relativas)
    except ValueError as e:
        return (motivos + [str(e)], [])
    resueltas = []
    for archivo in archivos:
        datos = cargar(archivo)
        if datos is None:
            motivos.append(f"no existe {archivo}")
            continue
        for cuenta, ruta in rutas:
            nodos = resolver(datos, ruta)
            if not nodos:
                motivos.append(f"ruta que no existe: {ruta} en {archivo}")
            elif cuenta and not all(isinstance(n, list) for n in nodos):
                motivos.append(f"n() sobre algo que no es una lista: {ruta} en {archivo}")
            else:
                resueltas.append({"archivo": archivo, "ruta": ruta, "cuenta": bool(cuenta), "nodos": len(nodos)})
    return motivos, resueltas


def parte_de_referencias(parte):
    """(motivos, archivo, local_ausente)."""
    m = ARCHIVO_REFERENCIAS.search(parte)
    archivo = m.group(0).rstrip(".,:")
    local = "_texto-completo/" in archivo or "LOCAL" in parte
    existe = os.path.exists(os.path.join(RAIZ, archivo))
    motivos = []
    if not LINEAS.search(parte):
        motivos.append(f"referencia sin líneas: {archivo}")
    if not existe and not local:
        motivos.append(f"no existe {archivo}")
    return motivos, archivo, (local and not existe)


def analizar_comentario(texto, abreviaturas, cargar, relativas=True):
    partes = partir(" ".join(texto.split()))
    salida = {"motivos": [], "documentos": [], "rutas": [], "referencias": [], "local_ausente": [],
              "sin_fuente": None, "fuentes": 0}
    for p in partes:
        if p.lower().startswith("sin fuente:"):
            salida["sin_fuente"] = p.split(":", 1)[1].strip()
        elif "referencias/" in p:
            salida["fuentes"] += 1
            motivos, archivo, ausente = parte_de_referencias(p)
            salida["motivos"] += motivos
            salida["referencias"].append(archivo)
            if ausente:
                salida["local_ausente"].append(archivo)
        elif " > " in p or "outputs/" in p:
            salida["fuentes"] += 1
            motivos, rutas = parte_de_outputs(p, abreviaturas, cargar, relativas)
            salida["motivos"] += motivos
            salida["rutas"] += rutas
        else:
            salida["documentos"].append(tipo_de_documento(p))
    if salida["sin_fuente"] is not None:
        salida["clase"] = "sin fuente"
    elif salida["fuentes"] == 0:
        salida["clase"] = "solo documentos del proyecto"
    elif salida["motivos"]:
        salida["clase"] = "no entra"
    else:
        salida["clase"] = "entra"
    return salida


# ---- los números del cuerpo ----------------------------------------------------------------------

def numeros_del_cuerpo(texto):
    """(posición, crudo, línea) de los números que verificar_trazabilidad.py
    busca en outputs/: los mismos pasos que extraer_numeros_del_borrador, y sin
    los de comentarios, contextos omitidos ni porcentajes del método."""
    lineas = texto.split("\n")
    inicios = [m.end() for m in re.finditer(r"^", texto, re.MULTILINE)]
    comentarios = [(m.start(), m.end()) for m in vt.COMENTARIO_HTML.finditer(texto)]
    salida = []
    for m in vt.NUM_PATTERN.finditer(texto):
        crudo = m.group()
        if vt.es_parte_de_identificador(texto, m.start(), m.end()):
            continue
        n_linea = texto[: m.start()].count("\n")
        if vt.es_numeracion_de_seccion(texto, m.start(), lineas[n_linea], m.start() - inicios[n_linea]):
            continue
        valores = vt.candidatos(crudo)
        if not valores:
            continue
        contexto = texto[max(0, m.start() - 40): min(len(texto), m.end() + 10)].replace("\n", " ").strip()
        if any(a <= m.start() < b for a, b in comentarios) or any(ig in contexto for ig in vt.IGNORAR_CONTEXTOS):
            continue
        if crudo.endswith("%") and any(any(abs(x - v) <= vt.EXACTO for x, _ in valores)
                                        for v in vt.PORCENTAJES_DE_METODO):
            continue
        salida.append((m.start(), crudo, n_linea + 1))
    return salida


def segun_el_verificador(texto):
    """(crudo, línea) de los números del cuerpo según verificar_trazabilidad.py,
    con sus mismos filtros, para el control."""
    salida = []
    for valores, crudo, contexto, linea, en_comentario in vt.extraer_numeros_del_borrador(texto):
        if en_comentario or any(ig in contexto for ig in vt.IGNORAR_CONTEXTOS):
            continue
        if crudo.endswith("%") and any(any(abs(x - v) <= vt.EXACTO for x, _ in valores)
                                        for v in vt.PORCENTAJES_DE_METODO):
            continue
        salida.append((crudo, linea))
    return salida


# ---- el informe ----------------------------------------------------------------------------------

def analizar(texto, outputs_dir, relativas=True):
    cache = {}

    def cargar(archivo):
        if archivo not in cache:
            ruta = os.path.join(outputs_dir, os.path.basename(archivo))
            try:
                with open(ruta, encoding="utf-8") as f:
                    cache[archivo] = json.load(f)
            except (OSError, json.JSONDecodeError):
                cache[archivo] = None
        return cache[archivo]

    bloques = leer_abreviaturas(texto)
    encabezados = [m.start() for m in ENCABEZADO.finditer(texto)]
    comentarios = []
    for m in COMENTARIO_F.finditer(texto):
        a = analizar_comentario(m.group(1), abreviaturas_en(bloques, m.start()), cargar, relativas)
        a.update({"inicio": m.start(), "linea": texto[: m.start()].count("\n") + 1,
                  "texto": " ".join(m.group(0).split()), "numeros": []})
        comentarios.append(a)
    sin_comentario = []
    for pos, crudo, linea in numeros_del_cuerpo(texto):
        siguiente = next((c for c in comentarios if c["inicio"] >= pos), None)
        if siguiente is None or any(pos < h < siguiente["inicio"] for h in encabezados):
            sin_comentario.append({"valor": crudo, "linea": linea})
        else:
            siguiente["numeros"].append({"valor": crudo, "linea": linea})
    return comentarios, sin_comentario, bloques


def informe(texto, outputs_dir, borrador):
    comentarios, sin_comentario, bloques = analizar(texto, outputs_dir)
    propios = [(crudo, linea) for _, crudo, linea in numeros_del_cuerpo(texto)]
    esperado = segun_el_verificador(texto)
    if propios != esperado:
        raise SystemExit(f"ERROR: los {len(propios)} números del cuerpo no son los {len(esperado)} del verificador.")
    n_cuerpo = sum(len(c["numeros"]) for c in comentarios) + len(sin_comentario)
    if n_cuerpo != len(propios):
        raise SystemExit(f"ERROR: se asignaron {n_cuerpo} números de {len(propios)}.")

    por_clase = collections.Counter(c["clase"] for c in comentarios)
    numeros_por_clase = collections.Counter()
    for c in comentarios:
        numeros_por_clase[c["clase"]] += len(c["numeros"])
    no_entran = [c for c in comentarios if c["clase"] == "no entra"]
    motivos = collections.Counter(re.sub(r":.*", "", m) for c in no_entran for m in c["motivos"])
    grupos = collections.defaultdict(lambda: {"comentarios": 0, "numeros": 0, "lineas": []})
    for c in comentarios:
        if c["clase"] == "solo documentos del proyecto":
            g = grupos[" + ".join(sorted(set(c["documentos"])))]
            g["comentarios"] += 1
            g["numeros"] += len(c["numeros"])
            g["lineas"].append(c["linea"])

    def ficha(c):
        return {"linea": c["linea"], "comentario": c["texto"], "motivos": c["motivos"],
                "numeros_que_cubre": c["numeros"]}

    return {
        "que_es": ("Analizador de los comentarios F: del borrador, solo en modo informe (PLAN.md, Fase 6, «La "
                   "verificación por campo: especificación», paso 2). No verifica cifras ni toca el borrador."),
        "borrador": borrador,
        "abreviaturas": [{"linea": texto[:p].count("\n") + 1, "tabla": t} for p, t in bloques],
        "resumen": {
            "comentarios_f": len(comentarios),
            "por_clase": dict(por_clase),
            "no_entran_que_cubren_numeros": sum(1 for c in no_entran if c["numeros"]),
            "numeros_del_cuerpo": n_cuerpo,
            "numeros_por_clase_de_comentario": dict(numeros_por_clase),
            "numeros_sin_comentario": len(sin_comentario),
            "marcas_sin_fuente": por_clase.get("sin fuente", 0),
        },
        "motivos_de_los_que_no_entran": dict(motivos),
        "no_entran": [ficha(c) for c in no_entran],
        "solo_documentos_del_proyecto_por_tipo": dict(sorted(grupos.items(), key=lambda kv: -kv[1]["comentarios"])),
        "solo_documentos_del_proyecto": [ficha(c) | {"tipos": sorted(set(c["documentos"]))} for c in comentarios
                                         if c["clase"] == "solo documentos del proyecto"],
        "marcas_sin_fuente": [{"linea": c["linea"], "motivo": c["sin_fuente"], "numeros_que_cubre": c["numeros"]}
                              for c in comentarios if c["clase"] == "sin fuente"],
        "referencias_local_ausentes": sorted({a for c in comentarios for a in c["local_ausente"]}),
        "numeros_sin_comentario": sin_comentario,
        "control": {"numeros_del_cuerpo_segun_el_verificador": len(esperado), "misma_lista": True},
    }


def escribir(out, r):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    s = r["resumen"]
    clases = s["por_clase"]
    lineas = [f"# Comentarios F: de {r['borrador']} (modo informe)", "",
              f"Comentarios F: {s['comentarios_f']}: entran {clases.get('entra', 0)}, no entran "
              f"{clases.get('no entra', 0)} ({s['no_entran_que_cubren_numeros']} de ellos cubren números del cuerpo), "
              f"solo documentos del proyecto {clases.get('solo documentos del proyecto', 0)}, sin fuente "
              f"{clases.get('sin fuente', 0)}.",
              f"Números del cuerpo: {s['numeros_del_cuerpo']} (los mismos que cuenta el verificador); por clase de "
              f"su comentario: {s['numeros_por_clase_de_comentario']}; sin comentario: {s['numeros_sin_comentario']}.",
              "", "Motivos de los que no entran (un comentario puede tener varios): " + "; ".join(
                  f"{k}: {v}" for k, v in sorted(r["motivos_de_los_que_no_entran"].items(), key=lambda kv: -kv[1])) + ".",
              "", "Solo documentos del proyecto, por tipo: " + "; ".join(
                  f"{k}: {g['comentarios']} comentarios, {g['numeros']} números"
                  for k, g in r["solo_documentos_del_proyecto_por_tipo"].items()) + ".",
              "", f"Marcas «sin fuente»: {s['marcas_sin_fuente']}. Referencias LOCAL que no están en esta máquina: "
              f"{len(r['referencias_local_ausentes'])}. El detalle, en el .json. No interpreta."]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {out}.json y .md")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--borrador", required=True)
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.borrador, encoding="utf-8") as f:
        texto = f.read()
    r = informe(texto, args.outputs_dir, os.path.relpath(os.path.abspath(args.borrador), RAIZ))
    r["comando"] = {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv}
    escribir(args.out, r)


if __name__ == "__main__":
    main()

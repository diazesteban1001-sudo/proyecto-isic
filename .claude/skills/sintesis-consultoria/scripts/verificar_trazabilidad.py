#!/usr/bin/env python3
"""
verificar_trazabilidad.py — instrumento de verificación para la skill
sintesis-consultoria.

Extrae todo número presente en el borrador del informe y lo compara
contra el conjunto de valores numéricos que aparecen en outputs/*.json.
No decide si un número está bien citado en contexto — solo señala
cuáles no tienen respaldo exacto (con tolerancia) en ningún archivo de
outputs/. La revisión de cada señal la hace una persona.

Uso:
    python verificar_trazabilidad.py --borrador informe/borrador.md \
                                      --outputs-dir outputs/ \
                                      --out outputs/sintesis-verificacion \
                                      --tolerancia 0.01
"""

import argparse
import fnmatch
import glob
import json
import os
import re


# El borrador está en español: separador decimal coma, separador de miles
# punto ("0,8053", "401.059"). Un patrón que asuma convención inglesa parte
# "0,8053" en dos números y lee "401.059" como cuatrocientos uno con cincuenta
# y nueve — ninguno de los dos tiene respaldo en outputs/ y ambos se señalan
# como falsos positivos.
NUM_PATTERN = re.compile(r"-?\d[\d.,]*%?")

# Punto seguido de exactamente tres dígitos = separador de miles, no decimal.
MILES = re.compile(r"(?<=\d)\.(?=\d{3}(?!\d))")


def candidatos(crudo):
    """Devuelve todas las lecturas plausibles de un token numérico.

    El punto es ambiguo en este informe: el cuerpo usa convención española
    ("401.059" son cuatrocientos un mil) pero el anexo de trazabilidad cita
    los valores crudos del JSON ("0.098" es un decimal). No se adivina cuál
    es: se generan las dos lecturas y basta con que una tenga respaldo. El
    script es un filtro, no un árbitro."""
    limpio = crudo.rstrip("%").rstrip(".,").replace(",", ".")
    lecturas = {limpio, MILES.sub("", limpio)}
    valores = []
    for lectura in lecturas:
        try:
            valores.append(float(lectura))
        except ValueError:
            pass
    return valores

# Números triviales que casi siempre aparecen sin venir de outputs/
# (numeración de secciones, años, "5 skills", etc.) — se listan aparte,
# no se descartan en silencio.
IGNORAR_CONTEXTOS = ["2024", "2026", "Nivel 0", "Nivel 1", "Nivel 2"]


# ---------------------------------------------------------------------------
# Porcentajes que NO son mediciones
# ---------------------------------------------------------------------------
# Un porcentaje puede ser un resultado ("el 99,04% de los grupos tiene fuga")
# o un PARÁMETRO DEL MÉTODO ("intervalo al 95%", "pAUC sobre 80% TPR"). Los
# segundos no salen de ningún cálculo nuestro: son constantes del diseño o
# del cliente. Buscarles respaldo en outputs/ es un error de categoría, y
# dejarlos pasar "porque alguien los respalda" es peor: es respaldarlos por
# coincidencia.
#
# Por eso salen del conteo por esta lista explícita, no por azar numérico.
# Se reportan aparte, en `porcentajes_de_metodo_excluidos`, para que la
# exclusión sea visible y auditable en vez de silenciosa.
#
# Solo aplica a tokens escritos CON el signo "%": "80 pacientes" no es lo
# mismo que "80% TPR" y no se excluye.
PORCENTAJES_DE_METODO = {
    # Nivel de confianza de los intervalos del informe. Es una convención
    # estadística elegida por nosotros, no un valor medido: ningún script
    # produce "95" como resultado.
    95.0: "nivel de confianza de los intervalos (convención, no medición)",
    # Umbral de TPR de la métrica oficial de Kaggle, rango [0.0, 0.2]
    # (referencias/kaggle-evaluation.md). Es la constante MIN_TPR del
    # proyecto, declarada por el cliente. Guardarraíl 3 de CLAUDE.md.
    80.0: "umbral de TPR del pAUC de Kaggle (constante del cliente)",
    # Umbral de TPR del esquema de premios del organizador ISIC, rango
    # [0.00, 0.12] (referencias/isic-metrics-readme.md). Es el valor rival
    # que el informe cita para explicar por qué NO se usa. Cifra externa.
    88.0: "umbral de TPR del esquema de premios ISIC (cifra externa, no usada)",
}

# Nombres de campo que declaran unidades de porcentaje. Se aplica sobre la
# ruta completa del campo, así que basta con que un ancestro lo declare.
CAMPO_PORCENTAJE = re.compile(r"(^|[._\[])(pct|porcentaje|porciento|percent)",
                              re.IGNORECASE)

# Margen para la comparación "fracción reescalada". A diferencia de la
# tolerancia de redondeo, aquí NO hay margen: 0.8816 × 100 = 88.16, que no
# es 88. Ese cero es lo que mata la coincidencia fortuita.
EXACTO = 1e-9


def extraer_valores_numericos(obj, acumulador, ruta="", acumulador_pct=None):
    """Recorre recursivamente un dict/list de JSON y junta todos los
    números que encuentre, como floats.

    Lleva además la ruta del campo (`nivel_1.pauc_por_fold[0]`) para poder
    separar los valores que vienen de un campo cuyo NOMBRE declara unidades
    de porcentaje. Sin esa distinción, un porcentaje del informe se compara
    contra cualquier float del corpus y encuentra pareja por azar."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            sub = f"{ruta}.{k}" if ruta else str(k)
            extraer_valores_numericos(v, acumulador, sub, acumulador_pct)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            extraer_valores_numericos(v, acumulador, f"{ruta}[{i}]", acumulador_pct)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        acumulador.add(float(obj))
        if acumulador_pct is not None and CAMPO_PORCENTAJE.search(ruta):
            acumulador_pct.add(float(obj))


# Archivos de outputs/ en los que NO se busca respaldo, cada uno con su
# motivo. Sus cifras existen, pero ninguna cifra del informe puede apoyarse
# en ellas: si una coincide, es casualidad, no trazabilidad. Se comparan por
# nombre de archivo, con comodines.
FUERA_DEL_CORPUS = {
    "holdout-pacientes.json": (
        "Recuentos del conjunto reservado. No son mediciones del informe, y el "
        "conjunto reservado no se toca hasta la evaluación final."
    ),
    "sensibilidad-*.json": (
        "Análisis de sensibilidad. No sustituyen a la corrida principal ni se usan "
        "para elegir nada, así que no respaldan cifras del informe."
    ),
    "sintesis-verificacion.json": (
        "La salida de este mismo script. Sus recuentos describen una verificación "
        "anterior del borrador, no mediciones; en el corpus, el borrador quedaría "
        "respaldado por su propia verificación."
    ),
}


def fuera_del_corpus(nombre):
    """El motivo si el archivo está en la lista declarada; None si no."""
    return next((m for patron, m in FUERA_DEL_CORPUS.items() if fnmatch.fnmatch(nombre, patron)), None)


def cargar_valores_permitidos(outputs_dir, excluidos=None):
    """Devuelve (todos_los_valores, valores_de_campos_declarados_porcentaje).
    Si se pasa `excluidos`, añade ahí los archivos que dejó fuera y por qué."""
    valores = set()
    valores_pct = set()
    for path in sorted(glob.glob(os.path.join(outputs_dir, "*.json"))):
        motivo = fuera_del_corpus(os.path.basename(path))
        if motivo:
            if excluidos is not None:
                excluidos.append({"archivo": os.path.basename(path), "motivo": motivo})
            continue
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        extraer_valores_numericos(data, valores, os.path.basename(path), valores_pct)
    return valores, valores_pct


def es_parte_de_identificador(texto, ini, fin):
    """Un número pegado a letras no es una cifra citada: es parte de un
    identificador (PMC11324883, SLICE-3D, 133px). Y [T18]/[E3] son marcas
    del anexo de trazabilidad, no cifras del informe."""
    antes = texto[ini - 1] if ini > 0 else ""
    despues = texto[fin] if fin < len(texto) else ""
    if antes.isalpha() or despues.isalpha():
        return True
    # snake_case: `intervalo_t_95`, `nivel_2b_...` — el guion bajo une tanto
    # como una letra. El 95 de `intervalo_t_95` es parte del nombre del campo,
    # no una cifra que el informe afirme.
    if antes == "_" or despues == "_":
        return True
    if texto[max(0, ini - 2) : ini] in ("[T", "[E") and despues == "]":
        return True
    return False


# Un "3.1" de encabezado o un "sección 7.4" son numeración del documento, no
# cifras medidas. IGNORAR_CONTEXTOS ya lo declaraba en su comentario —
# "numeración de secciones"— pero nunca lo implementó: pasaban porque la
# regla de reescalado le encontraba respaldo a cualquier cosa. Al endurecer
# esa regla quedaron a la vista, así que aquí se excluyen por mecanismo
# explícito en vez de por accidente.
REFERENCIA_A_SECCION = re.compile(r"(secci[oó]n(es)?|§)\s*$", re.IGNORECASE)


def es_numeracion_de_seccion(texto, ini, linea_texto, col):
    """True si el token es numeración del propio documento."""
    # a) Encabezado Markdown: "### 7.3 Lectura de los resultados"
    encabezado = re.match(r"^\s*#{1,6}\s+", linea_texto)
    if encabezado and col == encabezado.end():
        return True
    # b) Referencia cruzada: "(sección 7.4)", "§10.1"
    if REFERENCIA_A_SECCION.search(texto[max(0, ini - 12):ini]):
        return True
    return False


def extraer_numeros_del_borrador(texto):
    encontrados = []
    inicios_de_linea = [m.end() for m in re.finditer(r"^", texto, re.MULTILINE)]
    lineas = texto.split("\n")
    for match in NUM_PATTERN.finditer(texto):
        crudo = match.group()
        if es_parte_de_identificador(texto, match.start(), match.end()):
            continue
        n_linea = texto[: match.start()].count("\n")
        col = match.start() - (inicios_de_linea[n_linea] if n_linea < len(inicios_de_linea) else 0)
        if es_numeracion_de_seccion(texto, match.start(), lineas[n_linea], col):
            continue
        valores = candidatos(crudo)
        if not valores:
            continue
        inicio = max(0, match.start() - 40)
        fin = min(len(texto), match.end() + 10)
        contexto = texto[inicio:fin].replace("\n", " ").strip()
        linea_aprox = texto[: match.start()].count("\n") + 1
        encontrados.append((valores, crudo, contexto, linea_aprox))
    return encontrados


def tiene_respaldo(valores, es_porcentaje, permitidos, permitidos_pct, tolerancia):
    """¿Alguna lectura del token tiene respaldo en outputs/?

    El signo "%" del token decide en qué espacio se compara. Esto es
    deliberado: la versión anterior comparaba TODO número contra el corpus
    en las tres escalas a la vez (v, v/100, v*100) con la misma tolerancia
    de redondeo, y con cientos de floats entre 0 y 1 eso equivale a aceptar
    cualquier porcentaje que caiga a menos de un punto porcentual de
    cualquier valor del corpus. El control se aflojaba al crecer la base de
    datos — la dirección exacta en la que un verificador no puede fallar."""
    if es_porcentaje:
        return any(_respalda_porcentaje(v, permitidos, permitidos_pct, tolerancia)
                   for v in valores)
    return any(_respalda_directo(v, permitidos, tolerancia) for v in valores)


def _respalda_directo(valor, permitidos, tolerancia):
    """Un número sin "%" se compara solo contra sí mismo, con la tolerancia
    de redondeo. Sin reescalados: si el informe escribe 0,1451 el corpus
    tiene que tener 0,1451, no 14,51."""
    return any(abs(valor - p) <= tolerancia for p in permitidos)


def _respalda_porcentaje(valor, permitidos, permitidos_pct, tolerancia):
    """Un porcentaje del informe tiene respaldo por una de dos vías, ambas
    estrechas a propósito:

    (a) Coincide, dentro de la tolerancia de redondeo, con un campo cuyo
        NOMBRE declara unidades de porcentaje (pct_*, *porcentaje*). Ahí el
        reescalado no es una suposición del script: lo declaró quien midió.

    (b) Coincide EXACTAMENTE con una fracción del corpus multiplicada por
        100, sin margen de redondeo. Cubre el caso legítimo de citar como
        porcentaje un valor almacenado como fracción, y solo ese: 0.8816
        × 100 = 88.16, que no es 88, así que el AUC del nivel 1 deja de
        "respaldar" el umbral de 88% TPR."""
    if any(abs(valor - p) <= tolerancia for p in permitidos_pct):
        return True
    if any(abs(valor - p * 100) <= EXACTO for p in permitidos):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--borrador", required=True)
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tolerancia", type=float, default=0.01)
    args = ap.parse_args()

    with open(args.borrador, encoding="utf-8") as f:
        texto = f.read()

    archivos_fuera = []
    valores_permitidos, valores_pct = cargar_valores_permitidos(args.outputs_dir, archivos_fuera)
    encontrados = extraer_numeros_del_borrador(texto)

    sin_respaldo = []
    excluidos_metodo = []
    con_respaldo = 0
    for valores, crudo, contexto, linea in encontrados:
        if any(ig in contexto for ig in IGNORAR_CONTEXTOS):
            continue

        es_porcentaje = crudo.endswith("%")

        # Parámetro del método, no cifra medida: sale del conteo por lista
        # declarada y se reporta aparte (ver PORCENTAJES_DE_METODO).
        if es_porcentaje:
            motivo = next((m for v, m in PORCENTAJES_DE_METODO.items()
                           if any(abs(x - v) <= EXACTO for x in valores)), None)
            if motivo:
                excluidos_metodo.append({"valor": crudo, "motivo": motivo,
                                         "contexto": contexto, "linea_aprox": linea})
                continue

        if tiene_respaldo(valores, es_porcentaje, valores_permitidos,
                          valores_pct, args.tolerancia):
            con_respaldo += 1
        else:
            sin_respaldo.append({"valor": crudo, "contexto": contexto, "linea_aprox": linea})

    resultado = {
        "numeros_en_borrador": len(encontrados),
        "numeros_con_respaldo_en_outputs": con_respaldo,
        "numeros_sin_respaldo": sin_respaldo,
        "porcentajes_de_metodo_excluidos": excluidos_metodo,
        "tolerancia_redondeo": args.tolerancia,
        "archivos_fuera_del_corpus": archivos_fuera,
        "campos_declarados_como_porcentaje_en_outputs": len(valores_pct),
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    lineas = []
    lineas.append(f"# Verificación de trazabilidad — {args.borrador}")
    lineas.append(f"Números encontrados en el borrador: {len(encontrados)}")
    lineas.append(f"Con respaldo exacto en outputs/ (tolerancia {args.tolerancia}): {con_respaldo}")
    lineas.append(f"SIN respaldo — revisar uno por uno: {len(sin_respaldo)}")
    for s in sin_respaldo[:10]:
        lineas.append(f"  - línea ~{s['linea_aprox']}: \"{s['valor']}\" en «...{s['contexto']}...»")
    if len(sin_respaldo) > 10:
        lineas.append(f"  ... y {len(sin_respaldo) - 10} más — detalle en el .json")
    lineas.append(
        f"Porcentajes que son parámetros del método, excluidos por lista "
        f"declarada (no se les busca respaldo): {len(excluidos_metodo)}"
    )
    lineas.append(
        f"Archivos de outputs/ en los que no se busca respaldo, por lista declarada: "
        f"{len(archivos_fuera)} {[a['archivo'] for a in archivos_fuera]}"
    )
    lineas.append(
        "Nota: este script señala, no decide. Un número sin respaldo puede ser "
        "legítimo (ej. un conteo estructural obvio) — revisar cada uno a mano."
    )

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

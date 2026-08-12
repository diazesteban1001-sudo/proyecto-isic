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


def extraer_valores_numericos(obj, acumulador):
    """Recorre recursivamente un dict/list de JSON y junta todos los
    números que encuentre, como floats."""
    if isinstance(obj, dict):
        for v in obj.values():
            extraer_valores_numericos(v, acumulador)
    elif isinstance(obj, list):
        for v in obj:
            extraer_valores_numericos(v, acumulador)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        acumulador.add(float(obj))


def cargar_valores_permitidos(outputs_dir):
    valores = set()
    for path in glob.glob(os.path.join(outputs_dir, "*.json")):
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        extraer_valores_numericos(data, valores)
    return valores


def es_parte_de_identificador(texto, ini, fin):
    """Un número pegado a letras no es una cifra citada: es parte de un
    identificador (PMC11324883, SLICE-3D, 133px). Y [T18]/[E3] son marcas
    del anexo de trazabilidad, no cifras del informe."""
    antes = texto[ini - 1] if ini > 0 else ""
    despues = texto[fin] if fin < len(texto) else ""
    if antes.isalpha() or despues.isalpha():
        return True
    if texto[max(0, ini - 2) : ini] in ("[T", "[E") and despues == "]":
        return True
    return False


def extraer_numeros_del_borrador(texto):
    encontrados = []
    for match in NUM_PATTERN.finditer(texto):
        crudo = match.group()
        if es_parte_de_identificador(texto, match.start(), match.end()):
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


def tiene_respaldo(valores, valores_permitidos, tolerancia):
    return any(_respalda(v, valores_permitidos, tolerancia) for v in valores)


def _respalda(valor, valores_permitidos, tolerancia):
    for permitido in valores_permitidos:
        if abs(valor - permitido) <= tolerancia:
            return True
        # también compara como porcentaje (0.098 vs 9.8, por ejemplo)
        if abs(valor / 100 - permitido) <= tolerancia:
            return True
        if abs(valor - permitido * 100) <= tolerancia:
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

    valores_permitidos = cargar_valores_permitidos(args.outputs_dir)
    encontrados = extraer_numeros_del_borrador(texto)

    sin_respaldo = []
    con_respaldo = 0
    for valores, crudo, contexto, linea in encontrados:
        if any(ig in contexto for ig in IGNORAR_CONTEXTOS):
            continue
        if tiene_respaldo(valores, valores_permitidos, args.tolerancia):
            con_respaldo += 1
        else:
            sin_respaldo.append({"valor": crudo, "contexto": contexto, "linea_aprox": linea})

    resultado = {
        "numeros_en_borrador": len(encontrados),
        "numeros_con_respaldo_en_outputs": con_respaldo,
        "numeros_sin_respaldo": sin_respaldo,
        "tolerancia_redondeo": args.tolerancia,
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
        "Nota: este script señala, no decide. Un número sin respaldo puede ser "
        "legítimo (ej. un conteo estructural obvio) — revisar cada uno a mano."
    )

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

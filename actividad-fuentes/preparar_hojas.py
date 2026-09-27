#!/usr/bin/env python3
"""
preparar_hojas.py — hojas de clasificación a ciegas para el experimento de la
actividad «Nada sin fuente» (protocolo-experimento-v1.md, «Las dos pasadas»).

Lee respuestas.csv, una fila por referencia extraída de las respuestas:

    id, tratamiento, orden, referencia, doi, afirmacion

- id: identificador de la referencia. Tiene que ser opaco. Si el tratamiento se
  deduce de él, la hoja deja de ser ciega, y el guion se niega a escribirla
  (ver `ids_delatan_tratamiento`).
- tratamiento: A, B o C.
- orden: posición de la referencia en su respuesta, de 1 a 5.
- referencia: tal como la dio la respuesta.
- doi: el DOI dado; vacío si no dio ninguno.
- afirmacion: la afirmación que la respuesta le atribuye, literal.

Con --pasada N escribe pasada-N.csv: las mismas filas, mezcladas con la semilla
N, sin la columna de tratamiento y con las columnas de clasificación vacías. La
llave id -> tratamiento va a llave.csv. La hoja de la pasada 2 sale solo de
respuestas.csv: este guion nunca lee pasada-1.csv.

Se niega a sobrescribir una hoja que ya existe. Si llave.csv ya existe y no
coincide con la que sale de respuestas.csv, también se niega: quiere decir que
respuestas.csv cambió entre una pasada y otra.

Uso:
    python actividad-fuentes/preparar_hojas.py --pasada 1
    python actividad-fuentes/preparar_hojas.py --pasada 2
Opción --dir: carpeta de respuestas.csv y de las hojas. Por defecto, la de este
guion.
"""

import argparse
import csv
import io
import os
import random
import sys

COLUMNAS_RESPUESTAS = ["id", "tratamiento", "orden", "referencia", "doi", "afirmacion"]
COLUMNAS_CLASIFICACION = ["categoria", "ubicacion", "solo_resumen", "doi_erroneo", "nota"]
COLUMNAS_HOJA = [c for c in COLUMNAS_RESPUESTAS if c != "tratamiento"] + COLUMNAS_CLASIFICACION
TRATAMIENTOS = ("A", "B", "C")
PEDIDAS = 5


class Rechazo(Exception):
    """Un motivo para no escribir nada."""


def leer_csv(ruta):
    """Filas como diccionarios. Acepta coma o punto y coma como separador, que
    es lo que guarda una hoja de cálculo con configuración regional en español,
    y un BOM al principio."""
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        texto = f.read()
    cabecera = texto.split("\n", 1)[0]
    separador = ";" if cabecera.count(";") > cabecera.count(",") else ","
    lector = csv.DictReader(io.StringIO(texto, newline=""), delimiter=separador)
    return lector.fieldnames or [], list(lector)


def clave_natural(id_):
    """Los id numéricos se ordenan como números; los demás, como texto."""
    try:
        return (0, int(id_), "")
    except ValueError:
        return (1, 0, id_)


def validar(columnas, filas):
    if sorted(columnas) != sorted(COLUMNAS_RESPUESTAS):
        raise Rechazo(
            f"respuestas.csv tiene que tener exactamente las columnas {COLUMNAS_RESPUESTAS}; "
            f"tiene {columnas}. Una columna de más pasaría a la hoja, y podría delatar el "
            "tratamiento."
        )
    if not filas:
        raise Rechazo("respuestas.csv no tiene filas.")
    vistos, ordenes = set(), set()
    for n, fila in enumerate(filas, start=2):
        id_ = fila["id"].strip()
        if not id_:
            raise Rechazo(f"línea {n}: id vacío.")
        if id_ in vistos:
            raise Rechazo(f"línea {n}: id repetido, {id_!r}.")
        vistos.add(id_)
        if fila["tratamiento"].strip() not in TRATAMIENTOS:
            raise Rechazo(f"línea {n}: tratamiento {fila['tratamiento']!r}; tiene que ser A, B o C.")
        try:
            orden = int(fila["orden"])
        except ValueError:
            raise Rechazo(f"línea {n}: orden {fila['orden']!r} no es un entero.")
        if not 1 <= orden <= PEDIDAS:
            raise Rechazo(f"línea {n}: orden {orden}; el protocolo toma las primeras {PEDIDAS}.")
        clave = (fila["tratamiento"].strip(), orden)
        if clave in ordenes:
            raise Rechazo(f"línea {n}: el tratamiento {clave[0]} ya tiene una referencia con orden {orden}.")
        ordenes.add(clave)
        if not fila["referencia"].strip():
            raise Rechazo(f"línea {n}: referencia vacía.")


def ids_delatan_tratamiento(filas):
    """True si el id deja ver el tratamiento.

    Dos formas, las dos de numerar a mano: que al ordenar los id cada
    tratamiento quede en un solo bloque (1-5 A, 6-10 B, 11-15 C), o que todos
    los id empiecen o terminen con su tratamiento (A1, 3C). Con id al azar, lo
    primero pasa con probabilidad despreciable: con 5, 5 y 5 referencias,
    3! * (5!)^3 / 15!, 1 entre 126.126."""
    trat = {f["id"].strip(): f["tratamiento"].strip() for f in filas}
    if len(set(trat.values())) < 2:
        return False
    secuencia = [trat[i] for i in sorted(trat, key=clave_natural)]
    bloques = 1 + sum(a != b for a, b in zip(secuencia, secuencia[1:]))
    if bloques == len(set(secuencia)):
        return True
    return all(i.upper().startswith(t) or i.upper().endswith(t) for i, t in trat.items())


def mezclar(filas, semilla):
    """Fisher-Yates con random.Random(semilla).random().

    No se usa random.shuffle: Python solo garantiza que random() da la misma
    secuencia con la misma semilla entre versiones, no el algoritmo de shuffle.
    Las filas se ordenan por id antes de mezclar, así que el resultado depende
    del contenido de respuestas.csv y no del orden de sus filas."""
    filas = sorted(filas, key=lambda f: clave_natural(f["id"].strip()))
    rng = random.Random(semilla)
    for i in range(len(filas) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        filas[i], filas[j] = filas[j], filas[i]
    return filas


def texto_csv(columnas, filas):
    buf = io.StringIO(newline="")
    escritor = csv.DictWriter(buf, fieldnames=columnas, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return buf.getvalue()


def preparar(directorio, pasada):
    ruta_respuestas = os.path.join(directorio, "respuestas.csv")
    ruta_hoja = os.path.join(directorio, f"pasada-{pasada}.csv")
    ruta_llave = os.path.join(directorio, "llave.csv")

    if os.path.exists(ruta_hoja):
        raise Rechazo(f"{ruta_hoja} ya existe; no se sobrescribe.")
    if not os.path.exists(ruta_respuestas):
        raise Rechazo(f"no existe {ruta_respuestas}.")

    columnas, filas = leer_csv(ruta_respuestas)
    validar(columnas, filas)
    if ids_delatan_tratamiento(filas):
        raise Rechazo(
            "el tratamiento se deduce de los id: al ordenarlos, cada tratamiento queda en un "
            "solo bloque, o todos los id llevan su tratamiento al principio o al final. La hoja "
            "no sería ciega. Asigna id al azar en respuestas.csv."
        )

    llave = texto_csv(
        ["id", "tratamiento"],
        [{"id": f["id"].strip(), "tratamiento": f["tratamiento"].strip()}
         for f in sorted(filas, key=lambda f: clave_natural(f["id"].strip()))],
    )
    if os.path.exists(ruta_llave):
        # Se compara sin mostrarla: la llave no se abre hasta el análisis.
        with open(ruta_llave, encoding="utf-8-sig", newline="") as f:
            if f.read() != llave:
                raise Rechazo(
                    f"{ruta_llave} ya existe y no coincide con la que sale de respuestas.csv: "
                    "respuestas.csv cambió desde que se escribió la llave."
                )
        escribir_llave = False
    else:
        escribir_llave = True

    hoja = [
        {**{c: f[c] for c in COLUMNAS_HOJA if c in f}, "id": f["id"].strip(),
         **{c: "" for c in COLUMNAS_CLASIFICACION}}
        for f in mezclar(filas, semilla=pasada)
    ]
    # "x": falla si el archivo apareció entre la comprobación de arriba y aquí.
    with open(ruta_hoja, "x", encoding="utf-8-sig", newline="") as f:
        f.write(texto_csv(COLUMNAS_HOJA, hoja))
    if escribir_llave:
        with open(ruta_llave, "x", encoding="utf-8", newline="") as f:
            f.write(llave)
    return len(hoja), escribir_llave


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pasada", type=int, choices=(1, 2), required=True)
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    try:
        n, llave_nueva = preparar(args.dir, args.pasada)
    except Rechazo as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Escrito pasada-{args.pasada}.csv: {n} referencias, semilla {args.pasada}.")
    print("Escrito llave.csv." if llave_nueva else "llave.csv ya existía y coincide; no se tocó.")


if __name__ == "__main__":
    main()

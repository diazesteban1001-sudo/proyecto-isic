#!/usr/bin/env python3
"""
test_referencias_a_celdas.py — control positivo de las referencias a celdas
de un notebook en verificar_trazabilidad.py (REFERENCIA_A_SECCION).

Desde el 2026-10-22, «la celda 24» es numeración de otro documento, como
«sección 4.2» lo es del propio: no se le busca respaldo ni se cuenta. El
«24» de informe/borrador-v2.md, en «las 22 columnas de la celda 24 del
notebook», pasaba por coincidencia con las iteraciones de C3 en
outputs/fase4b-c3-vs-m3limpio.json.

Borrador sintético, con un corpus que tiene el 22 y no el 24:
  A. «la celda 24»: el 24 no se cuenta ni se señala.
  B. «las 22 columnas», junto a esa celda: el 22 sigue buscando respaldo, y lo
     tiene.
  C. Una cifra real, «24 lesiones», sin respaldo: sigue señalada. La regla no
     esconde un 24 que no sea una celda.
  D. «celdas 14», en plural: tampoco se cuenta.
  E. «(sección 4.2)»: sigue sin contarse, como antes.
  F. Los cinco grupos suman el total.

Control positivo: con la expresión anterior, sin «celdas?», A tiene que
fallar: el 24 de la celda queda señalado.

Uso:
    python3 .claude/skills/sintesis-consultoria/scripts/test_referencias_a_celdas.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")
BORRADOR = (
    "# Informe de prueba\n\n"
    "M3 limpio no descarta las 22 columnas de la celda 24 del notebook.\n\n"
    "Las variables de las celdas 14 del notebook no entran.\n\n"
    "Una cifra real sin respaldo: 24 lesiones.\n\n"
    "Lo dice la sección 4.2 del anteproyecto.\n"
)
REGLA_NUEVA = 'r"(secci[oó]n(es)?|§|celdas?)\\s*$"'
REGLA_ANTERIOR = 'r"(secci[oó]n(es)?|§)\\s*$"'


def verificar(script, tmp):
    outputs_dir = os.path.join(tmp, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, "modelado-baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"columnas_de_la_celda": 22}, f)
    borrador = os.path.join(tmp, "borrador.md")
    with open(borrador, "w", encoding="utf-8") as f:
        f.write(BORRADOR)
    salida = os.path.join(tmp, "verificacion")
    r = subprocess.run([sys.executable, script, "--borrador", borrador, "--outputs-dir", outputs_dir,
                        "--out", salida], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"el verificador no corrió: {r.stderr.strip().splitlines()[-1:]}")
    with open(f"{salida}.json", encoding="utf-8") as f:
        return json.load(f)


def lineas_senaladas(r):
    return [(s["valor"].rstrip(".,"), s["linea_aprox"]) for s in r["numeros_sin_respaldo"]]


def main():
    with open(VERIFICADOR, encoding="utf-8") as f:
        codigo = f.read()
    if codigo.count(REGLA_NUEVA) != 1:
        print("[FALLA] el verificador no tiene la expresión con «celdas?»")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        r = verificar(VERIFICADOR, tmp)
    with tempfile.TemporaryDirectory() as tmp:
        mutante = os.path.join(tmp, "verificar_mutante.py")
        with open(mutante, "w", encoding="utf-8") as f:
            f.write(codigo.replace(REGLA_NUEVA, REGLA_ANTERIOR))
        r_mut = verificar(mutante, tmp)

    senaladas = lineas_senaladas(r)
    contados = r["numeros_en_borrador"]
    suma = (r["numeros_con_respaldo_en_outputs"] + len(r["numeros_sin_respaldo"])
            + len(r["porcentajes_de_metodo_excluidos"]) + len(r["numeros_en_contextos_omitidos"])
            + len(r["numeros_en_comentarios"]))
    casos = [
        ("A. el 24 de «la celda 24» no se cuenta ni se señala", ("24", 3) not in senaladas,
         f"señalados: {senaladas}"),
        ("B. el 22 de «las 22 columnas» sigue buscando respaldo, y lo tiene",
         r["numeros_con_respaldo_en_outputs"] == 1 and ("22", 3) not in senaladas,
         f"con respaldo: {r['numeros_con_respaldo_en_outputs']}"),
        ("C. un 24 real, «24 lesiones», sigue señalado", ("24", 7) in senaladas, f"señalados: {senaladas}"),
        ("D. «celdas 14» tampoco se cuenta", ("14", 5) not in senaladas, f"señalados: {senaladas}"),
        ("E. «sección 4.2» sigue sin contarse", all(v not in ("4.2", "4,2") for v, _ in senaladas),
         f"señalados: {senaladas}"),
        ("F. los cinco grupos suman el total, que es 2: el 22 y el 24 real", suma == contados == 2,
         f"{suma} frente a {contados}"),
        ("control positivo: con la expresión anterior, el 24 de la celda queda señalado (debe fallar A)",
         ("24", 3) in lineas_senaladas(r_mut), f"señalados del mutante: {lineas_senaladas(r_mut)}"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

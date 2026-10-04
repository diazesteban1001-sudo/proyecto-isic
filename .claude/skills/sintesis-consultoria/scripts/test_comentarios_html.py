#!/usr/bin/env python3
"""
test_comentarios_html.py — control positivo de los números dentro de
comentarios HTML (<!-- … -->) en verificar_trazabilidad.py.

Los comentarios <!-- F: … --> del borrador son trazabilidad, no
afirmaciones: dicen de dónde sale una frase. Hasta el 2026-10-04 el
verificador buscaba respaldo también para sus números, y el resultado eran
señales que nadie tiene que revisar (el 59 y el 495 de dos números de línea)
y respaldos por coincidencia (el 31, el 33 y el 55, otros números de línea).
Desde entonces no se les busca respaldo, pero se cuentan y se listan aparte,
en numeros_en_comentarios, como los omitidos por su contexto.

Borrador sintético, con un comentario de una línea y otro de varias:
  - 0,1234, fuera de comentario y presente en outputs/: con respaldo.
  - 0,5555, fuera de comentario y en ningún archivo: señalado.
  - 0,7777, dentro de un comentario y en ningún archivo: tiene que ir a
    numeros_en_comentarios, no a los señalados.
  - 31 y 33, números de línea dentro de un comentario, con un 31 en
    outputs/: tienen que ir a numeros_en_comentarios, no a los respaldados.
  - 0,8888, dentro de un comentario de varias líneas: también.
Los cinco grupos tienen que sumar el total, y el .md tiene que dar el
conteo y el detalle de los números en comentarios.

Contra el verificador anterior al cambio, el caso tiene que fallar. Contra
un mutante que no registra los números en comentarios, la comprobación de la
suma tiene que detenerlo.

Uso:
    python3 .claude/skills/sintesis-consultoria/scripts/test_comentarios_html.py [--verificador RUTA]
Devuelve 0 si los casos se comportan como se espera.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")
BORRADOR = (
    "# Informe de prueba\n\n"
    "El modelo da 0,1234.\n"
    "<!-- F: outputs/x.json > campo; «Método», líneas 31–33; y 0,7777 -->\n\n"
    "Una cifra sin respaldo: 0,5555.\n"
    "<!-- F: un comentario\n"
    "     de varias líneas con 0,8888 -->\n"
)
REGISTRO = "comentarios.append({\"valor\": crudo, \"contexto\": contexto, \"linea_aprox\": linea})"


def verificar(script, tmp):
    outputs_dir = os.path.join(tmp, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, "modelado-baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"pauc_media": 0.1234, "un_recuento": 31}, f)
    borrador = os.path.join(tmp, "borrador.md")
    with open(borrador, "w", encoding="utf-8") as f:
        f.write(BORRADOR)
    salida = os.path.join(tmp, "verificacion")
    r = subprocess.run([sys.executable, script, "--borrador", borrador, "--outputs-dir", outputs_dir,
                        "--out", salida], capture_output=True, text=True)
    if r.returncode != 0:
        return None, None, (r.stderr.strip().splitlines() or [""])[-1]
    with open(f"{salida}.json", encoding="utf-8") as f:
        resultado = json.load(f)
    with open(f"{salida}.md", encoding="utf-8") as f:
        md = f.read()
    return resultado, md, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificador", default=VERIFICADOR)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        r, md, err = verificar(args.verificador, tmp)
    with tempfile.TemporaryDirectory() as tmp:
        with open(args.verificador, encoding="utf-8") as f:
            codigo = f.read()
        mutante = os.path.join(tmp, "verificar_mutante.py")
        with open(mutante, "w", encoding="utf-8") as f:
            f.write(codigo.replace(REGISTRO, "pass"))
        r_mut, _, err_mut = verificar(mutante, tmp)
        mutante_distinto = REGISTRO in codigo

    if r is None:
        print(f"[FALLA] el verificador no corrió: {err}")
        return 1
    comentarios = r.get("numeros_en_comentarios")
    en_comentarios = [c["valor"].rstrip(".,") for c in comentarios or []]
    senalados = [s["valor"].rstrip(".,") for s in r["numeros_sin_respaldo"]]
    suma = (r["numeros_con_respaldo_en_outputs"] + len(r["numeros_sin_respaldo"])
            + len(r["porcentajes_de_metodo_excluidos"]) + len(r["numeros_en_contextos_omitidos"])
            + len(comentarios or []))
    siete = next((c for c in comentarios or [] if c["valor"].rstrip(".,") == "0,7777"), None)

    casos = [
        ("0,7777, dentro de un comentario, va a numeros_en_comentarios con su línea, no a los señalados",
         siete is not None and siete["linea_aprox"] == 4 and "0,7777" not in senalados,
         f"en comentarios: {en_comentarios}; señalados: {senalados}"),
        ("31 y 33, números de línea en un comentario, no se respaldan por coincidencia con el 31 de outputs/",
         "31" in en_comentarios and "33" in en_comentarios and r["numeros_con_respaldo_en_outputs"] == 1,
         f"en comentarios: {en_comentarios}; con respaldo: {r['numeros_con_respaldo_en_outputs']}"),
        ("0,8888, en un comentario de varias líneas, también",
         "0,8888" in en_comentarios, f"en comentarios: {en_comentarios}"),
        ("fuera de los comentarios no cambia nada: 0,1234 con respaldo, 0,5555 señalado",
         senalados == ["0,5555"], f"señalados: {senalados}"),
        ("los cinco grupos suman el total",
         suma == r["numeros_en_borrador"], f"{suma} frente a {r['numeros_en_borrador']}"),
        ("el .md da el conteo y el detalle de los números en comentarios",
         "comentarios HTML" in md and "0,7777" in md, md.splitlines()[3:9]),
        ("el caso discrimina: el mutante que no registra los números en comentarios se detiene en la suma",
         mutante_distinto and r_mut is None and "suman" in err_mut,
         f"mutante: {err_mut or 'corrió sin error'}" if mutante_distinto else "el código no tiene el registro"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

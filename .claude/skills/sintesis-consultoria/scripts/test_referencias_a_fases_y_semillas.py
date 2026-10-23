#!/usr/bin/env python3
"""
test_referencias_a_fases_y_semillas.py — control positivo de las referencias a
fases y semillas en verificar_trazabilidad.py (REFERENCIA_A_SECCION).

Desde el 2026-10-23, «la Fase 4» y «la semilla 0» son etiquetas, como «sección
4.2» o «la celda 24»: no se les busca respaldo ni se cuentan. El «4» de «las
fases 4 y 4b» y el «0» de «la semilla 0», en informe/borrador-v2.md, pasaban por
coincidencia con cualquier 4 y cualquier 0 de outputs/.

Borrador sintético, con un corpus que solo tiene el 10:
  A. «la Fase 4»: el 4 no se cuenta ni se señala.
  B. «las fases 4 y 4b»: tampoco el 4.
  C. «la semilla 0»: tampoco el 0.
  D. «las 10 semillas»: el número va antes de la palabra, así que el 10 sigue
     buscando respaldo, y lo tiene.
  E. «7 fases»: lo mismo, y el 7, sin respaldo, sigue señalado.
  F. Una cifra real sin respaldo, «4 lesiones»: sigue señalada. La regla no
     esconde un 4 que no sea una fase.
  G. «la interfase 3»: «fase» dentro de otra palabra no cuenta, y el 3 sigue
     señalado.
  H. «(sección 4.2)»: sigue sin contarse, como antes.
  I. Los cinco grupos suman el total, que es 4: el 10, el 7, el 4 y el 3.

Control positivo: con la expresión anterior, sin «fases?» ni «semillas?», A y C
tienen que fallar: el 4 de la fase y el 0 de la semilla quedan señalados.

Uso:
    python3 .claude/skills/sintesis-consultoria/scripts/test_referencias_a_fases_y_semillas.py
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
    "Lo fijó la Fase 4, antes de correr.\n\n"
    "Después vinieron las fases 4 y 4b del plan.\n\n"
    "En la semilla 0, la versión estricta dio más.\n\n"
    "Queda por encima en las 10 semillas.\n\n"
    "El método tiene 7 fases.\n\n"
    "Una cifra real sin respaldo: 4 lesiones.\n\n"
    "En la interfase 3 no cambia.\n\n"
    "Lo dice la sección 4.2 del anteproyecto.\n"
)
REGLA_NUEVA = 'r"(secci[oó]n(es)?|§|celdas?|\\bfases?|\\bsemillas?)\\s*$"'
REGLA_ANTERIOR = 'r"(secci[oó]n(es)?|§|celdas?)\\s*$"'


def verificar(script, tmp):
    outputs_dir = os.path.join(tmp, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, "modelado-baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"de_semillas": 10}, f)
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


def senalados(r):
    return [(s["valor"].rstrip(".,"), s["linea_aprox"]) for s in r["numeros_sin_respaldo"]]


def main():
    with open(VERIFICADOR, encoding="utf-8") as f:
        codigo = f.read()
    if codigo.count(REGLA_NUEVA) != 1:
        print("[FALLA] el verificador no tiene la expresión con «fases?» y «semillas?»")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        r = verificar(VERIFICADOR, tmp)
    with tempfile.TemporaryDirectory() as tmp:
        mutante = os.path.join(tmp, "verificar_mutante.py")
        with open(mutante, "w", encoding="utf-8") as f:
            f.write(codigo.replace(REGLA_NUEVA, REGLA_ANTERIOR))
        r_mut = verificar(mutante, tmp)

    s, s_mut = senalados(r), senalados(r_mut)
    suma = (r["numeros_con_respaldo_en_outputs"] + len(r["numeros_sin_respaldo"])
            + len(r["porcentajes_de_metodo_excluidos"]) + len(r["numeros_en_contextos_omitidos"])
            + len(r["numeros_en_comentarios"]))
    casos = [
        ("A. el 4 de «la Fase 4» no se cuenta ni se señala", ("4", 3) not in s, f"señalados: {s}"),
        ("B. el 4 de «las fases 4 y 4b» tampoco", ("4", 5) not in s, f"señalados: {s}"),
        ("C. el 0 de «la semilla 0» tampoco", ("0", 7) not in s, f"señalados: {s}"),
        ("D. el 10 de «las 10 semillas» sigue buscando respaldo, y lo tiene",
         r["numeros_con_respaldo_en_outputs"] == 1 and ("10", 9) not in s,
         f"con respaldo: {r['numeros_con_respaldo_en_outputs']}"),
        ("E. el 7 de «7 fases» sigue buscando respaldo, y sin él queda señalado", ("7", 11) in s, f"señalados: {s}"),
        ("F. un 4 real, «4 lesiones», sigue señalado", ("4", 13) in s, f"señalados: {s}"),
        ("G. «la interfase 3»: el 3 sigue señalado", ("3", 15) in s, f"señalados: {s}"),
        ("H. «sección 4.2» sigue sin contarse", all(v not in ("4.2", "4,2") for v, _ in s), f"señalados: {s}"),
        ("I. los cinco grupos suman el total, que es 4", suma == r["numeros_en_borrador"] == 4,
         f"{suma} frente a {r['numeros_en_borrador']}"),
        ("control positivo: con la expresión anterior, el 4 de la fase queda señalado (debe fallar A)",
         ("4", 3) in s_mut, f"señalados del mutante: {s_mut}"),
        ("control positivo: con la expresión anterior, el 0 de la semilla queda señalado (debe fallar C)",
         ("0", 7) in s_mut, f"señalados del mutante: {s_mut}"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

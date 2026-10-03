#!/usr/bin/env python3
"""
test_contextos_omitidos.py — control positivo de los números que
verificar_trazabilidad.py omite por su contexto (IGNORAR_CONTEXTOS).

Hasta el 2026-10-02 el verificador los saltaba con un `continue` sin
registrarlos, aunque su comentario decía que se listaban aparte: sobre
informe/borrador-v2.md faltaban 48 de 352. Una cifra con «Nivel 1» o «2026»
en su contexto no se revisaba nunca, y nada lo mostraba. Se fuerza el caso con
un borrador sintético de cinco números, uno por grupo y uno más en la etiqueta:

  - «Nivel 1: pAUC 0,9999»: 0,9999 tiene que aparecer en la lista de
    omitidos, con su contexto y su línea, no desaparecer; y el «1» de la
    etiqueta, también.
  - 0,1234, presente en outputs/: con respaldo.
  - 0,5555, en ningún archivo: señalado.
  - «al 95%»: porcentaje del método.

Los cuatro grupos tienen que sumar el total, y el .md tiene que dar el conteo
y el detalle de los omitidos. El caso discrimina: sobre un mutante del
verificador que vuelve al `continue` sin registrar, la comprobación de la
suma tiene que detenerlo.

Uso:
    python3 .claude/skills/sintesis-consultoria/scripts/test_contextos_omitidos.py
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
    "Nivel 1: pAUC 0,9999 en la tabla.\n\n"
    "El modelo da 0,1234.\n\n"
    "Una cifra sin respaldo: 0,5555.\n\n"
    "El intervalo es al 95%.\n"
)
REGISTRO = "omitidos.append({\"valor\": crudo, \"contexto\": contexto, \"linea_aprox\": linea})"


def verificar(script, tmp):
    outputs_dir = os.path.join(tmp, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, "modelado-baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"pauc_media": 0.1234}, f)
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
    with tempfile.TemporaryDirectory() as tmp:
        r, md, err = verificar(VERIFICADOR, tmp)
    with tempfile.TemporaryDirectory() as tmp:
        with open(VERIFICADOR, encoding="utf-8") as f:
            codigo = f.read()
        mutante = os.path.join(tmp, "verificar_mutante.py")
        with open(mutante, "w", encoding="utf-8") as f:
            f.write(codigo.replace(REGISTRO, "pass"))
        r_mut, _, err_mut = verificar(mutante, tmp)

    if r is None:
        print(f"[FALLA] el verificador no corrió: {err}")
        return 1
    omitidos = r.get("numeros_en_contextos_omitidos")
    valores_omitidos = [o["valor"].rstrip(".,") for o in omitidos or []]
    senalados = [s["valor"].rstrip(".,") for s in r["numeros_sin_respaldo"]]
    suma = (r["numeros_con_respaldo_en_outputs"] + len(r["numeros_sin_respaldo"])
            + len(r["porcentajes_de_metodo_excluidos"]) + len(omitidos or []))
    nueve = next((o for o in omitidos or [] if o["valor"].rstrip(".,") == "0,9999"), None)

    casos = [
        ("0,9999, con «Nivel 1» en su contexto, aparece en la lista de omitidos",
         nueve is not None and "Nivel 1" in nueve["contexto"] and nueve["linea_aprox"] == 3,
         f"omitidos: {omitidos}"),
        ("el «1» de la etiqueta también se registra",
         "1" in valores_omitidos, f"omitidos: {valores_omitidos}"),
        ("los demás grupos no cambian: 0,1234 con respaldo, 0,5555 señalado, 95% del método",
         r["numeros_con_respaldo_en_outputs"] == 1 and senalados == ["0,5555"]
         and len(r["porcentajes_de_metodo_excluidos"]) == 1,
         f"con respaldo: {r['numeros_con_respaldo_en_outputs']}; señalados: {senalados}; "
         f"método: {len(r['porcentajes_de_metodo_excluidos'])}"),
        ("los cuatro grupos suman el total",
         suma == r["numeros_en_borrador"], f"{suma} frente a {r['numeros_en_borrador']}"),
        ("el .md da el conteo y el detalle de los omitidos, y no dice «respaldo exacto»",
         "Omitidos por su contexto" in md and "0,9999" in md and "respaldo exacto" not in md,
         md.splitlines()[3:7]),
        ("el caso discrimina: el mutante que no registra los omitidos se detiene en la suma",
         r_mut is None and "suman" in err_mut, f"mutante: {err_mut or 'corrió sin error'}"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

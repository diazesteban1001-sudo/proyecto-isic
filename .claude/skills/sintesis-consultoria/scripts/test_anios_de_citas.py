#!/usr/bin/env python3
"""
test_anios_de_citas.py — los años de las citas bibliográficas se omiten por su
contexto en verificar_trazabilidad.py, listados con su motivo, como los años de
IGNORAR_CONTEXTOS (decisión de la persona del 2026-11-04). Borrador sintético:

  - Se omiten, con el motivo «año de una cita bibliográfica»: «Marchetti et al.
    (2023)», «Nadeau y Bengio (2003)», «Barrera-Valencia y Perea-Flórez (2019)»,
    «(Kurtansky et al.,\\n2025)», con salto de línea, y «(Novoselskiy, 2017)».
  - Siguen contando, porque no son el año de una cita: «agosto de 2025», «1200
    pacientes», «un total de (2023) casos», sin autor delante, y «2022
    lesiones».

Casos que deben fallar: los números de cuatro cifras que no son años de cita
siguen contando; y con un verificador mutante sin la regla, los años de cita se
cuentan y se señalan. Los grupos suman el total en los dos.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/test_anios_de_citas.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")
BORRADOR = (
    "# Prueba\n\n"
    "Antes del reto, Marchetti et al. (2023) estudiaron el triaje.\n\n"
    "Con la corrección de Nadeau y Bengio (2003) se corrige la varianza.\n\n"
    "Barrera-Valencia y Perea-Flórez (2019) compararon costos.\n\n"
    "Los organizadores publicaron su análisis (Kurtansky et al.,\n2025). Con él se compara.\n\n"
    "El código es público (Novoselskiy, 2017).\n\n"
    "Su artículo es de agosto de 2025, y no da fechas.\n\n"
    "El conjunto de prueba tiene 1200 pacientes.\n\n"
    "Hubo un total de (2023) casos.\n\n"
    "Se revisaron 2022 lesiones.\n"
)
CITAS = {"2023": 3, "2003": 5, "2019": 7, "2025": 10, "2017": 12}
NO_CITAS = {"2025": 14, "1200": 16, "2023": 18, "2022": 20}
REGLA = "    if es_anio_de_cita(texto, ini):"
SIN_REGLA = "    if False:"


def verificar(script, tmp):
    outputs = os.path.join(tmp, "outputs")
    os.makedirs(outputs, exist_ok=True)
    with open(os.path.join(outputs, "modelado-baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"pauc_media": 0.1234}, f)
    borrador = os.path.join(tmp, "borrador.md")
    with open(borrador, "w", encoding="utf-8") as f:
        f.write(BORRADOR)
    salida = os.path.join(tmp, "verificacion")
    entorno = dict(os.environ, PYTHONPATH=os.pathsep.join(
        x for x in (os.path.dirname(VERIFICADOR), os.environ.get("PYTHONPATH")) if x))
    r = subprocess.run([sys.executable, script, "--borrador", borrador, "--outputs-dir", outputs, "--out", salida],
                       capture_output=True, text=True, env=entorno)
    if r.returncode != 0:
        raise SystemExit(f"el verificador no corrió: {r.stderr.strip().splitlines()[-1:]}")
    with open(salida + ".json", encoding="utf-8") as f:
        return json.load(f)


def main():
    codigo = open(VERIFICADOR, encoding="utf-8").read()
    if codigo.count(REGLA) != 1:
        print("[FALLA] el verificador no tiene la regla de los años de cita")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        r = verificar(VERIFICADOR, tmp)
    with tempfile.TemporaryDirectory() as tmp:
        mutante = os.path.join(tmp, "verificar_mutante.py")
        open(mutante, "w", encoding="utf-8").write(codigo.replace(REGLA, SIN_REGLA))
        r_mut = verificar(mutante, tmp)

    def omitidos_por_cita(res):
        return {(o["valor"].rstrip(".,)"), o["linea_aprox"]) for o in res["numeros_en_contextos_omitidos"]
                if o.get("motivo") == "año de una cita bibliográfica"}

    def senalados(res):
        return {(s["valor"].rstrip(".,)"), s["linea_aprox"]) for s in res["numeros_sin_respaldo"]}

    def suma(res):
        return (res["numeros_con_respaldo_en_outputs"] + len(res["numeros_sin_respaldo"])
                + len(res["porcentajes_de_metodo_excluidos"]) + len(res["numeros_en_contextos_omitidos"])
                + len(res["numeros_en_comentarios"])) == res["numeros_en_borrador"]

    citas = {(v, l) for v, l in CITAS.items()}
    no_citas = {(v, l) for v, l in NO_CITAS.items()}
    casos = [
        ("los cinco años de cita se omiten, con su motivo", omitidos_por_cita(r) == citas,
         f"omitidos por cita: {sorted(omitidos_por_cita(r))}"),
        ("debe fallar: los cuatro números de cuatro cifras que no son años de cita siguen contando",
         no_citas <= senalados(r), f"señalados: {sorted(senalados(r))}"),
        ("los grupos suman el total", suma(r), ""),
        ("debe fallar: sin la regla, los años de cita se cuentan y se señalan",
         not omitidos_por_cita(r_mut) and citas <= senalados(r_mut), f"señalados: {sorted(senalados(r_mut))}"),
        ("sin la regla, los grupos también suman el total", suma(r_mut), ""),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}" + (f"\n      {detalle}" if detalle else ""))
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

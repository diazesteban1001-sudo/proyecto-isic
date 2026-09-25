#!/usr/bin/env python3
"""
test_fuera_del_corpus.py — control positivo de FUERA_DEL_CORPUS en
verificar_trazabilidad.py.

El verificador no debe buscar respaldo en holdout-pacientes.json ni en
sensibilidad-*.json. Se fuerza el caso, por el corolario de la regla 6: un
borrador sintético con tres cifras, cada una presente en un solo archivo de
un outputs/ sintético, en un directorio temporal.

  - 0,1234 solo en modelado-baseline.json: tiene que contar como respaldada.
  - 0,5678 solo en sensibilidad-procedencia.json: NO debe contar.
  - 777 solo en holdout-pacientes.json: NO debe contar.

Y el caso discrimina: con los dos últimos archivos renombrados fuera de la
lista, las tres cuentan como respaldadas. La diferencia la hace la lista y
nada más.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/test_fuera_del_corpus.py
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
    "El modelo principal da 0,1234.\n\n"
    "La corrida con otras columnas da 0,5678.\n\n"
    "Quedan apartados 777 pacientes.\n"
)


def verificar(archivos):
    with tempfile.TemporaryDirectory() as tmp:
        outputs_dir = os.path.join(tmp, "outputs")
        os.makedirs(outputs_dir)
        for nombre, contenido in archivos.items():
            with open(os.path.join(outputs_dir, nombre), "w", encoding="utf-8") as f:
                json.dump(contenido, f)
        borrador = os.path.join(tmp, "borrador.md")
        with open(borrador, "w", encoding="utf-8") as f:
            f.write(BORRADOR)
        salida = os.path.join(tmp, "verificacion")
        subprocess.run([sys.executable, VERIFICADOR, "--borrador", borrador, "--outputs-dir", outputs_dir,
                        "--out", salida, "--tolerancia", "0.01"], check=True, capture_output=True)
        with open(f"{salida}.json", encoding="utf-8") as f:
            return json.load(f)


def main():
    con_lista = verificar({
        "modelado-baseline.json": {"pauc_media": 0.1234},
        "sensibilidad-procedencia.json": {"pauc_media": 0.5678},
        "holdout-pacientes.json": {"recuentos": {"pacientes": 777}},
    })
    renombrados = verificar({
        "modelado-baseline.json": {"pauc_media": 0.1234},
        "otra-corrida.json": {"pauc_media": 0.5678},
        "otros-recuentos.json": {"recuentos": {"pacientes": 777}},
    })
    # El verificador guarda el token tal cual, con la puntuación que lo sigue
    # ("0,5678."). Se normaliza antes de comparar: sin eso, un caso que
    # compruebe que una cifra NO está señalada pasaría siempre.
    def tokens(r):
        return {s["valor"].rstrip(".,") for s in r["numeros_sin_respaldo"]}
    senalados = tokens(con_lista)
    senalados_ren = tokens(renombrados)
    fuera = sorted(a["archivo"] for a in con_lista["archivos_fuera_del_corpus"])

    casos = [
        ("la cifra del archivo principal cuenta como respaldada",
         "0,1234" not in senalados and con_lista["numeros_con_respaldo_en_outputs"] == 1,
         f"señaladas: {sorted(senalados)}; con respaldo: {con_lista['numeros_con_respaldo_en_outputs']}"),
        ("la cifra que solo está en un archivo de sensibilidad NO cuenta",
         "0,5678" in senalados, f"señaladas: {sorted(senalados)}"),
        ("la cifra que solo está en holdout-pacientes.json NO cuenta",
         "777" in senalados, f"señaladas: {sorted(senalados)}"),
        ("los dos archivos quedan registrados fuera del corpus, con su motivo",
         fuera == ["holdout-pacientes.json", "sensibilidad-procedencia.json"]
         and all(a["motivo"] for a in con_lista["archivos_fuera_del_corpus"]),
         f"archivos_fuera_del_corpus: {fuera}"),
        ("el caso discrimina: renombrados fuera de la lista, las tres cuentan",
         not senalados_ren and renombrados["numeros_con_respaldo_en_outputs"] == 3,
         f"señaladas: {sorted(senalados_ren) or 'ninguna'}; con respaldo: {renombrados['numeros_con_respaldo_en_outputs']}"),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

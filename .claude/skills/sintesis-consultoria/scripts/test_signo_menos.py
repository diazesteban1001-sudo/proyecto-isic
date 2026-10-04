#!/usr/bin/env python3
"""
test_signo_menos.py — control del defecto de lectura (b) de
verificar_trazabilidad.py: el signo menos tipográfico (U+2212).

El defecto
----------
NUM_PATTERN solo aceptaba el guion ASCII como signo. El borrador escribe los
negativos con «−» (U+2212), así que «−0,0579» se leía como 0,0579: quedaba
respaldado por un 0.0579 positivo del corpus, y señalado frente al −0.0579 que
de verdad está en outputs/. Registro de incidentes de CLAUDE.md, duodécima
fila, defecto (b).

La regla
--------
«−» es signo si va pegado a un dígito y no lo precede otro dígito. Así:
  - «−0,0579», «[−0,084; −0,0319]» y «(−0,1039)» son negativos;
  - en «M2 − M1» y «2b − 1» el «−» va separado por un espacio: es una resta
    entre nombres, no un signo, y el «1» se lee positivo;
  - «60−64», un rango, se sigue leyendo 60 y 64, como antes.
El guion ASCII no cambia: se sigue leyendo como antes (ver «Rangos», abajo).

Se escribió antes del arreglo y fallaba con el código de entonces, por el
corolario de la regla 6 de CLAUDE.md: un chequeo que no puede fallar no vale
nada.

Casos
-----
  A. corpus {0.0579}: «−0,0579» señalada. Es el defecto: con el código de
     antes, respaldada.
  B. corpus {-0.0579}: «−0,0579» respaldada.
  C. «[−0,084; −0,0319]» da dos cifras, las dos negativas: respaldadas frente a
     {-0.084, -0.0319} y señaladas frente a {0.084, 0.0319}. Todas las lecturas
     de cada cifra tienen que ser negativas: «−0,084» recibe también la lectura
     −84 por el defecto (a), que sigue abierto.
  D. «M2 − M1»: ninguna cifra.
  E. «2b − 1»: una cifra, el 1, positiva.
  F. «60−64»: dos cifras, 60 y 64, positivas.

Informativo, no cuenta para el resultado: cómo se leen los rangos con guion
ASCII y con raya. No cambia con el arreglo.

Uso
---
    .venv/bin/python .claude/skills/sintesis-consultoria/scripts/test_signo_menos.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
VERIFICADOR = os.path.join(AQUI, "verificar_trazabilidad.py")
sys.path.insert(0, AQUI)
import verificar_trazabilidad as vt  # noqa: E402


def verificar(valores, texto):
    """Corre el verificador sobre un borrador con `texto` y un outputs/ con `valores`."""
    with tempfile.TemporaryDirectory() as tmp:
        outputs_dir = os.path.join(tmp, "outputs")
        os.makedirs(outputs_dir)
        with open(os.path.join(outputs_dir, "fase4-sintetica.json"), "w", encoding="utf-8") as f:
            json.dump({"comparaciones_nuevo_menos_base": {"valores": valores}}, f)
        borrador = os.path.join(tmp, "borrador.md")
        with open(borrador, "w", encoding="utf-8") as f:
            f.write(f"# Informe de prueba\n\nLa diferencia es {texto} en la comparación.\n")
        salida = os.path.join(tmp, "verificacion")
        subprocess.run([sys.executable, VERIFICADOR, "--borrador", borrador, "--outputs-dir", outputs_dir,
                        "--out", salida], check=True, capture_output=True)
        with open(f"{salida}.json", encoding="utf-8") as f:
            return json.load(f)


def lecturas(texto):
    """Los valores que el verificador lee en `texto`, una lista por cifra."""
    return [sorted(v for v, _ in valores) for valores, *_ in vt.extraer_numeros_del_borrador(texto)]


def main():
    casos = []

    r = verificar([0.0579], "−0,0579")
    casos.append(("A. corpus {0.0579}: «−0,0579» señalada (el defecto la daba por respaldada)",
                  r["numeros_en_borrador"] == 1 and len(r["numeros_sin_respaldo"]) == 1,
                  f"{r['numeros_en_borrador']} cifras; con respaldo {r['numeros_con_respaldo_en_outputs']}; "
                  f"señaladas {[s['valor'] for s in r['numeros_sin_respaldo']]}"))

    r = verificar([-0.0579], "−0,0579")
    casos.append(("B. corpus {-0.0579}: «−0,0579» respaldada",
                  r["numeros_en_borrador"] == 1 and r["numeros_con_respaldo_en_outputs"] == 1,
                  f"{r['numeros_en_borrador']} cifras; con respaldo {r['numeros_con_respaldo_en_outputs']}; "
                  f"señaladas {[s['valor'] for s in r['numeros_sin_respaldo']]}"))

    leidas = lecturas("intervalo [−0,084; −0,0319].")
    r_neg = verificar([-0.084, -0.0319], "[−0,084; −0,0319]")
    r_pos = verificar([0.084, 0.0319], "[−0,084; −0,0319]")
    casos.append(("C. «[−0,084; −0,0319]»: dos negativas; respaldadas frente a negativos, señaladas frente a positivos",
                  len(leidas) == 2 and all(v < 0 for l in leidas for v in l) and -0.084 in leidas[0]
                  and leidas[1] == [-0.0319] and r_neg["numeros_con_respaldo_en_outputs"] == 2
                  and len(r_pos["numeros_sin_respaldo"]) == 2,
                  f"lecturas {leidas}; frente a negativos: {r_neg['numeros_con_respaldo_en_outputs']} respaldadas; "
                  f"frente a positivos: {len(r_pos['numeros_sin_respaldo'])} señaladas"))

    leidas = lecturas("la comparación M2 − M1 en la pAUC.")
    casos.append(("D. «M2 − M1»: ninguna cifra", leidas == [], f"lecturas {leidas}"))

    leidas = lecturas("la diferencia 2b − 1 en la pAUC.")
    casos.append(("E. «2b − 1»: una cifra, el 1, positiva", leidas == [[1.0]], f"lecturas {leidas}"))

    leidas = lecturas("entre 60−64 años.")
    casos.append(("F. «60−64»: 60 y 64, positivas, como antes del arreglo", leidas == [[60.0], [64.0]],
                  f"lecturas {leidas}"))

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")

    print("\nInformativo, no cuenta para el resultado: rangos con guion ASCII y con raya")
    for texto in ("entre 60-64 años.", "entre 60–64 años.", "de 2015-2024."):
        print(f"  «{texto}» → {lecturas(texto)}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

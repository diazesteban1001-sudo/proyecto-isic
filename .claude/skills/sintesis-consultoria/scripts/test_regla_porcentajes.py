#!/usr/bin/env python3
"""
test_regla_porcentajes.py — control del verificador de trazabilidad.

Por qué existe (regla 5 de CLAUDE.md, corolario): un chequeo que no puede
fallar no vale nada. Este archivo fuerza deliberadamente el caso que
`verificar_trazabilidad.py` debe detectar y comprueba que se dispara.

El defecto que documenta
------------------------
La regla de porcentajes original daba por respaldado un porcentaje del
informe si `abs(valor/100 - permitido) <= tolerancia` contra CUALQUIER
número de `outputs/`. Con la tolerancia por defecto (0.01) eso equivale a
aceptar cualquier coincidencia a menos de UN PUNTO PORCENTUAL de cualquier
float del corpus. Con cientos de valores entre 0 y 1, casi todo porcentaje
encuentra pareja por azar.

Caso real medido el 2026-09-17: al incorporarse `auc_estandar_por_fold` a
`outputs/modelado-baseline.json`, el "88%" del informe —umbral de TPR del
esquema de premios del organizador ISIC, una cifra externa— quedó
respaldado por 0.8816, un AUC del nivel 1. Y el "95%" —nivel de confianza
de un intervalo— por 0.9415, un AUC del nivel 2b. El control se afloja a
medida que crece la base de datos, que es la dirección exacta en la que un
verificador no puede fallar.

Los dos casos
-------------
1. `88_medido`  — reproduce el caso real: "88%" contra un corpus cuyo único
   contenido es 0.8816. Es el que se observó en producción.
2. `73_neutro`  — el mismo mecanismo con un porcentaje que NO está en
   ninguna lista de exclusión del verificador, para aislar la regla
   numérica de cualquier otro filtro: "73%" contra 0.7316.

Uso
---
    python test_regla_porcentajes.py            # los dos casos

Salida y código de retorno:
  - `DEFECTO REPRODUCIDO`: el verificador dio el porcentaje por respaldado.
    Sale con código 0 mientras el defecto siga vivo.
  - `DEFECTO CORREGIDO`: el verificador ya no lo acepta. Sale con código 1.

El código de retorno está invertido a propósito: este archivo es un control
positivo, no una prueba de regresión. Su trabajo es demostrar que el fallo
existe; cuando deja de existir, el control debe romperse. Es la señal de
que la corrección llegó.
"""

import json
import os
import subprocess
import sys
import tempfile

VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "verificar_trazabilidad.py")

CASOS = [
    {
        "nombre": "88_medido",
        "token": "88%",
        "borrador": (
            "# Informe de prueba\n\n"
            "El esquema de premios del organizador ISIC evalua el pAUC por "
            "encima de 88% de sensibilidad.\n"
        ),
        # Un unico campo, sin ninguna relacion con umbrales de TPR: es un AUC.
        "outputs": {"nivel_1_regresion_logistica": {"auc_estandar_por_fold": [0.8816]}},
        "por_que": "0.8816 es un AUC del nivel 1; el 88% es un umbral de TPR externo",
    },
    {
        "nombre": "73_neutro",
        "token": "73%",
        "borrador": (
            "# Informe de prueba\n\n"
            "Un 73% de las lesiones quedaria en el grupo de interes.\n"
        ),
        "outputs": {"campo_sin_relacion": {"valor_cualquiera": [0.7316]}},
        "por_que": "0.7316 no es un porcentaje ni tiene nombre que lo declare",
    },
]


def correr_caso(caso):
    """Corre el verificador sobre un corpus sintetico y devuelve si el
    porcentaje quedo contado como respaldado por outputs/."""
    with tempfile.TemporaryDirectory() as tmp:
        outputs_dir = os.path.join(tmp, "outputs")
        os.makedirs(outputs_dir)
        with open(os.path.join(outputs_dir, "sintetico.json"), "w", encoding="utf-8") as f:
            json.dump(caso["outputs"], f)

        borrador = os.path.join(tmp, "borrador.md")
        with open(borrador, "w", encoding="utf-8") as f:
            f.write(caso["borrador"])

        salida = os.path.join(tmp, "verificacion")
        subprocess.run(
            [sys.executable, VERIFICADOR,
             "--borrador", borrador,
             "--outputs-dir", outputs_dir,
             "--out", salida,
             "--tolerancia", "0.01"],
            check=True, capture_output=True,
        )
        with open(f"{salida}.json", encoding="utf-8") as f:
            resultado = json.load(f)

    senalados = {s["valor"] for s in resultado["numeros_sin_respaldo"]}
    # Un porcentaje declarado como parametro del metodo no es un respaldo
    # numerico: se excluye por lista y se reporta aparte. Cuenta como "no
    # aceptado por coincidencia", que es lo que este control mide.
    excluidos = {e["valor"] for e in resultado.get("porcentajes_de_metodo_excluidos", [])}
    token = caso["token"]
    aceptado_por_coincidencia = token not in senalados and token not in excluidos
    return aceptado_por_coincidencia, resultado


def main():
    print("Control positivo de la regla de porcentajes")
    print(f"Verificador: {VERIFICADOR}\n")

    defecto_vivo = False
    for caso in CASOS:
        aceptado, resultado = correr_caso(caso)
        estado = "DEFECTO REPRODUCIDO" if aceptado else "DEFECTO CORREGIDO"
        print(f"[{caso['nombre']}] {estado}")
        print(f"    informe dice        : {caso['token']}")
        print(f"    outputs solo tiene  : {caso['por_que']}")
        print(f"    el verificador lo da por respaldado: {aceptado}")
        print(f"    conteo              : {resultado['numeros_con_respaldo_en_outputs']} "
              f"con respaldo, {len(resultado['numeros_sin_respaldo'])} senalados")
        print()
        defecto_vivo = defecto_vivo or aceptado

    if defecto_vivo:
        print("RESULTADO: el defecto sigue vivo. El control positivo PASA "
              "(codigo 0), que es lo que debe hacer mientras no se corrija.")
        return 0
    print("RESULTADO: el verificador ya no acepta esas coincidencias. El "
          "control positivo FALLA (codigo 1) a proposito: es la senal de que "
          "la correccion llego.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

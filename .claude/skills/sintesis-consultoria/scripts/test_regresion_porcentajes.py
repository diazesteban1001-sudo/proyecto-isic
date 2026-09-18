#!/usr/bin/env python3
"""
test_regresion_porcentajes.py — prueba de regresión de la regla de
porcentajes de `verificar_trazabilidad.py`.

De dónde sale este archivo
--------------------------
Nació el 2026-09-17 como **control positivo**, no como prueba: se escribió
para reproducir un defecto real que estaba vivo ese día, y su código de
retorno estaba invertido a propósito —pasaba mientras el defecto
existiera— porque su trabajo era demostrar el fallo, no protegerse de él.
Es la aplicación literal del corolario de la regla 6 de CLAUDE.md: un
chequeo que no puede fallar no vale nada, así que antes de escribir el
arreglo hay que forzar el caso que debería detectarse y confirmar que se
dispara.

Cumplió esa función. Con la regla floja los dos casos quedaban
respaldados; con la regla corregida, ninguno. Cerrado el defecto, el
control positivo ya no tiene nada que demostrar y se invierte: pasa a ser
lo que su nombre dice, una prueba de regresión que **falla si la regla
floja vuelve**.

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
Se conservan los dos porque comprueban mecanismos distintos, y basta con
que uno se rompa para que el defecto esté de vuelta.

1. `88_medido`  — reproduce el caso real: "88%" contra un corpus cuyo único
   contenido es 0.8816. Es el que se observó en producción. Hoy queda fuera
   por la lista declarada `PORCENTAJES_DE_METODO`, que es una forma válida
   de no estar respaldado: el informe no lo afirma como medición propia.
2. `73_neutro`  — el mismo mecanismo con un porcentaje que NO está en
   ninguna lista de exclusión del verificador, para aislar la regla
   numérica de cualquier otro filtro: "73%" contra 0.7316. Este tiene que
   salir señalado por la regla, no por una lista — es el que detectaría una
   reintroducción del reescalado con tolerancia aunque la lista siguiera en
   su sitio.

Uso
---
    python test_regresion_porcentajes.py         # los dos casos

Código de retorno, ya convencional:
  - 0 si la regla sigue rechazando las coincidencias fortuitas.
  - 1 si algún caso volvió a quedar respaldado por una de ellas.
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
    # aceptado por coincidencia", que es lo que esta prueba mide.
    excluidos = {e["valor"] for e in resultado.get("porcentajes_de_metodo_excluidos", [])}
    token = caso["token"]
    aceptado_por_coincidencia = token not in senalados and token not in excluidos
    return aceptado_por_coincidencia, resultado


def main():
    print("Prueba de regresion de la regla de porcentajes")
    print(f"Verificador: {VERIFICADOR}\n")

    fallos = 0
    for caso in CASOS:
        aceptado, resultado = correr_caso(caso)
        # El aserto: el porcentaje NO debe quedar respaldado por coincidencia.
        ok = not aceptado
        print(f"[{caso['nombre']}] {'OK' if ok else 'REGRESION'}")
        print(f"    informe dice        : {caso['token']}")
        print(f"    outputs solo tiene  : {caso['por_que']}")
        print(f"    respaldado por coincidencia: {aceptado}  (se espera False)")
        print(f"    conteo              : {resultado['numeros_con_respaldo_en_outputs']} "
              f"con respaldo, {len(resultado['numeros_sin_respaldo'])} senalados")
        print()
        if not ok:
            fallos += 1

    if fallos:
        print(f"RESULTADO: FALLA — {fallos} de {len(CASOS)} caso(s) volvieron a "
              "quedar respaldados por coincidencia fortuita. La regla floja "
              "regreso; el encabezado de este archivo explica cual era.")
        return 1
    print("RESULTADO: PASA — la regla sigue rechazando las coincidencias "
          "fortuitas que motivaron este archivo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

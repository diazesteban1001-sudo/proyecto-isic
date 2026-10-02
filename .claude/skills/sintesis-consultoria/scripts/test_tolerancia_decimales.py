#!/usr/bin/env python3
"""
test_tolerancia_decimales.py — control de la tolerancia de redondeo de
verificar_trazabilidad.py.

El defecto
----------
Hasta el 2026-10-02, por defecto, un número sin "%" tenía respaldo si
quedaba a menos de 0,01 absoluto de cualquier valor del corpus. La pAUC va de
0 a 0,2, así que ese margen es el 5 % de la escala: el README seguía pasando
con 0,1451 y 0,1331 cuando outputs/ ya decía 0,1398 y 0,1326. Es la misma
clase de defecto que test_regresion_porcentajes.py cerró para los
porcentajes; la vía directa había quedado abierta.

La regla
--------
Sin --tolerancia, una cifra con decimales admite media unidad de su último
dígito escrito: 0,1451 → ±0,00005; 0,14 → ±0,005. Una sin decimales, sea
recuento o porcentaje, tiene que coincidir exacta. Con --tolerancia, el margen
fijo de antes para todas. La salida declara el modo en `modo_tolerancia`.

Media unidad también en los enteros —±0,5— fue la primera especificación, y
aflojaba el chequeo: sobre el outputs/ de ese día, 16 enteros del borrador
dejaban de estar señalados, todos respaldados por azar (78 por un NNT de
77,58). Se vio antes del commit, midiendo qué cifras dejaban de estar
señaladas y no solo cuáles empezaban a estarlo. Los casos «11», «99%» y
«99 %» existen para que no vuelva.

Se escribió antes del arreglo y fallaba con el código de entonces, por el
corolario de la regla 6 de CLAUDE.md: un chequeo que no puede fallar no vale
nada.

Casos, cada uno con un borrador de una sola cifra sobre un outputs/ sintético
-----------------------------------------------------------------------------
  - corpus {0.1398}: "0,1451" señalada; "0,1398", "0,140" y "0,14" con respaldo;
  - corpus {401059}: "401.059" con respaldo; "401.060" señalada;
  - corpus {11.16}: "11" señalada;
  - corpus {pct_grupos_con_fuga: 98.92}: "99%" señalada. Y "99 %", con
    espacio, también, pero por otra vía: el verificador lo lee como "99" sin
    "%" (ver abajo);
  - la salida declara el modo;
  - el caso discrimina: con --tolerancia 0.01, "0,1451" vuelve a quedar
    respaldada y la salida declara el modo fijo.

Informativo, no cuenta para el resultado: tres defectos de lectura abiertos
---------------------------------------------------------------------------
  (a) candidatos() cambia la coma por punto antes de aplicar MILES, así que
      "0,008" recibe también la lectura 8: un 8 del corpus la respalda.
  (b) NUM_PATTERN solo reconoce el guion ASCII como signo. "−0,1398", con el
      signo menos U+2212 que usa el borrador, se lee como 0,1398: respaldada
      por {0.1398} y señalada frente a {-0.1398}, las dos al revés. Con guion
      ASCII se lee bien. Lo mismo "−0,0263" frente a {0.0263}.
  (c) El "%" solo se reconoce pegado al número: "99 %" se lee como "99" y va
      por la vía directa, sin la lista de PORCENTAJES_DE_METODO.
No se corrigen en el commit de la regla de decimales.

Uso
---
    .venv/bin/python .claude/skills/sintesis-consultoria/scripts/test_tolerancia_decimales.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import subprocess
import sys
import tempfile

VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")


def pauc(valor):
    return {"nivel_2b_gradient_boosting_balanceado": {"pauc_media": valor}}


FILAS = {"fuente": {"n_filas": 401059}}
SEGUNDOS = {"segundos_de_entrenamiento_por_fold": {"media": 11.16}}
FUGA = {"comparacion_particion_naive": {"pct_grupos_con_fuga": 98.92}}


def verificar(corpus, cifra, *extra):
    """Corre el verificador sobre un borrador con una sola cifra."""
    with tempfile.TemporaryDirectory() as tmp:
        outputs_dir = os.path.join(tmp, "outputs")
        os.makedirs(outputs_dir)
        with open(os.path.join(outputs_dir, "modelado-baseline.json"), "w", encoding="utf-8") as f:
            json.dump(corpus, f)
        borrador = os.path.join(tmp, "borrador.md")
        with open(borrador, "w", encoding="utf-8") as f:
            f.write(f"# Informe de prueba\n\nLa cifra citada es {cifra} de lo esperado.\n")
        salida = os.path.join(tmp, "verificacion")
        subprocess.run([sys.executable, VERIFICADOR, "--borrador", borrador, "--outputs-dir", outputs_dir,
                        "--out", salida, *extra], check=True, capture_output=True)
        with open(f"{salida}.json", encoding="utf-8") as f:
            return json.load(f)


def estado(r):
    """'respaldada', 'señalada «token»' u otra cosa, descrita. Se exige que la
    cifra se haya extraído: una que el verificador descarta no está señalada,
    pero tampoco respaldada, y contarla como lo segundo haría pasar el caso."""
    if r["numeros_en_borrador"] != 1:
        return f"extraídas {r['numeros_en_borrador']} cifras, se esperaba 1"
    if r["numeros_con_respaldo_en_outputs"] == 1 and not r["numeros_sin_respaldo"]:
        return "respaldada"
    if r["numeros_con_respaldo_en_outputs"] == 0 and len(r["numeros_sin_respaldo"]) == 1:
        return f"señalada «{r['numeros_sin_respaldo'][0]['valor']}»"
    return "ignorada por contexto"


def modo(r):
    return f"modo_tolerancia={r.get('modo_tolerancia', '(falta)')}, tolerancia_redondeo={r.get('tolerancia_redondeo')}"


def rotulo(corpus):
    return json.dumps(corpus, ensure_ascii=False)


def main():
    casos = []
    for corpus, cifra, esperado in [
        (pauc(0.1398), "0,1451", "señalada"),
        (pauc(0.1398), "0,1398", "respaldada"),
        (pauc(0.1398), "0,140", "respaldada"),
        (pauc(0.1398), "0,14", "respaldada"),
        (FILAS, "401.059", "respaldada"),
        (FILAS, "401.060", "señalada"),
        (SEGUNDOS, "11", "señalada"),
        (FUGA, "99%", "señalada"),
        (FUGA, "99 %", "señalada"),
    ]:
        obtenido = estado(verificar(corpus, cifra))
        casos.append((f"{rotulo(corpus)}: «{cifra}» {esperado}",
                      obtenido.startswith(esperado), f"obtenido: {obtenido}"))

    r = verificar(pauc(0.1398), "0,1398")
    casos.append(("sin --tolerancia, la salida declara la regla de decimales",
                  r.get("modo_tolerancia") == "decimales_escritos" and r.get("tolerancia_redondeo") is None,
                  modo(r)))

    r = verificar(pauc(0.1398), "0,1451", "--tolerancia", "0.01")
    casos.append(("el caso discrimina: con --tolerancia 0.01, «0,1451» respaldada y modo fijo",
                  estado(r) == "respaldada" and r.get("modo_tolerancia") == "fija"
                  and r.get("tolerancia_redondeo") == 0.01, f"obtenido: {estado(r)}; {modo(r)}"))

    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")

    print("\nInformativo, no cuenta para el resultado: defectos de lectura abiertos")
    for defecto, corpus, cifra in [
        ("(a) coma y MILES", {"recuento": 8}, "0,008"),
        ("(b) signo U+2212", pauc(0.1398), "−0,1398"),
        ("(b) signo U+2212", pauc(-0.1398), "−0,1398"),
        ("(b) guion ASCII ", pauc(-0.1398), "-0,1398"),
        ("(b) signo U+2212", pauc(0.0263), "−0,0263"),
        ("(c) % separado  ", FUGA, "99 %"),
    ]:
        print(f"  {defecto}: {rotulo(corpus)}, «{cifra}» → {estado(verificar(corpus, cifra))}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

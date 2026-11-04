#!/usr/bin/env python3
"""
test_comentarios_f.py — controles de comentarios_f.py, el analizador de los
comentarios F: en modo informe (PLAN.md, Fase 6, «La verificación por campo:
especificación»). Un borrador y un outputs/ sintéticos, en un directorio temporal.

  - Las rutas relativas, las abreviaturas de archivo y de tramo, los comodines, los
    índices, los paréntesis y n(lista) entran en la gramática y se resuelven.
  - No entran: una ruta mal escrita, un comodín en la fuente, una clave abreviada
    con «…», una abreviatura usada antes de declararse, n() sobre algo que no es
    una lista, una referencia sin líneas y un archivo de referencias que no existe.
  - Una parte que solo cita PLAN.md o una sección del informe va a «solo
    documentos del proyecto», con su tipo; una marca «sin fuente» va a su clase,
    con su motivo.
  - La asociación: un número separado de su comentario por un encabezado queda
    sin comentario.

Casos que deben fallar: con el resolvedor que ignora las rutas relativas, la ruta
relativa no existe; el mismo número sin encabezado en medio sí queda cubierto; si
el analizador perdiera un número del cuerpo, el control contra el verificador lo
detiene.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/test_comentarios_f.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comentarios_f as cf  # noqa: E402

REFERENCIA = "referencias/nadeau-bengio-2003-t-corregido.md"  # versionada: existe en cualquier clon
SALIDA = {
    "faltantes": {"age_approx": {"pct": 1.5}, "sex": {"pct": 2.5}},
    "comparaciones_nuevo_menos_base": {"pauc": {"media": 0.0123, "intervalo_t_95_nadeau_bengio": [0.001, 0.02]},
                                       "auc": {"media": 0.0456, "intervalo_t_95_nadeau_bengio": [0.01, 0.08]}},
    "por_fold": [{"n": 10}, {"n": 11}],
    "columnas": ["a", "b", "c"],
}
BORRADOR = f"""# Prueba

<!-- Abreviaturas de los comentarios: S = outputs/salida.json; C = comparaciones_nuevo_menos_base;
     IC = intervalo_t_95_nadeau_bengio. -->

Faltan el 1,5 % y el 2,5 %.
<!-- F: outputs/salida.json > faltantes.age_approx.pct y .sex.pct -->

Los intervalos son [0,001; 0,02] y [0,01; 0,08].
<!-- F: S > C.*.IC -->

Los pliegues tienen 10 y 11 pacientes.
<!-- F: S > por_fold[*].n -->

Las columnas son 3.
<!-- F: S > n(columnas) -->

Los faltantes, de nuevo: 1,5.
<!-- F: S > faltantes (age_approx y sex) -->

Una media mal citada: 0,0123.
<!-- F: S > C.pauc.mediaa -->

Un comodín en la fuente: 0,0456.
<!-- F: outputs/*.json > C.auc.media -->

Una clave abreviada: 0,0456.
<!-- F: S > C.a….media -->

Una cuenta sobre un diccionario: 2.
<!-- F: S > n(faltantes) -->

Una referencia sin líneas: 0,25.
<!-- F: {REFERENCIA}, «La fórmula» -->

Una referencia con líneas: 0,25.
<!-- F: {REFERENCIA}, línea 95 -->

Una referencia que no existe: 0,5.
<!-- F: referencias/no-existe.md, línea 3 -->

Una decisión del plan: 20 %.
<!-- F: PLAN.md, Fase 1, «El reservado» -->

Una sección del informe: 7.
<!-- F: «Método», «Qué se compara» -->

Un recuento estructural: 4 secciones.
<!-- F: sin fuente: recuento de las secciones del propio informe -->

Un número antes de un encabezado: 99.

## Otra sección

<!-- F: S > C.pauc.media -->

Un número con su comentario detrás: 98.
<!-- F: S > C.pauc.media -->
"""
TEMPRANA = "Una abreviatura antes de declararse: 0,0123.\n<!-- F: T > C.pauc.media -->\n" \
           "<!-- Abreviaturas de los comentarios: T = outputs/salida.json. -->\n"


def main():
    with tempfile.TemporaryDirectory() as tmp:
        outputs = os.path.join(tmp, "outputs")
        os.makedirs(outputs)
        with open(os.path.join(outputs, "salida.json"), "w", encoding="utf-8") as f:
            json.dump(SALIDA, f)
        coms, sin, _ = cf.analizar(BORRADOR, outputs)
        coms_sin_relativas, _, _ = cf.analizar(BORRADOR, outputs, relativas=False)
        temprana, _, _ = cf.analizar(TEMPRANA, outputs)
        r = cf.informe(BORRADOR, outputs, "prueba.md")
        original = cf.numeros_del_cuerpo
        cf.numeros_del_cuerpo = lambda texto: original(texto)[1:]
        try:
            cf.informe(BORRADOR, outputs, "prueba.md")
            detenido = False
        except SystemExit:
            detenido = True
        finally:
            cf.numeros_del_cuerpo = original

    def de(fragmento, lista=coms):
        return next(c for c in lista if fragmento in c["texto"])

    def motivo(c, texto):
        return any(m.startswith(texto) for m in c["motivos"])

    casos = [
        ("una ruta relativa se resuelve", de(".sex.pct")["clase"] == "entra"
         and [x["ruta"] for x in de(".sex.pct")["rutas"]] == ["faltantes.age_approx.pct", "faltantes.sex.pct"]),
        ("abreviaturas de archivo y de tramo, y comodín", de("C.*.IC")["clase"] == "entra"
         and de("C.*.IC")["rutas"][0]["nodos"] == 2),
        ("comodín de índice", de("por_fold[*]")["clase"] == "entra" and de("por_fold[*]")["rutas"][0]["nodos"] == 2),
        ("n(lista)", de("n(columnas)")["clase"] == "entra"),
        ("los paréntesis se ignoran", de("faltantes (age_approx")["clase"] == "entra"),
        ("una ruta mal escrita no entra", motivo(de("mediaa"), "ruta que no existe")),
        ("un comodín en la fuente no entra", motivo(de("outputs/*.json"), "comodín en la fuente")),
        ("una clave abreviada con «…» no entra", motivo(de("C.a…"), "rutas fuera de la gramática")),
        ("n() sobre un diccionario no entra", motivo(de("n(faltantes)"), "n() sobre algo")),
        ("una abreviatura antes de declararse no entra", motivo(temprana[0], "fuente no reconocida")),
        ("una referencia sin líneas no entra", motivo(de("«La fórmula»"), "referencia sin líneas")),
        ("una referencia con líneas entra", de("línea 95")["clase"] == "entra"),
        ("un archivo de referencias que no existe no entra", motivo(de("no-existe.md"), "no existe")),
        ("PLAN.md va a documentos del proyecto, con su tipo", de("PLAN.md")["clase"] == "solo documentos del proyecto"
         and de("PLAN.md")["documentos"] == ["PLAN.md"]),
        ("una sección del informe, con su tipo", de("«Método»")["documentos"] == ["sección del informe"]),
        ("la marca «sin fuente», con su motivo", de("sin fuente")["clase"] == "sin fuente"
         and r["marcas_sin_fuente"][0]["motivo"].startswith("recuento de las secciones")),
        ("un número separado de su comentario por un encabezado queda sin comentario",
         [n["valor"] for n in sin] == ["99."]),
        ("el número con su comentario detrás queda cubierto",
         [n["valor"] for n in coms[-1]["numeros"]] == ["98."]),
        ("el informe cuadra con el verificador", r["control"]["misma_lista"]),
        ("debe fallar: sin rutas relativas, la relativa no existe",
         motivo(de(".sex.pct", coms_sin_relativas), "ruta que no existe")),
        ("debe fallar: si se pierde un número del cuerpo, el control lo detiene", detenido),
    ]
    fallos = 0
    for titulo, ok in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
test_por_campo.py — controles de por_campo.py, la verificación por campo (PLAN.md,
Fase 6, «La verificación por campo», paso 4, y las dos reglas añadidas antes de
él). Casos sintéticos, en un directorio temporal con su outputs/ y su
referencias/, y casos sobre los archivos reales.

  1. El caso central: una cifra que está en el corpus pero no en su campo queda
     señalada. Debe fallar: la búsqueda en todo el corpus la da por respaldada.
  2. Las regresiones reales, con la clase fijada antes de escribir el código:
     «0,922» (líneas 818 y 938) y «0,695» (835), respaldadas por su referencia;
     «20%» (462), por su campo, de un archivo fuera del corpus; «11» (528), no está
     en sus campos. Debe fallar: la búsqueda en todo el corpus respalda el «11» y
     el «0,922».
  3. Un comentario fuera de la gramática detiene la verificación. Debe fallar: el
     mismo comentario bien escrito no la detiene.
  4. Las referencias: una cifra en una línea de cita pasa; la misma, en otra línea
     que no la tiene, queda fuera de las líneas citadas; «0,94» se encuentra en una
     fuente que escribe «0.94». Debe fallar: la búsqueda literal de «0,94» en esa
     línea no lo encuentra.
  5. Sin comentario queda señalada. Debe fallar: con su comentario detrás, no.
  6. Si las clases no suman el total, se detiene.
  7. Las líneas nuestras (regla 2): las tres que vio la persona salen nuestras; la
     línea de cita de una ficha y una de texto completo salen originales; una cifra
     que solo está en una línea nuestra cita un documento del proyecto, y una «obra
     del proyecto» no tiene líneas originales. Deben fallar: el clasificador que
     toma todas las líneas por originales, y el que solo mira «## Texto original».
  8. Un campo de un archivo fuera del corpus cuenta (regla 1). Debe fallar: la
     búsqueda en todo el corpus no lo respalda.
  9. Una marca «sin fuente» va a su clase, con su motivo.

Uso:
    python .claude/skills/sintesis-consultoria/scripts/test_por_campo.py
Devuelve 0 si los casos se comportan como se espera.
"""

import json
import os
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comentarios_f as cf  # noqa: E402
import por_campo as pc  # noqa: E402
import verificar_trazabilidad as vt  # noqa: E402

FICHA = """# Una ficha

**LICENCIA: desconocida → FICHA.**

> The AUC was 0.94 in the test set.

*Nuestro.* Una lectura con 0,88 que no es del artículo.
Una línea sin cifras.
"""
COMPLETO = """# Un texto completo

**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**

Cabecera nuestra con 0.31.

## Texto original

The original text says 0.31.
"""
OBRA = """# Una búsqueda

**LICENCIA:** obra del proyecto.

> 0.42 en una línea de cita de una obra nuestra.
"""
BORRADOR = """# Prueba

El AUC fue 0,1234.
<!-- F: outputs/a.json > x.media -->

Otra cifra: 0,7777.
<!-- F: outputs/a.json > x.media -->

La fracción: 20%.
<!-- F: outputs/holdout-pacientes.json > metodo.fraccion -->

Son 3 columnas.
<!-- F: outputs/a.json > n(lista) -->

El AUC citado: 0,94.
<!-- F: referencias/ficha.md, línea 5, cita literal -->

La misma, fuera de sus líneas: 0,94.
<!-- F: referencias/ficha.md, línea 8 -->

En lo nuestro: 0,88.
<!-- F: referencias/ficha.md, línea 7 -->

Del texto completo: 0,31.
<!-- F: referencias/completo.md, línea 9 -->

De una obra nuestra: 0,42.
<!-- F: referencias/obra.md, línea 5 -->

Un recuento estructural: 4.
<!-- F: sin fuente: recuento de las secciones del propio informe -->

Solo el plan: 7.
<!-- F: PLAN.md, Fase 1 -->

Un número antes de un encabezado: 99.

## Otra sección

<!-- F: outputs/a.json > x.media -->

Un número con su comentario detrás: 98.
<!-- F: outputs/a.json > x.media -->
"""


def L(fragmento):
    """La línea del borrador sintético que contiene el fragmento."""
    return next(i + 1 for i, linea in enumerate(BORRADOR.split("\n")) if fragmento in linea)


def preparar(tmp):
    os.makedirs(os.path.join(tmp, "outputs"))
    os.makedirs(os.path.join(tmp, "referencias"))
    for nombre, datos in (("a.json", {"x": {"media": 0.1234}, "lista": ["a", "b", "c"]}),
                          ("b.json", {"y": 0.7777}),
                          ("holdout-pacientes.json", {"metodo": {"fraccion": 0.2}})):
        with open(os.path.join(tmp, "outputs", nombre), "w", encoding="utf-8") as f:
            json.dump(datos, f)
    for nombre, texto in (("ficha.md", FICHA), ("completo.md", COMPLETO), ("obra.md", OBRA)):
        with open(os.path.join(tmp, "referencias", nombre), "w", encoding="utf-8") as f:
            f.write(texto)


def clases(texto, outputs, raiz, **kw):
    """{(valor, línea): clase} de cada número del cuerpo."""
    r = pc.clasificar(texto, outputs, raiz=raiz, **kw)
    salida = {}
    for k in pc.CLASES:
        for n in r["detalle"].get(k, []):
            salida[(n["valor"].rstrip(".,"), n["linea"])] = k
    comentarios, _, _ = cf.analizar(texto, outputs, raiz=raiz)
    cache = {}
    for c in comentarios:
        a = pc.ambito(c, outputs, raiz, kw.get("regla", "propia"), cache)
        for n in c["numeros"]:
            salida.setdefault((n["valor"].rstrip(".,"), n["linea"]), pc.clase_de(n["valor"], c, a))
    return r, salida


def en_el_corpus(valor, outputs):
    P, Q = vt.cargar_valores_permitidos(outputs)
    return vt.tiene_respaldo(vt.candidatos(valor), valor.endswith("%"), P, Q)


def detiene(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def main():
    casos = []
    with tempfile.TemporaryDirectory() as tmp:
        preparar(tmp)
        out = os.path.join(tmp, "outputs")
        r, k = clases(BORRADOR, out, tmp)
        _, todas = clases(BORRADOR, out, tmp, regla="todas")
        _, solo_to = clases(BORRADOR, out, tmp, regla="solo_texto_original")
        casos += [
            ("1. una cifra en su campo", k[("0,1234", L("El AUC fue"))] == "respaldada_por_su_campo"),
            ("1. el caso central: en el corpus pero no en su campo, señalada", k[("0,7777", L("Otra cifra"))] == "no_esta_en_sus_campos"),
            ("1. debe fallar: la búsqueda en todo el corpus la respalda", en_el_corpus("0,7777", out)),
            ("4. una cifra en su línea de cita pasa, leída en inglés", k[("0,94", L("El AUC citado"))] == "respaldada_por_su_referencia"),
            ("4. la misma fuera de sus líneas", k[("0,94", L("fuera de sus líneas"))] == "fuera_de_las_lineas_citadas"),
            ("4. debe fallar: la búsqueda literal de «0,94» en la línea citada no lo encuentra",
             "0,94" not in FICHA.split("\n")[4] and "0.94" in FICHA.split("\n")[4]),
            ("5. un número separado de su comentario por un encabezado queda sin comentario",
             k[("99", L("antes de un encabezado"))] == "sin_comentario"),
            ("5. debe fallar: con su comentario detrás, no", k[("98", L("comentario detrás"))] == "respaldada_por_su_campo"
             or k[("98", L("comentario detrás"))] == "no_esta_en_sus_campos"),
            ("7. una cifra que solo está en una línea nuestra cita un documento del proyecto",
             k[("0,88", L("En lo nuestro"))] == "cita_un_documento_del_proyecto"),
            ("7. en un texto completo, la línea tras «## Texto original» es original",
             k[("0,31", L("Del texto completo"))] == "respaldada_por_su_referencia"),
            ("7. una «obra del proyecto» no tiene líneas originales", k[("0,42", L("De una obra"))] == "cita_un_documento_del_proyecto"),
            ("7. debe fallar: con todas las líneas originales, la de 0,88 pasa",
             todas[("0,88", L("En lo nuestro"))] == "respaldada_por_su_referencia"),
            ("7. debe fallar: solo con «## Texto original», la línea de cita de la ficha no cuenta",
             solo_to[("0,94", L("El AUC citado"))] != "respaldada_por_su_referencia"),
            ("8. un campo de un archivo fuera del corpus cuenta", k[("20%", L("La fracción"))] == "respaldada_por_su_campo"),
            ("8. debe fallar: la búsqueda en todo el corpus no lo respalda", not en_el_corpus("20%", out)),
            ("n(lista) cuenta los elementos", k[("3", L("Son 3 columnas"))] == "respaldada_por_su_campo"),
            ("solo PLAN.md cita un documento del proyecto", k[("7", L("Solo el plan"))] == "cita_un_documento_del_proyecto"),
            ("9. la marca «sin fuente», con su motivo", k[("4", L("recuento estructural"))] == "declarada_sin_fuente"
             and r["marcas_sin_fuente"][0]["motivo"].startswith("recuento de las secciones")),
            ("6. las clases suman el total", sum(r["por_clase"].values()) == r["numeros_del_cuerpo"]),
        ]
        roto = BORRADOR.replace("> x.media -->\n\nOtra", "> x.mediaa -->\n\nOtra")
        casos += [
            ("3. una ruta mal escrita detiene la verificación", detiene(lambda: pc.clasificar(roto, out, raiz=tmp))),
            ("3. debe fallar: bien escrita, no la detiene", not detiene(lambda: pc.clasificar(BORRADOR, out, raiz=tmp))),
        ]
        original = cf.segun_el_verificador
        cf.segun_el_verificador = lambda texto: original(texto) + [("1", 1)]
        try:
            casos.append(("6. si las clases no suman el total, se detiene",
                          detiene(lambda: pc.clasificar(BORRADOR, out, raiz=tmp))))
        finally:
            cf.segun_el_verificador = original

    # Los archivos reales
    def nuestras(archivo, a, b, regla="propia"):
        _, orig = pc.lineas_originales(archivo, regla=regla)
        return not (set(range(a, b + 1)) & orig)

    def original(archivo, n, regla="propia"):
        return n in pc.lineas_originales(archivo, regla=regla)[1]

    tres = [("referencias/nadeau-bengio-2003-t-corregido.md", 134, 143),
            ("referencias/slice3d-metadata-tbp-lv.md", 81, 87),
            ("referencias/efficientnet-b0-preentrenamiento.md", 77, 108)]
    casos += [
        ("7. reales: las tres que vio la persona salen nuestras", all(nuestras(*t) for t in tres)),
        ("7. reales: la línea de cita 47 de slice3d-metadata-tbp-lv.md sale original",
         original("referencias/slice3d-metadata-tbp-lv.md", 47)),
        ("7. reales: la línea 209 de Kurtansky 2025, tras «## Texto original», sale original",
         original("referencias/kurtansky-2025-triaje-automatizado-tbp.md", 209)),
        ("7. reales, debe fallar: con todas las líneas originales, las tres no salen nuestras",
         not any(nuestras(*t, regla="todas") for t in tres)),
        ("7. reales, debe fallar: solo con «## Texto original», la línea 47 no sale original",
         not original("referencias/slice3d-metadata-tbp-lv.md", 47, regla="solo_texto_original")),
    ]
    texto = open(os.path.join(cf.RAIZ, "informe", "borrador-v2.md"), encoding="utf-8").read()
    outputs = os.path.join(cf.RAIZ, "outputs")
    _, real = clases(texto, outputs, cf.RAIZ)
    esperadas = {("0,922", 818): "respaldada_por_su_referencia", ("0,922", 938): "respaldada_por_su_referencia",
                 ("0,695", 835): "respaldada_por_su_referencia", ("20%", 462): "respaldada_por_su_campo",
                 ("11", 528): "no_esta_en_sus_campos"}
    for (v, l), esperada in esperadas.items():
        casos.append((f"2. «{v}» (línea {l}): {esperada}", real.get((v, l)) == esperada))
    casos.append(("2. debe fallar: la búsqueda en todo el corpus respalda el «11» y el «0,922»",
                  en_el_corpus("11", outputs) and en_el_corpus("0,922", outputs)))

    fallos = 0
    for titulo, ok in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

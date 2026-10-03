#!/usr/bin/env python3
"""
test_generar_demo.py — controles positivos de generar_demo.py: el control de
la recomendación y el aviso de estado.

Cada caso arma un outputs/ sintético en un directorio temporal —una copia del
outputs/ real con la verificación recalculada sobre informe/borrador-v2.md y,
según el caso, un archivo cambiado— y corre el generador sobre él. Por el
corolario de la regla 6 de CLAUDE.md, cada condición se fuerza:

  A. Base: la copia sin cambios. El generador escribe la página, sin aviso.
     Sin este caso, los demás pasarían con un generador que se negara siempre.
  B. Recomendación: el intervalo corregido de la pAUC de M3 limpio − M2 cruza
     el cero. La regla da M2, no coincide con RECOMENDADO y no se escribe.
  C. Archivo sin conjunto: diseno-validacion.json sin el campo datos. La
     página sale con el aviso de cifras exploratorias.
  D. El mismo caso en fase4-m3limpio-vs-m2.json, que la página lee solo para
     el control de la recomendación. También sale con el aviso: se revisan los
     archivos que la página lee, no una lista escrita a mano.
  E. Reservado fuera de la Fase 5: modelado-baseline.json declara el
     reservado. No se escribe.
  F. Reservado en la salida de la Fase 5: comprobar_conjuntos lo acepta en el
     archivo que se le declara como esa salida, y lo rechaza en el mismo
     archivo si no se le declara.
  G. Verificación sobre otro borrador: sintesis-verificacion.* hecha sobre
     informe/borrador.md. No se escribe.
  H. Verificación con otro modo de tolerancia: sobre informe/borrador-v2.md,
     con --tolerancia 0.01. No se escribe.
  I. extraccion-imagen.json sin datos.reparto: reparte los dos conjuntos y
     solo cuenta como no exploratorio si lo declara. Sale con el aviso.
  J. holdout-pacientes.json sin fecha_sellado: lo mismo con el registro del
     sellado, del que la página lee la semilla y la fracción.

Uso:
    .venv/bin/python .claude/skills/sintesis-consultoria/scripts/test_generar_demo.py
Devuelve 0 si los casos se comportan como se espera.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
GENERADOR = os.path.join(SCRIPTS, "generar_demo.py")
VERIFICADOR = os.path.join(SCRIPTS, "verificar_trazabilidad.py")
RAIZ = os.path.abspath(os.path.join(SCRIPTS, "..", "..", "..", ".."))
OUTPUTS = os.path.join(RAIZ, "outputs")
AVISO = 'class="exploratorio"'


def verificar(outputs_dir, borrador, *extra):
    subprocess.run([sys.executable, VERIFICADOR, "--borrador", borrador, "--outputs-dir", outputs_dir,
                    "--out", os.path.join(outputs_dir, "sintesis-verificacion"), *extra],
                   cwd=RAIZ, check=True, capture_output=True)


def preparar(tmp):
    """Copia de outputs/ con la verificación recalculada sobre el borrador vigente."""
    destino = os.path.join(tmp, "outputs")
    os.makedirs(destino)
    for ruta in glob.glob(os.path.join(OUTPUTS, "*.json")) + glob.glob(os.path.join(OUTPUTS, "*.md")):
        shutil.copy(ruta, destino)
    verificar(destino, "informe/borrador-v2.md")
    return destino


def cambiar(outputs_dir, nombre, cambio):
    ruta = os.path.join(outputs_dir, f"{nombre}.json")
    with open(ruta, encoding="utf-8") as f:
        contenido = json.load(f)
    cambio(contenido)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False)


def generar(caso, ajuste=None):
    """Corre el generador sobre una copia ajustada. Devuelve (escrita, html, error)."""
    with tempfile.TemporaryDirectory() as tmp:
        outputs_dir = preparar(tmp)
        if ajuste:
            ajuste(outputs_dir)
        salida = os.path.join(tmp, "demo.html")
        r = subprocess.run([sys.executable, GENERADOR, "--outputs-dir", outputs_dir, "--salida", salida],
                           capture_output=True, text=True)
        html = open(salida, encoding="utf-8").read() if os.path.exists(salida) else None
        return html is not None and r.returncode == 0, html, (r.stderr.strip().splitlines() or [""])[-1]


def caso_f():
    """F: llama a comprobar_conjuntos directamente, con una salida de la Fase 5 sintética."""
    sys.path.insert(0, SCRIPTS)
    try:
        import generar_demo
    except Exception as e:  # noqa: BLE001
        return False, f"no se pudo importar generar_demo: {e}"
    if not hasattr(generar_demo, "comprobar_conjuntos"):
        return False, "generar_demo no tiene comprobar_conjuntos"
    leidos = {"eda-diagnostico": {"datos": {"conjunto": "desarrollo"}},
              "fase5-sintetica": {"datos": {"conjunto": "reservado"}}}
    try:
        aviso = generar_demo.comprobar_conjuntos(leidos, salida_fase_5="fase5-sintetica")
    except SystemExit as e:
        return False, f"declarada como salida de la Fase 5, se negó: {e}"
    try:
        generar_demo.comprobar_conjuntos(leidos, salida_fase_5=None)
    except SystemExit:
        return aviso == "", f"aceptada como salida de la Fase 5 (aviso: {aviso!r}); rechazada si no se declara"
    return False, "sin declararla como salida de la Fase 5, la aceptó"


def main():
    def intervalo_que_cruza(o):
        o["comparaciones_nuevo_menos_base"]["pauc"]["intervalo_t_95_nadeau_bengio"] = [-0.001, 0.0341]

    def sin_datos(o):
        o.pop("datos", None)

    def reservado(o):
        o["datos"]["conjunto"] = "reservado"

    def sin_reparto(o):
        o["datos"].pop("reparto", None)

    def sin_sellado(o):
        o.pop("fecha_sellado", None)

    corridas = {
        "A": generar("A"),
        "B": generar("B", lambda d: cambiar(d, "fase4-m3limpio-vs-m2", intervalo_que_cruza)),
        "C": generar("C", lambda d: cambiar(d, "diseno-validacion", sin_datos)),
        "D": generar("D", lambda d: cambiar(d, "fase4-m3limpio-vs-m2", sin_datos)),
        "E": generar("E", lambda d: cambiar(d, "modelado-baseline", reservado)),
        "G": generar("G", lambda d: verificar(d, "informe/borrador.md")),
        "H": generar("H", lambda d: verificar(d, "informe/borrador-v2.md", "--tolerancia", "0.01")),
        "I": generar("I", lambda d: cambiar(d, "extraccion-imagen", sin_reparto)),
        "J": generar("J", lambda d: cambiar(d, "holdout-pacientes", sin_sellado)),
    }
    f_ok, f_detalle = caso_f()

    def escrita(c, con_aviso):
        ok, html, err = corridas[c]
        return ok and ((AVISO in html) == con_aviso), f"escrita: {ok}; aviso: {html is not None and AVISO in html}; {err}"

    def negada(c):
        ok, _, err = corridas[c]
        return not ok, f"escrita: {ok}; {err}"

    casos = [
        ("A. base: escribe la página, sin aviso", *escrita("A", False)),
        ("B. el intervalo de M3 limpio − M2 cruza el cero: no escribe", *negada("B")),
        ("C. diseno-validacion.json sin datos: escribe con aviso", *escrita("C", True)),
        ("D. fase4-m3limpio-vs-m2.json sin datos: escribe con aviso", *escrita("D", True)),
        ("E. modelado-baseline.json declara el reservado: no escribe", *negada("E")),
        ("F. el reservado se acepta solo en la salida de la Fase 5", f_ok, f_detalle),
        ("G. verificación sobre informe/borrador.md: no escribe", *negada("G")),
        ("H. verificación con --tolerancia 0.01: no escribe", *negada("H")),
        ("I. extraccion-imagen.json sin datos.reparto: escribe con aviso", *escrita("I", True)),
        ("J. holdout-pacientes.json sin fecha_sellado: escribe con aviso", *escrita("J", True)),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

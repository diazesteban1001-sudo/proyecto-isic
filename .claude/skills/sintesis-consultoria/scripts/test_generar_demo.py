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
  K. Los cinco grupos de la verificación no suman el total: se quita un
     número de numeros_en_comentarios en sintesis-verificacion.json. La ficha
     de síntesis los enumera como si cubrieran todo, así que no se escribe, y
     el motivo tiene que ser la suma, no la correspondencia con el borrador.
  L. Cada frase de «La imagen sola, sin el sistema de fotografía corporal
     total» que depende de los datos, y la viñeta de DINOv2, con un archivo
     alterado para que deje de ser cierta. No se escribe, y el motivo tiene
     que ser esa frase. Las diferencias que la página da por establecidas se
     invierten (media e intervalo cambian de signo); las que da por no
     establecidas no se rompen invirtiéndolas, así que se les mueve el
     intervalo para que excluya el cero.
  M. Las dos lecturas de referencias/ que hace la subsección: con la fila de
     solo recortes de la Tabla 3 duplicada, el 0,922 no se lee; con una cita
     quitada de su archivo —la de las fotos de los pacientes o la de los datos
     básicos—, la página no se escribe. Sobre copias en una raíz
     temporal; con las copias sin tocar, las dos lecturas pasan.

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


def caso_m():
    """M: auc_solo_recortes y las citas de datos_imagen_sola, sobre copias de las
    dos fuentes en una raíz temporal."""
    sys.path.insert(0, SCRIPTS)
    import generar_demo as g
    salidas = {n: json.load(open(os.path.join(OUTPUTS, f"{n}.json"), encoding="utf-8"))
               for n in ("imagen-sola", "modelado-baseline", "fase4-m2-vs-m1", "fase4-m3-vs-m2", "extraccion-imagen",
                         "tiempo-inferencia")}

    def correr(fn):
        try:
            return fn(), None
        except SystemExit as e:
            return None, str(e)

    def datos():
        return g.datos_imagen_sola(salidas["imagen-sola"], salidas["modelado-baseline"]["escala_de_referencia_pauc"],
                                   salidas["modelado-baseline"],
                                   {n: salidas[n] for n in ("fase4-m2-vs-m1", "fase4-m3-vs-m2")},
                                   salidas["extraccion-imagen"], salidas["tiempo-inferencia"])
    raiz_real = g.RAIZ
    resultado = {}
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "referencias"))
        for ruta in (g.KURTANSKY_2025, g.KURTANSKY_2024):
            shutil.copy(os.path.join(raiz_real, ruta), os.path.join(tmp, ruta))
        try:
            g.RAIZ = tmp
            base, err = correr(datos)
            resultado["base"] = (base is not None and base["auc_recortes"]["auc"] == 0.922, err or "lee 0,922 y las citas")
            ruta25 = os.path.join(tmp, g.KURTANSKY_2025)
            texto = open(ruta25, encoding="utf-8").read()
            fila = next(l for l in texto.split("\n") if l.startswith("\t\t\t\tx\t\t0.142\t0.922"))
            open(ruta25, "w", encoding="utf-8").write(texto.replace(fila, fila + "\n" + fila, 1))
            _, err = correr(g.auc_solo_recortes)
            resultado["tabla"] = (err is not None and "una sola vez" in err, err or "no falló")
            open(ruta25, "w", encoding="utf-8").write(texto)
            ruta24 = os.path.join(tmp, g.KURTANSKY_2024)
            texto = open(ruta24, encoding="utf-8").read()
            open(ruta24, "w", encoding="utf-8").write(texto.replace("vary greatly in lighting and FOV", "vary in lighting"))
            _, err = correr(datos)
            resultado["cita"] = (err is not None and "vary greatly in lighting and FOV" in err, err or "no falló")
            open(ruta24, "w", encoding="utf-8").write(texto)
            texto = open(ruta25, encoding="utf-8").read()
            open(ruta25, "w", encoding="utf-8").write(texto.replace("are not directly attained from images",
                                                                     "are not attained from images"))
            _, err = correr(datos)
            resultado["cita_basicos"] = (err is not None and "are not directly attained from images" in err,
                                         err or "no falló")
        finally:
            g.RAIZ = raiz_real
    return resultado


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

    def grupos_que_no_suman(o):
        o["numeros_en_comentarios"].pop()

    def invertir(o, n, k):
        d = o["comparaciones_nuevo_menos_base"][n][k]
        d["media"] = -d["media"]
        lo, hi = d["intervalo_t_95_nadeau_bengio"]
        d["intervalo_t_95_nadeau_bengio"] = [-hi, -lo]

    def excluir_cero(o, n, k):
        o["comparaciones_nuevo_menos_base"][n][k]["intervalo_t_95_nadeau_bengio"][0] = 0.001

    def sin_control(o):
        o["control_m1_contra_referencia"]["m1_reproduce_fold_a_fold"] = False

    def un_pliegue_bajo_el_azar(o):
        o["metricas"]["Imagen"]["pauc"]["por_semilla_y_fold"]["0"][0] = 0.019

    def sin_tbp_lv(o):
        o["features_usadas"] = [v for v in o["features_usadas"] if not v.startswith("tbp_lv_")]

    def m4b_establecida(o):
        o["comparaciones_nuevo_menos_base"]["pauc"]["intervalo_t_95_nadeau_bengio"] = [0.001, 0.0202]

    def victoria_de_mas(o, n, k, campo):
        o["comparaciones_nuevo_menos_base"][n][k][campo] += 1

    def victoria_de_menos(o, n, k, campo):
        o["comparaciones_nuevo_menos_base"][n][k][campo] -= 1

    def tiempo_de_la_imagen_sola(o):
        o["tiempos"]["Imagen"] = dict(o["tiempos"]["M4"])

    def segundos_en_imagen_sola(o):
        o["segundos_por_pliegue"] = {"Imagen": [1.0]}

    def sin_sexo(o):
        o["features_usadas"] = [v for v in o["features_usadas"] if v != "sex"]

    def m4_barato(o):
        o["tiempos"]["M4"]["mediana_segundos_por_1000_lesiones"] = 0.001

    IS, IM1, IB = "imagen-sola", "imagen_menos_m1", "imagen_basicos_menos_imagen"
    casos_l = [
        ("control de M1 en falso", IS, sin_control, "en los mismos pliegues de M1"),
        ("M1 sin variables tbp_lv_", "modelado-baseline", sin_tbp_lv,
         "Las mediciones de las que dependen M1, M2 y M3 limpio"),
        ("un pliegue de la imagen sola bajo el azar", IS, un_pliegue_bajo_el_azar, "muy por encima del azar"),
        ("Imagen − M1 invertida en la pAUC", IS, lambda o: invertir(o, IM1, "pauc"), "establecidas (la pAUC)"),
        ("Imagen − M1 invertida en el AUC", IS, lambda o: invertir(o, IM1, "auc"), "establecidas (el AUC)"),
        ("Imagen − M1 invertida en la sensibilidad top-15", IS, lambda o: invertir(o, IM1, "setop15"),
         "establecidas (la sensibilidad top-15)"),
        ("Imagen − M1 invertida en el NNT80% SE", IS, lambda o: invertir(o, IM1, "nnt80"), "establecidas (el NNT80% SE)"),
        ("(Imagen + básicos) − Imagen invertida en el AUC", IS, lambda o: invertir(o, IB, "auc"),
         "mejora el AUC de forma distinguible"),
        ("(Imagen + básicos) − Imagen, la pAUC excluye el cero", IS, lambda o: excluir_cero(o, IB, "pauc"),
         "un intervalo que, con la precisión guardada, no excluye el cero"),
        ("(Imagen + básicos) − Imagen, la sensibilidad top-15 excluye el cero", IS,
         lambda o: excluir_cero(o, IB, "setop15"), "en las otras tres métricas la mejora no se da por establecida"),
        ("Imagen − M1, un pliegue ganado de más en la pAUC", IS,
         lambda o: victoria_de_mas(o, IM1, "pauc", "nuevo_mejor_en_folds"), "Imagen − M1: los pliegues y las semillas"),
        ("Imagen − M1, una semilla ganada de más en el AUC", IS,
         lambda o: victoria_de_mas(o, IM1, "auc", "nuevo_mejor_en_semillas"), "Imagen − M1: los pliegues y las semillas"),
        ("(Imagen + básicos) − Imagen, un pliegue ganado de menos en el AUC", IS,
         lambda o: victoria_de_menos(o, IB, "auc", "nuevo_mejor_en_folds"),
         "(Imagen + básicos) − Imagen: los pliegues y las semillas"),
        ("(Imagen + básicos) − Imagen, una semilla ganada de menos en el NNT80% SE", IS,
         lambda o: victoria_de_menos(o, IB, "nnt80", "nuevo_mejor_en_semillas"),
         "(Imagen + básicos) − Imagen: los pliegues y las semillas"),
        ("tiempo-inferencia.json con un tiempo de la imagen sola", "tiempo-inferencia", tiempo_de_la_imagen_sola,
         "El tiempo de inferencia de la imagen sola no se midió"),
        ("imagen-sola.json con segundos", IS, segundos_en_imagen_sola,
         "El tiempo de inferencia de la imagen sola no se midió"),
        ("M1 sin la variable sex", "modelado-baseline", sin_sexo, "M1 también usa la edad y el sexo"),
        ("M4 más barato que M3 limpio al predecir", "tiempo-inferencia", m4_barato,
         "Lo caro, con diferencia, es la imagen, y ni M4 ni M4b"),
        ("M4b − M2 establecida en la pAUC (viñeta de DINOv2)", "fase4-m4b-vs-m2", m4b_establecida,
         "Añadidas al modelo con contexto de paciente, las variables de imagen de DINOv2"),
    ]

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
        "K": generar("K", lambda d: cambiar(d, "sintesis-verificacion", grupos_que_no_suman)),
    }
    for i, (_, archivo, cambio, _) in enumerate(casos_l):
        corridas[f"L{i}"] = generar(f"L{i}", lambda d, a=archivo, c=cambio: cambiar(d, a, c))
    f_ok, f_detalle = caso_f()
    m = caso_m()

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
        ("K. los cinco grupos de la verificación no suman el total: no escribe, por la suma",
         not corridas["K"][0] and "suman" in corridas["K"][2], f"escrita: {corridas['K'][0]}; {corridas['K'][2]}"),
    ] + [
        (f"L. {titulo}: no escribe, por esa frase",
         not corridas[f"L{i}"][0] and frase in corridas[f"L{i}"][2], f"escrita: {corridas[f'L{i}'][0]}; {corridas[f'L{i}'][2]}")
        for i, (titulo, _, _, frase) in enumerate(casos_l)
    ] + [
        ("M. copias sin tocar: se leen el 0,922 y las citas", *m["base"]),
        ("M. fila de solo recortes duplicada en la Tabla 3: no se lee", *m["tabla"]),
        ("M. cita quitada de su archivo: no se escribe", *m["cita"]),
        ("M. cita de los datos básicos quitada de Kurtansky 2025: no se escribe", *m["cita_basicos"]),
    ]
    fallos = 0
    for titulo, ok, detalle in casos:
        print(f"[{'OK' if ok else 'FALLA'}] {titulo}\n      {detalle}")
        fallos += not ok
    print(f"\n{len(casos) - fallos} de {len(casos)} casos como se esperaba.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

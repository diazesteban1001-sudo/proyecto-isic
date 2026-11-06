#!/usr/bin/env python3
"""
generar_demo.py — construye informe/demo.html, la síntesis en formato
presentación.

Etapa 4 de la skill sintesis-consultoria. El HTML no se escribe a mano:
se genera desde outputs/*.json igual que el informe, para que una
corrección en los instrumentos llegue a los dos entregables o a
ninguno. Un número tecleado en la plantilla sería una cifra inventada.

El texto fijo sale de frases ya verificadas de informe/borrador-v2.md; los
comentarios de la plantilla dan la línea de cada una. Las frases cuya verdad
depende de los datos se comprueban al generar (afirmar): si una deja de ser
cierta, no se escribe la página.

Los datos van embebidos en el archivo, no se piden con fetch: la demo
tiene que abrir con doble clic desde una USB, sin servidor.

Uso:
    python generar_demo.py --outputs-dir outputs/ --salida informe/demo.html
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")


# Los .md de cada instrumento se muestran al hacer clic en su casilla del
# diagrama. sintesis-consultoria no mide nada, así que no tiene un .md de
# resultados propio: se le asocia el de la verificación de trazabilidad,
# que es lo que esta skill sí produce como evidencia de su trabajo.
# Los textos de las cuatro primeras etapas son los de antes; los de la
# extracción, el modelado y la síntesis, los de huecos-demo.md, Parte B.
# «palabra» es lo único que la tira muestra de cada etapa; el nombre y la
# función pasan al «Detalle» de la sección (rediseño, paso 1, 2026-11-06).
CADENA = [
    {
        "nombre": "eda-diagnostico",
        "etapa": "Diagnóstico del dataset",
        "palabra": "Diagnóstico",
        "tipo": "medición",
        "funcion": "Se perfiló el archivo: tipos, faltantes, desbalance y estructura de grupos por paciente",
        "md": "eda-diagnostico",
        "mide": "Estructura del archivo, tipos, faltantes por columna, desbalance de la "
                "respuesta, tamaño de los grupos y qué columnas existen en train pero no en test.",
        "porque": "Ninguna decisión de diseño posterior se puede tomar sin esto. El esquema de "
                  "validación depende de la estructura de grupos, y la auditoría de fugas parte "
                  "de la lista de columnas asimétricas.",
    },
    {
        "nombre": "diseno-validacion",
        "etapa": "Diseño de la validación",
        "palabra": "Validación",
        "tipo": "medición",
        "funcion": "Se construyó y se verificó la validación cruzada agrupada por paciente",
        "md": "diseno-validacion",
        "mide": "Se construyeron los folds agrupando por paciente y estratificando por clase, y "
                "después se comprobó que ningún paciente cruzara de un lado al otro. Además se "
                "cuantificó cuánta fuga habría producido no hacerlo.",
        "porque": "Proponer un esquema es barato; verificarlo es lo que lo convierte en evidencia. "
                  "Sin la comparación contra la partición ingenua, «hay que agrupar por paciente» "
                  "es una recomendación de manual y no un hallazgo sobre estos datos.",
    },
    {
        "nombre": "auditoria-de-fugas",
        "etapa": "Auditoría de fugas",
        "palabra": "Fugas",
        "tipo": "medición",
        "funcion": "Se auditó la fuga estructural y se escaneó columna por columna",
        "md": "auditoria-de-fugas",
        "mide": "Dos cosas distintas: fuga estructural —columnas ausentes en test, constantes, "
                "identificadores— y fuga oculta, entrenando un modelo por columna sobre los folds "
                "agrupados para ver si alguna predice el objetivo sospechosamente bien.",
        "porque": "Es el paso adversario: existe para encontrar defectos, no para "
                  "confirmar que todo está bien. Un chequeo que no puede fallar no vale nada.",
    },
    {
        "nombre": "extraccion-imagen",
        "etapa": "Extracción de imagen",
        "palabra": "Imagen",
        "tipo": "medición",
        "funcion": "Se extrajeron características congeladas de cada imagen con DINOv2, sin ajuste fino",
        "md": "extraccion-imagen",
        # «mide» lleva cifras, así que se arma en la página (MIDE).
        "mide": None,
        "porque": "Para medir si la imagen añade algo a la metadata, y a qué costo, sin ajustar "
                  "la red: las características se extraen una vez y alimentan M4 y M4b.",
    },
    {
        "nombre": "modelado-baseline",
        "etapa": "Modelos de referencia",
        "palabra": "Modelos",
        "tipo": "medición",
        "funcion": "Se entrenaron y evaluaron los niveles de referencia, los modelos M1 a M4b, los "
                   "intentos de mejorar al recomendado de las fases 4b a 4e y las redes de imagen "
                   "entrenadas, sobre pliegues agrupados por paciente; al final, el conjunto reservado, "
                   "una sola vez, y los envíos a Kaggle",
        "md": "modelado-baseline",
        "mide": "Primero, los niveles de referencia con la métrica oficial. Después, los modelos "
                "M1 a M4b en validación cruzada repetida, en cuatro métricas —la pAUC, el AUC "
                "estándar, la sensibilidad top-15 y el NNT80% SE—, y el tiempo de inferencia de "
                "todos menos M3.",
        "porque": "Los niveles existen para acotar: sin la referencia univariada no se sabe "
                  "cuánto aporta combinar columnas. Y ninguna conclusión comparativa se escribe "
                  "desde una sola partición: dos veces, un resultado de una sola partición no "
                  "sobrevivió a la validación repetida.",
    },
    {
        "nombre": "sintesis-consultoria",
        "etapa": "Síntesis y verificación",
        "palabra": "Síntesis",
        "tipo": "interpretación",
        "funcion": "Se cruzaron las cinco salidas, se redactó el informe y se verificó su trazabilidad",
        # No mide nada, así que no tiene un .md de resultados propio: se le
        # asocia el de la verificación de trazabilidad, que es la evidencia
        # de que hizo su trabajo.
        "md": "sintesis-verificacion",
        "mide": "Nada. Es la única etapa que interpreta: cruza las cinco salidas anteriores, "
                "resuelve sus contradicciones y emite la recomendación. Lo que sí hace es "
                "verificarse a sí misma: extrae cada número del informe y busca su respaldo en "
                "outputs/.",
        "porque": "Es el trabajo del consultor, y está separado de las etapas de medición a "
                  "propósito: una etapa que interpretara sus propios resultados tendería a "
                  "justificarlos.",
    },
]

# Las cinco comparaciones de la Fase 4, en el orden de «Resultados».
COMPARACIONES = [
    ("M2 − M1", "fase4-m2-vs-m1"),
    ("M4 − M2", "fase4-m4-vs-m2"),
    ("M4b − M2", "fase4-m4b-vs-m2"),
    ("M3 − M2", "fase4-m3-vs-m2"),
    ("M3 limpio − M2", "fase4-m3limpio-vs-m2"),
]
METRICAS = ["pauc", "auc", "setop15", "nnt80"]
# Las filas de la tabla de tres ejes: M3 sin limpiar queda fuera, porque no es
# candidato y su camino de predicción no se cronometró (decisión de la persona,
# 2026-10-02).
TABLA = [
    ("M1", "fase4-m2-vs-m1", "M1"),
    ("M2", "fase4-m2-vs-m1", "M2"),
    ("M3 limpio", "fase4-m3limpio-vs-m2", "M3limpio"),
    ("M4", "fase4-m4-vs-m2", "M4"),
    ("M4b", "fase4-m4b-vs-m2", "M4b"),
]
# Los tres candidatos de la Fase 4b contra M3 limpio (PLAN.md, Fase 4b), en su
# orden. La regla de la fase usa el intervalo con la confianza de Bonferroni.
FASE4B = [
    ("M3 limpio mezclado con M2", "fase4b-c1-vs-m3limpio"),
    ("M3 limpio con las dos variables de imagen de M4b", "fase4b-c2-vs-m3limpio"),
    ("M3 limpio mezclado con un segundo boosting", "fase4b-c3-vs-m3limpio"),
]
CLAVE_BONFERRONI = "intervalo_bonferroni_nadeau_bengio"
# Las dos preguntas de la Fase 4c (PLAN.md, Fase 4c), en su orden: su etiqueta en
# la tabla, su archivo y los nombres de modelo que trae. La regla usa también el
# intervalo de Bonferroni, aquí a 1 − 0,05/2.
FASE4C = {
    "red_sola": ("La red sola frente a la imagen sola con DINOv2", "fase4c-red-sola-vs-imagen", "Red", "Imagen"),
    "c4": ("M3 limpio con la red frente a M3 limpio", "fase4c-c4-vs-m3limpio", "C4", "M3limpio"),
}
# Las cinco preguntas de las fases 4d y 4e (PLAN.md), en su orden, con su
# etiqueta, su archivo y los modelos que compara. La regla de las dos fases es
# Holm sobre el valor p bilateral de Nadeau y Bengio, y el intervalo que se
# muestra es el de Nadeau y Bengio al 95 %.
FASE4DE = [
    ("4d", "M3 limpio con las variables de imagen del ganador, sin el hospital (C5)", "fase4d-c5-vs-m3limpio", "C5", "M3limpio"),
    ("4d", "La red con más épocas frente a la red de la Fase 4c", "fase4d-red-mejorada-vs-red", "RedMejorada", "Red"),
    ("4d", "C5 con esa red (C6)", "fase4d-c6-vs-m3limpio", "C6", "M3limpio"),
    ("4e", "La red con la receta del 10.º puesto frente a la de la Fase 4c", "fase4e-red-vs-red4c", "Red4eAjustada", "Red"),
    ("4e", "M3 limpio con esa red (C7)", "fase4e-c7-vs-m3limpio", "C7", "M3limpio"),
]
CLAVE_IC_NB = "intervalo_t_95_nadeau_bengio"
# Los ocho envíos a Kaggle (PLAN.md, fases 5b y 5c), con su nombre en la página.
NOMBRES_KAGGLE = {"M3limpio": "M3 limpio", "Red4e": "Red de la 4e", "C7": "C7", "ImagenBasicos": "«Imagen + básicos»",
                  "M3limpioProm": "M3 limpio promediado", "M3limpioPromHosp": "M3 limpio promediado + hospital",
                  "C7Prom": "C7 promediado", "C7PromHosp": "C7 promediado + hospital"}
NIVELES_VR = [
    ("Nivel 1", "Regresión logística", "nivel_1_regresion_logistica"),
    ("Nivel 2a", "Gradient boosting sin balancear", "nivel_2a_gradient_boosting_sin_balancear"),
    ("Nivel 2b", "Gradient boosting balanceado", "nivel_2b_gradient_boosting_balanceado"),
]
# La cita de PanDerm se lee de su texto versionado al generar: así se
# comprueba cada vez, y su cifra no se teclea.
CITA_PANDERM = ("referencias/panderm-reduccion-examenes.md",
                re.compile(r"(We selected a subset containing )([\d,]+)( tile images, stratified by institutions)"))
# borrador-v2.md, «La imagen sola, sin el sistema de fotografía corporal total» y
# «Recomendación»: las citas literales que la página muestra se leen de aquí y se
# comprueban contra su archivo; si una deja de estar, no se escribe la página.
KURTANSKY_2025 = "referencias/kurtansky-2025-triaje-automatizado-tbp.md"
KURTANSKY_2024 = "referencias/kurtansky-2024-slice3d-descriptor.md"
CITAS_IMAGEN_SOLA = {
    "costo_tbp": (KURTANSKY_2025, "less accessible and more expensive than standard clinical and dermoscopic imaging methods"),
    "lesiones_sueltas": (KURTANSKY_2025, "cannot be directly applied to analyze single lesions at a time"),
    "telefono": (KURTANSKY_2024, "clinical photos resembling the resolution of smartphone images"),
    "luz_y_campo": (KURTANSKY_2024, "vary greatly in lighting and FOV"),
    "datos_basicos": (KURTANSKY_2025, "are not directly attained from images"),
}


def leer(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def cargar_json(outputs_dir, nombre, leidos):
    """Lee outputs/<nombre>.json y lo anota en `leidos`. El aviso de estado
    revisa todo lo que pasó por aquí, no una lista escrita a mano: un archivo
    que la página empiece a leer queda cubierto sin tocar el aviso."""
    contenido = json.loads(leer(os.path.join(outputs_dir, f"{nombre}.json")))
    leidos[nombre] = contenido
    return contenido


def afirmar(condicion, frase):
    """Las frases del texto fijo que dicen algo de los datos se comprueban
    contra los datos. Si una deja de ser cierta, la página no se escribe."""
    if not condicion:
        raise SystemExit(f"La frase «{frase}» ya no es cierta con outputs/. No se escribe la página.")


# Los grupos en que la verificación reparte los números del borrador, además
# de numeros_con_respaldo_en_outputs, que es un recuento y no una lista.
GRUPOS_VERIFICACION = ("numeros_sin_respaldo", "porcentajes_de_metodo_excluidos",
                       "numeros_en_contextos_omitidos", "numeros_en_comentarios")


def comprobar_suma_verificacion(verificacion):
    """La ficha de síntesis reparte el total de números en cinco grupos. Si no
    suman el total, la frase que los enumera sería falsa: no se escribe la
    página. Control positivo: test_generar_demo.py, caso K."""
    try:
        grupos = verificacion["numeros_con_respaldo_en_outputs"] + sum(
            len(verificacion[g]) for g in GRUPOS_VERIFICACION)
    except KeyError as e:
        raise SystemExit(f"sintesis-verificacion.json no trae el grupo {e}. No se escribe la página.")
    if grupos != verificacion["numeros_en_borrador"]:
        raise SystemExit(
            f"Los cinco grupos de la verificación suman {grupos} y el borrador tiene "
            f"{verificacion['numeros_en_borrador']} números. No se escribe la página.")


def contiene_cero(ic):
    return ic[0] <= 0 <= ic[1]


def extraer(patron, texto, que):
    m = re.search(patron, texto)
    if not m:
        raise SystemExit(f"No se encontró {que} en «{texto}». No se escribe la página.")
    return m


def auc_solo_recortes():
    """El AUC de la variante del ganador que solo usa los recortes, en la tarea de
    cáncer de piel: la única fila de la Tabla 3 de Kurtansky 2025 con solo la
    columna Tiles marcada, entre «Malignancy classification» y «Melanoma
    classification». Se lee del archivo, no se teclea."""
    lineas = leer(os.path.join(RAIZ, KURTANSKY_2025)).split("\n")
    ini = next(i for i, l in enumerate(lineas) if l.startswith("Malignancy classification\t"))
    fin = next(i for i, l in enumerate(lineas) if l.startswith("Melanoma classification\t"))
    cabecera = [i for i in range(ini, fin) if "\tMeta-basic\tMeta-WB360\tTiles\tPatient context" in lineas[i]]
    filas = [(i, re.fullmatch(r"\t\t\t\tx\t\t(\d\.\d+)\t(\d\.\d+)\t.*", lineas[i])) for i in range(ini, fin)]
    filas = [(i, m) for i, m in filas if m]
    if len(cabecera) != 1 or len(filas) != 1:
        raise SystemExit(f"La fila de solo recortes de la Tabla 3 no está una sola vez en {KURTANSKY_2025}. "
                         f"No se escribe la página.")
    i, m = filas[0]
    return {"auc": float(m.group(2)), "fuente": f"{KURTANSKY_2025}, Tabla 3, línea {i + 1} (solo la columna Tiles)"}


def victorias_coherentes(comp, n_splits, n_semillas):
    """Los conteos de pliegues y semillas en que gana el nuevo, contra sus
    diferencias por pliegue. Las diferencias están redondeadas a 4 decimales y
    los conteos se hicieron sin redondear, así que cada conteo tiene que caer
    entre el recuento estricto y el que cuenta como victoria lo que el
    redondeo dejó en el límite (media unidad del cuarto decimal)."""
    tol = 5e-5
    for k in METRICAS:
        x, d = comp[k], comp[k]["diferencias_nuevo_menos_base"]
        signo = 1 if x["mayor_es_mejor"] else -1
        if not (len(d) == x["de_folds"] == n_splits * n_semillas and x["de_semillas"] == n_semillas):
            return False
        if not sum(signo * v > 0 for v in d) <= x["nuevo_mejor_en_folds"] <= sum(signo * v >= 0 for v in d):
            return False
        medias = [sum(d[i * n_splits:(i + 1) * n_splits]) / n_splits for i in range(n_semillas)]
        if not sum(signo * m > tol for m in medias) <= x["nuevo_mejor_en_semillas"] <= sum(signo * m > -tol for m in medias):
            return False
    return True


def claves_anidadas(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from claves_anidadas(v)
    elif isinstance(o, list):
        for v in o:
            yield from claves_anidadas(v)


# Los modelos cuyo tiempo de inferencia está medido (outputs/tiempo-inferencia.json > tiempos).
MODELOS_CRONOMETRADOS = {"M1", "M2", "M3limpio", "M4", "M4b"}


def datos_imagen_sola(imagen_sola, escala, modelado, fase4, extraccion, tiempo):
    """Cifras de «La imagen sola, sin el sistema de fotografía corporal total» y
    las frases que dependen de ellas. Control positivo: test_generar_demo.py,
    caso L, con un archivo alterado que rompe cada frase."""
    m, c = imagen_sola["metricas"], imagen_sola["comparaciones_nuevo_menos_base"]
    clave_ic = "intervalo_t_95_nadeau_bengio"
    ctrl = imagen_sola["control_m1_contra_referencia"]
    afirmar(ctrl["m1_reproduce_fold_a_fold"] and ctrl["huellas_de_pliegues_iguales"], "en los mismos pliegues de M1")
    m3_brutas = fase4["fase4-m3-vs-m2"]["m3"]["variables"]["entran"]["numericas_brutas"]
    afirmar(all(any(v.startswith("tbp_lv_") for v in lista) for lista in
                (modelado["features_usadas"], fase4["fase4-m2-vs-m1"]["variables_de_contexto"], m3_brutas)),
            "Las mediciones de las que dependen M1, M2 y M3 limpio las calcula el software de la fotografía corporal total")
    afirmar({"age_approx", "sex"} <= set(modelado["features_usadas"]), "M1 también usa la edad y el sexo")
    pliegues = [v for s in imagen_sola["esquema"]["semillas"] for v in m["Imagen"]["pauc"]["por_semilla_y_fold"][str(s)]]
    afirmar(all(v > escala["azar"] for v in pliegues), "La imagen sola distingue lesiones malignas muy por encima del azar")
    im1 = c["imagen_menos_m1"]
    for k, frase in (("pauc", "la pAUC"), ("auc", "el AUC"), ("setop15", "la sensibilidad top-15")):
        afirmar(im1[k]["media"] < 0 and im1[k][clave_ic][1] < 0,
                f"queda por debajo de M1 en las cuatro métricas, y las cuatro diferencias están establecidas ({frase})")
    afirmar(im1["nnt80"]["media"] > 0 and im1["nnt80"][clave_ic][0] > 0,
            "queda por debajo de M1 en las cuatro métricas, y las cuatro diferencias están establecidas (el NNT80% SE)")
    n_splits, n_semillas = imagen_sola["esquema"]["n_splits"], len(imagen_sola["esquema"]["semillas"])
    afirmar(victorias_coherentes(im1, n_splits, n_semillas),
            "Imagen − M1: los pliegues y las semillas en que gana el nuevo, entre paréntesis")
    afirmar(not any(re.search(r"tiempo|segundo", k) for k in claves_anidadas(imagen_sola))
            and set(tiempo["tiempos"]) <= MODELOS_CRONOMETRADOS,
            "El tiempo de inferencia de la imagen sola no se midió")
    ib = c["imagen_basicos_menos_imagen"]
    afirmar(ib["auc"]["media"] > 0 and ib["auc"][clave_ic][0] > 0,
            "Añadir edad, sexo y zona del cuerpo mejora el AUC de forma distinguible")
    afirmar(contiene_cero(ib["pauc"][clave_ic]), "un intervalo que, con la precisión guardada, no excluye el cero")
    afirmar(all(contiene_cero(ib[k][clave_ic]) for k in ("pauc", "setop15", "nnt80"))
            and ib["pauc"]["media"] > 0 and ib["setop15"]["media"] > 0 and ib["nnt80"]["media"] < 0,
            "en las otras tres métricas la mejora no se da por establecida")
    afirmar(victorias_coherentes(ib, n_splits, n_semillas),
            "(Imagen + básicos) − Imagen: los pliegues y las semillas en que gana el nuevo, entre paréntesis")
    citas = {}
    for clave, (ruta, texto) in CITAS_IMAGEN_SOLA.items():
        if texto not in leer(os.path.join(RAIZ, ruta)):
            raise SystemExit(f"La cita «{texto}» no está en {ruta}. No se escribe la página.")
        citas[clave] = texto
    return {
        "n_variables": int(extraer(r"(\d+) dimensiones", extraccion["caracteristica"],
                                   "las dimensiones de la característica").group(1)),
        "medias": {mod: {k: m[mod][k]["media_global"] for k in METRICAS} for mod in ("M1", "Imagen", "Imagen + básicos")},
        "comp": {n: {k: {"media": c[n][k]["media"], "ic": c[n][k][clave_ic],
                         "folds": c[n][k]["nuevo_mejor_en_folds"], "de_folds": c[n][k]["de_folds"],
                         "semillas": c[n][k]["nuevo_mejor_en_semillas"], "de_semillas": c[n][k]["de_semillas"]}
                     for k in METRICAS}
                 for n in ("imagen_menos_m1", "imagen_basicos_menos_imagen")},
        "clave_ic": clave_ic,
        "auc_recortes": auc_solo_recortes(),
        "citas": citas,
    }


def rango_de_semillas(semillas):
    """«semillas a a b»: el rótulo solo es cierto si las semillas son consecutivas."""
    afirmar(semillas == list(range(semillas[0], semillas[-1] + 1)),
            f"las semillas {semillas} se pueden rotular como un rango")
    return f"semillas {semillas[0]} a {semillas[-1]}"


def datos_imagen_barras(cargar, imagen_sola):
    """Rediseño, paso 2, gráfico 2: la pAUC media de los cuatro modelos de imagen
    sin el sistema de fotografía corporal total, con M1 como referencia, cada uno
    con sus semillas. La barra de la red de la 4e sale de la Fase 4f, que la
    compara con «Imagen + básicos»; solo es la red de la Fase 4e si esa fase la
    reproduce. Control: test_generar_demo.py, caso T2."""
    red4c = cargar("fase4c-red-sola-vs-imagen")
    f4f = cargar("fase4f-red4e-vs-imagen-basicos")
    f4e = cargar("fase4e-red-vs-red4c")
    afirmar(f4f["reproduccion_de_la_red"]["reproduce_fold_a_fold"]
            and f4f["metricas"]["Red4eAjustada"]["pauc"]["media_global"]
            == f4e["metricas"]["Red4eAjustada"]["pauc"]["media_global"],
            "La barra de la red de la 4e es la red de la Fase 4e: fase4f-red4e-vs-imagen-basicos.json la reproduce")
    sem_is = imagen_sola["esquema"]["semillas"]
    barras = [
        ("Imagen", "imagen-sola.json", "metricas.Imagen.pauc.media_global",
         imagen_sola["metricas"]["Imagen"]["pauc"]["media_global"], sem_is, "esquema.semillas"),
        ("Imagen + básicos", "imagen-sola.json", "metricas.Imagen + básicos.pauc.media_global",
         imagen_sola["metricas"]["Imagen + básicos"]["pauc"]["media_global"], sem_is, "esquema.semillas"),
        ("Red de la 4c", "fase4c-red-sola-vs-imagen.json", "metricas.Red.pauc.media_global",
         red4c["metricas"]["Red"]["pauc"]["media_global"], red4c["semillas_corridas"], "semillas_corridas"),
        ("Red de la 4e", "fase4f-red4e-vs-imagen-basicos.json", "metricas.Red4eAjustada.pauc.media_global",
         f4f["metricas"]["Red4eAjustada"]["pauc"]["media_global"], f4f["semillas_corridas"], "semillas_corridas"),
    ]
    return {
        "barras": [{"etiqueta": e, "archivo": a, "campo": c, "pauc": v, "semillas": rango_de_semillas(sem),
                    "campo_semillas": cs} for e, a, c, v, sem, cs in barras],
        "m1": {"pauc": imagen_sola["metricas"]["M1"]["pauc"]["media_global"], "semillas": rango_de_semillas(sem_is)},
    }


# Rediseño, paso 2, gráfico 5: las siete versiones que se compararon con M3 limpio,
# con el intervalo que usó la regla de su fase. En las fases 4b y 4c, el de
# Bonferroni; en la 4d y la 4e, cuya regla es Holm sobre el valor p, el de Nadeau y
# Bengio al 95 %, que no es el que decide.
SIETE_VERSIONES = [
    ("C1", "fase4b-c1-vs-m3limpio", CLAVE_BONFERRONI),
    ("C2", "fase4b-c2-vs-m3limpio", CLAVE_BONFERRONI),
    ("C3", "fase4b-c3-vs-m3limpio", CLAVE_BONFERRONI),
    ("C4", "fase4c-c4-vs-m3limpio", CLAVE_BONFERRONI),
    ("C5", "fase4d-c5-vs-m3limpio", "intervalo_t_95_nadeau_bengio"),
    ("C6", "fase4d-c6-vs-m3limpio", "intervalo_t_95_nadeau_bengio"),
    ("C7", "fase4e-c7-vs-m3limpio", "intervalo_t_95_nadeau_bengio"),
]


def datos_siete_versiones(cargar):
    """Las filas del gráfico 5 y la banda de lo que la prueba alcanza a ver al 80 %
    (potencia-nadeau-bengio.json > comparaciones.*.delta_80). La banda se calculó
    con la variabilidad de C4 a C7, y solo vale para esas filas si son las mismas
    comparaciones. Control: test_generar_demo.py, caso T5."""
    filas = []
    for nombre, archivo, clave in SIETE_VERSIONES:
        o = cargar(archivo)
        if (o["comparacion"]["nuevo"], o["comparacion"]["base"]) != (nombre, "M3limpio"):
            raise SystemExit(f"{archivo}.json no compara {nombre} con M3 limpio. No se escribe la página.")
        p = o["comparaciones_nuevo_menos_base"]["pauc"]
        filas.append({"nombre": nombre, "archivo": f"{archivo}.json", "media": p["media"], "ic": p[clave], "clave_ic": clave,
                      "confianza": p.get("confianza_bonferroni") if clave == CLAVE_BONFERRONI else None})
    pc = cargar("potencia-nadeau-bengio")["comparaciones"]
    medias = {f["nombre"]: f["media"] for f in filas}
    afirmar(sorted(pc) == ["C4", "C5", "C6", "C7"] and all(pc[k]["media_observada"] == medias[k] for k in pc),
            "La banda del 80 % se calculó con las mismas comparaciones que el gráfico muestra de C4 a C7")
    d80 = [v for k in pc for v in pc[k]["delta_80"].values()]
    return {"filas": filas, "banda": [min(d80), max(d80)], "banda_de": sorted(pc)}


def datos_mecanismo(mecanismo, metrica):
    """borrador-v2.md, «Una decisión por defecto cambia el veredicto», el
    párrafo de cómo falla el 2a (outputs/mecanismo-2a.json). Los porcentajes
    se calculan aquí desde los campos; ninguno se teclea."""
    m2a = mecanismo["niveles"]["nivel_2a_gradient_boosting_sin_balancear"]["total"]
    m2b = mecanismo["niveles"]["nivel_2b_gradient_boosting_balanceado"]["total"]
    percentil = int(extraer(r"percentil (\d+) de las probabilidades de los negativos",
                            mecanismo["definiciones"]["p20_neg / frac_pos_bajo_p20_neg"],
                            "el percentil de los negativos").group(1))
    # Capturar el tpr% de los positivos deja fuera la cola de 100 − tpr: su
    # decil en deciles_rango_pos (10, 20, …, 90) es el que dice dónde cae.
    cola = 100 - metrica["tpr"]
    afirmar(cola % 10 == 0 and 10 <= cola <= 90,
            "el umbral tiene que bajar hasta el … de positivos de menor rango (un decil)")
    indice = cola // 10 - 1
    decil = m2a["deciles_rango_pos"][indice]
    marcadas = math.floor((1 - decil) * 100)
    afirmar(m2a["frac_neg_ge_0999"] < m2a["frac_pos_ge_0999"],
            "No es que ponga arriba a más negativos que positivos, en proporción")
    afirmar(marcadas > metrica["tpr"],
            "Ahí queda marcado más del … de las lesiones, cuando al azar quedaría marcado el …")
    return {
        "seed": mecanismo["esquema_cv"]["seed"],
        "umbral_alto": mecanismo["umbral_alto"],
        "neg_alto": round(m2a["frac_neg_ge_0999"] * 100, 2),
        "pos_alto": round(m2a["frac_pos_ge_0999"] * 100, 2),
        "percentil": percentil,
        "pos_bajo": round(m2a["frac_pos_bajo_p20_neg"] * 100, 2),
        "pos_bajo_2b": round(m2b["frac_pos_bajo_p20_neg"] * 100, 2),
        "n_pos_min": m2a["n_pos_en_el_minimo"],
        "n_neg_min": m2a["n_neg_en_el_minimo"],
        "minimo": m2a["minimo_predicho"],
        "cola": cola,
        "indice_decil": indice,
        "decil": round(decil * 100, 2),
        "marcadas": marcadas,
    }


def datos_particion(particion):
    """borrador-v2.md, «Una ventaja que la pAUC no ve» y «Partir por filas no
    cambia el veredicto» (outputs/efecto-particion.json)."""
    clave_ic = "intervalo_t_95_nadeau_bengio"
    afirmar(all(c["coincide"] for c in particion["control_paciente_contra_referencia"].values()),
            "la partición por paciente reproduce la validación repetida pliegue a pliegue")
    cp = particion["particiones"]["paciente"]["comparacion_2b_menos_1"]
    cf = particion["particiones"]["filas"]["comparacion_2b_menos_1"]
    fmp = particion["filas_menos_paciente"]
    n1, n2b = "nivel_1_regresion_logistica", "nivel_2b_gradient_boosting_balanceado"
    afirmar(contiene_cero(cp["pauc"][clave_ic]) and cp["auc"][clave_ic][0] > 0 and cp["setop15"][clave_ic][0] > 0
            and cp["nnt80"][clave_ic][1] < 0,
            "En las otras tres métricas sí lo está … la pAUC no distingue una ventaja que las métricas de triaje sí distinguen")
    en_la_regla = [(n, m) for n in (n1, n2b) for m in ("pauc", "auc", "nnt80")
                   if fmp[n][m]["semillas_filas_mejor"] == fmp[n][m]["de_semillas"]]
    afirmar(not en_la_regla and contiene_cero(cp["pauc"][clave_ic]) and contiene_cero(cf["pauc"][clave_ic]),
            "No se cumple ninguna de las dos")
    afirmar(fmp[n1]["auc"]["semillas_filas_mejor"] == fmp[n1]["nnt80"]["semillas_filas_mejor"],
            "En el AUC y el NNT80% SE de la logística da mejor en … de …")
    afirmar(fmp[n1]["setop15"]["diferencia_de_medias"] > 0 and fmp[n2b]["setop15"]["diferencia_de_medias"] > 0,
            "La sensibilidad top-15 sí sube con filas")
    return {
        "otras": {k: {"media": cp[k]["media"], "ic": cp[k][clave_ic],
                      "folds": cp[k]["nivel_2b_mejor_en_pliegues"], "de_folds": cp[k]["de_pliegues"],
                      "semillas": cp[k]["nivel_2b_mejor_en_semillas"], "de_semillas": cp[k]["de_semillas"]}
                  for k in ("auc", "setop15", "nnt80")},
        "ic_paciente": cp["pauc"][clave_ic],
        "ic_filas": cf["pauc"][clave_ic],
        "semillas": len(particion["esquema"]["semillas"]),
        "filas_menos_paciente": {
            corto: {m: {"dif": fmp[n][m]["diferencia_de_medias"], "mejor": fmp[n][m]["semillas_filas_mejor"]}
                    for m in ("pauc", "auc", "nnt80")}
            for corto, n in (("n1", n1), ("n2b", n2b))
        },
    }


def datos_fases_4d_a_5c(cargar):
    """borrador-v2.md, «Resultados»: el final de «La imagen sola» (la red de la 4e
    y la Fase 4f), el de «El modelo recomendado» (las fases 4d y 4e), «Lo que la
    prueba alcanza a ver», «El conjunto reservado, abierto una sola vez» y «En la
    prueba de Kaggle»; y lo que de ellas usa «Recomendación». Cada frase que dice
    algo de los datos se comprueba aquí. Control positivo: test_generar_demo.py,
    caso R."""
    preguntas = []
    for fase, etiqueta, archivo, nuevo, base in FASE4DE:
        o = cargar(archivo)
        if (o["comparacion"]["nuevo"], o["comparacion"]["base"]) != (nuevo, base):
            raise SystemExit(f"{archivo}.json no compara {nuevo} con {base}. No se escribe la página.")
        c = o["comparaciones_nuevo_menos_base"]
        preguntas.append({
            "fase": fase, "etiqueta": etiqueta, "archivo": f"{archivo}.json", "nuevo": nuevo, "base": base,
            "media_nuevo": o["metricas"][nuevo]["pauc"]["media_global"],
            "media_base": o["metricas"][base]["pauc"]["media_global"],
            "semillas_corridas": len(o["semillas_corridas"]),
            "metricas": {k: {"media": c[k]["media"], "ic": c[k][CLAVE_IC_NB], "p": c[k]["valor_p_nadeau_bengio"],
                             "folds": c[k]["nuevo_mejor_en_folds"], "de_folds": c[k]["de_folds"],
                             "semillas": c[k]["nuevo_mejor_en_semillas"], "de_semillas": c[k]["de_semillas"]}
                         for k in METRICAS},
        })
    Q = {q["nuevo"]: q for q in preguntas}
    holm = {"4d": cargar("fase4d-holm"), "4e": cargar("fase4e-holm")}
    for fase, h in holm.items():
        archivos = [p["archivo"] for p in h["preguntas"]]
        esperados = [f"outputs/{q['archivo']}" for q in preguntas if q["fase"] == fase]
        if sorted(archivos) != sorted(esperados):
            raise SystemExit(f"fase{fase}-holm.json no es la decisión de las preguntas de la Fase {fase}. No se escribe la página.")
        afirmar(not any(p["a_favor"] for p in h["preguntas"]),
                f"Holm no aceptó ninguna de las preguntas de la Fase {fase}, y M3 limpio siguió siendo el modelo recomendado")
    p_red = next(p for p in holm["4e"]["preguntas"] if p["archivo"] == "outputs/fase4e-red-vs-red4c.json")
    afirmar(p_red["orden_holm"] == 1 and p_red["umbral_holm"] < p_red["valor_p"] < holm["4e"]["alfa"],
            "Su valor p no llega al umbral de Holm para la primera de dos preguntas; con una sola pregunta, el umbral habría sido 0,05")
    red = Q["Red4eAjustada"]["metricas"]
    afirmar(red["pauc"]["media"] > 0 and red["pauc"]["ic"][0] > 0 and red["auc"]["ic"][0] > 0
            and red["setop15"]["ic"][0] > 0 and contiene_cero(red["nnt80"]["ic"]),
            "En el AUC y en la sensibilidad top-15 el intervalo también excluye el cero; en el NNT80% SE, no")

    potencia = cargar("potencia-nadeau-bengio")
    pc = potencia["comparaciones"]
    observadas = {k: v["media_observada"] for k, v in pc.items()}
    afirmar(set(pc) == {"C4", "C5", "C6", "C7"} and all(v > 0 for v in observadas.values()),
            "Las cuatro versiones que apilan una red de imagen sobre M3 limpio quedaron por encima de él en la media")
    afirmar(all(observadas[k] < min(pc[k]["delta_50"].values()) for k in pc),
            "las cuatro diferencias quedan por debajo del tamaño que la prueba distingue con un 50% de probabilidad")
    d80 = [v for k in pc for v in pc[k]["delta_80"].values()]
    d50 = [v for k in pc for v in pc[k]["delta_50"].values()]
    razones = [pc[k]["entre_semillas"]["ee_prueba_sobre_ee_semillas"] for k in pc]

    f4f = cargar("fase4f-red4e-vs-imagen-basicos")
    c4f = f4f["comparaciones_nuevo_menos_base"]
    afirmar(f4f["regla"]["a_favor"] and c4f["pauc"]["media"] > 0 and c4f["pauc"]["valor_p_nadeau_bengio"] < 0.05,
            "Con la regla de una sola pregunta, la red supera a «Imagen + básicos»")
    afirmar(c4f["auc"][CLAVE_IC_NB][0] > 0 and c4f["setop15"][CLAVE_IC_NB][0] > 0 and c4f["nnt80"][CLAVE_IC_NB][1] < 0,
            "Las tres métricas secundarias van en la misma dirección, con intervalos que excluyen el cero")

    reservado = cargar("fase5-reservado")
    dif = reservado["diferencia_m3limpio_menos_m2"]
    afirmar(dif["pauc"]["intervalo_95"][0] > 0 and dif["auc"]["intervalo_95"][0] > 0,
            "en el conjunto reservado, abierto una sola vez, la ventaja sobre M2 se mantiene en la pAUC y en el AUC")
    afirmar(contiene_cero(dif["setop15"]["intervalo_95"]) and contiene_cero(dif["nnt80"]["intervalo_95"]),
            "En la sensibilidad top-15 y el NNT80% SE, el intervalo contiene el cero, como en el desarrollo")
    posterior = cargar("fase5-posterior")
    rib = posterior["red4e_menos_imagen_basicos"]
    afirmar(all(contiene_cero(rib[k]["intervalo_95"]) for k in METRICAS) and rib["pauc"]["punto"] < 0,
            "La ventaja de la red sobre «Imagen + básicos» no se reprodujo")

    comparacion = cargar("fase5b-comparacion")
    efectos = cargar("fase5c-efectos")
    medicion = cargar("fase5b-kaggle-medicion")
    ganador = comparacion["referencias"]["ganador_tablero_privado"]["pauc"]
    privadas = {m: v["privada"] for m, v in efectos["kaggle"].items()}
    privadas.update({m: comparacion["kaggle"][m]["privada"] for m in ("Red4e", "ImagenBasicos")})
    afirmar(len(privadas) == 8 and max(privadas.values()) < ganador,
            "En la puntuación privada de Kaggle, ninguno de los ocho envíos llega a la del ganador")
    afirmar(max(privadas, key=privadas.get) == "C7PromHosp"
            and max((m for m in privadas if "Hosp" not in m), key=privadas.get) == "C7Prom",
            "El más cercano, «C7 promediado + hospital», y el más cercano sin la etiqueta del hospital, «C7 promediado»")
    ef = efectos["efectos"]
    afirmar(not ef["hospital_con_imagen"]["mismo_signo_en_la_publica"]
            and all(v["mismo_signo_en_la_publica"] for k, v in ef.items() if k != "hospital_con_imagen"),
            "el mayor de los dos efectos del hospital cambia de signo entre la puntuación pública y la privada")
    afirmar(privadas["Red4e"] > privadas["ImagenBasicos"], "en Kaggle la red vuelve a quedar por encima")
    tabla = comparacion["tabla_tres_evaluaciones"]
    dev = {m: next(d["pauc"] for d in tabla[m]["desarrollo"] if d["semillas"] == [5, 6, 7, 8, 9]) for m in tabla}
    kag = {m: tabla[m]["kaggle_privada"]["pauc"] for m in tabla}
    afirmar(sorted(dev, key=dev.get) == sorted(kag, key=kag.get)
            and tabla["ImagenBasicos"]["reservado"]["pauc"] > tabla["Red4e"]["reservado"]["pauc"],
            "En el desarrollo y en Kaggle, los cuatro modelos quedan en el mismo orden; en el reservado, «Imagen + básicos» queda por encima de la red")
    # Rediseño, paso 2, gráfico 3: los puntos del reservado salen de la tabla de tres
    # evaluaciones y su intervalo, de fase5-reservado.json. Solo se pueden dibujar
    # juntos si el punto de la tabla es el de ese archivo, y el modelo que la tabla
    # no evaluó en el reservado tampoco está en él. Control: test_generar_demo.py,
    # caso T3.
    afirmar(all((tabla[m]["reservado"] is None) == (m not in reservado["metricas"])
                and (tabla[m]["reservado"] is None
                     or tabla[m]["reservado"]["pauc"] == reservado["metricas"][m]["pauc"]["punto"])
                for m in tabla),
            "Los puntos del reservado de la tabla de tres evaluaciones son los de fase5-reservado.json, con su intervalo")
    # Gráfico 4 (rehecho el 2026-11-06): una barra con la distancia de C7 al ganador
    # partida en tres tramos, y debajo el recorrido de cuatro puntos en la misma
    # escala. Los tramos salen de descomposicion_de_la_distancia_al_ganador y los
    # puntos, de kaggle.*.privada; la figura solo es cierta si cada tramo es la
    # diferencia entre dos puntos seguidos, los tres suman la distancia, la
    # distancia es la de fase5b-comparacion.json y cada porcentaje es su tramo
    # sobre la distancia. Control: test_generar_demo.py, caso T4.
    des = efectos["descomposicion_de_la_distancia_al_ganador"]
    kp = {m: efectos["kaggle"][m]["privada"] for m in ("C7", "C7Prom", "C7PromHosp")}
    gan, dist = des["ganador"]["pauc"], des["distancia_de_c7_al_ganador"]
    cerca = lambda a, b: abs(a - b) < 5e-6
    tramos = {"promediar": des["cubre_promediar"], "hospital": des["cubre_el_hospital"], "queda": des["queda"]}
    afirmar(cerca(kp["C7"] - gan, dist) and cerca(kp["C7Prom"] - kp["C7"], tramos["promediar"])
            and cerca(kp["C7PromHosp"] - kp["C7Prom"], tramos["hospital"]) and cerca(kp["C7PromHosp"] - gan, tramos["queda"])
            and cerca(dist + tramos["promediar"] + tramos["hospital"], tramos["queda"])
            and dist == comparacion["comparaciones_con_la_privada"]["c7_menos_ganador"]["diferencia"]
            and all(abs(des["porcentaje_de_la_distancia"][k] - abs(v) / abs(dist) * 100) <= 0.05 + 1e-9 for k, v in tramos.items()),
            "La barra y el recorrido son la misma descomposición: cada tramo va de un punto del recorrido al siguiente, y los tres suman la distancia de C7 al ganador")
    proy = medicion["salida_del_notebook"]["tiempo"]
    return {
        "preguntas": preguntas,
        "holm": {f: {"alfa": h["alfa"], "preguntas": [{"archivo": p["archivo"], "umbral": p["umbral_holm"],
                                                       "a_favor": p["a_favor"]} for p in h["preguntas"]]}
                 for f, h in holm.items()},
        "red_holm": {"p": p_red["valor_p"], "umbral": p_red["umbral_holm"], "alfa": holm["4e"]["alfa"]},
        "potencia": {"obs_min": min(observadas.values()), "obs_max": max(observadas.values()),
                     "obs_min_de": min(observadas, key=observadas.get), "obs_max_de": max(observadas, key=observadas.get),
                     "d80": [min(d80), max(d80)], "d50": [min(d50), max(d50)],
                     "d80_c4": pc["C4"]["delta_80"], "d80_c7": pc["C7"]["delta_80"],
                     "razones": [min(razones), max(razones)], "termino": potencia["prueba"]["termino_de_correccion"],
                     "objetivos": potencia["objetivos"]},
        "fase4f": {"media_red": f4f["metricas"]["Red4eAjustada"]["pauc"]["media_global"],
                   "media_ib": f4f["metricas"]["ImagenBasicos"]["pauc"]["media_global"],
                   "metricas": {k: {"media": c4f[k]["media"], "ic": c4f[k][CLAVE_IC_NB], "p": c4f[k]["valor_p_nadeau_bengio"],
                                    "folds": c4f[k]["nuevo_mejor_en_folds"], "de_folds": c4f[k]["de_folds"],
                                    "semillas": c4f[k]["nuevo_mejor_en_semillas"], "de_semillas": c4f[k]["de_semillas"]}
                                for k in METRICAS}},
        "reservado": {"pacientes": reservado["datos"]["evaluacion"]["pacientes"],
                      "malignas": reservado["datos"]["evaluacion"]["malignas"],
                      "pacientes_con_malignas": reservado["datos"]["evaluacion"]["pacientes_con_malignas"],
                      "remuestras": reservado["bootstrap"]["remuestras"],
                      "m3": reservado["metricas"]["M3limpio"]["pauc"], "m2": reservado["metricas"]["M2"]["pauc"],
                      "dif": {k: dif[k] for k in ("pauc", "auc")},
                      "red": reservado["metricas"]["Red4e"]["pauc"]["punto"],
                      "ib": reservado["metricas"]["ImagenBasicos"]["pauc"]["punto"],
                      "red_menos_ib": {k: rib[k] for k in ("pauc", "setop15")}},
        "kaggle": {"ganador": ganador, "comparaciones": comparacion["comparaciones_con_la_privada"],
                   "c7_menos_m3": comparacion["aritmetica_de_dos_fuentes"]["c7_menos_m3limpio_kaggle_privada"],
                   "pacientes": reservado["datos"]["entrenamiento"]["pacientes"] + reservado["datos"]["evaluacion"]["pacientes"],
                   "pacientes_desarrollo": reservado["datos"]["entrenamiento"]["pacientes"],
                   "privadas": privadas, "nombres": NOMBRES_KAGGLE,
                   "tabla": {m: {"desarrollo": dev[m], "reservado": (tabla[m]["reservado"] or {}).get("pauc"),
                                 "reservado_ic": (reservado["metricas"].get(m) or {}).get("pauc", {}).get("intervalo_95"),
                                 "kaggle": kag[m]} for m in ("C7", "M3limpio", "Red4e", "ImagenBasicos")},
                   "semillas_desarrollo": rango_de_semillas([5, 6, 7, 8, 9]),
                   "efectos": {k: {"privada": v["privada"], "publica": v["publica"]} for k, v in ef.items()},
                   "descomposicion": efectos["descomposicion_de_la_distancia_al_ganador"],
                   "horas": {m: proy["proyeccion"][m]["horas_proyectadas"] for m in ("M3limpio", "C7", "Red4e")},
                   "lesiones_prueba": proy["lesiones_de_prueba_supuestas"]},
    }


def construir_datos(outputs_dir, leidos):
    def cargar(nombre):
        return cargar_json(outputs_dir, nombre, leidos)

    eda = cargar("eda-diagnostico")
    validacion = cargar("diseno-validacion")
    auditoria = cargar("auditoria-de-fugas")
    modelado = cargar("modelado-baseline")
    vr = cargar("validacion-repetida")
    procedencia = cargar("sensibilidad-procedencia-repetida")
    tiempo = cargar("tiempo-inferencia")
    extraccion = cargar("extraccion-imagen")
    sellado = cargar("holdout-pacientes")
    verificacion = cargar("sintesis-verificacion")
    comprobar_suma_verificacion(verificacion)
    # Parte B, B8: el ejemplo tiene que seguir existiendo entre los señalados.
    # *Desde el 2026-11-04 los años de las citas bibliográficas, «Autor (AAAA)»,
    # se omiten por su contexto; el ejemplo es ahora un año de una fuente que no
    # va entre paréntesis, como «agosto de 2025». Antes se exigía el paréntesis.*
    afirmar(any(re.fullmatch(r"(19|20)\d\d", s["valor"].rstrip(".,"))
                for s in verificacion["numeros_sin_respaldo"]),
            "un número señalado puede ser legítimo, como el año de una fuente")
    fase4 = {archivo: cargar(archivo) for _, archivo in COMPARACIONES}
    fase4b = {archivo: cargar(archivo) for _, archivo in FASE4B}
    mecanismo = cargar("mecanismo-2a")
    particion = cargar("efecto-particion")
    imagen_sola = cargar("imagen-sola")

    escala = modelado["escala_de_referencia_pauc"]

    # Cifras que outputs/ guarda dentro de un texto: se extraen del texto en
    # vez de teclearse.
    m = extraer(r"pAUC sobre (\d+)% TPR, rango \[(\d+(?:\.\d+)?), (\d+(?:\.\d+)?)\]",
                modelado["metrica"], "el umbral y el rango de la métrica")
    metrica = {"tpr": int(m.group(1)), "rmin": float(m.group(2)), "rmax": float(m.group(3))}
    auc_azar = float(extraer(r"el AUC va de (\d+(?:\.\d+)?) \(azar\)",
                             modelado["nivel_0_referencia_univariada"]["nota"], "el azar del AUC").group(1))
    clave_ic = next(k for k in fase4["fase4-m2-vs-m1"]["comparaciones_nuevo_menos_base"]["pauc"]
                    if re.fullmatch(r"intervalo_t_\d+_nadeau_bengio", k))
    nivel_ic = int(re.fullmatch(r"intervalo_t_(\d+)_nadeau_bengio", clave_ic).group(1))
    nota_nnt = extraer(r"En el NNT80% SE menos es mejor[^.]*\.", fase4["fase4-m2-vs-m1"]["nota"],
                       "la nota del NNT").group(0)

    ruta_cita, patron_cita = CITA_PANDERM
    lineas_cita = [(i, patron_cita.search(l)) for i, l in enumerate(leer(os.path.join(RAIZ, ruta_cita)).split("\n"), 1)]
    lineas_cita = [(i, c) for i, c in lineas_cita if c]
    if len(lineas_cita) != 1:
        raise SystemExit(f"La cita de PanDerm aparece {len(lineas_cita)} veces en {ruta_cita}, no una.")
    linea_cita, cita = lineas_cita[0]

    # --- validación repetida: niveles y comparación 2b − 1 ---
    niveles = []
    for etiqueta, descripcion, clave in NIVELES_VR:
        bloque = vr[clave]
        folds = [x for s in vr["semillas_corridas"] for x in bloque["pauc_por_semilla_y_fold"][str(s)]]
        niveles.append({"etiqueta": etiqueta, "descripcion": descripcion, "campo": clave,
                        "media": bloque["pauc_media_global"], "std": bloque["pauc_std_entre_folds"],
                        "folds": folds})
    n1, n2a, n2b = niveles
    pareada = vr["comparacion_pareada_2b_menos_1"]
    etiquetas_pareadas = [f"semilla {s}, pliegue {f}" for s in vr["semillas_corridas"] for f in range(vr["n_splits"])]

    # --- Fase 4b: tres intentos de mejorar a M3 limpio ---
    intentos = []
    for etiqueta, archivo in FASE4B:
        if fase4b[archivo]["comparacion"]["base"] != "M3limpio":
            raise SystemExit(f"{archivo}.json no compara contra M3 limpio. No se escribe la página.")
        p = fase4b[archivo]["comparaciones_nuevo_menos_base"]["pauc"]
        intentos.append({"etiqueta": etiqueta, "archivo": f"{archivo}.json", "media": p["media"],
                         "bonferroni": p[CLAVE_BONFERRONI]})
    # borrador-v2.md, «Resultados», «El modelo recomendado»: «Ninguna lo supera en la pAUC».
    afirmar(len(intentos) == 3 and all(not i["bonferroni"][0] > 0 for i in intentos),
            "ninguna de las tres combinaciones supera a M3 limpio en la pAUC")

    # --- Fase 4c: la red de imagen entrenada, sola y apilada sobre M3 limpio ---
    preguntas_4c = []
    for clave, (etiqueta, archivo, nuevo, base) in FASE4C.items():
        o = cargar(archivo)
        if (o["comparacion"]["nuevo"], o["comparacion"]["base"]) != (nuevo, base):
            raise SystemExit(f"{archivo}.json no compara {nuevo} con {base}. No se escribe la página.")
        c = o["comparaciones_nuevo_menos_base"]
        preguntas_4c.append({
            "clave": clave, "etiqueta": etiqueta, "archivo": f"{archivo}.json", "nuevo": nuevo, "base": base,
            "media_nuevo": o["metricas"][nuevo]["pauc"]["media_global"],
            "media_base": o["metricas"][base]["pauc"]["media_global"],
            "metricas": {k: {"media": c[k]["media"], "bonferroni": c[k][CLAVE_BONFERRONI],
                             "folds": c[k]["nuevo_mejor_en_folds"], "de_folds": c[k]["de_folds"],
                             "semillas": c[k]["nuevo_mejor_en_semillas"], "de_semillas": c[k]["de_semillas"]}
                         for k in METRICAS},
        })
    Q4C = {q["clave"]: q for q in preguntas_4c}
    rs = Q4C["red_sola"]["metricas"]
    # borrador-v2.md, «El modelo recomendado» y «La imagen sola»: ninguna de las dos preguntas
    # llega a la regla. Si un intervalo de Bonferroni de la pAUC quedara entero por encima de
    # cero, la página diría algo falso: no se escribe.
    afirmar(all(not q["metricas"]["pauc"]["bonferroni"][0] > 0 for q in preguntas_4c),
            "ninguna de las dos preguntas de la Fase 4c llega a la regla")
    afirmar(all(q["metricas"]["pauc"]["semillas"] == q["metricas"]["pauc"]["de_semillas"] for q in preguntas_4c),
            "en las dos el modelo con la red queda por encima en las 10 semillas")
    afirmar(rs["auc"]["bonferroni"][0] > 0, "En el AUC estándar, que no decide, sí queda entero por encima de cero")
    afirmar(contiene_cero(rs["setop15"]["bonferroni"]) and contiene_cero(rs["nnt80"]["bonferroni"]),
            "en la sensibilidad top-15 y el NNT80% SE, el intervalo contiene el cero")
    afirmar(2 * rs["pauc"]["folds"] > rs["pauc"]["de_folds"],
            "Una red entrenada sobre los recortes supera a la imagen sola en la mayoría de los pliegues")
    afirmar(Q4C["red_sola"]["media_base"] == imagen_sola["metricas"]["Imagen"]["pauc"]["media_global"],
            "la imagen sola con DINOv2 de la Fase 4c es la de imagen-sola.json")
    afirmar(Q4C["c4"]["media_base"] == fase4["fase4-m3limpio-vs-m2"]["metricas"]["M3limpio"]["pauc"]["media_global"],
            "M3 limpio, en la Fase 4c, es el de la Fase 4")

    # --- comparaciones de la Fase 4 ---
    comparaciones = []
    for etiqueta, archivo in COMPARACIONES:
        c = fase4[archivo]["comparaciones_nuevo_menos_base"]
        comparaciones.append({
            "etiqueta": etiqueta, "archivo": f"{archivo}.json",
            "metricas": {k: {"media": c[k]["media"], "ic": c[k][clave_ic],
                             "folds": c[k]["nuevo_mejor_en_folds"], "de_folds": c[k]["de_folds"],
                             "semillas": c[k]["nuevo_mejor_en_semillas"], "de_semillas": c[k]["de_semillas"],
                             "mayor_es_mejor": c[k]["mayor_es_mejor"]} for k in METRICAS},
        })
    C = {c["etiqueta"]: c["metricas"] for c in comparaciones}

    tabla = []
    for modelo, archivo, clave in TABLA:
        mt = fase4[archivo]["metricas"][clave]
        tabla.append({"modelo": modelo, "archivo": f"{archivo}.json", "clave": clave,
                      "pauc": mt["pauc"]["media_global"], "setop15": mt["setop15"]["media_global"],
                      "nnt80": mt["nnt80"]["media_global"],
                      "tiempo": tiempo["tiempos"][clave]["mediana_segundos_por_1000_lesiones"]})
    T = {f["modelo"]: f for f in tabla}

    # El modelo recomendado se muestra desde la constante comprobada, con su
    # pAUC media; el texto de la recomendación describe M3 limpio.
    origen_recomendado = {"M3 limpio": ("fase4-m3limpio-vs-m2", "M3limpio")}
    if RECOMENDADO not in origen_recomendado:
        raise SystemExit(f"El texto de la recomendación describe M3 limpio, no {RECOMENDADO}.")
    archivo_rec, clave_rec = origen_recomendado[RECOMENDADO]

    por_fold = validacion["por_fold"]
    c_proc = procedencia["comparaciones"]
    univariado = {u["columna"]: u for u in auditoria["univariado"]}
    solo_train = auditoria["columnas_solo_en_train"]

    # --- frases que dicen algo de los datos ---
    afirmar(all(x < escala["azar"] for x in n2a["folds"]),
            "por debajo del piso aleatorio de 0,02 en los 50 pliegues")
    afirmar(modelado["nivel_2a_gradient_boosting_sin_balancear"]["auc_estandar_media"] > auc_azar
            and modelado["nivel_2a_gradient_boosting_sin_balancear"]["pauc_media"] < escala["azar"],
            "Las dos métricas discrepan sobre si el modelo supera al azar")
    afirmar(contiene_cero(pareada["intervalo_t_95_nadeau_bengio"]), "La ventaja no está establecida")
    # Rediseño, paso 2, gráfico 1: los cuatro paneles de 2b − 1 toman la pAUC de
    # validacion-repetida.json y las otras tres métricas de efecto-particion.json.
    # Solo se pueden poner juntos si los dos archivos traen la misma comparación.
    # Control: test_generar_demo.py, caso T1.
    pauc_ep = particion["particiones"]["paciente"]["comparacion_2b_menos_1"]["pauc"]
    afirmar(pareada["diferencias"] == pauc_ep["diferencias"] and pareada["media"] == pauc_ep["media"]
            and pareada["intervalo_t_95_nadeau_bengio"] == pauc_ep["intervalo_t_95_nadeau_bengio"]
            and pareada["gana_2b_en"] == pauc_ep["nivel_2b_mejor_en_pliegues"]
            and pareada["semillas_a_favor_de_2b"] == pauc_ep["nivel_2b_mejor_en_semillas"],
            "Los cuatro paneles de 2b − 1 son la misma comparación: la pAUC de validacion-repetida.json es la de efecto-particion.json")
    afirmar(n2b["std"] > n1["std"], "Con las 10 semillas el orden se invierte")
    afirmar(contiene_cero(c_proc["b_2b_con_menos_2b_sin"]["intervalo_t_95_nadeau_bengio"])
            and contiene_cero(c_proc["c_1_con_menos_1_sin"]["intervalo_t_95_nadeau_bengio"]),
            "La exclusión se sostiene por razón de uso, no de desempeño")
    afirmar(c_proc["c_1_con_menos_1_sin"]["gana_primer_termino_en_semillas"]
            == c_proc["c_1_con_menos_1_sin"]["de_semillas"],
            "En la logística, incluirlas mejora en las 10 semillas")
    m21, m42, m4b, m32, m3l = (C[e] for e, _ in COMPARACIONES)
    afirmar(contiene_cero(m21["pauc"]["ic"]) and not contiene_cero(m21["setop15"]["ic"])
            and not contiene_cero(m21["nnt80"]["ic"]) and m21["setop15"]["media"] > 0 and m21["nnt80"]["media"] < 0,
            "M2 se distingue de M1 en las dos métricas de triaje, no en la pAUC")
    afirmar(all(contiene_cero(m42[k]["ic"]) for k in METRICAS)
            and all(m42[k]["media"] < 0 for k in ("pauc", "auc", "setop15")) and m42["nnt80"]["media"] > 0,
            "Ningún intervalo excluye el cero, y la estimación puntual es peor en las cuatro métricas")
    afirmar(all(contiene_cero(m42[k]["ic"]) and contiene_cero(m4b[k]["ic"]) for k in METRICAS),
            "Añadidas al modelo con contexto de paciente, las variables de imagen de DINOv2, como variables "
            "sueltas o apiladas, no mejoran de forma distinguible ninguna de las métricas")
    afirmar(2 * m42["pauc"]["semillas"] < m42["pauc"]["de_semillas"] < 2 * m4b["pauc"]["semillas"],
            "la forma de incorporar la imagen invierte la dirección de la pAUC")
    afirmar(m32["pauc"]["ic"][0] > 0, "esa ventaja no se puede separar de los dos sesgos conocidos a favor de M3")
    afirmar(m3l["pauc"]["ic"][0] > 0 and m3l["auc"]["ic"][0] > 0
            and contiene_cero(m3l["setop15"]["ic"]) and contiene_cero(m3l["nnt80"]["ic"]),
            "solo M3 limpio se distingue, y solo en la pAUC y en el AUC estándar")
    afirmar(T["M2"]["tiempo"] < T["M3 limpio"]["tiempo"] < 0.1,
            "M3 limpio cuesta más que M2, pero los dos quedan por debajo de una décima de segundo")
    afirmar(min(T["M4"]["tiempo"], T["M4b"]["tiempo"]) > max(T[x]["tiempo"] for x in ("M1", "M2", "M3 limpio"))
            and contiene_cero(m42["pauc"]["ic"]) and contiene_cero(m4b["pauc"]["ic"]),
            "Lo caro, con diferencia, es la imagen, y ni M4 ni M4b mejoraron a M2 en la métrica principal de forma distinguible")
    afirmar(all(fase4[a]["metricas"]["M2"]["pauc"]["media_global"] == T["M2"]["pauc"] for _, a in COMPARACIONES[1:]),
            "M2 es el mismo en las cuatro comparaciones contra M2")
    afirmar(len(solo_train) + len(auditoria["columnas_constantes"]) + len(auditoria["columnas_identificador"])
            + len(auditoria["columnas_procedencia"]) == len(modelado["columnas_excluidas"])
            and len(auditoria["columnas_constantes"]) == 1 and len(auditoria["columnas_identificador"]) == 1
            and len(auditoria["columnas_procedencia"]) == 2,
            "Quedan fuera de los modelos 15 columnas, por cuatro motivos")
    afirmar("target" in solo_train and any(c.startswith("iddx") for c in solo_train)
            and {"mel_mitotic_index", "mel_thick_mm"} <= set(solo_train),
            "Entre ellas están la propia etiqueta, la taxonomía diagnóstica y dos medidas que solo existen tras la biopsia")
    preguntas = [p["columna"] for p in auditoria["preguntas_abiertas"]]
    afirmar(preguntas[0] == "tbp_lv_nevi_confidence" and "tbp_lv_nevi_confidence" not in solo_train
            and set(preguntas[1:]) <= set(solo_train),
            "la única que no contestan los motivos de arriba es tbp_lv_nevi_confidence")

    resumenes = {}
    for etapa in CADENA:
        ruta = os.path.join(outputs_dir, f"{etapa['md']}.md")
        resumenes[etapa["md"]] = leer(ruta) if os.path.exists(ruta) else "(sin archivo)"

    return {
        "generado": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "cadena": CADENA,
        "resumenes": resumenes,
        "recomendado": RECOMENDADO,
        "recomendado_pauc": fase4[archivo_rec]["metricas"][clave_rec]["pauc"]["media_global"],
        "recomendado_fuente": f"{archivo_rec}.json > metricas.{clave_rec}.pauc.media_global",
        "escala": {"azar": escala["azar"], "maximo": escala["maximo"]},
        "metrica": metrica,
        "auc_azar": auc_azar,
        "nivel_ic": nivel_ic,
        "clave_ic": clave_ic,
        "nota_nnt": nota_nnt,
        "panderm": {"antes": cita.group(1), "numero": cita.group(2), "despues": cita.group(3),
                    "fuente": f"{ruta_cita}, línea {linea_cita} (cita literal)"},
        "eda": {
            "n_filas": eda["estructura_grupos"]["n_filas"],
            "n_pacientes": eda["estructura_grupos"]["n_grupos"],
            "n_columnas": eda["fuente"]["n_columnas"],
            "positivos": eda["desbalance_target"]["conteos"]["1"],
            "pct_positivos": eda["desbalance_target"]["pct_positivos"],
            "min": eda["estructura_grupos"]["filas_por_grupo"]["min"],
            "max": eda["estructura_grupos"]["filas_por_grupo"]["max"],
            "mediana": eda["estructura_grupos"]["filas_por_grupo"]["mediana"],
        },
        "sellado": {"pct": round(sellado["metodo"]["fraccion"] * 100), "semilla": sellado["semilla"]},
        "extraccion": {
            "caracteristica": extraccion["caracteristica"],
            "desarrollo": {k: extraccion["conjuntos"]["desarrollo"]["cobertura"][k] for k in ("imagenes", "decodificadas", "pacientes")},
            "reservado": {k: extraccion["conjuntos"]["reservado"]["cobertura"][k] for k in ("imagenes", "decodificadas", "pacientes")},
        },
        "diseno": {
            "seed": validacion["esquema"]["seed"],
            "min_grupos": min(f["n_val_grupos"] for f in por_fold),
            "max_grupos": max(f["n_val_grupos"] for f in por_fold),
            "min_pos": min(f["n_val_positivos"] for f in por_fold),
            "max_pos": max(f["n_val_positivos"] for f in por_fold),
            "n_grupos_positivos": validacion["n_grupos_positivos"],
            "naive_n": validacion["comparacion_particion_naive"]["n_grupos_con_fuga"],
            "naive_pct": validacion["comparacion_particion_naive"]["pct_grupos_con_fuga"],
        },
        "auditoria": {
            "n_excluidas": len(modelado["columnas_excluidas"]),
            "n_solo_train": len(solo_train),
            "nevi_auc": univariado["tbp_lv_nevi_confidence"]["auc_oof"],
        },
        "seed42": {
            "seed": modelado["esquema_cv"]["seed"],
            "auc_2a": modelado["nivel_2a_gradient_boosting_sin_balancear"]["auc_estandar_media"],
        },
        "vr": {
            "semillas": len(vr["semillas_corridas"]),
            "n_splits": vr["n_splits"],
            "niveles": [{k: v for k, v in n.items() if k != "folds"} for n in niveles],
            "n_folds_2a": len(n2a["folds"]),
            "pareada": {"media": pareada["media"], "ic": pareada["intervalo_t_95_nadeau_bengio"],
                        "gana": pareada["gana_2b_en"], "de": pareada["de"],
                        "semillas": pareada["semillas_a_favor_de_2b"],
                        "diferencias": pareada["diferencias"], "etiquetas": etiquetas_pareadas},
        },
        "procedencia": {
            "a_con": c_proc["a_2b_menos_1_con_procedencia"]["media"],
            "a_sin": c_proc["a_2b_menos_1_sin_procedencia"]["media"],
            "b": {"media": c_proc["b_2b_con_menos_2b_sin"]["media"],
                  "ic": c_proc["b_2b_con_menos_2b_sin"]["intervalo_t_95_nadeau_bengio"]},
            "c": {"media": c_proc["c_1_con_menos_1_sin"]["media"],
                  "ic": c_proc["c_1_con_menos_1_sin"]["intervalo_t_95_nadeau_bengio"],
                  "semillas": c_proc["c_1_con_menos_1_sin"]["gana_primer_termino_en_semillas"],
                  "folds": c_proc["c_1_con_menos_1_sin"]["gana_primer_termino_en_folds"],
                  "de_folds": c_proc["c_1_con_menos_1_sin"]["de_folds"]},
        },
        "comparaciones": comparaciones,
        "fase4b": intentos,
        "fase4c": preguntas_4c,
        "tabla": tabla,
        "mecanismo": datos_mecanismo(mecanismo, metrica),
        "particion": datos_particion(particion),
        "imagen_sola": datos_imagen_sola(imagen_sola, escala, modelado, fase4, extraccion, tiempo),
        "imagen_barras": datos_imagen_barras(cargar, imagen_sola),
        "posteriores": datos_fases_4d_a_5c(cargar),
        "siete": datos_siete_versiones(cargar),
        "verificacion": {
            "total": verificacion["numeros_en_borrador"],
            "con": verificacion["numeros_con_respaldo_en_outputs"],
            "sin": len(verificacion["numeros_sin_respaldo"]),
            "metodo": len(verificacion["porcentajes_de_metodo_excluidos"]),
            "omitidos": len(verificacion["numeros_en_contextos_omitidos"]),
            "comentarios": len(verificacion["numeros_en_comentarios"]),
        },
    }


PLANTILLA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proyecto de consultor&iacute;a ISIC 2024 &mdash; Detecci&oacute;n de c&aacute;ncer de piel</title>
<script>__CHARTJS__</script>
<style>
  :root {
    --tinta: #16202b;
    --suave: #5b6b7c;
    --linea: #d8e0e8;
    --fondo: #f4f6f9;
    --acento: #1f5f8b;
    --alarma: #b8341f;
    --bien: #1e7a52;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    color: var(--tinta);
    background: var(--fondo);
    line-height: 1.55;
    overflow-wrap: break-word;
  }
  .hoja { max-width: 1080px; margin: 0 auto; padding: 0 28px 72px; }
  header { padding: 44px 0 28px; border-bottom: 3px solid var(--tinta); }
  .kicker {
    text-transform: uppercase; letter-spacing: .16em; font-size: 12px;
    color: var(--suave); font-weight: 600;
  }
  h1 { font-size: 30px; margin: 10px 0 12px; line-height: 1.25; }
  .tesis { margin: 0 0 22px; max-width: 860px; font-size: 18px; line-height: 1.45; }
  /* Las cuatro cifras de los datos, en una fila; en el teléfono, dos por fila. */
  .cifras { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .cifras .medida { padding: 16px 10px; }
  .cifras .medida .cifra { font-size: 34px; color: var(--acento); }
  .cifras .medida .rot { margin-top: 6px; font-size: 14px; }
  section { margin-top: 52px; }
  /* La frase que queda a la vista en cada sección; el resto va en «Detalle». */
  .frase { margin: 0 0 16px; font-size: 16px; max-width: 860px; }
  details.detalle { margin-top: 18px; border-top: 1px solid var(--linea); padding-top: 12px; }
  details.detalle > summary { cursor: pointer; font-weight: 600; font-size: 14px; color: var(--acento); }
  details.detalle[open] > summary { margin-bottom: 14px; }
  header details.detalle { max-width: 860px; }
  .columnas { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .columnas h3 { margin-top: 4px; }
  .medida.reco .det { font-size: 13px; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; margin: 0 0 10px; }
  .medida.reco .cifra { font-size: 30px; line-height: 1.15; }
  h2 { font-size: 21px; margin: 0 0 6px; display: flex; align-items: center; }
  h2 .num {
    flex: 0 0 30px; width: 30px; height: 30px; line-height: 30px;
    text-align: center; background: var(--tinta); color: #fff;
    border-radius: 50%; font-size: 14px; margin-right: 10px;
  }
  h3 { font-size: 16px; margin: 22px 0 8px; }
  .tarjeta > h3:first-child { margin-top: 0; }
  .sub { color: var(--suave); margin: 0 0 20px; font-size: 15px; }
  .tarjeta {
    background: #fff; border: 1px solid var(--linea); border-radius: 10px;
    padding: 22px; box-shadow: 0 1px 2px rgba(22,32,43,.05);
  }
  .texto p { margin: 0 0 12px; font-size: 15px; }
  .texto ul { margin: 0 0 12px; padding-left: 20px; font-size: 15px; }
  .texto li { margin-bottom: 8px; }
  /* Una sola fila, también a 375 px: los pasos encogen, no saltan de línea. */
  .cadena { display: flex; align-items: stretch; gap: 4px; flex-wrap: nowrap; }
  .paso {
    flex: 1 1 0; min-width: 0; text-align: center; cursor: pointer; background: #fff;
    border: 1px solid var(--linea); border-top: 4px solid var(--suave);
    border-radius: 8px; padding: 12px 6px; font: inherit; color: inherit;
    transition: transform .12s, box-shadow .12s, border-color .12s;
  }
  .paso:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(22,32,43,.12); }
  .paso[aria-selected="true"] { border-color: var(--acento); border-top-color: var(--acento); background: #eef5fa; }
  .paso.final { border-top-color: var(--acento); }
  .paso .nom { font-weight: 700; font-size: 14px; display: block; white-space: nowrap; }
  .flecha { align-self: center; color: var(--suave); font-size: 16px; }
  .salida {
    margin-top: 16px; background: #fff; border: 1px solid var(--linea);
    border-radius: 10px; padding: 0 20px 4px;
  }
  .salida h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .08em; color: var(--suave); }
  .ficha { margin: 0 0 16px; }
  .ficha p { margin: 0 0 9px; font-size: 14.5px; }
  .ficha b { color: var(--acento); }
  .ficha .hallazgo { border-left: 3px solid var(--acento); background: #f4f8fb; padding: 9px 13px; border-radius: 0 6px 6px 0; font-size: 14.5px; }
  .ficha .hallazgo p { margin: 0 0 8px; }
  .ficha .hallazgo ul { margin: 0 0 8px; padding-left: 20px; }
  .salida pre {
    white-space: pre-wrap; font-family: Menlo, Consolas, monospace;
    font-size: 12.5px; line-height: 1.6; background: #fbfcfd;
    border: 1px solid var(--linea); border-radius: 6px; padding: 14px; overflow-x: auto;
  }
  .duo { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
  .medida { text-align: center; padding: 24px 18px; border-radius: 10px; border: 1px solid var(--linea); background: #fff; }
  .medida .cifra { font-size: 52px; font-weight: 700; line-height: 1; }
  .medida.mal { border-color: #f0c4bc; background: #fdf4f2; }
  .medida.mal .cifra { color: var(--alarma); }
  .medida.ok { border-color: #b9ded0; background: #f2faf6; }
  .medida.ok .cifra { color: var(--bien); }
  .medida .rot { font-weight: 600; margin-top: 10px; }
  .medida .det { font-size: 13px; color: var(--suave); margin-top: 4px; }
  .medida.sola { max-width: 420px; margin: 0 auto 18px; }
  .tabla-envoltura { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; font-size: 14px; }
  th, td { text-align: right; padding: 8px 10px; border-bottom: 1px solid var(--linea); vertical-align: top; white-space: nowrap; }
  th:first-child, td:first-child { text-align: left; }
  th { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--suave); white-space: normal; }
  .tabla-intentos { margin-bottom: 16px; }
  .tabla-intentos td:first-child { white-space: normal; }
  .aviso {
    font-size: 12.5px; color: var(--suave); background: #fbfcfd;
    border-left: 3px solid var(--linea); padding: 8px 12px; margin: 14px 0 0;
  }
  .exploratorio {
    margin: 24px 0 0; padding: 12px 16px; border: 2px solid var(--alarma);
    border-radius: 8px; background: #fdf3f1; color: var(--tinta); font-size: 15px;
  }
  .exploratorio b { color: var(--alarma); }
  .barra { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
  .lienzo { position: relative; height: 340px; }
  .paneles { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  /* Sin esto, el panel —un elemento de la rejilla— no baja del ancho que
     Chart.js le dio al lienzo, y a 375 px la página desbordaba a lo ancho. */
  .panel { min-width: 0; }
  .panel h3 { margin: 0 0 6px; font-size: 14px; }
  .panel .lienzo { height: 230px; }
  /* Paneles de una sola fila, como los de 2b − 1 en la sección 3. */
  .paneles.uno .panel .lienzo { height: 96px; }
  .pie-grafico { font-size: 13px; color: var(--suave); margin-top: 14px; }
  /* Leyenda en HTML: se parte en líneas a 375 px, y la de Chart.js cortaba los
     rótulos largos. */
  .leyenda { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 12.5px; color: var(--suave); margin-top: 10px; }
  .leyenda > span { display: inline-flex; align-items: center; gap: 6px; }
  .leyenda i { display: inline-block; width: 22px; height: 11px; border-radius: 2px; flex: 0 0 22px; box-sizing: border-box; }
  .cifra-fuente { border-bottom: 1px dotted var(--suave); cursor: help; }
  footer {
    margin-top: 64px; padding-top: 20px; border-top: 1px solid var(--linea);
    font-size: 12.5px; color: var(--suave);
  }
  @media (max-width: 760px) {
    .hoja { padding: 0 16px 56px; }
    h1 { font-size: 25px; }
    .duo, .paneles, .columnas { grid-template-columns: 1fr; }
    .cifras { grid-template-columns: 1fr 1fr; gap: 10px; }
    .cifras .medida .cifra { font-size: 28px; }
    .tesis { font-size: 16.5px; }
    .flecha { display: none; }
    /* Cada paso toma el ancho de su palabra y reparte el sobrante: con anchos
       iguales, «Diagnóstico» no cabía en su casilla a 375 px. */
    .cadena { gap: 3px; }
    .paso { flex: 1 1 auto; padding: 10px 2px; }
    .paso .nom { font-size: 10.5px; }
    .tarjeta { padding: 16px; }
    .medida .cifra { font-size: 44px; }
    .lienzo { height: 300px; }
    /* La tabla de tres ejes cabe entera: el costo no queda fuera de la vista. */
    table { font-size: 12.5px; }
    /* Con 4 px por lado, la tabla de tres ejes sobresalía 7 px de su caja a 375 px
       y recortaba la última columna; el nombre del modelo puede partirse. */
    th, td { padding: 6px 3px; }
    td:first-child { white-space: normal; }
    /* La de las fases 4d y 4e, en el «Detalle» de la sección 7, sobresalía 15 px:
       sus intervalos se parten tras el punto y coma. */
    .tabla-intentos td { white-space: normal; }
    th { font-size: 9.5px; letter-spacing: .03em; }
  }
</style>
</head>
<body>
<div class="hoja">
__AVISO_EXPLORATORIO__

<header>
  <div class="kicker">Consultor&iacute;a e Investigaci&oacute;n &middot; Estad&iacute;stica &middot; caso ISIC 2024</div>
  <h1>Proyecto de consultor&iacute;a ISIC 2024</h1>
  <p class="tesis" id="tesis"></p>
  <div class="cifras" id="cifras"></div>
  <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-0"></div></details>
</header>

<section>
  <h2><span class="num">1</span>C&oacute;mo se desarroll&oacute; el trabajo</h2>
  <p class="frase">Haz clic en cualquiera para ver la salida real que produjo.</p>
  <div class="cadena" id="cadena"></div>
  <div class="salida" id="salida" hidden>
    <h3 id="salida-nombre"></h3>
    <div class="ficha">
      <p><b>Qu&eacute; se midi&oacute;.</b> <span id="ficha-mide"></span></p>
      <p><b>Por qu&eacute; se hizo.</b> <span id="ficha-porque"></span></p>
      <div class="hallazgo"><p><b>Un hallazgo concreto.</b></p><div id="ficha-hallazgo"></div></div>
    </div>
    <h3 id="salida-titulo"></h3>
    <pre id="salida-texto"></pre>
  </div>
  <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-1"></div></details>
</section>

<section>
  <h2><span class="num">2</span>Una decisi&oacute;n por defecto cambia el veredicto</h2>
  <div class="tarjeta">
    <p class="frase" id="frase-2"></p>
    <div class="lienzo"><canvas id="gr-niveles"></canvas></div>
    <p class="pie-grafico">Los bigotes marcan una desviaci&oacute;n est&aacute;ndar entre pliegues, no un intervalo de confianza.</p>
    <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-2"></div></details>
  </div>
</section>

<section>
  <h2><span class="num">3</span>Una ventaja que la pAUC no ve</h2>
  <div class="tarjeta">
    <p class="frase" id="frase-3"></p>
    <div class="paneles uno" id="paneles-2b1"></div>
    <p class="pie-grafico" id="pie-paneles-2b1"></p>
    <h3>Las columnas de procedencia no explican la ventaja</h3>
    <p class="frase" id="frase-3b"></p>
    <h3>Partir por filas no cambia el veredicto</h3>
    <p class="frase" id="frase-3c"></p>
    <details class="detalle"><summary>Detalle</summary>
      <div class="texto" id="det-3a"></div>
      <div class="lienzo"><canvas id="gr-pareada"></canvas></div>
      <div class="texto" id="det-3b"></div>
    </details>
  </div>
</section>

<section>
  <h2><span class="num">4</span>La m&eacute;trica principal no agota lo que pidi&oacute; el cliente</h2>
  <div class="tarjeta">
    <p class="frase" id="frase-4"></p>
    <div class="paneles" id="paneles"></div>
    <p class="pie-grafico" id="pie-paneles"></p>
    <h3>La imagen sola, sin el sistema de fotograf&iacute;a corporal total</h3>
    <p class="frase" id="frase-4b"></p>
    <div class="lienzo"><canvas id="gr-imagen"></canvas></div>
    <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-4"></div></details>
  </div>
</section>

<section>
  <h2><span class="num">5</span>Fuera del conjunto de desarrollo</h2>
  <div class="tarjeta">
    <h3>El conjunto reservado, abierto una sola vez</h3>
    <p class="frase" id="frase-reservado"></p>
    <h3>En la prueba de Kaggle</h3>
    <p class="frase" id="frase-kaggle"></p>
    <div class="lienzo"><canvas id="gr-tres"></canvas></div>
    <div class="leyenda" id="leyenda-tres"></div>
    <p class="pie-grafico" id="pie-tres"></p>
    <div class="lienzo" style="height:110px;margin-top:24px"><canvas id="gr-distancia"></canvas></div>
    <div class="leyenda" id="leyenda-distancia"></div>
    <div class="lienzo" style="height:150px;margin-top:8px"><canvas id="gr-recorrido"></canvas></div>
    <p class="pie-grafico" id="pie-cascada"></p>
    <details class="detalle"><summary>Detalle</summary>
      <div class="texto" id="det-5a"></div>
      <div class="tabla-envoltura"><table id="tabla-tres"></table></div>
      <div class="texto" id="det-5b" style="margin-top:16px"></div>
    </details>
  </div>
</section>

<section>
  <h2><span class="num">6</span>La pregunta del cliente, entera</h2>
  <div class="tarjeta">
    <div class="tabla-envoltura"><table id="tabla-ejes"></table></div>
    <p class="frase" id="frase-6" style="margin-top:16px"></p>
    <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-6"></div></details>
  </div>
</section>

<section>
  <h2><span class="num">7</span>Recomendaci&oacute;n</h2>
  <div class="tarjeta" style="margin-bottom:18px">
    <div class="lienzo"><canvas id="gr-siete"></canvas></div>
    <div class="leyenda" id="leyenda-siete"></div>
    <p class="pie-grafico" id="pie-siete"></p>
  </div>
  <div class="duo">
    <div class="medida ok reco">
      <div class="det">Con fotograf&iacute;a corporal total</div>
      <div class="cifra" id="reco-con"></div>
    </div>
    <div class="medida ok reco">
      <div class="det">Sin fotograf&iacute;a corporal total</div>
      <div class="cifra" id="reco-sin"></div>
    </div>
  </div>
  <div class="tarjeta">
    <p class="frase" id="frase-7"></p>
    <div class="columnas">
      <div><h3>Qu&eacute; se puede afirmar</h3><div class="texto" id="se-puede"></div></div>
      <div><h3>Qu&eacute; no se puede afirmar</h3><div class="texto" id="no-se-puede"></div></div>
    </div>
    <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-7"></div></details>
  </div>
</section>

<section>
  <h2><span class="num">8</span>Limitaciones</h2>
  <div class="tarjeta">
    <p class="frase" id="frase-8"></p>
    <div class="texto" id="limitaciones"></div>
    <details class="detalle"><summary>Detalle</summary><div class="texto" id="det-8"></div></details>
  </div>
</section>

<footer id="pie"></footer>
</div>

<script id="datos" type="application/json">__DATOS__</script>
<script>
const D = JSON.parse(document.getElementById("datos").textContent);
// Los ejes de los gráficos, con coma decimal como el texto.
Chart.defaults.locale = "es";
const esc = t => String(t).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const menos = s => s.replace("-", "−");
// Cifras con los decimales que trae el JSON, como las escribe el informe.
const dec = v => menos(String(v).replace(".", ","));
const fijo = (v, d) => menos(v.toFixed(d).replace(".", ","));
const firmado = (v, d) => (v > 0 ? "+" : "") + (d === undefined ? dec(v) : fijo(v, d));
// useGrouping "always" porque el defecto español omite el punto en los
// números de cuatro cifras.
const mil = v => v.toLocaleString("es", {useGrouping: "always"});
// Cada cifra lleva su origen en el title: la trazabilidad del informe
// escrito, disponible al pasar el raton en la version proyectada.
const cifra = (v, fuente) => `<span class="cifra-fuente" title="${esc(fuente)}">${v}</span>`;
const P = ps => ps.map(p => `<p>${p}</p>`).join("");
const L = ls => `<ul>${ls.map(l => `<li>${l}</li>`).join("")}</ul>`;
// El texto va en su propio span: suelto, cada cifra quedaba como un elemento más
// del flex, con hueco a los lados («( 36,1% )»).
const leyenda = (id, items) => document.getElementById(id).innerHTML =
  items.map(([estilo, texto]) => `<span>${estilo ? `<i style="${estilo}"></i>` : ""}<span>${texto}</span></span>`).join("");

const E = D.eda, R = D.extraccion.reservado, DS = D.extraccion.desarrollo, DI = D.diseno, A = D.auditoria;
const VR = D.vr, PR = D.procedencia, V = D.verificacion;
const fEda = c => "eda-diagnostico.json > " + c, fDis = c => "diseno-validacion.json > " + c;
const fVR = c => "validacion-repetida.json > " + c, fPro = c => "sensibilidad-procedencia-repetida.json > comparaciones." + c;
const fExt = c => "extraccion-imagen.json > " + c, fVer = c => "sintesis-verificacion.json > " + c;
const fMod = c => "modelado-baseline.json > " + c;
const MC = D.mecanismo, fMec = c => "mecanismo-2a.json > niveles.nivel_2a_gradient_boosting_sin_balancear.total." + c;
const azar = cifra(dec(D.escala.azar), fMod("escala_de_referencia_pauc.azar"));
const nivelIC = cifra(D.nivel_ic + "%", "fase4-*.json > comparaciones_nuevo_menos_base.*." + D.clave_ic + " (nivel del intervalo)");
const semillasVR = cifra(VR.semillas, fVR("semillas_corridas"));
const ic = (lo, hi, fuente, d) => cifra("[" + (d === undefined ? dec(lo) : fijo(lo, d)) + "; " + (d === undefined ? dec(hi) : fijo(hi, d)) + "]", fuente);
const COMP = Object.fromEntries(D.comparaciones.map(c => [c.etiqueta, c]));
const fComp = (et, k, campo) => `${COMP[et].archivo} > comparaciones_nuevo_menos_base.${k}.${campo}`;
const mediaC = (et, k) => cifra(firmado(COMP[et].metricas[k].media, k === "nnt80" ? 2 : undefined), fComp(et, k, "media"));
const semC = (et, k) => cifra(COMP[et].metricas[k].semillas, fComp(et, k, "nuevo_mejor_en_semillas"));
const deSemC = (et, k) => cifra(COMP[et].metricas[k].de_semillas, fComp(et, k, "de_semillas"));
const NIV = Object.fromEntries(VR.niveles.map(n => [n.etiqueta, n]));
const mediaN = et => cifra(dec(NIV[et].media), fVR(NIV[et].campo + ".pauc_media_global"));
const stdN = et => cifra(dec(NIV[et].std), fVR(NIV[et].campo + ".pauc_std_entre_folds"));
const T = Object.fromEntries(D.tabla.map(f => [f.modelo, f]));
const tiempoT = m => cifra(dec(T[m].tiempo), `tiempo-inferencia.json > tiempos.${T[m].clave}.mediana_segundos_por_1000_lesiones`);
const milLesiones = cifra(mil(1000), "tiempo-inferencia.json > tiempos.*.mediana_segundos_por_1000_lesiones (unidad)");
const reco = cifra(esc(D.recomendado), "RECOMENDADO, comprobado contra la regla de recomendación sobre fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.pauc." + D.clave_ic);

/* ---------- 0. cabecera ---------- */
// Rediseño, paso 1 (2026-11-06): la cabecera queda con una línea de tesis y las
// cuatro cifras de los datos. «El problema», «Los datos» y «Por qué este caso»
// se quitaron; la definición de la métrica pasa a su «Detalle».
// borrador-v2.md, «Estado del arte», «Cómo se evalúa un sistema de triaje».
document.getElementById("tesis").innerHTML =
  `Toma la métrica que eligió el cliente y lee a su lado el AUC y las dos métricas de triaje, porque sobre las mismas predicciones pueden discrepar.`;
const tarjetaCifra = (v, fuente, rotulo) =>
  `<div class="medida"><div class="cifra">${cifra(v, fuente)}</div><div class="rot">${rotulo}</div></div>`;
// borrador-v2.md, «Datos y validación», «El conjunto de desarrollo» y «El conjunto reservado».
document.getElementById("cifras").innerHTML =
  tarjetaCifra(mil(E.n_filas), fEda("estructura_grupos.n_filas"), "lesiones de desarrollo") +
  tarjetaCifra(mil(E.positivos), fEda("desbalance_target.conteos.1"), "malignas") +
  tarjetaCifra(mil(E.n_pacientes), fEda("estructura_grupos.n_grupos"), "pacientes de desarrollo") +
  tarjetaCifra(mil(R.pacientes), fExt("conjuntos.reservado.cobertura.pacientes"), "pacientes reservados");

// borrador-v2.md, «Método», «Qué se mide».
document.getElementById("det-0").innerHTML = P([
  `<b>La métrica principal es la del reto:</b> el área parcial bajo la curva ROC por encima del ` +
  `${cifra(D.metrica.tpr + "%", fMod("metrica"))} de sensibilidad, o pAUC, que va de ` +
  `${cifra(dec(D.metrica.rmin), fMod("metrica"))} a ${cifra(dec(D.metrica.rmax), fMod("metrica"))}. ` +
  `El organizador la justifica en términos clínicos, no estadísticos: <i>"there are regions in the ROC space where the values of TPR are unacceptable in clinical practice"</i>, ` +
  `y <i>"Systems that aid in diagnosing cancers are required to be highly-sensitive"</i>. ` +
  `Esa es la función de utilidad del cliente, escrita en su métrica: la región del espacio ROC donde la sensibilidad es clínicamente inaceptable no cuenta. ` +
  `Un clasificador al azar obtiene ${azar} y uno perfecto, ${cifra(dec(D.escala.maximo), fMod("escala_de_referencia_pauc.maximo"))}.`]);

/* ---------- 1. cadena ---------- */
// La prosa de cada instrumento (que mide, por que existe) viaja en el JSON
// desde CADENA. Lo que lleva cifras se arma aqui: cada una pasa por cifra()
// y por tanto por su archivo y campo de origen.
const MIDE = {
  // Parte B, B6.
  "extraccion-imagen": () =>
    `Una característica por imagen: ${cifra(esc(D.extraccion.caracteristica), fExt("caracteristica"))}. ` +
    `Se decodificaron ${cifra(mil(DS.decodificadas), fExt("conjuntos.desarrollo.cobertura.decodificadas"))} de ` +
    `${cifra(mil(DS.imagenes), fExt("conjuntos.desarrollo.cobertura.imagenes"))} imágenes del desarrollo y ` +
    `${cifra(mil(R.decodificadas), fExt("conjuntos.reservado.cobertura.decodificadas"))} de ` +
    `${cifra(mil(R.imagenes), fExt("conjuntos.reservado.cobertura.imagenes"))} del reservado. ` +
    `No se leyó ninguna etiqueta ni se calculó ninguna métrica.`
};
const MB_1 = `El mismo gradient boosting da resultados opuestos según una sola opción.`;
const MB_resto = () =>
  `Sin balancear, su pAUC media es ${mediaN("Nivel 2a")}, ` +
  `por debajo del piso aleatorio de ${azar} en los ${cifra(VR.n_folds_2a, fVR("nivel_2a_gradient_boosting_sin_balancear.pauc_por_semilla_y_fold (todos)"))} pliegues. ` +
  `Con <code>class_weight="balanced"</code>, y nada más distinto, llega a ${mediaN("Nivel 2b")}.`;
const HALLAZGOS = {
  // borrador-v2.md, «Datos y validación», «Los datos» y «La auditoría de columnas».
  "eda-diagnostico": () => P([
    `Los datos son la metadata del reto: una fila por lesión y ${cifra(E.n_columnas, fEda("fuente.n_columnas"))} columnas, ` +
    `con las mediciones que el software de la fotografía corporal total calcula sobre cada lesión, datos del paciente y, ` +
    `solo en el conjunto de entrenamiento, el diagnóstico.`,
    `<b>${cifra(A.n_solo_train, "auditoria-de-fugas.json > columnas_solo_en_train")} no existen al predecir.</b> ` +
    `El conjunto de prueba no las trae. Entre ellas están la propia etiqueta, la taxonomía diagnóstica y dos medidas que solo existen tras la biopsia.`]),
  // borrador-v2.md, «Datos y validación», «La partición: por paciente».
  "diseno-validacion": () => P([
    `La validación cruzada agrupa por paciente: cada paciente queda entero de un lado de cada pliegue. ` +
    `En la partición de la semilla ${cifra(String(DI.seed), fDis("esquema.seed"))}, cada pliegue de validación tiene entre ` +
    `${cifra(DI.min_grupos, fDis("por_fold[*].n_val_grupos (mínimo)"))} y ${cifra(DI.max_grupos, fDis("por_fold[*].n_val_grupos (máximo)"))} pacientes y entre ` +
    `${cifra(DI.min_pos, fDis("por_fold[*].n_val_positivos (mínimo)"))} y ${cifra(DI.max_pos, fDis("por_fold[*].n_val_positivos (máximo)"))} lesiones malignas.`,
    `Lo que evita esa agrupación se midió. Una partición aleatoria por filas, con la misma semilla, habría dejado a ` +
    `${cifra(mil(DI.naive_n), fDis("comparacion_particion_naive.n_grupos_con_fuga"))} pacientes, el ` +
    `${cifra(dec(DI.naive_pct) + "%", fDis("comparacion_particion_naive.pct_grupos_con_fuga"))}, con lesiones a los dos lados.`]),
  // borrador-v2.md, «Datos y validación», «La auditoría de columnas».
  "auditoria-de-fugas": () =>
    P([`Quedan fuera de los modelos ${cifra(A.n_excluidas, fMod("columnas_excluidas"))} columnas, por cuatro motivos:`]) +
    L([`<b>${cifra(A.n_solo_train, "auditoria-de-fugas.json > columnas_solo_en_train")} no existen al predecir.</b>`,
       `<b>Una es constante:</b> <code>image_type</code>.`,
       `<b>Una identifica la fila:</b> <code>isic_id</code>.`,
       `<b>Dos describen el centro y la licencia de la imagen, no la lesión:</b> <code>attribution</code> y <code>copyright_license</code>.`]) +
    P([`De las preguntas abiertas de la auditoría, la única que no contestan los motivos de arriba es <code>tbp_lv_nevi_confidence</code>, ` +
       `por su nombre, aunque sí está en el conjunto de prueba.`,
       `El artículo del conjunto de datos la define como <i>"a convolutional neural network classifier estimated probability that the lesion is a nevus"</i>, ` +
       `así que la calcula el software sobre la imagen y está disponible al predecir. Se usa. Su AUC por sí sola es ` +
       `${cifra(dec(A.nevi_auc), "auditoria-de-fugas.json > univariado (tbp_lv_nevi_confidence.auc_oof)")}.`]),
  // borrador-v2.md, «El extractor de imagen»: las dos primeras frases de su
  // segundo párrafo y la de interpretación (Parte B, B6).
  "extraccion-imagen": () => P([
    `PanDerm, un modelo fundacional de dermatología, no se usa. Su artículo declara un subconjunto de ISIC 2024 entre sus datos de preentrenamiento: ` +
    `<i>"${esc(D.panderm.antes)}${cifra(esc(D.panderm.numero), D.panderm.fuente)}${esc(D.panderm.despues)}"</i>.`,
    `<i>Interpretación, no medición:</i> es el razonamiento de la auditoría de fugas, un nivel más arriba. ` +
    `Con modelos fundacionales, la fuga puede venir del preentrenamiento de un tercero y no del conjunto de datos.`]),
  // borrador-v2.md, «Resultados», «Una decisión por defecto cambia el veredicto». La
  // sección 2 muestra la primera frase y pasa el resto a su «Detalle».
  "modelado-baseline": () => P([MB_1 + " " + MB_resto()]),
  // Parte B, B8, con el texto de la persona del 2026-10-04.
  "sintesis-consultoria": () => P([
    `El verificador encontró ${cifra(mil(V.total), fVer("numeros_en_borrador"))} números en el informe. ` +
    `${cifra(mil(V.comentarios), fVer("numeros_en_comentarios"))} están en los comentarios que dan la fuente de cada frase, ` +
    `y no se les busca respaldo; ` +
    `${cifra(V.omitidos, fVer("numeros_en_contextos_omitidos"))} se omiten por su contexto, con una lista declarada y los años de las citas bibliográficas; ` +
    `${cifra(V.metodo, fVer("porcentajes_de_metodo_excluidos"))} son parámetros del método; ` +
    `${cifra(mil(V.con), fVer("numeros_con_respaldo_en_outputs"))} tienen respaldo en outputs/, y ` +
    `${cifra(V.sin, fVer("numeros_sin_respaldo"))} quedan señalados para revisarlos a mano. ` +
    `El verificador señala, no decide: un número señalado puede ser legítimo, como el año de una fuente.`])
};

const cadena = document.getElementById("cadena");
D.cadena.forEach((s, i) => {
  const b = document.createElement("button");
  b.className = "paso" + (s.tipo === "interpretación" ? " final" : "");
  b.setAttribute("aria-selected", "false");
  b.title = s.etapa;
  b.innerHTML = `<span class="nom">${esc(s.palabra)}</span>`;
  b.onclick = () => {
    const abierto = b.getAttribute("aria-selected") === "true";
    document.querySelectorAll(".paso").forEach(p => p.setAttribute("aria-selected", "false"));
    const caja = document.getElementById("salida");
    if (abierto) { caja.hidden = true; return; }
    b.setAttribute("aria-selected", "true");
    document.getElementById("salida-nombre").textContent = s.etapa;
    document.getElementById("ficha-mide").innerHTML = MIDE[s.nombre] ? MIDE[s.nombre]() : esc(s.mide);
    document.getElementById("ficha-porque").textContent = s.porque;
    document.getElementById("ficha-hallazgo").innerHTML = HALLAZGOS[s.nombre]();
    document.getElementById("salida-titulo").textContent = "outputs/" + s.md + ".md";
    document.getElementById("salida-texto").textContent = D.resumenes[s.md];
    caja.hidden = false;
  };
  cadena.appendChild(b);
  if (i < D.cadena.length - 1) {
    const f = document.createElement("div");
    f.className = "flecha"; f.textContent = "→";
    cadena.appendChild(f);
  }
});
// Lo que la tira mostraba antes del rediseño: la frase de las seis etapas y el
// nombre, el tipo y la función de cada una.
document.getElementById("det-1").innerHTML =
  P([`Seis etapas. Las cinco primeras miden y dejan su salida en un archivo; la sexta interpreta y redacta.`]) +
  L(D.cadena.map((s, i) => `<b>${i + 1}. ${esc(s.etapa)}</b> (${esc(s.tipo)}). ${esc(s.funcion)}.`));

/* ---------- 2. una decision por defecto ---------- */
// Desde el rediseño, paso 1 (2026-11-06), cada sección deja a la vista la
// primera frase de cada subsección y su gráfico o tabla; el resto va en su
// «Detalle», plegado. Las dos cifras grandes del 2a y el 2b se quitaron: el
// gráfico y el «Detalle» dan las mismas.
document.getElementById("frase-2").innerHTML = MB_1;
// borrador-v2.md, «Resultados», párrafo inicial, y «Una decisión por defecto cambia el veredicto».
document.getElementById("det-2").innerHTML = P([
  `Salvo donde se indica, las métricas de desempeño son del conjunto de desarrollo, con ${semillasVR} semillas y ` +
  `${cifra(VR.n_splits, fVR("n_splits"))} pliegues. Cada diferencia es «nuevo − base», y su intervalo es el corregido al ${nivelIC}. ` +
  `Los pliegues y semillas en que gana el nuevo se dan entre paréntesis.`, MB_resto(),
  `La métrica por defecto no es ciega a ese fallo, pero lo lee distinto. En la partición de la semilla ` +
  `${cifra(String(D.seed42.seed), fMod("esquema_cv.seed"))}, el AUC estándar del modelo sin balancear es ` +
  `${cifra(dec(D.seed42.auc_2a), fMod("nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media"))}, por encima del azar de su escala, ` +
  `${cifra(dec(D.auc_azar), fMod("nivel_0_referencia_univariada.nota"))}; su pAUC queda por debajo del azar de la suya. ` +
  `Las dos métricas discrepan sobre si el modelo supera al azar.`,
  `Se midió también cómo falla el modelo sin balancear, en la partición de la semilla ` +
  `${cifra(String(MC.seed), "mecanismo-2a.json > esquema_cv.seed")}. No es que ponga arriba a más negativos que ` +
  `positivos, en proporción: con probabilidad de ${cifra(dec(MC.umbral_alto), "mecanismo-2a.json > umbral_alto")} o más queda el ` +
  `${cifra(dec(MC.neg_alto) + "%", fMec("frac_neg_ge_0999"))} de los negativos y el ` +
  `${cifra(dec(MC.pos_alto) + "%", fMec("frac_pos_ge_0999"))} de los positivos. ` +
  `Lo que hace es hundir a una parte de los positivos al fondo del ordenamiento: el ` +
  `${cifra(dec(MC.pos_bajo) + "%", fMec("frac_pos_bajo_p20_neg"))} queda en o por debajo del percentil ` +
  `${cifra(MC.percentil, "mecanismo-2a.json > definiciones (p20_neg)")} de los negativos, frente al ` +
  `${cifra(dec(MC.pos_bajo_2b) + "%", "mecanismo-2a.json > niveles.nivel_2b_gradient_boosting_balanceado.total.frac_pos_bajo_p20_neg")} ` +
  `con el modelo balanceado, y ${cifra(MC.n_pos_min, fMec("n_pos_en_el_minimo"))} positivos comparten con ` +
  `${cifra(MC.n_neg_min, fMec("n_neg_en_el_minimo"))} negativos la probabilidad mínima, ${cifra(dec(MC.minimo), fMec("minimo_predicho"))}. ` +
  `Eso es coherente con una pAUC bajo el azar: para capturar el ${cifra(D.metrica.tpr + "%", fMod("metrica"))} de los ` +
  `positivos, el umbral tiene que bajar hasta el ${cifra(MC.cola + "%", fMod("metrica") + " (100 menos el umbral de sensibilidad)")} ` +
  `de positivos de menor rango, y ese ${cifra(MC.cola + "%", fMod("metrica") + " (100 menos el umbral de sensibilidad)")} está entre el ` +
  `${cifra(dec(MC.decil) + "%", fMec("deciles_rango_pos[" + MC.indice_decil + "] (× 100)"))} de lesiones con menor puntuación. ` +
  `Ahí queda marcado más del ${cifra(MC.marcadas + "%", fMec("deciles_rango_pos[" + MC.indice_decil + "] (100 · (1 − valor), por abajo)"))} ` +
  `de las lesiones, cuando al azar quedaría marcado el ${cifra(D.metrica.tpr + "%", fMod("metrica"))}. ` +
  `Por qué el modelo los hunde no se midió.`]);

// Bigotes de +/- 1 desviacion entre folds. Se dibujan a mano porque
// Chart.js no trae barras de error: sin ellas la vista de medias
// sugiere una precision que estos folds no tienen.
const bigotes = {
  id: "bigotes",
  afterDatasetsDraw(ch) {
    const ds = ch.data.datasets[0];
    if (!ds.desviaciones) return;
    const meta = ch.getDatasetMeta(0), ejeY = ch.scales.y, cx = ch.ctx;
    cx.save(); cx.strokeStyle = "#16202b"; cx.lineWidth = 1.5;
    meta.data.forEach((barra, i) => {
      const s = ds.desviaciones[i], v = ds.data[i];
      if (!s) return;
      const arriba = ejeY.getPixelForValue(v + s), abajo = ejeY.getPixelForValue(Math.max(0, v - s)), x = barra.x;
      cx.beginPath();
      cx.moveTo(x, arriba); cx.lineTo(x, abajo);
      cx.moveTo(x - 7, arriba); cx.lineTo(x + 7, arriba);
      cx.moveTo(x - 7, abajo); cx.lineTo(x + 7, abajo);
      cx.stroke();
    });
    cx.restore();
  }
};

const piso = {
  id: "piso",
  beforeDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(D.escala.azar), cx = ch.ctx;
    if (!isFinite(y)) return;
    cx.save();
    cx.strokeStyle = "#b8341f"; cx.setLineDash([5, 4]); cx.lineWidth = 1.5;
    cx.beginPath(); cx.moveTo(ch.chartArea.left, y); cx.lineTo(ch.chartArea.right, y); cx.stroke();
    cx.restore();
  },
  // El rótulo va DESPUÉS de las barras y sobre fondo opaco: dibujado
  // antes, la barra del nivel 2b le pasaba por encima y solo se leia
  // "aleatorio 0,02".
  // Centrado sobre el nivel 2a, cuya barra no llega a la línea: a la derecha, a
  // 375 px, el rótulo quedaba encima de la barra del nivel 2b.
  afterDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(D.escala.azar), cx = ch.ctx;
    if (!isFinite(y)) return;
    const texto = "piso aleatorio " + dec(D.escala.azar);
    cx.save();
    cx.font = `600 ${ch.width < 500 ? 10 : 11}px -apple-system, sans-serif`; cx.textAlign = "center";
    const ancho = cx.measureText(texto).width;
    const x = ch.getDatasetMeta(0).data[VR.niveles.findIndex(n => n.etiqueta === "Nivel 2a")].x;
    cx.fillStyle = "rgba(255,255,255,.85)";
    cx.fillRect(x - ancho / 2 - 4, y - 18, ancho + 8, 15);
    cx.fillStyle = "#b8341f";
    cx.fillText(texto, x, y - 7);
    cx.restore();
  }
};

new Chart(document.getElementById("gr-niveles"), {
  type: "bar",
  plugins: [bigotes, piso],
  data: {
    labels: VR.niveles.map(n => n.etiqueta),
    datasets: [{
      label: "pAUC medio",
      data: VR.niveles.map(n => n.media),
      desviaciones: VR.niveles.map(n => n.std),
      backgroundColor: ["#4a7fa5", "#c98b7a", "#1f5f8b"],
      borderRadius: 4,
      maxBarThickness: 96
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: {
      y: { beginAtZero: true, suggestedMax: D.escala.maximo,
           title: { display: true, text: `pAUC (${dec(D.escala.azar)} = azar, ${dec(D.escala.maximo)} = perfecto)` } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: it => VR.niveles[it[0].dataIndex].etiqueta + " — " + VR.niveles[it[0].dataIndex].descripcion,
          label: it => "pAUC " + dec(VR.niveles[it.dataIndex].media) + "  ±" + dec(VR.niveles[it.dataIndex].std) + " entre folds",
          afterLabel: it => "validacion-repetida.json > " + VR.niveles[it.dataIndex].campo
        }
      }
    }
  }
});

const NOMBRES = { pauc: "pAUC", auc: "AUC estándar", setop15: "Sensibilidad top-15", nnt80: "NNT80% SE" };
// Marca de la media sobre cada barra de intervalo, y la línea del cero.
const mediasYcero = {
  id: "mediasYcero",
  afterDatasetsDraw(ch) {
    const ds = ch.data.datasets[0], meta = ch.getDatasetMeta(0), ejeX = ch.scales.x, cx = ch.ctx, a = ch.chartArea;
    const x0 = ejeX.getPixelForValue(0);
    cx.save(); cx.strokeStyle = "#16202b"; cx.setLineDash([4, 3]); cx.lineWidth = 1.2;
    cx.beginPath(); cx.moveTo(x0, a.top); cx.lineTo(x0, a.bottom); cx.stroke();
    cx.setLineDash([]); cx.lineWidth = 2.5;
    meta.data.forEach((barra, i) => {
      const x = ejeX.getPixelForValue(ds.medias[i]);
      cx.beginPath(); cx.moveTo(x, barra.y - 9); cx.lineTo(x, barra.y + 9); cx.stroke();
    });
    cx.restore();
  }
};
// Un panel por métrica: la barra es el intervalo, la marca, la media, y la línea
// discontinua, el cero; en verde si el intervalo excluye el cero. Lo usan la
// sección 4 y, desde el rediseño, paso 2, la 3.
function panelesDeIntervalos(contenedor, etiquetas, filasDe, fuenteDe) {
  ["pauc", "auc", "setop15", "nnt80"].forEach(k => {
    const div = document.createElement("div");
    div.className = "panel";
    div.innerHTML = `<h3>${NOMBRES[k]}</h3><div class="lienzo"><canvas></canvas></div>`;
    contenedor.appendChild(div);
    const filas = filasDe(k);
    const distinguible = filas.map(m => !(m.ic[0] <= 0 && 0 <= m.ic[1]));
    const d = k === "nnt80" ? 2 : undefined;
    new Chart(div.querySelector("canvas"), {
      type: "bar",
      plugins: [mediasYcero],
      data: {
        labels: etiquetas,
        datasets: [{
          data: filas.map(m => m.ic), medias: filas.map(m => m.media),
          backgroundColor: distinguible.map(x => x ? "rgba(30,122,82,.55)" : "rgba(91,107,124,.35)"),
          borderSkipped: false, borderRadius: 3, barPercentage: .55
        }]
      },
      options: {
        indexAxis: "y", responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: it => {
                const m = filas[it.dataIndex];
                return `${firmado(m.media, d)}, [${d ? fijo(m.ic[0], d) : dec(m.ic[0])}; ${d ? fijo(m.ic[1], d) : dec(m.ic[1])}] ` +
                       `(${m.folds} de ${m.de_folds}; ${m.semillas} de ${m.de_semillas})`;
              },
              afterLabel: it => fuenteDe(k, it.dataIndex)
            }
          }
        }
      }
    });
  });
}

/* ---------- 3. una ventaja que la pAUC no ve ---------- */
const PA = VR.pareada, EP = D.particion;
const fEP = c => "efecto-particion.json > particiones.paciente.comparacion_2b_menos_1." + c;
const fEPf = c => "efecto-particion.json > filas_menos_paciente." + c;
// borrador-v2.md, «Resultados», «Una ventaja que la pAUC no ve».
document.getElementById("frase-3").innerHTML =
  `El gradient boosting balanceado supera a la regresión logística balanceada por ` +
  `${cifra(dec(PA.media), fVR("comparacion_pareada_2b_menos_1.media"))} en promedio, con intervalo ` +
  `${ic(PA.ic[0], PA.ic[1], fVR("comparacion_pareada_2b_menos_1.intervalo_t_95_nadeau_bengio"))} ` +
  `(${cifra(PA.gana, fVR("comparacion_pareada_2b_menos_1.gana_2b_en"))} de ${cifra(PA.de, fVR("comparacion_pareada_2b_menos_1.de"))} pliegues; ` +
  `${cifra(PA.semillas, fVR("comparacion_pareada_2b_menos_1.semillas_a_favor_de_2b"))} de ${semillasVR} semillas).`;
const resto3 = P([
  `La ventaja no está establecida. ` +
  `En las otras tres métricas sí lo está: AUC ${cifra(firmado(EP.otras.auc.media), fEP("auc.media"))}, ` +
  `${ic(EP.otras.auc.ic[0], EP.otras.auc.ic[1], fEP("auc.intervalo_t_95_nadeau_bengio"))}; sensibilidad top-15 ` +
  `${cifra(firmado(EP.otras.setop15.media), fEP("setop15.media"))}, ` +
  `${ic(EP.otras.setop15.ic[0], EP.otras.setop15.ic[1], fEP("setop15.intervalo_t_95_nadeau_bengio"))}; NNT80% SE ` +
  `${cifra(firmado(EP.otras.nnt80.media, 2), fEP("nnt80.media"))} lesiones por cada maligna, ` +
  `${ic(EP.otras.nnt80.ic[0], EP.otras.nnt80.ic[1], fEP("nnt80.intervalo_t_95_nadeau_bengio"), 2)}. ` +
  `Como en M2 − M1, la pAUC no distingue una ventaja que las métricas de triaje sí distinguen.`,
  `Sobre una sola partición de los datos completos, el boosting parecía además más estable que la logística. ` +
  `Con las ${semillasVR} semillas el orden se invierte: su desviación entre pliegues es ${stdN("Nivel 2b")}, frente a ${stdN("Nivel 1")}. ` +
  `Ese argumento se retiró.`]);
// borrador-v2.md, «Resultados», «Las columnas de procedencia no explican la ventaja».
document.getElementById("frase-3b").innerHTML =
  `Con las columnas de centro y licencia, la diferencia entre el boosting y la logística es ` +
  `${cifra(dec(PR.a_con), fPro("a_2b_menos_1_con_procedencia.media"))}; sin ellas, ${cifra(dec(PR.a_sin), fPro("a_2b_menos_1_sin_procedencia.media"))}.`;
const resto3b = P([
  `Incluirlas mueve el boosting en ${cifra(dec(PR.b.media), fPro("b_2b_con_menos_2b_sin.media"))}, con intervalo ` +
  `${ic(PR.b.ic[0], PR.b.ic[1], fPro("b_2b_con_menos_2b_sin.intervalo_t_95_nadeau_bengio"))}, y la logística en ` +
  `${cifra(dec(PR.c.media), fPro("c_1_con_menos_1_sin.media"))}, con ${ic(PR.c.ic[0], PR.c.ic[1], fPro("c_1_con_menos_1_sin.intervalo_t_95_nadeau_bengio"))}. ` +
  `En la logística, incluirlas mejora en las ${cifra(PR.c.semillas, fPro("c_1_con_menos_1_sin.gana_primer_termino_en_semillas"))} semillas y en ` +
  `${cifra(PR.c.folds, fPro("c_1_con_menos_1_sin.gana_primer_termino_en_folds"))} de ${cifra(PR.c.de_folds, fPro("c_1_con_menos_1_sin.de_folds"))} pliegues. ` +
  `La magnitud no está establecida. ` +
  `La exclusión se sostiene por razón de uso, no de desempeño. Una sola partición sugería lo contrario; ` +
  `es el segundo resultado de una sola partición que no sobrevive a la validación repetida.`]);
// borrador-v2.md, «Resultados», «Partir por filas no cambia el veredicto».
const FP = EP.filas_menos_paciente, semEP = cifra(EP.semillas, "efecto-particion.json > esquema.semillas");
const mejorF = (n, m, nivel) => cifra(FP[n][m].mejor, fEPf(nivel + "." + m + ".semillas_filas_mejor"));
const N1 = "nivel_1_regresion_logistica", N2B = "nivel_2b_gradient_boosting_balanceado";
document.getElementById("frase-3c").innerHTML =
  `Se probaron las dos particiones con la logística y el gradient boosting balanceados, con una regla de lectura ` +
  `fijada antes de correr.`;
const resto3c = P([
  `La partición por filas infla una métrica si da mejor en las ${semEP} semillas, y cambia el ` +
  `veredicto si el intervalo de 2b − 1 en la pAUC excluye el cero en una partición y no en la otra.`,
  `No se cumple ninguna de las dos. Partir por filas mueve la pAUC en ` +
  `${cifra(firmado(FP.n1.pauc.dif), fEPf(N1 + ".pauc.diferencia_de_medias"))} con la logística y en ` +
  `${cifra(firmado(FP.n2b.pauc.dif), fEPf(N2B + ".pauc.diferencia_de_medias"))} con el boosting, y da mejor en ` +
  `${mejorF("n1", "pauc", N1)} y en ${mejorF("n2b", "pauc", N2B)} de las ${semEP} semillas. ` +
  `En el AUC y el NNT80% SE de la logística da mejor en ${mejorF("n1", "auc", N1)} de ${semEP}, no en las ${semEP} que pedía la ` +
  `regla; con el boosting, en ${mejorF("n2b", "auc", N2B)} y en ${mejorF("n2b", "nnt80", N2B)}. ` +
  `El intervalo de 2b − 1 en la pAUC contiene el cero en las dos particiones: ` +
  `${ic(EP.ic_paciente[0], EP.ic_paciente[1], fEP("pauc.intervalo_t_95_nadeau_bengio"))} por paciente y ` +
  `${ic(EP.ic_filas[0], EP.ic_filas[1], "efecto-particion.json > particiones.filas.comparacion_2b_menos_1.pauc.intervalo_t_95_nadeau_bengio")} por filas.`,
  `La sensibilidad top-15 sí sube con filas, pero queda fuera de la regla: con esa partición cada paciente tiene en ` +
  `validación solo una parte de sus lesiones, y el top-15 no mide lo mismo.`,
  `<i>Interpretación, no medición:</i> con estos datos y estos dos modelos, que el ` +
  `${cifra(dec(DI.naive_pct) + "%", fDis("comparacion_particion_naive.pct_grupos_con_fuga"))} de los pacientes quede a los dos ` +
  `lados no se traduce en una métrica inflada. Lo medido vale para la logística y el boosting balanceados; no se probó con ` +
  `el contexto de paciente ni con M3 limpio.`]);
// Los 50 pliegues de 2b − 1 pasan al «Detalle», debajo del resto de su párrafo
// (rediseño, paso 2).
document.getElementById("det-3a").innerHTML = resto3;
document.getElementById("det-3b").innerHTML =
  `<h3>Las columnas de procedencia no explican la ventaja</h3>` + resto3b +
  `<h3>Partir por filas no cambia el veredicto</h3>` + resto3c;

// Rediseño, paso 2, gráfico 1: 2b − 1 en las cuatro métricas, con el estilo de la
// sección 4. La pAUC sale de validacion-repetida.json, la de la frase de arriba;
// las otras tres, de efecto-particion.json, que reproduce esa comparación pliegue
// a pliegue (lo comprueba construir_datos).
const fPareada = "validacion-repetida.json > comparacion_pareada_2b_menos_1 (media, intervalo_t_95_nadeau_bengio, gana_2b_en, de, semillas_a_favor_de_2b; semillas_corridas)";
panelesDeIntervalos(document.getElementById("paneles-2b1"), ["2b − 1"],
  k => [k === "pauc" ? {media: PA.media, ic: PA.ic, folds: PA.gana, de_folds: PA.de, semillas: PA.semillas, de_semillas: VR.semillas}
                     : EP.otras[k]],
  k => k === "pauc" ? fPareada
    : `efecto-particion.json > particiones.paciente.comparacion_2b_menos_1.${k} (media, intervalo_t_95_nadeau_bengio, ` +
      `nivel_2b_mejor_en_pliegues, de_pliegues, nivel_2b_mejor_en_semillas, de_semillas)`);
document.getElementById("pie-paneles-2b1").innerHTML = esc(D.nota_nnt);

// Líneas horizontales: el cero, la media y el intervalo corregido.
const lineasH = {
  id: "lineasH",
  afterDatasetsDraw(ch) {
    const ejeY = ch.scales.y, cx = ch.ctx, a = ch.chartArea;
    const linea = (v, color, guion, ancho) => {
      const y = ejeY.getPixelForValue(v);
      cx.save(); cx.strokeStyle = color; cx.setLineDash(guion); cx.lineWidth = ancho;
      cx.beginPath(); cx.moveTo(a.left, y); cx.lineTo(a.right, y); cx.stroke(); cx.restore();
    };
    linea(0, "#16202b", [], 1);
    linea(PA.media, "#1f5f8b", [], 2);
    linea(PA.ic[0], "#1f5f8b", [5, 4], 1.5);
    linea(PA.ic[1], "#1f5f8b", [5, 4], 1.5);
  }
};
new Chart(document.getElementById("gr-pareada"), {
  type: "bar",
  plugins: [lineasH],
  data: {
    labels: PA.etiquetas,
    datasets: [
      { label: "Diferencia 2b − 1 por pliegue", data: PA.diferencias,
        backgroundColor: PA.diferencias.map(d => d > 0 ? "#1f5f8b" : "#c98b7a"), borderRadius: 2 },
      { type: "line", label: "media", data: [], borderColor: "#1f5f8b", borderWidth: 2, pointStyle: "line" },
      { type: "line", label: "intervalo corregido al " + D.nivel_ic + "%", data: [], borderColor: "#1f5f8b", borderDash: [5, 4], borderWidth: 1.5, pointStyle: "line" }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { ticks: { display: false }, grid: { display: false } },
      y: { title: { display: true, text: "Diferencia 2b − 1" } }
    },
    plugins: {
      legend: { position: "bottom", labels: { usePointStyle: true, filter: it => it.datasetIndex > 0 } },
      tooltip: {
        filter: it => it.datasetIndex === 0,
        callbacks: { label: it => firmado(it.parsed.y) }
      }
    }
  }
});

/* ---------- 4. la metrica principal no agota lo que pidio el cliente ---------- */
// borrador-v2.md, «Método», «Cómo se compara».
document.getElementById("frase-4").innerHTML =
  `<b>El criterio:</b> una diferencia se da por establecida solo si su intervalo corregido al ${nivelIC} no contiene el cero.`;
const resto4 = P([`Junto al intervalo se reportan los pliegues y las semillas en que gana cada modelo.`]);
panelesDeIntervalos(document.getElementById("paneles"), D.comparaciones.map(c => c.etiqueta),
  k => D.comparaciones.map(c => c.metricas[k]),
  (k, i) => `${D.comparaciones[i].archivo} > comparaciones_nuevo_menos_base.${k}`);
document.getElementById("pie-paneles").innerHTML = esc(D.nota_nnt);
// borrador-v2.md, «Resultados», «La métrica principal no agota lo que pidió el cliente»,
// «Añadida al modelo con contexto de paciente, la imagen no justifica su costo» y «El modelo recomendado».
const lectura4 = L([
  `<b>M2 − M1.</b> Quien solo lea la pAUC concluye que el contexto de paciente no aporta; la sensibilidad top-15, que el cliente premió aparte, y el NNT80% SE dicen lo contrario. ` +
  `Son cuatro métricas sobre una misma comparación, y el intervalo del NNT queda al límite del cero. ` +
  `<i>Interpretación, no medición:</i> las variables relativas al paciente ordenan las lesiones dentro de cada paciente, que es lo que mide la sensibilidad top-15, ` +
  `mientras que la pAUC ordena todas las lesiones juntas.`,
  `<b>M4 − M2.</b> Ningún intervalo excluye el cero, y la estimación puntual es peor en las cuatro métricas. ` +
  `Por el criterio fijado antes de medir, la imagen, así incorporada, no justifica su costo.`,
  `<b>M4b − M2.</b> <i>Patrón, no efecto establecido:</i> la forma de incorporar la imagen invierte la dirección de la pAUC. ` +
  `Como variables sueltas, M4 queda por encima de M2 en ${semC("M4 − M2", "pauc")} de ${deSemC("M4 − M2", "pauc")} semillas; ` +
  `como puntuación apilada, M4b, en ${semC("M4b − M2", "pauc")} de ${deSemC("M4b − M2", "pauc")}.`,
  `<b>M3 − M2.</b> Por la nota de lectura fijada antes de correr, esa ventaja no se puede separar de los dos sesgos conocidos a favor de M3.`,
  `<b>M3 limpio − M2.</b> El intervalo de la pAUC queda entero por encima de cero, así que, por la regla fijada antes de correr, el modelo recomendado es ${reco}. ` +
  `Quitar los sesgos casi no movió la diferencia media: ${mediaC("M3 − M2", "pauc")} con ellos, ${mediaC("M3 limpio − M2", "pauc")} sin ellos. ` +
  `Esa comparación es descriptiva, entre dos corridas, sin intervalo propio y sin fijar antes.`]);

// borrador-v2.md, «Resultados», «La imagen sola, sin el sistema de fotografía corporal total».
const IS = D.imagen_sola, fIS = c => "imagen-sola.json > " + c;
const fISc = (n, k, campo) => fIS(`comparaciones_nuevo_menos_base.${n}.${k}.${campo}`);
// Un 0.0 del JSON llega a JavaScript como 0: se escribe con el decimal guardado, como en el informe.
const decG = v => Number.isInteger(v) ? fijo(v, 1) : dec(v);
const mediaIS = (n, k) => cifra(firmado(IS.comp[n][k].media, k === "nnt80" ? 2 : undefined), fISc(n, k, "media"));
const icIS = (n, k) => k === "nnt80"
  ? ic(IS.comp[n][k].ic[0], IS.comp[n][k].ic[1], fISc(n, k, IS.clave_ic), 2)
  : cifra("[" + decG(IS.comp[n][k].ic[0]) + "; " + decG(IS.comp[n][k].ic[1]) + "]", fISc(n, k, IS.clave_ic));
const auc922 = cifra(dec(IS.auc_recortes.auc), IS.auc_recortes.fuente);
const citaIS = k => `<i>"${esc(IS.citas[k])}"</i>`;
const IM1 = "imagen_menos_m1", IB = "imagen_basicos_menos_imagen";
const vicIS = (n, k) => `${cifra(IS.comp[n][k].folds, fISc(n, k, "nuevo_mejor_en_folds"))} de ` +
  `${cifra(IS.comp[n][k].de_folds, fISc(n, k, "de_folds"))}; ${cifra(IS.comp[n][k].semillas, fISc(n, k, "nuevo_mejor_en_semillas"))} de ` +
  `${cifra(IS.comp[n][k].de_semillas, fISc(n, k, "de_semillas"))}`;
// borrador-v2.md, «Resultados»: el párrafo de la Fase 4c en «La imagen sola» y la tabla de «El modelo recomendado».
const F4C = Object.fromEntries(D.fase4c.map(q => [q.clave, q]));
const fF4c = (q, k, campo) => `${F4C[q].archivo} > comparaciones_nuevo_menos_base.${k}.${campo}`;
const fF4cM = (q, modelo) => `${F4C[q].archivo} > metricas.${modelo}.pauc.media_global`;
const RS = F4C.red_sola.metricas, C4 = F4C.c4.metricas;
const bonfF4c = (q, k) => fF4c(q, k, "intervalo_bonferroni_nadeau_bengio");
// Las fases 4d a 5c (datos_fases_4d_a_5c): las preguntas de las fases 4d y 4e, la 4f,
// la potencia, el reservado y Kaggle.
const PO = D.posteriores, Q4 = Object.fromEntries(PO.preguntas.map(q => [q.nuevo, q]));
const fQ = (n, k, campo) => `${Q4[n].archivo} > comparaciones_nuevo_menos_base.${k}.${campo}`;
const mediaQ = (n, k) => cifra(firmado(Q4[n].metricas[k].media, k === "nnt80" ? 2 : undefined), fQ(n, k, "media"));
const icQ = (n, k) => ic(Q4[n].metricas[k].ic[0], Q4[n].metricas[k].ic[1], fQ(n, k, "intervalo_t_95_nadeau_bengio"),
  k === "nnt80" ? 2 : undefined);
const pQ = (n, k) => cifra(fijo(Q4[n].metricas[k].p, 4), fQ(n, k, "valor_p_nadeau_bengio"));
const vicQ = (n, k) => `${cifra(Q4[n].metricas[k].folds, fQ(n, k, "nuevo_mejor_en_folds"))} de ` +
  `${cifra(Q4[n].metricas[k].de_folds, fQ(n, k, "de_folds"))}; ${cifra(Q4[n].metricas[k].semillas, fQ(n, k, "nuevo_mejor_en_semillas"))} de ` +
  `${cifra(Q4[n].metricas[k].de_semillas, fQ(n, k, "de_semillas"))}`;
const medQ = (n, cual) => cifra(dec(cual === "nuevo" ? Q4[n].media_nuevo : Q4[n].media_base),
  `${Q4[n].archivo} > metricas.${cual === "nuevo" ? Q4[n].nuevo : Q4[n].base}.pauc.media_global`);
const F4F = PO.fase4f, fF = (k, campo) => `fase4f-red4e-vs-imagen-basicos.json > comparaciones_nuevo_menos_base.${k}.${campo}`;
const mediaF = k => cifra(firmado(F4F.metricas[k].media, k === "nnt80" ? 2 : undefined), fF(k, "media"));
const icF = k => ic(F4F.metricas[k].ic[0], F4F.metricas[k].ic[1], fF(k, "intervalo_t_95_nadeau_bengio"), k === "nnt80" ? 2 : undefined);
const vicF = k => `${cifra(F4F.metricas[k].folds, fF(k, "nuevo_mejor_en_folds"))} de ${cifra(F4F.metricas[k].de_folds, fF(k, "de_folds"))}; ` +
  `${cifra(F4F.metricas[k].semillas, fF(k, "nuevo_mejor_en_semillas"))} de ${cifra(F4F.metricas[k].de_semillas, fF(k, "de_semillas"))}`;
const RH = PO.red_holm, fH4e = c => "fase4e-holm.json > " + c;
const POT = PO.potencia, fPot = c => "potencia-nadeau-bengio.json > " + c;
const RES = PO.reservado, fRes = c => "fase5-reservado.json > " + c, fPos = c => "fase5-posterior.json > " + c;
const icRes = (o, fuente, d) => ic(o.intervalo_95[0], o.intervalo_95[1], fuente, d);
const KG = PO.kaggle, fK = c => "fase5b-comparacion.json > " + c, fE = c => "fase5c-efectos.json > " + c;
const priv = m => cifra(dec(KG.privadas[m]), ["Red4e", "ImagenBasicos"].includes(m)
  ? fK(`kaggle.${m}.privada`) : fE(`kaggle.${m}.privada`));
const efecto = k => cifra(firmado(KG.efectos[k].privada), fE(`efectos.${k}.privada`));
const DES = KG.descomposicion, fDes = c => fE("descomposicion_de_la_distancia_al_ganador." + c);
const horas = m => cifra(dec(KG.horas[m]), `fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.proyeccion.${m}.horas_proyectadas`);
const lesionesPrueba = cifra(mil(KG.lesiones_prueba), "fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.lesiones_de_prueba_supuestas");
const pctObj = k => cifra(Math.round(POT.objetivos[k] * 100) + "%", fPot("objetivos." + k));
document.getElementById("frase-4b").innerHTML =
  `Las mediciones de las que dependen M1, M2 y M3 limpio las calcula el software de la fotografía corporal total; ` +
  `sin ese sistema, esos modelos no se pueden aplicar tal cual.`;
const resto4b = P([
  `Los organizadores del reto describen ese sistema como ${citaIS("costo_tbp")}. ` +
  `M2 y M3 limpio, además, comparan cada lesión con las demás del mismo paciente. Del modelo ganador, que hace lo mismo, ` +
  `los organizadores advierten que por eso ${citaIS("lesiones_sueltas")}.`,
  `Para ese escenario se midió qué da la imagen sola, con una especificación fijada antes de correr: una regresión ` +
  `logística balanceada sobre las ${cifra(IS.n_variables, fExt("caracteristica"))} variables de DINOv2, sola y con edad, ` +
  `sexo y zona del cuerpo, en los mismos pliegues de M1. Las dos versiones analizan cada lesión por separado.`,
  `La imagen sola distingue lesiones malignas muy por encima del azar: su pAUC es de ` +
  `${cifra(dec(IS.medias.Imagen.pauc), fIS("metricas.Imagen.pauc.media_global"))}, frente a ${azar} del azar, y su AUC, de ` +
  `${cifra(dec(IS.medias.Imagen.auc), fIS("metricas.Imagen.auc.media_global"))}. Pero queda por debajo de M1 en las cuatro ` +
  `métricas, y las cuatro diferencias están establecidas:`]) + L([
  `pAUC: ${mediaIS(IM1, "pauc")}, ${icIS(IM1, "pauc")} (${vicIS(IM1, "pauc")});`,
  `AUC: ${mediaIS(IM1, "auc")}, ${icIS(IM1, "auc")} (${vicIS(IM1, "auc")});`,
  `sensibilidad top-15: ${mediaIS(IM1, "setop15")}, ${icIS(IM1, "setop15")} (${vicIS(IM1, "setop15")});`,
  `NNT80% SE: ${mediaIS(IM1, "nnt80")} lesiones por cada maligna, ${icIS(IM1, "nnt80")} (${vicIS(IM1, "nnt80")}).`]) + P([
  `Para capturar el ${cifra(D.metrica.tpr + "%", fMod("metrica"))} de las malignas, la imagen sola marca ` +
  `${cifra(fijo(IS.medias.Imagen.nnt80, 2), fIS("metricas.Imagen.nnt80.media_global"))} lesiones por cada una, frente a ` +
  `${cifra(fijo(IS.medias.M1.nnt80, 2), fIS("metricas.M1.nnt80.media_global"))} de M1. ` +
  `Esa distancia no mide solo lo que aportan las mediciones del sistema: M1 también usa la edad y el sexo, y la imagen con ` +
  `los datos básicos no se comparó con M1. El tiempo de inferencia de la imagen sola no se midió.`,
  `Añadir edad, sexo y zona del cuerpo mejora el AUC de forma distinguible; en las otras tres métricas la mejora no se da por establecida:`]) + L([
  `AUC: ${mediaIS(IB, "auc")}, ${icIS(IB, "auc")} (${vicIS(IB, "auc")});`,
  `pAUC: ${mediaIS(IB, "pauc")}, ${icIS(IB, "pauc")} (${vicIS(IB, "pauc")}), un intervalo que, con la precisión guardada, no excluye el cero;`,
  `sensibilidad top-15: ${mediaIS(IB, "setop15")}, ${icIS(IB, "setop15")} (${vicIS(IB, "setop15")});`,
  `NNT80% SE: ${mediaIS(IB, "nnt80")} lesiones por cada maligna, ${icIS(IB, "nnt80")} (${vicIS(IB, "nnt80")}).`]) + P([
  `Sobre la zona del cuerpo, las fuentes no coinciden. La tabla de variables del artículo del conjunto de datos la marca como ` +
  `una métrica del software del sistema; el artículo de los organizadores la cuenta entre los datos básicos, que ${citaIS("datos_basicos")}.`,
  `Después se entrenó una red de imagen sobre los recortes, EfficientNet-B0, en cada pliegue. ` +
  `Su pAUC media es de ${cifra(dec(F4C.red_sola.media_nuevo), fF4cM("red_sola", "Red"))}, frente a ` +
  `${cifra(dec(F4C.red_sola.media_base), fF4cM("red_sola", "Imagen"))} de la imagen sola con DINOv2, y queda por encima en ` +
  `${cifra(RS.pauc.folds, fF4c("red_sola", "pauc", "nuevo_mejor_en_folds"))} de ${cifra(RS.pauc.de_folds, fF4c("red_sola", "pauc", "de_folds"))} ` +
  `pliegues y en las ${cifra(RS.pauc.semillas, fF4c("red_sola", "pauc", "nuevo_mejor_en_semillas"))} semillas. ` +
  `Con la corrección por haber hecho dos preguntas, el intervalo de la diferencia, ` +
  `${cifra(firmado(RS.pauc.media), fF4c("red_sola", "pauc", "media"))}, va de ` +
  `${cifra(dec(RS.pauc.bonferroni[0]), bonfF4c("red_sola", "pauc"))} a ${cifra(dec(RS.pauc.bonferroni[1]), bonfF4c("red_sola", "pauc"))}, ` +
  `así que la regla fijada antes no la da por establecida. En el AUC estándar, que no decide, sí queda entero por encima de cero: ` +
  `${cifra(firmado(RS.auc.media), fF4c("red_sola", "auc", "media"))}, ${ic(RS.auc.bonferroni[0], RS.auc.bonferroni[1], bonfF4c("red_sola", "auc"))}; ` +
  `en la sensibilidad top-15 y el NNT80% SE, el intervalo contiene el cero.`,
  `<i>Interpretación, no medición:</i> sin el sistema de fotografía corporal total, la imagen sí sirve para ordenar lesiones ` +
  `por sospecha, aunque con el extractor congelado, DINOv2, queda lejos de M1. Edad, sexo y zona del cuerpo son ` +
  `datos que una persona puede informar sin aparatos, aunque en estos datos la zona del cuerpo pudo venir del software del sistema. El ganador ajustó sus propias redes de imagen, y su variante con solo los ` +
  `recortes llega a un AUC de ${auc922}, pero en otros datos y con otra evaluación, así que las cifras no se comparan. ` +
  `Y todo esto se midió sobre los recortes del sistema de fotografía corporal total, no sobre fotos de teléfono.`,
  // borrador-v2.md, «Resultados», el final de «La imagen sola, sin el sistema de fotografía corporal total».
  `La red de la Fase 4e, la EfficientNet-B0 con la receta del décimo puesto y el ajuste fino que se describen en ` +
  `«Recomendación», queda sola por encima de la red de la Fase 4c: ${medQ("Red4eAjustada", "nuevo")} frente a ` +
  `${medQ("Red4eAjustada", "base")}, ${mediaQ("Red4eAjustada", "pauc")}, ${icQ("Red4eAjustada", "pauc")} (${vicQ("Red4eAjustada", "pauc")}). ` +
  `En el AUC, ${mediaQ("Red4eAjustada", "auc")}, ${icQ("Red4eAjustada", "auc")}, y en la sensibilidad top-15, ` +
  `${mediaQ("Red4eAjustada", "setop15")}, ${icQ("Red4eAjustada", "setop15")}, el intervalo también excluye el cero; en el NNT80% SE, no.`,
  `Aun así, la regla no la da por establecida. Su valor p, ${cifra(fijo(RH.p, 4), fH4e("preguntas[0].valor_p"))}, no llega al ` +
  `umbral de Holm para la primera de dos preguntas, ${cifra(dec(RH.umbral), fH4e("preguntas[0].umbral_holm"))}; con una sola ` +
  `pregunta, el umbral habría sido ${cifra(dec(RH.alfa), fH4e("alfa"))}. Lo que decide es la corrección por multiplicidad, ` +
  `fijada antes de correr. Es el mismo tipo de hallazgo que el de la sección 2: una decisión de método, aquí cuántas ` +
  `preguntas se corrigen juntas, cambia el veredicto.`,
  `Después se comparó esa red con «Imagen + básicos», el punto de partida que el informe daba para el escenario sin ` +
  `fotografía corporal total, en los mismos ${cifra(F4F.metricas.pauc.de_folds, fF("pauc", "de_folds"))} pliegues de la ` +
  `confirmación. La pregunta se eligió después de ver la Fase 4e, y se declara así: la diferencia de medias ya se podía ` +
  `calcular con lo guardado, y el valor p no se había calculado.`,
  `Con la regla de una sola pregunta, la red supera a «Imagen + básicos»: ` +
  `${cifra(dec(F4F.media_red), "fase4f-red4e-vs-imagen-basicos.json > metricas.Red4eAjustada.pauc.media_global")} frente a ` +
  `${cifra(dec(F4F.media_ib), "fase4f-red4e-vs-imagen-basicos.json > metricas.ImagenBasicos.pauc.media_global")}, ` +
  `${mediaF("pauc")}, ${icF("pauc")} (${vicF("pauc")}), con un valor p de ${cifra(fijo(F4F.metricas.pauc.p, 4), fF("pauc", "valor_p_nadeau_bengio"))}. ` +
  `Las tres métricas secundarias van en la misma dirección, con intervalos que excluyen el cero: AUC ${mediaF("auc")}, ` +
  `${icF("auc")}; sensibilidad top-15 ${mediaF("setop15")}, ${icF("setop15")}, y NNT80% SE ${mediaF("nnt80")}, ${icF("nnt80")}.`,
  `Por la regla, la recomendación para ese escenario pasó a la red, que además usa menos datos de entrada: solo la imagen, ` +
  `sin edad, sexo ni zona del cuerpo. Se midió sobre los recortes de SLICE-3D, no sobre fotos de teléfono.`]);
// Rediseño, paso 2, gráfico 2: la pAUC media de los cuatro modelos de imagen, cada
// uno con sus semillas, y M1 como línea de referencia. El tooltip de cada barra da
// sus campos y los de M1.
const GI = D.imagen_barras;
const referenciaM1 = {
  id: "referenciaM1",
  afterDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(GI.m1.pauc), a = ch.chartArea, cx = ch.ctx;
    cx.save();
    cx.strokeStyle = "#b8341f"; cx.setLineDash([6, 4]); cx.lineWidth = 1.8;
    cx.beginPath(); cx.moveTo(a.left, y); cx.lineTo(a.right, y); cx.stroke();
    // El rótulo va a la izquierda, sobre las barras más bajas: a la derecha
    // chocaba con el valor de la red de la 4e, que queda casi en la línea.
    const texto = `M1, ${GI.m1.semillas}: ${dec(GI.m1.pauc)}`;
    cx.font = "600 11px -apple-system, sans-serif"; cx.textAlign = "left";
    const ancho = cx.measureText(texto).width, x = a.left + 6;
    cx.fillStyle = "rgba(255,255,255,.85)"; cx.fillRect(x - 4, y - 18, ancho + 8, 15);
    cx.fillStyle = "#b8341f"; cx.fillText(texto, x, y - 7);
    // El valor de cada barra, encima de ella.
    cx.fillStyle = "#16202b"; cx.textAlign = "center";
    ch.getDatasetMeta(0).data.forEach((barra, i) => cx.fillText(dec(GI.barras[i].pauc), barra.x, barra.y - 6));
    cx.restore();
  }
};
new Chart(document.getElementById("gr-imagen"), {
  type: "bar",
  plugins: [referenciaM1],
  data: {
    labels: GI.barras.map(b => [b.etiqueta, b.semillas]),
    datasets: [{ data: GI.barras.map(b => b.pauc), backgroundColor: ["#9db7cc", "#7fa3bf", "#4a7fa5", "#1f5f8b"],
                 borderRadius: 4, maxBarThickness: 90 }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: { y: { beginAtZero: true, suggestedMax: D.escala.maximo,
                   title: { display: true, text: "pAUC media en el desarrollo" } } },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: it => `${GI.barras[it[0].dataIndex].etiqueta}, ${GI.barras[it[0].dataIndex].semillas}`,
          label: it => "pAUC " + dec(GI.barras[it.dataIndex].pauc),
          afterLabel: it => {
            const b = GI.barras[it.dataIndex];
            return [`${b.archivo} > ${b.campo}`, `${b.archivo} > ${b.campo_semillas}`,
                    `M1, la línea: imagen-sola.json > metricas.M1.pauc.media_global y esquema.semillas`];
          }
        }
      }
    }
  }
});
document.getElementById("det-4").innerHTML = resto4 + lectura4 +
  `<h3>La imagen sola, sin el sistema de fotografía corporal total</h3>` + resto4b;

/* ---------- 5. fuera del conjunto de desarrollo ---------- */
// borrador-v2.md, «Resultados», «El conjunto reservado, abierto una sola vez».
const M3L = COMP["M3 limpio − M2"].metricas;
// Rediseño, paso 3: a la vista, la frase del resultado; la que describe la
// apertura vuelve al «Detalle», al principio de su párrafo.
document.getElementById("frase-reservado").innerHTML =
  `Con pacientes con los que no se entrenó ningún modelo, la ventaja de M3 limpio sobre M2 se mantiene en la pAUC y el AUC.`;
const restoReservado = P([
  `El conjunto reservado se abrió una sola vez, con todo fijado antes: M3 limpio, el modelo recomendado, y M2 como ` +
  `referencia, entrenados con todo el desarrollo, y, como resultado descriptivo, la red de la Fase 4e e «Imagen + básicos». ` +
  `Son ${cifra(RES.pacientes, fRes("datos.evaluacion.pacientes"))} pacientes, con ${cifra(RES.malignas, fRes("datos.evaluacion.malignas"))} ` +
  `lesiones malignas repartidas en ${cifra(RES.pacientes_con_malignas, fRes("datos.evaluacion.pacientes_con_malignas"))} de ellos. ` +
  `Los intervalos salen de un bootstrap por paciente con ${cifra(mil(RES.remuestras), fRes("bootstrap.remuestras"))} remuestras.`,
  `M3 limpio da una pAUC de ${cifra(dec(RES.m3.punto), fRes("metricas.M3limpio.pauc.punto"))}, ` +
  `${icRes(RES.m3, fRes("metricas.M3limpio.pauc.intervalo_95"))}, y supera a M2, ${cifra(dec(RES.m2.punto), fRes("metricas.M2.pauc.punto"))}, ` +
  `por ${cifra(firmado(RES.dif.pauc.punto), fRes("diferencia_m3limpio_menos_m2.pauc.punto"))}, ` +
  `${icRes(RES.dif.pauc, fRes("diferencia_m3limpio_menos_m2.pauc.intervalo_95"))}. En el AUC, ` +
  `${cifra(firmado(RES.dif.auc.punto), fRes("diferencia_m3limpio_menos_m2.auc.punto"))}, ` +
  `${icRes(RES.dif.auc, fRes("diferencia_m3limpio_menos_m2.auc.intervalo_95"))}. En el desarrollo, la diferencia en la pAUC era ` +
  `${mediaC("M3 limpio − M2", "pauc")}, ${ic(M3L.pauc.ic[0], M3L.pauc.ic[1], fComp("M3 limpio − M2", "pauc", D.clave_ic))}: en los dos ` +
  `lados, el intervalo excluye el cero y el signo es el mismo. En la sensibilidad top-15 y el NNT80% SE, el intervalo ` +
  `contiene el cero, como en el desarrollo. Los dos intervalos no miden lo mismo: en el desarrollo, el de la media por ` +
  `pliegue, con la corrección de Nadeau y Bengio; en el reservado, el de un solo modelo, con el bootstrap por paciente.`,
  `El reservado no es ajeno del todo: el diseño de las variables de M2 y de M3 limpio lo fijó el ganador sobre todo el ` +
  `conjunto de entrenamiento del reto, que incluye a estos pacientes.`,
  `La ventaja de la red sobre «Imagen + básicos» no se reprodujo. En el reservado, la red da ` +
  `${cifra(dec(RES.red), fRes("metricas.Red4e.pauc.punto"))} e «Imagen + básicos», ${cifra(dec(RES.ib), fRes("metricas.ImagenBasicos.pauc.punto"))}; ` +
  `la diferencia es de ${cifra(firmado(RES.red_menos_ib.pauc.punto), fPos("red4e_menos_imagen_basicos.pauc.punto"))}, ` +
  `${icRes(RES.red_menos_ib.pauc, fPos("red4e_menos_imagen_basicos.pauc.intervalo_95"))}. En la sensibilidad top-15 la red ` +
  `queda por encima, ${cifra(firmado(RES.red_menos_ib.setop15.punto), fPos("red4e_menos_imagen_basicos.setop15.punto"))}, pero el ` +
  `intervalo, ${icRes(RES.red_menos_ib.setop15, fPos("red4e_menos_imagen_basicos.setop15.intervalo_95"))}, contiene el cero, como los ` +
  `de las otras tres métricas; en la Fase 4f, los cuatro lo excluían. Por qué «Imagen + básicos» da más en el reservado que ` +
  `en el desarrollo no está medido.`,
  `Por la regla fijada antes, el reservado no cambia ninguna recomendación: la estimación principal sigue siendo la ` +
  `validación cruzada repetida. Pero la ventaja de la red sobre «Imagen + básicos» no quedó confirmada con los pacientes reservados.`]);
// borrador-v2.md, «Resultados», «En la prueba de Kaggle».
const CP = KG.comparaciones, fCP = (k, c) => fK(`comparaciones_con_la_privada.${k}.${c}`);
document.getElementById("frase-kaggle").innerHTML =
  `Kaggle sigue aceptando envíos a la competición cerrada, y a cada uno le dio una puntuación pública y una privada, sin ` +
  `intervalo.`;
const restoKaggle = P([
  `Se enviaron cuatro modelos entrenados con los ` +
  `${cifra(mil(KG.pacientes), fRes("datos.entrenamiento.pacientes") + " + datos.evaluacion.pacientes")} pacientes, cada uno una ` +
  `sola vez: M3 limpio, la red de la 4e y C7, fijados antes de abrir el reservado, y un cuarto, «Imagen + básicos», decidido ` +
  `después. Que la puntuación privada salga del mismo subconjunto de la prueba que el tablero final del reto es lectura ` +
  `nuestra: ninguna fuente versionada lo dice.`,
  `En la puntuación privada, C7 obtiene ${cifra(dec(CP.c7_menos_ganador.modelo), fCP("c7_menos_ganador", "modelo"))}, y el ganador, ` +
  `${cifra(dec(CP.c7_menos_ganador.referencia), fCP("c7_menos_ganador", "referencia"))}: una diferencia de ` +
  `${cifra(firmado(CP.c7_menos_ganador.diferencia), fCP("c7_menos_ganador", "diferencia"))}. M3 limpio obtiene ` +
  `${cifra(dec(CP.m3limpio_menos_sin_imagenes.modelo), fCP("m3limpio_menos_sin_imagenes", "modelo"))}, frente a ` +
  `${cifra(dec(CP.m3limpio_menos_sin_imagenes.referencia), fCP("m3limpio_menos_sin_imagenes", "referencia"))} de la versión del ganador ` +
  `sin imágenes, que usa la etiqueta del hospital; la red sola, ${cifra(dec(CP.red4e_menos_solo_imagenes.modelo), fCP("red4e_menos_solo_imagenes", "modelo"))}, ` +
  `frente a ${cifra(dec(CP.red4e_menos_solo_imagenes.referencia), fCP("red4e_menos_solo_imagenes", "referencia"))} de la versión que solo ` +
  `usa las imágenes. Esas dos versiones son de la reproducción del ganador que hicieron los organizadores, sobre el conjunto ` +
  `del tablero privado, con tres decimales.`,
  `El cuarto envío comparó la red con «Imagen + básicos» en Kaggle. Se decidió después de ver el reservado, y se declara así. ` +
  `La red obtiene ${priv("Red4e")} e «Imagen + básicos», ${priv("ImagenBasicos")}: en la privada, la red vuelve a quedar por ` +
  `encima, como en el desarrollo y al revés que en el reservado.`]);
const fTres = (m, c) => fK(`tabla_tres_evaluaciones.${m}.${c}`);
document.getElementById("tabla-tres").innerHTML =
  `<thead><tr><th>Modelo</th><th>Desarrollo, semillas 5 a 9</th><th>Reservado</th><th>Kaggle, privada</th></tr></thead><tbody>` +
  Object.entries(KG.tabla).map(([m, f]) => `<tr><td>${esc(KG.nombres[m])}</td>` +
    `<td>${cifra(dec(f.desarrollo), fTres(m, "desarrollo"))}</td>` +
    `<td>${f.reservado === null ? "no se evaluó" : cifra(dec(f.reservado), fTres(m, "reservado.pauc"))}</td>` +
    `<td>${cifra(dec(f.kaggle), fTres(m, "kaggle_privada.pauc"))}</td></tr>`).join("") + `</tbody>`;
const restoKaggle2 = P([
  `En el desarrollo y en Kaggle, los cuatro modelos quedan en el mismo orden; en el reservado, «Imagen + básicos» queda por ` +
  `encima de la red.`,
  `Para descomponer la distancia al ganador se hicieron cuatro envíos más, en un diseño de dos por dos fijado antes de ` +
  `entrenarlos: con imagen o sin ella, y con la etiqueta del hospital o sin ella. En los cuatro, la parte tabular es la media ` +
  `de varios CatBoost, uno por pliegue y semilla, como los que entrena el código del ganador; cómo combina él sus ` +
  `predicciones en la prueba no está en su notebook. El diseño se decidió después de ver los primeros envíos, y con él el ` +
  `proyecto cerró Kaggle: no se envía nada más.`,
  `Promediar sube la puntuación privada en ${efecto("promediar_sin_imagen")} sin imagen y en ${efecto("promediar_con_imagen")} ` +
  `con imagen, con el mismo signo en la pública. El hospital suma ${efecto("hospital_sin_imagen")} sin imagen y ` +
  `${efecto("hospital_con_imagen")} con imagen, y este último cambia de signo en la pública. C7 promediado obtiene ` +
  `${priv("C7Prom")}, y con el hospital, ${priv("C7PromHosp")}.`,
  `Como aritmética descriptiva, de la diferencia de C7 con el ganador, ${cifra(firmado(DES.distancia_de_c7_al_ganador), fDes("distancia_de_c7_al_ganador"))}, ` +
  `promediar cubre ${cifra(firmado(DES.cubre_promediar), fDes("cubre_promediar"))}, el ` +
  `${cifra(dec(DES.porcentaje_de_la_distancia.promediar) + "%", fDes("porcentaje_de_la_distancia.promediar"))}; el hospital, ` +
  `${cifra(firmado(DES.cubre_el_hospital), fDes("cubre_el_hospital"))}, el ` +
  `${cifra(dec(DES.porcentaje_de_la_distancia.hospital) + "%", fDes("porcentaje_de_la_distancia.hospital"))}, y quedan ` +
  `${cifra(firmado(DES.queda), fDes("queda"))}, el ${cifra(dec(DES.porcentaje_de_la_distancia.queda) + "%", fDes("porcentaje_de_la_distancia.queda"))}.`,
  `De las dos mejoras de la descomposición, promediar es la única que no usa datos que el proyecto excluyó, y casi la ` +
  `mitad de la distancia no la cubre ninguna de las dos. Ninguno de estos envíos cambia una recomendación.`]);
// La frase que hacía de subtítulo de la sección va también al «Detalle».
// Rediseño, paso 2, gráfico 3: la tabla de tres evaluaciones pasa al «Detalle», y
// la frase de que no miden lo mismo, al pie del gráfico.
document.getElementById("pie-tres").innerHTML =
  `Son conjuntos y estimaciones distintos: la media por pliegue en el desarrollo, un solo modelo en el ` +
  `reservado y una sola puntuación en Kaggle, sin intervalo.`;
const EVAL = [
  { nombre: `Desarrollo, ${KG.semillas_desarrollo}`, clave: "desarrollo", color: "#9db7cc",
    campo: m => `fase5b-comparacion.json > tabla_tres_evaluaciones.${m}.desarrollo (la de ${KG.semillas_desarrollo})` },
  { nombre: "Reservado, con el intervalo del bootstrap por paciente", clave: "reservado", color: "#1f5f8b",
    campo: m => `fase5b-comparacion.json > tabla_tres_evaluaciones.${m}.reservado.pauc; fase5-reservado.json > metricas.${m}.pauc.intervalo_95` },
  { nombre: "Kaggle, privada", clave: "kaggle", color: "#d08c3a",
    campo: m => `fase5b-comparacion.json > tabla_tres_evaluaciones.${m}.kaggle_privada.pauc` },
];
const MODELOS_TRES = Object.keys(KG.tabla);
// El intervalo del reservado, como bigote sobre su barra, y «no se evaluó» donde
// el modelo no entró en el reservado.
const bigotesReservado = {
  id: "bigotesReservado",
  afterDatasetsDraw(ch) {
    const meta = ch.getDatasetMeta(1), y = ch.scales.y, cx = ch.ctx;
    cx.save(); cx.strokeStyle = "#16202b"; cx.lineWidth = 1.5;
    meta.data.forEach((barra, i) => {
      const f = KG.tabla[MODELOS_TRES[i]];
      if (f.reservado_ic === null) {
        cx.save(); cx.translate(barra.x, ch.chartArea.bottom - 6); cx.rotate(-Math.PI / 2);
        cx.font = "11px -apple-system, sans-serif"; cx.fillStyle = "#5b6b7c"; cx.textAlign = "left";
        cx.fillText("no se evaluó", 0, 4); cx.restore();
        return;
      }
      const arriba = y.getPixelForValue(f.reservado_ic[1]), abajo = y.getPixelForValue(f.reservado_ic[0]), x = barra.x;
      cx.beginPath();
      cx.moveTo(x, arriba); cx.lineTo(x, abajo);
      cx.moveTo(x - 6, arriba); cx.lineTo(x + 6, arriba);
      cx.moveTo(x - 6, abajo); cx.lineTo(x + 6, abajo);
      cx.stroke();
    });
    cx.restore();
  }
};
new Chart(document.getElementById("gr-tres"), {
  type: "bar",
  plugins: [bigotesReservado],
  data: {
    labels: MODELOS_TRES.map(m => KG.nombres[m]),
    datasets: EVAL.map(e => ({ label: e.nombre, data: MODELOS_TRES.map(m => KG.tabla[m][e.clave]),
                              backgroundColor: e.color, borderRadius: 3 }))
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    scales: { y: { beginAtZero: true, suggestedMax: D.escala.maximo, title: { display: true, text: "pAUC" } } },
    plugins: {
      // La leyenda va en HTML (leyenda-tres): la de Chart.js cortaba a 375 px el
      // rótulo del reservado.
      legend: { display: false },
      title: { display: true, text: "La pAUC de los cuatro modelos en las tres evaluaciones", align: "start" },
      tooltip: {
        callbacks: {
          label: it => {
            const f = KG.tabla[MODELOS_TRES[it.dataIndex]], e = EVAL[it.datasetIndex];
            return `${e.nombre.split(",")[0]}: ${dec(f[e.clave])}` +
                   (e.clave === "reservado" ? `, [${dec(f.reservado_ic[0])}; ${dec(f.reservado_ic[1])}]` : "");
          },
          afterLabel: it => EVAL[it.datasetIndex].campo(MODELOS_TRES[it.dataIndex])
        }
      }
    }
  }
});
// Gráfico 4 (rehecho el 2026-11-06): la distancia de C7 al ganador en la privada,
// como una sola barra partida en tres tramos —promediar, el hospital y lo que queda
// sin explicar—, y debajo el recorrido de cuatro puntos con sus pAUC privadas. Las
// dos figuras comparten la escala, así que cada tramo va de un punto al siguiente.
// Los tramos son campos de descomposicion_de_la_distancia_al_ganador; los puntos,
// de kaggle.*.privada; construir_datos comprueba que coinciden. Sustituye a una
// cascada con el eje en negativo, que no se entendía. La salvedad del orden va al
// pie.
document.getElementById("pie-cascada").innerHTML =
  `El reparto depende del orden: C7 con el hospital y sin promediar no se envió.`;
const fDesc = c => fE("descomposicion_de_la_distancia_al_ganador." + c);
const RECORRIDO = [
  { nombre: "C7", pauc: KG.privadas.C7, campo: fE("kaggle.C7.privada"), color: "#c98b7a" },
  { nombre: "C7 promediado", pauc: KG.privadas.C7Prom, campo: fE("kaggle.C7Prom.privada"), color: "rgba(30,122,82,.9)" },
  { nombre: "C7 promediado + hospital", pauc: KG.privadas.C7PromHosp, campo: fE("kaggle.C7PromHosp.privada"), color: "#d08c3a" },
  { nombre: "Ganador", pauc: DES.ganador.pauc, campo: fDesc("ganador.pauc"), color: "#16202b" },
];
const TRAMOS = [
  { nombre: "Promediar", campo: "cubre_promediar", pct: "promediar", color: "rgba(30,122,82,.75)", texto: "#fff" },
  { nombre: "Hospital", campo: "cubre_el_hospital", pct: "hospital", color: "#d08c3a", texto: "#fff" },
  { nombre: "Sin explicar", campo: "queda", pct: "queda", color: "rgba(91,107,124,.35)", texto: "#16202b" },
].map((t, i) => ({ ...t, desde: RECORRIDO[i].pauc, hasta: RECORRIDO[i + 1].pauc,
                   etiqueta: `${firmado(DES[t.campo])} (${dec(DES.porcentaje_de_la_distancia[t.pct])}%)` }));
// La misma escala horizontal y el mismo relleno en las dos figuras, sin ejes
// verticales: así sus áreas de dibujo quedan alineadas. El relleno tiene que
// cubrir la mitad del rótulo de los extremos del eje del recorrido; con 12 px,
// Chart.js le añadía 6 y los tramos se desviaban de los puntos hasta 5 px.
const margenX = (DES.ganador.pauc - KG.privadas.C7) * 0.06;
const ejeX = { type: "linear", min: KG.privadas.C7 - margenX, max: DES.ganador.pauc + margenX };
const rellenoX = { left: 24, right: 24 };
// Dentro de cada tramo, su nombre y su valor con el porcentaje si caben; si no,
// solo el porcentaje, y si tampoco, nada: la leyenda de debajo lo da siempre.
const rotulosTramos = {
  id: "rotulosTramos",
  afterDatasetsDraw(ch) {
    const cx = ch.ctx;
    cx.save(); cx.textAlign = "center"; cx.textBaseline = "middle";
    TRAMOS.forEach((t, i) => {
      const b = ch.getDatasetMeta(i).data[0], ancho = Math.abs(b.x - b.base), xc = (b.x + b.base) / 2;
      const pct = `${dec(DES.porcentaje_de_la_distancia[t.pct])}%`;
      cx.fillStyle = t.texto;
      cx.font = "600 11px -apple-system, sans-serif";
      const necesita = Math.max(cx.measureText(t.nombre).width, cx.measureText(t.etiqueta).width) + 10;
      if (ancho >= necesita) {
        cx.fillText(t.nombre, xc, b.y - 8);
        cx.font = "11px -apple-system, sans-serif"; cx.fillText(t.etiqueta, xc, b.y + 8);
      } else if (ancho >= cx.measureText(pct).width + 6) {
        cx.fillText(pct, xc, b.y);
      }
    });
    cx.restore();
  }
};
new Chart(document.getElementById("gr-distancia"), {
  type: "bar",
  plugins: [rotulosTramos],
  data: {
    labels: ["Distancia de C7 al ganador"],
    datasets: TRAMOS.map(t => ({ label: t.nombre, data: [[t.desde, t.hasta]], backgroundColor: t.color,
                                 grouped: false, borderSkipped: false, borderRadius: 0, barPercentage: 1, categoryPercentage: .85 }))
  },
  options: {
    indexAxis: "y", responsive: true, maintainAspectRatio: false,
    layout: { padding: rellenoX },
    scales: { x: { ...ejeX, display: false }, y: { display: false } },
    plugins: {
      legend: { display: false },
      title: { display: true, text: "La distancia de C7 al ganador en la privada de Kaggle", align: "start" },
      tooltip: {
        callbacks: {
          title: () => `Distancia de C7 al ganador: ${firmado(DES.distancia_de_c7_al_ganador)}`,
          label: it => `${TRAMOS[it.datasetIndex].nombre}: ${TRAMOS[it.datasetIndex].etiqueta}`,
          afterLabel: it => {
            const t = TRAMOS[it.datasetIndex];
            return [fDesc(t.campo), fDesc("porcentaje_de_la_distancia." + t.pct),
                    `De ${RECORRIDO[it.datasetIndex].nombre} a ${RECORRIDO[it.datasetIndex + 1].nombre}`];
          }
        }
      }
    }
  }
});
leyenda("leyenda-distancia", [
  [null, `Distancia de C7 al ganador: ${cifra(firmado(DES.distancia_de_c7_al_ganador), fDesc("distancia_de_c7_al_ganador"))}`],
  ...TRAMOS.map(t => [`background:${t.color}`,
    `${t.nombre} ${cifra(firmado(DES[t.campo]), fDesc(t.campo))} ` +
    `(${cifra(dec(DES.porcentaje_de_la_distancia[t.pct]) + "%", fDesc("porcentaje_de_la_distancia." + t.pct))})`])]);
// El recorrido: los rótulos se alternan arriba y abajo para que no choquen a 375 px,
// y los de los extremos se alinean hacia dentro.
const rotulosRecorrido = {
  id: "rotulosRecorrido",
  afterDatasetsDraw(ch) {
    const cx = ch.ctx, puntos = ch.getDatasetMeta(0).data;
    cx.save(); cx.font = "600 11px -apple-system, sans-serif"; cx.fillStyle = "#16202b";
    RECORRIDO.forEach((p, i) => {
      const {x, y} = puntos[i], arriba = i % 2 === 0;
      cx.textAlign = i === 0 ? "left" : i === RECORRIDO.length - 1 ? "right" : "center";
      const xt = i === 0 ? x - 6 : i === RECORRIDO.length - 1 ? x + 6 : x;
      const [l1, l2] = arriba ? [p.nombre, dec(p.pauc)] : [dec(p.pauc), p.nombre];
      const y1 = arriba ? y - 26 : y + 20, y2 = arriba ? y - 12 : y + 34;
      cx.font = arriba ? "600 11px -apple-system, sans-serif" : "11px -apple-system, sans-serif"; cx.fillText(l1, xt, y1);
      cx.font = arriba ? "11px -apple-system, sans-serif" : "600 11px -apple-system, sans-serif"; cx.fillText(l2, xt, y2);
    });
    cx.restore();
  }
};
new Chart(document.getElementById("gr-recorrido"), {
  type: "scatter",
  plugins: [rotulosRecorrido],
  data: {
    datasets: [{ data: RECORRIDO.map(p => ({ x: p.pauc, y: 0 })), showLine: true, borderColor: "#5b6b7c", borderWidth: 1.5,
                 pointRadius: 6, pointHoverRadius: 8, pointBackgroundColor: RECORRIDO.map(p => p.color), pointBorderColor: "#fff" }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    layout: { padding: rellenoX },
    scales: { x: { ...ejeX, title: { display: true, text: "pAUC privada de Kaggle" } },
              y: { display: false, min: -1, max: 1 } },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: it => `${RECORRIDO[it.dataIndex].nombre}: ${dec(RECORRIDO[it.dataIndex].pauc)}`,
          afterLabel: it => RECORRIDO[it.dataIndex].campo
        }
      }
    }
  }
});
leyenda("leyenda-tres", EVAL.map(e => [`background:${e.color}`, e.nombre]));
document.getElementById("det-5a").innerHTML =
  P([`El conjunto reservado, abierto una sola vez, y Kaggle, que da una sola cifra por envío.`]) +
  `<h3>El conjunto reservado, abierto una sola vez</h3>` + restoReservado +
  `<h3>En la prueba de Kaggle</h3>` + restoKaggle;
document.getElementById("det-5b").innerHTML = restoKaggle2;

/* ---------- 6. la pregunta del cliente, entera ---------- */
// borrador-v2.md, «Resultados», «La pregunta del cliente, entera»: la cabecera y las filas, con las cifras de outputs/.
const fMet = (f, k) => `${f.archivo} > metricas.${f.clave}.${k}.media_global`;
document.getElementById("tabla-ejes").innerHTML =
  `<thead><tr><th>Modelo</th><th>pAUC</th><th>Sensibilidad top-15</th><th>NNT80% SE</th><th>Segundos por ${milLesiones} lesiones</th></tr></thead><tbody>` +
  D.tabla.map(f => `<tr><td>${esc(f.modelo)}</td><td>${cifra(fijo(f.pauc, 4), fMet(f, "pauc"))}</td>` +
    `<td>${cifra(fijo(f.setop15, 4), fMet(f, "setop15"))}</td><td>${cifra(fijo(f.nnt80, 2), fMet(f, "nnt80"))}</td>` +
    `<td>${tiempoT(f.modelo)}</td></tr>`).join("") + `</tbody>`;
// borrador-v2.md, «Resultados», «La pregunta del cliente, entera» y «El costo de inferencia».
document.getElementById("frase-6").innerHTML =
  `La tabla responde la pregunta con sus tres ejes —la métrica principal, la sensibilidad por paciente y el costo— y añade el NNT80% SE, la segunda métrica de triaje.`;
document.getElementById("det-6").innerHTML = P([
  `Son medias y medianas; las diferencias, con sus intervalos, están arriba. M2 se distingue de M1 en las dos métricas de triaje, no en la pAUC. ` +
  `Frente a M2, de los otros tres solo M3 limpio se distingue, y solo en la pAUC y en el AUC estándar; en las métricas de triaje no se distingue ninguno de los tres.`,
  `M3 limpio cuesta más que M2, pero los dos quedan por debajo de una décima de segundo por cada ${milLesiones} lesiones. ` +
  `Lo caro, con diferencia, es la imagen, y ni M4 ni M4b mejoraron a M2 en la métrica principal de forma distinguible.`]);

/* ---------- 7. recomendacion ---------- */
// Rediseño, paso 2, gráfico 5: las siete versiones frente a M3 limpio. Cada fila
// lleva el intervalo de la regla de su fase, rotulado y en otro color: el de
// Bonferroni en C1 a C4 y el de Nadeau y Bengio al 95 % en C5 a C7. La banda
// sombreada, detrás de C4 a C7, es lo que la prueba distingue con un 80 % de
// probabilidad, calculado con la variabilidad de esas cuatro.
const SV = D.siete;
const esBonf = f => f.confianza !== null;
const rotuloIC = f => esBonf(f) ? `Bonferroni, ${dec(Math.round(f.confianza * 1000) / 10)} %` : "95 %, Nadeau y Bengio";
const bandaYmedias = {
  id: "bandaYmedias",
  beforeDatasetsDraw(ch) {
    const x = ch.scales.x, y = ch.scales.y, cx = ch.ctx;
    const filas = SV.filas.map((f, i) => SV.banda_de.includes(f.nombre) ? i : null).filter(i => i !== null);
    const paso = (y.getPixelForValue(1) - y.getPixelForValue(0)) / 2;
    const arriba = y.getPixelForValue(filas[0]) - paso, abajo = y.getPixelForValue(filas[filas.length - 1]) + paso;
    const izq = x.getPixelForValue(SV.banda[0]), der = x.getPixelForValue(SV.banda[1]);
    cx.save();
    cx.fillStyle = "rgba(201,139,122,.22)"; cx.fillRect(izq, arriba, der - izq, abajo - arriba);
    // El rótulo, justo encima de la banda: dentro chocaba con la barra de C4. Sin
    // salirse por la derecha, que a 375 px lo cortaba.
    cx.font = "600 11px -apple-system, sans-serif"; cx.fillStyle = "#8a4a3a"; cx.textAlign = "center";
    const rotulo = "δ al 80 %", medio = cx.measureText(rotulo).width / 2;
    cx.fillText(rotulo, Math.min((izq + der) / 2, ch.chartArea.right - medio - 2), arriba - 4);
    cx.restore();
  },
  afterDatasetsDraw(ch) {
    const x = ch.scales.x, y = ch.scales.y, a = ch.chartArea, cx = ch.ctx;
    cx.save();
    const x0 = x.getPixelForValue(0);
    cx.strokeStyle = "#16202b"; cx.setLineDash([4, 3]); cx.lineWidth = 1.2;
    cx.beginPath(); cx.moveTo(x0, a.top); cx.lineTo(x0, a.bottom); cx.stroke();
    // El rótulo del cero, encima del área del gráfico: dentro tocaba la barra de C1.
    cx.font = "600 11px -apple-system, sans-serif"; cx.fillStyle = "#16202b"; cx.textAlign = "left";
    cx.fillText("M3 limpio", x0 + 4, a.top - 5);
    cx.setLineDash([]); cx.lineWidth = 2.5;
    SV.filas.forEach((f, i) => {
      const xm = x.getPixelForValue(f.media), ym = y.getPixelForValue(i);
      cx.beginPath(); cx.moveTo(xm, ym - 8); cx.lineTo(xm, ym + 8); cx.stroke();
    });
    cx.restore();
  }
};
new Chart(document.getElementById("gr-siete"), {
  type: "bar",
  plugins: [bandaYmedias],
  data: {
    labels: SV.filas.map(f => [f.nombre, rotuloIC(f)]),
    datasets: [
      { label: "Intervalo de Bonferroni, la regla de las fases 4b y 4c",
        data: SV.filas.map(f => esBonf(f) ? f.ic : null), backgroundColor: "rgba(91,107,124,.45)" },
      { label: "Intervalo al 95 % de Nadeau y Bengio; la regla de las fases 4d y 4e es Holm",
        data: SV.filas.map(f => esBonf(f) ? null : f.ic), backgroundColor: "rgba(255,255,255,0)",
        borderColor: "#1f5f8b", borderWidth: 2 }
    ].map(ds => ({ ...ds, grouped: false, borderSkipped: false, borderRadius: 3, barPercentage: .55 }))
  },
  options: {
    indexAxis: "y", responsive: true, maintainAspectRatio: false,
    layout: { padding: { top: 16 } },
    scales: { x: { title: { display: true, text: "Diferencia de pAUC con M3 limpio" } },
              // Sin saltar rótulos: a 375 px Chart.js dejaba sin nombre a C2, C4 y C6.
              y: { ticks: { autoSkip: false, font: c => ({ size: c.chart.width < 500 ? 10 : 12 }) } } },
    plugins: {
      legend: { display: false },
      tooltip: {
        filter: it => it.raw !== null,
        callbacks: {
          label: it => {
            const f = SV.filas[it.dataIndex];
            return `${f.nombre}: ${firmado(f.media)}, [${dec(f.ic[0])}; ${dec(f.ic[1])}], ${rotuloIC(f)}`;
          },
          afterLabel: it => {
            const f = SV.filas[it.dataIndex];
            const campos = [`${f.archivo} > comparaciones_nuevo_menos_base.pauc.media y .${f.clave_ic}`];
            if (esBonf(f)) campos.push(`${f.archivo} > comparaciones_nuevo_menos_base.pauc.confianza_bonferroni`);
            if (SV.banda_de.includes(f.nombre))
              campos.push(`Banda: potencia-nadeau-bengio.json > comparaciones.*.delta_80, de ${SV.banda_de[0]} a ${SV.banda_de[SV.banda_de.length - 1]}`);
            return campos;
          }
        }
      }
    }
  }
});
leyenda("leyenda-siete", [
  ["background:rgba(91,107,124,.45)", "Intervalo de Bonferroni, la regla de las fases 4b y 4c"],
  ["border:2px solid #1f5f8b;background:#fff", "Intervalo al 95 % de Nadeau y Bengio; la regla de las fases 4d y 4e es Holm"],
  ["background:rgba(201,139,122,.35)", `δ al 80 %, calculado con la variabilidad de ${SV.banda_de[0]} a ${SV.banda_de[SV.banda_de.length - 1]}`]]);
// borrador-v2.md, «Limitaciones», la viñeta de lo que la prueba distingue.
document.getElementById("pie-siete").innerHTML =
  `La prueba no distingue mejoras pequeñas frente a M3 limpio. Con la variabilidad observada, para dar su resultado a ` +
  `favor con un ${pctObj("delta_80")} de probabilidad necesita una mejora real de entre ${cifra(dec(POT.d80[0]), fPot("comparaciones.*.delta_80"))} ` +
  `y ${cifra(dec(POT.d80[1]), fPot("comparaciones.*.delta_80"))} de pAUC, y más semillas casi no bajan ese umbral.`;
// Las dos recomendaciones, en dos tarjetas: la de M3 limpio sale de la constante
// comprobada; la de la red, de la regla de la Fase 4f, que la página comprueba al
// generarse (datos_fases_4d_a_5c).
document.getElementById("reco-con").innerHTML = reco;
document.getElementById("reco-sin").innerHTML =
  cifra("Red de la Fase 4e", "fase4f-red4e-vs-imagen-basicos.json > regla.a_favor (la regla de la Fase 4f)");
// borrador-v2.md, «Resultados», «El modelo recomendado», los párrafos de las fases 4b y 4c: el texto y las cifras de las tablas.
const fIntento = (i, campo) => `${i.archivo} > comparaciones_nuevo_menos_base.pauc.${campo}`;
const intentos = P([
  `<b>Tres intentos de mejorarlo.</b> Antes de abrir el conjunto reservado se probaron tres combinaciones, fijadas antes de correr, contra M3 limpio. ` +
  `Como fueron tres intentos, el intervalo se corrige además por multiplicidad (Bonferroni). Ninguna lo supera en la pAUC.`]) +
  `<div class="tabla-envoltura"><table class="tabla-intentos"><thead><tr><th>Combinación</th>` +
  `<th>Diferencia con M3 limpio en la pAUC</th><th>Intervalo corregido (Bonferroni)</th></tr></thead><tbody>` +
  D.fase4b.map(i => `<tr><td>${esc(i.etiqueta)}</td><td>${cifra(firmado(i.media), fIntento(i, "media"))}</td>` +
    `<td>${ic(i.bonferroni[0], i.bonferroni[1], fIntento(i, "intervalo_bonferroni_nadeau_bengio"))}</td></tr>`).join("") +
  `</tbody></table></div>`;
const red4c = P([
  `<b>Una red de imagen entrenada.</b> Después se entrenó una red de imagen sobre los recortes y se hicieron dos preguntas, ` +
  `fijadas antes de correr, con el intervalo corregido por haber hecho dos (Bonferroni). Ninguna llega a la regla, aunque en las dos ` +
  `el modelo con la red queda por encima en las ` +
  `${cifra(C4.pauc.semillas, "fase4c-red-sola-vs-imagen.json y fase4c-c4-vs-m3limpio.json > comparaciones_nuevo_menos_base.pauc.nuevo_mejor_en_semillas")} semillas.`]) +
  `<div class="tabla-envoltura"><table class="tabla-intentos"><thead><tr><th>Pregunta</th><th>Diferencia en la pAUC</th>` +
  `<th>Intervalo corregido (Bonferroni)</th><th>Semillas en que gana</th></tr></thead><tbody>` +
  D.fase4c.map(q => `<tr><td>${esc(q.etiqueta)}</td><td>${cifra(firmado(q.metricas.pauc.media), fF4c(q.clave, "pauc", "media"))}</td>` +
    `<td>${ic(q.metricas.pauc.bonferroni[0], q.metricas.pauc.bonferroni[1], bonfF4c(q.clave, "pauc"))}</td>` +
    `<td>${cifra(q.metricas.pauc.semillas, fF4c(q.clave, "pauc", "nuevo_mejor_en_semillas"))} de ` +
    `${cifra(q.metricas.pauc.de_semillas, fF4c(q.clave, "pauc", "de_semillas"))}</td></tr>`).join("") +
  `</tbody></table></div>`;
// borrador-v2.md, «Resultados», «El modelo recomendado», los párrafos de las fases 4d y 4e, y «Lo que la prueba alcanza a ver».
const ronda4de = P([
  `<b>Dos rondas más, las fases 4d y 4e.</b> La retroalimentación del avance pidió acercarse al ganador con el equipo propio, ` +
  `antes de alquilar cómputo. Cada ronda tuvo sus preguntas y su regla fijadas antes de correr, con la corrección de Holm por ` +
  `varias preguntas. Holm no aceptó ninguna, y M3 limpio siguió siendo el modelo recomendado. Cada ronda se eligió conociendo ` +
  `los resultados de las anteriores, y su corrección cubre solo sus propias preguntas.`]) +
  `<div class="tabla-envoltura"><table class="tabla-intentos"><thead><tr><th>Pregunta</th><th>Fase</th>` +
  `<th>Diferencia en la pAUC</th><th>Intervalo al 95%</th><th>Valor p</th></tr></thead><tbody>` +
  PO.preguntas.map(q => `<tr><td>${esc(q.etiqueta)}</td><td>${esc(q.fase)}</td><td>${mediaQ(q.nuevo, "pauc")}</td>` +
    `<td>${icQ(q.nuevo, "pauc")}</td><td>${pQ(q.nuevo, "pauc")}</td></tr>`).join("") +
  `</tbody></table></div>` + P([
  `<b>Lo que la prueba alcanza a ver.</b> Las cuatro versiones que apilan una red de imagen sobre M3 limpio, de C4 a C7, ` +
  `quedaron por encima de él en la media, de ${cifra(firmado(POT.obs_min), fPot(`comparaciones.${POT.obs_min_de}.media_observada`))} a ` +
  `${cifra(firmado(POT.obs_max), fPot(`comparaciones.${POT.obs_max_de}.media_observada`))}, y ninguna diferencia llegó a la regla. ` +
  `Con la variabilidad observada, para dar su resultado a favor con un ${pctObj("delta_80")} de probabilidad, la prueba necesita ` +
  `una mejora real de entre ${cifra(dec(POT.d80[0]), fPot("comparaciones.*.delta_80"))} y ${cifra(dec(POT.d80[1]), fPot("comparaciones.*.delta_80"))} ` +
  `de pAUC, según la comparación y el número de semillas; para un ${pctObj("delta_50")}, de entre ` +
  `${cifra(dec(POT.d50[0]), fPot("comparaciones.*.delta_50"))} y ${cifra(dec(POT.d50[1]), fPot("comparaciones.*.delta_50"))}. ` +
  `Más semillas casi no ayudan: su error estándar entre semillas es entre ${cifra(dec(POT.razones[0]), fPot("comparaciones.*.entre_semillas.ee_prueba_sobre_ee_semillas"))} ` +
  `y ${cifra(dec(POT.razones[1]), fPot("comparaciones.*.entre_semillas.ee_prueba_sobre_ee_semillas"))} veces menor que el que usa la prueba. ` +
  `Lo que se midió es compatible con que no haya mejora, y también con una mejora que esta prueba no alcanza a ver.`]);
// borrador-v2.md, «Recomendación», «Qué se recomienda».
document.getElementById("frase-7").innerHTML =
  `<b>Al cliente se le recomienda ${reco}:</b> la parte tabular reproducida de la solución ganadora, sin los dos sesgos conocidos a su favor.`;
const resto7 = P([
  `Se eligió con una regla fijada antes de correr la comparación: el intervalo corregido de su diferencia con M2 en la pAUC queda entero por encima de cero. ` +
  `Ninguna de las versiones que se le compararon después de elegirlo, de la Fase 4b a la 4e, llegó a su regla, y en el ` +
  `conjunto reservado, abierto una sola vez, la ventaja sobre M2 se mantiene en la pAUC y en el AUC.`]) +
  intentos + red4c + ronda4de + P([
  `<b>Donde se toma la fotografía corporal total, no se recomienda, por ahora, añadir la imagen.</b> Añadida al modelo con ` +
  `contexto de paciente como variables de DINOv2, sueltas en M4 o apiladas en M4b, no mejoró ninguna métrica de forma distinguible, ` +
  `y al predecir esos dos modelos cuestan ${tiempoT("M4")} y ${tiempoT("M4b")} segundos por cada ${milLesiones} lesiones, frente a ${tiempoT("M3 limpio")} de M3 limpio. ` +
  `Eso no dice que la imagen no sirva para detectar cáncer: en la ablación de los organizadores, la variante del modelo ganador ` +
  `que solo usa los recortes llega a un AUC de ${auc922}, y la presentan como una base sólida para cuando no se pueden recoger ` +
  `los metadatos, como al usar la cámara de un teléfono. ` +
  `Con una red entrenada sobre los recortes y apilada sobre M3 limpio, las cuatro versiones, de C4 a C7, quedaron por encima de ` +
  `él en la media, y ninguna llegó a su regla; las cuatro diferencias quedan por debajo del tamaño que la prueba distingue con ` +
  `un ${pctObj("delta_50")} de probabilidad. En Kaggle, C7 queda por encima de M3 limpio en la puntuación privada, ` +
  `${cifra(firmado(KG.c7_menos_m3), fK("aritmetica_de_dos_fuentes.c7_menos_m3limpio_kaggle_privada"))}, sin intervalo. ` +
  `El tiempo de inferencia de C7 no se midió con el procedimiento del proyecto; el notebook de Kaggle, en otro equipo, lo ` +
  `proyectó en ${horas("C7")} horas por cada ${lesionesPrueba} lesiones, frente a ${horas("M3limpio")} horas de M3 limpio.`,
  `<i>Lectura, no medición:</i> con lo medido, no se puede decir si apilar la red sobre M3 limpio lo mejora: la mejora no se ` +
  `distingue, pero tampoco se descarta. Por eso la recomendación se queda, por ahora, con M3 limpio, sin imagen.`,
  `<b>Donde no hay ese sistema, M3 limpio no se puede aplicar tal cual, y la imagen es el insumo disponible.</b> ` +
  `Es el escenario que el artículo del conjunto de datos pone como objetivo: algoritmos que decidan a partir de ${citaIS("telefono")}. ` +
  `Ahí se recomienda la red de la Fase 4e, que usa solo la imagen. Por la regla de la Fase 4f, fijada antes de correr, supera a ` +
  `«Imagen + básicos», el punto de partida que daba antes el informe: ${mediaF("pauc")} de pAUC, ${icF("pauc")}, mejor en ` +
  `${cifra(F4F.metricas.pauc.folds, fF("pauc", "nuevo_mejor_en_folds"))} de ${cifra(F4F.metricas.pauc.de_folds, fF("pauc", "de_folds"))} pliegues.`,
  `Esta recomendación tiene tres salvedades. La pregunta se eligió después de ver la Fase 4e. En el conjunto reservado, la ventaja ` +
  `no se reprodujo: ${cifra(firmado(RES.red_menos_ib.pauc.punto), fPos("red4e_menos_imagen_basicos.pauc.punto"))}, ` +
  `${icRes(RES.red_menos_ib.pauc, fPos("red4e_menos_imagen_basicos.pauc.intervalo_95"))}, y por qué «Imagen + básicos» da más en el ` +
  `reservado no está medido. Y en Kaggle la red vuelve a quedar por encima, ${priv("Red4e")} frente a ${priv("ImagenBasicos")}, ` +
  `pero es una sola cifra por envío, sin intervalo, y ese envío se decidió después de ver el reservado. Por la regla fijada antes ` +
  `de abrirlo, el reservado no cambia la recomendación.`,
  `Para usarla con pacientes falta medir cómo rinde con fotos de teléfono y cuánto cuesta al predecir con el procedimiento del ` +
  `proyecto; el notebook de Kaggle, en otro equipo, lo proyectó en ${horas("Red4e")} horas por cada ${lesionesPrueba} lesiones. ` +
  `La red con edad, sexo y zona del cuerpo no se probó.`,
  `<i>Lectura, no medición:</i> como la red no usa la zona del cuerpo, no le alcanza la salvedad de «Imagen + básicos», cuya ` +
  `zona del cuerpo pudo venir del software del sistema.`,
  `<b>Y se recomienda no leer solo la pAUC.</b> El contexto de paciente no se nota en ella y sí en las dos métricas de triaje: la sensibilidad top-15 y el NNT80% SE.`]);
// borrador-v2.md, «Recomendación», «Qué se puede afirmar».
const masCercano = Object.entries(KG.privadas).sort((a, b) => b[1] - a[1]);
const SE_PUEDE = [
  `En el conjunto de desarrollo, con validación cruzada repetida y el intervalo corregido, M3 limpio supera a M2 en la pAUC y en el AUC estándar.`,
  `En el conjunto reservado, con pacientes con los que no se entrenó ningún modelo, M3 limpio también supera a M2 en la pAUC, ` +
  `${cifra(firmado(RES.dif.pauc.punto), fRes("diferencia_m3limpio_menos_m2.pauc.punto"))}, ${icRes(RES.dif.pauc, fRes("diferencia_m3limpio_menos_m2.pauc.intervalo_95"))}, ` +
  `y en el AUC, ${cifra(firmado(RES.dif.auc.punto), fRes("diferencia_m3limpio_menos_m2.auc.punto"))}, ${icRes(RES.dif.auc, fRes("diferencia_m3limpio_menos_m2.auc.intervalo_95"))}.`,
  `El contexto de paciente mejora frente a M1 la sensibilidad top-15 y el NNT80% SE.`,
  `Añadidas al modelo con contexto de paciente, las variables de imagen de DINOv2, como variables sueltas o apiladas, no mejoran de forma distinguible ninguna de las métricas.`,
  `Sin el sistema de fotografía corporal total, la imagen sola distingue lesiones malignas muy por encima del azar, pero con el extractor congelado, DINOv2, queda por debajo de M1 en las cuatro métricas.`,
  `En el conjunto de desarrollo, la red de la Fase 4e, que usa solo la imagen, supera a «Imagen + básicos» en la pAUC con la regla de una sola pregunta, y las tres métricas secundarias van en la misma dirección.`,
  `Una decisión de método cambia el veredicto sobre la red de la Fase 4e frente a la de la 4c. Su valor p, ` +
  `${cifra(fijo(RH.p, 4), fH4e("preguntas[0].valor_p"))}, no llega al umbral de Holm para la primera de dos preguntas, ` +
  `${cifra(dec(RH.umbral), fH4e("preguntas[0].umbral_holm"))}; con una sola pregunta, el umbral habría sido ${cifra(dec(RH.alfa), fH4e("alfa"))}.`,
  `Una partición por filas habría dejado al ${cifra(dec(DI.naive_pct) + "%", fDis("comparacion_particion_naive.pct_grupos_con_fuga"))} de los pacientes a los dos lados de la validación.`,
  `En la puntuación privada de Kaggle, ninguno de los ocho envíos llega a la del ganador, ` +
  `${cifra(dec(KG.ganador), fK("referencias.ganador_tablero_privado.pauc"))}. El más cercano, «${esc(KG.nombres[masCercano[0][0]])}», da ` +
  `${priv(masCercano[0][0])}, y el más cercano sin la etiqueta del hospital, «C7 promediado», ${priv("C7Prom")}. Son cifras sueltas, sin intervalo.`];
// borrador-v2.md, «Recomendación», «Qué no se puede afirmar».
const NO_SE_PUEDE = [
  `<b>Que M3 limpio sea mejor en las métricas de triaje.</b> En la sensibilidad top-15 y en el NNT80% SE no se distingue de M2.`,
  `<b>Cuál de los dos sesgos de M3 pesaba.</b> M3 limpio cambia tres cosas a la vez.`,
  `<b>Que la red de la Fase 4e supere a «Imagen + básicos» con pacientes nuevos.</b> En el reservado la ventaja no se ` +
  `reprodujo, y Kaggle da una sola cifra por envío. Por qué «Imagen + básicos» da más en el reservado que en el desarrollo no ` +
  `está medido. Se midió su curva de aprendizaje en el desarrollo, pero no la de la red, así que no se sabe si uno de los dos ` +
  `mejora más que el otro con más datos.`,
  `<b>Nada sobre otras redes de imagen.</b> Solo se probaron las variables de DINOv2 sin reentrenarlo y una red pequeña, ` +
  `EfficientNet-B0, entrenada sobre los recortes con tres recetas: la de la Fase 4c, con ajustes fijos; la de la 4d, con más ` +
  `épocas y los negativos en bloques; y la del 10.º puesto, con un ajuste fino por la pAUC, en la 4e. Las redes del ganador quedaron fuera.`,
  `<b>Cuánto rinde un modelo con fotos de teléfono.</b> Todos los modelos de imagen, también la red de la Fase 4e, se midieron ` +
  `sobre los recortes estandarizados del sistema de fotografía corporal total, y en Kaggle, sobre los recortes de la prueba del ` +
  `reto. El artículo del conjunto de datos advierte que las fotos que toman los pacientes ${citaIS("luz_y_campo")}.`,
  `<b>Cuánto cuesta predecir con la red de la Fase 4e o con C7 frente a los demás modelos.</b> Sus tiempos no se midieron con ` +
  `el procedimiento del proyecto, y la eficiencia es uno de los tres ejes de la pregunta del cliente. Solo hay la proyección del ` +
  `notebook de Kaggle, en otro equipo: ${horas("Red4e")} horas para la red y ${horas("C7")} para C7 por cada ${lesionesPrueba} ` +
  `lesiones, que no se compara con los tiempos de la sección 6.`,
  `<b>Que no exista una forma de mejorar a M3 limpio.</b> Ninguna de las siete versiones que se le compararon, de C1 a C7, en ` +
  `las fases 4b a 4e, llegó a su regla. Ninguna buscó hiperparámetros: sus ajustes se fijaron antes de correr, y la única ` +
  `elección hecha con resultados fue la de la exploración de la 4e, que decidió con la semilla 0 usar el ajuste fino. Las ` +
  `cuatro que apilan una red de imagen, de C4 a C7, quedaron por encima de él en la media, y la prueba no distingue mejoras de ` +
  `ese tamaño: no distinguirlas no es lo mismo que no tenerlas.`,
  `<b>Que promediar varios CatBoost, o usar la etiqueta del hospital, mejore el modelo.</b> Solo se midieron en Kaggle, con una ` +
  `cifra por envío. Promediar cambia dos cosas a la vez, y el mayor de los dos efectos del hospital cambia de signo entre la ` +
  `puntuación pública y la privada. En la validación cruzada no se probó promediar varios CatBoost de la misma especificación, ` +
  `ni la etiqueta del hospital con M3 limpio o con C7. Esa etiqueta, junto con la otra columna de procedencia, solo se probó con ` +
  `los modelos de referencia.`,
  `<b>Cuánto se separa de verdad este trabajo de la solución ganadora.</b> La distancia en Kaggle es una resta entre dos cifras ` +
  `sin intervalo, y su reparto entre promediar y el hospital depende del orden de los envíos. En el desarrollo, la evaluación ` +
  `usó otros datos y otras particiones que la del ganador.`,
  `<b>Nada clínico.</b> Los modelos ordenan lesiones por sospecha; no dicen qué tiene un paciente ni qué hacer con él. Son evidencia para una decisión humana.`];
// La primera frase de una viñeta que abre en negrita: la negrita entera si acaba
// en punto; si no, hasta el primer punto seguido de espacio que venga después.
const partir = b => {
  if (!b.startsWith("<b>")) return [b, ""];
  const fin = b.indexOf("</b>") + 4;
  if (b[fin - 5] === ".") return [b.slice(0, fin), b.slice(fin).trim()];
  const punto = b.indexOf(". ", fin);
  return punto < 0 ? [b, ""] : [b.slice(0, punto + 1), b.slice(punto + 2)];
};
// A la vista, cuatro viñetas en «Qué se puede» y cinco en «Qué no se puede»; las
// listas enteras van en el «Detalle». Qué se puede: las dos de M3 limpio frente a
// M2, la del contexto de paciente y la de la red frente a «Imagen + básicos», que
// respalda la segunda tarjeta. Qué no se puede: la primera frase de las que acotan
// cada recomendación —las métricas de triaje de M3 limpio, la red con pacientes
// nuevos y con fotos de teléfono—, la del uso clínico y, de quinta desde el paso 3
// del rediseño, la de que no exista una forma de mejorar a M3 limpio.
document.getElementById("se-puede").innerHTML = L([0, 1, 2, 5].map(i => SE_PUEDE[i]));
document.getElementById("no-se-puede").innerHTML = L([0, 2, 4, 9, 6].map(i => partir(NO_SE_PUEDE[i])[0]));
document.getElementById("det-7").innerHTML =
  P([`Lo que un consultor le entregaría al cliente: el hallazgo, la recomendación y lo que aún no se puede afirmar.`]) +
  resto7 + `<h3>Qué se puede afirmar</h3>` + L(SE_PUEDE) + `<h3>Qué no se puede afirmar</h3>` + L(NO_SE_PUEDE);

/* ---------- 8. limitaciones ---------- */
// borrador-v2.md, «Datos y validación», «Los datos» (la frase del archivo de prueba), y «Limitaciones».
document.getElementById("frase-8").innerHTML =
  `El archivo de prueba que publica el reto es un marcador de posición, sin casos reales.`;
const restoPrueba = P([`La prueba oculta solo se puede ` +
  `medir enviando modelos a Kaggle, que da una cifra por envío, sin intervalo; el resultado final con intervalo es el del ` +
  `conjunto que este proyecto apartó.`]);
const LIMITACIONES = [
  `<b>La clase negativa no está confirmada.</b> Las lesiones malignas tienen patología; de las benignas, <i>"most never underwent a skin biopsy"</i>. ` +
  `La mayoría de los negativos son lesiones que un dermatólogo no consideró preocupantes, no lesiones confirmadas como sanas.`,
  `<b>Las imágenes tienen una resolución óptica comparable a la de un teléfono inteligente.</b> Así las describe el artículo del conjunto de datos: ` +
  `<i>"comparable in optical resolution to smartphone images"</i>. El resultado de la imagen se limita a estas imágenes y a estos dos ` +
  `modelos de imagen: DINOv2 congelado y EfficientNet-B0 entrenada.`,
  `<b>Muchas comparaciones a la vez.</b> Cada comparación (M2 − M1, M4 − M2, M4b − M2, M3 − M2, M3 limpio − M2, 2b − 1 en las dos particiones, ` +
  `Imagen − M1, (Imagen + básicos) − Imagen, las tres de la Fase 4b contra M3 limpio, red sola − Imagen y C4 − M3 limpio) se lee en ` +
  `cuatro métricas, y las dos de las columnas de procedencia —con y sin ellas, en el boosting y en la logística—, solo en la pAUC. ` +
  `Las de las fases 4b y 4c se corrigen por multiplicidad dentro de cada fase, con Bonferroni; las demás no, y el intervalo del ` +
  `NNT80% SE de M2 − M1 queda al límite del cero.`,
  `<b>Cada ronda se eligió viendo las anteriores.</b> La bitácora del proyecto registra todas las comparaciones por la pAUC ` +
  `desde la Fase 4. Las fases 4d y 4e se corrigen con Holm dentro de cada una, y la 4f es una sola pregunta, sin corrección; ` +
  `ninguna corrección cubre varias rondas a la vez. La pregunta de la 4f se eligió con la diferencia de medias ya calculable ` +
  `desde outputs/, y en la 4e la exploración y la confirmación usan semillas que reparten a los mismos pacientes.`,
  `<b>La prueba no distingue mejoras pequeñas frente a M3 limpio.</b> Con la variabilidad observada, para dar su resultado a ` +
  `favor con un ${pctObj("delta_80")} de probabilidad necesita una mejora real de entre ${cifra(dec(POT.d80[0]), fPot("comparaciones.*.delta_80"))} ` +
  `y ${cifra(dec(POT.d80[1]), fPot("comparaciones.*.delta_80"))} de pAUC, y más semillas casi no bajan ese umbral. El cálculo hereda la ` +
  `aproximación de la propia prueba y toma la dispersión observada como la verdadera.`,
  `<b>La corrección de la varianza es aproximada.</b> Nadeau y Bengio la derivan para divisiones aleatorias independientes, y aquí se aplica a una validación por pliegues.`,
  `<b>El NNT80% SE se calcula con una lectura propia</b>, porque el organizador no publica script para él.`,
  `<b>El conjunto reservado no es del todo independiente.</b> No es ajeno a las decisiones tomadas antes de sellarlo, al diseño ` +
  `de las variables de la solución ganadora, que siguen M2 y M3 limpio, ni a la receta de la red de la Fase 4e, que su autor ` +
  `fijó sobre todo el conjunto de entrenamiento del reto. Tiene ${cifra(RES.malignas, fRes("datos.evaluacion.malignas"))} lesiones ` +
  `malignas, en ${cifra(RES.pacientes_con_malignas, fRes("datos.evaluacion.pacientes_con_malignas"))} pacientes. Y después de su ` +
  `única evaluación dejó de estar reservado: los modelos de Kaggle se entrenaron también con él.`,
  `<b>Kaggle da una sola cifra por envío.</b> Sin intervalo, no se puede decir qué diferencias entre los ocho envíos son ruido. ` +
  `Los cuatro de la Fase 5c se decidieron después de ver los de la 5b: son una segunda mirada al mismo conjunto de prueba. Y que ` +
  `la puntuación privada de los envíos tardíos salga del mismo subconjunto que el tablero final es lectura nuestra; ninguna ` +
  `fuente versionada lo dice.`,
  `<b>Los tiempos son de un solo equipo</b>, con DINOv2 en la GPU y los modelos tabulares en la CPU. Solo comparan estos modelos entre sí.`,
  `<b>Dos supuestos sin verificar.</b> No se sabe si el clasificador de nevus que produce <code>tbp_lv_nevi_confidence</code> se entrenó con lesiones ` +
  `de este conjunto. Y nada comprueba la versión del código de DINOv2; solo sus pesos, por hash.`,
  `<b>Un mecanismo medido a medias.</b> Se midió cómo falla el gradient boosting sin balancear: hunde a una parte de los ` +
  `positivos al fondo del ordenamiento. Por qué lo hace no se midió.`,
  `<b>La prueba de la partición cubre dos modelos.</b> Que partir por filas no cambie el veredicto se midió con la logística ` +
  `y el boosting balanceados, no con los modelos que usan el contexto de paciente.`];
// Una línea por limitación: su primera frase. La lista entera va en el «Detalle».
document.getElementById("limitaciones").innerHTML = L(LIMITACIONES.map(b => partir(b)[0]));
document.getElementById("det-8").innerHTML = restoPrueba + L(LIMITACIONES);

/* ---------- pie ---------- */
// Parte B, B10, con el texto de la persona del 2026-10-04.
document.getElementById("pie").innerHTML =
  `Generado el ${esc(D.generado)} por <code>generar_demo.py</code> desde <code>outputs/*.json</code>. ` +
  `Ninguna cifra de esta página está escrita a mano: pasa el ratón sobre cualquiera para ver su origen, ` +
  `el archivo y el campo de outputs/ o el archivo y la línea de la fuente.`;
</script>
</body>
</html>
"""


# Aviso de cifras exploratorias. Desde la Fase 1 (2026-09-25) cada instrumento
# declara en su JSON sobre qué datos midió (campo "datos"). Si alguno de los
# que lee la demo no declara el conjunto de desarrollo, sus cifras son las de
# la corrida exploratoria sobre el 100 % de los datos, y la página lo dice
# arriba. Se decide con los datos de entrada, no con una bandera: así el aviso
# no puede quedarse puesto en una demo regenerada con las cifras nuevas, ni
# faltar en una hecha con las viejas. Va en el HTML servido, no en el script
# de la página, para que se vea aunque el JavaScript falle.
AVISO_EXPLORATORIO = (
    '<div class="exploratorio" role="note"><b>Cifras exploratorias.</b> '
    "Las cifras de esta p&aacute;gina son de la corrida exploratoria sobre el 100&nbsp;% "
    "de los datos y se est&aacute;n re-midiendo sobre el conjunto de desarrollo.</div>"
)

# Nombre, sin extensión, de la salida de la Fase 5 en outputs/: la que escribió
# el guion que abrió el reservado, una sola vez (PLAN.md, Fase 5). Ningún otro
# archivo que lea la página puede declarar el reservado. *Hasta el 2026-11-06
# valía None: el reservado no se había abierto.* La salida no declara
# datos.conjunto: declara datos.entrenamiento y datos.evaluacion, y cuenta como
# válida si entrena con el desarrollo y evalúa los pacientes de
# holdout-pacientes.json.
SALIDA_FASE_5 = "fase5-reservado"


def es_salida_fase_5(contenido):
    d = contenido.get("datos") or {}
    if d.get("conjunto") == "reservado":
        return True
    return ((d.get("entrenamiento") or {}).get("conjunto") == "desarrollo"
            and "holdout-pacientes" in str((d.get("evaluacion") or {}).get("que_es", "")))


# Archivos que no miden sobre un conjunto sino que resumen otros. Cuentan como
# no exploratorios solo si cada archivo del que salen está entre los leídos y
# declara el conjunto de desarrollo.
# - fase4d-holm y fase4e-holm: la decisión de Holm sobre las preguntas de cada
#   fase (preguntas[*].archivo).
# - potencia-nadeau-bengio: la potencia de la prueba con las comparaciones de C4
#   a C7 contra M3 limpio (comparaciones.*.archivo).
DERIVADOS = {
    "fase4d-holm": lambda c: [p["archivo"] for p in c.get("preguntas", [])],
    "fase4e-holm": lambda c: [p["archivo"] for p in c.get("preguntas", [])],
    "potencia-nadeau-bengio": lambda c: [v["archivo"] for v in (c.get("comparaciones") or {}).values()],
}

# Archivos posteriores a la apertura del reservado, que tampoco miden sobre el
# desarrollo. Cuentan como no exploratorios solo si declaran lo que los hace
# válidos:
# - fase5-posterior: el análisis posterior a la apertura, con sus controles bien.
# - fase5b-comparacion y fase5c-efectos: comparaciones con las puntuaciones de
#   Kaggle, cada una leída de un registro de envío, con sus controles bien.
# - fase5b-kaggle-medicion: la corrida del notebook de medición en Kaggle,
#   privado y sin internet, con el control bien.
POSTERIORES = {
    "fase5-posterior": lambda c: "posterior a la apertura" in str(c.get("que_es", ""))
    and (c.get("controles") or {}).get("fallos") == 0,
    "fase5b-comparacion": lambda c: bool(c.get("kaggle")) and all(
        str(v.get("fuente", "")).startswith("outputs/fase5b-envio-") for v in c["kaggle"].values())
    and (c.get("controles") or {}).get("fallos") == 0,
    "fase5c-efectos": lambda c: bool(c.get("kaggle")) and all(
        str(v.get("fuente", "")).startswith(("outputs/fase5b-envio-", "outputs/fase5c-envio-")) for v in c["kaggle"].values())
    and (c.get("controles") or {}).get("fallos") == 0,
    "fase5b-kaggle-medicion": lambda c: (c.get("kernel") or {}).get("privado") is True
    and (c.get("kernel") or {}).get("internet") is False
    and ((c.get("salida_del_notebook") or {}).get("control") or {}).get("fallos") == 0,
}

# Archivos que no miden sobre un conjunto sino que reparten entre los dos, y
# por eso no declaran datos.conjunto. Cuentan como no exploratorios solo si
# declaran lo que los hace válidos:
# - extraccion-imagen: datos.reparto. No lee etiquetas (su campo nota), así
#   que extraer el reservado no es mirarlo. Decisión de la persona, 2026-10-02.
# - holdout-pacientes: fecha_sellado. Es el registro del sellado de la Fase 1;
#   la página lee solo su semilla y su fracción, nunca sus recuentos.
REPARTOS = {
    "extraccion-imagen": lambda c: bool((c.get("datos") or {}).get("reparto")),
    "holdout-pacientes": lambda c: bool(c.get("fecha_sellado")),
}


def comprobar_conjuntos(leidos, salida_fase_5=SALIDA_FASE_5):
    """Devuelve el aviso exploratorio, o "" si no hace falta, mirando cada
    archivo que la página leyó. El reservado solo se acepta en la salida de la
    Fase 5: en cualquier otro archivo no se escribe la página, porque el aviso
    diría «corrida exploratoria» de unas cifras que no lo son.
    sintesis-verificacion no declara conjunto; se comprueba aparte."""
    exploratorio = False
    for nombre, contenido in leidos.items():
        if nombre == "sintesis-verificacion":
            continue
        if nombre in REPARTOS:
            exploratorio = exploratorio or not REPARTOS[nombre](contenido)
            continue
        if nombre in POSTERIORES:
            exploratorio = exploratorio or not POSTERIORES[nombre](contenido)
            continue
        if nombre in DERIVADOS:
            fuentes = [os.path.splitext(os.path.basename(a))[0] for a in DERIVADOS[nombre](contenido)]
            exploratorio = exploratorio or not fuentes or not all(
                f in leidos and (leidos[f].get("datos") or {}).get("conjunto") == "desarrollo" for f in fuentes)
            continue
        if nombre == salida_fase_5 and es_salida_fase_5(contenido):
            continue
        conjunto = (contenido.get("datos") or {}).get("conjunto")
        if conjunto == "reservado":
            if nombre != salida_fase_5:
                raise SystemExit(
                    f"outputs/{nombre}.json declara el conjunto reservado y no es la salida "
                    "de la Fase 5. No se escribe la página."
                )
        elif conjunto != "desarrollo":
            exploratorio = True
    return AVISO_EXPLORATORIO if exploratorio else ""


# La verificación que la página muestra tiene que ser la del borrador vigente,
# hecha con el verificador de hoy. Se comprueba recalculándola, porque su JSON
# no dice sobre qué borrador se corrió. Comparar resultado contra resultado
# detecta además una verificación que se quedó atrás de outputs/: la cuarta
# fila del registro de incidentes de CLAUDE.md fue exactamente eso.
BORRADOR_VIGENTE = "informe/borrador-v2.md"


def comprobar_verificacion(outputs_dir):
    with tempfile.TemporaryDirectory() as tmp:
        recalculada = os.path.join(tmp, "sintesis-verificacion")
        r = subprocess.run(
            [sys.executable, VERIFICADOR, "--borrador", BORRADOR_VIGENTE,
             "--outputs-dir", os.path.abspath(outputs_dir), "--out", recalculada],
            cwd=RAIZ, capture_output=True, text=True,
        )
        # Desde la verificación por campo, el verificador se detiene si un
        # comentario F: no entra en la gramática; una ruta citada que no existe
        # es una cita rota. Entonces no se escribe la página, con su motivo.
        if r.returncode != 0:
            motivo = (r.stderr.strip().splitlines() or ["sin mensaje"])[-1]
            raise SystemExit(f"El verificador se detuvo: {motivo} No se escribe la página.")
        esperado_json = json.loads(leer(f"{recalculada}.json"))
        esperado_md = leer(f"{recalculada}.md")
    actual_json = json.loads(leer(os.path.join(outputs_dir, "sintesis-verificacion.json")))
    actual_md = leer(os.path.join(outputs_dir, "sintesis-verificacion.md"))
    if actual_json == esperado_json and actual_md == esperado_md:
        return
    motivos = []
    cabecera_actual = actual_md.split("\n", 1)[0]
    if cabecera_actual != esperado_md.split("\n", 1)[0]:
        motivos.append(f"se corrió sobre otro borrador («{cabecera_actual}»)")
    if (actual_json.get("modo_tolerancia"), actual_json.get("tolerancia_redondeo")) != (
            esperado_json["modo_tolerancia"], esperado_json["tolerancia_redondeo"]):
        motivos.append(f"modo de tolerancia {actual_json.get('modo_tolerancia')!r} con margen "
                       f"{actual_json.get('tolerancia_redondeo')!r}, no {esperado_json['modo_tolerancia']!r}")
    if not motivos:
        motivos.append("no coincide con recalcularla sobre el outputs/ actual")
    raise SystemExit(
        f"outputs/sintesis-verificacion no corresponde a {BORRADOR_VIGENTE} con el verificador "
        f"actual: {'; '.join(motivos)}. Hay que regenerarla. No se escribe la página."
    )


# El modelo recomendado no está en ningún campo de outputs/: es la decisión de
# la persona del 2026-09-26 (PLAN.md, Fase 4, «Modelo recomendado: decisión de
# la persona, 2026-09-26»). El generador no lo da por supuesto: aplica la regla
# fijada antes de correr sobre la salida de M3 limpio − M2 y no escribe la
# página si el resultado no coincide con esta constante. La página muestra el
# modelo recomendado desde esta constante, no desde texto tecleado.
RECOMENDADO = "M3 limpio"


def regla_de_recomendacion(f3l):
    """PLAN.md, Fase 4, «Regla de recomendación»: M3 limpio si el intervalo
    corregido de la pAUC de M3 limpio − M2 queda entero por encima de cero; en
    cualquier otro caso, M2."""
    if (f3l["comparacion"]["nuevo"], f3l["comparacion"]["base"]) != ("M3limpio", "M2"):
        raise SystemExit(f"fase4-m3limpio-vs-m2.json compara {f3l['comparacion']}, no M3 limpio − M2.")
    bajo, _ = f3l["comparaciones_nuevo_menos_base"]["pauc"]["intervalo_t_95_nadeau_bengio"]
    return "M3 limpio" if bajo > 0 else "M2"


def comprobar_recomendacion(f3l):
    regla = regla_de_recomendacion(f3l)
    if regla != RECOMENDADO:
        raise SystemExit(
            f"La regla de recomendación da {regla} y RECOMENDADO dice {RECOMENDADO}. "
            "No se escribe la página."
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument(
        "--salida",
        required=True,
        nargs="+",
        help="Una o más rutas de destino. El HTML se renderiza UNA vez y esa "
        "misma cadena se escribe en todas: informe/demo.html para abrir por "
        "doble clic y docs/index.html para GitHub Pages.",
    )
    args = ap.parse_args()

    # Las comprobaciones van antes de renderizar: si una se niega, no se
    # escribe ningún destino, ni siquiera a medias. La recomendación se
    # comprueba antes de construir los datos, que la muestran.
    leidos = {}
    comprobar_recomendacion(cargar_json(args.outputs_dir, "fase4-m3limpio-vs-m2", leidos))
    datos = construir_datos(args.outputs_dir, leidos)
    comprobar_verificacion(args.outputs_dir)
    aviso = comprobar_conjuntos(leidos)
    # </script> dentro de la cadena JSON cerraria la etiqueta que la contiene;
    # \/ es escape válido en JSON, así que el dato llega intacto al parser.
    crudo = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")

    # Chart.js se empotra desde disco en vez de cargarse por CDN. Antes iba en
    # un <script src> a jsdelivr, y sin red la pagina lanzaba
    # "Chart is not defined", lo que ABORTA el script y deja sin rellenar todo
    # lo que viene despues: los pAUC y las fichas por skill desaparecian
    # mientras la cabecera seguia a la vista. Fallo silencioso en mitad de una
    # presentacion. Procedencia y hash en assets/PROCEDENCIA.md.
    #
    # La ruta se resuelve contra __file__, no contra el directorio de trabajo,
    # para que el script funcione invocado desde cualquier sitio.
    chartjs_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "assets",
        "chart.umd.min.js",
    )
    with open(chartjs_path, encoding="utf-8") as f:
        chartjs = f.read()

    # Verificado al empotrarla: la libreria no contiene "</script". Si una
    # version futura lo hiciera, cerraria la etiqueta antes de tiempo y
    # romperia la pagina sin ruido, asi que se comprueba en vez de confiar.
    if "</script" in chartjs.lower():
        raise SystemExit(
            f"{chartjs_path} contiene '</script': empotrarla cerraria la "
            "etiqueta antes de tiempo. Hay que escaparla antes de seguir."
        )

    # Se renderiza una sola vez, fuera del bucle, y se escribe la misma cadena
    # en cada destino. No es una optimización: el payload lleva una marca de
    # tiempo (datos["generado"]), así que dos renderizados podrían diferir en
    # ese campo y las copias dejarían de ser idénticas. Renderizar aquí hace
    # que la igualdad sea estructural en vez de algo que haya que comprobar.
    html = (
        PLANTILLA.replace("__CHARTJS__", chartjs)
        .replace("__AVISO_EXPLORATORIO__", aviso)
        .replace("__DATOS__", crudo)
    )

    for salida in args.salida:
        os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
        with open(salida, "w", encoding="utf-8") as f:
            f.write(html)

    print(
        f"Escrito: {', '.join(args.salida)} — {len(datos['cadena'])} etapas en la cadena, "
        f"{len(datos['comparaciones'])} comparaciones, {len(datos['tabla'])} modelos en la tabla"
    )


if __name__ == "__main__":
    main()

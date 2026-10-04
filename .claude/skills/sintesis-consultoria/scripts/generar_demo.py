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
CADENA = [
    {
        "nombre": "eda-diagnostico",
        "etapa": "Diagnóstico del dataset",
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
        "tipo": "medición",
        "funcion": "Se entrenaron y evaluaron los niveles de referencia y los modelos M1 a M4b "
                   "sobre pliegues agrupados por paciente",
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


def datos_imagen_sola(imagen_sola, escala, modelado, fase4, extraccion):
    """Cifras de «La imagen sola, sin el sistema de fotografía corporal total» y
    las frases que dependen de ellas. Control positivo: test_generar_demo.py,
    caso L, con un imagen-sola.json que rompe cada frase."""
    m, c = imagen_sola["metricas"], imagen_sola["comparaciones_nuevo_menos_base"]
    clave_ic = "intervalo_t_95_nadeau_bengio"
    ctrl = imagen_sola["control_m1_contra_referencia"]
    afirmar(ctrl["m1_reproduce_fold_a_fold"] and ctrl["huellas_de_pliegues_iguales"], "en los mismos pliegues de M1")
    m3_brutas = fase4["fase4-m3-vs-m2"]["m3"]["variables"]["entran"]["numericas_brutas"]
    afirmar(all(any(v.startswith("tbp_lv_") for v in lista) for lista in
                (modelado["features_usadas"], fase4["fase4-m2-vs-m1"]["variables_de_contexto"], m3_brutas)),
            "Las mediciones de las que dependen M1, M2 y M3 limpio las calcula el software de la fotografía corporal total")
    pliegues = [v for s in imagen_sola["esquema"]["semillas"] for v in m["Imagen"]["pauc"]["por_semilla_y_fold"][str(s)]]
    afirmar(all(v > escala["azar"] for v in pliegues), "La imagen sola distingue lesiones malignas muy por encima del azar")
    im1 = c["imagen_menos_m1"]
    for k, frase in (("pauc", "la pAUC"), ("auc", "el AUC"), ("setop15", "la sensibilidad top-15")):
        afirmar(im1[k]["media"] < 0 and im1[k][clave_ic][1] < 0,
                f"queda por debajo de M1 en las cuatro métricas, y las cuatro diferencias están establecidas ({frase})")
    afirmar(im1["nnt80"]["media"] > 0 and im1["nnt80"][clave_ic][0] > 0,
            "queda por debajo de M1 en las cuatro métricas, y las cuatro diferencias están establecidas (el NNT80% SE)")
    ib = c["imagen_basicos_menos_imagen"]
    afirmar(ib["auc"]["media"] > 0 and ib["auc"][clave_ic][0] > 0,
            "Añadir edad, sexo y zona del cuerpo mejora el AUC de forma distinguible")
    afirmar(contiene_cero(ib["pauc"][clave_ic]), "En la pAUC, con la precisión guardada, el intervalo no excluye el cero")
    afirmar(contiene_cero(ib["setop15"][clave_ic]) and contiene_cero(ib["nnt80"][clave_ic]),
            "en la sensibilidad top-15 y en el NNT80% SE, el intervalo contiene el cero")
    citas = {}
    for clave, (ruta, texto) in CITAS_IMAGEN_SOLA.items():
        if texto not in leer(os.path.join(RAIZ, ruta)):
            raise SystemExit(f"La cita «{texto}» no está en {ruta}. No se escribe la página.")
        citas[clave] = texto
    return {
        "n_variables": int(extraer(r"(\d+) dimensiones", extraccion["caracteristica"],
                                   "las dimensiones de la característica").group(1)),
        "medias": {mod: {k: m[mod][k]["media_global"] for k in METRICAS} for mod in ("M1", "Imagen", "Imagen + básicos")},
        "comp": {n: {k: {"media": c[n][k]["media"], "ic": c[n][k][clave_ic]} for k in METRICAS}
                 for n in ("imagen_menos_m1", "imagen_basicos_menos_imagen")},
        "clave_ic": clave_ic,
        "auc_recortes": auc_solo_recortes(),
        "citas": citas,
    }


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
        "otras": {k: {"media": cp[k]["media"], "ic": cp[k][clave_ic]} for k in ("auc", "setop15", "nnt80")},
        "ic_paciente": cp["pauc"][clave_ic],
        "ic_filas": cf["pauc"][clave_ic],
        "semillas": len(particion["esquema"]["semillas"]),
        "filas_menos_paciente": {
            corto: {m: {"dif": fmp[n][m]["diferencia_de_medias"], "mejor": fmp[n][m]["semillas_filas_mejor"]}
                    for m in ("pauc", "auc", "nnt80")}
            for corto, n in (("n1", n1), ("n2b", n2b))
        },
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
    afirmar(any(re.fullmatch(r"(19|20)\d\d", s["valor"].rstrip(".,"))
                and f"({s['valor'].rstrip('.,')})" in s["contexto"]
                for s in verificacion["numeros_sin_respaldo"]),
            "un número señalado puede ser legítimo, como el año de una fuente")
    fase4 = {archivo: cargar(archivo) for _, archivo in COMPARACIONES}
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
    afirmar(min(T["M4"]["tiempo"], T["M4b"]["tiempo"]) > max(T[x]["tiempo"] for x in ("M1", "M2", "M3 limpio")),
            "Lo caro, con diferencia, es la imagen")
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
        "tabla": tabla,
        "mecanismo": datos_mecanismo(mecanismo, metrica),
        "particion": datos_particion(particion),
        "imagen_sola": datos_imagen_sola(imagen_sola, escala, modelado, fase4, extraccion),
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
  h1 { font-size: 30px; margin: 10px 0 16px; line-height: 1.25; }
  .contexto { margin: 0 0 22px; max-width: 860px; }
  .contexto p { margin: 0 0 12px; font-size: 15.5px; }
  .contexto b { color: var(--acento); }
  section { margin-top: 52px; }
  h2 { font-size: 21px; margin: 0 0 6px; display: flex; align-items: center; }
  h2 .num {
    flex: 0 0 30px; width: 30px; height: 30px; line-height: 30px;
    text-align: center; background: var(--tinta); color: #fff;
    border-radius: 50%; font-size: 14px; margin-right: 10px;
  }
  h3 { font-size: 16px; margin: 22px 0 8px; }
  .sub { color: var(--suave); margin: 0 0 20px; font-size: 15px; }
  .tarjeta {
    background: #fff; border: 1px solid var(--linea); border-radius: 10px;
    padding: 22px; box-shadow: 0 1px 2px rgba(22,32,43,.05);
  }
  .texto p { margin: 0 0 12px; font-size: 15px; }
  .texto ul { margin: 0 0 12px; padding-left: 20px; font-size: 15px; }
  .texto li { margin-bottom: 8px; }
  .cadena { display: flex; align-items: stretch; gap: 4px; flex-wrap: wrap; }
  .paso {
    flex: 1 1 120px; text-align: left; cursor: pointer; background: #fff;
    border: 1px solid var(--linea); border-top: 4px solid var(--suave);
    border-radius: 8px; padding: 13px 14px; font: inherit; color: inherit;
    transition: transform .12s, box-shadow .12s, border-color .12s;
    display: flex; flex-direction: column;
  }
  .paso:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(22,32,43,.12); }
  .paso[aria-selected="true"] { border-color: var(--acento); border-top-color: var(--acento); background: #eef5fa; }
  .paso.final { border-top-color: var(--acento); }
  .paso .nom { font-weight: 700; font-size: 14px; display: block; }
  .paso .tipo {
    font-size: 10px; text-transform: uppercase; letter-spacing: .1em;
    color: var(--suave); font-weight: 600; white-space: nowrap;
  }
  .paso.final .tipo { color: var(--acento); }
  .paso .fun { font-size: 12px; color: var(--suave); margin-top: 6px; display: block; }
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
  .panel h3 { margin: 0 0 6px; font-size: 14px; }
  .panel .lienzo { height: 230px; }
  .pie-grafico { font-size: 13px; color: var(--suave); margin-top: 14px; }
  .cifra-fuente { border-bottom: 1px dotted var(--suave); cursor: help; }
  footer {
    margin-top: 64px; padding-top: 20px; border-top: 1px solid var(--linea);
    font-size: 12.5px; color: var(--suave);
  }
  @media (max-width: 760px) {
    .hoja { padding: 0 16px 56px; }
    h1 { font-size: 25px; }
    .duo, .paneles { grid-template-columns: 1fr; }
    .flecha { display: none; }
    .tarjeta { padding: 16px; }
    .medida .cifra { font-size: 44px; }
    .lienzo { height: 300px; }
    /* La tabla de tres ejes cabe entera: el costo no queda fuera de la vista. */
    table { font-size: 12.5px; }
    th, td { padding: 6px 4px; }
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
  <div class="contexto">
    <p><b>El problema.</b> <span id="ctx-problema"></span></p>
    <p><b>Los datos.</b> <span id="ctx-datos"></span></p>
    <p id="ctx-metrica"></p>
    <p><b>Por qu&eacute; este caso.</b> <span id="ctx-eleccion"></span></p>
  </div>
</header>

<section>
  <h2><span class="num">1</span>C&oacute;mo se desarroll&oacute; el trabajo</h2>
  <p class="sub">Seis etapas. Las cinco primeras miden y dejan su salida en un archivo; la sexta interpreta y redacta. Haz clic en cualquiera para ver la salida real que produjo.</p>
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
</section>

<section>
  <h2><span class="num">2</span>Una decisi&oacute;n por defecto cambia el veredicto</h2>
  <p class="sub" id="sub-resultados"></p>
  <div class="duo">
    <div class="medida mal">
      <div class="cifra" id="tit-2a"></div>
      <div class="rot" id="rot-2a"></div>
    </div>
    <div class="medida ok">
      <div class="cifra" id="tit-2b"></div>
      <div class="rot" id="rot-2b"></div>
    </div>
  </div>
  <div class="tarjeta">
    <div class="texto" id="texto-2"></div>
    <div class="lienzo"><canvas id="gr-niveles"></canvas></div>
    <p class="pie-grafico">Los bigotes marcan una desviaci&oacute;n est&aacute;ndar entre pliegues, no un intervalo de confianza.</p>
  </div>
</section>

<section>
  <h2><span class="num">3</span>Una ventaja que la pAUC no ve</h2>
  <div class="tarjeta">
    <div class="texto" id="texto-3"></div>
    <div class="lienzo"><canvas id="gr-pareada"></canvas></div>
    <h3>Las columnas de procedencia no explican la ventaja</h3>
    <div class="texto" id="texto-3b"></div>
    <h3>Partir por filas no cambia el veredicto</h3>
    <div class="texto" id="texto-3c"></div>
  </div>
</section>

<section>
  <h2><span class="num">4</span>La m&eacute;trica principal no agota lo que pidi&oacute; el cliente</h2>
  <div class="tarjeta">
    <div class="texto" id="texto-4"></div>
    <div class="paneles" id="paneles"></div>
    <p class="pie-grafico" id="pie-paneles"></p>
    <div class="texto" id="lectura-4"></div>
    <h3>La imagen sola, sin el sistema de fotograf&iacute;a corporal total</h3>
    <div class="texto" id="texto-4b"></div>
  </div>
</section>

<section>
  <h2><span class="num">5</span>La pregunta del cliente, entera</h2>
  <div class="tarjeta">
    <div class="tabla-envoltura"><table id="tabla-ejes"></table></div>
    <div class="texto" id="texto-5" style="margin-top:16px"></div>
  </div>
</section>

<section>
  <h2><span class="num">6</span>Recomendaci&oacute;n</h2>
  <p class="sub">Lo que un consultor le entregar&iacute;a al cliente: el hallazgo, la recomendaci&oacute;n y lo que a&uacute;n no se puede afirmar.</p>
  <div class="medida ok sola">
    <div class="cifra" id="tit-reco"></div>
    <div class="rot" id="rot-reco"></div>
    <div class="det">El modelo recomendado &middot; pAUC</div>
  </div>
  <div class="tarjeta">
    <div class="texto" id="texto-6"></div>
    <h3>Qu&eacute; se puede afirmar</h3>
    <div class="texto" id="se-puede"></div>
    <h3>Qu&eacute; no se puede afirmar</h3>
    <div class="texto" id="no-se-puede"></div>
  </div>
</section>

<section>
  <h2><span class="num">7</span>Limitaciones</h2>
  <div class="tarjeta"><div class="texto" id="limitaciones"></div></div>
</section>

<section>
  <h2><span class="num">8</span>Lo que sigue</h2>
  <p class="sub">Trabajo previsto, no ejecutado. Sin cifras: el conjunto reservado no se ha abierto.</p>
  <div class="tarjeta">
    <div class="texto"><p>Abrir el conjunto reservado, una sola vez. M3 limpio se entrena una sola vez con los pacientes de desarrollo y se eval&uacute;a sobre los reservados, con punto e intervalo por bootstrap de pacientes; M2 se punt&uacute;a en la misma corrida, como referencia. Todo se fij&oacute; antes de abrirlo, y despu&eacute;s no se cambia nada: ni el modelo, ni las caracter&iacute;sticas, ni el criterio. El resultado se reporta sea cual sea, y la recomendaci&oacute;n no cambia por &eacute;l.</p></div>
    <p class="aviso">Ninguna cifra aparece en esta secci&oacute;n porque ninguna est&aacute; medida.
    A diferencia del resto de la p&aacute;gina, aqu&iacute; no hay archivo en <code>outputs/</code> que
    respalde nada &mdash; y por eso no se afirma nada.</p>
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
// huecos-demo.md, Parte B, B2; borrador-v2.md, «Limitaciones», la viñeta de la resolución.
document.getElementById("ctx-problema").innerHTML =
  `El reto ISIC 2024 usa el conjunto SLICE-3D: recortes de lesiones de piel extraídos de fotografías corporales totales en 3D, para detectar cáncer de piel. ` +
  `La clase maligna está confirmada por patología: melanoma, carcinoma basocelular o carcinoma escamocelular. ` +
  `Las imágenes tienen una resolución óptica comparable a la de un teléfono inteligente. ` +
  `Así las describe el artículo del conjunto de datos: <i>"comparable in optical resolution to smartphone images"</i>.`;

// borrador-v2.md, «Datos y validación», «El conjunto de desarrollo» y «El conjunto reservado»; Parte B, B3.
document.getElementById("ctx-datos").innerHTML =
  `El conjunto de desarrollo tiene ${cifra(mil(E.n_filas), fEda("estructura_grupos.n_filas"))} lesiones de ` +
  `${cifra(mil(E.n_pacientes), fEda("estructura_grupos.n_grupos"))} pacientes. ` +
  `Solo ${cifra(mil(E.positivos), fEda("desbalance_target.conteos.1"))} lesiones son malignas, el ` +
  `${cifra(dec(E.pct_positivos) + "%", fEda("desbalance_target.pct_positivos"))}, y solo ` +
  `${cifra(mil(DI.n_grupos_positivos), fDis("n_grupos_positivos"))} pacientes tienen alguna. ` +
  `Cada paciente aporta entre ${cifra(mil(E.min), fEda("estructura_grupos.filas_por_grupo.min"))} y ` +
  `${cifra(mil(E.max), fEda("estructura_grupos.filas_por_grupo.max"))} lesiones, con una mediana de ` +
  `${cifra(mil(E.mediana), fEda("estructura_grupos.filas_por_grupo.mediana"))}. ` +
  `Antes de volver a medir nada, se apartó el ${cifra(D.sellado.pct + "%", "holdout-pacientes.json > metodo.fraccion")} de los pacientes ` +
  `—no de las filas—, estratificado por centro y por tener al menos una lesión maligna, con semilla ` +
  `${cifra(String(D.sellado.semilla), "holdout-pacientes.json > semilla")}, y se selló. ` +
  `El conjunto reservado tiene ${cifra(mil(R.pacientes), fExt("conjuntos.reservado.cobertura.pacientes"))} pacientes y ` +
  `${cifra(mil(R.imagenes), fExt("conjuntos.reservado.cobertura.imagenes"))} imágenes, y ningún modelo se ha evaluado sobre él.`;

// borrador-v2.md, «Método», «Qué se mide».
document.getElementById("ctx-metrica").innerHTML =
  `<b>La métrica principal es la del reto:</b> el área parcial bajo la curva ROC por encima del ` +
  `${cifra(D.metrica.tpr + "%", fMod("metrica"))} de sensibilidad, o pAUC, que va de ` +
  `${cifra(dec(D.metrica.rmin), fMod("metrica"))} a ${cifra(dec(D.metrica.rmax), fMod("metrica"))}. ` +
  `El organizador la justifica en términos clínicos, no estadísticos: <i>"there are regions in the ROC space where the values of TPR are unacceptable in clinical practice"</i>, ` +
  `y <i>"Systems that aid in diagnosing cancers are required to be highly-sensitive"</i>. ` +
  `Esa es la función de utilidad del cliente, escrita en su métrica: la región del espacio ROC donde la sensibilidad es clínicamente inaceptable no cuenta. ` +
  `Un clasificador al azar obtiene ${azar} y uno perfecto, ${cifra(dec(D.escala.maximo), fMod("escala_de_referencia_pauc.maximo"))}.`;

// Parte B, B4.
document.getElementById("ctx-eleccion").innerHTML =
  `Se eligió este caso y se descartaron dos de RSNA, de rodilla y de columna lumbar: son imágenes médicas en 3D, que exigen una GPU potente y aportan poco desde lo estadístico. ` +
  `En este, la metadata tabular hace gran parte del trabajo, y el desbalance y la agrupación por paciente son estadísticamente interesantes. ` +
  `La imagen entró después, como una extensión que profundiza la tesis sin reemplazarla.`;

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
  // borrador-v2.md, «Resultados», «Una decisión por defecto cambia el veredicto».
  "modelado-baseline": () => P([
    `El mismo gradient boosting da resultados opuestos según una sola opción. Sin balancear, su pAUC media es ${mediaN("Nivel 2a")}, ` +
    `por debajo del piso aleatorio de ${azar} en los ${cifra(VR.n_folds_2a, fVR("nivel_2a_gradient_boosting_sin_balancear.pauc_por_semilla_y_fold (todos)"))} pliegues. ` +
    `Con <code>class_weight="balanced"</code>, y nada más distinto, llega a ${mediaN("Nivel 2b")}.`]),
  // Parte B, B8, con el texto de la persona del 2026-10-04.
  "sintesis-consultoria": () => P([
    `El verificador encontró ${cifra(mil(V.total), fVer("numeros_en_borrador"))} números en el informe. ` +
    `${cifra(mil(V.comentarios), fVer("numeros_en_comentarios"))} están en los comentarios que dan la fuente de cada frase, ` +
    `y no se les busca respaldo; ` +
    `${cifra(V.omitidos, fVer("numeros_en_contextos_omitidos"))} se omiten por una lista declarada de contextos; ` +
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
  b.innerHTML = `<span class="tipo">${i + 1} &middot; ${esc(s.tipo)}</span>
                 <span class="nom">${esc(s.etapa)}</span>
                 <span class="fun">${esc(s.funcion)}</span>`;
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

/* ---------- 2. una decision por defecto ---------- */
// borrador-v2.md, «Resultados», párrafo inicial.
document.getElementById("sub-resultados").innerHTML =
  `Salvo donde se indica, las métricas de desempeño son del conjunto de desarrollo, con ${semillasVR} semillas y ` +
  `${cifra(VR.n_splits, fVR("n_splits"))} pliegues. Cada diferencia es «nuevo − base», y su intervalo es el corregido al ${nivelIC}. ` +
  `Los pliegues y semillas en que gana el nuevo se dan entre paréntesis.`;
document.getElementById("tit-2a").innerHTML = mediaN("Nivel 2a");
document.getElementById("rot-2a").textContent = "Nivel 2a — " + NIV["Nivel 2a"].descripcion;
document.getElementById("tit-2b").innerHTML = mediaN("Nivel 2b");
document.getElementById("rot-2b").textContent = "Nivel 2b — " + NIV["Nivel 2b"].descripcion;
// borrador-v2.md, «Resultados», «Una decisión por defecto cambia el veredicto».
document.getElementById("texto-2").innerHTML = HALLAZGOS["modelado-baseline"]() + P([
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
  afterDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(D.escala.azar), cx = ch.ctx;
    if (!isFinite(y)) return;
    const texto = "piso aleatorio " + dec(D.escala.azar);
    cx.save();
    cx.font = "600 11px -apple-system, sans-serif"; cx.textAlign = "right";
    const ancho = cx.measureText(texto).width;
    const x = ch.chartArea.right - 6;
    cx.fillStyle = "rgba(255,255,255,.85)";
    cx.fillRect(x - ancho - 4, y - 18, ancho + 8, 15);
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

/* ---------- 3. una ventaja que la pAUC no ve ---------- */
const PA = VR.pareada, EP = D.particion;
const fEP = c => "efecto-particion.json > particiones.paciente.comparacion_2b_menos_1." + c;
const fEPf = c => "efecto-particion.json > filas_menos_paciente." + c;
// borrador-v2.md, «Resultados», «Una ventaja que la pAUC no ve».
document.getElementById("texto-3").innerHTML = P([
  `El gradient boosting balanceado supera a la regresión logística balanceada por ` +
  `${cifra(dec(PA.media), fVR("comparacion_pareada_2b_menos_1.media"))} en promedio, con intervalo ` +
  `${ic(PA.ic[0], PA.ic[1], fVR("comparacion_pareada_2b_menos_1.intervalo_t_95_nadeau_bengio"))} ` +
  `(${cifra(PA.gana, fVR("comparacion_pareada_2b_menos_1.gana_2b_en"))} de ${cifra(PA.de, fVR("comparacion_pareada_2b_menos_1.de"))} pliegues; ` +
  `${cifra(PA.semillas, fVR("comparacion_pareada_2b_menos_1.semillas_a_favor_de_2b"))} de ${semillasVR} semillas). La ventaja no está establecida. ` +
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
document.getElementById("texto-3b").innerHTML = P([
  `Con las columnas de centro y licencia, la diferencia entre el boosting y la logística es ` +
  `${cifra(dec(PR.a_con), fPro("a_2b_menos_1_con_procedencia.media"))}; sin ellas, ${cifra(dec(PR.a_sin), fPro("a_2b_menos_1_sin_procedencia.media"))}. ` +
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
document.getElementById("texto-3c").innerHTML = P([
  `Se probaron las dos particiones con la logística y el gradient boosting balanceados, con una regla de lectura ` +
  `fijada antes de correr. La partición por filas infla una métrica si da mejor en las ${semEP} semillas, y cambia el ` +
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
document.getElementById("texto-4").innerHTML = P([
  `<b>El criterio:</b> una diferencia se da por establecida solo si su intervalo corregido al ${nivelIC} no contiene el cero. ` +
  `Junto al intervalo se reportan los pliegues y las semillas en que gana cada modelo.`]);
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
const paneles = document.getElementById("paneles");
["pauc", "auc", "setop15", "nnt80"].forEach(k => {
  const div = document.createElement("div");
  div.className = "panel";
  div.innerHTML = `<h3>${NOMBRES[k]}</h3><div class="lienzo"><canvas></canvas></div>`;
  paneles.appendChild(div);
  const filas = D.comparaciones.map(c => c.metricas[k]);
  const distinguible = filas.map(m => !(m.ic[0] <= 0 && 0 <= m.ic[1]));
  const d = k === "nnt80" ? 2 : undefined;
  new Chart(div.querySelector("canvas"), {
    type: "bar",
    plugins: [mediasYcero],
    data: {
      labels: D.comparaciones.map(c => c.etiqueta),
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
            afterLabel: it => `${D.comparaciones[it.dataIndex].archivo} > comparaciones_nuevo_menos_base.${k}`
          }
        }
      }
    }
  });
});
document.getElementById("pie-paneles").innerHTML = esc(D.nota_nnt);
// borrador-v2.md, «Resultados», «La métrica principal no agota lo que pidió el cliente»,
// «Añadida al modelo con contexto de paciente, la imagen no justifica su costo» y «El modelo recomendado».
document.getElementById("lectura-4").innerHTML = L([
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
document.getElementById("texto-4b").innerHTML = P([
  `Las mediciones de las que dependen M1, M2 y M3 limpio las calcula el software de la fotografía corporal total; ` +
  `sin ese sistema, esos modelos no se pueden aplicar tal cual. ` +
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
  `pAUC: ${mediaIS("imagen_menos_m1", "pauc")}, ${icIS("imagen_menos_m1", "pauc")};`,
  `AUC: ${mediaIS("imagen_menos_m1", "auc")}, ${icIS("imagen_menos_m1", "auc")};`,
  `sensibilidad top-15: ${mediaIS("imagen_menos_m1", "setop15")}, ${icIS("imagen_menos_m1", "setop15")};`,
  `NNT80% SE: ${mediaIS("imagen_menos_m1", "nnt80")} lesiones por cada maligna, ${icIS("imagen_menos_m1", "nnt80")}.`]) + P([
  `Para capturar el ${cifra(D.metrica.tpr + "%", fMod("metrica"))} de las malignas, la imagen sola marca ` +
  `${cifra(fijo(IS.medias.Imagen.nnt80, 2), fIS("metricas.Imagen.nnt80.media_global"))} lesiones por cada una, frente a ` +
  `${cifra(fijo(IS.medias.M1.nnt80, 2), fIS("metricas.M1.nnt80.media_global"))} de M1.`,
  `Añadir edad, sexo y zona del cuerpo mejora el AUC de forma distinguible: ` +
  `${mediaIS("imagen_basicos_menos_imagen", "auc")}, ${icIS("imagen_basicos_menos_imagen", "auc")}. ` +
  `En la pAUC, con la precisión guardada, el intervalo no excluye el cero, ${icIS("imagen_basicos_menos_imagen", "pauc")}, ` +
  `así que esa mejora no se da por establecida; en la sensibilidad top-15 y en el NNT80% SE, el intervalo contiene el cero.`,
  `<i>Interpretación, no medición:</i> sin el sistema de fotografía corporal total, la imagen sí sirve para ordenar lesiones ` +
  `por sospecha, pero con este extractor congelado rinde bastante menos que las mediciones. Edad, sexo y zona del cuerpo son ` +
  `datos que cualquiera puede dar sin aparatos. El ganador ajustó sus propias redes de imagen, y su variante con solo los ` +
  `recortes llega a un AUC de ${auc922}, pero en otros datos y con otra evaluación, así que las cifras no se comparan. ` +
  `Y todo esto se midió sobre los recortes del sistema de fotografía corporal total, no sobre fotos de teléfono.`]);

/* ---------- 5. la pregunta del cliente, entera ---------- */
// borrador-v2.md, «Resultados», «La pregunta del cliente, entera»: la cabecera y las filas, con las cifras de outputs/.
const fMet = (f, k) => `${f.archivo} > metricas.${f.clave}.${k}.media_global`;
document.getElementById("tabla-ejes").innerHTML =
  `<thead><tr><th>Modelo</th><th>pAUC</th><th>Sensibilidad top-15</th><th>NNT80% SE</th><th>Segundos por ${milLesiones} lesiones</th></tr></thead><tbody>` +
  D.tabla.map(f => `<tr><td>${esc(f.modelo)}</td><td>${cifra(fijo(f.pauc, 4), fMet(f, "pauc"))}</td>` +
    `<td>${cifra(fijo(f.setop15, 4), fMet(f, "setop15"))}</td><td>${cifra(fijo(f.nnt80, 2), fMet(f, "nnt80"))}</td>` +
    `<td>${tiempoT(f.modelo)}</td></tr>`).join("") + `</tbody>`;
// borrador-v2.md, «Resultados», «La pregunta del cliente, entera» y «El costo de inferencia».
document.getElementById("texto-5").innerHTML = P([
  `La tabla responde la pregunta con sus tres ejes —la métrica principal, la sensibilidad por paciente y el costo— y añade el NNT80% SE, la segunda métrica de triaje. ` +
  `Son medias y medianas; las diferencias, con sus intervalos, están arriba. M2 se distingue de M1 en las dos métricas de triaje, no en la pAUC. ` +
  `Frente a M2, de los otros tres solo M3 limpio se distingue, y solo en la pAUC y en el AUC estándar; en las métricas de triaje no se distingue ninguno de los tres.`,
  `M3 limpio cuesta más que M2, pero los dos quedan por debajo de una décima de segundo por cada ${milLesiones} lesiones. ` +
  `Lo caro, con diferencia, es la imagen, y los modelos con imagen no mejoraron la métrica principal de forma distinguible.`]);

/* ---------- 6. recomendacion ---------- */
document.getElementById("tit-reco").innerHTML = cifra(dec(D.recomendado_pauc), D.recomendado_fuente);
document.getElementById("rot-reco").innerHTML = reco;
// borrador-v2.md, «Recomendación», «Qué se recomienda».
document.getElementById("texto-6").innerHTML = P([
  `<b>Al cliente se le recomienda ${reco}:</b> la parte tabular reproducida de la solución ganadora, sin los dos sesgos conocidos a su favor. ` +
  `Se eligió con una regla fijada antes de correr la comparación: el intervalo corregido de su diferencia con M2 en la pAUC queda entero por encima de cero.`,
  `<b>Donde se toma la fotografía corporal total, no se recomienda añadir las variables de imagen</b> tal como se probaron. ` +
  `Añadidas al modelo con contexto de paciente no mejoraron ninguna métrica de forma distinguible, ` +
  `y al predecir cuestan ${tiempoT("M4")} y ${tiempoT("M4b")} segundos por cada ${milLesiones} lesiones, frente a ${tiempoT("M3 limpio")} de M3 limpio. ` +
  `Eso no dice que la imagen no sirva para detectar cáncer: en la ablación de los organizadores, la variante del modelo ganador ` +
  `que solo usa los recortes llega a un AUC de ${auc922}, y la presentan como una base sólida para cuando no se pueden recoger ` +
  `los metadatos, como al usar la cámara de un teléfono.`,
  `<b>Donde no hay ese sistema, M3 limpio no se puede aplicar tal cual, y la imagen es el insumo disponible.</b> ` +
  `Es el escenario que el artículo del conjunto de datos pone como objetivo: algoritmos que decidan a partir de ${citaIS("telefono")}. ` +
  `Ahí, el punto de partida es la imagen con edad, sexo y zona del cuerpo, que mejora el AUC de la imagen sola; antes de usarla ` +
  `habría que medirla con fotos de teléfono. Cómo mejorarla, por ejemplo ajustando redes propias, no se ha medido.`,
  `<b>Y se recomienda no leer solo la pAUC.</b> El contexto de paciente no se nota en ella y sí en las dos métricas de triaje: la sensibilidad top-15 y el NNT80% SE.`]);
// borrador-v2.md, «Recomendación», «Qué se puede afirmar».
document.getElementById("se-puede").innerHTML = L([
  `En el conjunto de desarrollo, con validación cruzada repetida y el intervalo corregido, M3 limpio supera a M2 en la pAUC y en el AUC estándar.`,
  `El contexto de paciente mejora frente a M1 la sensibilidad top-15 y el NNT80% SE.`,
  `Añadidas al modelo con contexto de paciente, las variables de imagen de DINOv2, como variables sueltas o apiladas, no mejoran de forma distinguible ninguna de las métricas.`,
  `Sin el sistema de fotografía corporal total, la imagen sola distingue lesiones malignas muy por encima del azar, pero con este extractor queda por debajo de M1 en las cuatro métricas.`,
  `Una partición por filas habría dejado al ${cifra(dec(DI.naive_pct) + "%", fDis("comparacion_particion_naive.pct_grupos_con_fuga"))} de los pacientes a los dos lados de la validación.`]);
// borrador-v2.md, «Recomendación», «Qué no se puede afirmar».
document.getElementById("no-se-puede").innerHTML = L([
  `<b>Que M3 limpio sea mejor en las métricas de triaje.</b> En la sensibilidad top-15 y en el NNT80% SE no se distingue de M2.`,
  `<b>Cuál de los dos sesgos de M3 pesaba.</b> M3 limpio cambia tres cosas a la vez.`,
  `<b>Cuánto rinde M3 limpio fuera del conjunto de desarrollo.</b> El conjunto reservado no se ha abierto. Cuando se abra, la estimación principal ` +
  `seguirá siendo la validación cruzada repetida, y la recomendación no cambiará por su resultado.`,
  `<b>Nada sobre otros extractores de imagen.</b> Solo se probaron las variables de DINOv2 sin reentrenarlo; las redes de imagen del ganador quedaron fuera.`,
  `<b>Cuánto rinde un modelo con fotos de teléfono.</b> La imagen sola se midió sobre los recortes estandarizados del sistema de fotografía corporal total. ` +
  `El artículo del conjunto de datos advierte que las fotos que toman los pacientes ${citaIS("luz_y_campo")}.`,
  `<b>Que este trabajo supere o no a la solución ganadora.</b> Su evaluación usó otros datos y otras particiones.`,
  `<b>Nada clínico.</b> Los modelos ordenan lesiones por sospecha; no dicen qué tiene un paciente ni qué hacer con él. Son evidencia para una decisión humana.`]);

/* ---------- 7. limitaciones ---------- */
// borrador-v2.md, «Datos y validación», «Los datos» (la frase del archivo de prueba), y «Limitaciones».
document.getElementById("limitaciones").innerHTML = P([
  `El archivo de prueba que publica el reto es un marcador de posición, sin casos reales, así que no hay contra qué medir un resultado final ` +
  `independiente fuera de lo que este proyecto aparte.`]) + L([
  `<b>La clase negativa no está confirmada.</b> Las lesiones malignas tienen patología; de las benignas, <i>"most never underwent a skin biopsy"</i>. ` +
  `La mayoría de los negativos son lesiones que un dermatólogo no consideró preocupantes, no lesiones confirmadas como sanas.`,
  `<b>Las imágenes tienen una resolución óptica comparable a la de un teléfono inteligente.</b> Así las describe el artículo del conjunto de datos: ` +
  `<i>"comparable in optical resolution to smartphone images"</i>. El resultado de la imagen se limita a estas imágenes y a este extractor.`,
  `<b>Muchas comparaciones a la vez.</b> Las cinco comparaciones M2 − M1, M4 − M2, M4b − M2, M3 − M2 y M3 limpio − M2 se leen en cuatro métricas cada una, ` +
  `sin corregir por multiplicidad, y el intervalo del NNT80% SE de M2 − M1 queda al límite del cero.`,
  `<b>La corrección de la varianza es aproximada.</b> Nadeau y Bengio la derivan para divisiones aleatorias independientes, y aquí se aplica a una validación por pliegues.`,
  `<b>El NNT80% SE se calcula con una lectura propia</b>, porque el organizador no publica script para él.`,
  `<b>El conjunto reservado no es del todo independiente.</b> No es ajeno a las decisiones tomadas antes de sellarlo ni al diseño de las variables de la ` +
  `solución ganadora, que siguen M2 y M3 limpio.`,
  `<b>Los tiempos son de un solo equipo</b>, con DINOv2 en la GPU y los modelos tabulares en la CPU. Solo comparan estos modelos entre sí.`,
  `<b>Dos supuestos sin verificar.</b> No se sabe si el clasificador de nevus que produce <code>tbp_lv_nevi_confidence</code> se entrenó con lesiones ` +
  `de este conjunto. Y nada comprueba la versión del código de DINOv2; solo sus pesos, por hash.`,
  `<b>Un mecanismo medido a medias.</b> Se midió cómo falla el gradient boosting sin balancear: hunde a una parte de los ` +
  `positivos al fondo del ordenamiento. Por qué lo hace no se midió.`,
  `<b>La prueba de la partición cubre dos modelos.</b> Que partir por filas no cambie el veredicto se midió con la logística ` +
  `y el boosting balanceados, no con los modelos que usan el contexto de paciente.`]);

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

# Nombre, sin extensión, de la salida de la Fase 5 en outputs/. No está
# fijado: lo fija el guion que abra el reservado (PLAN.md, Fase 5). Hasta
# entonces ningún archivo que lea la página puede declarar el reservado.
SALIDA_FASE_5 = None

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
        subprocess.run(
            [sys.executable, VERIFICADOR, "--borrador", BORRADOR_VIGENTE,
             "--outputs-dir", os.path.abspath(outputs_dir), "--out", recalculada],
            cwd=RAIZ, check=True, capture_output=True,
        )
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

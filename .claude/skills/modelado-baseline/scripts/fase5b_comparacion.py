#!/usr/bin/env python3
"""
fase5b_comparacion.py — la comparación descriptiva de la puerta de la Fase 5b (PLAN.md): las puntuaciones
privadas de Kaggle de los cuatro envíos frente a las referencias fijadas, y los cuatro modelos en las tres
evaluaciones del proyecto. Lee solo outputs/ y referencias/; no entrena, no puntúa y no da ningún intervalo.

Las cifras de Kurtansky et al. 2025 se leen de su texto completo versionado, en la línea fijada, y el script se
detiene si la línea no dice lo que se espera. Las públicas de Kaggle se reportan; las comparaciones se hacen con
las privadas, las del tablero final. No da posiciones en el tablero: no hay ninguna fuente versionada de él.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5b_comparacion.py --out outputs/fase5b-comparacion
"""

import argparse
import json
import os
import re
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
KURTANSKY = "referencias/kurtansky-2025-triaje-automatizado-tbp.md"
MODELOS = ("M3limpio", "Red4e", "C7", "ImagenBasicos")  # el orden de envío
# El ganador en el tablero privado: la línea y la frase que da su pAUC.
GANADOR = (196, r"The winning model scored pAUC>80% TPR\s=\s(0\.\d+) on the private leaderboard")
# Las variantes del ganador en la Tabla 3, clasificación de malignidad: la línea y sus cuatro clases de variables
# (Meta-basic, Meta-WB360, Tiles, Patient context), marcadas con x. La pAUC va en la columna 6.
TABLA_3 = {"modelo_completo": (207, ["x", "x", "x", "x"]),
           "sin_imagenes": (209, ["x", "x", "", "x"]),
           "solo_imagenes": (216, ["", "", "x", ""])}
CABECERA_TABLA_3 = ["Meta-basic", "Meta-WB360", "Tiles", "Patient context"]


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return f.read()


def json_de(ruta):
    return json.loads(leer(ruta))


def estructura_tabla_3(lineas):
    """Que las filas fijadas están en el bloque de clasificación de malignidad, con las columnas esperadas."""
    problemas = []
    if lineas[202].split("\t")[6:7] != ["pAUC>80% TPR"]:
        problemas.append("la línea 203 no tiene la pAUC en la columna 6")
    if not lineas[203].startswith("Malignancy classification\t"):
        problemas.append("la línea 204 no abre el bloque de malignidad")
    if lineas[205].split("\t")[2:6] != CABECERA_TABLA_3:
        problemas.append("la línea 206 no tiene las cuatro clases de variables en las columnas 2 a 5")
    if not lineas[216].startswith("Melanoma classification\t"):
        problemas.append("la línea 217 no abre el bloque de melanoma")
    return problemas


def fila_tabla_3(lineas, n, marcas):
    celdas = lineas[n - 1].split("\t")
    if celdas[2:6] != marcas:
        raise ValueError(f"la línea {n} tiene las clases {celdas[2:6]}, no {marcas}")
    return celdas[6]


def frase(lineas, n, patron):
    encontradas = re.findall(patron, lineas[n - 1])
    if len(encontradas) != 1:
        raise ValueError(f"la línea {n} tiene {len(encontradas)} coincidencias de la frase, no 1")
    return encontradas[0]


def falla(f, *args):
    try:
        f(*args)
    except (ValueError, SystemExit):
        return True
    return False


def puntuado(registro):
    """El envío con puntuación de un modelo; se detiene si no hay exactamente uno."""
    completos = [e for e in registro["envios"] if e.get("status") == "COMPLETE"]
    if len(completos) != 1:
        raise SystemExit(f"ERROR: {registro['modelo']} tiene {len(completos)} envíos con puntuación, no 1.")
    return completos[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lineas = leer(KURTANSKY).split("\n")
    problemas = estructura_tabla_3(lineas)
    if problemas:
        raise SystemExit("ERROR: " + "; ".join(problemas))
    referencias = {"ganador_tablero_privado": {"texto": frase(lineas, *GANADOR), "fuente": f"{KURTANSKY}, línea "
                                               f"{GANADOR[0]}"}}
    for clave, (n, marcas) in TABLA_3.items():
        referencias[clave] = {"texto": fila_tabla_3(lineas, n, marcas), "fuente": f"{KURTANSKY}, Tabla 3, línea {n}",
                              "clases_de_variables": dict(zip(CABECERA_TABLA_3, [m == "x" for m in marcas]))}
    for r in referencias.values():
        r["pauc"] = float(r["texto"])

    kaggle = {}
    for m in MODELOS:
        ruta = f"outputs/fase5b-envio-{m.lower()}.json"
        e = puntuado(json_de(ruta))
        kaggle[m] = {"envio": e["ref"], "publica": float(e["publicScore"]), "privada": float(e["privateScore"]),
                     "texto": {"publica": e["publicScore"], "privada": e["privateScore"]},
                     "fuente": f"{ruta} > envios.0.publicScore y .privateScore"}

    posterior = json_de("outputs/fase5-posterior.json")["tabla"]["modelos"]
    reservado = json_de("outputs/fase5-reservado.json")["metricas"]
    c7 = json_de("outputs/fase4e-c7-vs-m3limpio.json")
    if c7["semillas_corridas"] != [5, 6, 7, 8, 9]:
        raise SystemExit("ERROR: la confirmación de C7 no es la de las semillas 5 a 9.")
    desarrollo = {m: [{"semillas": d["semillas"], "pauc": d["pauc"], "fuente": d["fuente"]}
                      for d in posterior[m]["desarrollo"]] for m in ("M3limpio", "Red4e", "ImagenBasicos")}
    desarrollo["M3limpio"].append({"semillas": c7["semillas_corridas"], "pauc": c7["metricas"]["M3limpio"]["pauc"]
                                   ["media_global"], "fuente": "outputs/fase4e-c7-vs-m3limpio.json > "
                                                               "metricas.M3limpio.pauc.media_global"})
    desarrollo["C7"] = [{"semillas": c7["semillas_corridas"], "pauc": c7["metricas"]["C7"]["pauc"]["media_global"],
                         "fuente": "outputs/fase4e-c7-vs-m3limpio.json > metricas.C7.pauc.media_global"}]
    tabla = {m: {"desarrollo": desarrollo[m],
                 "reservado": ({"pauc": reservado[m]["pauc"]["punto"],
                                "fuente": f"outputs/fase5-reservado.json > metricas.{m}.pauc.punto"}
                               if m in reservado else None),
                 "kaggle_privada": {"pauc": kaggle[m]["privada"], "fuente": kaggle[m]["fuente"]}}
             for m in MODELOS}

    procedencia = json_de("outputs/auditoria-de-fugas.json")["columnas_procedencia"]
    if "attribution" not in procedencia:
        raise SystemExit("ERROR: la etiqueta del hospital no está entre las columnas de procedencia excluidas.")

    def diferencia(a, b):
        return round(a - b, 5)

    p = {m: kaggle[m]["privada"] for m in MODELOS}
    comparaciones = {
        "c7_menos_ganador": {"que_es": "C7 frente al ganador en el tablero privado",
                             "modelo": p["C7"], "referencia": referencias["ganador_tablero_privado"]["pauc"],
                             "diferencia": diferencia(p["C7"], referencias["ganador_tablero_privado"]["pauc"])},
        "m3limpio_menos_sin_imagenes": {"que_es": "M3 limpio frente a la variante «sin imágenes» de la Tabla 3",
                                        "modelo": p["M3limpio"], "referencia": referencias["sin_imagenes"]["pauc"],
                                        "diferencia": diferencia(p["M3limpio"], referencias["sin_imagenes"]["pauc"])},
        "red4e_menos_solo_imagenes": {"que_es": "la red de la 4e frente a la variante «solo imágenes» de la Tabla 3",
                                      "modelo": p["Red4e"], "referencia": referencias["solo_imagenes"]["pauc"],
                                      "diferencia": diferencia(p["Red4e"], referencias["solo_imagenes"]["pauc"])},
        "red4e_menos_imagen_basicos": {"que_es": "la red de la 4e frente a «Imagen + básicos», las dos puntuaciones "
                                                 "de Kaggle; el cuarto envío se decidió después de ver el reservado",
                                       "modelo": p["Red4e"], "referencia": p["ImagenBasicos"],
                                       "diferencia": diferencia(p["Red4e"], p["ImagenBasicos"])},
    }
    aritmetica = {
        "que_es": "aritmética descriptiva de dos fuentes distintas: la diferencia C7 − M3 limpio en la puntuación "
                  "privada de Kaggle, y la diferencia «modelo completo» − «sin imágenes» de la Tabla 3",
        "c7_menos_m3limpio_kaggle_privada": diferencia(p["C7"], p["M3limpio"]),
        "completo_menos_sin_imagenes_tabla_3": diferencia(referencias["modelo_completo"]["pauc"],
                                                          referencias["sin_imagenes"]["pauc"])}

    ganador, n_sin = GANADOR, TABLA_3["sin_imagenes"]
    casos = [
        {"caso": "las cuatro referencias se leen en su línea", "ok": len(referencias) == 4, "debe_fallar": False},
        {"caso": "las clases de «sin imágenes» en la línea siguiente no se leen",
         "ok": falla(fila_tabla_3, lineas, n_sin[0] + 1, n_sin[1]), "debe_fallar": True},
        {"caso": "la frase del ganador en la línea siguiente no se lee", "ok": falla(frase, lineas, ganador[0] + 1,
                                                                                  ganador[1]), "debe_fallar": True},
        {"caso": "la Tabla 3 corrida una línea no tiene la estructura esperada",
         "ok": bool(estructura_tabla_3(lineas[1:])), "debe_fallar": True},
        {"caso": "un modelo sin envío puntuado se rechaza",
         "ok": falla(puntuado, {"modelo": "falso", "envios": [{"status": "ERROR"}]}), "debe_fallar": True},
    ]
    controles = {"casos": casos, "fallos": sum(not c["ok"] for c in casos)}
    if controles["fallos"]:
        print(json.dumps(controles, ensure_ascii=False, indent=1))
        raise SystemExit("ERROR: los controles fallaron; no se escribe la salida.")

    salida = {
        "que_es": "la comparación descriptiva de la puerta de la Fase 5b (PLAN.md, Fase 5b): sin intervalo, no da "
                  "ningún resultado a favor ni en contra y no cambia ninguna recomendación",
        "referencias": referencias, "kaggle": kaggle, "comparaciones_con_la_privada": comparaciones,
        "aritmetica_de_dos_fuentes": aritmetica, "tabla_tres_evaluaciones": tabla,
        "como_leerla": [
            "las tres evaluaciones son conjuntos y tipos de estimación distintos. Desarrollo: la media por pliegue "
            "de la validación cruzada repetida sobre los 833 pacientes de desarrollo, con las semillas indicadas, "
            "entrenando con cuatro quintos. Reservado: un solo modelo entrenado con el desarrollo y puntuado en los "
            "209 pacientes reservados. Kaggle: modelos entrenados con los 1.042 pacientes y puntuados en el "
            "subconjunto privado de la prueba oculta",
            "Kaggle da una cifra por envío, sin intervalo",
            "las cifras de la Tabla 3 son de la reproducción del ganador que los organizadores hicieron en su "
            "entorno, con 3 decimales, sobre el conjunto del tablero privado (líneas 200 y 315); el 0.1726 es la "
            "puntuación oficial del ganador en el tablero privado (línea 196)",
            "la variante «sin imágenes» de la Tabla 3 usa los datos básicos, que incluyen la etiqueta del hospital "
            "(línea 315); M3 limpio no la usa (outputs/auditoria-de-fugas.json > columnas_procedencia)",
            "el C7 de Kaggle puntúa con la media de cinco redes, una por pliegue; en la validación cruzada se evaluó "
            "con una red por pliegue (PLAN.md, Fase 5b)",
            "C7 no se evaluó en el reservado: la Fase 5 no lo incluía",
            "las públicas se reportan; las comparaciones se hacen con las privadas, las del tablero final",
            "no se dan posiciones en el tablero: no hay ninguna fuente versionada del tablero completo",
        ],
        "controles": controles, "comando": {"argumentos": ["--out", args.out]},
        "fecha": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    def semillas(s):
        return f"semillas {s[0]} a {s[-1]}"

    lineas_md = ["# Fase 5b — la comparación descriptiva de la puerta",
                 "Puntuaciones privadas de Kaggle; sin intervalo, descriptiva:"]
    for c in comparaciones.values():
        lineas_md.append(f"- {c['que_es']}: {c['modelo']} frente a {c['referencia']}, diferencia {c['diferencia']}.")
    lineas_md.append(f"- Aritmética de dos fuentes: C7 − M3 limpio en Kaggle {aritmetica['c7_menos_m3limpio_kaggle_privada']}; "
                     f"«modelo completo» − «sin imágenes» en la Tabla 3 {aritmetica['completo_menos_sin_imagenes_tabla_3']}.")
    lineas_md.append("pAUC en desarrollo, reservado y Kaggle (privada; pública entre paréntesis):")
    for m in MODELOS:
        t = tabla[m]
        dev = "; ".join(f"{d['pauc']} ({semillas(d['semillas'])})" for d in t["desarrollo"])
        res = t["reservado"]["pauc"] if t["reservado"] else "no se evaluó"
        lineas_md.append(f"- {m}: desarrollo {dev}; reservado {res}; Kaggle {kaggle[m]['privada']} "
                         f"({kaggle[m]['publica']}).")
    lineas_md.append(f"Controles: {len(casos)} de {len(casos)} bien, {sum(c['debe_fallar'] for c in casos)} de ellos "
                     "casos que deben fallar. Conjuntos y estimaciones distintos; Kaggle no da intervalo.")
    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_md) + "\n")
    print(f"Escrito: {args.out}.json y .md")


if __name__ == "__main__":
    main()

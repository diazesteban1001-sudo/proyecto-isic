#!/usr/bin/env python3
"""
fase5c_efectos.py — los seis efectos descriptivos de la Fase 5c (PLAN.md), con las
puntuaciones de Kaggle tal como están en outputs/: las de M3 limpio y C7 de la
Fase 5b y las de los cuatro envíos de la 5c. Cada efecto es una resta entre dos
puntuaciones privadas, las del tablero final, como en la 5b; las públicas se
reportan al lado. Sin intervalo: Kaggle da una cifra por envío. No envía nada y
no cambia ninguna recomendación.

  - promediar, sin hospital: «M3 limpio promediado» − M3 limpio, y «C7
    promediado» − C7;
  - el hospital: sin imagen, «M3 limpio promediado + hospital» − «M3 limpio
    promediado»; con imagen, «C7 promediado + hospital» − «C7 promediado»;
  - la imagen: sin hospital, «C7 promediado» − «M3 limpio promediado»; con
    hospital, «C7 promediado + hospital» − «M3 limpio promediado + hospital».

Cada efecto dice además si tiene el mismo signo en la pública y en la privada.
Y, como aritmética descriptiva, la descomposición de la distancia de C7 al
ganador en la privada (outputs/fase5b-comparacion.json): cuánto cubre
promediar, cuánto el hospital y cuánto queda, en ese orden, el de los envíos.

Uso:
    .venv/bin/python .claude/skills/modelado-baseline/scripts/fase5c_efectos.py --out outputs/fase5c-efectos
"""

import argparse
import datetime
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))
FUENTES = {"M3limpio": "outputs/fase5b-envio-m3limpio.json", "C7": "outputs/fase5b-envio-c7.json",
           "M3limpioProm": "outputs/fase5c-envio-m3limpioprom.json",
           "M3limpioPromHosp": "outputs/fase5c-envio-m3limpiopromhosp.json",
           "C7Prom": "outputs/fase5c-envio-c7prom.json", "C7PromHosp": "outputs/fase5c-envio-c7promhosp.json"}
NOMBRES = {"M3limpio": "M3 limpio (Fase 5b)", "C7": "C7 (Fase 5b)", "M3limpioProm": "M3 limpio promediado",
           "M3limpioPromHosp": "M3 limpio promediado + hospital", "C7Prom": "C7 promediado",
           "C7PromHosp": "C7 promediado + hospital"}
EFECTOS = {  # efecto: (qué mide, modelo, menos este)
    "promediar_sin_imagen": ("el efecto de promediar, sin hospital y sin imagen", "M3limpioProm", "M3limpio"),
    "promediar_con_imagen": ("el efecto de promediar, sin hospital y con imagen", "C7Prom", "C7"),
    "hospital_sin_imagen": ("el efecto del hospital, sin imagen", "M3limpioPromHosp", "M3limpioProm"),
    "hospital_con_imagen": ("el efecto del hospital, con imagen", "C7PromHosp", "C7Prom"),
    "imagen_sin_hospital": ("el efecto de la imagen, sin hospital", "C7Prom", "M3limpioProm"),
    "imagen_con_hospital": ("el efecto de la imagen, con hospital", "C7PromHosp", "M3limpioPromHosp"),
}


def json_de(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return json.load(f)


def puntuado(registro, modelo):
    """El envío con puntuación del modelo; se detiene si el registro es de otro modelo o si
    no tiene exactamente un envío puntuado."""
    if registro.get("modelo") != modelo:
        raise SystemExit(f"ERROR: el registro es de {registro.get('modelo')!r}, no de {modelo!r}.")
    completos = [e for e in registro["envios"] if e.get("status") == "COMPLETE"]
    if len(completos) != 1:
        raise SystemExit(f"ERROR: {modelo} tiene {len(completos)} envíos con puntuación, no 1.")
    return completos[0]


def falla(f, *args):
    try:
        f(*args)
    except SystemExit:
        return True
    return False


def diferencia(a, b):
    return round(a - b, 5)


def efectos(kaggle):
    salida = {}
    for k, (q, a, b) in EFECTOS.items():
        privada = diferencia(kaggle[a]["privada"], kaggle[b]["privada"])
        publica = diferencia(kaggle[a]["publica"], kaggle[b]["publica"])
        salida[k] = {"que_es": q, "modelo": NOMBRES[a], "menos": NOMBRES[b], "privada": privada, "publica": publica,
                     "mismo_signo_en_la_publica": (privada > 0) == (publica > 0) and privada != 0 and publica != 0}
    return salida


def descomposicion(c7_privada, ganador, efectos_):
    """La distancia de C7 al ganador en la privada, en tres partes: lo que cubre promediar
    («C7 promediado» − C7), lo que cubre el hospital («C7 promediado + hospital» − «C7
    promediado») y lo que queda («C7 promediado + hospital» − el ganador)."""
    distancia = diferencia(c7_privada, ganador)
    partes = {"promediar": efectos_["promediar_con_imagen"]["privada"],
              "hospital": efectos_["hospital_con_imagen"]["privada"]}
    queda = diferencia(c7_privada + partes["promediar"] + partes["hospital"], ganador)
    return {"distancia_de_c7_al_ganador": distancia, "cubre_promediar": partes["promediar"],
            "cubre_el_hospital": partes["hospital"], "queda": queda,
            "porcentaje_de_la_distancia": {"promediar": round(100 * partes["promediar"] / -distancia, 1),
                                           "hospital": round(100 * partes["hospital"] / -distancia, 1),
                                           "queda": round(100 * queda / distancia, 1)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    kaggle = {}
    for m, ruta in FUENTES.items():
        e = puntuado(json_de(ruta), m)
        kaggle[m] = {"nombre": NOMBRES[m], "envio": e["ref"], "publica": float(e["publicScore"]),
                     "privada": float(e["privateScore"]),
                     "texto": {"publica": e["publicScore"], "privada": e["privateScore"]},
                     "fuente": f"{ruta} > envios.0.publicScore y .privateScore"}
    resultado_efectos = efectos(kaggle)
    comparacion_5b = json_de("outputs/fase5b-comparacion.json")
    ganador = comparacion_5b["referencias"]["ganador_tablero_privado"]
    distancia_5b = comparacion_5b["comparaciones_con_la_privada"]["c7_menos_ganador"]["diferencia"]
    desc = descomposicion(kaggle["C7"]["privada"], ganador["pauc"], resultado_efectos)
    queda_directo = diferencia(kaggle["C7PromHosp"]["privada"], ganador["pauc"])

    sintetico = {"modelo": "M3limpioProm", "envios": [{"status": "COMPLETE", "publicScore": "0.1", "privateScore": "0.1"}]}
    con_error = {"modelo": "M3limpioProm", "envios": [{"status": "ERROR"}]}
    cambio = {"C7Prom": "M3limpioProm", "M3limpioProm": "C7Prom"}
    invertido = {m: {**v, "privada": kaggle[cambio.get(m, m)]["privada"]} for m, v in kaggle.items()}
    casos = [
        {"caso": "los seis registros tienen un envío puntuado de su modelo", "ok": len(kaggle) == 6, "debe_fallar": False},
        {"caso": "un registro sin envío puntuado se rechaza", "ok": falla(puntuado, con_error, "M3limpioProm"),
         "debe_fallar": True},
        {"caso": "el registro de otro modelo se rechaza", "ok": falla(puntuado, sintetico, "M3limpioPromHosp"),
         "debe_fallar": True},
        {"caso": "con C7 promediado y M3 limpio promediado intercambiados, el efecto de la imagen sin hospital "
                 "cambia de signo",
         "ok": efectos(invertido)["imagen_sin_hospital"]["privada"] == -resultado_efectos["imagen_sin_hospital"]["privada"]
         and resultado_efectos["imagen_sin_hospital"]["privada"] != 0, "debe_fallar": True},
        {"caso": "la distancia de C7 al ganador es la de outputs/fase5b-comparacion.json",
         "ok": desc["distancia_de_c7_al_ganador"] == distancia_5b, "debe_fallar": False},
        {"caso": "con la puntuación pública de C7, la distancia no es la de la 5b",
         "ok": descomposicion(kaggle["C7"]["publica"], ganador["pauc"], resultado_efectos)["distancia_de_c7_al_ganador"]
         != distancia_5b, "debe_fallar": True},
        {"caso": "lo que queda es «C7 promediado + hospital» − el ganador",
         "ok": desc["queda"] == queda_directo, "debe_fallar": False},
    ]
    controles = {"casos": casos, "de_casos": len(casos), "fallos": sum(not c["ok"] for c in casos),
                 "deben_fallar": sum(c["debe_fallar"] for c in casos)}
    if controles["fallos"]:
        print(json.dumps(casos, ensure_ascii=False, indent=2))
        raise SystemExit("ERROR: fallaron controles; no se escribe nada.")

    resultado = {
        "que_es": ("los seis efectos descriptivos de la Fase 5c (PLAN.md): restas entre puntuaciones de Kaggle, sin "
                   "intervalo; no da ningún resultado a favor ni en contra y no cambia ninguna recomendación"),
        "kaggle": kaggle,
        "efectos": resultado_efectos,
        "descomposicion_de_la_distancia_al_ganador": {
            "que_es": ("aritmética descriptiva: la distancia de C7 al ganador en la privada, en lo que cubre promediar, lo "
                       "que cubre el hospital y lo que queda, en ese orden"),
            "ganador": {"pauc": ganador["pauc"], "fuente": f"outputs/fase5b-comparacion.json > "
                                                            f"referencias.ganador_tablero_privado ({ganador['fuente']})"},
            **desc,
            "como_leerla": ("el orden es el de los envíos: primero promediar, después el hospital; C7 con hospital y sin "
                            "promediar no se envió, así que la parte de cada uno depende de ese orden"),
        },
        "como_leerlos": [
            "cada efecto es una resta entre las puntuaciones de dos envíos; la privada es la del tablero final, y con "
            "ella se compara, como en la Fase 5b; la pública se reporta al lado",
            "Kaggle da una cifra por envío y no da intervalo",
            "promediar cambia dos cosas a la vez: los modelos de la 5b se ajustan con todos los pacientes y cada uno de "
            "los 45 con cuatro quintos (PLAN.md, Fase 5c, «Salvedades»)",
            "la fase se decidió después de ver los resultados de la 5b: es una segunda mirada al mismo conjunto de "
            "prueba",
        ],
        "controles": controles,
        "comando": {"interprete": os.path.relpath(sys.executable, RAIZ), "argumentos": sys.argv},
        "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out = args.out if os.path.isabs(args.out) else os.path.join(RAIZ, args.out)
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    lineas = ["# Fase 5c — los seis efectos, descriptivos y sin intervalo",
              "Puntuación privada (pública): " + "; ".join(f"{v['nombre']} {v['texto']['privada']} ({v['texto']['publica']})"
                                                          for v in kaggle.values()) + "."]
    lineas += [f"- {v['que_es']}: {v['privada']:+g} en la privada ({v['publica']:+g} en la pública)"
               for v in resultado_efectos.values()]
    d = resultado["descomposicion_de_la_distancia_al_ganador"]
    lineas.append(f"Distancia de C7 al ganador en la privada: {d['distancia_de_c7_al_ganador']:+g}; promediar cubre "
                  f"{d['cubre_promediar']:+g}, el hospital {d['cubre_el_hospital']:+g} y queda {d['queda']:+g}.")
    lineas.append(f"Controles: {controles['de_casos']} de {controles['de_casos']} bien, {controles['deben_fallar']} de "
                  "ellos casos que deben fallar. Kaggle no da intervalo; no cambia ninguna recomendación.")
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito: {args.out}.json y .md", flush=True)


if __name__ == "__main__":
    main()

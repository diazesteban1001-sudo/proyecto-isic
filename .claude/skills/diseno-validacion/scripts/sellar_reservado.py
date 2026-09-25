#!/usr/bin/env python3
"""
sellar_reservado.py — aparta y sella el conjunto reservado (holdout) de
pacientes. Parte de la skill diseno-validacion.

Decisión de la persona (PLAN.md, Fase 1, 2026-09-25): 20 % de los
pacientes, estratificado por centro (`attribution`) y por presencia de al
menos una lesión maligna, semilla 2026. Si algún estrato queda vacío a un
lado —en particular, un centro sin pacientes portadores en el reservado o
en desarrollo—, el script se detiene sin escribir nada.

Es el único script del proyecto que lee el CSV de entrenamiento entero:
los instrumentos leen solo el conjunto de desarrollo, a través de
datos_desarrollo.py, que exige este archivo.

No entrena nada ni calcula ninguna métrica de modelo. Escribe la lista de
pacientes reservados y recuentos a cada lado.

Sellado: si el archivo de salida ya existe, no se sobrescribe. El script
vuelve a calcular la partición y la compara con la sellada; si coincide lo
dice, y si no coincide falla. Para sellar otra partición hay que borrar el
archivo a mano, y eso queda en el historial.

Uso:
    python sellar_reservado.py --data data/train-metadata.csv \
                               --group-col patient_id \
                               --target-col target \
                               --centro-col attribution \
                               --fraccion 0.2 \
                               --seed 2026 \
                               --out outputs/holdout-pacientes
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

MAX_CENTROS_MD = 8


def tabla_de_pacientes(df, group_col, target_col, centro_col):
    """Una fila por paciente, ordenada por patient_id para que la semilla
    reproduzca la misma partición con el mismo archivo."""
    centros_por_paciente = df.groupby(group_col)[centro_col].nunique(dropna=False)
    varios = centros_por_paciente[centros_por_paciente > 1]
    if len(varios):
        raise SystemExit(
            f"ERROR: {len(varios)} pacientes tienen más de un valor de '{centro_col}' "
            f"(p. ej. {list(varios.index[:3])}). No se puede estratificar por centro."
        )
    p = df.groupby(group_col).agg(
        centro=(centro_col, "first"),
        malignas=(target_col, "sum"),
    ).sort_index()
    p["portador"] = p["malignas"] > 0
    return p


def recuentos(p):
    por_centro = {}
    for centro, g in p.groupby("centro"):
        por_centro[str(centro)] = {
            "pacientes": int(len(g)),
            "pacientes_portadores": int(g["portador"].sum()),
        }
    return {
        "pacientes": int(len(p)),
        "pacientes_portadores": int(p["portador"].sum()),
        "lesiones_malignas": int(p["malignas"].sum()),
        "pacientes_por_centro": por_centro,
    }


def estratos_vacios(p, reservado):
    """Estratos (centro × portador) sin ningún paciente a uno de los dos
    lados. Devuelve una lista de mensajes; vacía si todo está bien."""
    problemas = []
    for (centro, portador), g in p.groupby(["centro", "portador"]):
        n_res = int(g.index.isin(reservado).sum())
        n_des = len(g) - n_res
        tipo = "portadores" if portador else "no portadores"
        if n_res == 0:
            problemas.append(f"{centro}, {tipo}: 0 en el reservado ({n_des} en desarrollo)")
        if n_des == 0:
            problemas.append(f"{centro}, {tipo}: 0 en desarrollo ({n_res} en el reservado)")
    return problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--group-col", required=True)
    ap.add_argument("--target-col", required=True)
    ap.add_argument("--centro-col", required=True)
    ap.add_argument("--fraccion", type=float, default=0.2)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.data, low_memory=False,
                     usecols=[args.group_col, args.target_col, args.centro_col])

    p = tabla_de_pacientes(df, args.group_col, args.target_col, args.centro_col)
    estrato = p["centro"].astype(str) + " | " + p["portador"].map({True: "portador", False: "no portador"})

    try:
        _, reservado = train_test_split(
            p.index.to_numpy(), test_size=args.fraccion,
            stratify=estrato.to_numpy(), random_state=args.seed,
        )
    except ValueError as e:
        raise SystemExit(f"ERROR: no se pudo estratificar: {e}")
    reservado = sorted(str(x) for x in reservado)

    problemas = estratos_vacios(p, reservado)
    if problemas:
        raise SystemExit(
            "ERROR: la partición deja estratos vacíos a un lado. No se sella nada:\n  - "
            + "\n  - ".join(problemas)
        )

    ruta_json = f"{args.out}.json"
    if os.path.exists(ruta_json):
        with open(ruta_json, encoding="utf-8") as f:
            sellado = json.load(f)
        if sellado.get("pacientes_reservados") == reservado and sellado.get("semilla") == args.seed:
            print(f"{ruta_json} ya está sellado y coincide con la partición recalculada. No se reescribe.")
            return
        raise SystemExit(
            f"ERROR: {ruta_json} ya está sellado y NO coincide con la partición recalculada. "
            f"No se sobrescribe un conjunto sellado."
        )

    es_reservado = p.index.isin(reservado)
    resultado = {
        "semilla": args.seed,
        "metodo": {
            "descripcion": (
                f"{round(100 * args.fraccion)} % de los pacientes, estratificado por centro "
                f"('{args.centro_col}') y por presencia de al menos una lesión maligna"
            ),
            "unidad": f"paciente ('{args.group_col}')",
            "funcion": "sklearn.model_selection.train_test_split(test_size=fraccion, stratify=estrato, random_state=semilla)",
            "entrada": f"una fila por paciente, ordenada por '{args.group_col}'",
            "fraccion": args.fraccion,
            "version_scikit_learn": sklearn.__version__,
            "regla_de_parada": "si algún estrato (centro × portador) queda vacío a un lado, no se sella",
        },
        "fuente": args.data,
        "fecha_sellado": datetime.now(timezone.utc).isoformat(),
        "pacientes_reservados": reservado,
        "recuentos": {
            "reservado": recuentos(p[es_reservado]),
            "desarrollo": recuentos(p[~es_reservado]),
        },
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    r, d = resultado["recuentos"]["reservado"], resultado["recuentos"]["desarrollo"]
    lineas = []
    lineas.append(f"# Conjunto reservado — sellado sobre {args.data}")
    lineas.append(f"Semilla {args.seed} · {resultado['metodo']['descripcion']}")
    lineas.append(
        f"Método: train_test_split estratificado de scikit-learn {sklearn.__version__}, "
        f"sobre una fila por paciente ordenada por {args.group_col}"
    )
    for etiqueta, bloque in (("Reservado", r), ("Desarrollo", d)):
        lineas.append(
            f"{etiqueta}: {bloque['pacientes']} pacientes · {bloque['pacientes_portadores']} portadores · "
            f"{bloque['lesiones_malignas']} lesiones malignas"
        )
    lineas.append("Pacientes por centro, reservado / desarrollo (portadores entre paréntesis):")
    centros = sorted(set(r["pacientes_por_centro"]) | set(d["pacientes_por_centro"]))
    vacio = {"pacientes": 0, "pacientes_portadores": 0}
    for c in centros[:MAX_CENTROS_MD]:
        cr, cd = r["pacientes_por_centro"].get(c, vacio), d["pacientes_por_centro"].get(c, vacio)
        lineas.append(
            f"- {c}: {cr['pacientes']} ({cr['pacientes_portadores']}) / "
            f"{cd['pacientes']} ({cd['pacientes_portadores']})"
        )
    if len(centros) > MAX_CENTROS_MD:
        lineas.append(f"- ... y {len(centros) - MAX_CENTROS_MD} centros más")
    lineas.append(f"Lista de patient_id reservados: {ruta_json}, campo `pacientes_reservados`.")

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {ruta_json} y {args.out}.md")


if __name__ == "__main__":
    main()

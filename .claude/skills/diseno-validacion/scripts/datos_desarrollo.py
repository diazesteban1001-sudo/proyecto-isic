#!/usr/bin/env python3
"""
datos_desarrollo.py — carga el conjunto de desarrollo: el CSV de
entrenamiento sin los pacientes del conjunto reservado.

La usan las cuatro skills instrumento (eda-diagnostico, diseno-validacion,
auditoria-de-fugas, modelado-baseline). Vive en diseno-validacion porque es
la skill que sella el conjunto reservado (sellar_reservado.py), que es el
único script que lee el CSV entero.

Falla de forma explícita en dos casos, con SystemExit: código 1 y el
mensaje en stderr, como el guardarraíl de las columnas excluidas.

1. No existe outputs/holdout-pacientes.json. Sin conjunto sellado ningún
   instrumento lee los datos, y se comprueba antes de leer el CSV.
2. Aparece un paciente reservado en los datos que se van a entregar.

La exclusión (excluir_reservados) y la comprobación (exigir_sin_reservados)
son pasos separados a propósito. Mientras la exclusión funcione, la
comprobación no puede fallar: está para cuando no funcione, porque un
cambio la rompa o porque alguien lea el CSV por otra vía y llame solo a
exigir_sin_reservados. El control positivo, test_datos_desarrollo.py,
desactiva la exclusión y comprueba que la comprobación se dispara.

Desde la Fase 3 carga también las características de imagen de desarrollo
(cargar_caracteristicas_desarrollo). Se niega a leer el archivo del conjunto
reservado por dos vías independientes: el atributo "conjunto" del archivo, que
tiene que decir "desarrollo", y su contenido: ningún isic_id puede ser de un
paciente reservado. La primera atrapa el archivo equivocado; la segunda, un
archivo mal etiquetado o hecho a mano.
"""

import json
import os

import pandas as pd

RUTA_HOLDOUT = "outputs/holdout-pacientes.json"


def leer_reservados(ruta_holdout=RUTA_HOLDOUT):
    if not os.path.exists(ruta_holdout):
        raise SystemExit(
            f"ERROR: no existe {ruta_holdout}. El conjunto reservado no está sellado, "
            f"y ningún instrumento lee los datos sin él — corre "
            f"diseno-validacion/scripts/sellar_reservado.py primero."
        )
    with open(ruta_holdout, encoding="utf-8") as f:
        sellado = json.load(f)
    reservados = sellado.get("pacientes_reservados")
    if not reservados:
        raise SystemExit(f"ERROR: {ruta_holdout} no tiene lista de pacientes reservados.")
    return {str(p) for p in reservados}


def excluir_reservados(df, reservados, group_col):
    return df[~df[group_col].astype(str).isin(reservados)].reset_index(drop=True)


def exigir_sin_reservados(df, reservados, group_col, origen):
    presentes = sorted(set(df[group_col].astype(str)) & reservados)
    if presentes:
        raise SystemExit(
            f"ERROR: {len(presentes)} pacientes del conjunto reservado aparecen en {origen} "
            f"(p. ej. {presentes[:3]}). El conjunto reservado no se toca hasta la "
            f"evaluación final."
        )


def cargar_desarrollo(ruta_csv, group_col="patient_id", ruta_holdout=RUTA_HOLDOUT):
    """Devuelve (df, datos): el conjunto de desarrollo con índice 0..n-1, y
    un bloque que cada instrumento copia a su JSON para declarar sobre qué
    datos midió."""
    reservados = leer_reservados(ruta_holdout)
    df = pd.read_csv(ruta_csv, low_memory=False)
    if group_col not in df.columns:
        raise SystemExit(f"ERROR: la columna '{group_col}' no existe en {ruta_csv}")
    desarrollo = excluir_reservados(df, reservados, group_col)
    exigir_sin_reservados(desarrollo, reservados, group_col, f"el conjunto de desarrollo leído de {ruta_csv}")
    datos = {
        "archivo": ruta_csv,
        "conjunto": "desarrollo",
        "sin_los_pacientes_de": ruta_holdout,
    }
    return desarrollo, datos


def cargar_caracteristicas_desarrollo(ruta_h5, ruta_csv, group_col="patient_id", ruta_holdout=RUTA_HOLDOUT):
    """Devuelve (isic_id, cls, decodificada) de un archivo de características de
    desarrollo. Falla si el archivo no declara ser de desarrollo, si alguno de
    sus isic_id no está en el CSV o si alguno es de un paciente reservado."""
    import h5py

    reservados = leer_reservados(ruta_holdout)
    with h5py.File(ruta_h5, "r") as f:
        conjunto = f.attrs.get("conjunto")
        if conjunto != "desarrollo":
            raise SystemExit(
                f"ERROR: {ruta_h5} declara el conjunto {conjunto!r}, no 'desarrollo'. El cargador de "
                f"desarrollo no lee las características del conjunto reservado."
            )
        ids = f["isic_id"].asstr()[:]
        cls = f["cls"][:]
        decodificada = f["decodificada"][:]
    mapa = pd.read_csv(ruta_csv, usecols=["isic_id", group_col]).set_index("isic_id")[group_col]
    desconocidos = pd.Index(ids).difference(mapa.index)
    if len(desconocidos):
        raise SystemExit(f"ERROR: {len(desconocidos)} isic_id de {ruta_h5} no están en {ruta_csv}.")
    exigir_sin_reservados(pd.DataFrame({group_col: mapa.loc[ids].to_numpy()}), reservados, group_col,
                          f"las características de {ruta_h5}")
    return list(ids), cls, decodificada

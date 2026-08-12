#!/usr/bin/env python3
"""
eda_profile.py — instrumento de medición para la skill eda-diagnostico.

No interpreta resultados. Solo mide y escribe outputs/<nombre>.json y
outputs/<nombre>.md según el contrato definido en SKILL.md.

Uso:
    python eda_profile.py --train data/train-metadata.csv \
                           --test data/test-metadata.csv \
                           --group-col patient_id \
                           --target-col target \
                           --out outputs/eda-diagnostico
"""

import argparse
import json
import os
from datetime import datetime, timezone

import pandas as pd


def perfil_columnas(df: pd.DataFrame) -> dict:
    tipos = {c: str(df[c].dtype) for c in df.columns}
    faltantes = {}
    for c in df.columns:
        n_na = int(df[c].isna().sum())
        faltantes[c] = {"n": n_na, "pct": round(100 * n_na / len(df), 3) if len(df) else 0.0}
    return tipos, faltantes


def perfil_desbalance(df: pd.DataFrame, target_col: str | None) -> dict | None:
    if not target_col or target_col not in df.columns:
        return None
    conteos = df[target_col].value_counts(dropna=False).to_dict()
    conteos = {str(k): int(v) for k, v in conteos.items()}
    total = len(df)
    pct_pos = None
    # Asume codificación binaria 0/1 si aplica; si no, reporta conteos crudos.
    if set(df[target_col].dropna().unique()) <= {0, 1}:
        pct_pos = round(100 * df[target_col].sum() / total, 4) if total else None
    return {"columna_target": target_col, "conteos": conteos, "pct_positivos": pct_pos}


def perfil_grupos(df: pd.DataFrame, group_col: str | None) -> dict | None:
    if not group_col or group_col not in df.columns:
        return None
    conteo = df.groupby(group_col).size()
    return {
        "columna_grupo": group_col,
        "n_grupos": int(conteo.shape[0]),
        "n_filas": int(len(df)),
        "filas_por_grupo": {
            "min": int(conteo.min()),
            "max": int(conteo.max()),
            "media": round(float(conteo.mean()), 2),
            "mediana": float(conteo.median()),
        },
    }


def columnas_constantes(df: pd.DataFrame) -> list:
    return [c for c in df.columns if df[c].nunique(dropna=False) <= 1]


# Nombres que son identificador por convención del dataset aunque su
# cardinalidad no lo delate (p. ej. lesion_id, mayoritariamente nulo).
IDENTIFICADORES_CONOCIDOS = ("isic_id", "lesion_id")


def columnas_identificador(df: pd.DataFrame) -> list:
    n = len(df)
    ids = {c for c in IDENTIFICADORES_CONOCIDOS if c in df.columns}
    ids |= {c for c in df.columns if n and df[c].nunique(dropna=False) == n}
    return sorted(ids)


def perfil_duplicados(df: pd.DataFrame) -> dict:
    """Cuenta filas duplicadas ignorando las columnas identificador.

    Incluirlas haría que el conteo fuera siempre 0 en cualquier tabla con
    clave primaria, es decir, un chequeo incapaz de detectar lo que mide.
    """
    ids = columnas_identificador(df)
    restantes = [c for c in df.columns if c not in ids]
    if not restantes:
        return {"n": None, "columnas_excluidas": ids}
    return {"n": int(df[restantes].duplicated().sum()), "columnas_excluidas": ids}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--test", required=False, default=None)
    ap.add_argument("--group-col", required=False, default=None)
    ap.add_argument("--target-col", required=False, default=None)
    ap.add_argument("--out", required=True, help="Ruta base sin extensión, ej. outputs/eda-diagnostico")
    args = ap.parse_args()

    # low_memory=False: infiere tipos sobre el archivo completo en vez de por
    # bloques. Evita el DtypeWarning sin alterar los tipos resultantes.
    train = pd.read_csv(args.train, low_memory=False)

    test = None
    test_is_placeholder = False
    if args.test and os.path.exists(args.test):
        test = pd.read_csv(args.test, low_memory=False)
        if len(test) < max(1, 0.01 * len(train)):
            test_is_placeholder = True

    tipos, faltantes = perfil_columnas(train)

    # El test solo se perfila si es un test real; si es placeholder, perfilarlo
    # daria estadisticas sin sentido sobre un punado de filas.
    test_perfil = None
    if test is not None and not test_is_placeholder:
        tipos_test, faltantes_test = perfil_columnas(test)
        test_perfil = {
            "archivo": args.test,
            "n_filas": int(len(test)),
            "n_columnas": int(test.shape[1]),
            "tipos": tipos_test,
            "faltantes": faltantes_test,
        }

    cols_train = set(train.columns)
    cols_test = set(test.columns) if test is not None else set()
    solo_train = sorted(cols_train - cols_test) if test is not None else []
    solo_test = sorted(cols_test - cols_train) if test is not None else []

    dup = perfil_duplicados(train)

    resultado = {
        "fuente": {
            "archivo": args.train,
            "fecha_ejecucion": datetime.now(timezone.utc).isoformat(),
            "n_filas": int(len(train)),
            "n_columnas": int(train.shape[1]),
        },
        "tipos": tipos,
        "faltantes": faltantes,
        "desbalance_target": perfil_desbalance(train, args.target_col),
        "estructura_grupos": perfil_grupos(train, args.group_col),
        "columnas_solo_en_train": solo_train,
        "columnas_solo_en_test": solo_test,
        "test_is_placeholder": test_is_placeholder,
        "test_perfil": test_perfil,
        "duplicados_exactos": dup["n"],
        "duplicados_columnas_excluidas": dup["columnas_excluidas"],
        "constantes": columnas_constantes(train),
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    # Resumen .md: máximo 15 líneas, sin interpretación.
    lineas = []
    lineas.append(f"# EDA diagnóstico — {args.train}")
    lineas.append(f"Filas: {resultado['fuente']['n_filas']} · Columnas: {resultado['fuente']['n_columnas']}")
    n_con_faltantes = sum(1 for v in faltantes.values() if v["n"] > 0)
    lineas.append(f"Columnas con al menos un faltante: {n_con_faltantes}")
    if resultado["desbalance_target"]:
        d = resultado["desbalance_target"]
        lineas.append(f"Target `{d['columna_target']}`: conteos {d['conteos']}, % positivos: {d['pct_positivos']}")
    elif not args.target_col:
        lineas.append("Target: no especificado (--target-col no se pasó).")
    else:
        lineas.append(f"Target: columna '{args.target_col}' no encontrada en el archivo.")
    if resultado["estructura_grupos"]:
        g = resultado["estructura_grupos"]
        lineas.append(
            f"Grupos por `{g['columna_grupo']}`: {g['n_grupos']} grupos, "
            f"{g['filas_por_grupo']['media']} filas/grupo en promedio "
            f"(min {g['filas_por_grupo']['min']}, max {g['filas_por_grupo']['max']})"
        )
    elif not args.group_col:
        lineas.append("Estructura de grupos: no especificada (--group-col no se pasó).")
    else:
        lineas.append(f"Estructura de grupos: columna '{args.group_col}' no encontrada en el archivo.")
    lineas.append(f"Columnas solo en train ({len(solo_train)}): {solo_train}")
    lineas.append(f"Columnas solo en test ({len(solo_test)}): {solo_test}")
    if test is None:
        lineas.append("Test: no se pasó archivo de test.")
    elif test_is_placeholder:
        lineas.append(f"Test es placeholder ({len(test)} filas), no se perfiló.")
    else:
        n_na_test = sum(1 for v in test_perfil["faltantes"].values() if v["n"] > 0)
        lineas.append(
            f"Test perfilado: {test_perfil['n_filas']} filas · {test_perfil['n_columnas']} columnas · "
            f"{n_na_test} columnas con faltantes"
        )
    lineas.append(
        f"Duplicados exactos (excluyendo {len(dup['columnas_excluidas'])} columnas "
        f"identificador {dup['columnas_excluidas']}): {resultado['duplicados_exactos']}"
    )
    lineas.append(f"Columnas constantes: {resultado['constantes']}")

    with open(f"{args.out}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Escrito: {args.out}.json y {args.out}.md")


if __name__ == "__main__":
    main()

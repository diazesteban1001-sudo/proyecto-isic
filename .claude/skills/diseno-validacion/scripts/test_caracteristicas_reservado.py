#!/usr/bin/env python3
"""
test_caracteristicas_reservado.py — control positivo de
cargar_caracteristicas_desarrollo, en datos_desarrollo.py.

El cargador de desarrollo se niega a leer las características del conjunto
reservado, por dos vías independientes: el atributo "conjunto" del archivo y
su contenido. Se fuerza cada caso por separado (corolario de la regla 6), con
archivos sintéticos en un directorio temporal:

  A. Un archivo que declara conjunto = "reservado": falla.
  B. Un archivo sin el atributo "conjunto": falla.
  C. Un archivo que declara "desarrollo" pero contiene un isic_id de un
     paciente reservado: falla. Es el caso que el atributo no atraparía.
  D. Un archivo de desarrollo limpio: se carga, con sus filas intactas.

Y con los archivos reales de data/, si existen:

  E. data/dinov2-vits14-reservado.h5: falla.
  F. data/dinov2-vits14-desarrollo.h5: se carga.

Si los reales no existen —data/ no se versiona—, E y F salen como NO CORRIDO,
a la vista, sin contar como aprobados.

Uso:
    python .claude/skills/diseno-validacion/scripts/test_caracteristicas_reservado.py
Devuelve 0 si todos los casos corridos se comportan como se espera.
"""

import json
import os
import sys
import tempfile

import h5py
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import datos_desarrollo  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", "..", "..", ".."))


def archivo(ruta, ids, conjunto):
    with h5py.File(ruta, "w") as f:
        f.create_dataset("cls", data=np.arange(len(ids) * 4, dtype=np.float32).reshape(len(ids), 4))
        f.create_dataset("isic_id", data=np.array(ids, dtype=object), dtype=h5py.string_dtype("utf-8"))
        f.create_dataset("decodificada", data=np.ones(len(ids), dtype=bool))
        if conjunto is not None:
            f.attrs["conjunto"] = conjunto


def falla_con(fn, texto):
    try:
        fn()
    except SystemExit as e:
        return texto in str(e.code), str(e.code)
    return False, "no falló"


def main():
    casos = []
    with tempfile.TemporaryDirectory() as d:
        csv = os.path.join(d, "metadata.csv")
        pd.DataFrame({"isic_id": [f"ISIC_{i}" for i in range(6)],
                      "patient_id": ["P1", "P1", "P2", "P3", "P3", "P4"]}).to_csv(csv, index=False)
        holdout = os.path.join(d, "holdout.json")
        with open(holdout, "w", encoding="utf-8") as f:
            json.dump({"pacientes_reservados": ["P3"]}, f)
        desarrollo_ids, reservado_ids = ["ISIC_0", "ISIC_1", "ISIC_2", "ISIC_5"], ["ISIC_3", "ISIC_4"]

        cargar = lambda ruta: datos_desarrollo.cargar_caracteristicas_desarrollo(ruta, csv, ruta_holdout=holdout)  # noqa: E731

        archivo(os.path.join(d, "a.h5"), reservado_ids, "reservado")
        casos.append(("A. archivo que declara 'reservado': falla",
                      *falla_con(lambda: cargar(os.path.join(d, "a.h5")), "declara el conjunto 'reservado'")))
        archivo(os.path.join(d, "b.h5"), desarrollo_ids, None)
        casos.append(("B. archivo sin atributo 'conjunto': falla",
                      *falla_con(lambda: cargar(os.path.join(d, "b.h5")), "declara el conjunto None")))
        archivo(os.path.join(d, "c.h5"), desarrollo_ids + ["ISIC_3"], "desarrollo")
        casos.append(("C. declara 'desarrollo' pero trae un paciente reservado: falla por el contenido",
                      *falla_con(lambda: cargar(os.path.join(d, "c.h5")), "1 pacientes del conjunto reservado")))
        archivo(os.path.join(d, "d.h5"), desarrollo_ids, "desarrollo")
        ids, cls, dec = cargar(os.path.join(d, "d.h5"))
        casos.append(("D. archivo de desarrollo limpio: se carga",
                      ids == desarrollo_ids and cls.shape == (4, 4) and bool(dec.all()),
                      f"{len(ids)} filas, cls {cls.shape}"))

    datos = os.path.join(RAIZ, "data")
    csv_real = os.path.join(datos, "train-metadata.csv")
    reservado_real = os.path.join(datos, "dinov2-vits14-reservado.h5")
    desarrollo_real = os.path.join(datos, "dinov2-vits14-desarrollo.h5")
    holdout_real = os.path.join(RAIZ, "outputs", "holdout-pacientes.json")
    if os.path.exists(reservado_real):
        casos.append(("E. el archivo real del reservado: falla",
                      *falla_con(lambda: datos_desarrollo.cargar_caracteristicas_desarrollo(
                          reservado_real, csv_real, ruta_holdout=holdout_real), "declara el conjunto 'reservado'")))
    else:
        casos.append(("E. el archivo real del reservado", None, f"NO CORRIDO: no existe {reservado_real}"))
    if os.path.exists(desarrollo_real):
        ids, cls, dec = datos_desarrollo.cargar_caracteristicas_desarrollo(desarrollo_real, csv_real, ruta_holdout=holdout_real)
        casos.append(("F. el archivo real de desarrollo: se carga", cls.shape == (len(ids), 384),
                      f"{len(ids)} filas, cls {cls.shape}, decodificadas {int(dec.sum())}"))
    else:
        casos.append(("F. el archivo real de desarrollo", None, f"NO CORRIDO: no existe {desarrollo_real}"))

    fallos = corridos = 0
    for titulo, ok, detalle in casos:
        etiqueta = "NO CORRIDO" if ok is None else ("OK" if ok else "FALLA")
        print(f"[{etiqueta}] {titulo}\n      {detalle}")
        if ok is not None:
            corridos += 1
            fallos += not ok
    print(f"\n{corridos - fallos} de {corridos} casos corridos como se esperaba; "
          f"{len(casos) - corridos} no corridos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

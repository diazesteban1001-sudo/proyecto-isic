#!/usr/bin/env python3
"""
inferencia_5b.py — la inferencia de los envíos de la Fase 5b (PLAN.md), la misma
en el Mac y en el notebook de Kaggle, que corre sin internet.

Depende solo de numpy, pandas, scipy, scikit-learn, torch, torchvision, PIL,
h5py y catboost, y de ganador_m3.py, que viaja con ella. Los ajustes viajan en
números (json y npz), no como objetos de scikit-learn serializados, para no
depender de la versión de la librería que tenga Kaggle. Cada pieza reproduce una
del código verificado, y fase5b_paquete.py lo comprueba en el Mac:

- variables_m3: las variables de M3 limpio para filas nuevas, como
  tiempo_inferencia._puntuar_m3limpio, con el one-hot, el estandarizado y el
  k-means del ajuste en números.
- puntuar_cbm: un CatBoost guardado, el de M3 limpio o el de C7.
- recorrer: una sola pasada por las imágenes. Cada recorte se decodifica una vez
  y alimenta a las redes de la 4e, con el preprocesado de
  fase4e.preprocesado_prediccion, y a DINOv2, con el de extraer.preprocesar.
- variables_c7: las dos de imagen de C7, como fase4c.variables_red y
  fase4b.con_imagen, sobre la media de las puntuaciones de las cinco redes.
- puntuar_imagen_basicos: codificar_fold y el pipeline de
  apilado_imagen.modelo_imagen, en números.

No lee etiquetas ni calcula métricas.
"""

import io
import json
import os

import numpy as np
import pandas as pd
from scipy.special import expit

import ganador_m3

G = "patient_id"
LADO_RED = 128  # fase4e.LADO
LOTE = 256  # fase4e.LOTE_PREDICCION
LADO_DINOV2 = 224  # extraer.LADO
LOTE_DINOV2 = 64  # el lote de la extracción
MEDIA = [0.485, 0.456, 0.406]  # prueba_tiempo_red_imagen.MEDIA y extraer.MEDIA, la de ImageNet
DESV = [0.229, 0.224, 0.225]
COLUMNAS_IMAGEN = ["img_lr_puntuacion", "img_lr_razon_paciente"]  # fase4b.COLUMNAS_IMAGEN
REDES_DE_C7 = [f"pliegue-{k}" for k in range(5)]


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def probabilidad(logit):
    """fase4c.probabilidad: la sigmoide del logit, en float64."""
    return expit(np.asarray(logit, dtype=np.float64))


# ---- M3 limpio y C7 -----------------------------------------------------------------------

def cargar_ajuste_m3(directorio):
    return leer_json(os.path.join(directorio, "m3limpio-ajuste.json")), \
        dict(np.load(os.path.join(directorio, "m3limpio-ajuste.npz")))


def conglomerado(escalada, centros):
    """KMeans.predict: el centro más cercano, con ||c||² − 2·x·c, como scikit-learn."""
    d = (centros * centros).sum(axis=1)[None, :] - 2.0 * escalada @ centros.T
    return np.argmin(d, axis=1)


def variables_m3(filas, ajuste):
    """Las variables de M3 limpio de filas nuevas (sin etiqueta), con el ajuste del
    entrenamiento. Lo que va dentro del paciente se calcula con sus propias filas."""
    aj, nz = ajuste
    listas = aj["listas"]
    b = ganador_m3.variables_lectura(filas, listas, G, aj["medianas"])
    cat = aj["categoricas_brutas"]
    texto = filas[cat].astype(object).where(filas[cat].notna(), "").astype(str)
    columnas = [(texto[c].to_numpy() == k).astype(np.int32)
                for c, categorias in zip(cat, aj["categorias_one_hot"]) for k in categorias]
    oh = pd.DataFrame(np.column_stack(columnas), index=filas.index, columns=aj["nombres_one_hot"]).astype("category")
    escalada = (b[listas["top_lof_features"]].to_numpy(dtype=float) - nz["escala_media"]) / nz["escala_escala"]
    b["of"] = ganador_m3.lof_publicado(escalada, filas[G])
    et = conglomerado(escalada, nz["centros"])
    cols = aj["columnas_conglomerado"]
    valores = (b[cols].to_numpy() - nz["media_conglomerado"][et]) / nz["desviacion_conglomerado"][et]
    cl = pd.DataFrame(valores, index=filas.index, columns=[f"{c}__cluster" for c in cols])
    return pd.concat([b, oh, cl], axis=1)[aj["finales"]], et


def puntuar_cbm(ruta, x):
    from catboost import CatBoostClassifier
    modelo = CatBoostClassifier()
    modelo.load_model(ruta)
    return modelo.predict_proba(x)[:, 1]


def variables_c7(x_m3, p_media, grupos):
    """Las variables de C7: las de M3 limpio y, al final, la puntuación de la red y su
    razón a la media del paciente, con las filas de este lado."""
    p = np.asarray(p_media, dtype=np.float64)
    if not np.all(np.isfinite(p)) or np.any(p < 0):
        raise SystemExit("ERROR: hay puntuaciones de la red negativas o faltantes.")
    s = pd.Series(p)
    razon = (s / s.groupby(np.asarray(grupos)).transform("mean")).to_numpy()
    if not np.all(np.isfinite(razon)):
        raise SystemExit("ERROR: un paciente tiene todas sus puntuaciones en 0; su razón no está definida.")
    x = x_m3.copy()
    x[COLUMNAS_IMAGEN[0]] = p
    x[COLUMNAS_IMAGEN[1]] = razon
    return x


# ---- «Imagen + básicos» -------------------------------------------------------------------

def basicos(filas, aj):
    """codificar_fold de los tres básicos, con las medianas y medias del entrenamiento."""
    salida = [filas[c].fillna(aj["medianas"][c]).to_numpy(dtype=float) for c in aj["numericas"]]
    salida += [filas[c].map(aj["medias"][c]).fillna(aj["media_global"]).to_numpy(dtype=float)
               for c in aj["categoricas"]]
    return np.column_stack(salida)


def puntuar_imagen_basicos(filas, dinov2, directorio):
    aj = leer_json(os.path.join(directorio, "imagen-basicos.json"))
    nz = np.load(os.path.join(directorio, "imagen-basicos.npz"))
    x = np.hstack([np.asarray(dinov2, dtype=np.float64), basicos(filas, aj)])
    z = (x - nz["escala_media"]) / nz["escala_escala"]
    return expit(z @ nz["coef"] + nz["intercepto"][0])


# ---- las imágenes: redes de la 4e y DINOv2 --------------------------------------------------

def red(ruta, dispositivo):
    """EfficientNet-B0 de torchvision con la salida de una neurona, sin descargar nada,
    con los pesos ajustados de la Fase 5b."""
    import torch
    from torchvision.models import efficientnet_b0
    modelo = efficientnet_b0(weights=None)
    modelo.classifier[1] = torch.nn.Linear(modelo.classifier[1].in_features, 1)
    modelo.load_state_dict(torch.load(ruta, map_location="cpu"))
    return modelo.eval().to(dispositivo)


def dinov2(ruta_pesos, dispositivo):
    """DINOv2 ViT-S/14 desde el código del repositorio que viaja con el conjunto de
    datos, con sus pesos públicos, sin descargar nada."""
    import torch
    from dinov2.hub import backbones
    modelo = backbones.dinov2_vits14(pretrained=False)
    modelo.load_state_dict(torch.load(ruta_pesos, map_location="cpu"), strict=True)
    return modelo.eval().to(dispositivo)


class Recortes:
    """Los recortes por isic_id: cada uno se decodifica una vez y sale con el
    preprocesado de la red y, si se pide, con el de DINOv2."""

    def __init__(self, hdf5, ids, con_red=True, con_dinov2=False):
        from torchvision import transforms
        self.hdf5, self.ids, self.con_red, self.con_dinov2, self._f = hdf5, list(ids), con_red, con_dinov2, None
        self.t_red = transforms.Compose([transforms.Resize((LADO_RED, LADO_RED)), transforms.ToTensor(),
                                         transforms.Normalize(mean=MEDIA, std=DESV)])

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, i):
        import h5py
        import torch
        from PIL import Image
        if self._f is None:
            self._f = h5py.File(self.hdf5, "r")
        img = Image.open(io.BytesIO(bytes(self._f[self.ids[i]][()]))).convert("RGB")
        salida = {}
        if self.con_red:
            salida["red"] = self.t_red(img)
        if self.con_dinov2:
            x = np.asarray(img.resize((LADO_DINOV2, LADO_DINOV2), Image.BICUBIC), dtype=np.float32) / 255.0
            x = (x - np.array(MEDIA, dtype=np.float32)) / np.array(DESV, dtype=np.float32)
            salida["dino"] = torch.from_numpy(x.transpose(2, 0, 1).copy())
        return salida

    def __getstate__(self):
        d = dict(self.__dict__)
        d["_f"] = None
        return d


def recorrer(hdf5, ids, redes, modelo_dinov2, dispositivo, trabajadores=0):
    """Logits de cada red (dict nombre → float32) y variables de DINOv2 (n × 384), en el
    orden de ids, en una sola pasada por las imágenes."""
    import torch
    ds = Recortes(hdf5, ids, con_red=bool(redes), con_dinov2=modelo_dinov2 is not None)
    carga = torch.utils.data.DataLoader(ds, batch_size=LOTE, shuffle=False, num_workers=trabajadores)
    logits = {k: [] for k in redes}
    caracteristicas = []
    with torch.no_grad():
        for lote in carga:
            if redes:
                x = lote["red"].to(dispositivo)
                for k, m in redes.items():
                    logits[k].append(m(x).squeeze(1).float().cpu())
            if modelo_dinov2 is not None:
                for desde in range(0, len(lote["dino"]), LOTE_DINOV2):
                    xd = lote["dino"][desde:desde + LOTE_DINOV2].to(dispositivo)
                    caracteristicas.append(modelo_dinov2(xd).float().cpu())
    return ({k: torch.cat(v).numpy() for k, v in logits.items()},
            torch.cat(caracteristicas).numpy() if caracteristicas else None)

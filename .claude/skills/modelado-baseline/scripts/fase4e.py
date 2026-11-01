#!/usr/bin/env python3
"""
fase4e.py — las piezas de la red de la Fase 4e (PLAN.md, decisión de la persona
del 2026-10-31): la receta de imagen del 10.º puesto, con el equipo propio. No
corre la fase: prueba_tiempo_red_4e.py la cronometra y test_fase4e_controles.py
controla estas piezas antes de la exploración.

Lo que no se nombra aquí es la red de la Fase 4c: EfficientNet-B0 de torchvision
con los pesos ya verificados (prueba_tiempo_red_imagen.red), lote de 64, float32 y
la predicción sobre todo el pliegue de validación.

- Negativos por época, como el README del autor: los negativos del pliegue de
  entrenamiento se reparten al azar, con la semilla externa, en CONJUNTOS
  conjuntos de tamaño casi igual (conjuntos_de_negativos), y cada época usa uno,
  con todos los positivos. La implementación es nuestra: el código del autor
  hace head(50) por paciente.
- Aumentos: el patrón 2 del autor (aumentos_entrenamiento), con la interpolación
  bilineal de torchvision por defecto; al predecir, redimensionar a LADO y
  normalizar (preprocesado_prediccion), como su valid_transform_p2. Los que se
  aplican con una probabilidad usan transforms.RandomApply, con el generador de
  torch, en lugar de la clase del autor, que usa el módulo random.
- Optimizador y calendario: AdamW con tasa TASA y decaimiento DECAIMIENTO, y
  OneCycle con max_lr=TASA, pct_start=PCT_INICIO, anneal_strategy='cos' y los
  demás argumentos por defecto, un paso por lote; el total de pasos es el de los
  lotes de las épocas.
- EPOCAS épocas fijas; puntúa la red de la última.
- La decodificación y los aumentos van en TRABAJADORES procesos del DataLoader,
  persistentes durante el entrenamiento. Sus semillas salen del generador de la
  semilla externa, así que la red se repite igual con la misma semilla.

autor_p2() reconstruye el patrón 2 del autor desde la cita literal de su código en
la ficha (referencias/tomo20180402-2024-isic2024-10mo-puesto.md), leyéndola con
ast, sin ejecutar su código; describir() resume una transformación para
compararlas.
"""

import ast
import io
import math
import os
import re
import sys
import textwrap
import time

import h5py
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from prueba_tiempo_red_imagen import DESV, MEDIA, red, sha256, sincronizar  # noqa: E402

LADO = 128
LADO_PREVIO = 144
TASA = 5e-4
DECAIMIENTO = 5e-4
PCT_INICIO = 0.1
EPOCAS = 20
CONJUNTOS = 20
LOTE = 64
LOTE_PREDICCION = 256
TRABAJADORES = 6
FICHA = os.path.normpath(os.path.join(AQUI, "..", "..", "..", "..", "referencias",
                                      "tomo20180402-2024-isic2024-10mo-puesto.md"))


def aumentos_entrenamiento():
    """El patrón 2 del autor (scripts/image_dataset.py, líneas 47–57)."""
    return transforms.Compose([
        transforms.Resize((LADO_PREVIO, LADO_PREVIO)),
        transforms.RandomResizedCrop(LADO, scale=(0.8, 1.2), ratio=(0.75, 1.3333)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomApply([transforms.RandomRotation(45)], p=0.5),
        transforms.RandomApply([transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0, hue=0)], p=0.5),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEDIA, std=DESV),
    ])


def preprocesado_prediccion():
    """El valid_transform_p2 del autor (scripts/image_dataset.py, líneas 66–70)."""
    return transforms.Compose([
        transforms.Resize((LADO, LADO)),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEDIA, std=DESV),
    ])


def _valor(v):
    if isinstance(v, (list, tuple)):
        return [_valor(x) for x in v]
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return str(v)


def describir(t):
    """Lista de {nombre, atributos} de una transformación de torchvision, con las
    que van dentro de RandomApply anidadas."""
    pasos = t.transforms if isinstance(t, transforms.Compose) else [t]
    salida = []
    for p in pasos:
        if isinstance(p, transforms.RandomApply):
            salida.append({"nombre": "RandomApply", "p": p.p,
                           "dentro": [d for x in p.transforms for d in describir(x)]})
            continue
        atributos = {k: _valor(v) for k, v in vars(p).items() if not k.startswith("_") and k != "training"}
        salida.append({"nombre": type(p).__name__, **atributos})
    return salida


def _bloque_de_la_ficha(primera_linea):
    texto = open(FICHA, encoding="utf-8").read()
    for b in re.findall(r"```python\n(.*?)\n```", texto, re.S):
        if b.lstrip().startswith(primera_linea):
            return textwrap.dedent(b)
    raise SystemExit(f"ERROR: la ficha no tiene el bloque que empieza por {primera_linea!r}.")


def autor_p2(nombre="train_transform_p2"):
    """El patrón 2 del autor, construido con torchvision desde la cita de su código
    en la ficha: train_transform_p2 o valid_transform_p2. Los argumentos se leen con
    ast.literal_eval; image_size, de la cita de config.py; su RandomApply(t, p) se
    traduce a transforms.RandomApply([t], p)."""
    config = _bloque_de_la_ficha("IMAGE_SIZE")
    lado = int(re.search(r"IMAGE_SIZE = (\d+)", config).group(1))
    arbol = ast.parse(_bloque_de_la_ficha(nombre))

    class Lado(ast.NodeTransformer):
        def visit_Name(self, n):
            return ast.copy_location(ast.Constant(lado), n) if n.id == "image_size" else n
    arbol = Lado().visit(arbol)
    lista = arbol.body[0].value.args[0].elts

    def construir(nodo):
        if isinstance(nodo.func, ast.Name) and nodo.func.id == "RandomApply":
            p = next(ast.literal_eval(k.value) for k in nodo.keywords if k.arg == "p")
            return transforms.RandomApply([construir(nodo.args[0])], p=p)
        nombre = nodo.func.attr
        args = [ast.literal_eval(a) for a in nodo.args]
        kwargs = {k.arg: ast.literal_eval(k.value) for k in nodo.keywords}
        return getattr(transforms, nombre)(*args, **kwargs)
    return transforms.Compose([construir(n) for n in lista])


def conjuntos_de_negativos(neg, n_conjuntos, rng):
    """Los negativos (índices de fila), barajados con rng y repartidos en
    n_conjuntos de tamaño casi igual. Cada negativo queda en uno solo."""
    return np.array_split(rng.permutation(np.asarray(neg)), n_conjuntos)


class Recortes(torch.utils.data.Dataset):
    """Recortes de SLICE-3D por isic_id, decodificados en el proceso que los pide;
    cada proceso abre su propio HDF5."""

    def __init__(self, hdf5, ids, etiquetas, transformacion):
        self.hdf5, self.ids, self.transformacion = hdf5, list(ids), transformacion
        self.etiquetas = np.asarray(etiquetas, dtype=np.float32)
        self._f = None

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, i):
        if self._f is None:
            self._f = h5py.File(self.hdf5, "r")
        img = Image.open(io.BytesIO(bytes(self._f[self.ids[i]][()]))).convert("RGB")
        return self.transformacion(img), self.etiquetas[i]

    def __getstate__(self):
        d = dict(self.__dict__)
        d["_f"] = None
        return d


class OrdenPorEpoca(torch.utils.data.Sampler):
    """Las posiciones de la época vigente, barajadas con (semilla, época)."""

    def __init__(self, por_epoca, semilla):
        self.por_epoca, self.semilla, self.epoca = por_epoca, int(semilla), 0

    def __iter__(self):
        rng = np.random.default_rng([self.semilla, self.epoca])
        return iter(rng.permutation(self.por_epoca[self.epoca]).tolist())

    def __len__(self):
        return len(self.por_epoca[self.epoca])


def cargador(ds, lote, trabajadores, semilla=None, muestreo=None, persistente=False):
    g = None if semilla is None else torch.Generator().manual_seed(int(semilla))
    extra = {"prefetch_factor": 4, "persistent_workers": persistente,
             "multiprocessing_context": "spawn"} if trabajadores else {}
    return torch.utils.data.DataLoader(ds, batch_size=lote, sampler=muestreo, shuffle=False,
                                       num_workers=trabajadores, generator=g, **extra)


def predecir(modelo, hdf5, ids, dispositivo, transformacion=None, trabajadores=TRABAJADORES, semilla=None):
    """El logit, en float32 y en el orden de ids. No lee etiquetas."""
    ds = Recortes(hdf5, ids, np.zeros(len(ids)), transformacion or preprocesado_prediccion())
    modelo.eval()
    salidas = []
    with torch.no_grad():
        for xb, _ in cargador(ds, LOTE_PREDICCION, trabajadores, semilla=semilla):
            salidas.append(modelo(xb.to(dispositivo)).squeeze(1).float().cpu())
    sincronizar()
    return torch.cat(salidas).numpy()


def entrenar_y_puntuar(hdf5, isic, etiquetas, filas_ent, filas_pred, semilla, dispositivo, epocas=EPOCAS,
                       n_conjuntos=CONJUNTOS, parar_tras=None, tasas=False, pesos_en=None,
                       trabajadores=TRABAJADORES, predecir_filas=True):
    """Entrena una red de la 4e con filas_ent (índices sobre isic y etiquetas) y
    devuelve (logit en float32 para filas_pred, en ese orden, o None; registro). Solo
    se leen las etiquetas de filas_ent. parar_tras corta el entrenamiento tras esas
    épocas, con el calendario de todas: solo para la prueba de tiempo. tasas=True
    guarda la tasa de cada paso en el registro."""
    t_inicio = time.perf_counter()
    filas_ent, filas_pred = np.asarray(filas_ent), np.asarray(filas_pred)
    if np.intersect1d(filas_ent, filas_pred).size:
        raise SystemExit("ERROR: la red puntuaría filas con las que se entrena.")
    y_ent = etiquetas[filas_ent]
    pos, neg = filas_ent[y_ent == 1], filas_ent[y_ent == 0]
    if len(pos) == 0 or epocas > n_conjuntos:
        raise SystemExit(f"ERROR: {len(pos)} positivos; {epocas} épocas con {n_conjuntos} conjuntos.")
    rng = np.random.default_rng(semilla)  # el reparto de los negativos
    grupos = conjuntos_de_negativos(neg, n_conjuntos, rng)
    filas_epoca = [np.concatenate([pos, grupos[e]]) for e in range(epocas)]
    universo = np.unique(np.concatenate(filas_epoca))
    por_epoca = [np.searchsorted(universo, fe) for fe in filas_epoca]
    ds = Recortes(hdf5, isic[universo], etiquetas[universo], aumentos_entrenamiento())
    muestreo = OrdenPorEpoca(por_epoca, semilla)
    carga = cargador(ds, LOTE, trabajadores, semilla=semilla, muestreo=muestreo, persistente=trabajadores > 0)

    torch.manual_seed(semilla)  # la capa de salida nueva
    modelo, pesos = red(dispositivo)
    opt = torch.optim.AdamW(modelo.parameters(), lr=TASA, weight_decay=DECAIMIENTO)
    pasos = sum(math.ceil(len(p) / LOTE) for p in por_epoca)
    calendario = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=TASA, total_steps=pasos, pct_start=PCT_INICIO,
                                                     anneal_strategy="cos")
    perdida = torch.nn.BCEWithLogitsLoss()

    lista_tasas, s_epoca, s_espera = [], [], []
    modelo.train()
    for e in range(epocas):
        if parar_tras is not None and e >= parar_tras:
            break
        muestreo.epoca = e
        t0 = time.perf_counter()
        espera = 0.0
        t_pedido = time.perf_counter()
        for xb, yb in carga:
            espera += time.perf_counter() - t_pedido
            xb, yb = xb.to(dispositivo), yb.to(dispositivo)
            opt.zero_grad(set_to_none=True)
            loss = perdida(modelo(xb).squeeze(1), yb)
            loss.backward()
            if tasas:
                lista_tasas.append(opt.param_groups[0]["lr"])
            opt.step()
            calendario.step()
            t_pedido = time.perf_counter()
        sincronizar()
        s_epoca.append(round(time.perf_counter() - t0, 3))
        s_espera.append(round(espera, 3))
    del carga

    sha_pesos = None
    if pesos_en:
        torch.save(modelo.state_dict(), pesos_en)
        sha_pesos = sha256(pesos_en)
    t0 = time.perf_counter()
    logit = predecir(modelo, hdf5, isic[filas_pred], dispositivo, trabajadores=trabajadores) if predecir_filas \
        else None
    s_pred = round(time.perf_counter() - t0, 3)
    del modelo, opt
    torch.mps.empty_cache()
    tamanos = [len(g) for g in grupos]
    registro = {
        "semilla": int(semilla), "positivos": int(len(pos)), "negativos": "conjuntos", "conjuntos": int(n_conjuntos),
        "tamano_de_los_conjuntos": {"minimo": int(min(tamanos)), "maximo": int(max(tamanos))},
        "negativos_del_pliegue": int(len(neg)),
        "negativos_en_mas_de_una_epoca": int(len(np.concatenate(grupos[:epocas])) -
                                             len(np.unique(np.concatenate(grupos[:epocas])))),
        "imagenes_por_epoca": [int(len(p)) for p in por_epoca], "epocas": int(epocas),
        "epocas_corridas": len(s_epoca), "pasos_del_calendario": int(pasos), "trabajadores": int(trabajadores),
        "filas_puntuadas": int(len(filas_pred)) if predecir_filas else 0,
        "segundos_por_epoca": s_epoca, "segundos_esperando_datos_por_epoca": s_espera,
        "segundos_prediccion": s_pred, "segundos_total": round(time.perf_counter() - t_inicio, 3),
        "sha256_pesos_imagenet": pesos["sha256"], "pesos_guardados": pesos_en, "sha256_pesos_guardados": sha_pesos,
    }
    if tasas:
        registro["tasas"] = lista_tasas
    return logit, registro

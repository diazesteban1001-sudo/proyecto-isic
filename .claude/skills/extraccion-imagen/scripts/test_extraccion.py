#!/usr/bin/env python3
"""
test_extraccion.py — auditoría de extraer.py con casos sintéticos.

Cubre lo que la evidencia que ya existe no cubre. Las salidas de la Fase 4
comprueban, sobre los archivos reales, el hash, los isic_id, los NaN, el orden
y 1.000 filas al azar; el control de tiempo-inferencia.json recalcula DINOv2
y queda a 0,0 del archivo. Pero en la extracción real no falló ninguna imagen,
no faltó ningún isic_id ni hubo duplicados, y el control de tiempo usa el mismo
extraer.preprocesar que produjo el archivo, así que no prueba que el
preprocesado sea el que fija SKILL.md.

Casos, con imágenes sintéticas en un HDF5 temporal y un modelo falso en CPU
(una función fija de la imagen), salvo F:

  A. Una imagen que no decodifica, en mitad de un lote: queda en «fallidas»
     con su error, su fila va en NaN y con decodificada = false, y las demás
     filas llevan las características de su propia imagen, sin corrimiento.
  B. Un isic_id del CSV que falta en el HDF5: no se escribe para él ninguna
     característica. O la extracción se detiene o lo registra como fallida.
  C. Un isic_id duplicado: hay una fila por cada aparición, cada una con las
     características de su imagen; no se pierde ni se fusiona ninguna.
  D. Filas en otro orden: con el CSV barajado, la fila i del archivo escrito
     tiene el i-ésimo isic_id del CSV y las características de su imagen.
  E. El preprocesado es el que fija SKILL.md: igual, a 1e-5, a la cadena de
     torchvision con las constantes de dinov2/data/transforms.py: bicúbica a
     224 × 224 sin recorte, ToTensor y Normalize. Con una imagen no cuadrada.
  F. La característica es x_norm_clstoken: con el modelo real, en CPU,
     forward en inferencia devuelve exactamente forward_features(x)["x_norm_clstoken"].
     Necesita la copia local del repositorio y los pesos con el SHA-256 fijado;
     si faltan, sale como NO CORRIDO, a la vista.

Cada caso se corre también contra un mutante de extraer.py con un defecto
plantado (sustitución de texto en el código, que exige una coincidencia
exacta), y tiene que FALLAR contra él. Si el mutante no lo hace fallar, el
caso no sirve y la prueba falla. En F, la comparación contra x_prenorm, el
token CLS sin la normalización final, tiene que dar distinto.

Uso:
    .venv/bin/python .claude/skills/extraccion-imagen/scripts/test_extraccion.py
Devuelve 0 si todos los casos corridos se comportan como se espera.
"""

import io
import os
import sys
import tempfile
import types

import h5py
import numpy as np
import torch
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
RUTA_EXTRAER = os.path.join(AQUI, "extraer.py")
REPO_DINOV2 = os.path.join(RAIZ, "data", "dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8")
CPU = torch.device("cpu")


def cargar_modulo(sustituciones=()):
    """extraer.py tal cual, o un mutante con las sustituciones dadas. Cada
    texto viejo tiene que aparecer exactamente una vez: si el código cambia,
    el mutante deja de existir y la prueba lo dice, en vez de pasar sin él."""
    with open(RUTA_EXTRAER, encoding="utf-8") as f:
        fuente = f.read()
    for viejo, nuevo in sustituciones:
        if fuente.count(viejo) != 1:
            raise SystemExit(f"ERROR: el mutante no aplica; el código cambió: {viejo!r}")
        fuente = fuente.replace(viejo, nuevo)
    modulo = types.ModuleType("extraer_bajo_prueba")
    modulo.__file__ = RUTA_EXTRAER
    exec(compile(fuente, RUTA_EXTRAER, "exec"), modulo.__dict__)
    return modulo


def jpeg(semilla, ancho=40, alto=40):
    """Una imagen JPEG de ruido, distinta para cada semilla."""
    rng = np.random.default_rng(semilla)
    img = Image.fromarray(rng.integers(0, 256, size=(alto, ancho, 3), dtype=np.uint8), "RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


class ModeloFalso:
    """Una función fija de la imagen preprocesada, con salida de 384: media por
    canal en una rejilla de 8 × 8 (192 valores), proyectada con una matriz fija."""
    def __init__(self):
        self.w = torch.from_numpy(np.random.default_rng(7).normal(size=(192, 384)).astype(np.float32))

    def __call__(self, x):
        p = torch.nn.functional.adaptive_avg_pool2d(x, 8).reshape(x.shape[0], -1)
        return p @ self.w


def hdf5_de_imagenes(ruta, crudos):
    """El mismo formato que data/train-image.hdf5: un conjunto de datos por
    isic_id, con los bytes del JPEG como cadena de longitud fija."""
    with h5py.File(ruta, "w") as f:
        for isic_id, b in crudos.items():
            f.create_dataset(isic_id, data=np.bytes_(b))


def esperada(ex, modelo, b):
    """Las características de una imagen extraída sola, fuera del lote."""
    x, _ = ex.preprocesar(b)
    return modelo(torch.from_numpy(x[None])).numpy()[0]


def extraer_y_escribir(ex, d, ids, crudos, lote, nombre="desarrollo"):
    """extraer_conjunto + escribir, como en main(), y relee el archivo."""
    ruta_img = os.path.join(d, f"imagenes-{len(os.listdir(d))}.h5")
    hdf5_de_imagenes(ruta_img, crudos)
    ruta_out = os.path.join(d, f"caract-{len(os.listdir(d))}.h5")
    with h5py.File(ruta_img, "r") as imagenes:
        cls, dec, fallidas, _, _ = ex.extraer_conjunto(nombre, ids, imagenes, ModeloFalso(), CPU, lote)
    ex.escribir(ruta_out, nombre, ids, cls, dec, "commit-de-prueba")
    with h5py.File(ruta_out, "r") as f:
        return f["isic_id"].asstr()[:].tolist(), f["cls"][:], f["decodificada"][:], fallidas, dict(f.attrs)


# --- los casos: cada uno devuelve (ok, detalle) para un módulo dado ----------

def caso_a(ex, d):
    ids = [f"ISIC_{i}" for i in range(7)]
    crudos = {i: jpeg(k) for k, i in enumerate(ids)}
    crudos["ISIC_2"] = b"esto no es un JPEG"
    leidos, cls, dec, fallidas, attrs = extraer_y_escribir(ex, d, ids, crudos, lote=4)
    modelo = ModeloFalso()
    buenas_ok = all(np.allclose(cls[k], esperada(ex, modelo, crudos[i]), atol=1e-5)
                    for k, i in enumerate(ids) if i != "ISIC_2")
    ok = (leidos == ids and np.isnan(cls[2]).all() and not dec[2] and dec.sum() == 6
          and [f["isic_id"] for f in fallidas] == ["ISIC_2"] and fallidas[0]["error"] and buenas_ok
          and attrs.get("conjunto") == "desarrollo")
    return ok, (f"fallidas {[f['isic_id'] for f in fallidas]}, decodificadas {int(dec.sum())} de 7, "
                f"fila 2 en NaN: {bool(np.isnan(cls[2]).all())}, demás filas con su imagen: {buenas_ok}")


def caso_b(ex, d):
    ids = [f"ISIC_{i}" for i in range(5)]
    crudos = {i: jpeg(k) for k, i in enumerate(ids) if i != "ISIC_3"}
    try:
        leidos, cls, dec, fallidas, _ = extraer_y_escribir(ex, d, ids, crudos, lote=2)
    except KeyError as e:
        return True, f"se detiene con KeyError {e}; no escribe ningún archivo"
    registrada = "ISIC_3" in [f["isic_id"] for f in fallidas] and np.isnan(cls[3]).all() and not dec[3]
    return bool(registrada), ("la registra como fallida" if registrada
                              else f"escribe características para ISIC_3 sin imagen: decodificada={bool(dec[3])}")


def caso_c(ex, d):
    ids = ["ISIC_0", "ISIC_1", "ISIC_0", "ISIC_2"]
    crudos = {i: jpeg(k) for k, i in enumerate(dict.fromkeys(ids))}
    leidos, cls, dec, fallidas, _ = extraer_y_escribir(ex, d, ids, crudos, lote=3)
    modelo = ModeloFalso()
    ok = (leidos == ids and cls.shape[0] == 4 and dec.all()
          and all(np.allclose(cls[k], esperada(ex, modelo, crudos[i]), atol=1e-5) for k, i in enumerate(leidos)))
    return ok, f"filas {cls.shape[0]} para 4 apariciones; isic_id escritos {leidos}"


def caso_d(ex, d):
    base = [f"ISIC_{i}" for i in range(9)]
    crudos = {i: jpeg(k) for k, i in enumerate(base)}
    crudos["ISIC_4"] = b"roto"  # una fallida en mitad, para que el orden y las posiciones se crucen
    ids = [base[k] for k in np.random.default_rng(3).permutation(len(base))]
    leidos, cls, dec, _, _ = extraer_y_escribir(ex, d, ids, crudos, lote=4)
    modelo = ModeloFalso()
    filas_ok = all((np.isnan(cls[k]).all() and not dec[k]) if i == "ISIC_4"
                   else np.allclose(cls[k], esperada(ex, modelo, crudos[i]), atol=1e-5)
                   for k, i in enumerate(leidos))
    return (leidos == ids and filas_ok), f"orden del CSV conservado: {leidos == ids}; cada fila con su imagen: {filas_ok}"


def caso_e(ex, d):
    sys.path.insert(0, REPO_DINOV2)
    try:
        from dinov2.data.transforms import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD
        origen = "dinov2/data/transforms.py"
    except ImportError:
        IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
        origen = "constantes escritas aquí (sin la copia local de dinov2)"
    from torchvision import transforms
    cadena = transforms.Compose([
        transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD),
    ])
    b = jpeg(11, ancho=137, alto=90)
    x, cuadrada = ex.preprocesar(b)
    ref = cadena(Image.open(io.BytesIO(b)).convert("RGB")).numpy()
    dif = float(np.abs(x - ref).max()) if x.shape == ref.shape else float("inf")
    return (x.shape == (3, 224, 224) and not cuadrada and dif <= 1e-5), \
        f"forma {x.shape}, diferencia máxima con la cadena de referencia {dif:.2e} (constantes: {origen})"


CASOS = [
    ("A. imagen que no decodifica, en mitad de un lote", caso_a,
     [("cls[buenas] = salida", "cls[list(posiciones)[:len(buenas)]] = salida")],
     "las salidas se asignan a las primeras posiciones del lote, no a las buenas"),
    ("B. isic_id del CSV que falta en el HDF5", caso_b,
     [("crudos = [bytes(imagenes[ids[i]][()]) for i in posiciones]",
       "crudos = [bytes(imagenes[ids[i] if ids[i] in imagenes else ids[0]][()]) for i in posiciones]")],
     "un isic_id ausente toma en silencio la imagen de otro"),
    ("C. isic_id duplicado", caso_c,
     [("    n = len(ids)\n", "    ids = list(dict.fromkeys(ids))\n    n = len(ids)\n")],
     "la extracción quita los duplicados en silencio"),
    ("D. filas del CSV en otro orden", caso_d,
     [("    n = len(ids)\n", "    ids = sorted(ids)\n    n = len(ids)\n")],
     "la extracción ordena los isic_id y desalinea las filas"),
    ("E. preprocesado igual al que fija SKILL.md", caso_e,
     [("img = img.resize((LADO, LADO), Image.BICUBIC)", "img = img.resize((LADO, LADO), Image.BILINEAR)")],
     "interpolación bilineal en vez de bicúbica"),
]


def caso_f():
    """El modelo real en CPU: forward en inferencia == x_norm_clstoken."""
    ex = cargar_modulo()
    ruta_pesos = os.path.join(torch.hub.get_dir(), "checkpoints", ex.PESOS)
    if not os.path.isdir(REPO_DINOV2):
        return None, f"NO CORRIDO: no existe {REPO_DINOV2}"
    if not os.path.exists(ruta_pesos) or ex.sha256(ruta_pesos) != ex.PESOS_SHA256:
        return None, f"NO CORRIDO: {ruta_pesos} no existe o su SHA-256 no es el fijado"
    sys.path.insert(0, REPO_DINOV2)
    from dinov2.hub import backbones
    modelo = getattr(backbones, ex.MODELO)(pretrained=True).eval()
    x = torch.from_numpy(np.stack([ex.preprocesar(jpeg(s, 60, 45))[0] for s in (1, 2)]))
    with torch.no_grad():
        salida = modelo(x)
        f = modelo.forward_features(x)
    igual = torch.equal(salida, f["x_norm_clstoken"])
    discrimina = not torch.allclose(salida, f["x_prenorm"][:, 0], atol=1e-3)
    return (igual and discrimina and tuple(salida.shape) == (2, 384)), \
        (f"salida {tuple(salida.shape)}; idéntica a x_norm_clstoken: {igual}; "
         f"distinta del CLS sin normalizar (x_prenorm), como debe: {discrimina}")


def main():
    resultados = []
    original = cargar_modulo()
    with tempfile.TemporaryDirectory() as d:
        for titulo, caso, mutacion, que_rompe in CASOS:
            ok, detalle = caso(original, d)
            mutante = cargar_modulo(mutacion)
            try:
                ok_mut, det_mut = caso(mutante, d)
            except Exception as e:  # noqa: BLE001 — un mutante que revienta también cuenta como detectado
                ok_mut, det_mut = False, f"{type(e).__name__}: {e}"
            resultados.append((titulo, ok and not ok_mut,
                               f"tal cual: {'pasa' if ok else 'FALLA'} — {detalle}\n"
                               f"      mutante ({que_rompe}): {'FALLA, como debe' if not ok_mut else 'PASA: el caso no discrimina'} — {det_mut}"))
    ok_f, det_f = caso_f()
    resultados.append(("F. la característica es x_norm_clstoken (modelo real, CPU)", ok_f, det_f))

    fallos = corridos = 0
    for titulo, ok, detalle in resultados:
        etiqueta = "NO CORRIDO" if ok is None else ("OK" if ok else "FALLA")
        print(f"[{etiqueta}] {titulo}\n      {detalle}")
        if ok is not None:
            corridos += 1
            fallos += not ok
    print(f"\n{corridos - fallos} de {corridos} casos corridos como se esperaba; {len(resultados) - corridos} no corridos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

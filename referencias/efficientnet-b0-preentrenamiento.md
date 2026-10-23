# EfficientNet-B0 de torchvision — de dónde salen sus pesos (FICHA)

**Qué es:** las fuentes con que se comprueba el preentrenamiento de
EfficientNet-B0, la red pequeña de la prueba de tiempo de redes de imagen
entrenadas sobre los recortes (`outputs/prueba-tiempo-red-imagen.json`). La regla
es la de la Fase 2 de `PLAN.md`. Son tres fuentes: el artículo original, el código
de torchvision que declara los pesos y la cabecera del archivo de pesos.
**Fecha de consulta:** 2026-10-22, antes de descargar los pesos.

## 1. El artículo: Tan y Le (2019)

**Título:** *"EfficientNet: Rethinking Model Scaling for Convolutional Neural
Networks"*. **Autores:** Mingxing Tan y Quoc V. Le. **Dónde:** arXiv:1905.11946.
Historial de envíos de la página de arXiv: **v1 del 28 de mayo de 2019**; la v5,
del 11 de septiembre de 2020, es la última.
**URL:** https://arxiv.org/abs/1905.11946 y el PDF de la v1,
https://arxiv.org/pdf/1905.11946v1.

**LICENCIA: con copyright → FICHA.** La página de arXiv enlaza la **licencia no
exclusiva de distribución de arXiv 1.0**
(`http://arxiv.org/licenses/nonexclusive-distrib/1.0/`), que autoriza a arXiv a
distribuir, no a terceros. Por la regla 3 de `CLAUDE.md` va a ficha.

**Texto completo:** en local, en `referencias/_texto-completo/`:
- `tan-le-2019-efficientnet-abs.html`, la página de arXiv, SHA-256
  `7067ab18452b359bc1c38d448aba723f8f676267daa93f1f9b1d433f9223968c`;
- `tan-le-2019-efficientnet-v1.pdf`, el PDF de la v1, 921.834 bytes, SHA-256
  `c74eb39a6142d448dc61c7ccb9afb1170f5a0509c0a02566f523ce56893bf80f`, y su
  texto extraído con pypdf, `tan-le-2019-efficientnet-v1.txt`.

**Citas que el proyecto usa**, comprobadas carácter a carácter el 2026-10-22:
- El título, de las etiquetas `citation_title` de la página de arXiv:
  > EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks
- La afiliación de los dos autores, nota 1 de la primera página del PDF:
  > Google Research, Brain Team, Mountain View, CA
- Los datos de entrenamiento, sección 5.2 del PDF:
  > We train our EfficientNet models on ImageNet

  En el texto extraído del PDF, *"EfficientNet"* lleva la ligadura `ﬁ`
  (U+FB01). Sin ella, la cita coincide carácter a carácter.

## 2. El código de torchvision que declara los pesos

**Dónde:** `torchvision/models/efficientnet.py` de **torchvision 0.29.0**, la del
`.venv` (`requirements.txt`), clase `EfficientNet_B0_Weights`, peso
`IMAGENET1K_V1`. **LICENCIA:** BSD 3-Clause (`LICENSE` y `License: BSD` en el
`METADATA` del paquete instalado).

**Citas, del archivo instalado:**
- Línea 442:
  > # Weights ported from https://github.com/rwightman/pytorch-image-models/
- Línea 458:
  > "_docs": """These weights are ported from the original paper.""",
- Sus métricas declaradas son de *ImageNet-1K*, y el peso trae las 1.000
  categorías de ImageNet (`meta["categories"]`).
- El archivo es
  `https://download.pytorch.org/models/efficientnet_b0_rwightman-7f5810bc.pth`.

## 3. La cabecera del archivo de pesos

Pedida el 2026-10-22 con `curl -sI`, sin descargar el archivo:

> last-modified: Tue, 10 Oct 2023 11:32:27 GMT

> content-length: 21444401

Es la fecha en que el servidor modificó el archivo por última vez: el contenido
existía a más tardar ese día. No dice cuándo se entrenó.

**El archivo descargado**, después de esta comprobación, el 2026-10-22, con
`curl` a la caché de torch: desde el Python del `.venv` la verificación TLS
fallaba por falta de certificados raíz, y no se desactivó. Tiene 21.444.401
bytes, como la cabecera, y SHA-256
`7f5810bc96def8f7552d5b7e68d53c4786f81167d28291b21c0d90e1fca14934`, que empieza
por el `7f5810bc` del nombre del archivo.

## Lo que es nuestro: la regla de la Fase 2 aplicada

La regla (`PLAN.md`, Fase 2, decisión del 2026-09-24) tiene dos casos. El que se
mira es el primero: pesos o datos de preentrenamiento anteriores a la primera
fecha pública de SLICE-3D, y autores que no pertenezcan a las instituciones que
aportaron los datos.

- **Fechas.** El artículo, de mayo de 2019, entrena sobre ImageNet, así que esos
  datos son anteriores a mayo de 2019. torchvision declara que los pesos son
  los del artículo, portados. El archivo existía con su contenido actual el 10
  de octubre de 2023. Ninguna fuente fija la primera fecha pública de SLICE-3D.
  La cadena de evidencia concluye que los datos se aportaron después de que el
  proyecto se presentara en la EADV, del 11 al 14 de octubre de 2023, y que el
  conjunto completo no estaba terminado antes de 2024
  (`referencias/slice3d-fechas-de-publicacion.md`, sección 5). Las tres fechas
  son anteriores.
- **Autores.** Google Research, Brain Team. No está entre las siete
  instituciones que aportaron SLICE-3D ni entre las dos que solo aportaron a la
  prueba del reto (`referencias/kurtansky-2024-slice3d-descriptor.md`, líneas
  134 y 320).

**Salvedades.**
- Quien portó los pesos, el repositorio pytorch-image-models, no se ha
  examinado. Lo que dice que el contenido es el del artículo es torchvision.
- La fecha del archivo queda un día antes del congreso. Es una fecha de
  servidor, y el orden frente a SLICE-3D sale de la cadena de evidencia, que es
  inferencia nuestra, no de una fecha fijada.
- La cadena de evidencia no excluye que alguna imagen original de SLICE-3D
  fuera pública antes por otra vía (misma sección 5).

Con eso, EfficientNet-B0 cumple el caso 1. Es una lectura para la prueba de
tiempo: usarla en una fase es decisión de la persona.

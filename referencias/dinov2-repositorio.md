# DINOv2 — documentación de los puntos de control (repositorio oficial)

**Fuente:** repositorio *dinov2* de Meta AI Research,
https://github.com/facebookresearch/dinov2
**Commit:** `7764ea0f912e53c92e82eb78a2a1631e92725fc8` (rama `main`, 2026-06-03,
asunto *"Safely load weights from specified URLs (#598)"*). Es el `HEAD` remoto de
`main` consultado en `api.github.com` el 2026-09-25. *Este hash es el dato que
identifica la versión copiada, no un puntero a la historia de este repositorio
(regla 6, la excepción): no se actualiza.*
**Fecha de consulta:** 2026-09-25. Cada URL respondió 200 antes de descargar
nada; los archivos se bajaron con `curl` desde `raw.githubusercontent.com` en ese
commit.
**Para qué está aquí:** la condición de la decisión de la Fase 2 (`PLAN.md`):
el punto de control de DINOv2 que se use tiene que documentar LVD-142M como sus
datos de entrenamiento. Los candidatos son ViT-S/14 y ViT-B/14, sin registros.

**LICENCIA: Apache License 2.0 → COPIA EXACTA.** Determinada por dos vías, el
2026-09-25:
- el archivo `LICENSE` del repositorio es, con los espacios normalizados,
  idéntico al texto canónico de https://www.apache.org/licenses/LICENSE-2.0.txt;
- la API de GitHub detecta `Apache-2.0` (`spdx_id`) en `LICENSE`.

El propio README dice *"DINOv2 code and model weights are released under the
Apache License 2.0."*. El repositorio no tiene archivo `NOTICE`. Como pide la
regla 3 para Apache 2.0, los tres archivos se versionan **byte a byte** en
`referencias/dinov2-repositorio/`, sin cabecera, y la procedencia va en este
archivo.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `README.md` | 32.799 | `d1bc2e9686522bbd66ed6123dc81eb36b3a98e8ea9a2ca97778f54a1c641c9e1` |
| `MODEL_CARD.md` | 9.152 | `70ca59606bee0a5fbb1baec80e7e29a93cd7cfbe26ca1910c52a852c4aab09d0` |
| `LICENSE` | 11.359 | `600cc67cc4cb2f5ea317dcfc687ad1c74dc4bec8782bbe9db0afd83513b935b7` |

---

## Lo que documenta

`MODEL_CARD.md` cubre los modelos S, B, L y g:

> # Model Card for DINOv2-S/B/L/g

> - 1 ViT-g trained from scratch with 3 ViT-S/B/L models distilled from the ViT-g, without registers.

Y sus datos de entrenamiento, sección *"Training Data"*:

> - **Training data:** LVD-142M (see paper)

El README enlaza los pesos de los dos candidatos, en la tabla de modelos, filas
*"ViT-S/14 distilled"* y *"ViT-B/14 distilled"* sin registros:

> https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth

> https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/dinov2_vitb14_pretrain.pth

**Los dos candidatos cumplen la condición:** su documentación oficial da LVD-142M
como datos de entrenamiento. Los pesos que se usen son esos dos archivos.

Las dos URL respondieron 200 el 2026-09-25, con estos datos de la cabecera HTTP:

| Archivo | `content-length` | `last-modified` |
|---|---|---|
| `dinov2_vits14_pretrain.pth` | 88.283.115 | Thu, 13 Apr 2023 22:01:20 GMT |
| `dinov2_vitb14_pretrain.pth` | 346.378.731 | Thu, 13 Apr 2023 22:01:34 GMT |

*Nuestro.* `last-modified` es lo que declara el servidor sobre el archivo que
sirve hoy, no documentación del modelo: fecha la última subida, no el
entrenamiento.

## Las copias de Hugging Face no cumplen la condición

Las fichas de `facebook/dinov2-small` y `facebook/dinov2-base` en Hugging Face
no nombran LVD-142M. Dicen, las dos:

> pretrained on a large collection of images in a self-supervised fashion

Copias locales: `referencias/_texto-completo/hf-facebook-dinov2-small-README.md` y
`hf-facebook-dinov2-base-README.md`, bajadas de
`https://huggingface.co/facebook/dinov2-{small,base}/raw/main/README.md`. Su
licencia declarada, `apache-2.0`, es la del modelo; que cubra el texto de la
ficha es lectura nuestra, así que van a local y aquí solo la cita. Por la
condición de la Fase 2, **esos puntos de control no se usan**: se usan los del
repositorio oficial.

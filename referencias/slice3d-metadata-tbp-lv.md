# Definición de las columnas `tbp_lv_*` — paper SLICE-3D

**Fuente:** Kurtansky NR et al., *"The SLICE-3D dataset: 400,000 skin lesion
image crops extracted from 3D TBP for skin cancer detection"*, Scientific Data
(2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/

**Fecha de consulta:** 2026-08-11
**Consultado por:** el agente, vía WebFetch sobre la versión de PMC (el paper es
de acceso abierto y sí es legible sin sesión, a diferencia de Kaggle).

Este archivo existe para que las afirmaciones sobre el origen de las columnas
`tbp_lv_*` sean trazables a un archivo del repositorio y no a la memoria del
agente, siguiendo la regla 3 de `CLAUDE.md`.

---

## Qué significa el prefijo `lv`

Nota al pie de la Tabla 1 del paper:

> "*Canfield Scientific, Inc. Lesion Visualizer metric."

`lv` = **Lesion Visualizer**, herramienta de Canfield Scientific que acompaña al
sistema de fotografía corporal total 3D. El paper la describe en Métodos como un
conjunto de algoritmos de IA que localizan lesiones automáticamente a lo largo
de la captura 3D TBP.

Sobre cómo se identifican las lesiones:

> "Hence, lesions are identified in one of two ways; (1) manual lesion tagging
> performed by the human... (2) automated lesion detection performed by the LV."

Es decir: las métricas `tbp_lv_*` las **computa el software de imagen sobre la
captura fotográfica**, no un patólogo sobre una biopsia.

## `tbp_lv_nevi_confidence` — definición literal (Tabla 1)

> "Nevus confidence score (0–100 scale) is a convolutional neural network
> classifier estimated probability that the lesion is a nevus. The neural network
> was trained on approximately 57,000 lesions that were classified and labeled by
> a dermatologist."

## `tbp_lv_dnn_lesion_confidence` — definición literal (Tabla 1)

> "Lesion confidence score (0–100 scale)."

La Tabla 1 no explica más. Nota operativa: esta columna **no está en
`test-metadata.csv`** (una de las 11 exclusivas de train), así que su origen es
irrelevante para el modelado — no está disponible en inferencia.

## Otras `tbp_lv_*` representativas (Tabla 1)

| Columna | Definición literal |
|---|---|
| `tbp_lv_H` | "Hue inside the lesion; calculated as the angle of A* and B* in L*A*B* color space. Typical values range from 25 (red) to 75 (brown)" |
| `tbp_lv_deltaB` | "Average L,A,B contrast (inside lesion vs. outside lesion)." |
| `tbp_lv_norm_color` | "Color variation (0–10 scale); the normalized average of color asymmetry and color irregularity." |
| `tbp_lv_symm_2axis` | "Border asymmetry" (escala 0–10) |

Todas son mediciones geométricas y colorimétricas derivadas de la imagen.

---

## Lo que el paper NO dice — dos límites de esta verificación

1. **No hay una frase explícita sobre el momento de cómputo respecto de la
   biopsia.** Que las `tbp_lv_*` sean previas al diagnóstico se deduce de la
   construcción del dataset, no de una afirmación directa: son métricas que el
   Lesion Visualizer calcula sobre la captura 3D, y los positivos se definen
   como lesiones diagnosticadas *dentro de los 3 meses posteriores* a esa
   captura. La captura precede al diagnóstico; las métricas derivan de la
   captura.

2. **No se dice si las ~57.000 lesiones con que se entrenó el clasificador de
   nevus se solapan con SLICE-3D.** Si se solaparan, `tbp_lv_nevi_confidence`
   incorporaría de forma indirecta etiquetas de dermatólogo sobre las mismas
   lesiones del dataset. No es verificable con el paper. Es una limitación para
   el informe, no un motivo para excluir la columna: el score está disponible en
   test, o sea que es computable en inferencia real, que es el criterio que
   importa para decidir si una variable es usable.

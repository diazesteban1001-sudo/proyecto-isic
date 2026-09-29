# Correcciones propuestas al anteproyecto

Qué es: las dos frases del anteproyecto que la tabla de trazabilidad
(`trazabilidad-borrador.csv`) dejó en PARCIAL porque su fuente no sostenía una
parte. Para cada una se da la frase literal, qué dice la fuente y la
corrección que se propone. **El anteproyecto no se ha tocado.** 2026-09-29.

**Resultado de la revisión, que corrige un aviso anterior.** Las dos frases se
habían señalado como frases que «dicen más que su fuente». Leídas contra las
fuentes completas, no es así:
- **Marchetti (2.1):** la frase dice más que el resumen de Marchetti, pero casi
  todo lo que dice lo sostiene Kurtansky et al. (2025). Solo el final es
  inferencia. Hace falta corregir la atribución.
- **Yang (2.2):** la frase no dice más que su fuente. El resumen publicado dice
  lo que se le atribuye. Lo que faltaba era la cita en la ficha, no una
  corrección en el anteproyecto.

El aviso anterior juzgó las dos frases contra lo versionado: el resumen de
Marchetti y la ficha de Yang, que es un extracto. De ahí concluyó que la fuente
no lo decía. Es la octava clase del registro de incidentes (`CLAUDE.md`, regla
6): una afirmación de ausencia sacada de una búsqueda incompleta.

## 1. Marchetti et al. (2023), sección 2.1

**Frase literal:**

> En este dominio concreto, los organizadores señalan que existe **un único
> estudio previo publicado** (Kurtansky et al., 2025): Marchetti et al. (2023)
> ajustaron un modelo de regresión multivariado sobre medidas morfológicas que
> el propio sistema de captura extrae de cada lesión —tamaño, variación de
> color, irregularidad del borde—, sin usar las imágenes ni redes neuronales.

**Qué dice la fuente.**
- **El resumen de Marchetti et al. (2023)**, en la copia local
  `referencias/_texto-completo/marchetti-2023-resumen-pubmed.txt`. Es lo único
  accesible del artículo.
  - *"Automated data from image processing (i.e. lesion size, colour, border)
    for all eligible participants were exported from VECTRA DermaGraphix
    research software for analysis."*
  - *"The AUC for the prediction model was 0.94 (95% CI: 0.92-0.96)."*

  No dice que el modelo sea de regresión ni multivariado. Tampoco dice que no
  use las imágenes ni redes neuronales.
- **Kurtansky et al. (2025)**, en `referencias/kurtansky-2025-triaje-automatizado-tbp.md`, describen el modelo:
  - *"The statistical model by Marchetti et al.27 was used as a benchmark of
    diagnostic performance. Their multivariate model used 11 morphological WB360
    measurements"*
  - *"reported that regression models could use WB360-measurments extracted from
    lesion tiles, like color variation, size, and border irregularity"*
  - *"the potential of higher-capacity ML-models over generalized linear models"*
- **Ninguna de las dos fuentes dice «sin usar las imágenes ni redes
  neuronales».** Se infiere de que el modelo sea un modelo lineal generalizado
  sobre medidas extraídas, pero no está escrito.

**Qué hay que corregir.**
- La descripción del modelo se atribuye a Marchetti et al. (2023), cuyo resumen
  no la da. La fuente que la sostiene es Kurtansky et al. (2025).
- «Sin usar las imágenes ni redes neuronales» se presenta como un hecho y es
  una inferencia.

**Corrección propuesta:**

> En este dominio concreto, los organizadores señalan que existe **un único
> estudio previo publicado**, el de Marchetti et al. (2023), y describen su
> modelo como un modelo estadístico multivariado sobre 11 medidas morfológicas
> que el propio sistema de captura extrae de cada lesión —entre ellas el
> tamaño, la variación de color y la irregularidad del borde—, un modelo
> lineal generalizado frente a los modelos de aprendizaje automático de mayor
> capacidad de la competencia (Kurtansky et al., 2025).

**Efecto en la trazabilidad.** La fila de Kurtansky et al. (2025) para esta
frase puede añadir las tres citas de arriba. La fila de Marchetti queda como
está: su resumen no sostiene la descripción.

## 2. Yang et al. (2019), sección 2.2

**Frase literal:**

> Yang et al. (2019) proponen el área parcial de dos vías, que restringe
> simultáneamente la sensibilidad y la tasa de falsos positivos, y objetan a
> los enfoques que fijan un límite artificial sobre un eje para controlar el
> otro de forma indirecta; ese control indirecto sobre la sensibilidad es, en
> sus palabras, «conceptually and practically misleading» (Yang et al., 2019).

**Qué dice la fuente.** El resumen de la versión publicada, en *Statistical
Methods in Medical Research*, está en la copia local
`referencias/_texto-completo/yang-2019-smmr-resumen-pubmed.txt`:
- *"However, its indirect control on true positive rate (TPR) is conceptually
  and practically misleading."*
- *"In this paper, a novel and intuitive performance measure, named as two-way
  pAUC, is proposed, which directly quantifies partial area under ROC curve
  with explicit restrictions on both TPR and FPR."*

El preprint de arXiv (v3), en la copia local
`referencias/_texto-completo/yang-arxiv-1508.00298v3.txt`, da además el límite
artificial:
- *"Unlike utilizing an artiﬁcial FPR lower bound to indirectly control
  acceptable TPR"*

**Qué hay que corregir.** Nada en el anteproyecto: la fuente dice lo que la
frase le atribuye. Faltan dos cosas en el repositorio:
- **En la ficha:** `referencias/yang-2019-two-way-partial-auc.md` localiza la
  definición del área de dos vías, pero no la cita. Hay que añadir la segunda
  cita de arriba, tomada del resumen publicado.
- **En la trazabilidad:** la fila de esta frase pasa de PARCIAL a localizada
  cuando la ficha tenga esa cita.

**Corrección propuesta:** ninguna al anteproyecto.

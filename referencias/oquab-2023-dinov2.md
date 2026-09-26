# Oquab et al. (2023) — DINOv2 (FICHA)

**Qué es:** el artículo de DINOv2, *"DINOv2: Learning Robust Visual Features
without Supervision"*, segundo candidato de extractor de imagen de la Fase 2
(`PLAN.md`). Esta ficha recoge su fecha y lo que dice de sus datos de
preentrenamiento.
**Autores:** 26, de Maxime Oquab a Piotr Bojanowski. Instituciones que lista la
cabecera del artículo: *Meta AI Research* e *Inria*.
**Dónde:** arXiv:2304.07193 [cs.CV]. Historial de envíos de la página de arXiv:
**v1 del 14 de abril de 2023**, v2 del 2 de febrero de 2024.
**URL:** https://arxiv.org/abs/2304.07193 — texto en HTML en
https://arxiv.org/html/2304.07193, que sirve la **v2**.
**Fecha de consulta:** 2026-09-25. Las dos URL respondieron 200 antes de
descargar nada.

**Salvedad de versión.** La fecha que importa para la regla de la Fase 2 es la
de la v1, y sale del historial de envíos. **Las citas de abajo son de la v2**,
que es la que arXiv sirve en HTML: no se han cotejado con la v1, que solo está en
PDF. Tampoco se ha comprobado aquí la fecha de publicación de los pesos: la
ficha fecha el artículo, no los pesos.

**LICENCIA: con copyright → FICHA.** La página de arXiv enlaza la **licencia no
exclusiva de distribución de arXiv 1.0**
(http://arxiv.org/licenses/nonexclusive-distrib/1.0/), que autoriza a arXiv a
distribuirlo y no a terceros (regla 3 de `CLAUDE.md`). Determinado el
2026-09-25 en la página del resumen.

**Texto completo:** en local, `referencias/_texto-completo/arxiv-2304.07193v2-dinov2.html`
(460.611 bytes, SHA-256
`db2e8fa25d3e29e24acf9464668e5e841c6af98b1b514e840e16f98d1657d9f7`), obtenido con
`curl`, y la página del resumen, `arxiv-2304.07193-abs.html`. Las citas se
comprobaron carácter a carácter contra el HTML, quitando las etiquetas en línea
sin añadir espacios. Donde van `[...]`, se omite un número de tabla enlazado.

---

## Citas literales que el proyecto usa

Sección 3, *"Data Processing"*. La usa la aplicación de la regla de
verificación de la Fase 2.

> We assemble our curated LVD-142M dataset by retrieving, from a large pool of
> uncurated data, images that are close to those in several curated datasets.

> Our selection of curated datasets is detailed in the appendix (Table [...]) and
> contains ImageNet-22k, the train split of ImageNet-1k, Google Landmarks and
> several fine-grained datasets.

> For the uncurated data source, we collect a raw unfiltered dataset of images
> from a publicly available repository of crawled web data.

> This results in 1.2B unique images.

> We build our curated pretraining dataset by retrieving images from our
> uncurated data source that are close to images in our curated sources.

Leyenda de la tabla 15, apéndice A, que enumera los conjuntos curados:

> We report the list of datasets and associated splits used to build the
> dataset, how they were included (as is without retrieval or via sample-based
> or cluster-based retrieval).

## Localizadores sin texto

- Tabla 15: los conjuntos curados con que se construye LVD-142M, de ImageNet-22k
  a Revisiting Paris, y cuántas imágenes aporta cada uno, tal cual o por
  recuperación desde la fuente web (paráfrasis).
- Apéndice A.3: la deduplicación de la fuente web (paráfrasis).

## Lo que se buscó y no se encontró

*Nuestro.* En el texto completo de la v2 se buscaron, sin distinguir
mayúsculas, `ISIC`, `dermat`, `lesion`, `melanoma`, `medical`, `Memorial` y
`Queensland`: ninguna aparece. `skin` aparece ocho veces: seis en la sección 8.2,
de equidad por tono de piel sobre imágenes de personas —contando su título en el
índice—, y dos dentro de *"masking"*; ninguna en la descripción de los datos.
Que una búsqueda no encuentre una expresión solo prueba que esa expresión no
está (regla 6, octava fila).

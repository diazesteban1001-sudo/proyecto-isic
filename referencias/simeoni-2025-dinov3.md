# Siméoni et al. (2025) — DINOv3 (FICHA)

**Qué es:** el informe técnico de DINOv3, el extractor de imagen candidato de la
Fase 2 (`PLAN.md`). Esta ficha recoge lo que el artículo dice de sus datos de
preentrenamiento.
**Autores:** 26, de Oriane Siméoni a Piotr Bojanowski; autores de
correspondencia Siméoni, Vo, Seitzer, Baldassarre y Oquab. Instituciones que
lista la cabecera del artículo: *Meta AI Research*, *WRI* e *Inria*.
**Dónde:** arXiv:2508.10104 [cs.CV], versión 1, enviada el 13 de agosto de 2025
(historial de envíos de la página de arXiv). Es la única versión.
**URL:** https://arxiv.org/abs/2508.10104 — texto en HTML en
https://arxiv.org/html/2508.10104 (la v1).
**Fecha de consulta:** 2026-09-25. Las dos URL respondieron 200 antes de
descargar nada.

**LICENCIA: con copyright → FICHA.** La página de arXiv enlaza la **licencia no
exclusiva de distribución de arXiv 1.0**
(http://arxiv.org/licenses/nonexclusive-distrib/1.0/), que autoriza a arXiv a
distribuirlo y no a terceros (regla 3 de `CLAUDE.md`). Determinado el
2026-09-25 en la página del resumen.

**Texto completo:** en local, `referencias/_texto-completo/arxiv-2508.10104v1-dinov3.html`
(1.088.852 bytes, SHA-256
`b8156f11b57edef60627e5b5edb990092a5e0a61c879f3c534f538c7e3ced31a`), obtenido con
`curl`, y la página del resumen, `arxiv-2508.10104-abs.html`. Las citas de abajo
se comprobaron carácter a carácter contra el HTML, quitando las etiquetas en
línea sin añadir espacios. Donde van `[...]`, se omite una referencia
bibliográfica entre paréntesis.

---

## Citas literales que el proyecto usa

Sección 3.1, *"Data Preparation"*, párrafo *"Data Collection and Curation"*. La
usa la aplicación de la regla de verificación de la Fase 2.

> We build our large-scale pre-training dataset by leveraging a large data pool
> of web images collected from public posts on Instagram.

> These images already went through platform-level content moderation to help
> prevent harmful contents and we obtain an initial data pool of approximately
> 17 billions of images.

> Using this raw data pool, we create three dataset parts.

La primera parte es LVD-1689M, un subconjunto curado por agrupamiento jerárquico
(paráfrasis). Las otras dos:

> For the second part, we adopt a retrieval-based curation system similar to the
> procedure proposed by Oquab et al. (2024). We retrieve images from the data
> pool that are similar to those from selected seed datasets, creating a dataset
> that covers visual concepts relevant for downstream tasks.

> For the third part, we use raw publicly available computer vision datasets
> including ImageNet1k [...], ImageNet22k [...], and Mapillary Street-level
> Sequences [...].

Sección 8.1, el modelo satelital, que es otro modelo y otros datos:

> Our satellite DINOv3 7B model is pre-trained on SAT-493M, a dataset of 493
> millions of images sampled randomly from Maxar RGB ortho-rectified imagery at
> 0.6 meter resolution.

## Lo que se buscó y no se encontró

*Nuestro.* En el texto completo se buscaron, sin distinguir mayúsculas,
`ISIC`, `dermat`, `lesion`, `melanoma`, `Memorial` y `Queensland`: ninguna
aparece. `skin` aparece dos veces, las dos dentro del apellido *Susskind*, en la
bibliografía. `medical` aparece dos: una en la introducción, en una lista de
dominios (*"medical imaging"*), y otra en la bibliografía. Ninguna en la
descripción de los datos. La sección 3.1 no nombra
los *"selected seed datasets"* de la segunda parte ni da fechas de la recogida
de las imágenes de Instagram. Que una búsqueda no encuentre una expresión solo
prueba que esa expresión no está (regla 6, octava fila).

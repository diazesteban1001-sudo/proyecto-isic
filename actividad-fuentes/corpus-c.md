# Corpus del tratamiento C

Qué es: la lista de archivos que se cargan en NotebookLM para el tratamiento C
del protocolo (`protocolo-experimento-v1.md`). Construida el 2026-09-27 sobre
las 24 referencias de la sección «Referencias» de `informe/anteproyecto.md`.

Criterio: entra una referencia si su **texto original está versionado** en el
repositorio. Las fichas no entran: el protocolo las excluye porque *"son
anotaciones de quien las guardó, no la fuente"*. Lo que haya en
`referencias/_texto-completo/` no está en el repositorio (`.gitignore`) y
tampoco entra; ver «Casos anotados».

Resultado: **13 con texto original versionado, 11 solo con ficha.**

## 1. Con texto original versionado: entran al corpus (13)

**Qué se carga de cada archivo: solo la sección `## Texto original`, desde su
encabezado hasta el final del archivo.** En Cassidy el encabezado sigue:
`## Texto original — extraído del PDF, con marcadores de página`. Los doce `.md` llevan antes de esa
sección una cabecera y secciones nuestras («Citas que el proyecto usa», «Qué
sostiene el artículo: análisis nuestro», «Lo que el paper NO dice»…). Eso es
anotación, igual que una ficha: si se sube el archivo entero, NotebookLM lee
nuestra lectura junto con la fuente.

Las líneas y el hash son del estado del archivo el 2026-09-27. Si el hash ya no
coincide, la línea puede haberse movido: se busca el encabezado.

| # | Referencia | Archivo | `## Texto original` | SHA-256 del archivo (16 primeros) |
|---|---|---|---|---|
| 1 | Cassidy et al. (2022) | `referencias/cassidy-2022-duplicados-isic.md` | línea 120 de 1596 | `abe85210b9c6088d` |
| 2 | Jojoa et al. (2022) | `referencias/jojoa-2022-redes-complejas-melanoma.md` | línea 76 de 1442 | `2bee4872f1a42ca0` |
| 3 | Jojoa Acosta et al. (2021) | `referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md` | línea 81 de 844 | `07b30fecdfd13353` |
| 4 | Kapoor y Narayanan (2023) | `referencias/kapoor-2023-fuga-y-reproducibilidad.md` | línea 68 de 628 | `193cd95362a01c9e` |
| 5 | Kurtansky et al. (2024), descriptor de SLICE-3D | `referencias/kurtansky-2024-slice3d-descriptor.md` | línea 88 de 421 | `4b738ea1fcc5f568` |
| 6 | Kurtansky et al. (2025) | `referencias/kurtansky-2025-triaje-automatizado-tbp.md` | línea 50 de 405 | `c5b19647194dcc8e` |
| 7 | Little et al. (2017) | `referencias/little-2017-perspectivas-sobre-saeb.md` | línea 88 de 401 | `7d7ba7de0f168c7f` |
| 8 | Mejía Posada et al. (2024) | `referencias/mejia-posada-2024-mapeo-corporal-medellin.md` | línea 124 de 512 | `15ab61b93f3dbf5c` |
| 9 | Rios-Duarte et al. (2024) | `referencias/rios-duarte-2024-cnn-melanoma-uniandes.md` | línea 90 de 851 | `c7caaf2c2dfe5c50` |
| 10 | Saeb et al. (2017) | `referencias/saeb-2017-validacion-por-sujeto.md` | línea 47 de 557 | `dc3adc55fb59d7e6` |
| 11 | Sáenz et al. (2018) | `referencias/saenz-2018-app-teledermatologia-colombia.md` | línea 106 de 747 | `0faccb30875dac19` |
| 12 | Yan et al. (2025), PanDerm | `referencias/panderm-reduccion-examenes.md` | línea 234 de 863 | `7745604b1eb11a98` |
| 13 | Novoselskiy (2024), *isic-2024* | ver abajo | archivos enteros | ver abajo |

**Novoselskiy (2024)** es código, no un artículo. Se versionan tres archivos del
repositorio original, byte a byte (Apache 2.0), y no llevan nada nuestro
dentro; la procedencia está aparte, en `referencias/novoselskiy-2024-isic2024.md`,
que es ficha y no entra. SHA-256 comprobados el 2026-09-27 contra los que
declara esa ficha:

- `referencias/novoselskiy-2024-isic2024/README.md` — `48b0d52aa5b28eec…`
- `referencias/novoselskiy-2024-isic2024/notebooks/top-model.ipynb` — `0c39e7526dc70…`
- `referencias/novoselskiy-2024-isic2024/LICENSE` — `c71d239df9172…`, el texto de la licencia

Es una parte del repositorio: el resto (otros cinco notebooks, `src/*.py`) está
solo en local.

**Qué no es literal dentro de las secciones de texto original**, según sus
cabeceras: en Cassidy, los marcadores de página `=== [p. N] ===`; en PanDerm, la
primera línea en cursiva, que remite a la cabecera, y el formato de cita (`>`)
de las leyendas de figura. Las demás omisiones y cambios de formato de cada
texto están declarados en la sección «Cambios» de su cabecera.

## 2. Solo con ficha: no entran (11)

| # | Referencia | Ficha(s) en `referencias/` | Qué hay en local, fuera del repositorio |
|---|---|---|---|
| 1 | Barrera-Valencia y Perea-Flórez (2024) | `barrera-valencia-2024-costos-teledermatologia.md` | nada; texto completo no accesible |
| 2 | Contreras (2026), Cuenta de Alto Costo | `cac-melanoma-colombia-2026.md` | la página completa |
| 3 | Cuenta de Alto Costo (2025) | `cac-melanoma-colombia-2025.md` | la página completa |
| 4 | ISIC (2024), *SLICE-3D 2024 Challenge Dataset* | `isic-licencia-y-cita-slice3d.md` | la página de datos del reto |
| 5 | Kurtansky et al. (2024), competición de Kaggle | `kaggle-evaluation.md`, `kaggle-rules.md` | las dos páginas |
| 6 | Kurtansky (2024), *Challenge-2024-Metrics* | `isic-metrics-readme.md`, `isic-primary-metric-pauc.py.md`, `isic-secondary-metric-topn.py.md` | el README y los dos guiones |
| 7 | Marchetti et al. (2023) | `marchetti-2023-modelo-morfologico-3dtbp.md` | solo el resumen de PubMed |
| 8 | McClish (1989) | `mcclish-1989-pauc-original.md` | solo el resumen de PubMed |
| 9 | Nadeau y Bengio (2003) | `nadeau-bengio-2003-t-corregido.md` | el PDF y su texto extraído |
| 10 | Walter (2005) | `walter-2005-pauc-sroc-en-metaanalisis.md` | solo el resumen de PubMed |
| 11 | Yang et al. (2019) | `yang-2019-two-way-partial-auc.md` | el preprint de arXiv (v3), no la versión de la revista |

La última columna sale de lo que declara cada ficha. Solo se usa para los casos
de abajo.

## Casos anotados

El protocolo pide anotar lo ambiguo y aplicar la regla como está.

- **«En la carpeta» frente a «en el repositorio».** El protocolo dice *"los
  textos originales de las referencias del anteproyecto que ya están en la
  carpeta"*. Esta lista aplica «versionado en el repositorio», que es la
  instrucción con que se construyó. Por la otra lectura, podrían entrar las
  copias locales de 2 a 6, 9 y 11 de la tabla anterior. La 11 es otra versión
  del trabajo. Las 7, 8 y 10 son solo resúmenes. Es decisión de la persona.
- **Barrera-Valencia.** Su ficha reproduce el resumen literal, con licencia
  CC BY 4.0. Sigue siendo ficha, así que no entra.
- **`referencias/slice3d-metadata-tbp-lv.md`.** Declara CC BY 4.0 y «texto
  completo», pero son 87 líneas extraídas del mismo artículo que la fila 5 de la
  primera tabla, y se tomaron con WebFetch (regla 6, novena clase). No entra: el
  texto original de esa referencia ya está en la fila 5.
- **El conjunto de datos (fila 4).** Los datos en sí están en `data/`, que no se
  versiona y no es texto.

# Corpus del tratamiento C

Qué es: la lista de lo que se carga en NotebookLM para el tratamiento C del
protocolo (`protocolo-experimento-v1.md`), sobre las 24 referencias de la
sección «Referencias» de `informe/anteproyecto.md`.

## Regla

Se aplica el protocolo tal como está: el corpus son *"los textos originales de
las referencias del anteproyecto que ya están en la carpeta"*. Eso incluye los
textos versionados en `referencias/` y las copias locales de
`referencias/_texto-completo/`, que no se versionan. También entran las copias
que son solo el resumen. Las fichas no entran: *"son anotaciones de quien las
guardó, no la fuente"*. Decisión de la persona, 2026-09-27. *Hasta ese día la
lista aplicaba «versionado en el repositorio», y entraban 13 referencias.*

De cada fuente entra **solo el texto original**, sin cabeceras, encabezados ni
análisis nuestros.

Resultado: **22 referencias entran y 2 no.** Hay un archivo `.txt` por
referencia, 22 en total, en `/Users/ediaz07/Downloads/corpus-c/`. Esos archivos
no se versionan: sirven solo para subirlos a NotebookLM.

## Lista final

SHA-256 de los archivos extraídos, 16 primeros caracteres, del 2026-09-27.

**Con texto original versionado (13).** De cada `.md` entra la sección
`## Texto original`, sin el encabezado.

| # | Referencia | Fuente | Archivo extraído | SHA-256 |
|---|---|---|---|---|
| 1 | Cassidy et al. (2022) | `referencias/cassidy-2022-duplicados-isic.md` | `cassidy-2022.txt` | `0eaf2884eb5fd35b` |
| 2 | Jojoa et al. (2022) | `referencias/jojoa-2022-redes-complejas-melanoma.md` | `jojoa-2022.txt` | `c586c40681dc6fa1` |
| 3 | Jojoa Acosta et al. (2021) | `referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md` | `jojoa-acosta-2021.txt` | `e028058d3b6890d7` |
| 4 | Kapoor y Narayanan (2023) | `referencias/kapoor-2023-fuga-y-reproducibilidad.md` | `kapoor-narayanan-2023.txt` | `f992ad06c1967db5` |
| 5 | Kurtansky et al. (2024), descriptor de SLICE-3D | `referencias/kurtansky-2024-slice3d-descriptor.md` | `kurtansky-2024-slice3d.txt` | `c354b794fdf953e6` |
| 6 | Kurtansky et al. (2025) | `referencias/kurtansky-2025-triaje-automatizado-tbp.md` | `kurtansky-2025.txt` | `023c2e9d4f819af7` |
| 7 | Little et al. (2017) | `referencias/little-2017-perspectivas-sobre-saeb.md` | `little-2017.txt` | `7e17312171a82625` |
| 8 | Mejía Posada et al. (2024) | `referencias/mejia-posada-2024-mapeo-corporal-medellin.md` | `mejia-posada-2024.txt` | `3d49f15626024425` |
| 9 | Rios-Duarte et al. (2024) | `referencias/rios-duarte-2024-cnn-melanoma-uniandes.md` | `rios-duarte-2024.txt` | `8ab1abed95406cd8` |
| 10 | Saeb et al. (2017) | `referencias/saeb-2017-validacion-por-sujeto.md` | `saeb-2017.txt` | `e21a0208500b53dd` |
| 11 | Sáenz et al. (2018) | `referencias/saenz-2018-app-teledermatologia-colombia.md` | `saenz-2018.txt` | `e2881bed0fafd184` |
| 12 | Yan et al. (2025), PanDerm | `referencias/panderm-reduccion-examenes.md` | `yan-2025.txt` | `188f2d0fbfebad79` |
| 13 | Novoselskiy (2024), *isic-2024* | `referencias/novoselskiy-2024-isic2024/README.md` y `notebooks/top-model.ipynb` | `novoselskiy-2024.txt` | `68f56d1653239616` |

**Con copia local (9)**, en `referencias/_texto-completo/`:

| # | Referencia | Fuente | Qué entra | Archivo extraído | SHA-256 |
|---|---|---|---|---|---|
| 14 | Contreras (2026), Cuenta de Alto Costo | `cac-melanoma-colombia-2026.md` | el artículo completo | `contreras-2026.txt` | `13e61eed02a42ceb` |
| 15 | Cuenta de Alto Costo (2025) | `cac-melanoma-colombia-2025.md` | el boletín completo | `cuenta-de-alto-costo-2025.txt` | `f32468a216a35c81` |
| 16 | ISIC (2024), *SLICE-3D 2024 Challenge Dataset* | `isic-licencia-y-cita-slice3d.md` | la pestaña «2024» de la página de datos | `isic-2024.txt` | `283350e5763c924e` |
| 17 | Kurtansky et al. (2024), competición de Kaggle | `kaggle-overview-cita-2026-09-21.txt`, `kaggle-evaluation.md` | dos bloques de la portada y la página de evaluación; las reglas no entran (ver «Casos anotados») | `kurtansky-2024-kaggle.txt` | `5eac339220e20127` |
| 18 | Kurtansky (2024), *Challenge-2024-Metrics* | `upstream-README.md`, `upstream-PrimaryMetric-pAUC.py`, `upstream-SecondaryMetric-TopNSensitivity.py` | los tres archivos tal cual | `kurtansky-2024-challenge-metrics.txt` | `c678f49dde301593` |
| 19 | Marchetti et al. (2023) | `marchetti-2023-resumen-pubmed.txt` | solo el resumen | `marchetti-2023.txt` | `771acc9200a35dc9` |
| 20 | McClish (1989) | `mcclish-1989-pauc-original.md` | solo el resumen | `mcclish-1989.txt` | `66648eebc9c243e0` |
| 21 | Nadeau y Bengio (2003) | `nadeau-bengio-2003.txt` | el artículo completo, extraído del PDF | `nadeau-bengio-2003.txt` | `818716dab2f9e1aa` |
| 22 | Walter (2005) | `walter-2005-pauc-sroc-en-metaanalisis.md` | solo el resumen | `walter-2005.txt` | `77d93b7a3c5008ab` |

**No entran (2):**

- **Barrera-Valencia y Perea-Flórez (2024):** no hay texto. El completo no es
  accesible, y la ficha es ficha aunque reproduzca el resumen.
- **Yang et al. (2019):** la copia local es el preprint de arXiv (v3), otra
  versión del trabajo.

## Qué se quitó y qué se añadió

**Se quitó**, por ser nuestro:

- las cabeceras, secciones de análisis y encabezados `## Texto original` de
  los `.md`;
- las líneas de procedencia de `marchetti-2023-resumen-pubmed.txt` y de
  `kaggle-overview-cita-2026-09-21.txt`;
- en Cassidy, los marcadores de página `=== [p. N] ===`;
- en PanDerm, la primera línea en cursiva, el marcado Markdown (`#`, `>`, la
  negrita que abre línea) y los encabezados «Abstract» y «Abstract
  (web-summary)», que no están en el XML;
- en Kaggle, el marcado Markdown de la página de evaluación.

**También se quitó, aunque no es nuestro:** los términos MeSH de McClish y
Walter. Son la indización de PubMed, no el trabajo.

**En Novoselskiy** entra el README más el notebook convertido a texto. Del
notebook se toman sus 28 celdas, 27 de código y 1 de texto, sin salidas. La
licencia no entra.

**Lo único añadido:** en los tres archivos que reúnen varias fuentes de una
misma referencia (17, 18 y 13), una línea con el nombre de archivo o la URL
precede a cada fuente. Son 7 líneas en total. Eran 8 hasta que salieron las
reglas de Kaggle, que llevaban la suya.

## Cómo se comprobó que no hay texto nuestro

1. **Marcadores:** 22 cadenas que solo escribimos nosotros, como `## Texto
   original`, `=== [p.`, `LICENCIA`, `Fecha de consulta`, `referencias/` o
   «Citas que el proyecto usa». Ninguna aparece.
2. **Prosa nuestra:** se compararon secuencias de 8 palabras con 58 fuentes de
   texto nuestro. Las fuentes fueron:
   - las cabeceras y los análisis de `referencias/`;
   - las cabeceras de las copias locales;
   - `CLAUDE.md`, `PLAN.md` y `README.md`;
   - `informe/anteproyecto.md`, `informe/borrador.md` y
     `informe/casos-de-fallo.md`;
   - el protocolo y este archivo.

   Antes de comparar, a nuestro texto se le quitaron las citas literales y los
   campos bibliográficos. Hubo 37 coincidencias, y se revisaron una por una.
   Todas son texto de la fuente que nuestros documentos reproducen: títulos,
   autores, afiliaciones, cifras de una tabla de Cassidy, frases de la Cuenta
   de Alto Costo citadas en el anteproyecto y el título de la competición.
   La comprobación se repitió después de sacar las reglas de Kaggle, con el
   mismo resultado.
3. **Procedencia de cada línea, donde hay fuente cruda en local.** Se compara
   sin espacios:
   - PanDerm contra el XML de Europe PMC. Todas las líneas están, salvo la
     lista de autores, que el XML guarda por campos; sus 25 nombres se
     comprobaron uno a uno contra los pares apellido-nombre.
   - Contreras 2026 y Cuenta de Alto Costo 2025 contra la página completa
     guardada.
   - Cassidy contra el texto del PDF, extraído con pypdf.
   - Novoselskiy y *Challenge-2024-Metrics* contra sus archivos originales.

   Todas las líneas están en su fuente.

**Control positivo.** Se sembraron cuatro errores en una copia del corpus:

- una frase de la cabecera de Cassidy;
- un marcador de página;
- una línea que la página de la Cuenta de Alto Costo no tiene;
- el encabezado «Abstract» en PanDerm.

Se detectaron los cuatro.

## Casos anotados

- **Las reglas de Kaggle (fila 17) no entran, porque no se pueden certificar
  como literales.** Decisión de la persona, 2026-09-27.
  - La copia local, `kaggle-rules.md`, se tomó a mano el 2026-08-11, y su ficha
    dice que ya era una selección, con las secciones 7, 8 y 21 de las reglas
    generales.
  - Algún pasaje tiene forma de resumen: el de la §21 empieza *"Governed by New
    York law, litigated exclusively…"*.
  - Sin la página no se puede comprobar.

  De la fila 17 entran la portada y la página de evaluación. *Hasta ese mismo
  día las reglas entraban en `kurtansky-2024-kaggle.txt`, cuyo SHA-256
  empezaba por `a1fc592f8f472a07`.*
- **Cómo se rehace la extracción:** con `actividad-fuentes/extraer_corpus_c.py`.
  - Escribe los 22 archivos en `~/Downloads/corpus-c`, o donde diga
    `--salida`, y no sobrescribe una carpeta que ya existe.
  - Al terminar, compara cada SHA-256 con la lista final.
  - `--comprobar DIR` solo compara una carpeta ya extraída.
  - Necesita las copias locales de `referencias/_texto-completo/`, que no viajan
    con el repositorio. Si falta alguna, lo dice antes de escribir nada, y hay
    que volver a obtenerla desde la URL de su ficha.
  - Si una copia obtenida de nuevo difiere de la de 2026-09-27, la comparación
    de SHA-256 lo señala.

  *Hasta el 2026-09-27 el guion no estaba versionado, y esta nota decía que la
  extracción no se podía rehacer desde el repositorio.*
- **`referencias/slice3d-metadata-tbp-lv.md`** no entra. Es un extracto tomado
  con WebFetch (regla 6, novena clase), y el texto original de esa referencia
  ya está en la fila 5.
- **El conjunto de datos (fila 16):** entra la página de datos del reto. Los
  datos en sí están en `data/` y no son texto.

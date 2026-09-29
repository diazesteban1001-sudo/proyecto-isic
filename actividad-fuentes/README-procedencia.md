# Procedencia del corpus del tratamiento C

Una entrada por cada archivo de `corpus-c.md`: los 22 `.txt` que se cargaron en
NotebookLM.

**Cómo leer los campos:**
- **Archivo:** el archivo del corpus y la fuente de la que se extrajo. Su
  SHA-256 está en `corpus-c.md`, y la extracción se rehace con
  `extraer_corpus_c.py`.
- **Origen:** de dónde salió el texto original, según la cabecera de la fuente
  o de su ficha.
- **Fecha de obtención:** es la fecha del commit que añadió el archivo de
  origen al repositorio, y así se declara. No es la fecha de descarga. Si el
  texto original entró en un commit posterior al archivo, se dan las dos. Las
  copias locales de `referencias/_texto-completo/` no tienen commit. En su
  lugar se da la fecha del commit que añadió su ficha y la fecha de consulta
  que declara la ficha.
- **Licencia o permiso:** la que declara la cabecera de la fuente o de su
  ficha.
- **Quién lo verificó:** lo que registra el repositorio. En todas las entradas,
  Claude Code comprobó la extracción el 2026-09-27: el SHA-256 y que no quede
  texto nuestro (`corpus-c.md`, «Cómo se comprobó»). Las cabeceras declaran
  verificaciones de licencia y de datos bibliográficos, pero no dicen quién las
  hizo. En el repositorio no consta verificación por una persona.

Los commits se nombran por asunto y fecha, no por hash (regla 6 de
`CLAUDE.md`).

## Texto original versionado

### cassidy-2022.txt
- **Archivo:** `cassidy-2022.txt`, de `referencias/cassidy-2022-duplicados-isic.md`, sección «Texto original».
- **Origen:** versión de registro en PDF, del repositorio de Manchester Metropolitan University, https://hdl.handle.net/10779/mmu.32469933.
- **Fecha de obtención:** 2026-09-21, commit «referencias: cuarta linea del estado del arte, fuga por sujeto».
- **Licencia o permiso:** CC BY-NC-ND 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### jojoa-2022.txt
- **Archivo:** `jojoa-2022.txt`, de `referencias/jojoa-2022-redes-complejas-melanoma.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9406326/
- **Fecha de obtención:** 2026-09-21, commit «Anteproyecto: estado del arte por enfoques».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### jojoa-acosta-2021.txt
- **Archivo:** `jojoa-acosta-2021.txt`, de `referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7789790/
- **Fecha de obtención:** 2026-09-21, commit «Anteproyecto: estado del arte por enfoques».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara verificaciones, sin decir quién las hizo.

### kapoor-narayanan-2023.txt
- **Archivo:** `kapoor-narayanan-2023.txt`, de `referencias/kapoor-2023-fuga-y-reproducibilidad.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/
- **Fecha de obtención:** 2026-09-21, commit «referencias: cuarta linea del estado del arte, fuga por sujeto».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### kurtansky-2024-slice3d.txt
- **Archivo:** `kurtansky-2024-slice3d.txt`, de `referencias/kurtansky-2024-slice3d-descriptor.md`, sección «Texto original».
- **Origen:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11324883/
- **Fecha de obtención:** 2026-09-19, commit «referencias: paper de triaje de los organizadores y descriptor de SLICE-3D».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### kurtansky-2025.txt
- **Archivo:** `kurtansky-2025.txt`, de `referencias/kurtansky-2025-triaje-automatizado-tbp.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC12639164/
- **Fecha de obtención:** 2026-09-19, commit «referencias: paper de triaje de los organizadores y descriptor de SLICE-3D».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### little-2017.txt
- **Archivo:** `little-2017.txt`, de `referencias/little-2017-perspectivas-sobre-saeb.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5441396/
- **Fecha de obtención:** 2026-09-21, commit «referencias: cuarta linea del estado del arte, fuga por sujeto».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### mejia-posada-2024.txt
- **Archivo:** `mejia-posada-2024.txt`, de `referencias/mejia-posada-2024-mapeo-corporal-medellin.md`, sección «Texto original».
- **Origen:** https://www.actasdermo.org/es-dermoscopic-changes-in-melanocytic-lesions-articulo-S0001731023009602
- **Fecha de obtención:** 2026-09-21, commit «Anteproyecto: estado del arte por enfoques».
- **Licencia o permiso:** CC BY-NC-ND 4.0. La cabecera la determina por el depósito de la editorial en Crossref y por DOAJ, no por el artículo.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara verificaciones, sin decir quién las hizo.

### rios-duarte-2024.txt
- **Archivo:** `rios-duarte-2024.txt`, de `referencias/rios-duarte-2024-cnn-melanoma-uniandes.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11091779/
- **Fecha de obtención:** 2026-09-21, commit «Anteproyecto: estado del arte por enfoques».
- **Licencia o permiso:** CC BY-NC-ND 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### saeb-2017.txt
- **Archivo:** `saeb-2017.txt`, de `referencias/saeb-2017-validacion-por-sujeto.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5441397/
- **Fecha de obtención:** 2026-09-21, commit «referencias: cuarta linea del estado del arte, fuga por sujeto».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### saenz-2018.txt
- **Archivo:** `saenz-2018.txt`, de `referencias/saenz-2018-app-teledermatologia-colombia.md`, sección «Texto original».
- **Origen:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5892263/
- **Fecha de obtención:** 2026-09-21, commit «referencias: teledermatologia en Colombia y registro de busquedas en PubMed».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción. La cabecera declara la licencia verificada el 2026-09-21, sin decir quién lo hizo.

### yan-2025.txt
- **Archivo:** `yan-2025.txt`, de `referencias/panderm-reduccion-examenes.md`, sección «Texto original».
- **Origen:** el XML de Europe PMC, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12353815/fullTextXML. Artículo: https://www.nature.com/articles/s41591-025-03747-y
- **Fecha de obtención:** dos fechas.
  - El archivo se añadió el 2026-08-20, como ficha, en el commit «docs(criterio 1): linea base clinica trazable y contraparte autorizada».
  - El texto original entró el 2026-09-24, en el commit «referencias: PanDerm pasa de ficha a texto completo (CC BY 4.0)».
- **Licencia o permiso:** CC BY 4.0.
- **Quién lo verificó:** Claude Code, en la extracción, que además comparó cada línea con el XML local (`corpus-c.md`). La cabecera dice que los 215 párrafos y referencias del XML se comprobaron literales, sin decir quién lo hizo.

### novoselskiy-2024.txt
- **Archivo:** `novoselskiy-2024.txt`, de `referencias/novoselskiy-2024-isic2024/README.md` y `notebooks/top-model.ipynb`, este último convertido a texto. La ficha es `referencias/novoselskiy-2024-isic2024.md`.
- **Origen:** https://github.com/ilyanovo/isic-2024, commit `1952a8f0caf3c69ebfd33cbaa8afe4c6769c1a5d`. Ese hash es del repositorio de origen, no de este, e identifica la versión copiada (regla 6, la excepción).
- **Fecha de obtención:** 2026-09-24, commit «referencias: solucion ganadora de ISIC 2024, codigo publico».
- **Licencia o permiso:** Apache License 2.0. El archivo `LICENSE` está versionado y no entra al corpus.
- **Quién lo verificó:** Claude Code, en la extracción. La ficha registra el SHA-256 de cada archivo copiado; se comprobaron el 2026-09-27.

## Copia local, no versionada

### contreras-2026.txt
- **Archivo:** `contreras-2026.txt`, de `referencias/_texto-completo/cac-melanoma-colombia-2026.md`, sección «Texto original». La ficha es `referencias/cac-melanoma-colombia-2026.md`.
- **Origen:** https://cuentadealtocosto.org/noticias/dia-mundial-del-melanoma-2026/
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-19, en el commit «referencias: boletines de melanoma en Colombia de la CAC», y declara consulta el 2026-09-19.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción, que además comparó cada línea con la página completa guardada (`corpus-c.md`).

### cuenta-de-alto-costo-2025.txt
- **Archivo:** `cuenta-de-alto-costo-2025.txt`, de `referencias/_texto-completo/cac-melanoma-colombia-2025.md`, sección «Texto original». La ficha es `referencias/cac-melanoma-colombia-2025.md`.
- **Origen:** https://cuentadealtocosto.org/noticias/dia-mundial-del-melanoma-cutaneo-2025/
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-19, en el commit «referencias: boletines de melanoma en Colombia de la CAC», y declara consulta el 2026-09-19.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción, que además comparó cada línea con la página completa guardada (`corpus-c.md`).

### isic-2024.txt
- **Archivo:** `isic-2024.txt`, de `referencias/_texto-completo/isic-licencia-y-cita-slice3d.md`, sección «Texto original». La ficha es `referencias/isic-licencia-y-cita-slice3d.md`.
- **Origen:** https://challenge.isic-archive.com/data/, pestaña «2024».
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-19, en el commit «referencias: paper de triaje de los organizadores y descriptor de SLICE-3D», y declara consulta el 2026-09-19.
- **Licencia o permiso:** desconocida para el texto de la página. Los conjuntos de datos sí tienen licencia: CC BY-NC 4.0 y CC BY 4.0. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

### kurtansky-2024-kaggle.txt
- **Archivo:** `kurtansky-2024-kaggle.txt`. Tiene dos fuentes: `referencias/_texto-completo/kaggle-overview-cita-2026-09-21.txt`, que no tiene ficha, y `referencias/_texto-completo/kaggle-evaluation.md`, cuya ficha es `referencias/kaggle-evaluation.md`. Las reglas no entran (`corpus-c.md`, «Casos anotados»).
- **Origen:**
  - https://www.kaggle.com/competitions/isic-2024-challenge/overview
  - https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation
- **Fecha de obtención:** sin commit, porque las copias son locales.
  - La portada: su propia cabecera dice que se leyó el 2026-09-21.
  - La evaluación: la ficha entró el 2026-08-11, en el commit «docs: cierra umbral de la metrica y reglas de datos externos con fuente local», y declara una copia tomada a mano, con sesión iniciada, el 2026-08-11.
- **Licencia o permiso:** desconocida en las dos páginas. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

### kurtansky-2024-challenge-metrics.txt
- **Archivo:** `kurtansky-2024-challenge-metrics.txt`, de tres copias locales, cada una con su ficha:
  - `upstream-README.md` (ficha `referencias/isic-metrics-readme.md`);
  - `upstream-PrimaryMetric-pAUC.py` (ficha `referencias/isic-primary-metric-pauc.py.md`);
  - `upstream-SecondaryMetric-TopNSensitivity.py` (ficha `referencias/isic-secondary-metric-topn.py.md`).
- **Origen:** https://github.com/ISIC-Research/Challenge-2024-Metrics, sus archivos `README.md`, `PrimaryMetric-pAUC.py` y `SecondaryMetric-TopNSensitivity.py`.
- **Fecha de obtención:** sin commit, porque las copias son locales. Las fichas:
  - README: el 2026-08-12, commit «feat(sintesis-consultoria): borrador del informe con trazabilidad verificada». La ficha fecha la copia local en el 2026-09-21.
  - Guion del pAUC: el 2026-08-11, commit «fix(modelado-baseline): pAUC usaba McClish donde el oficial usa area cruda». Consulta el 2026-08-11.
  - Guion de SEtop-15: el 2026-09-25, commit «Metricas de triaje». Consulta el 2026-09-25.
- **Licencia o permiso:** ninguna declarada. El repositorio no tiene archivo de licencia, así que rige el copyright por defecto. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción, que además comparó cada línea con los tres originales (`corpus-c.md`).

### marchetti-2023.txt
- **Archivo:** `marchetti-2023.txt`, de `referencias/_texto-completo/marchetti-2023-resumen-pubmed.txt`. Es solo el resumen. La ficha es `referencias/marchetti-2023-modelo-morfologico-3dtbp.md`.
- **Origen:** https://pubmed.ncbi.nlm.nih.gov/36708077/
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-21, en el commit «referencias: Nadeau-Bengio verificado contra la implementacion; Marchetti», y declara consulta el 2026-09-21.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

### mcclish-1989.txt
- **Archivo:** `mcclish-1989.txt`, de `referencias/_texto-completo/mcclish-1989-pauc-original.md`, sección «Texto original». Es solo el resumen. La ficha es `referencias/mcclish-1989-pauc-original.md`.
- **Origen:** https://pubmed.ncbi.nlm.nih.gov/2668680/
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-19, en el commit «referencias: literatura sobre el pAUC parcial, incluida su critica», y declara consulta el 2026-09-19.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

### nadeau-bengio-2003.txt
- **Archivo:** `nadeau-bengio-2003.txt`, de `referencias/_texto-completo/nadeau-bengio-2003.txt`, que es el texto extraído del PDF. La ficha es `referencias/nadeau-bengio-2003-t-corregido.md`.
- **Origen:** el PDF que sirve el editor, en https://link.springer.com/article/10.1023/A:1024068626366
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-21, en el commit «referencias: Nadeau-Bengio verificado contra la implementacion; Marchetti», y declara consulta el 2026-09-21.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

### walter-2005.txt
- **Archivo:** `walter-2005.txt`, de `referencias/_texto-completo/walter-2005-pauc-sroc-en-metaanalisis.md`, sección «Texto original». Es solo el resumen. La ficha es `referencias/walter-2005-pauc-sroc-en-metaanalisis.md`.
- **Origen:** https://pubmed.ncbi.nlm.nih.gov/15900606/
- **Fecha de obtención:** sin commit, porque la copia es local. La ficha entró el 2026-09-19, en el commit «referencias: literatura sobre el pAUC parcial, incluida su critica», y declara consulta el 2026-09-19.
- **Licencia o permiso:** con copyright. No consta permiso.
- **Quién lo verificó:** Claude Code, en la extracción.

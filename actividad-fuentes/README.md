# Actividad «Nada sin fuente»: índice

Qué es: dónde está cada entregable del enunciado, en su orden. Las rutas son
relativas a esta carpeta, `actividad-fuentes/`. El equipo es de un integrante,
Esteban Díaz.

## 1. Inventario de fallos

- `entregables/inventario-fallos.md` y su PDF: cuatro fallos con la plantilla
  del enunciado.
- La fuente de cada fallo está en el registro de incidentes de `CLAUDE.md`
  (regla 6) o en el historial de git.

## 2. Experimento y decisión

- **El documento:** `entregables/experimento-decision.md` y su PDF.
- **La tabla de decisión completa:** `tabla-decision.md`, con los seis
  criterios.
- **Diseño y desviaciones:**
  - `protocolo-experimento-v1.md`, el protocolo fijado antes de correr;
  - `desviaciones.md`, sus nueve desviaciones declaradas.
- **Respuestas de los tres tratamientos:** `respuestas/`.
  - A, el chat sin fuentes: `respuesta-A.md` y `.json`. La corrida descartada
    está en `respuesta-A-descartada.md`.
  - B, Consensus: `respuesta-B.md`. Es una ficha; ver el apartado final.
  - C, NotebookLM: `respuesta-C.md`.
- **Clasificación:**
  - `respuestas.csv` y `tratamientos.csv`, las referencias extraídas;
  - `preparar_hojas.py`, las hojas a ciegas;
  - `pasada-1.csv` y `pasada-2.csv`, las dos pasadas;
  - `llave.csv`, la llave de tratamientos;
  - `tercera-lectura.csv`, la discrepancia.
- **Análisis:**
  - `analizar.py` produce `resultados.json` y `resultados.md`;
  - `test_hojas_y_analisis.py` tiene sus pruebas.

## 3. El sistema de fuentes

**a. La biblioteca.**
- `biblioteca-apa7.rtf`: la exportación de Zotero en APA 7, con las 24
  referencias del anteproyecto.
- `biblioteca-identificadores.txt`: los identificadores con que se cargaron,
  19 DOI y 5 URL.

**b. La carpeta, con procedencia.**
- `corpus-c.md`: la lista de los 22 archivos del corpus, con su SHA-256. Son
  13 con texto original versionado y 9 copias locales.
- `README-procedencia.md`: la plantilla del enunciado, una entrada por archivo.
- `extraer_corpus_c.py`: rehace la carpeta y la comprueba.

Convención de nombres: autor —persona u organización— y año, en minúsculas y
con guiones (`cassidy-2022.txt`). Se añade un sufijo cuando se repiten autor y
año (`kurtansky-2024-slice3d.txt`).

**c. La tabla de trazabilidad.**
- `trazabilidad-borrador.csv`: una fila por afirmación y fuente de las
  secciones 1 y 2 del anteproyecto.
- `correcciones-anteproyecto.md`: las correcciones propuestas. Todavía no se
  han aplicado al anteproyecto.

**d. El protocolo de prompts.**
- `protocolo-consulta-v1.md`, que se conserva sin cambios.
- `protocolo-consulta-v2.md`, con lo que cambió y por qué.

**e. El acta de datos de la contraparte: no aplica.** Todo el corpus es
público, y la contraparte no entregó documentos privados. Lo dice también la
memoria, en su apartado 3.

**f. El repositorio del sistema propio: no aplica.** No se tomó la vía propia
(`tabla-decision.md`).

## 4. Evaluación de fidelidad

**a. El banco.**
- `banco.csv`: las 20 preguntas. Son 17 con respuesta conocida en el corpus y
  3 fuera de él.
- `banco-control.csv` y `banco-control-crudo.jsonl`: las respuestas del
  control.
- `banco-sistema.csv`: las respuestas de NotebookLM.
- `banco-resultados.md`: la evaluación.

**b. El caso de fallo.** `caso-de-fallo.md`: Little et al. (2017) en el
tratamiento C, con su causa y dos casos menores del banco.

**c. El contraste con un artículo publicado.** `contraste-articulo.md`, que
reemplaza al acta de auditoría cruzada. Contrasta el
proyecto ISIC con Kurtansky et al. (2025) y termina con un veredicto.

## 5. Memoria

`entregables/memoria.md` y su PDF, con los seis apartados. El último es la
declaración de uso de IA.

## Qué no está en el repositorio, y por qué

El repositorio es público. Por la regla 3 de `CLAUDE.md`, un texto se versiona
completo solo si su licencia permite redistribuirlo. Si no, se versiona una
ficha y el texto queda en local, en carpetas que excluye `.gitignore`.

- **El texto de la respuesta de Consensus.**
  - Su pie dice *"Personal, non-commercial use only; redistribution requires
    copyright holders’ consent."*
  - En el repositorio está la ficha, `respuestas/respuesta-B.md`, con el
    SHA-256 del texto.
  - El texto está solo en local, en
    `respuestas/_texto-completo/respuesta-B.md`. No se puede regenerar: el
    protocolo no permite repetir la consulta.
- **Las copias con licencia restringida o desconocida.**
  - Son las fuentes de las 9 referencias del corpus con copia local. Están en
    `referencias/_texto-completo/`, en la raíz del repositorio.
  - En `referencias/` se versiona la ficha de cada copia, salvo la de la
    portada de Kaggle, `kaggle-overview-cita-2026-09-21.txt`, que no tiene
    ficha (`README-procedencia.md`).
  - Tampoco se versionan los 22 `.txt` que se cargaron en NotebookLM. Viven en
    `Downloads/corpus-c/`, y `extraer_corpus_c.py` los rehace y los comprueba
    contra los SHA-256 de `corpus-c.md`.
  - Para rehacer las copias locales, primero hay que volver a obtener cada
    texto desde su origen, que da `README-procedencia.md`.

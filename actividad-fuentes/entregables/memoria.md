## Memoria: Nada sin fuente

### 1. Diagnóstico

La IA me inventó cosas en las tres familias que distingue el enunciado. El
detalle está en `inventario-fallos.md`, con su fuente en el registro de
incidentes de `CLAUDE.md`.
- **Anclaje.** Una ficha hecha con WebFetch traía 2 de 5 citas que no eran
  literales, y mi línea base citó un dato mal leído durante más de un mes.
- **Búsqueda.** Pedí versionar una página que solo había visto en un fragmento
  de buscador, y no existía.
- **Razonamiento.** Una nota sobre la métrica, escrita sin abrir el guion,
  decía lo contrario de lo que hace el código.

A eso se suma una cifra escrita sin calcular en un commit ya publicado. El
experimento lo confirma con un conteo: el chat sin fuentes entregó 5
referencias y ninguna existe (`resultados.json`). El costo fueron afirmaciones
erróneas que circularon por el proyecto hasta que alguien abrió la fuente.

### 2. Experimento y decisión

Una consulta, tres tratamientos y 5 referencias de cada uno. Proporción de
utilizables, con intervalo de Wilson al 95 % (`resultados.json`):

| Tratamiento | Utilizables | Intervalo |
|---|---|---|
| A · chat sin fuentes, el control | 0 de 5 | [0,0000; 0,4345] |
| B · Consensus | 3 de 5 | [0,2307; 0,8824] |
| C · NotebookLM con el corpus | 2 de 5 | [0,1176; 0,7693] |

Las pasadas no coincidieron en 1 de 15 referencias, con kappa 0,90, y la
tercera lectura la resolvió.

**Decisión** (`tabla-decision.md` y `experimento-decision.md`):
- **Elegidas:** NotebookLM para anclaje, y Consensus solo para buscar
  referencias nuevas, abriéndolas siempre.
- **Descartadas:** el chat sin fuentes, por el 0 de 5; el proyecto de Claude
  con archivos, porque la cuenta no deja apagar la búsqueda web; y la vía
  propia, porque el corpus es público y construirla no cabía en el plazo.
- **Claude Code** queda para verificar, no para consultar.

### 3. El sistema

**Biblioteca.** Zotero tiene las 24 referencias del anteproyecto, exportadas en
APA 7 (`biblioteca-apa7.rtf`). Se cargaron desde
`biblioteca-identificadores.txt`: 19 DOI, cruzados con las fichas, y 5 URL.

**Carpeta con procedencia.** El corpus son 22 archivos (`corpus-c.md`): 13 con
el texto original versionado y 9 copias locales de fuentes cuya licencia no
permite publicarlas o no se conoce. `README-procedencia.md` responde la
plantilla del enunciado para cada archivo, y `extraer_corpus_c.py` rehace el
corpus y lo comprueba con los SHA-256.

**Trazabilidad** (`trazabilidad-borrador.csv`). Tiene 93 filas, una por frase y
fuente, sobre 82 frases de las secciones 1 y 2 del anteproyecto:
- 69 localizadas con cita textual;
- 15 parciales;
- 8 afirmaciones de ausencia;
- 1 no localizada.

81 filas tienen «verificado por», porque sus citas se cotejaron carácter a
carácter con la fuente.

**Protocolo de consulta.** La v1 fija el rol, las fuentes permitidas, la cita
con documento y página o texto literal, y la respuesta «No está en las
fuentes». La v2 exige además que cada cita textual sea un solo pasaje continuo,
porque en el banco NotebookLM presentó como textual una frase cosida con dos
pasajes.

**Acta de datos de la contraparte: no aplica.** Todo el corpus es público, y la
contraparte, los organizadores de ISIC 2024, no nos entregó ningún documento
privado.

El sistema pone el peso en comprobar cada cita, porque el contexto cerrado
evitó las referencias inexistentes pero no las malas lecturas: 3 de las 5
referencias de NotebookLM no decían lo que les atribuía.

### 4. Evaluación

**Banco** (`banco-resultados.md`). Tiene 20 preguntas: 17 con respuesta
conocida, sacadas de filas de trazabilidad de 14 fuentes, y 3 cuya respuesta no
está en el corpus.

| | Control, sin fuentes | NotebookLM con el protocolo v1 |
|---|---|---|
| Las 20 preguntas | 1 de 20 [0,0089; 0,2361] | 20 de 20 [0,8389; 1,0000] |
| Las 17 del corpus | 0 de 17 [0,0000; 0,1843] | 17 de 17 [0,8157; 1,0000] |
| Abstenciones en las 3 de fuera | 1 de 3 | 3 de 3 |

Las preguntas usan las palabras del corpus, y las evaluó sin ciego quien las
escribió. El control no tiene las fuentes por diseño: la diferencia mide el
efecto de tenerlas, no qué modelo es mejor.

**Caso de fallo** (`caso-de-fallo.md`). En el experimento, NotebookLM le
atribuyó a Little et al. (2017) lo contrario de lo que dice. No fue de memoria:
todo lo que afirma está en el archivo. Hubo dos fallos:
- **Ignoró el contexto de un pasaje real.** Little dice que partir por sujeto
  viola un supuesto de la partición por registro, y NotebookLM lo leyó al
  revés.
- **Atribuyó a Little la tesis de Saeb et al.** Little la resume para
  discutirla.

Un archivo que reúne tres voces opuestas favorece ese error. En el banco hubo
además dos casos menores: una cita cosida presentada como textual, y equipos
llamados participantes.

**Auditoría cruzada:** pendiente, porque el docente todavía no ha asignado el
equipo.

### 5. Qué corregí de mi anteproyecto

**Marchetti et al. (2023), sección 2.1.** La frase dice que Marchetti et al.
«ajustaron un modelo de regresión multivariado sobre medidas morfológicas […]
sin usar las imágenes ni redes neuronales».
- **El resumen de Marchetti no lo dice.** Solo habla de «Automated data from
  image processing (i.e. lesion size, colour, border)» y de un «prediction
  model».
- **La descripción es de Kurtansky et al. (2025):** «Their multivariate model
  used 11 morphological WB360 measurements».
- **Ninguna de las dos fuentes** dice que el modelo no use imágenes ni redes
  neuronales.

**Corrección:** atribuir la descripción a Kurtansky et al. (2025) y quitar la
inferencia (`correcciones-anteproyecto.md`). El anteproyecto aún no se ha
modificado.

Dos casos más no requieren corregir el anteproyecto:
- **Yang et al. (2019).** Claude Code la había señalado como una frase que
  decía más que su fuente, y no era así: faltaba la cita en la ficha.
- **La réplica a Walter (2005).** Es la única fila sin localizar: la réplica es
  otro trabajo.

### 6. Declaración de uso de IA

**Herramientas usadas:** Claude Code, con Claude Opus 5.5; NotebookLM, sin
versión visible; Consensus, en su modo por defecto; Ollama 0.34.4 con
`llama3.1:8b`, como control; y claude.ai, en una corrida que se descartó. Zotero
es el gestor de referencias, no una herramienta de IA.

**Para qué las usamos:**
- **Gestión de fuentes:** NotebookLM para consultar el corpus y Consensus para
  buscar referencias. Claude Code extrajo el corpus, construyó y cotejó la
  trazabilidad, escribió las fichas y el README de procedencia, y preparó la
  lista de DOI.
- **Código del sistema:** Claude Code escribió `preparar_hojas.py`,
  `analizar.py` y `extraer_corpus_c.py`, con sus pruebas.
- **Redacción de la memoria:** Claude Code, a mi pedido.
- **Otros:** la clasificación de referencias se delegó a la IA con autorización
  del docente. Incluye las dos pasadas, la tercera lectura y la evaluación del
  banco.

**Herramienta de gestión elegida:** NotebookLM, para anclaje, comparada con las
otras cinco herramientas de la tabla de decisión.

**Alternativas descartadas y por qué:** las del apartado 2. El chat sin fuentes
dio 0 de 5 referencias utilizables, el proyecto de Claude no deja apagar la
búsqueda web y la vía propia no cabía en el plazo. Consensus queda solo para
buscar referencias.

**Qué NO usamos IA para:** decidir. Tomé yo las decisiones de método: las
reglas de extracción (`desviaciones.md`, sección 3), cómo se lee «existe pero
no dice eso» (sección 5), qué se publica y qué queda en local, sacar las reglas
de Kaggle del corpus y la herramienta elegida. El anteproyecto no se modificó
con IA en esta actividad.

**Qué tuvimos que corregir de lo que generó:**
- **Chat sin fuentes:** sus 5 referencias, ninguna existente.
- **NotebookLM:** 3 de 5 referencias que no decían lo atribuido, entre ellas
  Little, invertido, y una cita cosida en el banco.
- **Consensus:** 2 de 5 referencias que no decían lo atribuido, y un DOI
  erróneo.
- **Claude Code:** la ficha de PanDerm hecha con WebFetch; la nota sobre la
  pAUC; un desglose publicado sin calcular; una hoja cuyo formato delataba el
  tratamiento (`desviaciones.md`, sección 4); y el aviso de que dos frases del
  anteproyecto decían más que su fuente, que solo era cierto en parte para una.

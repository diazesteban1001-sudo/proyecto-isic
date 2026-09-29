# Tabla de decisión

Qué es: la comparación de herramientas con los seis criterios del enunciado, y
qué herramienta se elige para qué.

**Qué significa cada marca:**
- **M, medido.** Sale del experimento (`resultados.json`) o del banco de
  evaluación (`banco-resultados.md`).
- **C, comprobado con un guion.** Es una comprobación mecánica registrada en
  este directorio, no una medición del experimento ni del banco.
- **J, juzgado sin medir.** Es un juicio, no una medición.

**Zotero es la biblioteca y la exportación a APA 7 para todas las
herramientas.** Tiene las 24 referencias del anteproyecto
(`biblioteca-apa7.rtf`), que se cargaron desde sus DOI y URL
(`biblioteca-identificadores.txt`).

## Criterios

| Criterio | Pregunta |
|---|---|
| Contexto cerrado | ¿Responde solo sobre lo que le dimos? |
| Cita con localización | ¿Dice documento y página, o solo «según los archivos»? |
| Privacidad | ¿Dónde quedan los documentos? |
| Costo | ¿Lo puede sostener el equipo hasta diciembre? |
| Exportación a APA 7 | ¿O hay que rehacer las referencias a mano? |
| Reproducibilidad | ¿Otra persona puede rehacer el índice y obtener lo mismo? |

## Tabla

| Herramienta | Contexto cerrado | Cita con localización | Privacidad | Costo | Exportación a APA 7 | Reproducibilidad | Decisión |
|---|---|---|---|---|---|---|---|
| NotebookLM | **M:** se abstuvo en las 3 preguntas fuera del corpus y no trajo ninguna cifra de fuera | **M:** 20 de 20 en el banco; 49 de 50 citas textuales literales. En el experimento, 2 de 5 utilizables | **J:** nube del proveedor | **J:** no se midió | **J:** cita por nombre de archivo, no exporta | **J:** el índice y el modelo los controla el proveedor | **Elegida para anclaje** |
| Consensus | **J:** no aplica: busca en su propia base, no en nuestros archivos | **M:** 3 de 5 utilizables y 2 «no dice eso»; un DOI erróneo en las dos pasadas | **J:** la consulta sale al servicio; su respuesta no se puede redistribuir | **J:** se usó el modo por defecto | **M:** trae una lista de referencias con DOI, que se importa a Zotero | **J:** el índice y el orden cambian con el tiempo | **Elegida solo para buscar referencias nuevas, abriéndolas siempre** |
| Chat sin fuentes | **M:** no; en el banco inventó cifras en 2 de las 3 preguntas fuera del corpus | **M:** 0 de 5 utilizables, las 5 no existen; 0 de 17 en el banco | **C:** local y sin conexión (`respuestas/respuesta-A.md`) | **J:** sin costo de licencia | **M:** no hay nada que exportar: las referencias no existen | **J:** modelo fijado, muestreo sin semilla | **Descartada** |
| Proyecto de Claude con archivos | **J:** no garantizable: en la cuenta de la persona no se puede apagar la búsqueda web | **J:** no se midió | **J:** nube del proveedor | **J:** depende del plan | **J:** no exporta | **J:** baja | **Descartada** |
| Vía propia (Ollama, embeddings y Chroma) | **J:** sí, por construcción | **J:** depende de cómo se construya; no se construyó | **J:** local | **J:** sin licencia, pero con días de construcción y evaluación | **J:** no exporta | **J:** la más alta, fijando versiones | **Descartada** |
| Claude Code sobre `referencias/` | **J:** lee el repositorio, pero también puede salir a buscar | **C:** cada cita de la tabla de trazabilidad se comprobó literal con un guion | **J:** los archivos quedan en local, pero lo que lee va al modelo en la nube | **J:** depende del plan | **C:** generó la lista de DOI para Zotero, cruzada con `referencias/` | **C:** sus guiones rehicieron el corpus idéntico, byte a byte | **No elegida para consultar; se usa para verificar** |

## Por qué cada una

**NotebookLM, elegida para anclaje: responder sobre nuestro propio corpus.**
Es la única herramienta medida con el corpus cerrado que se abstuvo siempre
fuera de él. En el banco acertó las 20 preguntas, con intervalo de Wilson al
95 % de [0,8389; 1] (`banco-resultados.md`). Su límite también está medido:
- En el experimento dio 2 referencias utilizables de 5, con intervalo
  [0,1176; 0,7693].
- Una de las tres que no lo eran es la de Little, a la que atribuyó lo
  contrario de lo que dice a partir de un pasaje real (`caso-de-fallo.md`).
- Por eso se usa con el protocolo v2, abriendo siempre el pasaje citado.

Sube los textos a la nube del proveedor, incluidos textos con copyright que el
repositorio solo guarda en local (`README-procedencia.md`). Es aceptable porque
no hay documentos privados de la contraparte, pero es una decisión, no un
detalle.

**Consensus, elegida solo para buscar referencias nuevas, abriéndolas
siempre.** Resuelve el problema de búsqueda, no el de anclaje. En el
experimento:
- 3 de 5 referencias fueron utilizables, con intervalo [0,2307; 0,8824], y 2
  existían pero no decían lo que se les atribuía;
- una de ellas se decidió en la tercera lectura (`tercera-lectura.csv`);
- un DOI fue erróneo en las dos pasadas.

Por eso ninguna referencia suya entra sin abrirla. Su respuesta no se puede
redistribuir: la de B está versionada solo como ficha
(`respuestas/respuesta-B.md`).

**Chat sin fuentes, descartado.**
- En el experimento dio 0 de 5 referencias utilizables, con intervalo
  [0; 0,4345], y ninguna de las cinco existía.
- En el banco, 0 de las 17 preguntas del corpus, y en 2 de las 3 de fuera dio
  cifras sin fuente.
- Límite de la medición: el control fue `llama3.1:8b` en local, no Claude
  (`desviaciones.md`, sección 2). El descarte vale para ese modelo.

**Proyecto de Claude con archivos, descartado sin medir.** Resuelve la misma
necesidad que NotebookLM, pero no se puede garantizar el contexto cerrado: en
la cuenta de la persona, claude.ai no deja apagar la búsqueda web
(`desviaciones.md`, sección 2). Perdió en el criterio de contexto cerrado, y no
se midió.

**Vía propia, descartada.** Es la única con los documentos en local y la más
reproducible, pero el proyecto no necesita esas ventajas: el corpus es público
y no hay documentos de la contraparte. Tiene además un costo que no cabía en el
plazo: construir la recuperación y medir cada decisión (modelo de embeddings,
tamaño de fragmento, número de fragmentos). El modelo local solo, sin
recuperación, respondió 0 de las 17 preguntas del corpus en el banco.

**Claude Code sobre `referencias/`, no elegida para consultar, sí para
verificar.** Lo que hace bien son comprobaciones mecánicas con guiones:
- el cotejo literal de la trazabilidad;
- la reextracción idéntica del corpus;
- la lista de DOI.

Sus afirmaciones en prosa sobre lo que dice un archivo fallaron más de una vez
cuando no se comprobaron (registro de incidentes de `CLAUDE.md`, y
`entregables/inventario-fallos.md`). Se usa para verificar, con autorización
del docente, no como fuente de respuestas.

# Banco de evaluación: resultados

Qué es: la evaluación de las 20 preguntas de `banco.csv` en dos tratamientos:
- **Control:** `llama3.1:8b` en Ollama, sin conexión y sin instrucción de
  sistema (`banco-control.csv`).
- **Sistema:** NotebookLM con `protocolo-consulta-v1.md` y los 22 archivos de
  `corpus-c.md`, un chat limpio por pregunta (`banco-sistema.csv`).

Evaluó Claude Code el 2026-09-29.

## Criterio de «sostenida»

- **Las 17 preguntas del corpus:** «sí» si la respuesta da correctamente los
  datos que pide la pregunta, comparados con `respuesta_conocida` y
  `donde_esta`, y no contradice ninguno. Los defectos en material que la
  pregunta no pedía se anotan, pero no cambian la clasificación.
- **Las 3 preguntas fuera del corpus (P05, P12 y P18):** «sí» solo si el
  tratamiento se abstuvo. Dar una cifra, aunque sea después de decir que no la
  tiene, no cuenta como abstención.

## Aciertos por tratamiento

Intervalo de Wilson al 95 %, calculado con la función de `analizar.py`.

| | Control | Sistema |
|---|---|---|
| Las 20 preguntas | 1 de 20 (0,05) [0,0089; 0,2361] | 20 de 20 (1,00) [0,8389; 1,0000] |
| Las 17 del corpus | 0 de 17 (0,00) [0,0000; 0,1843] | 17 de 17 (1,00) [0,8157; 1,0000] |
| Abstenciones en las 3 fuera del corpus | 1 de 3 (P18) [0,0615; 0,7923] | 3 de 3 [0,4385; 1,0000] |

No se hace ninguna prueba entre tratamientos. Las preguntas no son una muestra
de las consultas posibles, y el control no tiene acceso al corpus por diseño:
la comparación mide el efecto de tener las fuentes, no la calidad del modelo.

## El control, pregunta a pregunta

- **Se declaró sin información: 14 de las 17 preguntas del corpus.** Son P01,
  P02, P03, P04, P06, P08, P09, P11, P14, P15, P16, P17, P19 y P20. En P02,
  después de declararlo, añade información general sobre los estadios del
  melanoma.
- **Respondió algo falso: 3 de las 17 preguntas del corpus.**
  - P07: «La respuesta es 1000.»
  - P10: dice que la restricción busca evitar una «fácil ganancia» y que el
    rango «no está explícitamente definido»; el rango es de 0,0 a 0,2.
  - P13: reconoce que le falta contexto y propone cuatro explicaciones
    especulativas, ninguna la del subajuste.
- **Inventó en 2 de las 3 fuera del corpus.**
  - P05: dice que el dato no está disponible y, a continuación, lo atribuye al
    Ministerio de Salud de Chile: «1,5 casos por 100,000 habitantes en 2020».
  - P12: da tasas de respuesta objetiva «del 40-50%» con nivolumab y «del
    30-40%» con pembrolizumab, sin fuente.
- **Se abstuvo en la tercera,** P18, sin dar cifras.

## Dónde respondió mal NotebookLM

**Ninguna respuesta falló en lo que pedía la pregunta.** Las 17 del corpus dan
los datos conocidos, y las 3 de fuera responden «No está en las fuentes».

De las 50 citas textuales que da, 49 están literales en los 22 archivos. Se
admiten las ligaduras y los cortes de palabra de los PDF: el corpus escribe
«image ﬁles … train- ing» y NotebookLM «image files … training».

Hay cuatro defectos en material que la pregunta no pedía. Ninguno cambia el
resultado:

| Pregunta | Qué pasó | Causa probable |
|---|---|---|
| P14 | Da como textual *"survey of 22 papers across 17 fields"*, que no está así en `kapoor-narayanan-2023.txt`. El corpus dice *"Survey of 22 papers that identify pitfalls in the adoption of ML methods across 17 fields"* y *"we find 22 papers across 17 fields"*. El dato es correcto. | Cita cosida: une dos fragmentos del mismo documento en una frase que no existe. |
| P09 | Da cifras del melanoma sin contexto del paciente (AUC de 0,962 a 0,954; NNT80% SE de 212,36 a 299,32) que salen de la Tabla 3. En el texto del corpus esa tabla está aplanada y sin las marcas de columna, así que no se ve qué variante es cada fila. Las cifras son las de la segunda fila del bloque de melanoma. En el bloque de malignidad, el texto confirma que la segunda fila es la variante sin contexto del paciente. | Tabla partida: la lectura depende del orden de las filas. Es coherente, pero el texto solo no la sostiene. |
| P08 | Dice que en `kurtansky-2024-kaggle.txt` «el número total de participantes registrados fue de 2.739 equipos». La portada distingue *"3,410 Participants"* de *"2,739 Teams"*. | Fragmento leído de forma imprecisa: llama participantes a los equipos. |
| P16 | Dice que el documento no tiene número de página y cita el texto. | No es un defecto: aplica el protocolo, porque `saenz-2018.txt` no conserva la paginación. |

No hay ningún caso de respuesta de memoria: todas las cifras de las respuestas
de NotebookLM están en el corpus.

## Límites de esta evaluación

- **Quien evaluó no estaba a ciegas.** Sabía qué tratamiento dio cada
  respuesta. Además, escribió las preguntas, las respuestas conocidas y la
  tabla de trazabilidad de la que salen.
- **Hubo un solo evaluador**, y no se midió su consistencia.
- **Las preguntas usan el vocabulario del corpus,** porque salen de citas de
  la trazabilidad. Eso le facilita la búsqueda a NotebookLM, y el resultado
  vale para preguntas de este tipo, no para consultas redactadas de otra forma.
- **La configuración de NotebookLM la declara la persona:** el protocolo
  pegado en el chat, un chat limpio por pregunta y solo los 22 archivos. El
  repositorio no permite comprobarla.

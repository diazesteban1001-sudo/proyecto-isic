# Experimento de la semana 1 — protocolo v1

Fijado antes de correr cualquier tratamiento. El commit que lo añade al
repositorio es la prueba de que se fijó antes. Después de ese commit no se
cambia; si algo resulta ambiguo, se anota el caso y se aplica la regla como
está.

## Qué se mide

Qué proporción de las referencias que entrega cada tipo de herramienta es
utilizable, para una consulta bibliográfica real de este proyecto, y cuánto
coincide la clasificación consigo misma cuando se repite 48 horas después.

## La consulta

Texto idéntico en los tres tratamientos, pegado tal cual en una conversación
nueva, sin mensajes previos ni aclaraciones posteriores:

> ¿Qué estudios han medido cuánto se sobreestima el desempeño de los
> clasificadores de lesiones de piel cuando los datos se parten por imagen o por
> lesión en vez de por paciente? Dame 5 referencias, cada una con la afirmación
> concreta que sostiene y su DOI.

Una sola corrida por tratamiento. No se repite la consulta ni se elige entre
respuestas.

## Tratamientos

| | Qué representa | Herramienta |
|---|---|---|
| A | Control: chat sin fuentes ni navegación | Claude (claude.ai), chat de incógnito, fuera de cualquier proyecto, sin búsqueda web. El modelo se registra en la respuesta. |
| B | Búsqueda en bases bibliográficas reales | Consensus (consensus.app), modo por defecto, sin «Profundo» ni filtros, con la traducción del navegador desactivada. |
| C | Anclaje: contexto cerrado con documentos propios | NotebookLM, con los archivos de `corpus-c.md` y nada más. |

El corpus de C son los textos originales de las referencias del anteproyecto que
ya están en la carpeta. Las fichas de `referencias/` no entran: son anotaciones
de quien las guardó, no la fuente.

De cada tratamiento se guardan la herramienta, el modelo o la versión visible, la
fecha y la hora, la respuesta completa en texto y una captura.

## Qué se extrae de cada respuesta

- Las primeras 5 referencias, en el orden en que aparecen. Si una se repite
  dentro de la misma respuesta, cuenta una vez.
- De cada referencia, la afirmación que la respuesta le atribuye, copiada literal.
- En C cuenta como referencia cualquier trabajo que la respuesta presente como
  sustento de una afirmación, sea uno de los documentos cargados o uno citado
  dentro de ellos.
- Si un tratamiento da menos de 5, se cuentan las que dé. Se registra cuántas
  faltaron y si se abstuvo de forma explícita («no está en las fuentes»).

## Las tres categorías

- **No existe.** No se encuentra una publicación con ese título y ese primer
  autor, ni por el DOI ni buscando el título en Google Scholar y en Crossref.
  Si el DOI no resuelve o lleva a otro trabajo, pero el título y el primer autor
  sí existen, la referencia no cuenta como inexistente: se marca «DOI erróneo» y
  se clasifica por el trabajo encontrado.
- **Existe pero no dice eso.** El trabajo existe, pero la afirmación atribuida
  no se localiza en él con su alcance: población, tipo de dato y esquema de
  partición. Una afirmación sobre otro mecanismo (por ejemplo, duplicados de
  imagen en lugar de agrupación por paciente) o sobre otro dominio cuenta aquí.
- **Utilizable.** El trabajo existe y la afirmación se localiza en él con su
  alcance. Se anota la página, la sección o una cita textual.

Acceso: se usa el texto completo si está disponible; si no, el resumen, y se
marca «solo resumen». Si la afirmación no se localiza en lo que se pudo leer, la
referencia va a «existe pero no dice eso», porque lo que no se localiza no se
puede usar. El análisis reporta cuántas llevan esa marca.

## Las dos pasadas

- Las referencias de los tres tratamientos se juntan y se mezclan con la
  semilla 1, sin la columna de tratamiento. La llave que asocia cada referencia a
  su tratamiento queda en un archivo aparte que no se abre hasta el análisis.
- La primera pasada se cierra con un commit. La hora de ese commit marca el
  comienzo de las 48 horas.
- La segunda pasada empieza al menos 48 horas después, sobre una hoja mezclada
  con la semilla 2, sin abrir la hoja ni las notas de la primera.
- Después de la segunda pasada, solo las referencias en que las dos no
  coinciden se leen una tercera vez, con el motivo escrito. Esa tercera lectura
  da la clasificación final.

El ciego es parcial: quien clasifica conoce el corpus de C y puede reconocer sus
referencias. Se declara así.

## Análisis

- Por tratamiento: cuántas referencias entregó de las 5 pedidas, y el conteo de
  cada categoría en la primera pasada, en la segunda y en la clasificación final.
- Proporción de utilizables por tratamiento, con intervalo de Wilson al 95 %,
  sobre las referencias que entregó.
- Consistencia: la tabla de 3 × 3 de la primera pasada contra la segunda, el
  número de referencias en que no coinciden, en qué categorías y por qué. El
  kappa de Cohen se reporta como dato secundario, sin inferencia, porque con
  15 referencias o menos es inestable.
- Entre tratamientos no se hace ninguna prueba de hipótesis. Las referencias de
  un tratamiento salen de una sola respuesta, así que no son independientes. Los
  intervalos valen para esta consulta, no para la herramienta en general.

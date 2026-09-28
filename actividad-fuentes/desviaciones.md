# Desviaciones del protocolo: experimento de la semana 1

Qué es: el registro de lo que se hizo distinto de `protocolo-experimento-v1.md`.
El protocolo no se cambia después de fijarlo, y lo que no se pudo cumplir se
anota aquí con su fecha, su motivo y su efecto sobre los resultados.

## 1. Corrida de A descartada: buscó en internet (2026-09-27)

**Qué pasó.** El tratamiento A se corrió en claude.ai con la búsqueda web
activa. Lo dice la persona, y la respuesta lo confirma desde su primera frase:
*"Voy a buscar estudios que cuantifiquen ese efecto de fuga de datos (data
leakage) en dermatología y a verificar cada DOI."*

**Por qué es una desviación.** El protocolo define A como *"Control: chat sin
fuentes ni navegación"*: *"Claude (claude.ai), chat de incógnito, fuera de
cualquier proyecto, sin búsqueda web"*. Una corrida con búsqueda no es el
tratamiento A.

**Qué se hizo.**
- La respuesta no se clasifica.
- Se conserva sin cambios en `respuestas/respuesta-A-descartada.md`. Se guardó
  el 2026-09-27 a las 18:47:07 (-0500). La hora de la corrida no se registró.

**Efecto.** El protocolo pide *"Una sola corrida por tratamiento. No se repite
la consulta ni se elige entre respuestas."* A se corre otra vez, porque la
primera corrida no fue del tratamiento A. No se elige entre dos respuestas de
A: la descartada no entra en ninguna hoja ni en el análisis.

## 2. Cambio de herramienta de A: de Claude en claude.ai a un modelo local en Ollama (2026-09-27)

**Qué cambia.** A pasa de *"Claude (claude.ai)"* a un modelo local, `llama3.1:8b`
en Ollama, corrido sin conexión a internet y sin instrucción de sistema. La
versión de Ollama y el identificador exacto del modelo van en la cabecera de
`respuestas/respuesta-A.md`.

**Motivo.** Ninguna de las dos opciones disponibles permite un chat sin
búsqueda:
- en la cuenta de la persona, claude.ai no deja apagar la búsqueda web;
- AI Studio no tiene un modelo gratuito.

**Efecto sobre el control.** Queda más estricto que el del protocolo: sin
ninguna conexión, no solo sin búsqueda.

**Límite, que se declara con los resultados.** Llama 3.1 de 8.000 millones de
parámetros es un modelo más pequeño que Claude, y de otra familia. Lo que mida
A vale para ese modelo, no para Claude ni para *"chat sin fuentes"* en general.
Al comparar A con B y C, la ausencia de fuentes va mezclada con el tamaño y la
familia del modelo, y el experimento no puede separar esos dos efectos.

## 3. Reglas de extracción añadidas (2026-09-27, 23:22 -0500)

**Por qué.** La sección «Qué se extrae de cada respuesta» del protocolo no
alcanzó para decidir seis casos de la extracción, marcados como «duda» en
`respuestas.csv`. La persona los decidió con estas reglas **antes de clasificar
ninguna referencia**, y antes de generar la hoja de la pasada 1.

1. **Una afirmación por referencia.** Si la respuesta no atribuye una afirmación
   propia a cada referencia, la afirmación es el rótulo en negrita de su ítem.
   Se aplica a las 5 referencias de A.
2. **Referencias repetidas.** Si una referencia aparece varias veces, la
   afirmación y el DOI se toman de la tabla «Cinco Referencias». Si ahí no hay
   DOI, se toma el de la lista «References». Se aplica a B:
   - Rotemberg et al.: el DOI de la tabla.
   - Jamaludin & Kim: el DOI de la lista.
   - Cassidy et al.: la afirmación de la tabla.

   **2b.** Jamaludin & Kim ocupa dos filas de esa tabla. Se toma la afirmación
   de la primera.
3. **Qué es una referencia.** Es referencia lo que nombra un trabajo, por su
   autor, su título o su DOI, y lo presenta como sustento.
   - La figura sin autor de B no cuenta, y Haggenmüller et al. queda como
     quinta referencia de B.
   - Los conjuntos de datos que nombra C (ISIC 2017, HAM10000, BCN20000) son el
     objeto de la afirmación, no su sustento, y Little et al. queda como quinta
     referencia de C.
4. **Abstención explícita.**
   - A se abstuvo. El texto de la abstención es su primera frase, completa y
     literal.
   - B y C no se abstuvieron.

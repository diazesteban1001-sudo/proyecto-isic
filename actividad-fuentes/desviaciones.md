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

## 4. La hoja de la pasada 1 delataba el tratamiento por el formato (2026-09-27, 23:28 -0500)

**Qué pasó.** La extracción copió cada campo con el marcado de su respuesta, y
cada tratamiento marcaba distinto:

| Tratamiento | DOI | Afirmaciones | Referencias |
|---|---|---|---|
| A | sin marca | rótulos en negrita | lista con viñetas, en varias líneas |
| B | en negrita o como URL | negritas | cursivas |
| C | entre comillas invertidas | — | — |

La hoja de la pasada 1 dejaba ver el tratamiento sin leer el contenido. Es una
pista que no venía de las respuestas, sino de cómo se extrajeron. El protocolo
declara el ciego parcial solo porque quien clasifica conoce el corpus de C.

**Qué se hizo.** Nadie había clasificado la hoja todavía.
1. Se retiraron la hoja y la llave.
2. Se limpió `respuestas.csv`:
   - se quitaron los asteriscos de negritas y cursivas y las comillas
     invertidas;
   - se quitaron las viñetas de las referencias de A;
   - los saltos de línea y los espacios repetidos se reducen a un espacio;
   - en el campo DOI se quitó el prefijo `https://doi.org/`.

   Comprobado: sin marcas ni espacios, cada campo es igual al anterior. Las
   URL que forman parte del texto de una referencia se quedan.
3. Los 15 id se volvieron a sortear, sin repetir ninguno de los anteriores.
   Los anteriores habían salido junto a su tratamiento en la salida del guion
   de extracción, y la hoja retirada los asociaba al formato.
4. Se regeneró la pasada 1 con la semilla 1, como fija el protocolo. Se
   comprobó que ningún campo de la hoja conserva marcas de formato.

**Qué no cambia.** Las 15 referencias, su orden dentro de cada respuesta y el
texto de cada campo. Las diferencias de contenido entre tratamientos se
quedan, porque son parte de las respuestas: por ejemplo, A etiqueta sus
referencias con «Título:» y «Autor:», y B las da en formato APA. Se declaran
con el ciego parcial.

## 5. Pasada 1: quién clasificó, cómo, y cómo se lee «existe pero no dice eso» (2026-09-29)

**Quién clasificó.** La pasada 1 la hizo Claude (Opus 5.5, en Claude Code), a
petición de la persona. El protocolo no dice quién clasifica, pero «Las dos
pasadas» mide cuánto coincide la clasificación consigo misma, así que supone el
mismo clasificador en las dos.

**Qué se abrió y qué no.**
- No se abrieron la llave, `tratamientos.csv`, `respuestas.csv`, `respuestas/`
  ni `corpus-c.md`.
- Sí se leyeron las primeras 30 líneas de cuatro archivos de `referencias/`
  (Little, Saeb, Kapoor y Cassidy), para saber si traían el texto completo. En
  dos de ellos esas líneas incluían el comienzo de la sección de citas que usa
  el proyecto. Se usaron además dos textos de `referencias/_texto-completo/`.
- El ciego sigue siendo parcial, como declara el protocolo: quien clasificó
  conoce el corpus de C.

**Cómo se comprobó.**
- Existencia: el DOI contra el servicio de resolución de doi.org y contra
  Crossref, en lugar de pegarlo en el navegador. Si no resolvía, el título con
  el primer autor en Google Scholar y en Crossref. La búsqueda de Scholar se
  probó antes con dos trabajos que existen.
- Afirmación: contra el texto completo de todas las que existen, tomado de
  Europe PMC, de PMC o de la página de la editorial. Donde la editorial pedía
  una verificación anti-bots, se leyó la versión publicada depositada en un
  repositorio institucional. Ninguna quedó con solo el resumen.
- Citas de las columnas ubicación y nota: comprobadas carácter a carácter contra
  el texto leído, con un control negativo.

**La ambigüedad.** El protocolo define «Existe pero no dice eso» y añade:
*"Una afirmación sobre otro mecanismo (por ejemplo, duplicados de imagen en
lugar de agrupación por paciente) o sobre otro dominio cuenta aquí."* La frase
admite dos lecturas:
1. El otro mecanismo o dominio se mide contra la consulta: una afirmación que la
   fuente sí sostiene, pero sobre otro tema, va a «no dice eso».
2. Se mide contra la fuente: la categoría solo compara la afirmación atribuida
   con lo que dice la fuente.

**Qué se decidió.** La persona eligió la segunda: «no dice eso» compara la
afirmación atribuida con la fuente, no con la consulta. Si la fuente dice lo que
se le atribuye, la referencia es «utilizable» aunque trate otro tema, y la falta
de pertinencia a la consulta queda en la nota. El ejemplo del protocolo se lee
entonces como una afirmación sobre agrupación por paciente atribuida a una
fuente que trata de duplicados.

**Orden de los hechos, que se declara.**
- Claude clasificó primero con la primera lectura, marcó el caso como duda y
  preguntó antes de cerrar la pasada.
- La persona decidió después de ver la clasificación. Conocía el efecto de cada
  lectura sobre los conteos, pero no la llave, así que la decisión no pudo
  favorecer a ningún tratamiento.
- La decisión cambió la categoría de algunas referencias. Cuáles y cuántas no se
  dice aquí, porque la pasada 2 no debe saberlo; está en la hoja de la pasada 1.
- La pasada se cerró con el commit «Actividad «Nada sin fuente»: pasada 1
  clasificada», del 2026-09-29 a las 15:09:34 (-0500). Esta sección se escribió
  después.

**Efecto sobre la pasada 2.**
- Se clasifica con la segunda lectura, para que las diferencias entre pasadas
  vengan de la clasificación y no de la regla.
- La hace también Claude, en una conversación nueva, sin abrir `pasada-1.csv`,
  la hoja de texto de la pasada 1 ni la conversación de la pasada 1.
  `pasada-1.csv` está versionada, así que esto es una instrucción, no una
  barrera.
- Límite: Claude no guardó nada de esta pasada en su memoria entre
  conversaciones. Las 48 horas no cumplen para Claude la función de olvido que
  tendrían para una persona: la repetición mide cuánto varía el clasificador
  ante la misma hoja, no cuánto recuerda. Se mantienen porque el protocolo las
  fija.

**Qué no cambia.** El texto del protocolo; esta sección fija cómo se lee.

## 6. Pasada 2: sin esperar 48 horas (2026-09-29)

**Qué pasó.** La pasada 2 la hizo Claude Code en una sesión nueva. Se cerró
con el commit «Actividad «Nada sin fuente»: pasada 2 clasificada», del
2026-09-29 a las 15:38:30 (-0500). La pasada 1 se cerró con el commit
«Actividad «Nada sin fuente»: pasada 1 clasificada», del 2026-09-29 a las
15:09:34 (-0500). Las dos horas se comprobaron en el historial. Entre un commit
y otro pasaron 28 minutos y 56 segundos, no 48 horas.

**Por qué, según la persona.** Las 48 horas existen para que una persona olvide
su primera clasificación. Una sesión nueva de Claude Code no recuerda la
pasada 1, así que esperar no cumplía esa función.

**Cambio respecto de la sección 5.** Aquella sección decía que las 48 horas se
mantenían porque el protocolo las fija. Esta decisión la deja sin efecto.

**Cómo se garantizó el ciego, según la persona.** A la sesión de la pasada 2 se
le prohibió leer la pasada 1, la llave y el historial de git. Es una
instrucción, no una barrera: los tres están en el repositorio, como ya
advertía la sección 5. El commit de la pasada 2 no describe cómo se clasificó
ni qué se abrió. Lo que dice este párrafo sobre el ciego lo declara la persona,
y el repositorio no permite comprobarlo.

**Efecto.** La consistencia entre pasadas mide cuánto varían dos sesiones de
Claude Code ante la misma hoja y con la misma regla (sección 5). No mide cuánto
coincide consigo misma una persona al cabo de 48 horas.

## 7. Tercera lectura: quién la hizo y qué sabía (2026-09-29)

**Qué se leyó.** Solo la referencia en que las dos pasadas no coinciden. Es 1
de 15, con id 126 (Jamaludin y Kim, 2026): «existe pero no dice eso» en la
pasada 1 y «utilizable» en la pasada 2. La clasificación y el motivo están en
`tercera-lectura.csv`.

**Quién la hizo.** Claude Code, a petición de la persona, en la misma sesión
que construyó `respuestas.csv`.

**Qué sabía quien leyó. No fue una lectura ciega.**
- Esta sesión extrajo las respuestas y sabe de qué tratamiento sale cada
  referencia.
- Leyó las dos clasificaciones anteriores y sus notas antes de leer la fuente.
- No abrió la llave. `analizar.py` la lee después.

El protocolo no pide que la tercera lectura sea ciega, pero es la que da la
clasificación final, así que se declara.

**Cómo se leyó.**
- Existencia: el DOI, contra doi.org y Crossref.
- Afirmación: contra el texto completo en IEEE Xplore, leído con el navegador
  integrado.
- Las cuatro citas del motivo se comprobaron literales en el texto de la
  página, con un control negativo.

**Qué no cambia.** Las pasadas 1 y 2. La tercera lectura solo fija la
clasificación final de la referencia discrepante.

## 8. Las dos pasadas, revisadas por la persona (2026-10-03 y 2026-10-05)

**Qué pasó, según la persona.** La persona revisó las dos pasadas de Claude Code
sobre las hojas ya clasificadas, comprobó cada referencia contra su fuente y
confirmó sus resultados:
- la pasada 1, el 2026-10-03 a las 13:00 (-0500);
- la pasada 2, el 2026-10-05 a las 15:00 (-0500).

**Qué encontró.** Coincidió con cada clasificación de las dos pasadas, también
en Jamaludin y Kim (id 126), que la pasada 1 pone en «existe pero no dice eso»
y la pasada 2 en «utilizable». Ninguna hoja cambió.

**Qué no hay.** Ningún commit ni registro de las revisiones. Las fechas, las
horas y el resultado los declara la persona, y el repositorio no permite
comprobarlos.

**Qué fueron y qué no.** No son pasadas independientes:
- se hicieron con las categorías y las notas de Claude a la vista;
- los resultados del experimento estaban escritos desde el 2026-09-29
  (`resultados.md`);
- entre una revisión y otra pasaron 50 horas, pero sobre hojas ya clasificadas
  ese intervalo no cumple la función que le da el protocolo.

**Efecto.**
- Las hojas, la tercera lectura y los resultados no cambian.
- La consistencia de `resultados.md` sigue midiendo dos sesiones de Claude Code
  (sección 6). La revisión dice que la persona está de acuerdo con cada
  clasificación, no cuánto coincide consigo misma.
- En la 126, la persona coincidió con las dos pasadas, que no coinciden entre
  sí. La clasificación final sigue siendo la de la tercera lectura (sección 7).

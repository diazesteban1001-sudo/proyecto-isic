# Un agente consultor estadístico sobre el caso ISIC 2024

**Trabajo final — Consultoría e Investigación**
Borrador generado por la skill `sintesis-consultoria` a partir de `outputs/`.
Fecha: 2026-08-12.

> **Cómo leer las cifras de este informe.** Cada número lleva una marca `[T#]`
> que remite a la fila correspondiente del Anexo de trazabilidad (sección 10),
> donde consta el archivo y el campo exacto del que sale. Ningún número del
> cuerpo procede de la memoria del agente. Las pocas cifras que provienen de
> fuentes externas y no de `outputs/` están marcadas `[E#]` y separadas en el
> anexo, para que la distinción sea visible y no haya que confiar en nadie.

---

## 1. Resumen ejecutivo

Este proyecto no intenta ganar la competencia ISIC 2024 de Kaggle. Intenta algo
distinto y, para una materia de consultoría, más pertinente: construir un agente
que se comporte como un **consultor estadístico** ante una pregunta clínica —que
ejecute instrumentos de medición, lea sus resultados, resuelva las
contradicciones entre ellos, y emita una recomendación defendible con supuestos y
limitaciones explícitos.

La arquitectura separa deliberadamente dos cosas que suelen confundirse: los
**instrumentos**, que miden y reportan sin interpretar, y el **consultor**, que
interpreta. Cuatro skills instrumento (`eda-diagnostico`, `diseno-validacion`,
`auditoria-de-fugas`, `modelado-baseline`) producen archivos estructurados; una
quinta (`sintesis-consultoria`) los lee y produce este informe. Es la misma
separación que existe entre el software estadístico y el estadístico.

El caso ISIC 2024 se eligió porque su métrica **codifica la función de utilidad
del cliente**. El organizador no evalúa el AUC completo sino el área bajo la
curva ROC restringida a sensibilidad superior al 80%, y justifica esa decisión en
términos clínicos, no estadísticos `[E1]`. Un falso negativo en dermatología es
un melanoma no detectado. La región del espacio ROC donde la sensibilidad es baja
sencillamente no le interesa al cliente, y el organizador la descartó por escrito.

Los resultados sostienen la tesis mejor de lo previsto. Tres hallazgos concretos:

1. **Partir los datos al azar habría inflado toda medición del proyecto.** Bajo
   una partición aleatoria a nivel de fila, el 99,04% de los pacientes `[T18]`
   quedaría repartido entre entrenamiento y validación. No es un riesgo teórico:
   es lo que ocurre por defecto.
2. **Once columnas del conjunto de entrenamiento no existen en el de prueba**
   `[T10]`, y tres familias distintas de razones lo explican. Un modelo que las
   use produce números excelentes e inservibles.
3. **El modelo de mayor capacidad falla de un modo que la métrica estándar no
   detecta.** Sin ajustar por el desbalance, el gradient boosting obtiene un pAUC
   de 0,0013 `[T30]` —por debajo del 0,02 que obtendría el azar `[T27]`— mientras
   su AUC convencional sugiere un desempeño mediocre pero no alarmante. La
   métrica del cliente ve el problema; la métrica por defecto no.

La recomendación al cliente no es "use el modelo 2b". Es más modesta y se
detalla en la sección 9.

---

## 2. Contexto y objetivo

La competencia ISIC 2024 plantea identificar lesiones cancerosas a partir de
recortes de imagen extraídos de fotografía corporal total en 3D, acompañados de
metadatos tabulares. Este proyecto trabaja **solo con la metadata tabular**: es
suficiente para todos los problemas estadísticamente interesantes del caso
—desbalance extremo, agrupación por paciente, fugas de información— y no exige
GPU.

El caso se eligió sobre otras alternativas (RSNA rodilla, RSNA columna lumbar)
precisamente porque esas requieren procesamiento de imagen 3D y aportan poco
desde lo estadístico. Aquí, en cambio, la estructura de los datos plantea
preguntas de diseño antes de que aparezca ningún modelo.

**La pregunta que el consultor debe responder no es "¿qué modelo maximiza la
métrica?"** sino "¿qué se puede afirmar con honestidad sobre la detección de
lesiones malignas con estos datos, y con qué grado de confianza?".

Un matiz que conviene fijar desde el principio, porque condiciona todo lo demás:
**la etiqueta no es simétrica**. Los casos positivos están confirmados por
patología. Los negativos, en su gran mayoría, nunca fueron biopsiados: se asumen
benignos por evaluación clínica `[E2]`. La clase negativa arrastra ruido de
etiqueta estructural. Esto va en las limitaciones (sección 8) y no como nota al
pie.

---

## 3. Metodología: instrumentos y consultor

### 3.1 La cadena de skills

| Skill | Función | Tipo |
|---|---|---|
| `eda-diagnostico` | Perfil de datos, faltantes, desbalance, estructura de grupos | instrumento |
| `diseno-validacion` | Propone y **verifica** el esquema de validación cruzada | instrumento |
| `auditoria-de-fugas` | Chequeos de fuga estructural y escaneo univariado | instrumento |
| `modelado-baseline` | Modelos de referencia con la métrica oficial | instrumento |
| `sintesis-consultoria` | Lee todo `outputs/` y produce este informe | interpretación |

Cada instrumento escribe dos archivos: un `.json` con resultados completos y un
`.md` de resumen acotado a 15 líneas. Y cada uno declara explícitamente en su
documentación: *no interpretes los resultados aquí*.

### 3.2 Por qué la separación es el argumento, no un detalle de implementación

La tentación al construir un agente de análisis de datos es que el mismo
componente mida e interprete. Separarlos tiene tres consecuencias verificables:

- **La interpretación es auditable.** Si el informe afirma algo, existe un
  archivo que lo respalda. La verificación deja de ser un acto de fe.
- **Los instrumentos no pueden mentir a su favor.** Un instrumento que
  interpretara sus propios resultados tendería a justificarlos.
- **Las contradicciones salen a la superficie en vez de resolverse en silencio.**
  El caso de `tbp_lv_nevi_confidence` (sección 6.3) es exactamente eso: el
  instrumento marcó una columna y se detuvo en una pregunta que no podía
  responder. Resolverla exigió leer una fuente externa.

### 3.3 Tres reglas que gobernaron el trabajo

1. **Trazabilidad total.** Ninguna cifra del informe aparece si no está en un
   archivo de `outputs/`. Este borrador se somete a un verificador automático que
   extrae todos sus números y comprueba que tengan respaldo.
2. **Nada de memoria como fuente.** El agente no cita de memoria las reglas de la
   competencia ni la definición de la métrica. Cuando Kaggle resultó ilegible
   —sus páginas se renderizan con JavaScript y no devuelven contenido a un
   cliente sin navegador— se resolvió con copias literales versionadas en
   `referencias/`, no completando de memoria.
3. **Antes de borrar código que parece muerto, comprobar si conectarlo cambia el
   resultado.** Esta regla se añadió a mitad de proyecto, después de que el
   patrón apareciera tres veces (sección 3.4).

### 3.4 Las cuatro skills tenían defectos, y encontrarlos fue parte del trabajo

Ninguna skill se dio por buena sin correrla contra los datos reales. Las cuatro
tenían al menos un defecto. Los más instructivos:

- **Un chequeo vacío de contenido.** La detección de duplicados exactos incluía
  la clave primaria entre las columnas comparadas, de modo que nunca podía
  encontrar nada. Daba cero, y el cero era correcto por la razón equivocada.
- **Una rama inalcanzable.** En la auditoría de fugas, una condición comparaba
  contra `None` un valor que nunca podía ser `None`. El efecto: nueve de las diez
  preguntas abiertas que la skill debía plantear se perdían en silencio.
- **Una corrección a medio cablear.** En el modelado, `StandardScaler` estaba
  importado y nunca usado. Parecía código sobrante. No lo era: sin escalar, la
  regresión logística no convergía, y el número reportado era el del optimizador
  detenido a mitad de camino, no el del modelo.
- **Una métrica mal implementada.** La primera versión del pAUC aplicaba una
  corrección que el algoritmo oficial no aplica. Un clasificador perfecto habría
  obtenido 0,12 en vez de 0,20. Se detectó comparando contra el script del
  organizador y se verificó la corrección en 200 casos aleatorios `[E3]`.

Que los cuatro instrumentos estuvieran defectuosos y los cuatro defectos fueran
detectables **por confrontación con los datos reales o con la fuente primaria**
es, en sí, un resultado del proyecto.

---

## 4. Hallazgos del análisis exploratorio

Fuente: `outputs/eda-diagnostico.json`.

El conjunto de entrenamiento tiene **401.059 filas** `[T1]` y **55 columnas**
`[T2]`.

### 4.1 Desbalance extremo

De las 401.059 lesiones, **393 son positivas** `[T3]` y **400.666 negativas**
`[T4]`: un **0,098%** de prevalencia `[T5]`.

La magnitud importa por una razón operativa concreta: un clasificador que prediga
"benigno" siempre acierta el 99,9% de las veces. Cualquier métrica basada en tasa
de acierto es inútil aquí, y cualquier modelo entrenado sin ajustar por el
desbalance está expuesto a degenerar. La sección 7 muestra que eso ocurre, y de
una forma menos evidente que la esperada.

### 4.2 Estructura de grupos: el hallazgo que condiciona todo el diseño

Las 401.059 lesiones provienen de **1.042 pacientes** `[T6]`. El promedio es de
**384,89 lesiones por paciente** `[T7]`, con mediana **241,5** `[T8]` y un
máximo de **9.184** `[T9]` en un solo paciente.

Esto no es un dato descriptivo: es una restricción de diseño. Con ese promedio
de lesiones por paciente, las del mismo individuo comparten
características de piel, edad, tipo de captura y sesgo del centro. Si caen a
ambos lados de una partición, el modelo reconoce al paciente, no a la patología.
La sección 5 lo cuantifica.

### 4.3 Datos faltantes y calidad

Diez columnas tienen al menos un valor faltante. Entre las clínicamente
relevantes: `sex` con **11.517** ausentes (**2,872%**) `[T13]`,
`anatom_site_general` con **5.756** (**1,435%**) `[T14]`, y `age_approx` con
**2.798** (**0,698%**) `[T15]`.

Las demás columnas con faltantes masivos —`lesion_id`, `iddx_2` a `iddx_5`,
`mel_mitotic_index`, `mel_thick_mm`— son precisamente las que la auditoría de
fugas excluye (sección 6). Su ausencia no es un problema de calidad de datos:
es la huella de que solo existen para un subconjunto diagnosticado.

**Duplicados exactos: 0** `[T12]`, excluyendo del cotejo las dos columnas
identificadoras `isic_id` y `lesion_id`. La exclusión no es cosmética: con la
clave primaria incluida el chequeo no podía detectar nada.

**Una columna constante:** `image_type`. Sin valor informativo; se excluye del
modelado.

---

## 5. Diseño de validación: cuantificar lo que se evitó

Fuente: `outputs/diseno-validacion.json`.

### 5.1 El esquema

Se construyó una partición **StratifiedGroupKFold** `[T16]` con **5 folds**
`[T17]` y semilla **42** `[T18b]`, agrupando por `patient_id` y estratificando
por la etiqueta. La estratificación no es un refinamiento opcional: con 393
positivos repartidos en 1.042 pacientes, un fold sin un solo caso positivo dejaría
la métrica indefinida —el script oficial lanza un error si el vector de etiquetas
tiene una sola clase.

De los 1.042 pacientes, **259 tienen al menos una lesión positiva** `[T19]`.

### 5.2 La verificación, que es el punto

El instrumento no asume que la partición esté bien construida: lo comprueba de
forma independiente, buscando si algún paciente aparece simultáneamente en
entrenamiento y validación dentro del mismo fold. Resultado: **ninguno**
`[T20]`.

Ese `false` es el resultado esperado, y ahí está su valor. Un chequeo que solo
puede dar el resultado bueno no vale nada, así que se verificó también al revés:
corrompiendo deliberadamente la asignación de un paciente, el detector cambia a
`true`. Solo entonces el `false` significa algo.

### 5.3 La cifra central: cuánta fuga se evitó

El instrumento corre además una partición aleatoria a nivel de fila —el 80/20 por
defecto de cualquier tutorial—, con la misma semilla, ignorando la columna de
paciente. Resultado: **1.032 de los 1.042 pacientes** `[T21]`, un **99,04%**
`[T18]`, quedarían repartidos entre entrenamiento y validación.

Esta es la evidencia central de la sección y merece leerse despacio. No es que
partir al azar sea *arriesgado*: es que en este dataset la fuga por partición
aleatoria **es el caso por defecto**, y afecta a prácticamente todos los
pacientes. Cualquier número producido bajo ese esquema —y buena parte de los
notebooks públicos de una competición así lo usan— mide la capacidad del modelo
de reconocer pacientes vistos, no lesiones malignas.

### 5.4 Balance de los folds

Los positivos en validación por fold son **78, 78, 83, 77 y 77** `[T22]`, sobre
particiones de entre **80.210 y 80.216 filas** `[T23]`. El reparto es
razonablemente uniforme, pero la cifra absoluta —entre 77 y 83 casos positivos
por fold `[T22]`— es pequeña, y condiciona cuánta precisión puede tener cualquier estimación
de desempeño. Se retoma en la sección 7.3.

---

## 6. Auditoría de fugas

Fuente: `outputs/auditoria-de-fugas.json`.

### 6.1 Fuga estructural: once columnas que no existen al predecir

El conjunto de entrenamiento tiene once columnas que el de prueba no tiene
`[T10]`. No son una anomalía menor: son la mayor fuente de fuga del caso, y se
agrupan en tres familias con implicaciones distintas.

| Familia | Columnas | Por qué se excluye |
|---|---|---|
| Taxonomía diagnóstica | `iddx_full`, `iddx_1` … `iddx_5` | Es la etiqueta con otro nombre. |
| Variables post-biopsia | `mel_mitotic_index`, `mel_thick_mm` | Solo existen tras la biopsia, y solo para melanomas. Usarlas es predecir el pasado con información del futuro. |
| Identificador y derivadas | `lesion_id`, `tbp_lv_dnn_lesion_confidence` | No son post-biopsia, pero al no estar en el conjunto de prueba, un modelo que las use es inservible en inferencia. |

La distinción entre las tres familias importa porque **el criterio operativo para
excluir no es el mismo**. Las dos primeras son fuga en sentido estricto:
información posterior al evento que se quiere predecir. La tercera no lo es —una
puntuación de confianza del sistema de imagen no sabe nada del diagnóstico— pero
se excluye igual, por un motivo puramente práctico: no estará disponible cuando
haya que predecir de verdad.

Un consultor que solo repita "estas once columnas tienen fuga" está simplificando.
Son once columnas que hay que excluir por tres razones distintas, y solo dos de
ellas son fuga.

Se excluyen además `image_type`, por constante, e `isic_id`, por identificador
`[T24]`. Quedan **41 columnas** utilizables `[T25]`.

### 6.2 Escaneo univariado: ninguna columna delata fuga oculta

Sobre las 41 columnas supervivientes se calculó el AUC fuera de muestra de cada
una por separado, usando la misma partición agrupada por paciente —usar una
partición ingenua habría metido en el detector justo la fuga que busca.

El umbral de sospecha se fijó en **0,90** `[T26]`. **Ninguna columna lo supera.**
La más predictiva es `tbp_lv_H` con AUC **0,8053** `[T27]`, seguida de
`tbp_lv_deltaB` con **0,7541** `[T28]` y `tbp_lv_Hext` con **0,7195** `[T29]`.

Un resultado negativo, y es una buena noticia: tras excluir las once columnas
estructurales, no queda ninguna variable que por sí sola prediga el diagnóstico
casi perfectamente. La fuga de este caso era estructural, no encubierta.

### 6.3 Una pregunta que el instrumento no podía responder

El instrumento marca por nombre cualquier columna que sugiera derivación
posterior al diagnóstico, y deja constancia de diez preguntas abiertas `[T30]`.
Nueve se responden con lo ya sabido: son las columnas `iddx_*`, `mel_*` y
`tbp_lv_dnn_lesion_confidence`, todas ausentes del conjunto de prueba.

La décima no. **`tbp_lv_nevi_confidence` contiene la palabra "confidence" pero
sí está presente en el conjunto de prueba**, y obtiene un AUC univariado de
**0,6457** `[T31]` — moderado, ni despreciable ni sospechoso. El instrumento
formuló la pregunta correcta y se detuvo: *¿por qué existiría en ambos conjuntos
si fuera derivada del diagnóstico?*

Responderla exigió ir a la fuente primaria. El artículo que describe el dataset
define la columna como la probabilidad estimada por una red neuronal
convolucional de que la lesión sea un nevus, y aclara que el prefijo `lv`
corresponde a *Lesion Visualizer*, el software de Canfield Scientific que
acompaña al equipo de fotografía 3D `[E4]`. Todas las columnas `tbp_lv_*` son
mediciones que la máquina calcula sobre la imagen capturada, no resultados de
patología.

**Conclusión: la columna es legítima.** Deriva de la imagen, está disponible al
predecir, y su AUC moderado es exactamente lo que cabe esperar de un clasificador
de nevus, no la firma de una fuga.

Con una salvedad que se declara como supuesto y no se esconde: el artículo no
indica si las aproximadamente 57.000 lesiones con que se entrenó ese clasificador
se solapan con el dataset de la competencia `[E5]`. Si se solaparan, la
puntuación arrastraría de forma indirecta etiquetas de dermatólogo sobre las
mismas lesiones. No es verificable con la fuente disponible y no cambia la
decisión —el criterio operativo sigue siendo la disponibilidad al predecir— pero
el informe no puede afirmar independencia total.

Este caso es la mejor ilustración de la arquitectura funcionando: el instrumento
midió y planteó una duda honesta; el consultor la resolvió leyendo una fuente
externa y distinguiendo "nombre sospechoso" de "fuga real".

---

## 7. Resultados de modelado

Fuente: `outputs/modelado-baseline.json`.

### 7.1 La métrica, y por qué su escala no es la que uno supone

Todos los resultados de esta sección usan el **pAUC sobre 80% de sensibilidad**,
la métrica oficial. Su implementación se verificó contra el script del organizador
antes de reportar ningún número `[T32]`.

La escala tiene una propiedad que invalida la lectura intuitiva: **el azar no
vale 0, vale 0,02** `[T33]`, y el máximo alcanzable es **0,2** `[T34]`. Un modelo
con pAUC 0,10 no está "a la mitad": está al 44% del recorrido entre el azar y el
clasificador perfecto. Por eso todos los resultados se expresan también como
porcentaje de ese recorrido.

### 7.2 Los cuatro niveles

| Nivel | Modelo | pAUC medio | Desv. entre folds | % del recorrido azar→perfecto |
|---|---|---|---|---|
| 0 | `tbp_lv_H` sola | 0,0809 `[T35]` | ±0,0247 `[T36]` | 33,8% `[T37]` |
| 1 | Regresión logística balanceada | 0,1331 `[T38]` | ±0,0173 `[T39]` | 62,8% `[T40]` |
| 2a | Gradient boosting sin balancear | 0,0013 `[T30b]` | ±0,0015 `[T41]` | −10,4% `[T42]` |
| 2b | Gradient boosting balanceado | 0,1451 `[T43]` | ±0,0055 `[T44]` | 69,5% `[T45]` |

### 7.3 Lectura de los resultados

**El piso univariado es más bajo de lo que aparenta.** La columna `tbp_lv_H`
obtiene un AUC estándar de 0,8053 `[T27]`, que suena a un predictor
razonablemente fuerte. En la métrica del cliente cae al 33,8% del recorrido
posible `[T37]`. La señal de esa columna no está donde la sensibilidad es
clínicamente aceptable. Es el argumento central de la tesis expresado en dos
números del mismo dato: **la elección de métrica cambia la conclusión, no solo
la cifra.**

**Los modelos combinados justifican su complejidad.** Tanto la logística (62,8%)
como el boosting balanceado (69,5%) recorren cerca del doble de distancia que la
mejor columna sola. Combinar variables aporta algo real, y no era evidente de
antemano.

**El nivel 2a es el hallazgo más citable del proyecto.** Con pAUC de 0,0013
`[T30b]`, queda *por debajo del piso aleatorio* de la métrica. Y el modo de fallo
no es el de manual. Uno espera que un modelo sin ajuste de desbalance "prediga
siempre negativo" y quede plano. Lo que ocurre es distinto y peor: satura en
probabilidad máxima sobre un puñado de casos negativos y los coloca por encima de
los positivos reales, arrasando justo la región de sensibilidad alta que la
métrica evalúa. Su AUC convencional —medido como diagnóstico auxiliar, no
reportado aquí porque no está en `outputs/` y este informe no cita cifras sin
respaldo— sugería un desempeño mediocre pero nada alarmante.

La única diferencia entre 2a y 2b es el parámetro de balanceo `[T46]`. Mismo
modelo, misma semilla, mismos folds.

**La estabilidad discrimina más que la media.** El nivel 2b no solo tiene mejor
media que el nivel 1 (0,1451 frente a 0,1331) sino que es **más de tres veces más
estable** entre folds: ±0,0055 `[T44]` frente a ±0,0173 `[T39]`.

Y aquí el consultor debe frenar en vez de rematar: **la diferencia de medias
entre 2b y 1 es de 0,012, menor que la desviación entre folds del nivel 1**. Con
77 a 83 positivos por fold `[T22]`, esa dispersión no permite afirmar que 2b sea
superior a partir de las medias.

### 7.4 Comparación pareada por fold

Comparar dos desviaciones marginales no es la forma correcta de hacerlo. Ambos
niveles se evaluaron sobre **los mismos cinco folds**, así que la dificultad de
cada fold —cuántos positivos tiene, qué pacientes le tocaron— afecta a los dos
modelos a la vez. Es un factor de ruido común que se puede eliminar comparando
fold a fold en vez de media contra media:

| Fold | Nivel 1 `[T48]` | Nivel 2b `[T49]` | Diferencia |
|---|---|---|---|
| 1 | 0,1524 | 0,1509 | **−0,0015** |
| 2 | 0,1253 | 0,1386 | +0,0133 |
| 3 | 0,1553 | 0,1499 | **−0,0054** |
| 4 | 0,1142 | 0,1478 | +0,0336 |
| 5 | 0,1184 | 0,1385 | +0,0201 |

La comparación pareada **no refuerza la superioridad de 2b: la debilita.**

- **2b gana en tres folds de cinco.** En dos pierde. Un resultado que se
  distingue poco de lanzar una moneda.
- **La media de las diferencias es 0,0120, y su desviación típica es 0,0160** —
  mayor que la propia media. La dispersión del efecto excede su tamaño.
- Un intervalo *t* al 95% sobre esas cinco diferencias va de **−0,008 a
  +0,032**: contiene el cero holgadamente.

Ese intervalo, además, es **optimista**, no conservador. Los folds de una
validación cruzada comparten la mayor parte de sus datos de entrenamiento, de
modo que las cinco diferencias no son observaciones independientes y el
intervalo *t* ordinario subestima la variabilidad real. La conclusión honesta es
por tanto más débil todavía que lo que sugiere el propio intervalo.

Queda una asimetría real y que sí se sostiene: 2b es sensiblemente **más
estable** —±0,0055 `[T44]` frente a ±0,0173 `[T39]`—, y su peor fold (0,1385) es
mejor que los dos peores del nivel 1 (0,1142 y 0,1184). Un modelo cuyo
desempeño depende menos de qué pacientes cayeron en validación es preferible
ante datos nuevos, y ese argumento no descansa en la diferencia de medias.

**Lo que no se puede afirmar:** que 2b sea superior al nivel 1 en pAUC medio.
Con cinco folds y entre 77 y 83 positivos en cada uno `[T22]`, el diseño
no tiene resolución para sostenerlo. Cuantificar la incertidumbre como es debido
—remuestreo a nivel de paciente, o un número mayor de repeticiones de la
validación cruzada— queda fuera del alcance de este trabajo y se declara como
tal.

---

## 8. Limitaciones

Ordenadas por cuánto comprometen las conclusiones.

**1. La clase negativa tiene ruido de etiqueta estructural.** Los positivos están
confirmados por patología; la mayoría de los negativos nunca fue biopsiada y se
asume benigna por evaluación clínica `[E2]`. Todo el desempeño reportado se mide
contra una referencia que es sólida en una clase y presunta en la otra. Un caso
maligno no detectado por el dermatólogo y nunca biopsiado cuenta aquí como
negativo, y un modelo que lo señalara sería penalizado por acertar.

**2. No hay conjunto de prueba real.** El archivo de prueba disponible es un
marcador de posición `[T47]`, sin etiquetas. Todo lo reportado es validación
cruzada sobre entrenamiento. No hay ninguna estimación de desempeño fuera de
muestra en el sentido fuerte, y el leaderboard privado no es accesible.

**3. El número de positivos es pequeño en términos absolutos.** 393 casos
`[T3]`, entre 77 y 83 por fold `[T22]`. Cualquier estimación de desempeño tiene
una precisión limitada por ese número, con independencia de cuántas filas totales
haya.

**4. Solo se usó la metadata tabular.** No se tocaron las imágenes. Los
resultados son un piso de lo alcanzable, no un techo.

**5. Ningún hiperparámetro fue ajustado.** Los modelos usan configuración por
defecto, deliberadamente. Los números de la sección 7 son referencias, no el
mejor desempeño alcanzable.

**6. La métrica y su umbral son una elección del organizador, no una verdad.**
Kaggle evalúa sobre 80% de sensibilidad; el esquema de premios del propio
organizador ISIC usa 88% `[E7]` sobre el mismo algoritmo. Son dos evaluaciones
distintas con dueños distintos. Este proyecto replica la de Kaggle, y esa
decisión es una convención adoptada, no un hallazgo.

**7. Queda una condición de la competencia sin verificar.** Los límites de
cómputo y el acceso a internet en las entregas no pudieron confirmarse: la página
correspondiente no está entre las copias disponibles y no se completó de memoria.
No afecta a los resultados estadísticos, pero sí a cualquier afirmación sobre
viabilidad de despliegue.

---

## 9. Conclusiones y recomendación

### 9.1 Qué se puede afirmar

- **La agrupación por paciente no es opcional en este dataset.** El 99,04%
  `[T18]` de los pacientes quedaría repartido bajo una partición aleatoria. Es la
  decisión de diseño con mayor impacto de todo el proyecto, y se toma antes de
  entrenar nada.
- **Once columnas deben excluirse** `[T10]`, por tres razones distintas que
  conviene no confundir (sección 6.1).
- **La metadata tabular tiene señal real.** Los modelos combinados alcanzan entre
  el 62,8% `[T40]` y el 69,5% `[T45]` del recorrido entre el azar y el
  clasificador perfecto, frente al 33,8% `[T37]` de la mejor columna sola.
- **El ajuste por desbalance no es un refinamiento, es un requisito.** Sin él, el
  modelo de mayor capacidad queda por debajo del azar en la métrica del cliente
  `[T30b]`.

### 9.2 Qué NO se puede afirmar

- **Que el nivel 2b sea superior al nivel 1.** La comparación pareada por fold
  —la forma correcta de hacerla, porque ambos se evaluaron sobre los mismos
  folds— lo deja claro: 2b gana en **tres de cinco** folds `[T48]` `[T49]`, la
  desviación de las diferencias (0,0160) supera a su media (0,0120), y el
  intervalo contiene el cero (sección 7.4). La estabilidad sí favorece a 2b,
  pero eso es un argumento distinto del de superioridad en media.
- **Que ninguno de estos modelos sirva para uso clínico.** No se probó, no se
  midió calibración, no hay conjunto de prueba real y la referencia de la clase
  negativa es presunta. Nada en este trabajo respalda esa afirmación.
- **Qué desempeño tendría el sistema en una población distinta.** Los datos
  provienen de siete centros dermatológicos `[E6]`; nada aquí mide
  generalización fuera de ellos.

### 9.3 Recomendación

Si el cliente fuera real, la recomendación sería en este orden:

1. **Adoptar el esquema de validación agrupado por paciente como requisito no
   negociable**, y auditar cualquier resultado previo obtenido sin él. Es la
   corrección de mayor impacto y la más barata.
2. **Preferir la regresión logística balanceada como modelo de referencia
   operativo**, no porque supere al boosting —no lo hace— sino porque su
   desempeño es indistinguible del de 2b con los datos disponibles (gana en dos
   de los cinco folds `[T48]` `[T49]`), y es interpretable. Ante empate en evidencia, el modelo
   explicable gana. Si trabajo posterior con más datos o remuestreo adecuado
   confirmara la ventaja de 2b, la decisión debería revisarse.
3. **Tratar el ajuste por desbalance como parte del contrato del modelo**, no
   como un hiperparámetro más. El nivel 2a demuestra que omitirlo produce un
   fallo silencioso bajo métricas convencionales.
4. **Resolver la calidad de la etiqueta negativa antes de invertir en
   modelos más complejos.** Es la limitación que más compromete las
   conclusiones, y ninguna mejora de modelado la compensa.
5. **No desplegar nada sin una evaluación prospectiva.** Todo lo medido aquí es
   retrospectivo y sobre datos de entrenamiento.

### 9.4 Sobre la tesis del proyecto

El caso confirma la distinción que motivó el trabajo. Un agente optimizador
habría reportado que el gradient boosting alcanza cierto AUC y habría seguido
adelante. El consultor detectó que ese mismo modelo, bajo la métrica que codifica
la utilidad real del cliente, es peor que lanzar una moneda; que la columna más
predictiva bajo AUC estándar pierde la mitad de su valor bajo la métrica clínica;
y que la decisión de mayor impacto del proyecto no fue elegir un modelo sino
elegir cómo partir los datos.

Ninguna de esas tres conclusiones aparece si uno solo optimiza la métrica sin
preguntarse por qué el cliente la eligió.

---

## 10. Anexo de trazabilidad

### 10.1 Cifras procedentes de `outputs/`

| Marca | Afirmación | Valor | Archivo y campo |
|---|---|---|---|
| T1 | Filas del conjunto de entrenamiento | 401059 | `eda-diagnostico.json` → `fuente.n_filas` |
| T2 | Columnas del conjunto de entrenamiento | 55 | `eda-diagnostico.json` → `fuente.n_columnas` |
| T3 | Lesiones positivas | 393 | `eda-diagnostico.json` → `desbalance_target.conteos["1"]` |
| T4 | Lesiones negativas | 400666 | `eda-diagnostico.json` → `desbalance_target.conteos["0"]` |
| T5 | Prevalencia de positivos (%) | 0.098 | `eda-diagnostico.json` → `desbalance_target.pct_positivos` |
| T6 | Número de pacientes | 1042 | `eda-diagnostico.json` → `estructura_grupos.n_grupos` |
| T7 | Lesiones por paciente (media) | 384.89 | `eda-diagnostico.json` → `estructura_grupos.filas_por_grupo.media` |
| T8 | Lesiones por paciente (mediana) | 241.5 | `eda-diagnostico.json` → `estructura_grupos.filas_por_grupo.mediana` |
| T9 | Lesiones por paciente (máximo) | 9184 | `eda-diagnostico.json` → `estructura_grupos.filas_por_grupo.max` |
| T10 | Columnas presentes solo en entrenamiento | 11 | `eda-diagnostico.json` → `columnas_solo_en_train` (longitud) |
| T12 | Duplicados exactos | 0 | `eda-diagnostico.json` → `duplicados_exactos` |
| T13 | Faltantes en `sex` | 11517 / 2.872% | `eda-diagnostico.json` → `faltantes.sex` |
| T14 | Faltantes en `anatom_site_general` | 5756 / 1.435% | `eda-diagnostico.json` → `faltantes.anatom_site_general` |
| T15 | Faltantes en `age_approx` | 2798 / 0.698% | `eda-diagnostico.json` → `faltantes.age_approx` |
| T16 | Método de validación cruzada | StratifiedGroupKFold | `diseno-validacion.json` → `esquema.metodo` |
| T17 | Número de folds | 5 | `diseno-validacion.json` → `esquema.n_splits` |
| T18 | Pacientes repartidos bajo partición ingenua (%) | 99.04 | `diseno-validacion.json` → `comparacion_particion_naive.pct_grupos_con_fuga` |
| T18b | Semilla aleatoria | 42 | `diseno-validacion.json` → `esquema.seed` |
| T19 | Pacientes con al menos un positivo | 259 | `diseno-validacion.json` → `n_grupos_positivos` |
| T20 | Fuga de grupo en el esquema construido | false | `diseno-validacion.json` → `fuga_de_grupo_detectada` |
| T21 | Pacientes repartidos bajo partición ingenua (conteo) | 1032 de 1042 | `diseno-validacion.json` → `comparacion_particion_naive.n_grupos_con_fuga` |
| T22 | Positivos en validación por fold | 78, 78, 83, 77, 77 | `diseno-validacion.json` → `por_fold[].n_val_positivos` |
| T23 | Filas en validación por fold | 80210–80216 | `diseno-validacion.json` → `por_fold[].n_val_filas` |
| T24 | Columnas constante e identificadora | `image_type`, `isic_id` | `auditoria-de-fugas.json` → `columnas_constantes`, `columnas_identificador` |
| T25 | Columnas utilizables para modelar | 41 | `modelado-baseline.json` → `n_features_usadas` |
| T26 | Umbral de AUC para marcar sospecha | 0.90 | `auditoria-de-fugas.json` → `umbral_auc_sospechoso` |
| T27 | AUC univariado de `tbp_lv_H` | 0.8053 | `auditoria-de-fugas.json` → `univariado[]` |
| T28 | AUC univariado de `tbp_lv_deltaB` | 0.7541 | `auditoria-de-fugas.json` → `univariado[]` |
| T29 | AUC univariado de `tbp_lv_Hext` | 0.7195 | `auditoria-de-fugas.json` → `univariado[]` |
| T30 | Preguntas abiertas planteadas | 10 | `auditoria-de-fugas.json` → `preguntas_abiertas` (longitud) |
| T30b | pAUC medio del nivel 2a | 0.0013 | `modelado-baseline.json` → `nivel_2a_....pauc_media` |
| T31 | AUC univariado de `tbp_lv_nevi_confidence` | 0.6457 | `auditoria-de-fugas.json` → `univariado[]` |
| T32 | Métrica verificada contra fuente oficial | true | `modelado-baseline.json` → `metrica_verificada_contra_fuente_oficial`, `metrica_fuente` |
| T33 | pAUC del azar | 0.02 | `modelado-baseline.json` → `escala_de_referencia_pauc.azar` |
| T34 | pAUC máximo alcanzable | 0.2 | `modelado-baseline.json` → `escala_de_referencia_pauc.maximo` |
| T35 | pAUC medio del nivel 0 | 0.0809 | `modelado-baseline.json` → `nivel_0_....pauc_media` |
| T36 | Desviación entre folds del nivel 0 | 0.0247 | `modelado-baseline.json` → `nivel_0_....pauc_std` |
| T37 | Nivel 0 como % del recorrido | 33.8 | `modelado-baseline.md` |
| T38 | pAUC medio del nivel 1 | 0.1331 | `modelado-baseline.json` → `nivel_1_....pauc_media` |
| T39 | Desviación entre folds del nivel 1 | 0.0173 | `modelado-baseline.json` → `nivel_1_....pauc_std` |
| T40 | Nivel 1 como % del recorrido | 62.8 | `modelado-baseline.md` |
| T41 | Desviación entre folds del nivel 2a | 0.0015 | `modelado-baseline.json` → `nivel_2a_....pauc_std` |
| T42 | Nivel 2a como % del recorrido | −10.4 | `modelado-baseline.md` |
| T43 | pAUC medio del nivel 2b | 0.1451 | `modelado-baseline.json` → `nivel_2b_....pauc_media` |
| T44 | Desviación entre folds del nivel 2b | 0.0055 | `modelado-baseline.json` → `nivel_2b_....pauc_std` |
| T45 | Nivel 2b como % del recorrido | 69.5 | `modelado-baseline.md` |
| T46 | Única diferencia entre 2a y 2b | `class_weight` | `modelado-baseline.json` → `nivel_2a_....modelo`, `nivel_2b_....modelo` |
| T47 | El conjunto de prueba es un marcador de posición | true | `eda-diagnostico.json` → `test_is_placeholder` |
| T48 | pAUC del nivel 1 en cada fold | 0.1524, 0.1253, 0.1553, 0.1142, 0.1184 | `modelado-baseline.json` → `nivel_1_....pauc_por_fold` |
| T49 | pAUC del nivel 2b en cada fold | 0.1509, 0.1386, 0.1499, 0.1478, 0.1385 | `modelado-baseline.json` → `nivel_2b_....pauc_por_fold` |

### 10.2 Cifras y citas de fuentes externas

Estas no proceden de `outputs/` sino de fuentes primarias versionadas en
`referencias/` o citadas por URL. Se separan a propósito: son contexto, no
resultados medidos por este proyecto.

| Marca | Afirmación | Fuente |
|---|---|---|
| E1 | Justificación clínica de la métrica: *"there are regions in the ROC space where the values of TPR are unacceptable in clinical practice"*, y el rango resultante [0.0, 0.2] | `referencias/kaggle-evaluation.md` (copia literal de la página de evaluación de Kaggle, 2026-08-11) |
| E2 | La mayoría de los casos negativos nunca fue biopsiada y se asume benigna | Artículo del dataset SLICE-3D, https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/ |
| E3 | Algoritmo oficial del pAUC, usado para verificar la implementación | `referencias/isic-primary-metric-pauc.py.md` (copia literal del script del organizador, 2026-08-11) |
| E4 | Definición de `tbp_lv_nevi_confidence` y del prefijo *Lesion Visualizer* | `referencias/slice3d-metadata-tbp-lv.md` (definiciones literales de la Tabla 1 del artículo, 2026-08-11) |
| E5 | El artículo no indica si las lesiones de entrenamiento del clasificador de nevus se solapan con el dataset | `referencias/slice3d-metadata-tbp-lv.md`, sección "Lo que el paper NO dice" |
| E6 | Los datos provienen de siete centros dermatológicos | Artículo del dataset SLICE-3D, https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/ |
| E7 | El esquema de premios del organizador ISIC evalúa *"above 88% true positive rate (TPR)"*, con rango resultante [0.00, 0.12] | `referencias/isic-metrics-readme.md` (copia literal del README del repositorio de métricas del organizador, 2026-08-12) |

### 10.3 Cifras deliberadamente ausentes

Dos números que aparecerían de forma natural en la sección 7 no se citan, porque
proceden de un diagnóstico auxiliar y no están en ningún archivo de `outputs/`:
el AUC convencional de los niveles 2a y 2b. La regla de trazabilidad no admite
excepciones por conveniencia narrativa. Se señala como mejora pendiente del
instrumento `modelado-baseline`: si el AUC estándar de cada nivel se incorporara
a su salida, el contraste entre métricas podría argumentarse con cifras en vez
de en términos cualitativos.

### 10.4 Cifras señaladas por la verificación y resueltas a mano

`verificar_trazabilidad.py` compara todo número del informe contra los valores
presentes en `outputs/*.json`. Señaló siete sin respaldo exacto. Dos eran
defectos reales del borrador y se corrigieron: un promedio redondeado a "casi
385" cuando la cifra medida es 384,89 `[T7]`, y un "menos de 85 positivos por
fold" que sustituía el rango medido de 77 a 83 `[T22]`. Los cinco restantes se
justifican:

| Cifra | Sección | Por qué no está en `outputs/*.json` |
|---|---|---|
| 44% | 7.1 | Derivación ilustrativa, no un resultado: es dónde caería un pAUC hipotético de 0,10 en el recorrido azar→perfecto, calculada a partir de `[T33]` y `[T34]`. Ningún modelo del proyecto obtuvo ese valor. |
| 33,8% (×3) | 7.2, 7.3, 9 | Está en `outputs/modelado-baseline.md`, no en el `.json`: el porcentaje del recorrido lo calcula el instrumento al redactar su resumen. El script solo lee archivos `.json`, y esa es una limitación suya, no una cifra sin origen. Es reproducible desde `[T35]`, `[T33]` y `[T34]`. |
| 88% | 8, punto 6 | Externa por naturaleza: es el umbral del esquema de premios del organizador, no un resultado de este proyecto. Trazable a `[E7]`. |
| 95% | 7.4 | Nivel de confianza convencional del intervalo, no una magnitud medida. |
| Diferencias por fold, su media (0,0120), su desviación (0,0160) y el intervalo *t* (−0,008 a +0,032) | 7.4 | Estadísticos derivados, calculados en este informe a partir de los pAUC por fold `[T48]` y `[T49]`, que sí están en `outputs/`. La regla de trazabilidad exige que toda cifra provenga de `outputs/`; estas provienen de restar dos columnas que están allí. El cálculo es reproducible con los dos vectores del anexo y no requiere volver a entrenar nada. |

Ningún número del informe queda, tras esta revisión, sin origen identificado.

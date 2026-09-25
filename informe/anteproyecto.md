# Anteproyecto

## 1. Problema y estado actual

### 1.1 El problema: detectar a tiempo sin saturar la consulta

La Cuenta de Alto Costo (CAC) reportó 9.272 casos de melanoma en Colombia para
su periodo 2025, con corte al 2 de febrero de 2026; la cifra es preliminar,
previa a auditoría (Contreras, 2026). El mismo boletín informa que los casos
prevalentes aumentaron un 12,65 % frente al periodo anterior y que la
mortalidad por todas las causas en las personas con melanoma creció un 10,53 %
frente a 2024.

Lo que está en juego es el estadio en que se diagnostica. Según el boletín del
año anterior, la supervivencia global a cinco años del melanoma cutáneo es del
60,9 %, pero en los estadios avanzados, y en particular en el estadio IV, menos
del 50 % de los pacientes sobrevive a los dos años de confirmado el diagnóstico
(Cuenta de Alto Costo [CAC], 2025). Ese boletín reporta además que el 67,4 % de
los casos de su periodo 2024 —que la CAC define como del 2 de enero de 2023 al 1
de enero de 2024— se diagnosticó en estadios tempranos, I y II.

Las cifras de los dos boletines no forman una serie, y no se leen aquí como
tendencia. Uno dice que «se han atendido» 11.064 casos hasta el 31 de diciembre
de 2024 y el otro habla de 9.272 casos «reportados» en el periodo 2025, sin que
ninguno defina qué cuenta. El «más del 50 %» en estadios tempranos del boletín
de 2026 remite a una meta, no es una estimación puntual, así que no puede
compararse con el 67,4 % del anterior (CAC, 2025; Contreras, 2026). Sirven para
dimensionar el problema, no para medir su evolución.

Esas cifras tampoco miden el problema que aborda este trabajo, y conviene
decirlo desde el principio. Los boletines señalan dos desafíos. El de 2025
dice que la detección temprana sigue siendo un desafío en algunas regiones del
país (CAC, 2025). El de 2026 señala la oportunidad del tratamiento: el tiempo
promedio al diagnóstico se ha mantenido cercano a 15 días, sin que se precise
desde qué momento se cuenta, mientras el inicio del tratamiento supera en
promedio los 30 días (Contreras, 2026). Ninguno de los dos informa cuántas
lesiones se examinan para encontrar cada melanoma. Ese es el costo del lado
opuesto: un sistema que detecta pronto pero envía a revisión muchas lesiones
benignas desplaza la carga hacia la consulta especializada.

### 1.2 Estado actual: el triaje sobre fotografía corporal total

La fotografía corporal total en 3D (3D-TBP) cambia la naturaleza de la tarea
clínica. Captura toda la superficie cutánea visible en una sola toma, y el
programa del fabricante identifica cada lesión por separado (Kurtansky,
D’Alessandro, et al., 2024). En los datos de este caso son 401.059 lesiones de
1.042 pacientes, una media de 384,89 por paciente. La dermatoscopia, en cambio,
se usa normalmente para documentar las lesiones más atípicas, las que se
biopsian o se vigilan (Kurtansky, D’Alessandro, et al., 2024). Con 3D-TBP la
pregunta clínica ya no es qué tiene una lesión que alguien escogió, sino cuáles
de varios cientos merecen que un especialista las mire. Es una tarea de
triaje, y sus dos errores cuestan: un falso negativo es un cáncer que nadie
revisa; un falso positivo, un examen detallado que alguien tiene que hacer.

La práctica humana actual en esta modalidad tiene al menos una medición
publicada, en la validación de PanDerm, un modelo fundacional dermatológico
(Yan et al., 2025). Los autores informan que los *melanographers* —el término
del artículo, que no lo define— recomendaron 8.913 lesiones para examen
detallado, frente a 3.498 del modelo. Según los métodos, el conjunto de prueba
de ese cribado reunió 80 pacientes de dos cohortes australianas, con 30.698
imágenes que incluyen 28 lesiones malignas (Yan et al., 2025).

El 8.913 es la línea base de este trabajo, y se usa con cuatro salvedades.

- **El denominador es lectura nuestra.** Ninguna frase del artículo dice que las
  8.913 recomendaciones se hicieron sobre esas 30.698 imágenes. Lo sugiere la
  leyenda de su figura 4, que presenta la selección humana sobre las lesiones de
  prueba.
- **El denominador no son todas las lesiones capturadas.** El conjunto se filtró
  antes con parámetros del propio sistema de captura, entre ellos una confianza
  de nevus superior a 80, y se cuenta en imágenes, no en lesiones. Procede de
  2.038 capturas de 480 pacientes, así que una misma lesión puede estar en más
  de una imagen (Yan et al., 2025).
- **Solo se usa el lado humano.** El 8.913 es el lado humano de una comparación
  que publican los autores del modelo. El 3.498 es desempeño del propio PanDerm,
  y aquí se cita solo como contexto.
- **El «79 out of 80» no se usa.** La frase de los resultados que da el 8.913
  atribuye además al modelo la detección de lesiones malignas «in 79 out of 80
  patients», sin definir cómo mide ese resultado por paciente. Si esos 80 fueran
  los de prueba y la frase se leyera al pie de la letra, no cuadraría con 28
  lesiones malignas. Ninguna de las dos condiciones está escrita en el artículo.

Una coincidencia hace esta línea base más pertinente de lo que parece: las dos
cohortes australianas de esa evaluación tienen los mismos números de
aprobación ética que los dos estudios con que la Universidad de Queensland
contribuyó a SLICE-3D (Kurtansky, D’Alessandro, et al., 2024; Yan et al., 2025).
La línea base se midió en los mismos estudios de los que proviene una parte de
los datos del caso.

### 1.3 El cliente y lo que declaró necesitar

La contraparte son los organizadores del reto ISIC 2024. La modalidad es de
datos abiertos: no hay acta ni reuniones, y lo que el cliente necesita se lee en
lo que publicó. La métrica principal es el área parcial bajo la curva ROC por
encima del 80 % de sensibilidad, justificada porque existen regiones del espacio
ROC donde la sensibilidad es inaceptable en la práctica clínica. Además hubo dos
premios secundarios de 7.500 dólares cada uno, uno a la *Top-15 Retrieval
Sensitivity* y otro a la *Model Efficiency* (Kurtansky, Rotemberg, et al.,
2024). La primera mide la sensibilidad sobre las quince lesiones de mayor riesgo
de cada paciente (Kurtansky et al., 2025). La función de utilidad del cliente,
por tanto, no cabe en una sola cifra: pide sensibilidad alta, la mide también
por paciente y le importa la eficiencia del modelo.

Los datos imponen dos condiciones que cualquier análisis tiene que respetar.
La primera es el desbalance: 393 lesiones malignas entre 401.059, un 0,098 %,
concentradas en 259 de los 1.042 pacientes. La segunda es que las dos clases no
se etiquetaron igual. Las malignas están confirmadas por patología. La mayoría
de las benignas, en cambio, nunca se biopsió: son lesiones que un dermatólogo
vio durante un examen de piel completo y no consideró preocupantes (Kurtansky,
D’Alessandro, et al., 2024). Un «negativo» en estos datos no significa «sano»:
en la mayoría de los casos significa «no enviado a biopsia».

### 1.4 El problema de consultoría

Con ese cliente y esos datos, la pregunta de este trabajo no es cómo obtener el
mejor puntaje, sino cuánto depende el veredicto sobre un modelo de las
decisiones metodológicas que se toman por defecto: con qué métrica se evalúa,
cómo se trata el desbalance y cómo se parten los datos cuando un mismo paciente
aporta cientos de lesiones. Cada una de esas decisiones puede cambiar qué modelo
parece mejor, y el cliente ya dejó escrito, en su métrica y en sus premios,
contra qué quiere que se juzgue. El trabajo del consultor es leer esa función
de utilidad antes de optimizar nada y recomendar desde ella, diciendo con qué
seguridad se hace la recomendación.

El alcance geográfico de la conclusión queda acotado desde aquí. Ninguno de los
siete centros que aportan SLICE-3D está en América Latina: son centros de
Estados Unidos, España, Australia, Austria, Grecia y Suiza (Kurtansky,
D’Alessandro, et al., 2024). El contexto colombiano de la sección 1.1 explica
por qué importa detectar a tiempo. La carga que genera el triaje la dimensiona
la medición de la sección 1.2, no los boletines. Ninguno de los dos autoriza a
trasladar a pacientes colombianos un desempeño medido sobre estos datos. Lo que
sí es transferible es el procedimiento de evaluación, que es lo que este trabajo
se propone establecer.

## 2. Estado del arte

La revisión se organiza por enfoques y no por autor. Cuatro líneas convergen en
este proyecto: el caso clínico y su único precedente publicado; cómo se evalúa un
sistema de triaje; cómo se valida un modelo cuando las observaciones no son
independientes; y qué se ha investigado en Colombia. Las tres primeras son
literatura internacional; la cuarta responde a una pregunta distinta y por eso se
trata aparte.

### 2.1 Triaje sobre fotografía corporal total en 3D

La mayoría de los conjuntos públicos de imágenes de lesiones cutáneas son
dermatoscópicos y arrastran un sesgo de selección: el dermatólogo documenta con
dermatoscopia las lesiones más atípicas, las que se biopsian o se vigilan, de modo
que los ejemplos benignos ordinarios quedan subrepresentados (Kurtansky, D’Alessandro,
et al., 2024). El conjunto SLICE-3D se construyó para evitarlo. Reúne más de 400.000
lesiones de siete centros dermatológicos en tres continentes, extraídas de
fotografías corporales totales en 3D de más de mil pacientes atendidos entre 2015
y 2024, con una resolución óptica que los autores describen como comparable a la
de una fotografía de teléfono (Kurtansky, D’Alessandro, et al., 2024).

El argumento clínico que justifica ese diseño tiene dos lados y conviene no
quedarse con uno solo. Por un lado, los autores señalan que, frente al desarrollo de
algoritmos que asisten el diagnóstico en la consulta especializada, determinar quién
debe ver a un clínico en primer lugar tiene un gran impacto potencial; por otro, reducir las derivaciones innecesarias
disminuye las demoras de los pacientes que sí las necesitan y alivia la carga del
sistema de salud (Kurtansky, D’Alessandro, et al., 2024). Es decir: el problema no
es solo detectar, es detectar sin inundar la consulta.

En este dominio concreto, los organizadores señalan que existe **un único estudio
previo publicado** (Kurtansky et al., 2025): Marchetti
et al. (2023) ajustaron un modelo de regresión multivariado sobre medidas
morfológicas que el propio sistema de captura extrae de cada lesión —tamaño,
variación de color, irregularidad del borde—, sin usar las imágenes ni redes
neuronales. Sobre una muestra de conveniencia de 35 pacientes de un solo centro,
con 49 melanomas entre 23.538 lesiones, reportaron un AUC de 0,94 (IC 95 %:
0,92–0,96) y lo presentaron explícitamente como prueba de concepto piloto.
Kurtansky et al. (2025) describen ese modelo como capaz de reducir en un 75 % las
lesiones que requieren inspección cercana manteniendo un 95 % de sensibilidad para
melanoma; esa cifra no aparece en el resumen del artículo original, por lo que
aquí se atribuye a quienes la reportan y no a Marchetti et al. Los propios
organizadores señalan su límite: el modelo no ha sido validado en estudios
posteriores ni con datos de otros centros (Kurtansky et al., 2025).

El segundo enfoque es el de los ensambles con características de imagen, y quedó
documentado por los organizadores al analizar su propia competencia. ISIC 2024
recibió 4.998 envíos oficiales de 2.739 equipos; el modelo ganador alcanzó un
pAUC>80 % TPR de 0,1726 y un AUC de 0,9668 para clasificar cáncer de piel sobre el
conjunto de evaluación privado (Kurtansky et al., 2025). Los organizadores
reevaluaron también el modelo de Marchetti et al. sobre ese conjunto —menos las 209
lesiones de un paciente que participaba en los dos estudios— y obtuvieron un AUC de
0,704 en esa misma tarea y de 0,8927 al clasificar melanoma específicamente. Las dos
cifras miden tareas distintas y no son intercambiables.

El contraste entre los dos enfoques no es el que cabría esperar, y ese es el
hallazgo más útil de esta línea. El estudio de ablación de Kurtansky et al. (2025)
muestra que **los recortes de imagen fueron menos informativos que las medidas
morfológicas preextraídas**: la variante restringida a metadatos de apariencia
superó significativamente a la que usaba solo imágenes (AUC = 0,939 frente a
0,922; p = 0,016). Lo que sí resultó sustancial fue el contexto del paciente
—situar cada lesión frente a las demás del mismo paciente—: al retirarlo, la
discriminación cayó (AUC = 0,956 frente a 0,967; p < 0,001) y, al umbral del 80 %
de sensibilidad, el sistema derivaba 22 lesiones no malignas adicionales por cada
maligna detectada. La diferencia entre los dos enfoques, por tanto, no se reduce a
«con imágenes o sin ellas»: pasa por qué información se le da al modelo sobre el
paciente.

### 2.2 Cómo se evalúa un sistema de triaje

El área bajo la curva ROC resume el desempeño de un clasificador sobre todos los
umbrales posibles. McClish (1989) planteó calcular el área bajo solo una porción
de la curva, cuando el interés no abarca todo el rango de tasas de falsos
positivos, y propuso la integración numérica para evaluarla. Esa es la familia a
la que pertenece la métrica de ISIC 2024, que la competencia define como el área
bajo la curva ROC y por encima del 80 % de sensibilidad, con un recorrido de 0,0 a
0,2. La justificación que da el organizador es clínica y explícita: existen
regiones del espacio ROC donde los valores de sensibilidad son inaceptables en la
práctica clínica, y un sistema de apoyo al diagnóstico de cáncer debe ser
altamente sensible (Kurtansky, Rotemberg, et al., 2024).

El área parcial no está libre de crítica, y conviene traerla. Walter (2005)
concluye que, frente a lo hallado con el AUC completo, el área parcial es bastante
sensible a la heterogeneidad, que comparar pruebas se complica —sobre todo bajo
truncamiento empírico— y que, en conjunto, prefiere el AUC completo. Su alcance,
sin embargo, es la curva ROC de resumen en metaanálisis, donde cada estudio aporta
un punto y la heterogeneidad es entre estudios; trasladar esas desventajas a una
curva ROC empírica única sería una extensión, no una cita. El artículo recibió
además una réplica publicada en la misma revista, con respuesta del autor, de modo
que tampoco dentro de su propio ámbito es palabra final.

Una segunda crítica, más reciente, apunta a la construcción de la métrica. Yang et
al. (2019) proponen el área parcial de dos vías, que restringe simultáneamente la
sensibilidad y la tasa de falsos positivos, y objetan a los enfoques que fijan un
límite artificial sobre un eje para controlar el otro de forma indirecta; ese
control indirecto sobre la sensibilidad es, en sus palabras, «conceptually and
practically misleading» (Yang et al., 2019). Esa
objeción **no aplica a la métrica de ISIC 2024**, como se comprobó ejecutando la
implementación oficial del organizador: el guion invierte las etiquetas antes de
construir la curva, de modo que la restricción sobre la sensibilidad es directa y
la tasa de falsos positivos no queda acotada en absoluto. Lo que sí queda en pie
del marco de Yang et al., ya como lectura propia y no como afirmación suya sobre
este caso, es que restringir un solo eje deja el otro sin control.

Y ahí es donde la propia competencia da la razón a esa lectura. La métrica del
ranking nunca fue la única: SEtop-15 ya operaba como métrica de premio secundario
durante la competición, y al analizar los resultados los organizadores la
formalizaron junto a una segunda métrica orientada a la tarea clínica (Kurtansky et
al., 2025).
La primera, SEtop-15, mide la sensibilidad bajo la tarea hipotética de identificar
las quince lesiones de mayor riesgo en cada paciente, ponderando por igual a cada
paciente enfermo para que quienes tienen varias lesiones malignas no dominen el
resultado. La segunda, NNTx% SE, es el número medio de lesiones que hay que derivar
a evaluación experta para detectar una maligna, y los autores la emparentan
explícitamente con el *number needed to biopsy* que la dermatología usa para medir
el equilibrio entre detección y intervenciones evitables. El contraste con la
sección anterior es directo: una métrica de resumen ordena modelos, pero no dice
cuántas personas sanas pasan por la consulta, y por eso quien escribió la métrica
principal terminó reportando cuatro ejes.

### 2.3 Validación cuando las observaciones no son independientes

Saeb et al. (2017) formularon el principio que gobierna este punto: para que la
validación cruzada sea informativa, la relación entre el conjunto de entrenamiento
y el de validación debe imitar la relación entre el entrenamiento y los datos que
se esperan en el uso clínico. De ahí se sigue que, si el caso de uso es
diagnosticar a sujetos nuevos, la partición debe hacerse por sujeto y no por
registro. Comparando ambas estrategias sobre datos públicos y sobre una
simulación, encontraron que la partición por registro a menudo sobreestima
masivamente la precisión, y que casi la mitad de los estudios revisados —los que
predicen desenlaces clínicos a partir de acelerómetros, sensores portátiles o
teléfonos— usaba esa estrategia optimista.

La prescripción no se aceptó sin discusión, y la réplica se publicó junto al
artículo original. Little (en Little et al., 2017) acepta la diferencia observada,
pero discute tanto lo que demuestra —propone el subajuste como explicación
alternativa que no se puede descartar— como su aplicación automática: que la
partición por sujeto sea aplicable o no depende de la estructura
de dependencia y de distribución de los datos, que puede coincidir o no con el caso
de uso pretendido. Varoquaux (en Little et al., 2017), en la misma revisión, sostiene
la posición
contraria en lo que aquí importa: en un escenario de aplicación claro, como uno
clínico, el uso previsto debe dictar el esquema de validación. La discrepancia
entre ambos es la que decide qué hacer en cada caso concreto, y por eso Saeb et al.
no se cita en este proyecto sin esta réplica.

Kapoor y Narayanan (2023) dan la escala del problema: revisando la literatura de
campos que adoptaron aprendizaje automático, encontraron fuga de datos en 17
disciplinas, afectando al menos a 294 artículos, y propusieron una taxonomía de
ocho tipos. La falta de independencia entre entrenamiento y prueba es su tipo
L3.2, y el detalle de dónde lo clasifican es pertinente: no bajo la categoría de
ausencia de separación limpia entre entrenamiento y prueba, sino bajo la de que el
conjunto de prueba no procede de la distribución de interés científico. Para ellos, la no independencia constituye fuga *salvo que
la afirmación científica sea sobre una distribución con la misma estructura de
dependencia*, lo que es la misma idea del caso de uso de Saeb et al. formulada
desde el otro lado. Su estudio de caso muestra el efecto: en predicción de guerras
civiles, la supuesta superioridad de los modelos complejos sobre la regresión
logística desaparece una vez corregida la fuga.

El precedente existe también dentro del propio ecosistema ISIC. Cassidy et al.
(2022) analizaron las ediciones de 2016 a 2020 y encontraron un número
considerable de imágenes duplicadas dentro de cada conjunto y entre conjuntos,
incluidos duplicados repartidos entre los conjuntos de entrenamiento y de prueba;
su estrategia de depuración retiró 14.310 imágenes del conjunto de entrenamiento.
Son conjuntos dermatoscópicos anteriores, no SLICE-3D, y el mecanismo es la
duplicación de imágenes y no la agrupación por paciente: sirve como precedente de
que el defecto ocurre en estos datos, no como evidencia sobre los de este
proyecto.

La condición que plantea Little tiene dos partes, y para este caso solo una está
resuelta de antemano. El uso previsto sí lo está: el conjunto de evaluación de ISIC
2024 se compiló con pacientes distintos a los del entrenamiento (Kurtansky et al.,
2025), de modo que lo que se afirma es sobre pacientes nuevos. La otra parte —la
estructura de dependencia de los datos— no la resuelve la literatura revisada. Que
un paciente aporte muchas lesiones establece agrupamiento, y el propio Little
advierte que el agrupamiento no implica dependencia por sí solo. Determinar si en
estos datos la hay, y cuánto cuesta ignorarla, es una pregunta empírica sobre
SLICE-3D antes que una que se pueda zanjar citando.

### 2.4 Qué se ha investigado en Colombia

La búsqueda realizada devolvió producción colombiana en tres frentes vecinos a este
trabajo. En teledermatología, Sáenz et al. (2018) midieron en cuántas consultas
—48 de 64, un 75 %, con un intervalo de confianza del 95 % entre 64,4 % y 85,6 %—
al menos uno de los ocho diagnósticos diferenciales que producía una ontología
coincidía con el de la dermatóloga que juzgó el caso después; las consultas se
registraron durante una brigada de salud en una zona desfavorecida.
Barrera-Valencia y Perea-Flórez (2024) compararon los tiempos de atención de un
servicio de teledermatología para población rural dispersa, con computador y cámara
frente a teléfono inteligente, en un estudio que presentan como comparación de
costos.

En mapeo corporal digital, Mejía Posada et al. (2024) revisaron retrospectivamente
las historias clínicas de 368 pacientes con síndrome de nevus atípico atendidos en
una clínica especializada de Medellín entre 2017 y 2022, y encontraron melanoma en
el 12,2 % de ellos. Es la misma práctica clínica de la que provienen los datos de
este caso, sin la captura en tres dimensiones.

Y en aprendizaje automático dermatológico hay trabajo con participación colombiana:
Rios-Duarte et al. (2024), con los cinco autores en universidades del país, y dos
estudios en colaboración entre la Universidad del Norte y la Universidad de Deusto
(Jojoa Acosta et al., 2021; Jojoa et al., 2022). Los tres clasifican melanoma a
partir de imágenes, y ninguno usa datos de pacientes colombianos: entrenan y evalúan
sobre conjuntos internacionales —la base de los siete criterios, ISIC y PH2—.

Este trabajo se sitúa en la intersección de los tres: datos de fotografía corporal
de un mismo paciente, evaluados con aprendizaje automático, bajo la métrica de
triaje que el organizador declaró.

### 2.5 El vacío que este proyecto atiende

Las tres primeras líneas dejan el terreno así. El principio de validación por
sujeto está establecido y también acotado por su réplica; la escala de la fuga está
documentada de forma transversal y, dentro del ecosistema ISIC, con nombre propio;
la crítica a la métrica de área parcial existe y está publicada; y los propios
organizadores reportan cuatro ejes de desempeño porque uno solo no agota lo que
declararon necesitar.

Lo que no se encontró en ninguna de esas fuentes es un examen de **cuánto cambia el
veredicto sobre un mismo modelo según qué decisiones metodológicas por defecto se
acepten**. Los organizadores parten por paciente y lo declaran, sin cuantificar qué
habría ocurrido de no hacerlo. Marchetti et al. (2023) reportan un AUC sin que el
resumen permita saber con qué esquema de validación se obtuvo. Kapoor y Narayanan
(2023) muestran que corregir la fuga borra la ventaja de los modelos complejos,
pero en otro dominio y con otro mecanismo. Esa afirmación de ausencia tiene un
límite que conviene declarar: de McClish (1989), Walter (2005) y Marchetti et al.
(2023) solo se pudo leer el resumen, porque el texto completo está tras muro de
pago.

Este proyecto atiende ese vacío sobre SLICE-3D y con mediciones propias: cuantificar
la fuga que produciría una partición por registro frente a una agrupada por
paciente —el 99,04 % de los 1.042 pacientes habría quedado repartido entre
entrenamiento y validación—, y evaluar los mismos modelos bajo métricas que pueden
discrepar en el veredicto, incluidos los ejes de tarea clínica que los organizadores
definieron.

## 3. Objetivos

**Objetivo general.** Establecer un procedimiento de evaluación para modelos de triaje de melanoma sobre el conjunto SLICE-3D que priorice la función de utilidad declarada por el organizador, y determinar en qué medida las decisiones metodológicas por defecto —métrica, tratamiento del desbalance y esquema de partición— alteran el veredicto sobre un modelo.

**Objetivos específicos.**

1. Construir un esquema de evaluación libre de fuga: cuantificar la fuga de una partición por registro frente a una agrupada por paciente, identificar las variables no disponibles al momento de predecir y reservar un conjunto de pacientes que se evalúe una sola vez. *Se declara cumplido con la proporción de pacientes presentes a ambos lados de cada partición, el listado de variables excluidas con su motivo y el conjunto reservado sellado antes de cualquier decisión nueva de modelado.*
2. Estimar el desempeño de cuatro niveles de referencia bajo la métrica oficial y bajo el AUC estándar, sobre los mismos pliegues. *Se declara cumplido con las medias y las series por pliegue de ambas métricas, y con los casos donde las dos discrepan en el veredicto.*
3. Contrastar los niveles, y la solución ganadora de la competencia reproducida desde su código público sobre las mismas particiones, mediante comparación pareada con validación cruzada repetida, corrigiendo la varianza por el solape entre conjuntos de entrenamiento. *Se declara cumplido con el intervalo de confianza de cada diferencia en sus versiones ingenua y corregida, y con la lista de los componentes de la solución ganadora que no se pudieron reproducir, con su motivo: cómputo o riesgo de fuga.*
4. Evaluar los niveles bajo los ejes de triaje que definen los organizadores —sensibilidad en las quince lesiones de mayor riesgo por paciente y número de lesiones a derivar por maligna detectada— para determinar si el veredicto de la métrica principal se sostiene sobre la función de utilidad completa. *Se declara cumplido con la tabla de los tres ejes por nivel y con la implementación contrastada contra el orden de magnitud publicado.*
5. Incorporar características derivadas de imagen, previa verificación de que el conjunto no estuvo en el preentrenamiento del modelo fundacional empleado, y evaluar el modelo recomendado sobre el conjunto reservado. *Se declara cumplido con el resultado de esa verificación y con las métricas del conjunto reservado reportadas con su intervalo.*

## 4. Datos y método

### 4.1 Datos

El conjunto de trabajo es SLICE-3D, el conjunto de entrenamiento de ISIC 2024
(International Skin Imaging Collaboration, 2024; Kurtansky, D’Alessandro, et
al., 2024). Se distribuye en dos versiones:

- **SLICE-3D**, con los datos de las siete instituciones, bajo licencia CC BY-NC
  4.0.
- **SLICE-3D Permissive**, con las cuatro instituciones que no restringieron el
  uso comercial, bajo CC BY 4.0.

Así lo describen Kurtansky, D’Alessandro, et al. (2024). Este trabajo usa la
versión completa, y su uso académico y no comercial cumple la licencia. La
atribución que la licencia exige es la siguiente:

> International Skin Imaging Collaboration. SLICE-3D 2024 Challenge Dataset. International Skin Imaging Collaboration https://doi.org/10.34970/2024-slice-3d (2024).
>
> Creative Commons Attribution-Non Commercial 4.0 International License.
>
> The dataset was generated by the International Skin Imaging Collaboration (ISIC) and images are from the following sources: Hospital Clínic de Barcelona, Memorial Sloan Kettering Cancer Center, Hospital of Basel, FNQH Cairns, The University of Queensland, Melanoma Institute Australia, Monash University and Alfred Health, University of Athens Medical School, and Medical University of Vienna.
>
> You should have received a copy of the license along with this work.
>
> If not, see https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt .

La atribución nombra nueve fuentes, no siete. El descriptor limita SLICE-3D a
siete instituciones y añade que otros dos centros aportaron datos solo al
conjunto de prueba del reto (Kurtansky, D’Alessandro, et al., 2024). Que la
cadena recoja las fuentes del reto completo es la explicación más probable,
pero la página no lo dice.

El archivo de metadatos de entrenamiento tiene 401.059 filas, una por lesión, y
55 columnas. Aporta 1.042 pacientes, con una media de 384,89 lesiones cada uno,
un mínimo de 1 y un máximo de 9.184. Hay 393 lesiones malignas (0,098 %), y
están concentradas: solo 259 de los 1.042 pacientes tienen al menos una. El
archivo de prueba publicado contiene tres filas de ejemplo; el conjunto con el
que se evaluó la competencia no es accesible. Toda estimación de este trabajo
sale, por tanto, del conjunto de entrenamiento.

Antes de modelar se excluyen 13 columnas. Once existen en entrenamiento pero no
en prueba:

- la etiqueta y su taxonomía diagnóstica (`target` y las seis `iddx_*`);
- dos medidas que solo existen después de la biopsia (`mel_mitotic_index` y
  `mel_thick_mm`);
- una puntuación que no estaría disponible al predecir
  (`tbp_lv_dnn_lesion_confidence`);
- el identificador de lesión (`lesion_id`).

Las otras dos son una columna constante y el identificador de imagen. Quedan 41
variables, porque `patient_id` se usa para agrupar y no como variable. La
auditoría de fugas no encontró entre ellas ninguna con un AUC univariado de 0,9
o más, el umbral fijado para marcar una variable como sospechosa.

Las imágenes se incorporan en una fase posterior (sección 4.4), que reporta
cuántas lesiones tienen imagen utilizable. Si el cómputo no alcanza para todas,
se submuestrea por paciente conservando todas las lesiones malignas; la regla
se fija antes de medir cuánto tarda la extracción.

### 4.2 Esquema de evaluación

Los datos se parten por paciente, nunca por lesión, en cinco pliegues
estratificados por la etiqueta (`StratifiedGroupKFold`). La comprobación
automática del esquema no encontró ningún paciente repartido entre
entrenamiento y validación. En la partición de referencia (semilla 42), cada
pliegue de validación recibe entre 77 y 83 lesiones malignas. Una partición por
filas habría repartido 1.032 de los 1.042 pacientes (el 99,04 %) entre los dos
lados. El esquema se repite con diez semillas, para no depender de una sola
asignación de pliegues.

Antes de cualquier decisión nueva de modelado se aparta el 20 % de los
pacientes, estratificado por presencia de lesiones malignas, como conjunto
reservado. Ese conjunto se abre una sola vez, al final, para evaluar el modelo
recomendado, y el resultado se reporta sea cual sea. La estimación principal es
la de la validación cruzada repetida. El conjunto reservado confirma, y con
pocos pacientes portadores de lesiones malignas su intervalo será ancho.

Hay una salvedad que se declara. El conjunto reservado no es ajeno a las
decisiones tomadas antes de apartarlo, porque se tomaron con los datos
completos:

- qué columnas se excluyen;
- qué niveles de referencia se comparan;
- los hiperparámetros y las columnas descartadas de la solución ganadora, que
  su autor fijó sin ningún conjunto reservado.

Sí es ajeno a todo lo que se decida después de sellarlo, y todas las cifras se
vuelven a medir sobre el conjunto de desarrollo.

### 4.3 Métricas

La métrica principal es la del cliente: el área parcial bajo la curva ROC por
encima del 80 % de sensibilidad, con recorrido de 0 a 0,2 (Kurtansky, Rotemberg,
et al., 2024). Un clasificador al azar obtiene 0,02. Se calcula con las
funciones del proyecto, verificadas contra el guion oficial del organizador
(Kurtansky, 2024). Sobre las mismas predicciones se calcula el AUC estándar,
para registrar los casos en que las dos métricas discrepan en el veredicto.

Los ejes de triaje son los que definieron los organizadores (Kurtansky et al.,
2025):

- **SEtop-15.** La sensibilidad al revisar las quince lesiones de mayor riesgo
  de cada paciente, con el mismo peso para cada paciente enfermo.
- **NNT80% SE.** El número medio de lesiones que hay que derivar para detectar
  una maligna, con el umbral fijado en el 80 % de sensibilidad.

Los valores de referencia salen de la Tabla 3 de Kurtansky et al. (2025):

- para los modelos propios, la reevaluación que los organizadores hicieron del
  modelo de Marchetti et al. (2023);
- para la reproducción del ganador, la variante de su estudio de ablación sin
  recortes de imagen.

Sirven para comprobar que el cálculo está bien montado, no para comparar
desempeño, porque se midieron sobre otras particiones y otros conjuntos.

El costo de inferencia, que el cliente también premió (sección 1.3), todavía no
tiene definición operativa; se fija en el apartado 5.

### 4.4 Modelos

Se comparan cuatro niveles de referencia:

- **Nivel 0.** Una sola variable, imputada con la mediana del pliegue de
  entrenamiento y usada directamente como predictor. En las mediciones
  exploratorias, la variable y su orientación se eligieron con etiquetas de
  validación. En la nueva medición las dos elecciones se hacen dentro de cada
  pliegue de entrenamiento.
- **Nivel 1.** Regresión logística con pesos balanceados por clase, sobre las 41
  variables, estandarizadas dentro de cada pliegue de entrenamiento.
- **Nivel 2a.** *Gradient boosting* sobre las 41 variables, sin ajuste por
  desbalance.
- **Nivel 2b.** El mismo modelo con pesos balanceados.

Se comparan también contra la parte tabular de la solución ganadora de la
competencia, reproducida desde su código público (Novoselskiy, 2024) sobre las
mismas particiones: CatBoost con el z-score de cada variable dentro del
paciente, conteos y sumas de área por paciente y un indicador de atipicidad
(LOF) ajustado paciente por paciente.

- **Quedan fuera sus redes de imagen**, por cómputo: el código las ajusta por
  completo en una GPU de servidor.
- **Queda fuera su modelo entrenado con el archivo público de ISIC**, por
  riesgo de fuga: el código no excluye de esa descarga las imágenes de la
  competencia.
- **Sus hiperparámetros y columnas descartadas se eligieron con las variables de
  imagen presentes**, así que la parte reproducida no es un modelo ajustado para
  ir sin ellas.

Cada cambio que exija el código publicado se declara.

Las características de imagen se extraen con un modelo preentrenado y
congelado, en una sola pasada y sin ajuste fino. Se descartó PanDerm porque su
propio artículo declara un subconjunto de ISIC 2024 entre sus datos de
preentrenamiento (Yan et al., 2025). En su lugar se usa DINOv3, sujeto a la
misma verificación antes de extraer ninguna característica; su fuente se cita
cuando esté verificada.

### 4.5 Comparación estadística

Los modelos se comparan por pares, pliegue a pliegue, con las diferencias de las
diez repeticiones. Las diferencias no son independientes, porque los conjuntos
de entrenamiento de los pliegues se solapan. Por eso el intervalo de confianza
se calcula con la corrección de Nadeau y Bengio (2003):

- multiplica la varianza muestral de las diferencias por (1/J + n₂/n₁), donde J
  es el número de diferencias y n₂/n₁ la razón entre los tamaños de validación y
  entrenamiento (1/4 con cinco pliegues);
- usa J − 1 grados de libertad.

Los autores la presentan como una aproximación burda, preferible a suponer que
las diferencias no están correlacionadas (paráfrasis). La derivaron además para
divisiones aleatorias independientes entre sí, no para validación cruzada de
cinco pliegues repetida. Aquí se aplica fuera de ese escenario, y se declara.

Se reportan los dos intervalos, el ingenuo y el corregido, pero solo el
corregido sostiene conclusiones. El criterio para un resultado negativo queda
fijado antes de medir: si el intervalo corregido de una diferencia contiene el
cero, esa ventaja no se da por establecida, y la recomendación lo dice así.

## 5. Alcance y plan

## 6. Declaración de uso de IA y reparto del trabajo

Se usó Claude (Anthropic) como asistente de redacción y de análisis: se le
pidieron borradores, búsquedas de fuentes y la ejecución del código; la persona
revisó, decidió y corrigió cada resultado. Cada cita se verificó contra el texto
disponible de su fuente antes de entrar al documento; de tres fuentes solo se
pudo leer el resumen (sección 2.5). El historial de commits del repositorio
registra qué se pidió y qué se corrigió en cada caso.

## Referencias

Barrera-Valencia, C., & Perea-Flórez, E. X. (2024). Comparison of costs in
teledermatology using PC and camera versus smartphone. *Telemedicine and e-Health,
30*(7), e2087–e2095. https://doi.org/10.1089/tmj.2023.0369

Cassidy, B., Kendrick, C., Brodzicki, A., Jaworek-Korjakowska, J., & Yap, M. H.
(2022). Analysis of the ISIC image datasets: Usage, benchmarks and
recommendations. *Medical Image Analysis, 75*, 102305.
https://doi.org/10.1016/j.media.2021.102305

Contreras, J. (2026, 22 de mayo). *Día mundial del melanoma 2026: Las cifras
detrás de la piel: panorama del melanoma en Colombia*. Cuenta de Alto Costo.
https://cuentadealtocosto.org/noticias/dia-mundial-del-melanoma-2026/

Cuenta de Alto Costo. (2025, 23 de mayo). *Día mundial del melanoma cutáneo
2025: «¡Más allá de la piel, están las cifras del melanoma en Colombia!»*
[Boletín de prensa].
https://cuentadealtocosto.org/noticias/dia-mundial-del-melanoma-cutaneo-2025/

International Skin Imaging Collaboration. (2024). *SLICE-3D 2024 Challenge
Dataset* [Conjunto de datos]. https://doi.org/10.34970/2024-slice-3d

Jojoa, M., Garcia-Zapirain, B., & Percybrooks, W. (2022). A fair performance
comparison between complex-valued and real-valued neural networks for disease
detection. *Diagnostics, 12*(8), Artículo 1893.
https://doi.org/10.3390/diagnostics12081893

Jojoa Acosta, M. F., Caballero Tovar, L. Y., Garcia-Zapirain, M. B., & Percybrooks,
W. S. (2021). Melanoma diagnosis using deep learning techniques on dermatoscopic
images. *BMC Medical Imaging, 21*, Artículo 6.
https://doi.org/10.1186/s12880-020-00534-8

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in
machine-learning-based science. *Patterns, 4*(9), 100804.
https://doi.org/10.1016/j.patter.2023.100804

Kurtansky, N., Rotemberg, V., Gillis, M., Kose, K., Reade, W., & Chow, A. (2024).
*ISIC 2024 - Skin Cancer Detection with 3D-TBP* [Competencia]. Kaggle.
https://www.kaggle.com/competitions/isic-2024-challenge

Kurtansky, N. R. (2024). *Challenge-2024-Metrics* [Software]. GitHub.
https://github.com/ISIC-Research/Challenge-2024-Metrics

Kurtansky, N. R., D’Alessandro, B. M., Gillis, M. C., Betz-Stablein, B.,
Cerminara, S. E., Garcia, R., Girundi, M. A., Goessinger, E. V., Gottfrois, P.,
Guitera, P., Halpern, A. C., Jakrot, V., Kittler, H., Kose, K., Liopyris, K.,
Malvehy, J., Mar, V. J., Martin, L. K., Mathew, T.,
… Rotemberg, V. (2024). The SLICE-3D dataset:
400,000 skin lesion image crops extracted from 3D TBP for skin cancer detection.
*Scientific Data, 11*, 884. https://doi.org/10.1038/s41597-024-03743-w

Kurtansky, N. R., Gillis, M. C., Codella, N. C. F., D’Alessandro, B. M., Ge, Z.,
Guitera, P., Halpern, A. C., Kittler, H., Malvehy, J., Liopyris, K., Mar, V. J.,
Martin, L. K., Maul, L. V., Navarini, A., Rajeswaran, T., Rajeswaran, V.,
Reichman, N., Soyer, H. P., Weber, J., … Kose, K. (2025). Automated triage of
cancer-suspicious skin lesions with 3D total-body photography. *npj Digital
Medicine, 8*, Artículo 708. https://doi.org/10.1038/s41746-025-02070-7

Little, M. A., Varoquaux, G., Saeb, S., Lonini, L., Jayaraman, A., Mohr, D. C., &
Kording, K. P. (2017). Using and understanding cross-validation strategies:
Perspectives on Saeb et al. *GigaScience, 6*(5), gix020.
https://doi.org/10.1093/gigascience/gix020

Marchetti, M. A., Nazir, Z. H., Nanda, J. K., Dusza, S. W., D’Alessandro, B. M.,
DeFazio, J., Halpern, A. C., Rotemberg, V. M., & Marghoob, A. A. (2023). 3D
whole-body skin imaging for automated melanoma detection. *Journal of the European
Academy of Dermatology and Venereology, 37*(5), 945–950.
https://doi.org/10.1111/jdv.18924

McClish, D. K. (1989). Analyzing a portion of the ROC curve. *Medical Decision
Making, 9*(3), 190–195. https://doi.org/10.1177/0272989X8900900307

Mejía Posada, M. I., Gutiérrez Gómez, M., Vásquez-Trespalacios, E. M., Garces Abad,
M. A., Londoño García, A. M., & González Álvarez, T. (2024). [Translated article]
Dermoscopic changes in melanocytic lesions in 368 patients with atypical nevus
syndrome and their association with melanoma incidence: A cohort study. *Actas
Dermo-Sifiliográficas, 115*(2), T130–T136. https://doi.org/10.1016/j.ad.2023.11.018

Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error.
*Machine Learning, 52*(3), 239–281. https://doi.org/10.1023/A:1024068626366

Novoselskiy, I. (2024). *isic-2024* [Software]. GitHub.
https://github.com/ilyanovo/isic-2024

Rios-Duarte, J. A., Diaz-Valencia, A. C., Combariza, G., Feles, M., & Peña-Silva,
R. A. (2024). Comprehensive analysis of clinical images contributions for melanoma
classification using convolutional neural networks. *Skin Research and Technology,
30*(5), Artículo e13607. https://doi.org/10.1111/srt.13607

Saeb, S., Lonini, L., Jayaraman, A., Mohr, D. C., & Kording, K. P. (2017). The
need to approximate the use-case in clinical machine learning. *GigaScience,
6*(5), gix019. https://doi.org/10.1093/gigascience/gix019

Sáenz, J. P., Novoa, M. P., Correal, D., & Eapen, B. R. (2018). On using a mobile
application to support teledermatology: A case study in an underprivileged area in
Colombia. *International Journal of Telemedicine and Applications, 2018*, Artículo
1496941. https://doi.org/10.1155/2018/1496941

Walter, S. D. (2005). The partial area under the summary ROC curve. *Statistics in
Medicine, 24*(13), 2025–2040. https://doi.org/10.1002/sim.2103

Yan, S., Yu, Z., Primiero, C., Vico-Alonso, C., Wang, Z., Yang, L., Tschandl,
P., Hu, M., Ju, L., Tan, G., Tang, V., Ng, A. B., Powell, D., Bonnington, P.,
See, S., Magnaterra, E., Ferguson, P., Nguyen, J., Guitera, P., … Ge, Z.
(2025). A multimodal vision foundation model for clinical dermatology. *Nature
Medicine, 31*(8), 2691–2702. https://doi.org/10.1038/s41591-025-03747-y

Yang, H., Lu, K., Lyu, X., & Hu, F. (2019). Two-way partial AUC and its
properties. *Statistical Methods in Medical Research, 28*(1), 184–195.
https://doi.org/10.1177/0962280217718866

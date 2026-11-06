## Estado del arte

<!-- Sección nueva de informe/borrador-v2.md, antes de «Método». Versión 2:
     incluye el resultado de outputs/efecto-particion.json. Responde a la
     retroalimentación del docente: comparar con otros trabajos académicos,
     darles reconocimiento y declarar qué suma este proyecto. Mismas
     convenciones que las demás secciones; LOCAL = contrastar en
     referencias/_texto-completo/. Las citas salen de
     informe/insumos/estado-del-arte-comparacion.md, que ya las comprobó
     contra referencias/. -->

Este trabajo se apoya en cuatro líneas de trabajo previo. De cada una se dice
qué hizo, en qué se contrasta con las demás y qué toma o añade este proyecto.

### El triaje sobre fotografía corporal total

El conjunto de datos, SLICE-3D, se publicó con un objetivo explícito: *"to
facilitate the development of open-source AI algorithms capable of rendering
diagnostic decisions from reduced quality, clinical photos resembling the
resolution of smartphone images"*.
<!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, línea 109, cita literal -->
Reúne todas las lesiones de más de 1.000 pacientes, atendidos en siete
consultas dermatológicas de alto riesgo de tres continentes.
<!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, línea 111 («every lesion from a sample of 1,000+ patients … across seven high-risk dermatologic practices and three continents») -->

Antes del reto, Marchetti et al. (2023) estudiaron si el melanoma se
distingue de otras lesiones con los datos del análisis automático de esas
imágenes. En una muestra de conveniencia de un solo centro, con 35 pacientes
y 23.538 lesiones, obtuvieron un AUC de 0,94.
<!-- F: referencias/_texto-completo/marchetti-2023-resumen-pubmed.txt, líneas 7, 9 y 11 (LOCAL; solo resumen) -->
Los organizadores evaluaron después ese enfoque en los datos de evaluación del
reto: en la clasificación de melanoma obtuvo un AUC de 0,893 y una pAUC de
0,114, frente a 0,176 de la mejor entrega.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, Tabla 3, «Melanoma classification», filas «Marchetti et al.» y «Best across all ISIC'24 submissions» (líneas 217–218); nota a de la tabla: se excluyeron 209 lesiones de un paciente incluido en los dos estudios -->
*Interpretación, no medición:* un mismo enfoque da cifras distintas según en
qué datos se evalúe.

Los organizadores publicaron también su análisis del reto (Kurtansky et al.,
2025). Con un estudio de ablación sobre la solución ganadora encontraron que
el contexto de paciente tuvo un efecto *"substantial"* y que *"Tiles were less
informative than the pre-extracted WB360 measurements"*.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, líneas 61 y 248, citas literales -->
Este trabajo reproduce sobre sus propias particiones la parte tabular de esa
solución (Novoselskiy, 2024), y es esa parte, sin dos sesgos conocidos a su
favor, la que recomienda.
<!-- F: «Método», «Qué se compara» (M3 y M3 limpio); «Recomendación», «Qué se recomienda» -->
En el contexto de paciente, los resultados coinciden en dirección: aquí
también mejora las métricas de triaje. Las magnitudes no se comparan, porque
se midieron en otros datos y con otras particiones. Con la imagen la
comparación no procede: el ganador ajustó sus propias redes; aquí se probó un
extractor congelado y, después, una red pequeña entrenada sobre los recortes.
<!-- F: «Resultados», «La métrica principal no agota lo que pidió el cliente»; PLAN.md, Fase 4, «Orden de magnitud, no comparación»; «Método», «Qué se compara» (las redes de imagen del ganador quedan fuera) y «El extractor de imagen»; PLAN.md, Fase 4c, «La red» (la red pequeña, EfficientNet-B0, entrenada de punta a punta) -->

### Cómo se evalúa un sistema de triaje

McClish (1989) propuso calcular el área bajo una porción de la curva ROC:
*"Numerical integration is suggested for evaluating the area under a portion
of the ROC curve"*.
<!-- F: referencias/_texto-completo/mcclish-1989-pauc-original.md, línea 49, cita literal (LOCAL; solo resumen) -->
Walter (2005), en el contexto del metaanálisis, concluye que *"on balance the
use of the full AUC is preferred"*.
<!-- F: referencias/_texto-completo/walter-2005-pauc-sroc-en-metaanalisis.md, línea 48, cita literal (LOCAL; solo resumen) -->
Yang et al. (2019) proponen restringir los dos ejes de la curva: la
sensibilidad y la tasa de falsos positivos.
<!-- F: referencias/_texto-completo/yang-arxiv-1508.00298v3.txt, líneas 73–74 (LOCAL) -->
El reto restringe solo la sensibilidad, y lo justifica en términos clínicos.
<!-- F: «Método», «Qué se mide»; referencias/_texto-completo/kaggle-evaluation.md, líneas 17–20 (LOCAL) -->
Y los organizadores añaden dos métricas para escenarios de triaje: *"To gauge
performance in theoretical triaging scenarios, two additional metrics were
defined: SEtop-15 and NNTx% SE"*.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 307, cita literal -->

Este trabajo no elige entre ellas. Toma la métrica que eligió el cliente y lee
a su lado el AUC y las dos métricas de triaje, porque sobre las mismas
predicciones pueden discrepar. En la partición de la semilla 42, el gradient
boosting sin balancear tiene un AUC de 0,582, por encima del azar de su
escala, y una pAUC por debajo del azar de la suya.
<!-- F: «Método», «Qué se mide»; «Resultados», «Una decisión por defecto cambia el veredicto»; outputs/modelado-baseline.json > nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media -->

### Validación cuando las observaciones no son independientes

Saeb et al. (2017) se propusieron demostrar el sesgo que produce validar sin
respetar al sujeto, y prescriben: *"If the use-case is diagnosis, i.e., we
want to develop global models that can be used for new subjects, CV must be
subject-wise"*.
<!-- F: referencias/saeb-2017-validacion-por-sujeto.md, línea 146 (el objetivo) y línea 134, cita literal -->
Una revisión en tres partes, nacida de la revisión por pares de ese artículo,
matiza la regla. Little sostiene que la validación por sujeto *"does not
always work"* y sugiere, como solución pragmática, probar las dos
particiones. Varoquaux, en la misma revisión, sostiene que el uso previsto
decide: *"the intended usage should dictate the cross-validation setting"*.
<!-- F: referencias/little-2017-perspectivas-sobre-saeb.md, línea 171 (la revisión) y líneas 211, 231 y 263, citas literales -->
Kapoor y Narayanan (2023) clasifican la no independencia entre entrenamiento
y prueba como una forma de fuga. En su caso de estudio, al corregir la fuga,
los modelos complejos dejan de superar a la regresión logística, salvo en un
artículo, donde la diferencia de AUC baja de 0,14 a 0,01.
<!-- F: referencias/kapoor-2023-fuga-y-reproducibilidad.md, línea 218 (L3.2) y línea 304 («Each paper suffered from different forms of leakage»; «complex ML models perform no better than baseline LR models in each case except Wang»; «drops from 0.14 to 0.01») -->
Dentro de los conjuntos de ISIC, Cassidy et al. (2022) encontraron imágenes
duplicadas repartidas entre entrenamiento y prueba, y sugieren, como paso de
limpieza, quedarse con imágenes de pacientes únicos.
<!-- F: referencias/cassidy-2022-duplicados-isic.md, líneas 154–155 y 850–853 -->

Este trabajo sigue el criterio del uso. El reto se evalúa con pacientes
distintos de los de entrenamiento, así que la validación agrupa por paciente.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299 («albeit different patients than the training dataset»); «Datos y validación», «La partición: por paciente» -->
Y se midió qué evita esa agrupación: una partición por filas habría dejado al
98,92% de los pacientes a los dos lados.
<!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga -->

Como sugiere Little, se probaron también las dos particiones. Con la
logística y el gradient boosting balanceados, partir por filas no cambia de
forma distinguible la pAUC, el AUC ni el NNT80% SE, ni el veredicto entre los
dos modelos.
<!-- F: «Resultados», «Partir por filas no cambia el veredicto»; outputs/efecto-particion.json > filas_menos_paciente, particiones.paciente.comparacion_2b_menos_1 y particiones.filas.comparacion_2b_menos_1; PLAN.md, Fase 6, «El efecto de la partición: especificación y regla de lectura» -->
La agrupación por paciente se sostiene, entonces, por el uso y no porque aquí
cambie el resultado.
<!-- F: interpretación de este proyecto, sobre las dos frases anteriores -->

### Qué se ha investigado en Colombia

La producción colombiana cercana a este trabajo responde a tres preguntas
distintas: cómo llevar al paciente hasta el especialista, cómo clasificar una
lesión a partir de su imagen y qué lesiones debe mirar primero el
especialista.
<!-- F: interpretación de este proyecto, que ordena los trabajos de abajo; PLAN.md, Fase 0, «Pendiente del estado del arte» (el contraste acceso frente a selección) -->

La primera es la del acceso. Sáenz et al. (2018) probaron, en una brigada de
salud rural sin dermatólogo, una aplicación de apoyo al diagnóstico remoto.
Barrera-Valencia y Perea-Flórez (2024) compararon un servicio de
teledermatología para población rural dispersa con computador y cámara frente
a teléfono inteligente.
<!-- F: referencias/saenz-2018-app-teledermatologia-colombia.md, línea 234; referencias/barrera-valencia-2024-costos-teledermatologia.md, líneas 60–64 -->

La segunda es la del diagnóstico. Rios-Duarte et al. (2024), Jojoa Acosta et
al. (2021) y Jojoa et al. (2022) entrenan redes que clasifican melanoma a
partir de imágenes clínicas o dermatoscópicas de conjuntos públicos.
<!-- F: referencias/rios-duarte-2024-cnn-melanoma-uniandes.md, líneas 250 y 252; referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md, líneas 145 y 177; referencias/jojoa-2022-redes-complejas-melanoma.md, líneas 135 y 247 -->

La tercera es la de la selección, y es la de este trabajo. Mejía Posada et
al. (2024) estudiaron retrospectivamente a 368 pacientes en seguimiento con
mapeo corporal digital en una clínica de Medellín, y encontraron qué rasgos
dermatoscópicos se asocian a un menor tiempo hasta el melanoma.
<!-- F: referencias/mejia-posada-2024-mapeo-corporal-medellin.md, líneas 189 («retrospective follow-up study»), 190, 219 y 230 -->
Este trabajo aborda la misma pregunta con otros datos: las mediciones
automáticas de todas las lesiones de cada paciente, ordenadas para que el
especialista mire primero las más sospechosas.
<!-- F: «Datos y validación», «Los datos»; «Recomendación», «Qué no se puede afirmar» («Los modelos ordenan lesiones por sospecha») -->
Los tres trabajos de aprendizaje automático entrenan y evalúan con
conjuntos públicos ya publicados, y Rios-Duarte et al. advierten que esas
fuentes no dan la ascendencia de los pacientes. Los datos de este trabajo no
son colombianos: ninguno de los centros de SLICE-3D está en América Latina.
<!-- F: referencias/rios-duarte-2024-cnn-melanoma-uniandes.md, líneas 252, 256 («These sources did not provide details regarding the ancestry of patients») y 662; referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md, líneas 145, 237 y 724; referencias/jojoa-2022-redes-complejas-melanoma.md, líneas 247, 251 y 261; referencias/kurtansky-2024-slice3d-descriptor.md, línea 134 (los siete centros); informe/anteproyecto.md, 5.1, punto 5 -->

Este proyecto no propone una arquitectura nueva. Frente a los trabajos de
diagnóstico, lo que cambia es cómo se elige y se compara un modelo.
Rios-Duarte et al. eligen el mejor modelo por su AUC de validación; Jojoa
Acosta et al. comparan cinco modelos sobre un mismo conjunto de prueba y
reentrenan el mejor; Jojoa et al. comparan las medias de diez pliegues con
una prueba t.
<!-- F: referencias/rios-duarte-2024-cnn-melanoma-uniandes.md, línea 175; referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md, líneas 285 y 335; referencias/jojoa-2022-redes-complejas-melanoma.md, líneas 468 y 472 -->
Aquí la regla de recomendación se fijó antes de correr la comparación, el
conjunto reservado se abre una sola vez, y el intervalo se corrige porque los
pliegues comparten datos de entrenamiento.
<!-- F: «Método», «Qué se fijó antes de medir» y «Cómo se compara» -->

### Qué suma este proyecto

Lo que este trabajo añade a esas cuatro líneas es medir, sobre un mismo
conjunto, cuánto cambia el veredicto según las decisiones que se aceptan por
defecto:
<!-- F: informe/anteproyecto.md, 3, objetivo general; CLAUDE.md, «Tesis del proyecto» -->

- **La métrica.** El AUC y la pAUC discrepan sobre si el gradient boosting
  sin balancear supera al azar, y la pAUC no distingue ventajas que el AUC o
  las métricas de triaje sí distinguen.
  <!-- F: «Resultados», «Una decisión por defecto cambia el veredicto», «Una ventaja que la pAUC no ve» y «La métrica principal no agota lo que pidió el cliente» -->
- **El desbalance.** El mismo modelo pasa de una pAUC de 0,0018 a 0,1375 con
  solo ponderar las clases.
  <!-- F: «Resultados», «Una decisión por defecto cambia el veredicto»; outputs/validacion-repetida.json > nivel_2a_gradient_boosting_sin_balancear.pauc_media_global y nivel_2b_gradient_boosting_balanceado.pauc_media_global -->
- **La comparación.** Dos veces, un resultado de una sola partición no
  sobrevivió a la validación repetida.
  <!-- F: «Método», «Cómo se compara»; CLAUDE.md, «Hallazgos vivos», hallazgo 3 -->
- **La partición.** Una partición por filas dejaría al 98,92% de los
  pacientes a los dos lados, pero con los dos modelos probados no cambia el
  veredicto. Aquí la decisión por defecto se midió y no pesó.
  <!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga; «Resultados», «Partir por filas no cambia el veredicto» -->

Y lee entera la función de utilidad del cliente: con la pAUC sola, el
contexto de paciente no aporta; con la sensibilidad top-15 y el NNT80% SE, sí.
<!-- F: «Resultados», «La métrica principal no agota lo que pidió el cliente» -->
Por último, lleva la auditoría de fugas al preentrenamiento: PanDerm quedó
fuera porque su artículo declara datos de ISIC 2024 entre los suyos.
<!-- F: «Método», «El extractor de imagen» -->

## Método

<!-- Borrador de una sección de informe/borrador-v2.md. Cada comentario «F:»
     da la fuente de la frase o cifra que lo precede. Las marcadas «LOCAL» se
     contrastan con referencias/_texto-completo/, que solo está en el Mac. Los
     comentarios se quitan o se convierten en el anexo de trazabilidad al
     cerrar el informe. -->

### Qué se mide

**La métrica principal es la del reto:** el área parcial bajo la curva ROC por
encima del 80% de sensibilidad, o pAUC, que va de 0 a 0,2.
<!-- F: referencias/kaggle-evaluation.md, «Citas literales», párrafos 1 y 2, líneas 31–32 y 37–43 (LOCAL) -->
El organizador la justifica en términos clínicos, no estadísticos: *"there are
regions in the ROC space where the values of TPR are unacceptable in clinical
practice"*, y *"Systems that aid in diagnosing cancers are required to be
highly-sensitive"*.
<!-- F: referencias/kaggle-evaluation.md, párrafo 2, líneas 39–41, cita literal (LOCAL) -->
Esa es la función de utilidad del cliente, escrita en su métrica: la región
del espacio ROC donde la sensibilidad es clínicamente inaceptable no cuenta.
<!-- F: interpretación del proyecto; CLAUDE.md, «Tesis del proyecto» -->
Un clasificador al azar obtiene 0,02 y uno perfecto, 0,2.
<!-- F: outputs/modelado-baseline.json > escala_de_referencia_pauc.azar y .maximo -->

La implementación de la pAUC es una transcripción del algoritmo del
organizador, comprobada contra su script en 200 casos aleatorios, con
coincidencia exacta, y en el caso del clasificador perfecto, que devuelve
0,2.
<!-- F: .claude/skills/modelado-baseline/SKILL.md, «Sobre la métrica: VERIFICADA (2026-08-11)»; outputs/modelado-baseline.json > metrica_fuente y escala_de_referencia_pauc.maximo -->

**El cliente declaró dos ejes más, con premio propio:** *"Two Secondary
Prizes: $7,500 each for "Top-15 Retrieval Sensitivity" and "Model
Efficiency""*.
<!-- F: referencias/kaggle-rules.md, «Premios secundarios», líneas 25–26, cita literal (LOCAL) -->
La pAUC no captura ninguno de los dos.
<!-- F: CLAUDE.md, «Tesis del proyecto», «Corolario» -->

- **Sensibilidad top-15 por paciente (SEtop-15).** El premio se otorga al
  algoritmo *"most successful in scoring malignancies within the top-15
  highest scored images per patient"*.
  <!-- F: referencias/isic-metrics-readme.md, «Top-15 retrieval sensitivity», líneas 64–66, cita literal (LOCAL) -->
  Se calcula como la media, sobre los pacientes con alguna lesión maligna, de
  la fracción de sus lesiones malignas que quedan entre sus 15 de mayor
  puntuación. Así cada paciente enfermo pesa lo mismo, como la describen
  Kurtansky et al. (2025): *"weighed each diseased patient equally"*.
  <!-- F: .claude/skills/modelado-baseline/scripts/metricas_triaje.py, docstring; referencias/kurtansky-2025-triaje-automatizado-tbp.md, métodos, línea 307 -->
  La implementación coincide con el script del organizador, ejecutado sin
  modificar, en seis conjuntos sintéticos con empates.
  <!-- F: .claude/skills/modelado-baseline/SKILL.md, sección de metricas_triaje.py; test_metricas_triaje.py -->
- **Eficiencia.** El organizador la evaluó como *"inference time on an
  undisclosed subset of test set images"*.
  <!-- F: referencias/isic-metrics-readme.md, «Model Efficiency», líneas 71–72, cita literal (LOCAL) -->
  Aquí se mide como tiempo de inferencia, con la definición de más abajo.

Se reportan además otras dos métricas:

- **NNT80% SE**, de Kurtansky et al. (2025): *"the average number of lesions
  needed to triage to undergo expert evaluation to detect a single
  malignancy, using a threshold corresponding to a given sensitivity"*.
  <!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, métodos, línea 307, cita literal -->
  El organizador no publica script para ella, así que la lectura operativa es
  de este proyecto: el umbral es el más alto con el que la sensibilidad llega
  al 80%, y el NNT es el número de lesiones marcadas por cada maligna
  capturada. Con empates en el umbral, entran todas.
  <!-- F: .claude/skills/modelado-baseline/scripts/metricas_triaje.py, docstring -->
- **El AUC estándar**, porque el desacuerdo entre las dos métricas sobre las
  mismas predicciones ya es un hallazgo del proyecto.
  <!-- F: PLAN.md, Fase 4, «Qué se hace» -->

### Cómo se compara

Todas las comparaciones se hacen sobre el conjunto de desarrollo, con
validación cruzada de 5 pliegues agrupada por paciente y estratificada por la
etiqueta, repetida con 10 semillas (de la 0 a la 9).
<!-- F: outputs/validacion-repetida.json > semillas_corridas, n(semillas_corridas) y n_splits; outputs/diseno-validacion.json > esquema (StratifiedGroupKFold, group_col patient_id) -->
Los dos modelos de cada comparación se evalúan sobre los mismos pliegues, así
que cada comparación da 50 diferencias pareadas.
<!-- F: outputs/fase4-m2-vs-m1.json, outputs/fase4-m4-vs-m2.json, outputs/fase4-m4b-vs-m2.json, outputs/fase4-m3-vs-m2.json y outputs/fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.*.n_diferencias -->

El intervalo de la diferencia media se corrige por el solape entre los
conjuntos de entrenamiento, con la corrección de Nadeau y Bengio (2003): la
varianza de las diferencias se multiplica por 1/n + n_prueba/n_entrenamiento,
que en 5 pliegues es 1/n + 1/4, con el mismo t de n − 1 grados de libertad.
<!-- F: .claude/skills/modelado-baseline/scripts/evaluar_repetido.py, _nadeau_bengio; referencias/nadeau-bengio-2003-t-corregido.md, sección 4, líneas 60–74 y 95 (LOCAL) -->
El artículo deriva la corrección para divisiones aleatorias independientes,
y sus autores presentan ese estimador como cercano al de la validación
cruzada por K pliegues. Aquí se aplica a una validación cruzada por pliegues:
cercana, no igual.
<!-- F: paráfrasis, no cita: referencias/nadeau-bengio-2003-t-corregido.md, «El escenario en que el artículo deriva la fórmula», líneas 34–56, p. 242 (LOCAL) -->
El intervalo sin corregir no se cita: supone una independencia que el solape
no cumple, y en este proyecto ya dio una vez un intervalo que excluía el cero
cuando el corregido lo contenía.
<!-- F: PLAN.md, Fase 4, «Qué se hace» -->

**El criterio:** una diferencia se da por establecida solo si su intervalo
corregido al 95% no contiene el cero. Junto al intervalo se reportan los
pliegues y las semillas en que gana cada modelo.
<!-- F: CLAUDE.md, extensión, E2 («la mejora no se da por establecida si ese intervalo contiene el cero»); PLAN.md, Fase 4, «Contingencia» y «Reporte» («victorias por pliegue y por semilla») -->
Y ninguna conclusión comparativa se escribe desde una sola partición: dos
veces, un resultado de una sola partición no sobrevivió a la validación
repetida.
<!-- F: CLAUDE.md, «Hallazgos vivos», hallazgo 3 -->

### Qué se compara

| Modelo | Qué es |
|---|---|
| M1 | Gradient boosting (`HistGradientBoostingClassifier`) con `class_weight="balanced"`: el nivel 2b del modelado base. |
| M2 | M1 más el contexto de paciente: el z-score de cada una de las 34 variables numéricas de M1 dentro del paciente, los conteos y las sumas de área por paciente, y el LOF ajustado paciente por paciente. |
| M3 | La parte tabular de la solución ganadora del reto, reproducida desde su código público: CatBoost sobre la metadata y el contraste dentro del paciente, con los hiperparámetros publicados. |
| M3 limpio | M3 sin los dos sesgos conocidos a su favor: las transformaciones sin etiqueta se ajustan dentro de cada pliegue, los hiperparámetros vuelven a los valores por defecto de CatBoost, con la parada temprana de M3, y no se descartan las 22 columnas de la celda 24 del notebook. |
| M4 | M2 más las 384 variables de imagen de DINOv2 ViT-S/14, tal cual. |
| M4b | M2 más dos variables de imagen: la puntuación de una regresión logística balanceada sobre las 384, y esa puntuación dividida por su media dentro del paciente. |

<!-- F: PLAN.md, Fase 4: decisión del 2026-09-25 (M1, M2, M3, M4), «Variante secundaria M4b», «M3 limpio y regla de recomendación»; outputs/fase4-m3limpio-vs-m2.json > hiperparametros; .claude/skills/modelado-baseline/SKILL.md, «Contexto de paciente, las variables de M2» (las 34 variables) -->

La Fase 4b probó tres combinaciones de M3 limpio, y la Fase 4c una red de
imagen entrenada, EfficientNet-B0, sola y apilada sobre M3 limpio (C4).
<!-- F: PLAN.md, Fase 4b, «Qué se compara» (C1, C2 y C3, descritos ahí); PLAN.md, Fase 4c, «La red», «Pregunta 1» y «Pregunta 2» (C4, descrito ahí) -->

Los modelos propios no se ajustan: usan los hiperparámetros del nivel 2b; la
red de la Fase 4c usa los ajustes fijos de su prueba de tiempo.
<!-- F: PLAN.md, Fase 4, «Sin ajuste de hiperparámetros»; outputs/fase4-m3limpio-vs-m2.json > hiperparametros; PLAN.md, Fase 4c, «Cómo se entrena, fijado antes de correr y sin ajuste»; outputs/prueba-tiempo-red-imagen.json > entrada y entrenamiento -->
De la solución ganadora quedan fuera, cada cosa con su motivo, las dos redes
de imagen, por un costo que no se estimó; el modelo entrenado con el ISIC
Archive, por riesgo de fuga, y la razón de cada predicción a la media del
paciente, que en el código solo se calcula sobre las predicciones de esos
tres modelos de imagen. Cada cambio al código publicado está declarado.
<!-- F: PLAN.md, Fase 4, «Comparador añadido», «Quedan fuera, con su motivo» y la lista de parches -->

Las comparaciones principales se fijaron antes de correr ningún modelo con
imagen: M2 − M1, M4 − M2 y el mejor de los modelos propios frente a M3.
<!-- F: PLAN.md, Fase 4, decisión del 2026-09-25, «Comparaciones principales, fijadas» -->
Ese mejor fue M2, por su pAUC media en desarrollo. M4b, con una media mayor,
quedó fuera por ser una variante secundaria.
<!-- F: PLAN.md, Fase 4, «Comparador fijado: M2» -->
M4b − M2 se reporta como secundaria, y M3 limpio − M2 es la corrida de la
regla de recomendación.
<!-- F: PLAN.md, Fase 4, «Variante secundaria M4b» y «M3 limpio y regla de recomendación» -->

### El extractor de imagen

Un modelo de imagen preentrenado puede traer fuga en sus pesos: si se
preentrenó con estas mismas imágenes, lo que aporte no se puede atribuir al
método, y esa fuga no se puede quitar después.
<!-- F: PLAN.md, Fase 2, «No se extrae ni una característica antes de cerrar esto» -->
Por eso no se extrajo ninguna característica antes de decidir qué modelo usar,
y los criterios para decidirlo se fijaron antes de conocer lo que cada fuente
decía sobre SLICE-3D.
<!-- F: PLAN.md, Fase 2, «No se extrae ni una característica antes de cerrar esto» y regla «fijada antes de leer su fuente»; CLAUDE.md, «Riesgo bloqueante», «Criterio, fijado el 2026-08-18, antes del hallazgo» -->

PanDerm, un modelo fundacional de dermatología, no se usa. Su artículo declara
un subconjunto de ISIC 2024 entre sus datos de preentrenamiento: *"We selected
a subset containing 352,034 tile images, stratified by institutions"*.
<!-- F: referencias/panderm-reduccion-examenes.md, línea 244 («a multimodal dermatology foundation model») y línea 396, cita literal; PLAN.md, Fase 2, «Decisión (2026-09-24, de la persona)» -->
El criterio, fijado antes de conocer ese dato, era no usarlo si había solape.
Que ese preentrenamiento fuera sin etiquetas no se admitió como excepción,
porque el criterio no la preveía.
<!-- F: CLAUDE.md, «Riesgo bloqueante», «Criterio, fijado el 2026-08-18, antes del hallazgo»; PLAN.md, Fase 2, «Decisión (2026-09-24, de la persona)»; referencias/panderm-reduccion-examenes.md, línea 364 («unlabeled») -->

Para los modelos genéricos se fijó una regla, también antes de leer sus
fuentes. Un modelo cuenta como verificado si sus pesos o sus datos de
preentrenamiento son anteriores a la primera fecha en que los datos de
SLICE-3D fueron públicos y sus autores no pertenecen a las instituciones que
los aportaron, o si su documentación enumera fuentes cerradas que excluyen
SLICE-3D.
<!-- F: PLAN.md, Fase 2, «Decisión (2026-09-24, de la persona): regla de verificación del extractor de imagen» -->
DINOv3 no la cumple: su artículo es de agosto de 2025, y la sección que
describe sus datos no da la fecha en que se recogieron sus imágenes de
Instagram ni nombra los conjuntos semilla con que se seleccionó una de
sus partes.
<!-- F: PLAN.md, Fase 2, «Decisión (2026-09-25, de la persona)»; referencias/simeoni-2025-dinov3.md, «Dónde» y «Lo que se buscó y no se encontró», líneas 9–10 y 64–74 -->
DINOv2 sí: sus datos de preentrenamiento, LVD-142M, están descritos en un
artículo de abril de 2023, y sus autores no pertenecen a las instituciones que
aportaron los datos. El punto de control que se usó documenta LVD-142M como
sus datos de entrenamiento.
<!-- F: PLAN.md, Fase 2, «Decisión (2026-09-25, de la persona)»; referencias/oquab-2023-dinov2.md, línea 10; PLAN.md, Fase 3, «Preparación (2026-09-25)»; referencias/dinov2-repositorio.md, línea 47 -->
Queda una salvedad: ninguna fuente fija la primera fecha en que SLICE-3D fue
público, y el orden temporal se apoya en una cadena de evidencia.
<!-- F: PLAN.md, Fase 2, «Salvedad declarada»; referencias/slice3d-fechas-de-publicacion.md, sección 5, líneas 11–13 y 96–99 -->

*Interpretación, no medición:* es el razonamiento de la auditoría de fugas, un
nivel más arriba. Con modelos fundacionales, la fuga puede venir del
preentrenamiento de un tercero y no del conjunto de datos.
<!-- F: CLAUDE.md, «Riesgo bloqueante», criterio del 2026-08-18; PLAN.md, Fase 2, «No se extrae ni una característica antes de cerrar esto» -->

### Qué se fijó antes de medir

- **Un resultado negativo también es un resultado.** Si el intervalo
  corregido contiene el cero, la recomendación al cliente es que la imagen no
  aporta lo suficiente para justificar su costo. Lo que no se hace es buscar
  la semilla, el pliegue o la métrica en que la diferencia sí se distinga.
  <!-- F: PLAN.md, Fase 4, «Contingencia» -->
- **La regla de recomendación.** Si el intervalo corregido de la pAUC de M3
  limpio − M2 queda entero por encima de cero, el modelo recomendado es M3
  limpio; en cualquier otro caso, es M2. Se fijó antes de correr esa
  comparación, que se corrió una sola vez.
  <!-- F: PLAN.md, Fase 4, «M3 limpio y regla de recomendación», «Regla de recomendación» y «Solo esta corrida» -->
  M3 limpio difiere de M3 en tres cosas a la vez, así que su resultado no dice
  cuál de los dos sesgos pesaba.
  <!-- F: PLAN.md, Fase 4, «Lectura, declarada antes de correr» -->
- **Las reglas de las fases 4b y 4c se fijaron antes de correr.**
  <!-- F: PLAN.md, Fase 4b, «Regla, fijada antes de correr»; PLAN.md, Fase 4c, «Regla, fijada antes de correr» (las dos reglas, escritas ahí) -->
- **El conjunto reservado se abre una sola vez**, al final, con el modelo
  recomendado fijado en un commit anterior, y su resultado se reporta sea cual
  sea.
  <!-- F: PLAN.md, Fase 5, «Especificación» y «Contingencia» -->

### Cómo se mide el tiempo de inferencia

Se cronometra desde las filas de metadatos de un subconjunto, ya en memoria y
sin la etiqueta, hasta la puntuación de cada lesión. En M4 y M4b se parte
además de las imágenes del archivo original. Queda fuera la carga de los
modelos y de los pesos de DINOv2.
<!-- F: outputs/tiempo-inferencia.json > que_se_cronometra; PLAN.md, Fase 4, «Tiempo de inferencia» -->
Entra todo lo que se calcula al predecir, incluidos las variables por
paciente, el LOF, las transformaciones ya ajustadas y, en M4 y M4b, la
lectura de la imagen y DINOv2.
<!-- F: PLAN.md, Fase 4, «Tiempo de inferencia», «Qué se cronometra» -->

El subconjunto son 16 pacientes completos del conjunto de desarrollo, con
5.008 lesiones, elegidos con una semilla antes de medir.
<!-- F: outputs/tiempo-inferencia.json > subconjunto.n_pacientes, .n_lesiones y .semilla -->
Van pacientes completos porque los modelos con contexto de paciente
necesitan todas las lesiones de un paciente antes de puntuar cualquiera.
<!-- F: PLAN.md, Fase 6, «Definición operativa del tiempo de inferencia» -->
Cada modelo se entrena una vez con los demás 817 pacientes de desarrollo, y
el entrenamiento no se cronometra.
<!-- F: outputs/tiempo-inferencia.json > entrenamiento.pacientes y .no_se_cronometra -->
Se hacen cinco repeticiones seguidas y se reporta la mediana, en segundos por
cada 1.000 lesiones.
<!-- F: outputs/tiempo-inferencia.json > repeticiones; PLAN.md, Fase 6 -->

Antes de cronometrar, un control comprueba que el camino cronometrado da las
mismas puntuaciones que el de la Fase 4, y que quitar cualquiera de sus pasos
lo hace fallar. En M4, quitar la imputación cambia la matriz que entra
al modelo pero no las puntuaciones; ese paso queda cubierto por la matriz.
<!-- F: outputs/tiempo-inferencia.json > control.igualdad y control.pasos_quitados (M4.imputacion: matriz_distinta true, puntuaciones_distintas false); PLAN.md, Fase 4, «Enmienda del control» -->

El equipo es un Apple M4 de 10 núcleos y 16 GB. DINOv2 corre en su GPU, y los
modelos tabulares, en la CPU.
<!-- F: outputs/tiempo-inferencia.json > declaraciones.equipo y declaraciones.dinov2.dispositivo; CLAUDE.md, hallazgo 9, «Salvedad» -->
Por eso los tiempos solo comparan estos modelos entre sí, en este equipo, y
no se comparan con los de la competencia, que usó otro subconjunto y otro
equipo.
<!-- F: PLAN.md, Fase 6, «Qué no se afirma»; CLAUDE.md, hallazgo 9 -->

## Datos y validación

<!-- Sección de informe/borrador-v2.md. Mismas convenciones que «Método»: cada
     comentario «F:» da la fuente de lo que lo precede, y «LOCAL» marca lo que
     se contrasta con referencias/_texto-completo/. -->

### Los datos

Los datos son la metadata del reto: una fila por lesión y 55 columnas, con
las mediciones que el software de la fotografía corporal total calcula sobre
cada lesión, datos del paciente y, solo en el conjunto de entrenamiento, el
diagnóstico.
<!-- F: outputs/eda-diagnostico.json > fuente.n_columnas y columnas_solo_en_train; referencias/kurtansky-2024-slice3d-descriptor.md, Tabla 1 (las tbp_lv_*, el diámetro mayor y la zona del cuerpo llevan el asterisco de la línea 226, «Canfield Scientific, Inc. Lesion Visualizer metric»; la edad y el sexo, no) y línea 199 (el tipo de captura, la luz de la foto 3D); referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299 («estimated solely from 3D TBP images by proprietary Vectra WB360 tooling») -->
El archivo de prueba que publica el reto es un marcador de posición, sin
casos reales. La prueba oculta solo se puede medir enviando modelos a Kaggle,
que da una cifra por envío, sin intervalo; el resultado final con intervalo es
el del conjunto que este proyecto apartó.
<!-- F: outputs/eda-diagnostico.json > test_is_placeholder; referencias/kaggle-code-requirements.md, línea 31 (los envíos se hacen con notebooks); «Resultados», «En la prueba de Kaggle» y «El conjunto reservado, abierto una sola vez» -->

### El conjunto reservado

Antes de volver a medir nada, se apartó el 20% de los pacientes —no de las
filas—, estratificado por centro y por tener al menos una lesión maligna, con
semilla 2026, y se selló.
<!-- F: outputs/holdout-pacientes.json > metodo.fraccion y semilla; PLAN.md, Fase 1, «Qué se hace» y «Decisiones de la persona sobre el conjunto reservado (2026-09-25)» -->
Ningún estrato quedó vacío: todos los centros tienen al menos un paciente con
lesión maligna a cada lado.
<!-- F: PLAN.md, Fase 1, «Sellado (2026-09-25)» -->
Desde entonces y hasta abrirlo, una sola vez, todas las mediciones de este
informe son del conjunto de desarrollo; las del reservado y las de Kaggle van en
«Resultados», «El conjunto reservado, abierto una sola vez» y «En la prueba de
Kaggle».
<!-- F: «Resultados», «El conjunto reservado, abierto una sola vez» y «En la prueba de Kaggle»; PLAN.md, Fase 1, «Estado»; outputs/auditoria-de-fugas.json, outputs/diseno-validacion.json, outputs/eda-diagnostico.json, outputs/efecto-particion.json, outputs/fase4-m2-vs-m1.json, outputs/fase4-m3-vs-m2.json, outputs/fase4-m3limpio-vs-m2.json, outputs/fase4-m4-vs-m2.json, outputs/fase4-m4b-vs-m2.json, outputs/fase4b-c1-vs-m3limpio.json, outputs/fase4b-c2-vs-m3limpio.json, outputs/fase4b-c3-vs-m3limpio.json, outputs/fase4c-c4-vs-m3limpio.json, outputs/fase4c-control-atajo.json, outputs/fase4c-red-sola-vs-imagen.json, outputs/fase4d-c5-vs-m3limpio.json, outputs/fase4d-c6-vs-m3limpio.json, outputs/fase4d-red-mejorada-vs-red.json, outputs/fase4e-c7-vs-m3limpio.json, outputs/fase4e-exploracion.json, outputs/fase4e-red-vs-red4c.json, outputs/fase4f-red4e-vs-imagen-basicos.json, outputs/imagen-sola.json, outputs/mecanismo-2a.json, outputs/modelado-baseline.json, outputs/prueba-tiempo-dinov2.json, outputs/prueba-tiempo-red-4e.json, outputs/prueba-tiempo-red-imagen.json, outputs/sensibilidad-procedencia-repetida.json, outputs/sensibilidad-procedencia.json, outputs/tiempo-inferencia.json y outputs/validacion-repetida.json > datos.conjunto (los 32 dicen «desarrollo») -->

El reservado no es ajeno a lo que se decidió antes de apartarlo, con todos
los datos: qué columnas se excluyen —salvo las dos de procedencia, decididas
después del sellado—, qué niveles de referencia se comparan, y los
hiperparámetros y las columnas descartadas de la solución ganadora.
<!-- F: informe/anteproyecto.md, sección 4.2; PLAN.md, Fase 1, «Sellado (2026-09-25)» y «Decisión de la persona sobre las columnas de procedencia (2026-09-25)»; commits «Fase 1: sellar el conjunto reservado» (2026-09-25 18:07) y «auditoria-de-fugas: columnas de procedencia» (2026-09-25 18:35) -->
Tampoco al diseño de las variables de la solución ganadora, que siguen M2 y
M3 limpio y que se publicó sin ningún conjunto reservado.
<!-- F: CLAUDE.md, hallazgo 8, «Salvedad para la Fase 5»; PLAN.md, Fase 5, «Salvedad de M2» -->

### El conjunto de desarrollo

El conjunto de desarrollo tiene 318.229 lesiones de 833 pacientes.
<!-- F: outputs/eda-diagnostico.json > estructura_grupos.n_filas y .n_grupos -->
Solo 317 lesiones son malignas, el 0,0996%, y solo 207 pacientes tienen
alguna.
<!-- F: outputs/eda-diagnostico.json > desbalance_target.conteos y .pct_positivos; outputs/diseno-validacion.json > n_grupos_positivos -->
Cada paciente aporta entre 1 y 6.267 lesiones, con una mediana de 245.
<!-- F: outputs/eda-diagnostico.json > estructura_grupos.filas_por_grupo.min, .max y .mediana -->

Entre las variables que se usan para modelar, faltan valores en tres: la
edad, en el 0,851% de las filas; el sexo, en el 3,179%, y la zona
anatómica, en el 1,808%.
<!-- F: outputs/eda-diagnostico.json > faltantes.age_approx.pct, .sex.pct y .anatom_site_general.pct -->
Las demás columnas con faltantes están entre las que se excluyen, más abajo.
<!-- F: outputs/eda-diagnostico.json > faltantes (lesion_id, iddx_2 a iddx_5, mel_mitotic_index, mel_thick_mm); outputs/modelado-baseline.json > columnas_excluidas -->

### La partición: por paciente

La validación cruzada agrupa por paciente: cada paciente queda entero de un
lado de cada pliegue.
<!-- F: outputs/diseno-validacion.json > esquema.group_col y fuga_de_grupo_detectada -->
En la partición de la semilla 42, cada pliegue de validación tiene entre 166
y 168 pacientes y entre 63 y 64 lesiones malignas.
<!-- F: outputs/diseno-validacion.json > esquema.seed y por_fold[*].n_val_grupos y .n_val_positivos -->

Lo que evita esa agrupación se midió. Una partición aleatoria por filas, con
la misma semilla, habría dejado a 824 pacientes, el 98,92%, con lesiones a
los dos lados.
<!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.n_grupos_con_fuga y .pct_grupos_con_fuga -->
Si eso cambia el resultado también se midió, y con los dos modelos probados
no lo cambia de forma distinguible (ver «Resultados», «Partir por filas no
cambia el veredicto»).
<!-- F: outputs/efecto-particion.json > filas_menos_paciente, particiones.paciente.comparacion_2b_menos_1 y particiones.filas.comparacion_2b_menos_1; PLAN.md, Fase 6, «El efecto de la partición: especificación y regla de lectura» -->
La agrupación se sostiene por el uso: el reto se evalúa con pacientes
distintos de los de entrenamiento.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299 («albeit different patients than the training dataset») -->

### La auditoría de columnas

Antes de modelar, la auditoría de fugas revisa las columnas, y el modelado se
niega a correr sin su reporte.
<!-- F: .claude/skills/modelado-baseline/SKILL.md, requisitos; informe/casos-de-fallo.md, «Caso B» -->
Quedan fuera de los modelos 15 columnas, por cuatro motivos:
<!-- F: outputs/modelado-baseline.json > columnas_excluidas y n(columnas_excluidas) -->

- **11 no existen al predecir.** El conjunto de prueba no las trae. Entre
  ellas están la propia etiqueta, la taxonomía diagnóstica y dos medidas que
  solo existen tras la biopsia.
  <!-- F: outputs/auditoria-de-fugas.json > columnas_solo_en_train y n(columnas_solo_en_train); CLAUDE.md, «Sobre el problema», «Tercera nota» -->
- **Una es constante:** `image_type`.
  <!-- F: outputs/auditoria-de-fugas.json > columnas_constantes -->
- **Una identifica la fila:** `isic_id`.
  <!-- F: outputs/auditoria-de-fugas.json > columnas_identificador -->
- **Dos describen el centro y la licencia de la imagen, no la lesión:**
  `attribution` y `copyright_license`. En un centro nuevo no aportan
  información.
  <!-- F: outputs/auditoria-de-fugas.json > columnas_procedencia y motivo_columnas_procedencia -->
  Su exclusión se sostiene por razón de uso; los resultados muestran que no
  cambia el desempeño de forma distinguible.
  <!-- F: CLAUDE.md, hallazgo 3; PLAN.md, Fase 6, decisión del 2026-10-02 -->

La auditoría también mide, para cada una de las 41 columnas que no son
identificadores, constantes ni exclusivas del entrenamiento, ni `patient_id`,
su AUC por sí sola fuera de muestra, con la partición agrupada por paciente.
Ninguna llega al umbral de sospecha de 0,9; la más alta es `tbp_lv_H`, con
0,8045.
<!-- F: outputs/auditoria-de-fugas.json > univariado (ninguna sospechosa), n(univariado), umbral_auc_sospechoso, univariado[0]; .claude/skills/auditoria-de-fugas/SKILL.md, description; .claude/skills/auditoria-de-fugas/scripts/audit_leakage.py, excluir_del_univariado -->

De las preguntas abiertas de la auditoría, la única que no contestan los
motivos de arriba es `tbp_lv_nevi_confidence`, por su nombre, aunque sí está
en el conjunto de prueba.
<!-- F: outputs/auditoria-de-fugas.json > preguntas_abiertas[0]; CLAUDE.md, «Cuarta nota» -->
El artículo del conjunto de datos la define como *"a convolutional neural
network classifier estimated probability that the lesion is a nevus"*, así
que la calcula el software sobre la imagen y está disponible al predecir. Se
usa. Su AUC por sí sola es 0,6422.
<!-- F: referencias/slice3d-metadata-tbp-lv.md, Tabla 1, líneas 45–46, cita literal; CLAUDE.md, «Cuarta nota — tbp_lv_nevi_confidence»; outputs/auditoria-de-fugas.json > univariado (tbp_lv_nevi_confidence.auc_oof) -->
Queda una salvedad: el clasificador se entrenó con *"approximately 57,000
lesions"*, y el artículo no dice si se solapan con las de este conjunto.
<!-- F: referencias/slice3d-metadata-tbp-lv.md, Tabla 1 y nota 2, líneas 47 y 81–82 -->

## Resultados

<!-- Sección de informe/borrador-v2.md. Mismas convenciones que las
     anteriores. Abreviaturas de los comentarios: VR = outputs/validacion-repetida.json;
     F21 = outputs/fase4-m2-vs-m1.json; F42 = outputs/fase4-m4-vs-m2.json;
     F4b = outputs/fase4-m4b-vs-m2.json; F32 = outputs/fase4-m3-vs-m2.json;
     F3L = outputs/fase4-m3limpio-vs-m2.json; C = comparaciones_nuevo_menos_base;
     IC = intervalo_t_95_nadeau_bengio; EP = outputs/efecto-particion.json;
     MEC = outputs/mecanismo-2a.json; IS = outputs/imagen-sola.json. -->

Salvo donde se indica, las métricas de desempeño son del conjunto de
desarrollo, con 10 semillas y 5 pliegues. Cada diferencia es «nuevo − base»,
y su intervalo es el corregido al 95%. Los pliegues y semillas en que gana el
nuevo se dan entre paréntesis.
<!-- F: «Método», «Cómo se compara»; F21, F42, F4b, F32 y F3L > C.*.nuevo_mejor_en_folds y .nuevo_mejor_en_semillas; F21 > n(semillas_corridas) y n_splits -->

### Una decisión por defecto cambia el veredicto

El mismo gradient boosting da resultados opuestos según una sola opción. Sin
balancear, su pAUC media es 0,0018, por debajo del piso aleatorio de 0,02 en
los 50 pliegues. Con `class_weight="balanced"`, y nada más distinto, llega a
0,1375.
<!-- F: VR > nivel_2a_gradient_boosting_sin_balancear.pauc_media_global y .pauc_por_semilla_y_fold (los valores, todos bajo 0,02); VR > comparacion_pareada_2b_menos_1.n_diferencias (los pliegues de la validación repetida); VR > nivel_2b_gradient_boosting_balanceado.pauc_media_global; outputs/modelado-baseline.json > escala_de_referencia_pauc.azar y nivel_2b_gradient_boosting_balanceado.nota («Única diferencia con 2a: class_weight») -->

La métrica por defecto no es ciega a ese fallo, pero lo lee distinto. En la
partición de la semilla 42, el AUC estándar del modelo sin balancear es
0,582, por encima del azar de su escala, 0,5; su pAUC queda por debajo del
azar de la suya. Las dos métricas discrepan sobre si el modelo supera al azar.
<!-- F: outputs/modelado-baseline.json > esquema_cv.seed, nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media y .pauc_media; outputs/modelado-baseline.json > nivel_0_referencia_univariada.nota («el AUC va de 0.5 (azar) a 1»); CLAUDE.md, hallazgo 1 -->

Se midió también cómo falla el modelo sin balancear, en la partición de la
semilla 42. No es que ponga arriba a más negativos que positivos, en
proporción: con probabilidad de 0,999 o más queda el 0,09% de los negativos y
el 4,42% de los positivos.
<!-- F: MEC > niveles.nivel_2a_gradient_boosting_sin_balancear.total.frac_neg_ge_0999 y .frac_pos_ge_0999; MEC > umbral_alto; MEC > esquema_cv -->
Lo que hace es hundir a una parte de los positivos al fondo del ordenamiento:
el 36,28% queda en o por debajo del percentil 20 de los negativos, frente al
1,58% con el modelo balanceado, y 18 positivos comparten con 191 negativos la
probabilidad mínima, 0.
<!-- F: MEC > niveles.nivel_2a_gradient_boosting_sin_balancear.total.frac_pos_bajo_p20_neg, .n_pos_en_el_minimo, .n_neg_en_el_minimo y .minimo_predicho; MEC > niveles.nivel_2b_gradient_boosting_balanceado.total.frac_pos_bajo_p20_neg -->
Eso es coherente con una pAUC bajo el azar: para capturar el 80% de los
positivos, el umbral tiene que bajar hasta el 20% de positivos de menor rango,
y ese 20% está entre el 0,75% de lesiones con menor puntuación. Ahí queda
marcado más del 99% de las lesiones, cuando al azar quedaría marcado el 80%.
<!-- F: MEC > niveles.nivel_2a_gradient_boosting_sin_balancear.total.deciles_rango_pos[1]; definición de la pAUC («Método», «Qué se mide») -->
Por qué el modelo los hunde no se midió.
<!-- F: CLAUDE.md, Pendientes, el mecanismo del 2a -->

### Una ventaja que la pAUC no ve

El gradient boosting balanceado supera a la regresión logística balanceada
por 0,005 en promedio, con intervalo [−0,0145; 0,0245] (29 de 50 pliegues; 8
de 10 semillas). La ventaja no está establecida.
<!-- F: VR > comparacion_pareada_2b_menos_1.media, .intervalo_t_95_nadeau_bengio, .gana_2b_en, .de, .semillas_a_favor_de_2b y n(semillas_corridas) -->
En las otras tres métricas sí lo está: AUC +0,0228, [0,0012; 0,0444];
sensibilidad top-15 +0,1633, [0,0874; 0,2393]; NNT80% SE −94,82 lesiones por
cada maligna, [−152,31; −37,33].
<!-- F: EP > particiones.paciente.comparacion_2b_menos_1.auc, .setop15 y .nnt80 (media e intervalo_t_95_nadeau_bengio); EP > control_paciente_contra_referencia (reproduce la validación repetida pliegue a pliegue) -->
Como en M2 − M1, la pAUC no distingue una ventaja que las métricas de triaje
sí distinguen.
<!-- F: «La métrica principal no agota lo que pidió el cliente» (M2 − M1) -->

Sobre una sola partición de los datos completos, el boosting parecía además
más estable que la logística. Con las 10 semillas el orden se invierte: su
desviación entre pliegues es 0,0165, frente a 0,0138. Ese argumento se retiró.
<!-- F: CLAUDE.md, hallazgo 2 (la partición única); VR > nivel_2b_gradient_boosting_balanceado.pauc_std_entre_folds, nivel_1_regresion_logistica.pauc_std_entre_folds y n(semillas_corridas) -->

### Las columnas de procedencia no explican la ventaja

Con las columnas de centro y licencia, la diferencia entre el boosting y la
logística es 0,0046; sin ellas, 0,005.
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.a_2b_menos_1_con_procedencia.media y .a_2b_menos_1_sin_procedencia.media -->
Incluirlas mueve el boosting en 0,0021, con intervalo [−0,0082; 0,0124], y
la logística en 0,0025, con [−0,0023; 0,0073].
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.b_2b_con_menos_2b_sin y .c_1_con_menos_1_sin (media e IC) -->
En la logística, incluirlas mejora en las 10 semillas y en 34 de 50
pliegues. La magnitud no está establecida.
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.c_1_con_menos_1_sin.gana_primer_termino_en_semillas, .gana_primer_termino_en_folds y .de_folds -->
La exclusión se sostiene por razón de uso, no de desempeño. Una sola
partición sugería lo contrario; es el segundo resultado de una sola partición
que no sobrevive a la validación repetida.
<!-- F: CLAUDE.md, hallazgo 3; PLAN.md, Fase 6, decisión del 2026-10-02 -->

### Partir por filas no cambia el veredicto

Se probaron las dos particiones con la logística y el gradient boosting
balanceados, con una regla de lectura fijada antes de correr. La partición por
filas infla una métrica si da mejor en las 10 semillas, y cambia el veredicto
si el intervalo de 2b − 1 en la pAUC excluye el cero en una partición y no en
la otra.
<!-- F: PLAN.md, Fase 6, «El efecto de la partición: especificación y regla de lectura»; EP > esquema y n(esquema.semillas) -->

No se cumple ninguna de las dos. Partir por filas mueve la pAUC en +0,0005 con
la logística y en +0,0002 con el boosting, y da mejor en 6 y en 5 de las 10
semillas.
<!-- F: EP > filas_menos_paciente.nivel_1_regresion_logistica.pauc y filas_menos_paciente.nivel_2b_gradient_boosting_balanceado.pauc (diferencia_de_medias y semillas_filas_mejor) -->
En el AUC y el NNT80% SE de la logística da mejor en 9 de 10, no en las 10
que pedía la regla; con el boosting, en 5 y en 7.
<!-- F: EP > filas_menos_paciente.nivel_1_regresion_logistica.auc, .nnt80, filas_menos_paciente.nivel_2b_gradient_boosting_balanceado.auc y .nnt80 (semillas_filas_mejor) -->
El intervalo de 2b − 1 en la pAUC contiene el cero en las dos particiones:
[−0,0145; 0,0245] por paciente y [−0,0134; 0,0227] por filas.
<!-- F: EP > particiones.paciente.comparacion_2b_menos_1.pauc.intervalo_t_95_nadeau_bengio y particiones.filas.comparacion_2b_menos_1.pauc.intervalo_t_95_nadeau_bengio -->

La sensibilidad top-15 sí sube con filas, pero queda fuera de la regla: con
esa partición cada paciente tiene en validación solo una parte de sus
lesiones, y el top-15 no mide lo mismo.
<!-- F: EP > filas_menos_paciente.*.setop15; EP > nota; PLAN.md, Fase 6, regla (a) -->

*Interpretación, no medición:* con estos datos y estos dos modelos, que el
98,92% de los pacientes quede a los dos lados no se traduce en una métrica
inflada. Lo medido vale para la logística y el boosting balanceados; no se
probó con el contexto de paciente ni con M3 limpio.
<!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga; EP > esquema.niveles -->

### La métrica principal no agota lo que pidió el cliente

Añadir contexto de paciente (M2 − M1) no mueve la pAUC de forma
distinguible: +0,0065, [−0,0147; 0,0276] (28 de 50; 7 de 10). Sí mueve las
dos métricas de triaje:
<!-- F: F21 > C.pauc (media, IC, nuevo_mejor_en_folds, nuevo_mejor_en_semillas) -->

- sensibilidad top-15: +0,0842, [0,021; 0,1473] (46 de 50; 10 de 10);
- NNT80% SE: −30,55 lesiones por cada maligna, [−60,89; −0,20] (42 de 50;
  10 de 10).
<!-- F: F21 > C.setop15 y C.nnt80 (media, IC, nuevo_mejor_en_folds, nuevo_mejor_en_semillas) -->

Quien solo lea la pAUC concluye que el contexto de paciente no aporta; la
sensibilidad top-15, que el cliente premió aparte, y el NNT80% SE dicen lo
contrario. Son cuatro métricas sobre una misma comparación, y el intervalo del
NNT queda al límite del cero.
<!-- F: CLAUDE.md, hallazgo 4; «Método», «Qué se mide», líneas 31–33 -->
*Interpretación, no medición:* las variables relativas al paciente ordenan
las lesiones dentro de cada paciente, que es lo que mide la sensibilidad
top-15, mientras que la pAUC ordena todas las lesiones juntas.
<!-- F: CLAUDE.md, hallazgo 4, «Interpretación, no medición» -->

### Añadida al modelo con contexto de paciente, la imagen no justifica su costo

Las 384 variables de DINOv2 tal cual (M4 − M2) no mejoran el modelo con
contexto de paciente:
<!-- F: outputs/extraccion-imagen.json > caracteristica -->

- pAUC: −0,0065, [−0,0263; 0,0133] (19 de 50; 2 de 10);
- sensibilidad top-15: −0,0332, [−0,085; 0,0185] (9 de 50; 0 de 10);
- NNT80% SE: +11,24, [−19,90; 42,37].
<!-- F: F42 > C.pauc, C.setop15 y C.nnt80 -->

Ningún intervalo excluye el cero, y la estimación puntual es peor en las
cuatro métricas.
<!-- F: F42 > C.*.media y .IC (auc: −0,0085) -->
Por el criterio fijado antes de medir, la imagen, así incorporada, no
justifica su costo.
<!-- F: PLAN.md, Fase 4, «Contingencia» -->
*Interpretación, no medición:* 384 variables adicionales frente a 317
lesiones malignas probablemente diluyen la señal.
<!-- F: CLAUDE.md, hallazgo 5; outputs/eda-diagnostico.json > desbalance_target.conteos.1 -->

La variante secundaria, que resume la imagen en una puntuación apilada
(M4b − M2), tampoco cambia la conclusión:
<!-- F: PLAN.md, Fase 4, «Variante secundaria M4b» -->

- pAUC: +0,0056, [−0,0091; 0,0202] (36 de 50; 8 de 10);
- sensibilidad top-15: −0,0062, [−0,0444; 0,032] (22 de 50; 3 de 10);
- NNT80% SE: −3,87, [−25,10; 17,35].
<!-- F: F4b > C.pauc, C.setop15 y C.nnt80 -->

*Patrón, no efecto establecido:* la forma de incorporar la imagen invierte la
dirección de la pAUC. Como variables sueltas, M4 queda por encima de M2 en 2
de 10 semillas; como puntuación apilada, M4b, en 8 de 10.
<!-- F: F42 > C.pauc.nuevo_mejor_en_semillas y .de_semillas; F4b > C.pauc.nuevo_mejor_en_semillas y .de_semillas; CLAUDE.md, hallazgo 6 -->

### La imagen sola, sin el sistema de fotografía corporal total

Las mediciones de las que dependen M1, M2 y M3 limpio las calcula el software
de la fotografía corporal total; sin ese sistema, esos modelos no se pueden
aplicar tal cual.
<!-- F: «Datos y validación», «Los datos»; outputs/modelado-baseline.json > features_usadas (las variables de M1: F21 > modelos.M1); F21 > variables_de_contexto (las que añade M2); F32 > m3.variables (M3 limpio las conserva: F3L > modelos.M3limpio.descripcion); referencias/kurtansky-2025-triaje-automatizado-tbp.md, líneas 268 y 299 -->
Los organizadores del reto describen ese sistema como *"less accessible and
more expensive than standard clinical and dermoscopic imaging methods"*.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 292, cita literal -->
M2 y M3 limpio, además, comparan cada lesión con las demás del mismo
paciente. Del modelo ganador, que hace lo mismo, los organizadores advierten
que por eso *"cannot be directly applied to analyze single lesions at a
time"*.
<!-- F: «Método», «Qué se compara» (M2 y M3); F32 > m3.variables.entran.z_score_dentro_del_paciente y .conteos_y_sumas_por_paciente; .claude/skills/modelado-baseline/scripts/ganador_m3.py, variables_m3_en_pliegue (M3 limpio); referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 268, cita literal -->

Para ese escenario se midió qué da la imagen sola, con una especificación
fijada antes de correr: una regresión logística balanceada sobre las 384
variables de DINOv2, sola y con edad, sexo y zona del cuerpo, en los mismos
pliegues de M1. Las dos versiones analizan cada lesión por separado.
<!-- F: PLAN.md, Fase 6, «La imagen sola: especificación y regla de lectura (2026-10-04, de la persona)»; IS > esquema y modelos; .claude/skills/modelado-baseline/scripts/imagen_sola.py, puntuar_fold (ninguna variable de contexto de paciente) -->

La imagen sola distingue lesiones malignas muy por encima del azar: su pAUC
es de 0,0796, frente a 0,02 del azar, y su AUC, de 0,8213. Pero queda por
debajo de M1 en las cuatro métricas, y las cuatro diferencias están
establecidas:
<!-- F: IS > metricas.Imagen.pauc.media_global y metricas.Imagen.auc.media_global; IS > metricas.Imagen.pauc.por_semilla_y_fold (los 50 pliegues por encima del azar); outputs/modelado-baseline.json > escala_de_referencia_pauc.azar; «Método», «Cómo se compara» (el criterio) -->

- pAUC: −0,0579, [−0,084; −0,0319] (1 de 50; 0 de 10);
- AUC: −0,0997, [−0,1383; −0,061] (0 de 50; 0 de 10);
- sensibilidad top-15: −0,2364, [−0,323; −0,1498] (0 de 50; 0 de 10);
- NNT80% SE: +309,97 lesiones por cada maligna, [177,89; 442,06] (0 de 50;
  0 de 10).
<!-- F: IS > C.imagen_menos_m1.pauc, .auc, .setop15 y .nnt80 (media, IC, nuevo_mejor_en_folds, nuevo_mejor_en_semillas) -->

Para capturar el 80% de las malignas, la imagen sola marca 426,14 lesiones por
cada una, frente a 116,16 de M1.
<!-- F: IS > metricas.Imagen.nnt80.media_global y metricas.M1.nnt80.media_global; «Método», «Qué se mide» (la definición del NNT80% SE) -->
Esa distancia no mide solo lo que aportan las mediciones del sistema: M1
también usa la edad y el sexo, y la imagen con los datos básicos no se comparó
con M1.
<!-- F: outputs/modelado-baseline.json > features_usadas (age_approx y sex); referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299 (la edad y el sexo, entre los datos básicos); PLAN.md, Fase 6, especificación de la imagen sola (las dos comparaciones fijadas) -->
El tiempo de inferencia de la imagen sola no se midió.
<!-- F: IS (sin tiempos); outputs/tiempo-inferencia.json > tiempos (M1, M2, M3 limpio, M4 y M4b) -->

Añadir edad, sexo y zona del cuerpo mejora el AUC de forma distinguible; en
las otras tres métricas la mejora no se da por establecida:
<!-- F: «Método», «Cómo se compara» (el criterio) -->

- AUC: +0,0082, [0,0016; 0,0149] (46 de 50; 10 de 10);
- pAUC: +0,0045, [0,0; 0,0089] (45 de 50; 10 de 10), un intervalo que, con la
  precisión guardada, no excluye el cero;
- sensibilidad top-15: +0,0026, [−0,034; 0,0393] (26 de 50; 4 de 10);
- NNT80% SE: −35,57 lesiones por cada maligna, [−86,90; 15,75] (37 de 50;
  10 de 10).
<!-- F: IS > C.imagen_basicos_menos_imagen.auc, .pauc, .setop15 y .nnt80 (media, IC, nuevo_mejor_en_folds, nuevo_mejor_en_semillas); PLAN.md, Fase 6, «La imagen sola: dos decisiones sobre el resultado», 1 -->

Sobre la zona del cuerpo, las fuentes no coinciden. La tabla de variables del
artículo del conjunto de datos la marca como una métrica del software del
sistema; el artículo de los organizadores la cuenta entre los datos básicos,
que *"are not directly attained from images"*.
<!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, líneas 194 y 226 (el asterisco: «Canfield Scientific, Inc. Lesion Visualizer metric»); referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299, cita literal -->

Después se entrenó una red de imagen sobre los recortes, EfficientNet-B0, en
cada pliegue.
<!-- F: PLAN.md, Fase 4c, «La red» y «Cómo se entrena, fijado antes de correr y sin ajuste»; referencias/efficientnet-b0-preentrenamiento.md, líneas 77–108 (el criterio de la Fase 2, comprobado antes de descargar los pesos) -->
Su pAUC media es de 0,1083, frente a 0,0796 de la imagen sola con DINOv2, y
queda por encima en 44 de 50 pliegues y en las 10 semillas.
<!-- F: outputs/fase4c-red-sola-vs-imagen.json > metricas.Red.pauc.media_global, metricas.Imagen.pauc.media_global y comparaciones_nuevo_menos_base.pauc.nuevo_mejor_en_folds, .de_folds y .nuevo_mejor_en_semillas; «Imagen» es la de IS, a 4 decimales -->
Con la corrección por haber hecho dos preguntas, el intervalo de la
diferencia, +0,0287, va de −0,0037 a 0,0611, así que la regla fijada antes no
la da por establecida.
<!-- F: outputs/fase4c-red-sola-vs-imagen.json > comparaciones_nuevo_menos_base.pauc.media y .intervalo_bonferroni_nadeau_bengio (confianza 1 − 0,05/2, con la corrección de Nadeau y Bengio); PLAN.md, Fase 4c, «Regla, fijada antes de correr» y «Resultado de la regla (2026-10-23)» -->
En el AUC estándar, que no decide, sí queda entero por encima de cero:
+0,0529, [0,0018; 0,1039]; en la sensibilidad top-15 y el NNT80% SE, el
intervalo contiene el cero.
<!-- F: outputs/fase4c-red-sola-vs-imagen.json > comparaciones_nuevo_menos_base.auc.media y .auc.intervalo_bonferroni_nadeau_bengio; .setop15.intervalo_bonferroni_nadeau_bengio y .nnt80.intervalo_bonferroni_nadeau_bengio; PLAN.md, Fase 4c, «Regla, fijada antes de correr» (las secundarias no deciden) -->

*Interpretación, no medición:* sin el sistema de fotografía corporal total, la
imagen sí sirve para ordenar lesiones por sospecha, aunque con el extractor
congelado, DINOv2, queda lejos de M1. Edad, sexo y zona del
cuerpo son datos que una persona puede informar sin aparatos, aunque en estos
datos la zona del cuerpo pudo venir del software del sistema. El ganador ajustó sus
propias redes de imagen, y su variante con solo los recortes llega a un AUC de
0,922, pero en otros datos y con otra evaluación, así que las cifras no se
comparan. Y todo esto se midió sobre los recortes del sistema de fotografía
corporal total, no sobre fotos de teléfono.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, Tabla 3 (línea 216) y línea 272; PLAN.md, Fase 4, «Orden de magnitud, no comparación»; «Estado del arte» («el ganador ajustó sus propias redes»); IS > datos; referencias/kurtansky-2024-slice3d-descriptor.md, líneas 194 y 226; referencias/kurtansky-2025-triaje-automatizado-tbp.md, línea 299 -->

La red de la Fase 4e, la EfficientNet-B0 con la receta del décimo puesto y el
ajuste fino que se describen en «El modelo recomendado», queda sola por encima
de la red de la Fase 4c: 0,1376 frente a 0,1086, +0,029, [0,002; 0,056] (23 de
25; 5 de 5). En el AUC, +0,044, [0,0062; 0,0818], y en la sensibilidad top-15,
+0,1232, [0,043; 0,2035], el intervalo también excluye el cero; en el NNT80%
SE, no.
<!-- F: outputs/fase4e-red-vs-red4c.json > metricas.Red4eAjustada.pauc.media_global, metricas.Red.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, C.auc.media, .intervalo_t_95_nadeau_bengio, C.setop15.media, .intervalo_t_95_nadeau_bengio, C.nnt80.intervalo_t_95_nadeau_bengio y n(semillas_corridas); «Resultados», «El modelo recomendado» -->

Aun así, la regla no la da por establecida. Su valor p, 0,0365, no llega al
umbral de Holm para la primera de dos preguntas, 0,025; con una sola pregunta,
el umbral habría sido 0,05. Lo que decide es la corrección por multiplicidad,
fijada antes de correr. Es el mismo tipo de hallazgo que recoge «Qué suma este
proyecto»: una decisión de método, aquí cuántas preguntas se corrigen juntas,
cambia el veredicto.
<!-- F: outputs/fase4e-red-vs-red4c.json > C.pauc.valor_p_nadeau_bengio; outputs/fase4e-holm.json > preguntas[0].umbral_holm y alfa; PLAN.md, Fase 4e, «Regla, fijada antes de correr»; «Estado del arte», «Qué suma este proyecto» -->

Después se comparó esa red con «Imagen + básicos», el punto de partida que
este informe daba para el escenario sin fotografía corporal total, en los
mismos 25 pliegues de la confirmación. La pregunta se eligió después de ver la
Fase 4e, y se declara así: la diferencia de medias ya se podía calcular con lo
guardado, y el valor p no se había calculado.
<!-- F: outputs/fase4f-red4e-vs-imagen-basicos.json > C.pauc.n_diferencias; PLAN.md, Fase 4f, «Elegida después de ver la 4e, y se declara»; «Recomendación», «Qué se recomienda» -->

Con la regla de una sola pregunta, la red supera a «Imagen + básicos»: 0,1376
frente a 0,0884, +0,0493, [0,0218; 0,0767] (25 de 25; 5 de 5), con un valor p
de 0,0011. Las tres métricas secundarias van en la misma dirección, con
intervalos que excluyen el cero: AUC +0,0829, [0,0465; 0,1193]; sensibilidad
top-15 +0,1938, [0,1062; 0,2813], y NNT80% SE −212,65, [−337,81; −87,50].
<!-- F: outputs/fase4f-red4e-vs-imagen-basicos.json > metricas.Red4eAjustada.pauc.media_global, metricas.ImagenBasicos.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, .valor_p_nadeau_bengio, C.auc.media, .intervalo_t_95_nadeau_bengio, C.setop15.media, .intervalo_t_95_nadeau_bengio, C.nnt80.media, .intervalo_t_95_nadeau_bengio y n(semillas_corridas); PLAN.md, Fase 4f, «Regla, fijada antes de correr» -->

Por la regla, la recomendación para ese escenario pasó a la red, que además
usa menos datos de entrada: solo la imagen, sin edad, sexo ni zona del
cuerpo. Se midió sobre los recortes de SLICE-3D, no sobre fotos de teléfono.
<!-- F: PLAN.md, Fase 4f, «Resultado de la regla (2026-11-02)»; «Qué no se puede afirmar», «Cuánto rinde un modelo con fotos de teléfono» -->

### El modelo recomendado

La parte tabular reproducida del ganador (M3 − M2) supera a M2 en la métrica
principal: +0,0185, [0,0007; 0,0364] (45 de 50; 10 de 10). En las métricas de
triaje no se distingue: sensibilidad top-15 +0,0181, [−0,0365; 0,0726], y
NNT80% SE −12,62, [−49,29; 24,05].
<!-- F: F32 > C.pauc, C.setop15 y C.nnt80 -->
Por la nota de lectura fijada antes de correr, esa ventaja no se puede
separar de los dos sesgos conocidos a favor de M3.
<!-- F: PLAN.md, Fase 4, «Nota de lectura, de la persona, fijada antes de correr» -->
Como control de que la reproducción está bien montada, no como comparación:
M3 obtiene una pAUC media de 0,1625 y una sensibilidad top-15 de 0,7245, y la
variante del ganador sin recortes de imagen obtuvo 0,164 y 0,695 en la
evaluación privada del reto, con otros datos, otras particiones y la
etiqueta del hospital entre sus variables.
<!-- F: F32 > metricas.M3.pauc.media_global y .setop15.media_global; referencias/kurtansky-2025-triaje-automatizado-tbp.md, Tabla 3, líneas 206 y 209 (Meta-basic, Meta-WB360 y Patient context); PLAN.md, Fase 4, «Orden de magnitud, no comparación» -->

Sin esos dos sesgos (M3 limpio − M2), la ventaja se mantiene: +0,0181,
[0,0021; 0,0341] (43 de 50; 10 de 10), y en AUC estándar, +0,021,
[0,0043; 0,0376]. En las métricas de triaje sigue sin
distinguirse: sensibilidad top-15 +0,0227, [−0,0291; 0,0746], y NNT80% SE
−20,06, [−49,74; 9,61].
<!-- F: F3L > C.pauc, C.auc, C.setop15 y C.nnt80 -->
El intervalo de la pAUC queda entero por encima de cero, así que, por la
regla fijada antes de correr, el modelo recomendado es M3 limpio.
<!-- F: PLAN.md, Fase 4, «Regla de recomendación» y «Modelo recomendado: decisión de la persona, 2026-09-26» -->
Quitar los sesgos casi no movió la diferencia media: +0,0185 con ellos,
+0,0181 sin ellos. Esa comparación es descriptiva, entre dos corridas, sin
intervalo propio y sin fijar antes.
<!-- F: F32 > C.pauc.media; F3L > C.pauc.media; CLAUDE.md, hallazgo 8 -->

Antes de abrir el conjunto reservado se probaron tres combinaciones contra M3
limpio, fijadas antes de correr: mezclarlo con M2, añadirle las dos variables
de imagen de M4b y mezclarlo con un segundo boosting sobre sus mismas
variables. Como fueron tres intentos, el intervalo se corrige además por
multiplicidad, con la confianza de Bonferroni. Ninguna lo supera en la pAUC:
−0,0025, [−0,0129; 0,008]; +0,0011, [−0,012; 0,0142], y −0,0009,
[−0,012; 0,0101]. M3 limpio sigue siendo el modelo recomendado.
<!-- F: outputs/fase4b-c1-vs-m3limpio.json, outputs/fase4b-c2-vs-m3limpio.json y outputs/fase4b-c3-vs-m3limpio.json > C.pauc.media y C.pauc.intervalo_bonferroni_nadeau_bengio (confianza 1 − 0,05/3, con la corrección de Nadeau y Bengio); PLAN.md, Fase 4b, «Qué se compara», «Regla, fijada antes de correr» y «Resultado de la regla (2026-10-22)» -->
Las combinaciones se eligieron conociendo los resultados de la Fase 4, y la
corrección cubre solo esos tres intentos.
<!-- F: PLAN.md, Fase 4b, «Levanta la regla "Solo esta corrida" de la Fase 4» -->

Después se probó la red de imagen entrenada apilada sobre M3 limpio, con su
puntuación y su razón a la media del paciente.
<!-- F: PLAN.md, Fase 4c, «Pregunta 2» (C4: la puntuación de la red y esa puntuación dividida por su media dentro del paciente, como en M4b y C2) -->
Su pAUC media es de 0,1687, frente a 0,1621 de M3 limpio, y queda por encima
en 39 de 50 pliegues y en las 10 semillas.
<!-- F: outputs/fase4c-c4-vs-m3limpio.json > metricas.C4.pauc.media_global, metricas.M3limpio.pauc.media_global y comparaciones_nuevo_menos_base.pauc.nuevo_mejor_en_folds, .de_folds y .nuevo_mejor_en_semillas -->
Con la corrección de Bonferroni para dos preguntas, el intervalo de la
diferencia, +0,0067, va de −0,003 a 0,0164: la regla no la da por
establecida, y M3 limpio sigue siendo el modelo recomendado.
<!-- F: outputs/fase4c-c4-vs-m3limpio.json > comparaciones_nuevo_menos_base.pauc.media y .intervalo_bonferroni_nadeau_bengio (confianza 1 − 0,05/2, con la corrección de Nadeau y Bengio); PLAN.md, Fase 4c, «Regla, fijada antes de correr» y «Resultado de la regla (2026-10-23)» -->
Las puntuaciones se apilaron con los mismos pliegues, un atajo menos estricto
que la validación interna de M4b. En la semilla 0, la versión estricta dio más
pAUC que el atajo en los cinco pliegues, de +0,0012 a +0,0063.
<!-- F: PLAN.md, Fase 4c, «El atajo, declarado» y «Control del atajo, descriptivo»; outputs/fase4c-control-atajo.json > diferencia_de_pauc_interna_menos_atajo.por_pliegue, .minima y .maxima (la versión estricta: C4 con la validación interna de M4b en las filas de entrenamiento) -->
Las dos preguntas se eligieron conociendo los resultados de las fases 4 y 4b,
y la corrección cubre solo esas dos.
<!-- F: PLAN.md, Fase 4c, «Segunda ronda, declarada» -->

La retroalimentación del avance pidió acercarse al ganador con el equipo
propio, antes de alquilar cómputo. Se abrieron dos rondas más, las fases 4d y
4e, cada una con sus preguntas y su regla fijadas antes de correr, y con la
corrección de Holm por varias preguntas.
<!-- F: PLAN.md, Fase 4d, «Decisión de la persona (2026-10-30)» y «Regla, fijada antes de correr»; PLAN.md, Fase 4e, «Regla, fijada antes de correr» -->

La Fase 4d hizo tres preguntas. La primera, C5, añade a C4 las variables que
el código del ganador construye sobre la puntuación de imagen, sin la etiqueta
del hospital: la puntuación estandarizada por zona del cuerpo y edad, y las
estandarizadas por conglomerado, con un ruido en el apilado que no está en su
código. Su pAUC media es de 0,1659, frente a 0,1621 de M3 limpio: +0,0039,
[−0,005; 0,0127] (37 de 50; 10 de 10), con un valor p de 0,3859.
<!-- F: PLAN.md, Fase 4d, «Pregunta 1 · C5 frente a M3 limpio»; outputs/fase4d-c5-vs-m3limpio.json > metricas.C5.pauc.media_global, metricas.M3limpio.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, .valor_p_nadeau_bengio y n(semillas_corridas) -->

La segunda entrenó la red durante más épocas, con un conjunto distinto de
negativos en cada una, dos ideas que vienen del décimo puesto de la
competición. Salió por debajo de la red de la Fase 4c: 0,0923 frente a 0,1079,
−0,0156, [−0,0318; 0,0005] (5 de 25; 0 de 5), con un valor p de 0,0574. Cambió
dos cosas a la vez, así que el resultado no se atribuye a ninguna de las dos
por separado.
<!-- F: outputs/fase4d-red-mejorada-vs-red.json > metricas.RedMejorada.pauc.media_global, metricas.Red.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, .valor_p_nadeau_bengio y n(semillas_corridas); PLAN.md, Fase 4d, «Pregunta 2 · La red mejorada frente a la red de la Fase 4c» -->

La tercera, C6, que es C5 con esa red, queda en 0,165 frente a 0,1601 de M3
limpio en las mismas semillas: +0,005, [−0,0031; 0,0131] (19 de 25; 5 de 5),
con un valor p de 0,2172.
<!-- F: outputs/fase4d-c6-vs-m3limpio.json > metricas.C6.pauc.media_global, metricas.M3limpio.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, .valor_p_nadeau_bengio y n(semillas_corridas); PLAN.md, Fase 4d, «Pregunta 3 · C6 frente a M3 limpio» -->

Holm no aceptó ninguna de las tres preguntas, y M3 limpio siguió siendo el
modelo recomendado.
<!-- F: outputs/fase4d-holm.json > preguntas; PLAN.md, Fase 4d, «Resultado de la regla (2026-10-31)» -->

La Fase 4e cambió de estrategia: en lugar de añadir variables, entrenó mejor
la red. Siguió la receta de imagen del décimo puesto, que usa la misma red y la
misma resolución que la de la Fase 4c: aumentos fuertes de las imágenes, una
tasa de aprendizaje que sube y luego baja, y los negativos repartidos en un
conjunto distinto por época. En los negativos sigue el README del autor, no su
código, que hace otra cosa. Después, si la exploración lo justificaba, la red
se ajustaba con una pérdida de pAUC unilateral sobre las clases invertidas,
como las invierte el script oficial de la métrica.
<!-- F: PLAN.md, Fase 4e, «Por qué esta receta», «Qué se entrena: la red de la 4e», «Exploración, semilla 0 (descriptiva)» y «Los ajustes del paso 2 (2026-11-01), fijados antes de leer la exploración»; referencias/tomo20180402-2024-isic2024-10mo-puesto.md, líneas 73, 75, 84, 174 y 237–247; referencias/isic-primary-metric-pauc.py.md, líneas 48 y 49 -->

Una exploración en la semilla 0, que solo decidía si se gastaba la
confirmación y con qué red, puso la red nueva por encima de la de la Fase 4c en
5 de 5 pliegues, y la red ajustada por encima de la sin ajustar en 4 de 5, así
que la confirmación usó la red ajustada.
<!-- F: outputs/fase4e-exploracion.json > paso_1.nuevo_mejor_en_pliegues, paso_1.de_pliegues, paso_2.nuevo_mejor_en_pliegues, paso_2.de_pliegues y paso_2.llega_al_umbral; PLAN.md, Fase 4e, «Exploración, semilla 0 (descriptiva)» -->

En la confirmación, sobre otras semillas, C7, que es C4 con la red ajustada,
queda en 0,1669 frente a 0,1641 de M3 limpio: +0,0029, [−0,0084; 0,0141] (14
de 25; 4 de 5), con un valor p de 0,6028. Holm no aceptó ninguna de las dos
preguntas de la fase, y M3 limpio siguió siendo el modelo recomendado. La
otra pregunta, la de la red sola, está en «La imagen sola, sin el sistema de
fotografía corporal total».
<!-- F: outputs/fase4e-c7-vs-m3limpio.json > metricas.C7.pauc.media_global, metricas.M3limpio.pauc.media_global, C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .n_diferencias, .nuevo_mejor_en_semillas, .valor_p_nadeau_bengio y n(semillas_corridas); outputs/fase4e-holm.json > preguntas; PLAN.md, Fase 4e, «Resultado de la regla (2026-11-01)» -->

Las cuatro versiones que apilan una red de imagen sobre M3 limpio, de C4 a C7,
quedaron por encima de él en la media, de +0,0029 a +0,0067, y ninguna
diferencia llegó a la regla. Qué dice eso, y qué no, está en «Lo que la prueba
alcanza a ver».
<!-- F: outputs/potencia-nadeau-bengio.json > comparaciones.C7.media_observada y comparaciones.C4.media_observada -->

Cada ronda se eligió conociendo los resultados de las anteriores, y su
corrección cubre solo sus propias preguntas.
<!-- F: PLAN.md, Fase 4d, «Tercera ronda, declarada»; PLAN.md, Fase 4e, «Cuarta ronda, declarada» -->

### Lo que la prueba alcanza a ver

Que ninguna de esas diferencias llegara a la regla no dice si las mejoras
existen. Para saber qué tamaño de mejora alcanza a distinguir esta prueba, se
calculó la potencia de la prueba de Nadeau y Bengio con la variabilidad
observada en las comparaciones contra M3 limpio, de C4 a C7.
<!-- F: PLAN.md, Fase 6, «La potencia de la prueba: especificación (2026-11-04, de la persona)»; outputs/potencia-nadeau-bengio.json > comparaciones.*.s -->

Con esa variabilidad, para dar su resultado a favor con un 80% de
probabilidad, la prueba necesita una mejora real de entre 0,0109 y 0,0159 de
pAUC, según la comparación y el número de semillas; para un 50%, de entre
0,0076 y 0,0111. Las mejoras observadas, de +0,0029 a +0,0067, quedan por
debajo del umbral del 50% en las cuatro comparaciones.
<!-- F: outputs/potencia-nadeau-bengio.json > objetivos, comparaciones.*.delta_80, comparaciones.*.delta_50 y comparaciones.*.media_observada -->

Más semillas casi no ayudan. De 5 a 10 semillas, el umbral del 80% baja de
0,0127 a 0,0120 en C4 y de 0,0159 a 0,0150 en C7. El error estándar que usa la
prueba tiene dos términos: uno baja con el número de diferencias, y el otro,
0,25, corrige la correlación entre diferencias que comparten pacientes de
entrenamiento y no baja con más semillas. Al repetir con semillas nuevas, la
media casi no cambia: su error estándar entre semillas es entre 3,44 y 6,99
veces menor que el que usa la prueba.
<!-- F: outputs/potencia-nadeau-bengio.json > comparaciones.C4.delta_80, comparaciones.C7.delta_80, comparaciones.*.entre_semillas, prueba.error_estandar y prueba.termino_de_correccion; CLAUDE.md, hallazgo 16, «Cómo se calcula» -->

Por eso importa la diferencia entre «no se distingue» y «no mejora». Lo que
se midió es compatible con que no haya mejora, y también con una mejora que
esta prueba no alcanza a ver.
<!-- F: CLAUDE.md, hallazgo 16, «Lectura, no medición» -->

### El conjunto reservado, abierto una sola vez

El conjunto reservado se abrió una sola vez, con todo fijado antes: M3 limpio,
el modelo recomendado, y M2 como referencia, entrenados con todo el desarrollo,
y, como resultado descriptivo, la red de la Fase 4e e «Imagen + básicos». Son
209 pacientes, con 76 lesiones malignas repartidas en 52 de ellos. Los
intervalos salen de un bootstrap por paciente con 2.000 remuestras.
<!-- F: outputs/fase5-reservado.json > datos.evaluacion.pacientes, .malignas, .pacientes_con_malignas y bootstrap.remuestras; PLAN.md, Fase 5, «Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el reservado» -->

M3 limpio da una pAUC de 0,1588, [0,1387; 0,1766], y supera a M2, 0,1387, por
+0,0201, [0,0008; 0,0413]. En el AUC, +0,0219, [0,0009; 0,0459]. En el
desarrollo, la diferencia en la pAUC era +0,0181, [0,0021; 0,0341]: en los dos
lados, el intervalo excluye el cero y el signo es el mismo. En la sensibilidad
top-15 y el NNT80% SE, el intervalo contiene el cero, como en el desarrollo.
Los dos intervalos no miden lo mismo: en el desarrollo, el de la media por
pliegue, con la corrección de Nadeau y Bengio; en el reservado, el de un solo
modelo, con el bootstrap por paciente.
<!-- F: outputs/fase5-reservado.json > metricas.M3limpio.pauc.punto, .intervalo_95, metricas.M2.pauc.punto, diferencia_m3limpio_menos_m2.pauc.punto, .intervalo_95, diferencia_m3limpio_menos_m2.auc.punto, .intervalo_95, diferencia_m3limpio_menos_m2.setop15.intervalo_95 y diferencia_m3limpio_menos_m2.nnt80.intervalo_95; F3L > C.pauc.media e .intervalo_t_95_nadeau_bengio; outputs/fase5-posterior.json > tabla.como_leerla -->
Con pacientes con los que no se entrenó ningún modelo, la ventaja de M3 limpio
sobre M2 se mantiene en la pAUC y el AUC. El reservado no es ajeno del todo: el
diseño de las variables de M2 y de M3 limpio lo fijó el ganador sobre todo el
conjunto de entrenamiento del reto, que incluye a estos pacientes.
<!-- F: PLAN.md, Fase 5, «La apertura, corrida el 2026-11-04, una sola vez» y «Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el reservado»; CLAUDE.md, hallazgos 8 y 17 -->

La ventaja de la red sobre «Imagen + básicos» no se reprodujo. En el
reservado, la red da 0,1307 e «Imagen + básicos», 0,1385; la diferencia es de
−0,0078, [−0,0306; 0,02]. En la sensibilidad top-15 la red queda por encima,
+0,1282, pero el intervalo, [−0,0035; 0,2585], contiene el cero, como los de
las otras tres métricas; en la Fase 4f, los cuatro lo excluían.
<!-- F: outputs/fase5-reservado.json > metricas.Red4e.pauc.punto y metricas.ImagenBasicos.pauc.punto; outputs/fase5-posterior.json > red4e_menos_imagen_basicos.pauc.punto, .intervalo_95, red4e_menos_imagen_basicos.setop15.punto, .intervalo_95 y red4e_menos_imagen_basicos.*.intervalo_95; outputs/fase4f-red4e-vs-imagen-basicos.json > C.*.intervalo_t_95_nadeau_bengio -->
Después de abrir el reservado, y declarado así, se comprobó que las
características de imagen del reservado salen de la misma extracción que las
del desarrollo, y que «Imagen + básicos» es el mismo modelo que en la
validación cruzada, entrenado con todo el desarrollo. Lo que más se movió es
«Imagen + básicos»: en el desarrollo daba 0,0884, en las mismas semillas que la
red, y en el reservado, 0,1385; la red pasó de 0,1376 a 0,1307. Por qué, no
está medido.
<!-- F: outputs/fase5-posterior.json > procedencia, recalculo.por_archivo, imagen_basicos, tabla.modelos.ImagenBasicos.desarrollo[1].pauc, tabla.modelos.ImagenBasicos.reservado.pauc.punto, tabla.modelos.Red4e.desarrollo[0].pauc y tabla.modelos.Red4e.reservado.pauc.punto; PLAN.md, Fase 5, «Análisis posterior a la apertura (2026-11-04)» -->
Por la regla fijada antes, el reservado no cambia ninguna recomendación: la
estimación principal sigue siendo la validación cruzada repetida. Pero la
ventaja de la red sobre «Imagen + básicos» no quedó confirmada con los
pacientes reservados.
<!-- F: PLAN.md, Fase 5, «Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el reservado» -->

### En la prueba de Kaggle

Kaggle sigue aceptando envíos a la competición cerrada, y a cada uno le dio
una puntuación pública y una privada, sin intervalo. Se enviaron cuatro
modelos entrenados con los 1.042 pacientes, cada uno una sola vez: M3 limpio,
la red de la 4e y C7, fijados antes de abrir el reservado, y un cuarto,
«Imagen + básicos», decidido después.
<!-- F: outputs/fase5b-envio-m3limpio.json, outputs/fase5b-envio-red4e.json, outputs/fase5b-envio-c7.json y outputs/fase5b-envio-imagenbasicos.json > envios; outputs/fase5b-entrenamiento.json > datos.pacientes; referencias/kaggle-code-requirements.md, línea 63; PLAN.md, Fase 5b, «Estado» y «Qué se hace (decisión de la persona, 2026-11-04)» -->
Que la puntuación privada salga del mismo subconjunto de la prueba que el
tablero final del reto es lectura nuestra: ninguna fuente versionada lo dice.
<!-- F: referencias/kaggle-code-requirements.md, líneas 48 y 67–70 (la página no habla de los envíos después del cierre, y la captura solo muestra que el panel está abierto) -->

En la puntuación privada, C7 obtiene 0,15856, y el ganador, 0,1726: una
diferencia de −0,01404. M3 limpio obtiene 0,15134, frente a 0,164 de la versión
del ganador sin imágenes, que usa la etiqueta del hospital; la red sola,
0,1159, frente a 0,142 de la versión que solo usa las imágenes. Esas dos
versiones son de la reproducción del ganador que hicieron los organizadores,
sobre el conjunto del tablero privado, con tres decimales.
<!-- F: outputs/fase5b-comparacion.json > comparaciones_con_la_privada.c7_menos_ganador, .m3limpio_menos_sin_imagenes y .red4e_menos_solo_imagenes; referencias/kurtansky-2025-triaje-automatizado-tbp.md, líneas 196, 200, 209, 216 y 315 -->
Al lado, como aritmética descriptiva de dos fuentes distintas, lo que la
imagen le suma a la parte tabular: +0,00722 en la privada, C7 − M3 limpio, y
+0,009 en la tabla de los organizadores, el modelo completo menos la versión
sin imágenes. Las dos fuentes tienen datos y variables distintos, así que no es
una comparación.
<!-- F: outputs/fase5b-comparacion.json > aritmetica_de_dos_fuentes; referencias/kurtansky-2025-triaje-automatizado-tbp.md, líneas 207 y 209 -->

El cuarto envío comparó la red con «Imagen + básicos» en Kaggle. Se decidió
después de ver el reservado, y se declara así. La red obtiene 0,1159 e «Imagen
+ básicos», 0,08935: en la privada, la red vuelve a quedar por encima, como en
el desarrollo y al revés que en el reservado.
<!-- F: outputs/fase5b-comparacion.json > comparaciones_con_la_privada.red4e_menos_imagen_basicos; PLAN.md, Fase 5b, «Qué se hace (decisión de la persona, 2026-11-04)» -->

| Modelo | Desarrollo, semillas 5 a 9 | Reservado | Kaggle, privada |
|---|---|---|---|
| C7 | 0,1669 | no se evaluó | 0,15856 |
| M3 limpio | 0,1641 | 0,1588 | 0,15134 |
| Red de la 4e | 0,1376 | 0,1307 | 0,1159 |
| «Imagen + básicos» | 0,0884 | 0,1385 | 0,08935 |
<!-- F: outputs/fase5b-comparacion.json > tabla_tres_evaluaciones -->
En el desarrollo y en Kaggle, los cuatro modelos quedan en el mismo orden; en
el reservado, «Imagen + básicos» queda por encima de la red. Son conjuntos y
estimaciones distintos: la media por pliegue en el desarrollo, un solo modelo
en el reservado y una sola puntuación en Kaggle, sin intervalo.
<!-- F: outputs/fase5b-comparacion.json > tabla_tres_evaluaciones y como_leerla -->

Para descomponer la distancia al ganador se hicieron cuatro envíos más, en un
diseño de dos por dos fijado antes de entrenarlos: con imagen o sin ella, y con
la etiqueta del hospital o sin ella. En los cuatro, la parte tabular es la
media de 45 CatBoost, uno por pliegue de 5 pliegues con 9 semillas, como los
que entrena el código del ganador; cómo combina él sus predicciones en la
prueba no está en su notebook. El diseño se decidió después de ver los primeros
envíos, y con él el proyecto cerró Kaggle: no se envía nada más.
<!-- F: outputs/fase5c-entrenamiento.json > n(modelos.M3limpioProm.modelos), pliegues.n_splits y n(pliegues.semillas); PLAN.md, Fase 5c, «Estado», «Qué se hace (decisión de la persona, 2026-11-05)» y «Cierre (2026-11-05)» -->

Promediar sube la puntuación privada en +0,00443 sin imagen y en +0,00507 con
imagen, con el mismo signo en la pública; cada uno de los 45 modelos se
entrena, además, con cuatro quintos de los pacientes. El hospital suma
+0,00048 sin imagen y +0,00237 con imagen, y este último cambia de signo en la
pública. C7 promediado obtiene 0,16363, y con el hospital, 0,166.
<!-- F: outputs/fase5c-efectos.json > efectos.promediar_sin_imagen, efectos.promediar_con_imagen, efectos.hospital_sin_imagen, efectos.hospital_con_imagen, kaggle.C7Prom.privada y kaggle.C7PromHosp.privada; outputs/fase5c-entrenamiento.json > n(modelos.M3limpioProm.modelos); PLAN.md, Fase 5c, «Salvedades» -->
Como aritmética descriptiva, de la diferencia de C7 con el ganador, −0,01404,
promediar cubre +0,00507, el 36,1%; el hospital, +0,00237, el 16,9%, y quedan
−0,0066, el 47%. El reparto depende del orden: C7 con el hospital y sin
promediar no se envió.
<!-- F: outputs/fase5c-efectos.json > descomposicion_de_la_distancia_al_ganador -->

*Lectura, no medición:* excluir la etiqueta del hospital, por la razón de uso
de «La auditoría de columnas», cuesta en el tablero esas milésimas, y la mayor
de las dos cambia de signo en la pública.
<!-- F: outputs/fase5c-efectos.json > efectos.hospital_sin_imagen y efectos.hospital_con_imagen; «Datos y validación», «La auditoría de columnas» -->
De las dos mejoras de la descomposición, promediar es la única que no usa
datos que el proyecto excluyó, y casi la mitad de la distancia no la cubre
ninguna de las dos. Ninguno de estos envíos cambia una recomendación.
<!-- F: outputs/fase5c-efectos.json > descomposicion_de_la_distancia_al_ganador; outputs/auditoria-de-fugas.json > columnas_procedencia; PLAN.md, Fase 5c, «Qué se hace (decisión de la persona, 2026-11-05)» y «Cierre (2026-11-05)» -->

### El costo de inferencia

La mediana del tiempo de inferencia, en segundos por cada 1.000 lesiones, es
0,0021 para M1, 0,0209 para M2, 0,0435 para M3 limpio, 14,5156 para M4 y
14,6321 para M4b.
<!-- F: outputs/tiempo-inferencia.json > tiempos.*.mediana_segundos_por_1000_lesiones -->
M3 limpio cuesta más que M2, pero los dos quedan por debajo de una décima de
segundo por cada 1.000 lesiones. Lo caro, con diferencia, es la imagen, y ni
M4 ni M4b mejoraron a M2 en la métrica principal de forma distinguible.
<!-- F: outputs/tiempo-inferencia.json > tiempos; CLAUDE.md, hallazgo 9 -->

### La pregunta del cliente, entera

| Modelo | pAUC | Sensibilidad top-15 | NNT80% SE | Segundos por 1.000 lesiones |
|---|---|---|---|---|
| M1 | 0,1375 | 0,6223 | 116,16 | 0,0021 |
| M2 | 0,1440 | 0,7065 | 85,62 | 0,0209 |
| M3 limpio | 0,1621 | 0,7292 | 65,55 | 0,0435 |
| M4 | 0,1375 | 0,6732 | 96,85 | 14,5156 |
| M4b | 0,1496 | 0,7003 | 81,74 | 14,6321 |

<!-- F: F21 > metricas.M1 y metricas.M2 (las medias de los 50 pliegues, *.media_global); F3L > metricas.M3limpio; F42 > metricas.M4; F4b > metricas.M4b; M2 es igual en los cuatro archivos (reproduccion_del_base.reproduce_fold_a_fold); outputs/tiempo-inferencia.json > tiempos.*.mediana_segundos_por_1000_lesiones; M3 no está: no es candidato y su camino de predicción no se cronometró (PLAN.md, Fase 4, «Tiempo de inferencia») -->

La tabla responde la pregunta con sus tres ejes —la métrica principal, la
sensibilidad por paciente y el costo— y añade el NNT80% SE, la segunda métrica
de triaje. Son medias y medianas; las diferencias, con sus intervalos, están
arriba. M2 se distingue de M1 en las dos métricas de triaje, no en la pAUC.
Frente a M2, de los otros tres solo M3 limpio se distingue, y solo en la pAUC
y en el AUC estándar; en las métricas de triaje no se distingue ninguno de los
tres.
<!-- F: PLAN.md, Fase 6 («La tabla final responde la pregunta del cliente entera, con sus tres ejes»); F21, F42, F4b y F3L > C.*.IC; «Método», «Qué se mide», líneas 55–59 (NNT80% SE); informe/anteproyecto.md, línea 495 (la top-15 y el NNT como las dos de triaje) -->

## Recomendación

<!-- Sección de informe/borrador-v2.md. Mismas convenciones que las
     anteriores; las abreviaturas F21, F42, F4b, F3L, EP, MEC e IS son las de «Resultados». -->

### Qué se recomienda

**Al cliente se le recomienda M3 limpio:** la parte tabular reproducida de la
solución ganadora, sin los dos sesgos conocidos a su favor.
<!-- F: «Resultados», «El modelo recomendado»; PLAN.md, Fase 4, «Modelo recomendado: decisión de la persona, 2026-09-26» -->
Se eligió con una regla fijada antes de correr la comparación: el intervalo
corregido de su diferencia con M2 en la pAUC queda entero por encima de cero.
<!-- F: PLAN.md, Fase 4, «Regla de recomendación»; F3L > C.pauc.IC -->
Ninguna de las versiones que se le compararon después de elegirlo, de la Fase
4b a la 4e, llegó a su regla, y en el conjunto reservado, abierto una sola vez,
la ventaja sobre M2 se mantiene en la pAUC y en el AUC.
<!-- F: «Resultados», «El conjunto reservado, abierto una sola vez»; outputs/fase5-reservado.json > diferencia_m3limpio_menos_m2.pauc.intervalo_95 y diferencia_m3limpio_menos_m2.auc.intervalo_95; PLAN.md, Fase 4b, «Resultado de la regla (2026-10-22)»; PLAN.md, Fase 4c, «Resultado de la regla (2026-10-23)»; PLAN.md, Fase 4d, «Resultado de la regla (2026-10-31)»; PLAN.md, Fase 4e, «Resultado de la regla (2026-11-01)» -->

**Donde se toma la fotografía corporal total, no se recomienda, por ahora,
añadir la imagen.** Añadida al modelo con contexto de paciente como variables
de DINOv2, sueltas en M4 o apiladas en M4b, no mejoró ninguna métrica de forma
distinguible, y al predecir esos dos modelos cuestan 14,5156 y 14,6321
segundos por cada 1.000 lesiones, frente a 0,0435 de M3 limpio.
<!-- F: F42 y F4b > C.*.IC; outputs/tiempo-inferencia.json > tiempos.M4, tiempos.M4b y tiempos.M3limpio (mediana_segundos_por_1000_lesiones) -->
Eso no dice que la imagen no sirva para detectar cáncer: en la ablación de los
organizadores, la variante del modelo ganador que solo usa los recortes llega
a un AUC de 0,922, y la presentan como una base sólida para cuando no se pueden
recoger los metadatos, como al usar la cámara de un teléfono.
<!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, Tabla 3 (línea 216) y líneas 272 y 284 -->
Con una red entrenada sobre los recortes y apilada sobre M3 limpio, las cuatro
versiones, de C4 a C7, quedaron por encima de él en la media, de +0,0029 a
+0,0067, y ninguna llegó a su regla; las cuatro diferencias quedan por debajo
del tamaño que la prueba distingue con un 50% de probabilidad. En Kaggle, C7
queda por encima de M3 limpio en la puntuación privada, +0,00722, sin
intervalo. El tiempo de inferencia de C7 no se midió con el procedimiento del
proyecto; el notebook de Kaggle, en otro equipo, lo proyectó en 0,39 horas por
cada 500.000 lesiones, frente a 0,04 horas de M3 limpio.
<!-- F: outputs/potencia-nadeau-bengio.json > comparaciones.C7.media_observada, comparaciones.C4.media_observada, comparaciones.*.media_observada, comparaciones.*.delta_50 y objetivos; outputs/fase5b-comparacion.json > aritmetica_de_dos_fuentes.c7_menos_m3limpio_kaggle_privada; outputs/fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.proyeccion.C7.horas_proyectadas, salida_del_notebook.tiempo.proyeccion.M3limpio.horas_proyectadas y salida_del_notebook.tiempo.lesiones_de_prueba_supuestas; «Resultados», «El modelo recomendado» y «Lo que la prueba alcanza a ver»; CLAUDE.md, hallazgo 14 (no se midió con el procedimiento de tiempo-inferencia) -->
*Lectura, no medición:* con lo medido, no se puede decir si apilar la red sobre
M3 limpio lo mejora: la mejora no se distingue, pero tampoco se descarta. Por
eso la recomendación se queda, por ahora, con M3 limpio, sin imagen.
<!-- F: «Resultados», «Lo que la prueba alcanza a ver»; CLAUDE.md, hallazgo 16, «Lectura, no medición» -->

**Donde no hay ese sistema, M3 limpio no se puede aplicar tal cual, y la
imagen es el insumo disponible.** Es el escenario que el artículo del conjunto
de datos pone como objetivo: algoritmos que decidan a partir de *"clinical
photos resembling the resolution of smartphone images"*.
<!-- F: «Resultados», «La imagen sola, sin el sistema de fotografía corporal total»; referencias/kurtansky-2024-slice3d-descriptor.md, línea 109, cita literal -->
Ahí se recomienda la red de la Fase 4e, que usa solo la imagen. Por la regla
de la Fase 4f, fijada antes de correr, supera a «Imagen + básicos», el punto de
partida que daba antes este informe: +0,0493 de pAUC, [0,0218; 0,0767], mejor
en 25 de 25 pliegues.
<!-- F: outputs/fase4f-red4e-vs-imagen-basicos.json > C.pauc.media, .intervalo_t_95_nadeau_bengio, .nuevo_mejor_en_folds, .de_folds y regla.a_favor; PLAN.md, Fase 4f, «Resultado de la regla (2026-11-02)» -->
Esta recomendación tiene tres salvedades. La pregunta se eligió después de ver
la Fase 4e. En el conjunto reservado, la ventaja no se reprodujo: −0,0078,
[−0,0306; 0,02], y por qué «Imagen + básicos» da más en el reservado no está
medido. Y en Kaggle la red vuelve a quedar por encima, 0,1159 frente a 0,08935,
pero es una sola cifra por envío, sin intervalo, y ese envío se decidió después
de ver el reservado. Por la regla fijada antes de abrirlo, el reservado no
cambia la recomendación.
<!-- F: PLAN.md, Fase 4f, «Lo que el resultado no dice»; outputs/fase5-posterior.json > red4e_menos_imagen_basicos.pauc.punto e .intervalo_95; PLAN.md, Fase 5, «Análisis posterior a la apertura (2026-11-04)»; outputs/fase5b-comparacion.json > comparaciones_con_la_privada.red4e_menos_imagen_basicos.modelo y .referencia; PLAN.md, Fase 5b, «Qué se hace (decisión de la persona, 2026-11-04)»; PLAN.md, Fase 5, «Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el reservado» -->
Para usarla con pacientes falta medir cómo rinde con fotos de teléfono y
cuánto cuesta al predecir con el procedimiento del proyecto; el notebook de
Kaggle, en otro equipo, lo proyectó en 0,31 horas por cada 500.000 lesiones. La
red con edad, sexo y zona del cuerpo no se probó.
<!-- F: «Qué no se puede afirmar», «Cuánto rinde un modelo con fotos de teléfono»; outputs/fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.proyeccion.Red4e.horas_proyectadas y salida_del_notebook.tiempo.lesiones_de_prueba_supuestas; PLAN.md, Fase 4f, «Lo que el resultado no dice» y «Lo que esta fase no hace» -->
*Lectura, no medición:* como la red no usa la zona del cuerpo, no le alcanza la
salvedad de «Imagen + básicos», cuya zona del cuerpo pudo venir del software
del sistema.
<!-- F: PLAN.md, Fase 4f, «Lo que el resultado no dice» (la «Lectura nuestra, no medición» que le sigue); CLAUDE.md, hallazgo 10 -->

**Y se recomienda no leer solo la pAUC.** El contexto de paciente no se nota
en ella y sí en las dos métricas de triaje: la sensibilidad top-15 y el NNT80% SE.
<!-- F: F21 > C.pauc.IC, C.setop15.IC y C.nnt80.IC -->

### Qué se puede afirmar

- En el conjunto de desarrollo, con validación cruzada repetida y el
  intervalo corregido, M3 limpio supera a M2 en la pAUC y en el AUC estándar.
  <!-- F: F3L > C.pauc.IC y C.auc.IC -->
- En el conjunto reservado, con pacientes con los que no se entrenó ningún
  modelo, M3 limpio también supera a M2 en la pAUC, +0,0201, [0,0008; 0,0413],
  y en el AUC, +0,0219, [0,0009; 0,0459].
  <!-- F: outputs/fase5-reservado.json > diferencia_m3limpio_menos_m2.pauc.punto, .intervalo_95, diferencia_m3limpio_menos_m2.auc.punto e .intervalo_95 -->
- El contexto de paciente mejora frente a M1 la sensibilidad top-15 y el NNT80%
  SE.
  <!-- F: F21 > C.setop15.IC y C.nnt80.IC -->
- Añadidas al modelo con contexto de paciente, las variables de imagen de
  DINOv2, como variables sueltas o apiladas, no mejoran de forma distinguible
  ninguna de las métricas.
  <!-- F: F42 y F4b > C.*.IC -->
- Sin el sistema de fotografía corporal total, la imagen sola distingue
  lesiones malignas muy por encima del azar, pero con el extractor congelado,
  DINOv2, queda por debajo de M1 en las cuatro métricas.
  <!-- F: «Resultados», «La imagen sola, sin el sistema de fotografía corporal total»; IS > metricas.Imagen.pauc.por_semilla_y_fold; IS > C.imagen_menos_m1.*.IC -->
- En el conjunto de desarrollo, la red de la Fase 4e, que usa solo la imagen,
  supera a «Imagen + básicos» en la pAUC con la regla de una sola pregunta, y
  las tres métricas secundarias van en la misma dirección.
  <!-- F: outputs/fase4f-red4e-vs-imagen-basicos.json > C.pauc.valor_p_nadeau_bengio, regla.a_favor y C.*.intervalo_t_95_nadeau_bengio -->
- Una decisión de método cambia el veredicto sobre la red de la Fase 4e frente
  a la de la 4c. Su valor p, 0,0365, no llega al umbral de Holm para la primera
  de dos preguntas, 0,025; con una sola pregunta, el umbral habría sido 0,05.
  <!-- F: outputs/fase4e-red-vs-red4c.json > C.pauc.valor_p_nadeau_bengio; outputs/fase4e-holm.json > preguntas[0].umbral_holm y alfa -->
- Una partición por filas habría dejado al 98,92% de los pacientes a los dos
  lados de la validación.
  <!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga -->
- En la puntuación privada de Kaggle, ninguno de los ocho envíos llega a la del
  ganador, 0,1726. El más cercano, «C7 promediado + hospital», da 0,166, y el
  más cercano sin la etiqueta del hospital, «C7 promediado», 0,16363. Son cifras
  sueltas, sin intervalo.
  <!-- F: outputs/fase5b-comparacion.json > comparaciones_con_la_privada.c7_menos_ganador.referencia; outputs/fase5c-efectos.json > kaggle.*.privada, kaggle.C7PromHosp.privada y kaggle.C7Prom.privada; outputs/fase5b-envio-red4e.json y outputs/fase5b-envio-imagenbasicos.json > envios.0.privateScore -->

### Qué no se puede afirmar

- **Que M3 limpio sea mejor en las métricas de triaje.** En la sensibilidad top-15
  y en el NNT80% SE no se distingue de M2.
  <!-- F: F3L > C.setop15.IC y C.nnt80.IC -->
- **Cuál de los dos sesgos de M3 pesaba.** M3 limpio cambia tres cosas a la vez.
  <!-- F: PLAN.md, Fase 4, «Lectura, declarada antes de correr» -->
- **Que la red de la Fase 4e supere a «Imagen + básicos» con pacientes
  nuevos.** En el reservado la ventaja no se reprodujo, y Kaggle da una sola
  cifra por envío. Por qué «Imagen + básicos» da más en el reservado que en el
  desarrollo no está medido. Se midió su curva de aprendizaje en el desarrollo,
  pero no la de la red, así que no se sabe si uno de los dos mejora más que el
  otro con más datos.
  <!-- F: outputs/fase5-posterior.json > red4e_menos_imagen_basicos.*.intervalo_95; outputs/fase5b-comparacion.json > como_leerla; PLAN.md, Fase 5, «Análisis posterior a la apertura (2026-11-04)» y «Curva de aprendizaje, solo desarrollo (2026-11-04)»; outputs/curva-aprendizaje.json > imagen_basicos.curva y red4e -->
- **Nada sobre otras redes de imagen.** Solo se probaron las variables de
  DINOv2 sin reentrenarlo y una red pequeña, EfficientNet-B0, entrenada sobre
  los recortes con tres recetas: la de la Fase 4c, con ajustes fijos; la de la
  4d, con más épocas y los negativos en bloques; y la del 10.º puesto, con un
  ajuste fino por la pAUC, en la 4e. Las redes del ganador quedaron fuera.
  <!-- F: «Método», «Qué se compara»; PLAN.md, Fase 4, «Quedan fuera, con su motivo»; .claude/skills/extraccion-imagen/SKILL.md (sin ajuste fino; pasada congelada); PLAN.md, Fase 4c, «La red», «Cómo se entrena, fijado antes de correr y sin ajuste» y «Qué no entra, con su motivo»; PLAN.md, Fase 4d, «Pregunta 2 · La red mejorada frente a la red de la Fase 4c»; PLAN.md, Fase 4e, «Qué se entrena: la red de la 4e» -->
- **Cuánto rinde un modelo con fotos de teléfono.** Todos los modelos de
  imagen, también la red de la Fase 4e, se midieron sobre los recortes
  estandarizados del sistema de fotografía corporal total, y en Kaggle, sobre
  los recortes de la prueba del reto. El artículo del conjunto de datos advierte
  que las fotos que toman los pacientes *"vary greatly in lighting and FOV"*.
  <!-- F: IS > datos; PLAN.md, Fase 4f, «Resultado de la regla (2026-11-02)»; CLAUDE.md, hallazgo 18, «Sobre qué se midió»; referencias/kurtansky-2024-slice3d-descriptor.md, línea 115, cita literal -->
- **Cuánto cuesta predecir con la red de la Fase 4e o con C7 frente a los
  demás modelos.** Sus tiempos no se midieron con el procedimiento de «Cómo se
  mide el tiempo de inferencia», y la eficiencia es uno de los tres ejes de la
  pregunta del cliente. Solo hay la proyección del notebook de Kaggle, en otro
  equipo: 0,31 horas para la red y 0,39 para C7 por cada 500.000 lesiones, que
  no se compara con los tiempos de «El costo de inferencia».
  <!-- F: outputs/fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.proyeccion.Red4e.horas_proyectadas, salida_del_notebook.tiempo.proyeccion.C7.horas_proyectadas y salida_del_notebook.tiempo.lesiones_de_prueba_supuestas; PLAN.md, Fase 4f, «Lo que el resultado no dice»; CLAUDE.md, hallazgo 14; «Método», «Cómo se mide el tiempo de inferencia»; «Resultados», «La pregunta del cliente, entera» -->
- **Que no exista una forma de mejorar a M3 limpio.** Ninguna de las siete
  versiones que se le compararon, de C1 a C7, en las fases 4b a 4e, llegó a su
  regla. Ninguna buscó hiperparámetros: sus ajustes se fijaron antes de correr,
  y la única elección hecha con resultados fue la de la exploración de la 4e,
  que decidió con la semilla 0 usar el ajuste fino. Las cuatro que apilan una
  red de imagen, de C4 a C7, quedaron por encima de él en la media, y la prueba
  no distingue mejoras de ese tamaño: no distinguirlas no es lo mismo que no
  tenerlas.
  <!-- F: PLAN.md, Fase 4b, «Resultado de la regla (2026-10-22)»; PLAN.md, Fase 4c, «Resultado de la regla (2026-10-23)»; PLAN.md, Fase 4d, «Resultado de la regla (2026-10-31)»; PLAN.md, Fase 4e, «Resultado de la regla (2026-11-01)»; PLAN.md, fases 4b, 4c y 4d, «Qué no entra, con su motivo» (el ajuste de hiperparámetros); PLAN.md, Fase 4e, «Exploración, semilla 0 (descriptiva)» y «Los ajustes del paso 2 (2026-11-01), fijados antes de leer la exploración»; PLAN.md, Fase 4, especificación de M3 (del ajuste de hiperparámetros del ganador solo consta un estudio de Optuna comentado, celda 23); «Resultados», «Lo que la prueba alcanza a ver» -->
- **Que promediar varios CatBoost, o usar la etiqueta del hospital, mejore el
  modelo.** Solo se midieron en Kaggle, con una cifra por envío. Promediar
  cambia dos cosas a la vez, y el mayor de los dos efectos del hospital cambia
  de signo entre la puntuación pública y la privada. En la validación cruzada
  no se probó promediar varios CatBoost de la misma especificación, ni la
  etiqueta del hospital con M3 limpio o con C7. Esa etiqueta, junto con la otra
  columna de procedencia, solo se probó con los modelos de referencia.
  <!-- F: PLAN.md, Fase 5c, «Salvedades» y «Qué se hace (decisión de la persona, 2026-11-05)»; outputs/fase5c-efectos.json > efectos.hospital_con_imagen.mismo_signo_en_la_publica; outputs/auditoria-de-fugas.json > columnas_procedencia; outputs/sensibilidad-procedencia-repetida.json > comparaciones.b_2b_con_menos_2b_sin y .c_1_con_menos_1_sin; CLAUDE.md, hallazgo 3; .claude/skills/modelado-baseline/scripts/ganador_m3.py, docstring (M3 y M3 limpio excluyen attribution) -->
- **Cuánto se separa de verdad este trabajo de la solución ganadora.** La
  distancia en Kaggle es una resta entre dos cifras sin intervalo, y su reparto
  entre promediar y el hospital depende del orden de los envíos. En el
  desarrollo, la evaluación usó otros datos y otras particiones que la del
  ganador.
  <!-- F: outputs/fase5b-comparacion.json > como_leerla; outputs/fase5c-efectos.json > como_leerlos; PLAN.md, Fase 4, «Orden de magnitud, no comparación» -->
- **Nada clínico.** Los modelos ordenan lesiones por sospecha; no dicen qué
  tiene un paciente ni qué hacer con él. Son evidencia para una decisión
  humana.
  <!-- F: CLAUDE.md, «Guardarraíles del agente», 4 -->

## Limitaciones

- **La clase negativa no está confirmada.** Las lesiones malignas tienen
  patología; de las benignas, *"most never underwent a skin biopsy"*. La
  mayoría de los negativos son lesiones que un dermatólogo no consideró
  preocupantes, no lesiones confirmadas como sanas.
  <!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, línea 306, cita literal; CLAUDE.md, guardarraíl 4 -->
- **Las imágenes tienen una resolución óptica comparable a la de un teléfono
  inteligente.** Así las describe el artículo del conjunto de datos:
  *"comparable in optical resolution to smartphone images"*. El resultado
  de la imagen se limita a estas imágenes y a estos dos modelos de imagen:
  DINOv2 congelado y EfficientNet-B0 entrenada.
  <!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, línea 99, cita literal; la última frase acota el alcance (interpretación); PLAN.md, Fase 4c, «La red» -->
- **Muchas comparaciones a la vez.** Cada comparación (M2 − M1, M4 − M2,
  M4b − M2, M3 − M2, M3 limpio − M2, 2b − 1 en las dos particiones,
  Imagen − M1, (Imagen + básicos) − Imagen, las tres de la Fase 4b contra M3
  limpio, red sola − Imagen y C4 − M3 limpio) se lee en cuatro métricas, y las
  dos de las columnas de procedencia —con y sin ellas, en el boosting y en la
  logística—, solo en la pAUC. Las de las fases 4b y 4c se corrigen por
  multiplicidad dentro de cada fase, con Bonferroni; las demás no, y el
  intervalo del NNT80% SE de M2 − M1 queda al límite del cero.
  <!-- F: CLAUDE.md, hallazgo 4 («son cuatro métricas sobre una misma comparación, y el NNT queda al límite»); fase4_comparar.py (un intervalo por métrica, sin ajuste por multiplicidad); F21 > C.nnt80.IC; EP > particiones.paciente.comparacion_2b_menos_1 y particiones.filas.comparacion_2b_menos_1; IS > C.imagen_menos_m1 y C.imagen_basicos_menos_imagen; outputs/sensibilidad-procedencia-repetida.json > comparaciones.b_2b_con_menos_2b_sin y .c_1_con_menos_1_sin (solo la pAUC); outputs/fase4b-c1-vs-m3limpio.json, outputs/fase4b-c2-vs-m3limpio.json, outputs/fase4b-c3-vs-m3limpio.json, outputs/fase4c-red-sola-vs-imagen.json y outputs/fase4c-c4-vs-m3limpio.json > comparaciones_nuevo_menos_base.*.intervalo_bonferroni_nadeau_bengio (fase4b_comparar.py, confianza 1 − 0,05/3; fase4c_comparar.py, 1 − 0,05/2) -->
- **Cada ronda se eligió viendo las anteriores.** La bitácora de `PLAN.md`
  registra todas las comparaciones por la pAUC desde la Fase 4. Las fases 4d y 4e
  se corrigen con Holm dentro de cada una, y la 4f es una sola pregunta, sin
  corrección; ninguna corrección cubre varias rondas a la vez. La pregunta de la
  4f se eligió con la diferencia de medias ya calculable desde `outputs/`, y en
  la 4e la exploración y la confirmación usan semillas que reparten a los mismos
  pacientes.
  <!-- F: PLAN.md, Fase 4f, «Bitácora, fila de la Fase 4f» y «Lo que el resultado no dice»; outputs/fase4d-holm.json > preguntas; outputs/fase4e-holm.json > preguntas; CLAUDE.md, hallazgo 14, «Las semillas» -->
- **La prueba no distingue mejoras pequeñas frente a M3 limpio.** Con la
  variabilidad observada, para dar su resultado a favor con un 80% de
  probabilidad necesita una mejora real de entre 0,0109 y 0,0159 de pAUC, y más
  semillas casi no bajan ese umbral. El cálculo hereda la aproximación de la
  propia prueba y toma la dispersión observada como la verdadera.
  <!-- F: outputs/potencia-nadeau-bengio.json > comparaciones.*.delta_80 y prueba.rho; CLAUDE.md, hallazgo 16, «Salvedades» -->
- **La corrección de la varianza es aproximada.** Nadeau y Bengio la derivan
  para divisiones aleatorias independientes, y aquí se aplica a una validación
  por pliegues.
  <!-- F: «Método», «Cómo se compara»; referencias/nadeau-bengio-2003-t-corregido.md, «Salvedad de aplicabilidad», líneas 134–143 (LOCAL) -->
- **El NNT80% SE se calcula con una lectura propia**, porque el organizador no
  publica script para él.
  <!-- F: .claude/skills/modelado-baseline/scripts/metricas_triaje.py, docstring -->
- **El conjunto reservado no es del todo independiente.** No es ajeno a las
  decisiones tomadas antes de sellarlo, al diseño de las variables de la
  solución ganadora, que siguen M2 y M3 limpio, ni a la receta de la red de la
  Fase 4e, que su autor fijó sobre todo el conjunto de entrenamiento del reto.
  Tiene 76 lesiones malignas, en 52 pacientes. Y después de su única evaluación
  dejó de estar reservado: los modelos de Kaggle se entrenaron también con él.
  <!-- F: «Datos y validación», «El conjunto reservado»; PLAN.md, Fase 5, «Salvedad de M2» y «Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el reservado»; outputs/fase5-reservado.json > datos.evaluacion.malignas y .pacientes_con_malignas; CLAUDE.md, hallazgo 18, «El reservado dejó de estar reservado» -->
- **Kaggle da una sola cifra por envío.** Sin intervalo, no se puede decir qué
  diferencias entre los ocho envíos son ruido. Los cuatro de la Fase 5c se
  decidieron después de ver los de la 5b: son una segunda mirada al mismo
  conjunto de prueba. Y que la puntuación privada de los envíos tardíos salga
  del mismo subconjunto que el tablero final es lectura nuestra; ninguna fuente
  versionada lo dice.
  <!-- F: outputs/fase5b-comparacion.json > como_leerla; PLAN.md, Fase 5c, «Salvedades»; «Resultados», «En la prueba de Kaggle»; referencias/kaggle-code-requirements.md, líneas 48 y 67–70 -->
- **Los tiempos son de un solo equipo**, con DINOv2 en la GPU y los modelos
  tabulares en la CPU. Solo comparan estos modelos entre sí.
  <!-- F: «Método», «Cómo se mide el tiempo de inferencia»; CLAUDE.md, hallazgo 9 -->
- **Dos supuestos sin verificar.** No se sabe si el clasificador de nevus que
  produce `tbp_lv_nevi_confidence` se entrenó con lesiones de este conjunto. Y
  nada comprueba la versión del código de DINOv2; solo sus pesos, por hash.
  <!-- F: referencias/slice3d-metadata-tbp-lv.md, nota 2, líneas 81–87; .claude/skills/extraccion-imagen/SKILL.md, «Límites conocidos» -->
- **Un mecanismo medido a medias.** Se midió cómo falla el gradient boosting
  sin balancear: hunde a una parte de los positivos al fondo del ordenamiento.
  Por qué lo hace no se midió.
  <!-- F: MEC; «Resultados», «Una decisión por defecto cambia el veredicto» -->
- **La prueba de la partición cubre dos modelos.** Que partir por filas no
  cambie el veredicto se midió con la logística y el boosting balanceados, no
  con los modelos que usan el contexto de paciente.
  <!-- F: EP > esquema.niveles -->

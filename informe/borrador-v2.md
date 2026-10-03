## Método

<!-- Borrador de una sección de informe/borrador-v2.md. Cada comentario «F:»
     da la fuente de la frase o cifra que lo precede. Las marcadas «LOCAL» se
     contrastan con referencias/_texto-completo/, que solo está en el Mac. Los
     comentarios se quitan o se convierten en el anexo de trazabilidad al
     cerrar el informe. -->

### Qué se mide

**La métrica principal es la del reto:** el área parcial bajo la curva ROC por
encima del 80% de sensibilidad, o pAUC, que va de 0 a 0,2.
<!-- F: referencias/kaggle-evaluation.md, «Citas literales», párrafos 1 y 2 (LOCAL) -->
El organizador la justifica en términos clínicos, no estadísticos: *"there are
regions in the ROC space where the values of TPR are unacceptable in clinical
practice"*, y *"Systems that aid in diagnosing cancers are required to be
highly-sensitive"*.
<!-- F: referencias/kaggle-evaluation.md, párrafo 2, cita literal (LOCAL) -->
Esa es la función de utilidad del cliente, escrita en su métrica: la región
del espacio ROC donde la sensibilidad es clínicamente inaceptable no cuenta.
<!-- F: interpretación del proyecto; CLAUDE.md, «Tesis del proyecto» -->
Un clasificador al azar obtiene 0,02 y uno perfecto, 0,2.
<!-- F: outputs/modelado-baseline.json > escala_de_referencia_pauc.azar y .maximo -->

La implementación de la pAUC es una transcripción del algoritmo del
organizador, comprobada contra su script en 200 casos aleatorios, con
coincidencia exacta, y en el caso del clasificador perfecto, que devuelve
0,2.
<!-- F: .claude/skills/modelado-baseline/SKILL.md, «Sobre la métrica: VERIFICADA (2026-08-11)»; outputs/modelado-baseline.json > metrica_fuente -->

**El cliente declaró dos ejes más, con premio propio:** *"Two Secondary
Prizes: $7,500 each for "Top-15 Retrieval Sensitivity" and "Model
Efficiency""*.
<!-- F: referencias/kaggle-rules.md, «Premios secundarios», cita literal (LOCAL) -->
La pAUC no captura ninguno de los dos.
<!-- F: CLAUDE.md, «Tesis del proyecto», «Corolario» -->

- **Sensibilidad top-15 por paciente (SEtop-15).** El premio se otorga al
  algoritmo *"most successful in scoring malignancies within the top-15
  highest scored images per patient"*.
  <!-- F: referencias/isic-metrics-readme.md, «Top-15 retrieval sensitivity», cita literal (LOCAL) -->
  Se calcula como la media, sobre los pacientes con alguna lesión maligna, de
  la fracción de sus lesiones malignas que quedan entre sus 15 de mayor
  puntuación. Así cada paciente enfermo pesa lo mismo, como la describen
  Kurtansky et al. (2025): *"weighed each diseased patient equally"*.
  <!-- F: .claude/skills/modelado-baseline/scripts/metricas_triaje.py, docstring; referencias/kurtansky-2025-triaje-automatizado-tbp.md, métodos -->
  La implementación coincide con el script del organizador, ejecutado sin
  modificar, en seis conjuntos sintéticos con empates.
  <!-- F: .claude/skills/modelado-baseline/SKILL.md, sección de metricas_triaje.py; test_metricas_triaje.py -->
- **Eficiencia.** El organizador la evaluó como *"inference time on an
  undisclosed subset of test set images"*.
  <!-- F: referencias/isic-metrics-readme.md, «Model Efficiency», cita literal (LOCAL) -->
  Aquí se mide como tiempo de inferencia, con la definición de más abajo.

Se reportan además otras dos métricas:

- **NNT80% SE**, de Kurtansky et al. (2025): *"the average number of lesions
  needed to triage to undergo expert evaluation to detect a single
  malignancy, using a threshold corresponding to a given sensitivity"*.
  <!-- F: referencias/kurtansky-2025-triaje-automatizado-tbp.md, métodos, cita literal -->
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
<!-- F: outputs/validacion-repetida.json > semillas_corridas y n_splits; outputs/diseno-validacion.json > esquema (StratifiedGroupKFold, group_col patient_id) -->
Los dos modelos de cada comparación se evalúan sobre los mismos pliegues, así
que cada comparación da 50 diferencias pareadas.
<!-- F: outputs/fase4-*.json > comparaciones_nuevo_menos_base.*.n_diferencias -->

El intervalo de la diferencia media se corrige por el solape entre los
conjuntos de entrenamiento, con la corrección de Nadeau y Bengio (2003): la
varianza de las diferencias se multiplica por 1/n + n_prueba/n_entrenamiento,
que en 5 pliegues es 1/n + 1/4, con el mismo t de n − 1 grados de libertad.
<!-- F: .claude/skills/modelado-baseline/scripts/evaluar_repetido.py, _nadeau_bengio; referencias/nadeau-bengio-2003-t-corregido.md, sección 4 (LOCAL) -->
El artículo deriva la corrección para divisiones aleatorias independientes,
y sus autores presentan ese estimador como cercano al de la validación
cruzada por K pliegues. Aquí se aplica a una validación cruzada por pliegues:
cercana, no igual.
<!-- F: paráfrasis, no cita: referencias/nadeau-bengio-2003-t-corregido.md, «El escenario en que el artículo deriva la fórmula», p. 242 (LOCAL) -->
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

Los modelos propios no se ajustan: usan los hiperparámetros del nivel 2b.
<!-- F: PLAN.md, Fase 4, «Sin ajuste de hiperparámetros»; outputs/fase4-m3limpio-vs-m2.json > hiperparametros -->
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
<!-- F: PLAN.md, Fase 2, «Decisión (2026-09-25, de la persona)»; referencias/simeoni-2025-dinov3.md, «Dónde» y «Lo que se buscó y no se encontró» -->
DINOv2 sí: sus datos de preentrenamiento, LVD-142M, están descritos en un
artículo de abril de 2023, y sus autores no pertenecen a las instituciones que
aportaron los datos. El punto de control que se usó documenta LVD-142M como
sus datos de entrenamiento.
<!-- F: PLAN.md, Fase 2, «Decisión (2026-09-25, de la persona)»; referencias/oquab-2023-dinov2.md, línea 10; PLAN.md, Fase 3, «Preparación (2026-09-25)»; referencias/dinov2-repositorio.md -->
Queda una salvedad: ninguna fuente fija la primera fecha en que SLICE-3D fue
público, y el orden temporal se apoya en una cadena de evidencia.
<!-- F: PLAN.md, Fase 2, «Salvedad declarada»; referencias/slice3d-fechas-de-publicacion.md, sección 5 -->

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
<!-- F: outputs/eda-diagnostico.json > fuente.n_columnas y columnas_solo_en_train; referencias/slice3d-metadata-tbp-lv.md (las tbp_lv_* las computa el software sobre la captura) -->
El archivo de prueba que publica el reto es un marcador de posición, sin
casos reales, así que no hay contra qué medir un resultado final
independiente fuera de lo que este proyecto aparte.
<!-- F: outputs/eda-diagnostico.json > test_is_placeholder -->

### El conjunto reservado

Antes de volver a medir nada, se apartó el 20% de los pacientes —no de las
filas—, estratificado por centro y por tener al menos una lesión maligna, con
semilla 2026, y se selló.
<!-- F: PLAN.md, Fase 1, «Qué se hace» y «Decisiones de la persona sobre el conjunto reservado (2026-09-25)» -->
Ningún estrato quedó vacío: todos los centros tienen al menos un paciente con
lesión maligna a cada lado.
<!-- F: PLAN.md, Fase 1, «Sellado (2026-09-25)» -->
Desde entonces, todas las mediciones de este informe son del conjunto de
desarrollo, y ningún modelo se ha evaluado sobre el reservado.
<!-- F: PLAN.md, Fase 1, «Estado»; outputs/*.json de las mediciones > datos.conjunto = "desarrollo" -->

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
Con lesiones del mismo paciente en entrenamiento y en validación, la métrica
sale inflada.
<!-- F: CLAUDE.md, «Sobre el problema», «Nota metodológica clave» -->

### La auditoría de columnas

Antes de modelar, la auditoría de fugas revisa las columnas, y el modelado se
niega a correr sin su reporte.
<!-- F: .claude/skills/modelado-baseline/SKILL.md, requisitos; informe/casos-de-fallo.md, «Caso B» -->
Quedan fuera de los modelos 15 columnas, por cuatro motivos:
<!-- F: outputs/modelado-baseline.json > columnas_excluidas -->

- **11 no existen al predecir.** El conjunto de prueba no las trae. Entre
  ellas están la propia etiqueta, la taxonomía diagnóstica y dos medidas que
  solo existen tras la biopsia.
  <!-- F: outputs/auditoria-de-fugas.json > columnas_solo_en_train; CLAUDE.md, «Sobre el problema», «Tercera nota» -->
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
<!-- F: outputs/auditoria-de-fugas.json > univariado (41 entradas, ninguna sospechosa), umbral_auc_sospechoso, univariado[0]; .claude/skills/auditoria-de-fugas/SKILL.md, description; .claude/skills/auditoria-de-fugas/scripts/audit_leakage.py, excluir_del_univariado -->

De las preguntas abiertas de la auditoría, la única que no contestan los
motivos de arriba es `tbp_lv_nevi_confidence`, por su nombre, aunque sí está
en el conjunto de prueba.
<!-- F: outputs/auditoria-de-fugas.json > preguntas_abiertas[0]; CLAUDE.md, «Cuarta nota» -->
El artículo del conjunto de datos la define como *"a convolutional neural
network classifier estimated probability that the lesion is a nevus"*, así
que la calcula el software sobre la imagen y está disponible al predecir. Se
usa. Su AUC por sí sola es 0,6422.
<!-- F: referencias/slice3d-metadata-tbp-lv.md, Tabla 1, cita literal; CLAUDE.md, «Cuarta nota — tbp_lv_nevi_confidence»; outputs/auditoria-de-fugas.json > univariado (tbp_lv_nevi_confidence.auc_oof) -->
Queda una salvedad: el clasificador se entrenó con *"approximately 57,000
lesions"*, y el artículo no dice si se solapan con las de este conjunto.
<!-- F: referencias/slice3d-metadata-tbp-lv.md, Tabla 1 y nota 2 -->

## Resultados

<!-- Sección de informe/borrador-v2.md. Mismas convenciones que las
     anteriores. Abreviaturas de los comentarios: VR = outputs/validacion-repetida.json;
     F21 = outputs/fase4-m2-vs-m1.json; F42 = outputs/fase4-m4-vs-m2.json;
     F4b = outputs/fase4-m4b-vs-m2.json; F32 = outputs/fase4-m3-vs-m2.json;
     F3L = outputs/fase4-m3limpio-vs-m2.json; C = comparaciones_nuevo_menos_base;
     IC = intervalo_t_95_nadeau_bengio. -->

Salvo donde se indica, las métricas de desempeño son del conjunto de
desarrollo, con 10 semillas y 5 pliegues. Cada diferencia es «nuevo − base»,
y su intervalo es el corregido al 95%. Los pliegues y semillas en que gana el
nuevo se dan entre paréntesis.
<!-- F: «Método», «Cómo se compara»; F*.json > C.*.nuevo_mejor_en_folds y .nuevo_mejor_en_semillas -->

### Una decisión por defecto cambia el veredicto

El mismo gradient boosting da resultados opuestos según una sola opción. Sin
balancear, su pAUC media es 0,0018, por debajo del piso aleatorio de 0,02 en
los 50 pliegues. Con `class_weight="balanced"`, y nada más distinto, llega a
0,1375.
<!-- F: VR > nivel_2a_gradient_boosting_sin_balancear.pauc_media_global y .pauc_por_semilla_y_fold (los 50 valores bajo 0,02); VR > nivel_2b_gradient_boosting_balanceado.pauc_media_global; outputs/modelado-baseline.json > escala_de_referencia_pauc.azar y nivel_2b_….nota («Única diferencia con 2a: class_weight») -->

La métrica por defecto no es ciega a ese fallo, pero lo lee distinto. En la
partición de la semilla 42, el AUC estándar del modelo sin balancear es
0,582, por encima del azar de su escala, 0,5; su pAUC queda por debajo del
azar de la suya. Las dos métricas discrepan sobre si el modelo supera al azar.
<!-- F: outputs/modelado-baseline.json > esquema_cv.seed, nivel_2a_….auc_estandar_media y .pauc_media; outputs/modelado-baseline.json > nivel_0_referencia_univariada.nota («el AUC va de 0.5 (azar) a 1»); CLAUDE.md, hallazgo 1 -->

### Mejor media no es mejor modelo

El gradient boosting balanceado supera a la regresión logística balanceada
por 0,005 en promedio, con intervalo [−0,0145; 0,0245] (29 de 50 pliegues; 8
de 10 semillas). La ventaja no está establecida.
<!-- F: VR > comparacion_pareada_2b_menos_1.media, .intervalo_t_95_nadeau_bengio, .gana_2b_en y .semillas_a_favor_de_2b -->

Sobre una sola partición de los datos completos, el boosting parecía además
más estable que la logística. Con las 10 semillas el orden se invierte: su
desviación entre pliegues es 0,0165, frente a 0,0138. Ese argumento se retiró.
<!-- F: CLAUDE.md, hallazgo 2 (la partición única); VR > nivel_2b_….pauc_std_entre_folds y nivel_1_regresion_logistica.pauc_std_entre_folds -->

### Las columnas de procedencia no explican la ventaja

Con las columnas de centro y licencia, la diferencia entre el boosting y la
logística es 0,0046; sin ellas, 0,005.
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.a_2b_menos_1_con_procedencia.media y .a_2b_menos_1_sin_procedencia.media -->
Incluirlas mueve el boosting en 0,0021, con intervalo [−0,0082; 0,0124], y
la logística en 0,0025, con [−0,0023; 0,0073].
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.b_2b_con_menos_2b_sin y .c_1_con_menos_1_sin (media e IC) -->
En la logística, incluirlas mejora en las 10 semillas y en 34 de 50
pliegues. La magnitud no está establecida.
<!-- F: outputs/sensibilidad-procedencia-repetida.json > comparaciones.c_1_con_menos_1_sin.gana_primer_termino_en_semillas y .gana_primer_termino_en_folds -->
La exclusión se sostiene por razón de uso, no de desempeño. Una sola
partición sugería lo contrario; es el segundo resultado de una sola partición
que no sobrevive a la validación repetida.
<!-- F: CLAUDE.md, hallazgo 3; PLAN.md, Fase 6, decisión del 2026-10-02 -->

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

### La imagen no justifica su costo

Las 384 variables de DINOv2 tal cual (M4 − M2) no mejoran el modelo con
contexto de paciente:
<!-- F: outputs/extraccion-imagen.json > caracteristica -->

- pAUC: −0,0065, [−0,0263; 0,0133] (19 de 50; 2 de 10);
- sensibilidad top-15: −0,0332, [−0,085; 0,0185] (9 de 50; 0 de 10);
- NNT80% SE: +11,24, [−19,90; 42,37].
<!-- F: F42 > C.pauc, C.setop15 y C.nnt80 -->

Ningún intervalo excluye el cero, y la estimación puntual es peor en las
cuatro métricas.
<!-- F: F42 > C.*.media e IC (auc: −0,0085) -->
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
<!-- F: F42 > C.pauc.nuevo_mejor_en_semillas; F4b > C.pauc.nuevo_mejor_en_semillas; CLAUDE.md, hallazgo 6 -->

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
<!-- F: F32 > metricas.M3.pauc.media_global y .setop15.media_global; referencias/kurtansky-2025-triaje-automatizado-tbp.md, Tabla 3 (Meta-basic, Meta-WB360 y Patient context); PLAN.md, Fase 4, «Orden de magnitud, no comparación» -->

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

### El costo de inferencia

La mediana del tiempo de inferencia, en segundos por cada 1.000 lesiones, es
0,0021 para M1, 0,0209 para M2, 0,0435 para M3 limpio, 14,5156 para M4 y
14,6321 para M4b.
<!-- F: outputs/tiempo-inferencia.json > tiempos.*.mediana_segundos_por_1000_lesiones -->
M3 limpio cuesta más que M2, pero los dos quedan por debajo de una décima de
segundo por cada 1.000 lesiones. Lo caro, con diferencia, es la imagen, y los
modelos con imagen no mejoraron la métrica principal de forma distinguible.
<!-- F: outputs/tiempo-inferencia.json > tiempos; CLAUDE.md, hallazgo 9 -->

### La pregunta del cliente, entera

| Modelo | pAUC | Sensibilidad top-15 | NNT80% SE | Segundos por 1.000 lesiones |
|---|---|---|---|---|
| M1 | 0,1375 | 0,6223 | 116,16 | 0,0021 |
| M2 | 0,1440 | 0,7065 | 85,62 | 0,0209 |
| M3 limpio | 0,1621 | 0,7292 | 65,55 | 0,0435 |
| M4 | 0,1375 | 0,6732 | 96,85 | 14,5156 |
| M4b | 0,1496 | 0,7003 | 81,74 | 14,6321 |

<!-- F: medias de los 50 pliegues: F21 > metricas.M1 y metricas.M2 (*.media_global); F3L > metricas.M3limpio; F42 > metricas.M4; F4b > metricas.M4b. M2 es igual en los cuatro archivos (reproduccion_del_base.reproduce_fold_a_fold). Tiempos: outputs/tiempo-inferencia.json > tiempos.*.mediana_segundos_por_1000_lesiones. M3 no está: no es candidato y su camino de predicción no se cronometró (PLAN.md, Fase 4, «Tiempo de inferencia») -->

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
     anteriores; las abreviaturas F21, F42, F4b y F3L son las de «Resultados». -->

### Qué se recomienda

**Al cliente se le recomienda M3 limpio:** la parte tabular reproducida de la
solución ganadora, sin los dos sesgos conocidos a su favor.
<!-- F: «Resultados», «El modelo recomendado»; PLAN.md, Fase 4, «Modelo recomendado: decisión de la persona, 2026-09-26» -->
Se eligió con una regla fijada antes de correr la comparación: el intervalo
corregido de su diferencia con M2 en la pAUC queda entero por encima de cero.
<!-- F: PLAN.md, Fase 4, «Regla de recomendación»; F3L > C.pauc.IC -->

**No se recomienda añadir las variables de imagen** tal como se probaron. No
mejoraron ninguna métrica de forma distinguible, y al predecir cuestan 14,5156
y 14,6321 segundos por cada 1.000 lesiones, frente a 0,0435 de M3 limpio.
<!-- F: F42 y F4b > C.*.IC; outputs/tiempo-inferencia.json > tiempos.M4, tiempos.M4b y tiempos.M3limpio (mediana_segundos_por_1000_lesiones) -->

**Y se recomienda no leer solo la pAUC.** El contexto de paciente no se nota
en ella y sí en las dos métricas de triaje: la sensibilidad top-15 y el NNT80% SE.
<!-- F: F21 > C.pauc.IC, C.setop15.IC y C.nnt80.IC -->

### Qué se puede afirmar

- En el conjunto de desarrollo, con validación cruzada repetida y el
  intervalo corregido, M3 limpio supera a M2 en la pAUC y en el AUC estándar.
  <!-- F: F3L > C.pauc.IC y C.auc.IC -->
- El contexto de paciente mejora frente a M1 la sensibilidad top-15 y el NNT80%
  SE.
  <!-- F: F21 > C.setop15.IC y C.nnt80.IC -->
- Las variables de imagen de DINOv2, como variables sueltas o apiladas, no
  mejoran de forma distinguible ninguna de las métricas.
  <!-- F: F42 y F4b > C.*.IC -->
- Una partición por filas habría dejado al 98,92% de los pacientes a los dos
  lados de la validación.
  <!-- F: outputs/diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga -->

### Qué no se puede afirmar

- **Que M3 limpio sea mejor en las métricas de triaje.** En la sensibilidad top-15
  y en el NNT80% SE no se distingue de M2.
  <!-- F: F3L > C.setop15.IC y C.nnt80.IC -->
- **Cuál de los dos sesgos de M3 pesaba.** M3 limpio cambia tres cosas a la vez.
  <!-- F: PLAN.md, Fase 4, «Lectura, declarada antes de correr» -->
- **Cuánto rinde M3 limpio fuera del conjunto de desarrollo.** El conjunto
  reservado no se ha abierto. Cuando se abra, la estimación principal seguirá
  siendo la validación cruzada repetida, y la recomendación no cambiará por su
  resultado.
  <!-- F: PLAN.md, Fase 5, «Especificación» -->
- **Nada sobre otras formas de usar la imagen.** Solo se probaron las
  variables de DINOv2 sin reentrenarlo; las redes de imagen del ganador quedaron
  fuera.
  <!-- F: «Método», «Qué se compara»; PLAN.md, Fase 4, «Quedan fuera, con su motivo»; .claude/skills/extraccion-imagen/SKILL.md (sin ajuste fino; pasada congelada) -->
- **Que este trabajo supere o no a la solución ganadora.** Su evaluación usó
  otros datos y otras particiones.
  <!-- F: PLAN.md, Fase 4, «Orden de magnitud, no comparación» -->
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
  de la imagen se limita a estas imágenes y a este extractor.
  <!-- F: referencias/kurtansky-2024-slice3d-descriptor.md, línea 99, cita literal; la última frase acota el alcance (interpretación) -->
- **Muchas comparaciones a la vez.** Las cinco comparaciones M2 − M1, M4 − M2,
  M4b − M2, M3 − M2 y M3 limpio − M2 se leen en cuatro métricas cada una, sin
  corregir por multiplicidad, y el intervalo del NNT80% SE de M2 − M1 queda al
  límite del cero.
  <!-- F: CLAUDE.md, hallazgo 4 («son cuatro métricas sobre una misma comparación, y el NNT queda al límite»); fase4_comparar.py (un intervalo por métrica, sin ajuste por multiplicidad); F21 > C.nnt80.IC -->
- **La corrección de la varianza es aproximada.** Nadeau y Bengio la derivan
  para divisiones aleatorias independientes, y aquí se aplica a una validación
  por pliegues.
  <!-- F: «Método», «Cómo se compara»; referencias/nadeau-bengio-2003-t-corregido.md (LOCAL) -->
- **El NNT80% SE se calcula con una lectura propia**, porque el organizador no
  publica script para él.
  <!-- F: .claude/skills/modelado-baseline/scripts/metricas_triaje.py, docstring -->
- **El conjunto reservado no es del todo independiente.** No es ajeno a las
  decisiones tomadas antes de sellarlo ni al diseño de las variables de la
  solución ganadora, que siguen M2 y M3 limpio.
  <!-- F: «Datos y validación», «El conjunto reservado»; PLAN.md, Fase 5, «Salvedad de M2» -->
- **Los tiempos son de un solo equipo**, con DINOv2 en la GPU y los modelos
  tabulares en la CPU. Solo comparan estos modelos entre sí.
  <!-- F: «Método», «Cómo se mide el tiempo de inferencia»; CLAUDE.md, hallazgo 9 -->
- **Dos supuestos sin verificar.** No se sabe si el clasificador de nevus que
  produce `tbp_lv_nevi_confidence` se entrenó con lesiones de este conjunto. Y
  nada comprueba la versión del código de DINOv2; solo sus pesos, por hash.
  <!-- F: referencias/slice3d-metadata-tbp-lv.md, nota 2; .claude/skills/extraccion-imagen/SKILL.md, «Límites conocidos» -->
- **Un mecanismo sin medir.** No se midió por qué el gradient boosting sin
  balancear queda bajo el azar de la pAUC; el informe solo afirma que queda.
  <!-- F: CLAUDE.md, Pendientes, «el mecanismo del nivel 2a está sin medir» -->

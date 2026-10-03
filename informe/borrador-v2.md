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

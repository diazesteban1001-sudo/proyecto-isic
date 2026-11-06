# Proyecto de consultoría ISIC 2024 — Detección de cáncer de piel

**Estado: proyecto en curso, en su última fase.** Las cifras de este README
se confirmaron contra `outputs/` el 2026-11-06. El avance frente a los
objetivos del anteproyecto está en
[Avance respecto a los objetivos del anteproyecto](#avance-respecto-a-los-objetivos-del-anteproyecto).

## El problema y la contraparte

La International Skin Imaging Collaboration (ISIC) y Memorial Sloan
Kettering Cancer Center (MSKCC) plantearon un problema real de triage
clínico: identificar lesiones malignas de piel a partir de fotografía
corporal total en 3D — imágenes de calidad no clínica, pensadas para
contextos con acceso limitado a dermatoscopio.

La necesidad de la contraparte no se limita a una sola métrica. Además
del puntaje principal (pAUC sobre 80% de sensibilidad, que exige que el
sistema sea clínicamente sensible antes que preciso en general), ISIC
premió por separado la capacidad de priorizar las lesiones más
sospechosas por paciente ("Top-15 Retrieval Sensitivity") y la
eficiencia computacional del modelo. Esas tres señales, declaradas con
premios reales, son la línea base de lo que la contraparte necesita —
no solo lo que pidió en el leaderboard.

## Avance respecto a los objetivos del anteproyecto

Los objetivos y sus criterios de cumplimiento son los de
`informe/anteproyecto.md`, sección 3; la columna del criterio los resume, y
el texto literal está allí. En `PLAN.md` están cerradas las fases 0 a 5c.
Después de la Fase 4 se añadieron intentos de mejorar al modelo recomendado
y a la imagen: la 4b, con combinaciones de lo que ya había; la 4c, con una red
de imagen entrenada sobre los recortes; la 4d y la 4e, con ideas del código
del ganador y con la receta de imagen del 10.º puesto del reto; y la 4f, que
comparó esa red con el punto de partida sin fotografía corporal total. La
Fase 5 abrió el conjunto reservado, una sola vez. La 5b y la 5c enviaron ocho
modelos a Kaggle, que sigue aceptando envíos a la competición cerrada. Queda
la Fase 6: el informe y la demo.

| Objetivo específico | Su criterio, en resumen | Estado | Dónde se comprueba |
|---|---|---|---|
| 1. Esquema de evaluación libre de fuga | La proporción de pacientes presentes a ambos lados de cada partición; las variables excluidas, con su motivo; el conjunto reservado, sellado antes de cualquier decisión nueva de modelado | Cumplido | `diseno-validacion.json > fuga_de_grupo_detectada` y `comparacion_particion_naive`; `modelado-baseline.json > columnas_excluidas` y `auditoria-de-fugas.json`; `holdout-pacientes.json`, sellado en la Fase 1 de `PLAN.md` |
| 2. Cuatro niveles de referencia bajo la pAUC y el AUC, en los mismos pliegues | Las medias y las series por pliegue de las dos métricas; los casos en que discrepan en el veredicto | Cumplido | `modelado-baseline.json > nivel_*.pauc_por_fold` y `auc_estandar_por_fold`; las discrepancias, en `informe/borrador-v2.md`, «Una decisión por defecto cambia el veredicto» y «Una ventaja que la pAUC no ve» |
| 3. Comparación pareada de los niveles y de la solución ganadora reproducida | El intervalo de cada diferencia, ingenuo y corregido; los componentes del ganador que no se pudieron reproducir, con su motivo | Cumplido. Entre niveles, la comparación es 2b − 1; el ganador se compara con M2. Lo que falta del ganador quedó fuera por decisión, cada cosa con su motivo. Las fases 4b y 4c compararon además contra M3 limpio tres combinaciones y la red apilada, con corrección por multiplicidad, y las fases 4d y 4e, tres versiones más, C5 a C7, con la corrección de Holm. Ninguna llega a la regla. | `validacion-repetida.json` y `fase4-*.json`, campos `intervalo_t_95` e `intervalo_t_95_nadeau_bengio`; lo que queda fuera del ganador, en `informe/borrador-v2.md`, «Qué se compara»; las combinaciones, en `fase4b-*.json`; la red apilada, en `fase4c-c4-vs-m3limpio.json`; C5 a C7, en `fase4d-*.json` y `fase4e-*.json`, con `fase4d-holm.json` y `fase4e-holm.json` |
| 4. Ejes de triaje y tiempo de inferencia | La tabla por nivel de la métrica principal, los dos ejes de triaje y el tiempo; la implementación de los ejes, contrastada contra el orden de magnitud publicado | Cumplido en parte: la tabla, sobre los modelos de la Fase 4; el contraste, solo de la sensibilidad top-15. Ver la nota | `informe/borrador-v2.md`, «La pregunta del cliente, entera» y, para el contraste, «El modelo recomendado»; `tiempo-inferencia.json` |
| 5. Características de imagen, con verificación previa del preentrenamiento, y evaluación del modelo recomendado en el reservado | El resultado de la verificación; las métricas del reservado, con su intervalo | Cumplido: hechas la verificación, la extracción y la evaluación de la imagen en desarrollo, y la evaluación en el reservado del modelo recomendado, M3 limpio, que no usa imagen, en las cuatro métricas con su intervalo; en la pAUC, 0,1588 [0,1387; 0,1766]. Las fases 4c a 4e entrenaron además una red de imagen sobre los recortes, y la 4f la comparó con la imagen de DINOv2 con edad, sexo y zona del cuerpo | `informe/borrador-v2.md`, «El extractor de imagen»; `extraccion-imagen.json`; `fase4-m4-vs-m2.json`, `fase4-m4b-vs-m2.json` e `imagen-sola.json`; la red entrenada, en `fase4c-*.json`, `fase4d-red-mejorada-vs-red.json` y `fase4e-red-vs-red4c.json`; su preentrenamiento, en `referencias/efficientnet-b0-preentrenamiento.md`; el reservado, en `fase5-reservado.json > metricas.M3limpio.*.punto` e `.intervalo_95` |

**Nota sobre el objetivo 4.** La tabla no va por nivel, como dice el
criterio, sino por modelo de la Fase 4: M1, que es el nivel 2b; M2, M4 y
M4b, que lo extienden; y M3 limpio, la parte tabular del ganador. Los
niveles 1 y 2b tienen los dos ejes de triaje en `efecto-particion.json`; los
niveles 0 y 2a no los tienen, y ninguno de los niveles 0, 1 y 2a tiene
tiempo de inferencia. El contraste con el orden de magnitud publicado cubre
la sensibilidad top-15, no el NNT80% SE: el NNT depende de la prevalencia
del conjunto evaluado, y el publicado no es comparable (`PLAN.md`, Fase 4,
«Especificación de M3», nota «Orden de magnitud, no comparación»).

**El objetivo general** pide establecer un procedimiento de evaluación que
priorice la función de utilidad del organizador y determinar en qué medida
las decisiones por defecto alteran el veredicto sobre un modelo. El
procedimiento se cerró con la evaluación en el reservado, una sola vez
(objetivo 5). De las tres decisiones que nombra, en el conjunto de
desarrollo, el tratamiento del desbalance y la métrica cambian el
veredicto; el esquema de partición no lo cambia de forma distinguible para
la logística y el boosting balanceados (`informe/borrador-v2.md`, «Una
decisión por defecto cambia el veredicto», «Una ventaja que la pAUC no ve»
y «Partir por filas no cambia el veredicto»). Una decisión de método más,
cuántas preguntas se corrigen juntas, cambia el veredicto sobre la red de
imagen de la Fase 4e (`informe/borrador-v2.md`, «La imagen sola, sin el
sistema de fotografía corporal total»).

## Método

El análisis se reparte en seis carpetas de código. Cinco son de
instrumentos, que miden y reportan, cada uno en sus propios archivos de
`outputs/`; la sexta, la de síntesis, interpreta a partir de esos archivos,
redacta el informe y genera la demo.

| Carpeta | Papel | Qué hace |
|---|---|---|
| `eda-diagnostico` | Instrumento | Perfila los datos: tipos, faltantes, desbalance y estructura de las lesiones por paciente |
| `diseno-validacion` | Instrumento | Sella el conjunto reservado; construye y audita la partición cruzada agrupada por paciente |
| `auditoria-de-fugas` | Instrumento | Chequeos estructurales y escaneo de columnas con señal univariada sospechosa |
| `modelado-baseline` | Instrumento | Entrena y compara los modelos con la métrica oficial y las métricas de triaje, y mide el tiempo de inferencia |
| `extraccion-imagen` | Instrumento | Extrae las variables de imagen con DINOv2, sin reentrenarlo |
| `sintesis-consultoria` | Síntesis | Redacta el informe y genera la demo desde `outputs/`, y señala las cifras que no tienen respaldo en un archivo |

La demo usa las salidas hasta la Fase 5c. El informe está en
`informe/borrador-v2.md`, ya con todas las fases; `informe/borrador.md` es la
versión anterior a la reserva de pacientes. La regla que gobierna el informe: ninguna cifra
existe si no está en un archivo de `outputs/`.

## Hallazgos principales

*(Cada cifra indica el archivo y campo de `outputs/` del que sale. Salvo
donde se dice otra cosa, son cifras del conjunto de desarrollo: el 20 % de
los pacientes se reservó y se abrió una sola vez, después de todas las
comparaciones en el desarrollo. Las
decisiones tomadas antes de reservarlo, con todos los datos, están
declaradas en el anteproyecto (`informe/anteproyecto.md`, sección 4.2),
salvo el diseño de las variables del ganador, que se declara más abajo. Las
comparaciones entre modelos usan validación cruzada agrupada por paciente,
repetida con 10 semillas —50 pliegues—, o con 5 en parte de las fases 4d a
4f, e intervalos al 95 % corregidos por Nadeau y Bengio.)*

- **Riesgo de fuga cuantificado:** sin agrupar por paciente, el **98,92 %**
  de los pacientes habría quedado repartido entre entrenamiento y
  validación
  (`diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga`).
  Pero, medido, partir por filas no cambia de forma distinguible la pAUC, el
  AUC ni el NNT80% SE de la logística y el boosting balanceados, ni el
  veredicto entre ellos (`efecto-particion.json > filas_menos_paciente` y
  `particiones.*.comparacion_2b_menos_1.pauc`).
- **15 columnas quedan fuera de los modelos**, por cuatro motivos
  (`modelado-baseline.json > columnas_excluidas`). 11 no existen al
  predecir: el conjunto de prueba no las trae, y entre ellas va la propia
  respuesta (`auditoria-de-fugas.json > columnas_solo_en_train`).
  `image_type` es constante e `isic_id` identifica la fila
  (`auditoria-de-fugas.json > columnas_constantes` y
  `columnas_identificador`). `attribution`
  y `copyright_license` describen el centro y la licencia de la imagen, no
  la lesión (`auditoria-de-fugas.json > columnas_procedencia`).
- **Una decisión por defecto cambia el veredicto.** El gradient boosting
  sin balancear queda en pAUC **0,0018**, por debajo del piso aleatorio de
  la métrica, 0,02. El mismo modelo con `class_weight="balanced"` llega a
  **0,1375**
  (`validacion-repetida.json > nivel_2a_gradient_boosting_sin_balancear.pauc_media_global`
  y `nivel_2b_gradient_boosting_balanceado.pauc_media_global`; el piso, en
  `modelado-baseline.json > escala_de_referencia_pauc.azar`).
- **La pAUC no ve una ventaja que las otras métricas sí, y una conclusión
  propia se retiró.** El
  boosting balanceado supera a la regresión logística balanceada por 0,005
  en promedio, pero el intervalo corregido va de −0,0145 a 0,0245
  (`validacion-repetida.json > comparacion_pareada_2b_menos_1.media` y
  `comparacion_pareada_2b_menos_1.intervalo_t_95_nadeau_bengio`). En el
  AUC, la sensibilidad top-15 y el NNT80% SE la ventaja del boosting sí está
  establecida
  (`efecto-particion.json > particiones.paciente.comparacion_2b_menos_1`). En
  una sola partición de los datos completos parecía, además, más estable. Con
  las 10 semillas su dispersión entre pliegues es mayor: 0,0165 frente a
  0,0138
  (`validacion-repetida.json > nivel_2b_gradient_boosting_balanceado.pauc_std_entre_folds`
  y `nivel_1_regresion_logistica.pauc_std_entre_folds`). Ese argumento se
  retiró.
- **La métrica principal no agota lo que pidió el cliente.** Añadir
  contexto de paciente no mueve la pAUC de forma distinguible: +0,0065,
  intervalo [−0,0147; 0,0276]
  (`fase4-m2-vs-m1.json > comparaciones_nuevo_menos_base.pauc`). Sí mejora
  la sensibilidad top-15 por paciente, uno de los ejes que ISIC premió
  aparte: +0,0842 [0,021; 0,1473]
  (`fase4-m2-vs-m1.json > comparaciones_nuevo_menos_base.setop15`).
- **Añadida al modelo con contexto de paciente, la imagen no justifica su
  costo.** El modelo de imagen se eligió con
  dos criterios sobre sus datos de preentrenamiento, fijados antes de
  aplicarlos. El primero descartó PanDerm, específico de dermatología,
  porque su artículo declara un subconjunto de ISIC 2024 entre sus datos de
  preentrenamiento; el segundo descartó DINOv3, y quedó DINOv2. Sus 384
  variables (`extraccion-imagen.json > caracteristica`) no mejoran al
  modelo con contexto de paciente: pAUC −0,0065 [−0,0263; 0,0133]
  (`fase4-m4-vs-m2.json > comparaciones_nuevo_menos_base.pauc`). Al
  predecir, ese modelo tarda una mediana de 14,5156 segundos por cada 1.000
  lesiones; sin la imagen, 0,0209
  (`tiempo-inferencia.json > tiempos.M4` y `tiempos.M2`).
  DINOv2 corre en la GPU del equipo y los modelos tabulares en la CPU, así
  que los tiempos solo comparan estos modelos entre sí, en el mismo equipo.
  Eso vale donde se toma la fotografía corporal total, cuyo software calcula
  las mediciones de las que dependen los modelos tabulares. Sin ese sistema,
  la imagen sola distingue lesiones malignas muy por encima del azar, aunque
  por debajo de M1: pAUC 0,0796 frente a 0,1375
  (`imagen-sola.json > metricas.Imagen.pauc.media_global` y
  `metricas.M1.pauc.media_global`). No se ha medido con fotos de teléfono.
- **Una red de imagen entrenada sobre los recortes queda por encima de la
  imagen sola con DINOv2, sin llegar a la regla.** EfficientNet-B0, entrenada
  en cada pliegue, sube la pAUC media de la imagen sola de 0,0796 a 0,1083, y
  queda por encima en 44 de 50 pliegues y en las 10 semillas. Con el intervalo
  corregido por haber hecho dos preguntas (Bonferroni), la diferencia,
  +0,0287, va de −0,0037 a 0,0611, así que la regla fijada antes no la da por
  establecida
  (`fase4c-red-sola-vs-imagen.json > comparaciones_nuevo_menos_base.pauc.media`
  e `.intervalo_bonferroni_nadeau_bengio`). En el AUC estándar, que no decide,
  sí queda entero por encima de cero; en la sensibilidad top-15 y el NNT80% SE,
  el intervalo contiene el cero. Se midió sobre los recortes del sistema de
  fotografía corporal total, no con fotos de teléfono.
- **Con otra receta de entrenamiento, la red sube más, y pasa a ser la
  recomendación sin fotografía corporal total.** Con la receta de imagen del
  10.º puesto del reto y un ajuste fino por la pAUC, la red llega a 0,1376,
  frente a 0,1086 de la de la Fase 4c: +0,029 [0,002; 0,056]
  (`fase4e-red-vs-red4c.json > metricas.Red4eAjustada.pauc.media_global`,
  `metricas.Red.pauc.media_global`, `comparaciones_nuevo_menos_base.pauc.media`
  e `.intervalo_t_95_nadeau_bengio`). Su valor p, 0,0365, no llega al umbral
  de Holm para la primera de dos preguntas, 0,025; con una sola pregunta, el
  umbral habría sido 0,05, así que lo que decide es la corrección por
  multiplicidad (`fase4e-holm.json > preguntas` y `alfa`). Después, en una
  sola pregunta elegida tras ver la Fase 4e, la red supera a la imagen de
  DINOv2 con edad, sexo y zona del cuerpo, «Imagen + básicos»: +0,0493
  [0,0218; 0,0767], mejor en 25 de 25 pliegues
  (`fase4f-red4e-vs-imagen-basicos.json > comparaciones_nuevo_menos_base.pauc`).
  Por la regla, la red pasa a ser la recomendación donde no hay fotografía
  corporal total. En el reservado, esa ventaja no se reprodujo (abajo).
- **Modelo recomendado: la parte tabular de la solución ganadora del reto,
  reproducida y sin los dos sesgos conocidos que esa reproducción
  conservaba a su favor**: los hiperparámetros y las columnas descartadas,
  que su autor pudo elegir con todos los datos, y las transformaciones sin
  etiqueta, ajustadas también con las filas de validación. Supera al modelo
  con contexto de paciente en pAUC: +0,0181 [0,0021; 0,0341], mejor en 43
  de 50 pliegues
  (`fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.pauc`). En
  las métricas de triaje la diferencia no se distingue de cero: ni en
  sensibilidad top-15 ni en el número de lesiones que hay que revisar por
  cada maligna detectada al 80% de sensibilidad, NNT80% SE
  (`fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.setop15` y
  `comparaciones_nuevo_menos_base.nnt80`). Predice con una mediana de
  0,0435 segundos por cada 1.000 lesiones
  (`tiempo-inferencia.json > tiempos.M3limpio`). La regla de recomendación
  se fijó antes de correr la comparación. Entre lo que esa limpieza no
  quita está el diseño de sus variables, que su autor fijó sin ningún
  conjunto reservado: el reservado de este proyecto no le es ajeno.
- **Tres intentos de mejorar al modelo recomendado no lo superan.** Los
  candidatos y la regla se fijaron antes de correr, y el intervalo se corrigió
  además por haber probado tres (Bonferroni). Ninguna combinación supera a M3
  limpio en la pAUC: mezclarlo con el modelo con contexto de paciente,
  −0,0025 [−0,0129; 0,008]; añadirle las dos variables de imagen de M4b,
  +0,0011 [−0,012; 0,0142]; y mezclarlo con un segundo boosting sobre sus
  mismas variables, −0,0009 [−0,012; 0,0101]
  (`fase4b-c1-vs-m3limpio.json`, `fase4b-c2-vs-m3limpio.json` y
  `fase4b-c3-vs-m3limpio.json > comparaciones_nuevo_menos_base.pauc.media` y
  `comparaciones_nuevo_menos_base.pauc.intervalo_bonferroni_nadeau_bengio`).
  M3 limpio sigue siendo el modelo recomendado. Las combinaciones se eligieron
  después de conocer los resultados de la Fase 4, y así está declarado en
  `PLAN.md`.
- **Apilada sobre el modelo recomendado, la red tampoco lo supera según la
  regla.** M3 limpio con las dos variables de la red sube la pAUC media de
  0,1621 a 0,1687, y queda por encima en 39 de 50 pliegues y en las 10
  semillas. Pero el intervalo de la diferencia, +0,0067, va de −0,003 a 0,0164
  (`fase4c-c4-vs-m3limpio.json > comparaciones_nuevo_menos_base.pauc.media` e
  `.intervalo_bonferroni_nadeau_bengio`). M3 limpio sigue siendo el modelo
  recomendado. Las puntuaciones de la red se apilaron con los mismos pliegues,
  un atajo declarado en `PLAN.md`; en la semilla 0, la versión estricta dio más
  pAUC que el atajo en los cinco pliegues (`fase4c-control-atajo.json`).
- **Tres versiones más tampoco llegan a la regla.** Con ideas del código del
  ganador (Fase 4d) y con la red de la Fase 4e apilada (C7), la diferencia con
  M3 limpio en la pAUC es +0,0039 [−0,005; 0,0127] para C5, +0,005
  [−0,0031; 0,0131] para C6 y +0,0029 [−0,0084; 0,0141] para C7, y Holm no
  acepta ninguna (`fase4d-c5-vs-m3limpio.json`, `fase4d-c6-vs-m3limpio.json` y
  `fase4e-c7-vs-m3limpio.json > comparaciones_nuevo_menos_base.pauc.media` e
  `.intervalo_t_95_nadeau_bengio`; `fase4d-holm.json` y
  `fase4e-holm.json > preguntas`). Las cuatro versiones apiladas, de C4 a C7,
  quedan por encima de M3 limpio en la media. Al predecir, C7 se proyectó en
  Kaggle, en otro equipo y no con el procedimiento con que se midieron los
  demás tiempos, en 0,39 horas por cada 500.000 lesiones, frente a 0,04 horas
  de M3 limpio
  (`fase5b-kaggle-medicion.json > salida_del_notebook.tiempo.proyeccion` y
  `salida_del_notebook.tiempo.lesiones_de_prueba_supuestas`).
- **La prueba no alcanza a ver mejoras de ese tamaño.** Con la variabilidad
  observada, para dar su resultado a favor con un 80 % de probabilidad, la
  prueba con que se compara contra M3 limpio necesita una mejora real de entre
  0,0109 y 0,0159 de pAUC, según la comparación y el número de semillas; para
  un 50 %, de entre 0,0076 y 0,0111
  (`potencia-nadeau-bengio.json > comparaciones.*.delta_80` y `.delta_50`).
  Las mejoras observadas, de +0,0029 a +0,0067, quedan por debajo del umbral
  del 50 % (`comparaciones.*.media_observada`), y pasar de 5 a 10 semillas
  casi no mueve esos umbrales. No distinguir una mejora no es lo mismo que no
  tenerla.
- **El conjunto reservado, abierto una sola vez, mantiene la ventaja del
  modelo recomendado.** En sus 209 pacientes, M3 limpio da una pAUC de 0,1588
  [0,1387; 0,1766] y supera al modelo con contexto de paciente en la pAUC,
  +0,0201 [0,0008; 0,0413], y en el AUC, +0,0219 [0,0009; 0,0459]
  (`fase5-reservado.json > datos.evaluacion.pacientes`,
  `metricas.M3limpio.pauc` y `diferencia_m3limpio_menos_m2`). Los intervalos
  son de un bootstrap por paciente, que no mide lo mismo que el de la
  validación cruzada. La ventaja de la red de la Fase 4e sobre «Imagen +
  básicos», en cambio, no se reprodujo: −0,0078 [−0,0306; 0,02]
  (`fase5-posterior.json > red4e_menos_imagen_basicos.pauc`), y por qué
  «Imagen + básicos» da más en el reservado que en el desarrollo no está
  medido. En Kaggle, la red vuelve a quedar por encima, 0,1159 frente a
  0,08935, sin intervalo, en un envío que se decidió después de ver el
  reservado
  (`fase5b-comparacion.json > comparaciones_con_la_privada.red4e_menos_imagen_basicos`).
- **En la puntuación privada de Kaggle, ningún modelo de este proyecto llega
  al ganador.** Kaggle da una cifra por envío, sin intervalo. C7 obtiene
  0,15856, frente a 0,1726 del ganador: −0,01404
  (`fase5b-comparacion.json > comparaciones_con_la_privada.c7_menos_ganador`).
  Cuatro envíos más, en un diseño de dos por dos, descomponen esa distancia:
  promediar 45 CatBoost, como los que entrena el código del ganador, cubre
  +0,00507; usar la etiqueta del hospital, que este proyecto excluye,
  +0,00237; y quedan −0,0066
  (`fase5c-efectos.json > descomposicion_de_la_distancia_al_ganador`; los 45,
  en `fase5c-entrenamiento.json > modelos.*.modelos`). El reparto depende del
  orden de los envíos: primero promediar, después el hospital. El
  envío más cercano, con las dos cosas, da 0,166
  (`fase5c-efectos.json > kaggle.C7PromHosp.privada`). Que la puntuación
  privada de un envío tardío salga del mismo subconjunto que el tablero final
  es lectura nuestra. Con los ocho envíos, el proyecto cerró Kaggle.
- **La implementación de la métrica se verificó contra el script oficial
  del organizador** —no contra una reimplementación propia ni de memoria—
  antes de confiar en ningún resultado de modelado
  (`modelado-baseline.json > metrica_fuente`; la ficha de la fuente, con su
  URL, en `referencias/isic-primary-metric-pauc.py.md`).

**▶ [Ver demo en vivo](https://diazesteban1001-sudo.github.io/proyecto-isic/)**
— cada cifra del texto muestra su origen al pasar el cursor: el archivo y
el campo de `outputs/`, o el archivo y la línea de la fuente.
Como arriba, sus cifras son del conjunto de desarrollo, salvo las del
reservado y las de Kaggle, que se dicen como tales; están sobre todo en su
sección «Fuera del conjunto de desarrollo». El
borrador anterior del informe (`informe/borrador.md`) e
`informe/casos-de-fallo.md` son anteriores a la reserva: salen de la
corrida sobre el 100 % de los datos y ya no coinciden con estas cifras.

La misma demo está en `informe/demo.html`: **autocontenida de verdad**
—datos y librería de gráficos empotrados, cero peticiones de red— así que
abre con doble clic desde una USB, sin servidor y sin conexión. Verificado
renderizándola con todo el tráfico bloqueado, no solo leyendo el código.
Las dos copias —esa y la publicada— las escribe `generar_demo.py` en la
misma corrida, así que no pueden desincronizarse.

## Cómo reproducirlo

Los datos no se versionan. Son los de
[la competencia ISIC 2024 en Kaggle](https://www.kaggle.com/competitions/isic-2024-challenge/overview)
y van en `data/`: `train-metadata.csv`, `test-metadata.csv` y
`train-image.hdf5`, que llega comprimido.

Cada carpeta de código está en `.claude/skills/`, con sus scripts y su
descripción en `SKILL.md`. Tres scripts del modelado
—`evaluar_repetido.py`, `fase4_comparar.py` y `tiempo_inferencia.py`— no
tienen registrado el comando con que se corrieron; está anotado como
pendiente.

El orden importa:

- Primero se sella el conjunto reservado, con
  `diseno-validacion/scripts/sellar_reservado.py`. Después, los
  instrumentos leen su lista de pacientes: la extracción de imagen, para
  separar los dos conjuntos; los demás, para quedarse solo con el de
  desarrollo.
- La auditoría de fugas va antes del modelado, que se niega a correr sin
  ella.
- En el modelado, `evaluar_repetido.py` va antes de
  `sensibilidad_repetida.py`, que exige su salida.
- La extracción de imagen va antes de los modelos con imagen.
- La síntesis va al final, y en ella el verificador va antes de la demo,
  que lee su salida.

El conjunto reservado ya se abrió, y `fase5.py` se niega a volver a correr.
Los envíos a Kaggle tampoco se repiten: `fase5b_kaggle.py` y
`fase5c_kaggle.py` se niegan a reenviar un modelo que ya tiene puntuación.

El tiempo de inferencia se midió con Python 3.11.9, y en el mismo archivo
están las versiones de los paquetes de cada modelo
(`outputs/tiempo-inferencia.json > declaraciones`); las de la extracción de
imagen están en `outputs/extraccion-imagen.json > software`.

Tres pruebas comparan con código de 2024 del organizador o del ganador, y
lo ejecutan en un intérprete aparte: se indica con la variable de entorno
`PYTHON_GUION_ISIC` y lleva las versiones de
`.claude/skills/modelado-baseline/requisitos-interprete-2024.txt`. La que
compara con el guion del organizador necesita además una copia local que
no se versiona, así que en un clon nuevo esa comparación no corre.

Herramientas y versiones: [`HERRAMIENTAS.md`](HERRAMIENTAS.md).

## Qué falta

La ruta —qué fase sigue y qué condición la cierra— está en `PLAN.md`. Lo
que queda en ella:

- **Terminar el informe** (`informe/borrador-v2.md`). Ya tiene todas las
  fases; falta el anexo de trazabilidad, donde se revisan una por una las
  cifras que el verificador señala.

Dos puntos de una versión anterior de este README están cubiertos solo en
parte, y todavía no tienen lugar en la ruta:

- **La línea base de la práctica clínica.** El anteproyecto (apartado 1)
  trae una medición de la práctica humana, pero no tasas de biopsia
  innecesaria ni tiempos de triaje.
- **Los casos de fallo.** `informe/casos-de-fallo.md` documenta dos;
  todavía no son un conjunto de prueba propio.

Y uno que el proyecto no puede cerrar con sus datos: **cómo rinden los
modelos de imagen con fotos de teléfono.** Todos se midieron sobre los
recortes del sistema de fotografía corporal total, y el proyecto no tiene
fotos de teléfono con diagnóstico.

## Estructura del repositorio

- `CLAUDE.md` — bitácora de decisiones y contexto del proyecto
- `PLAN.md` — la ruta de trabajo: fases, condición de cierre y decisiones
- `.claude/skills/` — las seis carpetas de código, cada una con sus scripts y su SKILL.md
- `data/` — no versionado
- `outputs/` — salidas verificables: de aquí debe salir cada cifra del informe
- `referencias/` — fuentes citadas (texto, extracto o ficha, con su procedencia) y registros de búsqueda
- `informe/` — anteproyecto y su conversor a PDF, borrador del informe, casos de fallo y demo. La versión Word del borrador se genera a pedido y no se versiona
- `docs/` — copia de la demo publicada por GitHub Pages
- `actividad-fuentes/` — actividad «Nada sin fuente» del curso, con su propio índice

`docs/index.html` no se edita nunca a mano: lo escribe `generar_demo.py`
en la misma corrida que `informe/demo.html`, con el mismo contenido.

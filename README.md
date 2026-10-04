# Proyecto de consultoría ISIC 2024 — Detección de melanoma

**Estado: proyecto en curso.** Las cifras de este README se confirmaron
contra `outputs/` el 2026-10-02.

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

La demo ya usa las salidas de la Fase 4. El informe se está reescribiendo
en `informe/borrador-v2.md`; `informe/borrador.md` es la versión anterior a
la reserva de pacientes. La regla que gobierna el informe: ninguna cifra
existe si no está en un archivo de `outputs/`.

## Hallazgos principales hasta ahora

*(Cada cifra indica el archivo y campo de `outputs/` del que sale. Son
cifras del conjunto de desarrollo: el 20 % de los pacientes está reservado
y ningún modelo se ha evaluado sobre él desde que se reservó. Las
decisiones tomadas antes de reservarlo, con todos los datos, están
declaradas en el anteproyecto (`informe/anteproyecto.md`, sección 4.2),
salvo el diseño de las variables del ganador, que se declara más abajo. Las
comparaciones entre modelos usan validación cruzada agrupada por paciente,
repetida con 10 semillas —50 pliegues—, e intervalos al 95 % corregidos por
Nadeau y Bengio.)*

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
- **La implementación de la métrica se verificó contra el script oficial
  del organizador** —no contra una reimplementación propia ni de memoria—
  antes de confiar en ningún resultado de modelado
  (`modelado-baseline.json > metrica_fuente`; la ficha de la fuente, con su
  URL, en `referencias/isic-primary-metric-pauc.py.md`).

**▶ [Ver demo en vivo](https://diazesteban1001-sudo.github.io/proyecto-isic/)**
— cada cifra del texto muestra su origen al pasar el cursor: el archivo y
el campo de `outputs/`, o el archivo y la línea de la fuente.
Sus cifras son las del conjunto de desarrollo, como las de arriba; del
reservado solo da cómo se apartó, su tamaño y cuántas de sus imágenes
pasaron por el extractor, sin leer etiquetas, y no se ha abierto. El
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

## Qué falta

La ruta —qué fase sigue y qué condición la cierra— está en `PLAN.md`. Lo
que queda en ella:

- **Abrir el conjunto reservado, una sola vez**, con el modelo recomendado
  ya fijado en un commit anterior, y reportar el resultado con su
  intervalo, sea cual sea.
- **Terminar el informe** (`informe/borrador-v2.md`) y regenerar la demo
  cuando se abra el conjunto reservado.

Dos puntos de una versión anterior de este README están cubiertos solo en
parte, y todavía no tienen lugar en la ruta:

- **La línea base de la práctica clínica.** El anteproyecto (apartado 1)
  trae una medición de la práctica humana, pero no tasas de biopsia
  innecesaria ni tiempos de triaje.
- **Los casos de fallo.** `informe/casos-de-fallo.md` documenta dos;
  todavía no son un conjunto de prueba propio.

## Estructura del repositorio

- `CLAUDE.md` — bitácora de decisiones y contexto del proyecto
- `PLAN.md` — la ruta de trabajo: fases, condición de cierre y decisiones
- `.claude/skills/` — las seis carpetas de código, cada una con sus scripts y su SKILL.md
- `data/` — no versionado
- `outputs/` — salidas verificables: de aquí debe salir cada cifra del informe
- `referencias/` — fuentes citadas (texto, extracto o ficha, con su procedencia) y registros de búsqueda
- `informe/` — anteproyecto y su conversor a PDF, borrador del informe y su versión Word, casos de fallo y demo
- `docs/` — copia de la demo publicada por GitHub Pages
- `actividad-fuentes/` — actividad «Nada sin fuente» del curso, con su propio índice

`docs/index.html` no se edita nunca a mano: lo escribe `generar_demo.py`
en la misma corrida que `informe/demo.html`, con el mismo contenido.

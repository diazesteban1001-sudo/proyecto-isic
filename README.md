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

## Qué hace el sistema

Un único flujo orquestado en Claude Code, con cinco etapas, cada una con un rol:

| Skill | Función |
|---|---|
| `eda-diagnostico` | Perfila el dataset: tipos, faltantes, desbalance, estructura de grupos por paciente |
| `diseno-validacion` | Construye y audita la partición cruzada agrupada por paciente |
| `auditoria-de-fugas` | Chequeos estructurales + escaneo de columnas con señal univariada sospechosa |
| `modelado-baseline` | Entrena y evalúa niveles de referencia con la métrica oficial |
| `sintesis-consultoria` | Lee los cuatro reportes anteriores y redacta el informe final |

Las primeras cuatro miden y reportan; la última interpreta. Ningún
resultado del informe aparece si no está trazado hasta un archivo en
`outputs/`.

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
- **Mejor media no es mejor modelo, y una conclusión propia se retiró.** El
  boosting balanceado supera a la regresión logística balanceada por 0,005
  en promedio, pero el intervalo corregido va de −0,0145 a 0,0245
  (`validacion-repetida.json > comparacion_pareada_2b_menos_1.media` y
  `comparacion_pareada_2b_menos_1.intervalo_t_95_nadeau_bengio`). En una
  sola partición de los datos completos parecía, además, más estable. Con
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
- **La imagen no justifica su costo.** El modelo de imagen se eligió con
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
- **Modelo recomendado: la parte tabular de la solución ganadora del reto,
  reproducida y sin los dos sesgos conocidos que esa reproducción
  conservaba a su favor**: los hiperparámetros y las columnas descartadas,
  que su autor pudo elegir con todos los datos, y las transformaciones sin
  etiqueta, ajustadas también con las filas de validación. Supera al modelo
  con contexto de paciente en pAUC: +0,0181 [0,0021; 0,0341], mejor en 43
  de 50 pliegues
  (`fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.pauc`). En
  los ejes de triaje la diferencia no se distingue de cero: ni en
  sensibilidad top-15 ni en el número de lesiones que hay que revisar por
  cada maligna detectada al 80% de sensibilidad, NNT80% SE
  (`fase4-m3limpio-vs-m2.json > comparaciones_nuevo_menos_base.setop15` y
  `comparaciones_nuevo_menos_base.nnt80`). Predice con una mediana de
  0,0435 segundos por cada 1.000 lesiones
  (`tiempo-inferencia.json > tiempos.M3limpio`). La regla de recomendación
  se fijó antes de correr la comparación. Lo que esa limpieza no quita es
  el diseño de sus variables, que su autor fijó sin ningún conjunto
  reservado: el reservado de este proyecto no le es ajeno.
- **La implementación de la métrica se verificó contra el script oficial
  del organizador** —no contra una reimplementación propia ni de memoria—
  antes de confiar en ningún resultado de modelado
  (`modelado-baseline.json > metrica_fuente`; la ficha de la fuente, con su
  URL, en `referencias/isic-primary-metric-pauc.py.md`).

**▶ [Ver demo en vivo](https://diazesteban1001-sudo.github.io/proyecto-isic/)**
— cada cifra muestra su archivo y campo de origen al pasar el cursor.
**Sus cifras son anteriores a la reserva de pacientes:** salen de la
corrida sobre el 100 % de los datos, y desde entonces `outputs/` se
re-midió sobre el conjunto de desarrollo, así que ya no coinciden con las
de arriba. Lo mismo vale para el borrador del informe
(`informe/borrador.md`) y para `informe/casos-de-fallo.md`. Al cierre, la
demo se regenera y el borrador se reescribe.

La misma demo está en `informe/demo.html`: **autocontenida de verdad**
—datos y librería de gráficos empotrados, cero peticiones de red— así que
abre con doble clic desde una USB, sin servidor y sin conexión. Verificado
renderizándola con todo el tráfico bloqueado, no solo leyendo el código.
Las dos copias —esa y la publicada— las escribe `generar_demo.py` en la
misma corrida, así que no pueden desincronizarse.

## Cómo correrlo

```bash
# Requiere Claude Code y Python 3
git clone <url-del-repo>
cd proyecto-isic
claude   # lee CLAUDE.md automáticamente al arrancar
```

Los datos (`data/`) no están versionados — se descargan por separado
desde Kaggle (ver `CLAUDE.md` para el procedimiento).

## Qué falta

La ruta —qué fase sigue y qué condición la cierra— está en `PLAN.md`. Lo
que queda en ella:

- **Abrir el conjunto reservado, una sola vez**, con el modelo recomendado
  ya fijado en un commit anterior, y reportar el resultado con su
  intervalo, sea cual sea.
- **Reescribir el informe y regenerar la demo** desde `outputs/`, con la
  tabla final en los tres ejes que el cliente declaró: pAUC, sensibilidad
  top-15 por paciente y tiempo de inferencia.

Dos puntos de una versión anterior de este README están cubiertos solo en
parte, y todavía no tienen lugar en la ruta:

- **La línea base de la práctica clínica.** El anteproyecto (apartado 1)
  trae una medición de la práctica humana, pero no tasas de biopsia
  innecesaria ni tiempos de triaje.
- **Los casos de fallo.** `informe/casos-de-fallo.md` documenta dos;
  todavía no son un conjunto de prueba propio.

## Estructura del repositorio

```
├── CLAUDE.md              # bitácora de decisiones y contexto del proyecto
├── .claude/skills/         # las 5 skills
├── data/                   # no versionado
├── outputs/                # salidas verificables de cada skill
├── referencias/            # fuentes primarias citadas, versionadas
├── informe/                # borrador.md, informe-final.docx, demo.html
└── docs/                   # copia de la demo publicada por GitHub Pages
```

`docs/index.html` no se edita nunca a mano: lo escribe `generar_demo.py`
en la misma corrida que `informe/demo.html`, con el mismo contenido.

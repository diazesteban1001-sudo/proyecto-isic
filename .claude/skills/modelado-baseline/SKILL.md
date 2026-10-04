---
name: modelado-baseline
description: Entrena y evalúa tres niveles de baseline —referencia univariada, regresión logística balanceada, gradient boosting— usando la métrica oficial de la competencia (pAUC sobre 80% TPR) y la partición agrupada por paciente ya auditada. Úsala después de auditoria-de-fugas, nunca antes. Es un instrumento: entrena modelos y reporta su desempeño, pero no decide cuál "ganó" ni qué hacer a continuación.
---

# Modelado Baseline

Skill instrumento. A diferencia de las tres anteriores, esta sí entrena
modelos — pero solo para medir un piso de desempeño con la metodología
correcta, no para optimizar ni competir. No decide cuál nivel es "el
mejor" ni qué hacer después. Eso lo hace el agente al leer
`outputs/modelado-baseline.json`.

## Cuándo usarla

- Solo después de `auditoria-de-fugas`. Esta skill LEE
  `outputs/auditoria-de-fugas.json` para saber qué columnas excluir —
  solo en train, constantes, identificador y procedencia— y no vuelve a
  decidirlo por su cuenta. Si ese archivo no existe, falla
  con un mensaje explícito en vez de adivinar qué excluir.
- Usa el mismo esquema de partición que `diseno-validacion`
  (`--group-col`, `--n-splits`, `--seed` deben coincidir) para que los
  números sean comparables con el resto del proyecto.

## Por qué tres niveles, y qué es cada uno

**Nivel 0 — referencia univariada.** No se entrena nada. En cada fold,
y solo con las etiquetas del fold de **entrenamiento**, se elige la
columna numérica de mayor `max(AUC, 1 − AUC)` —el criterio de
`auditoria-de-fugas`— y su orientación, el signo de mayor pAUC. Esa
columna, imputada con la mediana de entrenamiento y con esa orientación,
es la puntuación sobre validación. Sirve como piso mínimo — cualquier
modelo combinado que apenas lo empate no está justificando su propia
complejidad. Solo columnas numéricas, porque una categórica habría que
codificarla.

*Hasta el 2026-09-25* la columna salía del reporte de fugas, calculado
sobre todos los folds, y la orientación se elegía en cada fold con las
etiquetas de validación, `max(pAUC(s), pAUC(−s))`. Esta sección decía que
la columna se usaba "cruda". Es la décima fila del registro de
incidentes de `CLAUDE.md`. El control positivo, con datos sintéticos en
los que entrenamiento y validación eligen distinto, es
`scripts/test_nivel0_en_entrenamiento.py`.

Se reportan **dos** números para este nivel, los dos medidos aquí sobre
validación: el AUC estándar (rango [0.5, 1]) y el pAUC (rango
[0.02, 0.2]). No son la misma escala y no se pueden
comparar entre sí. **Solo el pAUC es comparable con los niveles 1 y 2.**
Sin ese segundo número el `.md` invitaba a comparar 0.8053 contra 0.1331,
que es precisamente el error que la advertencia pretendía evitar.

Que ambos existan es informativo por sí solo: en la medición
exploratoria, sobre el 100 % de los datos y con la elección anterior,
`tbp_lv_H` recorría
el 61% del camino azar→perfecto en AUC estándar pero solo el 33.8% en
pAUC. Su señal no está donde la sensibilidad es clínicamente aceptable, y
eso solo se ve mirando la métrica del cliente.

**Nivel 1 — regresión logística balanceada.** El baseline estadístico
propiamente dicho: interpretable, con `class_weight="balanced"` porque
sin ajustar por el desbalance (393 positivos en 401,059 filas) el
modelo colapsa a predecir siempre negativo. Las features se estandarizan
con `StandardScaler` ajustado solo con el fold de entrenamiento: sin eso
—las escalas van de std 0.12 a std 408— la logística no converge dentro
de `max_iter` y el pAUC reportado sería el del optimizador detenido a
medio camino, no el del modelo. El nivel 2 no se escala: a un modelo de
árboles le da igual.

**Nivel 2 — gradient boosting, en dos variantes.** Cota superior realista
de lo que la metadata tabular puede lograr, sin tocar las imágenes. Usa
`HistGradientBoostingClassifier` de scikit-learn (ya está instalado,
maneja NaN nativamente). Se corre **dos veces**, y la única diferencia
entre las dos es `class_weight`:

- **2a — sin balancear** (`class_weight=None`). Se conserva aunque su pAUC
  quede *por debajo del piso aleatorio de la métrica* (ver
  `escala_de_referencia_pauc`). No es un fallo del script y no se borra. Por
  qué queda por debajo no se ha medido: es lo que dice su nota en el `.json`
  (`CLAUDE.md`, Pendientes, «El mecanismo del nivel 2a está sin medir»). *Hasta
  el 2026-10-03 este punto describía como hecho un mecanismo que nada en
  `outputs/` mide, con una cifra de la corrida sobre el 100 % de los datos.*
  Su AUC estándar, 0.582 en el conjunto de desarrollo
  (`auc_estandar_media`), lo pone por encima del azar de su escala, y el
  pAUC lo deja por debajo del de la suya: la métrica por defecto no es ciega
  al problema, y las dos discrepan sobre las mismas predicciones
  (`CLAUDE.md`, hallazgo 1). Es el hallazgo más citable de esta skill.
  *Hasta el 2026-10-02 decía: «Su AUC estándar (0.67) no deja ver el
  problema; el pAUC sí». El 0.67 era el AUC del primer fold en la corrida
  sobre el 100 % de los datos, no la media del modelo.*
- **2b — balanceado** (`class_weight="balanced"`). Mismo modelo, misma
  semilla, mismos folds.

Se conservan las dos porque el contraste es el resultado. Reportar solo
2b escondería que el desbalance no se manifiesta como "el modelo predice
siempre negativo" —el diagnóstico que uno espera— sino como confianza
máxima mal colocada, que es un modo de fallo distinto y peor.

No hay nivel 3. Añadir más modelos aquí es empezar a optimizar el
leaderboard, que no es el objetivo del proyecto — eso queda fuera del
alcance de esta skill a propósito.

## Sobre la métrica: VERIFICADA (2026-08-11)

`pauc_above_tpr()` es una transcripción del algoritmo oficial del
organizador (`p_auc_tpr`, Nicholas R. Kurtansky, MSKCC), cuya ficha, con
la URL del script, está versionada en
`referencias/isic-primary-metric-pauc.py.md`; el texto completo se guarda
solo en local, en `referencias/_texto-completo/upstream-PrimaryMetric-pAUC.py`.
Equivalencia comprobada numéricamente contra esa fuente en 200 casos
aleatorios (coincidencia exacta, atol 1e-12) más el caso del
clasificador perfecto, que devuelve 0.2 como debe. *Hasta el 2026-10-02
aquí decía «cuya copia literal está versionada»: la copia se redujo a ficha
el 2026-09-21, por la regla 3 de `CLAUDE.md`.*

**Procedencia de la verificación.** El notebook de Kaggle
`isic-pauc-abovetpr` NO es legible por el agente: como el resto de
Kaggle, devuelve solo el shell de JavaScript. Se verificó contra el
script del organizador en `raw.githubusercontent.com`, que sí es texto
plano. Ambos implementan el mismo algoritmo con `min_tpr` como
parámetro; difieren solo en su valor (Kaggle 0.80, premios ISIC 0.88).
Aquí se usa 0.80, la constante del proyecto.

**Qué estaba mal antes.** La versión inicial usaba
`roc_auc_score(..., max_fpr=0.2)` —AUC parcial corregido de McClish— y
lo reescalaba con `0.5*max_fpr² + (auc_scaled - 0.5)*max_fpr`. El
coeficiente correcto no es `max_fpr` sino `2*(max_fpr - 0.5*max_fpr²)`,
así que subestimaba por un factor de 0.556: un clasificador perfecto
daba 0.12 en vez de 0.2. El oficial no aplica la corrección de McClish
en absoluto — trunca la curva ROC en `max_fpr` interpolando el último
punto e integra el área cruda.

## Métricas de triaje: SEtop-15 y NNT80% SE (2026-09-25)

`scripts/metricas_triaje.py` implementa las dos métricas de triaje del cliente,
que acompañan al pAUC en la Fase 4.

- **SEtop-15**, verificada contra el guion del organizador
  (`referencias/isic-secondary-metric-topn.py.md`). Es la media, sobre los
  pacientes con alguna lesión maligna, de la fracción de sus malignas que caen
  entre sus 15 lesiones de mayor puntuación: el `raw_average_rank` del guion, con
  el mismo peso para cada paciente enfermo. El guion calcula además una
  sensibilidad con peso por lesión, que no es la del premio.
- **NNT80% SE**, según la definición de Kurtansky et al. 2025: *"the average
  number of lesions needed to triage to undergo expert evaluation to detect a
  single malignancy, using a threshold corresponding to a given sensitivity"*.
  El organizador no publica guion para esta métrica. La lectura operativa es
  nuestra: el umbral más alto con el que la sensibilidad llega al 80 %, y el NNT
  como lesiones marcadas entre malignas capturadas; con empates en el umbral,
  entran todas.

`scripts/test_metricas_triaje.py` tiene tres partes:
- casos con el valor calculado a mano;
- un control positivo: seis mutantes, cada uno un error plausible, y cada uno
  detectado por al menos un caso;
- la SEtop-15 frente al guion oficial, ejecutado sin modificar.

El guion es de 2024 y necesita pandas < 3; el intérprete se indica con
`PYTHON_GUION_ISIC` (versiones en `requisitos-interprete-2024.txt`). En la verificación del 2026-09-25 coincidió en seis
conjuntos sintéticos con empates, con pandas 2.3.3.

## Contexto de paciente, las variables de M2 (2026-09-25)

`scripts/contexto_paciente.py` calcula las variables con que M2 compara cada
lesión con las demás de su paciente (`PLAN.md`, Fase 4). Sigue la solución
ganadora (`referencias/novoselskiy-2024-isic2024/notebooks/top-model.ipynb`):

- el z-score dentro del paciente de cada una de las 34 variables numéricas de
  M1 (celda 7);
- el conteo de lesiones y las sumas de área del paciente, total y por zona
  anatómica (celda 7);
- el LOF por paciente con sus 17 variables, repeticiones incluidas, y
  `n_neighbors=min(n, 30)`; con menos de 3 lesiones vale −1 (celdas 10 y 11).

**Una desviación, declarada:** el ganador estandariza e imputa las variables
del LOF con todas las filas; aquí se hace dentro de cada paciente. **No usan
etiquetas y cada una se calcula con las lesiones de un solo paciente**, así que,
con los pliegues agrupados por paciente, no hay fuga entre pliegues. Se calculan
una vez y valen para todos los pliegues.

`scripts/test_contexto_paciente.py` comprueba:
- los valores calculados a mano;
- que barajar las etiquetas no cambia ninguna variable, en datos sintéticos y en
  el conjunto de desarrollo real, y que una variante con fuga sí cambia;
- que cambiar un paciente no cambia las variables de otro;
- que coinciden con `read_data` y `get_lof_score` del ganador, ejecutados sin
  modificar.

Esa última comprobación necesita el intérprete de 2024 de
`requisitos-interprete-2024.txt`, indicado con `PYTHON_GUION_ISIC`.

## M3, la parte tabular del ganador (2026-09-26)

`scripts/ganador_m3.py` reproduce en el entorno actual la parte tabular de la
solución ganadora, con la especificación fijada en `PLAN.md`, Fase 4. Las listas
de variables no se transcriben: se leen del notebook versionado, después de
comprobar su SHA-256.

- **Las variables:** 217 en el conjunto de desarrollo. Son las de las celdas 7,
  8, 10, 13, 18 y 19, sin las de imagen, sin `attribution` y sin las
  descartadas en la celda 24. La imputación, el one-hot, el estandarizado del
  LOF, el k-means y las medias por conglomerado se ajustan sobre todo el
  conjunto de desarrollo, como se publicó. **No leen la etiqueta, pero las
  variables de un paciente dependen de los demás.**
- **El ajuste:** el CatBoost y el remuestreo publicados, en CPU. El número de
  árboles se elige sobre un 20 % interno del pliegue de entrenamiento, nunca
  con el de validación.

`scripts/test_ganador_m3.py` comprueba:
- las listas y los parámetros, contra el notebook;
- que las 217 variables, los conglomerados y el LOF coinciden con el código
  del ganador, ejecutado en el intérprete de 2024 sobre el conjunto de
  desarrollo con los parches de la especificación;
- que las columnas repetidas del LOF pesan doble, con dos variantes que la
  comprobación tiene que detectar;
- que barajar las etiquetas de validación no cambia el ajuste, mientras que con
  el ajuste publicado sí cambia.

Necesita el intérprete de 2024 (`requisitos-interprete-2024.txt`, indicado con
`PYTHON_GUION_ISIC`), y en `.venv` catboost 1.2.8 e imbalanced-learn 0.14.2.

**M3 limpio** (`PLAN.md`, Fase 4, fijado el 2026-09-26) es M3 con tres cambios:
- `variables_m3_en_pliegue` ajusta la imputación, el one-hot, el estandarizado,
  el k-means y las medias por conglomerado solo con el pliegue de entrenamiento,
  y los aplica a su validación;
- no descarta las 22 columnas de la celda 24;
- `ajustar_m3` con `PARAMETROS_LIMPIO` conserva la parada de M3 y deja el resto
  del constructor de CatBoost por defecto.

Como el one-hot se ajusta con el entrenamiento, una categoría que solo aparece
en la validación no tiene columna, y ese pliegue queda con menos de 239
variables.

`scripts/test_m3_limpio.py`, con datos sintéticos, comprueba:
- que cambiar las demás filas de validación no cambia el entrenamiento ni a un
  paciente de validación, mientras que con M3 sí cambian;
- que el lado de entrenamiento coincide con el M3 verificado;
- que las 22 columnas no dependen de las que excluye el proyecto. Esto lo
  comprueba también sobre una muestra real de desarrollo;
- que el ajuste usa los valores por defecto y no ve las etiquetas de
  validación.

## Comparaciones de la Fase 4 (2026-09-25)

`scripts/fase4_comparar.py` hace una comparación principal de la Fase 4
(`PLAN.md`), nuevo − base, con validación repetida sobre los mismos folds de
desarrollo y los hiperparámetros de 2b, sin ajuste:

- **M1:** el nivel 2b.
- **M2:** M1 más el contexto de paciente.
- **M4:** M2 más las 384 variables de DINOv2 ViT-S/14. Se leen con el cargador
  protegido, que no lee las del reservado. Se alinean por `isic_id`, y el script
  se detiene si alguna fila no casa, si hay faltantes o si el hash del archivo
  no es el de `outputs/extraccion-imagen.json`.

- **M4b, variante secundaria:** M2 más dos variables de imagen apiladas, de
  `scripts/apilado_imagen.py`: la puntuación de una logística balanceada sobre
  las 384 variables y su razón a la media del paciente. Se rehacen en cada fold:
  fuera de pliegue en entrenamiento, con una validación interna agrupada por
  paciente, y con el modelo del fold en validación. El control de fuga,
  `scripts/test_apilado_imagen.py`, comprueba con datos sintéticos que barajar
  las etiquetas de validación no cambia ninguna puntuación y que ninguna fila,
  ni ningún paciente, se puntúa con un modelo que lo vio. Cada comprobación
  detecta el mutante hecho para incumplirla.
- **M3, desde el 2026-09-26:** la parte tabular reproducida del ganador, de
  `scripts/ganador_m3.py`. No usa los hiperparámetros de 2b sino los
  publicados, con los parches de la especificación. Sus variables se calculan
  una vez; el ajuste, en cada fold, con el número de árboles elegido dentro del
  pliegue de entrenamiento. Se registran los árboles de cada ajuste.
- **M3 limpio, desde el 2026-09-26:** sus variables se arman en cada fold. Se
  registran los árboles, las iteraciones corridas y la tasa de aprendizaje que
  elige CatBoost en cada ajuste.

Por modelo mide pAUC, AUC, SEtop-15 y NNT80% SE, y el tiempo de entrenamiento
por fold. Para cada métrica da nuevo − base con intervalo ingenuo y corregido, y
victorias en la dirección de la métrica. Con `--referencia` comprueba que el
modelo base reproduce fold a fold una corrida anterior. Hasta el 2026-09-25 se
llamaba `fase4_m2_vs_m1.py` y solo hacía M2 − M1.

## Tiempo de inferencia (2026-09-27)

`scripts/tiempo_inferencia.py` mide el tiempo de inferencia de M1, M2, M3 limpio,
M4 y M4b con la especificación fijada en `PLAN.md`, Fase 4, y su enmienda.
- **El subconjunto:** pacientes completos de desarrollo, barajados con semilla
  7, hasta 5.000 lesiones o más.
- **El entrenamiento:** una vez, con los demás pacientes de desarrollo, fuera
  del cronómetro.
- **Lo que se cronometra:** el camino desde los metadatos del subconjunto, y en
  M4 y M4b desde las imágenes de `data/train-image.hdf5`, hasta la puntuación.
  Ese camino tiene su propia implementación, que aplica las transformaciones ya
  ajustadas.

Antes de cronometrar compara ese camino con el de la Fase 4, con el mismo modelo:
- en M1, M2 y M3 limpio, igualdad exacta;
- en M4 y M4b, DINOv2 a 1e-3 como máximo del archivo de la extracción, e
  igualdad exacta con las variables de ese archivo.

Después quita cada paso, uno por vez, y exige que la comprobación falle. Para
la imputación compara la matriz que entra al modelo. Si algo falla, no
cronometra. Cinco repeticiones por modelo, en segundos por 1.000 lesiones.

## El mecanismo del 2a (2026-10-04)

`scripts/mecanismo_2a.py` mide cómo se reparten, sobre validación, las
probabilidades que predicen el 2a y, como control, el 2b. Usa la partición
de la semilla 42 y los mismos modelos, columnas y codificación que
`train_and_evaluate.py`, importados de ese script. Por pliegue y en total
reporta:
- el número de valores distintos de la probabilidad;
- la fracción de negativos y de positivos con probabilidad ≥ 0,999 y con la
  probabilidad máxima;
- el rango percentil medio de los positivos (`rango_medio_pos`, en escala
  0–1);
- la fracción de negativos por encima de la mediana de los positivos;
- la pAUC.

**Control:** la pAUC de cada pliegue, del 2a y del 2b, tiene que coincidir
con `outputs/modelado-baseline.json`; si no, se detiene sin escribir.
`scripts/test_mecanismo_2a.py` fuerza las medidas con un caso que satura
sobre los negativos y otro que no, y el control con una referencia alterada.
Salida: `outputs/mecanismo-2a.json` y `.md`.

```bash
.venv/bin/python .claude/skills/modelado-baseline/scripts/mecanismo_2a.py \
  --data data/train-metadata.csv --group-col patient_id --target-col target \
  --n-splits 5 --seed 42 --leakage-report outputs/auditoria-de-fugas.json \
  --referencia outputs/modelado-baseline.json --out outputs/mecanismo-2a
```

## El efecto de la partición (2026-10-04)

`scripts/efecto_particion.py` corre el nivel 1 y el 2b con la configuración
de `evaluar_repetido.py`, importada de él, en dos particiones del conjunto de
desarrollo: la de siempre, agrupada por paciente, y una por filas
(`StratifiedKFold`, sin agrupar). En las dos usa 5 pliegues y semillas de la 0
a la 9. Por partición reporta:
- las cuatro métricas de cada nivel, en media global y por semilla;
- la diferencia 2b − 1 en cada métrica, con el intervalo corregido de Nadeau y
  Bengio;
- por nivel y métrica, la diferencia de medias filas − paciente y en cuántas
  semillas la de filas es mayor y en cuántas es mejor (en el NNT80% SE, menor).

**Control:** la partición por paciente tiene que reproducir
`outputs/validacion-repetida.json` pliegue a pliegue en los niveles 1 y 2b; se
comprueba antes de correr la otra, y si no coincide se detiene sin escribir.
`scripts/test_efecto_particion.py` lo fuerza con una referencia alterada, y
comprueba la medida con dos conjuntos sintéticos: uno con efecto de sujeto,
donde la partición por filas tiene que dar más, y otro sin él. La
especificación y la regla de lectura son de la persona, fijadas antes de
correr (`PLAN.md`, Fase 6); el script no las aplica. Salida:
`outputs/efecto-particion.json` y `.md`.

```bash
.venv/bin/python .claude/skills/modelado-baseline/scripts/efecto_particion.py \
  --data data/train-metadata.csv --group-col patient_id --target-col target \
  --leakage-report outputs/auditoria-de-fugas.json \
  --referencia outputs/validacion-repetida.json --out outputs/efecto-particion
```

## Cómo correrlo

```bash
python .claude/skills/modelado-baseline/scripts/train_and_evaluate.py \
  --data data/train-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --n-splits 5 \
  --seed 42 \
  --leakage-report outputs/auditoria-de-fugas.json \
  --out outputs/modelado-baseline
```

**Solo lee el conjunto de desarrollo.** El CSV se carga con
`diseno-validacion/scripts/datos_desarrollo.py`, que excluye los pacientes
de `outputs/holdout-pacientes.json` (`--holdout`, por defecto esa ruta). Si
ese archivo no existe, el script falla con un mensaje explícito antes de
leer los datos. Lo mismo vale para `evaluar_repetido.py`. Los dos JSON de salida lo declaran en su campo `datos`.

**Análisis de sensibilidad de las columnas de procedencia.** Con
`--incluir-procedencia`, las columnas de procedencia del reporte de fugas
(`attribution`, `copyright_license`) quedan dentro del modelo, sobre las
mismas particiones de desarrollo. La salida va a su propio archivo,
`outputs/sensibilidad-procedencia.json` y `.md`, con un bloque
`sensibilidad` que lo declara: no sustituye a la corrida principal ni se
usa para elegir nada. El script se niega a escribir con esa opción sobre
`outputs/modelado-baseline`.

```bash
python .claude/skills/modelado-baseline/scripts/train_and_evaluate.py \
  --data data/train-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --n-splits 5 \
  --seed 42 \
  --leakage-report outputs/auditoria-de-fugas.json \
  --out outputs/sensibilidad-procedencia \
  --incluir-procedencia
```

La misma sensibilidad con validación repetida la hace
`scripts/sensibilidad_repetida.py`, que escribe
`outputs/sensibilidad-procedencia-repetida.json` y `.md` y nunca
`validacion-repetida.*`. Corre las dos configuraciones, sin y con
procedencia, sobre los mismos folds, construidos una vez por semilla, y
guarda su huella SHA-256. Comprueba que la configuración sin procedencia
reproduce fold a fold `outputs/validacion-repetida.json`. Reporta tres
comparaciones pareadas, con intervalo ingenuo y corregido por Nadeau y
Bengio y victorias por fold y por semilla: 2b − 1 con procedencia, junto
al de sin procedencia; 2b con menos 2b sin; y 1 con menos 1 sin.

```bash
python .claude/skills/modelado-baseline/scripts/sensibilidad_repetida.py \
  --data data/train-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --n-splits 5 \
  --leakage-report outputs/auditoria-de-fugas.json \
  --referencia outputs/validacion-repetida.json \
  --out outputs/sensibilidad-procedencia-repetida \
  --semillas 0 1 2 3 4 5 6 7 8 9
```

## Contrato de salida

- `outputs/modelado-baseline.json` — resultados completos por nivel y fold.
- `outputs/modelado-baseline.md` — resumen legible, máximo 15 líneas.
  Son 12 fijas: una por nivel, sin ningún bucle sobre folds, así que no
  crece con `--n-splits` (verificado con 2 y 5). El detalle fold a fold
  vive en el `.json` — lección aprendida de `diseno-validacion`.

### Campos del JSON

```
{
  "datos": {"archivo": str, "conjunto": "desarrollo", "sin_los_pacientes_de": str},
  "esquema_cv": {"group_col": str, "n_splits": int, "seed": int},
  "metrica": "pAUC sobre 80% TPR, rango [0, 0.2]",
  "metrica_verificada_contra_fuente_oficial": true,
  "metrica_fuente": str,
  "columnas_excluidas": [str, ...],
  "n_features_usadas": int,
  "features_usadas": [str, ...],
  "nivel_0_referencia_univariada": {
    "criterio": str,
    "columna_por_fold": [str, ...], "orientacion_por_fold": [1 | -1, ...],
    "pauc_por_fold": [float, ...], "pauc_media": float, "pauc_std": float,
    "auc_estandar_por_fold": [float, ...], "auc_estandar_media": float,
    "nota": str
  },
  "nivel_1_regresion_logistica": {
    "pauc_por_fold": [float, ...],
    "pauc_media": float, "pauc_std": float
  },
  "nivel_2a_gradient_boosting_sin_balancear": {
    "modelo": str, "pauc_por_fold": [float, ...],
    "pauc_media": float, "pauc_std": float, "nota": str
  },
  "nivel_2b_gradient_boosting_balanceado": {
    "modelo": str, "pauc_por_fold": [float, ...],
    "pauc_media": float, "pauc_std": float, "nota": str
  },
  "escala_de_referencia_pauc": {
    "azar": float, "maximo": float, "nota": str
  }
}
```

`escala_de_referencia_pauc` existe para que nadie tenga que recordar que
el azar en esta métrica es 0.02 y no 0. El `.md` la usa para expresar
cada nivel como porcentaje del recorrido azar→perfecto, que es la única
forma honesta de decir "este modelo es mejor que aquel" cuando el rango
útil de la métrica no empieza en cero.

## No interpretes aquí

- "El nivel 2b ganó, es el mejor modelo" → el agente decide si la
  diferencia justifica la complejidad adicional, considerando
  interpretabilidad y el argumento clínico de la tesis.
- "El nivel 2a demuestra que el gradient boosting no sirve aquí" → lo
  que muestra es qué pasa sin ajustar por el desbalance, con
  hiperparámetros por defecto y sin tocar las imágenes. Generalizar eso
  a la familia de modelos es del agente, y probablemente sea falso.
- "Con esto ya se puede pasar a producción" → fuera del alcance total
  de este proyecto y de esta skill.
- "El desempeño es (in)suficiente" → sin una referencia externa (no
  hay leaderboard privado accesible), esa valoración la hace el
  agente comparando contra la literatura, no esta skill.

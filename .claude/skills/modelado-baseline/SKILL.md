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

- **2a — sin balancear** (`class_weight=None`). En ISIC da pAUC ≈ 0.0013,
  *por debajo del piso aleatorio de la métrica* (0.02). No es un fallo del
  script y no se borra: con 0.098% de positivos el modelo satura en
  probabilidad 1.0 sobre un puñado de negativos y los coloca por encima de
  los positivos reales, destruyendo justo la región de sensibilidad alta
  que el pAUC mide. Su AUC estándar (0.67) no deja ver el problema; el
  pAUC sí. Es el hallazgo más citable de esta skill.
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
organizador (`p_auc_tpr`, Nicholas R. Kurtansky, MSKCC), cuya copia
literal está versionada en `referencias/isic-primary-metric-pauc.py.md`.
Equivalencia comprobada numéricamente contra esa fuente en 200 casos
aleatorios (coincidencia exacta, atol 1e-12) más el caso del
clasificador perfecto, que devuelve 0.2 como debe.

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

Por modelo mide pAUC, AUC, SEtop-15 y NNT80% SE, y el tiempo de entrenamiento
por fold. Para cada métrica da nuevo − base con intervalo ingenuo y corregido, y
victorias en la dirección de la métrica. Con `--referencia` comprueba que el
modelo base reproduce fold a fold una corrida anterior. Hasta el 2026-09-25 se
llamaba `fase4_m2_vs_m1.py` y solo hacía M2 − M1.

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

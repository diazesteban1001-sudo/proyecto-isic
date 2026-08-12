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
  no vuelve a decidirlo por su cuenta. Si ese archivo no existe, falla
  con un mensaje explícito en vez de adivinar qué excluir.
- Usa el mismo esquema de partición que `diseno-validacion`
  (`--group-col`, `--n-splits`, `--seed` deben coincidir) para que los
  números sean comparables con el resto del proyecto.

## Por qué tres niveles, y qué es cada uno

**Nivel 0 — referencia univariada.** No se entrena nada: se toma la
columna con mayor AUC individual ya calculada por `auditoria-de-fugas`
(en ISIC, `tbp_lv_H` con AUC ≈ 0.80) y se usa cruda como predictor,
imputada con la mediana del fold de entrenamiento. Sirve como piso
mínimo — cualquier modelo combinado que apenas lo empate no está
justificando su propia complejidad.

Se reportan **dos** números para este nivel: el AUC estándar que viene
del reporte de fugas (rango [0.5, 1]) y el pAUC calculado aquí sobre los
mismos folds (rango [0.02, 0.2]). No son la misma escala y no se pueden
comparar entre sí. **Solo el pAUC es comparable con los niveles 1 y 2.**
Sin ese segundo número el `.md` invitaba a comparar 0.8053 contra 0.1331,
que es precisamente el error que la advertencia pretendía evitar.

Que ambos existan es informativo por sí solo: en ISIC, `tbp_lv_H` recorre
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

## Contrato de salida

- `outputs/modelado-baseline.json` — resultados completos por nivel y fold.
- `outputs/modelado-baseline.md` — resumen legible, máximo 15 líneas.
  Son 12 fijas: una por nivel, sin ningún bucle sobre folds, así que no
  crece con `--n-splits` (verificado con 2 y 5). El detalle fold a fold
  vive en el `.json` — lección aprendida de `diseno-validacion`.

### Campos del JSON

```
{
  "esquema_cv": {"group_col": str, "n_splits": int, "seed": int},
  "metrica": "pAUC sobre 80% TPR, rango [0, 0.2]",
  "metrica_verificada_contra_fuente_oficial": true,
  "metrica_fuente": str,
  "columnas_excluidas": [str, ...],
  "n_features_usadas": int,
  "nivel_0_referencia_univariada": {
    "columna": str, "auc_estandar": float,
    "pauc_por_fold": [float, ...], "pauc_media": float, "pauc_std": float,
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

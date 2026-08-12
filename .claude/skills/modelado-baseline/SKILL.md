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

**Nivel 0 — referencia univariada.** No se re-entrena nada: se toma la
columna con mayor AUC individual ya calculada por `auditoria-de-fugas`
(en ISIC, `tbp_lv_H` con AUC ≈ 0.80). Sirve como piso mínimo — cualquier
modelo combinado que apenas lo empate no está justificando su propia
complejidad. Importante: ese número es AUC estándar (rango [0,1]), NO
pAUC (rango [0, 0.2]). No son comparables en la misma escala; se
reportan por separado, con la advertencia explícita.

**Nivel 1 — regresión logística balanceada.** El baseline estadístico
propiamente dicho: interpretable, con `class_weight="balanced"` porque
sin ajustar por el desbalance (393 positivos en 401,059 filas) el
modelo colapsa a predecir siempre negativo.

**Nivel 2 — gradient boosting.** Cota superior realista de lo que la
metadata tabular puede lograr, sin tocar las imágenes. Usa
`HistGradientBoostingClassifier` de scikit-learn por defecto (ya está
instalado, maneja NaN nativamente); si LightGBM está disponible se
puede usar en su lugar, pero no es una dependencia nueva obligatoria.

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
- `outputs/modelado-baseline.md` — resumen legible, máximo 15 líneas
  (fijas por diseño: no crece con `--n-splits`, los folds se resumen
  como min/max/media, no uno por línea — lección aprendida de
  diseno-validacion).

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
    "nota": "AUC estándar, NO pAUC — no comparable directamente con niveles 1 y 2"
  },
  "nivel_1_regresion_logistica": {
    "pauc_por_fold": [float, ...],
    "pauc_media": float, "pauc_std": float
  },
  "nivel_2_gradient_boosting": {
    "modelo": "HistGradientBoostingClassifier" | "LightGBM",
    "pauc_por_fold": [float, ...],
    "pauc_media": float, "pauc_std": float
  }
}
```

## No interpretes aquí

- "El nivel 2 ganó, es el mejor modelo" → el agente decide si la
  diferencia justifica la complejidad adicional, considerando
  interpretabilidad y el argumento clínico de la tesis.
- "Con esto ya se puede pasar a producción" → fuera del alcance total
  de este proyecto y de esta skill.
- "El desempeño es (in)suficiente" → sin una referencia externa (no
  hay leaderboard privado accesible), esa valoración la hace el
  agente comparando contra la literatura, no esta skill.

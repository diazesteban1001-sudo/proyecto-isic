# ISIC-Research/Challenge-2024-Metrics — `PrimaryMetric-pAUC.py` (FICHA)

**Qué es:** la implementación de referencia del pAUC del organizador, función
`p_auc_tpr`. Autor declarado en el propio archivo: *(c) 2024 Nicholas R
Kurtansky, MSKCC*.
**URL:** https://github.com/ISIC-Research/Challenge-2024-Metrics/blob/main/PrimaryMetric-pAUC.py
(en crudo: https://raw.githubusercontent.com/ISIC-Research/Challenge-2024-Metrics/main/PrimaryMetric-pAUC.py)
**Fecha de consulta:** 2026-08-11. Contrastado de nuevo el 2026-09-21: el
script no cambió.

**LICENCIA: ninguna → FICHA.** Mismo repositorio que el README, **sin archivo
de licencia** (API de GitHub: `license: null`; `/license` responde 404). Sin
licencia rige el copyright por defecto. Verificado el 2026-09-21.

**Texto completo:** en local,
`referencias/_texto-completo/upstream-PrimaryMetric-pAUC.py` (el script tal cual,
61 líneas) y `referencias/_texto-completo/isic-primary-metric-pauc.py.md` (la
copia que estuvo versionada hasta el 2026-09-21).

**Por qué está aquí:** el *notebook* oficial de Kaggle no es legible por el
agente. Este script es la implementación de referencia, y contra él se verificó
la del proyecto (`modelado-baseline/scripts/train_and_evaluate.py`), incluida la
corrección del factor 0,556 que documenta `modelado-baseline/SKILL.md`.

---

## ⚠️ Cómo leer los números de línea

**Los números de esta ficha son los del script original**, que no cambian con
nuestras cabeceras. Hasta el 2026-09-21 este archivo era una copia literal con
12 líneas de cabecera delante, y **algunas citas del repositorio se escribieron
con la numeración de esa copia**. La equivalencia es exacta —se comprobó que la
copia era idéntica al original byte a byte a partir de su línea 13—:

**línea del original = línea de la copia vieja − 12**

La última columna de la tabla de abajo da la numeración vieja, para que esas
citas sigan resolviendo.

## Líneas literales que el proyecto usa

| Original | Copia vieja | Código | Para qué la usa el proyecto |
|---|---|---|---|
| 24 | 36 | `def p_auc_tpr(v_gt, v_pred, min_tpr=None, sample_weight=None):` | el umbral es un **parámetro** sin valor por defecto (`CLAUDE.md`, "Sobre el problema") |
| 35 | 47 | `    if len(np.unique(v_gt)) != 2:` | un fold sin positivos hace la métrica indefinida (`CLAUDE.md`, "Segunda nota metodológica") |
| 36 | 48 | `        raise ValueError(` | ídem |
| 37 | 49 | `            "Only one class present in y_true. ROC AUC score "` | ídem |
| 42 | 54 | `    v_gt = abs(np.asarray(v_gt)-1)` | **inversión de etiquetas**: por ella la restricción sobre el TPR es directa (`CLAUDE.md`, regla 6, fila 7; `referencias/yang-2019-two-way-partial-auc.md`) |
| 43 | 55 | `    v_pred = abs(np.asarray(v_pred)-1)` | ídem, sobre los puntajes |
| 44 | 56 | `    max_fpr = abs(1-min_tpr)` | el tope se deriva del umbral de sensibilidad |
| 47 | 59 | `    fpr, tpr, _ = sklean.roc_curve(v_gt, v_pred, sample_weight=sample_weight)` | ROC **sobre las etiquetas ya invertidas** |
| 54 | 66 | `    stop = np.searchsorted(fpr, max_fpr, "right")` | truncamiento en el eje `fpr` invertido |
| 58 | 70 | `    fpr = np.append(fpr[:stop], max_fpr)` | ídem |
| 59 | 71 | `    partial_auc = sklean.auc(fpr, tpr)` | integra el área **cruda**, sin la corrección de McClish (`modelado-baseline/SKILL.md`) |

*`sklean` es así en el original —alias de `sklearn.metrics`, línea 21—; no es
errata nuestra.*

## Localizadores del resto — sin texto

- Líneas 1–14: docstring del módulo — propósito, enlace a Wikipedia, autoría.
- Líneas 25–34: docstring de la función. Documenta el retorno como *"Float
  value range [0, 1]"*, pero con `min_tpr = 0.80` el máximo real es 0,2.
- Líneas 48–51: casos límite — `max_fpr` igual a 1 devuelve el AUC completo; un
  `min_tpr` fuera de rango lanza `ValueError`.
- Líneas 55–57: interpolación lineal del punto en `max_fpr`.

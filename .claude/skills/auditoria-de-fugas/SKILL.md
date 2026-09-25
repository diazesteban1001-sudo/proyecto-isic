---
name: auditoria-de-fugas
description: Agente adversario que busca data leakage antes de que ningún modelo se entrene en serio. Combina chequeos estructurales (columnas ausentes en test, constantes, redundantes) con un escaneo univariado de AUC fuera-de-muestra usando partición agrupada — para detectar columnas que predicen el target casi perfectamente por sí solas sin ser obviamente un identificador. Úsala siempre después de eda-diagnostico y diseno-validacion, y siempre antes de confiar en cualquier resultado de modelado-baseline. No es un baseline: no combina columnas, no ajusta hiperparámetros, no compara modelos.
---

# Auditoría de Fugas

Skill instrumento, con una particularidad: parte de su trabajo es señalar
preguntas que no puede responder por sí sola —como el origen de una
columna ambigua— y dejarlas explícitas para que el agente las investigue.
No decide qué hacer con lo que encuentra. Eso lo hace el agente al leer
`outputs/auditoria-de-fugas.json`.

## Cuándo usarla

- Después de `eda-diagnostico` (necesita saber tipos, faltantes y
  columnas exclusivas de train).
- Después de `diseno-validacion` (usa el mismo esquema de partición
  agrupada para que el propio chequeo no tenga la fuga que busca
  detectar).
- Antes de que `modelado-baseline` entrene nada en serio. Ningún
  resultado de modelado se reporta sin haber corrido esta auditoría
  primero.

## Qué hace

### 1. Chequeos estructurales

- Columnas presentes en train y ausentes en test (fuga por construcción:
  no van a estar disponibles al predecir).
- Columnas constantes (sin valor informativo, no es fuga pero se reporta
  junto por conveniencia operativa).
- Columnas con cardinalidad igual al número de filas (identificadores,
  candidatas obvias a excluir de cualquier modelo).
- Cualquier columna cuyo nombre sugiera derivación posterior al evento
  objetivo (ej. contiene "confidence", "score", "pred", "diagnosis")
  se marca para revisión manual — el nombre no basta para confirmar
  fuga, así que esto es una señal, no una conclusión.
- **Columnas de procedencia** (`attribution`, `copyright_license`):
  describen el centro y la licencia de la imagen, no la lesión, y en un
  centro nuevo no aportan información. No es un hallazgo del script: es
  una decisión de la persona (`PLAN.md`, Fase 1, 2026-09-25), escrita en
  `COLUMNAS_PROCEDENCIA`. El script la aplica a las que existan y la
  escribe en el JSON con su motivo, para que `modelado-baseline` las
  excluya como excluye las demás. Siguen en el escaneo univariado: se
  excluyen de los modelos, no de la auditoría. Control positivo:
  `scripts/test_columnas_procedencia.py`.

### 2. Escaneo univariado de AUC fuera de muestra

Para cada columna que sobrevive los chequeos estructurales (no es ID,
no es el target, no es la columna de grupo):

- Si es numérica: usa el valor crudo (imputado con la mediana de train
  dentro de cada fold) como predictor directo.
- Si es categórica: usa codificación de medias ajustada dentro de cada
  fold de entrenamiento y aplicada al fold de validación (nunca al revés).
- Calcula AUC fuera de muestra con la MISMA partición agrupada por
  paciente que usó `diseno-validacion` — nunca una partición ingenua,
  porque eso metería en el detector la misma fuga que busca encontrar.
- Marca como sospechosa cualquier columna cuyo AUC supere el umbral
  (por defecto 0.90 — una sola columna prediciendo eso bien sola es
  atípico y merece revisión, no es evidencia final de fuga).

Esto NO es `modelado-baseline`: una columna a la vez, sin combinar
features, sin ajustar ningún hiperparámetro, sin comparar familias de
modelos. Es un detector de humo, no un modelo candidato.

## Cómo correrlo

```bash
python .claude/skills/auditoria-de-fugas/scripts/audit_leakage.py \
  --train data/train-metadata.csv \
  --test data/test-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --n-splits 5 \
  --seed 42 \
  --auc-threshold 0.90 \
  --out outputs/auditoria-de-fugas
```

**Solo lee el conjunto de desarrollo.** El CSV se carga con
`diseno-validacion/scripts/datos_desarrollo.py`, que excluye los pacientes
de `outputs/holdout-pacientes.json` (`--holdout`, por defecto esa ruta). Si
ese archivo no existe, el script falla con un mensaje explícito antes de
leer los datos. El JSON de salida lo declara en su campo `datos`.

Los parámetros de partición (`--group-col`, `--n-splits`, `--seed`) deben
coincidir con los que usó `diseno-validacion`, para que ambas skills midan
sobre el mismo esquema.

## Contrato de salida

- `outputs/auditoria-de-fugas.json` — hallazgos completos.
- `outputs/auditoria-de-fugas.md` — resumen legible, máximo 15 líneas.

El `.md` acota cada bloque de detalle a 3 entradas (columnas sospechosas y
preguntas abiertas), seguidas de una línea "... y N más". Así el límite de 15
líneas se respeta con cualquier número de hallazgos. El listado completo vive
en el `.json`.

### Campos del JSON

```
{
  "datos": {"archivo": str, "conjunto": "desarrollo", "sin_los_pacientes_de": str},
  "esquema_cv": {"group_col": str, "n_splits": int, "seed": int},
  "columnas_solo_en_train": [str, ...],
  "columnas_constantes": [str, ...],
  "columnas_identificador": [str, ...],
  "columnas_procedencia": [str, ...],
  "motivo_columnas_procedencia": str,
  "columnas_nombre_sospechoso": [str, ...],
  "umbral_auc_sospechoso": float,
  "univariado": [
    {
      "columna": str,
      "tipo": "numerica" | "categorica",
      "auc_oof": float,
      "n_faltantes": int,
      "sospechosa": bool
    }, ...
  ],
  "preguntas_abiertas": [
    {"columna": str, "pregunta": str}, ...
  ]
}
```

`preguntas_abiertas` es el campo distintivo de esta skill: para columnas
donde el nombre es sospechoso pero la ausencia en test no se explica
por post-procesamiento obvio (ej. una columna que no es claramente
post-biopsia pero tampoco está en test), el script no adivina la
respuesta — la deja como pregunta explícita.

## No interpretes aquí

- "Esta columna definitivamente tiene fuga" → un AUC alto es una señal,
  no una prueba; el agente decide tras investigar el origen de la columna.
- "Por lo tanto excluye estas 5 columnas del modelo" → esa decisión la
  toma el agente junto con `modelado-baseline`, con el reporte completo
  como evidencia.
- "El umbral 0.90 es el correcto para este proyecto" → es un valor por
  defecto razonable, no una verdad fija; el agente puede pedir que se
  recorra con otro umbral si el resultado lo amerita.

---
name: diseno-validacion
description: Propone y VERIFICA el esquema de validación cruzada para un dataset agrupado (ej. por paciente) con clase minoritaria escasa. No solo construye los folds — mide cuánta fuga produciría ignorar la agrupación, comparando contra una partición aleatoria ingenua. Úsala siempre después de eda-diagnostico y antes de modelado-baseline. Es un instrumento: mide y reporta, no decide el esquema final de modelado.
---

# Diseño de Validación

Skill instrumento. Propone un esquema de validación cruzada agrupado,
lo construye, y lo audita estructuralmente. No entrena ningún modelo —
eso es trabajo de `modelado-baseline`. No decide si el esquema propuesto
es el correcto para el proyecto — esa lectura la hace el agente al leer
`outputs/diseno-validacion.json`.

## Cuándo usarla

- Después de correr `eda-diagnostico` sobre el dataset (necesita saber
  la columna de grupo y la tasa de la clase minoritaria antes de elegir
  cuántos folds tienen sentido).
- Antes de `modelado-baseline`: ningún baseline se entrena sin un
  esquema de validación ya auditado.
- Cada vez que cambie la columna de agrupación, el target, o el número
  de folds deseado.

## Qué hace

1. Construye una partición cruzada agrupada (`GroupKFold`, o
   `StratifiedGroupKFold` si la versión de scikit-learn instalada lo
   soporta y hay suficientes grupos positivos para estratificar).
2. Verifica, por construcción y de forma independiente, que ningún
   grupo (ej. `patient_id`) aparezca simultáneamente en train y en
   validación dentro del mismo fold. Esto debería dar siempre cero si
   el esquema está bien construido — el script lo comprueba en vez de
   asumirlo.
3. Reporta el balance de cada fold: tamaño, número de grupos, y —crítico
   dada la escasez de positivos— cuántos casos positivos caen en cada
   fold de validación. Un fold con cero positivos es una medición, no
   una sugerencia de qué hacer al respecto.
4. **Cuantifica el riesgo de no agrupar.** Aparte del esquema agrupado,
   corre una partición aleatoria simple a nivel de fila (mismo tamaño
   de validación, misma semilla) que ignora la columna de grupo, y
   cuenta cuántos grupos quedan repartidos entre train y validación.
   Ese número es la evidencia concreta de cuánta fuga se evitó.
5. No entrena nada. No dice "por lo tanto usa k=5". Eso lo decide el
   agente, leyendo el reporte.

## Cómo correrlo

```bash
python .claude/skills/diseno-validacion/scripts/build_and_audit_cv.py \
  --data data/train-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --n-splits 5 \
  --seed 42 \
  --out outputs/diseno-validacion
```

Si `--group-col` o `--target-col` no existen en el archivo, el script
falla con un mensaje explícito — no continúa con un esquema sin sentido.

## Contrato de salida

- `outputs/diseno-validacion.json` — esquema completo y auditoría,
  incluido el detalle fold a fold en `por_fold`.
- `outputs/diseno-validacion.md` — resumen legible, máximo 15 líneas,
  sin interpretación ni recomendaciones.

El `.md` usa un número **fijo** de líneas: el balance de los folds se
resume en mínimo, máximo y promedio, no en una línea por fold. Así el
límite de 15 líneas se respeta con cualquier `--n-splits`. Quien
necesite el detalle por fold lo lee del `.json`.

### Campos del JSON

```
{
  "esquema": {
    "metodo": "StratifiedGroupKFold" | "GroupKFold",
    "n_splits": int,
    "group_col": str,
    "target_col": str,
    "seed": int
  },
  "n_grupos_total": int,
  "n_grupos_positivos": int,
  "por_fold": [
    {
      "fold": int,
      "n_train_grupos": int, "n_val_grupos": int,
      "n_train_filas": int, "n_val_filas": int,
      "n_val_positivos": int, "pct_val_positivos": float
    }, ...
  ],
  "fuga_de_grupo_detectada": bool,
  "comparacion_particion_naive": {
    "descripcion": "partición aleatoria 80/20 a nivel de fila, misma semilla, ignorando group_col",
    "n_grupos_con_fuga": int,
    "pct_grupos_con_fuga": float
  }
}
```

`fuga_de_grupo_detectada` debe dar `false` si el esquema agrupado está
bien construido. Si da `true`, es un defecto del script, no un hallazgo
del dataset — repórtalo como bug, no como resultado.

## No interpretes aquí

Ejemplos de lo que esta skill NO debe decir — eso es trabajo del agente,
normalmente al invocar `sintesis-consultoria` o al decidir el esquema
final junto con `modelado-baseline`:

- "Por lo tanto k=5 es el número correcto de folds" → lo decide el agente
  leyendo el balance de positivos por fold.
- "Esto confirma que había que agrupar por paciente" → ya se sabía por
  el hallazgo de eda-diagnostico; esta skill solo cuantifica cuánto.
- "El fold 3 no es confiable, exclúyelo" → el agente decide qué hacer
  con folds desbalanceados, esta skill solo los reporta.

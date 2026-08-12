---
name: eda-diagnostico
description: Perfila un conjunto de datos tabular antes de cualquier modelado — estructura, tipos, faltantes, desbalance de clases, estructura de grupos (ej. paciente) y columnas presentes en train pero ausentes en test. Úsala siempre que se cargue un dataset nuevo o antes de escribir diseno-validacion o modelado-baseline. Es un instrumento de medición: reporta, no interpreta.
---

# EDA Diagnóstico

Skill instrumento. Mide y reporta. La interpretación de estos resultados
—qué implican, qué decisiones sugieren— la hace el agente al leer
`outputs/eda-diagnostico.json`, no esta skill.

## Cuándo usarla

- Antes de escribir o correr `diseno-validacion`.
- Antes de escribir o correr `modelado-baseline`.
- Cada vez que cambie el archivo de datos de entrada (nueva descarga,
  filtro aplicado, columnas añadidas).

## Qué hace

1. Localiza el archivo de metadata más reciente en `data/` (por defecto
   `train-metadata.csv`; acepta ruta como argumento).
2. Ejecuta `scripts/eda_profile.py` sobre ese archivo, y sobre el archivo
   de test correspondiente si existe.
3. El script no asume nombres de columnas de antemano — los descubre del
   archivo real. Si algún nombre de columna se necesita para lógica
   específica (p. ej. identificar la columna de agrupación por paciente
   o el target), pregúntalo al usuario o infiérelo del propio `CLAUDE.md`
   del proyecto; nunca lo asumas de memoria.
4. Escribe el contrato de salida (ver abajo).
5. No decide nada. No dice "por lo tanto el baseline debería ser X". Eso
   lo hace el agente, después, leyendo el reporte.

## Cómo correrlo

```bash
python .claude/skills/eda-diagnostico/scripts/eda_profile.py \
  --train data/train-metadata.csv \
  --test data/test-metadata.csv \
  --group-col patient_id \
  --target-col target \
  --out outputs/eda-diagnostico
```

Si `--test` no se pasa o el archivo es un placeholder con muy pocas filas
(menos de 1% del tamaño de train), el script lo marca explícitamente en
el reporte como `test_is_placeholder: true` — no lo trata como test real
en silencio.

## Contrato de salida

Escribe siempre dos archivos, nunca solo uno:

- `outputs/eda-diagnostico.json` — todos los campos medidos, estructurados.
- `outputs/eda-diagnostico.md` — resumen legible, máximo 15 líneas, sin
  interpretación ni recomendaciones.

### Campos del JSON

```
{
  "fuente": {"archivo": str, "fecha_ejecucion": str, "n_filas": int, "n_columnas": int},
  "tipos": {columna: dtype, ...},
  "faltantes": {columna: {"n": int, "pct": float}, ...},
  "desbalance_target": {"columna_target": str, "conteos": {...}, "pct_positivos": float} | null,
  "estructura_grupos": {
    "columna_grupo": str,
    "n_grupos": int,
    "n_filas": int,
    "filas_por_grupo": {"min": int, "max": int, "media": float, "mediana": float}
  } | null,
  "columnas_solo_en_train": [str, ...],
  "columnas_solo_en_test": [str, ...],
  "test_is_placeholder": bool,
  "test_perfil": {
    "archivo": str, "n_filas": int, "n_columnas": int,
    "tipos": {columna: dtype, ...},
    "faltantes": {columna: {"n": int, "pct": float}, ...}
  } | null,
  "duplicados_exactos": int | null,
  "duplicados_columnas_excluidas": [str, ...],
  "constantes": [str, ...]
}
```

`test_perfil` es `null` cuando no se pasó `--test` o cuando
`test_is_placeholder` es `true`; en ese caso el `.md` lo dice
explícitamente en vez de omitir la línea.

`duplicados_exactos` se cuenta **excluyendo las columnas identificador**
(`isic_id`, `lesion_id`, y cualquier columna cuya cardinalidad iguale el
número de filas), que quedan listadas en `duplicados_columnas_excluidas`.
Incluirlas haría que el conteo fuera 0 en toda tabla con clave primaria:
un chequeo incapaz de detectar lo que dice medir. Es `null` si tras
excluirlas no queda ninguna columna.

Si `--group-col` o `--target-col` no existen en el archivo, el campo
correspondiente queda `null` con una nota en el `.md` — no se inventa ni
se omite silenciosamente.

## No interpretes aquí

Ejemplos de lo que esta skill NO debe decir (eso es trabajo del agente al
leer el JSON, normalmente dentro de `sintesis-consultoria` o al invocar
`auditoria-de-fugas`):

- "Esto sugiere fuga de datos" → auditoria-de-fugas lo evalúa.
- "El desbalance amerita SMOTE / class weights" → modelado-baseline decide.
- "La partición debería estratificarse por X" → diseno-validacion decide.

Esta skill solo mide y deja constancia.

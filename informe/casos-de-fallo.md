# Casos de fallo documentados

Dos fallos reales del sistema, reproducidos y con su salida literal. No
son hipótesis de lo que podría salir mal: el caso A es un resultado que
está en `outputs/modelado-baseline.json`, y el caso B se reprodujo
ejecutando el comando el 2026-08-18 y pegando lo que imprimió la consola.

Están aquí porque un sistema solo se entiende cuando se sabe cómo falla.
Reportar únicamente el desempeño agregado esconde justo la información
que un cliente necesita para confiar —o para no confiar— en la
herramienta.

Los dos son de naturaleza opuesta, y esa oposición es el punto:

- **Caso A: un fallo silencioso.** El modelo entrena sin quejarse,
  devuelve un número, y ese número es peor que el azar. Nada en la
  ejecución lo delata.
- **Caso B: un fallo ruidoso, y deliberado.** El sistema se niega a
  ejecutarse y dice exactamente por qué. Está programado para fallar así.

---

## Caso A — El gradient boosting sin balancear cae por debajo del azar

**Entrada.**

`data/train-metadata.csv` (401.059 lesiones, 393 positivas = 0,098% —
`eda-diagnostico.json > desbalance_target`), 41 features tras excluir las
columnas señaladas por la auditoría de fugas
(`modelado-baseline.json > n_features_usadas`). Validación cruzada
`StratifiedGroupKFold` agrupada por `patient_id`, 5 folds, semilla 42
(`modelado-baseline.json > esquema_cv`). Modelo:
`HistGradientBoostingClassifier(class_weight=None)`
(`modelado-baseline.json > nivel_2a_gradient_boosting_sin_balancear.modelo`).

**Salida esperada.**

Un gradient boosting sobre 41 features debería, como mínimo, superar
tanto al azar como a la referencia univariada de una sola columna. Las
dos referencias, ambas medidas:

| Referencia | pAUC | Fuente |
|---|---|---|
| Azar | 0,02 | `escala_de_referencia_pauc.azar` |
| Univariado (`tbp_lv_H`, una columna) | 0,0809 | `nivel_0_referencia_univariada.pauc_media` |
| Regresión logística | 0,1331 | `nivel_1_regresion_logistica.pauc_media` |

Lo esperable era algo en el entorno de 0,13 o mejor.

**Salida real.**

**pAUC medio = 0,0013** (`nivel_2a_gradient_boosting_sin_balancear.pauc_media`),
desviación entre folds 0,0015.

Por fold: 0,0009 · 0,0043 · 0,0002 · 0,0008 · 0,0003
(`nivel_2a_gradient_boosting_sin_balancear.pauc_por_fold`).

No es que quede por debajo de lo esperado: queda **por debajo del piso
aleatorio de la métrica**, unas quince veces por debajo. Los cinco folds
coinciden, así que no es un fold desafortunado. El mismo modelo, con la
misma semilla y sobre los mismos folds, cambiando **un solo argumento** a
`class_weight="balanced"`, da 0,1451
(`nivel_2b_gradient_boosting_balanceado.pauc_media`).

**Diagnóstico.**

El diagnóstico de manual para clase desbalanceada es que el modelo
colapsa a predecir siempre la clase mayoritaria. **No es lo que pasa
aquí**, y la diferencia importa. Con 0,098% de positivos, el modelo
*"satura en probabilidad 1.0 sobre negativos y los coloca por encima de
los positivos, destruyendo justo la región de sensibilidad alta que el
pAUC mide"* (`nivel_2a_gradient_boosting_sin_balancear.nota`).

Un colapso a la clase mayoritaria daría un ranking indiferente,
equivalente al azar: pAUC ≈ 0,02. Obtener 0,0013 exige algo peor que la
indiferencia — exige ordenar los casos **al revés** justo en la zona que
la métrica evalúa. El modelo no se rinde: se equivoca con confianza, y lo
hace precisamente donde el cliente mira.

Lo que convierte esto en un caso de fallo instructivo y no en una
anécdota es **quién lo detecta**. La métrica del cliente lo ve; una
métrica genérica no tiene por qué verlo, porque el pAUC sobre 80% TPR
solo puntúa la región de sensibilidad alta, que es donde este modelo
concentra su error. Es el argumento central del proyecto convertido en
número: la métrica que la contraparte definió no es una preferencia
estética, es lo que hace visible este fallo.

> **Nota de trazabilidad.** `CLAUDE.md` afirma que la AUC estándar de
> este nivel es 0,6685, sugiriendo que una métrica convencional lo daría
> por aceptable. Esa cifra **no está en `outputs/`**: el bloque
> `nivel_2a` no tiene campo `auc_estandar` —solo `nivel_0` lo tiene—, así
> que por la regla 2 no se cita aquí. El argumento se sostiene sin ella:
> el contraste medido entre 0,0013 y 0,1451 con un solo argumento de
> diferencia ya lo demuestra. Pendiente: medir esa AUC y añadirla a
> `outputs/`, o retirar la afirmación de `CLAUDE.md`.

**Decisión que se tomó.** El nivel 2a se conservó en los resultados en
lugar de borrarlo. Un pipeline que solo reporta su mejor configuración
oculta que la diferencia entre 0,0013 y 0,1451 es un argumento por
defecto del constructor.

---

## Caso B — `modelado-baseline` se niega a correr sin la auditoría de fugas

**Entrada.**

El comando documentado en la propia skill, con `outputs/auditoria-de-fugas.json`
ausente. Reproducido el 2026-08-18 apartando temporalmente el archivo y
restaurándolo después (verificado por SHA-256 tras la restauración):

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

**Salida esperada.**

Que el script **no entrene**. Sin el reporte de auditoría no hay lista de
columnas a excluir, y entrenar con todas las columnas numéricas produce
un modelo con AUC casi perfecto y completamente inútil: `iddx_*` es la
etiqueta con otro nombre, y `mel_mitotic_index` y `mel_thick_mm` solo
existen después de la biopsia. El fallo correcto es negarse, no
adivinar.

**Salida real** (copiada literalmente de la consola, `stderr`):

```
ERROR: no existe outputs/auditoria-de-fugas.json. Esta skill no decide qué columnas excluir por su cuenta — corre auditoria-de-fugas primero.
```

Código de salida: **1**. No se escribió ningún archivo en `outputs/`, no
se leyó el CSV, no se entrenó nada.

**Diagnóstico.**

Esto no es un fallo del sistema: es el sistema funcionando. El guardarraíl
está en `train_and_evaluate.py:165-171` y se ejecuta **antes** de leer los
datos, así que la negativa es lo primero que ocurre, no algo que se
comprueba a medias tras cargar 257 MB.

La parte que importa para la arquitectura del proyecto es *qué* se está
protegiendo. La decisión de qué columnas excluir es la decisión más
consecuente de todo el pipeline —determina si el modelo es honesto o una
fuga con buena puntuación— y el script está construido para **no poder**
tomarla por su cuenta. Las columnas se leen del reporte:

```python
columnas_excluidas = (
    reporte_fugas.get("columnas_solo_en_train", [])
    + reporte_fugas.get("columnas_constantes", [])
    + reporte_fugas.get("columnas_identificador", [])
)
```

No hay rama alternativa, ni valor por defecto, ni lista escrita a mano
como respaldo. Si el reporte no está, no hay nada que usar, y el script
lo dice en vez de improvisar.

El contraste con el caso A es el motivo de que ambos estén en este
documento. En el caso A el sistema falla en silencio y hace falta la
métrica correcta para verlo. En el caso B falla a gritos, en un segundo,
y explica el remedio en la misma frase. Un guardarraíl que no se puede
saltar por descuido vale más que una advertencia en la documentación.

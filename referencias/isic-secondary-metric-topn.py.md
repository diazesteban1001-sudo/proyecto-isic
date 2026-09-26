# ISIC-Research/Challenge-2024-Metrics — `SecondaryMetric-TopNSensitivity.py` (FICHA)

**Qué es:** el guion de puntuación del premio secundario *"Top-15 retrieval
sensitivity"* del organizador. Autoría declarada en el propio archivo:
*(c) 2024 Maura Gillis & Jochen Weber, MSKCC*.
**URL:** https://github.com/ISIC-Research/Challenge-2024-Metrics/blob/main/SecondaryMetric-TopNSensitivity.py
**Commit:** `34993a2f391fd027e6091cf7c377a8f3f0279c4b` (`HEAD` de `main`, del
2024-06-12, consultado en `api.github.com` el 2026-09-25). *Este hash es el dato
que identifica la versión copiada (regla 6, la excepción): no se actualiza.*
**Fecha de consulta:** 2026-09-25. La URL respondió 200 (5.359 bytes) antes de
descargarla.

**LICENCIA: ninguna → FICHA.** Es el mismo repositorio que el README y el guion
del pAUC, sin archivo de licencia: `/repos/ISIC-Research/Challenge-2024-Metrics/license`
responde 404 (comprobado el 2026-09-25; ver `referencias/isic-metrics-readme.md`).
Sin licencia rige el copyright por defecto.

**Texto completo:** en local,
`referencias/_texto-completo/upstream-SecondaryMetric-TopNSensitivity.py` (el guion
tal cual, 156 líneas, SHA-256
`af90b6b846c3d84fbc4132300c4a6f6035edce1fa8907b706abd98f5fa72800c`).

**Por qué está aquí:** contra este guion se verifica la SEtop-15 del proyecto
(`modelado-baseline/scripts/metricas_triaje.py`), igual que se verificó el pAUC
contra `PrimaryMetric-pAUC.py`. La verificación ejecuta el guion **sin
modificarlo** sobre datos sintéticos y compara su salida con la del proyecto
(`modelado-baseline/scripts/test_metricas_triaje.py`).

---

## Citas literales que el proyecto usa

Los números de línea son los del guion original.

El número de lesiones por paciente, parámetro con valor por defecto 15 (línea 50):

```python
    parser.add_argument("-t", "--topn", help="include top N scores per patient", default=15, type=int)
```

Solo cuentan los pacientes con al menos una lesión maligna (línea 85), y cada
maligna pesa la inversa de las malignas de su paciente (línea 90):

```python
    ground_truth=ground_truth[ground_truth.patient_id.isin(set(malignancies_per_patient[malignancies_per_patient.target > 0].patient_id))].copy()
```

```python
    ground_truth['target_fraction'] = ground_truth['target'].astype(float) / malignancies_per_patient
```

Las `top_n` lesiones de mayor puntuación de cada paciente (línea 114):

```python
        top_values = data.groupby('patient_id', group_keys=False).apply(lambda x: x.nlargest(top_n, score_column)).reset_index()
```

La métrica del premio: la suma de esas fracciones entre el número de pacientes
(línea 129), que es la primera columna por la que se ordena la clasificación
(línea 144):

```python
        raw_average_rank =top_values.target_fraction.sum() / no_patients
```

```python
    }).sort_values(by=["average ranks", "weighted ranks"], ascending=False).reset_index().drop('index', axis=1)
```

El guion calcula además otra sensibilidad, con peso por lesión (líneas 116 a
120), que **no** es la del premio:

```python
        found_malignancies=top_values["target"].sum()
```

```python
        sensitivity_calculation=found_malignancies/(found_malignancies+not_found_malignancies)
```

## Lectura

*Nuestro.* `raw_average_rank` es la media, sobre los pacientes enfermos, de la
fracción de sus lesiones malignas que caen entre sus 15 de mayor puntuación.
Kurtansky et al. 2025 describen así SEtop-15: *"The computation of SEtop-15
weighed each diseased patient equally to avoid being more strongly influenced by
patients who had multiple malignancies."*
(`referencias/kurtansky-2025-triaje-automatizado-tbp.md`, métodos). La SEtop-15
del proyecto es `raw_average_rank`, no `sensitivity`.

En los empates, `nlargest` usa su valor por defecto, `keep="first"`: entre
puntuaciones iguales en el borde, se queda con las que aparecen antes.

## Localizadores sin texto

- Líneas 41 a 73: entrada y salida. Lee los envíos de una carpeta con una ruta de
  Windows y la verdad de campo de `test-gt.csv`, junto al guion (paráfrasis).
- Línea 107: se queda con las filas que tienen `split` en la verdad de campo,
  que tras el filtro de la línea 85 son las de los pacientes enfermos
  (paráfrasis).
- Líneas 125 a 130: un segundo criterio, ponderado por el rango, que solo
  desempata (paráfrasis).

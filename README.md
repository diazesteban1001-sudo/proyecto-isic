# Agente consultor estadístico — Detección de melanoma (ISIC 2024)

**Estado: avance parcial.** Entrega de progreso — 20 de agosto de 2026.
Proyecto en curso, sustentación final en aprox. 3 meses. Ver "Qué falta"
más abajo para el alcance pendiente.

## El problema y la contraparte

La International Skin Imaging Collaboration (ISIC) y Memorial Sloan
Kettering Cancer Center (MSKCC) plantearon un problema real de triage
clínico: identificar lesiones malignas de piel a partir de fotografía
corporal total en 3D — imágenes de calidad no clínica, pensadas para
contextos con acceso limitado a dermatoscopio.

La necesidad de la contraparte no se limita a una sola métrica. Además
del puntaje principal (pAUC sobre 80% de sensibilidad, que exige que el
sistema sea clínicamente sensible antes que preciso en general), ISIC
premió por separado la capacidad de priorizar las lesiones más
sospechosas por paciente ("Top-15 Retrieval Sensitivity") y la
eficiencia computacional del modelo. Esas tres señales, declaradas con
premios reales, son la línea base de lo que la contraparte necesita —
no solo lo que pidió en el leaderboard.

## Qué hace el agente

Un solo agente (Claude Code), cinco skills con un rol cada una:

| Skill | Función |
|---|---|
| `eda-diagnostico` | Perfila el dataset: tipos, faltantes, desbalance, estructura de grupos por paciente |
| `diseno-validacion` | Construye y audita la partición cruzada agrupada por paciente |
| `auditoria-de-fugas` | Chequeos estructurales + escaneo de columnas con señal univariada sospechosa |
| `modelado-baseline` | Entrena y evalúa niveles de referencia con la métrica oficial |
| `sintesis-consultoria` | Lee los cuatro reportes anteriores y redacta el informe final |

Las primeras cuatro miden y reportan; la última interpreta. Ningún
resultado del informe aparece si no está trazado hasta un archivo en
`outputs/`.

## Hallazgos principales hasta ahora

*(Cada cifra indica el archivo y campo de `outputs/` del que sale.
Confirmadas contra esos archivos el 2026-08-18.)*

- **Riesgo de fuga cuantificado:** sin agrupar por paciente, el **99,04%**
  de los pacientes habría quedado repartido entre entrenamiento y
  validación
  (`diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga`).
- **11 columnas excluidas** por estar ausentes en el conjunto de prueba o
  ser derivadas post-diagnóstico
  (`auditoria-de-fugas.json > columnas_solo_en_train`). El modelo excluye
  dos más, `image_type` por constante e `isic_id` por identificador, que
  no son fuga sino higiene.
- **La comparación honesta entre modelos revirtió una conclusión propia:**
  el modelo con mejor media (0,1451 frente a 0,1331) no gana de forma
  sostenible al compararse par a par sobre los mismos folds — gana en
  **3 de 5**, y el intervalo *t* al 95% sobre las diferencias va de
  −0,008 a +0,032, conteniendo el cero. Lo que sí se sostiene es que es
  más estable: ±0,0055 frente a ±0,0173
  (`modelado-baseline.json > nivel_1_regresion_logistica` y
  `nivel_2b_gradient_boosting_balanceado`).
- **La implementación de la métrica se verificó contra el script oficial
  del organizador** —no contra una reimplementación propia ni de memoria—
  antes de confiar en ningún resultado de modelado
  (`modelado-baseline.json > metrica_fuente`, copia literal en
  `referencias/isic-primary-metric-pauc.py.md`).

Detalle completo en `informe/informe-final.docx` y `informe/demo.html`
(demo interactiva, abrir con doble clic).

## Cómo correrlo

```bash
# Requiere Claude Code y Python 3
git clone <url-del-repo>
cd proyecto-isic
claude   # lee CLAUDE.md automáticamente al arrancar
```

Los datos (`data/`) no están versionados — se descargan por separado
desde Kaggle (ver `CLAUDE.md` para el procedimiento).

## Qué falta (alcance pendiente, no parte de esta entrega)

- **Contraparte ampliada:** validar la línea base actual con evidencia
  adicional de la práctica clínica real (tasas de biopsia innecesaria,
  tiempos de triage), más allá de lo declarado por el organizador.
- **Modelado con imágenes:** extensión evaluando características de
  modelos fundacionales de dermatología, condicionada a verificar que no
  haya contaminación entre su preentrenamiento y este dataset.
- **Casos de fallo documentados explícitamente** como conjunto de prueba
  propio (no solo desempeño agregado).
- **Guardarraíles del agente** declarados explícitamente: qué no debe
  decidir por sí solo y cómo se verifica su salida.

## Estructura del repositorio

```
├── CLAUDE.md              # bitácora de decisiones y contexto del proyecto
├── .claude/skills/         # las 5 skills
├── data/                   # no versionado
├── outputs/                # salidas verificables de cada skill
├── referencias/            # fuentes primarias citadas, versionadas
└── informe/                # borrador.md, informe-final.docx, demo.html
```

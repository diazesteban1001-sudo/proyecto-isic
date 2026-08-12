# Proyecto: Agente consultor estadístico — ISIC 2024

## Contexto

Trabajo final de la materia **Consultoría e Investigación**, último semestre de
Estadística. El profesor pide desarrollar *skills* y resolver un problema real
con ayuda de un agente que las utilice.

**Entregable esperado:** las skills en sí + el problema resuelto + informe escrito.

---

## Tesis del proyecto

> La finalidad del agente **no es ganar la competencia de Kaggle.**

El agente es un **consultor estadístico** que, ante una pregunta clínica, ejecuta
instrumentos de medición, lee sus resultados, resuelve las contradicciones entre
ellos y emite una recomendación defendible con supuestos y limitaciones
explícitos.

El caso ISIC 2024 se eligió porque su métrica **codifica la función de utilidad
del cliente**: el AUC parcial restringido a sensibilidad alta existe porque en
dermatología un falso negativo es un melanoma no detectado. Al cliente no le
importa el desempeño en la región donde la sensibilidad es clínicamente
inaceptable. El agente debe *entender* eso, no solo optimizarlo. Esa distinción
—entre optimizar una métrica y comprender por qué esa métrica— es el argumento
central del informe.

**Esto no es una lectura nuestra: la propia página de evaluación lo dice.**
Kaggle justifica la métrica en términos clínicos, no estadísticos
(`referencias/kaggle-evaluation.md`):

> "The receiver operating characteristic (ROC) curve illustrates the diagnostic
> ability of a given binary classifier system as its discrimination threshold is
> varied. However, there are regions in the ROC space where the values of TPR
> are unacceptable in clinical practice. Systems that aid in diagnosing cancers
> are required to be highly-sensitive, so this metric focuses on the area under
> the ROC curve AND above 80% TPR. Hence, scores range from [0.0, 0.2]."

La frase *"unacceptable in clinical practice"* es el eje del informe. El
organizador no eligió el pAUC por conveniencia estadística: descartó
explícitamente una región del espacio ROC por inaceptable para el cliente. La
función de utilidad está escrita en la definición de la métrica, y el trabajo
del consultor es leerla ahí antes de optimizar nada.

**Corolario — la métrica principal no agota la utilidad del cliente.** Los
premios secundarios oficiales fueron *"Top-15 Retrieval Sensitivity"* y
*"Model Efficiency"*, con 7.500 USD cada uno (`referencias/kaggle-rules.md`).
El primero mide el desempeño **por paciente**, no por lesión; el segundo premia
el tiempo de inferencia. Es decir: el cliente también valoraba la unidad de
análisis clínica correcta y el costo de despliegue —dos cosas que el pAUC no
captura—. Un consultor que solo reporta el pAUC está respondiendo una parte de
la pregunta y omitiendo que el propio cliente señaló las otras.

---

## Arquitectura

**Un solo agente. Varias skills.**

Las skills NO son agentes. Son **instrumentos**: miden y reportan. El agente es
el **consultor**: invoca los instrumentos, lee sus salidas, las cruza e
interpreta.

Separación deliberada, análoga a la que existe entre el software estadístico y
el estadístico.

| Skill | Función | Tipo |
|---|---|---|
| `eda-diagnostico` | Perfil de datos, faltantes, desbalance, estructura de grupos | instrumento |
| `diseno-validacion` | Propone y **verifica** el esquema de validación cruzada | instrumento |
| `modelado-baseline` | Modelos de referencia, métricas con incertidumbre | instrumento |
| `auditoria-de-fugas` | Checklist de *data leakage*, hallazgos priorizados | instrumento |
| `sintesis-consultoria` | Lee todo `outputs/` y produce el informe | interpretación |

`sintesis-consultoria` es distinta a las demás: no mide nada. Materializa la
interpretación. Es el entregable estrella.

---

## Reglas invariantes del proyecto

Estas reglas aplican a toda sesión de trabajo. No se negocian sobre la marcha.

### 1. Contrato de salida

Cada skill instrumento termina escribiendo:

- `outputs/<nombre>.json` — resultados estructurados
- `outputs/<nombre>.md` — resumen legible, máximo 15 líneas

Y cada `SKILL.md` de instrumento debe declarar explícitamente:

> No interpretes los resultados aquí — eso lo hace el agente.

### 2. Trazabilidad total

**Ninguna cifra del informe puede aparecer si no está en un archivo de
`outputs/`.**

Si una cifra no se puede rastrear hasta un archivo generado por un script, es
inventada. Sin excepciones. Esto convierte la verificación en algo mecánico en
vez de un acto de fe.

### 3. Nada de memoria como fuente

El agente no cita de memoria las reglas de la competencia, la definición de la
métrica ni la estructura de los datos. Lee la página oficial y los datos reales.

### 4. El estado vive en archivos, no en conversaciones

Este `CLAUDE.md` se actualiza al cerrar cada sesión: decisiones tomadas, estado
actual, siguiente paso. Una conversación por tarea, no una para todo. Commit
frecuente.

### 5. Código que parece muerto: conectarlo antes de borrarlo

**Antes de eliminar un import, una variable o una rama que parezcan sin uso,
comprobar si conectarlos cambia el resultado.** Si lo cambia, no era código
sobrante: era una corrección a medio cablear, y borrarla habría consolidado el
defecto en vez de limpiarlo.

Esta regla existe porque el patrón ya apareció tres veces, y las tres el código
inerte marcaba el sitio exacto de un defecto real:

| Dónde | Qué parecía | Qué era en realidad |
|---|---|---|
| `eda-diagnostico`, `duplicados_exactos` | Un chequeo que siempre daba 0 | Incluía la clave primaria, así que no podía detectar nada. Vacío de contenido, no correcto. |
| `auditoria-de-fugas`, `preguntas_abiertas()` | Una rama que nunca se ejecutaba | `auc_alto is None` sobre un `.get(..., False)`. Se comía 9 de las 10 preguntas, incluida `tbp_lv_dnn_lesion_confidence`. |
| `modelado-baseline`, `StandardScaler` | Un import muerto | La logística no convergía sin escalar. El pAUC reportado era el del optimizador detenido, no el del modelo. |

El contraejemplo también importa: el `StratifiedKFold` de `diseno-validacion`
sí era un import muerto y se borró sin más. La regla no es "nunca borres", es
**"comprueba primero, y que la comprobación sea empírica"** — correr el código
con y sin la pieza, y comparar. Si no cambia nada, fuera.

Corolario para las skills instrumento: un chequeo que no puede fallar no vale
nada. Cuando se escriba uno, forzar deliberadamente el caso que debería
detectar y confirmar que se dispara.

---

## Estructura del repositorio

```
proyecto-isic/
├── CLAUDE.md              ← este archivo
├── .claude/skills/
│   ├── eda-diagnostico/SKILL.md
│   ├── diseno-validacion/SKILL.md
│   ├── modelado-baseline/SKILL.md
│   ├── auditoria-de-fugas/SKILL.md
│   └── sintesis-consultoria/SKILL.md
├── data/                  ← en .gitignore, los datos NO se versionan
├── referencias/           ← copias literales de fuentes oficiales, SÍ versionadas
├── outputs/               ← salidas de cada skill (.json + .md)
└── informe/
```

`referencias/` existe porque Kaggle no es legible por el agente (JavaScript +
sesión). Las copias se toman manualmente, se anota fuente y fecha en la cabecera
del archivo, y se versionan. Así una cita a Kaggle sigue siendo trazable a un
archivo del repositorio y no a la memoria del agente.

Anatomía de cada skill:

```
nombre-skill/
├── SKILL.md          ← obligatorio: frontmatter (name, description) + instrucciones
├── scripts/          ← código determinista y repetitivo
├── references/       ← docs que se leen bajo demanda
└── assets/           ← plantillas
```

El campo `description` del frontmatter es lo que decide si la skill se activa.
Debe decir **qué hace** y **cuándo usarla**, en tono insistente (las skills
tienden a sub-activarse).

---

## Sobre el problema — VERIFICADO (2026-08-11)

**Procedencia de la verificación:** las páginas de Kaggle se renderizan
enteramente con JavaScript y no devuelven contenido a un cliente sin navegador
ni sesión —tampoco vía Internet Archive—, así que el agente no puede leerlas por
su cuenta. Se resolvió con copias literales tomadas manualmente con sesión
iniciada, versionadas en `referencias/`: son ahora la fuente citable para todo
lo que dice Kaggle. El resto se verificó contra fuentes primarias del
organizador (ISIC / MSKCC). Cada punto indica su fuente.

**Regla operativa:** si Kaggle y el organizador ISIC dicen cosas distintas, para
este proyecto manda Kaggle — es la evaluación que estamos replicando.

- [x] Objetivo: *"Identify cancers among skin lesions cropped from 3D total body
      photographs"* (etiqueta `<meta name="description">` del HTML servido por
      https://www.kaggle.com/competitions/isic-2024-challenge/overview)
- [x] **Corrección importante — la etiqueta NO es simétrica.** Los positivos sí
      son de patología: lesiones *"diagnosed as either melanoma, basal cell
      carcinoma, or squamous cell carcinoma within 3 months of 3D TBP capture"*.
      Los negativos NO: *"most never underwent a skin biopsy"* y se asumen
      benignos por evaluación clínica del dermatólogo
      (https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/).
      → La clase negativa tiene ruido de etiqueta estructural. Va al informe
      como limitación, no como nota al pie.
- [x] Insumo: recortes de 15mm×15mm de fotografía corporal total 3D, resolución
      media 133px×133px, *"comparable in optical resolution to smartphone
      images"*, con *"fewer morphologic features than dermoscopic images"*
      (https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/)
- [x] Metadata tabular: 40+ campos — edad, sexo, sitio anatómico, diámetro,
      área, perímetro, color en L*A*B*, asimetría de borde y forma, puntajes de
      confianza, modalidad de captura (XP vs. luz blanca)
      (https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/)
- [x] Desbalance de clases extremo, con cifras: **401.059 lesiones únicas —
      393 malignas (0,1%), 400.552 benignas (99,9%), 114 indeterminadas**.
      Dentro de las malignas: 157 melanomas, 163 carcinomas basocelulares,
      73 espinocelulares (https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/;
      el conteo de 401.059 imágenes lo corrobora
      https://challenge.isic-archive.com/data/2024/)
- [x] **Observaciones agrupadas por paciente** ← crítico. **1.042 pacientes** de
      siete centros dermatológicos; *"Numerous tiles can be associated to the
      same patient with the metadata element patient_id"*
      (https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/).
      Refuerzo independiente: uno de los premios secundarios oficiales es
      *"top-15 retrieval sensitivity"* calculada **por paciente**
      (https://github.com/ISIC-Research/Challenge-2024-Metrics)
- [x] Métrica: AUC parcial (pAUC) restringido a la región **por encima** de un
      TPR mínimo. Justificación textual del organizador: *"there are regions in
      the ROC space where the values of TPR are unacceptable in clinical
      practice"* (https://github.com/ISIC-Research/Challenge-2024-Metrics).
      El script oficial `PrimaryMetric-pAUC.py` implementa el umbral como
      **parámetro** `min_tpr`, invirtiendo las etiquetas y usando
      `max_fpr = |1 - min_tpr|` sobre `sklearn.metrics.roc_curve`
      (https://raw.githubusercontent.com/ISIC-Research/Challenge-2024-Metrics/main/PrimaryMetric-pAUC.py)
- [x] **Umbral exacto de sensibilidad — CERRADO: 80% TPR, rango `[0.0, 0.2]`.**
      *"Submissions are evaluated on partial area under the ROC curve (pAUC)
      above 80% true positive rate (TPR) for binary classification of malignant
      examples."* (`referencias/kaggle-evaluation.md`, copia literal de
      https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation
      tomada con sesión iniciada el 2026-08-11)
      → **`min_tpr = 0.80` es la constante del proyecto.**
- [x] **La discrepancia 80/88 no era una contradicción: son dos evaluaciones
      distintas.** El 88% TPR (rango `[0.00, 0.12]`) corresponde al esquema de
      premios del ISIC Challenge
      (https://github.com/ISIC-Research/Challenge-2024-Metrics); el 80% TPR
      (rango `[0.0, 0.2]`) es el leaderboard de Kaggle
      (`referencias/kaggle-evaluation.md`). Mismo script, mismo parámetro
      `min_tpr`, dos valores para dos evaluaciones con dueños distintos.
      **Nosotros usamos la de Kaggle.**
      *Detalle para el informe:* al justificar la métrica, Kaggle escribe
      *"required to be highly-sensitive"* y el repo del organizador escribe
      *"required to be highly-specific"* sobre la misma restricción. Dado que
      el umbral acota el TPR, la redacción de Kaggle es la correcta. Ejemplo
      real y pequeño de por qué el consultor lee la fuente en vez de confiar en
      la primera formulación que encuentra.
- [x] Reglas de uso de datos externos — **permitidos con condiciones**:
      *"External Data (...) must be publicly available and equally accessible to
      use by all participants of the Competition for purposes of the competition
      at no cost to the other participants."* (`referencias/kaggle-rules.md`,
      §7.C). Los datos de la competencia son CC BY-NC 4.0, uso no comercial y
      académico. Herramientas de AutoML permitidas con licencia apropiada (§A.2).
- [ ] Límites de cómputo y acceso a internet en las entregas — **NO VERIFICADO.**
      Falta la página *Code Requirements* de Kaggle, que no está en
      `referencias/`. Ni la página de evaluación ni la de reglas mencionan
      tiempo máximo de ejecución, tipo de hardware ni si el notebook de
      inferencia corre sin internet. No se completa de memoria.
- [x] Licencia del dataset: dos variantes, estándar CC-BY-NC y *"Permissive"*
      CC-BY (https://challenge.isic-archive.com/data/2024/)

**Nota metodológica clave:** la agrupación por paciente hace que
`auditoria-de-fugas` tenga algo real que encontrar. Si se parten los datos al
azar, lesiones del mismo paciente caen en entrenamiento y validación, y la
métrica sale inflada. Error clásico, verificable, y material de primera para el
informe. Con 401.059 lesiones sobre 1.042 pacientes —≈385 lesiones por paciente
en promedio— la fuga por partición aleatoria no es un riesgo teórico: es la
partición por defecto.

**Segunda nota metodológica, regalada por los datos:** con 393 positivos
repartidos entre 1.042 pacientes, cualquier partición debe además estratificar
por clase. Un fold sin un solo positivo hace que la métrica ni siquiera esté
definida — el script oficial lanza `ValueError` si `y_true` tiene una sola
clase. `diseno-validacion` tiene ahí su primera verificación obligatoria.

**Tercera nota — `auditoria-de-fugas` ya tiene su primer hallazgo, y es real.**
Verificado contra los CSV descargados el 2026-08-11: `train-metadata.csv` tiene
**55 columnas** y `test-metadata.csv` solo **44**. Las 11 que sobran en train:

```
target, lesion_id, iddx_full, iddx_1, iddx_2, iddx_3, iddx_4, iddx_5,
mel_mitotic_index, mel_thick_mm, tbp_lv_dnn_lesion_confidence
```

Tres familias, con implicaciones distintas:
- `iddx_*` es la taxonomía diagnóstica — es la etiqueta con otro nombre.
- `mel_mitotic_index` y `mel_thick_mm` solo existen tras la biopsia, y solo para
  melanomas. Usarlas es predecir el pasado con información del futuro.
- `tbp_lv_dnn_lesion_confidence` no es post-biopsia, pero al no estar en test
  cualquier modelo que la use es inservible en inferencia.

Un modelo entrenado con todas las columnas numéricas sin mirar da AUC casi
perfecto y es inútil. Es el ejemplo canónico para el informe.

**Cuarta nota — `tbp_lv_nevi_confidence`: RESUELTA como legítima (2026-08-11).**
La corrida de `auditoria-de-fugas` sobre los datos reales dejó una sola pregunta
abierta que no se contestaba con lo ya documentado aquí: `tbp_lv_nevi_confidence`
tiene nombre sospechoso (contiene "confidence") pero **sí está en test**, y da
AUC univariado fuera de muestra de **0.6457**
(`outputs/auditoria-de-fugas.json`). El script no puede resolver el origen de una
columna; el agente sí, leyendo la fuente.

El paper de SLICE-3D la define (copia literal en
`referencias/slice3d-metadata-tbp-lv.md`, tomada de
https://pmc.ncbi.nlm.nih.gov/articles/PMC11324883/ el 2026-08-11):

> "Nevus confidence score (0–100 scale) is a convolutional neural network
> classifier estimated probability that the lesion is a nevus."

El prefijo `lv` es *Lesion Visualizer*, el software de Canfield Scientific que
acompaña al equipo de fotografía 3D: todas las `tbp_lv_*` son métricas que la
máquina calcula sobre la captura, no resultados de patología. **Es una variable
legítima:** deriva de la imagen, está disponible en test, y por tanto es
computable en inferencia real. Su AUC moderado es exactamente lo que se espera
de un clasificador de nevus, no la firma de una fuga.

*Salvedad para el informe, no para el modelado:* el paper no dice si las ~57.000
lesiones con que se entrenó ese clasificador se solapan con SLICE-3D. Si se
solaparan, el score arrastraría de forma indirecta etiquetas de dermatólogo
sobre las mismas lesiones. No verificable con la fuente disponible, y no cambia
la decisión —el criterio operativo es la disponibilidad en inferencia—, pero va
declarado como supuesto.

*Por qué esto va al informe:* es el caso donde la separación instrumento/
consultor se ve funcionando. El instrumento marcó la columna y se detuvo en una
pregunta honesta; resolverla exigió leer una fuente externa y distinguir "nombre
sospechoso" de "fuga". Las otras nueve preguntas abiertas de esa misma corrida
sí se contestan con la Tercera nota.

---

## Decisiones tomadas

| Decisión | Razón |
|---|---|
| ISIC 2024 sobre los demás problemas | La metadata tabular hace gran parte del trabajo → sin GPU. Desbalance y agrupación por paciente son estadísticamente interesantes. La métrica tiene justificación clínica discutible en el informe. |
| Se descartan RSNA rodilla y RSNA columna lumbar | Imágenes médicas 3D: exigen GPU seria y aportan poco desde lo estadístico. |
| Un agente, no varios | Las skills son instrumentos que el agente interpreta, no actores independientes. |
| Claude Code sobre claude.ai | Las skills son mecanismo nativo, ejecución de Python sobre datos reales, `outputs/` persistente, todo versionado en Git. |

---

## Estado actual

**Fase:** las cuatro skills instrumento están completas, corridas sobre los
datos reales y auditadas. Falta la de interpretación.

| Skill | Estado | Salida en `outputs/` |
|---|---|---|
| `eda-diagnostico` | completa, auditada (`3cc3a03`) | `.json` + `.md` |
| `diseno-validacion` | completa, auditada (`3df25fc`, `a53b199`) | `.json` + `.md` |
| `auditoria-de-fugas` | completa, auditada (`958cee0`) | `.json` + `.md` |
| `modelado-baseline` | completa, auditada (`50ba80d`, `30fbff5`, `ad22ba0`) | `.json` + `.md` |
| `sintesis-consultoria` | **no escrita** | — |

Ninguna se dio por buena sin correrla contra `data/train-metadata.csv` y
encontrarle defectos. Las cuatro tenían al menos uno. El detalle de cada
corrección está en el historial de commits, que es parte del entregable.

### Hallazgos vivos para el informe

Los tres primeros ya están arriba (agrupación por paciente, 11 columnas solo en
train, `tbp_lv_nevi_confidence`). Se suman dos del modelado, ambos trazables a
`outputs/modelado-baseline.json`:

1. **El gradient boosting sin balancear falla de un modo peor que el esperado.**
   Nivel 2a da pAUC 0.0013, *por debajo del piso aleatorio de la métrica* (0.02),
   mientras su AUC estándar es 0.6685 y no delata nada. No colapsa a "predecir
   siempre negativo" —el diagnóstico de manual— sino que satura en probabilidad
   1.0 sobre negativos y los coloca encima de los positivos, arrasando justo la
   región de sensibilidad alta. Con `class_weight="balanced"` (2b): 0.1451.
   La métrica del cliente ve el problema; la métrica por defecto no.

2. **2b no solo es mejor que la logística: es más estable.** Desviación entre
   folds de **±0.0055** frente a **±0.0173** del Nivel 1 — la logística varía
   más del triple. Con 393 positivos repartidos en 5 folds (77–83 por fold,
   según `outputs/diseno-validacion.json`), esa dispersión es grande respecto a
   la diferencia de medias (0.1451 vs 0.1331), así que la comparación de medias
   sola no sostiene un "2b gana". *Salvedad al citarlo:* es dispersión fold a
   fold sobre folds no independientes, no un intervalo de confianza. Cuantificar
   la incertidumbre como es debido es trabajo del informe, no de la skill.

### Siguiente paso

Escribir `sintesis-consultoria`. Es la única skill de interpretación y el
entregable estrella: lee todo `outputs/` y produce el informe, con cada cifra
trazable a un archivo (regla 2). A diferencia de las otras cuatro, no mide nada
y por tanto no lleva contrato de 15 líneas ni advertencia de "no interpretes
aquí" — es exactamente donde sí toca interpretar.

### Pendientes

- [ ] Instalar Claude Code y verificar qué incluye el plan actual
- [x] Verificar la sección "Sobre el problema" contra la fuente oficial
      (2026-08-11 — fuentes del organizador ISIC/MSKCC + copias literales de
      Kaggle en `referencias/`)
- [x] Cerrar el umbral de la métrica (80% TPR) y las reglas de datos externos
      (2026-08-11)
- [ ] Copiar la página *Code Requirements* de Kaggle a `referencias/` para
      cerrar límites de cómputo e internet en las entregas
- [x] Descargar la metadata a `data/` (2026-08-11 — `train-metadata.csv`
      257 MB / 401.059 filas / 55 columnas, `test-metadata.csv` 3 filas /
      44 columnas). Cifras del paper confirmadas contra los datos reales:
      393 positivos (0,098%), 1.042 pacientes.
- [ ] Descargar `train-image.hdf5` (1,21 GiB) cuando lleguemos al modelado con
      imágenes. Entorno: `.venv/` con Kaggle CLI 2.2.4; token en
      `~/.kaggle/access_token`
- [x] Escribir las 4 skills instrumento y auditarlas contra los datos reales
      (2026-08-12 — `eda-diagnostico`, `diseno-validacion`, `auditoria-de-fugas`,
      `modelado-baseline`; las cuatro con defectos encontrados y corregidos)
- [ ] Escribir `sintesis-consultoria`, la quinta
- [ ] Empaquetar las skills como archivos `.skill` instalables (extra para el profe)
- [ ] Preparar demo en vivo: plantear una pregunta al agente y que invoque las
      skills frente a la clase

---

## Presentación al profesor

1. **El repositorio** — el historial de commits es la narrativa de las decisiones.
2. **El informe escrito** — producido por `sintesis-consultoria` desde `outputs/`,
   con trazabilidad de cada cifra.
3. **Demo en vivo** — es lo que más pesa: muestra la arquitectura funcionando en
   vez de descrita.

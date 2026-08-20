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

## La contraparte y su línea base (criterio 1)

### Quién es la contraparte

**ISIC / MSKCC, los organizadores del reto.** No es una contraparte inventada
para el ejercicio: publicaron qué necesitaban —el pAUC sobre 80% TPR, la
sensibilidad de recuperación top-15 por paciente y la eficiencia de
inferencia—, lo justificaron en términos clínicos y respaldaron esas
prioridades con premios reales (`referencias/kaggle-evaluation.md`,
`referencias/kaggle-rules.md`). La función de utilidad del cliente está escrita
por el cliente, no inferida por nosotros.

Autorizado explícitamente por el profesor el 2026-08-20 (ver tabla de
decisiones).

### Línea base: cuántos exámenes innecesarios genera la práctica actual

Sin una línea base, "el modelo prioriza bien" no significa nada: hay que decir
*mejor que qué*. La cifra medida de referencia viene del cribado sobre
fotografía corporal total, la misma modalidad de este dataset
(`referencias/panderm-reduccion-examenes.md`, Nature Medicine 2025, consultado
el 2026-08-20):

> "Significantly, it detected malignant lesions in 79 out of 80 patients while
> reducing unnecessary examinations by 60.8% compared with melanographers
> (3,498 versus 8,913 lesions recommended for detailed examination)"

Sobre 80 pacientes, los **melanógrafos marcaron 8.913 lesiones** para examen
detallado; el sistema automático marcó **3.498** para el mismo grupo, una
**reducción del 60,8%** de exámenes innecesarios, con detección de malignidad
en **79 de 80** pacientes. El desbalance de esa evaluación —216 malignas contra
197.716 benignas— es del mismo orden que el de SLICE-3D.

Qué aporta al criterio 1: convierte "reducir carga de trabajo" en una magnitud
con unidades. El costo de un falso positivo deja de ser abstracto y pasa a ser
un examen detallado que alguien tiene que hacer, contable.

**Tres salvedades, obligatorias al citarla** (detalle en el archivo de
`referencias/`):

1. El paper dice **"melanographers"**, palabra que aparece una sola vez y que
   **no define**. Traducirlo como "especialistas en melanoma" sería una
   sustitución nuestra que probablemente exagera la comparación. Se cita la
   palabra del paper.
2. Los autores **no discuten esta comparación en sus limitaciones**: no hay
   análisis de factores de confusión ni de diferencias de protocolo.
3. El **8.913 es el lado humano** y es la línea base independiente utilizable;
   el 3.498 es desempeño de PanDerm reportado por sus propios autores.

*Nota de deslinde:* PanDerm es también el modelo cuya posible contaminación con
SLICE-3D es la Fase 0 bloqueante de la extensión. Citar el 8.913 no depende de
esa cuestión —es una medición sobre personas—; usar sus pesos, sí.

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
| **ISIC/MSKCC cuenta como contraparte válida, y la línea base se construye con fuentes investigadas** (2026-08-20) | Respuesta del profesor, consultado sobre el criterio 1: autorizó usar lo que los organizadores declararon que necesitaban como contraparte real, y fuentes confiables investigadas —no una entrevista obligatoria— para la línea base. Cierra la tensión que estaba abierta sobre si un cliente que publica sus requisitos pero no se sienta con nosotros califica bajo ese criterio. Consecuencia operativa: la sección "La contraparte y su línea base" queda como respuesta al criterio 1, y la exigencia de rigor se traslada de *con quién se habló* a *qué tan trazable es la fuente* — que es la regla 3, ya vigente. |

---

## Estado actual

**Fase:** las cinco skills están escritas, corridas y auditadas. El alcance
original —metadata tabular, sin imágenes— está cerrado. Lo que sigue es la
extensión documentada en la última sección de este archivo.

| Skill | Estado | Salida en `outputs/` |
|---|---|---|
| `eda-diagnostico` | completa, auditada (`3cc3a03`) | `.json` + `.md` |
| `diseno-validacion` | completa, auditada (`3df25fc`, `a53b199`) | `.json` + `.md` |
| `auditoria-de-fugas` | completa, auditada (`958cee0`) | `.json` + `.md` |
| `modelado-baseline` | completa, auditada (`50ba80d`, `30fbff5`, `ad22ba0`) | `.json` + `.md` |
| `sintesis-consultoria` | completa (`c3467a7`, `6d5754a`, `3e144e0`, `8a1f3ab`) | `sintesis-verificacion.json` + `.md` |

Ninguna se dio por buena sin correrla contra `data/train-metadata.csv` y
encontrarle defectos. Las cuatro instrumento tenían al menos uno. El detalle de
cada corrección está en el historial de commits, que es parte del entregable.

`sintesis-consultoria` produjo `informe/borrador.md`, `informe/informe-final.docx`,
`informe/informe-final.pdf` y `informe/demo.html`. Su salida en `outputs/` no son
mediciones sino el resultado del verificador de trazabilidad (regla 2): cuántas
cifras del borrador tienen respaldo en un archivo y cuáles no.

### Hallazgos vivos para el informe

Los tres primeros ya están arriba (agrupación por paciente, 11 columnas solo en
train, `tbp_lv_nevi_confidence`). Se suman dos del modelado, ambos trazables a
`outputs/modelado-baseline.json`:

1. **El gradient boosting sin balancear falla de un modo peor que el esperado.**
   Nivel 2a da pAUC 0.0013, *por debajo del piso aleatorio de la métrica* (0.02).
   No colapsa a "predecir siempre negativo" —el diagnóstico de manual— sino que
   satura en probabilidad 1.0 sobre negativos y los coloca encima de los
   positivos, arrasando justo la región de sensibilidad alta. Con
   `class_weight="balanced"` (2b): 0.1451. La métrica del cliente ve el
   problema; la métrica por defecto no.

   > **AUC estándar del Nivel 2a: no medido en `outputs/`** — se retiró una
   > cifra sin respaldo encontrada durante la verificación del 18 de agosto. El
   > diagnóstico del caso de fallo no depende de ella (ver
   > `informe/casos-de-fallo.md`).

2. **2b no solo es mejor que la logística: es más estable.** Desviación entre
   folds de **±0.0055** frente a **±0.0173** del Nivel 1 — la logística varía
   más del triple. Con 393 positivos repartidos en 5 folds (77–83 por fold,
   según `outputs/diseno-validacion.json`), esa dispersión es grande respecto a
   la diferencia de medias (0.1451 vs 0.1331), así que la comparación de medias
   sola no sostiene un "2b gana". *Salvedad al citarlo:* es dispersión fold a
   fold sobre folds no independientes, no un intervalo de confianza. Cuantificar
   la incertidumbre como es debido es trabajo del informe, no de la skill.

### Siguiente paso

Fase 0 de la extensión (última sección): resolver si SLICE-3D estuvo en el
preentrenamiento de PanDerm. Es bloqueante — condiciona qué pesos se pueden
usar, y por tanto todo lo demás.

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
- [x] Escribir `sintesis-consultoria`, la quinta (2026-08-18 — borrador con
      verificador de trazabilidad, conversión a Word/PDF y demo HTML autocontenida)
- [ ] **Semana del 20 al 26 de agosto de 2026 — extender
      `verificar_trazabilidad.py` para que escanee también `CLAUDE.md`**, no
      solo `informe/borrador.md`. Es el hueco exacto por el que pasó sin
      verificar la AUC de 0,6685 atribuida al Nivel 2a, retirada el 2026-08-18.
      Mientras el verificador solo mire el borrador, la regla 2 no cubre el
      archivo que la enuncia. Nota de diseño: `CLAUDE.md` cita legítimamente
      cifras que no son mediciones propias (conteos del paper, montos de
      premios, versiones), así que el modo sobre este archivo probablemente
      deba señalar para revisión en vez de fallar — igual que hoy con el
      borrador. Cierra también el punto 2 de "Guardarraíles del agente".
- [ ] Empaquetar las skills como archivos `.skill` instalables (extra para el profe)
- [x] Preparar demo en vivo: `informe/demo.html`, generada solo por
      `generar_demo.py`, abre por doble clic sin servidor y muestra cada cifra
      con su archivo y campo de origen al pasar el cursor
- [ ] Pendientes de la extensión de imágenes: ver la última sección

---

## Presentación al profesor

1. **El repositorio** — el historial de commits es la narrativa de las decisiones.
2. **El informe escrito** — producido por `sintesis-consultoria` desde `outputs/`,
   con trazabilidad de cada cifra.
3. **Demo en vivo** — es lo que más pesa: muestra la arquitectura funcionando en
   vez de descrita.

---

## Guardarraíles del agente

Qué no decide el agente por su cuenta. Cada punto nombra el **mecanismo
que lo hace cumplir**, porque una restricción que solo vive en la
documentación es una intención, no un guardarraíl. Donde el mecanismo no
existe todavía, se dice.

### 1. No decide qué columnas excluir

La decisión más consecuente del pipeline —qué columnas se quedan fuera—
determina si el modelo es honesto o una fuga con buena puntuación. El
agente no la toma: la lee del reporte de `auditoria-de-fugas`.

**Mecanismo.** `modelado-baseline/scripts/train_and_evaluate.py:165-171`
comprueba la existencia del reporte **antes** de leer el CSV y aborta con
código 1:

```
ERROR: no existe outputs/auditoria-de-fugas.json. Esta skill no decide qué
columnas excluir por su cuenta — corre auditoria-de-fugas primero.
```

No hay lista de respaldo escrita a mano ni valor por defecto: las
columnas se arman concatenando tres campos del reporte, así que sin
reporte no hay nada que usar. Reproducido y documentado en
`informe/casos-de-fallo.md`, caso B.

### 2. Ninguna cifra del informe existe sin estar en `outputs/`

Es la regla 2 con un verificador detrás, no un propósito.

**Mecanismo.** `sintesis-consultoria/scripts/verificar_trazabilidad.py`
extrae todo número del borrador y lo busca en los `outputs/*.json` con
tolerancia de redondeo 0,01. Última corrida
(`outputs/sintesis-verificacion.json`): **331 números en el borrador,
291 con respaldo, 13 señalados** para revisar uno por uno; el resto cae
en contextos que no son cifras medidas (años, etiquetas de nivel) y se
descarta explícitamente.

**Límite conocido de este mecanismo:** el verificador se ejecuta sobre
`informe/borrador.md`, **no sobre `CLAUDE.md`**. Y ese punto ciego ya
produjo un fallo real: este archivo atribuía al Nivel 2a una AUC estándar
de 0,6685 que no existe en ningún `outputs/*.json`. **Retirada el
2026-08-18** (sección "Hallazgos vivos"); el caso A de
`informe/casos-de-fallo.md` nunca la usó y su diagnóstico se sostiene sin
ella. Cerrar el hueco —que el verificador escanee también `CLAUDE.md`—
está en Pendientes con fecha objetivo.

### 3. No decide el umbral clínico de sensibilidad

El agente **mide bajo el umbral que la contraparte definió**; no lo elige
ni lo ajusta para que los resultados luzcan mejor. El pAUC sobre 80% TPR
existe porque el organizador declaró inaceptable la región de
sensibilidad baja — la función de utilidad es del cliente, no del
consultor.

**Mecanismo.** `MIN_TPR = 0.80` es una constante de módulo en
`train_and_evaluate.py:46`, no un argumento de línea de comandos: no se
puede cambiar por invocación. Su comentario cita la fuente y registra el
valor rival que **no** se usa:

```python
# Constante del proyecto: Kaggle evalua el pAUC sobre 80% TPR, rango [0, 0.2]
# (referencias/kaggle-evaluation.md). Los premios del organizador ISIC usan
# 0.88 sobre el mismo algoritmo; no es la evaluacion que replicamos.
```

La implementación se verificó contra el script oficial del organizador
(`referencias/isic-primary-metric-pauc.py.md`), no contra una
reimplementación propia — y esa verificación encontró un error real: la
primera versión subestimaba por un factor de 0,556, dando 0,12 donde el
máximo es 0,2 (`modelado-baseline/SKILL.md`, "Sobre la métrica").

### 4. No presenta resultados como diagnóstico ni recomendación de tratamiento

La salida es **evidencia para una decisión humana**, no una conclusión
clínica. El sistema ordena lesiones por sospecha; no dice qué tiene un
paciente ni qué hacer con él.

**Mecanismo, y su honesta debilidad.** A diferencia de los tres
anteriores, este guardarraíl **no está impuesto por código** — ningún
script puede impedir que alguien lea mal una tabla. Lo que sí existe es
material medido que hace insostenible la lectura clínica, y que por regla
del proyecto tiene que viajar con los resultados:

- **La clase negativa tiene ruido de etiqueta estructural.** Los
  positivos son de patología confirmada; de los negativos *"most never
  underwent a skin biopsy"* y se asumen benignos por evaluación clínica
  (sección "Sobre el problema"). Un "negativo" del modelo no es un
  "sano": es "ningún dermatólogo lo consideró digno de biopsia".
- **Las imágenes no son de calidad diagnóstica.** Recortes de ~133×133 px
  *"comparable in optical resolution to smartphone images"*, con *"fewer
  morphologic features than dermoscopic images"* (misma sección).
- **La mejor comparación medida no es concluyente.** El intervalo *t* de
  la diferencia entre los dos mejores modelos cruza el cero
  (`informe/borrador.md` §7.4), y ese intervalo es además optimista
  porque los folds no son independientes.

Un sistema del que no se puede afirmar con certeza que un modelo supere a
otro tampoco puede sostener una afirmación diagnóstica sobre un paciente.
`sintesis-consultoria` tiene el mandato de reportar supuestos y
limitaciones junto a cada resultado, y `informe/casos-de-fallo.md` existe
para que el modo de fallo sea parte del entregable y no una nota al pie.

**Pendiente para cerrar este punto con un mecanismo real:** que el
verificador de trazabilidad falle —no solo avise— si el informe presenta
una cifra de desempeño sin su limitación asociada. Hoy no lo hace.

---

## Extensión: fase de imágenes y modelos fundacionales

**Estado: PLAN ACORDADO, NADA EJECUTADO.** Sesión de planificación del
2026-08-18. Todo lo que sigue son decisiones de diseño, no resultados. Ninguna
cifra de esta sección puede citarse en el informe como medida hasta que exista
en `outputs/`.

### Por qué existe

El alcance original excluyó imágenes por restricción de cómputo. Con más tiempo
(1-2 meses) y hardware capaz (MacBook Air M4), se extiende el proyecto **sin
abandonar la tesis original**: la profundiza, no la reemplaza.

El *Corolario* de la sección "Tesis" —la métrica principal no agota la utilidad
del cliente, y los premios secundarios lo demuestran con 7.500 USD cada uno
(`referencias/kaggle-rules.md`)— hasta ahora estaba escrito pero no ejecutado:
todo lo medido son pAUC. Esta extensión lo toma en serio y evalúa los tres ejes.

**La pregunta:** ¿cuál es la mejor recomendación que un consultor le daría hoy a
MSKCC, evaluada contra su función de utilidad completa —no solo contra el pAUC
del leaderboard— con la tecnología de 2026?

No es "ganarle al primer lugar de 2024". Eso seguiría violando la tesis. Es
evaluar el problema completo tal como el cliente lo definió.

### Por qué no hay leaderboard privado

La competencia cerró; el test privado no es accesible. El primer lugar (Ilya
Novoselskiy, score privado 0,17265 sobre 0,2) documentó su solución en el
writeup de Kaggle.

> ⚠️ **Regla 3.** Ese writeup se leyó por capturas de pantalla en el chat de
> planificación, no por fetch (Kaggle bloquea con JavaScript) y **no está en
> `referencias/`**. Hasta que se guarde la copia, nada de este bloque puede
> citarse en el informe: es memoria de conversación, exactamente lo que la
> regla 3 prohíbe como fuente. Se anota aquí como orientación de trabajo, no
> como hecho verificado.

Orientación, entonces: imagen (EVA02-small + EdgeNeXt) → predicciones OOF
concatenadas con metadata tabular → ensamble grande de GBDT. La feature que
reporta como más valiosa es comparar cada lesión contra el promedio de lesiones
del mismo paciente — la traducción numérica del "patito feo" clínico. Datos
sintéticos mejoraron su CV individual pero no el ensamble, y los descartó.

Esto encaja con lo ya medido aquí: `outputs/eda-diagnostico.json` da una media
de 384,89 lesiones por paciente (máximo 9.184), así que hay material de sobra
para construir un contraste intra-paciente.

### Protocolo de medición sin leaderboard (DECIDIDO)

Dos vías, combinadas.

**Vía A — CV comparable.** Mismo esquema que ya está montado y verificado:
StratifiedGroupKFold por `patient_id`, 5 folds (`outputs/diseno-validacion.json`),
repetido con varias semillas. Comparar **distribuciones** de pAUC entre semillas,
no puntos únicos. Declarar en el informe que compara pipelines, no arquitecturas
aisladas, y que las asignaciones de fold no son idénticas a las de nadie más.

Esto no es un capricho: el hallazgo 2 de "Hallazgos vivos" ya mostró que con
±0.0055 y ±0.0173 de dispersión entre folds, una diferencia de medias de 0,1451
contra 0,1331 no se sostiene sola.

**Vía B — lockbox propio.** Antes de tocar ningún modelo nuevo: apartar ~20% de
los **pacientes** (no de las filas), estratificado, y no tocarlo hasta la
evaluación final única.

*Aritmética del lockbox, con su fuente.* Hay 393 positivos
(`eda-diagnostico.json > desbalance_target.conteos`) repartidos en solo **259
pacientes portadores** de 1.042 (`diseno-validacion.json > n_grupos_positivos`).
Un 20% estratificado deja ~79 positivos sobre ~52 pacientes. Suficiente para un
pAUC final, pero con varianza alta y **con los positivos concentrados en pocos
pacientes**, que es peor que 79 positivos independientes. Por eso el lockbox es
confirmación, no la estimación principal.

**Regla operativa: la Vía A y la Vía B se montan ANTES de entrenar nada nuevo**
— para que el protocolo no se ajuste al resultado.

### Riesgo bloqueante: contaminación del modelo fundacional

PanDerm (Nature Medicine 2025, `github.com/SiyuanYan1/PanDerm`) se preentrenó con
>2M imágenes de 11 instituciones, incluyendo ~757.890 de TBP (~35% del
preentrenamiento) — la misma modalidad que ISIC 2024. Sucesor: DermFM-Zero /
PanDerm-2 (`huggingface.co/redlessone/PanDerm2`).

**Antes de descargar pesos: verificar si SLICE-3D estuvo entre las fuentes de
preentrenamiento.** MSKCC, anfitrión de ISIC 2024, aparece mencionado como
fuente institucional. Si hay solape, cualquier resultado de un modelo congelado
sobre estos datos está inflado por fuga — no por un error del proyecto, sino por
el preentrenamiento del modelo descargado.

Si se confirma, no se usa PanDerm, y el hallazgo se documenta como parte del
informe: **en la era de los modelos fundacionales la fuga se desplaza del propio
dataset al preentrenamiento de terceros.** Es la continuación natural de lo que
`auditoria-de-fugas` ya encontró dentro del CSV, un nivel más arriba.

Respaldo si está contaminado: DINOv3 (genérico, no dermatológico, sin este
riesgo conocido).

*Precedente en este mismo archivo:* la Cuarta nota dejó abierta exactamente esta
pregunta para `tbp_lv_nevi_confidence` —si las lesiones con que se entrenó ese
clasificador se solapan con SLICE-3D— y se resolvió por criterio de
disponibilidad en inferencia. Aquí el criterio no basta, porque el modelo
congelado sí estará disponible en inferencia y aun así el número estaría inflado.

### Plan de fases (orden de dependencia)

- **Fase 0 — bloqueante.** Resolver la contaminación PanDerm/DermFM-Zero con
  SLICE-3D. Posiblemente escribiendo a los autores (correo público en el repo).
  Nada más empieza hasta cerrarla.
- **Fase 1 — features de paciente relativo.** Sobre la metadata tabular que ya
  está en `data/`: contraste de cada lesión contra el resto de su paciente (LOF
  agrupado por `patient_id`, razones contra el promedio del paciente). Sin
  imágenes. Días de trabajo, minutos de cómputo.
  *Hipótesis, no resultado:* debería mejorar el pAUC de 0,1451
  (`modelado-baseline.json > nivel_2b_gradient_boosting_balanceado.pauc_media`).
  Se escribe aquí como predicción declarada de antemano; si no mejora, eso
  también va al informe.
- **Fase 2 — protocolo.** Montar Vía A + Vía B. Antes de las fases 3 y 4.
- **Fase 3 — características congeladas.** Una pasada hacia adelante por imagen,
  sin fine-tuning. Factible en el M4 corriendo de noche. Requiere descargar
  `train-image.hdf5` (ya está en Pendientes).
- **Fase 4 — apilado y evaluación completa.** Características de imagen +
  metadata + features de paciente relativo en el mismo pipeline tabular ya
  auditado. Tabla final con los **tres** ejes de la función de utilidad: pAUC,
  retrieval top-15 por paciente, y costo de inferencia.

La fase 4 es la que cierra el argumento del informe: es donde el consultor deja
de reportar una sola cifra y responde la pregunta que el cliente escribió
entera.

### Nota sobre alternativas tabulares (contexto, no decisión)

TabPFN y otros "modelos fundacionales tabulares" (TabArena, 2026) superan a
gradient boosting en benchmarks, pero: (a) buena parte de los números provienen
del propio laboratorio que los publica, señalado como conflicto de interés por
los mantenedores independientes de TabArena; (b) sin ensamblar configuraciones,
CatBoost vuelve a liderar; (c) la zona segura documentada es de decenas de miles
de filas, y aquí hay 401.059 (`eda-diagnostico.json > fuente.n_filas`), muy por
encima del rango validado. **No se decidió usar TabPFN.** Queda como nota de
contexto.

### Pendientes de la extensión

- [ ] **Fase 0:** verificar contaminación de PanDerm/DermFM-Zero con SLICE-3D
- [ ] Guardar el writeup del 1er lugar en `referencias/` (con fuente y fecha en
      la cabecera) antes de citarlo en el informe — regla 3
- [ ] Decidir tamaño exacto del lockbox y semilla de partición, y verificar que
      la partición deja positivos en ambos lados (mismo chequeo obligatorio que
      `diseno-validacion` ya hace para los folds)
- [ ] Decidir cuántas semillas usar en la Vía A, según tiempo de cómputo real
- [ ] Definir cómo se mide el eje "costo de inferencia" — sin esa definición la
      tabla de la fase 4 tiene solo dos columnas de tres

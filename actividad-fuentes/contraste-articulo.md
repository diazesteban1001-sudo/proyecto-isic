# Contraste con un artículo publicado: Kurtansky et al. (2025)

Qué es: el contraste del proyecto ISIC con el artículo de los organizadores del
reto, para decidir si el proyecto está bien orientado y fundamentado. Va en
lugar de la auditoría cruzada. 2026-09-29.

**Fuentes:**
- **El artículo.** Kurtansky et al. (2025), *npj Digital Medicine* 8:708, en
  `referencias/kurtansky-2025-triaje-automatizado-tbp.md` (CC BY 4.0, texto
  completo versionado).
  - Las citas entre comillas son literales y salen de su sección «Texto
    original».
  - No se usan citas con llamadas a referencias, que la extracción deja pegadas
    a la palabra anterior.
  - Lo que va sin comillas es lectura nuestra.
- **Las diferencias entre variantes del artículo** son aritmética nuestra sobre
  su Tabla 3, calculada con un guion.
- **Las cifras del proyecto** salen de `outputs/`, con el archivo en cada una.
  Los intervalos son los corregidos por Nadeau y Bengio
  (`intervalo_t_95_nadeau_bengio`).

## 1. Qué hicieron

**Datos.** Entrenaron con SLICE-3D: 401.059 recortes de 1.042 pacientes, con
393 malignos (Tabla 2). La evaluación fue sobre datos que no se publicaron:

> "Competing submissions were judged on test data compiled from the same medical
> centers (albeit different patients than the training dataset), plus from two
> additional sources."

> "Unless otherwise stated, all analyses are based on the private leaderboard
> set, containing 370,704 lesions from 935 patients"

> "the diseased class contained 342 lesions, including 99 melanomas (55
> in-situ), 190 basal cell carcinomas (BCCs), and 53 squamous cell carcinomas
> (SCCs)."

Por la Tabla 2, las dos fuentes nuevas son FNQH Cairns y Monash University and
Alfred Health. No tienen ningún paciente en entrenamiento; en el conjunto
privado tienen 177 y 30.

**Métricas.** Las cuatro que usa también el proyecto, más el NNT al 90 %:

> "Measures of diagnostic discrimination included pAUC>80% TPR and area under
> the full ROC curve (AUC). To gauge performance in theoretical triaging
> scenarios, two additional metrics were defined: SEtop-15 and NNTx% SE."

> "The computation of SEtop-15 weighed each diseased patient equally to avoid
> being more strongly influenced by patients who had multiple malignancies."

Para comparar variantes usan una prueba sobre la AUC:

> "Two-sided DeLong’s test was used to statistically compare model variants in
> discriminating skin cancer."

Los cuatro valores p de la ablación son de comparaciones de AUC. La Tabla 3 no
da intervalo ni valor p para la pAUC, el SEtop-15 ni el NNT.

**Modelos evaluados.** Son tres grupos:
- las 4.998 entregas del reto, de las que reportan el mejor valor de cada
  métrica;
- el modelo de Marchetti et al. (2023) como referencia: una regresión con 11
  medidas WB360 y cinco categorías de sitio anatómico;
- el modelo ganador y sus variantes de ablación.

El ganador tiene una rama de imagen con tres redes: dos EVA y una EdgeNeXt, y
la primera EVA se entrenó con dermatoscopia externa. Después:

> "The neural network outputs and metadata features are fed into three gradient
> boosting tree (GBT) models whose outputs are aggregated to generate a risk
> estimate for each lesion."

**Estudio de ablación.** Trabaja con cuatro clases de información (Tabla 1):
- recortes;
- metadatos básicos: edad, sexo, sitio anatómico y hospital o institución;
- metadatos WB360: tamaño, color, borde y contraste;
- contexto de paciente.

> "Each experiment was conducted with and without the component of
> patient-contextual feature class. Table 3 displays the ten model variants of
> the ablation study."

> "Given that the image models were trained independently of other features, it
> was deemed unnecessary to retrain them for each ablation variant."

Lo que destacan:

> "Notably, patient context (i.e., putting the lesion in the context of all
> other lesions from the given patient) had a substantial effect."

> "Tiles were less informative than the pre-extracted WB360 measurements."

*Nota sobre una cifra del artículo.* Para el NNT80% SE del ganador, la sección
de resultados da 51,57, pero la Tabla 3 y el párrafo de la ablación dan 50,57.
Usamos 50,57, que es el valor que cuadra con las «22 additional non-malignant
lesions» de ese párrafo: 72,68 − 50,57 = 22,11.

## 2. Lado a lado

| | Artículo | Proyecto |
|---|---|---|
| **Datos** | SLICE-3D completo para entrenar: 401.059 recortes de 1.042 pacientes. Recortes, metadatos básicos (con hospital), metadatos WB360 y contexto de paciente. | El conjunto de desarrollo de SLICE-3D: 318.229 lesiones de 833 pacientes, 317 malignas (`eda-diagnostico.json`). Metadatos tabulares sin `attribution` ni `copyright_license` (`auditoria-de-fugas.json`, `columnas_procedencia`). En M4 y M4b, además, 384 variables por imagen de DINOv2 ViT-S/14 congelado (`extraccion-imagen.json`). |
| **Esquema de evaluación** | Se entrena con todo el conjunto de entrenamiento y se evalúa una vez en el conjunto privado. DeLong sobre la AUC. | Validación cruzada estratificada y agrupada por paciente: 5 pliegues por 10 semillas (`fase4-*.json`, `n_splits` y `semillas_corridas`). Diferencias pareadas con intervalo corregido en las cuatro métricas. |
| **Métricas** | pAUC>80% TPR, AUC, SEtop-15, NNT80% SE y NNT90% SE. | pAUC sobre 80 % TPR, AUC, SEtop-15 y NNT80% SE, y el tiempo de entrenamiento y el de inferencia (`tiempo-inferencia.json`). SEtop-15 con el guion del organizador y NNT80% SE con la definición del artículo. |
| **Modelos** | Las 4.998 entregas, Marchetti et al. (2023), y el ganador con sus 10 variantes. | M1, con 39 variables, y M2, con 77 (`fase4-m2-vs-m1.json`). M4, con 461 (`fase4-m4-vs-m2.json`), y M4b, con 79 (`fase4-m4b-vs-m2.json`). M3, la parte tabular del ganador, con 217 (`fase4-m3-vs-m2.json`), y M3 limpio, con 237 a 239 (`fase4-m3limpio-vs-m2.json`). |
| **Conjunto de evaluación** | El privado: 370.704 lesiones de 935 pacientes, 342 malignas. Son los mismos centros con otros pacientes, más dos fuentes nuevas. | Los pliegues de validación del desarrollo. En la partición de `diseno-validacion.json` (semilla 42) tienen de 166 a 168 pacientes y de 63 a 64 malignas cada uno. El conjunto reservado no se ha abierto. |

## 3. Dónde coinciden los hallazgos

### Contexto de paciente: hallazgo 4 frente a la ablación

La variante sin recortes es la más parecida a M1 y M2, porque ninguno de los
dos usa imagen. En el artículo, cada columna es la variante con contexto menos
la misma sin él.

| Métrica | Artículo, variante sin recortes | Artículo, modelo completo | Proyecto, M2 − M1 [IC corregido] |
|---|---|---|---|
| pAUC | +0,012 | +0,008 | +0,0065 [−0,0147; 0,0276] |
| AUC | +0,016 | +0,011 | +0,0134 [−0,0076; 0,0343] |
| NNT80% SE | −47,72 | −22,11 | −30,549 [−60,8933; −0,2047] |
| SEtop-15 | +0,049 | +0,042 | +0,0842 [0,021; 0,1473] |

Fuente del proyecto: `fase4-m2-vs-m1.json`. En el NNT, menos es mejor.

**Coinciden en la dirección, en las cuatro métricas.** Las cuatro diferencias
de la variante sin recortes caen además dentro de los intervalos corregidos del
proyecto.

**No coinciden en qué métrica lo distingue:**
- **El artículo** declara la diferencia significativa en la AUC del modelo
  completo, con p < 0,001.
- **El proyecto** no distingue de cero la AUC ni la pAUC. Sí distingue el
  SEtop-15 y el NNT80% SE.
- **El SEtop-15, que en el proyecto da el resultado más claro, es el menos
  constante en la ablación.** Añadir el contexto lo sube en 3 de los 5 pares
  de variantes y lo baja en 2: en la de solo WB360 (−0,013) y en la de solo
  recortes (−0,004). La AUC sube en los 5 pares, como dice el artículo:

> "Ablation variants incorporating patient context features surpassed their
> independent-lesion equivalents at skin cancer discrimination (in terms of
> AUC), which reinforces the importance of considering patient norms."

### Aporte de la imagen: hallazgos 5 y 6 frente a la variante sin recortes

| Métrica | Artículo, completo − sin recortes | Proyecto, M4 − M2 [IC corregido] | Proyecto, M4b − M2 [IC corregido] |
|---|---|---|---|
| pAUC | +0,009 | −0,0065 [−0,0263; 0,0133] | +0,0056 [−0,0091; 0,0202] |
| AUC | +0,010 | −0,0085 [−0,0288; 0,0117] | +0,0055 [−0,0096; 0,0207] |
| NNT80% SE | −13,05 | +11,2372 [−19,8953; 42,3696] | −3,8724 [−25,0965; 17,3517] |
| SEtop-15 | +0,034 | −0,0332 [−0,085; 0,0185] | −0,0062 [−0,0444; 0,032] |

Fuentes del proyecto: `fase4-m4-vs-m2.json` y `fase4-m4b-vs-m2.json`.

**Coinciden en que la imagen pesa menos que la información tabular.** El
artículo lo dice en la frase citada arriba, y añade:

> "the effect of excluding tiles from the full model was less detrimental than
> excluding the WB360 “appearance” metadata"

Esa comparación tiene p = 0,068, por encima del nivel de 0,05 que fija el propio
artículo. En el proyecto, ninguna de las dos formas de añadir la imagen mejora a
M2 de forma distinguible.

**En la dirección, coinciden a medias:**
- **M4b**, que apila la imagen como el ganador, sube la pAUC y la AUC y baja el
  NNT, como en el artículo.
- **M4**, con las 384 variables sueltas, va al revés en las cuatro métricas.
- **En pAUC, AUC y NNT80% SE**, la diferencia del artículo cae dentro de los
  dos intervalos del proyecto.
- **En SEtop-15, no.** El +0,034 del artículo queda por encima del límite
  superior de M4 (0,0185) y del de M4b (0,032).

En el texto completo del artículo no aparece un valor p para la comparación del
modelo completo con la variante sin recortes.

## 4. Dónde no se pueden comparar

- **Otro conjunto de evaluación.**
  - El artículo evalúa una vez en el conjunto privado, que incluye dos fuentes
    sin pacientes en entrenamiento. Ese conjunto no es accesible: *"The ISIC’24
    evaluation dataset files will remain private indefinitely to support future
    ISIC competitions."*
  - El proyecto evalúa en validación cruzada sobre 833 de los 1.042 pacientes
    de entrenamiento. Su conjunto reservado es el resto de esos pacientes, así
    que sale de los mismos centros.
- **Una medición frente a cincuenta.**
  - Cada cifra del artículo es una sola evaluación, con 342 malignas y sin
    incertidumbre para la pAUC, el SEtop-15 ni el NNT.
  - Cada cifra del proyecto es la media de 50 pliegues, cada uno con unas 63
    malignas.
  - Por eso lo que se puede comparar es la dirección y el orden de magnitud, no
    los valores.
- **La prueba de DeLong y la agrupación por paciente.** El artículo describe la
  prueba en la frase citada arriba y no dice cómo trata la agrupación.
  - La mediana es de 243 lesiones por paciente.
  - *Lectura nuestra:* si la prueba trata cada lesión como independiente, sus
    valores p son optimistas.
- **Otros modelos.**
  - M1 y M2 son un solo `HistGradientBoostingClassifier` con los
    hiperparámetros por defecto del nivel 2b (`fase4-m2-vs-m1.json`,
    `hiperparametros`), no los tres GBT del ganador.
  - La imagen del proyecto es DINOv2 congelado, sin ajuste. La del ganador son
    tres redes entrenadas para la tarea, y una de ellas usó datos externos que
    el proyecto excluyó por riesgo de fuga (`PLAN.md`, Fase 4).
  - Los hallazgos 5 y 6 valen para la imagen así incorporada, no para la imagen
    en general.
- **El hospital.**
  - Los metadatos básicos del artículo incluyen el hospital o institución. El
    propio artículo advierte: *"ISIC’24 models used hospital labels to inform
    predictions in the evaluation set that do not describe all potential use
    settings."*
  - El proyecto excluye esa variable, así que M1 no es la variante sin recortes
    y sin contexto del artículo.
- **El NNT depende de la prevalencia.** En el conjunto privado es del 0,09 %
  (*"In a dataset with a prevalence of 0.09% (342 skin cancers in 370,704
  lesions)"*); en el desarrollo, del 0,0996 % (`eda-diagnostico.json`). Son
  parecidas, pero los NNT absolutos no se comparan.
- **Orden de magnitud, no comparación.**
  - M3 limpio da una pAUC media de 0,1621 en el desarrollo
    (`fase4-m3limpio-vs-m2.json`).
  - La variante sin recortes del artículo da 0,164 en el conjunto privado.
  - Esa cercanía indica que la reproducción está bien montada. No mide si uno
    es mejor que el otro, como ya advierte `PLAN.md`, Fase 4.

## 5. Veredicto

**¿Está bien orientado? Sí.**
- **Mide lo que midió el cliente, con sus definiciones.** Son las cuatro
  métricas del artículo, más el tiempo de inferencia, que el artículo cuenta
  entre las barreras: *"Furthermore, model efficiency is another important
  factor."*
- **Se hace las dos preguntas de la ablación de los organizadores:** si aportan
  el contexto de paciente y la imagen.
- **Llega a respuestas compatibles con las suyas.** El contexto mejora en la
  misma dirección en las cuatro métricas, y la imagen pesa menos que la
  información tabular.

**¿Está bien fundamentado? Sí en el método, con un alcance más estrecho que el
del artículo.** Trata la incertidumbre con más cuidado:
- agrupa por paciente;
- repite con 10 semillas;
- corrige el intervalo por el solape entre pliegues.

La Tabla 3 no da incertidumbre para tres de las cuatro métricas. Los límites
son cinco:
1. **No evalúa en centros nuevos.** El conjunto privado del artículo sí los
   tiene, y el reservado del proyecto no.
2. **Su precisión no alcanza para efectos del tamaño que publica el
   artículo.** Las diferencias de pAUC por contexto (+0,012) y por imagen
   (+0,009) caen dentro de sus intervalos corregidos, que también contienen el
   cero. Que el proyecto no distinga un efecto no contradice al artículo.
3. **El resultado negativo de la imagen vale para DINOv2 congelado,** no para
   las redes del ganador, que el proyecto no reprodujo. El hallazgo 5 de
   `CLAUDE.md` ya lo acota: «la imagen, así incorporada, no justifica su
   costo».
4. **Su resultado más claro sobre el contexto de paciente**, el del SEtop-15,
   es el que la ablación del artículo sostiene de forma menos constante.
5. **Prescinde del hospital.** Es una variable que el artículo usa y cuya
   validez fuera de sus centros el mismo artículo pone en duda.

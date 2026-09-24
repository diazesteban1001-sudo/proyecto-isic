# PLAN.md — la ruta de trabajo

**Plazo total: un mes.** No hay fechas por fase a propósito: lo que ordena el
trabajo son las puertas, no el calendario. Una fase termina cuando existe su
archivo, no cuando se acaba su semana.

`CLAUDE.md` describe **el proyecto** —qué es, qué reglas lo gobiernan, qué se ha
medido—. Este archivo describe **la ruta**: en qué orden, con qué condición de
salida, y qué hacer cuando algo no se pueda cerrar.

## Cómo leer una puerta

Una **puerta** es un archivo concreto que tiene que existir en el repositorio
para pasar a la fase siguiente. No es una revisión ni un juicio: o el archivo
está, o no está. Es la misma lógica que la regla 2 de `CLAUDE.md` aplicada al
proceso en vez de a las cifras — convierte "¿ya podemos seguir?" en una pregunta
mecánica.

Las fases están ordenadas por dependencia real, no por comodidad. Las fases 1 y
2 son bloqueantes por razones distintas y ambas van antes de tocar imágenes: la
1 porque un holdout sellado después de mirar los datos no es un holdout, y la 2
porque una característica extraída de un modelo contaminado no se puede
descontaminar a posteriori.

---

## Fase 0 — Cerrar el anteproyecto

**Qué se hace.** El documento de anteproyecto, completo:

- **Objetivos escritos.** Bloqueante de la rúbrica: sin objetivos explícitos no
  hay nada que evaluar contra nada. Van redactados de forma que cada uno se
  pueda declarar cumplido o incumplido al final.
- **Estado del arte organizado por enfoques**, no por orden cronológico ni por
  lista de papers. Cada fuente citada queda abierta, leída y versionada en
  `referencias/` con su cabecera de procedencia y fecha.
- **Procedencia y licencia del dataset.** SLICE-3D / ISIC 2024, con las dos
  variantes de licencia y las condiciones de uso.
- **Alcance, con sus exclusiones escritas.** Lo que queda fuera se nombra y se
  razona; un alcance que solo dice lo que incluye no acota nada.
- **Declaración de uso de IA.** Qué hizo el agente, qué hizo la persona, y dónde
  está la evidencia de cada cosa (el historial de commits).

**Estado del documento** (`informe/anteproyecto.md`, al 2026-09-24):

| Apartado | Estado |
|---|---|
| 1. Problema y estado actual | escrito: cuatro subsecciones (1.1 a 1.4), verificado frase por frase el 2026-09-24 |
| 2. Estado del arte | escrito: cinco subsecciones (2.1 a 2.5) |
| 3. Objetivos | escrito |
| 4. Datos y método | vacío |
| 5. Alcance y plan | vacío |
| 6. Declaración de uso de IA y reparto del trabajo | escrito |

La lista final de referencias tiene 20 entradas: 17 del estado del arte y 3 del
apartado 1.

Decisión de la persona, prioritaria: el apartado 6 es mínimo, una línea por
cosa; no se le dedican más recursos.

**Estado del arte — las líneas, y dónde está cada una.** Las líneas 2 a 5 son
las del estado del arte y corresponden a las subsecciones 2.1 a 2.4 del
anteproyecto; las cuatro están cerradas, con sus fuentes versionadas en
`referencias/`. La línea 1 ya no pertenece al estado del arte.

1. **Magnitud del melanoma en Colombia — FUERA DEL ESTADO DEL ARTE
   (2026-09-21).** Los dos boletines de la Cuenta de Alto Costo
   (`referencias/cac-melanoma-colombia-2026.md`, periodo 2025, y
   `referencias/cac-melanoma-colombia-2025.md`, corte a dic. 2024) **ya no
   sostienen nada del estado del arte.** Sus cifras de carga, concentración
   regional y tiempos se retiraron del borrador del estado del arte el
   2026-09-21. Se usan en el **apartado 1** (problema y estado actual), escrito
   el 2026-09-24, junto con la línea base de práctica clínica de
   `referencias/panderm-reduccion-examenes.md`. **No se vuelven a meter en el
   estado del arte:** la subsección 2.4 trata de qué se ha investigado en
   Colombia, no de cuánto melanoma hay.
2. **El caso 3D-TBP y su triaje automatizado — CERRADA.** Los propios
   organizadores analizan ISIC 2024, definen las métricas de triaje y publican
   valores de referencia:
   `referencias/kurtansky-2025-triaje-automatizado-tbp.md`; el conjunto de
   datos lo describe `referencias/kurtansky-2024-slice3d-descriptor.md`.
3. **Métricas de área parcial — CERRADA.** El origen del pAUC
   (`referencias/mcclish-1989-pauc-original.md`), su crítica sobre la curva
   SROC en metaanálisis
   (`referencias/walter-2005-pauc-sroc-en-metaanalisis.md`) y la propuesta de
   restringir los dos ejes
   (`referencias/yang-2019-two-way-partial-auc.md`). *Las dos primeras son solo
   resumen, y cada archivo lo declara en su primera línea.*
4. **Fuga por sujeto en la validación de modelos médicos — CERRADA
   (2026-09-21).** Cuatro fuentes, las cuatro con licencia abierta y texto
   completo versionado:
   - `referencias/saeb-2017-validacion-por-sujeto.md` — **el principio**: la
     partición debe imitar la relación que habrá en el uso clínico; para
     diagnóstico, por sujeto.
   - `referencias/little-2017-perspectivas-sobre-saeb.md` — **la réplica**, en
     el mismo número. Little objeta que partir por sujeto no arregla la
     confusión y puede crear desajuste de distribución; Varoquaux respalda el
     principio, con condiciones. **Saeb no se cita sin esta réplica.**
   - `referencias/kapoor-2023-fuga-y-reproducibilidad.md` — **la taxonomía**: la
     falta de independencia entre entrenamiento y prueba es el tipo **[L3.2]**
     de ocho, clasificado como prueba que no sale de la distribución de interés,
     no como falta de separación.
   - `referencias/cassidy-2022-duplicados-isic.md` — **el precedente en el
     propio ISIC**: duplicados entre entrenamiento y prueba en las ediciones
     dermoscópicas de 2016 a 2020. Es anterior a SLICE-3D y no lo analiza.

   Con esto la medición propia —`outputs/diseno-validacion.json`, que compara
   el esquema agrupado contra una partición ingenua por filas— deja de estar
   sola: el anteproyecto puede atribuir a la literatura que partir por registro
   sobrestima el desempeño cuando hay varias observaciones por sujeto, **junto
   con su objeción publicada**.

   **La prueba de ISIC 2024 se construyó con pacientes distintos a los del
   entrenamiento, y la fuente es Kurtansky et al. 2025**
   (`referencias/kurtansky-2025-triaje-automatizado-tbp.md`, sección de
   métodos *"ISIC’24 competition and dataset"*):

   > Competing submissions were judged on test data compiled from the same
   > medical centers (albeit different patients than the training dataset), plus
   > from two additional sources.

   Dos cosas que **no** lo sostienen, aunque lo parezcan: el descriptor de
   SLICE-3D, que deja la prueba fuera de su alcance
   (`referencias/kurtansky-2024-slice3d-descriptor.md`), y la frase *"There was
   no patient overlap across subsets"* del mismo artículo de 2025, que habla de
   los subconjuntos **público y privado del leaderboard**, los dos dentro de la
   prueba. Este párrafo se equivocó dos veces antes de llegar aquí: primero
   presentó esa segunda frase como partición por paciente, y después afirmó
   que ninguna fuente versionada lo respaldaba. La frase de arriba estaba en el
   repositorio desde el 2026-09-19.
5. **Qué se ha investigado en Colombia — CERRADA (2026-09-21).** No estaba en
   el plan: salió al verificar el estado del arte, y es la subsección 2.4 del
   anteproyecto. Seis fuentes en tres frentes:
   - **Teledermatología.**
     - `referencias/saenz-2018-app-teledermatologia-colombia.md`: CC BY, texto
       completo.
     - `referencias/barrera-valencia-2024-costos-teledermatologia.md`: CC BY,
       ficha con el resumen de PubMed. El texto completo está detrás de un
       desafío de Cloudflare y no hay copia en PMC.
   - **Mapeo corporal digital.**
     - `referencias/mejia-posada-2024-mapeo-corporal-medellin.md`: CC BY-NC-ND,
       texto completo.
   - **Aprendizaje automático dermatológico.**
     - `referencias/rios-duarte-2024-cnn-melanoma-uniandes.md`: CC BY-NC-ND,
       texto completo.
     - `referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md`: CC BY,
       texto completo.
     - `referencias/jojoa-2022-redes-complejas-melanoma.md`: CC BY, texto
       completo.

   Las búsquedas que las encontraron están en
   `referencias/busqueda-pubmed-colombia-2026-09-21.md`, con sus expresiones,
   campos, fecha y resultados completos. Un hallazgo condiciona cómo se usan:
   ninguno de los tres trabajos de aprendizaje automático usa datos de pacientes
   colombianos. Los tres entrenan y evalúan sobre conjuntos internacionales.

**Pendiente del estado del arte.** Ninguna de las dos cosas bloquea la entrega.

- **Densidad de salvedades epistémicas.** Es alta para una revisión de unas
  2.500 palabras (la sección 2 sin la lista de referencias).
- **La subsección 2.4 enumera tres frentes sin contrastarlos.** Las subsecciones
  2.1 y 2.3 sí contrastan: 2.1 opone el modelo morfológico de Marchetti a los
  ensambles con características de imagen, y 2.3 opone a Saeb con la réplica de
  Little. El contraste que le falta a 2.4 es **acceso frente a selección**.

**Apartado 1 — ESCRITO (2026-09-24).** Se redactó desde las fichas de la CAC
(texto completo en local), `referencias/panderm-reduccion-examenes.md` (texto
completo versionado desde ese día), los descriptores de Kurtansky, las páginas
de Kaggle y `outputs/`, y no desde `d1-material-colombia.md`. Pasó la
verificación: todas sus citas son literales y todas sus cifras tienen fuente o
están en `outputs/`; no quedan cifras derivadas.

**Siguiente paso.** Quedan vacíos los apartados 4, 5 y 6. El orden entre ellos
no está fijado.

*Salvedad sobre PanDerm — resuelta el 2026-09-24.* Hasta esa fecha su archivo
decía "TEXTO COMPLETO" en la cabecera, pero solo reproducía la frase citada, y
en `referencias/_texto-completo/` no había copia. Desde el 2026-09-24
`referencias/panderm-reduccion-examenes.md` lleva el texto completo versionado
(CC BY 4.0), tomado del XML de Europe PMC, y las citas de PanDerm se comprueban
contra él. El material suplementario no se versiona: su licencia no está
determinada.

**Puerta.** El PDF del anteproyecto, entregado.

**Riesgo.** Una referencia que no diga lo que el documento afirma que dice. Es
el modo de fallo más caro de esta fase porque no degrada el criterio: lo deja en
**Insuficiente** de golpe, y basta una.

**Contingencia.** Ninguna fuente entra al documento sin estar antes en
`referencias/` con su texto original. No es una revisión posterior: es una
precondición para escribir la frase. Si la fuente no se puede abrir y copiar, la
afirmación no se escribe.

---

## Fase 1 — Sellar el holdout y re-medir

**Qué se hace.** Apartar el **20% de los pacientes** —no de las filas—,
estratificado por presencia de positivos, y sellarlo. Después, re-correr las
cuatro skills instrumento sobre el conjunto de desarrollo restante, y actualizar
la demo y el borrador con las cifras nuevas.

El orden importa y es el único posible: **sellar primero, medir después**. Todo
lo medido hasta hoy se calculó sobre el 100% de los datos, así que todas las
cifras del borrador cambian. Es trabajo de re-medición, no de re-análisis.

**Motivo medido, no precaución teórica.** Los propios organizadores
cuantificaron lo que cuesta mirar un conjunto antes de tiempo, sobre los 4.998
envíos oficiales de ISIC 2024
(`referencias/kurtansky-2025-triaje-automatizado-tbp.md`, sección *Results*):

> "Successful teams tended to submit dozens to several hundreds of entries for
> real-time “validation” scoring. This led to a degree of overfitting, as
> 95.5% of official submissions scored higher on the public leaderboard than on
> the private leaderboard."

Es decir: prácticamente todo el mundo obtuvo una cifra optimista en el conjunto
que podía consultar a diario, y la perdió en el que no. No hacía falta hacer
nada indebido —el leaderboard público estaba para eso—; bastó con poder mirarlo.
Nuestro holdout es el equivalente del privado, y la única defensa disponible es
no tener acceso a él mientras se decide nada.

**Puerta.** Dos archivos:
- `outputs/holdout-pacientes.json` — la lista de pacientes sellados, la semilla,
  y el recuento de positivos a cada lado.
- `outputs/sintesis-verificacion.json` en verde sobre el borrador ya actualizado,
  es decir: cada cifra señalada, revisada y justificada, y ninguna heredada de
  la corrida anterior.

**Riesgo.** El holdout se queda con pocos pacientes portadores de positivos y el
número final sale muy incierto. La aritmética ya está hecha y no es tranquila:
los 393 positivos (`eda-diagnostico.json > desbalance_target.conteos`) están
repartidos en solo 259 pacientes portadores de 1.042
(`diseno-validacion.json > n_grupos_positivos`). Un 20% deja del orden de 52
pacientes y 79 positivos, **concentrados**, que es peor que 79 positivos
independientes.

**Contingencia.** Reportar siempre el intervalo junto al punto, nunca el punto
solo. Esto no es un parche para cuando salga mal: es cómo se reporta desde el
principio. El holdout es **confirmación**, no la estimación principal; la
estimación principal sigue siendo la validación cruzada repetida sobre
desarrollo.

---

## Fase 2 — El bloqueante de preentrenamiento

**Qué se hace.** Verificar si SLICE-3D estuvo entre las fuentes de
preentrenamiento de PanDerm o de DermFM-Zero. ~35% del preentrenamiento de
PanDerm es fotografía corporal total — la misma modalidad que este dataset.
*Aquí se decía también que MSKCC "aparece mencionado como fuente institucional
de esos modelos"; en el texto del artículo de PanDerm solo aparece como conjunto
de evaluación.*

**Estado (2026-09-24): la fuente está versionada; la decisión, no.** Para
PanDerm, el propio artículo lo declara: sus métodos incluyen ISIC2024 entre las
fuentes de preentrenamiento, con 352.034 recortes y la referencia al descriptor
de SLICE-3D (`referencias/panderm-reduccion-examenes.md`, texto completo). Lo
que eso implica, y lo que el texto deja sin resolver —qué imágenes exactamente,
si ver imágenes sin etiqueta cuenta como fuga—, está en `CLAUDE.md`, «Riesgo
bloqueante». La fase sigue abierta: falta la decisión escrita, que es la otra
mitad de la puerta, y DermFM-Zero no se ha mirado.

**No se extrae ni una característica antes de cerrar esto.** Si hay solape,
cualquier resultado de un modelo congelado sobre estos datos viene inflado por
fuga, y la fuga no se puede quitar después: está dentro de los pesos. Es la
continuación natural de lo que `auditoria-de-fugas` encontró dentro del CSV, un
nivel más arriba — en la era de los modelos fundacionales la fuga se desplaza
del dataset propio al preentrenamiento de terceros.

Vías, en orden de preferencia: la documentación publicada del modelo, el
artículo, y si ninguna lo resuelve, escribir a los autores (correo público en el
repositorio).

**Puerta.** La fuente versionada en `referencias/` con su cabecera de
procedencia, **y la decisión escrita**: se usa, o no se usa, y por qué. Las dos
cosas. Una fuente sin decisión deja la fase abierta.

**Riesgo.** La verificación no se puede cerrar — los autores no contestan, o la
documentación no es concluyente. Es un riesgo real y no depende de nosotros.

**Contingencia.** DINOv3: genérico, no específico de dermatología, sin este
riesgo conocido. Se pierde el ajuste al dominio y probablemente desempeño; se
gana poder afirmar lo que se mida. El intercambio se declara en el informe, con
la verificación fallida documentada — **el hallazgo de que no se pudo verificar
es él mismo un resultado publicable** del trabajo.

---

## Fase 3 — Características de imagen

**Qué se hace.** Una skill instrumento nueva, con el **mismo contrato de salida**
que las cuatro existentes: `outputs/<nombre>.json` + `outputs/<nombre>.md` de
máximo 15 líneas, y la declaración explícita de que no interpreta sus
resultados.

Mide dos cosas, no una:
1. Las características extraídas por la pasada hacia adelante, sin ajuste fino.
2. **La cobertura**: cuántas lesiones tienen imagen utilizable. Un instrumento
   que devuelve características sin decir sobre cuántas lesiones las devuelve
   deja al consultor sin saber si el modelo posterior se entrenó con todo o con
   un trozo.

**Puerta.** `outputs/extraccion-imagen.json`.

**Riesgo.** Las 401.059 imágenes (`eda-diagnostico.json > fuente.n_filas`) no
caben en el equipo, ni en tiempo ni en disco.

**Contingencia — declarada de entrada, no como plan B.** Submuestreo por
paciente conservando **todos** los positivos y una muestra de negativos, con la
proporción reportada en el `.json`. Se decide antes de ver cuánto tarda, porque
una decisión de muestreo tomada a mitad del cómputo se toma para que quepa, no
para que mida.

---

## Fase 4 — Modelado con imagen

**Qué se hace.** Los mismos niveles del `modelado-baseline` actual, sobre los
mismos pliegues de desarrollo, con **pAUC y AUC estándar** para cada uno —las
dos, porque el desacuerdo entre ambas métricas sobre las mismas predicciones ya
es un hallazgo del proyecto y no se pierde ahora.

La comparación contra el baseline tabular es **pareada y repetida** sobre varias
semillas, con **corrección de varianza** por el solape entre pliegues. El
intervalo ingenuo sobre diferencias por fold no se cita: supone una
independencia que el solape no cumple, y en este proyecto ya produjo una vez un
intervalo que excluía el cero cuando el corregido lo contenía.

**Puerta.** El intervalo corregido de la diferencia contra el baseline tabular.

**Riesgo.** La mejora no se distingue del baseline.

**Contingencia.** **Un resultado negativo también es resultado**, y el criterio
para declararlo está fijado *antes* de medir: si el intervalo corregido contiene
el cero, la recomendación al cliente es que la imagen no aporta lo suficiente
para justificar su costo, y eso se escribe con esa claridad. Lo que no se hace
es buscar la semilla, el pliegue o la métrica en que sí se distinga.

---

## Fase 5 — Abrir el holdout. Una sola vez

**Qué se hace.** Evaluar sobre el holdout sellado en la fase 1 **el modelo
recomendado**, uno solo, y reportar punto e intervalo.

**Después de esto no se cambia nada.** Ni el modelo, ni las características, ni
el preprocesamiento, ni el criterio. Si el resultado decepciona, se reporta el
resultado que decepciona. Un holdout abierto dos veces es un conjunto de
validación con otro nombre, y la segunda apertura invalida la primera
retroactivamente.

**Puerta.** El número reportado con su incertidumbre — punto e intervalo juntos,
nunca el punto solo.

**Riesgo.** La tentación de reabrirlo. Es el riesgo de esta fase, y es humano,
no técnico: el resultado sale, no gusta, y siempre hay un ajuste razonable a
mano.

**Contingencia.** Que la apertura quede registrada en un commit propio, con el
modelo elegido fijado en el commit **anterior**. Así el orden es verificable
desde fuera y no depende de que nadie recuerde haberse portado bien.

---

## Fase 6 — Cierre

**Qué se hace.** Informe final y demo actualizada. El informe se produce desde
`outputs/` como hasta ahora, con la trazabilidad verificada; la demo se
regenera, no se edita a mano.

La tabla final responde la pregunta del cliente **entera**, con sus tres ejes:
pAUC, sensibilidad de recuperación top-15 por paciente, y costo de inferencia.
Es lo que cierra el argumento: el consultor deja de reportar una sola cifra.

**Puerta.** `informe/informe-final.pdf` y `informe/demo.html` regenerados desde
el estado final de `outputs/`.

**Riesgo.** Que el informe quede desfasado de `outputs/` — la cuarta clase de
fallo del registro de incidentes (`CLAUDE.md`, regla 6), que ya ocurrió una vez
en este proyecto y costó horas de razonar sobre una fuente equivocada.

**Contingencia.** Regenerar y volver a correr el verificador **como último paso
antes de entregar**, y que ese sea su propio commit. No confiar en que la última
corrida siga siendo la vigente.

---

## Decisiones

### El componente de recuperación de casos similares — DECIDIDO: entra (2026-09-19)

**Entra al alcance como objetivo específico 4 de cinco, y se mide en la Fase 4.**
No como sexto: la rúbrica pide entre tres y cinco objetivos específicos. Uno de los dos
premios secundarios oficiales del reto fue *"Top-15 Retrieval Sensitivity"*, con
el mismo monto que el de eficiencia (`referencias/kaggle-rules.md`). Mide el
desempeño **por paciente**, no por lesión — una unidad de análisis distinta de
la del pAUC, y la que un dermatólogo usa realmente. El proyecto lo citaba desde
el primer día como prueba de que la métrica principal no agota la función de
utilidad del cliente, sin haberlo medido nunca: se usaba como argumento y no
como resultado.

**Qué destrabó la decisión.** Lo que sostenía la opción de excluirlo era que no
había definición operativa: el reto nombraba el premio, pero nosotros no
teníamos cómo calcular la métrica ni contra qué comparar el resultado. Eso dejó
de ser cierto. En
`referencias/kurtansky-2025-triaje-automatizado-tbp.md` los organizadores
definen la métrica, explican por qué la ponderan así, y publican valores de
referencia:

> "SEtop-15 measured sensitivity under the hypothetical task of identifying 15
> lesions with the highest risk scores on each patient. (…) The computation of
> SEtop-15 weighed each diseased patient equally to avoid being more strongly
> influenced by patients who had multiple malignancies."

El mismo artículo define una segunda métrica de triaje, **NNTx% SE**, con
interpretación clínica explícita:

> "NNTx% SE defined the average number of lesions needed to triage to undergo
> expert evaluation to detect a single malignancy (…) similar to the number
> needed to biopsy to detect melanoma (NNB)45, which is used in dermatology to
> measure the trade-off between skin cancer detection and avoidable
> interventions."

Con la definición, la ponderación y los valores publicados sobre la mesa, la
exclusión ya no se puede razonar: lo que faltaba era exactamente eso.

**Consecuencias, que quedan fijadas aquí:**

- La tabla de la **Fase 6 tiene tres columnas**, no dos: pAUC, SEtop-15 por
  paciente y costo de inferencia. La duda que esta entrada dejaba abierta queda
  cerrada del lado de las tres.
- Los valores de referencia contra los que comparar salen de la Tabla 3 de esa
  misma fuente, y **hay que elegir cuál se usa como línea base** — no son
  intercambiables. Queda abajo, en los flecos.

**El objetivo está redactado por la persona, no por el agente**: es el
objetivo específico 4 de `informe/anteproyecto.md`, apartado 3. Esta entrada
registra la decisión y su motivo, no su redacción.

### Flecos que abre esa decisión

Tomar la decisión no fijaba contra qué se compara. Dos de esas tres cosas ya
están cerradas —y se cerraron antes de medir, que era la condición—; la tercera
sigue abierta.

**1 y 2 — CERRADOS (2026-09-19): la referencia es Marchetti et al., objetivo
melanoma, SEtop-15 = 0,541.** Eran dos preguntas —contra qué valor y sobre qué
tarea— y se contestan juntas porque la respuesta a una condiciona la otra. La
Tabla 3 de `referencias/kurtansky-2025-triaje-automatizado-tbp.md` ofrecía tres
candidatos por tarea:

| Referencia | SEtop-15 (malignidad) | SEtop-15 (melanoma) | Qué es |
|---|---|---|---|
| *Best across all ISIC'24 submissions* | 0,790 | 0,791 | Máximo por columna |
| Modelo ganador, variante completa | 0,729 | 0,689 | El sistema del primer puesto |
| **Marchetti et al.** | 0,360 | **0,541** | El único enfoque previo publicado en 3D-TBP |

**Por qué Marchetti.** Es el único enfoque previo publicado en esta área, y —lo
que decide— **es de la misma familia que nuestro baseline tabular**: un modelo
estadístico sobre medidas morfológicas, sin imágenes. Comparar contra algo del
mismo género es lo único que hace interpretable la diferencia.

**Por qué no los otros dos.** El máximo por columna **no corresponde
necesariamente a un modelo único**: es el mejor valor de esa columna, que puede
venir de un envío distinto del que lidera las demás, así que no hay un sistema
al que atribuírselo. Y el ganador es un **ensamble con características de
imagen**, que en este trabajo no tiene contraparte hasta la Fase 4; medirse
contra él antes de esa fase sería compararse con algo que todavía no se está
construyendo.

**Salvedad obligatoria al citarla, y no es menor.** Marchetti et al. se evaluó
sobre **particiones y poblaciones distintas** de las nuestras —de hecho los
organizadores tuvieron que excluir un paciente del conjunto de evaluación por
solaparse con aquel estudio—. Por tanto **es una referencia de orden de
magnitud, para detectar una implementación rota, no una comparación de
desempeño.** Si nuestro SEtop-15 sale en la vecindad de 0,5 el cálculo está
probablemente bien montado; si sale 0,05 o 0,95, el defecto está en el código
antes que en el modelo. Ninguna frase del informe puede decir que superamos o
no superamos a Marchetti et al.

**3 — ABIERTO. Una inconsistencia en la fuente, que hay que decidir cómo
citar.** El
artículo se contradice sobre el NNT80% SE del modelo ganador: la sección
*Results* dice **51,57**, mientras la Tabla 3 y la discusión de la ablación
dicen **50,57**. La aritmética de la ablación —*"triaged 22 additional non-malignant lesions
(NNT80% SE = 72.68 vs. NNT80% SE = 50.57)"*— cuadra con
50,57, así que probablemente la errata esté en *Results*. **Probablemente no es
suficiente:** si se cita esa cifra, se cita con las dos lecturas y con cuál se
elige y por qué, igual que se hizo con la fecha de publicación de los boletines
de la CAC.

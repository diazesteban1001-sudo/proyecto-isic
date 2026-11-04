# PLAN.md — la ruta de trabajo

**Plazo total: un mes.** No hay fechas por fase a propósito: lo que ordena el
trabajo son las puertas, no el calendario. Una fase termina cuando existe su
archivo, no cuando se acaba su semana.

`CLAUDE.md` describe **el proyecto** —qué es, qué reglas lo gobiernan, qué se ha
medido—. Este archivo describe **la ruta**: en qué orden, con qué condición de
salida, y qué hacer cuando algo no se pueda cerrar.

**Dónde está la ruta (2026-11-02): fases 0 a 4, 4b, 4c, 4d y 4e, cerradas; ni
la Fase 4b, ni la 4c, ni la 4d, que salió de la retroalimentación del avance,
ni la 4e, la receta de imagen del 10.º puesto, cambiaron el modelo
recomendado, M3 limpio, ni la especificación de la Fase 5; la Fase 4f, una sola
pregunta sobre el escenario sin fotografía corporal total, también cerrada, dio
su resultado a favor, y la recomendación para ese escenario pasa a la red de la
4e; al cerrar la 4e, la persona decide si se usa cómputo aparte, y la Fase 5
espera a esa decisión; de la Fase 6 hay trabajo hecho.** De la Fase 6:
`informe/borrador-v2.md`, las decisiones sobre la demo del 2026-10-02 y las dos
mediciones del 2026-10-04, el efecto de la partición y la imagen sola. La Fase 4 tiene fijados sus modelos y sus
comparaciones (decisión del 2026-09-25) y la especificación de M3 (2026-09-26).
Hechas:
- las métricas de triaje y el contexto de paciente;
- las tres comparaciones principales, M2 − M1, M4 − M2 y M3 − M2
  (`outputs/fase4-m2-vs-m1.json`, `outputs/fase4-m4-vs-m2.json` y
  `outputs/fase4-m3-vs-m2.json`);
- la variante secundaria M4b (`outputs/fase4-m4b-vs-m2.json`);
- M3 limpio − M2, la corrida única de la regla de recomendación
  (`outputs/fase4-m3limpio-vs-m2.json`), con el modelo recomendado: M3 limpio;
- el tiempo de inferencia, que cierra la fase (`outputs/tiempo-inferencia.json`).

La Fase 5 está fijada, y su apertura va en un commit propio. La Fase 5 no se
abre hasta conocer la retroalimentación del avance del segundo corte:
si piden cambios de modelado, se hacen antes de abrir el reservado.
*Decisión (2026-10-15, de la persona): el avance no tuvo rúbrica. La
instrucción del docente fue entregar el link al repositorio público, con al
menos un 75 % de avance frente a los objetivos del primer corte. La condición
deja de esperar una rúbrica.* *2026-10-30: la retroalimentación pidió acercarse
al ganador antes de alquilar cómputo; es la Fase 4d.* *2026-10-31: la Fase 4d
cerró por su regla sin que ninguna de sus tres preguntas diera su resultado a
favor.* *2026-10-31: la persona abrió la Fase 4e, diez días de trabajo con el
equipo propio sobre la red de imagen.* *2026-11-01: la Fase 4e cerró por su
regla sin que ninguna de sus dos preguntas diera su resultado a favor.*
*2026-11-02: la persona abrió la Fase 4f, una sola pregunta: la red de la 4e
frente a «Imagen + básicos».* *2026-11-02: la persona añadió a la
especificación de la Fase 5 la red de la 4e y «Imagen + básicos», como
resultado descriptivo que no cambia ninguna recomendación.* *2026-11-02: la
Fase 4f cerró por su regla con su pregunta a favor.*

## Cómo leer una puerta

Una **puerta** es un archivo concreto que tiene que existir en el repositorio
para pasar a la fase siguiente. No es una revisión ni un juicio: o el archivo
está, o no está. Es la misma lógica que la regla 2 de `CLAUDE.md` aplicada al
proceso en vez de a las cifras — convierte "¿ya podemos seguir?" en una pregunta
mecánica.

Las fases están ordenadas por dependencia real, no por comodidad. Las fases 1 y
2 son bloqueantes por razones distintas y ambas van antes de tocar imágenes: la
1 porque el holdout protege las decisiones que se tomen después de sellarlo —las
tomadas antes, con los datos completos, no las protege, y se declaran—, y la 2
porque una característica extraída de un modelo contaminado no se puede
descontaminar a posteriori.

---

## Fase 0 — Cerrar el anteproyecto — CERRADA

**Estado: CERRADA (2026-09-24).** La entrega del anteproyecto ya pasó, así que la
puerta está cumplida. `informe/anteproyecto.md` queda como base de diseño del
proyecto y no se vuelve a pulir salvo que el curso lo pida: sus cifras son las
de las mediciones exploratorias y no se actualizan con la re-medición de la
Fase 1. Lo que sigue en esta sección es el registro de cómo se cerró.

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
| 4. Datos y método | escrito: cinco subsecciones (4.1 a 4.5), verificado frase por frase el 2026-09-24 |
| 5. Alcance y plan | escrito: dos subsecciones (5.1 y 5.2), verificado el 2026-09-24 |
| 6. Declaración de uso de IA y reparto del trabajo | escrito |

La lista final de referencias tiene 24 entradas: 17 del estado del arte, 3 del
apartado 1 y 4 del apartado 4.

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
   los tres trabajos de aprendizaje automático entrenan y evalúan con
   conjuntos públicos ya publicados, y Rios-Duarte et al. advierten que esas
   fuentes no dan la ascendencia de los pacientes. Los datos de este trabajo
   no son colombianos: ninguno de los centros de SLICE-3D está en América
   Latina. *Hasta el 2026-10-04 aquí decía que ninguno de los tres usaba datos
   de pacientes colombianos y que los tres entrenaban y evaluaban sobre
   conjuntos internacionales. Sus fuentes no lo sostienen: Rios-Duarte et al.
   dicen que las fuentes no dan la ascendencia de los pacientes
   (`referencias/rios-duarte-2024-cnn-melanoma-uniandes.md`, línea 256), y su
   referencia 22, la que acompaña a ISIC, es la colección «Hospital Italiano de
   Buenos Aires Skin Lesions» (línea 800); los dos trabajos de Jojoa no dicen
   de dónde son los pacientes.*

**Pendiente del estado del arte — no se atiende.** Con la fase cerrada, el
documento no se vuelve a pulir salvo que el curso lo pida. Quedan anotadas como
mejoras posibles:

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

*El siguiente paso ya no está aquí: está al principio de este archivo, en
«Dónde está la ruta».*

*Salvedad sobre PanDerm — resuelta el 2026-09-24.* Hasta esa fecha su archivo
decía "TEXTO COMPLETO" en la cabecera, pero solo reproducía la frase citada, y
en `referencias/_texto-completo/` no había copia. Desde el 2026-09-24
`referencias/panderm-reduccion-examenes.md` lleva el texto completo versionado
(CC BY 4.0), tomado del XML de Europe PMC, y las citas de PanDerm se comprueban
contra él. El material suplementario no se versiona: su licencia no está
determinada.

**Puerta.** El PDF del anteproyecto, entregado. *Cumplida: la entrega ya
pasó.*

**Riesgo.** Una referencia que no diga lo que el documento afirma que dice. Es
el modo de fallo más caro de esta fase porque no degrada el criterio: lo deja en
**Insuficiente** de golpe, y basta una.

**Contingencia.** Ninguna fuente entra al documento sin estar antes en
`referencias/` con su texto original. No es una revisión posterior: es una
precondición para escribir la frase. Si la fuente no se puede abrir y copiar, la
afirmación no se escribe.

---

## Fase 1 — Sellar el holdout y re-medir — CERRADA

**Estado: CERRADA (2026-09-25).** Decisión de la persona: la condición de cierre
pasa a ser `outputs/` regenerado sobre el conjunto de desarrollo y los hallazgos
de `CLAUDE.md` actualizados. Las dos se cumplen: la re-medición y los hallazgos
son del 2026-09-25. **El borrador no se parchea con las cifras nuevas: se
reescribe después de la Fase 4.** Hasta entonces la demo lleva un aviso de que
sus cifras son las exploratorias. Lo que sigue en esta sección es el registro de
cómo se cerró.

**Qué se hace.** Apartar el **20% de los pacientes** —no de las filas—,
estratificado por centro y por presencia de positivos (decisión del
2026-09-25, abajo), y sellarlo. Después, re-correr las
cuatro skills instrumento sobre el conjunto de desarrollo restante, y actualizar
la demo y el borrador con las cifras nuevas. *Esto último cambió el 2026-09-25:
ver «Estado».*

El orden importa y es el único posible: **sellar primero, medir después**. Todo
lo medido hasta hoy se calculó sobre el 100% de los datos, así que todas las
cifras del borrador cambian. Es trabajo de re-medición, no de re-análisis.

**Antes de re-medir, un defecto que se corrige (2026-09-24).** El nivel 0 de
`modelado-baseline` elige la orientación de su variable con las etiquetas del
pliegue de validación: en cada pliegue toma `max(pauc(s), pauc(−s))`
(`evaluar_columna_sola`, en `train_and_evaluate.py`). Se corrige eligiendo la
orientación en el pliegue de entrenamiento, y solo después se vuelve a medir.
La elección de la columna tenía un problema parecido: se hace con el AUC fuera
de muestra de `auditoria-de-fugas`, calculado sobre todos los pliegues.
**Resuelto (2026-09-24): la variable también se elige dentro de cada pliegue de
entrenamiento**, por la regla de la clase décima: toda elección que dependa de
las etiquetas se hace dentro del pliegue de entrenamiento. **Corregido en el
código el 2026-09-25**, con control positivo
(`modelado-baseline/scripts/test_nivel0_en_entrenamiento.py`); el efecto se
mide al re-medir. El incidente está en el registro de `CLAUDE.md` (regla 6).

**Decisiones de la persona sobre el conjunto reservado (2026-09-25).**

- 20 % de los pacientes, estratificado por centro (`attribution`) y por
  presencia de al menos una lesión maligna. Hasta hoy se estratificaba solo
  por presencia de positivos.
- Semilla 2026.
- Si algún estrato queda sin pacientes portadores a un lado, se para antes de
  sellar y se consulta.

**Sellado (2026-09-25).** `outputs/holdout-pacientes.json`, escrito por
`diseno-validacion/scripts/sellar_reservado.py`. Ningún estrato quedó vacío:
todos los centros tienen al menos un paciente portador a cada lado. Los
recuentos están en `outputs/holdout-pacientes.md`.

**Decisión de la persona sobre las columnas de procedencia (2026-09-25).**
`attribution` y `copyright_license` se excluyen de los modelos, porque
describen el centro y la licencia y no la lesión, y en un centro nuevo no
aportan información. La exclusión entra por `auditoria-de-fugas`, como una
categoría propia con su motivo en el JSON (`columnas_procedencia`), y
`modelado-baseline` la lee como lee las demás (guardarraíl 1 de `CLAUDE.md`).

**Re-medición (2026-09-25).** Las cuatro skills instrumento y la validación
repetida de 10 semillas, por el cargador del conjunto de desarrollo, con los
mismos argumentos que la corrida anterior (semilla 42, 5 folds; semillas 0 a 9).
«Antes» es `outputs/` en el commit anterior a la re-medición. Entre las dos
corridas cambian tres cosas a la vez: los datos (el 100 % frente al conjunto de
desarrollo, y con ellos los folds), las variables (sin las de procedencia) y la
elección del nivel 0. La tabla no separa sus efectos.

| Cifra | Antes: 100 % de los datos | Después: conjunto de desarrollo | Campo |
|---|---|---|---|
| Filas | 401059 | 318229 | eda-diagnostico → fuente.n_filas |
| Pacientes | 1042 | 833 | eda-diagnostico → estructura_grupos.n_grupos |
| Lesiones malignas | 393 | 317 | eda-diagnostico → desbalance_target.conteos |
| Variables del modelo | 41 | 39 | modelado-baseline → n_features_usadas |
| Nivel 0, columna | tbp_lv_H | tbp_lv_H (5 de 5 folds) | antes: columna; ahora: columna_por_fold |
| Nivel 0, pAUC media | 0.0809 | 0.0796 | modelado-baseline → nivel_0….pauc_media |
| Nivel 0, AUC | 0.8053 (AUC fuera de muestra del reporte de fugas, otra medida) | 0.8048 (media por fold en validación) | antes: auc_estandar; ahora: auc_estandar_media |
| Nivel 1, pAUC media | 0.1331 | 0.1326 | modelado-baseline → nivel_1_regresion_logistica.pauc_media |
| Nivel 1, AUC media | 0.9013 | 0.8974 | modelado-baseline → nivel_1_regresion_logistica.auc_estandar_media |
| Nivel 2a, pAUC media | 0.0013 | 0.0005 | modelado-baseline → nivel_2a_gradient_boosting_sin_balancear.pauc_media |
| Nivel 2a, AUC media | 0.6159 | 0.582 | modelado-baseline → nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media |
| Nivel 2b, pAUC media | 0.1451 | 0.1398 | modelado-baseline → nivel_2b_gradient_boosting_balanceado.pauc_media |
| Nivel 2b, AUC media | 0.93 | 0.9247 | modelado-baseline → nivel_2b_gradient_boosting_balanceado.auc_estandar_media |
| Nivel 1, pAUC media, 10 semillas | 0.131 | 0.1325 | validacion-repetida → nivel_1_regresion_logistica.pauc_media_global |
| Nivel 2a, pAUC media, 10 semillas | 0.0022 | 0.0018 | validacion-repetida → nivel_2a_gradient_boosting_sin_balancear.pauc_media_global |
| Nivel 2b, pAUC media, 10 semillas | 0.1435 | 0.1375 | validacion-repetida → nivel_2b_gradient_boosting_balanceado.pauc_media_global |
| 2b − 1, media de las diferencias | 0.0125 | 0.005 | validacion-repetida → comparacion_pareada_2b_menos_1.media |
| 2b − 1, intervalo 95 % ingenuo | [0.0087, 0.0164] | [-0.0003, 0.0103] | ….intervalo_t_95 |
| 2b − 1, intervalo 95 % corregido (Nadeau-Bengio) | [-0.0017, 0.0268] | [-0.0145, 0.0245] | ….intervalo_t_95_nadeau_bengio |
| 2b gana, por fold | 40 de 50 | 29 de 50 | ….gana_2b_en / de |
| 2b gana, por semilla | 10 de 10 | 8 de 10 | ….semillas_a_favor_de_2b |

`outputs/sintesis-verificacion.*` no se regeneró: verifica el borrador, que
todavía no se ha actualizado.

**Pendiente conocido (2026-09-25), sin tocar.** `audit_leakage.py`
(`columnas_estructurales`) marca como identificador toda columna con tantos
valores únicos como filas, así que una variable continua sin valores repetidos
se excluiría de los modelos como si fuera un identificador. Se vio con datos
sintéticos. En la corrida actual solo cae `isic_id`
(`auditoria-de-fugas.json > columnas_identificador`).

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

*Sustituida el 2026-09-25 por decisión de la persona: la segunda condición pasa
a ser `outputs/` regenerado sobre el conjunto de desarrollo y los hallazgos
actualizados. Cumplida.*

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

## Fase 2 — El bloqueante de preentrenamiento — CERRADA

**Estado: CERRADA (2026-09-25).** La puerta está cumplida: las fuentes están
versionadas en `referencias/` y la decisión, escrita. PanDerm y DINOv3 no se
usan; se usa DINOv2, con una condición sobre el punto de control que se comprueba
al empezar la Fase 3. Lo que sigue en esta sección es el registro de cómo se
cerró.

**Qué se hace.** Verificar si SLICE-3D estuvo entre las fuentes de
preentrenamiento del modelo fundacional que se use. Se planteó para PanDerm o
DermFM-Zero; tras las decisiones de abajo, el modelo es DINOv2. *Hasta el
2026-09-25 aquí decía DINOv3.* ~35% del
preentrenamiento de PanDerm es fotografía corporal total — la misma modalidad
que este dataset.
*Aquí se decía también que MSKCC "aparece mencionado como fuente institucional
de esos modelos"; en el texto del artículo de PanDerm solo aparece como conjunto
de evaluación.*

**Decisión (2026-09-24, de la persona):** PanDerm no se usa. Su artículo declara
ISIC2024 (ref. 47, el descriptor de SLICE-3D) entre las fuentes de
preentrenamiento, con 352.034 recortes. El criterio de esta fase se fijó antes
de conocer ese dato: si hay solape, no se usa. Que el preentrenamiento fuera sin
etiquetas no se admite como excepción, porque el criterio no la preveía. Se usa
DINOv3, sujeto a la misma verificación del objetivo 5. DermFM-Zero no se examinó
y no se usa. *DINOv3 no superó esa verificación: decisión del 2026-09-25, abajo.*

**Estado (2026-09-24).** **La puerta queda cumplida para PanDerm**: la fuente
está versionada (`referencias/panderm-reduccion-examenes.md`, texto completo) y
la decisión, escrita. **La fase sigue abierta** hasta versionar la fuente de los
datos de preentrenamiento de DINOv3 y escribir la decisión sobre ella. Los
límites del hallazgo sobre PanDerm —qué imágenes exactamente, si el
preentrenamiento sin etiquetas infla un resultado— están en `CLAUDE.md`, «Riesgo
bloqueante»; no cambian la decisión.

**Decisión (2026-09-24, de la persona): regla de verificación del extractor de
imagen**, fijada antes de leer su fuente. Un modelo cuenta como verificado en
dos casos:
- sus pesos o sus datos de preentrenamiento son anteriores a la primera fecha
  en que los datos de SLICE-3D fueron públicos, y sus autores no pertenecen a
  las instituciones que aportaron los datos;
- su documentación enumera fuentes cerradas que excluyen SLICE-3D.

Si no se verifica, no se usa. Los candidatos se prueban en este orden: DINOv3,
DINOv2 y, si ninguno se verifica, el trabajo sigue sin imagen. *Las fechas de
DINOv2, de DINOv3 y la primera en que los datos de SLICE-3D fueron públicos no
se afirman aquí: se verifican con fuente en esta misma fase.*

**Fuentes reunidas (2026-09-25), sin decisión.**
`referencias/simeoni-2025-dinov3.md`, `referencias/oquab-2023-dinov2.md` y
`referencias/slice3d-fechas-de-publicacion.md`, las tres fichas, con el texto
completo en local. La tercera no fija la primera fecha en que los datos de
SLICE-3D fueron públicos, porque ninguna fuente la da; recoge las que sí dan.
*La decisión, que estaba pendiente, se tomó el mismo día; va a continuación.*

**Decisión (2026-09-25, de la persona): DINOv3 no se usa; se usa DINOv2.**
DINOv3 no se usa: no cumple ningún caso de la regla (artículo de agosto de 2025,
datos de un conjunto abierto de Instagram sin fecha de recogida y semillas no
enumeradas). Se usa DINOv2 por el caso 1 de la regla: sus datos de
preentrenamiento (LVD-142M) están descritos en un artículo de abril de 2023, sus
autores no pertenecen a las instituciones contribuyentes, y los recortes de
SLICE-3D se generaron con una herramienta que lleva el nombre del reto de 2024,
presentado en un congreso de 2023 (el de la EADV, del 11 al 14 de octubre de 2023:
`referencias/eadv-congress-2023.md`). Salvedad declarada: la primera fecha
pública de SLICE-3D no la fija ninguna fuente; el orden temporal se apoya en esa
cadena de evidencia.

**Condición:** el punto de control que se use tiene que documentar LVD-142M como
sus datos de entrenamiento. Se comprueba al empezar la Fase 3, antes de extraer
ninguna característica.

Fuentes: `referencias/simeoni-2025-dinov3.md`, `referencias/oquab-2023-dinov2.md`
(citas cotejadas con el PDF de la v1) y la cadena de evidencia en
`referencias/slice3d-fechas-de-publicacion.md`, sección 5. *Hasta el 2026-09-25 la
decisión decía «una herramienta creada para el reto de 2024»; el descriptor no lo
dice, y se cambió por el nombre de la herramienta, «ISIC2024 Tile Export Tool».*

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
documentación no es concluyente. Es un riesgo real y no depende de nosotros. Con
PanDerm no se dio: el artículo lo resolvió. *Con DINOv3 y DINOv2 tampoco
(2026-09-25): los artículos bastaron para aplicar la regla, y no hizo falta
escribir a los autores.*

**Contingencia.** Se planteó DINOv3 como respaldo: genérico, no específico de
dermatología. Tras la decisión es el modelo que se usa. *Aquí se decía que no
tenía "este riesgo conocido"; que no se le conozca no es una verificación, y se
le aplica la misma.* Con DINOv3 se pierde el ajuste al dominio y probablemente
desempeño, y el intercambio se declara en el informe. Solo se gana poder afirmar
lo que se mida cuando su verificación esté cerrada. Si esa verificación
tampoco se puede cerrar, lo decide la regla de arriba: no se usa, y se pasa al
siguiente candidato. *Hasta el 2026-09-24 aquí decía que no estaba decidido.*
*2026-09-25: así fue. DINOv3 no se verificó y se pasó a DINOv2, que sí se
verificó. Lo dicho del ajuste al dominio vale igual para DINOv2, que también es
genérico.*
**El hallazgo de que no se pudo verificar sería, él mismo, un resultado
publicable** del trabajo.

---

## Fase 3 — Características de imagen — CERRADA

**Estado: CERRADA (2026-09-25).** La puerta, `outputs/extraccion-imagen.json`,
existe: las 401.059 imágenes extraídas con DINOv2 ViT-S/14, desarrollo y
reservado en archivos separados, y el cargador de desarrollo se niega a leer el
del reservado. Lo que sigue en esta sección es el registro de cómo se cerró.

**Antes de extraer:** comprobar que el punto de control de DINOv2 que se use
documenta LVD-142M como sus datos de entrenamiento. Es la condición de la
decisión de la Fase 2; si no se cumple, el modelo no cuenta como verificado.

**Preparación (2026-09-25), sin extraer nada.**
- La condición de la Fase 2 se cumple para los dos candidatos: la documentación
  oficial de ViT-S/14 y ViT-B/14 sin registros da LVD-142M como datos de
  entrenamiento (`referencias/dinov2-repositorio.md`). Las copias de Hugging
  Face no la dan, y no se usan.
- `data/train-image.hdf5` está descargado: 401.059 imágenes, una por cada
  `isic_id` del CSV.
- La prueba de tiempo está en `outputs/prueba-tiempo-dinov2.json`: pasada
  congelada sobre 1.000 imágenes del conjunto de desarrollo, en MPS, sin guardar
  características ni calcular métricas. Los dos candidatos caben en las 8 horas
  del primer paso del orden de extracción; las horas estimadas están en su campo
  `horas_estimadas_total_con_lectura_y_preproceso`.
- La elección entre S y B es de la persona y está pendiente. *Se tomó el mismo
  día; va a continuación.*

**Decisión (2026-09-25, de la persona): se usa DINOv2 ViT-S/14.** Elegido antes
de ver ningún resultado de desempeño, por tres motivos:
- **Eficiencia**, que es un eje de la utilidad del cliente: en la prueba de
  tiempo, ViT-S/14 va unas 3,5 veces más rápido que ViT-B/14
  (`outputs/prueba-tiempo-dinov2.json`, `imagenes_por_segundo_solo_modelo`).
- **Dimensión frente a positivos:** su token CLS tiene 384 dimensiones, frente a
  las 768 de ViT-B/14 (`referencias/dinov2-repositorio/MODEL_CARD.md`), y el
  conjunto de desarrollo tiene 317 lesiones malignas
  (`eda-diagnostico.json > desbalance_target.conteos`).
- **Tamaño de los recortes:** miden 133 × 133 píxeles de media
  (`referencias/kurtansky-2024-slice3d-descriptor.md`, *"average image size of
  133px-by-133px"*), menos que los 224 píxeles de entrada del modelo.

**ViT-B/14 queda documentado como alternativa no elegida**, por esos mismos
motivos: más lento, con el doble de dimensiones para los mismos positivos, y
con recortes más pequeños que su entrada.

**Extracción (2026-09-25).** Las 401.059 imágenes, con `extraccion-imagen` en
el commit que graba `outputs/extraccion-imagen.json > codigo_commit`. La
cobertura por conjunto, los tiempos por fase y los hashes de los pesos y de cada
archivo de características están en ese JSON. Las características van en
`data/dinov2-vits14-desarrollo.h5` y `data/dinov2-vits14-reservado.h5`, en
float32; el cargador de desarrollo se niega a leer el segundo. No se leyó
ninguna etiqueta ni se calculó ninguna métrica.

*La extracción fue más lenta que la prueba de tiempo:* la fase del modelo sumó
`conjuntos.desarrollo.segundos_por_fase.modelo` para las imágenes de desarrollo,
frente al ritmo de `outputs/prueba-tiempo-dinov2.json >
imagenes_por_segundo_solo_modelo`. Hay dos diferencias entre las dos
mediciones: la prueba duró segundos y dejaba la salida en el dispositivo, y la
extracción duró más de una hora y pasa la salida a CPU en cada lote. No se ha
medido cuál explica la diferencia. Cuenta para el tiempo de inferencia de la
Fase 6: la prueba de tiempo sale optimista.

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

**Riesgo.** Las 401.059 imágenes (`referencias/isic-licencia-y-cita-slice3d.md`,
tabla de la página de datos) no caben en el equipo, ni en tiempo ni en disco.
*Hasta el 2026-09-25 la cifra remitía a `eda-diagnostico.json > fuente.n_filas`,
que desde la re-medición cuenta solo el conjunto de desarrollo.*

**Decisión (2026-09-25, de la persona): el orden de la extracción.** Sustituye a
la contingencia anterior.
1. Extracción completa en el M4, si cabe en 8 horas.
2. Si no cabe, extracción completa en Kaggle.
3. Submuestreo solo como último recurso, y declarado.

Motivo: submuestrear cambia la población evaluada y quita lesiones a los
pacientes, lo que rompe la comparación con el modelo tabular.

*Hasta el 2026-09-25 la contingencia era el submuestreo por paciente,
conservando todos los positivos y una muestra de negativos, con la proporción
reportada en el `.json` y decidido antes de ver cuánto tarda la extracción.*

---

## Fase 4 — Modelado con imagen — CERRADA

**Decisión (2026-09-25, de la persona), fijada antes de correr ningún modelo con
imagen.**

- **Modelos**, sobre los mismos pliegues de desarrollo y con 10 semillas:
  - **M1:** el nivel 2b actual.
  - **M2:** M1 más el contexto de paciente: el z-score de cada variable dentro
    del paciente, los conteos y las sumas de área por paciente, y el LOF
    ajustado paciente por paciente.
  - **M3:** la parte tabular reproducida del ganador.
  - **M4:** M2 más las 384 variables de DINOv2 ViT-S/14, tal cual.
- **Comparaciones principales, fijadas:** M2 − M1, M4 − M2 y el mejor de los
  modelos propios frente a M3, cada una con su intervalo corregido por Nadeau y
  Bengio. Se reportan las tres.
- **Sin ajuste de hiperparámetros** en los modelos propios, que usan los del
  nivel 2b. M3 usa los publicados.
- **Tabla final por modelo:** pAUC, AUC, SEtop-15, NNT80% SE y tiempo de
  inferencia, con la definición del apartado 5 del anteproyecto (sección 5.1),
  que recoge la Fase 6 de este archivo.
- **Apilar un clasificador de imagen** queda como variante secundaria, no como
  principal.

**Variante secundaria M4b: especificación de la persona, fijada el 2026-09-25
antes de correrla.** M4b es M2 más dos variables de imagen:
- la puntuación de una regresión logística con pesos balanceados sobre las 384
  variables de DINOv2 ViT-S/14, estandarizadas;
- esa puntuación dividida por su media dentro del paciente, como hizo el
  ganador con sus predicciones de imagen (`top-model.ipynb`, celda 15:
  `df_train['oof_eva_score_m'] = df_train['oof_eva_score'] / df_train['oof_eva_score_m']`,
  donde `oof_eva_score_m` es la media del paciente).

Para no filtrar etiquetas, la puntuación de las filas de entrenamiento se obtiene
fuera de pliegue, con una validación cruzada interna de 5 pliegues agrupada por
paciente dentro de cada pliegue de entrenamiento. La de las filas de validación
sale del modelo ajustado sobre todo el pliegue de entrenamiento. Se corre una
sola vez, con los mismos pliegues y semillas, y se reporta como secundaria: no
cambia la conclusión principal del hallazgo 5 de `CLAUDE.md`.

**Detalles de M4b: decisión de la persona, fijada el 2026-09-25 antes de
correr.** Cierran los tres que la especificación dejaba abiertos:
1. **Validación interna:** `StratifiedGroupKFold` de 5 pliegues, agrupada por
   `patient_id`, estratificada por la etiqueta y con la misma semilla que la
   externa.
2. **Estandarizado:** dentro de un pipeline con la logística, ajustado con las
   mismas filas que cada logística.
3. **Puntuación:** `predict_proba[:, 1]`. La razón se calcula contra la media del
   paciente sobre puntuaciones del mismo tipo: fuera de pliegue en
   entrenamiento, y del modelo del pliegue en validación.

La logística lleva `class_weight="balanced"`, `C` por defecto y
`max_iter=2000`, y se reporta el número de avisos de no convergencia.

**Qué se hace.** Los mismos niveles del `modelado-baseline` actual, sobre los
mismos pliegues de desarrollo, con **pAUC y AUC estándar** para cada uno —las
dos, porque el desacuerdo entre ambas métricas sobre las mismas predicciones ya
es un hallazgo del proyecto y no se pierde ahora.

La comparación contra el baseline tabular es **pareada y repetida** sobre varias
semillas, con **corrección de varianza** por el solape entre pliegues. El
intervalo ingenuo sobre diferencias por fold no se cita: supone una
independencia que el solape no cumple, y en este proyecto ya produjo una vez un
intervalo que excluía el cero cuando el corregido lo contenía.

**Comparador añadido: la parte tabular de la solución ganadora, reproducida**
(objetivo 3 del anteproyecto). Desde su código público
(`referencias/novoselskiy-2024-isic2024.md`) se reproduce la parte tabular y de
contraste intra-paciente del ganador, sobre las mismas particiones de desarrollo
y como comparador en la misma prueba pareada con varianza corregida: CatBoost
sobre la metadata, con el z-score de cada variable dentro del paciente, los
conteos y sumas de área por paciente y el LOF ajustado paciente por paciente.

Quedan fuera, con su motivo:

- **Las redes EVA02-small y EdgeNeXt-base.** Fuera del alcance de esta
  entrega: su costo no se ha estimado, y se reconsidera si esta fase muestra que
  la imagen aporta de forma distinguible (anteproyecto, sección 5.1). Lo que se
  sabe de ese costo: el código las ajusta por completo en GPU y depende de CUDA;
  el README declara una NVIDIA A6000. *Hasta el 2026-09-24 el motivo que se daba
  aquí era "cómputo".*
- **El modelo entrenado con el ISIC Archive** (el tercer modelo de imagen, otro
  EVA02-small). Riesgo de fuga: la descarga no se filtra contra las imágenes ni
  los pacientes de la competición, y el código no permite saber si contiene los
  recortes de SLICE-3D (pregunta abierta en `CLAUDE.md`). Es el mismo criterio
  de la Fase 2: no se usa sin verificar que no hay solape.
- **La razón de cada predicción contra la media del paciente.** En el código solo
  se calcula sobre las predicciones de esos tres modelos de imagen, así que sale
  con ellos.

**La canalización publicada está rota:** `top-model.ipynb` lee la columna
`tmp_predictions_all__pr`, que ningún código del repositorio produce; el
entrenamiento de imagen escribe `tmp_predictions_all`. Reproducirla exigirá
parchearla, y cada parche se declara: qué se cambió del código publicado y por
qué. Quitar la rama de imagen ya es uno. Otra salvedad que se declara: los
hiperparámetros y las columnas descartadas del CatBoost se eligieron con las
variables de imagen presentes, así que la parte tabular reproducida no es un
modelo ajustado para ir sin ellas.

**Orden de magnitud, no comparación.** La Tabla 3 de Kurtansky 2025
(`referencias/kurtansky-2025-triaje-automatizado-tbp.md`) publica una variante
de ablación del ganador sin recortes de imagen —*Meta-basic*, *Meta-WB360* y
*Patient context*—, que es la parte que se reproduce. Sirve para comprobar que la
reproducción está bien montada, no para compararse con ella: se midió sobre la
evaluación privada del reto, con particiones y conjuntos distintos de los
nuestros. Por tarea:

- Malignidad: pAUC 0,164; SEtop-15 0,695.
- Melanoma: pAUC 0,168; SEtop-15 0,708.

La referencia de SEtop-15 para nuestros modelos sigue siendo Marchetti et al.
(«Decisiones», abajo).

**Especificación de M3: fijada el 2026-09-26 antes de correr, con el visto bueno
y las decisiones de la persona.** Las celdas son las de `top-model.ipynb`. El
código está en `modelado-baseline/scripts/ganador_m3.py`, que lee las listas de
variables del notebook versionado en vez de transcribirlas, y su control en
`test_ganador_m3.py`.

- **Datos y pliegues.** El conjunto de desarrollo, con los mismos pliegues que
  M1, M2 y M4: `construir_folds`, 5 pliegues, semillas 0 a 9.
- **Variables: 217, las publicadas salvo lo que se lista abajo.** Por familia:
  - 25 numéricas brutas y 38 derivadas;
  - 69 z-scores dentro del paciente;
  - los 3 conteos y sumas por paciente;
  - 40 one-hot;
  - el LOF;
  - 41 de conglomerado.

  Se calculan una vez, sobre todo el conjunto de desarrollo, como el notebook
  las calcula sobre todo el CSV de entrenamiento. Eso incluye la edad imputada
  con la mediana, el one-hot, el estandarizado del LOF, el k-means y las medias
  por conglomerado. Ninguno lee la etiqueta, pero, a diferencia de M2, las
  variables de un paciente dependen de los demás. El conjunto reservado no
  entra. *Decisión de la persona:* así, como se publicó, y no dentro de cada
  pliegue de entrenamiento.
- **Salen, con su motivo:**
  - las 12 variables de los modelos de imagen (celdas 14 a 17) y las 8 de la
    celda 19 que se calculan sobre ellas. El k-means se queda: la celda 18 lo
    ajusta sobre `top_lof_features`, sin imagen;
  - `attribution` (celda 3, en `cat_cols`; su one-hot, celda 8), por la
    exclusión de procedencia de `auditoria-de-fugas`. `copyright_license` no
    aparece en el notebook;
  - las 22 de `columns_to_drop` (celda 24) que no son de imagen, como se publicó.
- **Modelo, como se publicó.** Es la ruta que ejecuta la celda 25: la función de
  la celda 22 con la configuración de la celda 24.
  - CatBoost `Logloss`, `eval_metric='AUC'` y 2000 iteraciones;
  - `learning_rate` 0,0261, `depth` 6, `l2_leaf_reg` 18,04 y `min_data_in_leaf`
    38;
  - `bagging_temperature` 0,874, `border_count` 256 y
    `grow_policy='Lossguide'`;
  - `od_wait=100` y la semilla del pliegue.

  Los valores exactos van en el código y el control comprueba que están
  literalmente en su celda. Antes del ajuste se sobremuestrean los positivos
  hasta una razón de 0,003 positivos por negativo y después se submuestrean los
  negativos hasta 0,01, con la misma semilla (celdas 3 y 22). `random_strength` (4,707 en la celda 24) no llega al modelo
  publicado: `ModelConfigCB` (celda 21) no tiene ese campo, pydantic lo descarta
  y la celda 22 tampoco lo pasa. Aquí tampoco llega.

**Parches, con su motivo:**

1. **Sin imagen.** Motivo: los de «Quedan fuera», arriba.
2. **Sin procedencia.** Motivo: la decisión del 2026-09-25 (Fase 1).
3. **Nuestros pliegues y semillas.** El publicado usa sus propios pliegues y las
   semillas 1 a 9 (celda 22, `range(1, n_rounds)` con `n_rounds=10`). Motivo:
   que la comparación con M2 sea pareada.
4. **El número de árboles no se elige con el pliegue de validación.**
   - *Qué hace el publicado.* La celda 22 le pasa el pliegue de validación a
     CatBoost como `eval_set`. Con eso, `use_best_model`, que por defecto vale
     `True`, se queda con los árboles hasta la mejor iteración en validación. Y
     con `od_wait=100` el entrenamiento se detiene 100 iteraciones después; esto
     último se comprobó en CPU.
   - *Motivo.* Es la clase 10 del registro de incidentes: una elección que
     depende de las etiquetas, hecha en el pliegue que se reporta. El control lo
     muestra con datos sintéticos: con el ajuste publicado, barajar las etiquetas
     de validación hace que el modelo pase de 76 árboles a 7.
   - *Decisión de la persona.* La misma parada, sobre un 20 % del pliegue de
     entrenamiento: el primer pliegue de un `StratifiedGroupKFold` de 5,
     agrupado por paciente, estratificado y con la semilla externa, como la
     validación interna de M4b. El remuestreo va solo en el 80 % restante, igual
     que el publicado remuestrea el entrenamiento y no la evaluación. El modelo
     que sale predice el pliegue de validación.
   - *Descartado:* los 2000 árboles, sin parada.
5. **CPU en lugar de GPU.** Celda 22: `task_type='GPU'`, `devices='0'`. Motivo: el
   M4 no tiene GPU CUDA.
   - En CPU, el bootstrap por defecto es MVS, que no usa `bagging_temperature`,
     así que se fija `bootstrap_type='Bayesian'`. Según la documentación de
     CatBoost (`referencias/catboost-parametros-entrenamiento.md`), es el valor
     por defecto en GPU.
   - No se reproduce el AUC calculado cada 5 iteraciones en GPU (salida de la
     celda 25): en CPU, con la parada activa, se calcula en cada una.
   - Tampoco los demás valores por defecto ni la implementación propios de la
     GPU. M3 en CPU no es el mismo modelo que el de GPU, aunque tenga los mismos
     parámetros explícitos.
6. **Versiones.**
   - *catboost 1.2.8.* La 1.2.5 que fija el `requirements.txt` del ganador no
     importa con el numpy 2 de `.venv`, y la 1.2.6 y la 1.2.7 tampoco (probadas
     el 2026-09-26).
   - *scikit-learn 1.9.0*, frente a la 1.2.0 fijada. El k-means lleva `n_init=10`
     explícito, que era el valor por defecto en la corrida publicada: la celda
     18 muestra el aviso de que cambiaría. El estandarizado del LOF recibe la
     matriz de numpy, porque el scikit-learn actual rechaza el DataFrame con
     columnas repetidas. Son las mismas 17 columnas, y las dos repetidas siguen
     pesando doble.
   - *imbalanced-learn 0.14.2*: el `requirements.txt` no fija versión.

**Sesgos declarados, que no se corrigen:**

- Los hiperparámetros y `columns_to_drop` se eligieron con las variables de
  imagen presentes, como ya se dijo arriba.
- El notebook contiene un estudio de Optuna (celda 23, comentado) sobre
  `df_train`, todo el CSV de entrenamiento. No dice de dónde salen los valores
  de la celda 24 ni cómo se eligió `columns_to_drop`. Si salen de ahí, se
  eligieron con etiquetas que incluyen nuestros pliegues de validación y nuestro
  conjunto reservado. El sesgo va a favor de M3, y pesa también en la Fase 5.

**Nota de lectura, de la persona, fijada antes de correr:** "Los dos sesgos
conocidos favorecen a M3: los hiperparámetros y columnas descartadas pudieron
elegirse con Optuna sobre todo el conjunto de entrenamiento, que incluye a los
pacientes reservados, y las transformaciones sin etiqueta se ajustan con filas
de validación. Si M2 no queda por debajo de M3, la conclusión es conservadora;
si M3 gana, su ventaja no se puede separar de esos sesgos."

**Comparador fijado: M2** (decisión de la persona, 2026-09-26). Es el mejor de
los modelos principales en pAUC: M1 0,1375, M2 0,144 y M4 0,1375 de media en
desarrollo (`outputs/fase4-m2-vs-m1.json` y `outputs/fase4-m4-vs-m2.json`). M4b,
con 0,1496, queda fuera por ser secundaria.

**Reporte,** con `fase4_comparar.py`, como las otras comparaciones:
- pAUC, AUC, SEtop-15 y NNT80% SE de M3 y de M2;
- M3 − M2, con el intervalo ingenuo y el corregido por Nadeau y Bengio, y las
  victorias por pliegue y por semilla;
- el tiempo de entrenamiento por pliegue y el número de árboles de cada ajuste.

M2 se recalcula, y se comprueba que reproduce pliegue a pliegue
`outputs/fase4-m2-vs-m1.json`. La salida es `outputs/fase4-m3-vs-m2.json`.

**Orden de magnitud, no comparación.** La fila sin recortes de la Tabla 3 de
Kurtansky 2025, para malignidad: pAUC 0,164, AUC 0,957, NNT80% SE 63,62 y
SEtop-15 0,695. No es comparable con M3, por tres motivos:
- se midió en la evaluación privada del reto, entrenando con todo el CSV;
- su *Meta-basic* incluye *"hospital/institution"*, que M3 no usa;
- el NNT depende de la prevalencia del conjunto evaluado.

**Tiempo estimado.** Medido el 2026-09-26 en el M4, con 10 núcleos, sobre la
semilla 0 y el pliegue 0, sin calcular ninguna métrica:
- variables, 17 s, una sola vez;
- ajuste de un pliegue: 5,4 s con la parada fijada, que se quedó en 74 árboles,
  y 55,5 s sin parada;
- predicción de las 63 646 filas de validación: menos de 0,3 s.

Con M2, cuya mediana es de 1,2 s por pliegue (`outputs/fase4-m2-vs-m1.json`), la
corrida entera tarda unos 7 minutos con la parada fijada, si los otros
pliegues paran como este, y unos 48 sin parada.

**Control, corrido el 2026-09-26 antes de correr M3:** `test_ganador_m3.py`, 11
de 11. El código del ganador, con los parches 1 y 2 y `n_init=10`, se corrió sin
más cambios en el intérprete de 2024 sobre el conjunto de desarrollo. Contra
esa corrida:
- las 217 variables coinciden, con los NaN en los mismos sitios y una
  diferencia relativa máxima de 1,1e-13;
- los conglomerados son idénticos;
- el LOF coincide exactamente.

Los controles de que la comprobación puede fallar, en 60 pacientes:
- sin las columnas repetidas, el LOF se aparta hasta 0,692;
- con la estandarización dentro del paciente de M2, hasta 11,8.

**M3 limpio y regla de recomendación: decisión de la persona, fijadas el
2026-09-26 antes de correr.** El motivo es el hallazgo 7 de `CLAUDE.md`: la
ventaja de M3 sobre M2 no se puede separar de los dos sesgos conocidos a su
favor. M3 limpio es M3 con tres cambios; todo lo demás, igual.

1. **Transformaciones sin etiqueta dentro de cada pliegue.** La imputación de la
   edad, el one-hot, el estandarizado del LOF, el k-means y las medias por
   conglomerado se ajustan con las filas de entrenamiento del pliegue y se
   aplican a su validación. Las variables que se calculan dentro del paciente no
   cambian de forma: el z-score, los conteos, las sumas y el LOF de cada
   paciente. Cada paciente está en un solo lado del pliegue.
2. **Hiperparámetros por defecto de CatBoost, con la parada de M3.** La parada
   es la del 20 % interno agrupado por paciente, con `eval_metric='AUC'`,
   `od_wait=100` y `use_best_model=True`. Todo parámetro del constructor que no
   sea de parada, de especificación de datos (`cat_features`) o de ejecución
   (`random_seed`, `thread_count`, `verbose`) vuelve a su valor por defecto,
   incluido el tope de 1000 iteraciones y cualquier parámetro de pesos de clase.
   Lo que M3 hace fuera del constructor sigue igual, incluido el remuestreo.
3. **239 variables.** No se descartan las 22 de la celda 24.

**Parámetros de M3 que vuelven a su valor por defecto.** Los valores por
defecto se leyeron con `get_all_params()` en catboost 1.2.8, en CPU, el
2026-09-26:

| Parámetro | M3 | M3 limpio |
|---|---|---|
| `iterations` | 2000 | 1000 |
| `learning_rate` | 0,0261 | automática: la elige CatBoost según los datos, y se reporta |
| `l2_leaf_reg` | 18,04 | 3 |
| `grow_policy` | `Lossguide` | `SymmetricTree` |
| `min_data_in_leaf` | 38 | 1 |
| `border_count` | 256 | 254 |
| `bootstrap_type` | `Bayesian` (parche 5) | `MVS`, con `subsample` 0,8 |
| `bagging_temperature` | 0,874 | sin efecto: MVS no lo usa |
| `depth` | 6 | 6, el mismo valor |
| `loss_function` | `Logloss` | `Logloss`, el mismo valor |

Ni M3 ni M3 limpio usan pesos de clase.

**Control previo, del 2026-09-26.** Ninguna de las 22 columnas está entre las
15 que excluye `auditoria-de-fugas`. Todas se calculan solo con las 34
numéricas brutas de la celda 3 y con `patient_id`, así que tampoco dependen de
una columna excluida ni de la etiqueta.

**Lectura, declarada antes de correr.** M3 limpio difiere de M3 en tres cosas a
la vez, así que el resultado no dice cuál de los dos sesgos pesaba.

**Regla de recomendación.**
- Si el intervalo corregido de la pAUC de M3 limpio − M2 queda entero **por
  encima de cero**, el modelo recomendado es M3 limpio, y es el que se evalúa en
  el reservado.
- En cualquier otro caso, el modelo recomendado es M2, y el informe declara que
  la configuración publicada del ganador parecía mejor, pero su ventaja no se
  pudo separar de sus sesgos. Eso incluye el caso de que el intervalo quede
  entero por debajo de cero.
- Si queda entero por debajo de cero, el informe dice además que M3 limpio quedó
  por debajo de M2 de forma distinguible, sin atribuirlo a ninguno de los tres
  cambios frente a M3.

**Solo esta corrida.** No se prueban otras variantes.

**Reporte,** con `fase4_comparar.py`, en `outputs/fase4-m3limpio-vs-m2.json` y
`.md`:
- las cuatro métricas;
- M3 limpio − M2, con los dos intervalos y las victorias;
- los árboles y los tiempos;
- cuántos ajustes no se detuvieron antes del tope de 1000 árboles, y qué tasa
  de aprendizaje automática eligió CatBoost.

Nada de eso cambia la corrida.

**Modelo recomendado: decisión de la persona, 2026-09-26.** Regla aplicada: M3
limpio − M2 en pAUC, corregido [0,0021; 0,0341], queda entero por encima de
cero (`outputs/fase4-m3limpio-vs-m2.json`). El modelo recomendado es M3 limpio,
y es el que se evalúa en el reservado. Queda fijado aquí antes de abrirlo.

**Tiempo de inferencia, que cierra la Fase 4: especificación de la persona,
fijada el 2026-09-26 antes de medir.** Concreta la definición operativa de la
Fase 6.

- **Modelos:** M1, M2, M3 limpio, M4 y M4b. M3 queda fuera: no es candidato, y su
  camino de predicción reajusta transformaciones con las filas nuevas.
- **Subconjunto:** pacientes completos de desarrollo. Los `patient_id` de
  desarrollo, ordenados, se barajan con `numpy.random.default_rng(7)` y se van
  añadiendo en ese orden hasta sumar 5.000 lesiones o más. La lista de pacientes
  va en la salida.
- **Entrenamiento, que no se cronometra.** Cada modelo se entrena una vez con los
  demás pacientes de desarrollo, con su especificación de la Fase 4 y semilla 0.
  En M4b, las puntuaciones apiladas de entrenamiento salen de la validación
  interna, y la logística que puntúa el subconjunto es la ajustada con todo el
  entrenamiento.
- **Qué se cronometra.** Desde las filas de metadatos del subconjunto, ya en
  memoria y sin la etiqueta, hasta la puntuación de cada lesión. Para M4 y M4b
  se parte también de las imágenes tal como están en el archivo del que se
  extrajeron, `data/train-image.hdf5`. Entra todo lo que se calcula al predecir:
  - las variables por paciente, el LOF y la asignación a conglomerados;
  - las transformaciones ya ajustadas: imputación, codificación de
    categóricas, one-hot, estandarizado, medias por conglomerado y la
    logística de M4b;
  - la lectura y decodificación de imagen y DINOv2, con el mismo dispositivo
    (MPS), el preprocesado y el lote de 64 de la extracción;
  - y la predicción.

  Queda fuera cargar los modelos y los pesos de DINOv2, que se hace una vez
  antes del cronómetro.
- **Repeticiones:** cinco seguidas por modelo, en el mismo proceso. Se reportan
  las cinco y la mediana, en segundos por 1.000 lesiones.
- **Declaraciones:** el equipo, el sistema, el intérprete y las versiones con que
  corre cada modelo, el dispositivo de DINOv2 y los hilos.
- **Alcance:** los tiempos solo comparan estos modelos entre sí.

**Control, antes de cronometrar.** Si algo falla, no se cronometra. El camino
normal es el de la Fase 4, con el mismo modelo ya entrenado:
- en M1 y M2, `codificar_fold` y `variables_contexto_paciente`;
- en M3 limpio, `variables_m3_en_pliegue`;
- en M4 y M4b, además, las variables del archivo de la extracción y
  `puntuaciones_imagen`.

Qué se comprueba:
- **M1, M2 y M3 limpio:** las puntuaciones del camino cronometrado son idénticas
  a las del camino normal.
- **M4 y M4b, con tolerancia declarada:**
  - (a) las 384 variables que el camino cronometrado calcula con DINOv2 difieren
    de las de `data/dinov2-vits14-desarrollo.h5` en 1e-3 como máximo, en valor
    absoluto;
  - (b) con las variables del archivo en lugar de las recalculadas, las
    puntuaciones son idénticas a las del camino normal;
  - (c) con las recalculadas, se reportan la diferencia máxima de puntuación y
    cuántas lesiones difieren en más de 1e-6, sin umbral: una diferencia
    dentro de la tolerancia puede cambiar la rama de un árbol.
- **Pasos quitados.** La comprobación se repite quitando cada paso del camino
  cronometrado, uno por vez, y tiene que fallar cada vez. Esta parte corre sobre
  una copia del subconjunto a la que se le borra la edad de todos sus pacientes
  en los dos caminos, para que la imputación tenga efecto; sobre esa copia se
  comprueba también la igualdad. *Hasta el 2026-09-27 decía «de un paciente»:
  ver la enmienda de abajo.* Los pasos:
  - *M1:* imputación con las medianas de entrenamiento y codificación de las
    categóricas con las medias de entrenamiento;
  - *M2:* los de M1, las variables por paciente (z-scores, conteos y sumas) y el
    LOF;
  - *M3 limpio:* imputación de la edad, variables por paciente, one-hot,
    estandarizado y LOF, asignación al conglomerado y medias por conglomerado;
  - *M4:* los de M2, la lectura y decodificación de la imagen, el preprocesado y
    DINOv2;
  - *M4b:* los de M4, la logística de imagen y la razón a la media del paciente.

La salida es `outputs/tiempo-inferencia.json` y `.md`.

**Enmienda del control: decisión de la persona del 2026-09-27, antes de la
corrida oficial.** En una prueba de humo con 300 lesiones, sin cronometrar,
borrar la edad de un solo paciente no ejerció la imputación en M2 ni en M4:
quitarla no cambió ninguna puntuación. Las lesiones de ese paciente no pasan por
las divisiones donde el NaN y la mediana van a lados distintos. Por eso:
- en la copia se borra la edad de todos los pacientes del subconjunto, en los dos
  caminos;
- para el paso de imputación se compara, entre los dos caminos, la matriz que
  entra al modelo, no solo las puntuaciones: que una puntuación no cambie no
  prueba que el paso se ejecutó. Sin la imputación, esa comparación tiene que
  fallar en todos los modelos. Si aun así las puntuaciones de M2 o M4 no
  cambian, el control de ese paso queda cubierto por las matrices, y el reporte
  lo dice;
- en M3 limpio, sin la imputación, el LOF se niega a correr con la edad en NaN y
  la matriz no llega a formarse. Cuenta como fallo de la comparación y se
  registra el error.

Nada de esto toca lo que se cronometra.

**Puerta.** Las tres comparaciones principales fijadas en la decisión de arriba,
cada una con su intervalo corregido por Nadeau y Bengio: **M2 − M1**, **M4 − M2**
y **el mejor de los modelos propios frente a M3**. Con ellas, la lista de lo que
no se reprodujo del ganador y su motivo. *Hasta el 2026-09-25 la puerta pedía
dos intervalos: la diferencia contra el baseline tabular y contra la parte
tabular reproducida del ganador.*

**Riesgo.** La mejora no se distingue del baseline.

**Contingencia.** **Un resultado negativo también es resultado**, y el criterio
para declararlo está fijado *antes* de medir: si el intervalo corregido contiene
el cero, la recomendación al cliente es que la imagen no aporta lo suficiente
para justificar su costo, y eso se escribe con esa claridad. Lo que no se hace
es buscar la semilla, el pliegue o la métrica en que sí se distinga.

---

## Fase 4b — Intentar mejorar al modelo recomendado — CERRADA

**Estado: CERRADA (2026-10-22), decisión de la persona.** Su puerta se cumplió:
los tres `outputs/fase4b-*.json` y el resultado de la regla, escrito al final
de esta fase. Ningún candidato mejora a M3 limpio, que sigue siendo el modelo
recomendado.

**Decisión de la persona (2026-10-22).** Antes de abrir el conjunto reservado se
intenta mejorar a M3 limpio, la parte tabular reproducida de la solución
ganadora. Motivo de la persona: la Fase 4 comparó los modelos por separado y
sin ajustarlos, a propósito, para que las comparaciones fueran limpias, y no
probó combinarlos. Esta fase usa las reglas de la Fase 4, salvo la que levanta
abajo, y corrige por multiplicidad. El conjunto reservado sigue cerrado durante
toda la fase.

**Levanta la regla «Solo esta corrida» de la Fase 4.** Esa regla («M3 limpio y
regla de recomendación») decía que no se probarían otras variantes. Esta fase
la levanta, por decisión de la persona, y lo declara. Los tres candidatos se
eligieron conociendo los resultados de la Fase 4, incluida la pista de M4b
frente a M2 (por encima en 8 de 10 semillas, sin diferencia establecida). Por
eso los candidatos se fijan aquí antes de correr, la regla corrige por
multiplicidad y no se añaden candidatos después de ver resultados. La
corrección cubre los tres candidatos de esta fase, no las corridas de la
Fase 4; esa limitación también se declara. Se reabren además el modelo
recomendado que fijó la decisión del 2026-09-26 («Modelo recomendado», Fase 4)
y la especificación de la Fase 5, que pasan a depender de esta fase.

**Lectura declarada (2026-10-22).** Al verificar este borrador se leyeron cinco
columnas categóricas de `data/train-metadata.csv` completo, con las filas del
reservado incluidas, para contar sus categorías. No se leyó la etiqueta ni se
evaluó nada, y ese recuento ya estaba en el inventario de M3. Ninguna decisión
de esta fase depende de él.

**Qué se compara.** Tres candidatos, fijados aquí antes de correr ninguno, cada
uno contra M3 limpio:

- **C1 · Mezcla de M3 limpio y M2.** En cada pliegue de validación, la
  puntuación de C1 es el promedio simple de los rangos de las puntuaciones de
  M3 limpio y de M2, con pesos 1/2 y 1/2 fijos. No se ajusta ningún peso. El
  rango se calcula sobre las puntuaciones, sin etiquetas, y los empates
  reciben el rango promedio (`rankdata(method="average")`).
- **C2 · M3 limpio con la imagen apilada.** M3 limpio más las dos variables de
  imagen de M4b, construidas con el mismo código de M4b (Fase 4, «Variante
  secundaria M4b» y «Detalles de M4b»): la puntuación de la logística
  balanceada sobre las 384 variables de DINOv2, fuera de pliegue en
  entrenamiento con la validación interna de 5 pliegues agrupada por paciente,
  y esa puntuación dividida por su media dentro del paciente. Las dos variables
  se calculan sobre todas las filas del pliegue de entrenamiento antes del
  remuestreo de M3 limpio, y el remuestreo las arrastra como dos columnas más.
  En validación, la puntuación sale de la logística ajustada sobre todo el
  pliegue de entrenamiento, y la media del paciente se calcula sobre sus
  lesiones de validación. Todo lo demás de M3 limpio, igual.
- **C3 · Dos boostings sobre las variables de M3 limpio.** El promedio simple de
  los rangos de M3 limpio (CatBoost) y de un segundo modelo, ajustados en el
  mismo pliegue, con pesos 1/2 y 1/2 fijos y los empates como en C1. El segundo
  modelo es el del nivel 2b, sin cambios:
  `HistGradientBoostingClassifier(class_weight="balanced", random_state=semilla)`,
  con todo lo demás por defecto. Su parada temprana aparta al azar un 10 % del
  pliegue de entrenamiento, sin agrupar por paciente, como en M1 y M2. Cambian
  solo sus variables:
  - **Variables:** las de M3 limpio en cada pliegue, con las mismas
    transformaciones ajustadas en el pliegue de entrenamiento. Como el one-hot
    se ajusta en cada pliegue, son 239 en 40 de los 50 pliegues, 238 en 9 y 237
    en 1. Las columnas one-hot, que M3 limpio pasa a CatBoost como
    categóricas, entran aquí como números (0 y 1): son binarias, así que un
    corte da lo mismo.
  - **Desbalance:** solo los pesos de clase del nivel 2b. No se le aplica el
    remuestreo de M3 limpio, para no corregir el desbalance dos veces.
  No se instala ninguna librería nueva.

**Datos y pliegues.** El conjunto de desarrollo, con los pliegues de la Fase 4:
`construir_folds`, 5 pliegues, semillas 0 a 9. Las mismas cuatro métricas:
pAUC como principal; AUC estándar, sensibilidad top-15 y NNT80% SE como
secundarias.

**Regla, fijada antes de correr.** Hay tres candidatos, así que el intervalo se
corrige por multiplicidad con Bonferroni: confianza de 1 − 0,05/3, alrededor del
98,3 %, con la corrección de Nadeau y Bengio.
- Un candidato **mejora a M3 limpio** si el intervalo de su diferencia en la
  pAUC (candidato − M3 limpio) queda entero por encima de cero.
- Si mejora más de uno, se elige el de mayor diferencia media en la pAUC.
- Si ninguno mejora, M3 limpio sigue siendo el modelo recomendado.
- Las tres métricas secundarias se reportan con su intervalo, y no deciden.
- Si el elegido es C2, se reporta su tiempo de inferencia con el procedimiento
  de `tiempo-inferencia`, y la recomendación lo pone al lado de la mejora.
  Como referencia, M4b, que apila la imagen igual, tarda 14,6321 segundos por
  cada 1.000 lesiones (`tiempo-inferencia.json > tiempos.M4b`).

**Controles, antes de leer cualquier resultado.**
- M3 limpio y M2 reproducen pliegue a pliegue sus cifras de
  `outputs/fase4-m3limpio-vs-m2.json`.
- C2, de punta a punta: no hay predicciones guardadas de M4b, así que el mismo
  código que construye las variables de imagen de C2, aplicado sobre M2,
  reproduce pliegue a pliegue las cuatro métricas de M4b en
  `outputs/fase4-m4b-vs-m2.json`.
- C2, alineación: dentro de C2, en un pliegue, las dos columnas de imagen
  coinciden fila a fila con lo que devuelve `puntuaciones_imagen` para ese
  pliegue, antes y después del remuestreo.
- C3: el nivel 2b, con el mismo código de ajuste de C3 y sus 39 variables con
  la codificación de M1 (`codificar_fold`), reproduce pliegue a pliegue las
  cuatro métricas de M1 en `outputs/fase4-m2-vs-m1.json`.
- El promedio de rangos tiene control positivo: un modelo mezclado consigo
  mismo da su misma pAUC, y mezclado con ruido aleatorio da una pAUC menor.

**Salida.** `outputs/fase4b-c1-vs-m3limpio.json`,
`outputs/fase4b-c2-vs-m3limpio.json` y `outputs/fase4b-c3-vs-m3limpio.json`, con
su `.md`, con la misma estructura de los `fase4-*.json`, más el intervalo con la
corrección de Bonferroni.

**Qué no entra, con su motivo.**
- **Ajuste de hiperparámetros.** Exige una validación cruzada anidada; queda
  para otra fase si esta no basta.
- **Redes de imagen entrenadas sobre los recortes,** como las del ganador.
  Exigen un cómputo que no se ha estimado, y son el camino del escenario sin
  sistema de fotografía corporal total, no de este.
- **Candidatos nuevos después de ver resultados.** Si se quiere probar otro, va
  en una fase nueva, declarada, con su propia corrección.

**Consecuencia para la Fase 5.** La Fase 5 evalúa en el reservado el modelo que
deje esta fase, con M3 limpio y M2 como referencia. La recomendación queda
fijada antes de abrirlo y no cambia por su resultado.

**Puerta.** Los tres `outputs/fase4b-*.json` y la decisión que sale de la regla,
escrita en este archivo.

**Controles, corridos el 2026-10-22 antes de los candidatos.**
`test_fase4b_controles.py`, 10 semillas × 5 pliegues: 24 de 24 casos como se
esperaba, incluidos los que debían fallar. `test_fase4b_comparar.py`, con datos
sintéticos: 15 de 15. En las tres corridas, M3 limpio reproduce pliegue a pliegue
las cuatro métricas de `outputs/fase4-m3limpio-vs-m2.json`. En C2 la alineación
se cumplió en los 50 pliegues, y en C3 ninguna variable entró como categórica.

**Resultado de la regla (2026-10-22).** El intervalo corregido por Nadeau y
Bengio con la confianza de Bonferroni, 1 − 0,05/3, de candidato − M3 limpio en
la pAUC
(`comparaciones_nuevo_menos_base.pauc.intervalo_bonferroni_nadeau_bengio`):
- C1: [−0,0129; 0,008] (`outputs/fase4b-c1-vs-m3limpio.json`);
- C2: [−0,012; 0,0142] (`outputs/fase4b-c2-vs-m3limpio.json`);
- C3: [−0,012; 0,0101] (`outputs/fase4b-c3-vs-m3limpio.json`).

Ninguno queda entero por encima de cero, así que ningún candidato mejora a M3
limpio. M3 limpio sigue siendo el modelo recomendado, y la especificación de la
Fase 5 no cambia. C2 no se elige, así que no se mide su tiempo de inferencia.

---

## Fase 4c — Una red de imagen entrenada sobre los recortes — CERRADA

**Estado: CERRADA (2026-10-23), por su puerta:** los dos `outputs/fase4c-*.json`
y el resultado de la regla, escrito al final de esta fase. Por la regla, ni la
red sola mejora a la imagen sola ni C4 mejora a M3 limpio, que sigue siendo el
modelo recomendado.

**Decisión de la persona (2026-10-22).** En la Fase 4b, ninguna de las tres
combinaciones probadas mejoró a M3 limpio según su regla. De la solución
ganadora quedaron fuera sus redes de imagen entrenadas sobre los recortes
(Fase 4, «Quedan fuera, con su motivo»), y la Fase 4b las dejó fuera también
porque su costo no estaba estimado. Ahora está estimado el de una red pequeña,
EfficientNet-B0 a 128 × 128 (`outputs/prueba-tiempo-red-imagen.json`); el de
las redes del ganador, no. Esta fase entrena una red propia y responde dos
preguntas, fijadas antes de correr. El conjunto reservado sigue cerrado durante
toda la fase.

**Segunda ronda, declarada.** Es la segunda vez que se reabre la regla «Solo
esta corrida» de la Fase 4, después de la Fase 4b. Las preguntas se eligieron
conociendo los resultados de la Fase 4 y de la Fase 4b. Por eso se fijan aquí
antes de correr, se corrige por multiplicidad dentro de la fase y no se añaden
preguntas después de ver resultados. La fase reabre además dos condiciones, y
lo declara:
- la de la Fase 4, que dejó las redes para reconsiderarlas *«si esta fase
  muestra que la imagen aporta de forma distinguible»*, y eso no ocurrió
  (`CLAUDE.md`, hallazgos 5 y 6);
- la de la Fase 4b, que dio un segundo motivo: *«son el camino del escenario sin
  sistema de fotografía corporal total, no de este»*, y la pregunta 2 las prueba
  justo en ese escenario.

**La red.** EfficientNet-B0 de torchvision con sus pesos de ImageNet, que
cumplen el criterio de la Fase 2 (`referencias/efficientnet-b0-preentrenamiento.md`).
Se entrena de punta a punta, sin congelar capas.

**Cómo se entrena, fijado antes de correr y sin ajuste.**
- **Pliegues:** los de la Fase 4: `construir_folds`, 5 pliegues, semillas 0 a 9.
  Una red por semilla y pliegue: 50 entrenamientos.
- **Filas de entrenamiento:** todos los positivos del pliegue de entrenamiento
  y 20 negativos por cada positivo. En cada época se sortea una submuestra
  nueva de negativos, con la semilla externa, para que la red vea más
  negativos sin aumentar el número de imágenes por época.
- **Entrada, optimización y número de épocas:** los de la prueba de tiempo
  (`outputs/prueba-tiempo-red-imagen.json`): 128 × 128 píxeles, la
  normalización de ImageNet, el mismo optimizador, la misma tasa de
  aprendizaje, el mismo lote y 3 épocas.
- **Aumento de datos:** volteos horizontales y verticales al azar, solo en
  entrenamiento.
- **Puntuación:** la probabilidad de la red, la sigmoide de su salida, calculada
  en float64, para cada lesión del pliegue de validación. Cada lesión recibe, en
  cada semilla, la puntuación de la red del pliegue en que está en validación.
- **Registro:** las puntuaciones se guardan en `data/`, que no se versiona, con
  su procedencia, como las predicciones de la Fase 4b. Se registra el tiempo de
  cada entrenamiento, para ver si el equipo bajó su velocidad por temperatura.

**Pregunta 1 · ¿Entrenar una red mejora a la imagen sola?** Es el escenario sin
sistema de fotografía corporal total. Se compara «Red sola», la puntuación de
la red, con «Imagen» de `outputs/imagen-sola.json`, la logística sobre DINOv2,
en los mismos pliegues y en las cuatro métricas.

**Pregunta 2 · ¿La red apilada mejora a M3 limpio?** C4 es M3 limpio más dos
variables de la red: su puntuación y esa puntuación dividida por su media
dentro del paciente, como en M4b y en C2. Todo lo demás de M3 limpio, igual,
y las variables se calculan antes de su remuestreo, como en C2.
- **El atajo, declarado.** En las filas de entrenamiento de un pliegue, la
  puntuación de la red sale de redes que se entrenaron con ese pliegue de
  validación entre sus datos. Es apilar predicciones fuera de pliegue sin
  validación interna, como hizo el ganador, aunque él las sacó de una partición
  distinta de la de su CatBoost (semillas 42 y 1997 frente a 1 a 9); aquí se
  usan los mismos pliegues. Las semillas del ganador están en
  `NN-competition-train.ipynb`, celdas 5 y 10, en la copia local del
  repositorio (`referencias/_texto-completo/novoselskiy-2024-isic2024-repo/`),
  y en `top-model.ipynb`, celda 22, con `n_rounds=10`. Es menos estricto que la
  validación interna de M4b. Hacerlo con esa validación interna en las 10
  semillas costaría unas 24 horas: diez veces las 2,41 h del escenario (b), que
  es de una semilla (`outputs/prueba-tiempo-red-imagen.json >
  extrapolacion.b_1_semilla_x_5_pliegues_con_validacion_interna`).
- **Control del atajo, si hay tiempo.** En la semilla 0 se repite C4 con la
  validación interna de 5 pliegues de M4b, y se reporta cuánto cambia la pAUC
  por pliegue frente al atajo. Es descriptivo: no cambia la regla.

**Regla, fijada antes de correr.** Dos preguntas, así que el intervalo se
corrige con Bonferroni a una confianza de 1 − 0,05/2, con la corrección de
Nadeau y Bengio.
- La red sola mejora a la imagen sola si el intervalo de su diferencia en la
  pAUC queda entero por encima de cero.
- C4 mejora a M3 limpio si el intervalo de su diferencia en la pAUC queda
  entero por encima de cero.
- Las tres métricas secundarias se reportan con su intervalo, y no deciden.
- Si C4 mejora, se mide su tiempo de inferencia con el procedimiento de
  `tiempo-inferencia`, red incluida, y la recomendación lo pone al lado.

**Controles, antes de leer cualquier resultado.**
- **La red puede fallar:** en la semilla 0, pliegue 0, se barajan las etiquetas
  de todo el pliegue de entrenamiento, con la semilla 0, antes de elegir los
  positivos y los negativos, y se entrena la red. Pasa si su pAUC en validación
  cae dentro del 99 % central de la pAUC de 1.000 puntuaciones aleatorias sobre
  ese mismo pliegue de validación. Caso que debe fallar: una puntuación
  sintética hecha de las etiquetas más un poco de ruido queda fuera de ese
  rango. *Añadido por decisión de la persona (2026-10-22), antes de la corrida
  completa:* el control solo vale si la red con las etiquetas reales, la de
  reproducibilidad, queda claramente por encima de 0,02 con puntuaciones que
  varían; si da puntuaciones constantes, no se lanza la corrida. «Claramente
  por encima» se operó como por encima del límite superior de ese mismo rango,
  con más de un logit distinto y desviación mayor que cero; una puntuación
  constante es el caso que debe fallar.
- **Alineación:** en cada semilla, cada lesión del conjunto de desarrollo
  recibe exactamente una puntuación, la de su pliegue de validación, y las
  puntuaciones se unen por `isic_id`.
- **Reproducibilidad:** se entrena dos veces la misma red, semilla 0,
  pliegue 0, y se reporta si las puntuaciones coinciden. Si en MPS no son
  idénticas, se declara, y las puntuaciones guardadas son el registro.
- **Referencias:** M3 limpio sale de las predicciones guardadas en la Fase 4b,
  comprobadas contra su huella. La imagen sola se toma de las métricas por
  pliegue de `outputs/imagen-sola.json`, guardadas a 4 decimales; antes se
  comprueba la huella de los pliegues contra
  `fase4-m2-vs-m1.json > folds.sha256_por_semilla`, como hizo `imagen_sola.py`.
- **C4:** los controles de alineación de C2, antes y después del remuestreo.

**Salida.** `outputs/fase4c-red-sola-vs-imagen.json` y
`outputs/fase4c-c4-vs-m3limpio.json`, con su `.md`, con la estructura de los
`fase4b-*.json` y el intervalo de Bonferroni a 1 − 0,05/2.

**Qué no entra, con su motivo.**
- **Otras redes, más épocas o el ajuste de hiperparámetros.** No hay tiempo de
  cómputo para compararlos con honestidad, y cada uno sería otra pregunta.
- **Fotos de teléfono.** El proyecto no tiene esos datos; la red se mide sobre
  los recortes del sistema de fotografía corporal total.
- **Preguntas nuevas después de ver resultados.** Irían en otra fase, declarada.

**Consecuencia para la Fase 5.** Si C4 mejora a M3 limpio, la Fase 5 evalúa C4
en el reservado, con la red entrenada sobre todo el conjunto de desarrollo, y
con M3 limpio y M2 como referencia. De dónde salen las variables de red de las
filas de entrenamiento de C4 se fija antes de abrir el reservado. Si no, la
Fase 5 no cambia. La pregunta 1 no cambia el modelo recomendado: informa la
recomendación para el escenario sin sistema de fotografía corporal total.

**Puerta.** Los dos `outputs/fase4c-*.json` y la decisión que sale de la regla,
escrita en este archivo.

**Controles, corridos antes de las preguntas.** `test_fase4c_controles.py`
completo, el 2026-10-22, antes de las 50 redes: 23 de 23 casos como se
esperaba, incluidos los que debían fallar (`data/fase4c-controles.json`, que no
se versiona). En la semilla 0, pliegue 0, sobre toda la validación:
- la red con las etiquetas barajadas dio una pAUC de 0,0224, dentro del rango
  del azar [0,0092; 0,0387], con 63.445 logits distintos;
- la red con las etiquetas reales dio 0,12, por encima del rango, con 63.440
  logits distintos;
- sus dos entrenamientos dieron logits idénticos en MPS.

La red principal de ese pliegue da la misma pAUC, 0,12
(`outputs/fase4c-red-sola-vs-imagen.json`). Tras la corrección de abajo, el
2026-10-23: 26 de 26 (`data/fase4c-controles-2.json`), con los que se
entrenaron las redes internas. En la pregunta 2, M3 limpio reprodujo pliegue a
pliegue `outputs/fase4-m3limpio-vs-m2.json`, y la alineación de C4 se cumplió en
los 50 pliegues.

**Una corrección durante la corrida (2026-10-23).** La primera corrida de la
pregunta 2 se detuvo en la semilla 2, en el guardián de `fase4c.variables_red`.
Una lesión recibe de la red de su pliegue un logit de −2674,47, cuya sigmoide
en float64 es 0 exacto; en las otras nueve semillas su logit va de −10,81 a
−0,53. El guardián exigía que todas las puntuaciones fueran positivas, más de
lo que la razón por paciente necesita: con la especificación de arriba, la
razón de esa lesión es 0. Ahora se detiene solo si hay puntuaciones negativas o
faltantes, o si un paciente tiene todas las suyas en 0 (commit «Fase 4c: la
razón por paciente admite una puntuación 0»). La corrección no depende de
ningún resultado de desempeño, y las 50 redes no se volvieron a entrenar:
`entrenar_y_puntuar` y `probabilidad` no cambiaron, aunque su procedencia
registra el SHA-256 anterior de `fase4c.py`. Las dos preguntas, las redes
internas y el atajo se corrieron con el código corregido.

**Tiempo de cada entrenamiento.** Por red, con su predicción: mediana 270,1 s,
de 262,6 a 403,7 s (`puntuaciones_de_la_red.segundos_por_red` en los dos
`outputs/fase4c-*.json`). Las cinco primeras tardaron de 335,8 a 378,1 s, y las
cinco últimas, de 263,8 a 266,9 s (`data/fase4c-puntuaciones-red.json >
redes`). Las 50 redes, 14.891 s en total.

**Resultado de la regla (2026-10-23).** El intervalo corregido por Nadeau y
Bengio con la confianza de Bonferroni, 1 − 0,05/2, de la diferencia en la pAUC
(`comparaciones_nuevo_menos_base.pauc.intervalo_bonferroni_nadeau_bengio`):
- pregunta 1, red sola − imagen sola: [−0,0037; 0,0611]
  (`outputs/fase4c-red-sola-vs-imagen.json`);
- pregunta 2, C4 − M3 limpio: [−0,003; 0,0164]
  (`outputs/fase4c-c4-vs-m3limpio.json`).

Ninguno queda entero por encima de cero, así que, por la regla, la red sola no
mejora a la imagen sola y C4 no mejora a M3 limpio. M3 limpio sigue siendo el
modelo recomendado, y la especificación de la Fase 5 no cambia. C4 no mejora,
así que no se mide su tiempo de inferencia. Las tres métricas secundarias están
en los dos archivos, con su intervalo, y no deciden.

**Control del atajo, descriptivo.** En la semilla 0, la pAUC de C4 con la
validación interna de M4b menos la de C4 con el atajo, por pliegue: 0,0012,
0,0021, 0,0062, 0,0024 y 0,0063; media 0,0037 (`outputs/fase4c-control-atajo.json`).
No cambia la regla. Su salida, `outputs/fase4c-control-atajo.json` y `.md`, se
añade a las dos de «Salida».

---

## Fase 4d — Acercarse al ganador con estadística y con el equipo propio — CERRADA

**Estado: CERRADA (2026-10-31), por su puerta:** los tres `outputs/fase4d-*.json`
de las preguntas, la decisión de Holm, los controles de la comparación, la
bitácora al día y el resultado de la regla, escrito al final de esta fase. Holm
no acepta ninguna de las tres preguntas: ni C5 ni C6 mejoran a M3 limpio, que
sigue siendo el modelo recomendado, y la red mejorada no mejora a la de la Fase
4c.

**Decisión de la persona (2026-10-30).** El docente, en la retroalimentación
del avance, planteó el reto: acercarse al ganador, o mejorarlo, con
estadística y con el cómputo disponible, antes de alquilar cómputo. Esta fase
sale de una investigación hecha el 2026-10-29, que se versiona como nota de
trabajo y no como fuente, en
`informe/insumos/investigacion-acercarse-al-ganador.md`. Sus citas valen solo
después de cotejarlas con el texto original en `referencias/`, y su cabecera
dice qué se cotejó y qué no se sostuvo. El conjunto reservado sigue cerrado
durante toda la fase. Como en las fases 4b y 4c, el modelo recomendado y la
especificación de la Fase 5 pasan a depender de esta fase.

**Tercera ronda, declarada.** Es la tercera vez que se reabre la regla «Solo
esta corrida» de la Fase 4, después de las fases 4b y 4c. Las preguntas se
eligieron conociendo los resultados de las fases 4, 4b y 4c, incluido que C4
quedó por encima de M3 limpio en las 10 semillas sin diferencia establecida.
Por eso se fijan aquí antes de correr, se corrige por multiplicidad dentro de la
fase y no se añaden preguntas después de ver resultados.

**Lectura declarada (2026-10-30).** Al verificar el borrador de esta fase se
calcularon, sobre las 50 diferencias guardadas de C4 − M3 limpio
(`outputs/fase4c-c4-vs-m3limpio.json`), su valor p de Nadeau y Bengio y el
control negativo que proponía el borrador (decisión 1, abajo). Los dos se
registran en `outputs/fase4d-controles-comparacion.json` al correr los
controles. No se calculó nada de C5, de la red mejorada ni de C6.

**Bitácora de intentos.** Todos los modelos comparados por la pAUC desde la
Fase 4, con su comparación y el resultado de su regla. Una afirmación del tipo
«el mejor de» cuenta todos los intentos, no solo los de la última ronda: hasta
esta fase son 13 comparaciones, y esta añade 3. «NB 95 %» es el intervalo
corregido por Nadeau y Bengio al 95 % (`intervalo_t_95_nadeau_bengio`); el de
la regla, cuando es otro, va en su columna.

| Modelo | Fase | Comparación | Diferencia de pAUC | NB 95 % | Intervalo de la regla | Resultado | Archivo |
|---|---|---|---|---|---|---|---|
| M1 | 4 | referencia de M2 | — | — | — | — | `fase4-m2-vs-m1.json` |
| M2 | 4 | M2 − M1 | +0,0065 | [−0,0147; 0,0276] | el mismo | no distinguible | `fase4-m2-vs-m1.json` |
| M4 | 4 | M4 − M2 | −0,0065 | [−0,0263; 0,0133] | el mismo | no distinguible | `fase4-m4-vs-m2.json` |
| M4b | 4 | M4b − M2 | +0,0056 | [−0,0091; 0,0202] | el mismo | no distinguible | `fase4-m4b-vs-m2.json` |
| M3 | 4 | M3 − M2 | +0,0185 | [0,0007; 0,0364] | el mismo | por encima, con sus dos sesgos | `fase4-m3-vs-m2.json` |
| M3 limpio | 4 | M3 limpio − M2 | +0,0181 | [0,0021; 0,0341] | el mismo | por encima: modelo recomendado | `fase4-m3limpio-vs-m2.json` |
| Imagen | 6, descriptiva | Imagen − M1 | −0,0579 | [−0,084; −0,0319] | el mismo | por debajo; no decide | `imagen-sola.json` |
| Imagen + básicos | 6, descriptiva | (Imagen + básicos) − Imagen | +0,0045 | [0,0; 0,0089] | el mismo | no se da por establecida | `imagen-sola.json` |
| C1 | 4b | C1 − M3 limpio | −0,0025 | [−0,0109; 0,006] | [−0,0129; 0,008] | no mejora | `fase4b-c1-vs-m3limpio.json` |
| C2 | 4b | C2 − M3 limpio | +0,0011 | [−0,0095; 0,0117] | [−0,012; 0,0142] | no mejora | `fase4b-c2-vs-m3limpio.json` |
| C3 | 4b | C3 − M3 limpio | −0,0009 | [−0,0099; 0,008] | [−0,012; 0,0101] | no mejora | `fase4b-c3-vs-m3limpio.json` |
| Red sola | 4c | Red − Imagen | +0,0287 | [0,0006; 0,0569] | [−0,0037; 0,0611] | no mejora | `fase4c-red-sola-vs-imagen.json` |
| C4 | 4c | C4 − M3 limpio | +0,0067 | [−0,0018; 0,0151] | [−0,003; 0,0164] | no mejora | `fase4c-c4-vs-m3limpio.json` |
| C4 con validación interna | 4c, descriptiva | C4 interna − C4 con el atajo, semilla 0 | +0,0037 de media en 5 pliegues | — | — | sin intervalo; no decide | `fase4c-control-atajo.json` |
| C5 | 4d | C5 − M3 limpio | +0,0039 | [−0,005; 0,0127] | Holm: valor p 0,3859 frente a 0,05 | no mejora | `fase4d-c5-vs-m3limpio.json` |
| Red mejorada | 4d | Red mejorada − Red de la 4c | −0,0156 | [−0,0318; 0,0005] | Holm: valor p 0,05741 frente a 0,01667 | no mejora | `fase4d-red-mejorada-vs-red.json` |
| C6 | 4d | C6 − M3 limpio | +0,005 | [−0,0031; 0,0131] | Holm: valor p 0,2172 frente a 0,025 | no mejora | `fase4d-c6-vs-m3limpio.json` |

Los archivos están en `outputs/`. Las 13 comparaciones son las 14 filas
anteriores a esta fase menos M1, que es una referencia. El intervalo de la regla
es el de Bonferroni a 1 − 0,05/3 en la Fase 4b y a 1 − 0,05/2 en la 4c. En la
4d la regla no usa un intervalo: la columna da el valor p de cada pregunta y su
umbral de Holm (`outputs/fase4d-holm.json`). En la
Fase 4, la regla de recomendación era la de M3 limpio − M2; las demás
comparaciones de esa fase seguían su propio criterio, fijado antes de medir.

**Lo que cambia en la forma de comparar.**
- **Holm en vez de Bonferroni** dentro de la fase. Cada pregunta da un valor p
  bilateral de la prueba t corregida de Nadeau y Bengio, la misma con que se
  calcularon los intervalos de las fases anteriores: la varianza de las
  diferencias multiplicada por (1/n + 1/(k − 1)), con k = 5 pliegues, y n − 1
  grados de libertad. Los tres valores p, ordenados de menor a mayor, se
  comparan con 0,05/3, 0,05/2 y 0,05; Holm acepta una pregunta solo si pasan
  también todas las anteriores en ese orden. **Una pregunta da su resultado a
  favor si Holm la acepta y además su diferencia media en la pAUC es
  positiva** (decisión 3). Se reportan además los intervalos al 95 %.
- **Unidad de lectura.** Cada pAUC se reporta también dividida por 0,2, como la
  especificidad media cuando la sensibilidad recorre de 0,8 a 1. Se verificó
  contra el código oficial de la métrica
  (`referencias/isic-primary-metric-pauc.py.md`): el script invierte las
  etiquetas (líneas 42 y 43), así que el área que integra es la de la
  especificidad sobre la sensibilidad entre 0,8 y 1, con la curva ROC
  interpolada linealmente entre sus puntos. En 40 casos sintéticos, con
  empates, el script oficial y `pauc_above_tpr` dieron lo mismo, y 0,2 veces la
  especificidad media difirió en 3,2e-7 como máximo, el error de la integración
  numérica; un clasificador perfecto da 0,2, y uno al azar, en teoría, 0,02. La
  comprobación numérica la repite `test_fase4d_comparacion.py`.
- **Control negativo de la comparación (decisión 1).** 1.000 juegos sintéticos
  de diferencias con media 0, con la correlación entre ellas que la corrección
  supone, 0,2. Se generan juegos de 50 diferencias, como la pregunta 1, y de
  25, como las preguntas 2 y 3. La prueba corregida tiene que rechazar al 5 %
  **a lo sumo el 5 % de las veces**, con el error de Monte Carlo: 62 de 1.000
  como máximo. Caso que debe fallar: la t sin corregir.
- **Control positivo de la comparación (decisión 2).** Sobre las predicciones
  guardadas de M3 limpio, se suben en la escala del logit las puntuaciones de
  los positivos de cada pliegue de validación, con el mismo desplazamiento en
  todos, hasta que la diferencia media de la pAUC con M3 limpio sea de +0,02
  (±0,002). La comparación completa tiene que dar un valor p por debajo de
  0,05/3, el umbral más estricto de Holm, en las 10 semillas y en las semillas
  0 a 4. Caso que debe fallar: el mismo desplazamiento con el signo contrario
  no puede dar un resultado a favor.

**Pregunta 1 · C5 frente a M3 limpio.** C5 es C4 con las variables que el
código del ganador construye sobre cada puntuación de imagen, sin el hospital,
y con ruido en el apilado. Las variables vienen del código del ganador; el
ruido, de un resumen secundario.
- **Contexto por zona y edad** (celda 17 de `top-model.ipynb`, decisión 6). El
  ganador estandariza cada puntuación de imagen dentro de los grupos
  `attribution` × `tbp_lv_location` × `age_approx`. Sin el hospital,
  `attribution`, porque las columnas de procedencia se excluyeron en la Fase 1,
  quedan `tbp_lv_location` × `age_approx`. Se ajusta con las filas de
  entrenamiento de cada pliegue y se aplica a su validación.
- **Contexto por conglomerado** (celda 19, decisión 5). El ganador estandariza
  también, dentro de cada uno de los 29 conglomerados de k-means, la
  puntuación, su razón a la media del paciente y la puntuación estandarizada
  por grupo. C5 lo hace con el k-means que M3 limpio ya ajusta en el pliegue de
  entrenamiento.
- **Ruido en el apilado** (decisión 4). En las filas de entrenamiento, a la
  puntuación estandarizada por zona y edad se le suma ruido normal de media 0 y
  desviación 0,1, con la semilla externa; en validación, sin ruido. Viene de un
  resumen secundario de la solución ganadora
  (`referencias/zenn-2g-2024-isic2024-resumen-soluciones.md`), que dice que
  las predicciones del modelo de imagen se usan estandarizadas y que se les
  suma un ruido de desviación 0,1 para no sobreajustar. No está en el código
  público del ganador, y la versión de esta fase es nuestra: se declara así.
- Todo lo demás, igual a C4: las mismas puntuaciones de la red guardadas en la
  Fase 4c, la misma razón a la media del paciente y el mismo atajo declarado.
  C5 tiene seis variables de la red: la puntuación y la razón de C4, la
  puntuación estandarizada por zona y edad, y las tres estandarizadas por
  conglomerado.
- 10 semillas × 5 pliegues. Solo usa el procesador.

**Pregunta 2 · La red mejorada frente a la red de la Fase 4c.** La misma
EfficientNet-B0 a 128 × 128, con el mismo optimizador, la misma tasa, el mismo
lote y los mismos volteos. Cambian solo dos cosas:
- **15 épocas** en vez de 3, fijas, sin mirar la validación entre épocas.
- **Negativos en bloques.** La red de la Fase 4c sorteaba en cada época una
  submuestra nueva de 20 negativos por positivo, y dos épocas podían repetir
  negativos. Ahora los negativos del pliegue de entrenamiento se reparten al
  azar, con la semilla externa, en bloques de 20 por cada positivo, y cada
  época usa un bloque distinto, sin repetir mientras queden bloques nuevos. Con
  unos 254 positivos y unos 254.000 negativos por pliegue de entrenamiento
  salen unos 50 bloques, así que las 15 épocas no repiten ninguno. Los
  negativos que no llenan un bloque no se usan.
- **De dónde sale.** El 10.º puesto
  (`referencias/tomo20180402-2024-isic2024-10mo-puesto.md`), con una
  EfficientNet-B0 a 128 píxeles como única red de imagen, escribe *"In the 1st
  stage, divide into 20 datasets and switch for each epoch (n_epoch=20)"* y
  *"Avoid early stopping"*. Esta fase toma las dos ideas, cambiar de bloque en
  cada época y fijar las épocas, pero no sus números: sus bloques son la
  vigésima parte de los negativos y aquí son de 20 por positivo, entrena 20
  épocas y aquí 15, y usa aumentos que aquí no se usan.
- **Semillas 0 a 4:** 25 redes. Se compara con la red de la Fase 4c en los
  mismos 25 pliegues, en las cuatro métricas.
- **Costo estimado.** Con los tiempos de la Fase 4c, una mediana de 35,4 s por
  época y unos 158 s de predicción por red (`data/fase4c-puntuaciones-red.json
  > redes`), una red de 15 épocas tarda unos 710 s. Las 25 redes, unas 5
  horas, y las tres redes de control, unos 36 minutos más.

**Pregunta 3 · C6 frente a M3 limpio.** C6 es C5 con la red mejorada en lugar
de la red de la Fase 4c: las mismas variables, el mismo ruido y el mismo atajo.
Se calcula cuando termina la pregunta 2, en las semillas 0 a 4.

**Regla, fijada antes de correr.** Una pregunta da su resultado a favor si Holm
la acepta en la pAUC y su diferencia media es positiva, como se describe arriba.
Las tres métricas secundarias se reportan con su intervalo y no deciden. Si C5
o C6 dan su resultado a favor, se mide su tiempo de inferencia con el
procedimiento de `tiempo-inferencia`, red incluida. La pregunta 2, por sí sola,
no cambia el modelo recomendado: informa la recomendación para el escenario sin
sistema de fotografía corporal total.

**Controles, antes de leer cualquier resultado.**
- Los de la comparación, arriba, y los casos de Holm: con valores p
  sintéticos, que se detiene en la primera pregunta que no pasa y que una
  diferencia negativa no da resultado a favor.
- **C5:**
  - la referencia C4 se reproduce pliegue a pliegue desde
    `outputs/fase4c-c4-vs-m3limpio.json`, en las cuatro métricas;
  - los controles de alineación de C2 y C4, extendidos a las seis variables de
    la red, antes y después del remuestreo;
  - la estandarización por zona y edad coincide con la de la celda 17 sin el
    hospital, calculada con pandas sobre las filas de entrenamiento; caso que
    debe fallar: calcularla con el entrenamiento y la validación juntos, como el
    ganador, cambia las filas de validación;
  - la asignación a conglomerados reproduce las variables por conglomerado que
    M3 limpio ya calcula; caso que debe fallar: con las etiquetas de
    conglomerado barajadas, no las reproduce;
  - el ruido va solo a las filas de entrenamiento, con desviación cercana a 0,1,
    y se repite con la misma semilla; caso que debe fallar: con ruido también en
    validación, se detecta.
- **Red mejorada:** los de la Fase 4c, con 15 épocas (etiquetas barajadas, red
  real por encima del azar, reproducibilidad y alineación), y además:
  - cada época usó un bloque de negativos distinto, sin ningún negativo en dos
    épocas; caso que debe fallar: los sorteos de la Fase 4c repiten negativos
    entre épocas;
  - fuera de la elección de los negativos, el entrenamiento es el de la Fase 4c:
    con los sorteos de la Fase 4c, una época da los mismos logits que
    `fase4c.entrenar_y_puntuar`; caso que debe fallar: con los bloques, no.

**Salida.**
- `outputs/fase4d-c5-vs-m3limpio.json`, `outputs/fase4d-red-mejorada-vs-red.json`
  y `outputs/fase4d-c6-vs-m3limpio.json`, con su `.md` y la estructura de los
  `fase4c-*.json`, más el valor p de Nadeau y Bengio de cada métrica y la pAUC
  dividida por 0,2.
- La decisión de Holm, en `outputs/fase4d-holm.json` y `.md`, que lee los tres.
- Los controles de la comparación, en `outputs/fase4d-controles-comparacion.json`
  y `.md`.
- Los controles de las redes y de C5, en `data/fase4d-controles.json`, y las
  puntuaciones de la red mejorada, en `data/fase4d-puntuaciones-red-mejorada.csv.gz`,
  con su procedencia; `data/` no se versiona.

**Qué no entra, con su motivo.**
- **El hospital** en la estandarización, por la exclusión de la Fase 1.
- **Objetivos auxiliares con `iddx`** para la red: son columnas que solo existen
  en entrenamiento; usarlos sería otra pregunta.
- **Los aumentos del 10.º puesto** y el **ensamble por rangos** del resumen
  secundario: cada uno sería otra pregunta.
- **Ajuste de hiperparámetros:** solo con validación anidada, en otra fase. La
  nota de trabajo propone también BBC-CV; su fuente no está en `referencias/`.
- **El margen de no inferioridad frente al ganador:** se fija antes de abrir el
  reservado, en la especificación de la Fase 5.

**Consecuencia para la Fase 5.** Si C5 o C6 dan su resultado a favor, la Fase 5
evalúa el que lo dio, con M3 limpio y M2 como referencia. Si lo dan los dos, se
elige el de mayor diferencia media en la pAUC en las semillas 0 a 4, las que
tienen los dos. De dónde salen las variables de la red de sus filas de
entrenamiento se fija antes de abrir el reservado. Si ninguno lo da, la Fase 5
no cambia.

**Puerta.** Los tres `outputs/fase4d-*.json` de las preguntas, la decisión de
Holm, el archivo de controles de la comparación, la bitácora de intentos al día
y la decisión que sale de la regla, escritos en este archivo.

**Cómo quedaron las seis decisiones de la verificación (2026-10-30).** El
borrador de esta fase se verificó frase por frase contra este archivo, el
código, `outputs/` y el código del ganador. Seis cosas no se sostenían o
quedaban sin fijar. La persona aprobó las seis correcciones, con tres criterios
suyos, y así quedaron:
1. **Control negativo.** El borrador intercambiaba al azar, dentro de cada
   pliegue, las puntuaciones de los dos modelos, y esperaba alrededor del 5 % de
   rechazos. Intercambiarlas solo invierte el signo de la diferencia de ese
   pliegue y quita la correlación entre pliegues que la corrección supone:
   sobre las 50 diferencias de C4 − M3 limpio, la prueba corregida no rechazaba
   nunca, y la t sin corregir rechazaba cerca del 5 %. Ninguna de las dos podía
   fallar. Queda el control sintético de arriba. *Criterio de la persona:* «a lo
   sumo 5 %» de rechazos; el control positivo es el que demuestra que la prueba
   detecta diferencias reales, y el «alrededor del 5 %» del borrador era un
   error. «A lo sumo 5 %» se lee con el error de Monte Carlo: con una tasa real
   del 5 %, pasar de 62 rechazos en 1.000 tiene una probabilidad del 3,8 %.
2. **Control positivo.** El borrador no fijaba el tamaño de la diferencia ni qué
   contaba como detectarla. Queda el de arriba: +0,02 en la pAUC, valor p por
   debajo de 0,05/3, y el signo contrario como caso que debe fallar.
3. **Dirección de Holm.** Con valores p bilaterales, una diferencia negativa
   también pasa Holm. *Criterio de la persona:* valores p bilaterales, como los
   intervalos de las fases anteriores, y una pregunta pasa solo si Holm la
   acepta y además su diferencia media es positiva.
4. **El ruido.** El borrador no fijaba a qué variable iba. *Criterio de la
   persona:* copiar exactamente lo que hace el código del ganador, quitando
   solo el hospital, y como el ruido no está en su código, fijar la versión más
   simple y declararla. Queda así: ruido normal de media 0 y desviación 0,1,
   sumado a la puntuación estandarizada por zona y edad; solo en las filas de
   entrenamiento; con `numpy.random.default_rng` y la semilla externa, sorteado
   en el orden de esas filas. Se suma después de calcular las seis variables,
   así que la estandarizada por conglomerado sale de la puntuación sin ruido, y
   antes del remuestreo de M3 limpio, que lo arrastra. La puntuación y su razón
   quedan sin ruido, como en C4.
5. **Contexto por conglomerado.** La celda 19 del ganador estandariza también,
   dentro de los conglomerados, la puntuación, su razón y la estandarizada por
   grupo, y el borrador ni lo incluía ni lo excluía. *Criterio de la persona:*
   copiar el código del ganador. Entra, como en la celda 19: la media y la
   desviación de cada conglomerado se calculan con las filas de entrenamiento,
   con las etiquetas del k-means que M3 limpio ajusta en el pliegue, y con la
   misma regla de NaN que la decisión 6.
6. **Contexto por zona y edad.** El borrador decía «zona del cuerpo», que en
   este proyecto es `anatom_site_general` («Imagen + básicos»). El ganador usa
   `tbp_lv_location`. *Criterio de la persona:* copiar la celda 17, quitando
   solo el hospital. Queda así:
   - los grupos son `tbp_lv_location` × `age_approx`;
   - la edad es la imputada como en M3 limpio, con la mediana del pliegue de
     entrenamiento;
   - la media y la desviación son las de pandas, con ddof = 1;
   - la variable es la puntuación menos la media de su grupo, dividida por la
     desviación;
   - queda en NaN si el grupo no tiene filas de entrenamiento, si tiene una sola
     o si su desviación es 0. Con pandas, el ganador obtiene NaN en los dos
     últimos casos; el primero no le ocurre, porque calcula sobre todas las
     filas.

   Esa es la otra diferencia con el ganador, ya prevista en el borrador: él
   calcula los grupos y los conglomerados con todas las filas, entrenamiento y
   validación juntas, y aquí se ajustan con el entrenamiento del pliegue, como
   todo lo que M3 limpio ajusta. La razón a la media del paciente es la de C4,
   que coincide con la del ganador (celda 15) porque los pliegues agrupan por
   paciente.

Además se aplicaron estas precisiones de la verificación:
- la frase sobre el origen de las variables, que decía «tomados del código del
  ganador» también para el ruido;
- la cita del 10.º puesto en la pregunta 2;
- las fichas del 10.º puesto y del resumen secundario en `referencias/`;
- la bitácora completa, con M1, la imagen sola y el control del atajo;
- la elección entre C5 y C6 en las semillas comunes;
- y el costo estimado.

**Controles, corridos antes de las preguntas.**
- **Los de la comparación:** `test_fase4d_comparacion.py` completo, el
  2026-10-30, con 19 de 19 casos como se esperaba
  (`outputs/fase4d-controles-comparacion.json`).
- **Los de las redes y de C5:** `test_fase4d_controles.py` completo, el mismo
  día, antes de la pregunta 1 y de las redes. Dio 34 de 34 casos como se
  esperaba, incluidos los que debían fallar, en 2.420,5 s
  (`data/fase4d-controles.json`, que no se versiona). En la semilla 0, pliegue
  0, sobre toda la validación:
  - con las etiquetas barajadas, la red mejorada dio una pAUC de 0,0141,
    dentro del rango del azar [0,0092; 0,0387];
  - con las etiquetas reales dio 0,092, sin ningún negativo en dos épocas;
  - sus dos entrenamientos dieron logits idénticos.

  La red principal de ese pliegue da la misma pAUC, 0,092
  (`outputs/fase4d-red-mejorada-vs-red.json`).
- **Las reproducciones:** M3 limpio reprodujo pliegue a pliegue
  `outputs/fase4-m3limpio-vs-m2.json` en las preguntas 1 y 3, C4 reprodujo
  `outputs/fase4c-c4-vs-m3limpio.json` en la 1, y la red de la Fase 4c
  reprodujo `outputs/fase4c-red-sola-vs-imagen.json` en la 2.
- **Los mismos controles en todo:** las tres salidas registran los mismos dos
  archivos de controles, con su SHA-256.

**La corrida, en dos tandas.** La persona la detuvo el 2026-10-30 a las 21:09.
Estaban terminadas la pregunta 1 y 11 de las 25 redes, guardadas en
`data/fase4d-redes/`: las semillas 0 y 1 completas y la semilla 2, pliegue 0.
La red que se entrenaba, semilla 2, pliegue 1, no había escrito nada. El 2026-10-31 se
reanudó con el mismo código commiteado:
- las 11 redes se leyeron sin volver a entrenarlas, después de comprobar el
  SHA-256 de su código y de sus puntuaciones;
- se entrenaron las 14 restantes;
- los controles no se volvieron a correr.

La procedencia de las puntuaciones registra el comando de la segunda tanda, y
su `segundos_total`, 9.805,6 s, es solo el de esa tanda.

**Tiempo de cada entrenamiento.** Por red, con su predicción: mediana 697,7 s,
de 682,3 a 802,2 s (`data/fase4d-puntuaciones-red-mejorada.json >
segundos_por_red`), frente a los 710 s estimados. Las 25 redes, 17.581,9 s en
total.

**Resultado de la regla (2026-10-31).** Holm sobre los valores p bilaterales de
Nadeau y Bengio de la pAUC (`outputs/fase4d-holm.json`), de menor a mayor:
- pregunta 2, red mejorada − red de la Fase 4c: −0,0156 [−0,0318; 0,0005];
  valor p 0,05741 frente a 0,05/3 = 0,01667
  (`outputs/fase4d-red-mejorada-vs-red.json`);
- pregunta 3, C6 − M3 limpio: +0,005 [−0,0031; 0,0131]; valor p 0,2172 frente
  a 0,025 (`outputs/fase4d-c6-vs-m3limpio.json`);
- pregunta 1, C5 − M3 limpio: +0,0039 [−0,005; 0,0127]; valor p 0,3859 frente
  a 0,05 (`outputs/fase4d-c5-vs-m3limpio.json`).

La primera no pasa su umbral, así que Holm se detiene ahí y no acepta ninguna;
las otras dos también quedan por encima del suyo. Ninguna da su resultado a
favor. Por la regla:
- ni C5 ni C6 mejoran a M3 limpio, que sigue siendo el modelo recomendado;
- la especificación de la Fase 5 no cambia;
- no se mide el tiempo de inferencia de C5 ni de C6;
- la red mejorada no mejora a la red de la Fase 4c.

En especificidad media, la pAUC dividida por 0,2, las diferencias de las
preguntas 2, 3 y 1 son −0,0782, +0,025 y +0,0193
(`comparaciones_nuevo_menos_base.pauc.en_especificidad_media`).
Las tres métricas secundarias están en los tres archivos, con su intervalo y su
valor p, y no deciden. Solo una tiene un intervalo que excluye el cero: el AUC
de la pregunta 2, −0,027 [−0,0522; −0,0019].

---

## Fase 4e — La receta de imagen del 10.º puesto, con el equipo propio — CERRADA

**Estado: CERRADA (2026-11-01), por su regla, sin que ninguna de sus dos
preguntas diera su resultado a favor.** La exploración pasó los pasos 1 y 2, y
la confirmación, con la red ajustada en las semillas 5 a 9, no pasó la regla de
Holm (al final de la fase, «Resultado de la regla»). M3 limpio sigue siendo el
modelo recomendado, y la especificación de la Fase 5 no cambia. Queda la
decisión de la persona sobre el cómputo aparte. *Hasta ese día decía que la
fase estaba en curso, primero esperando la orden de la persona para la
exploración y después en la confirmación.*

**Decisión de la persona (2026-10-31).** Al cerrar la Fase 4d, la persona
decidió dedicar diez días de trabajo a buscar, con su propio equipo, una mejora
de la red de imagen. Al terminar se decide si se usa cómputo aparte. El
conjunto reservado sigue cerrado durante toda la fase. Como en las fases 4b, 4c
y 4d, el modelo recomendado y la especificación de la Fase 5 pasan a depender
de esta fase. La fase sale de un borrador escrito en la conversación, verificado
frase por frase contra este archivo, `outputs/`, `referencias/` y el código del
10.º puesto antes de entrar aquí; lo que no se sostuvo está corregido abajo, en
«Cómo quedó la verificación».

**Cuarta ronda, declarada.** Es la cuarta vez que se reabre la regla «Solo esta
corrida» de la Fase 4. Las preguntas se eligieron conociendo los resultados de
las fases 4 a 4d, incluido que la red mejorada de la 4d, con 15 épocas y los
negativos en bloques, quedó por debajo de la red de la 4c en la media de la
pAUC, 0,0923 frente a 0,1079, sin que Holm aceptara la diferencia
(`outputs/fase4d-red-mejorada-vs-red.json`). Hasta esta fase la bitácora suma 16
comparaciones. Las preguntas se fijan aquí antes de correr, se corrige por
multiplicidad dentro de la fase y no se añaden preguntas después de ver
resultados.

**Por qué esta receta.**
- **La distancia.** El 10.º puesto, con la misma EfficientNet-B0 y la misma
  entrada de 128 píxeles, reporta para su red de imagen *"CV=0.152"* con el
  patrón 1 de aumentos y *"CV=0.156"* con el patrón 2
  (`referencias/tomo20180402-2024-isic2024-10mo-puesto.md`). La red de la Fase
  4c da 0,1083 en las 10 semillas (`outputs/fase4c-red-sola-vs-imagen.json`).
  La comparación es indicativa, no una prueba: el autor valida sobre todo el
  conjunto de entrenamiento del reto, que incluye a los pacientes que este
  proyecto reservó, y con sus propias particiones. Sí agrupa por paciente
  (`scripts/common_training.py`, `StratifiedGroupKFold` por `patient_id`). Su
  código calcula dos pAUC: una en cada época, sobre una submuestra de
  validación de hasta 50 negativos por paciente, con la que elige la «mejor
  época», y otra al final sobre todo el pliegue (`scripts/image_training.py`,
  `all_pauc`). El README no dice cuál de las dos es su `CV=`.
- **Lo que la 4d copió y lo que no.** La pregunta 2 de la Fase 4d tomó del
  README dos ideas, cambiar de negativos en cada época y fijar las épocas, y
  dejó fuera el resto. El código del autor, en el mismo commit que la ficha,
  muestra qué más cambia frente a la red de la 4c:
  - aumentos fuertes en el entrenamiento, no solo volteos
    (`scripts/image_dataset.py`, `generate_train_transforms`);
  - tasa 0,0005 con decaimiento de pesos 0,0005 y calendario OneCycle, con un
    10 % de calentamiento y descenso en coseno (`scripts/image_training.py`,
    líneas 120 y 121), frente a la tasa fija de 0,0001 de la 4c;
  - 20 épocas (`scripts/config.py`, `N_EPOCH = 20`).

  El decaimiento de pesos del autor, 0,0005, es menor que el 0,01 que la red de
  la 4c recibe por defecto de AdamW: lo que regulariza su receta son los
  aumentos, no el decaimiento. *Lectura nuestra, no medida:* la 4d cambió las
  épocas y los negativos sin los aumentos del autor; esta fase prueba la receta
  completa.
- **El README y el código no dicen lo mismo sobre los negativos.** El README
  dice *"divide into 20 datasets and switch for each epoch (n_epoch=20)"*. El
  código de ese commit no reparte los negativos en conjuntos: en cada época
  baraja los del pliegue de entrenamiento y toma hasta 50 por paciente
  (`.groupby('patient_id').head(50)`). Ese tope es la estrategia 6 del README,
  *"Train up to 50 negative samples per patient"*, que el autor da como la
  variante que empeoró: *"cv=0.182"* frente a *"CV=0.183"*. Su commit «fix:
  remove data cut» quitó ese mismo tope en la segunda etapa y no en la de
  imagen. *Lectura nuestra:* el código de imagen publicado sería la variante de
  la estrategia 6. **Esta fase sigue el README**, con una implementación nuestra,
  porque el esquema de 20 conjuntos no está en el código (decisión de la
  persona, 2026-10-31). La ficha registra la discrepancia, con las citas.
  *La pregunta 2 de la Fase 4d citó la frase del README como origen de sus
  bloques; eso no cambia.*

**Qué se entrena: la red de la 4e.** Lo que no se nombra aquí es igual a la red
de la Fase 4c (`fase4c.py`): EfficientNet-B0 con los pesos de ImageNet ya
verificados para la Fase 2 (`referencias/efficientnet-b0-preentrenamiento.md`),
entrada de 128 × 128, lote de 64, precisión float32 y la predicción sobre todo
el pliegue de validación. El lote y la precisión coinciden con los del autor
(`scripts/config.py`, `BS = 64`; su código no usa precisión mixta).
- **Negativos por época: como el README.** Los negativos del pliegue de
  entrenamiento se reparten al azar, con la semilla externa, en 20 conjuntos de
  tamaño casi igual, y cada época usa uno, durante 20 épocas: al terminar, la
  red vio cada negativo una vez. En cada época entran también todos los
  positivos del pliegue de entrenamiento, como en el código del autor (*"train
  all pos"*). La implementación es nuestra; el código del autor hace
  `head(50)` por paciente, y su README da esa variante como la que empeoró.
- **Aumentos: el patrón 2 del autor** (`scripts/image_dataset.py`,
  `train_transform_p2`): redimensionar a 144 × 144, recorte aleatorio a 128 con
  `scale=(0.8, 1.2)` y `ratio=(0.75, 1.3333)`, volteo horizontal y vertical con
  probabilidad 0,5 cada uno, rotación de hasta 45° con probabilidad 0,5, brillo
  y contraste de 0,5 con probabilidad 0,5, desenfoque gaussiano de núcleo 3 con
  probabilidad 0,3, y la normalización de ImageNet. Se elige el patrón 2 y no
  el 1 porque su CV reportada es la mayor de las dos y porque usa torchvision,
  que ya está en el `.venv/`; el patrón 1 necesita albumentations, que no está.
- **Interpolación bilineal, al entrenar y al predecir, como el autor.** Sus
  redimensiones son las de torchvision por defecto, bilineales; al predecir,
  redimensionar a 128 y normalizar (`valid_transform_p2`). La red de la 4c
  redimensiona con bicúbica: es una diferencia con ella, declarada.
- **Optimizador y calendario:** AdamW con tasa 0,0005 y decaimiento de pesos
  0,0005; OneCycle con `max_lr=0.0005`, `pct_start=0.1` y
  `anneal_strategy='cos'`, y los demás argumentos por defecto, como en el
  código del autor. Por defecto, OneCycle empieza en la tasa máxima dividida por
  25, termina en esa tasa inicial dividida por 10⁴ y hace ciclar el β1 de
  AdamW entre 0,85 y 0,95. El calendario avanza en cada lote, y su número total de pasos es el de
  los lotes de las 20 épocas.
- **Épocas:** 20, fijas, sin mirar la validación entre épocas. La red que
  puntúa es la de la última época, no la mejor: el autor reporta también la de
  la mejor época (*"selecting the best epoch yields CV=0.159"*), que se elige
  con las etiquetas de validación, y esta fase no la usa (regla de la décima
  clase del registro de incidentes).
- **Diferencias con el autor, declaradas:**
  - los pesos de ImageNet son los de torchvision ya verificados, no los de
    timm;
  - la EfficientNet-B0 de torchvision lleva dropout de 0,2 antes de la capa de
    salida y profundidad estocástica creciente hasta 0,1875 (comprobado en el
    `.venv/`); el autor usa la de timm, con la capa de salida cambiada por una
    lineal, y si timm añade dropout o profundidad estocástica por defecto no se
    comprobó, porque timm no está instalado;
  - la salida es un logit con `BCEWithLogitsLoss`, no dos clases con entropía
    cruzada: es la misma pérdida en función de la diferencia de los dos logits,
    salvo en cómo actúa el decaimiento de pesos sobre la capa de salida;
  - los aumentos que se aplican con una probabilidad usan `RandomApply` de
    torchvision, con el generador de torch, y no la clase del autor, que usa el
    módulo `random` de Python: hacen lo mismo con otro generador;
  - las particiones son las de este proyecto.
- **Los pesos de cada red** se guardan en `data/`, que no se versiona: los
  necesita el ajuste fino de abajo.

**Exploración, semilla 0 (descriptiva).** La red de la 4e se entrena en los 5
pliegues de la semilla 0, los de `construir_folds`, y se compara pliegue a
pliegue con la red de la 4c en esa misma semilla, que ya está guardada. La
exploración no da un resultado a favor por sí sola: solo decide si se gasta la
confirmación. Sus filas entran a la bitácora como descriptivas.
- **Paso 1 · La receta.** ¿Supera la red de la 4e a la de la 4c en al menos 4
  de los 5 pliegues de la semilla 0, en la pAUC? Si no, la fase se detiene
  aquí, no se confirma nada y se registra que la receta del 10.º no reprodujo
  su ventaja en estos datos y con este equipo.
- **Paso 2 · Ajuste fino con la métrica del reto (condicional).** Si el paso 1
  pasa y LibAUC instala y corre en MPS (abajo), cada red de la semilla 0 se
  ajusta 2 épocas más con una pérdida de pAUC unilateral, `pAUC_CVaR_Loss` de
  LibAUC con β = 0,2, sobre las clases invertidas: lo benigno pasa a ser la
  clase positiva y la puntuación se niega. Con esa inversión, la región que la
  pérdida optimiza tendría que ser la de la métrica del reto, porque el script
  oficial también invierte las etiquetas (registro de incidentes, séptima
  fila). *Esto se comprueba ejecutando, no razonando* (controles). El
  protocolo de preentrenar con entropía cruzada y después ajustar con la
  pérdida de pAUC es el de Zhu et al. (ICML 2022): preentrenan con entropía
  cruzada y Adam, reinicializan la capa de clasificación y ajustan todas las
  capas (`referencias/zhu-2022-sopa-pauc-dro.md`, página 8). Sus ajustes se
  fijaron antes de leer la exploración (al final de la fase, «Los ajustes del
  paso 2»). *Hasta el 2026-11-01 decía que el protocolo «se atribuye a» Zhu et
  al., pendiente de comprobar y versionar.* Si el ajuste fino supera a la red sin ajustar en al menos 4 de
  los 5 pliegues, la confirmación usa la red ajustada; si no, la red sin
  ajustar. Si la librería no instala, no corre en MPS o el control de la región
  falla, el paso 2 se cae, y se registra por qué.

**Confirmación, semillas 5 a 9 o 5 a 7.** Solo si el paso 1 pasa. La receta
elegida se entrena en los pliegues de las semillas de confirmación, 25 con 5
semillas o 15 con 3 (regla de abajo). La red de la 4c y M3 limpio ya están
calculados en ellas. **Las semillas de confirmación no son datos nuevos.**
Ninguna red de la Fase 4d ni la exploración usan esas particiones, pero sí las
usaron las fases 4, 4b y 4c y la pregunta 1 de la 4d, que corrieron las
semillas 0 a 9. Además, todas las semillas reparten a los mismos pacientes: la
confirmación y la exploración comparten lesiones y etiquetas, así que las
elecciones de los pasos 1 y 2 no son independientes de la confirmación. Se
declara como sesgo del resultado.
- **Pregunta 1 · La red de la 4e frente a la red de la 4c**, sola, en los
  mismos pliegues, en las cuatro métricas. Informa la recomendación para el
  escenario sin sistema de fotografía corporal total, pero no la cambia, como en
  las fases 4c y 4d: hoy esa recomendación es la imagen con edad, sexo y zona
  del cuerpo (`informe/borrador-v2.md`, «Qué se recomienda»), y la pregunta 1 no
  se compara con ella.
- **Pregunta 2 · C7 frente a M3 limpio.** C7 es C4 con la red de la 4e en lugar
  de la red de la 4c: las mismas dos variables, la puntuación y su razón a la
  media del paciente, y el mismo atajo declarado de apilar con los mismos
  pliegues. Se elige la forma de C4 y no la de C5 porque es la más simple, y
  porque C5 quedó por debajo de C4 en la media de la pAUC, 0,1659 frente a
  0,1687 (`outputs/fase4d-c5-vs-m3limpio.json` y
  `outputs/fase4c-c4-vs-m3limpio.json`), sin comparación directa entre las dos.
  La elección se hizo conociendo los resultados de la 4d, y se declara.

**Regla de las semillas de confirmación, fijada antes de correr y solo por
costo (decisión de la persona, 2026-10-31).** Si la prueba de tiempo proyecta
que la fase cabe en 45 horas de equipo con 5 semillas de confirmación, de la 5
a la 9, se confirma con 5. Si no, con 3, de la 5 a la 7. Motivo: más semillas
dan más potencia a la confirmación, y el único motivo para usar menos es el
costo; la regla depende solo de la proyección de horas, que se calcula antes de
ver ningún resultado. Si tampoco con 3 cabe en 45 horas, la fase no arranca y
la persona decide (abajo).

**Regla, fijada antes de correr.** La misma de la Fase 4d con dos preguntas: el
valor p bilateral de Nadeau y Bengio de la pAUC de cada pregunta, Holm a 0,05/2
y 0,05, y una pregunta da su resultado a favor si Holm la acepta y su
diferencia media es positiva. Las tres métricas secundarias se reportan con su
intervalo y no deciden.
- Si la pregunta 2 da a favor: C7 pasa a ser el modelo recomendado, se mide su
  tiempo de inferencia con el procedimiento de `tiempo-inferencia`, red
  incluida, y la especificación de la Fase 5 se reescribe para C7, con M3
  limpio como referencia, antes de abrir el reservado.
- Si solo la pregunta 1 da a favor: M3 limpio sigue siendo el recomendado, y el
  resultado informa la recomendación para el escenario sin fotografía corporal
  total, sin cambiarla.
- Si ninguna da a favor: nada cambia, y la fase se cierra con su resultado.

**Lectura declarada de antemano.** La nota de trabajo de la investigación
(`informe/insumos/investigacion-acercarse-al-ganador.md`) estima que, aun con
una red de imagen mucho mejor, el apilado ganaría poco, por debajo de lo que
el diseño de 10 semillas distingue. Es una inferencia de esa nota, marcada [I],
no una medición. Se escribe aquí para que un resultado nulo en la pregunta 2 no
se lea después como sorpresa, ni uno a favor en la pregunta 1 como una mejora
del modelo recomendado.

**Presupuesto de cómputo.** Antes de correr, una prueba de tiempo de la red de
la 4e en la semilla 0, pliegue 0, como la de la Fase 4c, con su salida en
`outputs/`. No calcula ninguna métrica. Con ella se proyecta el total de la
fase: las redes de control, las 5 de exploración, el ajuste fino y las de
confirmación, con 5 semillas y con 3. La regla de las semillas sale de esa
proyección. **Si con 3 semillas pasa de 45 horas de equipo, la fase no arranca
y la persona decide** qué se recorta. No se recorta nada de la receta por
cuenta propia, porque cualquier recorte sería una receta distinta de la del
autor.

**Controles, antes de leer cualquier resultado.** Los de la red se corren sobre
la semilla 1, pliegue 0, que no usan ni la exploración ni la confirmación, para
que ningún control calcule la pAUC de un pliegue que después decide.
- **Los de la comparación:** los de la Fase 4d, rehechos para juegos de 25 y de
  15 diferencias y para Holm con dos preguntas, con sus casos que deben fallar.
- **Los de la red:** los de la Fase 4c con la receta nueva (etiquetas
  barajadas, red real por encima del azar, reproducibilidad y alineación), y
  además:
  - los 20 conjuntos reparten todos los negativos del pliegue de entrenamiento,
    sin repetir ninguno, y cada época usa uno distinto con todos los positivos;
    caso que debe fallar: el sorteo de la 4c, que repite negativos entre
    épocas;
  - la tasa registrada en cada paso sigue el calendario OneCycle, con su
    máximo en el 10 % de los pasos; caso que debe fallar: una tasa fija;
  - los aumentos solo se aplican al entrenar: predecir dos veces la misma
    imagen da el mismo logit; caso que debe fallar: con los aumentos activos
    al predecir, cambia;
  - la lista de aumentos y sus parámetros coincide con `train_transform_p2`
    del autor, tal como lo cita la ficha; caso que debe fallar: quitando uno,
    se detecta.
- **Los del ajuste fino (si corre):**
  - con datos sintéticos, la métrica oficial
    (`referencias/isic-primary-metric-pauc.py.md`) y la pAUC unilateral con
    FPR ≤ 0,2 de las clases invertidas dan el mismo valor; caso que debe
    fallar: sin invertir las clases, no coinciden;
  - la pérdida responde a subir los positivos de menor puntuación y no a subir
    los de mayor puntuación; caso que debe fallar: sin invertir, responde al
    revés.
- **Los de C7:** los de alineación de C4, con la red de la 4e.

**Fuentes, antes de correr.**
- La ficha del 10.º puesto, ampliada con las citas literales del código que usa
  esta fase y con la discrepancia entre el README y el código: hecho el
  2026-10-31 (commit «Referencias: el código del 10.º puesto, con la
  discrepancia sobre los negativos»).
- Zhu et al. 2022 y la documentación de LibAUC: hecho el 2026-11-01
  (`referencias/zhu-2022-sopa-pauc-dro.md` y `referencias/libauc-2.0.1.md`,
  commit «Referencias: Zhu et al. 2022 y la documentación de LibAUC 2.0.1»).
- Las versiones de las librerías nuevas, con su licencia, en la procedencia de
  las salidas.

**Salida.**
- La prueba de tiempo, en `outputs/`.
- La exploración, en `outputs/fase4e-exploracion.json` y `.md`, descriptiva.
- Las dos preguntas, en `outputs/fase4e-red-vs-red4c.json` y
  `outputs/fase4e-c7-vs-m3limpio.json`, con su `.md` y la estructura de los
  `fase4d-*.json`.
- La decisión de Holm, en `outputs/fase4e-holm.json` y `.md`.
- Los controles de la comparación, en `outputs/fase4e-controles-comparacion.json`
  y `.md`; los de la red, en `data/`.

**Puerta.** Las salidas de arriba —o, si la fase se detiene en el paso 1, la
exploración y el registro de por qué se detuvo—, la bitácora al día con las
filas de la exploración y de la confirmación, y el resultado de la regla,
escrito al final de esta fase.

**Lo que esta fase no hace.**
- No abre el reservado ni cambia la especificación de la Fase 5, salvo por la
  regla de arriba.
- No elige épocas, tasa ni aumentos con los datos de este proyecto: toma los del
  autor.
- No prueba el patrón 1, el promedio de los dos patrones, la variante de 50
  negativos por paciente, redes más grandes ni más resolución. Lo más grande es
  lo que quedaría para el cómputo aparte.

**Cómo quedó la verificación (2026-10-31).** El borrador se verificó contra
este archivo, `outputs/`, `referencias/` y el código del 10.º puesto, leído con
`git clone` en el commit de la ficha. Dos puntos los decidió la persona y siete
se corrigieron:
- **Decisión A, los negativos:** el borrador seguía el código del autor; sigue
  el README, por la discrepancia de arriba.
- **Decisión B, la pregunta 1:** el borrador decía que, si daba a favor, la
  recomendación sin fotografía corporal total pasaba a la red de la 4e; la red
  de la 4c no superó a la imagen sola según su regla, y la recomendación actual
  es otra, así que la pregunta 1 informa sin cambiarla.
- **Correcciones:**
  1. el borrador decía que ninguna decisión de las fases 4d y 4e miró las
     semillas de confirmación; la pregunta 1 de la 4d y las fases 4 a 4c las
     usaron, y las semillas comparten pacientes;
  2. la lectura «la 4d entrenó más tiempo sin regularizar más, y la red
     empeoró» se retiró: la 4d cambió dos cosas, Holm no aceptó la
     diferencia, y el decaimiento de pesos del autor es menor que el de la 4c;
  3. «quedó por debajo» pasó a «quedó por debajo en la media de la pAUC, sin
     que Holm aceptara la diferencia»;
  4. el borrador daba la pAUC sobre todo el pliegue como la del autor; su
     código calcula dos, y el README no dice cuál es su CV;
  5. el borrador decía que la 4e predice como la 4c; el autor redimensiona con
     bilineal y la 4c con bicúbica, y la 4e sigue al autor;
  6. se añadieron como diferencias declaradas el dropout y la profundidad
     estocástica de torchvision, los argumentos por defecto de OneCycle, el
     decaimiento de pesos sobre la capa de salida y `RandomApply`;
  7. el protocolo de Zhu et al. pasó a «se atribuye a», pendiente de
     comprobar.

**Antes de la exploración (2026-11-01).**
- **La prueba de tiempo** (`outputs/prueba-tiempo-red-4e.json`): 1.714,6 s por
  red, con sus 20 épocas y su predicción, y 307,5 s por ajuste fino. La fase
  proyecta 18,19 horas con 5 semillas de confirmación y 12,53 con 3. Por la
  regla de las semillas, **la confirmación usa las semillas 5 a 9.** Se corrió
  con `fase4e.py` antes de que `autor_p2()` leyera también
  `valid_transform_p2`; ese cambio no toca el entrenamiento ni la predicción.
- **LibAUC 2.0.1**, instalada sin sus dependencias (`SKILL.md` de
  `modelado-baseline`), con licencia MIT. `pAUC_CVaR_Loss` corre en MPS como
  en CPU: la misma pérdida y, en el gradiente, una diferencia máxima de
  1,79e-07 (`data/fase4e-controles.json`, `ajuste_fino`).
  **El paso 2 sigue en pie en lo técnico.**
- **Los controles de la comparación:** `test_fase4e_comparacion.py` completo,
  19 de 19 casos como se esperaba
  (`outputs/fase4e-controles-comparacion.json`). En el caso negativo, con un
  límite de 62 rechazos en 1.000 juegos, la versión corregida rechaza 56 veces
  con 25 diferencias y 62 con 15: justo en el límite. Con la regla de las
  semillas, la confirmación no usa el juego de 15.
- **Los controles de la red:** `test_fase4e_controles.py` completo, 34 de 34
  casos como se esperaba, incluidos los que debían fallar, en 4.708,8 s
  (`data/fase4e-controles.json`, que no se versiona). Las dos redes completas
  tardaron 1.731,9 s y 1.746,1 s, algo más que la prueba de tiempo. En la
  semilla 1, pliegue 0, sobre toda la validación:
  - con las etiquetas barajadas, la pAUC es 0,0272, dentro del rango del azar
    [0,009; 0,0396];
  - con las reales, 0,1467, con 63.283 logits distintos y ningún negativo en
    dos épocas;
  - la tasa de los 4.060 pasos coincide con OneCycle, con el máximo en el paso
    405;
  - dos redes de 2 épocas dan logits idénticos, y predecir dos veces sin
    aumentos también; con los aumentos activos, el logit cambia.

  La pAUC de la red real de ese pliegue no se comparó con la de la red de la 4c
  en el mismo pliegue: adelantaría, fuera de la regla, la comparación del paso
  1.
- **Un criterio cambiado antes de la corrida completa.** En el modo rápido, el
  control del calendario falló: pedía que el máximo de la tasa fuera 5e-4 con
  un margen de 1e-12, y en 406 pasos el máximo de OneCycle cae entre dos pasos.
  El fallo era del criterio, no de la red. Se cambió por la comparación paso a
  paso con la fórmula de OneCycle, antes del commit de los controles, y su caso
  que debe fallar, la tasa fija, sigue fallando.
- **Lo que faltaba para el paso 2,** sus ajustes y Zhu et al. 2022: fijados y
  versionado el 2026-11-01, abajo. *Hasta ese día este punto listaba lo que
  faltaba fijar.*

**Los ajustes del paso 2 (2026-11-01), fijados antes de leer la exploración.**
La persona fijó la regla: primero lo que Zhu et al. 2022 fija para su
experimento de Melanoma (`referencias/zhu-2022-sopa-pauc-dro.md`); lo que no
fije, la documentación de SOPA en LibAUC 2.0.1 (`referencias/libauc-2.0.1.md`),
que manda sobre la firma; y lo que ninguno fije, el agente, con el criterio más
simple, declarado. También ordenó arrancar la exploración mientras tanto y no
leer sus salidas hasta el commit de estos ajustes: las cinco redes del paso 1
no dependen de ellos. El artículo da sus ajustes una sola vez para todos sus
experimentos de imagen, Melanoma incluido.
- **Del artículo:**
  - la pérdida, la bisagra cuadrada con margen 1: `pAUC_CVaR_Loss` con
    `margin` 1,0 y `surr_loss` 'squared_hinge', que es también lo que da su
    documentación;
  - la actualización «Adam-style»: `SOPA` con `mode` 'adam'; su documentación
    da 'sgd', y manda el artículo;
  - el decaimiento de pesos, 2e-4; la documentación da 1e-5;
  - el lote, 64;
  - el calendario, que baja la tasa diez veces cada 20 épocas: en las 2 del
    ajuste, la tasa es constante;
  - la capa de clasificación se reinicializa antes de ajustar, y se ajustan
    todas las capas.
- **De la documentación:**
  - el muestreo, `DualSampler` con `sampling_rate` 0,5: 32 casos de cada clase
    en cada lote, barajados, con su `random_seed` por defecto, 2023. Con 0,5
    da igual qué clase lleve la etiqueta 1. Su consejo de usar una proporción
    algo mayor que la de positivos no fija un valor, y supone que la clase
    positiva es la escasa;
  - el paso de las variables duales, `eta` 0,1;
  - en `SOPA`, `betas` (0,9; 0,999), `eps` 1e-8, `amsgrad` falso y
    `epoch_decay` 0.
- **Lo que ninguno fija, con el criterio más simple:**
  - **la tasa, 1e-3.** El artículo la eligió con la validación dentro de
    {1e-3, 1e-4, 1e-5} y no dice cuál quedó. La documentación da 0,1, fuera
    de esa rejilla, como valor del modo 'sgd'. Manda el artículo, que la deja
    en la rejilla. Dentro de ella se toma el primer valor, que es también la
    tasa por defecto de Adam, porque elegirla con los datos sería una elección
    con etiquetas que esta fase no hace;
  - **qué entra en cada época:** como en el entrenamiento, todos los positivos
    y un conjunto de negativos. Las dos épocas usan el primero y el segundo
    conjuntos del mismo reparto, que la red ya vio en sus dos primeras épocas.
    Con `DualSampler`, cada época tiene los lotes de 32 benignos que caben en
    su conjunto: 397 lotes de 64, unas 25.400 imágenes, y cada maligno se
    repite unas 50 veces;
  - una sola pérdida para las dos épocas, con una variable dual por imagen;
  - lo que entra en la pérdida es el logit negado, sin sigmoide, como en el
    ejemplo de la documentación, que usa `torch.randn`;
  - la capa nueva se reinicializa con su inicialización por defecto de
    PyTorch, `reset_parameters()`, tras fijar la semilla de la red;
  - `clip_value`, que no está en la documentación, queda en lo que hace la
    librería si no se pasa: recortar el gradiente a 1,0;
  - los aumentos, los procesos de datos y la predicción son los del
    entrenamiento de la 4e.
- **β = 0,2**, fijado arriba por la métrica del reto; el artículo lo elige en
  {0,1; 0,3; 0,5}.
- **Diferencias con el artículo, declaradas:** 2 épocas y no 60; una tasa fija
  y no elegida con la validación; EfficientNet-B0 y no ResNet18; el
  preentrenamiento de la receta del 10.º puesto, AdamW con OneCycle, y no Adam;
  y las clases invertidas.
- **Lectura declarada de antemano.** Con las clases invertidas, la pérdida
  tiene una variable dual por cada benigno, y cada benigno entra en el ajuste
  una vez como mucho. Su variable se actualiza, por tanto, una sola vez, desde
  0 y con paso 0,1, mientras que en el control de la respuesta de la pérdida
  se llevó al equilibrio con 3.000 iteraciones. Lejos de ese equilibrio, la pérdida puede
  comportarse más como una de AUC sobre todos los pares que como la de la
  pAUC por encima del 80 %. El registro de cada red guarda cuántas veces se
  actualizó cada variable dual. Si el paso 2 no mejora, esta es una
  explicación posible, sin medir.
- **Costo, estimado sin medir:** cada ajuste recorre unas 50.800 imágenes,
  casi el doble de lo que suponía la prueba de tiempo. Si la confirmación usa
  la red ajustada, la fase sube unas 1,2 horas y sigue lejos de las 45.
- La regla del paso 2 no cambia: la red ajustada tiene que superar a la sin
  ajustar en al menos 4 de los 5 pliegues de la semilla 0, en la pAUC.

**Resultado de la exploración (2026-11-01), descriptivo.** Semilla 0, los 5
pliegues de `construir_folds` (`outputs/fase4e-exploracion.json`). La red de la
4c reproduce sus métricas de `outputs/fase4c-red-sola-vs-imagen.json` pliegue a
pliegue. Una red gana un pliegue si su pAUC, sin redondear, es estrictamente
mayor.
- **Paso 1, la red de la 4e frente a la de la 4c:** gana en los 5 pliegues.
  pAUC 0,1443, 0,1521, 0,1157, 0,1335 y 0,1212, frente a 0,12, 0,1225,
  0,0999, 0,1177 y 0,0731; diferencia media +0,0267 (`paso_1`). **Llega al
  umbral, 4 de 5, y se corre el paso 2.**
- **Paso 2, la red ajustada frente a la de la 4e sin ajustar:** gana en 4 de los
  5 pliegues; pierde en el cuarto, 0,1174 frente a 0,1335. Diferencia media
  +0,0093 (`paso_2`). **Llega al umbral, y la confirmación usa la red
  ajustada.**
- Las tres métricas secundarias de las tres redes están en el mismo archivo, y
  no deciden.
- **Las variables duales,** como se declaró antes de correr: en cada una de las
  cinco redes, 25.408 benignos entraron una vez y 26 ninguna, y sus variables
  quedaron entre −0,1 y 0,4 (`data/fase4e-puntuaciones-red-ajustada-exploracion.json`,
  que no se versiona, campo `redes`).
- **Lo que no dice la exploración:** es una sola semilla, y elige; la
  confirmación es la que decide.
- **El tiempo medido:** una mediana de 1.738,7 s por red y de 536,7 s por
  ajuste (`data/fase4e-puntuaciones-red-exploracion.json` y
  `data/fase4e-puntuaciones-red-ajustada-exploracion.json`). La prueba de
  tiempo daba 1.714,6 s y 307,5 s. Con esos tiempos, la confirmación de 25
  redes con su ajuste son unas 15,8 horas, y la fase sigue por debajo de las
  45.

**La confirmación, arrancada el 2026-11-01** con las semillas 5 a 9, la regla
de las semillas, y la red ajustada, la del paso 2: `fase4e_redes.py` y después
`fase4e_ajuste.py`, con caffeinate.

**La confirmación, terminada el 2026-11-01, antes de leer ninguna
comparación.** Las 25 redes y sus 25 ajustes corrieron sin errores, con los
controles de la red en 34 de 34 y una puntuación por fila en cada semilla
(`data/fase4e-puntuaciones-red-confirmacion.json` y
`data/fase4e-puntuaciones-red-ajustada-confirmacion.json`, que no se
versionan). Mediana de 1.780,2 s por red y de 536,4 s por ajuste; en total,
44.842,2 s y 13.409,3 s, unas 16,2 horas. En los 25 ajustes, como en la
exploración, 25.408 benignos entraron una vez y 26 ninguna, con las variables
duales entre −0,1 y 0,4, y cada época corrió sus 397 lotes.

**Resultado de la regla (2026-11-01).** Semillas 5 a 9 × 5 pliegues, con la red
ajustada como red de la 4e. Holm sobre los valores p bilaterales de Nadeau y
Bengio de la pAUC (`outputs/fase4e-holm.json`), de menor a mayor:
- pregunta 1, red de la 4e − red de la Fase 4c: +0,029 [0,002; 0,056], 0,1376
  frente a 0,1086; valor p 0,03646 frente a 0,05/2 = 0,025; mejor en 23 de 25
  pliegues y 5 de 5 semillas (`outputs/fase4e-red-vs-red4c.json`);
- pregunta 2, C7 − M3 limpio: +0,0029 [−0,0084; 0,0141], 0,1669 frente a
  0,1641; valor p 0,6028 frente a 0,05; mejor en 14 de 25 pliegues y 4 de 5
  semillas (`outputs/fase4e-c7-vs-m3limpio.json`).

La primera no pasa su umbral, así que Holm se detiene ahí y no acepta ninguna;
la segunda queda también por encima del suyo. Ninguna da su resultado a favor.
Por la regla:
- C7 no mejora a M3 limpio, que sigue siendo el modelo recomendado;
- la especificación de la Fase 5 no cambia;
- no se mide el tiempo de inferencia de C7;
- la red de la 4e no mejora a la red de la Fase 4c, y la recomendación para el
  escenario sin fotografía corporal total no cambia. *Cambió el 2026-11-02, por
  la regla de la Fase 4f.*

El intervalo al 95 % de la pregunta 1 excluye el cero, pero la regla es Holm con
dos preguntas, no ese intervalo, y su valor p no llega a 0,025. En especificidad
media, la pAUC dividida por 0,2, las diferencias de las preguntas 1 y 2 son
+0,145 y +0,0143 (`comparaciones_nuevo_menos_base.pauc.en_especificidad_media`).
Las tres métricas secundarias están en los dos archivos, con su intervalo y su
valor p, y no deciden. En la pregunta 1, dos tienen un intervalo que excluye el
cero: el AUC, +0,044 [0,0062; 0,0818], y la sensibilidad top-15, +0,1232
[0,043; 0,2035]; el NNT80% SE, −123,87 [−269,37; 21,63], no. En la pregunta 2,
las tres contienen el cero. La red de la 4c reproduce
`outputs/fase4c-red-sola-vs-imagen.json`, y M3 limpio
`outputs/fase4-m3limpio-vs-m2.json`, pliegue a pliegue en las cuatro métricas
(`reproduccion_del_base`). En estas cinco semillas M3 limpio da 0,1641, frente a
0,1621 en las semillas 0 a 9 (`outputs/fase4d-c5-vs-m3limpio.json`) y 0,1601 en
las 0 a 4 (`outputs/fase4d-c6-vs-m3limpio.json`).

**Bitácora, filas de la Fase 4e.** Las de la exploración son descriptivas y no
cuentan como comparaciones de la regla. Con las dos de la confirmación, la
bitácora suma 18 comparaciones por la pAUC desde la Fase 4: las 16 anteriores
(Fase 4d, «Bitácora de intentos») y estas 2. En la confirmación, la columna de
la regla da el valor p de cada pregunta y su umbral de Holm.
*Hasta el 2026-11-01 este bloque se llamaba «Bitácora, filas de la exploración»
y solo tenía las dos primeras.*

| Modelo | Fase | Comparación | Diferencia de pAUC | NB 95 % | Intervalo de la regla | Resultado | Archivo |
|---|---|---|---|---|---|---|---|
| Red de la 4e | 4e, exploración, descriptiva | Red de la 4e − red de la 4c, semilla 0 | +0,0267 de media en 5 pliegues | — | — | gana en 5 de 5; pasa el paso 1 | `fase4e-exploracion.json` |
| Red de la 4e ajustada | 4e, exploración, descriptiva | Ajustada − sin ajustar, semilla 0 | +0,0093 de media en 5 pliegues | — | — | gana en 4 de 5; pasa el paso 2 | `fase4e-exploracion.json` |
| Red de la 4e ajustada | 4e | Red de la 4e − red de la 4c, semillas 5 a 9 | +0,029 | [0,002; 0,056] | Holm: valor p 0,03646 frente a 0,025 | no mejora | `fase4e-red-vs-red4c.json` |
| C7 | 4e | C7 − M3 limpio, semillas 5 a 9 | +0,0029 | [−0,0084; 0,0141] | Holm: valor p 0,6028 frente a 0,05 | no mejora | `fase4e-c7-vs-m3limpio.json` |

---

## Fase 4f — La red de la 4e frente a «Imagen + básicos» — CERRADA

**Estado: CERRADA (2026-11-02), por su regla, con su pregunta a favor.** La
recomendación para el escenario sin fotografía corporal total pasa a la red de
la 4e; M3 limpio sigue siendo el modelo recomendado donde se toma esa
fotografía (al final de la fase, «Resultado de la regla»). *Hasta ese día decía
que la fase estaba en curso, con la pregunta, la regla y los controles fijados
antes de correr.*

**Decisión de la persona (2026-11-02), tomada después de ver la Fase 4e.** Una
sola pregunta, sobre el escenario sin sistema de fotografía corporal total:
¿supera la red de la 4e a «Imagen + básicos», que hoy es el punto de partida
para ese escenario (`informe/borrador-v2.md`, «Qué se recomienda»)? La pregunta
1 de la 4e comparaba la red con la de la Fase 4c, no con ese punto de partida, y
por eso informaba sin cambiar nada (Fase 4e, «Pregunta 1»). El conjunto
reservado sigue cerrado.

**Elegida después de ver la 4e, y se declara.**
- **Lo que se sabía:** la red ajustada superó a la de la 4c en 23 de 25
  pliegues y en las 5 semillas, con un valor p de 0,03646 que no llegó al
  umbral de Holm, 0,025 (`outputs/fase4e-red-vs-red4c.json` y
  `outputs/fase4e-holm.json`).
- **Lo que ya estaba en `outputs/`:** las métricas por pliegue de los dos
  modelos, las de la red en `fase4e-red-vs-red4c.json` y las de «Imagen +
  básicos» en `imagen-sola.json`. Al verificar esta fase, el agente calculó la
  media de la pAUC de «Imagen + básicos» en las semillas 5 a 9 desde esos
  valores guardados. La diferencia de medias se conocía, por tanto, antes de
  fijar la regla; el valor p no se calculó.
- **Los pliegues:** son los 25 de la confirmación de la 4e, y comparten
  pacientes con la exploración en que se eligió la receta (Fase 4e,
  «Confirmación»).

**La pregunta.**
- **La red de la 4e:** la ajustada, la de la confirmación, `Red4eAjustada`
  (`data/fase4e-puntuaciones-red-ajustada-confirmacion.csv.gz`, que no se
  versiona). No se entrena nada: en cada pliegue, la puntuación de la red de ese
  pliegue sobre su validación.
- **«Imagen + básicos»:** la de la Fase 6, «La imagen sola». Es la logística
  balanceada de `modelo_imagen()` sobre las 384 variables de DINOv2 más
  `age_approx`, `sex` y `anatom_site_general`, codificadas con
  `codificar_fold` y estandarizadas con las de imagen, ajustada con el pliegue
  de entrenamiento. Se recalcula en estos pliegues con el código de
  `imagen_sola.py` (controles, abajo).
- **Los pliegues:** semillas 5 a 9 × 5 pliegues, los de `construir_folds`, con
  la huella de `outputs/fase4-m2-vs-m1.json`, la misma con que `imagen_sola.py`
  comprobó los suyos. Comprobado al escribir esta fase: en las cinco semillas
  coinciden la huella de `outputs/fase4-m2-vs-m1.json`, la de
  `outputs/fase4e-red-vs-red4c.json` y la de la procedencia de las
  puntuaciones de la red.
- **Las métricas:** la pAUC decide. El AUC, la sensibilidad top-15 y el NNT80%
  SE se reportan con su intervalo y su valor p, y no deciden.

**Regla, fijada antes de correr.** La diferencia pareada pliegue a pliegue, red
de la 4e − «Imagen + básicos», en la pAUC. Da su resultado a favor si el valor p
bilateral de Nadeau y Bengio, el de las fases 4d y 4e, es menor que 0,05 y la
diferencia media es positiva. Es una sola pregunta: dentro de la fase no hay
corrección por multiplicidad.
- **Si da a favor:** la recomendación para el escenario sin fotografía corporal
  total pasa a la red de la 4e, con la salvedad de que se midió en los recortes
  de SLICE-3D y no en fotos de teléfono. M3 limpio sigue siendo el modelo
  recomendado donde se toma la fotografía corporal total.
- **Si no:** nada cambia, y la fase se cierra con su resultado.

*Lectura nuestra, no una condición de la regla:* la red usa solo la imagen. Si
da a favor, la recomendación para ese escenario pasa a un modelo sin edad, sexo
ni zona del cuerpo, y la red con esos datos sigue sin probarse
(`informe/borrador-v2.md`, «Qué se recomienda»).

**Controles, antes de leer la comparación.** Si alguno falla, el script se
detiene sin escribir la salida.
- **«Imagen + básicos»:** el recálculo reproduce sus cuatro métricas de
  `outputs/imagen-sola.json` pliegue a pliegue, a 4 decimales, en las semillas
  5 a 9. Caso que debe fallar: el recálculo de cada semilla, frente a lo
  guardado para la semilla siguiente (la 9, frente a la 5), no coincide.
- **La red:** reproduce sus cuatro métricas de
  `outputs/fase4e-red-vs-red4c.json` pliegue a pliegue. Sus puntuaciones pasan
  las comprobaciones de `cargar_red_4e`: el SHA-256, la huella en float64, la
  sigmoide del logit, la alineación por semilla y los controles de la red con 0
  fallos.
- **La comparación:** los controles de la 4e para juegos de 25 diferencias, que
  incluyen el valor p (`outputs/fase4e-controles-comparacion.json`, 19 de 19).
- **Los valores:** la diferencia usa los recalculados, sin redondear, como las
  bases de las fases 4d y 4e. La decisión 1 de «La imagen sola» (Fase 6) dice
  que no se vuelve a correr y que no se cita un recálculo sin redondear. Se
  refiere a otra comparación, (Imagen + básicos) − Imagen, que esta fase no
  calcula.

**Salida.** `outputs/fase4f-red4e-vs-imagen-basicos.json` y `.md`, con la
estructura de los `fase4e-*.json` de las preguntas y la regla aplicada en el
mismo archivo, en el campo `regla`.

**Bitácora.** Con esta pregunta, la bitácora suma 19 comparaciones por la pAUC
desde la Fase 4: las 18 anteriores (Fase 4e, «Bitácora, filas de la Fase 4e»)
y esta. La fila va al final de la fase, con el resultado.

**Puerta.** La salida, la fila de la bitácora y el resultado de la regla,
escrito al final de esta fase.

**Lo que esta fase no hace.**
- No entrena ninguna red ni prueba la red con edad, sexo y zona del cuerpo.
- No abre el reservado.
- No cambia el modelo recomendado ni, por su regla, la especificación de la
  Fase 5.

**Resultado de la regla (2026-11-02).** Semillas 5 a 9 × 5 pliegues
(`outputs/fase4f-red4e-vs-imagen-basicos.json`). Red de la 4e − «Imagen +
básicos», en la pAUC: +0,0493 [0,0218; 0,0767], 0,1376 frente a 0,0884; valor
p 0,001105 frente a 0,05; mejor en 25 de 25 pliegues y 5 de 5 semillas. **Da
su resultado a favor** (`regla.a_favor`). Por la regla:
- la recomendación para el escenario sin fotografía corporal total pasa a la
  red de la 4e, con la salvedad de que se midió en los recortes de SLICE-3D y
  no en fotos de teléfono;
- M3 limpio sigue siendo el modelo recomendado donde se toma la fotografía
  corporal total;
- la especificación de la Fase 5 no cambia por esta regla. La red y «Imagen +
  básicos» entraron en ella como resultado descriptivo por una decisión de la
  persona del mismo día, escrita antes de leer este resultado (Fase 5).

Las tres métricas secundarias no deciden. Las tres tienen un intervalo al 95 %
que excluye el cero, a favor de la red, en 25 de 25 pliegues y 5 de 5
semillas:
- el AUC, +0,0829 [0,0465; 0,1193];
- la sensibilidad top-15, +0,1938 [0,1062; 0,2813];
- el NNT80% SE, −212,6526 [−337,8064; −87,4988].

En especificidad media, la pAUC dividida por 0,2, la diferencia es +0,2464
[0,1092; 0,3836] (`comparaciones_nuevo_menos_base.pauc.en_especificidad_media`).

**Los controles pasaron antes de la comparación.** «Imagen + básicos»
recalculado reproduce `outputs/imagen-sola.json` pliegue a pliegue en las
cuatro métricas, y frente a la semilla siguiente no coincide en ninguna
(`reproduccion_del_base`). La red reproduce `outputs/fase4e-red-vs-red4c.json`
(`reproduccion_de_la_red`). La logística no dio ningún aviso de no
convergencia, y la corrida tardó 164,1 s.

**Lo que el resultado no dice.**
- **Que la pregunta se eligiera a ciegas.** Se eligió después de ver la 4e, en
  los mismos pliegues de su confirmación, y con la diferencia de medias ya
  calculable desde `outputs/` (arriba).
- **Cuánto cuesta la red al predecir.** Su tiempo de inferencia no se midió con
  el procedimiento de `tiempo-inferencia`: la regla de esta fase no lo pedía.
- **Cómo rinde con fotos de teléfono.** Sigue sin medirse.

*Lectura nuestra, no medición:* la red no usa edad, sexo ni zona del cuerpo,
así que la salvedad de la zona del cuerpo de «Imagen + básicos», que pudo venir
del software del sistema (`CLAUDE.md`, hallazgo 10), no se aplica a la
recomendación nueva. La red con esos datos sigue sin probarse.

**Bitácora, fila de la Fase 4f.** Con ella, la bitácora suma 19 comparaciones
por la pAUC desde la Fase 4: las 18 anteriores (Fase 4e, «Bitácora, filas de la
Fase 4e») y esta. La columna de la regla da el valor p y su umbral; es una sola
pregunta, sin corrección por multiplicidad dentro de la fase.

| Modelo | Fase | Comparación | Diferencia de pAUC | NB 95 % | Intervalo de la regla | Resultado | Archivo |
|---|---|---|---|---|---|---|---|
| Red de la 4e ajustada | 4f | Red de la 4e − «Imagen + básicos», semillas 5 a 9 | +0,0493 | [0,0218; 0,0767] | valor p 0,001105 frente a 0,05 | a favor: recomendación sin fotografía corporal total | `fase4f-red4e-vs-imagen-basicos.json` |

---

## Fase 5 — Abrir el holdout. Una sola vez

**Qué se hace.** Evaluar sobre el holdout sellado en la fase 1 **el modelo
recomendado**, uno solo, y reportar punto e intervalo.

**Especificación: decisión de la persona, fijada el 2026-09-26 antes de abrir el
reservado.** El modelo recomendado es M3 limpio (Fase 4, «Modelo recomendado»).
Según `outputs/holdout-pacientes.json`:
- el reservado tiene 209 pacientes, 52 de ellos con alguna lesión maligna y 76
  lesiones malignas en total;
- el desarrollo tiene 833 pacientes, con 207 y 317.

- Se entrena M3 limpio una sola vez sobre los pacientes de desarrollo, con su
  especificación de la Fase 4 y semilla 0. La parada temprana usa el 20 %
  interno de desarrollo, agrupado por paciente. Todo lo que se ajusta, se ajusta
  con el desarrollo y se aplica al reservado.
- M2 se entrena igual y se puntúa en la misma corrida, como referencia. No estaba
  en el anteproyecto y se declara.
- *Salvedad de M2, añadida el 2026-10-02, antes de abrir el reservado.* Sus
  variables de contexto siguen el diseño de la solución ganadora
  (`modelado-baseline/scripts/contexto_paciente.py`; celdas 7, 10 y 11 de
  `top-model.ipynb`):
  - el z-score dentro del paciente de cada una de las 34 variables numéricas
    de M1;
  - los conteos y las sumas de área por paciente;
  - el LOF por paciente, con `n_neighbors=min(n, 30)`, sobre las 17 variables
    de `top_lof_features`, repeticiones incluidas (15 distintas).

  Ese diseño se publicó sin ningún conjunto reservado: el notebook lo aplica a
  todo el `train-metadata.csv` del reto (celdas 3 y 12), que incluye a los
  pacientes que este proyecto reservó, y no dice cómo se eligió. M2 no lo copia
  entero. La desviación declarada en `contexto_paciente.py`, estandarizar e
  imputar dentro de cada paciente las variables del LOF, no cambia qué variables
  se construyen. Pero el z-score se calcula solo para las 34 variables numéricas
  de M1, no para las 76 del ganador (esas 34 y sus 42 derivadas), y sobre la
  edad sin imputar, que el ganador rellena antes con la mediana global (celda
  7). M2 se puntúa en el reservado como referencia, y el reservado tampoco le es
  ajeno: es la misma salvedad que la del diseño de las variables de M3 limpio
  (`CLAUDE.md`, hallazgo 8). Además, M2 hereda de M1 el nivel 2b, que se eligió
  como nivel de referencia con todos los datos, antes del sellado
  (`informe/anteproyecto.md`, sección 4.2).
- *Añadido el 2026-11-02, por decisión de la persona, después de la Fase 4e y
  antes de abrir el reservado.* Además de M3 limpio y M2, se puntúan en el
  reservado, en la misma corrida y como resultado descriptivo del escenario sin
  fotografía corporal total:
  - **la red de la 4e,** entrenada una sola vez sobre todos los pacientes de
    desarrollo con la receta y el ajuste fino de la Fase 4e, semilla 0
    (`fase4e.entrenar_y_puntuar` y `fase4e_ajuste.ajustar_y_puntuar`), y
    puntuando los recortes del reservado;
  - **«Imagen + básicos»** (Fase 6, «La imagen sola»), ajustado sobre el
    desarrollo y puntuando el reservado con sus características de DINOv2, ya
    extraídas: `data/dinov2-vits14-reservado.h5`, 82.830 imágenes de 209
    pacientes, ninguna fallida (`outputs/extraccion-imagen.json`,
    `conjuntos.reservado.cobertura`).

  No cambian ninguna recomendación. Se reportan con las mismas métricas y los
  mismos intervalos de bootstrap que M3 limpio, porque la puerta de esta fase
  pide punto e intervalo juntos, y sin ninguna diferencia con otro modelo. No
  estaban en el anteproyecto ni en la especificación del 2026-09-26, y se
  declaran. *Salvedades:*
  - los dos se midieron en recortes de SLICE-3D, no en fotos de teléfono;
  - la receta de la red la fijó el 10.º puesto validando sobre todo el conjunto
    de entrenamiento del reto, que incluye a los pacientes reservados (Fase 4e,
    «Por qué esta receta»): el reservado tampoco le es ajeno, como no lo es al
    diseño de las variables de M2 y de M3 limpio;
  - la zona del cuerpo de «Imagen + básicos» pudo venir del software del
    sistema de fotografía corporal total (`CLAUDE.md`, hallazgo 10).
- Los pacientes reservados se puntúan en una sola corrida. M3 limpio es el
  resultado principal.
- Métricas: pAUC (principal), AUC, SEtop-15 y NNT80% SE.
- Intervalos: bootstrap por paciente sobre los reservados, 2.000 remuestras,
  semilla 2026, percentiles 2,5 y 97,5.
- La diferencia M3 limpio − M2 se calcula con las mismas remuestras. Si queda
  entera por debajo de cero, el informe lo declara como contradicción entre las
  dos estimaciones y rebaja la seguridad de la recomendación, sin cambiar de
  modelo.
- El resultado se reporta sea cual sea. La estimación principal sigue siendo la
  validación cruzada repetida, y la recomendación no cambia por el reservado.
- La apertura va en un commit propio, posterior a este. El guion se niega a
  correr si la salida del reservado ya existe.

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
regenera, no se edita a mano. *El borrador se reescribe después de la Fase 4, no
se parchea antes (decisión del 2026-09-25, en la Fase 1).*

La tabla final responde la pregunta del cliente **entera**, con sus tres ejes:
pAUC, sensibilidad de recuperación top-15 por paciente, y costo de inferencia.
Es lo que cierra el argumento: el consultor deja de reportar una sola cifra.

**Definición operativa del tiempo de inferencia** (anteproyecto, sección 5.1).
El costo de inferencia se mide como tiempo:
- **Qué se cronometra:** desde los metadatos y la imagen de cada lesión hasta su
  puntuación, sin el entrenamiento.
- **Sobre qué:** un subconjunto fijo de pacientes completos del conjunto de
  desarrollo, elegido con semilla antes de medir. Van pacientes completos porque
  los modelos con contexto de paciente necesitan todas las lesiones de un
  paciente antes de puntuar cualquiera.
- **Cómo se reporta:** la mediana de cinco repeticiones, en segundos por cada
  1.000 lesiones, con el equipo y las versiones de software declarados.
- **Qué no se afirma:** los tiempos no se comparan con los de la competencia,
  que usó otro subconjunto y otro equipo; solo comparan los modelos de este
  trabajo entre sí.

**Puerta.** El informe en Markdown, `informe/borrador-v2.md`, e
`informe/demo.html` regenerada, los dos al día con el estado final de
`outputs/`. *Decisión (2026-10-15, de la persona): el docente indicó ese día
que bastan los `.md` y que no se suban PDF. Hasta entonces la puerta era
`informe/informe-final.pdf` y `informe/demo.html` regenerados desde el estado
final de `outputs/`.*

**Riesgo.** Que el informe quede desfasado de `outputs/` — la cuarta clase de
fallo del registro de incidentes (`CLAUDE.md`, regla 6), que ya ocurrió una vez
en este proyecto y costó horas de razonar sobre una fuente equivocada.

**Contingencia.** Regenerar y volver a correr el verificador **como último paso
antes de entregar**, y que ese sea su propio commit. No confiar en que la última
corrida siga siendo la vigente.

**Pendiente (2026-09-26, de la persona).** El proyecto excluye 15 columnas, no
13 como dice el anteproyecto: sección 4.1, *"Antes de modelar se excluyen 13
columnas"*. Las 15 están en `outputs/auditoria-de-fugas.json`. El recuento de
variables del informe final se toma de `outputs/`, no del anteproyecto.

**Decisión (2026-10-02, de la persona): el hallazgo de procedencia entra al
informe.** Es el hallazgo 3 de `CLAUDE.md`. Las columnas de procedencia, que se
excluyen de los modelos desde la decisión del 2026-09-25 (Fase 1), no explican
la ventaja de 2b. Sus cifras salen de
`outputs/sensibilidad-procedencia-repetida.json`, y para que el informe pueda
citarlas, el verificador de trazabilidad deja de excluir ese archivo (commit
«Verificador: la exclusión de sensibilidad, por archivo»). Sigue excluido
`outputs/sensibilidad-procedencia.json`, de una sola partición. Motivo: el
informe tiene que justificar la exclusión de `attribution` y
`copyright_license`, y este hallazgo muestra que esa exclusión no cambia el
desempeño de forma distinguible: se sostiene por razón de uso. Además, es el
segundo resultado de una sola partición que no sobrevive a la validación
repetida.

**Decisiones sobre la demo (2026-10-02, de la persona).** Tomadas sobre el
inventario de lo desfasado en la demo publicada.
- **Menciones del agente.** Se quitan el comentario CSS «cadena de skills» y el
  comentario JS con el 0,0013. Los nombres de archivo y carpeta
  (`eda-diagnostico.md`, etc.) se quedan, con el mismo criterio que el README.
- **Cifras.**
  - Desarrollo y reservado se muestran por separado; no se suman.
  - Las malignas del reservado no se muestran hasta la Fase 5.
  - El 384 aparece solo dentro del texto de `extraccion-imagen.json >
    caracteristica`.
  - Los recuentos derivados, como «50 de 50», van solo si el informe los
    afirma, y hoy no lo hace.
  - El 0,164 y el 0,695 quedan fuera.
  - La Fase 5 se describe sin cifras.
  - M3 sin limpiar queda fuera de la tabla.
  - El porcentaje de positivos va con 4 decimales.
- **Texto.** Todo el texto fijo nuevo sale de frases ya verificadas de
  `informe/borrador-v2.md`. Donde ninguna sirva queda un hueco, y los huecos
  los redacta la persona.
- **Verificación.** La demo muestra los números de un
  `outputs/sintesis-verificacion.json` regenerado sobre
  `informe/borrador-v2.md`, con su `.md` al hacer clic. La explicación de cada
  cifra señalada espera al anexo.

**Respuestas sobre la demo (2026-10-02, de la persona)**, a lo que dejó abierto
el primer paso:
- Que el generador «falle» quiere decir que no escribe la página.
- `extraccion-imagen.json` cuenta como no exploratorio solo si declara
  `datos.reparto`, con el motivo en un comentario: no lee etiquetas (campo
  `nota`). Control positivo: una copia sintética sin `datos.reparto` tiene que
  disparar el aviso.
- El título del eje sale de `modelado-baseline.json >
  escala_de_referencia_pauc`.
- El gráfico de comparaciones muestra los 20 intervalos, cinco comparaciones
  por cuatro métricas: un panel por métrica, con la línea del cero. Elegir solo
  los que cita el informe sería seleccionar, y «Limitaciones» ya describe el
  conjunto completo.
- El nivel 0 sale del gráfico. La historia del error de la métrica sale de la
  demo. El pie deja de mencionar el `.docx`.
- Commodities: no se confirma, y queda fuera.
- Lo desfasado se actualiza: el guardarraíl 2 de `CLAUDE.md` y, en el
  `SKILL.md` de `sintesis-consultoria`, el comando de la Etapa 2 y la
  comprobación de «0,1451». Va después de corregir el verificador, porque sus
  cifras cambian, y en un commit de higiene aparte.

**El efecto de la partición: especificación y regla de lectura (2026-10-04, de
la persona).** Fijadas antes de correr nada. Responde la pendiente de
`CLAUDE.md` «El efecto de la partición sobre el resultado de un modelo no está
medido».

- **Qué se corre.** El nivel 1 (logística balanceada) y el nivel 2b (= M1),
  con la configuración de `evaluar_repetido.py`, sobre el conjunto de
  desarrollo y en dos particiones: la de siempre (`StratifiedGroupKFold` por
  `patient_id`) y una por filas (`StratifiedKFold`, sin agrupar). En las dos, 5
  pliegues y semillas de la 0 a la 9.
- **Qué se reporta, por partición:**
  - las cuatro métricas de cada nivel (pAUC, AUC, sensibilidad top-15 y
    NNT80% SE), en media global y por semilla;
  - la diferencia 2b − 1 en cada métrica, con su intervalo corregido de Nadeau
    y Bengio, como en `outputs/validacion-repetida.json`;
  - por nivel y métrica, la diferencia de medias filas − paciente y en cuántas
    semillas la de filas supera a la de paciente.
- **Control.** La corrida por paciente tiene que reproducir
  `outputs/validacion-repetida.json` pliegue a pliegue en los niveles 1 y 2b.
  Si no, se para.
- **Regla de lectura, fijada antes de correr:**
  - (a) La partición por filas infla una métrica de un nivel si su media
    supera a la de la partición por paciente en las 10 semillas. Vale para la
    pAUC, el AUC y el NNT80% SE, no para la sensibilidad top-15: con partición
    por filas, cada paciente solo tiene en validación una parte de sus
    lesiones, así que el top-15 no mide lo mismo. Se reporta, pero queda fuera
    de la regla. *Precisión de la persona, el mismo día y antes de correr: en
    el NNT80% SE, donde menos es mejor, «supera» se lee como «es mejor», es
    decir, menor. La salida da también los conteos numéricos, sin dirección.*
  - (b) La partición cambia el veredicto si el intervalo corregido de 2b − 1
    en la pAUC excluye el cero en una partición y no en la otra.
  - Si no se cumple ninguna de las dos, se reporta así.
- **Prueba sintética primero:** un caso con un efecto de sujeto fuerte, en el
  que la partición por filas tiene que dar una métrica más alta, y otro sin
  efecto de sujeto.
- **Salida:** `outputs/efecto-particion.json` y `.md` (máximo 15 líneas, sin
  interpretación). El cargador se niega a leer el reservado.

**El efecto de la partición: la corrida.**
- **Cuándo:** el 2026-10-04, en el commit «modelado-baseline: medir el efecto
  de la partición sobre el resultado», a las 12:05 (−0500).
- **Salida:** `outputs/efecto-particion.json` y su `.md`.
- **Lectura, según la regla fijada arriba:** en `informe/borrador-v2.md`,
  «Partir por filas no cambia el veredicto».

*Registro añadido el 2026-10-15: la corrida no se había anotado aquí.*

**La imagen sola: especificación y regla de lectura (2026-10-04, de la
persona).** Fijadas antes de correr nada.

- **Qué se corre.** Dos modelos con la configuración de la validación repetida
  (5 pliegues agrupados por paciente, semillas de la 0 a la 9, los mismos
  pliegues de M1), sobre el conjunto de desarrollo:
  - «Imagen»: regresión logística balanceada sobre las 384 variables de
    DINOv2, estandarizadas dentro del pliegue. Es la misma pieza que M4b usa
    como primera etapa.
  - «Imagen + básicos»: lo mismo, más `age_approx`, `sex` y
    `anatom_site_general`, codificadas como en M1.
- **Qué se reporta:** las cuatro métricas de cada modelo; las diferencias
  Imagen − M1 e (Imagen + básicos) − Imagen, con su intervalo corregido de
  Nadeau y Bengio. No se mide tiempo nuevo: el costo de la imagen ya está
  medido en M4.
- **Control.** M1 tiene que reproducir sus métricas de
  `outputs/fase4-m2-vs-m1.json` pliegue a pliegue. Si no, se para.
- **Regla de lectura, fijada antes:** es descriptivo. No cambia la
  recomendación, que vale para donde se toma la fotografía corporal total.
  Una diferencia se da por establecida solo si su intervalo corregido excluye
  el cero. Los resultados describen el escenario sin mediciones del equipo 3D
  sobre recortes de SLICE-3D, no sobre fotos de teléfono.
- **Salida:** `outputs/imagen-sola.json` y `.md` (máximo 15 líneas, sin
  interpretación). El cargador se niega a leer el reservado. Antes, una prueba
  sintética. No se toca el informe.
- *Precisiones del agente, el mismo día y antes de correr:* la pieza es
  `modelo_imagen()` de `apilado_imagen.py` (estandarizado y logística
  balanceada con `max_iter=2000`), ajustada con el pliegue de entrenamiento y
  puntuando la validación; en «Imagen + básicos» las tres variables pasan por
  `codificar_fold` y después por el mismo estandarizado. El control compara
  también la huella de los pliegues de cada semilla con la de
  `fase4-m2-vs-m1.json`.

**La imagen sola: dos decisiones sobre el resultado (2026-10-04, de la
persona).** Tomadas después de correr.

1. **El intervalo de la pAUC de (Imagen + básicos) − Imagen se lee con la
   precisión guardada.** En `outputs/imagen-sola.json` es [0,0; 0,0089]: no
   excluye el cero, así que esa mejora no se da por establecida. No se vuelve
   a correr, y el recálculo sin redondear que el agente hizo en su scratchpad
   no se cita.
2. **El campo `comando` de la salida.** `imagen_sola.py` lo escribía como
   `python` seguido de los argumentos, y la corrida fue con el intérprete del
   entorno virtual. Se corrige el script para que registre el intérprete y los
   argumentos reales (`sys.executable` y `sys.argv`, con rutas relativas al
   repositorio). `outputs/imagen-sola.json` no se edita a mano ni se vuelve a
   correr: conserva el `comando` de la corrida, y el commit de la corrección lo
   anota.

**La potencia de la prueba: especificación (2026-11-04, de la persona).**
Fijada antes de correr nada. Es descriptiva: no compara ningún modelo, no cambia
ninguna recomendación, no suma a la bitácora y no toca el reservado.

- **La pregunta.** Si un modelo fuera de verdad mejor que M3 limpio en la pAUC
  por una cantidad δ, ¿con qué probabilidad daría su resultado a favor la
  prueba de las fases 4d a 4f? Esa prueba es `fase4d.valor_p`, el valor p
  bilateral de Nadeau y Bengio, y da su resultado a favor con p < 0,05 y media
  positiva. Se responde con 5 y con 10 semillas × 5 pliegues, es decir, con
  n = 25 y n = 50 diferencias.
- **De dónde sale la variabilidad.** De las diferencias pliegue a pliegue de la
  pAUC de las cuatro comparaciones contra M3 limpio que ya están en `outputs/`,
  cada una por separado, sin juntarlas
  (`comparaciones_nuevo_menos_base.pauc.diferencias_nuevo_menos_base`):
  - C4, `fase4c-c4-vs-m3limpio.json`, semillas 0 a 9;
  - C5, `fase4d-c5-vs-m3limpio.json`, semillas 0 a 9;
  - C6, `fase4d-c6-vs-m3limpio.json`, semillas 0 a 4;
  - C7, `fase4e-c7-vs-m3limpio.json`, semillas 5 a 9.

  De cada una se toma s, la desviación típica de sus diferencias.
- **La curva principal: la potencia de la prueba bajo su propio modelo de
  varianza.**
  - Para cada comparación y n ∈ {25, 50}, el error estándar es
    s·√(1/n + 1/4).
  - La probabilidad de «a favor» sale de la t no central de n − 1 grados de
    libertad, con no centralidad δ / (s·√(1/n + 1/4)).
  - δ va de 0,002 a 0,02 en pasos de 0,001.
  - Se reporta, por comparación y n, el δ con el 50 % y con el 80 % de
    potencia.
- **El modelo de varianza no es un supuesto añadido: es el de la prueba.** La
  prueba ya supone una correlación ρ = 1/5 entre las diferencias, la razón
  n_prueba/(n_entrenamiento + n_prueba) con 5 pliegues. De ella sale el
  1/4 = ρ/(1 − ρ) de su error estándar
  (`referencias/nadeau-bengio-2003-t-corregido.md`). Sus autores la llaman
  *"gross"* (p. 254). En esa misma página, el artículo dice que, con
  diferencias normales y ρ igual a ρ₀, el estadístico sigue una t de J − 1
  grados de libertad; de ahí sale la t no central de la curva (paráfrasis; es
  su Lema 2).
- **Lo que la curva no incluye.**
  - La incertidumbre de s: se toma como la dispersión verdadera.
  - La forma de las diferencias de un modelo que fuera de verdad δ mejor: se
    supone la de C4 a C7, desplazada en δ.
- **Control por simulación.**
  - **El generador** es el del control negativo de la 4d,
    `test_fase4d_comparacion.correlacionadas`, con diferencias normales de
    correlación 0,2.
  - **La escala.** Para cada comparación, se llevan a la desviación s (cómo,
    en las precisiones del agente, abajo) y se les suma δ.
  - **Cuántas veces.** 20.000 juegos por comparación, n y δ, con semilla 2026,
    la del control de la 4d. Los juegos son los mismos para todos los δ de una
    comparación y un n.
  - **Los controles, cada uno con su caso que debe fallar:**
    - (a) La tasa simulada coincide con la analítica dentro del error de
      Monte Carlo, en cada comparación, n y δ. *Debe fallar:* el generador con
      ρ = 0.
    - (b) Con δ = 0, la tasa es a lo sumo el 5 %. *Debe fallar:* la t sin
      corregir, `fase4d.valor_p_ingenuo`, como en la 4d.
    - (c) Con δ = 0,05, la tasa a favor es al menos el 99 %. *Debe fallar:*
      δ = −0,05.
- **Controles previos, sobre las diferencias guardadas.**
  - **La prueba es la nuestra.** Desde las diferencias, `fase4d.valor_p` y el
    intervalo de `evaluar_repetido._nadeau_bengio` reproducen la `media`, la
    `desviacion` y el `intervalo_t_95_nadeau_bengio` guardados, a 4 decimales,
    en las cuatro. También reproducen el `valor_p_nadeau_bengio` de C5, C6 y
    C7, con una diferencia de como mucho 0,002, porque las diferencias están
    guardadas con 4 decimales. *Debe fallar:* la t sin corregir.
  - **Los bloques son semillas.** La lista guardada coincide, en su orden, con
    candidato − M3 limpio calculado desde `metricas.*.pauc.por_semilla_y_fold`,
    semilla por semilla, con una diferencia de como mucho 0,00015, porque son
    dos valores redondeados. *Debe fallar:* la lista desplazada una semilla.
- **Una línea descriptiva, entre semillas.** Por comparación, el error estándar
  de la media entre semillas frente al de la prueba, con su propio n:
  - entre semillas, la desviación de las medias por semilla dividida por
    √(semillas);
  - el de la prueba, s·√(1/n + 1/4).

  Va como una línea, no como curva. Mide cuánto cambia la media con los mismos
  pacientes; la pregunta es por pacientes nuevos.
- **Salida:** `outputs/potencia-nadeau-bengio.json` y su `.md` (máximo 15
  líneas, sin interpretación), de `potencia_nadeau_bengio.py`, en los scripts
  de `modelado-baseline`. El script solo lee los cuatro `.json`: ni `data/` ni
  el reservado.
- *Precisiones del agente, el mismo día y antes de correr:*
  - **La escala.** El generador da a cada diferencia varianza 1 y, dentro de
    un juego, una varianza esperada de 1 − ρ. Por eso se multiplica por
    s/√(1 − ρ) y no por s: así la desviación esperada dentro de un juego es s,
    la de la curva analítica.
  - **El error de Monte Carlo** es de 4 veces √(p(1 − p)/20.000), con p la
    tasa analítica y p(1 − p) de al menos 1/20.000. El control (a) se aplica a
    la tasa a favor y al rechazo bilateral.
  - **El control (b).** Con ρ = 0,2 la prueba es exacta, así que su rechazo
    bilateral con δ = 0 es del 5 % en esperanza, y un límite del 5 % sin
    margen fallaría por azar la mitad de las veces. El control pide que la
    tasa a favor sea a lo sumo 0,05, y que el rechazo bilateral sea a lo sumo
    0,05 más 4 errores de Monte Carlo. Que ese rechazo coincida con su valor
    analítico, el 5 %, lo comprueba el control (a).
  - **El valor p de la simulación** se calcula vectorizado, con la fórmula de
    `fase4d.valor_p`. Antes de usarlo, tiene que coincidir con
    `fase4d.valor_p` en los primeros 2.000 juegos de cada comparación y n, con
    una diferencia de como mucho 1e−12. *Debe fallar:* la versión vectorizada
    sin corregir.
  - **Los δ al 50 % y al 80 %** se buscan sobre la curva analítica continua,
    no en la rejilla de 0,001, y se reportan con 4 decimales.

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
al que atribuírselo. Y el ganador completo es un **ensamble con características
de imagen**. En este trabajo entra como comparador, pero reproducido solo en su
parte tabular y de contraste intra-paciente, sobre nuestras particiones (Fase
4): la comparación es contra esa parte, no contra su ensamble con imágenes.
*Hasta el 2026-09-24 esta frase decía que medirse contra él antes de la Fase 4
"sería compararse con algo que todavía no se está construyendo".*

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

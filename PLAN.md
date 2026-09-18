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
preentrenamiento de PanDerm o de DermFM-Zero. MSKCC, anfitrión de ISIC 2024,
aparece mencionado como fuente institucional de esos modelos, y ~35% del
preentrenamiento de PanDerm es fotografía corporal total — la misma modalidad
que este dataset.

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
fallo del registro de incidentes (`CLAUDE.md`, regla 5), que ya ocurrió una vez
en este proyecto y costó horas de razonar sobre una fuente equivocada.

**Contingencia.** Regenerar y volver a correr el verificador **como último paso
antes de entregar**, y que ese sea su propio commit. No confiar en que la última
corrida siga siendo la vigente.

---

## Decisiones pendientes

### ¿El componente de recuperación de casos similares entra al alcance?

**Estado: declarado y sin medir desde el principio.** Uno de los dos premios
secundarios oficiales del reto fue *"Top-15 Retrieval Sensitivity"*, con el
mismo monto que el de eficiencia (`referencias/kaggle-rules.md`). Mide el
desempeño **por paciente**, no por lesión — una unidad de análisis distinta de
la del pAUC, y la que un dermatólogo usa realmente.

El proyecto lo cita desde el primer día como prueba de que la métrica principal
no agota la función de utilidad del cliente, y hasta hoy no lo ha medido. Esa
asimetría es incómoda: se usa como argumento y no como resultado.

Las dos salidas son legítimas y **ninguna está tomada**:

- **Entra como sexto objetivo.** Se mide, y el argumento del corolario pasa de
  afirmado a demostrado.
- **Se excluye,** con la razón escrita en el alcance de la fase 0. Una exclusión
  razonada es una decisión de consultoría; una omisión silenciosa no.

Lo que **no** es aceptable es seguir citándolo sin decidir. La decisión se toma
en la fase 0, porque es donde se fija el alcance, y condiciona si la tabla de la
fase 6 tiene dos columnas o tres.

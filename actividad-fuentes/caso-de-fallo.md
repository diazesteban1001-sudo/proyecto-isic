# Caso de fallo: Little et al. (2017) en el tratamiento C

Qué es: el caso de fallo que pide el enunciado. NotebookLM, con el corpus
cerrado, le atribuyó a Little et al. (2017) lo contrario de lo que dice. Este
archivo busca la causa técnica. Añade además dos casos menores del banco de
evaluación.

## Qué respondió NotebookLM

Es la quinta referencia de la respuesta C (`respuestas/respuesta-C.md`):

> Afirmación concreta: Analiza las propiedades probabilísticas de las
> estrategias de validación cruzada y confirma que dividir los datos
> aleatoriamente por registro en lugar de por sujeto viola la suposición de
> muestras idénticamente distribuidas cuando los datos están agrupados por
> paciente. Esto genera estimadores sesgados que subestiman significativamente
> el error de predicción real que tendría el modelo al enfrentarse a nuevos
> pacientes en la práctica clínica.

Las dos pasadas la clasificaron como «existe pero no dice eso», por el mismo
motivo: invierte a Little (`pasada-1.csv` y `pasada-2.csv`, id 863).

## Qué dice Little

El artículo tiene tres voces. El archivo del corpus lo avisa al empezar:

> This review is organized in three sections, each presenting a different view
> on the suitability of different cross-validation strategies: one by M.A.
> Little, one by G. Varoquaux (who both also reviewed the original paper), and
> one by Saeb et al.

Para Little, la partición que rompe el supuesto de distribución idéntica es la
partición **por sujeto**, no la partición por registro:

> But this leads inevitably to violating the identically distributed
> assumption, which is required for subject-wise CV to produce consistent
> estimates of the out-of-sample prediction accuracy.

> in the identity-clustered data case (that can cause identity-confounded
> predictions), subject-wise CV does not produce a consistent estimate of the
> out-of-sample prediction error.

Que la partición por registro **subestima** el error es la tesis de Saeb et al.
Little la resume para discutirla, y Saeb et al. la defienden en la tercera
parte:

> (iii) record-wise CV creates dependence between training and test sets due
> to shared identities across train/test sets, so it will produce biased
> estimates (e.g., prediction errors are underestimated).

> When record-wise CV underestimates the use-case prediction error

## A qué pasajes apuntan sus citas

Según la lista de citas que copió la persona (`respuestas/respuesta-C.md`,
sección «Lista de citas»), las tres citas de esta referencia van a
`little-2017.txt`:

- **[19]** apunta a la cabecera del artículo: año, volumen, DOI y título. Solo
  sirve para identificar el trabajo.
- **[17]** apunta al comienzo del cuerpo, tras las palabras clave. El texto que
  sigue presenta las tres voces y abre la parte de Little. Poco después viene
  su resumen de las tesis de Saeb et al., con la (iii) citada arriba, y a
  continuación la frase *"I could not really grasp the assumptions of their
  probabilistic arguments"*.
- **[18]** apunta al pasaje de Little sobre partir los datos según una
  variable:

  > Let us now split the data in a way that is conditioned on one of the
  > variables in the data or some other variable upon which the data depends.
  > The split is no longer in general independent of the data. A simple example
  > is splitting on subject identity. This modification of record-wise CV is
  > indeed subject-wise CV, and we ideally want it to inherit the i.i.d.
  > assumption of record-wise CV, for then we can simply borrow the applicable
  > theory wholesale. But we will find that for some kinds of data we can
  > create a split that violates the “identically distributed” assumption of
  > record-wise CV

Ninguna cita apunta a la tercera parte, la de Saeb et al.

## Causa técnica

Son dos fallos que se suman, y ninguno es una respuesta de memoria: todo lo
que dice la afirmación está en el archivo.

1. **El modelo ignoró el contexto del fragmento correcto.** El pasaje [18] es
   de Little y es pertinente. Dice que una partición condicionada en la
   identidad, es decir, por sujeto, puede violar un supuesto que pertenece a
   la partición por registro: *"the “identically distributed” assumption of
   record-wise CV"*. La afirmación convierte a la partición por registro en la
   causa de la violación. Es una lectura invertida de quién rompe el supuesto
   y de quién es el supuesto.
2. **Atribuyó a Little una tesis de Saeb et al.** «Subestiman el error de
   predicción» es la tesis (iii) de Saeb et al. En la zona a la que apunta
   [17], Little la resume para discutirla, y la afirmación la presenta como lo
   que Little «confirma». Hay un indicio de que el fragmento recuperado de [17]
   llegaba hasta ese resumen: «propiedades probabilísticas» corresponde a
   *"their probabilistic arguments"*, la frase que sigue a la tesis (iii).

Queda un límite: la lista de citas solo da dónde empieza cada pasaje citado,
no cuánto abarca. Que el fragmento de [17] incluyera el resumen de las tesis de
Saeb et al. es una inferencia, no una observación. Tampoco se puede descartar
que el modelo tomara la tesis de la tercera parte sin citarla.

**Por qué este documento lo favorece.** Tres autores, con posiciones opuestas,
comparten un solo archivo y una sola cita: «Little et al. (2017)». Un fragmento
recuperado sin su encabezado, *"Perspective by M. A. Little"*, no dice qué voz
habla. Las frases de Little que resumen a Saeb et al. para rebatirlos se
parecen, fuera de contexto, a frases que los apoyan.

**Qué lo habría evitado.**
- Para el sistema: la v2 del protocolo exige citar pasajes continuos, pero no
  resuelve este caso. Este fallo solo lo detecta abrir el pasaje citado y leer
  quién habla.
- Para el corpus: partir los artículos de varias voces en un archivo por voz
  habría dado a cada fragmento su autor. No se hizo, y queda como mejora
  posible.

## Casos menores, del banco de evaluación

Salen de `banco-resultados.md`. Ninguno cambió la respuesta a lo que pedía la
pregunta.

- **P14, cita cosida presentada como textual.** NotebookLM puso entre comillas
  *"survey of 22 papers across 17 fields"*, una frase que no existe así en
  `kapoor-narayanan-2023.txt`. El archivo tiene *"Survey of 22 papers that
  identify pitfalls in the adoption of ML methods across 17 fields"* y *"we
  find 22 papers across 17 fields"*. El dato es correcto, pero la «cita
  textual» es una paráfrasis armada con dos pasajes. Motivó la v2 del
  protocolo (`protocolo-consulta-v2.md`).
- **P08, equipos llamados participantes.** Dice que en
  `kurtansky-2024-kaggle.txt` «el número total de participantes registrados fue
  de 2.739 equipos». La página distingue *"3,410 Participants"* de *"2,739
  Teams"*. Es una lectura imprecisa del fragmento correcto.

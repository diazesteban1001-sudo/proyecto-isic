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

Los **melanógrafos marcaron 8.913 lesiones** para examen detallado y el sistema
automático **3.498**, una **reducción del 60,8%** de exámenes innecesarios. Que
las dos cifras se refieran a los 80 pacientes de prueba es **lectura nuestra**:
la frase dice *"80 patients"*, no *test*, y los métodos definen ese conjunto
como *"80 patients for testing (30,698 images, including 28 malignant
lesions)"*. **El 79 de 80 no se usa.** Con 28 lesiones malignas, como mucho 28
de esos pacientes tienen malignidad, así que la frase, leída al pie de la letra
y sobre los pacientes de prueba, no cuadra. El artículo no define cómo mide el
resultado por paciente, y la *Supplementary Table 18* a la que remite solo da
precisión y recall por lesión (detalle en la ficha). *Hasta el 2026-09-24 este
párrafo daba el 79 de 80 como dato.*

El artículo da para el conjunto completo —los 480 pacientes, no la evaluación—
*"216 malignant versus 197,716 benign lesions"*, pero esas dos cifras suman
197.932, y el total que dan los métodos, la leyenda de la figura 4e y la suma de
las tres particiones es 196.933: el 197.716 no cuadra, y el artículo no declara
errata. La prueba tiene 28 malignas entre 30.698 imágenes. Con cualquiera de las
dos cifras el desbalance es del mismo orden que el de SLICE-3D (393 sobre
401.059). *Hasta el 2026-09-24 esta frase atribuía el 216/197.716 a la
evaluación y no advertía que no suma.*

Qué aporta al criterio 1: convierte "reducir carga de trabajo" en una magnitud
con unidades. El costo de un falso positivo deja de ser abstracto y pasa a ser
un examen detallado que alguien tiene que hacer, contable.

**Tres salvedades, obligatorias al citarla** (detalle en el archivo de
`referencias/`):

1. El paper dice **"melanographers"**, palabra que aparece una sola vez y que
   **no define**. Traducirlo como "especialistas en melanoma" sería una
   sustitución nuestra, y el artículo no da base para decir quiénes son. Se
   cita la palabra del paper. *Hasta el 2026-09-24 decía que la sustitución
   "probablemente exagera la comparación"; eso se apoyaba en una descripción
   del melanógrafo sin fuente, retirada de la ficha.*
2. Los autores **no discuten esta comparación en sus limitaciones**: no hay
   análisis de factores de confusión ni de diferencias de protocolo.
3. El **8.913 es el lado humano** y es la línea base independiente utilizable;
   el 3.498 es desempeño de PanDerm reportado por sus propios autores.

*Nota de deslinde:* PanDerm es también el modelo que la Fase 2 decidió no usar
(2026-09-24), porque su artículo declara SLICE-3D entre sus fuentes de
preentrenamiento (sub-etapa **E1**, «Riesgo bloqueante»). Citar el 8.913 no
depende de esa decisión: es una medición sobre personas.

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

### 3. Nada de memoria como fuente — y cómo se guarda la fuente

El agente no cita de memoria las reglas de la competencia, la definición de la
métrica ni la estructura de los datos. Lee la página oficial y los datos reales.
Toda fuente que el proyecto cite queda en `referencias/`, abierta, leída y con
su procedencia en la cabecera.

**Cómo se guarda depende de su licencia, porque este repositorio es público.**
Enmendada el 2026-09-21; antes se versionaba el texto completo de todo.

- **Cada archivo de `referencias/` declara su LICENCIA en la cabecera**, con la
  evidencia de dónde se leyó —la propia fuente, el depósito de la editorial en
  Crossref, los términos del sitio—. La licencia se determina, no se supone. Si
  no se puede determinar, o si su aplicación a ese texto es interpretación
  nuestra, cuenta como desconocida.
- **Licencia que autoriza redistribuir la obra sin modificar para este uso:** el
  texto completo se versiona, con la atribución, el enlace a la licencia y la
  nota de qué se omitió, que es lo que esas licencias exigen. El criterio no es
  el nombre de la licencia sino **qué autoriza para lo que hacemos**: publicar
  el texto tal cual en un repositorio académico, sin fines comerciales.
  - **CC BY: sí.**
  - **CC BY-NC-ND: también.** NC se cumple porque el repositorio es académico y
    no comercial; ND, porque el texto va **sin adaptar**. Extraer el texto de
    un PDF o de una página es un cambio de formato, no una adaptación, y todo
    lo nuestro va en secciones separadas y marcadas como nuestras. *Caso que
    motivó la precisión:* Cassidy et al. 2022
    (`referencias/cassidy-2022-duplicados-isic.md`), CC BY-NC-ND 4.0, cuyo
    texto legal autoriza *"reproduce and Share the Licensed Material, in whole
    or in part, for NonCommercial purposes only"* (§2(a)(1); en local,
    `referencias/_texto-completo/cc-by-nc-nd-4.0-legalcode.txt`). Con la
    redacción anterior, *"CC BY o similar"*, no estaba claro de qué lado caía.
  - **Apache 2.0, y cualquier licencia que obligue a marcar los archivos
    modificados: los originales se versionan intactos**, byte a byte, y la
    procedencia y la licencia van en un `.md` hermano, no dentro del archivo.
    Ponerle una cabecera sería modificarlo, y Apache 2.0 exige *"You must cause
    any modified files to carry prominent notices stating that You changed the
    files"* (§4(b)). Es la única excepción a que la licencia se declare en la
    cabecera del propio archivo. *Ejemplo:* la carpeta
    `referencias/novoselskiy-2024-isic2024/`, con el `README.md`, el `LICENSE`
    y un notebook de la solución ganadora sin tocar, y a su lado
    `referencias/novoselskiy-2024-isic2024.md`, con la URL, el commit, la fecha,
    la licencia y el SHA-256 de cada archivo.
  - **No bastan**, y van a ficha: una licencia solo de minería de textos, los
    términos generales de una editorial, o una licencia que autoriza a
    distribuir a un tercero concreto y no a nosotros —la no exclusiva de
    arXiv—.
- **Con copyright o licencia desconocida:** el archivo versionado es una
  **ficha** — datos bibliográficos, licencia, localizadores de página o
  sección, y las **citas literales exactas** de los pasajes que el proyecto
  usa. **Nunca paráfrasis presentada como cita**: lo que no es literal va
  marcado como paráfrasis. El texto completo se guarda en
  `referencias/_texto-completo/`, que está en `.gitignore`.
- **Una cita solo entra al informe si se comprobó carácter a carácter contra el
  texto completo**, esté versionado o sea la copia local. La ficha registra la
  cita; no sirve para verificarla, porque verificar es comprobar que la frase
  está en la fuente, y la ficha es un extracto hecho por nosotros.
- **Una cita se conserva en una ficha solo mientras algún documento del proyecto
  la use** —incluido el análisis de la propia ficha—. Cuando deja de usarse, se
  retira: una ficha que acumula citas que nadie usa vuelve a ser, poco a poco,
  el texto completo que la regla dejó de versionar.
- **Cuando un archivo de `referencias/` cambia de forma —de texto completo a
  ficha, o al revés; renombrado; renumerado—, se buscan en el repositorio las
  frases que lo describen**, porque pueden haber quedado falsas aunque nadie las
  haya tocado. No basta con buscar el nombre del archivo: hay que leer qué dice
  cada mención de él. *Motivo:* al reducir fuentes a ficha el 2026-09-21, el
  borrador y este archivo siguieron llamándolas "copia literal" en **ocho
  frases**. Tres se vieron al reducir; las otras cinco solo aparecieron al
  buscarlas expresamente, y cuatro de esas cinco no nombraban ningún archivo
  —hablaban de "copias literales en `referencias/`" en general—, así que buscar
  por nombre de archivo no las habría encontrado.
- **La historia de git no se reescribe.** Los textos con copyright que ya se
  subieron siguen en los commits anteriores y se retiran de este en adelante.
  Reescribir la historia para borrarlos rompería toda referencia a esos commits
  —el caso de los hashes de la regla 6— y no los retiraría de ningún clon ya
  hecho.

**Consecuencia que hay que tener presente:** `referencias/_texto-completo/` no
viaja con el repositorio. En una máquina nueva está vacío, y la comprobación
carácter a carácter no se puede hacer hasta volver a obtener cada texto desde la
URL de su ficha. Es el precio de no publicar lo que no es nuestro, y se paga a
sabiendas.

### 4. Graphify se consulta, no se cita

El grafo de Graphify se consulta para navegar el repositorio y para detectar
desfases entre documentos. No es una fuente. Ninguna cifra, afirmación ni
referencia sale de `graph.json`, `GRAPH_REPORT.md` o `graph.html` sin
comprobarse antes contra el archivo original.

**Motivo medido**, sobre la corrida identificada por `built_at_commit`
`500159ba064c9ad4c2e1155260fc8b94a5dc80a5` (37 archivos fuente, listados en
`graphify-out/manifest.json`): el paso semántico produjo **197 aristas**
repartidas en 25 archivos de caché, y **121 de ellas —el 61,4%— referencian
nodos que no están declarados en su propio archivo**. De esas 197, al construir
el grafo sobrevivieron **160**: **37 se descartaron**. El paso AST sobre código
es determinista y no tiene ese problema — sus 210 aristas en `graph.json` no
incluyen ninguna colgante.

*Sobre ese hash:* `500159ba…` es el valor que `graph.json` grabó en
`built_at_commit`, y por eso es el que imprime el comando de abajo. Ese commit
se reescribió al poner `main` al día con `origin` (rebase del 2026-09-19) y hoy
vive en la historia como `82f3fd6`, con el mismo árbol salvo una línea de fecha
en `README.md`. El identificador de la corrida no se toca —es un dato grabado
dentro del artefacto, no una cita que podamos actualizar—; lo que se anota es
la equivalencia, para que buscar `500159ba` en `git log` y no encontrarlo no se
lea como que la corrida no existió.

**El grafo exportado no muestra el problema, y eso es información, no un
inconveniente.** `graph.json` tiene **0 aristas colgantes** sobre sus 239 nodos
y 370 enlaces, porque el constructor descarta al exportar las que no resuelven.
La tasa de invención solo es visible en `graphify-out/cache/semantic/`, nunca en
el artefacto que uno abre para consultar. Es decir: el archivo que la regla
prohíbe citar es también el que oculta la razón por la que se prohíbe.

**Procedencia — cómo rehacer la cifra.** Desde la raíz del repositorio, con el
`graphify-out/` de esa corrida en su sitio:

```bash
python3 -c "
import json,glob
tot=huer=0
for f in glob.glob('graphify-out/cache/semantic/**/*.json',recursive=True):
    d=json.load(open(f)); ids={n['id'] for n in d['nodes']}
    for e in d['edges']:
        tot+=1; huer+= e['source'] not in ids or e['target'] not in ids
g=json.load(open('graphify-out/graph.json'))
sem=sum(1 for l in g['links'] if not l.get('_origin'))
print(f'corrida {g[\"built_at_commit\"][:12]}: {huer}/{tot} huerfanas; {tot-sem} descartadas; {sem} en graph.json')
"
```

Salida esperada, literal:

```
corrida 500159ba064c: 121/197 huerfanas; 37 descartadas; 160 en graph.json
```

Salvedad de reproducibilidad, que forma parte de la cifra: `graphify-out/` está
en `.gitignore`, así que esto se rehace sobre el directorio de esa corrida, no
desde el repositorio. Una corrida nueva da otros números — y ese es exactamente
el defecto que se describe abajo.

**Cifra retirada — segundo ejemplar de la cuarta clase de fallo.** Esta regla se
escribió el 2026-09-17 citando *"65 de las 163 aristas del paso semántico"*,
≈40%. Ese par de números **no se puede reproducir desde el estado actual de
`graphify-out/`**: corresponde a una corrida distinta, que ya no está en disco.
No estaba mal medido; estaba medido sobre otra cosa, y nada en el archivo decía
sobre cuál. Es el mismo modo de fallo registrado en la regla 6 —un artefacto que
se desfasa de lo que lo produce y se sigue citando como si no—, esta vez dentro
de la propia regla que prohíbe citar sin comprobar. Se retira, no se borra: la
línea de procedencia de arriba existe porque esta cifra no la tenía.

### 5. El estado vive en archivos, no en conversaciones

Al cerrar cada sesión se actualiza el archivo que corresponda, y son dos
distintos: las decisiones tomadas y lo medido van aquí; la fase vigente y el
siguiente paso van en `PLAN.md`. Un solo dueño por cosa — el "siguiente paso"
estuvo en los dos archivos a la vez y así fue como se desfasaron. Una
conversación por tarea, no una para todo. Commit frecuente.

### 6. Código que parece muerto: conectarlo antes de borrarlo

**Antes de eliminar un import, una variable o una rama que parezcan sin uso,
comprobar si conectarlos cambia el resultado.** Si lo cambia, no era código
sobrante: era una corrección a medio cablear, y borrarla habría consolidado el
defecto en vez de limpiarlo.

Esta regla existe porque el patrón ya apareció tres veces, y las tres el código
inerte marcaba el sitio exacto de un defecto real. Las filas siguientes no
son ese patrón: son otras formas de equivocarse que el proyecto ha cometido de
verdad, cada una con su propio remedio; la octava es una variante de la
séptima, y la novena no es una clase nueva: son dos instancias más de la
séptima y la octava. La décima sí es una clase nueva. La tabla es el registro de
incidentes del proyecto: las tres primeras filas son ese patrón; de la cuarta a
la octava, y la décima, son clases distintas, anotadas aquí porque el registro
vive en un solo sitio y partirlo lo volvería fácil de no consultar.

| Dónde | Qué parecía | Qué era en realidad |
|---|---|---|
| `eda-diagnostico`, `duplicados_exactos` | Un chequeo que siempre daba 0 | Incluía la clave primaria, así que no podía detectar nada. Vacío de contenido, no correcto. |
| `auditoria-de-fugas`, `preguntas_abiertas()` | Una rama que nunca se ejecutaba | `auc_alto is None` sobre un `.get(..., False)`. Se comía 9 de las 10 preguntas, incluida `tbp_lv_dnn_lesion_confidence`. |
| `modelado-baseline`, `StandardScaler` | Un import muerto | La logística no convergía sin escalar. El pAUC reportado era el del optimizador detenido, no el del modelo. |
| `sintesis-consultoria`, `outputs/sintesis-verificacion.json` | La salida de correr el verificador sobre el borrador | La salida de una corrida **intermedia** de esa sesión, commiteada junto a un código que ya no la producía (el commit "Verificador: la regla de porcentajes aceptaba coincidencias fortuitas", 2026-09-17). Decía 26 señalados; el código de ese mismo commit, sobre el corpus de ese mismo commit, da 27. El `15` de la línea 99 figuraba como respaldado sin haberlo estado nunca. |
| `CLAUDE.md`, la cifra que justificaba la regla 4 | Un motivo medido sobre el grafo de Graphify: "65 de las 163 aristas del paso semántico" | Una medición de una corrida **que ya no estaba en disco**. El `graphify-out/` presente da 121 de 197. La cifra no se podía rehacer, y el texto no decía sobre qué corrida se había tomado — así que tampoco se podía saber que no se podía rehacer. Retirada el 2026-09-17. |
| `CLAUDE.md`, tres hashes de commit citados | Punteros estables a tres cambios del repositorio | Dejaron de resolver desde `main` en cuanto un rebase los reescribió. Poner `main` al día con `origin` reescribió los 14 commits locales, y `29a0f47` (tabla de incidentes), `e930c89` (guardarraíl 2) y `500159ba` (regla 4) pasaron a no ser ancestros de `main`: buscarlos en `git log` no los encuentra. **Ningún archivo se tocó**; las citas caducaron solas, por una operación rutinaria hecha en otra parte del repositorio. 2026-09-19. |
| `referencias/yang-2019-two-way-partial-auc.md`, la nota sobre por qué importa | Una lectura del script oficial de la métrica: que ISIC 2024 restringe el FPR para controlar el TPR de forma indirecta, y que por eso le aplica la crítica de Yang et al. al *FPR pAUC* | Falso. La línea 42 del script original `PrimaryMetric-pAUC.py` —ficha en `referencias/isic-primary-metric-pauc.py.md`; era la 54 de la copia versionada hasta el 2026-09-21— **invierte las etiquetas** antes de calcular la ROC, así que la variable que el código llama `fpr` es `1 − TPR_original`: la restricción sobre el TPR es **directa** y el FPR **no se acota**. La afirmación se construyó combinando dos lecturas plausibles —`max_fpr` en el nombre, `auc(fpr, tpr)` en la integral— **sin abrir el archivo que las decidía**, y sobrevivió un commit entero. 2026-09-19. |
| **Dos instancias.** (1) `PLAN.md`, cuarta línea del estado del arte, y la nota de `referencias/kurtansky-2024-slice3d-descriptor.md`. (2) **La conversación**: la instrucción de versionar `challenge2024.isic-archive.com/background/` | (1) Una comprobación: que ninguna fuente versionada afirmaba que los pacientes de prueba de ISIC 2024 fueran distintos de los de entrenamiento. (2) Una fuente: que esa página dice que el conjunto de prueba contiene 500.000 imágenes adicionales de un conjunto de pacientes distinto | **(1) Del lado del agente — rastreable.** Falso. `referencias/kurtansky-2025-triaje-automatizado-tbp.md` lo dice en su sección de métodos —*"albeit different patients than the training dataset"*—, y estaba en el repositorio desde el 2026-09-19. La afirmación se hizo tras **buscar una expresión** —*"no patient overlap"*— en vez de leer el artículo: la búsqueda encontró otra frase, que hablaba de los subconjuntos del leaderboard, y ese hallazgo se tomó por el mapa completo. Entró con el commit "referencias: cuarta linea del estado del arte, fuga por sujeto" y se corrigió el mismo día, 2026-09-21. **(2) Del lado de la persona — NO rastreable en el repositorio: vive solo en la conversación**, y se registra aquí para que no parezca que hay un commit detrás. Instrucción dada en conversación el 2026-09-19, ejecutada el 2026-09-21. Salió de **un fragmento de resultado de un buscador**: la página nunca se abrió ni se comprobó que respondiera. Al ejecutarla, la página redirige de forma permanente (301) a la de datos del reto, y el Internet Archive **nunca la capturó** —de 73 capturas del dominio, ninguna es de `/background/`—, así que la afirmación no se puede comprobar ni siquiera a posteriori. **La tanda se gastó en buscarla mientras lo que afirmaba ya estaba en una fuente versionada**: Kurtansky 2025 dice *"Test data comprised about 500,000 lesion tiles from more than 1200 patients"* y, en la misma sección, *"albeit different patients than the training dataset"*. **Variante de la séptima clase: una afirmación de ausencia (1), y una fuente que nadie abrió (2).** |
| **Dos instancias.** (1) `referencias/panderm-reduccion-examenes.md` y `CLAUDE.md`, sección «Línea base». (2) **La conversación**: la nota de verificación del apartado 1 del anteproyecto, sobre la sección de preentrenamiento de Yan et al. 2025 | (1) Una lectura del alcance de la línea base: que el 3.498, el 8.913 y el «79 de 80» correspondían *"al mismo grupo de 80 pacientes"* porque la frase los enuncia en una sola oración, y que el desbalance «de esa evaluación» era 216 contra 197.716. (2) Una lectura de las fuentes de preentrenamiento de PanDerm: que su solape con SLICE-3D era *"evidencia de solape a nivel de estudio, no prueba de que las mismas imágenes estén en los dos conjuntos"* | **(1) Del lado del agente — rastreable.** Falso en las dos partes. Los métodos del mismo artículo definen la prueba como *"80 patients for testing (30,698 images, including 28 malignant lesions)"*: con 28 malignas, el 79 de 80 no cuadra leído al pie de la letra. Y 216 + 197.716 = 197.932, no el 196.933 que el artículo da tres veces, y es el conjunto completo, no la evaluación. La ficha se construyó con **WebFetch**, que no devuelve el texto de la página sino, según su propia descripción, lo que responde sobre ella *"a small fast model"*: dos de sus cinco citas no eran literales, y uno de sus límites era una afirmación de ausencia falsa —la declaración de ética dice *"Only de-identified retrospective data were used for research"*—. Entró el 2026-08-20 y se corrigió el 2026-09-24, desde el commit "Linea base: el 79 de 80 de PanDerm no se sostiene contra sus metodos" hasta "referencias: PanDerm, retirar la descripcion de melanografo sin fuente". **(2) Del lado de la persona — NO rastreable en el repositorio: vive solo en la conversación**, y se registra aquí para que no parezca que hay un commit detrás. En la sesión de redacción del apartado 1, el 2026-09-24, la sección *"Pretraining dataset for developing PanDerm"* se leyó cortada y la nota de verificación hizo esa afirmación, enumerando como fuentes de TBP solo MYM y HOP. Cinco subsecciones después de la de HOP, en la misma sección, la subsección *"ISIC2024"* declaraba *"We selected a subset containing 352,034 tile images"*, con la referencia 47, que es el descriptor de SLICE-3D. **La séptima clase en (1), una afirmación sobre una fuente sacada de una frase sin leer los métodos que la acotaban; la octava en (2), la lectura de un fragmento tomada por completa.** |
| `modelado-baseline`, nivel 0, función `evaluar_columna_sola` de `train_and_evaluate.py` | Una referencia univariada: la columna de mayor AUC, que `SKILL.md` describe como *"se usa cruda como predictor"* | Una referencia orientada con las etiquetas de validación. En cada pliegue toma `max(pauc_above_tpr(y[val_idx], s), pauc_above_tpr(y[val_idx], -s))`, así que la dirección de la variable se elige mirando el resultado que después se reporta. La docstring lo decía; `SKILL.md`, no. La columna misma se elige con el AUC fuera de muestra de `auditoria-de-fugas`, calculado sobre todos los pliegues, que tiene un problema parecido. Se detectó el 2026-09-24, al contrastar con el código la descripción del nivel 0 en el apartado 4 del anteproyecto. El efecto no está medido. Corregido en el código el 2026-09-25 (commit "modelado-baseline: el nivel 0 elige variable y orientación en el entrenamiento"); el efecto se mide en la re-medición de la Fase 1. **Clase nueva: el instrumento elige con las etiquetas con que se evalúa.** |

**De la cuarta a la octava, y la décima, son de otra clase, y por eso se anotan
aparte.**
Las tres primeras son código inerte dentro de un script: se detectan leyendo el
script, y la regla de arriba —conectarlo y comparar— basta para atraparlas. Las
demás no están en ningún script. La cuarta y la quinta son **artefactos
desfasados del código que los produce**: archivos sintácticamente válidos, con el nombre correcto y el
formato correcto, que aun así no eran el resultado de correr el código con el
que viajaban.

Su costo real no fue el número equivocado sino que **durante horas fue la fuente
que se usó para razonar**: un señalamiento que no existía se tomó como recién
aparecido, y se buscó en el corpus la causa de un cambio que nunca ocurrió. El
diagnóstico solo llegó reconstruyendo el corpus de `HEAD` y volviendo a correr
el verificador sobre él — es decir, haciendo a mano lo que nadie estaba
haciendo.

**La quinta añade un agravante que la cuarta no tenía: el artefacto ni siquiera
estaba versionado.** `graphify-out/` está en `.gitignore`, así que no había
forma de reconstruir la corrida de la que salía el 65/163 — con la cuarta al
menos existía `git show HEAD:`. Una cifra tomada de un artefacto no versionado
no es reproducible ni en principio, y el único remedio disponible es el que se
aplicó en la regla 4: **decir sobre qué corrida se midió y con qué comando se
rehace, dentro del mismo párrafo que la cita.** No es un control automático; es
lo que hace que la ausencia del control se note.

**La sexta no es un artefacto desfasado: es una cita que caduca sola.** Las dos
anteriores se rompen cuando alguien regenera algo mal, y en las dos hay un
momento en que una persona hizo algo. Esta se rompió sin que nadie tocara el
archivo que la contiene, sin que nadie se equivocara y sin que nada avisara. Un
hash de commit parece un identificador y no lo es: es un nombre que Git reasigna
cada vez que reescribe la historia, y `rebase`, `commit --amend` y `cherry-pick`
la reescriben como parte del trabajo normal. Citar un hash es apostar a que
nadie volverá a tocar esa rama.

**Regla que se deriva: no se citan hashes de commit en la documentación.** Para
señalar un cambio se lo nombra por lo que hizo —el asunto del commit, la fecha,
el archivo que tocó—, que sobrevive a cualquier reescritura. El historial sigue
siendo parte del entregable; lo que deja de ser citable es el hash como
dirección.

**La excepción, y es una sola:** el hash que identifica un **artefacto
inmutable** en vez de un punto de la historia. El `built_at_commit` que
`graph.json` grabó dentro de sí mismo (regla 4) es un dato de esa corrida, no
una referencia que podamos corregir: cambiarlo rompería la correspondencia con
la salida que imprime su propio comando de procedencia. En ese caso **se cita el
hash y se dice, en el mismo párrafo, por qué no se actualiza y cuál es su
equivalente vigente** — que es lo que hace la nota "Sobre ese hash" de la regla
4. La excepción no es "a veces vale citar hashes": es "cuando el hash es el
dato, se declara que lo es".

**La séptima es la más incómoda, porque no hay nada que la detecte.** No es
código inerte, ni un artefacto desfasado, ni una cita que caduca: es **una
afirmación sobre el contenido de un archivo del repositorio, escrita sin abrir
el archivo**. El archivo estaba ahí, versionado, a una orden de distancia, y
decía lo contrario. Lo que se escribió no fue una invención: fue una inferencia
razonable a partir de dos señales verdaderas —el parámetro se llama `max_fpr` y
la integral es `auc(fpr, tpr)`— que apuntaban a la conclusión equivocada porque
faltaba una tercera línea, la inversión de etiquetas, que nadie fue a leer.

Las otras seis clases tienen al menos un mecanismo que las puede atrapar:
conectar el código y comparar, regenerar el artefacto y volver a correr el
verificador, resolver el hash contra `git log`. **Esta no tiene ninguno.** Un
verificador de trazabilidad comprueba que una cifra exista en `outputs/`; no
existe —ni es evidente cómo sería— un verificador que compruebe que una frase
en prosa describe correctamente lo que hace un script. El único control
disponible es ir a mirar.

**Regla que se deriva: antes de afirmar qué hace un archivo del repositorio, se
abre.** Y si la afirmación es sobre **comportamiento** y no sobre texto, no se
razona: **se ejecuta contra las alternativas**. Así se detectó esta, y es el
único método que sirvió — se corrió el script oficial contra las dos hipótesis
con seis semillas, y las seis coincidieron al dígito con la restricción directa
sobre el TPR y ninguna con la restricción sobre el FPR. Leer el código con
atención habría bastado en este caso, pero leerlo con atención es lo que ya
creíamos haber hecho; ejecutarlo no admite esa confusión.

**La octava es una variante de la séptima, y más traicionera: afirma una
ausencia.** La séptima afirmaba qué hace un archivo sin abrirlo. La octava sí
fue a los archivos —con una búsqueda— y concluyó que algo **no** estaba en
ellos. Pero **una búsqueda puede probar presencia, nunca ausencia.** Si
encuentra la expresión, la frase existe; si no la encuentra, lo único probado es
que esa expresión, escrita exactamente así, no aparece. La idea puede estar
dicha con otras palabras, y lo estaba: se buscó *"no patient overlap"*, y la
fuente decía *"albeit different patients than the training dataset"*. Lo que la
búsqueda sí encontró —una frase sobre otra cosa— empeoró el error, porque dio
la sensación de haber mirado. Ocurrió dos veces en la misma tanda, una por cada
lado de la conversación.

**La segunda instancia añade una variante concreta: un fragmento de resultado de
búsqueda no es la fuente, es la anotación de quien la indexó.** Es el mismo
motivo por el que la regla 3 no acepta la ficha para verificar una cita: la
ficha es un extracto hecho por quien guarda el archivo, y el fragmento es un
extracto hecho por quien indexa la página. Ninguno de los dos es la fuente, y
los dos pueden estar desfasados, recortados o fuera de contexto sin que nada lo
avise. En este caso el fragmento decía lo mismo que ya decía una fuente
versionada, pero eso solo se supo al final. **Regla operativa: antes de instruir
que se versione una página, se comprueba que responde.** Una petición que sigue
las redirecciones y mira el código final cuesta segundos; no hacerla costó una
tanda.

**Regla que se deriva: antes de escribir que algo no está respaldado, se lee
completa la fuente candidata.** Si eso no es viable —demasiadas fuentes, o una
demasiado larga—, la frase no dice que no existe: dice **qué se buscó y
dónde**. No *"ninguna fuente lo afirma"*, sino *"se buscaron estas expresiones
en estos archivos, sin resultado"*, de modo que el lector sepa exactamente qué
quedó descartado y qué no se miró.

**La novena no añade una clase, pero sí un intermediario que no se veía.** La
ficha de PanDerm dice desde el 2026-08-20 que se consultó con WebFetch, y nadie
lo leyó como una advertencia. WebFetch no trae el texto: convierte la página y
devuelve la respuesta de un modelo pequeño a una pregunta sobre ella. Es el
mismo problema que el fragmento de buscador de la octava, con una diferencia que
lo empeora: el resultado **parece** una cita, entre comillas y en inglés, y dos
de cinco no lo eran. **Regla operativa: ninguna cita se toma de WebFetch.** Se
toma de una copia del texto —el XML, el HTML o el PDF obtenidos con `curl`, o
`get_page_text` del navegador— guardada en `referencias/_texto-completo/` o
versionada, y se comprueba contra esa copia. La otra ficha tomada con WebFetch,
`referencias/slice3d-metadata-tbp-lv.md`, queda por comprobar así. Su cita de
`tbp_lv_nevi_confidence`, la que usa la Cuarta nota, sí está literal en el texto
completo de Kurtansky 2024: comprobado el 2026-09-24.

**La décima es una clase nueva: el instrumento elige con las etiquetas con que
se evalúa.** No es código inerte ni un artefacto desfasado, y el archivo sí se
abrió: la función hace lo que su docstring dice. El defecto es de método. Una
elección que depende de las etiquetas —aquí, la orientación de la variable— se
hace en el pliegue de validación, el mismo cuyo resultado se reporta, así que
ese resultado sale sesgado a favor, en la misma dirección que la fuga que
`auditoria-de-fugas` busca en los datos. Nadie lo vio porque `SKILL.md` describía
el nivel como una columna *"cruda"*. Apareció al escribir el método con el
detalle suficiente para que otro lo reprodujera, y ese es su único detector
conocido: describir lo que hace el código, paso por paso, contra el código.

**Regla que se deriva: toda elección que dependa de las etiquetas —orientación,
columna, umbral, época, hiperparámetro— se hace dentro del pliegue de
entrenamiento.** Donde no se pueda, se declara como sesgo del resultado. *No se
aplica a `auditoria-de-fugas`:* allí `max(auc, 1 − auc)` mide la fuerza de la
asociación sin importar su signo, que es lo que un chequeo de fugas necesita, y
no se reporta como desempeño de un modelo.

**Volviendo a la cuarta y la quinta: ninguno de los controles del proyecto
detecta un artefacto desfasado, y conviene ser preciso sobre por qué.** El
verificador de trazabilidad comprueba que las cifras del informe
tengan respaldo en `outputs/`; da por supuesto que `outputs/` es lo que dice
ser. La regla 2 encadena informe → `outputs/`, y ahí se detiene: **nada encadena
`outputs/` → código.** El eslabón que falta no es una comprobación más estricta
de la que ya existe, es un eslabón distinto, y hoy no hay ninguno. Queda escrito
como hueco abierto; el control que lo cerraría no se propone todavía.

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
├── referencias/           ← fuentes: texto completo si la licencia es abierta, ficha si no
│   └── _texto-completo/   ← textos con copyright, solo en local (en .gitignore)
├── outputs/               ← salidas de cada skill (.json + .md)
└── informe/
```

`referencias/` existe porque Kaggle no es legible por el agente (JavaScript +
sesión), y porque ninguna fuente debe citarse de memoria. Cada fuente se toma de
su origen, con fuente, fecha y licencia en la cabecera. Qué parte de ella se
versiona lo decide su licencia, según la regla 3: el texto completo si es
abierta, una ficha con las citas literales si no. En los dos casos la cita sigue
siendo trazable a un archivo del repositorio y no a la memoria del agente.

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
su cuenta. Se resolvió con copias tomadas manualmente con sesión iniciada.
Desde el 2026-09-21 lo versionado en `referencias/` es una **ficha** con las
citas literales —las páginas de Kaggle no declaran licencia para su texto, así
que la regla 3 no permite versionarlo entero— y el texto completo queda en
local. Las fichas son la referencia citable para todo lo que dice Kaggle; las
citas se comprueban contra el texto completo. El resto se verificó contra fuentes primarias del
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
      examples."* (`referencias/kaggle-evaluation.md`, ficha de
      https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation;
      copia tomada con sesión iniciada el 2026-08-11, texto completo en local)
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

Las cinco skills están escritas, corridas y auditadas. El alcance
original —metadata tabular, sin imágenes— está cerrado. Lo que sigue es la
extensión documentada en la última sección de este archivo.

| Skill | Estado | Salida en `outputs/` |
|---|---|---|
| `eda-diagnostico` | completa, auditada (`3cc3a03`) | `.json` + `.md` |
| `diseno-validacion` | completa, auditada (`3df25fc`, `a53b199`) | `.json` + `.md` |
| `auditoria-de-fugas` | completa, auditada (`958cee0`) | `.json` + `.md` |
| `modelado-baseline` | completa, auditada (`50ba80d`, `30fbff5`, `ad22ba0`) | `.json` + `.md` |
| `sintesis-consultoria` | completa (`c3467a7`, `6d5754a`, `3e144e0`, `8a1f3ab`) | `sintesis-verificacion.json` + `.md` |

*Deuda declarada:* los once hashes de esta tabla **violan la regla derivada en
el registro de incidentes** —no se citan hashes en la documentación—. Siguen
resolviendo hoy porque el rebase del 2026-09-19 solo reescribió los commits que
estaban sin subir, y estos son anteriores; es decir, sobrevivieron por suerte,
no por diseño. Se dejan a la vista en vez de arreglarlos en silencio: está en
Pendientes reemplazarlos por asunto y fecha.

Ninguna se dio por buena sin correrla contra `data/train-metadata.csv` y
encontrarle defectos. Las cuatro instrumento tenían al menos uno. El detalle de
cada corrección está en el historial de commits, que es parte del entregable.

`sintesis-consultoria` produjo `informe/borrador.md`, `informe/informe-final.docx`,
`informe/informe-final.pdf` y `informe/demo.html`. Su salida en `outputs/` no son
mediciones sino el resultado del verificador de trazabilidad (regla 2): cuántas
cifras del borrador tienen respaldo en un archivo y cuáles no.

### Hallazgos vivos para el informe

Los tres primeros ya están arriba (agrupación por paciente, 11 columnas solo en
train, `tbp_lv_nevi_confidence`). Se suman tres del modelado, trazables a
`outputs/modelado-baseline.json`, `outputs/validacion-repetida.json` y
`outputs/sensibilidad-procedencia-repetida.json`. Desde el 2026-09-25 sus
cifras son las del conjunto de desarrollo; las de la corrida sobre el 100 % de
los datos están en la tabla de antes y después de `PLAN.md`, Fase 1.

1. **El gradient boosting sin balancear falla de un modo peor que el esperado.**
   Nivel 2a da pAUC 0,0005, *por debajo del piso aleatorio de la métrica* (0,02).
   No colapsa a "predecir siempre negativo" —el diagnóstico de manual— sino que
   satura en probabilidad 1.0 sobre negativos y los coloca encima de los
   positivos, arrasando justo la región de sensibilidad alta. Con
   `class_weight="balanced"` (2b): 0,1398. La métrica del cliente ve el
   problema; la métrica por defecto no. Cifras del conjunto de desarrollo
   (`outputs/modelado-baseline.json`); las conclusiones son las mismas que sobre
   el 100 % de los datos, donde eran 0,0013 y 0,1451.

   > **AUC estándar del Nivel 2a: 0,582**, en
   > `modelado-baseline.json > nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media`.
   > El 2026-08-18 se retiró de aquí una cifra sin respaldo (0.6685); después se
   > extendió el instrumento para medir el AUC estándar de cada nivel, y quedó
   > claro que 0.6685 era el AUC del **primer fold** en la corrida sobre el 100 %
   > de los datos (`...auc_estandar_por_fold`), no el del modelo, cuya media era
   > 0.6159: el número era real y estaba mal atribuido.
   >
   > Consecuencia sobre la última frase del párrafo de arriba: **la métrica por
   > defecto no es ciega al problema.** Lo puntúa por encima del azar de su
   > escala mientras el pAUC lo deja por debajo del azar de la suya (0,02): las
   > dos métricas siguen discrepando sobre si 2a supera al azar. No es un fallo
   > silencioso: es un desacuerdo entre dos métricas sobre las mismas
   > predicciones (ver `informe/casos-de-fallo.md`).

2. **La ventaja de 2b sobre 1 no está establecida, ni en magnitud ni en
   dirección.** Sobre el conjunto de desarrollo, con 10 semillas × 5 pliegues
   (`outputs/validacion-repetida.json`), la media de 2b − 1 es 0,005; 2b gana
   en 29 de 50 pliegues y 8 de 10 semillas, y el intervalo corregido es
   [−0,0145; 0,0245]. Sobre el 100 % de los datos la media era 0,0125, con 40
   de 50 y 10 de 10: la estimación se movió al quitar el 20 % de los pacientes.
   Se retira la conclusión anterior, «dirección sí; magnitud no».

   *Retirada antes, y de la misma forma: la ventaja de estabilidad de 2b.* Sobre
   una partición (semilla 42) 2b era el menos disperso, ±0,0055 entre folds
   frente a ±0,0173 del Nivel 1; sobre las diez de la validación repetida el
   orden se invertía, 0,0142 frente a 0,012. Lo que parecía una propiedad del
   modelo era una propiedad de la semilla. No usar la estabilidad como
   argumento a favor de 2b. *Son cifras de la corrida sobre el 100 % de los
   datos; este párrafo no se ha rehecho con el conjunto de desarrollo.*

3. **Las columnas de procedencia no explican la ventaja de 2b**
   (`outputs/sensibilidad-procedencia-repetida.json`). 2b − 1 es 0,0046 con
   ellas y 0,005 sin ellas. Incluirlas mueve 2b en 0,0021 (corregido
   [−0,0082; 0,0124]) y el nivel 1 en 0,0025 (34 de 50 pliegues, 10 de 10
   semillas, corregido [−0,0023; 0,0073]). La exclusión se sostiene por razón
   de uso, no por desempeño. Una sola partición (semilla 42:
   `outputs/sensibilidad-procedencia.json` frente a
   `outputs/modelado-baseline.json`) sugería lo contrario, 2b de 0,1398 a
   0,1467, y la hipótesis se formuló en la conversación desde esa corrida. Es
   la segunda vez que un resultado de una sola partición no sobrevive a la
   validación repetida; la primera fue la estabilidad de 2b. **Regla: ninguna
   conclusión comparativa se escribe desde una sola partición.**

### Dónde se lee la fase vigente

En `PLAN.md`, no aquí. La ruta —qué fase está en curso, cuál es el siguiente
paso y qué archivo es su puerta— vive en ese archivo y solo en ese archivo.
Este es estado que caduca, y mantenerlo en dos sitios es cómo se desfasan.

### Pendientes

- [ ] Instalar Claude Code y verificar qué incluye el plan actual
- [x] Verificar la sección "Sobre el problema" contra la fuente oficial
      (2026-08-11 — fuentes del organizador ISIC/MSKCC + copias literales de
      Kaggle en `referencias/`, reducidas a ficha el 2026-09-21 por la regla 3)
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
- [ ] Reemplazar por asunto y fecha los once hashes de commit que aún cita la
      tabla de "Estado actual", por la regla derivada en el registro de
      incidentes: un hash sobrevive solo hasta el siguiente rebase
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

**Mecanismo.** `modelado-baseline/scripts/train_and_evaluate.py`, al
principio de `main()`, comprueba la existencia del reporte **antes** de leer
el CSV y aborta con código 1:

```
ERROR: no existe outputs/auditoria-de-fugas.json. Esta skill no decide qué
columnas excluir por su cuenta — corre auditoria-de-fugas primero.
```

No hay lista de respaldo escrita a mano ni valor por defecto: las
columnas se arman concatenando cuatro campos del reporte, así que sin
reporte no hay nada que usar. El cuarto, las columnas de procedencia, no
es un hallazgo sino una decisión de la persona (2026-09-25), escrita en
`audit_leakage.py`; `modelado-baseline` la lee igual que las demás. Reproducido y documentado en
`informe/casos-de-fallo.md`, caso B.

### 2. Ninguna cifra del informe existe sin estar en `outputs/`

Es la regla 2 con un verificador detrás, no un propósito.

**Mecanismo.** `sintesis-consultoria/scripts/verificar_trazabilidad.py`
extrae todo número del borrador y lo busca en los `outputs/*.json` con
tolerancia de redondeo 0,01, salvo en los que declara fuera del corpus
(`FUERA_DEL_CORPUS`, desde el 2026-09-25: el conjunto reservado, los análisis
de sensibilidad y la salida del propio verificador). Última corrida
(`outputs/sintesis-verificacion.json`, regenerado por el commit "Regenerar la verificacion de trazabilidad desde el estado actual"): **344 números en el
borrador, 298 con respaldo, 16 señalados** —recuentos de la corrida anterior a
la re-medición de la Fase 1 (2026-09-25), sobre el borrador y el `outputs/` de
entonces, pendientes de regenerar— para revisar uno por uno; el
resto cae en contextos que no son cifras medidas (años, etiquetas de
nivel, numeración de secciones) y se descarta explícitamente. De esos 16,
catorce son siete cifras contadas dos veces: la sección §10.4 del
borrador tiene que reescribir cada cifra para justificarla, y el
verificador no distingue una afirmación de su propia auditoría.

Estas tres cifras estuvieron desactualizadas —decían 331/291/13— y son
un caso de la cuarta clase del registro de incidentes (regla 6): una
cifra derivada de `outputs/` que se quedó atrás sin que nada lo
advirtiera.

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
`train_and_evaluate.py`, no un argumento de línea de comandos: no se
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

**Estado: PLAN ACORDADO, NADA EJECUTADO.** *Salvo E1 para PanDerm: el
2026-09-24 se leyó su artículo y se decidió no usarlo (ver «Riesgo
bloqueante»).* Sesión de planificación del
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
>
> *2026-09-24: se versionó el código público de la solución
> (`referencias/novoselskiy-2024-isic2024.md`), no el writeup. El párrafo de
> abajo no se ha reescrito contra el código.*

**Pregunta abierta (2026-09-24): ¿vio el tercer modelo de imagen los recortes de
SLICE-3D?** Además de EVA02 y EdgeNeXt sobre los recortes de la competición, el
código entrena un tercer modelo —otro EVA02-small, de tres clases— con una
descarga del ISIC Archive (`data_pull.ipynb`: `!isic image download images/`), y
sus predicciones entran al CatBoost. La descarga no fija colección ni lista de
imágenes. Las celdas que preparan esos datos no los cruzan con
`train-metadata.csv` ni con los pacientes de la competición: solo deduplican
por hash de píxeles dentro del propio conjunto externo. **El código no permite
saber si esa descarga contiene los recortes de SLICE-3D.** Kurtansky 2025 dice
que ese modelo *"is trained on external dermoscopy data"*
(`referencias/kurtansky-2025-triaje-automatizado-tbp.md`, «Ablation study»),
pero el código no filtra por tipo de imagen, así que esa frase no lo resuelve.
No se afirma en ninguna dirección. Mientras siga abierta, ese modelo queda fuera
de la reproducción (`PLAN.md`, Fase 4), por el mismo criterio de la Fase 2.

*Ampliado el mismo día: SLICE-3D está en el ISIC Archive.* Lo dicen dos fuentes
del proyecto. El descriptor: *"Both versions are stored on the ISIC Archive."*
(`referencias/kurtansky-2024-slice3d-descriptor.md`, *"Data accessibility"*). Y
la página de datos del reto: *"The training data reflected currently in the ISIC
Archive proper are available at https://api.isic-archive.com/collections/390/."*
(`referencias/isic-licencia-y-cita-slice3d.md`, *"Version control"*). Una
descarga completa del archivo, sin filtro, **podía** por tanto incluir los
recortes de SLICE-3D. Sigue sin estar probado que los incluyera: depende de qué
descargue la herramienta y en qué fecha, y el código no lo registra.

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
preentrenamiento.** *Aquí se decía que MSKCC, anfitrión de ISIC 2024, "aparece
mencionado como fuente institucional"; en el texto del artículo de PanDerm solo
aparece como conjunto de evaluación (ver el hallazgo de abajo).* Si hay solape,
cualquier resultado de un modelo congelado sobre estos datos está inflado por
fuga — no por un error del proyecto, sino por el preentrenamiento del modelo
descargado.

**Hallazgo del 2026-09-24: el artículo de PanDerm declara SLICE-3D en su
preentrenamiento.** La decisión que se tomó con él está abajo, en «Decisión». En
`referencias/panderm-reduccion-examenes.md` (texto completo), métodos,
*"Pretraining dataset for developing PanDerm"*, subsección *"ISIC2024"*:

> "ISIC2024 (ref. 47) is an open-source TBP-based dataset for identifying skin
> cancers among lesions cropped from 3D total-body photographs. We selected a
> subset containing 352,034 tile images, stratified by institutions."

La referencia 47 del artículo es *"Kurtansky, N. R. et al. The SLICE-3D
dataset: 400,000 skin lesion image crops extracted from 3D TBP for skin cancer
detection."* La misma sección incluye las cohortes MYM y HOP, cuyos números de
aprobación ética coinciden con los de los dos estudios con que la Universidad de
Queensland contribuyó a SLICE-3D.

Lo que el texto **no** resuelve. Son límites del hallazgo, no condiciones de la
decisión: la decisión aplica un criterio fijado antes de conocer el dato, y
ninguna de estas preguntas la cambia.

- **Qué imágenes exactamente.** *Aritmética nuestra:* 405.856 (MYM) + 352.034 =
  757.890, el total de recortes TBP del preentrenamiento; y 352.034 + 49.025 =
  401.059, las filas de `train-metadata.csv`
  (`eda-diagnostico.json > fuente.n_filas`). Las 49.025 son el conjunto de
  ISIC2024 que el artículo reserva para evaluar, *"with three institutions
  (FNQH Cairns, Alfred Hospital, Melanoma Institute Australia)"*. Pero según el
  descriptor de SLICE-3D, Alfred y FNQH Cairns aportaron solo al conjunto de
  prueba del reto, así que esas 49.025 no pueden ser solo filas de SLICE-3D. El
  texto no permite saber qué versión de ISIC2024 se usó.
- **Si cuenta como fuga.** El preentrenamiento fue sobre imágenes sin etiqueta,
  *"2,149,706 unlabeled multimodal skin images"*: el modelo vio las imágenes, no
  los diagnósticos. Si eso infla un resultado sobre estos mismos datos, y
  cuánto, no se sabe. La decisión no lo admite como excepción, porque el
  criterio no la preveía.
- **MSKCC.** En el texto del artículo aparece solo como conjunto de evaluación
  dermatoscópico, *"8,984 dermoscopic images"*. El reparto del preentrenamiento
  por institución está en la figura 1c, que es una imagen y no se leyó.
  Entraría por ISIC2024, que en SLICE-3D incluye filas de MSKCC; el texto no
  dice qué instituciones tiene el subconjunto de 352.034.
- **DermFM-Zero** no se examinó. Por la decisión, tampoco se usa.

*Criterio, fijado el 2026-08-18, antes del hallazgo:* Si se confirma, no se usa
PanDerm, y el hallazgo se documenta como parte del informe: **en la era de los
modelos fundacionales la fuga se desplaza del propio dataset al preentrenamiento
de terceros.** Es la continuación natural de lo que `auditoria-de-fugas` ya
encontró dentro del CSV, un nivel más arriba.

**Decisión (2026-09-24, de la persona):** PanDerm no se usa. Su artículo declara
ISIC2024 (ref. 47, el descriptor de SLICE-3D) entre las fuentes de
preentrenamiento, con 352.034 recortes. El criterio de esta fase se fijó antes
de conocer ese dato: si hay solape, no se usa. Que el preentrenamiento fuera sin
etiquetas no se admite como excepción, porque el criterio no la preveía. Se usa
DINOv3, sujeto a la misma verificación del objetivo 5. DermFM-Zero no se examinó
y no se usa.

El estado de la fase vive en `PLAN.md`, Fase 2: la puerta queda cumplida para
PanDerm, y la fase sigue abierta hasta versionar la fuente de los datos de
preentrenamiento de DINOv3 y escribir la decisión sobre ella.

**DINOv3** (genérico, no dermatológico) pasa de respaldo a modelo elegido. *Aquí
se decía que era un respaldo "sin este riesgo conocido". Que no se le conozca el
riesgo no es una verificación: sus datos de preentrenamiento están por
comprobar, igual que se comprobaron los de PanDerm.*

*Precedente en este mismo archivo:* la Cuarta nota dejó abierta exactamente esta
pregunta para `tbp_lv_nevi_confidence` —si las lesiones con que se entrenó ese
clasificador se solapan con SLICE-3D— y se resolvió por criterio de
disponibilidad en inferencia. Aquí el criterio no basta, porque el modelo
congelado sí estará disponible en inferencia y aun así el número estaría inflado.

### Sub-etapas de la extensión (E1–E4), en orden de dependencia

Estas son las **sub-etapas del trabajo con imágenes**, no la ruta del proyecto:
en `PLAN.md` caen dentro de las **fases 2 a 4**. Se numeran E1–E4 a propósito,
para que "Fase 2" signifique siempre una sola cosa — la de `PLAN.md`.

| Sub-etapa | Dónde cae en la ruta (`PLAN.md`) |
|---|---|
| **E1** — contaminación del modelo fundacional | Fase 2 |
| **E2** — features de paciente relativo (sin imágenes) | preparación tabular, dentro de la fase 4 |
| **E3** — características congeladas | Fase 3 |
| **E4** — apilado y evaluación completa | Fase 4 |

- **E1 — bloqueante.** Resolver la contaminación PanDerm/DermFM-Zero con
  SLICE-3D. Posiblemente escribiendo a los autores (correo público en el repo).
  Nada más empieza hasta cerrarla. *2026-09-24: PanDerm no se usa, porque su
  artículo declara ISIC2024 en el preentrenamiento; DermFM-Zero no se examinó y
  no se usa (decisión en «Riesgo bloqueante»). E1 sigue abierta por DINOv3.*
- **E2 — features de paciente relativo.** Sobre la metadata tabular que ya
  está en `data/`: contraste de cada lesión contra el resto de su paciente (LOF
  agrupado por `patient_id`, razones contra el promedio del paciente). Sin
  imágenes. Días de trabajo, minutos de cómputo.
  *Hipótesis, no resultado:* debería mejorar sobre el nivel 2b medido en el
  conjunto de desarrollo. El criterio es la comparación pareada de E2 contra 2b
  en la validación repetida, con el intervalo corregido por Nadeau y Bengio, y
  no un valor puntual: la mejora no se da por establecida si ese intervalo
  contiene el cero. *Hasta el 2026-09-25 el punto de partida era un valor
  puntual: el pAUC de 0,1451 del nivel 2b sobre el 100 % de los datos, en una
  sola partición.* Se escribe aquí como predicción declarada de antemano; si no
  mejora, eso también va al informe.
- **E3 — características congeladas.** Una pasada hacia adelante por imagen,
  sin fine-tuning. Factible en el M4 corriendo de noche. Requiere descargar
  `train-image.hdf5` (ya está en Pendientes).
- **E4 — apilado y evaluación completa.** Características de imagen +
  metadata + features de paciente relativo en el mismo pipeline tabular ya
  auditado. Tabla final con los **tres** ejes de la función de utilidad: pAUC,
  retrieval top-15 por paciente, y costo de inferencia.

E4 es la que cierra el argumento del informe: es donde el consultor deja de
reportar una sola cifra y responde la pregunta que el cliente escribió entera.

**Qué pasó con la antigua "Fase 2 — protocolo (Vía A + Vía B)".** Ya no es una
sub-etapa de la extensión: montar el protocolo es la **fase 1 de `PLAN.md`**
—sellar el holdout y re-medir—, y es la ruta quien la ordena y le pone puerta.
El contenido de las dos vías no se movió: sigue arriba, en "Protocolo de
medición sin leaderboard".

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

- [ ] **E1:** verificar contaminación del modelo fundacional con SLICE-3D.
      PanDerm: cerrado el 2026-09-24, no se usa (su artículo declara ISIC2024
      en el preentrenamiento). DermFM-Zero: no se examinó y no se usa.
      Pendiente: versionar la fuente de los datos de preentrenamiento de
      DINOv3 y escribir la decisión sobre ella.
- [x] Guardar el writeup del 1er lugar en `referencias/` (con fuente y fecha en
      la cabecera) antes de citarlo en el informe — regla 3. *Cumplido el
      2026-09-24 con el **código** público de la solución, no con el writeup:
      `referencias/novoselskiy-2024-isic2024.md`. El writeup de Kaggle sigue
      sin estar en `referencias/`, así que lo que el autor reporta sobre por
      qué funciona su solución sigue sin ser citable.*
- [x] Decidir tamaño exacto del lockbox y semilla de partición, y verificar que
      la partición deja positivos en ambos lados (mismo chequeo obligatorio que
      `diseno-validacion` ya hace para los folds). *Cumplido el 2026-09-25: 20 %
      de los pacientes, estratificado por centro y por presencia de lesiones
      malignas, semilla 2026, sin ningún estrato vacío a un lado. Decisión en
      `PLAN.md`, Fase 1; lista en `outputs/holdout-pacientes.json`.*
- [ ] Decidir cuántas semillas usar en la Vía A, según tiempo de cómputo real
- [x] Definir cómo se mide el eje "costo de inferencia" — sin esa definición la
      tabla de E4 tiene solo dos columnas de tres. *Cumplido el 2026-09-24: se
      mide como tiempo de inferencia. La definición está en el anteproyecto,
      sección 5.1, y en `PLAN.md`, Fase 6.*

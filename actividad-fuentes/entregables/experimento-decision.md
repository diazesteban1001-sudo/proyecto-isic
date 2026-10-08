## Experimento y decisión

### Diseño

Una consulta, porque el equipo es de un integrante, corrida en tres
tratamientos (`protocolo-experimento-v1.md`): *«¿Qué estudios han medido cuánto
se sobreestima el desempeño de los clasificadores de lesiones de piel cuando
los datos se parten por imagen o por lesión en vez de por paciente? Dame 5
referencias, cada una con la afirmación concreta que sostiene y su DOI.»*

**A, el control,** es un chat sin fuentes: `llama3.1:8b` en Ollama, en local,
sin conexión y sin instrucción de sistema. **B** es Consensus, en su modo por
defecto. **C** es NotebookLM, con los 22 archivos de `corpus-c.md`.

De cada respuesta se tomaron las primeras 5 referencias. Cada una se abrió y se
clasificó como no existe, existe pero no dice eso, o utilizable. Se clasificó
dos veces, sobre hojas mezcladas y sin la columna de tratamiento, y las
discrepancias se leyeron una tercera vez. El análisis lo hizo `analizar.py`.

### Conteos y proporciones

Clasificación final (`resultados.json`). La proporción es la de referencias
utilizables, con intervalo de Wilson al 95 %:

| Tratamiento | Entregadas | No existe | No dice eso | Utilizable | Proporción [IC 95 %] | Se abstuvo |
|---|---|---|---|---|---|---|
| A · chat sin fuentes | 5 | 5 | 0 | 0 | 0,00 [0,0000; 0,4345] | sí |
| B · Consensus | 5 | 0 | 2 | 3 | 0,60 [0,2307; 0,8824] | no |
| C · NotebookLM | 5 | 0 | 3 | 2 | 0,40 [0,1176; 0,7693] | no |

Con 5 referencias por tratamiento los intervalos son anchos, y los de B y C se
solapan. Las referencias de un tratamiento salen de una sola respuesta y no son
independientes, así que no se hace ninguna prueba entre tratamientos. Lo claro
es que las 5 referencias del control no existen.

### Consistencia de la clasificación

Las dos pasadas no coinciden en **1 de 15 referencias**. El kappa de Cohen es
0,90, un dato secundario y sin inferencia, porque con 15 referencias es
inestable.

La discrepancia es la de **Jamaludin y Kim (2026)**, de B: «existe pero no dice
eso» en la pasada 1 y «utilizable» en la 2. Las cifras que se le atribuyen,
94,57 % y 78,41 %, están en el resumen. El texto completo, en cambio, atribuye
unos 11 puntos a la fuga y de 5 a 7 a la varianza de una sola semilla. La
tercera lectura la dejó en «existe pero no dice eso» (`tercera-lectura.csv`).

### Desviaciones declaradas

Están en `desviaciones.md`. (1) La primera corrida de A, en claude.ai, se
descartó porque tenía la búsqueda web activa. (2) A pasó a un modelo local: el
control es más estricto, pero el modelo es más pequeño y de otra familia que
Claude. (3) Las reglas de extracción se fijaron antes de clasificar. (4) La
hoja de la pasada 1 se regeneró, porque el formato delataba el tratamiento.
(5) Las pasadas las hizo Claude. (6) La pasada 2
no esperó 48 horas. (7) La tercera lectura no fue ciega. (8) Revisé las dos
pasadas, el 3 y el 5 de octubre, sobre las hojas ya clasificadas, sin cambiar
ninguna hoja. (9) En la auditoría manual de 5 referencias, discrepé de las dos
pasadas en Kapoor y Narayanan (2023), que puse en «no dice eso»; el hallazgo
no se aplicó.

### Decisión

Con los seis criterios del enunciado. La tabla completa, con qué se midió y
qué se juzgó sin medir, está en `tabla-decision.md`. El banco de 20 preguntas
de respuesta conocida (`banco-resultados.md`) completa el experimento.

| Herramienta | Dato que decide | Decisión |
|---|---|---|
| NotebookLM | Banco: 20 de 20 [0,8389; 1,0000]; se abstuvo en las 3 preguntas fuera del corpus | **Elegida para anclaje**, con el protocolo v2 y abriendo el pasaje citado |
| Consensus | 3 de 5 utilizables; un DOI erróneo | **Solo para buscar referencias nuevas**, abriéndolas siempre |
| Chat sin fuentes | 0 de 5, las 5 inexistentes; 0 de 17 en el banco | **Descartada** |
| Proyecto de Claude con archivos | Sin medir: la cuenta no deja apagar la búsqueda web | **Descartada** |
| Vía propia (Ollama, embeddings y Chroma) | Sin medir: corpus público, construcción costosa | **Descartada** |
| Claude Code sobre `referencias/` | Comprobaciones con guion | **Para verificar, no para consultar** |

La biblioteca y la exportación a APA 7 son de Zotero para todas.

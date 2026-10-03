---
name: sintesis-consultoria
description: Lee todo outputs/*.json, cruza los hallazgos de las cinco skills instrumento, y produce los entregables de consultoría — el informe final en Word y la demo interactiva en HTML para la presentación en vivo. A diferencia de las demás skills del proyecto, esta SÍ interpreta — es su función. Pero cada cifra que aparezca en cualquiera de los dos entregables debe rastrearse hasta un campo específico de un archivo de outputs/, nunca inventarse ni recordarse de memoria. Úsala solo al final, cuando las cinco skills instrumento ya corrieron sobre los datos reales.
---

# Síntesis de Consultoría

Esta es la única skill del proyecto que interpreta en vez de solo medir.
Es, literalmente, el trabajo del consultor: leer los instrumentos, resolver
las contradicciones entre ellos, y emitir una recomendación defendible.

Todas las demás skills existen para que esta pueda hacer su trabajo con
material confiable. Si alguna de las cinco no ha corrido sobre los datos
reales, o corrió pero no fue auditada, esta skill no debe usarse todavía
— el informe heredaría esa falta de rigor sin decirlo.

**Estado (2026-10-02):** las cinco corrieron sobre los datos reales y están
auditadas: las cuatro originales —`eda-diagnostico`, `diseno-validacion`,
`auditoria-de-fugas` y `modelado-baseline`— y `extraccion-imagen`, auditada
ese mismo día sin defectos (`extraccion-imagen/scripts/test_extraccion.py`).

## Antes de empezar

Verifica que existan y tengan contenido real (no vacíos, no de un CSV
sintético de prueba):

- `outputs/eda-diagnostico.json`
- `outputs/diseno-validacion.json`
- `outputs/auditoria-de-fugas.json`
- `outputs/modelado-baseline.json`
- `outputs/extraccion-imagen.json`

Si falta alguno, dilo explícitamente y detente. No redactes el informe
con huecos rellenados de memoria.

## Proceso, en etapas

*Se llaman **etapas** y no fases a propósito.* "Fase" ya nombra la ruta del
proyecto en `PLAN.md`, y "E1–E4" las sub-etapas de la extensión en
`CLAUDE.md`. Estas cuatro son internas de esta skill y no se corresponden con
ninguna de las dos: una palabra, un significado.

**Con qué intérprete se corre todo esto.** Con el del proyecto,
`.venv/bin/python` (CPython 3.11.9) — **no** con el `python3` del sistema, que
no tiene las dependencias. Los comandos de abajo lo escriben explícitamente en
vez de decir `python`, porque `python` a secas depende de si el entorno está
activado y el fallo no es obvio: el script aborta con `ModuleNotFoundError` a
mitad de la etapa.

| Script | Necesita | ¿Corre con el `python3` del sistema? |
|---|---|---|
| `verificar_trazabilidad.py` | solo biblioteca estándar | sí |
| `md_a_docx.py` | `python-docx` | **no** |
| `generar_demo.py` | `scipy` | **no** |

Si `.venv/` no existe, se recrea con
`python3 -m venv .venv && .venv/bin/pip install python-docx scipy`.

### Etapa 1 — Borrador en Markdown

Redacta primero `informe/borrador.md`, no el `.docx` directamente. Es
más fácil de revisar, corregir y iterar contigo antes de invertir tiempo
en formato. Estructura sugerida:

1. **Resumen ejecutivo** — la tesis del proyecto en un párrafo: el
   agente como consultor, no como competidor de Kaggle.
2. **Contexto y objetivo** — de dónde sale la pregunta, por qué ISIC 2024.
3. **Metodología** — las seis skills, cinco instrumentos y esta síntesis,
   con la separación medir/interpretar como argumento metodológico.
4. **Hallazgos de EDA** — desde `eda-diagnostico.json`.
5. **Diseño de validación** — desde `diseno-validacion.json`. La cifra
   de fuga bajo partición ingenua (99.04%) va aquí, como evidencia
   central, no como nota al pie.
6. **Auditoría de fugas** — desde `auditoria-de-fugas.json`. Las columnas
   excluidas, con su razón cada una. La resolución de
   `tbp_lv_nevi_confidence` como ejemplo de investigación hasta la
   fuente primaria.
7. **Resultados de modelado** — desde `modelado-baseline.json`. Los
   niveles en la escala correcta (pAUC, no AUC estándar), con la
   comparación de estabilidad entre folds como argumento, no solo la
   media.
8. **Limitaciones** — el ruido estructural en la clase negativa (no
   biopsiada), la ausencia de test real, el umbral de la métrica y su
   justificación clínica citada textualmente de Kaggle.
9. **Conclusiones y recomendación** — qué le dirías a un cliente real,
   no solo qué modelo tuvo mejor número.
10. **Anexo de trazabilidad** — tabla de tres columnas: afirmación,
    valor, archivo y campo de origen. Ver contrato abajo.

Cada cifra citada en el cuerpo del texto debe tener una nota o marca
que apunte a su fila en el anexo de trazabilidad. Nada de números
sueltos sin fuente.

### Etapa 2 — Verificación de trazabilidad (obligatoria antes de Word)

Corre el script de verificación sobre el borrador:

```bash
.venv/bin/python .claude/skills/sintesis-consultoria/scripts/verificar_trazabilidad.py \
  --borrador informe/borrador.md \
  --outputs-dir outputs/ \
  --out outputs/sintesis-verificacion
```

El script extrae todo número que aparezca en el borrador y lo compara
contra el conjunto de valores presentes en `outputs/*.json`. No decide
si un número está bien citado en contexto — solo señala cuáles no
tienen ningún respaldo numérico exacto (con tolerancia de redondeo) en
ningún archivo de `outputs/`. Cada número señalado se revisa a mano:
puede ser una cifra legítima que no viene de outputs/ (ej. "cinco
skills", "393 positivos" citado dos veces con redondeo distinto), pero
la revisión la hace una persona, no el script.

**La tolerancia de redondeo depende de cómo está escrita la cifra.** Con
decimales, admite media unidad de su último dígito: «0,1451» tiene que estar
entre 0,14505 y 0,14515, y «0,14», entre 0,135 y 0,145. Sin decimales, sea
recuento o porcentaje, tiene que coincidir exacta: «401.059» con 401059,
«99%» con 99. `--tolerancia` impone en su lugar un margen fijo para todas, y
la salida declara el modo en `modo_tolerancia`. *Hasta el 2026-10-02 el
margen por defecto era 0,01, el 5 % de la escala del pAUC: el README pasaba
con 0,1451 y 0,1331 cuando `outputs/` ya decía 0,1398 y 0,1326.* Control:
`scripts/test_tolerancia_decimales.py`.

**Límite que queda, medido.** El verificador busca cada cifra en todo el
corpus, no en el campo que el texto cita. Sobre el `outputs/` del 2026-10-02,
con 2.864 valores distintos en el corpus, pasarían por azar:

- de los enteros del 1 al 200, 95 de 200 (47,5 %);
- de los valores de cuatro decimales entre 0,0001 y 0,0499, 320 de 499
  (64,1 %);
- de los valores de cuatro decimales entre 0,0500 y 0,2000, 432 de 1.501
  (28,8 %).

*Antes de que `sensibilidad-procedencia-repetida.json` entrara al corpus, ese
mismo día, eran 2.767 valores y 93, 304 y 382 (46,5 %, 60,9 % y 25,4 %): más
corpus, más cifras que pasan por azar.*

Con el margen fijo de 0,01, los dos últimos eran el 100 %. Caso real, en el
`README.md` de ese día: «±0,0055 frente a ±0,0173», la ventaja de
estabilidad de 2b que `CLAUDE.md` retiró en su hallazgo 2, sigue pasando.
El README la atribuye a los niveles 2b y 1 de `modelado-baseline.json`, cuyo
`pauc_std` dice hoy 0,018 y 0,009, en ese orden. Lo que la respalda son
diferencias por pliegue de otra comparación:

- 0,0055: `fase4-m4b-vs-m2.json > comparaciones_nuevo_menos_base.pauc.diferencias_nuevo_menos_base[24]`,
  y también `….auc.diferencias_nuevo_menos_base[24]` y `….auc.media`, y
  `sensibilidad-procedencia-repetida.json > comparaciones.b_2b_con_menos_2b_sin.diferencias[17]`;
- 0,0173: `fase4-m4b-vs-m2.json > comparaciones_nuevo_menos_base.pauc.diferencias_nuevo_menos_base[12]`
  y `….auc.diferencias_nuevo_menos_base[28]`.

Cómo rehacer las tres fracciones, desde la raíz del repositorio:

```bash
.venv/bin/python -c "
import importlib.util as u
s=u.spec_from_file_location('v','.claude/skills/sintesis-consultoria/scripts/verificar_trazabilidad.py');v=u.module_from_spec(s);s.loader.exec_module(v)
P,Q=v.cargar_valores_permitidos('outputs/')
f=lambda ts:sum(v.tiene_respaldo(v.candidatos(t),False,P,Q) for t in ts)
print(len(P),f([str(n) for n in range(1,201)]),f([f'0,{k:04d}' for k in range(1,500)]),f([f'0,{k:04d}' for k in range(500,2001)]))
"
```

Salida sobre el `outputs/` del 2026-10-02, con el corpus vigente:
`2864 95 320 432`. Con otro `outputs/` o con otra lista `FUERA_DEL_CORPUS` da
otros números.

**El verificador señala; que una cifra pase no prueba que salga del campo
que se cita.**

**No todo `outputs/` es corpus.** La lista `FUERA_DEL_CORPUS`, en el
propio script, declara los archivos en los que no se busca respaldo, cada
uno con su motivo: `holdout-pacientes.json`, los recuentos del conjunto
reservado; `sensibilidad-procedencia.json`, el análisis de sensibilidad de una
sola partición, superado por `sensibilidad-procedencia-repetida.json`, que sí
es corpus; y `sintesis-verificacion.json`, la salida del propio verificador,
cuyos recuentos describen una verificación anterior. Un análisis de
sensibilidad nuevo entra al corpus salvo que se excluya por nombre y con su
motivo. *Hasta el 2026-10-02 el patrón `sensibilidad-*.json` los excluía
todos.* Si una cifra del borrador solo
coincide con uno de ellos, es casualidad, no trazabilidad. La salida los
lista en `archivos_fuera_del_corpus`. Control positivo:
`scripts/test_fuera_del_corpus.py`.

Si el script señala números sin respaldo, corrige el borrador o
justifica por qué esa cifra no necesita estar en `outputs/` (ej. es un
conteo estructural obvio, no un resultado medido) antes de continuar.

### Etapa 3 — Conversión a Word

Solo después de que la trazabilidad esté limpia:

1. Revisa si hay una skill `docx` disponible en este entorno de Claude
   Code (`/mnt/skills/public/docx/` o equivalente). Si existe, síguela
   — tiene gotchas específicas del entorno que conviene respetar.
2. Si no existe, corre el script del proyecto, que usa `python-docx` y
   produce los estilos de encabezado, la tabla de contenido y la tabla de
   trazabilidad como anexo con formato de tabla real, no texto plano:

   ```bash
   .venv/bin/python .claude/skills/sintesis-consultoria/scripts/md_a_docx.py \
     --entrada informe/borrador.md \
     --salida informe/informe-final.docx
   ```

3. Verifica el resultado abriendo el documento generado antes de darlo por
   terminado — no asumas que el formato salió bien sin mirarlo.

**Sobre el PDF: se exporta a mano y no se versiona.** No hay pipeline que lo
genere: esta máquina no tiene LibreOffice ni pandoc, y el script solo produce
`.docx`. Cuando haga falta un PDF —para entregar o para revisar el formato de
un vistazo— se exporta a mano desde el `.docx` y se trata como copia
desechable. Por eso `informe/*.pdf` está en `.gitignore`: un PDF versionado
sin pipeline que lo regenere es un artefacto que se desfasa del `.docx` sin
que nada avise, que es la cuarta clase de fallo del registro de incidentes de
`CLAUDE.md`. Ya pasó una vez: el `informe-final.pdf` que estuvo en disco desde
el 12 de agosto de 2026 siguió diciendo "% del recorrido" mucho después de que
el borrador pasara a "posición en la escala".

### Etapa 4 — Demo interactiva en HTML

El informe escrito no es la única forma de entregar la síntesis. La
defensa del trabajo se hace en vivo, y ahí un documento de 17 páginas
es el formato equivocado: nadie lee una tabla de trazabilidad
proyectada. `informe/demo.html` es **la misma síntesis en otro
soporte** — mismos datos, mismas cifras, mismo alcance— presentada
para ser mirada en una pantalla durante diez minutos.

Que sea un artefacto de esta skill y no una tarea aparte es
deliberado: si el HTML se construyera por fuera, tendría su propia
copia de los números y se desincronizaría del informe en la primera
corrección. Un solo origen (`outputs/*.json`), dos presentaciones.

Se genera con un script, nunca escribiendo el HTML a mano:

```bash
.venv/bin/python .claude/skills/sintesis-consultoria/scripts/generar_demo.py \
  --outputs-dir outputs/ \
  --salida informe/demo.html docs/index.html
```

`--salida` admite varias rutas y **siempre se le pasan las dos**:
`informe/demo.html` es la copia que abre por doble clic desde un USB sin
servidor, y `docs/index.html` es la que GitHub Pages publica. El script
renderiza el HTML una sola vez y escribe esa misma cadena en cada
destino, así que son idénticos byte a byte por construcción. Si alguna
vez difieren, es un defecto del script — nunca algo que se arregle
copiando un archivo sobre el otro.

`docs/.nojekyll` desactiva el procesado Jekyll de GitHub Pages, que
interpretaría `{{` y `{%` como plantillas Liquid y podría corromper el
JavaScript de los gráficos. Hoy la plantilla no contiene esas
secuencias; el archivo está para que tampoco importe si mañana las
contiene.

La generación **no requiere internet**: Chart.js se lee de
`assets/chart.umd.min.js`, versionado en el repositorio. Su procedencia,
hash y licencia (MIT) están en `assets/PROCEDENCIA.md`. Vive dentro de
la skill, no en la raíz del proyecto, porque al empaquetarla como
`.skill` instalable tiene que viajar con ella.

**Cómo se verifica que sigue siendo autocontenida** (no basta con
mirarla, que es justo como se coló el defecto la primera vez):

```bash
# 1. No debe quedar ningún recurso externo
grep -o -E '(src|href)="https?://[^"]*"' informe/demo.html   # sin salida

# 2. Debe renderizar con toda la red cortada
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --proxy-server="127.0.0.1:1" \
  --virtual-time-budget=6000 --dump-dom \
  "file://$PWD/informe/demo.html" | grep -c "0,1451"          # debe dar 1
```

Reglas, idénticas a las del informe escrito:

- **Ningún número tecleado en el HTML.** El script lee `outputs/*.json`
  y embebe los valores al generar el archivo. Un número escrito a mano
  en la plantilla es una cifra inventada, exactamente igual que en el
  `.docx`.
- **Aviso de cifras exploratorias.** Si alguno de los JSON de los
  instrumentos no declara en su campo `datos` el conjunto de desarrollo,
  la página abre con un aviso: sus cifras son las de la corrida
  exploratoria sobre el 100 % de los datos. Lo decide el script con los
  datos de entrada, no una bandera, y va en el HTML servido.
- **Mismo alcance de interpretación.** La demo puede ordenar, resaltar
  y comparar lo medido; no puede afirmar nada que el informe no
  sostenga. Donde muestre una lectura y no una medición —el porqué de
  una columna excluida, por ejemplo— debe marcarlo como tal en la
  propia página.
- **Autocontenida, sin excepciones.** Los datos van embebidos como JSON
  en el archivo, no se leen con `fetch` en tiempo real, y **la librería
  de gráficos va empotrada** desde `assets/chart.umd.min.js` — no por
  CDN. El archivo resultante no hace ni una sola petición de red: abre
  con doble clic desde una USB, sin servidor y sin conexión.
  *Esto no siempre fue así.* Chart.js se cargaba desde jsdelivr, y sin
  red la página no mostraba un hueco donde iría el gráfico: lanzaba
  `Chart is not defined`, lo que **aborta el script** y deja sin
  rellenar todo lo posterior —los pAUC y las fichas por skill—
  mientras la cabecera seguía viéndose normal. Si se vuelve a añadir
  cualquier recurso externo, el fallo regresa en esa forma silenciosa.
- **Se verifica mirándola**, igual que el `.docx`: abrir en el
  navegador, accionar los controles interactivos y confirmar que
  renderiza, no solo que el archivo se escribió.

## Contrato de salida

- `informe/borrador.md` — el borrador revisable.
- `informe/informe-final.docx` — el entregable escrito.
- `informe/demo.html` — el entregable para la presentación en vivo:
  la misma síntesis, generada desde el mismo `outputs/*.json`.
- `outputs/sintesis-verificacion.json` y `.md` — resultado de la
  verificación de trazabilidad (números señalados, resueltos o
  justificados).

### Campos del JSON de verificación

```
{
  "numeros_en_borrador": int,
  "numeros_con_respaldo_en_outputs": int,
  "numeros_sin_respaldo": [
    {"valor": str, "contexto": str, "linea_aprox": int}, ...
  ],
  "modo_tolerancia": "decimales_escritos" | "fija",
  "tolerancia_redondeo": float | null
}
```

`tolerancia_redondeo` solo tiene valor en el modo `fija`, el de
`--tolerancia`. En `decimales_escritos` es `null`, porque cada cifra lleva la
suya. *Hasta el 2026-10-02 no existía `modo_tolerancia`, y
`tolerancia_redondeo` valía 0,01 salvo que se pasara otro valor.*

## No interpretes de más

Esta skill sí interpreta —es su trabajo— pero dentro de límites:

- No inventes cifras que "probablemente" salieron de algún lado. Si
  no está en `outputs/`, no va en el cuerpo del informe sin marcar
  explícitamente que es una cifra estructural u obvia, no un resultado.
- No suavices los hallazgos incómodos (el Nivel 2a colapsando, el
  ruido estructural en la clase negativa) para que el informe se lea
  mejor. Son parte del argumento metodológico del proyecto.
- No le atribuyas al cliente conclusiones que el proyecto no probó
  (ej. "este modelo está listo para uso clínico" — nunca se dijo eso
  ni se probó).

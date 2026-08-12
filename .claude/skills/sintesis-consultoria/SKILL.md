---
name: sintesis-consultoria
description: Lee todo outputs/*.json, cruza los hallazgos de las cuatro skills instrumento, y redacta el informe final de consultoría como documento Word. A diferencia de las demás skills del proyecto, esta SÍ interpreta — es su función. Pero cada cifra que aparezca en el informe debe rastrearse hasta un campo específico de un archivo de outputs/, nunca inventarse ni recordarse de memoria. Úsala solo al final, cuando las cuatro skills instrumento ya corrieron sobre los datos reales.
---

# Síntesis de Consultoría

Esta es la única skill del proyecto que interpreta en vez de solo medir.
Es, literalmente, el trabajo del consultor: leer los instrumentos, resolver
las contradicciones entre ellos, y emitir una recomendación defendible.

Todas las demás skills existen para que esta pueda hacer su trabajo con
material confiable. Si alguna de las cuatro no ha corrido sobre los datos
reales, o corrió pero no fue auditada, esta skill no debe usarse todavía
— el informe heredaría esa falta de rigor sin decirlo.

## Antes de empezar

Verifica que existan y tengan contenido real (no vacíos, no de un CSV
sintético de prueba):

- `outputs/eda-diagnostico.json`
- `outputs/diseno-validacion.json`
- `outputs/auditoria-de-fugas.json`
- `outputs/modelado-baseline.json`

Si falta alguno, dilo explícitamente y detente. No redactes el informe
con huecos rellenados de memoria.

## Proceso, en dos fases obligatorias

### Fase 1 — Borrador en Markdown

Redacta primero `informe/borrador.md`, no el `.docx` directamente. Es
más fácil de revisar, corregir y iterar contigo antes de invertir tiempo
en formato. Estructura sugerida:

1. **Resumen ejecutivo** — la tesis del proyecto en un párrafo: el
   agente como consultor, no como competidor de Kaggle.
2. **Contexto y objetivo** — de dónde sale la pregunta, por qué ISIC 2024.
3. **Metodología** — las cinco skills como cadena de instrumentos,
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

### Fase 2 — Verificación de trazabilidad (obligatoria antes de Word)

Corre el script de verificación sobre el borrador:

```bash
python .claude/skills/sintesis-consultoria/scripts/verificar_trazabilidad.py \
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

Si el script señala números sin respaldo, corrige el borrador o
justifica por qué esa cifra no necesita estar en `outputs/` (ej. es un
conteo estructural obvio, no un resultado medido) antes de continuar.

### Fase 3 — Conversión a Word

Solo después de que la trazabilidad esté limpia:

1. Revisa si hay una skill `docx` disponible en este entorno de Claude
   Code (`/mnt/skills/public/docx/` o equivalente). Si existe, síguela
   — tiene gotchas específicas del entorno que conviene respetar.
2. Si no existe, usa `python-docx` (`pip install python-docx`) para
   convertir `informe/borrador.md` en `informe/informe-final.docx`,
   con estilos de encabezado, tabla de contenido, y la tabla de
   trazabilidad como anexo con formato de tabla real, no texto plano.
3. Verifica el resultado abriendo el documento generado o
   convirtiéndolo a PDF para inspección visual antes de darlo por
   terminado — no asumas que el formato salió bien sin mirarlo.

## Contrato de salida

- `informe/borrador.md` — el borrador revisable.
- `informe/informe-final.docx` — el entregable.
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
  "tolerancia_redondeo": float
}
```

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

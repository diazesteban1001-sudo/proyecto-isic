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
├── outputs/               ← salidas de cada skill (.json + .md)
└── informe/
```

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

## Sobre el problema — POR VERIFICAR

Todo lo de esta sección debe confirmarse contra la página oficial de la
competencia antes de usarse. Está escrito de memoria y puede estar desactualizado
o ser incorrecto.

- [ ] Objetivo: detectar lesiones malignas confirmadas por histología
- [ ] Insumo: recortes de fotografía corporal total 3D (calidad baja, tipo
      dispositivo casero, NO dermatoscopio clínico)
- [ ] Metadata tabular disponible: tamaño, color, forma, ubicación, edad, sexo
- [ ] Desbalance de clases extremo
- [ ] **Observaciones agrupadas por paciente** ← crítico
- [ ] Métrica: AUC parcial restringido a zona de sensibilidad alta
- [ ] Confirmar umbral exacto de sensibilidad de la métrica
- [ ] Confirmar reglas de uso de datos externos

**Nota metodológica clave:** la agrupación por paciente hace que
`auditoria-de-fugas` tenga algo real que encontrar. Si se parten los datos al
azar, lesiones del mismo paciente caen en entrenamiento y validación, y la
métrica sale inflada. Error clásico, verificable, y material de primera para el
informe.

---

## Decisiones tomadas

| Decisión | Razón |
|---|---|
| ISIC 2024 sobre los demás problemas | La metadata tabular hace gran parte del trabajo → sin GPU. Desbalance y agrupación por paciente son estadísticamente interesantes. La métrica tiene justificación clínica discutible en el informe. |
| Se descartan RSNA rodilla y RSNA columna lumbar | Imágenes médicas 3D: exigen GPU seria y aportan poco desde lo estadístico. |
| Un agente, no varios | Las skills son instrumentos que el agente interpreta, no actores independientes. |
| Claude Code sobre claude.ai | Las skills son mecanismo nativo, ejecución de Python sobre datos reales, `outputs/` persistente, todo versionado en Git. |

---

## Estado actual

**Fase:** diseño. Ninguna skill escrita todavía.

### Siguiente paso

Escribir `eda-diagnostico/SKILL.md` completo —frontmatter, contrato de salida y
script— como plantilla de referencia para las demás.

### Pendientes

- [ ] Instalar Claude Code y verificar qué incluye el plan actual
- [ ] Verificar la sección "Sobre el problema" contra la fuente oficial
- [ ] Descargar los datos a `data/`
- [ ] Escribir las 5 skills
- [ ] Empaquetar las skills como archivos `.skill` instalables (extra para el profe)
- [ ] Preparar demo en vivo: plantear una pregunta al agente y que invoque las
      skills frente a la clase

---

## Presentación al profesor

1. **El repositorio** — el historial de commits es la narrativa de las decisiones.
2. **El informe escrito** — producido por `sintesis-consultoria` desde `outputs/`,
   con trazabilidad de cada cifra.
3. **Demo en vivo** — es lo que más pesa: muestra la arquitectura funcionando en
   vez de descrita.

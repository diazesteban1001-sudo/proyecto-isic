## Extensión del proyecto — Fase de imágenes y modelos fundacionales

**Definido:** sesión de planificación del 18 de agosto de 2026. Estado: PLAN
ACORDADO, NADA EJECUTADO TODAVÍA. Esta sección documenta decisiones de
diseño, no resultados.

### Por qué esta extensión existe

El alcance original excluía imágenes por restricción de cómputo. Con más
tiempo disponible (1-2 meses) y hardware capaz (MacBook Air M4), se decidió
extender el proyecto — pero SIN abandonar la tesis original. Esta extensión
la profundiza, no la reemplaza.

### Tesis ampliada

La tesis original decía: la finalidad del agente es leer la función de
utilidad que el cliente escribió en su métrica, no ganar la competencia.

Esta extensión toma esa idea en serio hasta el final: la competencia ISIC
2024 declaró, con premios secundarios reales, que su función de utilidad
tenía TRES componentes, no uno:

1. pAUC sobre 80% TPR (métrica principal)
2. "Top-15 Retrieval Sensitivity" — capacidad de priorizar las 15 lesiones
   más sospechosas por paciente (relevante clínicamente: es la pregunta
   real que enfrenta un dermatólogo con cientos de lesiones por paciente)
3. "Model Efficiency" — costo de inferencia

**La pregunta que responde esta extensión:** ¿cuál es la mejor
recomendación que un consultor le daría hoy a MSKCC, evaluada contra su
función de utilidad completa —no solo contra el pAUC del leaderboard—
usando la tecnología disponible en 2026?

Esto NO es "intentar ganarle al primer lugar de 2024". Es evaluar el
problema completo tal como el cliente lo definió, con las herramientas de
hoy.

### Por qué no hay leaderboard privado que usar

La competencia cerró; el conjunto de prueba privado no es accesible. El
primer lugar (Ilya Novoselskiy, score privado 0,17265/0,2, ≈86,3% del
máximo) documentó su solución completa en:
https://www.kaggle.com/competitions/isic-2024-challenge/writeups/ilya-novoselskiy-1st-place-solution
(leído por capturas de pantalla del usuario, no accesible vía fetch por
bloqueo de JavaScript — pendiente guardar copia en referencias/ si se cita
textualmente).

Su arquitectura: EVA02-small + EdgeNeXt (imagen) → predicciones OOF
concatenadas con metadata tabular → ensamble de 150 modelos GBDT
(CatBoost/LGBM/XGBoost, 5 folds × 10 semillas). Feature más valiosa
reportada: comparación de cada lesión contra el promedio de lesiones del
mismo paciente (Local Outlier Factor agrupado por patient_id) — la
traducción numérica del concepto clínico "patito feo". Datos sintéticos
(Stable Diffusion) mejoraron CV individual pero NO el ensamble final; el
propio autor los descartó de su solución premiada.

### Protocolo de medición sin leaderboard (DECIDIDO)

Dos vías combinadas, no una sola:

**Vía A — CV comparable con el ganador.** Mismo esquema documentado por el
ganador: StratifiedGroupKFold, 5 folds, repetido con múltiples semillas
(el ganador usó 10). Comparar DISTRIBUCIONES de pAUC entre semillas, no
puntos únicos. Declarar explícitamente en el informe que esto compara
pipelines, no arquitecturas aisladas, y que las asignaciones de fold no
son idénticas a las suyas.

**Vía B — lockbox propio.** Antes de tocar ningún modelo nuevo: apartar
~20% de los PACIENTES (no de las filas), estratificado para contener
positivos, y no tocarlo hasta la evaluación final única. Con ~393
positivos totales, el lockbox tendrá ~79 — suficiente para pAUC final,
pero con varianza alta; por eso es confirmación, no la estimación
principal.

**Regla operativa: Fase 2 (protocolo) se monta ANTES que Fase 3-4 (modelos
nuevos), no después** — para que el protocolo no se ajuste al resultado.

### Riesgo bloqueante: contaminación del modelo fundacional

PanDerm (Nature Medicine 2025, github.com/SiyuanYan1/PanDerm) es un modelo
fundacional de dermatología preentrenado con >2M imágenes de 11
instituciones, incluyendo 757.890 imágenes de TBP (35,3% del
preentrenamiento) — la misma modalidad que ISIC 2024. Sucesor:
DermFM-Zero / PanDerm-2 (feb. 2026, huggingface.co/redlessone/PanDerm2).

**Antes de usar estos pesos: verificar si SLICE-3D (el dataset de ISIC
2024) estuvo entre las fuentes de preentrenamiento.** MSKCC —anfitrión de
ISIC 2024— aparece mencionado como fuente institucional de PanDerm. Si hay
solape, cualquier resultado de un modelo congelado sobre estos datos está
inflado por fuga — no por un error del proyecto, sino por el propio
preentrenamiento del modelo descargado. Esto se investiga (posiblemente
contactando a los autores, correo público en el repo) ANTES de descargar
pesos y usarlos. Si se confirma contaminación, no se usa PanDerm — y ese
hallazgo se documenta como parte del informe: la fuga en la era de modelos
fundacionales se desplaza del propio dataset al preentrenamiento de
terceros.

Alternativa de respaldo si PanDerm está contaminado: DINOv3 (modelo
genérico, no específico de dermatología, pero sin este riesgo conocido).

### Plan de fases (orden de dependencia)

- **Fase 0 (bloqueante):** resolver contaminación de PanDerm/DermFM-Zero
  con SLICE-3D antes de cualquier otra cosa.
- **Fase 1:** features de "paciente relativo" sobre metadata tabular
  existente (LOF agrupado por patient_id, ratio contra promedio del
  paciente). Sin imágenes. Días de trabajo, minutos de cómputo. Se espera
  que mejore el pAUC de modelado-baseline actual (0,1451).
- **Fase 2:** montar el protocolo de medición (Vía A + Vía B) antes de
  entrenar nada nuevo.
- **Fase 3:** extracción de características congeladas del modelo
  fundacional (una pasada hacia adelante por imagen, sin fine-tuning) —
  factible en M4 corriendo overnight.
- **Fase 4:** apilar esas características + metadata + features de paciente
  relativo en el mismo pipeline tabular ya auditado (extensión de
  modelado-baseline). Tabla final comparando los tres ejes de la función
  de utilidad (pAUC, retrieval top-15 por paciente, costo de inferencia).

### Nota sobre alternativas tabulares (contexto, no decisión)

TabPFN y otros "modelos fundacionales tabulares" (TabArena, 2026) superan
a gradient boosting en benchmarks, pero: (a) los números provienen en
buena parte del propio laboratorio que los publica — señalado como
conflicto de interés por los mantenedores independientes de TabArena; (b)
sin ensamblar configuraciones, CatBoost vuelve a liderar; (c) la "zona
seguía" documentada es de decenas de miles de filas — el dataset completo
(401.059) probablemente excede el rango validado. No se decidió usar
TabPFN; queda como nota de contexto, no como plan.

### Pendiente de esta sesión

- [ ] Verificar contaminación de PanDerm con SLICE-3D (Fase 0)
- [ ] Guardar copia del writeup del 1er lugar en referencias/ si se va a
      citar textualmente (actualmente solo visto por capturas de pantalla
      del usuario en el chat de planificación, no por fetch directo)
- [ ] Decidir tamaño exacto del lockbox y semilla de partición
- [ ] Decidir cuántas semillas usar en la Vía A (¿10, como el ganador, o
      menos por limitación de tiempo/cómputo?)

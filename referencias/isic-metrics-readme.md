# ISIC-Research/Challenge-2024-Metrics — README (FICHA)

**Qué es:** el README del repositorio de métricas del organizador del reto,
ISIC / MSKCC.
**URL:** https://github.com/ISIC-Research/Challenge-2024-Metrics (archivo
`README.md`, rama `main`; copia en crudo desde
https://raw.githubusercontent.com/ISIC-Research/Challenge-2024-Metrics/main/README.md).
**Fecha de consulta:** 2026-08-12. Contrastado de nuevo el 2026-09-21.

**LICENCIA: ninguna → FICHA.** El repositorio **no tiene archivo de
licencia**: la API de GitHub devuelve `license: null` y
`/repos/ISIC-Research/Challenge-2024-Metrics/license` responde 404; en la raíz
solo hay `PrimaryMetric-pAUC.py`, `README.md` y
`SecondaryMetric-TopNSensitivity.py`. Sin licencia rige el copyright por
defecto. Verificado el 2026-09-21.

**Texto completo:** en local, `referencias/_texto-completo/isic-metrics-readme.md`
(la copia del 2026-08-12) y `referencias/_texto-completo/upstream-README.md`
(copia del 2026-09-21).

**Por qué está aquí:** el umbral de 88% TPR del esquema de premios del
organizador **no está en el script** —allí `min_tpr` es un parámetro sin valor
por defecto—, así que citarlo exigía la fuente donde sí está escrito.

---

## Citas literales que el proyecto usa

**Sección "Primary Scoring Metric", párrafo 1** — el umbral del organizador,
distinto del de Kaggle (`informe/borrador.md`, Anexo E, fila E7):

> For the leaderboard prizes, submissions are evaluated on **partial area
> under the ROC curve (pAUC)** above 88% true positive rate (TPR) for binary
> classification of malignant examples.

**Misma sección, párrafo 2** — la justificación clínica en la versión del
organizador (`CLAUDE.md` y `informe/borrador.md` usan su segunda frase;
`CLAUDE.md` contrasta *"required to be highly-specific"* con el
*"highly-sensitive"* de Kaggle):

> The receiver operating characteristic (ROC) curve illustrates the diagnostic
> ability of a given binary classifier system as its discrimination threshold
> is varied. However, there are regions in the ROC space where the values of
> TPR are unacceptable in clinical practice. Systems that aid in diagnosing
> cancers are required to be highly-specific, so this metric focuses on the
> area under the ROC curve AND above 88% TRP. Therefore, scores range from
> [0.00, 0.12].

*"TRP" es errata del original, por "TPR"; se conserva porque la cita es
literal.*

**Sección "Two Secondary Scoring Metrics"** — los dos premios secundarios
(`CLAUDE.md`, "Tesis" y "Sobre el problema"):

> - Top-15 retrieval sensitivity
> - Model Efficiency

**Subsección "Top-15 retrieval sensitivity"** — que la métrica se calcula
**por paciente**, que es lo que `CLAUDE.md` afirma de ella:

> A secondary prize is awarded to the submission with the highest **top-15
> retrieval sensitivity**.

> To help answer this question, one secondary prize will be awarded to the
> algorithm that is most successful in scoring malignancies within the top-15
> highest scored images per patient.

**Subsección "Model Efficiency"** — el eje de costo de inferencia (`PLAN.md`,
Fase 6):

> Submissions will be evaluated for inference time on an undisclosed subset of
> test set images.

## Localizadores del resto — sin texto

- Tras el párrafo 2: figura de las regiones de pAUC de dos algoritmos.
- "Top-15 retrieval sensitivity", párrafo 1: escenario hipotético de un
  dermatólogo con pocos minutos por paciente (motivación, no definición).
- "Top-15 retrieval sensitivity", final: regla de desempate.
- "Model Efficiency", final: el premio es opcional y requiere enviar un
  *notebook* a los organizadores.

# Kaggle — ISIC 2024, página de evaluación (FICHA)

**Qué es:** la página de evaluación de la competición *ISIC 2024 - Skin Cancer
Detection with 3D-TBP* en Kaggle.
**URL:** https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation
**Entidad:** Kaggle (plataforma) · Memorial Sloan Kettering Cancer Center
(anfitrión y patrocinador de la competición).
**Fecha de consulta:** 2026-08-11, copia tomada a mano con sesión de Kaggle
iniciada (la página no es legible sin navegador ni sesión).

**LICENCIA: desconocida → FICHA.** La página licencia expresamente **una
figura** —*"pAUC defined by constraining TPR" by ProfGigio is licensed under
CC-BY-SA-4.0*— pero **no declara licencia para su propio texto**. Sin licencia
declarada, rige el copyright por defecto. Determinado leyendo la propia copia,
2026-09-21.

**Texto completo:** en local, `referencias/_texto-completo/kaggle-evaluation.md`
(no versionado; regla 3 de `CLAUDE.md`). Si falta, se vuelve a copiar desde la
URL con sesión iniciada.

---

## Citas literales que el proyecto usa

Todas de la sección **"Primary Scoring Metric"**, que es la primera de la
página. Son los dos primeros párrafos de esa sección, completos: el proyecto
cita casi todo lo que dicen.

**Párrafo 1** — la definición de la métrica (`CLAUDE.md`, "Sobre el problema"):

> Submissions are evaluated on partial area under the ROC curve (pAUC) above
> 80% true positive rate (TPR) for binary classification of malignant examples.

**Párrafo 2** — la justificación clínica, que es el eje de la tesis
(`CLAUDE.md`, "Tesis del proyecto"; `informe/borrador.md`, Anexo E, fila E1):

> The receiver operating characteristic (ROC) curve illustrates the diagnostic
> ability of a given binary classifier system as its discrimination threshold
> is varied. However, there are regions in the ROC space where the values of
> TPR are unacceptable in clinical practice. Systems that aid in diagnosing
> cancers are required to be highly-sensitive, so this metric focuses on the
> area under the ROC curve AND above 80% TPR. Hence, scores range from
> [0.0, 0.2].

De ese párrafo el proyecto usa además, por separado, los fragmentos
*"unacceptable in clinical practice"* y *"required to be highly-sensitive"*; los
dos están dentro de la cita de arriba.

## Localizadores del resto — sin texto

- Primer párrafo, final: remite a la implementación en el *notebook* "ISIC
  pAUC-aboveTPR" de Kaggle, que el agente no puede leer. La implementación
  equivalente del organizador está en `referencias/isic-primary-metric-pauc.py.md`.
- Tercer párrafo: pie de la figura de ProfGigio (CC-BY-SA-4.0).
- Sección **"Submission File"**: formato del archivo de envío — columnas
  `isic_id` y `target`, con cabecera.

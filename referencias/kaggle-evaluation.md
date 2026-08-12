# ISIC 2024 - Skin Cancer Detection with 3D-TBP — Evaluation

Fuente: https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation
Copiado manualmente con sesión de Kaggle iniciada, el 11 de agosto de 2026.

---

## Primary Scoring Metric

Submissions are evaluated on partial area under the ROC curve (pAUC) above
80% true positive rate (TPR) for binary classification of malignant examples.
(See the implementation in the notebook ISIC pAUC-aboveTPR.)

The receiver operating characteristic (ROC) curve illustrates the diagnostic
ability of a given binary classifier system as its discrimination threshold
is varied. However, there are regions in the ROC space where the values of
TPR are unacceptable in clinical practice. Systems that aid in diagnosing
cancers are required to be highly-sensitive, so this metric focuses on the
area under the ROC curve AND above 80% TPR. Hence, scores range from
[0.0, 0.2].

The shaded regions in the following example represents the pAUC of two
arbitrary algorithms (Ca and Cb) at an arbitrary minimum TPR: "pAUC defined
by constraining TPR" by ProfGigio is licensed under CC-BY-SA-4.0.

## Submission File

For each image (`isic_id`) in the test set, you must predict the probability
(`target`) that the lesion is malignant. The file should contain a header
and have the following format:

```
isic_id,target
ISIC_0015657,0.7
ISIC_0015729,0.9
ISIC_0015740,0.8
etc.
```

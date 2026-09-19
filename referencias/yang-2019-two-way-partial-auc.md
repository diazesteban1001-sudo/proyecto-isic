# Yang, Lu, Lyu y Hu — "Two-Way Partial AUC and Its Properties"

**Autores:** Hanfang Yang (autor de correspondencia, School of Statistics,
Renmin University of China), Kun Lu, Xiang Lyu, Feifang Hu.

**Doble publicación — las dos referencias, porque no son la misma cosa:**

| | Preprint | Versión de revista |
|---|---|---|
| Dónde | arXiv:1508.00298 [stat.ME] | Statistical Methods in Medical Research |
| Año | enviado 3 ago 2015; v3 del 21 jun 2017 | 2019 ene; 28(1):184–195 |
| DOI | 10.48550/arXiv.1508.00298 | 10.1177/0962280217718866 |
| Otros | — | Epub 14 jul 2017 · PMID 28707503 |

**Sí tiene publicación en revista además del preprint**, con los mismos cuatro
autores y el mismo título. Se verificó en PubMed
(https://pubmed.ncbi.nlm.nih.gov/?term=%22two-way+partial+AUC%22), no en la
página de arXiv: **la entrada de arXiv no declara referencia de revista**, así
que quien mire solo ahí concluiría que es un preprint sin publicar.

**Para citar:** la versión citable es la de *Statistical Methods in Medical
Research* (2019). **El cuerpo de este archivo es el preprint v3 de arXiv**, que
es el texto accesible. No se ha comparado con la versión publicada: la
paginación es distinta con seguridad, y la redacción puede serlo. **Si una
frase de aquí se cita en el informe, se cita como del preprint**, o se
comprueba antes contra la versión de revista.

**Fecha de consulta:** 2026-09-19
**URL del preprint:** https://arxiv.org/abs/1508.00298 (PDF:
https://arxiv.org/pdf/1508.00298)

**Cómo se tomó:** el PDF de arXiv (46 páginas) se descargó y se extrajo su
texto con `pypdf`. **No se reproduce entero a propósito:** la extracción
destroza la notación matemática —integrales, subíndices y ligaduras `ﬁ`/`ﬀ`
quedan corruptas—, así que un volcado completo sería ilegible y daría falsa
sensación de fidelidad. Se reproducen literalmente los pasajes que el proyecto
necesita, indicando la línea del texto extraído. Lo que no está aquí se
consulta en el PDF.

---

## Texto original — resumen (páginas 1–2 del preprint)

Abstract
Simultaneous control on true positive rate (TPR) and false positive rate (FPR) is of sig-
niﬁcant importance in the performance evaluation of diagnostic tests. Most of the established
literature utilizes partial area under the receiver operating characteristic (ROC) curve with re-
strictions only on FPR, called FPR pAUC, as a performance measure. However, its indirect
control on TPR is conceptually and practically misleading. In this paper, a novel and intuitive
performance measure, named as two-way pAUC, is proposed, which directly quantiﬁes partial
area under the ROC curve with explicit restrictions on both TPR and FPR. To estimate two-
way pAUC, we devise a nonparametric estimator. Based on the estimator, a bootstrap-assisted
testing method for two-way pAUC comparison is established. Moreover, to evaluate possible
covariate eﬀects on two-way pAUC, a regression analysis framework is constructed. Asymptotic
normalities of the methods are provided. Advantages of the proposed methods are illustrated by
simulation and Wisconsin Breast Cancer Data. We encode the methods as a publicly available
R package tpAUC.
Keyword: ROC curve; True positive rate; False positive rate; Discrimination capability; Diagnos-
tic test.
∗Corresponding Author. Associate Professor, School of Statistics, Renmin University of China, China. E-mail:
hyang@ruc.edu.cn.

---

## Texto original — el pasaje sobre el límite inferior artificial de FPR

### (a) Introducción, donde se plantea el problema

to assess the region of interest with TPR constraint. In particular, one of the most popular
methods is to set lower and upper restrictions on FPR, which is named FPR pAUC and deﬁned
as FPR pAUC(p1,p 2) :=
∫p2
p1
ROC(t)dt and p1 (p2) is an lower (upper) constraint on FPR. See
(4; 5; 6; 7; 8; 9; 10). The lower bound of FPR, p1, is to indirectly maintain the lower bound of TPR
atROC(p1). Meanwhile, p2 is to restrict FPR from being too high. However, regarding area under
ROC in economical and ethical region, such a deﬁnition incorporates the redundant area below
TPR constraint (see Figure 1 and Remark 3.1). This leads FPR pAUC to suﬀer ineﬃciency and
inaccuracy in performance evaluation. Therefore, the need for a direct and practical performance
measure of the region with high TPR and low FPR arises in clinical research.
In this paper, we design a novel performance measure, named as two-way partial AUC (two-
way pAUC), which is a ﬂexible tool to control explicit TPR and FPR restrictions. Unlike utilizing
an artiﬁcial FPR lower bound to indirectly control acceptable TPR, two-way pAUC provides a
straightforward measure to substitute existing methods with independent vertical and horizontal
limits. Due to this natural principle, two-way pAUC is convenient and intuitive for implementation
2

### (b) Pie de la Figura 1, y la comparación de dos curvas

Figure 1: Two-way pAUC denotes the area of shaded region A. This shaded region is directly
determined by explicit FPR upper boundp0 (= 0.5) and TPR lower boundq0 (= 0.65). In contrast,
FPR pAUC denotes the area of both region A and B. Its indirect FPR lower bound (green dotted
line) is determined by the TPR lower bound q0.
within the given region. Note that the lower bounds on FPR in FPR pAUC at two diﬀerent ROC
curves are respectively determined by the pre-speciﬁc TPR lower bound. Hence, as shown in Figure
2a, FPR pAUCs ofROC1 andROC2 are the areas ofS3 +S4 andS1 +S2 +S3 +S4 respectively, and
corresponding two-way pAUCs areS3 andS1 +S3. The diﬀerence of two classiﬁers’ discrimination
capabilities is S1 by two-way pAUC. In contrast, the diﬀerence is S1 +S2 by FPR pAUC. Due
to that S2 is below TPR constraint, it should not be taken into consideration. The redundant
unethical area, S2, distorts the comparison of two classiﬁers. Thus, two-way pAUC with direct
restrictions is more eﬃcient (links to statistical power) than FPR pAUC (refer to numerical study
in Section 5).
Scenario 2: In Figure 2b, the region is of interest where TPR is larger than 0.6 and FPR is smaller
than 0.6. ROC1 has better discrimination capability in the region than ROC2 (due to S6>S 5, as

### (c) Remark 3.1 — la formulación explícita de la crítica

Remark 3.1. Two-way pAUC aggregates the discrimination capability of a binary classiﬁer within
a given region directly determined by explicit constraints on both TPR and FPR. Previous works,
instead, utilize an synthetic approach, namely FPR pAUC here, to put an indirect lower restric-
tion on TPR via artiﬁcially setting a corresponding FPR lower bound (6). In particular, p1 is
to indirectly lower bound TPR so that it can be maintained at an acceptable level. Let q0 be the
lower constraint of interest on TPR. Likewise, p2 is the pre-speciﬁc upper bound on FPR. In order
to maintain acceptable TPR, investigators denote p1 = ROC−1(q0) = SG[S−1
F (q0)] as the lower
constraint on FPR. FPR pAUC is calculated as follows,
FPR pAUC (p1,p 2) =
∫ p2
SG[S−1
F (q0)]

### (d) Remark 3.2 — el mismo defecto, simétrico, en el TPR pAUC

ROC(t)dt.
Remark 3.2. Similar to FPR pAUC, there exists another indirect synthetic approach, named as
TPR pAUC (11). Under TPR and FPR constraints, its philosophy is to indirectly prevent FPR from
being too high via setting an artiﬁcial upper bound on TPR. Letq0 andp0 be the bounds of interest on
FPR (≤p0) and TPR (≥q0), respectively. TPR pAUC is formulated as TPR pAUC (q0, q1(p0)) :=
∫q1(p0)

---

## Por qué importa para este proyecto

**Nota nuestra, no del artículo — se marca como tal.** La métrica de ISIC 2024
es exactamente un *FPR pAUC* en el sentido de este artículo: el script oficial
fija `max_fpr = |1 - min_tpr|` e integra sobre FPR, de modo que el control
sobre el TPR es indirecto (`referencias/isic-primary-metric-pauc.py.md`). Este
trabajo sostiene que ese control indirecto es *"conceptually and practically
misleading"* y que el área sobrante por debajo de la restricción de TPR
*"distorts the comparison of two classifiers"*. No se sigue de ahí que la
métrica del cliente esté mal elegida: se sigue que tiene una crítica publicada
y con nombre, y que conviene citarla en vez de presentarla como incontestada.

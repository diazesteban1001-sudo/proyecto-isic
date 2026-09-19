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

## Qué relación tiene con este proyecto — CORREGIDO el 2026-09-19

> **Una versión anterior de este archivo afirmaba que la métrica de ISIC 2024
> "es exactamente un *FPR pAUC* en el sentido de este artículo". Es falso.**
> La afirmación se escribió sin comprobarla contra el script oficial; al ir a
> buscar la línea que la respaldara, resultó que no existe. Se deja el error
> anotado en vez de borrarlo, porque el modo de fallo —una lectura plausible
> dada por buena sin abrir el código— es el que el proyecto registra.

### Qué hace realmente el script oficial

Todas las líneas son de `referencias/isic-primary-metric-pauc.py.md`:

| Línea | Código | Qué hace |
|---|---|---|
| 54–55 | `v_gt = abs(np.asarray(v_gt)-1)` y lo mismo con `v_pred` | **invierte etiquetas y puntajes** |
| 56 | `max_fpr = abs(1-min_tpr)` | deriva el tope del umbral de sensibilidad |
| 59 | `fpr, tpr, _ = sklean.roc_curve(v_gt, v_pred, ...)` | ROC **sobre las etiquetas ya invertidas** |
| 66, 70 | `stop = np.searchsorted(fpr, max_fpr, "right")` … `fpr = np.append(fpr[:stop], max_fpr)` | trunca en el eje `fpr` |
| 71 | `partial_auc = sklean.auc(fpr, tpr)` | integra con `fpr` como eje x |

**La línea 54 lo cambia todo.** Como las etiquetas están invertidas, la variable
que el código llama `fpr` **no es el FPR del problema original**: es
`1 − TPR_original`. Acotarla por arriba con `max_fpr = 1 − min_tpr` equivale
entonces a acotar `TPR_original ≥ min_tpr`, **directamente**. La métrica es una
restricción **vertical sobre el TPR**, y **no impone ninguna restricción sobre
el FPR**: la región integrada incluye cualquier FPR mientras el TPR supere el
umbral.

### Comprobación, no deducción

Se corrió el script oficial contra las dos hipótesis, con seis semillas
(n = 20.000, prevalencia 2%, `min_tpr = 0.80`):

| Semilla | Script oficial | (A) área con TPR ≥ 0,80 | (B) pAUC con FPR ≤ 0,20 |
|---|---|---|---|
| 0 | 0,080512 | **0,080512** | 0,081155 |
| 1 | 0,091335 | **0,091335** | 0,085318 |
| 2 | 0,089962 | **0,089962** | 0,093062 |
| 3 | 0,079038 | **0,079038** | 0,084093 |
| 4 | 0,083016 | **0,083016** | 0,083691 |
| 5 | 0,082145 | **0,082145** | 0,084461 |

Seis de seis coinciden con (A) al dígito y ninguna con (B). El máximo teórico de
(A) es `1 − 0,80 = 0,2`, que es el rango `[0.0, 0.2]` que documenta Kaggle
(`referencias/kaggle-evaluation.md`) — coincidencia que (B) no explica por sí
sola pero que junto a la tabla cierra el caso.

### Qué se sigue, y qué no

- **La crítica central de Yang et al. NO aplica a ISIC 2024.** Su objeto es el
  *FPR pAUC*: un límite **inferior artificial sobre el FPR** usado para
  controlar el TPR de forma indirecta. ISIC no hace eso — su restricción sobre
  el TPR es explícita y directa. Ninguna frase del informe puede decir que la
  métrica del cliente incurre en el defecto que este artículo describe.
- **Tampoco es el *TPR pAUC* del Remark 3.2**, que pone un límite **superior**
  artificial sobre el TPR para frenar el FPR. ISIC integra hasta TPR = 1 y no
  tiene ese segundo límite.
- **Lo que sí conecta — y es lectura nuestra, no del artículo.** El argumento
  general de fondo es que restringir un solo eje deja el otro sin controlar.
  ISIC fija el TPR y no acota el FPR en absoluto. Que eso sea un defecto
  depende de si al cliente le importa un techo de FPR, y por su propio artículo
  de 2025 parece que sí: definen `NNTx% SE`, una métrica de precisión
  (`referencias/kurtansky-2025-triaje-automatizado-tbp.md`). Esa conexión es
  defendible y es la que vale la pena desarrollar — pero se presenta como
  razonamiento propio apoyado en el marco de Yang et al., nunca como algo que
  el artículo diga sobre ISIC.

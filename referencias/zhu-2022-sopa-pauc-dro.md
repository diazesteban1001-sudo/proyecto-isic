# Zhu et al. (2022) — When AUC meets DRO: la pAUC unilateral con SOPA

**Autores:** Dixian Zhu, Gang Li, Bokun Wang, Xiaodong Wu, Tianbao Yang.
**Título:** *When AUC meets DRO: Optimizing Partial AUC for Deep Learning with
Non-Convex Convergence Guarantee.*
**Publicación:** Proceedings of the 39th International Conference on Machine
Learning (ICML 2022), PMLR 162, pp. 27548–27573 (metadatos `citation_*` de
https://proceedings.mlr.press/v162/zhu22g.html).
**arXiv:** 2203.00176. Cinco versiones: v1 a v3 de marzo de 2022, v4 del 27 de
junio de 2022 y v5 del 18 de septiembre de 2023 (historial de la página de
resumen).
**Fecha de consulta:** 2026-11-01.

**LICENCIA: CC BY 4.0 → TEXTO COMPLETO, el de arXiv v5.** La página de resumen
de la v5 (https://arxiv.org/abs/2203.00176v5) y la de la v4 enlazan
https://creativecommons.org/licenses/by/4.0/ como licencia del artículo
(«view license»). La versión de PMLR no declara licencia propia: su página solo
dice *"Copyright © The authors and PMLR 2026."*, el pie del sitio; cuenta como
desconocida y no se versiona. Atribución: Zhu D, Li G, Wang B, Wu X, Yang T,
arXiv:2203.00176v5 (2023), CC BY 4.0. **Cambios** respecto del original, como
pide la licencia: el texto es la salida de `pypdf` 6.15.0 sobre el PDF de la v5,
con una marca «=== página N ===» nuestra al empezar cada página; las fórmulas,
las tablas y los ejes de las figuras salen desordenados, los superíndices y
subíndices quedan en la línea, y las figuras no se reproducen. Se añaden esta
cabecera y las secciones marcadas como nuestras.

**Cómo se tomó:** con `curl`, sin WebFetch (regla 3), los PDF de
https://proceedings.mlr.press/v162/zhu22g/zhu22g.pdf (SHA-256 `ce0c5e44…`),
https://arxiv.org/pdf/2203.00176v4 (`9d47ea4d…`) y
https://arxiv.org/pdf/2203.00176v5 (`0fd6aecb…`), y las páginas de resumen de
las dos versiones de arXiv. El enlace al material suplementario de PMLR
(`zhu22g-supp.pdf`) da 404; el apéndice va dentro del PDF del artículo. Los
tres PDF, su texto y las páginas de resumen están en
`referencias/_texto-completo/`, con el prefijo `zhu-`.

**Qué versión se cita y por qué.** El artículo es el de ICML 2022. Se versiona
la v5 porque es la que tiene licencia abierta y la que mejor se extrae: la v4
sale con ligaduras («ﬁ») y sin algunos espacios. *Comprobado el 2026-11-01:*
cada una de las nueve citas de abajo está literal, con los espacios
normalizados, en el texto de la v5 y en el de PMLR, en la misma página. En el de
la v4, tres de las nueve están literales, y las otras seis coinciden al quitar
las ligaduras (NFKC) y los espacios.

---

## Lo que usa el proyecto *(sección nuestra)*

`PLAN.md`, Fase 4e, paso 2: el ajuste fino con la pérdida de pAUC unilateral
y la regla con que se fijan sus ajustes, decidida por la persona el
2026-11-01: primero lo que el artículo fija para su experimento de Melanoma,
después la documentación de SOPA en LibAUC (`referencias/libauc-2.0.1.md`), y
lo que ninguno fije lo decide el agente con el criterio más simple y lo declara.

**Los ajustes del experimento no son propios de Melanoma.** El artículo los da
una vez, para todos sus conjuntos de imágenes; Melanoma es uno de ellos, con el
mismo modelo que los otros dos. Página 7, «Datasets.»:

> "The Melanoma dataset is a naturally imbalanced medical dataset which is
> released on Kaggle (Rotemberg et al., 2021)."

Página 7, «Deep Models.»:

> "use ResNet18 (He et al., 2016) for CIFAR-10, CIFAR100 and Melanoma."

Su tabla 5, página 12, da 26.500 imágenes de entrenamiento de Melanoma, el
1,76 % positivas.

**La pérdida y la actualización.** Página 8:

> "and also use the Adam-style update unless specified explicitly."

La frase empieza con la pérdida subrogada, ℓ(t) = (1 − t)²₊ (*paráfrasis de la
fórmula*, que en el texto extraído sale como «ℓ(t) = (1 − t)2» y un «+» en la
línea siguiente): la bisagra cuadrada con margen 1.

**El protocolo de dos etapas.** Página 8; la frase empieza con *"we use a pre-
training step that"*, cortada por un guion de fin de línea:

> "optimizes the base model by optimizing CE loss with an Adam optimizer, and
> then re-initialize the classifier layer and fine-tune all layers by
> different methods."

**Los ajustes.** Página 8, «Parameter Tuning.»:

> "The learning rate of all methods is tuned in {1e-3, 1e-4, 1e-5}"

> "Weight decay is fixed as 2e-4. Each method is run 60 epochs in total and
> learning rate decays 10-fold after every 20 epochs. The mini-batch size is
> 64."

> "For SOPA, we tune the truncated FPR i.e. β in {0.1, 0.3, 0.5}."

> "For comparison of testing performance, the parameters are tuned according
> to the validation performance."

Es decir: la tasa y β se eligieron con la validación, dentro de una rejilla, y
el artículo no dice qué valor quedó para Melanoma. El decaimiento de pesos, las
épocas, el calendario y el lote sí están fijados.

**El muestreo.** Página 5, algoritmo 1, paso 3:

> "Sample two mini-batches B+ ⊂ S+, B− ⊂ S−"

Un minilote de cada clase. El artículo no dice cuántos casos de cada una.

**Lo que no dice la descripción de los experimentos** *(se leyeron completas
la sección 6 y el apéndice A, páginas 7 a 13; no las demostraciones de los
apéndices B y C)*: el tamaño de cada uno de los dos minilotes, el paso de las
variables duales, la inicialización de la capa de clasificación nueva, si la
salida de la red pasa por una sigmoide antes de la pérdida, el recorte del
gradiente y la semilla del muestreo.

---

## Texto original

=== página 1 ===
When AUC meets DRO: Optimizing Partial AUC
for Deep Learning with Non-Convex Convergence Guarantee
Dixian Zhu * 1 Gang Li * 1 Bokun Wang 1 Xiaodong Wu 2 Tianbao Yang 1
Abstract
In this paper, we propose systematic and effi-
cient gradient-based methods for both one-way
and two-way partial AUC (pAUC) maximization
that are applicable to deep learning. We pro-
pose new formulations of pAUC surrogate ob-
jectives by using the distributionally robust opti-
mization (DRO) to define the loss for each individ-
ual positive data. We consider two formulations
of DRO, one of which is based on conditional-
value-at-risk (CVaR) that yields a non-smooth
but exact estimator for pAUC, and another one
is based on a KL divergence regularized DRO
that yields an inexact but smooth (soft) estimator
for pAUC. For both one-way and two-way pAUC
maximization, we propose two algorithms and
prove their convergence for optimizing their two
formulations, respectively. Experiments demon-
strate the effectiveness of the proposed algorithms
for pAUC maximization for deep learning on var-
ious datasets. The proposed methods are imple-
mented with tutorials in our open-sourced library
LibAUC (www.libauc.org).
1. Introduction
AUC, short for the area under the ROC curve, is a perfor-
mance measure of a model, where the ROC curve is a curve
of true positive rate (TPR) vs false positive rate (FPR) for all
possible thresholds. AUC maximization in machine learn-
ing has a long history dating back to early 2000s (Herbrich
et al., 1999). It has four ages in the twenty-years history,
full-batch based methods in the first age, online methods
in the second age, stochastic methods in the third age, and
deep learning methods in the recent age. The first three
*Equal contribution 1Department of Computer Science, Univer-
sity of Iowa, Iowa City, Iowa, USA 2Department of Electrical and
Computer Engineering, University of Iowa, Iowa City, Iowa, USA.
Correspondence to: Tianbao Yang <tianbao-yang@uiowa.edu>.
Proceedings of the 39 th International Conference on Machine
Learning, Baltimore, Maryland, USA, PMLR 162, 2022. Copy-
right 2022 by the author(s).
ages focus on learning linear models or kernelized mod-
els. In each age, there have been seminal works in rigorous
optimization algorithms that play important roles in the evo-
lution of AUC maximization methods. Recent advances in
non-convex optimization (in particular non-convex min-max
optimization) (Liu et al., 2020) has driven large-scale deep
AUC maximization to succeed in real-world tasks, e.g., med-
ical image classification (Yuan et al., 2020) and molecular
properties prediction (Wang et al., 2021).
Nevertheless, the research on efficient optimization algo-
rithms for partial AUC (pAUC) lag behind. In many ap-
plications, there are large monetary costs due to high false
positive rates (FPR) and low true positive rates (TPR), e.g.,
in medical diagnosis. Hence, a measure of primary interest
is the region of the curve corresponding to low FPR and/or
high TPR, i.e., pAUC. There are two commonly used ver-
sions of pAUC, namely one-way pAUC (OPAUC) (Dodd
& Pepe, 2003) and two-way pAUC (TPAUC) (Yang et al.,
2019), where OPAUC puts a restriction on the range of FPR,
i.e., FPR∈ [α, β] (Figure 1 middle) and TPAUC puts a re-
striction on the lower bound of TPR and the upper bound
of FPR, i.e., TPR≥ α, FPR≤ β (Figure 1 right). Compared
with standard AUC maximization, pAUC maximization is
more challenging since its estimator based on training exam-
ples involves selection of examples whose prediction scores
are in certain ranks.
To the best of our knowledge, there are few rigorous and
efficient algorithms developed for pAUC maximization for
deep learning. Some earlier works have focused on pAUC
maximization for learning linear models. For example,
Narasimhan & Agarwal (2017) have proposed a structured
SVM approach for one-way pAUC maximization, which
is guaranteed to converge for optimizing the surrogate ob-
jective of pAUC. However, their approach is not efficient
for big data and is not applicable to deep learning, which
needs to evaluate the prediction scores of all examples and
sort them at each iteration. There are some heuristic ap-
proaches, e.g., updating the model parameters according
to the gradient of surrogate pAUC computed based on a
mini-batch data (Kar et al., 2014) or using an ad-hoc weight-
ing function for each example for computing the stochastic
gradient (Yang et al., 2021). However, such approaches are
arXiv:2203.00176v5  [cs.LG]  18 Sep 2023
=== página 2 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Figure 1. From left to right: AUC, one-way pAUC, two-way pAUC
either not guaranteed to converge or could suffer a large
approximation error.
In this paper, we propose more systematic and rigorous
optimization algorithms for pAUC maximization with con-
vergence guarantee, which are applicable to deep learning.
We consider both OPAUC maximization and TPAUC maxi-
mization, where for OPAUC we focus on maximizing pAUC
in the region where FPR ∈ [0, β] and for TPAUC we focus
on maximizing pAUC in the region where FPR ≤ β and
TPR ≥ α for some α, β∈ (0, 1). In order to tackle the
challenge of computing unbiased stochastic gradients of the
surrogate objective of pAUC, we propose new formulations
based on distributionally robust optimization (DRO), which
allows us to formulate the problem into weakly convex opti-
mization, and novel compositional optimization problems,
and to develop efficient stochastic algorithms with conver-
gence guarantee. We summarize our contributions below.
• For OPAUC maximization, for each positive example,
we define a loss over all negative examples based on
DRO. We consider two special formulations of DRO,
with one based on the conditional-value-at-risk (CVaR)
function that yields an exact estimator of the surrogate
objective of OPAUC, and another one based on Kull-
back–Leibler (KL) divergence regularized DRO that
yields a soft estimator of the surrogate objective.
• We propose efficient stochastic algorithms for optimiz-
ing both formulations of OPAUC and establish their
convergence guarantee and complexities for finding a
(nearly) stationary solution. We also demonstrate that
the algorithm for optimizing the soft estimator based on
the KL divergence regularized DRO can enjoy parallel
speed-up.
• For TPAUC maximization, we apply another level of
DRO with respect to the positive examples on top of
OPAUC formulations, yielding both exact and soft
estimators for TPAUC. We also provide two rigorous
stochastic algorithms with provable convergence for
optimizing both the exact and soft estimator of TPAUC,
with the latter problem formulated as a novel three-
level compositional stochastic optimization problem.
• We conduct extensive experiments for deep learning on
image classification and graph classification tasks with
imbalanced data. We compare with heuristic and ad-
hoc approaches for pAUC maximization and multiple
baseline methods, and observe superior performance
of the proposed algorithms.
To the best our knowledge, this work is the first one that
provides rigorous stochastic algorithms and convergence
guarantee for pAUC maximization that are efficient and ap-
plicable to deep learning. We expect the proposed novel
formulations for OPAUC and TPAUC will allow researchers
to develop even faster algorithms than the proposed algo-
rithms in this paper.
2. Related Work
In this section, we provide a brief overview of related work
for pAUC maximization.
Earlier works have considered indirect methods for pAUC
maximization (Rudin, 2009; Agarwal, 2011; Rakotoma-
monjy, 2012; Li et al., 2014; Wu et al., 2008). They did
not directly optimize the surrogate objective of pAUC but
instead some objectives that have some relationship to the
right corner of ROC curve, e.g., p-norm push (Rudin, 2009),
infinite-push (Agarwal, 2011; Rakotomamonjy, 2012; Li
et al., 2014), and asymmetric SVM objective (Wu et al.,
2008). Nevertheless, none of these studies propose algo-
rithms that are scalable and applicable for deep learning.
In (Kar et al., 2014), the authors proposed mini-batch based
stochastic methods for pAUC maximization. At each iter-
ation, a gradient estimator is simply computed based on
the pAUC surrogate function of the mini-batch data. How-
ever, this heuristic approach is not guaranteed to converge
for minimizing the pAUC objective and its error scales as
O(1/
√
B), where B is the mini-batch size. Narasimhan
& Agarwal (2013b;a; 2017) developed rigorous algorithms
for optimizing pAUC with FPR restricted in a range (α, β)
based on the structured SVM formulation. However, their
algorithms are only applicable to learning linear models
and are not efficient for big data due to per-iteration costs
proportional to the size of training data. Recently, Yang et al.
(2021) considered optimizing two-way partial AUC with
FPR less than β and TPR larger than α. Their paper focuses
on simplifying the optimization problem that involves se-
lection of top ranked negative examples and bottom ranked
positive examples. They use ad-hoc weight functions for
each positive and negative examples to relax the objective
function into decomposable over pairs. The weight function
is designed such that the larger the scores of negative exam-
ples the higher are their weights, the smaller the scores of
positive examples the higher are their weights. Nevertheless,
their objective function might have a large approximation
error for the pAUC estimator.
=== página 3 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
There are also some studies about partial AUC maximization
without providing rigorous convergence guarantee on their
methods, including greedy methods (Wang & Chang, 2011;
Ricamato & Tortorella, 2011) and boosting methods (Ko-
mori & Eguchi, 2010; Takenouchi et al., 2012). Some works
also use pAUC maximization for learning non-linear neural
networks (Ueda & Fujino, 2018; Iwata et al., 2020). How-
ever, it is unclear how the optimization algorithms were
designed as there were no discussion on the algorithm de-
sign and convergence analysis. Finally, it was brought to our
attention that a recent work (Yao et al., 2022) also consid-
ered partial AUC maximization with a non-convex objective.
The difference between this work and (Yao et al., 2022) is
that: (i) they focus on optimizing one-way pAUC with FPR
in a certain range (α, β) where α >0; in contrast we con-
sider optimizing both one-way pAUC and two-way pAUC,
but for one-way pAUC we only consider FPR in a range of
(0, β); (ii) the second difference is that the proposed algo-
rithms in this paper for one-way pAUC maximization has a
better complexity than that established in (Yao et al., 2022).
3. Preliminaries
In this section, we present some notations and preliminaries.
Let S = {(x1, y1), . . . ,(xn, yn)} denote a set of training
data, where xi represents an input training example (e.g.,
an image), and yi ∈ {1, −1} denotes its corresponding
label (e.g., the indicator of a certain disease). Let hw(x) =
h(w, x) denote the score function of the neural network
on an input data x, where w ∈ Rd denotes the parameters
of the network. Denote by I(·) an indicator function of a
predicate, and by [s]+ = max( s, 0). For a set of given
training examples S, let S+ and S− be the subsets of S
with only positive and negative examples, respectively, with
n+ = |S+| and n− = |S−|. Let S ↓[k1, k2] ⊂ Sbe the
subset of examples whose rank in terms of their prediction
scores in the descending order are in the range of [k1, k2],
where k1 ≤ k2. Similarly, let S ↑[k1, k2] ⊂ Sdenote the
subset of examples whose rank in terms of their prediction
scores in the ascending order are in the range of [k1, k2],
where k1 ≤ k2. We denote by Ex∼S the average over
x ∈ S. Let x+ ∼ P+ denote a random positive example
and x− ∼ P− denote a random negative example. We use
∆ to denote a simplex of a proper dimension.
A function F (w) is weakly convex if there exists C > 0
such that F (w) + C
2 ∥w∥2 is a convex function. A function
F (w) is L-smooth if its gradient is Lipchitz continuous, i.e.,
∥∇F (w) − ∇F (w′)∥ ≤L∥w − w′∥.
pAUC and its non-parametric estimator . For a given
threshold t and a score function h(·), the TPR can be writ-
ten as TPR(t) = Pr(h(x) ≥ t|y = 1), and the FPR can be
written as FPR(t) = Pr( h(x) > t|y = −1). For a given
u ∈ [0, 1], let FPR−1(u) = inf {t ∈ R : FPR(t) ≤ u}
and TPR−1(u) = inf {t ∈ R : TPR(t) ≤ u}. The
ROC curve defined as {u, ROC(u)}, where u ∈ [0, 1] and
ROC(u) = TPR(FPR−1(u)). OPAUC (non-normalized)
with FRP restricted in the range (α0, α1) is equal to (Dodd
& Pepe, 2003)
OPAUC(h, α0, α1) =
Z α1
α0
ROC(u)du = (1)
Pr(h(x+) > h(x−), h(x−) ∈ [FPR−1(α1), FPR−1(α0)]),
where h(x−) ∈ [FPR−1(α1), FPR−1(α0)] means that only
negative examples whose prediction scores are in certain
quantiles are considered. As a result, we have the following
non-parametric estimator of OPAUC:
\OPAUC(h, α0, α1) = (2)
1
n+
1
n−
X
xi∈S+
X
xj ∈S ↓
−[k1+1,k2]
I(h(xi) > h(xj)),
where k1 = ⌈n−α0⌉, k2 = ⌊n−α1⌋. In this work, we will
focus on optimizing \OPAUC(h, 0, β) for some β ∈ (0, 1).
Similarly, a non-parametric estimator of TPAUC with
FPR ≤ β, TPR ≥ α is given by
\TPAUC(h, α, β) = (3)
1
n+
1
n−
X
xi∈S ↑
+[1,k1]
X
xj ∈S ↓
−[1,k2]
I(h(xi) > h(xj)),
where k1 = ⌊n+α⌋, k2 = ⌊n−β⌋.
Distributionally Robust Optimization (DRO). For a set
of random loss functions ℓ1(·), . . . , ℓn(·), a DRO loss can
be written as
ˆLϕ(·) = max
p∈∆
X
j
pjℓj(·) − λDϕ(p, 1/n), (4)
where Dϕ(p, 1/n) = 1
n
P
i ϕ(npi) is a divergence measure,
and λ >0 is a parameter. The idea of the DRO loss is to as-
sign an importance weightpi to each individual loss and take
the uncertainty into account by maximization over p ∈ ∆
with a proper constraint/regularization onp. In the literature,
several divergence measures have been considered (Levy
et al., 2020). In this paper, we will consider two special
divergence measures that are of most interest for our pur-
pose, i.e., the KL divergence ϕkl(t) = t log t − t + 1, which
gives Dϕ(p, 1/n) = P
i pi log(npi), and the CVaR diver-
gence ϕc(t) = I(0 < t≤ 1/γ) with a parameter γ ∈ (0, 1),
which gives Dϕ(p, 1/n) = 0 if pi ≤ 1/(nγ) and infinity
otherwise. The following lemma gives the closed form of
ˆLϕ for ϕc and ϕkl.
=== página 4 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Lemma 1. By using KL divergence measure, we have
ˆLkl(·; λ) = λ log
 
1
n
nX
i=1
exp
 ℓi(·)
λ
!
. (5)
By using the CVaR divergence ϕc(t) for some γ such that
nγ is an integer, we have,
ˆLcvar(·; γ) = 1
nγ
nγX
i=1
ℓ[i](·), (6)
where ℓ[i](·) denotes the i-th largest value in {ℓ1, . . . , ℓn}.
The estimator in (6) is also known as the estimator of
conditional-value-at-risk (Rockafellar et al., 2000).
4. AUC meets DRO for OPAUC Maximization
Since the non-parametric estimator of OPAUC in (2) is non-
continuous and non-differentiable, a continuous surrogate
objective for OPAUC(hw, 0, β) is usually defined by us-
ing a continuous pairwise surrogate loss L(w; xi, xj) =
ℓ(hw(xi) − hw(xj)), resulting in the following problem:
min
w
1
n+
X
xi∈S+
1
n−β
X
xj ∈S ↓
−[1,n−β]
L(w; xi, xj), (7)
where we assume n−β is an positive integer for simplicity
of presentation. For the surrogate loss ℓ(·), we assume it
satisfies the following properties.
Assumption 1. We assume ℓ(·) is a convex, differentiable
and monotonically decreasing function when ℓ(·) > 0, and
ℓ′(0) < 0.
It is notable that the above condition is a sufficient con-
dition to ensure that the surrogate ℓ(·) is consistent for
AUC maximization (Gao & Zhou, 2015). There are many
surrogate loss functions that have the above properties,
e.g., squared hinge loss ℓ(s) = ( c − s)2
+, logistic loss
ℓ(s) = log(1 + exp(−s/c)) where c >0 is a parameter.
The challenge of optimizing a surrogate objective of pAUC
in (7) lies at tackling the selection of top ranked negative
examples from S−, i.e., S ↓
−[1, k] for some fixed k. It is
impossible to compute an unbiased stochastic gradient of
the objective in (7) based on a mini-batch of examples that
include only a part of negative examples.
4.1. AUC meets DRO for OPAUC
To address the above challenge, we define new formula-
tions for OPAUC maximization by leveraging the DRO. In
particular, we define a robust loss for each positive data by
ˆLϕ(w; xi) = max
p∈∆
X
xj ∈S−
pjL(w; xi, xj) − λDϕ(p, 1/n−).
Then we define the following objective for OPAUC maxi-
mization:
min
w
1
n+
X
xi∈S+
ˆLϕ(w; xi). (8)
When ϕ(·) = ϕc(·), we refer to the above estimator (i.e.,
the objective function) as CVaR-based OPAUC estimator;
and when ϕ(·) = ϕkl(·), we refer to the above estimator
as KLDRO-based OPAUC estimator. Below, we present
two theorems to state the equivalent form of the objective,
and the relationship between the two estimators and the
surrogate objective in (7) of OPAUC.
Theorem 1. By choosing ϕ(·) = ϕc(·) = I(· ∈(0, 1/β]),
then the problem (8) is equivalent to
min
w
min
s∈Rn+
F (w, s) = 1
n+
X
xi∈S+

si + 1
β ψi(w, si)

, (9)
where ψi(w, si) = 1
n−
P
xj ∈S− (L(w; xi, xj) − si)+. If ℓ
is a monotonically decreasing function for ℓ(·) > 0, then
the objective in (8) is equivalent to (7) of OPAUC.
Remark: The above theorem indicates that CVaR-based
OPAUC estimator is an exact estimator of OPAUC, which is
consistent for OPAUC maximization. The variablesi can be
considered as the threshold variable to select the top-ranked
negative examples for each positive data.
Theorem 2. By choosing ϕ(·) = ϕkl(·), then the prob-
lem (8) becomes
min
w
1
n+
X
xi∼S+
λ log Exj ∈S− exp( L(w; xi, xj)
λ ). (10)
If ℓ(·) is a monotonically decreasing function for ℓ(·) >
0, when λ = 0 , the above objective is a surrogate of
\OPAUC(hw, 0, 1
n−
); and when λ = + ∞, the above ob-
jective is a surrogate of \OPAUC(hw, 0, 1), i.e., the AUC.
Remark: Theorem 2 indicates that KLDRO-based OPAUC
estimator is a soft estimator, which interpolates between
OPAUC(hw, 0, 1/n−) and OPAUC(hw, 0, 1) by varying λ.
It is also notable that when β = 1/n− in CVaR-based es-
timator, the objective in (8) becomes the infinite-push (or
top-push) objective considered in the literature (Agarwal,
2011; Rakotomamonjy, 2012; Li et al., 2014), and hence
our algorithm for solving (9) can be also used for solving
the infinite-push objective for deep learning. In contrast,
the previous works for the infinite-push objective focus on
learning linear models. Similarly, when λ = 0 in KLDRO-
based estimator, the objective in (10) becomes the infinite-
push objective. Nevertheless, our algorithm for optimizing
KLDRO-based estimator is not exactly applicable to opti-
mizing the infinite-push objective as we focus on the cases
λ > 0, which yields a smooth objective function under
proper conditions of ℓ(·) and h(·; x). As a result, we could
=== página 5 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
have stronger convergence by optimizing the KLDRO-based
estimator as indicated by our convergence results in next
subsection.
4.2. Optimization Algorithms and Convergence Results
In this subsection, we present the optimization algorithms
for solving both (9) and (10), and then present their conver-
gence results for finding a nearly stationary solution. The
key to our development is to formulate the two optimization
problems into known non-convex optimization problems
that have been studied in the literature, and then to develop
stochastic algorithms by borrowing the existing techniques.
Optimizing CVaR-based estimator .We first consider opti-
mizing the CVaR-based estimator, which is equivalent to (9).
A benefit for solving (9) is that an unbiased stochastic sub-
gradient can be computed in terms of (w, s). However, this
problem is still challenging because the objective function
F (w, s) is non-smooth non-convex. In order to develop a
stochastic algorithm with convergence guarantee, we prove
that F (w, s) is weakly convex in terms of (w, s), which
allows us to borrow the techniques of optimizing weakly
convex function (Davis & Drusvyatskiy, 2018) for solv-
ing our problem and to establish the convergence. We first
establish the weak convexity of F (w, s).
Lemma 2. If L(·; xi, xj) is a Ls-smooth function for any
xi, xj, then F (w, s) is ρ-weakly convex with ρ = Ls/β.
Another challenge for optimizingF (w, s) is that s is of high
dimensionality and computing the gradient for all entries
in s at each iteration is expensive. Therefore, we develop a
tailored stochastic algorithm for solving (9), which is shown
in Algorithm 1. This algorithm uses stochastic gradient
descent (SGD) updates for updating w and stochastic coor-
dinate gradient descent (SCGD) updates for updating s. We
refer to the algorithm as SOPA. A key feature of SOPA is
that the stochastic gradient estimator for w is a weighted
average gradient of the pairwise losses for all pairs in the
mini-batch, i.e., step 6. The hard weights pij (either 0 or 1)
are dynamically computed by step 4, which compares the
pairwise loss (ℓ(h(wt, xi) − h(wt, xj)) with the threshold
variable st
i, which is also updated by a SGD step.
Optimizing KLDRO-based estimator of OPAUC. Next,
we consider optimizing the KLDRO-based estimator, which
is equivalent to (10). A nice property of the objective func-
tion is that it is smooth under a proper condition as stated in
Assumption 2. However, the challenge for solving (10) is
that an unbiased stochastic gradient is not readily computed.
To highlight the issue, the problem (10) can be written as
min
w
F (w) = 1
n+
X
xi∈S+
f (gi(w)), (11)
where gi(w) = E xj ∼S− exp( L(w;xi,xj )
λ ) and f (·) =
λ log(·). A similar optimization problem has been studied
Algorithm 1 SOPA
1: Set s1 = 0 and initialize w
2: for t = 1, . . . , Tdo
3: Sample two mini-batches B+ ⊂ S+, B− ⊂ S−
4: Let pij = I(ℓ(h(wt, xi) − h(wt, xj)) − st
i > 0)
5: Update st+1
i = st
i − η2
n+
(1 −
P
j pij
β|B−| ) for xi ∈ B+
6: Compute a gradient estimator ∇t by
∇t = 1
β|B+||B−|
X
xi∈B+
X
xj ∈B−
pij∇wL(wt; xi, xj)
7: Update wt+1 = wt − η1∇t
8: end for
in (Qi et al., 2021) for maximizing average precision, which
is referred to as finite-sum coupled compositional stochastic
optimization, where f (gi(w)) is a compositional function
and gi(w) depends on the index i for the outer summation.
A full gradient of f (gi(w)) is given by f ′(gi(w))∇gi(w).
With a mini-batch of samples, gi(w) can be estimated by an
unbiased estimator ˆgi(w). However, f ′(ˆgi(w))∇ˆgi(w) is a
biased estimator due to the compositional form. To address
this challenge, Qi et al. (2021) proposed a novel stochas-
tic algorithm that maintains a moving average estimator
for gi(w) denoted by ui. Recently, Wang & Yang (2022)
has also studied the finite-sum coupled compositional opti-
mization problem comprehensively and proposed a similar
algorithm (SOX) and derived better convergence results than
that in (Qi et al., 2021). Hence, we employ the same algo-
rithm in (Wang & Yang, 2022) for solving (10), which is in
shown in Algorithm 2 and is referred to as SOPA-s.
There are two key differences between SOPA-s and SOPA.
First, the pairwise weights pij in SOPA-s (step 5) are soft
weights between 0 and 1, in contrast to the hard weights
pij ∈ {0, 1} in SOPA. Second, the update for wt+1 is a
momentum-based update where γ1 ∈ (0, 1). We can also
use an Adam-style update, which shares similar convergence
as the momentum-based update (Guo et al., 2021).
4.3. Convergence Analysis
For convergence analysis, we make the following assump-
tion about h and ℓ(·).
Assumption 2. Assume h(·; x) is Lipschitz continuous,
smooth and bounded, ℓ(·) is a smooth function and has
a bounded gradient for a bounded argument.
A bounded smooth score function h(·; x) is ensured if the
activation function of the neural network is smooth and the
output layer uses a bounded and smooth activation func-
tion. For example, let ˆh(w; x) denote the plain output
of the neural network, then the score function h(w; x) =
=== página 6 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Algorithm 2 SOPA-s
1: Set u1 = 0 and initialize w
2: for t = 1, . . . , Tdo
3: Sample two mini-batches B+ ⊂ S+, B− ⊂ S−
4: For each xi ∈ B+, update ut+1
i = (1 − γ0)ut
i +
γ0 1
|B−|
P
xj ∈B− exp

L(wt;xi,xj )
λ

5: Let pij = exp(L(wt; xi, xj)/λ)/ut
i
6: Compute a gradient estimator ∇t by
∇t = 1
|B+|
1
|B−|
X
xi∈B+
X
xj ∈B−
pij∇L(wt; xi, xj)
7: Update vt = (1 − γ1)vt−1 + γ1∇t
8: Update wt+1 = wt − ηvt (or Adam-style)
9: end for
1/(1 + exp(−ˆh(w; x)) is bounded and smooth. The Lip-
schitz continuity of h(w; x) can be guaranteed if w is
bounded.
We first consider the analysis of SOPA. Since F (w, s) is
non-smooth, for presenting the convergence result, we need
to introduce a convergence measure based on the Moreau
envelope of F (w, s) given below for some ˆρ > ρ:
F ˆρ(w, s) = minw,s F (w, s) + ˆρ
2 (∥w∥2 + ∥s∥2).
It is guaranteed that F ˆρ(w, s) is a smooth function (Drusvy-
atskiy & Paquette, 2019). A point (w, s) is called an ϵ-
nearly stationary solution to F (w, s) if ∥∇F ˆρ(w, s)∥ ≤ϵ
for some ˆρ > ρ, where ρ is the weak convexity parameter
of F . This convergence measure has been widely used for
weakly convex optimization problems (Davis & Drusvy-
atskiy, 2018; Rafique et al., 2020; Chen et al., 2019). Then
we establish the following convergence guarantee for SOPA.
Theorem 3. Under Assumption 2, Algorithm 1 ensures that
after T = O(1/(βϵ4)) iterations we can find an ϵ nearly
stationary solution of F (w, s), i.e., E∥∇F ˆρ(wτ , sτ )∥2 ≤
ϵ2 for a randomly selected τ ∈ {1, . . . , T} and ˆρ = 1.5ρ.
Next, we establish the convergence of SOPA-s. Under As-
sumption 2, we can show that F (w) in (11) is smooth.
Hence, we use the standard convergence measure in terms
of gradient norm of F (w).
Theorem 4. Under Assumption 2, Algorithm 2
with γ0 = O(B−ϵ2), γ1 = O(min{B−, B+}ϵ2),
η = O(min{γ0B1/n+, γ1}) ensures that after
T = O( 1
min(B+,B−)ϵ4 + n+
B+B−ϵ4 ) iterations we can find an
ϵ-stationary solution of F (w), i.e., E[∥∇F (wτ )∥2] ≤ ϵ2
for a randomly selected τ ∈ {1, . . . , T}, where B+ = |B+|
and B− = |B−|.
Remark: The convergence analysis of Algorithm 2 follows
directly from that in (Wang & Yang, 2022). Compared with
that in Theorem 3 for SOPA, the convergence of SOPA-s is
stronger than that of SOPA in several aspects: (i) the conver-
gence measure of SOPA-s is stronger than that of SOPA due
to that Theorem 4 guarantees the convergence in terms of
gradient norm of the objective, while Theorem 3 guarantees
the convergence on a weaker convergence measure namely
the gradient norm of the Moreau envelope of the objective;
(ii) the complexity of SOPA-s enjoys a parallel speed-up by
using a mini-batch of data. However, it is also notable that
the complexity of SOPA does not depend on the number of
positive data as that of SOPA-s.
5. AUC meets DRO for TPAUC Maximization
In this section, we propose estimators for the surrogate
objective of TPAUC and stochastic algorithms with conver-
gence guarantee for optimizing the estimators. To this end,
we apply another level of DRO on top of ˆLϕ(xi, w), xi ∈
S+ and define the following estimator of TPAUC:
F (w; ϕ, ϕ′) = max
p∈∆
X
xi∈S+
pi ˆLϕ(xi, w) − λ′Dϕ′(p, 1
n+
).
Next, we focus on optimizing the soft estimator of TPAUC
defined by using ϕ = ϕ′ = ϕkl. First, we have the following
form for the estimator.
Lemma 3. When ϕ = ϕ′ = ϕkl, we have
F (w; ϕkl, ϕkl)
= λ′ log Exi∼S+

Exj ∼S− exp( ℓ(w; xi, xj)
λ )
 λ
λ′
.
For minimizing this function, we formulate the problem as
a novel three-level compositional stochastic optimization:
min
w
f1( 1
n+
X
xi∈S+
f2(gi(w))),
where f1(s) = λ′ log(s), f2(g) = gλ/λ′
and gi(w) =
Exj ∼S− exp(L(w; xi, xj)/λ). We propose a novel stochas-
tic algorithm for solving the above problem, which is
shown in Algorithm 3, to which we refer as SOTA-
s. Note that the problem is similar to multi-level com-
positional optimization (Balasubramanian et al., 2021)
but also has subtle difference. The function inside f1
has a form similar to that in (11). Hence, we use
similar technique to SOPA-s by maintaining and updat-
ing ui to track gi(w) in step 4. Besides, we need to
maintain and update vt+1 to track 1
n+
P
xi∈S+ f2(gi(wt))
in step 5. Then the gradient estimator in step 7 is
computed by ∇f1(vt+1) 1
|B+|
P
xi∈B+ ∇ˆgi(wt)∇f2(ui
t),
where ˆgi(w) = E xj ∼B− exp(L(wt; xi, xj)/λ). Then we
update the model parameter by the momentum-style or
Adam-style update.
Theorem 5. Under Assumption 2, Algorithm 3 with γ0 =
=== página 7 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Algorithm 3 SOTA-s
1: Set u0 = 0, v0 = 0, m0 = 0 and initialize w
2: for t = 1, . . . , Tdo
3: Sample two mini-batches B+ ⊂ S+, B− ⊂ S−
4: For each xi ∈ B+ compute ui
t = (1 − γ0)ui
t−1 +
γ0 1
|B−|
P
xj ∈B− L(wt; xi, xj)
5: Let vt = (1 − γ1)vt−1 + γ1 1
|B+|
P
xi∈B+ f2(ui
t−1)
6: Let pij = (ui
t−1)λ/λ′−1 exp(L(wt, xi, xj)/λ)/vt
7: Compute a gradient estimator ∇t by
∇t = 1
|B+
1
|B−|
X
xi∈B+
X
xj ∈B−
pij∇L(wt; xi, xj)
8: Update mt = (1 − γ2)mt−1 + γ2∇t
9: Update wt+1 = wt − ηmt (or Adam-style)
10: end for
O(B−ϵ2), γ1 = O(B+ϵ2), γ2 = O(min{B−, B+}ϵ2),
η = O(min{γ0B1/n+, γ1, γ2}) ensures that after T =
O( 1
min(B+,B−)ϵ4 + n+
B+B−ϵ4 ) iterations we can find an ϵ
nearly stationary solution of F (w), where B+ = |B+| and
B− = |B−|.
Remark: It is notable that SOTA-s has an iteration complex-
ity in the same order of SOPA-s for OPAUC maximization.
Finally, we discuss how to optimize the exact estimator of
TPAUC defined byF (w; ϕc, ϕ′
c), where ϕc(t) = I(0 ≤ t ≤
1/β) and ϕ′
c(t) = I(0 ≤ t ≤ 1/α) with K2 = n−β and
K1 = n+α being integers. Lemma 7 in the supplement
shows that if ℓ(·) is monotonically decreasing for ℓ(·) > 0
F (w; ϕc,ϕ′
c) =
1
K1K2
X
xi∈S ↑
+[1,K1]
X
xj ∈S ↓
−[1,K2]
L(w; xi, xj),
is a consistent surrogate function of TPAUC forTPR ≥ α
and FPR ≤ β in view of the estimator \TPAUC given in (3).
Similar to Theorem 1, we can show that F (w; ϕc, ϕ′
c) is
equivalent to:
min
s′∈R,s∈Rn+
s′ + 1
n+α
X
xi∈S+
(si + 1
β ψi(w; si) − s′)+.
Like F (w, s) in (9), we can prove the inner function is
weakly convex in terms of (w, s, s′). However, computing
an unbiased stochastic gradient in terms of w and si is also
impossible due to that ψi(w; si) is inside a hinge function.
To solve this problem, we can use the conjugate form of the
hinge function to convert the minimization of F (w; ϕc, ϕ′
c)
into a weakly-convex concave min-max problem (Rafique
et al., 2020) and we can develop a stochastic algorithm but
only with O(1/ϵ6) iteration complexity for finding a nearly
stationary solution. We present the algorithm and analysis
in the supplement for interested readers.
6. Experiments
Datasets. We consider binary classification tasks on two
types of datasets, namely image datasets and molecular
datasets. For image datasets, we use CIFAR-10, CIFAR-
100, Melanoma for experiments. For CIFAR-10 and CIFAR-
100 (Krizhevsky et al., 2009), we construct imbalanced
versions of the datasets by randomly removing some pos-
itive samples following (Yuan et al., 2020). Specifically,
we take first half of classes as the negative class and last
half of classes as the positive class, and then remove 80%
samples from the positive class to make it imbalanced. The
Melanoma dataset is a naturally imbalanced medical dataset
which is released on Kaggle (Rotemberg et al., 2021). For
molecular datasets, we use ogbg-moltox21 (the No.0 tar-
get), ogbg-molmuv (the No.1 target) and ogbg-molpbca (the
No.0 target) for experiments, which are from the Stanford
Open Graph Benchmark (OGB) website (Hu et al., 2020).
The task on these molecular datasets is to predict certain
property of molecules. The statistics for the datasets are
presented in Table 5 in the supplement.
Deep Models. For image datasets, we learn convolutional
neural network (CNN) and use ResNet18 (He et al., 2016)
for CIFAR-10, CIFAR100 and Melanoma. For molecular
datasets, we learn graph neural network (GNN) and use
Graph Isomorphism Network (GIN) as the backbone model
on all datasets (Xu et al., 2018), which has 5 mean-pooling
layers with 64 number of hidden units and dropout rate 0.5.
Baselines. We will compare our methods with different
baselines for both training performance and testing perfor-
mance. For comparison of training convergence, we con-
sider different methods for optimizing the same objective,
i.e., partial AUC. We compare with 2 baselines, i.e., the
naive mini-batch based method (Kar et al., 2014), to which
we refer as MB, and a recently proposed ad-hoc weight
based method (Yang et al., 2021), to which we refer as AW-
poly. MB that optimizes OPAUC only considers the top
negative samples in the mini-batch; and MB that optimizes
TPAUC considers the top negative samples and bottom pos-
itive samples in the mini-batch. For AW-poly, we use the
polynomial weight function according to their paper. It is
notable that AW-poly was originally proposed for optimiz-
ing TPAUC. But it can be easily modified for optimizing
OPAUC with FPR in (0, β). For comparison of testing per-
formance, we compare different methods for optimizing
different objectives, including the cross-entropy loss (CE),
the pair-wise squared hinge loss for AUC maximization
(AUC-SH), the AUC min-max margin loss (AUC-M) (Yuan
et al., 2021), p-norm push (P-push) (Rudin, 2009). For
optimizing CE and AUC-SH, we use the standard Adam
optimizer. For optimizing AUC-M, we use their proposed
=== página 8 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
0 10 20 30 40 50 60
Epochs
0.86
0.88
0.90
0.92
0.94
0.96
0.98
1.00pAUC
CIFAR-10(FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95
1.00pAUC
CIFAR-100(FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.80
0.82
0.84
0.86
0.88
0.90
0.92
0.94pAUC
moltox21-t0 (FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.68
0.70
0.72
0.74
0.76
0.78pAUC
molpcba-t0 (FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.4
0.5
0.6
0.7
0.8
0.9
1.0pAUC
CIFAR-10(TPR 0.6,FPR 0.4)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.0
0.2
0.4
0.6
0.8
1.0pAUC
CIFAR-100(TPR 0.6,FPR 0.4)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9pAUC
moltox21-t0 (TPR 0.6, FPR 0.4)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.10
0.15
0.20
0.25
0.30
0.35
0.40pAUC
molpcba-t0 (TPR 0.6, FPR 0.4)
SOTA-s
AW-poly
MB
Figure 2. Training Convergence Curves on image and molecular datasets; Top for OPAUC maximization, bottom for TPAUC maximization.
optimizer PESG. For P-push, we use a stochastic algorithm
with an Adam-style update similar to that proposed in (Qi
et al., 2021). For our methods, we use ℓ(t) = (1 − t)2
+ and
also use the Adam-style update unless specified explicitly.
Similar to (Yuan et al., 2021; Qi et al., 2021), we use a pre-
training step that optimizes the base model by optimizing
CE loss with an Adam optimizer, and then re-initialize the
classifier layer and fine-tune all layers by different methods.
Target Measures. For OPAUC maximization, we evaluate
OPAUC with two FPR upper bounds, i.e., FPR ≤ 0.3 and
FPR≤ 0.5 separately. For TPAUC maximization, we evalu-
ate TPAUC with two settings, i.e, FPR≤ 0.4 and TPR≥ 0.6,
and FPR≤ 0.5 and TPR≥ 0.5.
Parameter Tuning. The learning rate of all methods is
tuned in {1e-3, 1e-4, 1e-5}, except for PESG which is tuned
at {1e-1, 1e-2, 1e-3 } because it favors a larger learning
rate. Weight decay is fixed as 2e-4. Each method is run 60
epochs in total and learning rate decays 10-fold after every
20 epochs. The mini-batch size is 64. For AUC-M, we
tune the hyperparameter γ that controls consecutive epoch-
regularization in {100, 500, 1000}. For P-push, we tune the
polynomial power hyper-parameter in{2, 4, 6}. For MB that
optimizes OPAUC, we tune the top proportion of negative
samples in {10%, 30%, 50%}, and for MB that optimizes
TPAUC we tune the top proportion of negative samples in
{30%, 40%, 50%}, and tune the bottom proportion of posi-
tive samples in the range {30%, 40%, 50%}. For AW-poly,
we follow (Yang et al., 2021) and tune its parameter γ in
{101, 34, 11}. For SOPA, we tune the truncated FPR i.e. β
in {0.1, 0.3, 0.5}. For SOPA-s, we fix γ0 = 0.9 and tune
the KL-regularization parameter λ in {0.1, 1.0, 10}, and for
SOTA-s, we fix γ0 = γ1 = 0.9, and tune both λ and λ′ in
{0.1, 1.0, 10}. The momentum parameter for updating vt in
SOPA-s (i.e., 1 − γ1) and SOTA-s (i.e., 1 − γ2) is set to the
default value as in the Adam optimizer, i.e., 0.1. For com-
parison of training convergence, the parameters are tuned
according to the training performance. For comparison of
testing performance, the parameters are tuned according to
the validation performance. For each experiment, we repeat
multiple times with different train/validation splits and ran-
dom seeds, then report average and standard deviation over
multiple runs.
Results. We show the plots of training convergence in Fig-
ure 2 on two image datasets (CIFAR-10, -100) and on two
molecular datasets (moltox21, molpcba). From the results,
we can see that SOPA-s (SOTA-s) converge always faster
than MB and AW-poly for OPAUC (TPAUC) maximization.
For OPAUC maximization, SOPA-s is usually faster than
SOPA. More results are included in the supplement on other
datasets with similar observations. The testing performance
on all six datasets are shown in Table 1, 2, 3 and 4. In most
cases, the proposed methods are better than the baselines.
In particular, dramatic improvements have been observed
on Melanoma and ogbg-molmuv datasets, which are two
datasets with the highest imbalance ratios. In addition, we
see that AUC maximization methods (AUC-M, AUC-SH)
are not necessarily good for pAUC maximization.
Accuracy of KLDRO-based estimator . Of independent
interest, we conduct simple experiments to verify the accu-
racy of KLDRO-based estimator of OPAUC. To this end,
we compute the relative error (RE) of KLDRO-based esti-
mator compared with the exact estimator (i.e., CVaR-based
estimator). For a given upper bound of FRP we vary λ
for 100 independently randomly generated model parame-
ters w, and the results are shown in the following figure on
moltox21-t0 data (please refer to the experiments section for
more information of the dataset), which demonstrates that
for a given FPR there exists λ such that KLDRO estimator
is close to the exact estimator.
Ablation Study. We also conduct some ablation study to
understand the proposed algorithm SOPA-s and SOTA-s. In
particular for both algorithms, we verify that tuning γ0 in
SOPA-s and γ0, γ1 in SOTA-s can help further improve the
performance. The results are included in the supplement.
=== página 9 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Table 1. One way partial AUC on testing data of three image datasets
CIFAR-10 CIFAR-100 Melanoma
Methods FPR≤0.3 FPR ≤0.5 FPR≤0.3 FPR ≤0.5 FPR≤0.3 FPR ≤0.5
CE 0.8446(0.0018) 0.8777(0.0014)0.7338(0.0047) 0.7787(0.0044)0.7651(0.0135) 0.8151(0.0028)
AUC-SH 0.8657(0.0056) 0.8948(0.0036)0.7467(0.0047) 0.7930(0.0027)0.7824(0.0138) 0.8176(0.0160)
AUC-M 0.8678(0.0016) 0.8934(0.0022)0.7371(0.0031) 0.7828(0.0005)0.7788(0.0068) 0.8249(0.0141)
P-push 0.8610(0.0007) 0.8889(0.0021)0.7445(0.0025) 0.7930(0.0029)0.7440(0.0130) 0.8028(0.0170)
MB 0.8690(0.0016) 0.8931(0.0015)0.7487(0.0017) 0.7930(0.0014)0.7683(0.0303) 0.8184(0.0278)
AW-poly0.8664(0.0052) 0.8915(0.0075)0.7490(0.0058) 0.7909(0.0068)0.7936(0.0238) 0.8355(0.0067)
SOPA 0.8766(0.0034) 0.9028(0.0031)0.7551(0.0044) 0.7999(0.0028)0.8093(0.0248) 0.8585(0.0210)
SOPA-s 0.8691(0.0036) 0.8961(0.0036)0.7468(0.0056) 0.7877(0.0053)0.7775(0.0076) 0.8401(0.0206)
Table 2. Two way partial AUC on testing data of three image datasets; (α,β) represents TPR≥ α and FPR ≤ β.
CIFAR-10 CIFAR-100 Melanoma
Methods (0.6,0.4) (0.5,0.5) (0.6,0.4) (0.5,0.5) (0.6,0.4) (0.5,0.5)
CE 0.4981(0.0078) 0.6414(0.0080)0.2178(0.0136) 0.4011(0.0118)0.3399(0.0135) 0.5150(0.0038)
AUC-SH 0.5622(0.0064) 0.6923(0.0071)0.2599(0.0061) 0.4397(0.0062)0.3640(0.0354) 0.5291(0.0312)
AUC-M 0.5691(0.0021) 0.6907(0.0125)0.2336(0.0041) 0.4153(0.0022)0.3665(0.0646) 0.5404(0.0545)
P-push 0.5477(0.0077) 0.6781(0.0055)0.2623(0.0042) 0.4417(0.0092)0.3317(0.0304) 0.4870(0.0443)
MB 0.5404(0.0041) 0.6724(0.0011)0.2207(0.0033) 0.4017(0.0149)0.3330(0.0258) 0.4981(0.0252)
AW-poly0.5536(0.0196) 0.6814(0.0203)0.2489(0.0166) 0.4342(0.0112)0.3878(0.0292) 0.5216(0.0288)
SOTA-s 0.5799(0.0202) 0.7074(0.0145)0.2708(0.0055) 0.4528(0.0069)0.4198(0.0825) 0.5865(0.0664)
Table 3. One way partial AUC on testing data of three molecular datasets
moltox21(t0) molmuv(t1) molpcba(t0)
Methods FPR≤0.3 FPR ≤0.5 FPR≤0.3 FPR ≤0.5 FPR≤0.3 FPR ≤0.5
CE 0.6671(0.0009) 0.6954(0.005)0.8008(0.0090) 0.8201(0.0061)0.6802(0.0002) 0.7169(0.0002)
AUC-SH 0.7161(0.0043) 0.7295(0.0036)0.7880(0.0382) 0.8025(0.0437)0.6939(0.0009) 0.7350(0.0015)
AUC-M 0.6866(0.0048) 0.7080(0.0020)0.7960(0.0123) 0.8076(0.0175)0.6985(0.0016) 0.7399(0.0005)
P-push 0.6946(0.0107) 0.7160(0.0073)0.7832(0.0220) 0.7940(0.0321)0.6841(0.0007) 0.7293(0.0043)
MB 0.7398(0.0131)0.7329(0.0099)0.7672(0.0563) 0.7772(0.0547)0.6899(0.0002) 0.7253(0.0006)
AW-poly0.7227(0.0024) 0.7271(0.0112)0.7754(0.0372) 0.7883(0.0431)0.6975(0.0006) 0.7350(0.0015)
SOPA 0.7209(0.0063) 0.7318(0.0084)0.8187(0.0319) 0.8245(0.0312)0.6989(0.0022) 0.7371(0.0011)
SOPA-s 0.7309(0.0151)0.7330(0.0073)0.8449(0.0399) 0.8412(0.0447)0.7027(0.0018) 0.7416(0.0006)
Table 4. Two way partial AUC on testing data of three molecular datasets; (α,β) represents TPR≥ α and FPR ≤ β.
moltox21(t0) molmuv(t1) molpcba(t0)
Methods (0.6,0.4) (0.5,0.5) (0.6,0.4) (0.5,0.5) (0.6,0.4) (0.5,0.5)
CE 0.0674(0.0014) 0.2082(0.0011)0.1613(0.0337) 0.4691(0.0183)0.0949(0.0006) 0.2639(0.0006)
AUC-SH 0.0640(0.0080) 0.2170(0.0140)0.2600(0.1300) 0.4440(0.1280)0.1400(0.0030) 0.3120(0.0030)
AUC-M 0.0660(0.0090) 0.2090(0.0100)0.1140(0.0790) 0.4330(0.0530)0.1420(0.0090) 0.3130(0.0030)
P-push 0.0610(0.0180) 0.2070(0.0120)0.1860(0.1520) 0.4170(0.1080)0.1350(0.0020) 0.3000(0.0120)
MB 0.0670(0.0150) 0.2150(0.0230)0.1730(0.1530) 0.4260(0.1180)0.0950(0.0020) 0.2620(0.0030)
AW-poly0.0640(0.0100) 0.2060(0.0250)0.1720(0.1440) 0.3930(0.1230)0.1100(0.0010) 0.2810(0.0020)
SOTA-s 0.0680(0.0180) 0.2300(0.0210)0.3270(0.1640) 0.5260(0.1220)0.1430(0.0010) 0.3140(0.0020)
-3 -2 -1 0 1 2 3
log( )
0.00
0.01
0.02
0.03
0.04
0.05RE of KLDRO estimator (FPR<0.3)
moltox21-t0
-3 -2 -1 0 1 2 3
log( )
0.00
0.01
0.02
0.03
0.04
0.05RE of KLDRO estimator (FPR<0.5)
moltox21-t0
Figure 3. Relative error (RE) for KLDRO-based estimator for
OPAUC on moltox21-t0 dataset with FPR={0.3, 0.5}.
7. Conclusions
In this paper, we have proposed new formulations for partial
AUC maximization by using distributionally robust opti-
mization. We propose two formulations for both one-way
and two-way partial AUC, and develop stochastic algorithms
with convergence guarantee for solving the two formula-
tions, respectively. Extensive experiments on image and
molecular graph datasets verify the effectiveness of the pro-
posed algorithms.
8. Acknowledgements
This work is partially supported by NSF Grant 2110545,
NSF Career Award 1844403, and NSF Grant 1933212. D.
Zhu and X. Wu was partially supported by NSF grant CCF-
1733742. We also thank anonymous reviewers for construc-
tive comments.
=== página 10 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
References
Agarwal, S. The infinite push: A new support vector ranking
algorithm that directly optimizes accuracy at the absolute
top of the list. In SDM, 2011.
Balasubramanian, K., Ghadimi, S., and Nguyen, A. Stochas-
tic multi-level composition optimization algorithms with
level-independent convergence rates. ArXiv e-prints ,
arXiv:2008.10526, 2021.
Chen, Z., Yuan, Z., Yi, J., Zhou, B., Chen, E., and Yang,
T. Universal stagewise learning for non-convex problems
with convergence on averaged solutions. In 7th Interna-
tional Conference on Learning Representations (ICLR),
2019.
Davis, D. and Drusvyatskiy, D. Stochastic subgradient
method converges at the rate o(k−1/4) on weakly convex
functions. CoRR, /abs/1802.02988, 2018.
Dodd, L. and Pepe, M. Partial auc estimation and regres-
sion. Biometrics, 59:614–23, 10 2003. doi: 10.1111/
1541-0420.00071.
Drusvyatskiy, D. and Paquette, C. Efficiency of minimiz-
ing compositions of convex functions and smooth maps.
Mathematical Programming, pp. 1–56, 2019.
Gao, W. and Zhou, Z.-H. On the consistency of auc pair-
wise optimization. In Proceedings of the 24th Interna-
tional Conference on Artificial Intelligence, IJCAI’15, pp.
939–945. AAAI Press, 2015. ISBN 9781577357384.
Guo, Z., Xu, Y ., Yin, W., Jin, R., and Yang, T. On stochastic
moving-average estimators for non-convex optimization.
ArXiv e-prints, arXiv:2104.14840, 2021.
He, K., Zhang, X., Ren, S., and Sun, J. Deep residual learn-
ing for image recognition. In Proceedings of the IEEE
conference on computer vision and pattern recognition,
pp. 770–778, 2016.
Herbrich, R., Graepel, T., and Obermayer, K. Large Margin
Rank Boundaries for Ordinal Regression. In Advances
in Large Margin Classifiers , chapter 7, pp. 115–132.
The MIT Press, 1999. URL http://www.herbrich.
me/papers/nips98_ordinal.pdf.
Hu, W., Fey, M., Zitnik, M., Dong, Y ., Ren, H., Liu, B.,
Catasta, M., and Leskovec, J. Open graph benchmark:
Datasets for machine learning on graphs. arXiv preprint
arXiv:2005.00687, 2020.
Iwata, T., Fujino, A., and Ueda, N. Semi-supervised learning
for maximizing the partial auc. In AAAI, 2020.
Kar, P., Narasimhan, H., and Jain, P. Online and stochas-
tic gradient methods for non-decomposable loss func-
tions. In Proceedings of the 27th International Confer-
ence on Neural Information Processing Systems - Volume
1, NIPS’14, pp. 694–702, Cambridge, MA, USA, 2014.
MIT Press.
Komori, O. and Eguchi, S. A boosting method for maximiz-
ing the partial area under the roc curve. BMC Bioinfor-
matics, 11:314 – 314, 2010.
Krizhevsky, A., Hinton, G., et al. Learning multiple layers
of features from tiny images. 2009.
Levy, D., Carmon, Y ., Duchi, J. C., and Sidford, A. Large-
scale methods for distributionally robust optimization.
Advances in Neural Information Processing Systems, 33,
2020.
Li, N., Jin, R., and Zhou, Z.-H. Top rank optimization in
linear time. In NIPS, 2014.
Liu, M., Yuan, Z., Ying, Y ., and Yang, T. Stochastic AUC
maximization with deep neural networks. In 8th Interna-
tional Conference on Learning Representations (ICLR),
2020.
Narasimhan, H. and Agarwal, S. Svmpauctight: A new
support vector method for optimizing partial auc based
on a tight convex upper bound. In Proceedings of
the 19th ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining , KDD ’13, pp.
167–175, New York, NY , USA, 2013a. Association for
Computing Machinery. ISBN 9781450321747. doi: 10.
1145/2487575.2487674. URL https://doi.org/
10.1145/2487575.2487674.
Narasimhan, H. and Agarwal, S. A structural SVM based
approach for optimizing partial auc. In Dasgupta, S. and
McAllester, D. (eds.), Proceedings of the 30th Interna-
tional Conference on Machine Learning, volume 28 of
Proceedings of Machine Learning Research , pp. 516–
524, Atlanta, Georgia, USA, 17–19 Jun 2013b. PMLR.
URL https://proceedings.mlr.press/v28/
narasimhan13.html.
Narasimhan, H. and Agarwal, S. Support vector algorithms
for optimizing the partial area under the roc curve.Neural
Computation, 29:1919–1963, 2017.
Ogryczak, W. and Tamir, A. Minimizing the sum of the
k largest functions in linear time. Information Pro-
cessing Letters, 85:117–122, 02 2003. doi: 10.1016/
S0020-0190(02)00370-8.
Qi, Q., Luo, Y ., Xu, Z., Ji, S., and Yang, T. Stochas-
tic optimization of area under precision-recall curve
=== página 11 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
for deep learning with provable convergence. In Ad-
vances in neural information processing systems, volume
abs/2104.08736, 2021. URL https://arxiv.org/
abs/2104.08736.
Rafique, H., Liu, M., Lin, Q., and Yang, T. Non-convex min-
max optimization: Provable algorithms and applications
in machine learning. Optimization Methods and Software,
2020.
Rakotomamonjy, A. Sparse support vector infinite push. In
ICML, 2012.
Ricamato, M. T. and Tortorella, F. Partial auc maximiza-
tion in a linear combination of dichotomizers. Pattern
Recognit., 44:2669–2677, 2011.
Rockafellar, R. T., Uryasev, S., et al. Optimization of condi-
tional value-at-risk. Journal of risk, 2:21–42, 2000.
Rotemberg, V ., Kurtansky, N., Betz-Stablein, B., Caffery,
L., Chousakos, E., Codella, N., Combalia, M., Dusza, S.,
Guitera, P., Gutman, D., et al. A patient-centric dataset
of images and metadata for identifying melanomas using
clinical context. Scientific data, 8(1):1–8, 2021.
Rudin, C. The p-norm push: A simple convex rank-
ing algorithm that concentrates at the top of the list.
Journal of Machine Learning Research , 10(78):2233–
2271, 2009. URL http://jmlr.org/papers/
v10/rudin09b.html.
Takenouchi, T., Komori, O., and Eguchi, S. An extension
of the receiver operating characteristic curve and auc-
optimal classification. Neural computation, 24:2789–824,
06 2012. doi: 10.1162/NECO a 00336.
Ueda, N. and Fujino, A. Partial auc maximization via non-
linear scoring functions. ArXiv, abs/1806.04838, 2018.
Wang, B. and Yang, T. Finite-sum coupled compositional
stochastic optimization: Theory and applications. In
Proceedings of the International Conference on Machine
Learning, pp. –, 2022.
Wang, Z. and Chang, Y .-C. I. Marker selection via maxi-
mizing the partial area under the roc curve of linear risk
scores. Biostatistics, 12 2:369–85, 2011.
Wang, Z., Liu, M., Luo, Y ., Xu, Z., Xie, Y ., Wang, L., Cai,
L., Qi, Q., Yuan, Z., Yang, T., and Ji, S. Advanced graph
and sequence neural networks for molecular property
prediction and drug discovery, 2021.
Wu, S.-H., Lin, K.-P., Chen, C.-M., and Chen, M.-S.
Asymmetric support vector machines: Low false-positive
learning under the user tolerance. In Proceedings of
the 14th ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining , KDD ’08, pp.
749–757, New York, NY , USA, 2008. Association for
Computing Machinery. ISBN 9781605581934. doi: 10.
1145/1401890.1401980. URL https://doi.org/
10.1145/1401890.1401980.
Xu, K., Hu, W., Leskovec, J., and Jegelka, S. How
powerful are graph neural networks? arXiv preprint
arXiv:1810.00826, 2018.
Yang, H., Lu, K., Lyu, X., and Hu, F. Two-way partial
auc and its properties. Statistical methods in medical
research, 28(1):184–195, 2019.
Yang, Z., Xu, Q., Bao, S., He, Y ., Cao, X., and Huang,
Q. When all we need is a piece of the pie: A
generic framework for optimizing two-way partial auc.
In Meila, M. and Zhang, T. (eds.), Proceedings of
the 38th International Conference on Machine Learn-
ing, volume 139 of Proceedings of Machine Learn-
ing Research , pp. 11820–11829. PMLR, 18–24 Jul
2021. URL https://proceedings.mlr.press/
v139/yang21k.html.
Yao, Y ., Lin, Q., and Yang, T. Large-scale optimization
of partial auc in a range of false positive rates. arXiv
preprint, 2022.
Yuan, Z., Yan, Y ., Sonka, M., and Yang, T. Robust
deep AUC maximization: A new surrogate loss and
empirical studies on medical image classification. In
Interntional Conference on Computer Vision , volume
abs/2012.03173, 2020. URL https://arxiv.org/
abs/2012.03173.
Yuan, Z., Guo, Z., Xu, Y ., Ying, Y ., and Yang, T. Federated
deep AUC maximization for hetergeneous data with a
constant communication complexity. In Meila, M. and
Zhang, T. (eds.), Proceedings of the 38th International
Conference on Machine Learning, ICML 2021, 18-24
July 2021, Virtual Event, volume 139 of Proceedings of
Machine Learning Research, pp. 12219–12229. PMLR,
2021. URL http://proceedings.mlr.press/
v139/yuan21a.html.
=== página 12 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
A. More Experimental Results
Table 5. Datasets Statistics. The percentage in parenthesis represents the proportion of positive samples.
Dataset Train Validation Test
CIFAR-10 24000 (16.67%) 6000 (16.67%) 6000 (16.67%)
CIFAR-100 24000 (16.67%) 6000 (16.67%) 6000 (16.67%)
Melanoma 26500 (1.76%) 3313 (1.78%) 3313 (1.75%)
moltox21(t0) 5834 (4.25%) 722 (4.01%) 709 (4.51%)
molmuv(t1) 11466 (0.18%) 1559 (0.13%) 1709 (0.35%)
molpcba(t0) 120762 (9.32%) 19865 (11.74%) 20397 (11.61%)
A.1. Additional plots for training convergence
We present more training convergence plots on Melanoma dataset and molmuv dataset at Figure 4. For OPAUC maximization,
We can observe that both our proposed SOPA-s and SOPA converge much better than AW-poly and MB method under
different settings, i.e., FPR≤ 0.3 and FPR≤ 0.5. And our proposed SOTA-s converge higher by a noticeable margin than
AW-poly and MB method for TPAUC maximization all the time.
0 10 20 30 40 50 60
Epochs
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95
1.00pAUC
Melanoma(FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95
1.00pAUC
Melanoma(FPR 0.5)
SOPA-s
SOPA
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.95
0.96
0.97
0.98
0.99
1.00pAUC
molmuv-t1 (FPR 0.3)
SOPA-s
SOPA
AW-poly
MB
30 40 50 60
0.9988
0.9990
0.9992
0.9994
0.9996
0 10 20 30 40 50 60
Epochs
0.95
0.96
0.97
0.98
0.99
1.00pAUC
molmuv-t1 (FPR 0.5)
SOPA-s
SOPA
AW-poly
MB
30 40 50 60
0.9992
0.9994
0.9996
0.9998
0 10 20 30 40 50 60
Epochs
0.0
0.2
0.4
0.6
0.8
1.0pAUC
Melanoma(TPR 0.6,FPR 0.4)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.0
0.2
0.4
0.6
0.8
1.0pAUC
Melanoma(TPR 0.5,FPR 0.5)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.9800
0.9825
0.9850
0.9875
0.9900
0.9925
0.9950
0.9975
1.0000pAUC
molmuv-t1 (TPR 0.6, FPR 0.4)
SOTA-s
AW-poly
MB
0 10 20 30 40 50 60
Epochs
0.9800
0.9825
0.9850
0.9875
0.9900
0.9925
0.9950
0.9975
1.0000pAUC
molmuv-t1 (TPR 0.5, FPR 0.5)
SOTA-s
AW-poly
MB
Figure 4. Training Convergence Curves on Melanoma and molmuv datasets; Top for OPAUC maximization, bottom for TPAUC maxi-
mization.
A.2. Ablation study for γ0 in SOPA-s and γ0, γ1 in SOTA-s
We conduct extensive ablation study for understanding the extra hyper-parameters γ0 in SOPA-s and γ0, γ1 in SOTA-s
algorithms. We fix it as 0.9 for all of our experiments in the main content. But in practice, the performance would be further
improved if we tune those hyper-parameters as well.
For image datasets, we conduct experiments on CIFAR-10 and CIFAR-100; for molecule datasets, we conduct experiments
on ogbg-moltox21 and ogbg-molmuv. For each dataset, we first fix the best learning rate and other hyper-parameters based
on our previous results in the paper. Then, for SOPA-s, we investigateγ0 at {1.0, 0.9, 0.7, 0.5, 0.3, 0.1}; for SOTA-s, we
investigate both γ0 and γ1 at {1.0, 0.9, 0.7, 0.5, 0.3, 0.1}
For training aspect, we include the comparisons for SOPA-s at Figure 5; we include the comparisons for SOTA-s at Figure 6.
From Figure 5, we can see that better training performance could be achieved by tuning the parameter γ0 in SOPA-s,
compared with fixing it as 0.9; the similar result for SOTA-s can be also observed from Figure 6.
For testing aspect, we include the testing pAUC results at Table 6 for SOPA-s; Table 7 for SOTA-s. Both verify that tuning
these parameters can further improve the performance.
=== página 13 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
0 10 20 30 40 50 60
Epochs
0.86
0.88
0.90
0.92
0.94
0.96
0.98
1.00pAUC
CIFAR-10(FPR 0.3)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50 60
0.993
0.994
0.995
0 10 20 30 40 50 60
Epochs
0.90
0.92
0.94
0.96
0.98
1.00pAUC
CIFAR-10(FPR 0.5)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50 60
0.994
0.995
0.996
0 10 20 30 40 50 60
Epochs
0.75
0.80
0.85
0.90
0.95pAUC
CIFAR-100(FPR 0.3)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50 60
0.980
0.982
0.984
0 10 20 30 40 50 60
Epochs
0.800
0.825
0.850
0.875
0.900
0.925
0.950
0.975pAUC
CIFAR-100(FPR 0.5)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50 60
0.984
0.986
0.988
0 10 20 30 40 50 60
Epochs
0.80
0.82
0.84
0.86
0.88
0.90
0.92
0.94pAUC
moltox21-t0 (FPR 0.3)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50
0.946
0.948
0.950
0.952
0 10 20 30 40 50 60
Epochs
0.82
0.84
0.86
0.88
0.90
0.92
0.94pAUC
moltox21-t0 (FPR 0.5)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
40 50
0.952
0.954
0.956
0.958
0 10 20 30 40 50 60
Epochs
0.97
0.98
0.99
1.00pAUC
molmuv-t1 (FPR 0.3)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
30 40 50 60
0.9994
0.9996
0.9998
0 10 20 30 40 50 60
Epochs
0.98
0.99
1.00pAUC
molmuv-t1 (FPR 0.5)
0 = 1.0
0 = 0.9
0 = 0.7
0 = 0.5
0 = 0.3
0 = 0.1
30 40 50 60
0.9996
0.9998
Figure 5. Training convergence for SOPA-s on differentγ0.
0 10 20 30 40 50 60
Epochs
0.60
0.65
0.70
0.75
0.80
0.85
0.90
0.95
1.00pAUC
CIFAR-10(TPR 0.6,FPR 0.4)
0 = 0.5, 1 = 0.7
0 = 0.9, 1 = 0.7
0 = 0.5, 1 = 0.5
0 = 1.0, 1 = 0.1
0 = 1.0, 1 = 1.0
0 = 0.7, 1 = 0.5
40 50 60
0.989
0.990
0.991
0.992
0 10 20 30 40 50 60
Epochs
0.70
0.75
0.80
0.85
0.90
0.95
1.00pAUC
CIFAR-10(TPR 0.5,FPR 0.5)
0 = 0.5, 1 = 0.7
0 = 1.0, 1 = 0.1
0 = 0.5, 1 = 0.5
0 = 0.9, 1 = 0.7
0 = 1.0, 1 = 1.0
0 = 0.5, 1 = 0.9
40 50 60
0.993
0.994
0.995
0 10 20 30 40 50 60
Epochs
0.3
0.4
0.5
0.6
0.7
0.8
0.9pAUC
CIFAR-100(TPR 0.6,FPR 0.4)
0 = 0.1, 1 = 0.3
0 = 0.1, 1 = 0.5
0 = 0.1, 1 = 0.9
0 = 0.5, 1 = 1.0
0 = 0.9, 1 = 0.7
0 = 0.1, 1 = 1.0
40 50 60
0.945
0.950
0.955
0 10 20 30 40 50 60
Epochs
0.5
0.6
0.7
0.8
0.9pAUC
CIFAR-100(TPR 0.5,FPR 0.5)
0 = 0.1, 1 = 0.3
0 = 0.1, 1 = 0.5
0 = 0.1, 1 = 0.9
0 = 0.5, 1 = 1.0
0 = 0.9, 1 = 0.7
0 = 0.5, 1 = 0.7
40 50 60
0.9625
0.9650
0.9675
0.9700
0 10 20 30 40 50 60
Epochs
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9pAUC
moltox21-t0 (TPR 0.6, FPR 0.4)
0 = 0.5, 1 = 1.0
0 = 0.5, 1 = 0.7
0 = 1.0, 1 = 0.7
0 = 0.3, 1 = 0.3
0 = 0.9, 1 = 0.5
0 = 0.7, 1 = 0.9
30 40 50 60
0.90
0.91
0.92
0 10 20 30 40 50 60
Epochs
0.4
0.5
0.6
0.7
0.8
0.9pAUC
moltox21-t0 (TPR 0.5, FPR 0.5)
0 = 0.5, 1 = 1.0
0 = 0.5, 1 = 0.7
0 = 0.3, 1 = 0.3
0 = 1.0, 1 = 0.7
0 = 0.9, 1 = 0.5
0 = 0.5, 1 = 0.5
30 40 50 60
0.935
0.940
0.945
0 10 20 30 40 50 60
Epochs
0.97
0.98
0.99
1.00pAUC
molmuv-t1 (TPR 0.6, FPR 0.4)
0 = 0.1, 1 = 0.1
0 = 0.1, 1 = 0.3
0 = 0.1, 1 = 0.9
0 = 1.0, 1 = 0.5
0 = 0.1, 1 = 1.0
0 = 0.7, 1 = 0.5
30 40 50 60
0.9990
0.9995
0 10 20 30 40 50 60
Epochs
0.98
0.99
1.00pAUC
molmuv-t1 (TPR 0.5, FPR 0.5)
0 = 0.1, 1 = 0.1
0 = 0.1, 1 = 0.3
0 = 0.1, 1 = 0.9
0 = 1.0, 1 = 0.5
0 = 0.1, 1 = 1.0
0 = 0.5, 1 = 0.5
30 40 50 60
0.99900
0.99925
0.99950
0.99975
Figure 6. Top-6 choices of γ0 and γ1 for SOTA-s from training perspective.
Table 6. Test pAUC for SOPA-s on differentγ0.
Dataset Metric γ0 = 1.0 γ0 = 0.9 γ0 = 0.7 γ0 = 0.5 γ0 = 0.3 γ0 = 0.1
CIFAR-10 FPR ≤0.3 0.8721(0.0049) 0.8691(0.0036) 0.8682(0.0048) 0.8697(0.0032) 0.8674(0.0045) 0.8725(0.0012)
FPR≤0.5 0.8989(0.0051) 0.8961(0.0036) 0.8946(0.0040) 0.8980(0.0037) 0.8947(0.0028) 0.8996(0.0021)
CIFAR-100 FPR≤0.3 0.7464(0.0012) 0.7460(0.0068) 0.7482(0.0031) 0.7508(0.0038) 0.7494(0.0048) 0.7514(0.0018)
FPR≤0.5 0.7888(0.0016) 0.7877(0.0053) 0.7936(0.0040) 0.7961(0.0063) 0.7922(0.0059) 0.7954(0.0015)
moltox21 FPR ≤0.3 0.7242(0.0170) 0.7288(0.0125) 0.7274(0.0087) 0.7274(0.0062) 0.7158(0.0069) 0.7340(0.0079)
FPR≤0.5 0.7245(0.0194) 0.7266(0.0111) 0.7280(0.0066) 0.7358(0.0079) 0.7249(0.0090) 0.7360(0.0123)
molmuv FPR ≤0.3 0.8692(0.0116) 0.8376(0.0340) 0.8642(0.0214) 0.8735(0.0070) 0.8732(0.0104) 0.8496(0.0392)
FPR≤0.5 0.8773(0.0186) 0.8616(0.0355) 0.8747(0.0053) 0.8996(0.0228) 0.8918(0.0232) 0.8622(0.0415)
B. Proofs
We next present several lemmas. The first lemma is straightforward.
Lemma 4. For ˆLkl(·; λ), when λ = 0 it reduces to the maximal value of {ℓ1(·), . . . , ℓn(·)}, i.e., ˆLkl(·, 0) = max i ℓi(·);
and when λ = ∞, it reduces to the average value of {ℓ1, . . . , ℓn}, i.e., ˆLkl(·; ∞) = 1
n
Pn
i=1 ℓi(·).
Lemma 5. [Lemma 1 (Ogryczak & Tamir, 2003)] Assume γ = k/n for some integer k ∈ [n], we have ˆLcvar(·; γ) =
mins s + 1
nγ
Pn
i=1[ℓi(·) − s]+.
A major difference between ˆLkl(·; λ) and ˆLcvar(·; γ) that has an impact on optimization is that ˆLcvar(·; γ) is a non-smooth
function, and ˆLkl(·; λ) is a smooth function for λ >0 when ℓi(·) is smooth and bounded as indicated by the following
lemma.
=== página 14 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Table 7. Test pAUC for SOTA-s on differentγ0 and γ1.
CIFAR-10 (0.4, 0.6) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.5731(0.0069) 0.5744(0.0083) 0.5668(0.0048) 0.5686(0.0089) 0.5678(0.0070) 0.5739(0.0135)
γ0 = 0.9 0.5802(0.0081) 0.5839(0.0116) 0.5693(0.0072) 0.5743(0.0131) 0.5688(0.0048) 0.5760(0.0095)
γ0 = 0.7 0.5755(0.0098) 0.5715(0.0032) 0.5684(0.0131) 0.5797(0.0036) 0.5718(0.0095) 0.5695(0.0111)
γ0 = 0.5 0.5743(0.0058) 0.5706(0.0025) 0.5641(0.0094) 0.5819(0.0077) 0.5725(0.0109) 0.5739(0.0068)
γ0 = 0.3 0.5767(0.0121) 0.5638(0.0144) 0.5617(0.0075) 0.5644(0.0099) 0.5595(0.0028) 0.5768(0.0100)
γ0 = 0.1 0.5608(0.0075) 0.5689(0.0134) 0.5699(0.0096) 0.5685(0.0056) 0.5583(0.0101) 0.5756(0.0135)
CIFAR-10 (0.5, 0.5) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.7022(0.0054) 0.6999(0.0076) 0.6922(0.0076) 0.6969(0.0087) 0.6982(0.0046) 0.6981(0.0074)
γ0 = 0.9 0.7051(0.0083) 0.7047(0.0072) 0.6987(0.0034) 0.7008(0.0103) 0.6964(0.0048) 0.7003(0.0064)
γ0 = 0.7 0.7027(0.0046) 0.6999(0.0031) 0.6959(0.0099) 0.7043(0.0056) 0.6988(0.0099) 0.6914(0.0110)
γ0 = 0.5 0.7012(0.0050) 0.6988(0.0008) 0.6944(0.0067) 0.7044(0.0067) 0.7014(0.0047) 0.7031(0.0088)
γ0 = 0.3 0.7024(0.0099) 0.6940(0.0085) 0.6901(0.0060) 0.6981(0.0047) 0.6908(0.0025) 0.6977(0.0129)
γ0 = 0.1 0.6934(0.0068) 0.7009(0.0060) 0.6972(0.0088) 0.6946(0.0037) 0.6891(0.0098) 0.7027(0.0082)
CIFAR-100 (0.4, 0.6) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.2710(0.0144) 0.2650(0.0052) 0.2528(0.0061) 0.2573(0.0129) 0.2587(0.0096) 0.2613(0.0046)
γ0 = 0.9 0.2666(0.0144) 0.2708(0.0055) 0.2698(0.0117) 0.2586(0.0116) 0.2562(0.0032) 0.2663(0.0056)
γ0 = 0.7 0.2634(0.0086) 0.2624(0.0065) 0.2577(0.0045) 0.2664(0.0051) 0.2634(0.0090) 0.2626(0.0144)
γ0 = 0.5 0.2633(0.0010) 0.2591(0.0026) 0.2552(0.0068) 0.2530(0.0069) 0.2656(0.0089) 0.2594(0.0052)
γ0 = 0.3 0.2572(0.0063) 0.2542(0.0076) 0.2517(0.0111) 0.2599(0.0184) 0.2580(0.0191) 0.2631(0.0081)
γ0 = 0.1 0.2532(0.0050) 0.2745(0.0029) 0.2529(0.0060) 0.2573(0.0115) 0.2568(0.0029) 0.2671(0.0187)
CIFAR-100 (0.5, 0.5) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.4489(0.0122) 0.4454(0.0084) 0.4337(0.0097) 0.4418(0.0083) 0.4361(0.0093) 0.4405(0.0063)
γ0 = 0.9 0.4416(0.0115) 0.4528(0.0069) 0.4494(0.0073) 0.4449(0.0171) 0.4337(0.0046) 0.4421(0.0058)
γ0 = 0.7 0.4426(0.0119) 0.4426(0.0098) 0.4367(0.0092) 0.4414(0.0072) 0.4455(0.0046) 0.4430(0.0108)
γ0 = 0.5 0.4404(0.0058) 0.4388(0.0085) 0.4341(0.0066) 0.4332(0.0079) 0.4426(0.0107) 0.4421(0.0057)
γ0 = 0.3 0.4384(0.0090) 0.4313(0.0081) 0.4377(0.0104) 0.4392(0.0185) 0.4401(0.0095) 0.4384(0.0125)
γ0 = 0.1 0.4325(0.0006) 0.4500(0.0015) 0.4361(0.0085) 0.4316(0.0083) 0.4355(0.0053) 0.4461(0.0213)
moltox21 (0.4, 0.6) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.0769(0.0403) 0.0800(0.0345) 0.0594(0.0377) 0.0409(0.0241) 0.0774(0.0342) 0.0607(0.0139)
γ0 = 0.9 0.0668(0.0304) 0.0733(0.0198) 0.0676(0.0357) 0.0761(0.0316) 0.0737(0.0245) 0.0588(0.0249)
γ0 = 0.7 0.0657(0.0280) 0.0849(0.0451) 0.0840(0.0162) 0.0807(0.0253) 0.0665(0.0171) 0.0573(0.0262)
γ0 = 0.5 0.0795(0.0537) 0.0513(0.0140) 0.0704(0.0301) 0.0367(0.0164) 0.0754(0.0190) 0.0676(0.0350)
γ0 = 0.3 0.1009(0.0133) 0.0695(0.0256) 0.0806(0.0289) 0.0805(0.0358) 0.0943(0.0453) 0.0546(0.0409)
γ0 = 0.1 0.0746(0.0473) 0.0610(0.0224) 0.0694(0.0303) 0.0578(0.0458) 0.0768(0.0574) 0.0485(0.0254)
moltox21 (0.5, 0.5) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.2474(0.0154) 0.2489(0.0282) 0.2355(0.0508) 0.2127(0.0326) 0.2798(0.0640) 0.2254(0.0223)
γ0 = 0.9 0.2483(0.0214) 0.2476(0.0222) 0.2373(0.0552) 0.2457(0.0296) 0.2341(0.0137) 0.2198(0.0233)
γ0 = 0.7 0.2306(0.0286) 0.2354(0.0360) 0.2531(0.0217) 0.2546(0.0174) 0.2415(0.0181) 0.2233(0.0225)
γ0 = 0.5 0.2536(0.0531) 0.2251(0.0163) 0.2276(0.0241) 0.2153(0.0196) 0.2488(0.0121) 0.2230(0.0228)
γ0 = 0.3 0.2773(0.0207) 0.2482(0.0256) 0.2434(0.0224) 0.2603(0.0323) 0.2574(0.0455) 0.2208(0.0494)
γ0 = 0.1 0.2368(0.0193) 0.2395(0.0267) 0.2323(0.0239) 0.1973(0.0383) 0.2543(0.0611) 0.2121(0.0369)
molmuv (0.4, 0.6) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.5021(0.1222) 0.4508(0.1263) 0.3878(0.0776) 0.5399(0.1575) 0.3972(0.0768) 0.3904(0.1404)
γ0 = 0.9 0.5651(0.0833) 0.4524(0.0290) 0.6060(0.2187) 0.5711(0.1495) 0.4250(0.0543) 0.4313(0.1174)
γ0 = 0.7 0.4120(0.1026) 0.4338(0.0407) 0.5375(0.1339) 0.5765(0.1719) 0.3251(0.0889) 0.4744(0.1379)
γ0 = 0.5 0.5432(0.1177) 0.4934(0.1065) 0.4812(0.0744) 0.3890(0.0976) 0.4507(0.0387) 0.3859(0.0488)
γ0 = 0.3 0.4680(0.1079) 0.4559(0.1037) 0.4811(0.1237) 0.4221(0.1322) 0.4297(0.2263) 0.3828(0.0606)
γ0 = 0.1 0.4777(0.0591) 0.4264(0.1414) 0.5322(0.1342) 0.4122(0.0260) 0.3836(0.0368) 0.3903(0.0325)
molmuv (0.5, 0.5) γ1 = 1.0 γ1 = 0.9 γ1 = 0.7 γ1 = 0.5 γ1 = 0.3 γ1 = 0.1
γ0 = 1.0 0.6780(0.0880) 0.6384(0.0964) 0.6175(0.0447) 0.7135(0.1074) 0.6188(0.0483) 0.6152(0.0965)
γ0 = 0.9 0.7405(0.0621) 0.6399(0.0276) 0.7481(0.1464) 0.7230(0.1020) 0.6136(0.0321) 0.6277(0.0854)
γ0 = 0.7 0.6201(0.0698) 0.6445(0.0430) 0.7007(0.1013) 0.7272(0.1178) 0.5588(0.0482) 0.6496(0.1030)
γ0 = 0.5 0.7071(0.0869) 0.6854(0.0853) 0.6542(0.0646) 0.5867(0.0657) 0.6495(0.0470) 0.5996(0.0431)
γ0 = 0.3 0.6626(0.0737) 0.6561(0.0778) 0.6658(0.0910) 0.6408(0.0825) 0.6264(0.1791) 0.5801(0.0399)
γ0 = 0.1 0.6643(0.0562) 0.6362(0.1103) 0.7142(0.0904) 0.6271(0.0188) 0.5746(0.0283) 0.5877(0.0449)
=== página 15 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Lemma 6. If ℓi(·) is a smooth function, and has a bounded value and bounded gradient for a bounded input, then for λ >0
the function ˆLkl(·; λ) is also a smooth and bounded function.
Lemma 7. When ϕc(t) = I(0 ≤ t ≤ 1/β) and ϕ′
c(t) = I(0 ≤ t ≤ 1/α) with K2 = n−β and K1 = n+α being integers, if
ℓ(·) is monotonically decreasing for ℓ(·) > 0, we can show that
F (w; ϕc, ϕ′
c) = 1
K1K2
X
xi∈S ↑
+[1,K1]
X
xj ∈S ↓
−[1,K2]
L(w; xi, xj),
which is also equivalent to
F (w; ϕc, ϕ′
c) = min
s′∈R,s∈Rn+
s′ + 1
n+α
X
xi∈S+
(si + 1
β ψi(w; si) − s′)+.
B.1. Proof of Lemma 6
It is easy to see if ℓ(w) ∈ [0, C] is bounded and smooth, we have exp( ℓ(w)
λ ) is bounded and smooth due to its second order
gradient is upper bounded. Then log Ei exp( ℓi(w)
λ ) is bounded. Its smoothness due to that is a composition of f = log(·)
and g = Ei exp( ℓi(w)
λ ) ∈ [1, C′] and both f, gare smooth and Lipschitz continuous for their inputs.
B.2. Proof of Lemma 7
Proof. First, following Lemma 1, we have F (w; ϕ, ϕ′) is equivalent to 1
K1
PK1
i=1 ˆLϕ(xπi , w), where πi denote the index of
the positive example whose ˆLϕ(xπi , w) is the i-th largest among all positive examples. We prove that this is equivalent
to 1
K1
P
xi∈S ↑
+[1,K1]
ˆLϕ(xi, w). To this end, we just need to show that if hw(x) ≥ hw(x′) then ˆLϕ(x′, w) ≥ ˆLϕ(x, w),
which is true due to ˆLϕ(xi, w) = 1
K2
P
xj ∈S ↓
−[1,K2] ℓ(hw(xi) − hw(xj)) and ℓ is monotonically decreasing function. The
second equation in the lemma is applying Lemma 5 twice and by noting that (minx f (x) − s)+ = minx(f (x) − s)+.
B.3. Proof of Theorem 1
Proof. Let us consider for a particular xi ∈ S+. When ϕ(·) = ϕc(·) = I(· ∈(0, 1/β]), then ˆL(w; xi) becomes the CVaR
estimator, i.e., the average of top K = n−β losses of ℓ(hw(xi) − hw(xj)) among xj ∈ S−. Since ℓ(·) is monotonically
decreasing when ℓ(·)) > 0, the top K = n−β losses of ℓ(hw(xi) − hw(xj)) among all xj ∈ S− correspond to negative
samples with top K prediction scores. Hence, ˆLϕc (w; xi) = 1
K
P
xj ∈S ↓
−[1,K] ℓ(hw(xi) − hw(xj)). Then the equivalent
problem in (9) follows from Lemma 5.
B.4. Proof of Theorem 2
Proof. When choosing ϕ(·) = ϕkl(·), the ˆLϕ(w; xi) in problem (8) becomes
max
p∈∆
X
xj ∈S−
pjL(w; xi, xj) − λ
X
j
pj log(npj).
With Karush-Kuhn-Tucker(KKT) conditions, it is not difficult to havep⋆
j = exp(L(w;xi,xj )/λP
j exp(L(w;xi,xj )/λ. By plugging in this back
we obtain the claimed objective (10). When λ = 0, the above becomes the maximal one among {L(w; xi, xj), xj ∈ S+}
for each xi. Then the object is 1
n+
maxxj ∈S− L(w; xi, xj), which is the surrogate of pAUC with FPR ≤ 1/n−. When
λ = ∞, the above becomes the average of {L(w; xi, xj), xj ∈ S+}, which gives the standard surrogate of AUC.
B.5. Proof of Lemma 2
First note that F (w, s) = 1
n+
P
xi∈S+

si + 1
β gi(w, si)

, and gi(w, si) = 1
n−
P
xj ∈S− (L(w; xi, xj) − si)+. We prove
that (L(w; xi, xj) − si)+ is weakly convex in terms of (w, si), i.e. there exists ρ >0 such that (L(w; xi, xj) − si)+ +
ρ
2 ∥w∥2 + ρ
2 s2
i is jointly convex in terms of w, s. To this end, let ψ(·) = [·]+ which is convex and Lipchitz continuous, and
q(w, si) = L(w; xi, xj) − si, which is Ls-smooth function with respect to (w, si) due to that L(w; xi, xj) is Ls-smooth
=== página 16 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
function. Then for any ω ∈ ϕ′(ψ(w′, s′
i)) we have
ψ(q(w, si)) ≥ ψ(q(w′, s′
i)) + ω(q(w, si) − q(w′, s′
i))
≥ ψ(q(w′, s′
i)) + ω(∇q(w′, s′
i) − Ls
2 (∥w − w′∥2 + |si − s′
i|2))
≥ ψ(q(w′, s′
i)) + ∂ψ(q(w′, s′
i)) − Ls
2 (∥w − w′∥2 + |si − s′
i|2)
where we use 0 ≤ ω ≤ 1. The above inequality implies that [L(w; xi, xj) − si]+ is Ls-weakly convex in terms of
(w, si) (Davis & Drusvyatskiy, 2018), i.e., 1
n−
P
xj ∈S−

(L(w; xi, xj) − si)+ + Ls
2 (∥w∥2 + |si|2)
	
is convex. As a result
1
n−
P
xj ∈S− (L(w; xi, xj) − si)+ + Ls
2 (∥w∥2 + ∥si∥2) is jointly convex in (w, si). Then F (w, s) + Ls
2β (∥w∥2 + P
i |si|2)
is jointly convex in terms of (w, s).
B.6. Proof of Theorem 3
Let F (w, s) denote the objective function, and let v = (w, s). Define F1/ ˆρ(v) = minu F (u) + ˆρ
2 ∥u − v∥2 for some ˆρ > ρ
and the minimizer is denoted by proxF/ ˆρ(v). Let bvt = proxF/ ˆρ(vt). Define ∥v − v′∥2 = ∥w − w′∥2 + ∥s − s′∥2.
Et[F1/ ˆρ(vt+1)] = Et[F (bvt) + ˆρ
2 ∥vt+1 − bvt∥2]
≤ F (bvt) + ˆρ
2 Et[∥wt − η1∇wF (wt, st, ξt) − bwt∥2 + ∥st+1 − ˆst∥2]
≤ F (bvt) + ˆρ
2 Et[∥wt − η1∇wF (wt, st, ξt) − bwt∥2] + ˆρ
2 Et[∥st+1 − ˆst∥2]
≤ F (bxt) + ˆρ
2 ∥wt − bwt∥2 + ˆρηtEt[( bwt − wt)⊤∇wF (wt, st)] + ˆρη2
1G2
2 + ˆρ
2 Et[∥st+1 − ˆst∥2]
where we assume E[∥∇wF (wt, st, ξt)∥2] ≤ G2 = C2
β2 . According to the analysis of stochastic coordinate descent method,
for any s = (s1, . . . , sn+ ) we have
2η2(st,i − si)⊤∇si F (wt, st; ξt) ≤ η2
2∥∇si F ( ¯wt, ut; ξt)∥2 + (∥si − st,i∥2 − ∥si − st+1,i∥2)
Summing the above inequality over i ∈ B+, we have
2η2
X
i∈B+
(st,i − si)⊤∇si F (wt, st; ξt) ≤ η2
2
X
i∈B+
∥∇si F ( ¯wt, ut; ξt)∥2 + (∥s − st∥2 − ∥s − st+1∥2)
Taking expectation and re-arrange, we have
E[ 1
2 ∥st+1 − bst∥2] ≤ E[ 1
2 ∥st − bst∥2 + η2
B+
n+
(bst − st)⊤∇sF (wt, st) + η2
2B+C 2
2
2 ]
where we use the fact E[|∇si F (w, s)|2] ≤ C 2
2 = 1
n2
+
(1 + 1/β)2. Let η2B+/n+ = η1, we have
Et[F1/ ˆρ(vt+1)]
≤ F (bxt) + ˆρ
2 ∥wt − bwt∥2 + ˆρη1Et[( bwt − wt)⊤∇wF (wt, st)] + ˆρ
2 Et[∥st+1 − bst)] + ˆρη2
1G2
2
≤ F (bvt) + ˆρ
2 ∥vt − bvt∥2 + ˆρη1Et[(bvt − vt)⊤∂F (wt, st)] + ˆρη2
1(G2 + n2
+C 2
2 /B+)
2
≤ F1/ ˆρ(vt) + ˆρη1(F (bvt) − F (vt) + ρ
2 ∥vt − bvt∥2) + ˆρη2
1(G2 + n2
+C 2
2 /B+)
2
=== página 17 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
As a result, we have
ˆρη1(F (vt) − F (bvt) − ρ∥vt − bvt∥2) ≤ F1/ ˆρ(vt) − Et[F1/ ˆρ(vt+1)] + ˆρη2
1(G2 + n2
+C 2
2 /B+)
2
Since we have
F (vt) − F (bvt) − ρ∥vt − bvt∥2 = (F (vt) + ˆρ∥vt − vt∥2) − (F (bvt) + ˆρ∥bvt − vt∥2) + (ˆρ − ρ)∥vt − bvt∥2
≥ (2ˆρ − ρ)
2 ∥bvt − vt∥2 + (ˆρ − ρ)∥vt − bvt∥2 = (2ˆρ − 3/2ρ)∥vt − bvt∥2 = (2ˆρ − 3/2ρ)
ˆρ2 ∥∇F1/ ˆρ(vt)∥2
Let ˆρ = 3ρ/2. As a result, we have
1
T
TX
t=1
∥∇F1/ ˆρ(vt)∥2 ≤ (F1/ ˆρ(v1) − min F )
η1T + ˆρη1(G2 + n2
+C 2
2 /B+)
2
≤ (F1/ ˆρ(v1) − min F )
η1T + ˆρη1(C 2/β2 + (1 + 1/β)2/B+)
2
By setting η1 = O(βϵ2) and T = O( 1
ϵ2η1
) = O(1/(βϵ4)) we have E[∥∇F1/ ˆρ(vτ )∥2] ≤ ϵ2 for a randomly selected
τ ∈ [T ].
B.7. Proof of Theorem 4
Note that the SOPA-s algorithm is just a special case of the SOX algorithm (Wang & Yang, 2022) for the more general
problem minw 1
n
P
zi∈D fi(gi(w)) and the convergence proof just follows the proof of Theorem 1 in Wang & Yang (2022).
B.8. Proof of Theorem 5
We consider the following problem:
min
w
F (w), F (w) = f1
 
1
n
X
i∈S
f2(gi(w))
!
. (12)
Lemma 8. If gi is Cg-Lipschitz, Lg-smooth and f1, f2 are Cf -Lipschitz, Lg-smooth, F in (12) is LF -smooth and LF =
Lf C 2
f C 2
g + C 2
f Lg + Cf CgLf .
Proof. Based on the definition of F , we have
∥∇F (w) − ∇F (w′)∥
=





∇f1
 
1
n
X
i∈S
f2(gi(w))
!  
1
n
X
i∈S
∇f2(gi(w))∇gi(w)
!
−∇f1
 
1
n
X
i∈S
f2(gi(w′))
!  
1
n
X
i∈S
∇f2(gi(w′))∇gi(w′)
!




≤ Lf





1
n
X
i∈S
∇f2(gi(w))∇gi(w)










1
n
X
i∈S
(f2(gi(w)) − f2(gi(w′)))





+





∇f1
 
1
n
X
i∈S
f2(gi(w′))
!









1
n
X
i∈S
(∇f2(gi(w))∇gi(w) − ∇f2(gi(w′))∇gi(w′))





 .
We can show that


 1
n
P
i∈S (∇f2(gi(w))∇gi(w) − ∇f2(gi(w′))∇gi(w′))


 ≤ (Cf Lg + CgLf ) ∥w − w′∥. Thus,
∥∇F (w) − ∇F (w′)∥ ≤Lf C 2
f C 2
g ∥w − w′∥ + Cf (Cf Lg + CgLf ) ∥w − w′∥
= (Lf C 2
f C 2
g + C 2
f Lg + Cf CgLf ) ∥w − w′∥ .
We propose SOTA-s to solve (12).
=== página 18 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Lemma 9. Consider a sequence wt+1 = wt − ηmt and the LF -smooth function F and the step size ηLF ≤ 1/2.
F (wt+1) ≤ F (wt) + η
2 ∥∆t∥2 − η
2 ∥∇F (wt)∥2 − η
4 ∥mt∥2 , (13)
where ∆t := mt − ∇F (wt)
Lemma 10. For the gradient estimator mt in SOTA-s and ∆t = mt − ∇F (wt),
E
h
∥∆t+1∥2
i
≤ (1 − γ2)E
h
∥∆t∥2
i
+ 2L2
F η2
γ2
E
h
∥mt∥2
i
+ 10γ2C 2
f C 2
1 L2
f E
h
∥Ψt+1∥2
i
+ 20γ2C 2
f L2
f C 2
1 E
 1
n ∥Ξt+1∥2

+ 20γ2C 2
f L2
f C 2
1 E
 1
n ∥ut+1 − ut∥2

+ 2γ2
2 C 4
f
 
ζ 2
B−
+ C 2
g
B+
!
, (14)
where we denote ∆t := mt+1 − ∇F (wt), Ξt := ut+1 − g(wt) and Ψt := vt+1 − 1
n
P
i∈S f2(gi(wt)).
Proof. Based on the update rule mt+1 = (1 − γ2)mt + γ2G(wt+1), we have
∥mt+1 − ∇F (wt+1)∥2
=






(1 − γ2)mt + γ2
1
B+
X
i∈B+
∇f1(vt+1)∇f2(ui
t)∇gi(wt+1; B−) − ∇F (wt+1)






2
=







(1 − γ2)(mt − ∇F (wt))| {z }
a⃝
+ (1 − γ2)(∇F (wt) − ∇F (wt+1))| {z }
b⃝
+γ2
1
B+
X
i∈B+
∇f1(vt+1)∇f2(ui
t)∇gi(wt+1; B−)
−γ2
1
B+
X
i∈B+
∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!
∇f2(gi(wt+1))∇gi(wt+1; B−)
+ γ2

 1
B+
X
i∈B+
∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!
∇f2(gi(wt+1))∇gi(wt+1; B−) − ∇F (wt+1)


| {z }
d⃝











2
.
We define that
c⃝ := γ2

 1
B+
X
i∈B+
∇f1(vt+1)∇f2(ui
t)∇gi(wt+1; B−)
− 1
B+
X
i∈B+
∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!
∇f2(gi(wt+1))∇gi(wt+1; B−)

 .
We define that ∆t := mt − ∇F (wt). Note that E [⟨ a⃝, d⃝⟩] = E [⟨ b⃝, d⃝⟩] = 0. Then,
Et
h
∥ a⃝ + b⃝ + c⃝ + d⃝∥2
i
= ∥ a⃝∥2 + ∥ b⃝∥2 + Et
h
∥ c⃝∥2
i
+ Et
h
∥ d⃝∥2
i
+ 2 ⟨ a⃝, b⃝⟩
+ 2Et [⟨ a⃝, c⃝⟩] + 2Et [⟨ b⃝, c⃝⟩] + 2Et [⟨ c⃝, d⃝⟩] .
Based on the Young’s inequality for products, we have2 ⟨a, b⟩ ≤∥a∥2c
2 + 2∥b∥2
c for c >0.
Et
h
∥ a⃝ + b⃝ + c⃝ + d⃝∥2
i
≤ (1 + γ2) ∥ a⃝∥2 + 2(1 + 1/γ2) ∥ b⃝∥2 + 2 + 3γ2
γ2
Et
h
∥ c⃝∥2
i
+ 2Et
h
∥ d⃝∥2
i
.
Thus, we have
Et[∥∆t+1∥2] ≤ (1 − γ2) ∥∆t∥2 + 2(1 + γ2)
γ2
∥ b⃝∥2 + 5
γ2
Et[∥ c⃝∥2] + 2Et[∥ d⃝∥2]. (15)
=== página 19 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Moreover, we have
∥ b⃝∥2 = (1 − γ2)2 ∥∇F (wt) − ∇F (wt+1)∥2 ≤ (1 − γ2)2η2L2
F ∥mt∥2 . (16)
On the other hand,
∥ c⃝∥2 ≤ 2γ2
2
B+
X
i∈B+
∥∇gi(wt+1; B−)∥2





∇f1(vt+1) − ∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!




2


∇f2(ui
t)


2
+ 2γ2
2
B+
X
i∈B+
∥∇gi(wt+1; B−)∥2





∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!




2


∇f2(ui
t) − ∇f2(gi(wt+1))


2
≤
2γ2
2 L2
f C 2
f
B+
X
i∈B+
∥∇gi(wt+1; B−)∥2





vt+1 − 1
n
X
i∈S
f2(gi(wt+1))





2
+
2γ2
2 L2
f C 2
f
B+
X
i∈B+
∥∇gi(wt+1; B−)∥2 

ui
t − gi(wt+1)


2
Due to EB−
h
∥∇gi(wt+1; B−)∥2
i
≤ C 2
g + ζ 2/B− := C 2
1, we have
Et
h
∥ c⃝∥2
i
≤
2γ2
2 L2
f C 2
f C 2
1
n
X
i∈S
Et







vt+1 − 1
n
X
i∈S
f2(gi(wt+1))





2
+


ui
t − gi(wt+1)


2


Besides, we also have
Et
h
∥ d⃝∥2
i
≤ γ2
2 Et








1
B+
X
i∈B+
∇f1
 
1
n
X
i∈S
f2(gi(wt+1))
!
∇f2(gi(wt+1))∇gi(wt+1; B−) − ∇F (wt+1)






2

= γ2
2 C 2
f Et








1
B+
X
i∈B+
(∇f2(gi(wt+1))∇gi(wt+1; B−) − ∇f2(gi(wt+1))∇gi(wt+1))






2

+ γ2
2 C 2
f Et








1
B+
X
i∈B+
∇f2(gi(wt+1))∇gi(wt+1; B−) − 1
n
X
i∈S
∇f2(gi(wt+1))∇gi(wt+1; B−)






2

≤
γ2
2 C 4
f ζ 2
B−
+
γ2
2 C 4
f C 2
g
B+
. (17)
Then,
E
h
∥∆t+1∥2
i
≤ (1 − γ2)E
h
∥∆t∥2
i
+ 2L2
F η2
γ2
E
h
∥mt∥2
i
+ 10γ2C 2
f C 2
1 L2
f E
h
∥Ψt+1∥2
i
+ 20γ2C 2
f L2
f C 2
1 E
 1
n ∥Ξt+1∥2

+ 20γ2C 2
f L2
f C 2
1 E
 1
n ∥ut+1 − ut∥2

+ 2γ2
2 C 4
f
 
ζ 2
B−
+ C 2
g
B+
!
,
where we denote Ξt := ut − g(wt) and Ψt := vt − 1
n
P
i∈S f2(gi(wt)).
Lemma 11. For the function value estimator vt+1 in SOTA-s and Ψt := vt − 1
n
P
i∈S f2(gi(wt)),
Et
h
∥Ψt+1∥2
i
≤ (1 − γ1) ∥Ψt∥2 +
2C 2
f C 2
g η2
γ1
∥mt∥2 + 5γ1C 2
f Et
 1
n ∥Ξt+1∥2

(18)
+
10γ1C 2
f
n Et
h
∥ut − ut+1∥2
i
+
2γ2
1 C 2
f
B+
.
=== página 20 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Proof. According to the update of v in SOTA-s, we have





vt+1 − 1
n
X
i∈S
f2(gi(wt+1))





2
=






(1 − γ1)vt + γ1
1
B+
X
i∈B+
f2(ui
t) − 1
n
X
i∈S
f2(gi(wt+1))






2
=





(1 − γ1)
 
vt − 1
n
X
i∈S
f2(gi(wt))
!
+ (1 − γ1)
 
1
n
X
i∈S
(f2(gi(wt)) − f2(gi(wt+1)))
!
+γ1

 1
B+
X
i∈B+
f2(ui
t) − 1
B+
X
i∈B+
f2(gi(wt+1))

 + γ1

 1
B+
X
i∈B+
f2(gi(wt+1)) − 1
n
X
i∈S
f2(gi(wt+1))








2
.
Denoting Ψt :=


vt − 1
n
P
i∈S f2(gi(wt))


2
, we have
Et
h
∥Ψt+1∥2
i
≤ (1 − γ1) ∥Ψt∥2 +
2(1 − γ1)C 2
f C 2
g η2
γ1
∥mt∥2 +
(2 + 3β)C 2
f
γ1
γ2
1 Et

 1
B+
X
i∈B+


ui
t − gi(wt+1)


2

 +
2γ2
1 C 2
f
B+
≤ (1 − γ1) ∥Ψt∥2 +
2C 2
f C 2
g η2
γ1
∥mt∥2 +
5γ1C 2
f
n Et
h
∥ut − g(wt+1)∥2
i
+
2γ2
1 C 2
f
B+
≤ (1 − γ1) ∥Ψt∥2 +
2C 2
f C 2
g η2
γ1
∥mt∥2 +
10γ1C 2
f
n Et
h
∥ut+1 − g(wt+1)∥2
i
+
10γ1C 2
f
n Et
h
∥ut − ut+1∥2
i
+
2γ2
1 C 2
f
B+
.
Proof of Theorem 5. Based on (13), we have
E [F (wt+1) − Finf ] ≤ E [F (wt) − Finf ] + η
2 E
h
∥∆t∥2
i
− η
2 E
h
∥∇F (wt)∥2
i
− η
4 E
h
∥mt∥2
i
(19)
Re-arranging the terms and telescoping (19) from t = 1 to T leads to
1
T
TX
t=1
E
h
∥∇F (wt)∥2
i
≤ 2E [F (w1) − Finf ]
ηT + 1
T
TX
t=1
E
h
∥∆t∥2
i
| {z }
:= e⃝
− 1
2T
TX
t=1
E
h
∥mt∥2
i
. (20)
Based on (14), the term e⃝ can be upper bounded as
1
T
TX
t=1
E
h
∥∆t∥2
i
≤
E
h
∥∆1∥2
i
γ2T + 2L2
F η2
γ2
2
1
T
TX
t=1
E
h
∥mt∥2
i
+ 2γ2C 4
f
 
ζ 2
B−
+ C 2
g
B+
!
+ 20C 2
f C 2
1 L2
f
TX
t=1
1
n E[∥ut+1 − ut∥2] + 20C 2
f C 2
1 L2
f


1
T
TX
t=1
E
h
∥Ψt+1∥2
i
| {z }
:= f⃝
+ 1
T
TX
t=1
E
 1
n ∥Ξt+1∥2

| {z }
:= g⃝


.
Based on Lemma 2 in Wang & Yang (2022), the term g⃝ can be upper bounded as
1
T
TX
t=1
E
 1
n ∥Ξt+1∥2

≤
4nE
h
1
n ∥Ξ2∥2
i
γ0B+T + 20C 2
g
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+1∥2
i
+ 8γ0σ2
B−
− 1
γ0B+
TX
t=1
E
h

ut+1 − ut

2i
.
=== página 21 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
With 1/(γ0B+) ≥ max(10C 2
f /n, 1/n), based on (18), the term f⃝ can be bounded as
1
T
TX
t=1
E
h
∥Ψt+1∥2
i
≤
E
h
∥Ψ2∥2
i
γ1T +
2C 2
f C 2
g η2
γ2
1
1
T
TX
t=1
E
h
∥mt+1∥2
i
+ 5C 2
f
1
T
TX
t=1
E
 1
n ∥Ξt+2∥2

+
2γ1C 2
f
B+
≤
E
h
∥Ψ2∥2
i
γ1T +
2C 2
f C 2
g η2
γ2
1
1
T
TX
t=1
E
h
∥mt+1∥2
i
+
2γ1C 2
f
B+
+
20C 2
f nE
h
1
n ∥Ξ3∥2
i
γ0B+T
+ 100C 2
f C 2
g
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+2∥2
i
+
40C 2
f γ0σ2
B−
.
Plug the upper bounds of f⃝ and g⃝ into (20).
1
T
TX
t=1
E
h
∥∇F (wt)∥2
i
≤ 2E [F (w1) − Finf ]
ηT +
E
h
∥∆1∥2
i
γ2T + 2γ2C 4
f
 
ζ 2
B−
+ C 2
g
B+
!
+
40nC 2
f C 2
1 L2
f E
h
1
n ∥Ξ2∥2
i
γ0B+T −
 1
2 − 2L2
F η2
γ2
2
 1
T
TX
t=1
E
h
∥mt∥2
i
+ 200C 2
f C 2
g C 2
1 L2
f
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+1∥2
i
+
80γ0C 2
f C 2
1 L2
f σ2
B−
+
10C 2
f C 2
1 L2
f E
h
∥Ψ2∥2
i
γ1T +
20C 4
f C 2
g C 2
1 L2
f η2
γ2
1
1
T
TX
t=1
E
h
∥mt+1∥2
i
+
20γ1C 4
f C 2
1 L2
f
B+
+
200nC 4
f C 2
1 L2
f E
h
1
n ∥Ξ3∥2
i
γ0B+T + 1000C 4
f C 2
1 C 2
g
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+2∥2
i
+
400γ0C 4
f C 2
1 L2
f σ2
B−
.
If we choose η ≤ min

γ2
4LF
, γ0B+
40nCf CgC1
√
L2
f +5C2
f
, γ1
15C2
f CgC1Lf

, we have
−
 1
2 − 2L2
F η2
γ2
2
 1
T
TX
t=1
E
h
∥mt∥2
i
+ 200C 2
f C 2
g C 2
1 L2
f
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+1∥2
i
+
20C 4
f C 2
g C 2
1 L2
f η2
γ2
1
1
T
TX
t=1
E
h
∥mt+1∥2
i
+ 1000C 4
f C 2
1 C 2
g
 nη
γ0B+
2 1
T
TX
t=1
E
h
∥mt+2∥2
i
≤
E
h
∥mT +1∥2
i
+ E
h
∥mT +2∥2
i
8T .
Besides, Lemma 2 in Wang & Yang (2022) and Lemma 11 imply that
E
 1
n ∥Ξ2∥2

≤ E
 1
n ∥Ξ1∥2

+ 5nη2C 2
g
γ0B+
E
h
∥m1∥2
i
+ 2γ2
0 σ2B+
nB−
≤ E
 1
n ∥Ξ1∥2

+ ηCg
8Cf C1
q
L2
f + 5C 2
f
E
h
∥m1∥2
i
+ 2γ2
0 σ2B+
nB−
,
E
 1
n ∥Ξ3∥2

≤ E
 1
n ∥Ξ1∥2

+ ηCg
8Cf C1
q
L2
f + 5C 2
f

E
h
∥m1∥2 + ∥m2∥2
i
+ 4γ2
0 σ2B+
nB−
,
E
h
∥Ψ2∥2
i
≤ E
h
∥Ψ1∥2
i
+ 2Cgη
15C1Lf
∥m1∥2 + 5γ1C 2
f E
 1
n ∥Ξt+1∥2

+
2γ2
1 C 2
f
B+
.
=== página 22 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
If we initialize m1 = 0 , then E
h
∥mt∥2
i
≤ C 2
f C 2
1 for any t ≥ 1. We define that ΛF,1 = E [F (w1) − Finf ] < +∞,
Λ∆,1 = E
h
∥∆1∥2
i
< +∞, ΛΞ,2 = E
h
1
n ∥Ξ2∥2
i
< +∞, ΛΞ,3 = E
h
1
n ∥Ξ2∥2
i
< +∞, Λ2
Ψ = E
h
∥Ψ2∥2
i
< +∞. Then,
1
T
TX
t=1
E
h
∥∇F (wt)∥2
i
≤ 2ΛF,1
ηT + Λ∆,1
γ2T +
40nC 2
f C 2
1 L2
f ΛΞ,2
γ0B+T +
10C 2
f C 2
1 L2
f Λ2
Ψ
γ1T +
200nC 4
f C 2
1 L2
f ΛΞ,3
γ0B+T
+ 2βC 4
f
 
ζ 2
B−
+ C 2
g
B+
!
+
80γ0C 2
f C 2
1 L2
f σ2
B−
+
20γ1C 4
f C 2
1 L2
f
B+
+
400γ0C 4
f C 2
1 L2
f σ2
B−
+
C 2
f C 2
1
4T .
Set γ0 = B−ϵ2
400C2
f C2
1 L2
f σ2(1+5C2
f ), γ1 = B+ϵ2
200C4
f C2
1 L2
f
, γ2 = min{B−,B+}ϵ2
20C4
f (ζ2+C2g ) , and
η ≤ min



γ2
4LF
, γ0B+
40nCf CgC1
q
L2
f + 5C 2
f
, γ1
15C 2
f CgC1Lf


 ,
T = max



1600ΛF,1LF C 4
f (ζ 2 + C 2
g )
min{B−, B+}ϵ4 ,
320000nΛF,1C 3
f CgC 3
1 L2
f (1 + 5C 2
f )
q
L2
f + 5C 2
f σ2
B−B+ϵ4 ,
60000ΛF,1C 6
f CgC 3
1 L3
f
B+ϵ4 ,
200C 4
f (ζ 2 + C 2
g )Λ∆,1
min{B−, B+}ϵ4 ,
160000nC 4
f C 4
1 L4
f σ2(1 + 5C 2
f )Λ2
Ξ
B−B+ϵ4 ,
20000C 6
f C 4
1 L4
f Λ2
Ψ
B+ϵ4 ,
800000nC 6
f C 4
1 L4
f (1 + 5C 2
f )ΛΞ,3σ2
B−B+ϵ4
)
.
Then, we have 1
T
PT
t=1 E
h
∥∇F (wt)∥2
i
≤ ϵ2.
C. Optimization of CVaR-estimator of TPAUC
We have the following estimator
F (w) = min
π∈R
π + 1
n+α
X
xi∈S+
(min
si
si + 1
β ψi(w; si) − π)+, ψ i(w; si) = 1
n−
X
xj ∈S−
(L(w; xi, xj) − si)+.
It is not difficult to show that the above estimator is equivalent to
F (w) = min
π∈R,s∈Rn+
π + 1
n+α
X
xi∈S+
(si + 1
β ψi(w; si) − π)+.
The reason is that (minx f (x) − s)+ = minx(f (x) − s)+. Using the conjugate of [·]+, we have
min
w,s∈Rn+ ,π∈R
max
u∈[0,1]n+
π + 1
n+α
X
xi∈S+
ui(si + 1
β ψi(w; si) − π)
| {z }
F (w,s,π,u)
.
Define Fi(w, si, π, ui) = π + 1
α ui(si + 1
β ψi(w; si) − π) such that F (w, s, π,u) = 1
n+
P
xi∈S+ Fi(w, si, π, ui). Based
on a minibatch B− ⊆ S−, we can estimate Fi(w, si, π, ui) by Fi(w, si, π, ui; B−) := π + 1
α ui(si + 1
β ψi(w; si; B−) − π)
and ψi(w; si; B−) := 1
B−
P
xj ∈B− (L(w; xi, xj) − si)+. We consider the function F (w, s, π,u), which can be proved to
be weakly convex w.r.t. (w, s, π) and concave w.r.t. u. Hence, we can use the stagewise proximal point method to solve the
problem (Rafique et al., 2020). At the k-th stage, we solve the following problem approximately:
min
¯w
max
u∈[0,1]n+
Fk(w, s, π,u) = F (w, s, π,u) + 1
2γ ∥(w, s, π) − (wk,0, sk,0, πk,0)∥2,
=== página 23 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
where vk,0 is the initial value of v in the k-th stage. We will use stochastic primal-dual algorithm for solving Fk. However,
for s we use stochastic coordinate gradient descent update, and for u we also use stochastic coordinate gradient ascent
update. Let ˜gk,t
w , ˜gk,t
s , ˜gk,t
π , ˜gk,t
u denote stochastic estimators of partial gradient of F w.r.t. w, s, π,u, respectively. We
consider the following update:
wk,t+1 = arg min
w

w⊤˜gk,t
w + 1
2η1
∥w − wk,t∥2 + 1
2γ ∥w − wk,0∥2

sk,t+1 = arg min
s

s⊤˜gk,t
s + 1
2η2


s − sk,t

2
2 + 1
2γ


s − sk,0

2
2

,
πk,t+1 = arg min
π

π˜gk,t
π + 1
2η3
|π − πk,t|2 + 1
2γ |π − πk,0|2

uk,t+1 = arg max
u∈[0,1]n+

u⊤˜gk,t
u − 1
2η4


u − uk,t

2
2

,
(21)
Note that different from (Rafique et al., 2020), we use stochastic coordinate descent (ascent) to update st+1 (ut+1). Next,
we present the stochastic estimators of partial gradients. We define Ui ∈ Rn+×1 whose i-th coordinate is 1 while others are
zero. Note that P
xi∈S+ Ui = In+, where In+ is a size-(n+ × n+) identity matrix.
˜gk,t
w = 1
B+B−αβ
X
xi∈Bk,t
+
X
xj ∈Bk,t
−
uk,t
i I(L(wk,t; xi, xj) − sk,t
i > 0)∇L(wk,t; xi, xj),
˜gk,t
s = 1
αB+
X
xi∈Bk,t
+
Uiuk,t
i (1 − 1
B−β
X
xj ∈Bk,t
−
I(L(wk,t; xi, xj) − sk,t
i > 0)),
˜gk,t
π = 1 − 1
B+α
X
xi∈Bk,t
+
uk,t
i ,
˜gk,t
u = 1
αB+
X
xi∈Bk,t
+
Ui(sk,t
i − πk,t + 1
B−β
X
xj ∈Bk,t
−
(L(wk,t; xi, xj) − sk,t
i )+).
Assume max(|πk,t|, |sk,t
i |, L(wk,t; xi, xj), ∥∇L(wk,t; xi, xj)∥) ≤ C. Then, we have
E[˜gk,t
w ] = ∇1F (wk,t, sk,t, πk,t, uk,t), E[∥˜gk,t
w ∥2] ≤ C
α2β2 ,
E[˜gk,t
s ] = ∇2F (wk,t, sk,t, πk,t, uk,t), E[∥˜gk,t
s ∥2] ≤ 1
α2 (1 + 1
β )2,
E[˜gk,t
π ] = ∇3F (wk,t, sk,t, πk,t, uk,t), E[∥˜gk,t
π ∥2] ≤ (1 + 1
α )2,
E[˜gk,t
u ] = ∇4F (wk,t, sk,t, πk,t, uk,t), E[∥˜gk,t
u ∥2] ≤ 4C 2
α2 (1 + 1
β )2.
Let v := (w, s, π). We first show that F (v, u) is weakly convex in terms of v for any u.
Lemma 12. Under Assumption 2, then F (v, u) is ρ/(αβ)-weakly convex in terms of v for any u, where ρ is the smoothness
constant of L(w; xi, xj) w.r.t. w.
Proof. Following similar analysis of Lemma 2, we can show that F (v, u) + ρ
2αβ ∥v∥2 = F (v, u) + 1
n+α
P
i ui( ρ
2β ∥w∥2 +
ρ
2β |si|2 + ρ
2β |π|2) + ρ
2n+αβ
P
i(1 − ui)(∥w∥2 + |si|2 + |π|2) + (n+−1)
2n+αβ ∥s∥2 is jointly convex in terms w, s, πfor any
u ∈ [0, 1]. Then F (v, u) is ρ′ = ρ
αβ -weakly convex in terms of v for any u.
Lemma 13. Consider the proximal gradient update
xt+1 = arg minx⊤Gt + 1
2η ∥x − xt∥2 + g(x),
=== página 24 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Algorithm 4 SOTA
1: for k = 0, . . . , K− 1 do
2: if k = 0 then
3: Set s0,0
i = 0, π0,0 = 0, u0,0
i = 1 and initialize w0,1
4: else
5: Let wk,0 = wk−1, sk,0 = sk−1, πk,0 = πk−1, uk,0 = uk−1
6: end if
7: for t = 0, . . . , Tk − 1 do
8: Sample Bk,t
+ ⊂ S+ and Bk,t
− ⊂ S−
9: Obtain wk,t+1, sk,t+1, πk,t+1, uk,t+1 according to (21)
10: end for
11: Let wk, sk, πk, uk be the average of wk,t, sk,t, πk,t, uk,t, respectively
12: end for
we have
(xt − x)⊤Gt + g(xt) − g(x) + 1
2γ ∥x − xt+1∥2
≤ η∥Gt∥2 + 1
2η (∥x − xt∥2 − ∥x − xt+1∥2) + g(xt) − g(xt+1) − 1
4η ∥xt+1 − xt∥2.
Proof. Due to the update of xt+1, we have
x⊤
t+1Gt + 1
2η ∥xt+1 − xt∥2 + g(xt+1) + ( 1
2η + 1
2γ )∥x − xt+1∥2 ≤ x⊤Gt + 1
2η ∥x − xt∥2 + g(x).
As a result, we have
(xt − x)⊤Gt + g(xt) − g(x) + 1
2γ ∥x − xt+1∥2
≤ (xt − xt+1)⊤Gt + 1
2η (∥x − xt∥2 − ∥x − xt+1∥2) + g(xt) − g(xt+1) − 1
2η ∥xt+1 − xt∥2
≤ η∥Gt∥2 + 1
2η (∥x − xt∥2 − ∥x − xt+1∥2) + g(xt) − g(xt+1) − 1
4η ∥xt+1 − xt∥2.
Theorem 6. Assume there exists C >0 such that max(|s′
t|, |st,i|, L(wt; xi, xj), ∥∇L(wt; xi, xj)∥) ≤ C at every stage.
Let 1/γ ≥ ρ, ηk
1 = ηk
2 = ηk
3 = ηk
4 =∝ 1/k, Tk ∝ n+k2. SOTA ensures that after T = O(n+/ϵ6) iterations we can find an
ϵ-nearly stationary solution for minw,s,s′ F (w, s, s′).
Proof. Let R1(w) := 1
2γ ∥w − wk,0∥2, R2(s) := 1
2γ ∥s − sk,0∥2, and R3(π) = 1
2γ |π − πk,0|2. Apply Lemma 13 to wk,t+1.
(wk,t − w)⊤˜gk,t
w + R1(wt) − R1(w) ≤ η1∥˜gk,t
w ∥2 + 1
2η1
(∥w − wk,t∥2 − ∥w − wk,t+1∥2) + g1(wk,t) − g1(wk,t+1).
Take expectation on both sides conditioned on the randomness that occurred before the t-th iteration in the k-th stage.
(wk,t − w)⊤∇wF (vk,t, uk,t) + R1(wk,t) − R1(w)
≤ η1Et[∥˜gk,t
w ∥2] + 1
2η1
(∥w − wk,t∥2 − Et[∥w − wk,t+1∥2]) + R1(wk,t) − Et[R1(wk,t+1)].
=== página 25 ===
Optimizing Partial AUC for Deep Learning with Convergence Guarantee
Similarly, apply Lemma 13 to sk,t+1
i and πk,t+1 and take the conditional expectations.
(sk,t − s)⊤∇sF (vk,t, uk,t) + R2(sk,t) − R2(s)
≤ η2Et[∥˜gk,t
s ∥2
2] + 1
2η2
(∥s − sk,t∥2 − Et[∥s − sk,t+1∥2]) + R2(sk,t) − Et[R2(sk,t+1)],
(πk,t − π)∇πF (vk,t, uk,t) + R3(πk,t) − R3(π)
≤ η3Et[|˜gk,t
π |2
2] + 1
2η2
(|π − πk,t|2 − Et[|π − πk,t+1|2]) + R3(πk,t) − Et[R3(πk,t+1)].
Note that Fk(vk,t, uk,t)−Fk(v, uk,t) = F (vk,t, uk,t)−F (v, uk,t) + 1
2γ ∥vk,t −vk,0∥2
2 − 1
2γ ∥v −vk,0∥2
2. If 1
γ ≥ ρ′ = ρ
αβ ,
we have Fk(v, u) is convex w.r.t. v such that Fk(vk,t, uk,t) − Fk(v, uk,t) ≤ (vk,t − v)⊤∇vF (vk,t, uk,t) + (vk,t −
v)⊤∇vR(vk,t, uk,t). where R = (R1, R2, R3)⊤. Note that (vk,t − v)⊤∇vR(vk,t, uk,t) = 1
γ (vk,t − v)⊤(vk,t − vk,0) ≥
R(vk,t) − R(v). Adding the above inequalities for w, s, πtogether we have
E[
Tk−1X
t=0
(Fk(vk,t, uk,t) − Fk(v, uk,t))] ≤ η1C 2
1 T + η2C 2
2 T + η3C 2
3 T + 1
2η1
∥w − wk,0∥2 + 1
2η2
∥s − sk,0∥2 + 1
2η3
|π − πk,0|2,
where C 2
1 := C
α2β2 , C 2
2 = 1
α2 (1 + 1/β)2, C 2
3 := (1 + 1/α)2. Applying the same analysis to the update of uk,t, we have
(u − uk,t)⊤˜gk,t
u ≤ η4∥˜gk,t
u ∥2 + 1
2η4
(∥u − uk,t∥2 − ∥u − uk,t+1∥2)
We do not assume u is independent of the randomness in the updates of our algorithm. As a result,
(u − uk,t)⊤∇4F (vt, ut) = η4∥˜gk,t
u ∥2 + 1
2η4
(∥u − uk,t∥2 − ∥u − uk,t+1∥2) + (u − uk,t)⊤(∇4F (vt, ut) − ˜gk,t
u ).
Following previous analysis (e.g., Proposition A.1 in (Rafique et al., 2020)), for an auxiliary sequence {˜uk,t} we have
E[(u − uk,t)⊤(∇4F (vk,t, uk,t) − ˜gk,t
u )]
≤ η4E[∥∇4F (vk,t, uk,t) − ˜gk,t
u ∥2] + 1
2η4
(E[∥u − ˜uk,t∥2] − E[∥u − ˜uk,t+1∥2]).
Hence for any u and ˜uk,0 = uk,0, C 2
4 := 4C2
α2 (1 + 1/β)2, we have
E[Fk(vk,t, u) − Fk(vk,t, uk,t)] ≤ E[
X
t=0
(u − uk,t)⊤∇4F (vt, ut)] ≤ 2η4E[∥˜gk,t
u ∥2] + 1
η4
∥u − uk,0∥2
≤ 2ηC 2
4 + 1
η4
∥u − uk,0∥2.
According to the initialization in Algorithm 4, for any v = (w, s, π) and u we have
E[
Tk−1X
t=0
Fk(vk,t, u) − Fk(v, uk,t)] ≤ η1C 2
1 T + η2C 2
2 T + η3C 2
3 T + 2η4C 2
4
+ 1
2η1
∥wk,0 − w∥2 + 1
2η2
∥s∥2 + 1
2η3
|π|2 + 1
η4
∥u − 1∥2.
Note that ∥s∥2 ≤ n+C 2 and ∥u − 1∥2 ≤ n+. It remains to apply the analysis in (Rafique et al., 2020, Theorem 4.1)
to derive the convergence for the Moreau envelope of F (w, s, π) with a complexity in the order of O(n+/ϵ6) by setting
ηk ∝ 1/k and Tk ∝ n+k2 and the total number of stages K = O(1/ϵ2).
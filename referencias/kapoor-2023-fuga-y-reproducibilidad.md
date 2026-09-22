# Kapoor y Narayanan (2023) — Fuga y crisis de reproducibilidad en ciencia con ML

**Autores:** Sayash Kapoor, Arvind Narayanan.
**Título:** Leakage and the reproducibility crisis in machine-learning-based
science.
**Revista:** Patterns, volumen 4, número 9, artículo 100804.
**Año:** 2023 (septiembre).
**DOI:** 10.1016/j.patter.2023.100804
**PMCID:** PMC10499856 — **PMID:** 37720327
**Fecha de consulta:** 2026-09-21
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/

**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.** *"© 2023 The Author(s) This is an open access article under the CC BY license"* (https://creativecommons.org/licenses/by/4.0/). Verificado el 2026-09-21 en la página del artículo y en el depósito de la editorial en Crossref. Atribución: Kapoor S, Narayanan A, *Patterns* 4(9):100804 (2023), DOI 10.1016/j.patter.2023.100804. **Cambios** respecto del original, como pide la licencia: el texto se extrajo de la versión HTML de PMC con un script que conserva el contenido del elemento `<article>` y quita etiquetas, scripts y botones. **No se omite el resto del armazón del sitio**, que queda mezclado con el artículo: nombres de autor duplicados, afiliaciones repetidas, enlaces "Find articles by…", "Open in a new tab" junto a cada figura, las etiquetas "[DOI]", "[PubMed]", "[PMC free article]" y "[Google Scholar]" tras las referencias, "PMC Copyright notice" y la línea final "Articles from … are provided here courtesy of …". La línea de cita inicial perdió el nombre de la revista. Las figuras 1 a 3 son imágenes y no se reproducen; quedan su número y su leyenda. Se añaden esta cabecera y las secciones marcadas como nuestras. *Hasta el 2026-09-21 esta nota decía que se omitían las afiliaciones desplegables, los botones y los enlaces "Find articles by…", y que las fórmulas en imagen aparecían como "(1)", "(2)"…, marcadores que este texto no contiene; de eso solo era cierto lo de los botones.*

---

## Citas que el proyecto usa

**La taxonomía tiene ocho tipos** — lo dice el propio artículo:

> Based on our survey, we introduce a detailed taxonomy of eight types of
> leakage, ranging from textbook errors to open research problems.

Los ocho son las hojas del árbol: L1.1–L1.4, L2, L3.1–L3.3.

**El tipo que corresponde a la falta de independencia entre entrenamiento y
prueba es [L3.2]**, definición literal:

> [L3.2] Nonindependence between training and test samples. Nonindependence
> between training and test samples constitutes leakage, unless the scientific
> claim is about a distribution that has the same dependence structure. In the
> extreme (but unfortunately common) case, training and test samples come from
> the same people or units.

**Y dónde lo clasifican —importa—:** no bajo L1, *"Lack of clean separation"*,
sino bajo **L3**, la prueba que no sale de la distribución de interés
científico. La fuga por paciente es, para Kapoor y Narayanan, un desajuste
entre lo que se evalúa y lo que se afirma; es la misma idea del caso de uso de
Saeb et al.

> [L3] Test set is not drawn from the distribution of scientific interest. The
> distribution of data on which the performance of an ML model is evaluated
> differs from the distribution of data about which the scientific claims are
> made.

**Qué prescriben** para L3.2:

> The train-test split should account for the dependencies in the data to ensure
> correct performance evaluation.

**Dos tipos más que tocan a este proyecto:**

> [L1.4] Duplicates in datasets. If a dataset with duplicates is used for the
> purposes of training and evaluating an ML model, the same data could exist in
> the training set and the test set.

> [L2] Model uses features that are not legitimate. If the model has access to
> features that should not be legitimately available for use in the modeling
> exercise, this could result in leakage.

*Lectura nuestra, no del artículo:* L2 es la clase del hallazgo de
`auditoria-de-fugas` —las columnas que solo existen en entrenamiento—, y L1.4
la de los duplicados que documenta
`referencias/cassidy-2022-duplicados-isic.md` en ediciones anteriores del ISIC.

---

## Texto original

. 2023 Aug 4;4(9):100804. doi: 10.1016/j.patter.2023.100804

Leakage and the reproducibility crisis in machine-learning-based science

Sayash Kapoor
Sayash Kapoor

1Department of Computer Science and Center for Information Technology Policy, Princeton University, Princeton, NJ 08540, USA

Find articles by Sayash Kapoor

1,2,∗, Arvind Narayanan
Arvind Narayanan

1Department of Computer Science and Center for Information Technology Policy, Princeton University, Princeton, NJ 08540, USA

Find articles by Arvind Narayanan

1

1Department of Computer Science and Center for Information Technology Policy, Princeton University, Princeton, NJ 08540, USA

∗Corresponding author sayashk@princeton.edu

2Lead contact

Received 2023 Mar 3; Revised 2023 May 18; Accepted 2023 Jul 5; Collection date 2023 Sep 8.

© 2023 The Author(s)

This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

PMC Copyright notice

PMCID: PMC10499856 PMID: 37720327

Summary

Machine-learning (ML) methods have gained prominence in the quantitative sciences. However, there are many known methodological pitfalls, including data leakage, in ML-based science. We systematically investigate reproducibility issues in ML-based science. Through a survey of literature in fields that have adopted ML methods, we find 17 fields where leakage has been found, collectively affecting 294 papers and, in some cases, leading to wildly overoptimistic conclusions. Based on our survey, we introduce a detailed taxonomy of eight types of leakage, ranging from textbook errors to open research problems. We propose that researchers test for each type of leakage by filling out model info sheets, which we introduce. Finally, we conduct a reproducibility study of civil war prediction, where complex ML models are believed to vastly outperform traditional statistical models such as logistic regression (LR). When the errors are corrected, complex ML models do not perform substantively better than decades-old LR models.

Keywords: reproducibility, machine learning, leakage

Highlights

•Data leakage is a flaw in machine learning that leads to overoptimistic results

•Our survey of prior reviews shows leakage affects 294 papers across 17 scientific fields

•We provide a taxonomy of leakage and introduce model info sheets to mitigate it

•We show how leakage can lead to overoptimism with a case study on civil war prediction

The bigger picture

Machine learning (ML) is widely used across dozens of scientific fields. However, a common issue called “data leakage” can lead to errors in data analysis. We surveyed a variety of research that uses ML and found that data leakage affects at least 294 studies across 17 fields, leading to overoptimistic findings. We classified these errors into eight different types. We propose a solution: model info sheets that can be used to identify and prevent each of these eight types of leakage. We also tested the reproducibility of ML in a specific field: predicting civil wars, where complex ML models were thought to outperform traditional statistical models. Interestingly, when we corrected for data leakage, the supposed superiority of ML models disappeared: they did not perform any better than older methods. Our work serves as a cautionary note against taking results in ML-based science at face value.

Kapoor and Narayanan show that leakage is a widespread failure mode in machine-learning (ML)-based science. Based on a survey of past reviews, they find that it affects at least 294 papers across 17 disciplines. They provide a taxonomy of eight types of leakage and propose model info sheets to mitigate it. They show that leakage can lead to severe overoptimism through a case study of civil war prediction. Several papers claimed that ML models drastically outperform older regression models. This is no longer the case when leakage is fixed.

Introduction

There has been a marked shift toward the paradigm of predictive modeling across quantitative science fields. This shift has been facilitated by the widespread use of machine learning (ML) methods. However, pitfalls in using ML methods have led to exaggerated claims about their performance. Such errors can lead to a feedback loop of overoptimism about the paradigm of prediction, especially because non-replicable publications tend to be cited more often than replicable ones.1 It is therefore important to examine the reproducibility of findings in communities adopting ML methods.

Scope. We focus on reproducibility issues in ML-based science, which involves making a scientific claim using the performance of the ML model as evidence. There is a better-known reproducibility crisis in research that uses traditional statistical methods.2 We also situate our work in contrast with other ML domains, such as methods research (creating and improving widely applicable ML methods), ethics research (studying the ethical implications of ML methods), engineering applications (building or improving a product or service), and modeling contests (improving predictive performance on a fixed dataset created by an independent third party). Investigating the validity of claims in all these areas is important, and there is ongoing work to address reproducibility issues in these domains.3,4,5,6

We define a research finding as reproducible if the code and data used to obtain the finding are available and the data are correctly analyzed.4,7,8 This is a broader definition than computational reproducibility, when the results in a paper can be replicated using the exact code and dataset provided by the authors (see supplemental experimental procedures, section S1).

Leakage. Data leakage is a spurious relationship between the independent variables and the target variable that arises as an artifact of the data collection, sampling, or pre-processing strategy. Because the spurious relationship will not be present in the distribution about which scientific claims are made, leakage usually leads to inflated estimates of model performance.

Data leakage has long been recognized as a leading cause of errors in ML applications.9 In formative work on leakage, Kaufman et al.10 provide an overview of different types of error and give several recommendations for mitigating these errors. Since this paper was published, the ML community has investigated leakage in several engineering applications and modeling competitions.11,12,13,14,15 However, leakage occurring in ML-based science has not been comprehensively investigated. As a result, mitigations for data leakage in scientific applications of ML remain understudied.

In this paper, we systematically investigate reproducibility issues in ML-based science as a result of data leakage. Our main contributions are as follows:

1. A survey and taxonomy of reproducibility issues caused by leakage. We provide evidence for a growing reproducibility crisis in ML-based science. Through a survey of literature in research communities that adopted ML methods, we find 22 papers across 17 fields where leakage has been found, collectively affecting 294 papers (Figure 1). We highlight that data leakage mitigation strategies developed for other ML applications, such as modeling contests and engineering applications, often do not translate to ML-based science. Based on our survey, we present a fine-grained taxonomy of eight types of leakage that range from textbook errors to open research problems.

Figure 1.

Open in a new tab

Survey of 22 papers that identify pitfalls in the adoption of ML methods across 17 fields, collectively affecting 294 papers

In each field, papers adopting ML methods suffer from data leakage. The column headings for types of data leakage, shown in bold, are based on our taxonomy of data leakage. We also highlight other issues that are reported in the papers: (1) computational reproducibility (the lack of availability of code, data, and computing environment to reproduce the exact results reported in the paper); (2) data quality (e.g., small size or large amounts of missing data); (3) metric choice (using incorrect metrics for the task at hand, e.g., using accuracy for measuring model performance in the presence of heavy class imbalance); and (4) standard dataset use, where issues are found despite the use of standard datasets in a field.16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37

2. Model info sheets to detect and prevent leakage. Current standards for reporting model performance in ML-based science often fall short in addressing issues caused by leakage. Specifically, checklists and model cards are one way to provide standard best practices for reporting details about ML models.38,39,40 However, current efforts do not address issues arising because of leakage. Further, most checklists currently in use are not developed for ML-based science in general but rather for specific scientific or research communities.4,38 As a result, best practices for model reporting in ML-based science are underspecified.

We introduce model info sheets to detect and prevent leakage in ML-based science. They are inspired by the model cards in Mitchell et al.40 Filling out a model info sheet requires the researcher to provide precise arguments to justify that models used for making scientific claims do not suffer from leakage, by answering 21 questions based on our taxonomy of leakage.

3. An empirical case study of leakage in civil war prediction. For an in-depth look at the impact of reproducibility errors, we undertake a reproducibility study in civil war prediction, a subfield of political science where ML models are believed to vastly outperform older statistical models such as logistic regression (LR). We perform a systematic review to find papers on civil war prediction and find that all papers in our review claiming the superior performance of complex ML models compared with KR models fail to reproduce because of data leakage.

Each of these papers was published in top political science journals. Leakage affects complex ML models, as well as simpler LR models. But when the errors caused by leakage are corrected, ML models no longer perform substantively better than decades-old LR models.

Results

Evidence of a reproducibility crisis

Many scientific fields have adopted ML methods and the paradigm of predictive modeling.41,42,43,44,45,46 We find at least three main uses of ML models in scientific literature. First, models that are better at prediction are thought to enable an improved understanding of scientific phenomena.47 Second, especially when used in medical fields, models with higher predictive accuracy can aid in research and development of better diagnostic tools.48 Finally, ML-based methods have also been used to investigate the inherent predictability of phenomena, especially for predicting social outcomes.49 The increased adoption of ML methods in science motivates our investigation of reproducibility issues in ML-based science.

Data leakage causes irreproducible results

Researchers in many communities have already documented reproducibility failures in ML-based science within their fields. Here we conduct a cross-disciplinary analysis by building on these individual reviews. This enables us to highlight the scale and scope of the crisis, identify common patterns, and make progress toward a solution.

When searching for past literature that documents reproducibility failures in ML-based science, we found that different fields often use different terms to describe pitfalls and errors. This makes it difficult to conduct a systematic search to find papers with errors. Therefore, we do not present our results as a systematic meta-review of leakage from a coherent sample of papers but rather as a lower bound of reproducibility issues in ML-based science. In addition, most reviews look only at the content of the papers and not the code and data provided with the papers to check for errors. This leads to under-counting the number of affected papers, because the code might have errors that are not apparent from reading the papers.

We find 22 papers from 17 fields that outline errors in ML-based science in their field, collectively affecting 294 papers. A prominent finding that emerges is that data leakage is a pitfall in every single case. Our findings present a worrying trend for the reproducibility of ML-based science.

Note that leakage is one of many causes of irreproducible results. Other factors, such as the lack of available code and data, can also lead to irreproducibility, and there are several studies investigating these shortcomings.50,51 We discuss our choice of terminology in detail in the supplemental experimental procedures (section S1).

The results from our survey are presented in Figure 1. Columns in bold represent different types of leakage. The last four columns represent other common trends in the papers we study. For systematic reviews, we report the number of papers reviewed. Each paper in our survey highlights issues with leakage, with six papers highlighting the presence of multiple types of leakage in their field.

Data leakage mitigations for other ML applications do not apply to scientific research

Most previous research and writing on data leakage has focused on mitigating data leakage in engineering settings or predictive modeling competitions.10,11,12 However, the taxonomy of data leakage outlined in this body of work does not address all types of leakage that we identify in our survey. In particular, we find that leakage can result from a difference between the distribution of the test set and the distribution of scientific interest. Robustness to distribution shift is an area of ongoing research in ML methods and is as such an open problem.52 In addition, these settings are very different from scientific research, and mitigations for data leakage in modeling competitions, as well as engineering applications of ML, often do not translate into strategies for mitigating data leakage in ML-based science.

Leakage in modeling competitions

In predictive modeling competitions, dataset creation and model evaluation are left to impartial third parties who have the expertise and incentives to avoid errors. Within this framework, none of the participants have access to the held-out evaluation set before the competition ends. In contrast, in most ML-based science, the researcher has access to the entire dataset while creating the ML models. Leakage often occurs because of the researcher having access to the entire dataset during the modeling process.

Leakage in engineering applications

Leakage in real-world applications has led to exaggerated performance estimates, even in consequential settings such as child maltreatment prediction.53 One of the most common recommendations for detecting and mitigating leakage is to deploy the ML model at a limited scale in production. This advice is applicable only to engineering applications of ML, where the end goal is not to gain insights about a particular process but rather to serve as a component in a product. Often, a rough idea of model performance is enough to decide whether a model is good enough to be deployed in a product. Contrarily, ML-based science involves making a scientific claim using the performance of the ML model as evidence. In addition, engineering applications of ML often operate in a rapidly changing context and have access to large datasets, so small differences in performances are often not as important, whereas scientific claims are sensitive to small performance differences between ML models.

Why do we call it a reproducibility crisis?

We say that ML-based science is suffering from a reproducibility crisis for two related reasons. First, our results show that reproducibility failures in ML-based science are systemic. In nearly every scientific field that has carried out a systematic study of reproducibility issues, papers are plagued by common pitfalls. In many systematic reviews, a majority of the papers reviewed suffer from these pitfalls. Similar problems are likely to arise in many fields that are adopting ML methods. Second, despite the urgency of addressing reproducibility failures, there are no systemic solutions that have been deployed for these failures. Scientific communities are discovering the same failure modes across disciplines but have yet to converge on best practices for avoiding reproducibility failures.

Calling attention to and addressing these widespread failures is vital to maintaining public confidence in ML-based science. At the same time, the use of ML methods is still in its infancy in many scientific fields. Addressing reproducibility failures pre-emptively in such fields can correct a lot of scientific research that would otherwise be flawed.

Toward a solution: A taxonomy of data leakage

We now provide our taxonomy of data leakage errors in ML-based science. Such a taxonomy can enable a better understanding of why leakage occurs and inform potential solutions. Our taxonomy is comprehensive and addresses data leakage arising during the data collection, pre-processing, modeling, and evaluation steps. In particular, our taxonomy addresses all cases of data leakage that we found in our survey (Figure 1). Some of the categories in our taxonomy, e.g., sampling bias [L3.3], were not considered types of leakage in prior work, but they have the same cause as other categories of leakage: spurious correlations between the outcome variables and the features. They also have the same effect: they lead to overestimates of model performance.

[L1] Lack of clean separation of training and test dataset. If the training dataset is not separated from the test dataset during all pre-processing, modeling, and evaluation steps, the model has access to information in the test set before its performance is evaluated. Because the model has access to information from the test set at training time, the model learns relationships between the predictors and the outcome that would not be available in additional data drawn from the distribution of interest. The performance of the model on these data therefore does not reflect how well the model would perform on a new test set drawn from the same distribution of data. This can happen in several ways, such as:

[L1.1] No test set. Using the same dataset for training and testing the model is a textbook example of overfitting, which leads to overoptimistic performance estimates.54

[L1.2] Pre-processing on training and test set. Using the entire dataset for any pre-processing steps, such as imputation or over/under sampling, results in leakage. For instance, using oversampling before splitting the data into training and test sets leads to an imperfect separation between the training and test sets because data generated using oversampling from the training set will also be present in the test set.

[L1.3] Feature selection on training and test set. Feature selection on the entire dataset results in using information about which feature performs well on the test set to make a decision about which features should be included in the model.

[L1.4] Duplicates in datasets. If a dataset with duplicates is used for the purposes of training and evaluating an ML model, the same data could exist in the training set and the test set.

[L2] Model uses features that are not legitimate. If the model has access to features that should not be legitimately available for use in the modeling exercise, this could result in leakage. One instance when this can happen is if a feature is a proxy for the outcome variable.10 For example, Filho et al.55 find that a recent study included the use of anti-hypertensive drugs as a feature for predicting hypertension. Such a feature could lead to leakage because the model would not have access to this information when predicting the health outcome for a new patient. Further, if the fact that a patient uses anti-hypertensive drugs is already known at prediction time, the prediction of hypertension becomes a trivial task.

The judgment of whether the use of a given feature is legitimate for a modeling task requires domain knowledge and can be highly problem specific. As a result, we do not provide sub-categories for this sort of leakage. Instead, we suggest that researchers clearly specify which features are suitable for a modeling task and justify their choice using domain expertise.

[L3] Test set is not drawn from the distribution of scientific interest. The distribution of data on which the performance of an ML model is evaluated differs from the distribution of data about which the scientific claims are made. The performance of the model on the test set does not correspond to its performance on data drawn from the distribution of scientific interest.

[L3.1] Temporal leakage. When an ML model is used to make predictions about a future outcome of interest, the test set should not contain any data from a date before the training set. If the test set contains data from before the training set, the model is built using data “from the future” that it should not have access to during training and can cause leakage.

[L3.2] Nonindependence between training and test samples. Nonindependence between training and test samples constitutes leakage, unless the scientific claim is about a distribution that has the same dependence structure. In the extreme (but unfortunately common) case, training and test samples come from the same people or units. For example, Oner et al.56 find that a recent study on histopathology uses different observations of the same patient in the training and test sets. In this case, the scientific claim is being made about the ability to predict gene mutations in new patients; however, it is evaluated on data from old patients (i.e., data from patients in the training set), leading to a mismatch between the test set distribution and the scientific claim. Similarly, for predicting protein function, the family of the protein can lead to dependencies if proteins from the same family are split across the training and test sets.57 The train-test split should account for the dependencies in the data to ensure correct performance evaluation. Methods such as “block cross-validation” can partition the dataset strategically so that the performance evaluation does not suffer from data leakage and overoptimism.58,59 Handling nonindependence between the training and test sets in general (i.e., without any assumptions about independence in the data) is a hard problem, because we might not know the underlying dependency structure of the task in many cases.60

[L3.3] Sampling bias in test distribution. Sampling bias in the choice of test dataset can lead to data leakage. One example of sampling bias is spatial bias, which refers to choosing the test data from a geographic location but making claims about model performance in other geographic locations. Another example is selection bias, which entails choosing a non-representative subset of the dataset for evaluation. For example, Bone et al.61 highlight that in a study on predicting autism using ML models, excluding the data corresponding to borderline cases of autism leads to leakage because the test set is no longer representative of the general population about which claims are made. In addition, borderline cases of autism are often the trickiest to diagnose, so excluding them from the evaluation set is likely to lead to overoptimistic results. Cases of leakage caused by sampling bias can often be subtle. For example, Zech et al.62 find that models for pneumonia prediction trained on images from one hospital do not generalize to images from another hospital because of subtle differences in how images are generated in each hospital.

A model may have leakage when the distribution about which the scientific claim is made does not match the distribution from which the evaluation set is drawn. ML models may also suffer from a related but distinct limitation: the lack of generalization when we try to apply a result about one population to another similar but distinct population. Several issues with the generalization of ML models operating under a distribution shift have been highlighted in ML methods research, such as fragility toward adversarial examples,63 image distortion and texture,64 and overinterpretation.65 Robustness to distribution shift is an ongoing area of work in ML methods research. Even slight shifts in the target distribution can cause performance estimates to change drastically.66 Despite ongoing work to create ML methods that are robust to distribution shift, best practices to deal with distribution shift currently include testing the ML models on the data from the distribution we want to make claims about.52 In ML-based science, where the aim is to create generalizable knowledge, we should take results that claim to generalize to a different population from the one models were evaluated on with caution.

Other issues identified in our survey

Computational reproducibility issues

Computational reproducibility of a finding refers to sharing the complete code and data needed to reproduce the findings reported in a paper exactly. This is important to enable external researchers to reproduce results and verify their correctness. Five papers in our survey outlined the lack of computational reproducibility in their field.

Data quality issues

Access to good-quality data is essential for creating ML models.67,68 Issues with the quality of the dataset could affect the results of ML-based science. Ten papers in our survey highlighted data quality issues such as not addressing missing values in the data, the small size of datasets compared with the number of predictors, and the outcome variable being a poor proxy for the phenomenon being studied.

Metric choice issues

A mismatch between the metric used to evaluate performance and the scientific problem of interest leads to issues with performance claims. For example, using accuracy as the evaluation metric with a heavily imbalanced dataset leads to overoptimistic results, because the model can get a high accuracy score by always predicting the majority class. Four papers in our survey highlighted metric choice issues.

Use of standard datasets

Reproducibility issues arose despite the use of standard, widely used datasets, often because of the lack of standard modeling and evaluation procedures such as fixing the train-test split and evaluation metric for the dataset. Seven papers in our survey highlighted that issues arose despite the use of standard datasets.

Model info sheets for detecting and preventing leakage

Our taxonomy of data leakage highlights several failure modes that are prevalent in ML-based science. To detect cases of leakage, we provide a template for a model info sheet to accompany scientific claims using predictive modeling as a supplemental document (supplemental experimental procedures, section S4). The template consists of 21 questions that elicit precise arguments needed to justify the absence of leakage.

Prior work on model cards and reporting standards

Our proposal is inspired by prior work on model cards and checklists, which we now review. Mitchell et al.40 introduced model cards for reporting details about ML models, with a focus on precisely reporting the intended use cases of ML models. They also addressed fairness and transparency concerns: they require that the performance of ML models on different groups of users (e.g., on the basis of race, gender, and age) is reported and documented transparently. These model cards complement the datasheets introduced by Gebru et al.69 to document details about datasets in a standard format.

The use of checklists has also been impactful in improving reporting practices in the few fields that have adopted them.70 Although checklists and model cards provide concrete best practices for reporting standards,38,39,40,71 current efforts do not address pitfalls arising because of leakage. Further, even though several scientific fields, especially those related to medicine, have adopted checklists to improve reporting standards, most checklists are developed for specific scientific or research communities instead of ML-based science in general.

Scientific arguments to surface and prevent leakage

When ML models are used to make scientific claims, it is not enough to simply separate the training and test sets and report performance metrics on the test set. Unlike research in ML methods, where a model’s performance on a hypothetical task (i.e., one that is not linked to a specific scientific claim) is still of interest to the researcher in some cases,72 in ML-based science, claims about a model’s performance need to be connected to scientific claims using explicit arguments. The burden of proof for ensuring the correctness of these arguments is on the researcher making the scientific claims.73

In our model info sheet, we ask researchers to answer 21 questions. These questions help them present three arguments that are essential for determining that scientific results that use ML methods do not suffer from data leakage. Note that most ML-based science papers do not present any of the three arguments, although they sometimes partially address the first argument (clean train-test separation) by reporting out-of-sample prediction performance. The arguments below are based on our taxonomy of data leakage issues and inform the main sections of the model info sheet.

[L1] Clean train-test separation. The researcher needs to argue why the test set does not interact with training data during any of the pre-processing, modeling, or evaluation steps to ensure a clean train-test separation.

[L2] Each feature in the model is legitimate. The researcher needs to argue why each feature used in their model is legitimate, i.e., a claim made using each feature is of scientific interest. Note that some models might use hundreds of features. In such cases, it is even more important to reason about the correctness of the features used, because the incorrect use of a single feature in the model can cause leakage. That said, the same argument for why a feature is legitimate can often apply to a whole set of features. For example, for a study using individuals’ location history as a feature vector, the use of the entire vector can be justified together. Note that we do not ask for the researcher to list each feature used in their model; rather, we ask that the justification provided for the legitimacy of the features used in their model should cover every feature used in their model.

[L3] Test set is drawn from the distribution of scientific interest. If the distribution about which the scientific claims are made is different from the one on which the model is tested, then any claims about the performance of an ML model on the evaluation step fall short. The researcher needs to justify that the test set is drawn from the distribution of scientific interest and there is no selection or sampling bias in the data collection process. This step can help clarify the distribution regarding which scientific claims are being made and detect temporal leakage.

Model info sheets and our theory of change

Model info sheets can influence research practices in two ways: first, researchers who introduce a scientific model alongside a paper can use model info sheets to detect and prevent leakage in their models. These info sheets can be included as supplementary materials with their paper for transparently reporting details about their models. In scientific fields where the use of ML methods is not yet widespread, using transparent reporting practices at an early stage could enable easier adoption and more trust in ML methods. This would also help assuage reviewer concerns about reproducibility.

Second, journal submission guidelines could encourage or require authors to fill out model info sheets if a paper does not transparently report how the model was created. In this case, model info sheets can be used to start a conversation between authors and reviewers about the details of the models introduced in a paper. Current peer-review practices often do not require the authors to disclose any code or data during the review process.74 Even if the code and data are available to reviewers, reproducing results and spotting errors in code is a time-consuming process that often cannot be carried out under current peer-review practices. Model info sheets offer a middle ground: they could enable a closer scrutiny of methods without making the process onerous for reviewers.

Limitations of model info sheets

Although model info sheets can enable the detection of all types of leakage we identify in our survey, they suffer from limitations owing to the lack of computational reproducibility of results in scientific research, incorrect claims made in model info sheets, and the lack of expertise of authors and reviewers.

First, the claims made in model info sheets cannot be verified in the absence of computational reproducibility. That is, unless the code, data, and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain whether model info sheets are filled out correctly. Ensuring the computational reproducibility of results therefore remains an important goal for improving scientific research standards.

Second, incorrect claims made in model info sheets might provide false assurances to reviewers about the correctness of the claims made in a paper. However, by requiring authors to precisely state details about their modeling process, model info sheets enable incorrect claims to be challenged more directly than in status quo, where details about the modeling process are often left undisclosed.

Filling out and evaluating model info sheets requires some expertise in ML. In fields where both authors and reviewers lack any ML expertise, subtle cases of leakage might slip under the radar despite the use of model info sheets. In such cases, we hope that model info sheets released publicly along with papers will enable discourse within scientific communities on the shortcomings of scientific models.

Finally, we acknowledge that our understanding of leakage may evolve, and model info sheets may need to evolve with it. To that end, we have versioned model info sheets, and plan to update them as we continue to better understand leakage in ML-based science.

A case study of civil war prediction

To understand the impact of data leakage, we undertake a reproducibility study in a field where ML models are believed to vastly outperform older statistical models such as LR for predictive modeling: civil war prediction.

Over the last few years, this field has switched to predictive modeling using complex ML models such as Random Forests and Adaboost instead of LR (see Figure 2), with several papers claiming near-perfect performance of these models for civil war prediction.75,76,77,78 The goal of these papers is to predict civil war in a region and time period using features such as GDP, poverty rates, whether it is a democracy, etc. This is in contrast with the field’s earlier focus on understanding and explaining past conflicts. Table S6 gives an overview of the training data used for the papers we considered. For a detailed overview of the recent turn to predictive modeling in this field, see Bara.79

Figure 2.

Open in a new tab

The sharp increase in civil war papers that use ML methods in the last few years

The number of political science papers containing the terms “civil war” and “machine learning” in the dimensions database of academic research.104

Although the literature we reviewed in our survey highlighted the pitfalls in adopting ML methods (Figure 1), we go further than most previous research to investigate whether the claims made in the reviewed studies survive once the errors are corrected.

Systematic search of predictive modeling literature in civil war research

We conducted a systematic search to find relevant literature (detailed in supplemental experimental procedures, section S2.1). This yielded 124 papers. We narrowed this list to the 12 papers that focused on predicting civil war, evaluated performance using a train-test split, and shared the complete code and data. For these 12, we attempted to identify errors and reproducibility issues from the text and by reviewing the code provided with the papers. When we identified errors, we re-analyzed the data with the errors corrected.

Finding 1: Data leakage causes irreproducible results

We present our results in Figure 3. We found errors in 4 of the 12 papers—exactly the 4 papers that claimed superior performance of complex ML models over baseline LR models for predicting civil war. Each paper suffered from different forms of leakage. All 4 papers were published in top-10 journals in the fields of political science and international relations.80 When the errors are corrected, complex ML models perform no better than baseline LR models in each case except Wang,77 where the difference between the area under the curve (AUC) of the complex ML models and LR models drops from 0.14 to 0.01. This is despite the fact that the LR models were not trained to optimize predictive accuracy: they were conceived as explanatory models to understand past conflicts instead of predicting future ones.47,81,82

Figure 3.

Open in a new tab

A comparison of reported and corrected results in civil war prediction papers published in top political science journals

The main findings of each of these papers are invalid due to various forms of data leakage: Muchlinski et al.75 impute the training and test data together, Colaresi and Mahmood76 and Wang77 incorrectly reuse an imputed dataset, and Kaufman et al.78 use proxies for the target variable that cause data leakage. When we correct these errors, complex ML models (such as Adaboost and Random Forests) do not perform substantively better than decades-old logistic regression models for civil war prediction in each case. Each column in the table outlines the impact of leakage on the results of a paper. The figure above each column shows the difference in performance that results from fixing leakage.

We test our model info sheets on the four civil war prediction papers with errors and find that they would detect each type of leakage we identified in these papers (supplemental experimental procedures, section S3). Note that leakage affects both simple and complex models for civil war prediction. However, because of higher model capacity, complex ML models tend to over-fit to spurious correlations more easily in this case (supplemental experimental procedures, section S2.2).

Beyond reproducibility, our results show that complex ML models are not substantively better at civil war prediction than decades-old LR models. This is consistent with similar sobering findings in other tasks involving predicting social outcomes, such as children’s life outcomes49 and recidivism.83 Although prior work has found that some fields will benefit from the use of ML methods,84 our findings suggest the need for tempering the optimism about predictive modeling in the field of civil war prediction and question the use of ML models in this field. We provide a detailed overview of our methodology for correcting the errors and show that our results hold under several robustness checks in the supplemental experimental procedures, section S2.

Finding 2: No significance testing or uncertainty quantification

We found that 9 of the 12 papers for which complete code and data were available included no significance tests or uncertainty quantification for classifier performance comparison (Table S6). Especially when sample sizes are small, significance testing and uncertainty quantification are important steps toward reproducibility.48,85 As an illustration, we examine this issue in detail in the case of Blair and Sambanis86 because their test dataset has a particularly small number of instances of civil war onset (only 11). They propose a model of civil war onset that uses theoretically informed features and report that it outperforms other baseline models of civil war onset using the AUC metric on an out-of-sample dataset. We find that the performance of their model is not significantly better than other baseline models for civil war prediction (Z = 0.64, 1.09, 0.42, and 0.67; p = 0.26, 0.14, 0.34, and 0.25 for a one-tailed significance test comparing the smoothed AUC performance of the model proposed in the paper—the escalation model—with other baseline models reported in their paper—quad, goldstein, cameo, and average, respectively). We implement the comparison test for smoothed receiver operating characteristic curves detailed by Robin et al.87 Note that we do not correct for multiple comparisons; such a correction would further reduce the significance of the results. Further, all models have large confidence intervals for their out-of-sample performance. For instance, while the smoothed AUC performance reported by the authors is 0.85, the 95% confidence interval calculated using bootstrapped test set re-sampling is 0.66–0.95.

Lack of standard reporting practices for ML-based science

Our hypothesis for why leakage is prevalent is that current standards for reporting model performance in ML-based science often fall short in addressing leakage. Specifically, checklists and model cards are one way to provide standard best practices for reporting details about ML models.38,39,40 However, current efforts do not address issues arising because of leakage. Further, most checklists currently in use are not developed for ML-based science in general but rather for specific scientific or research communities.4,38 As a result, best practices for model reporting in ML-based science are underspecified.

Discussion

Beyond leakage: Perspectives on enhancing the reproducibility of ML-based science

We found a number of other reproducibility issues in our survey not limited to leakage. Here, we present five diagnoses for reproducibility failures in fields adopting ML methods. Each of our diagnoses is paired with a recommendation to address it.

[D1] Lack of understanding of the limits to prediction. Recent research for predicting social outcomes has shown that even with complex models and large datasets, there are strong limits to predictive performance.49,83 However, results such as the better-than-human performance of ML models in perception tasks such as image classification88,89 give the impression of ML models surpassing human performance across tasks, which can confuse researchers about the performance they should realistically expect from ML models.

[R1] Understand and communicate limits to prediction. A research agenda that investigates the efficacy of ML models in tasks across scientific fields would increase our understanding of the limits to prediction. This can alleviate the overoptimism that arises from confusing progress in one task (e.g., image classification) with another (e.g., predicting social outcomes). If we can identify upper bounds on the predictive accuracy of tasks (i.e., lower bound of the Bayes Error Rate for a task), then once the achievable accuracy has been reached, we can avoid a futile effort to increase it further and can apply increased skepticism toward results that claim to violate known bounds.

[D2] Hype, overoptimism, and publication biases. The hype about commercial AI applications can spill over into ML-based science, leading to overoptimism about their performance. Non-replicable findings are cited more than replicable ones,1 which can result in feedback loops of overoptimism in ML-based science. Besides, publication biases that have been documented in several scientific fields90,91 can also affect ML-based science.92,93

[R2] Treat results from ML-based science as tentative. When overoptimism is prevalent in a field, it is important to engage with results emerging from the field critically. Until reproducibility issues in ML-based science are widely addressed and resolved, results from this body of work should be treated with caution. Researchers, journal editors, and policymakers who use scientific research to inform real-world policy decisions should look beyond headline performance numbers when assessing papers.

[D3] Inadequate expertise. The rapid adoption of ML methods in a scientific field can lead to errors. These can be caused by the lack of expertise of domain experts in using ML methods and vice versa.

[R3] Interdisciplinary collaborations and communication of best practices. Literature in the ML community should address the different failure modes that arise during the modeling process. Researchers with expertise in ML methods should clearly communicate best practices in deploying ML for scientific research.94 Having an interdisciplinary team consisting of researchers with domain expertise and ML expertise can avoid errors.

[D4] Lack of standardization. Several applied ML fields, such as engineering applications and modeling contests, have adopted practices such as standardized train-test splits, evaluation metrics, and modeling tasks to ensure the validity of the modeling and evaluation process.95,96 However, these have not yet been adopted widely in ML-based science. This leads to subtle errors in the modeling process that can be hard to detect.

[R4] Adopt the common task framework when possible. The common task framework allows us to compare the performance of competing ML models using an agreed-upon training dataset and evaluation metrics, a secret holdout dataset, and a public leaderboard.97,98 Dataset creation and model evaluation are left to impartial third parties who have the expertise and incentives to avoid errors. However, one undesirable outcome that has been observed in communities that have adopted the common task framework is a singular focus on optimizing a particular accuracy metric to the exclusion of other scientific and normatively desirable properties of models.67,85,99

[D5] Lack of computational reproducibility. The lack of computational reproducibility hinders verification of results by independent researchers. Although computational reproducibility does not mean that the code is error free, it can make the process of finding errors easier, because researchers attempting to reproduce results do not have to spend time getting the code to run.

[R5] Ensure computational reproducibility. Platforms such as CodeOcean,100 a cloud computing platform that replicates the exact computational environment used to create the original results, can be used to ensure the long-term reproducibility of results. We follow several academic journals and researchers in recommending that future research in fields using ML methods should use similar methods to ensure computational reproducibility.74,101

Conclusions

The attractiveness of adopting ML methods in scientific research is in part due to the widespread availability of off-the-shelf tools to create models without expertise in ML methods.102 However, this laissez-faire approach leads to common pitfalls spreading to all scientific fields that use ML. So far, each research community has independently rediscovered these pitfalls. Without fundamental changes to research and reporting practices, we risk losing public trust because of the severity and prevalence of the reproducibility crisis across disciplines. Our paper is a call for interdisciplinary efforts to address the crisis by developing and driving the adoption of best practices for ML-based science. Model info sheets for detecting and preventing leakage are a first step in that direction.

Experimental procedures

Resource availability

Lead contact

Further information and requests for resources should be directed to and will be fulfilled by the lead contact, Sayash Kapoor (sayashk@princeton.edu).

Materials availability

This study did not generate new materials.

Acknowledgments

We are grateful to Jessica Hullman, Matthew J. Salganik, and Brandon Stewart for their valuable feedback on drafts of this paper. We thank Robert Blair, Aaron Kaufman, David Muchlinski, and Yu Wang for their quick and helpful responses to drafts of this paper. We are especially thankful to Matthew Sun, who reviewed our code and provided helpful suggestions and corrections for ensuring the computational reproducibility of our own results, and to Angelina Wang, Orestis Papakyriakopolous, and Anne Kohlbrenner for their feedback on model info sheets. This material is based upon work supported by the National Science Foundation under grant NSF IIS-1763642.

Author contributions

S.K. and A.N. contributed to all aspects of this paper.

Declaration of interests

The authors declare no competing interests.

Published: August 4, 2023

Footnotes

Supplemental information can be found online at https://doi.org/10.1016/j.patter.2023.100804.

Supplemental information

Document S1. Supplemental experimental procedures, Figures S1–S3, and Tables S1–S6

mmc1.pdf (684.4KB, pdf)

Document S2. Article plus supplemental information

mmc2.pdf (3.4MB, pdf)

Data and code availability

The code and data required to reproduce our case study on civil war prediction have been uploaded to a CodeOcean capsule (CodeOcean: https://doi.org/10.24433/CO.4899453.v1).103 The supplemental experimental procedures (section S2) contains a detailed description of our methods and results from additional robustness checks.

References

1.Serra-Garcia M., Gneezy U. Nonreplicable publications are cited more than replicable ones. Sci. Adv. 2021;7 doi: 10.1126/sciadv.abd1705. Publisher: American Association for the Advancement of Science Section: Research Article. [DOI] [PMC free article] [PubMed] [Google Scholar]

2.Open Science Collaboration Estimating the reproducibility of psychological science. Science. 2015;349 doi: 10.1126/science.aac4716. Publisher: American Association for the Advancement of Science Section: Research Article. [DOI] [PubMed] [Google Scholar]

3.Hullman J., Kapoor S., Nanayakkara P., Gelman A., Narayanan A. The worst of both worlds: A comparative analysis of errors in learning from data in psychology and machine learning. arXiv. 2022 doi: 10.48550/arXiv.2203.06498. Preprint at. [DOI] [Google Scholar]

4.Pineau, J.; Vincent-Lamarre, P.; Sinha, K.; Larivière, V.; Beygelzimer, A.; d’Alché-Buc, F.; Fox, E.; Larochelle, H. Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program).Preprint at arXiv:https://doi.org/10.48550/arXiv.2003.122062003.12206 [cs, stat] 2020, arXiv: 2003.12206.

5.Erik Gundersen O. The fundamental principles of reproducibility. Philosophical Transactions of the Royal Society. 2021;379 doi: 10.1098/rsta.2020.0210. Publisher: Royal Society. [DOI] [PubMed] [Google Scholar]

6.Bell S.J., Kampman O.P. 2021. Perspectives on Machine Learning from Psychology’s Reproducibility Crisis. [Google Scholar]

7.Hofman J.M., Goldstein D.G., Sen S., Poursabzi-Sangdeh F., Allen J., Dong L.L., Fried B., Gaur H., Hoq A., Mbazor E., et al. Expanding the scope of reproducibility research through data analysis replications. Organ. Behav. Hum. Decis. Process. 2021;164:192–202. [Google Scholar]

8.Leek J.T., Peng R.D. Opinion: Reproducible research can still be wrong: Adopting a prevention approach. Proc. Natl. Acad. Sci. USA. 2015;112:1645–1646. doi: 10.1073/pnas.1421412111. Publisher: National Academy of Sciences Section: Opinion. [DOI] [PMC free article] [PubMed] [Google Scholar]

9.Nisbet R., Elder J., Miner G. Elsevier; 2009. Handbook of Statistical Analysis and Data Mining Applications. [Google Scholar]

10.Kaufman S., Rosset S., Perlich C., Stitelman O. Leakage in data mining: Formulation, detection, and avoidance. ACM Trans. Knowl. Discov. Data. 2012;6:1–15. [Google Scholar]

11.Fraser C. 2016. The Treachery of Leakage. en. [Google Scholar]

12.Ghani R., Walsh J., Wang J. 2020. Top 10 Ways Your Machine Learning Models May Have Leakage.http://www.rayidghani.com/2020/01/24/top-10-ways-your-machine-learning-models-may-have-leakage/) en-US. [Google Scholar]

13.Becker D. Data Leakage; 2018. en. [Google Scholar]

14.Brownlee J. 2016. Data Leakage in Machine Learning. en-US. [Google Scholar]

15.Collins-Thompson, K. Data Leakage - Module 4: Supervised Machine Learning - Part 2, en.

16.Bouwmeester W., Zuithoff N.P.A., Mallett S., Geerlings M.I., Vergouwe Y., Steyerberg E.W., Altman D.G., Moons K.G.M. Reporting and Methods in Clinical Prediction Research: A Systematic Review. PLOS Med. 2012;9 doi: 10.1371/journal.pmed.1001221. [DOI] [PMC free article] [PubMed] [Google Scholar]

17.Whelan R., Garavan H. When Optimism Hurts: Inflated Predictions in Psychiatric Neuroimaging. Biol. Psychiatry. 2014;75:746–748. doi: 10.1016/j.biopsych.2013.05.014. [DOI] [PubMed] [Google Scholar]

18.Blagus R., Lusa L. Joint Use of Over- and under-Sampling Techniques and Cross-Validation for the Development and Assessment of Prediction Models. BMC Bioinformatics. 2015;16:363. doi: 10.1186/s12859-015-0784-9. [DOI] [PMC free article] [PubMed] [Google Scholar]

19.Bone D., Goodwin M.S., Black M.P., Lee C.-C., Audhkhasi K., Narayanan S. Applying Machine Learning to Facilitate Autism Diagnostics: Pitfalls and Promises. J. Autism Dev. Disord. 2015;45:1121–1136. doi: 10.1007/s10803-014-2268-6. [DOI] [PMC free article] [PubMed] [Google Scholar]

20.Ivanescu A.E., Li P., George B., Brown A.W., Keith S.W., Raju D., Allison D.B. The Importance of Prediction Model Validation and Assessment in Obesity and Nutrition Research. Int. J. Obes. 2016;40:887–894. doi: 10.1038/ijo.2015.214. [DOI] [PMC free article] [PubMed] [Google Scholar]

21.Tu F., Zhu J., Zheng Q., Zhou M. Proceedings of the 2018 26th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering. ACM: Lake Buena Vista FL USA; 2018. Be Careful of When: An Empirical Study on Time-Related Misuse of Issue Tracking Data; pp. 307–318. [DOI] [Google Scholar]

22.Alves V.M., Borba J., Capuzzi S.J., Muratov E., Andrade C.H., Rusyn I., Tropsha A. Oy Vey! A Comment on “Machine Learning of Toxicological Big Data Enables Read-Across Structure Activity Relationships Outperforming Animal Test Reproducibility. Toxicol. Sci. 2019;167:3–4. doi: 10.1093/toxsci/kfy286. [DOI] [PMC free article] [PubMed] [Google Scholar]

23.Christodoulou E., Ma J., Collins G.S., Steyerberg E.W., Verbakel J.Y., Van Calster B. A Systematic Review Shows No Performance Benefit of Machine Learning over Logistic Regression for Clinical Prediction Models. J. Clin. Epidemiol. 2019;110:12–22. doi: 10.1016/j.jclinepi.2019.02.004. [DOI] [PubMed] [Google Scholar]

24.Nalepa J., Myller M., Kawulok M. Validating Hyperspectral Image Segmentation. IEEE Geosci. Remote Sens. Lett. 2019;16:1264–1268. doi: 10.1109/LGRS.2019.2895697. [DOI] [Google Scholar]

25.Poulin P., Jörgens D., Jodoin P.-M., Descoteaux M. Tractography and Machine Learning: Current State and Open Challenges. Magn. Reson. Imaging. 2019;64:37–48. doi: 10.1016/j.mri.2019.04.013. [DOI] [PubMed] [Google Scholar]

26.Nakanishi M., Xu M., Wang Y., Chiang K.-J., Han J., Jung T.-P. Questionable Classification Accuracy Reported in “Designing a Sum of Squared Correlations Framework for Enhancing SSVEP-Based BCIs. IEEE Trans. Neural Syst. Rehabil. Eng. 2020;28:1042–1043. doi: 10.1109/TNSRE.2020.2974272. [DOI] [PubMed] [Google Scholar]

27.Oner M.U., Cheng Y.-C., Lee H.K., Sung W.-K. techreport; 2020. Training Machine Learning Models on Patient Level Data Segregation Is Crucial in Practical Clinical Applications. [DOI] [Google Scholar]

28.Poldrack R.A., Huckins G., Varoquaux G. Establishment of Best Practices for Evidence for Prediction A Review. JAMA Psychiatry. 2020;77:534–540. doi: 10.1001/jamapsychiatry.2019.3671. [DOI] [PMC free article] [PubMed] [Google Scholar]

29.Ahmed H., Wilbur R.B., Bharadwaj H., Siskind J.M. Confounds in the Data—Comments on “Decoding Brain Representations by Multimodal Learning of Neural Activity and Visual Features”. IEEE Trans. Pattern Anal. Mach. Intell. 2021 doi: 10.1109/TPAMI.2021.3121268. 1–1. [DOI] [PMC free article] [PubMed] [Google Scholar]

30.Li R., Johansen J.S., Ahmed H., Ilyevsky T.V., Wilbur R.B., Bharadwaj H.M., Siskind J.M. The Perils and Pitfalls of Block Design for EEG Classification Experiments. IEEE Trans. Pattern Anal. Mach. Intell. 2021;43:316–333. doi: 10.1109/TPAMI.2020.2973153. [DOI] [PubMed] [Google Scholar]

31.Lyu Y., Li H., Sayagh M., (Jack) Jiang Z.M., Hassan A.E. An Empirical Study of the Impact of Data Splitting Decisions on the Performance of AIOps Solutions. ACM Trans. Software Eng. Method. 2021;30:1–38. doi: 10.1145/3447876. [DOI] [Google Scholar]

32.Filho A.C., Batista A.F.D.M., dos Santos H.G. Data Leakage in Health Outcomes Prediction With Machine Learning. Comment on “Prediction of Incident Hypertension Within the Next Year: Prospective Study Using Statewide Electronic Health Records and Machine Learning. J. Med. Internet Res. 2021;23 doi: 10.2196/10969. [DOI] [PMC free article] [PubMed] [Google Scholar]

33.Roberts M., Driggs D., Thorpe M., Gilbey J., Yeung M., Ursprung S., Aviles-Rivero A.I., Etmann C., McCague C., Beer L., Weir-McCall J.R., Teng Z., Gkrania-Klotsas E., Rudd J.H.F., Sala E., Schönlieb C.-B. Common Pitfalls and Recommendations for Using Machine Learning to Detect and Prognosticate for COVID-19 Using Chest Radiographs and CT Scans. Nat. Mach. Intell. 2021;3:199–217. doi: 10.1038/s42256-021-00307-0. [DOI] [Google Scholar]

34.Shim M., Lee S.-H., Hwang H.-J. Inflated Prediction Accuracy of Neuropsychiatric Biomarkers Caused by Data Leakage in Feature Selection. Sci. Rep. 2021;11:7980. doi: 10.1038/s41598-021-87157-3. [DOI] [PMC free article] [PubMed] [Google Scholar]

35.Vandewiele G., Dehaene I., Kovács G., Sterckx L., Janssens O., Ongenae F., De Backere F., De Turck F., Roelens K., Decruyenaere J., Van Hoecke S., Demeester T. Overly Optimistic Prediction Results on Imbalanced Data: A Case Study of Flaws and Benefits When Applying over-Sampling. Artif. Intell. Med. 2021;111 doi: 10.1016/j.artmed.2020.101987. [DOI] [PubMed] [Google Scholar]

36.Arp D., Quiring E., Pendlebury F., Warnecke A., Pierazzi F., Wressnegger C., Cavallaro L., Rieck K. USENIX Security Symposium; 2022. Dos and Don’ts of Machine Learning in Computer Security. [Google Scholar]

37.Barnett E., Onete D., Salekin A., Faraone S.V. Genomic Machine Learning Meta-Regression: Insights on Associations of Study Features with Reported Model Performance; techreport. medRxiv. 2022 doi: 10.1109/TCBB.2023.3343808. 2022.01.10.22268751. [DOI] [PubMed] [Google Scholar]

38.Mongan J., Moy L., Kahn C.E. Checklist for Artificial Intelligence in Medical Imaging (CLAIM): A Guide for Authors and Reviewers. Radiology: Artif. Intell. 2020;2 doi: 10.1148/ryai.2020200029. Publisher: Radiological Society of North America. [DOI] [PMC free article] [PubMed] [Google Scholar]

39.Collins G.S., Reitsma J.B., Altman D.G., Moons K.G.M. Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis (TRIPOD): the TRIPOD Statement. BMC Med. 2015;13:1. doi: 10.1186/s12916-014-0241-z. [DOI] [PMC free article] [PubMed] [Google Scholar]

40.Mitchell M., Wu S., Zaldivar A., Barnes P., Vasserman L., Hutchinson B., Spitzer E., Raji I.D., Gebru T. Association for Computing Machinery; 2019. In Proceedings of the Conference on Fairness, Accountability, and Transparency; pp. 220–229. [Google Scholar]

41.Athey S., Imbens G.W. Machine Learning Methods That Economists Should Know About. Annu. Rev. Econom. 2019;11:685–725. doi: 10.1146/annurev-economics-080217-053433. [DOI] [Google Scholar]

42.Schrider D.R., Kern A.D. Supervised Machine Learning for Population Genetics: A New Paradigm. Trends Genet. 2018;34:301–312. doi: 10.1016/j.tig.2017.12.005. [DOI] [PMC free article] [PubMed] [Google Scholar]

43.Valletta J.J., Torney C., Kings M., Thornton A., Madden J. Applications of machine learning in animal behaviour studies. Anim. Behav. 2017;124:203–220. [Google Scholar]

44.Iniesta R., Stahl D., McGuffin P. Machine learning, statistical learning and the future of biological research in psychiatry. Psychol. Med. 2016;46:2455–2465. doi: 10.1017/S0033291716001367. Publisher: Cambridge University Press. [DOI] [PMC free article] [PubMed] [Google Scholar]

45.Tonidandel S., King E.B., Cortina J.M. Big Data Methods: Leveraging Modern Data Analytic Techniques to Build Organizational Science. Organ. Res. Methods. 2018;21:525–547. Publisher: SAGE Publications Inc. [Google Scholar]

46.Yarkoni T., Westfall J. Choosing Prediction Over Explanation in Psychology: Lessons From Machine Learning. Perspect. Psychol. Sci. 2017;12:1100–1122. doi: 10.1177/1745691617693393. Publisher: SAGE Publications Inc. [DOI] [PMC free article] [PubMed] [Google Scholar]

47.Hofman J.M., Watts D.J., Athey S., Garip F., Griffiths T.L., Kleinberg J., Margetts H., Mullainathan S., Salganik M.J., Vazire S., et al. Integrating explanation and prediction in computational social science. Nature. 2021;595:181–188. doi: 10.1038/s41586-021-03659-0. Bandiera_abtest: a Cg_type: Nature Research Journals Number: 7866 Primary_atype: Reviews Publisher: Nature Publishing Group Subject_term: Interdisciplinary studies;Scientific community Subject_term_id: interdisciplinary-studies;scientificcommunity, [DOI] [PubMed] [Google Scholar]

48.McDermott M.B.A., Wang S., Marinsek N., Ranganath R., Foschini L., Ghassemi M. Reproducibility in machine learning for health research: Still a ways to go. Sci. Transl. Med. 2021;13 doi: 10.1126/scitranslmed.abb1655. Publisher: American Association for the Advancement of Science Section: Perspective. [DOI] [PMC free article] [PubMed] [Google Scholar]

49.Salganik M.J., et al. Measuring the predictability of life outcomes with a scientific mass collaboration. Proc. Natl. Acad. Sci. USA. 2020;117:8398–8403. doi: 10.1073/pnas.1915006117. Publisher: National Academy of Sciences Section: Social Sciences. [DOI] [PMC free article] [PubMed] [Google Scholar]

50.Stodden V., Seiler J., Ma Z. An empirical analysis of journal policy effectiveness for computational reproducibility. Proc. Natl. Acad. Sci. USA. 2018;115:2584–2589. doi: 10.1073/pnas.1708290115. [DOI] [PMC free article] [PubMed] [Google Scholar]

51.Seibold H., Czerny S., Decke S., Dieterle R., Eder T., Fohr S., Hahn N., Hartmann R., Heindl C., Kopper P., et al. A computational reproducibility study of PLOS ONE articles featuring longitudinal data analyses. PLoS One. 2021;16 doi: 10.1371/journal.pone.0251194. [DOI] [PMC free article] [PubMed] [Google Scholar]

52.Geirhos R., Jacobsen J.-H., Michaelis C., Zemel R., Brendel W., Bethge M., Wichmann F.A. Shortcut learning in deep neural networks. Nat. Mach. Intell. 2020;2:665–673. [Google Scholar]

53.Chouldechova A., Benavides-Prado D., Fialko O., Vaithianathan R. In Proceedings of the 1st Conference on Fairness, Accountability and Transparency. 2018. pp. 134–148. [Google Scholar]

54.Kuhn M., Johnson K. Springer-Verlag; 2013. Applied Predictive Modeling. [Google Scholar]

55.Filho A.C., Batista A.F.D.M., Santos H.G.d. Data Leakage in Health Outcomes Prediction With Machine Learning. Comment on “Prediction of Incident Hypertension Within the Next Year: Prospective Study Using Statewide Electronic Health Records and Machine Learning”. J. Med. Internet Res. 2021;23 doi: 10.2196/10969. Company: Journal of Medical Internet Research Distributor: Journal of Medical Internet Research Institution: Journal of Medical Internet Research Label: Journal of Medical Internet Research Publisher: JMIR Publications Inc., Toronto, Canada. [DOI] [PMC free article] [PubMed] [Google Scholar]

56.Oner M.U., Cheng Y.-C., Lee H.K., Sung W.-K. Cold Spring Ha1rbor Laboratory Press Distributor: Cold Spring Harbor Laboratory Press Label: Cold Spring Harbor Laboratory Press Type: article; 2020. Training Machine Learning Models on Patient Level Data Segregation Is Crucial in Practical Clinical Applications; Tech. rep., Company; p. 2020. [Google Scholar]

57.Whalen S., Schreiber J., Noble W.S., Pollard K.S. Navigating the pitfalls of applying machine learning in genomics. Nat. Rev. Genet. 2022;23:169–181. doi: 10.1038/s41576-021-00434-9. [DOI] [PubMed] [Google Scholar]

58.Roberts D.R., Bahn V., Ciuti S., Boyce M.S., Elith J., Guillera-Arroita G., Hauenstein S., Lahoz-Monfort J.J., Schröder B., Thuiller W., et al. Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography. 2017;40:913–929. [Google Scholar]

59.Valavi R., Elith J., Lahoz-Monfort J., Guillera-Arroita G. 2021. Block Cross-Validation for Species Distribution Modelling. [Google Scholar]

60.Malik M.M.A. Hierarchy of Limitations in Machine Learning. arXiv. 2020 doi: 10.48550/arXiv.2002.05193. Preprint at. [DOI] [Google Scholar]

61.Bone D., Goodwin M.S., Black M.P., Lee C.-C., Audhkhasi K., Narayanan S. Applying Machine Learning to Facilitate Autism Diagnostics: Pitfalls and Promises. J. Autism Dev. Disord. 2015;45:1121–1136. doi: 10.1007/s10803-014-2268-6. [DOI] [PMC free article] [PubMed] [Google Scholar]

62.Zech J.R., Badgeley M.A., Liu M., Costa A.B., Titano J.J., Oermann E.K. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study. PLoS Med. 2018;15 doi: 10.1371/journal.pmed.1002683. Publisher: Public Library of Science, e1002683. [DOI] [PMC free article] [PubMed] [Google Scholar]

63.Szegedy C., Zaremba W., Sutskever I., Bruna J., Erhan D., Goodfellow I., Fergus R. Intriguing properties of neural networks. Proceedings of the International Conference on Learning Representations. 2014 [Google Scholar]

64.Geirhos R., Rubisch P., Michaelis C., Bethge M., Wichmann F.A., Brendel W. Proceedings of the International Conference on Learning Representations. 2018. ImageNet-trained CNNs are biased towards texture; increasing shape bias improves accuracy and robustness.https://openreview.net/forum?id=Bygh9j09KX [Google Scholar]

65.Carter B., Jain S., Mueller J., Gifford D. Overinterpretation reveals image classification model pathologies. Adv. Neural Inf. Process. Syst. 2021 [Google Scholar]

66.Recht B., Roelofs R., Schmidt L., Shankar V. In Proceedings of the 36th International Conference on Machine Learning. 2019. Do ImageNet Classifiers Generalize to ImageNet? pp. 5389–5400.https://proceedings.mlr.press/v97/recht19a.html [Google Scholar]

67.Paullada, A.; Raji, I. D.; Bender, E. M.; Denton, E.; Hanna, A. Data and its (dis) contents: A survey of dataset development and use in machine learning research.Preprint at arXiv https://doi.org/10.1016/j.patter.2021.100336preprint arXiv:2012.05345 2020. [DOI] [PMC free article] [PubMed]

68.Scheuerman M.K., Hanna A., Denton E. Do Datasets Have Politics? Disciplinary Values in Computer Vision Dataset Development. Proc. ACM Hum. Comput. Interact. 2021;5:1–37. [Google Scholar]

69.Gebru T., Morgenstern J., Vecchione B., Vaughan J.W., Wallach H., Iii H.D., Crawford K., Crawford K. Datasheets for datasets. Commun. ACM. 2021;64:86–92. [Google Scholar]

70.Han S., Olonisakin T.F., Pribis J.P., Zupetic J., Yoon J.H., Holleran K.M., Jeong K., Shaikh N., Rubio D.M., Lee J.S. A checklist is associated with increased quality of reporting preclinical biomedical research: A systematic review. PLoS One. 2017;12 doi: 10.1371/journal.pone.0183591. [DOI] [PMC free article] [PubMed] [Google Scholar]

71.Garbin C., Marques O. Assessing Methods and Tools to Improve Reporting, Increase Transparency, and Reduce Failures in Machine Learning Applications in Health Care. Radiol. Artif. Intell. 2022;4 doi: 10.1148/ryai.210127. [DOI] [PMC free article] [PubMed] [Google Scholar]

72.Raji D., Denton E., Bender E.M., Hanna A., Paullada A. AI and the Everything in the Whole Wide World Benchmark. Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks. 2021:1. [Google Scholar]

73.Lundberg I., Johnson R., Stewart B.M. What Is Your Estimand? Defining the Target Quantity Connects Statistical Evidence to Theory. Am. Socio. Rev. 2021;86:532–565. [Google Scholar]

74.Liu D.M., Salganik M.J. Successes and Struggles with Computational Reproducibility: Lessons from the Fragile Families Challenge. Socius. 2019;5 doi: 10.1177/2378023119849803. [DOI] [PMC free article] [PubMed] [Google Scholar]

75.Muchlinski D., Siroky D., He J., Kocher M. Comparing Random Forest with Logistic Regression for Predicting Class-Imbalanced CivilWar Onset Data. Polit. Anal. 2016;24:87–103. Publisher: Cambridge University Press. [Google Scholar]

76.Colaresi M., Mahmood Z. Do the robot: Lessons from machine learning to improve conflict forecasting. J. Peace Res. 2017;54:193–214. Publisher: SAGE Publications Ltd. [Google Scholar]

77.Wang, Y. Comparing Random Forest with Logistic Regression for Predicting Class-Imbalanced Civil War Onset Data: A Comment. Political Analysis 2019, 27, Publisher: Cambridge University Press, 107–110.

78.Kaufman A.R., Kraft P., Sen M. Vol. 27. Cambridge University Press; 2019. Improving Supreme Court Forecasting Using Boosted Decision Trees. Political Analysis; pp. 381–387. [Google Scholar]

79.Bara C. 2020. Forecasting civil war and political violence; pp. 177–193. Publication Title: The Politics and Science of Prevision; Routledge. [Google Scholar]

80.2020. Scimago Journal and Country Rank.http://archive.today/oUs4K [Google Scholar]

81.Ward M.D., Greenhill B.D., Bakke K.M. The perils of policy by p-value: Predicting civil conflicts. J. Peace Res. 2010;47:363–375. Publisher: SAGE Publications Ltd. [Google Scholar]

82.Breiman L. Statistical Modeling: The Two Cultures (with comments and a rejoinder by the author) Stat. Sci. 2001;16:199–231. Publisher: Institute of Mathematical Statistics. [Google Scholar]

83.Dressel J., Farid H. The accuracy, fairness, and limits of predicting recidivism. Sci. Adv. 2018;4:eaao5580. doi: 10.1126/sciadv.aao5580. [DOI] [PMC free article] [PubMed] [Google Scholar]

84.Olson R.S., Cava W.L., Mustahsan Z., Varik A., Moore J.H. Data-driven advice for applying machine learning to bioinformatics problems. Pacific Symposium on Biocomputing. Pac. Symp. Biocomput. 2018;23:192–203. [PMC free article] [PubMed] [Google Scholar]

85.Gorman K., Bedrick S. In Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics. Association for Computational Linguistics: Florence, Italy; 2019. We Need to Talk about Standard Splits; pp. 2786–2791.https://aclanthology.org/P19-1267/ [DOI] [PMC free article] [PubMed] [Google Scholar]

86.Blair R.A., Sambanis N. Forecasting Civil Wars: Theory and Structure in an Age of “Big Data” and Machine Learning. J. Conflict Resolut. 2020;64:1885–1915. Publisher: SAGE Publications Inc. [Google Scholar]

87.Robin X., Turck N., Hainard A., Tiberti N., Lisacek F., Sanchez J.-C., Müller M. pROC: an open-source package for R and S+ to analyze and compare ROC curves. BMC Bioinf. 2011;12:77. doi: 10.1186/1471-2105-12-77. [DOI] [PMC free article] [PubMed] [Google Scholar]

88.He K., Zhang X., Ren S., Sun J. Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification. CoRR. 2015 [Google Scholar]

89.Szeliski R. 2nd ed. 2021. Computer Vision: Algorithms and Applications.https://szeliski.org/Book [Google Scholar]

90.Shi L., Lin L. The trim-and-fill method for publication bias: practical guidelines and recommendations based on a large database of meta-analyses. Medicine. 2019;98 doi: 10.1097/MD.0000000000015987. [DOI] [PMC free article] [PubMed] [Google Scholar]

91.Gurevitch J., Koricheva J., Nakagawa S., Stewart G. Meta-analysis and the science of research synthesis. Nature. 2018;555:175–182. doi: 10.1038/nature25753. Bandiera_abtest: a Cg_type: Nature Research Journals Number: 7695 Primary_atype: Reviews Publisher: Nature Publishing Group Subject_term: Biodiversity;Outcomes research Subject_term_id: biodiversity;outcomes-research. [DOI] [PubMed] [Google Scholar]

92.Hofman J.M., Sharma A., Watts D.J. Prediction and explanation in social systems. Science. 2017;355:486–488. doi: 10.1126/science.aal3856. Publisher: American Association for the Advancement of Science Section: Essays. [DOI] [PubMed] [Google Scholar]

93.Islam R., Henderson P., Gomrokchi M., Precup D. 2017. Reproducibility of Benchmarked Deep Reinforcement Learning Tasks for Continuous Control. [Google Scholar]

94.Lones, M. A. How to avoid machine learning pitfalls: a guide for academic researchers.Preprint at arXiv:2108.02497 [cs] 2021,https://doi.org/10.48550/arXiv.2108.02497 arXiv: 2108.02497.

95.Russakovsky O., Deng J., Su H., Krause J., Satheesh S., Ma S., Huang Z., Karpathy A., Khosla A., Bernstein M., et al. ImageNet Large Scale Visual Recognition Challenge. Int. J. Comput. Vis. 2015;115:211–252. [Google Scholar]

96.Koh P.W., et al. In Proceedings of the 38th International Conference on Machine Learning. 2021. pp. 5637–5664. [Google Scholar]

97.Rocca R., Yarkoni T. Putting Psychology to the Test: Rethinking Model Evaluation Through Benchmarking and Prediction. Advances in Methods and Practices in Psychological Science. 2021;4 doi: 10.1177/25152459211026864. [DOI] [PMC free article] [PubMed] [Google Scholar]

98.Donoho D. 50 Years of Data Science. J. Comput. Graph Stat. 2017;26:745–766. doi: 10.1080/10618600.2017.1384734. Publisher: Taylor & Francis _eprint: [DOI] [Google Scholar]

99.Marie B., Fujita A., Rubino R. Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing. 2021. Scientific Credibility of Machine Translation Research: A Meta-Evaluation of 769 Papers; pp. 7297–7306. [DOI] [Google Scholar]

100.Clyburne-Sherin A., Fei X., Green S.A. Computational reproducibility via containers in social psychology. Meta-Psychology. 2019;3 [Google Scholar]

101.Easing the burden of code review. Nat. Methods. 2018;15:641. doi: 10.1038/s41592-018-0137-5. Bandiera_abtest: a Cg_type: Nature Research Journals Number: 9 Primary_atype: Editorial Publisher: Nature Publishing Group Subject_term: Computational biology and bioinformatics;Publishing Subject_term_id: computationalbiology-and-bioinformatics;publishing. [DOI] [PubMed] [Google Scholar]

102.Hutson M. No coding required: Companies make it easier than ever for scientists to use artificial intelligence. Science. 2019 [Google Scholar]

103.Kapoor S., Narayanan A. 2021. Claims of Superior Performance of Machine Learning over Logistic Regression for Civil War Prediction Don’t Reproduce.https://www.codeocean.com/, version v1 [Google Scholar]

104.Hook D.W., Porter S.J., Herzog C. Dimensions: Building Context for Search and Evaluation. Frontiers in Research Metrics and Analytics. 2018;3 doi: 10.3389/frma.2018.00023. Publisher: Frontiers. [DOI] [Google Scholar]

Associated Data

This section collects any data citations, data availability statements, or supplementary materials included in this article.

Supplementary Materials

Document S1. Supplemental experimental procedures, Figures S1–S3, and Tables S1–S6

mmc1.pdf (684.4KB, pdf)

Document S2. Article plus supplemental information

mmc2.pdf (3.4MB, pdf)

Data Availability Statement

The code and data required to reproduce our case study on civil war prediction have been uploaded to a CodeOcean capsule (CodeOcean: https://doi.org/10.24433/CO.4899453.v1).103 The supplemental experimental procedures (section S2) contains a detailed description of our methods and results from additional robustness checks.

Articles from Patterns are provided here courtesy of Elsevier

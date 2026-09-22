# Rios-Duarte et al. (2024) — Redes convolucionales para melanoma, desde Uniandes y el Externado

**Autores:** Jorge A. Rios-Duarte, Andres C. Diaz-Valencia y Ricardo A.
Peña-Silva, de la Universidad de los Andes (Bogotá); Germán Combariza y Miguel
Feles, de la Universidad Externado de Colombia (Bogotá). Peña-Silva tiene además
afiliación en el Lown Scholars Program de la Harvard T.H. Chan School of Public
Health. Rios-Duarte y Peña-Silva son los autores de correspondencia.
**Título:** Comprehensive analysis of clinical images contributions for melanoma
classification using convolutional neural networks.
**Revista:** Skin Research and Technology, volumen 30, número 5, artículo e13607.
**Año:** 2024 (en línea el 14 de mayo de 2024).
**DOI:** 10.1111/srt.13607
**PMCID:** PMC11091779 — **PMID:** 38742379
**Fecha de consulta:** 2026-09-21
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11091779/
*Datos bibliográficos comprobados en PubMed (E-utilities) y en `api.crossref.org`
el 2026-09-21.*

**LICENCIA: CC BY-NC-ND 4.0 → TEXTO COMPLETO.** El artículo dice:

> This is an open access article under the terms of the
> http://creativecommons.org/licenses/by-nc-nd/4.0/ License, which permits use and
> distribution in any medium, provided the original work is properly cited, the
> use is non‐commercial and no modifications or adaptations are made.

El depósito de la editorial en Crossref registra la misma licencia para la versión
publicada (`content-version: vor`). Verificado el 2026-09-21 en la página del
artículo en PMC y en Crossref. **Es más restrictiva que CC BY, y se versiona
porque la permite:** autoriza compartir con fines no comerciales y sin
adaptaciones, y el texto va sin adaptar. Atribución: Rios-Duarte JA et al.,
*Skin Research and Technology* 30(5):e13607 (2024), DOI 10.1111/srt.13607.
**Cambios** respecto del original, como pide la licencia: el texto se extrajo de la versión HTML de PMC con un script
que conserva el contenido del elemento `<article>` y quita etiquetas, scripts y
botones. **No se omite el resto del armazón del sitio**, que queda mezclado con
el artículo: nombres de autor duplicados, afiliaciones repetidas, enlaces "Find
articles by…", "Open in a new tab" junto a cada figura y tabla, las etiquetas
"[DOI]", "[PubMed]", "[PMC free article]" y "[Google Scholar]" tras las
referencias, "PMC Copyright notice" y la línea final "Articles from … are
provided here courtesy of …". La línea de cita inicial perdió el nombre de la
revista. Las figuras 1 a 3 son imágenes y no se reproducen; quedan su número y su
leyenda. Las tablas 1 y 2 aparecen con una celda por línea. **Nada del artículo se adapta:** la extracción cambia el formato, no el
texto. Se añaden esta cabecera y las secciones
marcadas como nuestras.

**Uso en el proyecto:** estado del arte del anteproyecto (`informe/anteproyecto.md`,
§2.4), que lo describe como trabajo colombiano de aprendizaje automático
dermatológico.

---

## Citas que el proyecto usa

**Resumen:** qué clasifican.

> This study aims to compare the classification performance for melanoma of three
> types of CNN models: those trained on clinical images, dermoscopy images, and a
> combination of paired clinical and dermoscopy images from the same lesion.

**Métodos, 2.1 "Data source":** de dónde salen las imágenes. En el texto
extraído, la frase queda cortada por los números de las referencias, así que se
cita en dos tramos.

> A total of 914 pairs of images were gathered from public dermatology image
> repositories, comprising 822 from the “7‐point criteria evaluation database”

> and 92 from “The International Skin Imaging Collaboration”

**Declaración ética:** las imágenes son públicas.

> In consideration of our research, which involves the use of images that have
> been previously published in public repositories, the Ethics Committee of the
> Faculty of Medicine at the Universidad de los Andes has assessed it as “research
> with no inherent risk.”

---

## Qué sostiene el artículo: análisis nuestro, sobre el texto completo

- **Autoría.** Los cinco autores tienen afiliación en universidades colombianas.
- **Tarea.** Clasificación binaria de melanoma frente a nevus con redes
  convolucionales (Inception-ResNetV2 preentrenada), a partir de imágenes
  clínicas, dermatoscópicas o de ambas.
- **Datos.** 914 pares de imágenes de repositorios públicos: 822 de la base de
  los 7 criterios y 92 de ISIC. No hay imágenes de pacientes colombianos.
- **Límite que declaran los autores.** Los repositorios no traen ascendencia ni
  fototipo de los pacientes, lo que limita la generalización.

---

## Texto original

. 2024 May 14;30(5):e13607. doi: 10.1111/srt.13607

Comprehensive analysis of clinical images contributions for melanoma classification using convolutional neural networks

Jorge A Rios‐Duarte
Jorge A Rios‐Duarte

1
School of Medicine, Universidad de los Andes, Bogotá, Colombia

Find articles by Jorge A Rios‐Duarte

1,✉, Andres C Diaz‐Valencia
Andres C Diaz‐Valencia

1
School of Medicine, Universidad de los Andes, Bogotá, Colombia

Find articles by Andres C Diaz‐Valencia

1, Germán Combariza
Germán Combariza

2
Department of Mathematics, Universidad Externado de Colombia, Bogotá, Colombia

Find articles by Germán Combariza

2, Miguel Feles
Miguel Feles

2
Department of Mathematics, Universidad Externado de Colombia, Bogotá, Colombia

Find articles by Miguel Feles

2, Ricardo A Peña‐Silva
Ricardo A Peña‐Silva

1
School of Medicine, Universidad de los Andes, Bogotá, Colombia

3
Lown Scholars Program, T.H. Chan School of Public Health, Harvard University, Boston, Massachusetts, USA

Find articles by Ricardo A Peña‐Silva

1,3,✉

1
School of Medicine, Universidad de los Andes, Bogotá, Colombia

2
Department of Mathematics, Universidad Externado de Colombia, Bogotá, Colombia

3
Lown Scholars Program, T.H. Chan School of Public Health, Harvard University, Boston, Massachusetts, USA

*

Correspondence
, Jorge A. Rios‐Duarte and Ricardo A. Peña‐Silva, Pharmacology laboratory, School of Medicine, Universidad de los Andes, Bogotá D.C, Colombia. Email: ja.rios11@uniandes.edu.co and rpena@uniandes.edu.co

✉Corresponding author.

Received 2023 Oct 11; Accepted 2024 Jan 19; Collection date 2024 May.

© 2024 The Authors. Skin Research and Technology published by John Wiley & Sons Ltd.

This is an open access article under the terms of the http://creativecommons.org/licenses/by-nc-nd/4.0/ License, which permits use and distribution in any medium, provided the original work is properly cited, the use is non‐commercial and no modifications or adaptations are made.

PMC Copyright notice

PMCID: PMC11091779 PMID: 38742379

Abstract

Background

Timely diagnosis plays a critical role in determining melanoma prognosis, prompting the development of deep learning models to aid clinicians. Questions persist regarding the efficacy of clinical images alone or in conjunction with dermoscopy images for model training. This study aims to compare the classification performance for melanoma of three types of CNN models: those trained on clinical images, dermoscopy images, and a combination of paired clinical and dermoscopy images from the same lesion.

Materials and Methods

We divided 914 image pairs into training, validation, and test sets. Models were built using pre‐trained Inception‐ResNetV2 convolutional layers for feature extraction, followed by binary classification. Training comprised 20 models per CNN type using sets of random hyperparameters. Best models were chosen based on validation AUC‐ROC.

Results

Significant AUC‐ROC differences were found between clinical versus dermoscopy models (0.661 vs. 0.869, p < 0.001) and clinical versus clinical + dermoscopy models (0.661 vs. 0.822, p = 0.001). Significant sensitivity differences were found between clinical and dermoscopy models (0.513 vs. 0.799, p = 0.01), dermoscopy versus clinical + dermoscopy models (0.799 vs. 1.000, p = 0.02), and clinical versus clinical + dermoscopy models (0.513 vs. 1.000, p < 0.001). Significant specificity differences were found between dermoscopy versus clinical + dermoscopy models (0.800 vs. 0.288, p < 0.001) and clinical versus clinical + dermoscopy models (0.650 vs. 0.288, p < 0.001).

Conclusion

CNN models trained on dermoscopy images outperformed those relying solely on clinical images under our study conditions. The potential advantages of incorporating paired clinical and dermoscopy images for CNN‐based melanoma classification appear less clear based on our findings.

Keywords: artificial intelligence, deep learning, dermoscopy images, melanoma, skin cancer

Abbreviations

AUC‐ROC
Area Under the Receiver Operating Characteristic Curve

CNN
convolutional neural network

1. INTRODUCTION

Cutaneous melanoma incidence has been increasing over recent decades. According to GLOBOCAN 2020 the age standardized rate of melanoma is 3.8/100 000 person‐years for males and 3.0/100 000 person‐years for females,
1
notably affecting patients with lower skin phototypes and aged 55–84 years.
1
,
2
Diagnosis of melanoma predominantly relies on clinical skin examination, with complementary dermoscopy recommended for adequately trained physicians, achieving an increase in diagnostic sensitivity from 0.71 to 0.90 compared to clinical examination alone.
3
,
4

Early‐stage melanoma diagnosis boasts favorable survival rates, particularly in low Breslow depth tumors.
5
,
6
,
7
,
8

(p31) However, diagnostic delays can lead to advanced cancer staging and increased Breslow depth. These delays are primarily attributed to challenges in identifying atypical cases or patient unawareness of lesion significance.
9
,
10
,
11
In pursuit of increasing diagnostic accuracy for early melanoma detection, various computer vision models, including machine learning algorithms like logistic regression, support vector machines, and convolutional neural networks (CNNs), have been developed.
12
Deep CNN models have demonstrated remarkable potential, equaling or even outperforming dermatologists in distinguishing melanoma from non‐malignant lesions.
4
,
13

(p13),

14
,
15
,
16
,
17

Despite these advancements, challenges remain. Particularly, the impact on model performance attributable to the image type (clinical or dermoscopy) used for model training and testing. While some studies have employed clinical images for model training and testing, comparative assessments with models based on dermoscopy and paired clinical/dermoscopy images are scarce.
18
,
19
This study aims to bridge this gap by evaluating and comparing the classification performance of three types of CNN models: those trained on clinical images, dermoscopy images, and a combination of paired clinical and dermoscopy images from the same lesion. By systematically analyzing metrics such as the Area Under the Receiver Operating Characteristic Curve (AUC‐ROC), sensitivity, and specificity, our investigation provides insights into the efficacy of these CNN models for melanoma classification. Through rigorous experimental design and statistical analysis, we evaluate the impact of image sources on model performance, offering valuable contributions to the realm of computer‐aided diagnosis of melanoma.

2. MATERIALS AND METHODS

2.1. Data source

We conducted a comparative accuracy study to evaluate and compare the performance of CNN models trained using different image inputs: clinical, dermoscopy, and a combination of clinical and dermoscopy. This study aimed to adhere to the CLEAR Derm Consensus Guidelines established by the International Skin Imaging Collaboration Artificial Intelligence Working Group.
20
A total of 914 pairs of images were gathered from public dermatology image repositories, comprising 822 from the “7‐point criteria evaluation database”
21
and 92 from “The International Skin Imaging Collaboration”
22
(ISIC) repository. These repositories provide information about patient demographic characteristics, lesion localization, and diagnosis, as well as clinical and/or dermoscopy images. These sources did not provide details regarding the ancestry of patients or the technical specifications of the imaging systems used. Image selection was based on the availability of paired dermoscopy and clinical photographs from the same pigmented skin lesion, diagnosis of melanoma or nevi (any type), and a license/permit for research use.

For the classification algorithm, all lesions were reclassified into binary categories: “1” denoting any type of melanoma and “0” for non‐melanoma lesions (nevi). Our dataset had predominantly non‐melanoma lesions (class imbalance), which can influence the final models' performance. However, we used a weighted loss function during training to reduce model prediction biases toward non‐malignant lesions. Other patient characteristics including sex, lesion location, repository, and definitive diagnosis were documented (Table 1). The diagnoses as reported in the repositories were used for a stratified data splitting into training, validation, and test set. Images of metastatic melanoma were excluded from our dataset to ensure that our models were trained exclusively on primary melanoma lesions, whose characteristics are essential for early and accurate diagnosis. Finally, the dataset was divided into 676 pairs of images for training, 119 for validation, and 119 for testing. The training set was employed to train the models, while the validation set was used for initial analysis and to compare model performance metrics across the different hyperparameter sets (further details in the “modeling” section). Subsequently, the test set was employed to compare the performance metrics of the best models, determined by their validation AUC‐ROC scores.

TABLE 1.

Descriptive characteristics of the study groups.

Characteristic
Non melanoma
Melanoma
Overall

N

619
295
914

Female
313 (50.6%)
152 (51.5%)
465 (50.9%)

Lesion location

Acral
52 (8.4%)
2 (0.7%)
54 (5.9%)

Head and neck
21 (3.4%)
30 (10.2%)
51 (5.6%)

Lower extremity
129 (20.8%)
86 (29.2%)
215 (23.5%)

Torso
352 (56.9%)
135 (45.8%)
487 (53.3%)

Upper extremity
63 (10.2%)
41 (13.9%)
104 (11.4%)

Missing
2 (0.3%)
1 (0.3%)
3 (0.3%)

Image repository

ISIC
44 (7.1%)
48 (16.3%)
92 (10.1%)

SEVEN
575 (92.9%)
247 (83.7%)
822 (89.9%)

Definitive diagnosis
a

Blue nevus
28 (4.5%)
0 (0%)
28 (3.1%)

Clark nevus
399 (64.5%)
0 (0%)
399 (43.7%)

Combined nevus
13 (2.1%)
0 (0%)
13 (1.4%)

Congenital nevus
17 (2.7%)
0 (0%)
17 (1.9%)

Dermal nevus
33 (5.3%)
0 (0%)
33 (3.6%)

Melanoma
0 (0%)
49 (16.6%)
49 (5.4%)

Melanoma (0.76–1.5 mm)
0 (0%)
53 (18.0%)
53 (5.8%)

Melanoma (in situ)
0 (0%)
64 (21.7%)
64 (7.0%)

Melanoma (less than 0.76 mm)
0 (0%)
102 (34.6%)
102 (11.2%)

Melanoma (more than 1.5 mm)
0 (0%)
27 (9.2%)
27 (3.0%)

Nevus
44 (7.1%)
0 (0%)
44 (4.8%)

Recurrent nevus
6 (1.0%)
0 (0%)
6 (0.7%)

Reed or spitz nevus
79 (12.8%)
0 (0%)
79 (8.6%)

Open in a new tab

Categorical variables are displayed as N (%).

Abbreviations: ISIC, The International Skin Imaging Collaboration, SEVEN, 7‐point criteria evaluation database.

a
Definitive diagnosis as reported in the repository.

2.2. Image preprocessing

A multi‐step approach to enhance pigmented lesion images was conducted, thereby optimizing the input data for improved performance of CNN models for melanoma detection. Initial concerns encompassed the presence of black borders stemming from obstructions or image clipping. This was effectively addressed through a meticulous procedure. Each image underwent scrutiny at the pixel level, followed by a row‐wise analysis. Rows with a maximum color intensity below 100 were identified as part of the black background and subsequently removed. This process was repeated four times by rotating the image 90 degrees in each iteration.

After border removal, the focus shifted to precise segmentation using masking techniques followed by resizing. The pigmented lesion was highlighted as an “active” region by applying a mask to the original image using thresholding, and then we cropped the image based on the non‐active pixels from the mask. Ultimately, images were resized to 299 × 299 pixels, followed by the standard preprocessing steps used in the original InceptionResnetV2 CNN architecture, available in TensorFlow. A more comprehensive description of the preprocessing steps is provided in the supporting information document 1.

2.3. Modeling

Model training was conducted solely on imaging information, no metadata was used during training. Clinical and dermoscopy models employed transfer learning using the Inception‐ResNetV2 CNN architecture. The convolutional layers, with weights trained on ImageNet, were preserved for feature extraction, while the final softmax layer was replaced with a trainable sigmoid unit for binary classification after a global average pooling layer and a variable probability of dropout (Figure 1). The total trainable and non‐trainable parameters were 1537 and 54 338 273, respectively.

FIGURE 1.

Open in a new tab

Structure of the single‐image approach model (clinical and dermoscopy models) and the combined images approach model (clinical + dermoscopy models). The clinical + dermoscopy models used two feature extractors (one for each type of image), explaining the size of the feature vector after concatenation (BS, 3072). The information inside the parentheses shows the tensor size in each phase of the process. BS, batch size. Clinical and dermoscopy images taken from public repositories.
21
,
22

The clinical + dermoscopy models combined two Inception‐ResNetV2 CNN architectures (one for each type of image). The convolutional layers trained on ImageNet were preserved for feature extraction, while the final softmax layer was eliminated. After global average pooling, the outputs of both architectures were concatenated. The structure after concatenation mirrored the clinical or dermoscopy models, with a variable dropout probability followed by a trainable sigmoid unit (Figure 1). The total trainable and non‐trainable parameters were 3073 and 54 336 736, respectively.

Training employed Adam for optimization, and loss function weighting adjusted for class imbalance. Twenty hyperparameter sets (learning rate, batch size, epochs, dropout probability) were randomly generated (Table 2), and each set was used to train each model type (20 of each type, and 60 models in total). This allowed us to make paired comparisons between models trained with the same hyperparameters but varying image types. Initially we compared the performance of the 20 models of each type using the validation set. Following this, we conducted a comprehensive comparison of the performance metrics on the test set for the best models selected based on the validation AUC‐ROC. Images were loaded sequentially, and seed values maintained consistency, isolating image type as the primary differentiator. The training was conducted on Python 3, using a Google Colab virtual machine with 83.5GB of RAM and an A100 Nvidia GPU.

TABLE 2.

Sets of random hyperparameters used for model training.

Set
Learning rate
Dropout probability
Number of epoch
Batch size

0
0.0002096136429
0.3
10
169

1
0.01009393687
0.1
10
13

2
0.0003438053502
0.05
35
169

3
0.07497390349
0.4
20
52

4
0.04753680185
0
20
169

5
0.001639999846
0.05
35
169

6
0.002573640685
0.3
30
13

7
0.005540866855
0.05
30
52

8
0.009857719409
0.4
30
13

9
0.001356568422
0.2
20
13

10
0.004848146354
0.1
25
52

11
0.0006199457413
0.2
35
13

12
0.002791841534
0.05
35
52

13
0.001834105019
0
10
26

14
0.00115860317
0.4
20
169

15
0.000106986058
0.05
30
13

16
0.0003470766598
0.4
20
26

17
0.005759664619
0.3
25
52

18
0.0002350699064
0.1
30
13

19
0.0003378482722
0
30
26

Open in a new tab

The set number aligns with the number of each model in the Tables S1–S4.

2.4. Statistical analyses

To compare the performance metrics of the three types of models on the validation set, we employed the Friedman's test. In cases where the Friedman's test revealed statistical significance, we conducted pairwise comparisons using Wilcoxon signed‐ranks tests to pinpoint specific differences between the models. For performance evaluation and comparison on the test set, we selected the best model of each type based on validation AUC‐ROC, and then, we used the De‐Long test to compare correlated ROC curves and the McNemar's test for non‐independent samples to compare sensitivity and specificity. We adjusted the p‐values using the Bonferroni method to account for multiple comparisons when making pairwise comparisons. Statistical significance was reported for p‐values less than 0.05. R statistical software was used for plotting and statistical testing.

3. RESULTS

3.1. Validation set metrics

In the analysis of the 20 models for each type of input, evaluated on the validation set, dermoscopy and clinical + dermoscopy models exhibited superior performance compared to clinical models. Specifically, the AUC‐ROC values were significantly higher for dermoscopy models (median: 0.853, [min–max: 0.715–0.862]), as well as for clinical + dermoscopy models (0.839 [0.775–0.867]), when contrasted with clinical models (0.744 [0.542–0.793]). Furthermore, the overfitting assessment revealed that dermoscopy models displayed a significantly smaller difference in AUC‐ROC between the training and validation sets (0.071 [0.021–0.135]) in comparison to both, clinical + dermoscopy models (0.125 [0.039–0.169]) and clinical models (0.156 [0.127–0.214]). Notably, clinical + dermoscopy models demonstrated a significantly lower AUC‐ROC difference than clinical models (Figure 2A,B).

FIGURE 2.

Open in a new tab

Pairwise performance comparisons between the three types of CNN models. (A) AUC‐ROC on the validation set. (B) Difference of AUC‐ROC between training and validation set. (C) Sensitivity on the validation set (D) Specificity on the validation set. Each but one (specificity) of the four Friedman tests used to compare the performance metrics between the three groups was statistically significant (p < 0.001). The points represent the 20 models for each type of input, trained using the random sets of hyperparameters. The symbols over the bars show the significance level of the respective pairwise comparisons after the p‐value adjustment. NS: p > 0.05, *: p < = 0.05, **: p < = 0.01, ***: p < = 0.001.

When considering sensitivity, dermoscopy (0.684 [0.316–0.842]) and clinical + dermoscopy models (0.671 [0.553–1.000]) consistently outperformed clinical models (0.553 [0.421–0.842]). However, we did not find significant differences in the specificity of dermoscopy models (0.796 [0.704–0.988]), clinical + dermoscopy models (0.790 [0.506–0.852]), and clinical models (0.827 [0.420–0.889]) (Figure 2C,D).

Tables S1–S3 present an in‐depth breakdown of the aforementioned metrics calculated using the validation set, corresponding to the clinical, dermoscopy, and clinical + dermoscopy models, respectively. Table S4 presents the performance metrics of the clinical + dermoscopy models calculated using the test set.

3.2. Test set evaluation: AUC‐ROC, sensitivity, and specificity

Upon transitioning to the test set, we selected the best model from each type based on their AUC‐ROC values in the validation set. The dermoscopy model displayed the highest AUC‐ROC value of 0.869, followed by the clinical + dermoscopy model at 0.822, and finally, the clinical model at 0.661. Notably, we observed significant differences in AUC‐ROC values between the clinical and dermoscopy models (p < 0.001) and between the clinical and clinical + dermoscopy models (p = 0.001). Conversely, no significant difference in AUC‐ROC was found between the dermoscopy and clinical + dermoscopy models (Figure 3).

FIGURE 3.

Open in a new tab

Test set AUC‐ROC calculated using the best models predictions. (A) Clinical. (B) Dermoscopy. (C) Clinical + Dermoscopy. One model was selected for each type of model based on the validation set AUC‐ROC performance. AUC, Area under the receiver operating characteristic curve.

In terms of sensitivity, the clinical + dermoscopy model achieved the highest value at 1.000, followed by the dermoscopy model at 0.799, and the clinical model at 0.513. We observed statistically significant differences in sensitivity between the clinical and dermoscopy models (p = 0.01), the dermoscopy and clinical + dermoscopy models (p = 0.02), and between the clinical and clinical + dermoscopy models (p < 0.001). Regarding model specificity, the dermoscopy model exhibited the highest value of 0.800, while the clinical model achieved a specificity of 0.650, and the clinical + dermoscopy model registered a specificity of 0.288. We observed statistically significant differences in specificity between the dermoscopy and clinical + dermoscopy models (p < 0.001), and clinical and clinical + dermoscopy models (p < 0.001).

4. DISCUSSION

Melanoma prognosis is highly dependent on the timing of diagnosis. This has prompted the development of deep learning models to aid clinicians in melanoma diagnosis. However, these models are not flawless, and there are still unanswered questions surrounding the use of clinical images as the sole input or in conjunction with dermoscopy images in model training. Our results underscore the superior performance of CNNs trained using dermoscopy images in the context of the training parameters and hyperparameters of our experiment. Additionally, our findings do not indicate a discernible increase in classification performance when utilizing a combination of paired clinical and dermoscopy images from the same lesion for model training.

The application of clinical images for machine learning model training in melanoma has been relatively limited in existing research. A study in 2020 achieved an accuracy of 75.9% in identifying suspicious pigmented skin lesions from wide‐field clinical images, although this was accomplished through a multistep system rather than an end‐to‐end model.
19
Another study in 2021 using transfer learning reported a 62.4% accuracy in classifying three types of skin lesions (benign, malignant, and non‐neoplastic), but it lacks a specific focus on melanoma classification.
23
Lastly, studies evaluating CNN models using clinical images for melanoma classification have yielded variable results concerning sensitivity and specificity. A 2016 publication reported a sensitivity of 0.81 and a specificity of 0.80, while a 2018 study reported a sensitivity of 0.91 and a specificity of 0.90 for melanoma classification.
24
,
25
Those discrepancies may arise from the diversity of study datasets and the heterogeneity of the methodologies employed.

Regarding literature on CNN models trained on dermoscopy images, various models have demonstrated remarkable classification performance for melanoma, as evidenced by high scores in AUC‐ROC, sensitivity, specificity, and accuracy metrics.
4
,
14
,
15
,
16
,
17
Moreover, some of these models have even outperformed human dermatologists on classification accuracy for melanoma.
4
,
13
,
15
Our results align with these previous reports, reaffirming the effectiveness of CNN models trained on dermoscopy images due to their higher performance and reduced overfitting, as demonstrated in our validation set and test set evaluations.

While it was initially expected that the integration of paired clinical and dermoscopy images would result in improved performance, as previously reported by Kawahara et al.
21
and Ge et al.,
26
our findings present a different perspective. Accordingly, Kawahara et al. noted that the modest improvement in classification performance they observed in their results might be primarily attributed to the increased depth of the model when incorporating multiple inputs rather than an increase in significant information contributions from clinical images.
21
It is imperative to recognize that the differences observed in our results in comparison to previous studies may arise from significant methodological distinctions. These differences encompass various aspects, including model design and architecture, data preprocessing and augmentation strategies, and the incorporation of metadata in conjunction with clinical and dermoscopy images. Additionally, the observed lack of enhanced diagnostic accuracy when combining clinical and dermoscopy features may be to our relatively small sample size, especially in the context of the increased complexity of our models, which have a higher number of trainable parameters compared to those trained solely on either dermoscopy or clinical images.

Finally, the lower generalizability and performance of the models trained using clinical images found in our results, coupled with previous findings in the literature, underscores the notion that deep learning models relying on clinical images may necessitate supplementary preprocessing steps, an expanded training dataset, or adjustments in model parameters. These challenges pose significant obstacles to the practical application of clinical image‐based models, particularly when contrasted with the performance of models utilizing dermoscopy images.

Our study underscores the necessity for further research in the field of computer vision for dermatology, focusing on three critical factors that were beyond the scope of our current experiment but hold significant relevance. First, the issue of hair contamination in dermoscopy images presents a challenge for accurate feature extraction. Bardou et al.
27
developed an efficient algorithm to address this issue, suggesting a potential area for enhancement in future models.
27
Second, incorporating automatic image segmentation for melanoma classification could substantially benefit the accuracy of AI models, as demonstrated by Oukil et al.
28
Lastly, the shift from binary to multiclass classification in AI‐based diagnostic aid algorithms represents a crucial area for development. Future models should be evaluated not only on binary tasks but also on their ability to classify a wide range of dermatological conditions using a combination of clinical and dermoscopy images. This approach could significantly broaden the applicability and effectiveness of AI in dermatology.

5. LIMITATIONS

While our study has made valuable contributions, it is important to acknowledge its limitations. The relatively small sample size, especially within the context of deep learning and big data, was primarily due to the scarcity of paired clinical and dermoscopy images from the same lesion available in public repositories. However, it is worth noting that this challenge is a recognized issue in the field of deep learning applied to healthcare. To mitigate this limitation, we employed techniques such as transfer learning, which allowed us to reduce the required quantity of input data for training CNN models. Moreover, our dataset did not include information on the patients' ancestry or skin phototype, limiting the generalizability of our results. As datasets evolve to encompass a wider variety of ancestry and skin phototype data, future research should reevaluate the efficacy of combining clinical and dermoscopy images. Such studies would enhance the utility and inclusiveness of AI tools in dermatology and medicine.

Moreover, the choice of our model architecture may affect the final results. However, we opted for the InceptionResNetV2 CNN architecture due to its capacity to blend the strengths of two potent architectures (Inception and ResNet), as well as its proven track record of high performance in earlier studies focused on evaluating melanoma classification from images.
16
Conversely, the selection of hyperparameters has the potential to influence model performance. To mitigate any potential impact, we adopted a randomized approach when choosing values for various hyperparameters fine‐tuned in our models. This encompassed a wide range of values for parameters such as batch size, learning rate, and the number of training epochs.

Lastly, despite the preprocessing steps taken, it is essential to recognize that variations in image quality and camera proximity may influence the feature extraction process from clinical images. These factors could, in turn, contribute to the observed lower performance of models when trained using clinical images. Therefore, Further investigations are needed to explore the impact of image quality on model performance, especially in settings where dermoscopy images might not be readily available.

Our study holds significance as an attempt to systematically compare the performance of models using clinical, dermoscopy, and paired clinical + dermoscopy images from the same lesions for melanoma classification. We have meticulously controlled for variables that might influence model performance aside from image input. This includes considerations such as hyperparameters, image order within mini‐batches, and the use of seeds for parameter initialization and other stochastic processes.

6. CONCLUSION

Our research supports the superiority of CNN models trained on dermoscopy images compared to those relying solely on clinical images under the conditions studied in our study. However, the potential benefits of incorporating paired clinical and dermoscopy images for enhancing CNN‐based melanoma classification appear less certain. These outcomes suggest a possible limited contribution of clinical images, both independently and in conjunction with dermoscopy, in the effective training of CNN models for melanoma classification. As the realm of deep learning makes continuous strides, our findings prompt a cautious reevaluation of the value and role of clinical images in the construction of more accurate melanoma classification systems using CNN‐based methodologies.

CONFLICT OF INTEREST STATEMENT

The authors report no conflict of interest.

ETHICAL STATEMENT

In consideration of our research, which involves the use of images that have been previously published in public repositories, the Ethics Committee of the Faculty of Medicine at the Universidad de los Andes has assessed it as “research with no inherent risk.” Consequently, the committee has granted approval without any exceptions.

Supporting information

Supporting Information

SRT-30-e13607-s001.docx (15.3KB, docx)

Supporting Information

SRT-30-e13607-s002.docx (14.5KB, docx)

ACKNOWLEDGMENTS

This study was funded by the FAPA grant from the Universidad de los Andes to R.A.P.S.

Rios‐Duarte JA, Diaz‐Valencia AC, Combariza G, Feles M, Peña‐Silva RA. Comprehensive analysis of clinical images contributions for melanoma classification using convolutional neural networks. Skin Res Technol. 2024;30:e13607. 10.1111/srt.13607

Declaration of Generative AI and AI‐assisted technologies in the writing process:

During the preparation of this work the authors used ChatGPT to enhance readability. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of this publication.

Contributor Information

Jorge A. Rios‐Duarte, Email: ja.rios11@uniandes.edu.co.

Ricardo A. Peña‐Silva, Email: rpena@uniandes.edu.co.

DATA AVAILABILITY STATEMENT

Permissions to access and use the images can be obtained by making a request through the following channels: https://derm.cs.sfu.ca/Welcome.html and https://www.isic‐archive.com/. Once permission is granted, interested parties can access the preprocessed images and the code required for model training and testing by reaching out to the corresponding author.

REFERENCES

1.
Sung H, Ferlay J, Siegel RL, et al. Global cancer statistics 2020: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. CA Cancer J Clin. 2021;71(3):209‐249. doi: 10.3322/caac.21660

[DOI] [PubMed] [Google Scholar]

2.
Rigel DS. Epidemiology of melanoma. Semin Cutan Med Surg. 2010;29(4):204‐209. doi: 10.1016/j.sder.2010.10.005

[DOI] [PubMed] [Google Scholar]

3.
Vestergaard ME, Macaskill P, Holt PE, Menzies SW. Dermoscopy compared with naked eye examination for the diagnosis of primary melanoma: a meta‐analysis of studies performed in a clinical setting. Br J Dermatol. Published online June 2008;159(3):669‐676. doi: 10.1111/j.1365-2133.2008.08713.x

[DOI] [PubMed] [Google Scholar]

4.
Phillips M, Greenhalgh J, Marsden H, Palamaras I. Detection of malignant melanoma using artificial intelligence: an observational study of diagnostic accuracy. Dermatol Pract Concept. 2019;10(1):e2020011. Published 2019 Dec 31. doi: 10.5826/dpc.1001a11

[DOI] [PMC free article] [PubMed] [Google Scholar]

5.
Balch CM, Buzaid AC, Soong SJ, et al. Final version of the American joint committee on cancer staging system for cutaneous melanoma. J Clin Oncol. 2001;19(16):3635‐3648. doi: 10.1200/JCO.2001.19.16.3635

[DOI] [PubMed] [Google Scholar]

6.
Green AC, Baade P, Coory M, Aitken JF, Smithers M. Population‐based 20‐year survival among people diagnosed with thin melanomas in Queensland, Australia. J Clin Oncol. 2012;30(13):1462‐1467. doi: 10.1200/JCO.2011.38.8561

[DOI] [PubMed] [Google Scholar]

7.
Maurichi A, Miceli R, Camerini T, et al. Prediction of survival in patients with thin melanoma: results from a multi‐institution study. J Clin Oncol. 2014;32(23):2479‐2485. doi: 10.1200/JCO.2013.54.2340

[DOI] [PubMed] [Google Scholar]

8.
Isaksson K, Mikiver R, Eriksson H, et al. Survival in 31 670 patients with thin melanomas: a Swedish population‐based study*. Br J Dermatol. 2021;184(1):60‐67. doi: 10.1111/bjd.19015

[DOI] [PubMed] [Google Scholar]

9.
Richard MA, Grob JJ, Avril MF, et al. Melanoma and tumor thickness: challenges of early diagnosis. Arch Dermatol. 1999;135(3):269‐274. doi: 10.1001/archderm.135.3.269

[DOI] [PubMed] [Google Scholar]

10.
Richard MA, Grob JJ, Avril MF, et al. Delays in diagnosis and melanoma prognosis (I): the role of patients. Int J Cancer. 2000;89(3):271‐279. doi: 10.1002/1097-0215(20000520)89:3<271::AID‐IJC10>3.0.CO;2‐7
[DOI] [PubMed] [Google Scholar]

11.
Richard MA, Grob JJ, Avril MF, et al. Delays in diagnosis and melanoma prognosis (II): the role of doctors. Int J Cancer. 2000;89(3):280‐285. doi: 10.1002/1097-0215(20000520)89:3<280::AID‐IJC11>3.0.CO;2‐2
[DOI] [PubMed] [Google Scholar]

12.
Adegun A, Viriri S. Deep learning techniques for skin lesion analysis and melanoma cancer detection: a survey of state‐of‐the‐art. Artif Intell Rev. 2021;54(2):811‐841. doi: 10.1007/s10462-020-09865-y
[DOI] [Google Scholar]

13.
Brinker TJ, Hekler A, Enk AH, et al. Deep learning outperformed 136 of 157 dermatologists in a head‐to‐head dermoscopic melanoma image classification task. Eur J Cancer. 2019;113:47‐54. doi: 10.1016/j.ejca.2019.04.001

[DOI] [PubMed] [Google Scholar]

14.
Sanvordekar M, Kuppili V, Modi C. Machine learning approach for skin melanoma classification.
In: 2022 International Conference on Smart Generation Computing, Communication and Networking (SMART GENCON)
. IEEE; 2022:1‐5. doi: 10.1109/SMARTGENCON56628.2022.10083665
[DOI] [Google Scholar]

15.
Haenssle HA, Fink C, Schneiderbauer R, et al. Man against machine: diagnostic performance of a deep learning convolutional neural network for dermoscopic melanoma recognition in comparison to 58 dermatologists. Ann Oncol. 2018;29(8):1836‐1842. doi: 10.1093/annonc/mdy166

[DOI] [PubMed] [Google Scholar]

16.
Guergueb T, Akhloufi MA. Melanoma skin cancer detection using recent deep learning models. Annu Int Conf IEEE Eng Med Biol Soc. 2021;2021:3074‐3077. doi: 10.1109/EMBC46164.2021.9631047

[DOI] [PubMed] [Google Scholar]

17.
Zhang Y, Wang C. SIIM‐ISIC melanoma classification with DenseNet. In:
2021 IEEE 2nd International Conference on Big Data, Artificial Intelligence and Internet of Things Engineering (ICBAIE)
. IEEE; 2021:14‐17. doi: 10.1109/ICBAIE52039.2021.9389983
[DOI] [Google Scholar]

18.
Brinker TJ, Hekler A, Enk AH, et al. A convolutional neural network trained with dermoscopic images performed on par with 145 dermatologists in a clinical melanoma image classification task. Eur J Cancer. 2019;111:148‐154. doi: 10.1016/j.ejca.2019.02.005

[DOI] [PubMed] [Google Scholar]

19.
Birkenfeld JS, Tucker‐Schwartz JM, Soenksen LR, Avilés‐Izquierdo JA, Marti‐Fuster B. Computer‐aided classification of suspicious pigmented lesions using wide‐field images. Comput Methods Programs Biomed. 2020;195:105631. doi: 10.1016/j.cmpb.2020.105631

[DOI] [PubMed] [Google Scholar]

20.
Daneshjou R, Barata C, Betz‐Stablein B, et al. Checklist for evaluation of image‐based artificial intelligence reports in dermatology: CLEAR derm consensus guidelines from the international skin imaging collaboration artificial intelligence working group. JAMA Dermatol. 2022;158(1):90. doi: 10.1001/jamadermatol.2021.4915

[DOI] [PMC free article] [PubMed] [Google Scholar]

21.
Kawahara J, Daneshvar S, Argenziano G, Hamarneh G. Seven‐point checklist and skin lesion classification using multitask multimodal neural nets. IEEE J Biomed Health Inform. 2019;23(2):538‐546. doi: 10.1109/JBHI.2018.2824327
[DOI] [PubMed] [Google Scholar]

22.
Hospital Italiano de Buenos Aires
. Hospital Italiano de Buenos Aires Skin Lesions. doi: 10.34970/432362
[DOI]

23.
Groh M, Harris C, Soenksen L, et al. Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset. ArXiv. doi: 10.48550/ARVIX.2104.09957
[DOI]

24.
Nasr‐Esfahani E, Samavi S, Karimi N, et al. Melanoma detection by analysis of clinical images using convolutional neural network.
In: 2016 38th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC)
. IEEE; 2016:1373‐1376. doi: 10.1109/EMBC.2016.7590963
[DOI] [PubMed] [Google Scholar]

25.
Han SS, Kim MS, Lim W, Park GH, Park I, Chang SE. Classification of the clinical images for benign and malignant cutaneous tumors using a deep learning algorithm. J Invest Dermatol. 2018;138(7):1529‐1538. doi: 10.1016/j.jid.2018.01.028

[DOI] [PubMed] [Google Scholar]

26.
Ge Z, Demyanov S, Chakravorty R, Bowling A, Garnavi R. Skin disease recognition using deep saliency features and multimodal learning of dermoscopy and clinical images. In: Descoteaux M, Maier‐Hein L, Franz A, Jannin P, Collins DL, Duchesne S, eds. Medical Image Computing and Computer Assisted Intervention − MICCAI 2017. Vol 10435. Lecture Notes in Computer Science. Springer International Publishing; 2017:250‐258. doi: 10.1007/978-3-319-66179-7_29
[DOI] [Google Scholar]

27.
Bardou D, Bouaziz H, Lv L, Zhang T. Hair removal in dermoscopy images using variational autoencoders. Skin Res Technol. 2022;28(3):445‐454. doi: 10.1111/srt.13145

[DOI] [PMC free article] [PubMed] [Google Scholar]

28.
Oukil S, Kasmi R, Mokrani K, García‐Zapirain B. Automatic segmentation and melanoma detection based on color and texture features in dermoscopic images. Skin Res Technol. 2022;28(2):203‐211. doi: 10.1111/srt.13111

[DOI] [PMC free article] [PubMed] [Google Scholar]

Associated Data

This section collects any data citations, data availability statements, or supplementary materials included in this article.

Supplementary Materials

Supporting Information

SRT-30-e13607-s001.docx (15.3KB, docx)

Supporting Information

SRT-30-e13607-s002.docx (14.5KB, docx)

Data Availability Statement

Permissions to access and use the images can be obtained by making a request through the following channels: https://derm.cs.sfu.ca/Welcome.html and https://www.isic‐archive.com/. Once permission is granted, interested parties can access the preprocessed images and the code required for model training and testing by reaching out to the corresponding author.

Articles from Skin Research and Technology are provided here courtesy of International Society of Biophysics and Imaging of the Skin, International Society for Digital Imaging of the Skin, and John Wiley & Sons Ltd

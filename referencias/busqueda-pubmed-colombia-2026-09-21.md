# Búsquedas en PubMed sobre trabajo publicado en Colombia (2026-09-21)

**Qué es:** el registro de las once búsquedas en PubMed que corrió el agente el
2026-09-21, en dos baterías.
- **Batería 1, cinco consultas, a las 18:26 (UTC−5).** Se corrió al verificar la
  v2 del estado del arte (D2, §2.4). Es la que devolvió los dos estudios
  colombianos de teledermatología, Sáenz et al. (2018) y Barrera-Valencia y
  Perea-Flórez (2024).
- **Batería 2, seis consultas, más tarde ese mismo día.** Se corrió para verificar
  un párrafo de la v3 que decía: *"una búsqueda en PubMed no devolvió trabajo
  publicado sobre fotografía corporal total en 3D ni sobre aprendizaje automático
  dermatológico en Colombia, ni un equivalente colombiano de la carga de
  cribado"*. La v4 retiró ese párrafo.

**Por qué se versiona:** la octava clase del registro de incidentes (regla 6 de
`CLAUDE.md`) exige que, cuando no se puede leer completa la fuente candidata, una
afirmación de ausencia diga qué se buscó y dónde. Este archivo es eso, con las
expresiones, los campos, la fecha y los resultados completos.

**LICENCIA:** obra del proyecto. Los listados reproducen solo datos
bibliográficos (PMID, año, revista abreviada y título) tal como los devuelve la
API de NCBI. No se reproduce ningún resumen: lo que se dice del contenido de un
registro es paráfrasis nuestra, y las pocas citas literales van entre comillas y
en cursiva.

**Herramienta:** NCBI E-utilities.
- `esearch.fcgi` da la lista de PMID (`db=pubmed`, `retmax=200`, `retmode=json`).
- `esummary.fcgi` da título, año y revista.
- `efetch.fcgi` (`retmode=xml`) da resumen y afiliaciones de los registros
  examinados.

**Fecha y corridas:** 2026-09-21.
- **Batería 1.** A las 18:26 se corrió con `retmax=5`, así que de cada consulta
  solo se vieron los cinco primeros PMID. Se repitió a las 20:05 con listas
  completas: los cinco conteos y los cinco primeros PMID de cada consulta
  coinciden con los de las 18:26.
- **Batería 2.** La primera corrida listó solo los 40 primeros resultados de la
  consulta 2.4; los 19 restantes se listaron después. Se repitió a las 18:57 con
  listas completas, y los seis conteos coinciden entre las dos corridas.

**Campos.** La batería 1 usa `Colombia[tiab]` y también "Colombia" sin campo. La
batería 2 usa dos campos, porque "en Colombia" admite dos lecturas:
- `Colombia[tiab]` busca la palabra en el título o el resumen. Recoge trabajos
  **sobre** Colombia.
- `Colombia[ad]` busca la palabra en la afiliación de algún autor. Recoge
  trabajos **hechos desde** Colombia, usen o no datos colombianos. Acierta con
  cualquier afiliación que contenga la palabra, incluida una dirección como
  "Vía Puerto Colombia, Barranquilla".
- **"Colombia" sin campo** (solo en la batería 1): PubMed lo traduce como
  `"colombia"[MeSH Terms] OR "colombia"[All Fields] OR "colombia s"[All Fields]`.

---

## Batería 1: verificación de la v2 (18:26)

**Procedencia de las expresiones.** Se copiaron de la transcripción de la sesión
en que se corrieron, no de memoria. Son las cinco consultas de una misma orden,
tal como se enviaron a `esearch.fcgi`. A diferencia de la batería 2, van sin
comillas en las frases de varias palabras, y PubMed las descompone palabra por
palabra. Por eso la consulta 1.3 devuelve sobre todo registros ajenos a la piel.

| # | Consulta | Resultados |
|---|---|---|
| 1.1 | `teledermatology[tiab] AND Colombia` | 5 |
| 1.2 | `(telemedicine OR teledermatology) AND (dermatology OR skin) AND Colombia[tiab]` | 3 |
| 1.3 | `(total body photography OR 3D total body OR mole mapping) AND Colombia` | 13 |
| 1.4 | `(machine learning OR deep learning OR artificial intelligence) AND (skin cancer OR melanoma OR dermatology) AND Colombia[tiab]` | 1 |
| 1.5 | `melanoma AND screening AND Colombia[tiab]` | 27 |

**Resultados completos (corrida de las 20:05).** [E] marca los registros
examinados, que tienen ficha propia en `referencias/`: 29785181 y 38669106
(teledermatología) y 38048957 (mapeo corporal digital). Los demás se
clasificaron solo por el título.

### 1.1. `teledermatology[tiab] AND Colombia`: 5

- 38909171 (2024, *Dermatol Ther (Heidelb)*). A Systematic Review and Meta-analysis of Mobile Health Applications and Telemonitoring in Atopic Dermatitis Self-Management.
- [E] 38669106 (2024, *Telemed J E Health*). Comparison of Costs in Teledermatology Using PC and Camera Versus Smartphone.
- 34990342 (2021, *Acta Dermatovenerol Croat*). Potential Dermatological Conditions Resulting from a Prolonged Stay at Home during the COVID-19 Pandemic: A Review.
- [E] 29785181 (2018, *Int J Telemed Appl*). On Using a Mobile Application to Support Teledermatology: A Case Study in an Underprivileged Area in Colombia.
- 27690203 (2016, *Telemed J E Health*). Practice Guidelines for Teledermatology.

### 1.2. `(telemedicine OR teledermatology) AND (dermatology OR skin) AND Colombia[tiab]`: 3

- 36972285 (2023, *PLoS Negl Trop Dis*). Randomized trial evaluating an mHealth intervention for the early community-based detection and follow-up of cutaneous leishmaniasis in rural Colombia.
- [E] 29785181 (2018, *Int J Telemed Appl*). On Using a Mobile Application to Support Teledermatology: A Case Study in an Underprivileged Area in Colombia.
- 17954469 (2007, *J Med Internet Res*). Web-based asynchronous teleconsulting for consumers in Colombia: a case study.

### 1.3. `(total body photography OR 3D total body OR mole mapping) AND Colombia`: 13

- 40537107 (2025, *J Bone Metab*). Positive Effect of Yerba Mate (Ilex paraguariensis) Consumption on Bone Mineral Density in Postmenopausal Women Assessed by Dual Energy X-Ray Absorptiometry-Based 3-Dimensional Modeling.
- 39339721 (2024, *Nutrients*). Sum of Skinfold-Corrected Girths Correlates with Resting Energy Expenditure: Development of the NRG(CO) Equation.
- [E] 38048957 (2024, *Actas Dermosifiliogr*). [Translated article] Dermoscopic Changes in Melanocytic Lesions in 368 Patients With Atypical Nevus Syndrome and Their Association With Melanoma Incidence: A Cohort Study.
- 36472537 (2023, *Radiology*). Risk of Acute Kidney Injury Following Contrast-enhanced CT in a Cohort of 10 407 Children and Adolescents.
- 35648191 (2022, *Aesthetic Plast Surg*). Quantitative Mobility Analysis of the Face and its Relevance for Surgical and Non-surgical Aesthetic Facial Procedures.
- 34043153 (2021, *Clin Transl Oncol*). 5-year results of accelerated partial breast irradiation (APBI) with SBRT (stereotactic body radiation therapy) and exactrac adaptive gating (Novalis(®)) for very early breast cancer patients: was it all worth it?
- 33987696 (2021, *Aesthetic Plast Surg*). The Influence of Different Light Angles During Standardized Patient Photographic Assessment on the Aesthetic Perception of the Face.
- 33566882 (2021, *Rev Paul Pediatr*). CRANIAL OSTEOMYELITIS AS A COMPLICATION OF FURUNCULAR MYIASIS.
- 32662554 (2020, *J Cosmet Dermatol*). Clinical validation of the temporal lifting technique using soft tissue fillers.
- 32364980 (2020, *J Therm Biol*). Paper wasps are darker at high elevation.
- 30910763 (2019, *J Stomatol Oral Maxillofac Surg*). Exploratory study of the three-dimensional morphological variation of the jaw associated to teeth loss.
- 30424890 (2019, *Rev Esp Anestesiol Reanim (Engl Ed)*). Radiologic assessment of gastric emptying of water-soluble contrast media: New data security from a longitudinal study.
- 30150329 (2018, *BMJ Case Rep*). Hypothalamic relapse of a cardiac large B-cell lymphoma presenting with memory loss, confabulation, alexia-agraphia, apathy, hypersomnia, appetite disturbances and diabetes insipidus.

### 1.4. `(machine learning OR deep learning OR artificial intelligence) AND (skin cancer OR melanoma OR dermatology) AND Colombia[tiab]`: 1

- 42140643 (2026, *J Rheumatol*). Transforming Psoriatic Disease Care Through Innovation and Real-World Data: GRAPPA 2025 Soapbox Highlights.

### 1.5. `melanoma AND screening AND Colombia[tiab]`: 27

- 42749123 (2026, *Actas Dermosifiliogr*). Temporal trends in melanoma and non-melanoma skin cancer mortality in Colombia, 2008-2022.
- 42307794 (2026, *Head Neck Pathol*). Oral Melanoma: A South American Collaborative Series of 21 Cases.
- 42211527 (2026, *Front Oncol*). Clinical characteristics and real-world survival in acral melanoma: experience from a comprehensive cancer center in Latin America.
- 42035614 (2026, *Cancer Epidemiol*). Epidemiology, clinical characteristics, and survival of acral and non-acral melanoma in Colombia.
- 42004443 (2026, *Public Health Pract (Oxf)*). Economic benefit of expanding mammography screening for breast cancer in Colombia: A cost modelling analysis.
- 40497569 (2025, *Dermatol Surg*). Is Functional Surgery the Treatment of Choice for Subungual Melanoma in Situ and Subungual Microinvasive Melanoma? A Retrospective Cohort Study in a Latin American Population.
- 39869442 (2024, *Melanoma Manag*). Melanoma in a Colombian population: a survival study.
- 39044133 (2024, *BMC Cancer*). Survival of patients with mucosal melanoma in Cali, Colombia: a retrospective cohort study.
- [E] 38048957 (2024, *Actas Dermosifiliogr*). [Translated article] Dermoscopic Changes in Melanocytic Lesions in 368 Patients With Atypical Nevus Syndrome and Their Association With Melanoma Incidence: A Cohort Study.
- 37849291 (2024, *Ophthalmic Epidemiol*). Epidemiology of Eye Cancer in Cali, Colombia: A 55-Year Study.
- 37372871 (2023, *Healthcare (Basel)*). Clinical Cancer Research in South America and Potential Health Economic Impacts.
- 37216624 (2023, *JCO Glob Oncol*). Clinical Outcomes and Prognostic Factors of Patients With Early Malignant Melanoma in One Latin American Country: Results of the Epidemiological Registry of Malignant Melanoma in Colombia Study.
- 37196281 (2023, *Dermatol Pract Concept*). Dermoscopy in Selected Latin American Countries: A Preliminary Look into Current Trends and Future Opportunities Among Dermatology Residency Programs.
- 36575614 (2023, *J Vet Dent*). Histopathological Results of Mouth Lesions in Dogs and Cats from Colombia.
- 35722901 (2022, *J Int Med Res*). Cutaneous melanoma incidence, mortality, and survival in Manizales, Colombia: a population-based study.
- 35141880 (2022, *Int J Dermatol*). Burden of skin cancer in Colombia.
- 34214264 (2021, *Biomedica*). Exogenous pigmentation by silver nitrate: Dermatological and toxicological aspects, case report.
- 33102592 (2020, *Biomed Res Int*). CDKN2A Polymorphism in Melanoma Patients in Colombian Population: A Case-Control Study.
- 33014232 (2020, *Radiol Case Rep*). Extrapulmonary tuberculosis: mimicking metastases in a patient with melanoma in a high TB-burden country; case report.
- 30793185 (2019, *Mil Med*). Health Characteristics of the Wayuu Indigenous People.
- 30570006 (2018, *Rev Salud Publica (Bogota)*). Epidemiological profile of primary cutaneous melanoma over a 15-year period at a private skin cancer center in Colombia.
- 29983461 (2018, *Colomb Med (Cali)*). Reliable information for cancer control in Cali, Colombia.
- 27992981 (2016, *Biomedica*). [Years of life lost as a measure of cancer burden in Colombia, 1997-2012].
- 27518480 (2017, *J Eur Acad Dermatol Venereol*). Survival of acral lentiginous melanoma in the National Cancer Institute of Colombia.
- 26296697 (2016, *Photodiagnosis Photodyn Ther*). Photodynamic therapy: Progress toward a scientific and clinical network in Latin America.
- 25124243 (2013, *Rev Salud Publica (Bogota)*). [Colombian experience regarding skin cancer: healthcare-related barriers to access to healthcare and bureaucratic itineraries].
- 19662813 (2009, *Invest Clin*). [Cytogenetic study in peripheral blood of melanoma patients].

**Lo encontrado.**
1. **1.1 y 1.2** devuelven los dos estudios colombianos de teledermatología que
   tienen ficha: 29785181 (Sáenz et al., 2018), que sale en ambas, y 38669106
   (Barrera-Valencia y Perea-Flórez, 2024), que sale solo en la 1.1.
   - Además aparece 36972285, un ensayo aleatorizado de una intervención mHealth
     para detectar leishmaniasis cutánea en zonas rurales de Colombia, que no se
     examinó.
   - El resto, a juzgar por el título: una revisión sobre dermatitis atópica, una
     revisión sobre afecciones de piel durante el confinamiento por COVID-19 y
     unas guías de práctica de teledermatología, ninguna sobre un servicio
     colombiano. Queda 17954469, un estudio de caso de teleconsulta web para
     consumidores en Colombia, que el título no restringe a dermatología y que no
     se examinó.
2. **1.3 y 1.5** devuelven 38048957 (Mejía Posada et al., 2024), el mismo
   registro que encuentra la batería 2.
3. **1.4** devuelve solo 42140643, el mismo que la consulta 2.3.

---

## Batería 2: verificación de la v3 (seis consultas)

### Las consultas

Cada consulta es la expresión del tema seguida de `AND Colombia[tiab]` o de
`AND Colombia[ad]`.

**Fotografía corporal total y seguimiento digital**

```
(("total body photography" OR "total-body photography" OR "3D total body" OR "total body imaging" OR "whole body imaging" OR "whole-body photography" OR "mole mapping" OR "body mapping" OR "sequential digital dermoscopy" OR "digital dermoscopy follow-up"))
```

**Aprendizaje automático aplicado a piel**

```
(("machine learning" OR "deep learning" OR "artificial intelligence" OR "neural network" OR convolutional OR "computer-aided" OR "automated classification") AND (melanoma OR "skin cancer" OR "skin lesion" OR "skin lesions" OR dermoscop* OR dermatolog*))
```

**Carga de cribado (lesiones extirpadas o biopsiadas por cada maligna)**

```
(("number needed to excise" OR "number needed to biopsy" OR "number needed to treat" OR "biopsy ratio" OR "benign-to-malignant" OR "unnecessary excisions" OR "unnecessary biopsies") AND (melanoma OR "skin cancer" OR nevus OR nevi))
```

| # | Tema | Campo | Resultados |
|---|---|---|---|
| 2.1 | Fotografía corporal total y seguimiento digital | `tiab` | 2 |
| 2.2 | Fotografía corporal total y seguimiento digital | `ad` | 6 |
| 2.3 | Aprendizaje automático aplicado a piel | `tiab` | 1 |
| 2.4 | Aprendizaje automático aplicado a piel | `ad` | 59 |
| 2.5 | Carga de cribado | `tiab` | 0 |
| 2.6 | Carga de cribado | `ad` | 1 |

---

### Resultados completos

**[E]** marca los registros examinados: se leyeron el resumen y las
afiliaciones con `efetch`. Los demás se clasificaron **solo por el título**.

#### 2.1. Fotografía corporal total y seguimiento digital, `Colombia[tiab]`: 2

- [E] 38048957 (2024, *Actas Dermosifiliogr*). [Translated article] Dermoscopic Changes in Melanocytic Lesions in 368 Patients With Atypical Nevus Syndrome and Their Association With Melanoma Incidence: A Cohort Study.
- 37982434 (2023, *Sex Reprod Health Matters*). Tírala Plena: findings from the formative research to inform the initiative "Reaching those most left behind through comprehensive sexuality education for out-of-school young people" in Colombia.

#### 2.2. Fotografía corporal total y seguimiento digital, `Colombia[ad]`: 6

- 38050325 (2024, *J Cachexia Sarcopenia Muscle*). Using magnetic resonance imaging to measure head muscles: An innovative method to opportunistically determine muscle mass and detect sarcopenia.
- [E] 38048957 (2024, *Actas Dermosifiliogr*). [Translated article] Dermoscopic Changes in Melanocytic Lesions in 368 Patients With Atypical Nevus Syndrome and Their Association With Melanoma Incidence: A Cohort Study.
- 37982434 (2023, *Sex Reprod Health Matters*). Tírala Plena: findings from the formative research to inform the initiative "Reaching those most left behind through comprehensive sexuality education for out-of-school young people" in Colombia.
- 34602669 (2021, *Radiol Bras*). Whole-body magnetic resonance imaging for the diagnosis of metastasis in children and adolescents: a systematic review and meta-analysis.
- 25293431 (2015, *Eur J Clin Nutr*). Effect of resistance training on resting metabolic rate and its estimation by a dual-energy X-ray absorptiometry metabolic map.
- 21630165 (2011, *Comput Methods Biomech Biomed Engin*). A kinematic method for computing the motion of the body centre-of-mass (CoM) during walking: a Bayesian approach.

#### 2.3. Aprendizaje automático aplicado a piel, `Colombia[tiab]`: 1

- 42140643 (2026, *J Rheumatol*). Transforming Psoriatic Disease Care Through Innovation and Real-World Data: GRAPPA 2025 Soapbox Highlights.

#### 2.4. Aprendizaje automático aplicado a piel, `Colombia[ad]`: 59

- [E] 42728887 (2026, *Skin Res Technol*). Demographic Reporting and the Absence of Hispanic/Latino Representation in Dermatology Artificial Intelligence: A Scoping Review.
- 42705247 (2026, *Lancet Public Health*). Global, regional, and national prevalence of second-hand smoke and attributable disease burden in 204 countries and territories, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42613592 (2026, *Clin Transl Allergy*). ARIA-EAACI 2025: Person-Centred, Digitally Enabled and Artificial Intelligence-Assisted Change Management in Airway Diseases: An OECD Best Practice for Integrated Care for Chronic Diseases.
- 42612664 (2026, *Lancet HIV*). Global, regional, and national burden of HIV/AIDS, 1990-2023, with the estimated burden attributable to intimate partner violence and forecasted impacts of funding cuts through 2030: results from the Global Burden of Disease Study 2023.
- 42612648 (2026, *Lancet Public Health*). Global and regional progress towards reduced burden of oral conditions between 2019 and 2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42612647 (2026, *Lancet Public Health*). Measuring the composition and availability of human resources for health by sex in 204 countries and territories, 1990-2023, and workforce gaps for universal health coverage: a systematic analysis for the Global Burden of Disease Study 2023.
- [E] 42512375 (2026, *Cancers (Basel)*). Basal Cell Carcinoma Research Landscape Overview via Latent Dirichlet Allocation and HJ-Biplot Analysis.
- 42476159 (2026, *Lancet Public Health*). Global, regional, and national burden of road injuries 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42385762 (2026, *Lancet Infect Dis*). Global, regional, and national burden of tuberculosis and multidrug-resistant tuberculosis by HIV status, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42229499 (2026, *Lancet Infect Dis*). Global burden of enteric infectious diseases, diarrhoeal diseases, and corresponding aetiologies, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42167272 (2026, *Lancet*). Updated trends in the global prevalence and burden of mental disorders, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 42140643 (2026, *J Rheumatol*). Transforming Psoriatic Disease Care Through Innovation and Real-World Data: GRAPPA 2025 Soapbox Highlights.
- 42093260 (2026, *World J Mens Health*). Artificial Intelligence-Driven Semen Analysis: Transforming Semen Analysis for Male Infertility Diagnostics.
- 42010942 (2026, *Oral Dis*). Quality and Readability of Large Language Models' Responses to Oral Lichen Planus Patients' FAQs.
- [E] 41999415 (2026, *Graefes Arch Clin Exp Ophthalmol*). Imaging-based machine learning for the diagnosis and prognosis of uveal melanoma: a systematic review and meta analysis.
- 41946660 (2026, *World J Mens Health*). Artificial Intelligence in Non-Obstructive Azoospermia: State of the Art in Sperm Retrieval.
- 41911930 (2026, *Lancet Neurol*). Global, regional, and national burden of meningitis, its risk factors, and aetiologies, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 41785894 (2026, *Lancet Oncol*). Global, regional, and national burden of breast cancer among females, 1990-2023, with forecasts to 2050: a systematic analysis for the Global Burden of Disease Study 2023.
- [E] 41418903 (2026, *Actas Dermosifiliogr*). Advances in Artificial Intelligence in Cosmetic Dermatology.
- 41412141 (2026, *Lancet Infect Dis*). Global burden of lower respiratory infections and aetiologies, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 41386261 (2026, *Lancet*). Disease burden attributable to intimate partner violence against females and sexual violence against children in 204 countries and territories, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 41350966 (2026, *Clin Rheumatol*). Living with systemic lupus erythematosus in 2024: Latin American experience based on a patient survey.
- 41268627 (2026, *Allergy*). Methodology for the Development of the Allergic Rhinitis and Its Impact on Asthma (ARIA)-EAACI 2024-2025 Guidelines: From Evidence-to-Decision Frameworks to Digitalised Shared Decision-Making Algorithms.
- [E] 41264800 (2025, *Medwave*). Artificial intelligence for skin lesion classification and diagnosis in dermatology: A narrative review.
- 41213283 (2025, *Lancet*). Global, regional, and national burden of chronic kidney disease in adults, 1990-2023, and its attributable risk factors: a systematic analysis for the Global Burden of Disease Study 2023.
- 41135560 (2025, *Lancet Glob Health*). Global, regional, and national sepsis incidence and mortality, 1990-2021: a systematic analysis.
- 41092928 (2025, *Lancet*). Global burden of 292 causes of death in 204 countries and territories and 660 subnational locations, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 41092927 (2025, *Lancet*). Global age-sex-specific all-cause mortality and life expectancy estimates for 204 countries and territories and 660 subnational locations, 1950-2023: a demographic analysis for the Global Burden of Disease Study 2023.
- 41092926 (2025, *Lancet*). Burden of 375 diseases and injuries, risk-attributable burden of 88 risk factors, and healthy life expectancy in 204 countries and territories, including 660 subnational locations, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023.
- 41040836 (2025, *Clin Case Rep*). Novel De Novo DLL4 Missense and Highly Accurate Protein Structure Prediction in Adams-Oliver Type 6 Syndrome.
- 41033837 (2025, *J Rheumatol*). Prologue: Group for Research and Assessment of Psoriasis and Psoriatic Arthritis (GRAPPA) 2024 Annual Meeting.
- 41024593 (2026, *J Ultrasound Med*). Artificial Intelligence Deep Learning Ultrasound Discrimination of Cosmetic Fillers: A Multicenter Study.
- 41015051 (2025, *Lancet*). The global, regional, and national burden of cancer, 1990-2023, with forecasts to 2050: a systematic analysis for the Global Burden of Disease Study 2023.
- 40990886 (2025, *J Am Coll Cardiol*). Global, Regional, and National Burden of Cardiovascular Diseases and Risk Factors in 204 Countries and Territories, 1990-2023.
- 40739974 (2025, *Ewha Med J*). The TRIPOD-LLM reporting guideline for studies using large language models: a Korean translation.
- 40493367 (2025, *JAMA Netw Open*). Multinational Attitudes Toward AI in Health Care and Diagnostics Among Hospital Patients.
- 40406922 (2025, *JAMA Neurol*). Global, Regional, and National Burden of Nontraumatic Subarachnoid Hemorrhage: The Global Burden of Disease Study 2021.
- 40256633 (2025, *Rheumatol Adv Pract*). Disease burden in inflammatory arthritis: an unsupervised machine learning approach of the COVAD-2 e-survey dataset.
- 39918978 (2025, *Rheumatology (Oxford)*). CAPI-Detect: machine learning in capillaroscopy reveals new variables influencing diagnosis.
- 39779929 (2025, *Nat Med*). The TRIPOD-LLM reporting guideline for studies using large language models.
- [E] 39771915 (2024, *Sensors (Basel)*). Enhanced Detection of Leishmania Parasites in Microscopic Images Using Machine Learning Models.
- [E] 39498903 (2025, *Am J Dermatopathol*). Evaluating Advanced Machine Learning Models for Histopathological Diagnosis of Hansen Disease.
- 39447753 (2025, *J Am Acad Dermatol*). Determining the medical Spanish translation capabilities of three artificial intelligence translation models for Mohs micrographic surgical instructions.
- 39366729 (2024, *Lancet Public Health*). Forecasting the effects of smoking prevalence scenarios on years of life lost and life expectancy from 2022 to 2050: a systematic analysis for the Global Burden of Disease Study 2021.
- 39304265 (2024, *Lancet Neurol*). Global, regional, and national burden of stroke and its risk factors, 1990-2021: a systematic analysis for the Global Burden of Disease Study 2021.
- 38971567 (2024, *J Allergy Clin Immunol Pract*). Concepts for the Development of Person-Centered, Digitally Enabled, Artificial Intelligence-Assisted ARIA Care Pathways (ARIA 2024).
- [E] 38742379 (2024, *Skin Res Technol*). Comprehensive analysis of clinical images contributions for melanoma classification using convolutional neural networks.
- [E] 38606989 (2024, *Histopathology*). Histological interpretation of spitzoid tumours: an extensive machine learning-based concordance analysis for improving decision making.
- 38092509 (2023, *J Am Coll Cardiol*). Global Burden of Cardiovascular Diseases and Risks, 1990-2022.
- 37459304 (2023, *PLoS Genet*). Combined genome-wide association study of 136 quantitative ear morphology traits in multiple populations reveal 8 novel loci.
- 37175421 (2023, *Int J Mol Sci*). 3D Visualization, Skeletonization and Branching Analysis of Blood Vessels in Angiogenesis.
- [E] 36612037 (2022, *Cancers (Basel)*). Deep Learning for Skin Melanocytic Tumors in Whole-Slide Images: A Systematic Review.
- 36030090 (2022, *J Cosmet Dermatol*). Aesthetic medicine-Quo Vadis?
- [E] 36010243 (2022, *Diagnostics (Basel)*). A Fair Performance Comparison between Complex-Valued and Real-Valued Neural Networks for Disease Detection.
- 34967848 (2022, *JAMA Oncol*). Cancer Incidence, Mortality, Years of Life Lost, Years Lived With Disability, and Disability-Adjusted Life Years for 29 Cancer Groups From 2010 to 2019: A Systematic Analysis for the Global Burden of Disease Study 2019.
- 34363696 (2021, *Int J Dermatol*). Cutaneous myiasis in skin cancer and malignant wounds: a systematic review.
- [E] 33407213 (2021, *BMC Med Imaging*). Melanoma diagnosis using deep learning techniques on dermatoscopic images.
- [E] 28969863 (2018, *J Am Acad Dermatol*). Results of the 2016 International Skin Imaging Collaboration International Symposium on Biomedical Imaging challenge: Comparison of the accuracy of computer algorithms to dermatologists for the diagnosis of melanoma from dermoscopic images.
- 26928228 (2016, *Nat Genet*). Breast cancer risk variants at 6q25 display different phenotype associations and regulate ESR1, RMND1 and CCDC170.

#### 2.5. Carga de cribado, `Colombia[tiab]`: 0

Sin resultados.

#### 2.6. Carga de cribado, `Colombia[ad]`: 1

- [E] 40078077 (2025, *J Med Econ*). Number needed to treat (NNT) with pembrolizumab as an adjuvant therapy in resected patients with high-risk stage II (IIB and IIC) melanoma and its application to cost of preventing an event (COPE) in Mexico.

---

### Registros examinados: qué dicen

Todo es paráfrasis nuestra del resumen, salvo lo que va entre comillas y en
cursiva. Los recuentos de autores con afiliación colombiana salen del XML de
PubMed.

**Fotografía corporal total**

- **38048957**, *Actas Dermo-Sifiliográficas* 2024 (artículo traducido). Seis
  autores, todos de la Universidad CES de Medellín. Es una cohorte retrospectiva
  de 368 pacientes con síndrome de nevus atípico, atendidos en *"a specialized
  skin cancer and digital body mapping clinic in Medellin, Colombia"* entre 2017
  y 2022. Estudia los cambios dermatoscópicos a cinco años y su asociación con
  la aparición de melanoma, que se diagnosticó en el 12,2 % de los pacientes
  durante el seguimiento.
  - Se trata de mapeo corporal digital. El resumen no menciona fotografía en 3D
    ni dice cuántas lesiones se marcaron o se extirparon. No se leyó el texto
    completo.
  - **Corrección:** en la primera corrida este registro se clasificó como no
    pertinente, solo por el título. El resumen muestra que sí lo es: es
    seguimiento con mapeo corporal digital en Colombia, sin el 3D.

**Aprendizaje automático sobre imágenes de lesiones cutáneas: trabajos
originales**

- **38742379**, *Skin Research and Technology* 2024. Los cinco autores tienen
  afiliación colombiana (Universidad de los Andes y Universidad Externado de
  Colombia). Comparan redes convolucionales que clasifican melanoma a partir de
  imágenes clínicas, dermatoscópicas o de ambas. Los 914 pares de imágenes
  salen de repositorios públicos (la base de los 7 criterios e ISIC), no de
  pacientes colombianos; así lo dice la sección 2.1 del texto completo, en
  PMC11091779.
- **33407213**, *BMC Medical Imaging* 2021. Uno de los cuatro autores tiene
  afiliación colombiana (Universidad del Norte). Aplican aprendizaje profundo a
  imágenes dermatoscópicas para diagnosticar melanoma. No se comprobó de dónde
  salen los datos.
- **36010243**, *Diagnostics* 2022. Dos de los tres autores tienen afiliación
  colombiana (Universidad del Norte). Comparan redes de valores complejos y
  reales para detectar melanoma y soplos cardíacos, con datos de ISIC2017, PH2 y
  Pascal.

**Aprendizaje automático sobre histología o microscopía de piel**

- **38606989**, *Histopathology* 2024. Dos de los once autores tienen afiliación
  colombiana (Fundación Universitaria Sanitas). Clasifican tumores spitzoides
  por histología, con 122 tumores.
- **39498903**, *American Journal of Dermatopathology* 2025. Los cuatro autores
  tienen afiliación colombiana (Universidad CES). Diagnóstico histopatológico de
  la lepra.
- **39771915**, *Sensors* 2024. Los cinco autores tienen afiliación colombiana
  (Pontificia Universidad Javeriana). Detectan Leishmania en frotis, para el
  diagnóstico de la leishmaniasis cutánea.

**Revisiones, retos y otros**

- **36612037**, *Cancers* 2022. Uno de los nueve autores tiene afiliación
  colombiana. Revisión sistemática del aprendizaje profundo sobre láminas
  completas de tumores melanocíticos.
- **41264800**, *Medwave* 2025. Siete de los ocho autores tienen afiliación
  colombiana (Universidad de La Sabana y Fundación Santa Fe de Bogotá). Revisión
  narrativa de la IA para clasificar lesiones cutáneas.
- **42728887**, *Skin Research and Technology* 2026. Uno de los dos autores es de
  la Pontificia Universidad Javeriana. Revisión de alcance sobre cómo se reportan
  los datos demográficos en la IA dermatológica, y sobre la ausencia de
  representación hispana y latina.
- **41418903**, *Actas Dermo-Sifiliográficas* 2026. Los tres autores son de la
  Universidad del Valle. Revisión de la IA en dermatología cosmética.
- **28969863**, *Journal of the American Academy of Dermatology* 2018. Uno de
  los dieciséis autores tiene afiliación en Medellín. Presenta los resultados del reto ISIC
  2016: algoritmos frente a dermatólogos sobre imágenes dermatoscópicas.
- **41999415**, *Graefe's Archive for Clinical and Experimental Ophthalmology*
  2026. Revisión sistemática sobre el melanoma uveal. Es ocular, no cutáneo.
- **42512375**, *Cancers* 2026. Bibliometría del carcinoma basocelular con LDA:
  el aprendizaje automático se aplica a la literatura, no a lesiones.
- **40078077**, consulta 2.6. Dos de los quince autores tienen afiliación en MSD
  Colombia. Calcula el número necesario a tratar de un tratamiento adyuvante del
  melanoma, no una medida de cribado.

---

### Lo encontrado, por consulta

1. **2.1. Fotografía corporal total, `[tiab]` (2 resultados).** Uno es pertinente:
   38048957, mapeo corporal digital en 2D. El otro no trata de piel.
2. **2.2. Fotografía corporal total, `[ad]` (6 resultados).** Aparece el mismo
   38048957. Los otros cinco no tratan de piel, a juzgar por el título.
3. **2.3. Aprendizaje automático, `[tiab]` (1 resultado).** 42140643, sobre la
   enfermedad psoriásica (reunión de GRAPPA). No trata de lesiones; se clasificó
   por el título.
4. **2.4. Aprendizaje automático, `[ad]` (59 resultados).**
   - Tres trabajos originales sobre imágenes de lesiones cutáneas: 38742379,
     33407213 y 36010243.
   - Tres sobre histología o microscopía de piel: 38606989, 39498903 y
     39771915.
   - Siete registros examinados más, entre revisiones, un reto y otros:
     36612037, 41264800, 42728887, 41418903, 28969863, 41999415 y 42512375.
   - El resto no aplica aprendizaje automático a lesiones cutáneas, a juzgar por
     el título. Buena parte son artículos del Global Burden of Disease con
     coautores colombianos. Varios tocan la dermatología por otro lado:
     psoriasis, dermatología cosmética, cirugía de Mohs y miasis.
   - En los trabajos originales cuyos datos se comprobaron (38742379 y
     36010243), las imágenes vienen de repositorios públicos, no de pacientes
     colombianos.
5. **2.5. Carga de cribado, `[tiab]` (0 resultados).**
6. **2.6. Carga de cribado, `[ad]` (1 resultado).** No es pertinente: es el número
   necesario a tratar de una terapia.

Los dos estudios colombianos de teledermatología —Sáenz et al. (2018) y
Barrera-Valencia y Perea-Flórez (2024)— no salen de estas seis consultas, porque
ninguna busca teledermatología. Salen de la batería 1 (consultas 1.1 y 1.2) y
tienen ficha propia:
`referencias/saenz-2018-app-teledermatologia-colombia.md` y
`referencias/barrera-valencia-2024-costos-teledermatologia.md`.

---

## Qué no se buscó: límites de este registro

Valen para las dos baterías.

- **Solo PubMed.** No se consultaron LILACS, SciELO, Scopus, repositorios
  institucionales colombianos, tesis, literatura gris ni revistas no indexadas en
  PubMed.
- **Solo expresiones en inglés.** No se buscaron términos en español, como
  "fotografía corporal total", "mapeo corporal" o "aprendizaje automático".
- **Pertinencia por título,** salvo en los registros marcados [E].
- **Frases sin comillas en la batería 1.** PubMed las descompone palabra por
  palabra, así que esas consultas son a la vez más amplias y menos precisas que
  las de la batería 2.
- **Lo que cada campo no ve.** `[ad]` no encuentra a autores colombianos con
  afiliación extranjera. `[tiab]` no encuentra trabajos con datos colombianos que
  no nombren el país en el título o el resumen.
- **Los conteos cambian con el tiempo.** Repetir las consultas otro día puede dar
  otros números. Los de arriba son los del 2026-09-21.

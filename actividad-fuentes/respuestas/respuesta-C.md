Herramienta: NotebookLM, cuaderno nuevo con los 22 archivos de corpus-c y nada más.
Fecha y hora: 2026-09-27 20:47:58 (-0500).
Corpus cargado: los 22 archivos de Downloads/corpus-c, subidos hacia las 20:45, con kurtansky-2024-kaggle.txt en la versión sin reglas (SHA-256 5eac339220e20127…); en esa carpeta solo estaba esa versión. Lo confirmó la persona.

---

Diversos estudios metodológicos y de evaluación en inteligencia artificial médica han medido el impacto de dividir los datos por imagen/registro (record-wise) en lugar de dividirlos por paciente (subject-wise). A continuación se presentan 5 referencias de la literatura incluidas en tus fuentes que cuantifican y explican esta sobreestimación del desempeño:

1. Saeb et al. (2017)
   * Afirmación concreta: Demuestra que la validación cruzada dividida por registro o imagen (record-wise CV) sobreestima masivamente la precisión diagnóstica debido a que el algoritmo de aprendizaje automático aprende atajos asociados a las características únicas de la identidad del sujeto. En su revisión sistemática de estudios clínicos, la tasa mediana de error fue del 5.60% con partición por registro/imagen frente al 13.00% con partición por paciente (más del doble de error real cuando se evalúa correctamente).
   * DOI: `10.1093/gigascience/gix019`
2. Kapoor y Narayanan (2023)
   * Afirmación concreta: Clasifica la falta de independencia entre las muestras de entrenamiento y prueba (como situar observaciones o imágenes procedentes de un mismo paciente en ambos conjuntos, tipo de fuga L3.2) como una de las causas principales de filtración de datos (data leakage). Esta práctica crea relaciones espurias que no existen en la población real, produciendo estimaciones de desempeño artificialmente altas e irreproducibles en la literatura científica.
   * DOI: `10.1016/j.patter.2023.100804`
3. Cassidy et al. (2022)
   * Afirmación concreta: Examina los conjuntos de datos dermatológicos de la International Skin Imaging Collaboration (ISIC) y muestra que la presencia de imágenes duplicadas o múltiples tomas de las mismas lesiones/pacientes repartidas entre los subconjuntos de entrenamiento y prueba introduce un sesgo cuantitativo severo. Al aplicar una estrategia de eliminación de duplicados (removiendo 14,310 imágenes sobrelapadas) y evaluar en conjuntos de prueba limpios y estrictamente segregados, el desempeño en clasificación se reduce drásticamente, obteniendo valores de AUC de apenas 0.50 a 0.56 en el conjunto de prueba ISIC 2017 en modelos base sin transfer learning.
   * DOI: `10.1016/j.media.2021.102305`
4. Yan et al. (2025)
   * Afirmación concreta: Señala que dividir imágenes o lesiones de un mismo paciente a través de las particiones de entrenamiento, validación y prueba genera fuga de datos (data leakage) y compromete la validez de la evaluación del modelo. Destaca que para obtener evaluaciones realistas en dermatología es indispensable utilizar versiones "limpias" de los benchmarks (como las versiones corregidas de HAM10000 y BCN20000), donde todas las lesiones pertenecientes a un mismo paciente quedan restringidas a una sola partición.
   * DOI: `10.1038/s41591-025-03747-y`
5. Little et al. (2017)
   * Afirmación concreta: Analiza las propiedades probabilísticas de las estrategias de validación cruzada y confirma que dividir los datos aleatoriamente por registro en lugar de por sujeto viola la suposición de muestras idénticamente distribuidas cuando los datos están agrupados por paciente. Esto genera estimadores sesgados que subestiman significativamente el error de predicción real que tendría el modelo al enfrentarse a nuevos pacientes en la práctica clínica.
   * DOI: `10.1093/gigascience/gix020`

💡 Si te interesa profundizar en este tema, podemos analizar qué técnicas de partición estructurada (como grouped k-fold o block cross-validation) se recomiendan específicamente para corregir el sesgo en bases de datos con fotografías 3D corporales completas (Total Body Photography).

---

## Lista de citas, de la persona

A qué archivo del corpus apunta cada número de cita de NotebookLM, con su posición. Se pegó tal cual, el 2026-09-27; no forma parte de la respuesta.

[1] tras «...In a diagnosis scenario (Fig. 1), we want...» → saeb-2017.txt
[2] tras «...Then, we extracted the reported accuracies...» → saeb-2017.txt
[3] tras «.... 2017 Mar 15;6(5):1–9. doi: 10.1093/gigascience/gix019
The need to approximate the use-case in clinical machine learning...» → saeb-2017.txt
[4] tras «...[L3.1] Temporal leakage. When an ML model is used to make pred...» → kapoor-narayanan-2023.txt
[5] tras «...Keywords: reproducibility, machine learning, leakage
Highlights...» → kapoor-narayanan-2023.txt
[6] tras «...Kapoor and Narayanan show that...» → kapoor-narayanan-2023.txt
[7] tras «.... 2023 Aug 4;4(9):100804\. doi: 10.1016/j.patter.2023.100804

Leakage and the r...» → kapoor-narayanan-2023.txt
[8] tras «...6\. Related work This section outlines...» → cassidy-2022.txt

[9] tras «...8\. Method This section details the followin...» → cassidy-2022.txt
[10] tras «...13\. Results Table 10 presents benchmark...» → cassidy-2022.txt
[11] tras «...12\. Delete all image ﬁles from each individual trainin...» → cassidy-2022.txt
[12] tras «...1\. Introduction Skin cancer is the most common of all cancers, with more peo...» → cassidy-2022.txt
[13] tras «...In this study, we introduce PanDerm, a versatile dermatology...» → yan-2025.txt
[14] tras «...Skin cancer and general skin condition classification datasets...» → yan-2025.txt
[15] tras «...BCN20000 (9 classes)

The BCN20000 (ref. 79) dat...» → yan-2025.txt
[16] tras «...Reporting summary

Further information on research design is available in the Nature...» → yan-2025.txt
[17] tras «...Keywords: machine learning, clinical applications, cross-validation...» → little-2017.txt

[18] tras «...Let us now split the data in a way that is conditioned on one...» → little-2017.txt
[19] tras «.... 2017 Mar 17;6(5):1–6\. doi: 10.1093/gigascience/gix020...» → little-2017.txt

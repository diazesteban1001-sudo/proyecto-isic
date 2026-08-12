# EDA diagnóstico — data/train-metadata.csv
Filas: 401059 · Columnas: 55
Columnas con al menos un faltante: 10
Target `target`: conteos {'0': 400666, '1': 393}, % positivos: 0.098
Grupos por `patient_id`: 1042 grupos, 384.89 filas/grupo en promedio (min 1, max 9184)
Columnas solo en train (11): ['iddx_1', 'iddx_2', 'iddx_3', 'iddx_4', 'iddx_5', 'iddx_full', 'lesion_id', 'mel_mitotic_index', 'mel_thick_mm', 'target', 'tbp_lv_dnn_lesion_confidence']
Columnas solo en test (0): []
Test es placeholder (3 filas), no se perfiló.
Duplicados exactos (excluyendo 2 columnas identificador ['isic_id', 'lesion_id']): 0
Columnas constantes: ['image_type']

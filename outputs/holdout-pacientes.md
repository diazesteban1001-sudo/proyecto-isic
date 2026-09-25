# Conjunto reservado — sellado sobre data/train-metadata.csv
Semilla 2026 · 20 % de los pacientes, estratificado por centro ('attribution') y por presencia de al menos una lesión maligna
Método: train_test_split estratificado de scikit-learn 1.9.0, sobre una fila por paciente ordenada por patient_id
Reservado: 209 pacientes · 52 portadores · 76 lesiones malignas
Desarrollo: 833 pacientes · 207 portadores · 317 lesiones malignas
Pacientes por centro, reservado / desarrollo (portadores entre paréntesis):
- ACEMID MIA: 9 (4) / 35 (16)
- Department of Dermatology, Hospital Clínic de Barcelona: 33 (13) / 130 (52)
- Department of Dermatology, University of Athens, Andreas Syggros Hospital of Skin and Venereal Diseases, Alexander Stratigos, Konstantinos Liopyris: 3 (1) / 13 (3)
- Frazer Institute, The University of Queensland, Dermatology Research Centre: 35 (8) / 141 (34)
- Memorial Sloan Kettering Cancer Center: 80 (21) / 318 (85)
- University Hospital of Basel: 46 (3) / 184 (10)
- ViDIR Group, Department of Dermatology, Medical University of Vienna: 3 (2) / 12 (7)
Lista de patient_id reservados: outputs/holdout-pacientes.json, campo `pacientes_reservados`.

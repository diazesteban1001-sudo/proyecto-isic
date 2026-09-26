# Fase 4 — M4b − M2, 10 semillas × 5 folds, conjunto de desarrollo
M2 = M1 + contexto de paciente (contexto_paciente.py) (77 variables) · M4b = M2 + 2 variables de imagen apiladas: puntuación de una logística balanceada sobre las 384 de DINOv2, fuera de pliegue, y su razón a la media del paciente (apilado_imagen.py) (79 variables) · hiperparámetros de 2b
M2 frente a M2 de la referencia (outputs/fase4-m2-vs-m1.json), fold a fold: True
Imagen: 318229 filas alineadas por isic_id, sin faltantes · hash igual al de la extracción: True
pAUC: M2 0.144, M4b 0.1496 · AUC: M2 0.9343, M4b 0.9398 · SEtop-15: M2 0.7065, M4b 0.7003 · NNT80% SE: M2 85.6158, M4b 81.7435
M4b − M2, pAUC (principal): media 0.0056 · ingenuo [0.0016, 0.0096] · corregido [-0.0091, 0.0202] · M4b mejor en 36/50 folds y 8/10 semillas
M4b − M2, AUC (secundaria): media 0.0055 · ingenuo [0.0014, 0.0097] · corregido [-0.0096, 0.0207] · M4b mejor en 35/50 folds y 9/10 semillas
M4b − M2, SEtop-15 (secundaria): media -0.0062 · ingenuo [-0.0166, 0.0042] · corregido [-0.0444, 0.032] · M4b mejor en 22/50 folds y 3/10 semillas
M4b − M2, NNT80% SE (secundaria): media -3.8724 · ingenuo [-9.6488, 1.9041] · corregido [-25.0965, 17.3517] · M4b mejor en 31/50 folds y 8/10 semillas
Apilado de imagen: 0 avisos de no convergencia · 21.305 s por fold de mediana (6 logísticas)
Entrenamiento por fold (fit), mediana: M2 1.35 s · M4b 1.44 s
En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.
Detalle por semilla y fold: outputs/fase4-m4b-vs-m2.json

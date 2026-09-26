# Fase 4 — M2 − M1, 10 semillas × 5 folds, conjunto de desarrollo
M1 = nivel 2b (39 variables) · M2 = M1 + contexto de paciente (77 variables) · hiperparámetros de 2b
M1 reproduce fold a fold el nivel 2b de outputs/validacion-repetida.json: True
pAUC: M1 0.1375 · M2 0.144
AUC: M1 0.9209 · M2 0.9343
SEtop-15: M1 0.6223 · M2 0.7065
NNT80% SE: M1 116.1648 · M2 85.6158
M2 − M1, pAUC (principal): media 0.0065 · ingenuo [0.0007, 0.0122] · corregido [-0.0147, 0.0276] · M2 mejor en 28/50 folds y 7/10 semillas
M2 − M1, AUC (secundaria): media 0.0134 · ingenuo [0.0077, 0.0191] · corregido [-0.0076, 0.0343] · M2 mejor en 36/50 folds y 9/10 semillas
M2 − M1, SEtop-15 (secundaria): media 0.0842 · ingenuo [0.067, 0.1014] · corregido [0.021, 0.1473] · M2 mejor en 46/50 folds y 10/10 semillas
M2 − M1, NNT80% SE (secundaria): media -30.549 · ingenuo [-38.8077, -22.2903] · corregido [-60.8933, -0.2047] · M2 mejor en 42/50 folds y 10/10 semillas
En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.
Detalle por semilla y fold: outputs/fase4-m2-vs-m1.json

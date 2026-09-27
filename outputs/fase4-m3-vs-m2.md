# Fase 4 — M3 − M2, 10 semillas × 5 folds, conjunto de desarrollo
M2 = M1 + contexto de paciente (contexto_paciente.py) (77 variables) · M3 = parte tabular reproducida del ganador: CatBoost publicado sobre sus variables, con los parches de la especificación (ganador_m3.py) (217 variables) · M3 con los hiperparámetros publicados; el otro, con los de 2b
M2 frente a M2 de la referencia (outputs/fase4-m2-vs-m1.json), fold a fold: True
pAUC: M2 0.144, M3 0.1625 · AUC: M2 0.9343, M3 0.9547 · SEtop-15: M2 0.7065, M3 0.7245 · NNT80% SE: M2 85.6158, M3 72.9964
M3 − M2, pAUC (principal): media 0.0185 · ingenuo [0.0137, 0.0234] · corregido [0.0007, 0.0364] · M3 mejor en 45/50 folds y 10/10 semillas
M3 − M2, AUC (secundaria): media 0.0204 · ingenuo [0.0151, 0.0256] · corregido [0.0011, 0.0397] · M3 mejor en 47/50 folds y 9/10 semillas
M3 − M2, SEtop-15 (secundaria): media 0.0181 · ingenuo [0.0032, 0.0329] · corregido [-0.0365, 0.0726] · M3 mejor en 30/50 folds y 8/10 semillas
M3 − M2, NNT80% SE (secundaria): media -12.6194 · ingenuo [-22.5997, -2.6392] · corregido [-49.2892, 24.0504] · M3 mejor en 38/50 folds y 9/10 semillas
M3: 217 variables, calculadas en 18.7 s · árboles por ajuste: mediana 376.0, mínimo 14, máximo 1352
Entrenamiento por fold (fit), mediana: M2 1.31 s · M3 18.12 s
En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.
Detalle por semilla y fold: outputs/fase4-m3-vs-m2.json

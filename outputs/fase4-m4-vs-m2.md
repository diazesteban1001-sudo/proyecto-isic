# Fase 4 — M4 − M2, 10 semillas × 5 folds, conjunto de desarrollo
M2 = M1 + contexto de paciente (contexto_paciente.py) (77 variables) · M4 = M2 + las 384 variables de DINOv2 ViT-S/14 (token CLS), tal cual (461 variables) · hiperparámetros de 2b
M2 frente a M2 de la referencia (outputs/fase4-m2-vs-m1.json), fold a fold: True
Imagen: 318229 filas alineadas por isic_id, sin faltantes · hash igual al de la extracción: True
pAUC: M2 0.144, M4 0.1375 · AUC: M2 0.9343, M4 0.9258 · SEtop-15: M2 0.7065, M4 0.6732 · NNT80% SE: M2 85.6158, M4 96.853
M4 − M2, pAUC (principal): media -0.0065 · ingenuo [-0.0119, -0.0011] · corregido [-0.0263, 0.0133] · M4 mejor en 19/50 folds y 2/10 semillas
M4 − M2, AUC (secundaria): media -0.0085 · ingenuo [-0.014, -0.003] · corregido [-0.0288, 0.0117] · M4 mejor en 16/50 folds y 1/10 semillas
M4 − M2, SEtop-15 (secundaria): media -0.0332 · ingenuo [-0.0473, -0.0191] · corregido [-0.085, 0.0185] · M4 mejor en 9/50 folds y 0/10 semillas
M4 − M2, NNT80% SE (secundaria): media 11.2372 · ingenuo [2.764, 19.7103] · corregido [-19.8953, 42.3696] · M4 mejor en 17/50 folds y 1/10 semillas
Entrenamiento por fold (fit), mediana: M2 1.19 s · M4 6.51 s
En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.
Detalle por semilla y fold: outputs/fase4-m4-vs-m2.json

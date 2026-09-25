# Validación repetida — 10 semillas, conjunto de desarrollo
Métrica: pAUC sobre 80% TPR [0, 0.2], funciones de train_and_evaluate.py (no reimplementada)
Semillas corridas: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
Folds por semilla: 5
Nivel 1 (logística balanceada): media global 0.1325 · std entre folds 0.0138 · std entre semillas 0.0018
Nivel 2a (GB sin balancear): media global 0.0018 · std entre folds 0.0037 · std entre semillas 0.0014
Nivel 2b (GB balanceado): media global 0.1375 · std entre folds 0.0165 · std entre semillas 0.0062
Comparación pareada 2b − 1 (n=50): media 0.005 · desviación 0.0187 · intervalo t 95% ingenuo [-0.0003, 0.0103] · 2b gana en 29/50 folds
Corrección Nadeau-Bengio (2003), varianza ajustada por solape entre folds: intervalo t 95% corregido [-0.0145, 0.0245] · 2b gana en 8/10 semillas
Nota: el intervalo ingenuo subestima la varianza real — folds con entrenamientos solapados. Ver .json.
Detalle por semilla y fold: outputs/validacion-repetida.json

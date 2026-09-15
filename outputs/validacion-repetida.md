# Validación repetida — 10 semillas
Métrica: pAUC sobre 80% TPR [0, 0.2], funciones de train_and_evaluate.py (no reimplementada)
Semillas corridas: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
Folds por semilla: 5
Nivel 1 (logística balanceada): media global 0.131 · std entre folds 0.012 · std entre semillas 0.0011
Nivel 2a (GB sin balancear): media global 0.0022 · std entre folds 0.0056 · std entre semillas 0.0025
Nivel 2b (GB balanceado): media global 0.1435 · std entre folds 0.0142 · std entre semillas 0.0046
Comparación pareada 2b − 1 (n=50): media 0.0125 · desviación 0.0136 · intervalo t 95% [0.0087, 0.0164] · 2b gana en 40/50
Nota: el intervalo t subestima la varianza real — folds con entrenamientos solapados. Ver .json.
Detalle por semilla y fold: outputs/validacion-repetida.json

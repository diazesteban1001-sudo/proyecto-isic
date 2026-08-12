# Modelado baseline — data/train-metadata.csv
Métrica: pAUC sobre 80% TPR [0, 0.2] · verificada contra el script oficial (2026-08-11)
Esquema CV: 5 folds agrupados por patient_id, seed 42
Columnas excluidas: 13 · features usadas: 41
Escala del pAUC: azar 0.02 · clasificador perfecto 0.2
Nivel 0 (univariado tbp_lv_H): AUC estándar 0.8053 — NO comparable con lo de abajo, escalas distintas
Nivel 0 (mismo, en pAUC): pAUC media 0.0809 ± 0.0247 (33.8% del recorrido azar→perfecto)
Nivel 1 (logística balanceada): pAUC media 0.1331 ± 0.0173 (62.8% del recorrido azar→perfecto)
Nivel 2a (GB sin balancear): pAUC media 0.0013 ± 0.0015 (-10.4% del recorrido azar→perfecto)
Nivel 2b (GB balanceado): pAUC media 0.1451 ± 0.0055 (69.5% del recorrido azar→perfecto)
2a por debajo del azar no es un bug: satura en 1.0 sobre negativos. Ver nota en el .json.
Detalle por fold: outputs/modelado-baseline.json

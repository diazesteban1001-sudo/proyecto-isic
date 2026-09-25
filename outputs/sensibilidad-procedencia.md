# Modelado baseline — data/train-metadata.csv, conjunto de desarrollo
SENSIBILIDAD: con las columnas de procedencia ['attribution', 'copyright_license'] dentro del modelo. No sustituye a outputs/modelado-baseline.json ni se usa para elegir nada.
Métrica: pAUC sobre 80% TPR [0, 0.2] · verificada contra el script oficial (2026-08-11)
Esquema CV: 5 folds agrupados por patient_id, seed 42
Columnas excluidas: 13 · features usadas: 41
Escala del pAUC: azar 0.02 · clasificador perfecto 0.2
Nivel 0 (univariado, elegido en entrenamiento: tbp_lv_H en 5 de 5): AUC estándar 0.8048 — NO comparable con lo de abajo, escalas distintas
Nivel 0 (mismo, en pAUC): pAUC media 0.0796 ± 0.0076 (33.1% del recorrido azar→perfecto)
Nivel 1 (logística balanceada): pAUC media 0.1336 ± 0.0099 (63.1% del recorrido azar→perfecto)
Nivel 2a (GB sin balancear): pAUC media 0.0006 ± 0.0003 (-10.8% del recorrido azar→perfecto)
Nivel 2b (GB balanceado): pAUC media 0.1467 ± 0.0155 (70.4% del recorrido azar→perfecto)
2a por debajo del azar no es un bug: satura en 1.0 sobre negativos. Ver nota en el .json.
Detalle por fold: outputs/sensibilidad-procedencia.json

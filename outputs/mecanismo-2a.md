# Mecanismo del 2a — data/train-metadata.csv, conjunto de desarrollo
Partición: 5 folds agrupados por patient_id, seed 42; validación de cada pliegue
Control: pAUC por pliegue igual a outputs/modelado-baseline.json en 2a y 2b
Total = validación de los 5 pliegues juntos (318229 lesiones, 317 positivas)
2a, total: 6665 valores distintos · máx 1.000000 · ≥0.999: neg 0.0009, pos 0.0442 · en el máx: neg 0.0002, pos 0.0221 · rango percentil medio pos 0.5646 · neg sobre la mediana pos 0.2176
2b, total: 189755 valores distintos · máx 0.966006 · ≥0.999: neg 0.0000, pos 0.0000 · en el máx: neg 0.0000, pos 0.0000 · rango percentil medio pos 0.9199 · neg sobre la mediana pos 0.0156
pAUC media de pliegues: 2a 0.0005 · 2b 0.1398
2a por pliegue, valores distintos: 1455, 2047, 1004, 1053, 1116
2a por pliegue, neg ≥0.999: 0.0007, 0.0010, 0.0010, 0.0009, 0.0012
2a por pliegue, rango percentil medio pos: 0.6038, 0.6668, 0.5595, 0.6013, 0.4782
2b por pliegue, rango percentil medio pos: 0.9006, 0.9070, 0.9601, 0.9333, 0.9204
Definiciones y detalle por pliegue: outputs/mecanismo-2a.json

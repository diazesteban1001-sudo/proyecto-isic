# Efecto de la partición — data/train-metadata.csv, conjunto de desarrollo
Niveles 1 y 2b, 5 pliegues, semillas 0–9; por paciente (StratifiedGroupKFold) y por filas (StratifiedKFold)
Control: la partición por paciente reproduce outputs/validacion-repetida.json pliegue a pliegue en 1 y 2b
Medias globales (pauc · auc · setop15 · nnt80):
  Nivel 1, por paciente: pauc 0.1325 · auc 0.8982 · setop15 0.4589 · nnt80 210.9825
  Nivel 1, por filas: pauc 0.133 · auc 0.9009 · setop15 0.7861 · nnt80 198.0256
  Nivel 2b, por paciente: pauc 0.1375 · auc 0.9209 · setop15 0.6223 · nnt80 116.1648
  Nivel 2b, por filas: pauc 0.1377 · auc 0.9224 · setop15 0.8573 · nnt80 108.8571
Filas − paciente, nivel 1: pauc +0.0005 (filas mejor en 6/10) · auc +0.0027 (filas mejor en 9/10) · setop15 +0.3272 (filas mejor en 10/10) · nnt80 -12.9569 (filas mejor en 9/10)
Filas − paciente, nivel 2b: pauc +0.0002 (filas mejor en 5/10) · auc +0.0015 (filas mejor en 5/10) · setop15 +0.235 (filas mejor en 10/10) · nnt80 -7.3077 (filas mejor en 7/10)
2b − 1 por paciente, media e intervalo corregido: pauc +0.005 [-0.0145, 0.0245] · auc +0.0228 [0.0012, 0.0444] · setop15 +0.1633 [0.0874, 0.2393] · nnt80 -94.8177 [-152.3068, -37.3286]
2b − 1 por filas, media e intervalo corregido: pauc +0.0047 [-0.0134, 0.0227] · auc +0.0215 [0.0026, 0.0403] · setop15 +0.0712 [0.0247, 0.1176] · nnt80 -89.1685 [-128.2124, -50.1246]
En el NNT80% SE menos es mejor. La sensibilidad top-15 no mide lo mismo en las dos particiones.
Detalle por semilla y pliegue: outputs/efecto-particion.json

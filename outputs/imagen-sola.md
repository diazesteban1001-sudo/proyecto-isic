# Imagen sola — data/train-metadata.csv, conjunto de desarrollo
Pliegues de M1 en la validación repetida: 5 agrupados por patient_id, semillas 0–9
Control: M1 reproduce outputs/fase4-m2-vs-m1.json pliegue a pliegue en las cuatro métricas, con los mismos pliegues
Imagen: logística balanceada sobre las 384 variables de DINOv2, estandarizadas en el pliegue
Imagen + básicos: lo mismo, más age_approx, sex, anatom_site_general, codificadas como en M1
Medias globales (pauc · auc · setop15 · nnt80):
  M1: pauc 0.1375 · auc 0.9209 · setop15 0.6223 · nnt80 116.1648
  Imagen: pauc 0.0796 · auc 0.8213 · setop15 0.3859 · nnt80 426.138
  Imagen + básicos: pauc 0.084 · auc 0.8295 · setop15 0.3885 · nnt80 390.5636
Imagen − M1, media e intervalo corregido: pauc -0.0579 [-0.084, -0.0319] · auc -0.0997 [-0.1383, -0.061] · setop15 -0.2364 [-0.323, -0.1498] · nnt80 +309.9732 [177.8869, 442.0595]
(Imagen + básicos) − Imagen, media e intervalo corregido: pauc +0.0045 [0.0, 0.0089] · auc +0.0082 [0.0016, 0.0149] · setop15 +0.0026 [-0.034, 0.0393] · nnt80 -35.5744 [-86.9038, 15.7549]
Avisos de no convergencia de la logística: Imagen 0 · Imagen + básicos 0
En el NNT80% SE menos es mejor. No se mide tiempo: el costo de la imagen está en tiempo-inferencia.json (M4).
Detalle por semilla y pliegue: outputs/imagen-sola.json

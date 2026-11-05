# Fase 5 — análisis posterior a la apertura (descriptivo)
DINOv2: los dos archivos, de una sola extracción, con los mismos atributos y los SHA-256 registrados; recalculado en 256 recortes de cada uno, diferencia máxima 0.0e+00 y 0.0e+00 (tolerancia 0.001). «Imagen + básicos»: el de imagen-sola.json, con todo el desarrollo.
Red de la 4e − «Imagen + básicos» en el reservado, mismas remuestras: pAUC -0.0078 [-0.0306; 0.02] · AUC 0.0011 [-0.0312; 0.036] · SEtop-15 0.1282 [-0.0035; 0.2585] · NNT80% SE -40.8361 [-194.3999; 110.3913]
| pAUC | desarrollo (semillas) | reservado [95 %] |
|---|---|---|
| M3 limpio | 0.1621 (0 a 9) | 0.1588 [0.1387; 0.1766] |
| M2 | 0.144 (0 a 9) | 0.1387 [0.1074; 0.1668] |
| Red de la 4e | 0.1376 (5 a 9) | 0.1307 [0.0986; 0.1614] |
| Imagen + básicos | 0.084 (0 a 9); 0.0884 (5 a 9) | 0.1385 [0.1117; 0.159] |
| M3 limpio − M2 | 0.0181 [0.0021; 0.0341] (0 a 9, NB) | 0.0201 [0.0008; 0.0413] |
| Red − Imagen + básicos | 0.0493 [0.0218; 0.0767] (5 a 9, NB) | -0.0078 [-0.0306; 0.02] |
Controles: 21 de 21 bien, 8 de ellos casos que deben fallar. Las cuatro métricas, en el .json. Posterior a la apertura; no interpreta.

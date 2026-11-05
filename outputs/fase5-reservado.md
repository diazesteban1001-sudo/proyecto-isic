# Fase 5 — el conjunto reservado

Entrenamiento: 833 pacientes, 318229 lesiones · evaluación: 209 pacientes, 82830 lesiones, 76 malignas · semilla 0
Bootstrap por paciente: 2000 remuestras, semilla 2026, percentiles 2,5 y 97,5

- M3 limpio (principal): pAUC 0.1588 [0.1387; 0.1766] · AUC 0.949 [0.9205; 0.9707] · SEtop-15 0.7628 [0.6438; 0.8599] · NNT80% SE 96.7541 [43.1217; 241.3779]
- M2 (referencia): pAUC 0.1387 [0.1074; 0.1668] · AUC 0.9271 [0.8837; 0.9611] · SEtop-15 0.7212 [0.603; 0.8262] · NNT80% SE 153.9508 [46.7726; 290.1911]
- red de la 4e (descriptivo): pAUC 0.1307 [0.0986; 0.1614] · AUC 0.9103 [0.863; 0.9478] · SEtop-15 0.6314 [0.5033; 0.75] · NNT80% SE 198.8852 [75.0072; 386.1779]
- «Imagen + básicos» (descriptivo): pAUC 0.1385 [0.1117; 0.159] · AUC 0.9093 [0.868; 0.9393] · SEtop-15 0.5032 [0.366; 0.6273] · NNT80% SE 239.7213 [106.3714; 376.0217]
- M3 limpio − M2: pAUC 0.0201 [0.0008; 0.0413] · AUC 0.0219 [0.0009; 0.0459] · SEtop-15 0.0417 [-0.0296; 0.117] · NNT80% SE -57.1967 [-127.1367; 41.4539]

Controles: 12 de 12 bien, 6 de ellos casos que deben fallar · tiempo total 3258.6 s
No interpreta.

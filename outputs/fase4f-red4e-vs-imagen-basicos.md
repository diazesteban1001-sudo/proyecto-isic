# Fase 4f: la red de la 4e − «Imagen + básicos»

Conjunto de desarrollo, semillas 5 a 9 × 5 pliegues. «Imagen + básicos» reproduce outputs/imagen-sola.json y la red outputs/fase4e-red-vs-red4c.json, pliegue a pliegue.

- pAUC: red de la 4e 0.1376, Imagen + básicos 0.0884; diferencia 0.0493, NB 95 % [0.0218, 0.0767], valor p 0.001105; mejor en 25 de 25 pliegues y 5 de 5 semillas
- AUC: red de la 4e 0.9179, Imagen + básicos 0.8349; diferencia 0.0829, NB 95 % [0.0465, 0.1193], valor p 8.851e-05; mejor en 25 de 25 pliegues y 5 de 5 semillas
- SEtop-15: red de la 4e 0.5859, Imagen + básicos 0.3921; diferencia 0.1938, NB 95 % [0.1062, 0.2813], valor p 0.000125; mejor en 25 de 25 pliegues y 5 de 5 semillas
- NNT80% SE: red de la 4e 154.3424, Imagen + básicos 366.995; diferencia -212.6526, NB 95 % [-337.8064, -87.4988], valor p 0.001811; mejor en 25 de 25 pliegues y 5 de 5 semillas

En especificidad media (pAUC/0,2): diferencia 0.2464, NB 95 % [0.1092, 0.3836].

Regla de PLAN.md, Fase 4f: valor p 0.001105 frente a 0.05; diferencia media positiva; a favor: sí.

Total: 164.1 s. Aplica la regla tal como la fija PLAN.md; no interpreta.

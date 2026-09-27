# Fase 4 — M3limpio − M2, 10 semillas × 5 folds, conjunto de desarrollo
M2 = M1 + contexto de paciente (contexto_paciente.py) (77 variables) · M3limpio = M3 limpio: las variables de M3 sin descartar las de la celda 24, con las transformaciones sin etiqueta ajustadas en cada pliegue de entrenamiento, y CatBoost con la parada de M3 y el resto por defecto (ganador_m3.py) ([237, 238, 239] variables) · M3 limpio con los parámetros por defecto y la parada de M3; el otro, con los de 2b
M2 frente a M2 de la referencia (outputs/fase4-m2-vs-m1.json), fold a fold: True
pAUC: M2 0.144, M3limpio 0.1621 · AUC: M2 0.9343, M3limpio 0.9552 · SEtop-15: M2 0.7065, M3limpio 0.7292 · NNT80% SE: M2 85.6158, M3limpio 65.554
M3limpio − M2, pAUC (principal): media 0.0181 · ingenuo [0.0137, 0.0224] · corregido [0.0021, 0.0341] · M3limpio mejor en 43/50 folds y 10/10 semillas
M3limpio − M2, AUC (secundaria): media 0.021 · ingenuo [0.0164, 0.0255] · corregido [0.0043, 0.0376] · M3limpio mejor en 46/50 folds y 10/10 semillas
M3limpio − M2, SEtop-15 (secundaria): media 0.0227 · ingenuo [0.0086, 0.0368] · corregido [-0.0291, 0.0746] · M3limpio mejor en 35/50 folds y 9/10 semillas
M3limpio − M2, NNT80% SE (secundaria): media -20.0618 · ingenuo [-28.1385, -11.9852] · corregido [-49.7373, 9.6137] · M3limpio mejor en 36/50 folds y 9/10 semillas
M3 limpio: {'239': 40, '238': 9, '237': 1} (variables: pliegues) · árboles por ajuste: mediana 123.0, mínimo 15, máximo 673 · sin parar antes del tope de 1000: 0/50 · tasa de aprendizaje automática: 0.0877 a 0.0877 · variables por pliegue: mediana 19.994999999999997 s
Entrenamiento por fold (fit), mediana: M2 1.42 s · M3limpio 4.69 s
En el NNT80% SE menos es mejor. El intervalo ingenuo supone diferencias independientes; no lo son.
Detalle por semilla y fold: outputs/fase4-m3limpio-vs-m2.json

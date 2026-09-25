# Sensibilidad de procedencia, validación repetida — 10 semillas, conjunto de desarrollo
SENSIBILIDAD: ['attribution', 'copyright_license'] dentro del modelo. No sustituye a outputs/validacion-repetida.json ni se usa para elegir nada.
Folds: los mismos en las dos configuraciones; sin procedencia reproduce la referencia fold a fold: True · 2b − 1 sin procedencia igual al de la referencia: True
pAUC media global, sin / con procedencia: nivel_1 0.1325 / 0.135 · nivel_2a 0.0018 / 0.0016 · nivel_2b 0.1375 / 0.1396
(a) 2b − 1, con procedencia: media 0.0046 · ingenuo [-0.0005, 0.0098] · corregido [-0.0143, 0.0236] · gana el primer término en 30/50 folds y 8/10 semillas
(a) 2b − 1, sin procedencia: media 0.005 · ingenuo [-0.0003, 0.0103] · corregido [-0.0145, 0.0245] · gana el primer término en 29/50 folds y 8/10 semillas
(b) 2b con − 2b sin procedencia: media 0.0021 · ingenuo [-0.0007, 0.0049] · corregido [-0.0082, 0.0124] · gana el primer término en 27/50 folds y 8/10 semillas
(c) 1 con − 1 sin procedencia: media 0.0025 · ingenuo [0.0012, 0.0038] · corregido [-0.0023, 0.0073] · gana el primer término en 34/50 folds y 10/10 semillas
Nota: el intervalo ingenuo supone diferencias independientes; los folds se solapan. Ver .json.
Detalle por semilla y fold: outputs/sensibilidad-procedencia-repetida.json

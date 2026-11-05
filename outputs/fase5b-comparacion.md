# Fase 5b — la comparación descriptiva de la puerta
Puntuaciones privadas de Kaggle; sin intervalo, descriptiva:
- C7 frente al ganador en el tablero privado: 0.15856 frente a 0.1726, diferencia -0.01404.
- M3 limpio frente a la variante «sin imágenes» de la Tabla 3: 0.15134 frente a 0.164, diferencia -0.01266.
- la red de la 4e frente a la variante «solo imágenes» de la Tabla 3: 0.1159 frente a 0.142, diferencia -0.0261.
- la red de la 4e frente a «Imagen + básicos», las dos puntuaciones de Kaggle; el cuarto envío se decidió después de ver el reservado: 0.1159 frente a 0.08935, diferencia 0.02655.
- Aritmética de dos fuentes: C7 − M3 limpio en Kaggle 0.00722; «modelo completo» − «sin imágenes» en la Tabla 3 0.009.
pAUC en desarrollo, reservado y Kaggle (privada; pública entre paréntesis):
- M3limpio: desarrollo 0.1621 (semillas 0 a 9); 0.1641 (semillas 5 a 9); reservado 0.1588; Kaggle 0.15134 (0.17229).
- Red4e: desarrollo 0.1376 (semillas 5 a 9); reservado 0.1307; Kaggle 0.1159 (0.11108).
- C7: desarrollo 0.1669 (semillas 5 a 9); reservado no se evaluó; Kaggle 0.15856 (0.17893).
- ImagenBasicos: desarrollo 0.084 (semillas 0 a 9); 0.0884 (semillas 5 a 9); reservado 0.1385; Kaggle 0.08935 (0.10126).
Controles: 5 de 5 bien, 4 de ellos casos que deben fallar. Conjuntos y estimaciones distintos; Kaggle no da intervalo.

# Fase 5c — entrenamiento con todos los datos
Datos: 1042 pacientes, 401059 lesiones, 393 malignas. Control: 6 pacientes, 1042 lesiones, puntuados como filas nuevas.
Cuatro envíos de 45 CatBoost cada uno (semillas 1 a 9 × 5 pliegues): M3limpioProm 239 variables, mediana de 145 árboles; M3limpioPromHosp 246 variables, mediana de 148 árboles; C7Prom 241 variables, mediana de 129 árboles; C7PromHosp 249 variables, mediana de 137 árboles.
Sin hospital, las variables y los CatBoost de la 5b reproducen su control sin diferencia. Hospital: 7 columnas de one-hot; celda 17 con 1302 grupos.
Tiempo: 932.0 s. No envía nada y no calcula ninguna métrica.

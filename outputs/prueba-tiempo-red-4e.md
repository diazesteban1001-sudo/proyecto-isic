# Prueba de tiempo: la red de la Fase 4e, MPS

Sin métricas: los logits de validación se descartan y sus etiquetas no se leen.
Equipo: Apple M4 · torch 2.14.0 · torchvision 0.29.0
Entrenamiento (semilla 0, pliegue 0): 254 positivos + un conjunto de negativos de 12716 a 12717 por época, lote 64, 6 procesos de datos
Segundos por época, 2 medidas: 90.643, 77.435 · esperando datos 11.168, 0.144
Predicción sobre 63,646 imágenes: 2.398 s por 1.000
Por red, 20 épocas y su predicción: 1714.6 s · ajuste fino 307.5 s
Proyección de la fase: 18.19 h con 5 semillas de confirmación · 12.53 h con 3 (límite 45 h)
Regla de las semillas: [5, 6, 7, 8, 9]; arranca: sí

Detalle y supuestos: outputs/prueba-tiempo-red-4e.json

# Prueba de tiempo: EfficientNet-B0 entrenada sobre los recortes, MPS
Sin métricas: las puntuaciones de validación se descartan y sus etiquetas no se leen.
Equipo: Apple M4, 16.0 GB · torch 2.14.0 · torchvision 0.29.0
Recortes de desarrollo (318,229, cuadrados): lado mediano 131.0 px, p5 107.0, p95 163.0 · entrada 128x128
Entrenamiento (semilla 0, pliegue 0): 254 positivos + 20 negativos por positivo = 5,334 imágenes, lote 64
Segundos por época: 63.246, 62.37, 61.917 · decodificación 1.123 s
Predicción sobre 63,646 imágenes: 2.198 s por 1.000 solo modelo · 2.486 s con lectura y decodificación
Memoria MPS, pico: 4.09 GB entrenando · 4.42 GB prediciendo · proceso 1.8 GB
Extrapolación, 3 épocas y 20 negativos por positivo:
  (a) 1 semilla × 5 pliegues: 0.45 h solo modelo · 0.48 h con lectura y decodificación (5 entrenamientos)
  (b) (a) con la validación interna de 5 pliegues: 2.27 h solo modelo · 2.41 h con lectura y decodificación (30 entrenamientos)
  (c) 10 semillas × 5 pliegues: 4.54 h solo modelo · 4.81 h con lectura y decodificación (50 entrenamientos)
Detalle y supuestos: outputs/prueba-tiempo-red-imagen.json

# Tiempo de inferencia — Fase 4, conjunto de desarrollo
Subconjunto: 16 pacientes completos, 5008 lesiones (semilla 7) · entrenamiento: 817 pacientes, semilla 0, sin cronometrar
Control: M1, M2 y M3 limpio idénticos al camino normal · M4 y M4b: DINOv2 a 0.0e+00 del archivo (tolerancia 0.001), idénticos con las variables del archivo; con las recalculadas, diferencia máxima 0.0e+00 (M4) y 0.0e+00 (M4b) · 28 de 28 pasos quitados detectados
Imputación quitada: la matriz que entra al modelo cambia en M1, M2, M4, M4b; en M3 limpio el camino no llega a formarla (el LOF no acepta NaN) · puntuaciones sin cambio en M4: ese paso lo cubren las matrices
M1: mediana 0.0021 s por 1.000 lesiones · las cinco: [0.0022, 0.0021, 0.002, 0.002, 0.0021]
M2: mediana 0.0209 s por 1.000 lesiones · las cinco: [0.0209, 0.0209, 0.0205, 0.0214, 0.0206]
M3 limpio: mediana 0.0435 s por 1.000 lesiones · las cinco: [0.0411, 0.0465, 0.0406, 0.0449, 0.0435]
M4: mediana 14.5156 s por 1.000 lesiones · las cinco: [14.3937, 14.425, 14.5187, 14.5156, 14.6365]
M4b: mediana 14.6321 s por 1.000 lesiones · las cinco: [14.5273, 14.5842, 14.6357, 14.6321, 14.7628]
Equipo: Apple M4, 10 núcleos, 16 GB · macOS 27.0 · Python 3.11.9 · DINOv2 en mps, lote 64 · hilos: torch 4, OpenMP [4, 10], CatBoost por defecto
Desde los metadatos (y las imágenes en M4 y M4b) hasta la puntuación; sin cargar modelos ni pesos.
Los tiempos solo comparan estos modelos entre sí.
Detalle, versiones y lista de pacientes: outputs/tiempo-inferencia.json

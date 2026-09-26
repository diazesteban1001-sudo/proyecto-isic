# Prueba de tiempo DINOv2 — 1000 imágenes del conjunto de desarrollo, MPS
Pasada hacia adelante congelada. No guarda características ni calcula métricas.
Equipo: Apple M4, 16.0 GB · torch 2.14.0 · lote 64 · 3 repeticiones
Lectura del HDF5: 0.358 s · decodificación y preprocesado: 0.836 s
dinov2_vits14 (22,056,576 parámetros): 132.5 img/s solo modelo · 114.4 img/s con lectura y preprocesado
  estimado para 401,059 imágenes: 0.84 h solo modelo · 0.97 h con lectura y preprocesado
dinov2_vitb14 (86,580,480 parámetros): 37.2 img/s solo modelo · 35.6 img/s con lectura y preprocesado
  estimado para 401,059 imágenes: 2.99 h solo modelo · 3.13 h con lectura y preprocesado
Detalle: outputs/prueba-tiempo-dinov2.json

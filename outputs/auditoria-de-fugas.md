# Auditoría de fugas — data/train-metadata.csv
Columnas solo en train (excluidas de entrada): 11
Columnas constantes: 1 · identificador: 1
Columnas evaluadas univariadamente: 41 · umbral AUC >= 0.9
Columnas sospechosas por AUC alto: 0
Preguntas abiertas sin resolver por el script: 10
  - tbp_lv_nevi_confidence: 'tbp_lv_nevi_confidence' tiene nombre sugerente pero SÍ está en test. ¿Por qué existiría en ambos conjuntos si fuera derivada del diagnóstico? Investigar el origen antes de usarla.
  - iddx_full: 'iddx_full' tiene nombre sugerente de derivación posterior y no está en test. ¿Es post-evento (excluir sin discusión) o una señal derivada que tampoco estaría disponible en inferencia real (excluir igual, pero por otra razón)?
  - iddx_1: 'iddx_1' tiene nombre sugerente de derivación posterior y no está en test. ¿Es post-evento (excluir sin discusión) o una señal derivada que tampoco estaría disponible en inferencia real (excluir igual, pero por otra razón)?
  ... y 7 más
Detalle completo: outputs/auditoria-de-fugas.json

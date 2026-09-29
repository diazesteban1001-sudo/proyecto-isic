## INVENTARIO DE FALLOS — Esteban Díaz

| | 1 · Anclaje | 2 · Búsqueda | 3 · Razonamiento | 4 · Cifras |
|---|---|---|---|---|
| **Herramienta** | WebFetch | Un buscador web | Claude Code | Claude Code |
| **Qué generó** | Ficha de PanDerm | Un fragmento sobre /background/ | Nota sin ejecutar: la pAUC acota el FPR | Desglose «11 y 9» en un commit |
| **Qué estaba mal** | 2 de 5 citas no literales | Inverificable: 301, y 0 de 73 capturas | Al revés: acota el TPR (línea 42) | Eran 8, 2 mixtas y 10 |
| **Cómo lo detecté** | Leí los métodos | Al ir a versionarla | Ejecuté el guion, con seis semillas | Recalculé tras el push |
| **Qué me costó** | Más de un mes con el dato mal | Una tanda, con el dato ya versionado | Sobrevivió un commit | Una cifra falsa publicada |
| **Qué lo habría evitado** | Citar de una copia del texto | Abrir la página antes | Abrir y ejecutar el archivo | Calcular antes de escribir |
| **Fuente** | `CLAUDE.md`, regla 6, fila 9 | Ídem, fila 8 | Ídem, fila 7 | Commit del 2026-09-29, 14:49, y su CSV |

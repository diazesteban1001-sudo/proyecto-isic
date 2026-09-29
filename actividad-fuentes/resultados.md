# Experimento de la semana 1: resultados

Protocolo: `protocolo-experimento-v1.md`. Referencias clasificadas: 15.

## Por tratamiento

| | Entregadas de 5 | Faltaron | Se abstuvo | No existe (P1 / P2 / final) | Existe pero no dice eso (P1 / P2 / final) | Utilizable (P1 / P2 / final) | Solo resumen (P1 / P2) | DOI erróneo (P1 / P2) |
|---|---|---|---|---|---|---|---|---|
| A | 5 | 0 | sí | 5 / 5 / 5 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 |
| B | 5 | 0 | no | 0 / 0 / 0 | 2 / 1 / 2 | 3 / 4 / 3 | 0 / 1 | 1 / 1 |
| C | 5 | 0 | no | 0 / 0 / 0 | 3 / 3 / 3 | 2 / 2 / 2 | 0 / 0 | 0 / 0 |

Abstenciones explícitas, texto literal:

- A: «Lo siento, pero no puedo encontrar las referencias exactas solicitadas para la sobreestimación del desempeño de los clasificadores de lesiones de piel cuando se dividen los datos por imagen o por lesión en lugar de por paciente.»

Proporción de utilizables en la clasificación final, sobre las que entregó, con intervalo de Wilson al 95 %:

- A: 0 de 5, 0,0000, [0,0000; 0,4345]
- B: 3 de 5, 0,6000, [0,2307; 0,8824]
- C: 2 de 5, 0,4000, [0,1176; 0,7693]

## Consistencia

Filas: pasada 1. Columnas: pasada 2.

| | No existe | Existe pero no dice eso | Utilizable |
|---|---|---|---|
| No existe | 5 | 0 | 0 |
| Existe pero no dice eso | 0 | 4 | 1 |
| Utilizable | 0 | 0 | 5 |

No coinciden: 1 de 15.
- 126 (B): no_dice_eso -> utilizable; final no_dice_eso. Motivo: Tercera lectura de Claude Code, el 2026-09-29, sobre el texto completo en IEEE Xplore (CC BY 4.0). El DOI resuelve a https://ieeexplore.ieee.org/document/11579778, y el título, los autores y las páginas coinciden con Crossref. Las dos cifras están en el resumen: «This setup reaches 78.41%» y «However, under the leakage-prone protocol, this exact same pipeline yields 94.57%.». La afirmación presenta la caída de 94.57% a 78.41% como efecto de la partición y como la medida de la sobreestimación. En «Result and Discussion» la fuente dice otra cosa: «That headline reflected a single fortunate seed where the same uncorrected protocol, averaged over five seeds, yields between 87% and 89%, and removing the leakage brings this down to a range between 76% and 78%.» y «The originally reported figure therefore combined two distinct sources of inflation, which include approximately 5% to 7% of single-seed variance and approximately 11% of data leakage.». Con su alcance, el efecto del esquema de partición, la afirmación no se localiza: la fuente lo cifra en unos 11 puntos, no en la diferencia 94.57 − 78.41. Por eso es «existe pero no dice eso», como en la pasada 1. La pasada 2 la dio por utilizable apoyándose en el resumen, pero el protocolo manda usar el texto completo cuando está disponible. El DOI no es erróneo, y no es solo resumen.

Kappa de Cohen: 0,9000. Dato secundario, sin intervalo ni prueba: con 15 referencias o menos es inestable.

## Entre tratamientos

Sin pruebas de hipótesis, por el protocolo: las referencias de un tratamiento salen de una sola respuesta y no son independientes. Los intervalos valen para esta consulta, no para la herramienta en general.

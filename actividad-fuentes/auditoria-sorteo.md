# Auditoría manual de las pasadas: sorteo fijado

Fecha: 2026-10-06. El sorteo se fijó y se commiteó antes de abrir ninguna fila
para auditarla.

## Qué se audita

- **Población:** los 15 id de `pasada-1.csv`, en el orden del archivo.
- **Sorteo:** 4 id, con `random.seed(20261006)`.
- **Desacuerdos:** entran también los id en que `pasada-1.csv` y `pasada-2.csv`
  no coinciden en la columna `categoria`, aunque no salgan en el sorteo. Se
  comparó el texto exacto; comparar sin espacios ni mayúsculas da los mismos.

## Código

Corrido desde esta carpeta con Python 3.14.7 (`/opt/homebrew/bin/python3`). El
resultado de `random.sample` depende del orden de la lista, así que otro orden
de las filas daría otro sorteo con la misma semilla.

```python
import csv, random

p1 = list(csv.DictReader(open("pasada-1.csv", encoding="utf-8-sig")))
p2 = list(csv.DictReader(open("pasada-2.csv", encoding="utf-8-sig")))

ids = [r["id"] for r in p1]  # en el orden del archivo
random.seed(20261006)
sorteados = random.sample(ids, 4)

cat2 = {r["id"]: r["categoria"] for r in p2}
desacuerdo = [r["id"] for r in p1 if r["categoria"] != cat2[r["id"]]]

print("sorteados:", sorteados)
print("desacuerdo:", desacuerdo)
```

Salida:

```
sorteados: ['485', '603', '405', '742']
desacuerdo: ['126']
```

## Resultado

| id | origen |
|---|---|
| 485 | sorteo |
| 603 | sorteo |
| 405 | sorteo |
| 742 | sorteo |
| 126 | desacuerdo |

Son 5 id. El 126 no salió en el sorteo; entra solo por el desacuerdo.

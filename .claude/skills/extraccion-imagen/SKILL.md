---
name: extraccion-imagen
description: Extrae características congeladas de las imágenes de SLICE-3D con DINOv2 ViT-S/14 —el token CLS, 384 dimensiones— en una sola pasada y sin ajuste fino, y mide la cobertura, es decir, cuántas imágenes se decodificaron y cuántas fallaron en cada conjunto. Úsala en la Fase 3, después de sellar el conjunto reservado y de verificar el preentrenamiento del extractor, y siempre antes de cualquier modelado con imagen. Es un instrumento: no lee etiquetas, no calcula métricas y no interpreta.
---

# Extracción de imagen

Skill instrumento. Convierte cada imagen en un vector de características y
reporta sobre cuántas imágenes lo consiguió. No entrena nada, no lee la
etiqueta y no calcula ninguna métrica de desempeño. Qué valen esas
características lo mide después `modelado-baseline`, en la Fase 4, y lo
interpreta el agente.

## Cuándo usarla

- Después de sellar el conjunto reservado (`outputs/holdout-pacientes.json`).
- Después de la decisión de la Fase 2 sobre el extractor (`PLAN.md`): se usa
  DINOv2, con la condición de que el punto de control documente LVD-142M como
  sus datos de entrenamiento. La condición se comprobó para ViT-S/14
  (`referencias/dinov2-repositorio.md`).
- Antes de cualquier modelado con imagen. Si el extractor o el preprocesado
  cambian, se vuelve a correr entera.

## El modelo y el preprocesado — fijados antes de correr (2026-09-25)

Se fijan por escrito antes de la primera extracción, para que ninguna de estas
elecciones se ajuste a un resultado.

- **Modelo:** `dinov2_vits14`, ViT-S/14 destilado, sin registros, elegido por
  la persona (`PLAN.md`, Fase 3). Código del repositorio oficial en el commit
  `7764ea0f912e53c92e82eb78a2a1631e92725fc8`, importado de una copia local.
  Pesos `dinov2_vits14_pretrain.pth`, SHA-256
  `b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9`. El script
  comprueba ese hash antes de extraer y se detiene si no coincide.
- **Decodificación:** el JPEG de cada recorte, convertido a RGB.
- **Redimensionado:** a 224 × 224, con interpolación bicúbica, que es la de
  DINOv2. No se recorta el centro. La transformación de evaluación por defecto
  de DINOv2 redimensiona a 256 y recorta 224 en el centro; aquí no se usa, por
  decisión de la persona.
- **Normalización:** la de DINOv2 por defecto, media `(0.485, 0.456, 0.406)` y
  desviación `(0.229, 0.224, 0.225)` (`IMAGENET_DEFAULT_MEAN` y
  `IMAGENET_DEFAULT_STD` en `dinov2/data/transforms.py`).
- **Característica:** el token CLS tras la normalización final,
  `x_norm_clstoken`, que es lo que devuelve `forward` en inferencia porque la
  cabeza es `nn.Identity`: 384 dimensiones por imagen.
- **Pasada:** congelada, con `torch.no_grad`, en MPS, en lotes de 64.

## Qué hace

1. Lee de `data/train-metadata.csv` **solo** `isic_id` y `patient_id`, sin la
   etiqueta ni ninguna otra columna. Reparte las imágenes entre desarrollo y
   reservado con la lista sellada de `outputs/holdout-pacientes.json`.
2. Extrae el token CLS de cada imagen de `data/train-image.hdf5`, conjunto por
   conjunto.
3. Escribe las características de cada conjunto en su propio archivo de
   `data/`, que no se versiona:
   - `data/dinov2-vits14-desarrollo.h5`
   - `data/dinov2-vits14-reservado.h5`

   Cada archivo es un HDF5 con tres conjuntos de datos, en el orden de las
   filas del CSV: `cls` (float32, n × 384), `isic_id` y `decodificada`
   (booleano; si una imagen no se decodificó, su fila de `cls` va en NaN). Los
   atributos del archivo dicen qué conjunto es, el modelo, el hash de los pesos
   y el commit del código.
4. Escribe el contrato de salida.

**El conjunto reservado se extrae, pero no se lee.** Sus características hacen
falta para la evaluación única de la Fase 5 y se sacan en la misma pasada, con
el mismo código. Van a un archivo aparte, y `diseno-validacion/scripts/datos_desarrollo.py`
se niega a cargarlo como datos de desarrollo.

## Cómo correrlo

El código y este archivo se commitean **antes** de correr, porque el JSON graba
el commit que lo produjo.

```bash
python .claude/skills/extraccion-imagen/scripts/extraer.py \
  --hdf5 data/train-image.hdf5 \
  --data data/train-metadata.csv \
  --repo data/dinov2-7764ea0f912e53c92e82eb78a2a1631e92725fc8 \
  --salida-dir data \
  --out outputs/extraccion-imagen
```

`scripts/prueba_tiempo.py` es la prueba de tiempo previa a la elección del
modelo (`outputs/prueba-tiempo-dinov2.json`); no extrae nada.

## Contrato de salida

- `outputs/extraccion-imagen.json`: la cobertura por conjunto (imágenes
  decodificadas frente a fallidas), los tiempos por fase y el total, el
  dispositivo, las versiones, el SHA-256 de los pesos y de cada archivo de
  características, y el commit del código.
- `outputs/extraccion-imagen.md`: resumen legible de máximo 15 líneas.

## No interpretes aquí

No interpretes los resultados aquí — eso lo hace el agente. Esta skill no dice
si las características sirven, ni si la cobertura basta, ni con qué modelo usarlas.

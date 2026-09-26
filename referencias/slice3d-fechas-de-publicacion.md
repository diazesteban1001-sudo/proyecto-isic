# SLICE-3D — qué dicen las fuentes sobre cuándo fueron públicos sus datos (FICHA)

**Qué es:** la recopilación de lo que las fuentes del proyecto dicen sobre
cuándo se publicaron los datos de SLICE-3D. La regla de verificación de la Fase 2
(`PLAN.md`) compara la fecha de un extractor de imagen con *"la primera fecha en
que los datos de SLICE-3D fueron públicos"*. Reúne un registro nuevo, el del DOI
en DataCite, y citas de dos fuentes que ya están versionadas con su texto
completo.
**Fecha de consulta:** 2026-09-25.

**Lo primero que hay que saber: ninguna de estas fuentes dice cuál fue esa
primera fecha.** Dan una fecha de registro del DOI, una fecha en la que los datos
ya eran públicos y una fecha antes de la cual el conjunto no estaba terminado.
Lo que cada una dice, y lo que no, va abajo; la sección 5 las encadena, que es
en lo que se apoya la decisión de la Fase 2.

**LICENCIA: desconocida → FICHA.** El registro de DataCite no declara licencia
en el propio registro, y no se ha determinado la de sus metadatos; de él se
anotan campos, que son datos y no texto. Las otras dos fuentes son CC BY 4.0 y
están versionadas enteras en sus propios archivos.

---

## 1. El registro del DOI en DataCite

**URL:** https://api.datacite.org/dois/10.34970/2024-slice-3d — respondió 200
(`application/json`) antes de descargarlo. Copia local:
`referencias/_texto-completo/datacite-10.34970-2024-slice-3d.json` (3.173 bytes,
SHA-256 `43aa7cf7d4ca29f38fff0cff263e1ff5d860366a7893b49bc871bc2bdc4a0b96`).

| Campo | Valor |
|---|---|
| `doi` | `10.34970/2024-slice-3d` |
| `titles` | *SLICE-3D 2024 Challenge Dataset* (`AlternativeTitle`) |
| `publicationYear` | 2024 |
| `created` | 2024-05-23T17:25:21.000Z |
| `registered` | 2024-05-23T17:30:37.000Z |
| `updated` | 2024-06-27T15:40:51.000Z |
| `url` | https://challenge2024.isic-archive.com/ |
| `dates` | vacío |

*Nuestro.* Son las fechas del **registro del DOI**, no de la publicación de los
datos: que el DOI existiera el 2024-05-23 no dice que los datos fueran públicos
ese día. El registro no trae ninguna fecha de publicación de los datos (`dates`
va vacío).

## 2. Kurtansky et al. 2025 — la competición

Texto completo versionado, CC BY 4.0: `referencias/kurtansky-2025-triaje-automatizado-tbp.md`,
sección de métodos.

> An online competition called “ISIC 2024 – Skin Cancer Detection with 3D-TBP”
> (ISIC’24) was held on Kaggle, a data science platform, from June 27th through
> September 6th, 2024.

> The official training dataset was the previously described and publicly
> available SLICE-3D dataset

*Nuestro.* Dice que durante la competición, que empezó el 27 de junio de 2024,
los datos eran públicos. No dice que ese fuera el primer día en que lo fueron.

## 3. Kurtansky et al. 2024 — el descriptor

Texto completo versionado, CC BY 4.0: `referencias/kurtansky-2024-slice3d-descriptor.md`,
sección *"Data collection"*.

> Plans for this dataset were initiated by the ISIC Artificial Intelligence
> working group and were presented at the VECTRA WB360 user group meeting during
> the 2023 EADV Congress.

> Each site identified patients who had been imaged with 3D TBP between 2015 and
> 2024.

La publicación del propio descriptor, en la cabecera de PMC:

> Sci Data. 2024 Aug 14;11:884.

*Nuestro.* Las dos primeras frases dicen que el conjunto se planteó en 2023 y
que incluye pacientes fotografiados hasta 2024. Leídas juntas, el conjunto
completo no pudo estar terminado antes de 2024. **Es una inferencia nuestra, no
algo que el texto afirme.** Tampoco dice si alguna de sus imágenes estuvo
pública antes por otra vía. El 14 de agosto de 2024 es la fecha del artículo,
no la de los datos.

## 4. La colección del ISIC Archive

**URL:** https://api.isic-archive.com/api/v2/collections/390/ — respondió 200.
Es la colección que la página de datos del reto da como el entrenamiento del
ISIC Archive (`referencias/isic-licencia-y-cita-slice3d.md`, *"Version
control"*). Copia local: `referencias/_texto-completo/isic-archive-coleccion-390.json`
(164 bytes, SHA-256
`e13ab20127652dc608723877be76976f699567848d160beb1a9f5721ac7f3aa6`). Campos:
`name` *"Challenge 2024: Training"*, `public` `true`, `doi` `null`. **No trae
ninguna fecha.**

## 5. La cadena de evidencia (2026-09-25)

En esto se apoya el orden temporal de la decisión de la Fase 2 sobre DINOv2
(`PLAN.md`), a falta de una fuente que fije la primera fecha pública. Primero
lo que dice cada fuente, literal; después lo que es nuestro.

**Lo que dicen las fuentes.**

1. Los recortes se generaron con una herramienta propia. Descriptor, *"Lesion-image
   “tile” cropping"* y *"Data collection"*:

   > The ISIC2024 Tile Export Tool was developed by Canfield Scientific for the
   > purpose of extracting standardized, de-identified, single-image photos from
   > individual 3D TBP captures.

   > Tile data was exported in bulk at each site using the ISIC2024 Tile Export
   > Tool.

2. El proyecto se presentó en el congreso de la EADV de 2023, y después las
   instituciones aportaron los datos. Descriptor, *"Data collection"*:

   > Plans for this dataset were initiated by the ISIC Artificial Intelligence
   > working group and were presented at the VECTRA WB360 user group meeting
   > during the 2023 EADV Congress.

   > Users from seven institutions ultimately received ethics approval from their
   > respective institutional review board (IRB) or human research ethics
   > committee (HREC) and contributed data to ISIC for the present dataset

3. Ese congreso fue del 11 al 14 de octubre de 2023, en Berlín.
   `referencias/eadv-congress-2023.md`:

   > 11-14 OCTOBER 2023

4. Las imágenes llegan hasta 2024. Descriptor, *"Data collection"*:

   > Each site identified patients who had been imaged with 3D TBP between 2015
   > and 2024.

5. En la competición, desde el 27 de junio de 2024, los datos ya eran públicos
   (sección 2, Kurtansky et al. 2025).

**Lo que es inferencia nuestra, y no dice ninguna fuente.**

- Que *"the 2023 EADV Congress"* del descriptor sea el de Berlín, del 11 al 14 de
  octubre de 2023. El descriptor no da lugar ni fecha.
- Que la herramienta se creara para el reto de 2024. El descriptor la llama
  *"ISIC2024 Tile Export Tool"* y dice para qué sirve, no para qué reto se hizo:
  el vínculo con el reto sale del nombre.
- Que los datos se aportaran después de la presentación de octubre de 2023. Se
  lee de *"ultimately"*, que marca un orden, no una fecha.
- Que el conjunto completo no pudo estar terminado antes de 2024, porque incluye
  pacientes fotografiados en 2024.
- La conclusión: los recortes de SLICE-3D no eran públicos en abril de 2023, ni
  el conjunto completo antes de 2024. **Nada de esto excluye que alguna de las
  imágenes originales estuviera pública antes por otra vía**; las fuentes no
  hablan de eso.

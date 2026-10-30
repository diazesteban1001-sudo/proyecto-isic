# 2g (2024) — «ISIC2024上位解法MEMO», resumen de las soluciones de cabeza (FICHA)

**Qué es:** un artículo de Zenn, en japonés, que resume las soluciones de los
primeros puestos de ISIC 2024 a partir de sus writeups de Kaggle. Es una
**fuente secundaria**: no es el writeup del primer puesto, que sigue sin estar
en `referencias/` (`CLAUDE.md`, «Por qué no hay leaderboard privado»), ni su
código (`referencias/novoselskiy-2024-isic2024.md`). Lo cita la Fase 4d de
`PLAN.md`, pregunta 1, como origen del ruido en el apilado, que no está en el
código público del ganador.
**URL:** https://zenn.dev/ottantachinque/articles/2024-09-12_isic2024-top-solution
**Autor:** la cuenta `ottantachinque`, con el nombre visible «2g».
**Fechas, de la propia página:** publicado el 2024-09-12 (`publishedAt`) y
modificado por última vez el 2025-02-01 (`bodyUpdatedAt`).
**Fecha de consulta:** 2026-10-30, con `curl`.

**LICENCIA: con copyright → FICHA.** La página no declara licencia. Los
términos de Zenn (https://zenn.dev/terms, artículo 6, «著作権等») reservan el
derecho de autor del contenido a quien lo publica:

> 利用者が本サービスを利用して投稿または編集した文章、画像等のコンテンツ（以下「利用者コンテンツ」といいます。）につき生じる著作権については、当該利用者あるいはその権利者に留保されるものとします。

*Traducción nuestra:* el derecho de autor de los textos e imágenes que un
usuario publica en el servicio queda reservado a ese usuario o a su titular.

**Texto completo:** en local, en `referencias/_texto-completo/`:
- `zenn-2g-2024-isic2024-resumen-soluciones.html`, la página tal como la sirvió
  Zenn, SHA-256
  `2dab7bd486b5a4e199a188a60bee0fd9993f6666d7d715dbee95b047b50ce270`;
- `zenn-terminos.html`, los términos, SHA-256
  `b0ef2f6e9c7bbaddb53417bce95646e2582a85463c2425634a619d5a4fab81c5`.

---

## Citas que el proyecto usa

Comprobadas carácter a carácter contra el HTML el 2026-10-30. Están en la
sección *«1st place solution»*, apartado *«tabuler model»* (así, con esa
errata, en el original), como tres elementos de una lista. En la tercera, el
espacio entre «image» y «model» es un espacio de ancho completo (U+3000), como
en el original.

> ensemble: rank ensembleで実施

> image modelの予測値は標準化して使用

> overfitしないようにimage　modelの予測値に標準偏差が0.1のノイズを追加している

*Traducción nuestra, no del autor:* «ensamble: se hizo por rangos»; «las
predicciones del modelo de imagen se usan estandarizadas»; «para no sobreajustar,
se añade a las predicciones del modelo de imagen un ruido con desviación
estándar de 0,1».

---

## Lo que es nuestro: qué dice y qué no

*Análisis nuestro.* El resumen no dice a qué variables del apilado va el ruido,
si se suma solo en el entrenamiento, con qué semilla, ni cómo se estandarizan
las predicciones. En el código público del ganador no hay ruido sobre las
predicciones de imagen: se buscaron, el 2026-10-30, `noise`, `random.normal`,
`randn`, `rankdata` y `.rank(` en toda la copia local del repositorio
(`referencias/_texto-completo/novoselskiy-2024-isic2024-repo/`). Solo aparecen
el `noise_offset` del entrenamiento de Stable Diffusion (`sd_training.ipynb`) y
un `GaussNoise` de aumento de imagen (`src/augmentations.py`). Tampoco hay
ensamble por rangos. Por eso la Fase 4d fija su propia versión del ruido y la
declara como suya.

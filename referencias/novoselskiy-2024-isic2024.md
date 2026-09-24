# Novoselskiy (2024) — Solución ganadora de ISIC 2024, código público

**Fuente:** repositorio *isic-2024* de Ilya Novoselskiy, primer puesto de la
competencia de Kaggle *ISIC 2024 - Skin Cancer Detection with 3D-TBP*.
https://github.com/ilyanovo/isic-2024
**Commit:** `1952a8f0caf3c69ebfd33cbaa8afe4c6769c1a5d` (rama `main`, 2024-11-18,
asunto *"Update README.md"*). Es el `HEAD` remoto de `main` consultado en
`api.github.com` el 2026-09-24. *Este hash es el dato que identifica la versión
copiada, no un puntero a la historia de este repositorio (regla 6, la
excepción): no se actualiza.*
**Autor:** "Ilya Novoselskiy", según el campo de autor de los commits del
repositorio. Que sea el primer puesto lo dice el propio README (*"This repo
contains first place solution for **isic-2024** competition"*).
**Fecha de consulta:** 2026-09-24, con `git clone`.

**LICENCIA: Apache License 2.0 → COPIA EXACTA.** Determinada por dos vías, el
2026-09-24:
- el archivo `LICENSE` del repositorio es, con los espacios normalizados,
  idéntico al texto canónico de https://www.apache.org/licenses/LICENSE-2.0.txt;
- la API de GitHub detecta `Apache-2.0` (`spdx_id`) en `LICENSE`.

La corrobora, sin ser una tercera vía sobre el repositorio, que es la licencia
que las reglas de la competencia exigían a las soluciones ganadoras: *"WINNER
LICENSE TYPE: Apache 2.0"*. La línea está en la copia local de las reglas,
`referencias/_texto-completo/kaggle-rules.md`; la ficha versionada
`referencias/kaggle-rules.md` no la recoge.

Apache 2.0 permite redistribuir la obra sin modificar con una copia de la
licencia (§4). Por eso los tres archivos se versionan **byte a byte**, sin
cabecera dentro: añadírsela sería modificarlos, y los archivos modificados
tendrían que llevar aviso de cambio (§4(b)). Esta cabecera va aparte. El
repositorio no tiene archivo `NOTICE`, y el `LICENSE` no lleva línea de
copyright propia (conserva la plantilla del apéndice sin rellenar).

**Qué se versiona**, en `referencias/novoselskiy-2024-isic2024/`:

| Archivo | SHA-256 |
|---|---|
| `README.md` | `48b0d52aa5b28eec71055d1fc4c371ced1fe12c9cddefbc1457071b3b7819180` |
| `LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| `notebooks/top-model.ipynb` | `0c39e7526dc7017b334a01d71a02a4a6f7e63d50f221011b8eee3f89e663362f` |

**Qué no se versiona:** el resto del repositorio —los otros cinco notebooks,
`src/*.py`, `requirements.txt` y `.gitignore`—. Está en local, sin la carpeta
`.git`, en `referencias/_texto-completo/novoselskiy-2024-isic2024-repo/`, sacado
con `git archive` del mismo commit, para comprobar contra él lo que se cite.

**Qué no es esta fuente: no es el writeup de Kaggle.** El writeup se leyó en
capturas de pantalla durante la planificación y sigue sin estar en
`referencias/`. Este archivo es el **código**: dice qué hace la solución, no qué
reportó su autor sobre por qué funciona. Una afirmación sobre lo que el autor
"reporta" o "descartó" no se respalda con este archivo salvo que el README o
las salidas de los notebooks lo digan.

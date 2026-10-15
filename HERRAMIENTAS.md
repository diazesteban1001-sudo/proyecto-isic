# Herramientas y versiones

Qué es: con qué se hizo cada cosa del proyecto y qué se puede rehacer. Cada
versión sale de un archivo del repositorio o de un comando ejecutado en el
equipo del proyecto el 2026-10-15, que a veces lee un archivo del equipo
fuera del repositorio; cada entrada dice de cuál. Lo que no se pudo leer dice
**«no registrado»**, con el motivo.

Una versión de hoy no es necesariamente la de cada corrida. Donde una salida
de `outputs/` graba la suya, aquí se compara con la de hoy; donde no la graba,
se dice.

## Resumen

| Herramienta | Versión | De dónde sale |
|---|---|---|
| [Equipo](#equipo) | MacBook Air (Mac16,12), Apple M4, 16 GB, macOS 27.0 | `system_profiler`, `sw_vers`; `outputs/extraccion-imagen.json > equipo` |
| [Python](#python-y-paquetes) | 3.11.9 | `.venv/bin/python --version`; `outputs/tiempo-inferencia.json > declaraciones.interprete` |
| [Paquetes de Python](#python-y-paquetes) | 66, en [`requirements.txt`](requirements.txt) | `.venv/bin/pip freeze` |
| [Intérprete de 2024](#intérprete-de-2024) | pandas 2.3.3, scikit-learn 1.5.2 y cuatro más | `requisitos-interprete-2024.txt` |
| [DINOv2](#dinov2) | `dinov2_vits14`, commit `7764ea0f…`, pesos con SHA-256 `b938bf1b…` | `outputs/extraccion-imagen.json > modelo` |
| [Ollama](#ollama-y-llama318b) | 0.34.4 | `ollama --version`; `respuestas/respuesta-A.md` |
| [llama3.1:8b](#ollama-y-llama318b) | ID `46e0c10c039e` | `ollama list`; `respuestas/respuesta-A.md` |
| [NotebookLM](#notebooklm) | no registrada | — |
| [Consensus](#consensus) | no registrada; modo por defecto | `respuestas/respuesta-B.md` |
| [Zotero](#zotero) | 10.0.4 en la exportación, inferida; 10.0.5 hoy | historial de actualizaciones del equipo; `Info.plist` |
| [Claude Code](#claude-code) | 2.1.265 hoy; la de cada commit, no registrada | `claude --version` |
| [Graphify](#graphify) | `graphifyy` 0.9.63 | `graphify --version`, `uv tool list` |
| [Chart.js](#chartjs) | 4.4.1 | cabecera de `chart.umd.min.js` |
| [Otras](#otras) | Kaggle CLI 2.2.4, Google Chrome 155.0.8059.80, git 2.50.1 | `requirements.txt`, `Info.plist`, `git --version` |

Ninguna versión de paquete grabada en `outputs/` difiere de la de hoy. Sí
difieren, y se explican en su entrada: Zotero, el intérprete de 2024 frente
al `.venv`, y el `python3` del PATH frente al `.venv`.

## Equipo

- **Versión.** MacBook Air, identificador Mac16,12, chip Apple M4 de 10
  núcleos (4 de rendimiento y 6 de eficiencia) y 16 GB de memoria
  (`system_profiler SPHardwareDataType`). macOS 27.0, compilación 26A428
  (`sw_vers`).
- **Grabado en las corridas.** `outputs/extraccion-imagen.json > equipo` y
  `outputs/prueba-tiempo-dinov2.json > equipo`: `"chip": "Apple M4"`,
  `"memoria_gb": 16.0`, `"macos": "27.0"`.
  `outputs/tiempo-inferencia.json > declaraciones` añade `equipo.nucleos`, 10,
  y `sistema.plataforma`, `macOS-27.0-arm64-arm-64bit`. Coinciden con el
  equipo de hoy.
- **Configuración.** *"DINOv2 corre en la GPU del equipo (MPS) y los modelos
  tabulares en CPU"* (hallazgo 9 de `CLAUDE.md`); el dispositivo está en
  `outputs/extraccion-imagen.json > dispositivo`, y los hilos de cada librería,
  en `outputs/tiempo-inferencia.json > declaraciones.hilos`.
- **Qué no se puede rehacer en otro equipo.** Los tiempos: solo comparan los
  modelos entre sí, en este equipo (hallazgo 9 de `CLAUDE.md`). Que las demás
  salidas den lo mismo en otro equipo no está comprobado.
- **No registrado.** El equipo de las salidas que no lo graban: todas salvo
  esas tres.

## Python y paquetes

- **Versión.** Python 3.11.9 (`.venv/bin/python --version`). El `.venv` sale
  de `/Library/Frameworks/Python.framework/Versions/3.11/bin`, según
  `.venv/pyvenv.cfg`. pip 26.2.1 (`.venv/bin/pip --version`).
- **Paquetes.** [`requirements.txt`](requirements.txt), generado el
  2026-10-15 con `.venv/bin/pip freeze` y sin tocar: 66 paquetes. `pip
  freeze` no lista pip ni setuptools; `pip freeze --all` da `pip==26.2.1` y
  `setuptools==84.0.0`.
- **Para qué.** Los scripts de `.claude/skills/` que importan paquetes de
  fuera de la biblioteca estándar: pandas, scikit-learn, torch, catboost y
  los demás.
- **El `python3` del PATH es otro intérprete.** Hoy es Python 3.14.7, de
  Homebrew (`which python3`, `python3 --version`), y fuera de un entorno
  activado no hay `python` (`which python` no lo encuentra). Así que las
  órdenes documentadas con `python`, como la de la extracción de imagen,
  piden el `.venv` activado.
- **Los guiones de biblioteca estándar.** `informe/md_a_pdf.py` y
  `actividad-fuentes/extraer_corpus_c.py` solo importan la biblioteca
  estándar, y el 2026-10-15 corrieron con ese `python3`. Con qué intérprete
  corrieron antes no está registrado.

**Comparación con lo grabado en `outputs/`.** Seis archivos graban versiones,
en 41 campos, y los 41 coinciden con `requirements.txt` y con Python 3.11.9:

| Paquete | Versión hoy | Grabada en |
|---|---|---|
| Python | 3.11.9 | `extraccion-imagen.json > software`; `tiempo-inferencia.json > declaraciones.interprete`; `prueba-tiempo-dinov2.json > software` |
| numpy | 2.4.6 | `extraccion-imagen.json > software`; `tiempo-inferencia.json > declaraciones.versiones_por_modelo`, de M1 a M4b |
| pandas | 3.0.5 | los mismos dos |
| scikit-learn | 1.9.0 | `tiempo-inferencia.json`, de M1 a M4b; `fase4-m3-vs-m2.json > m3.versiones`; `fase4-m3limpio-vs-m2.json > m3limpio.versiones`; `holdout-pacientes.json > metodo.version_scikit_learn` |
| torch | 2.14.0 | `extraccion-imagen.json > software`; `tiempo-inferencia.json`, M4 y M4b; `prueba-tiempo-dinov2.json > software` |
| pillow | 12.3.0 | `extraccion-imagen.json > software`; `tiempo-inferencia.json`, M4 y M4b |
| h5py | 3.16.0 | `extraccion-imagen.json > software`; `tiempo-inferencia.json`, M4 y M4b; `prueba-tiempo-dinov2.json > software` |
| catboost | 1.2.8 | `tiempo-inferencia.json`, M3limpio; `fase4-m3-vs-m2.json`; `fase4-m3limpio-vs-m2.json` |
| imbalanced-learn | 0.14.2 | `tiempo-inferencia.json > declaraciones.solo_en_el_entrenamiento`; `fase4-m3-vs-m2.json`; `fase4-m3limpio-vs-m2.json` |
| scipy | 1.17.1 | `tiempo-inferencia.json > declaraciones.solo_en_el_entrenamiento` |

De `holdout-pacientes.json` solo se usa ese campo.

**No registrado: las versiones de las demás salidas.** No graban ninguna
`eda-diagnostico`, `diseno-validacion`, `auditoria-de-fugas`,
`modelado-baseline`, `validacion-repetida`, `sensibilidad-procedencia`,
`sensibilidad-procedencia-repetida`, `efecto-particion`, `mecanismo-2a`,
`imagen-sola`, `fase4-m2-vs-m1`, `fase4-m4-vs-m2`, `fase4-m4b-vs-m2` ni
`sintesis-verificacion`.

*Inferencia, no registro.* Cada paquete del `.venv` tiene una sola carpeta
`.dist-info`, y la más reciente se creó el 2026-09-26 a las 21:32: la de
catboost y otras diez del mismo minuto (fecha de creación, con `stat`). Desde
entonces no se instaló ni se actualizó ningún paquete. Si una corrida usó el
`.venv`, usó las versiones de `requirements.txt`. Que lo usara no siempre
consta: `outputs/imagen-sola.json > comando` empieza por `python`, no por el
intérprete (hallazgo 10 de `CLAUDE.md`).

**Cómo se rehace el entorno.** No se ha probado en un clon nuevo:

```bash
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

**Qué no se puede rehacer tal cual.** Las invocaciones exactas de
`evaluar_repetido.py`, `fase4_comparar.py`, `tiempo_inferencia.py` y
`prueba_tiempo.py`, que no están registradas (`CLAUDE.md`, Pendientes, «Deuda
de reproducibilidad»).

## Intérprete de 2024

- **Versión.** Las de
  [`requisitos-interprete-2024.txt`](.claude/skills/modelado-baseline/requisitos-interprete-2024.txt),
  *"Versiones con las que se verificó el 2026-09-25"*: pandas 2.3.3, numpy
  2.4.6, scikit-learn 1.5.2, polars 1.9.0, pyarrow 17.0.0 y tqdm 4.70.1.
- **Para qué.** Ejecutar sin modificar el código de 2024 del organizador
  (`SecondaryMetric-TopNSensitivity.py`) y del ganador (`top-model.ipynb`), en
  `test_metricas_triaje.py`, `test_contexto_paciente.py` y
  `test_ganador_m3.py`. Se indica con la variable de entorno
  `PYTHON_GUION_ISIC`.
- **Diferencias con el `.venv`.** pandas 2.3.3 frente a 3.0.5 y scikit-learn
  1.5.2 frente a 1.9.0, a propósito: el archivo da el motivo. tqdm 4.70.1
  frente a 4.70.0, sin motivo registrado. polars y pyarrow no están en el
  `.venv`.
- **No registrado.** La versión de Python de ese intérprete, que el archivo
  no da, y dónde está. El 2026-10-15 `PYTHON_GUION_ISIC` estaba vacía. Se
  buscaron archivos `pyvenv.cfg` en la carpeta personal, hasta cinco niveles y
  sin `~/Library`, y en `/tmp`: aparecieron el `.venv` del proyecto y tres
  entornos de otros proyectos, y ninguno tiene pandas 2.3.3. Hasta rehacerlo,
  la parte de esas tres pruebas que compara con el código de 2024 sale como
  «NO CORRIDA» o «NO CORRIDO», según la prueba. La que compara con el guion
  del organizador necesita además una copia local que no se versiona
  (`README.md`, «Cómo reproducirlo»).

## DINOv2

- **Versión.** `dinov2_vits14` (ViT-S/14), del repositorio
  `facebookresearch/dinov2`, commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`.
  Pesos `dinov2_vits14_pretrain.pth`, SHA-256
  `b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9`
  (`outputs/extraccion-imagen.json > modelo`). Ese commit es un dato de la
  corrida, no una dirección de la historia de este repositorio (regla 6 de
  `CLAUDE.md`).
- **Para qué.** Las 384 características congeladas de imagen de
  `extraccion-imagen`, sin ajuste fino (Fase 3 de `PLAN.md`).
- **Configuración**, de `outputs/extraccion-imagen.json`:
  - `preprocesado`: JPEG a RGB, redimensionado bicúbico a 224 × 224 sin
    recorte central, normalización por defecto de DINOv2;
  - `caracteristica`: el token CLS tras la normalización final, 384
    dimensiones;
  - `lote`: 64; `dispositivo`: `mps`; `fecha`: 2026-09-26T02:53:06Z.
- **Comprobado el 2026-10-15.** `shasum -a 256` sobre
  `~/.cache/torch/hub/checkpoints/dinov2_vits14_pretrain.pth` da el mismo
  SHA-256.
- **Qué se puede rehacer.** La extracción, con el comando del `SKILL.md` de
  `extraccion-imagen`. El script comprueba el hash de los pesos antes de
  extraer y se detiene si no coincide.
- **Qué no está comprobado.**
  - El commit del código: es el nombre de la carpeta local
    `data/dinov2-7764ea0f…`, que no es un clon de git, y nada lo verifica
    (`SKILL.md`, «Límites conocidos»).
  - Que una segunda extracción dé los mismos bytes: no está registrado. Se
    buscaron «determin», «byte a byte», «mismos bytes» y «reproduc» en la
    carpeta de la skill, en `PLAN.md` y en `outputs/extraccion-imagen.*`.

## Ollama y llama3.1:8b

- **Versión.** Ollama 0.34.4. `ollama --version` da `ollama version is
  0.34.4` con el servidor en marcha, levantado el 2026-10-15 solo para leer
  la versión y la lista. Se instaló con Homebrew el 2026-09-27 a las 20:18:51
  (−0500), y es la única versión instalada (`brew info --json=v2 ollama`).
- **Modelo.** `llama3.1:8b`, con ID `46e0c10c039e` (`ollama list`): es el
  comienzo del identificador completo que registra `respuesta-A.md`,
  `sha256:46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
  `ollama show llama3.1:8b`: 8.0B parámetros, cuantización Q4_K_M.
- **Grabado.** La cabecera de `actividad-fuentes/respuestas/respuesta-A.md`:
  Ollama 0.34.4, el identificador completo, 8.0B y Q4_K_M. Coincide.
- **Para qué.** En la actividad «Nada sin fuente»:
  - el tratamiento A del experimento, el 2026-09-27, en lugar de Claude en
    claude.ai (`desviaciones.md`, sección 2);
  - el control del banco de evaluación, el 2026-09-29, entre las 16:19:22 y
    las 16:22:02 (−0500) (`banco-control-crudo.jsonl`).
- **Configuración.** En A, un solo mensaje de usuario, sin instrucción de
  sistema, sin herramientas y sin opciones; el muestreo por defecto, sin
  semilla fija (`respuesta-A.md`). En el banco, cada petición está cruda en
  `banco-control-crudo.jsonl`: el modelo, un mensaje de usuario y
  `"stream": false`.
- **El perfil de `sandbox-exec`: una reconstrucción.**
  [`actividad-fuentes/sin-red.sb`](actividad-fuentes/sin-red.sb) solo permite
  conexiones salientes a localhost y a sockets Unix locales. Lo usó el
  servidor en A y en el control del banco (mensaje del commit «Actividad «Nada
  sin fuente»: banco de evaluación corrido en el control»).
  - Sale de la transcripción local de la sesión del 2026-09-27, donde aparece
    dos veces, idéntico carácter a carácter. El original no se conservó, así
    que no tiene fecha de modificación propia. Su cabecera da los detalles.
  - Comprobado el 2026-10-15: con él, `curl` no llega a ollama.com (código 7);
    sin él, responde 200.
  - La cabecera de `respuesta-A.md` decía solo «salvo a localhost»; una nota
    del 2026-10-15, debajo, lo precisa.
- **Qué se puede rehacer.** El modelo exacto, fijado por su ID y no por la
  etiqueta, y las peticiones, que están en el protocolo y en el `.jsonl`.
- **Qué no.** El texto de las respuestas: sin semilla fija, nada garantiza
  que una corrida nueva dé el mismo, y para A el protocolo no permite repetir
  la consulta. El perfil de `sandbox-exec` no es el original, sino su
  reconstrucción.

## NotebookLM

- **Versión: no registrada.** La cabecera de `respuestas/respuesta-C.md` no
  trae versión ni modelo, aunque el protocolo pide guardar *"el modelo o la
  versión visible"* (`protocolo-experimento-v1.md`).
- **Fechas de uso.**
  - **2026-09-27, 20:47:58 (−0500):** el tratamiento C del experimento
    (`respuesta-C.md`), en un cuaderno nuevo con los 22 archivos, subidos
    hacia las 20:45.
  - **2026-09-29:** el banco de evaluación, con un chat limpio por pregunta
    (`banco-resultados.md`). Las respuestas entraron al repositorio con el
    commit «Actividad «Nada sin fuente»: respuestas de NotebookLM al banco de
    evaluación», ese día a las 17:11. La hora de cada consulta no está
    registrada.
- **Corpus.** Los 22 archivos de [`corpus-c.md`](actividad-fuentes/corpus-c.md),
  con los 16 primeros caracteres de su SHA-256. Comprobado el 2026-10-15:
  `python3 actividad-fuentes/extraer_corpus_c.py --comprobar ~/Downloads/corpus-c`
  responde *«Los SHA-256 coinciden con corpus-c.md, archivo por archivo.»*
- **Protocolos.**
  - [`protocolo-consulta-v1.md`](actividad-fuentes/protocolo-consulta-v1.md),
    del 2026-09-29: el que se usó en el banco (`banco-resultados.md`).
  - [`protocolo-consulta-v2.md`](actividad-fuentes/protocolo-consulta-v2.md),
    del mismo día, que añade tres reglas para la cita textual. Su commit es
    de las 17:23, después del de las respuestas del banco. Ninguna corrida
    registrada dice haberla usado: se buscó `protocolo-consulta-v2` en todo
    el repositorio, y solo lo nombran el README de la actividad y
    `caso-de-fallo.md`, que la describen.
  - En el tratamiento C no consta ningún protocolo de consulta: la cabecera
    de `respuesta-C.md` no lo menciona, y la v1 es de dos días después.
- **Configuración.** La declara la persona; *"El repositorio no permite
  comprobarla"* (`banco-resultados.md`).
- **Qué se puede rehacer.** El corpus, con `extraer_corpus_c.py`, que necesita
  las copias locales de `referencias/_texto-completo/`, y el texto de los dos
  protocolos.
- **Qué no.** El índice que NotebookLM construye sobre el corpus y el modelo
  que responde los controla el proveedor, y no se registró ninguna versión.
  Una consulta nueva puede dar otra respuesta.

## Consensus

- **Versión: no registrada.** La cabecera de `respuestas/respuesta-B.md`
  registra la herramienta y el modo: *"Consensus (consensus.app), modo por
  defecto, sin «Profundo» ni filtros, sin traducción del navegador."*
- **Fecha.** 2026-09-27, 20:39:51 (−0500): *"Es la hora en que se guardó la
  respuesta; la de la corrida no se registró aparte."* (`respuesta-B.md`).
- **Para qué.** El tratamiento B del experimento.
- **Por qué no se puede repetir.**
  - El protocolo lo prohíbe: *"Una sola corrida por tratamiento. No se repite
    la consulta ni se elige entre respuestas."*
    (`protocolo-experimento-v1.md`; `desviaciones.md`, sección 1, lo cita).
  - Y aunque se repitiera, *"una segunda corrida sería otra respuesta"*
    (`respuesta-B.md`).
- **Qué se conserva.** El texto no se versiona, por la licencia que trae su
  pie. En el repositorio está la ficha, `respuesta-B.md`, con el SHA-256 de
  la copia local. Comprobado el 2026-10-15 con `shasum -a 256`: la copia de
  `respuestas/_texto-completo/respuesta-B.md` da el mismo SHA-256, con 7.800
  bytes. Si se pierde, no se puede regenerar.

## Zotero

- **Versión de la exportación: 10.0.4, inferida; no está en el repositorio.**
  `biblioteca-apa7.rtf` no graba con qué se generó. El historial de
  actualizaciones del equipo,
  `~/Library/Caches/Zotero/updates/Applications/Zotero/updates.xml`, tiene una
  sola entrada: la 10.0.5, instalada el 2026-09-30 a las 18:57:33 (−0500),
  con `previousAppVersion="10.0.4"`. La exportación es anterior: la añadió el
  commit «Actividad «Nada sin fuente»: biblioteca en APA 7, exportación nueva
  de Zotero», del 2026-09-29 a las 19:02. Vale si no hubo otra actualización
  que el historial no guarde.
- **Hoy.** 10.0.5 (`defaults read /Applications/Zotero.app/Contents/Info.plist
  CFBundleShortVersionString`), con la 10.0.6 pendiente de instalar
  (`active-update.xml`, `statusText="Install Pending"`).
- **Para qué.** La biblioteca de las 24 referencias del anteproyecto:
  - [`biblioteca-apa7.rtf`](actividad-fuentes/biblioteca-apa7.rtf), la
    exportación en APA 7;
  - [`biblioteca-identificadores.txt`](actividad-fuentes/biblioteca-identificadores.txt),
    los identificadores con que se cargaron: 19 DOI y 5 URL.
- **Configuración.** El estilo instalado hoy es «APA Style 7th edition», con
  `<updated>2026-02-14T01:18:34+00:00</updated>` (`~/Zotero/styles/apa.csl`).
  El archivo se reescribió el 2026-10-06, después de la exportación, así que
  no consta que sea el que se usó.
- **Qué se puede rehacer.** Cargar los identificadores y exportar en APA 7. El
  formato puede cambiar: las dos exportaciones del 2026-09-29 ya difieren en
  páginas, fechas y la etiqueta «[Software]» (mensaje del commit citado).

## Claude Code

- **Versión.** 2.1.265 (`claude --version`, 2026-10-15). **No registrado:**
  con qué versión se hizo cada commit. Los commits graban el modelo, no la
  versión de la herramienta.
- **Modelos, según la línea `Co-Authored-By`.** Sobre la historia de `main`
  hasta el commit «Actividad «Nada sin fuente»: fuera los PDF de los
  entregables», del 2026-10-15: 353 commits, ninguno de fusión, y ninguno con
  más de una línea.

  | Línea `Co-Authored-By` | Commits | Primero | Último |
  |---|---|---|---|
  | Claude Opus 4.7 | 38 | 2026-08-11 | 2026-09-17 |
  | Claude Opus 5 | 32 | 2026-09-19 | 2026-09-21 |
  | Claude Opus 5.5 | 267 | 2026-09-24 | 2026-10-15 |
  | sin la línea | 16 | 2026-08-12 | 2026-09-14 |

  La línea la escribe la herramienta en el mensaje: dice qué modelo se
  declaró, no lo prueba. Su falta no dice quién hizo el commit. La tabla se
  midió así, con `HEAD` en ese commit; cada commit posterior la cambia:

  ```bash
  git log --format='%(trailers:key=Co-Authored-By,valueonly)%x1e' | tr -d '\n' | tr '\036' '\n' | sort | uniq -c
  ```

- **Para qué.** El agente del proyecto: corre las skills, escribe su código y
  redacta. En la actividad clasificó las pasadas 1 y 2 y la tercera lectura
  (`desviaciones.md`, secciones 5 a 7) y evaluó el banco
  (`banco-resultados.md`).
- **Qué se puede rehacer.** Lo que produjo y está versionado: los scripts, que
  se vuelven a correr.
- **Qué no.** Las conversaciones, que no están en el repositorio, y el
  modelo, que controla el proveedor.

## Graphify

- **Versión.** `graphifyy` 0.9.63: `graphify --version` da `graphify 0.9.63`, y
  `uv tool list`, `graphifyy v0.9.63`. Se instaló con uv el 2026-09-17 a las
  17:53, según la fecha de su `uv-receipt.toml`, sin versión fijada: el
  recibo pide solo `graphifyy`.
- **Para qué.** Un grafo del repositorio que se consulta para navegar y para
  detectar desfases entre documentos. No es una fuente:
  [regla 4 de `CLAUDE.md`](CLAUDE.md#4-graphify-se-consulta-no-se-cita).
- **No registrado: la versión de la corrida.** `graphify-out/` está en
  `.gitignore`, y su `graph.json` graba `built_at_commit`, no la versión de
  Graphify. *Inferencia:* `graphify-out/cost.json` registra dos pasadas el
  2026-09-17, desde las 18:07 (−0500), y `graph.json` se escribió ese día a
  las 19:35 (`stat`): las dos cosas, después de la instalación. El entorno de
  la herramienta tiene una sola carpeta `.dist-info`, la de 0.9.63, de las
  17:53 de ese día.
- **Qué no se puede rehacer.** Las cifras del paso semántico: una corrida
  nueva da otros números (regla 4).

## Chart.js

- **Versión.** 4.4.1, según la cabecera de
  `.claude/skills/sintesis-consultoria/assets/chart.umd.min.js`, `Chart.js
  v4.4.1`. Comprobado el 2026-10-15 con `shasum -a 256`: el archivo da
  `74401d738dd3e03ee5dfb3b6841210fe2c4ead8a960c4011ca4ba0b78a9fd8f3`, el que
  registra su [`PROCEDENCIA.md`](.claude/skills/sintesis-consultoria/assets/PROCEDENCIA.md).
- **Para qué.** Los gráficos de la demo, empotrados para que abra sin red.
  `informe/demo.html` y `docs/index.html` llevan la misma cabecera,
  `Chart.js v4.4.1`.
- **Qué se puede rehacer.** Todo: `PROCEDENCIA.md` da la orden de descarga y
  el SHA-256 que debe dar.

## Otras

- **Kaggle CLI 2.2.4** (`kaggle==2.2.4` en `requirements.txt`). Es el
  entorno con que se descargó `train-image.hdf5`: *«`.venv/` con Kaggle CLI
  2.2.4; token en `~/.kaggle/access_token`»* (`CLAUDE.md`, Pendientes).
- **Google Chrome 155.0.8059.80** hoy (`defaults read "/Applications/Google
  Chrome.app/Contents/Info.plist" CFBundleShortVersionString`).
  `informe/md_a_pdf.py` lo llama sin interfaz para pasar Markdown a PDF.
  - **No registrado:** la versión con que se hicieron los PDF anteriores.
  - Los de los entregables de la actividad ya no se versionan, porque basta
    con el `.md` (`actividad-fuentes/README.md`). El 2026-10-15, con esta
    versión, `memoria.md` dio un PDF con el mismo texto, página a página, que
    el que estuvo versionado.
- **git 2.50.1 (Apple Git-155)** (`git --version`).

## Qué quedó «no registrado»

| Qué | Por qué |
|---|---|
| Versiones de paquetes de 14 salidas de `outputs/` | Esas salidas no las graban; hay una inferencia por fechas de instalación |
| Con qué intérprete corrieron los guiones de biblioteca estándar | Ningún archivo lo dice; hoy `python3` es 3.14.7 y el `.venv`, 3.11.9 |
| Las invocaciones de cuatro scripts | `CLAUDE.md`, Pendientes, «Deuda de reproducibilidad» |
| Versión de Python y ubicación del intérprete de 2024 | El archivo de requisitos no la da, y el entorno no aparece en el equipo |
| Commit del código de DINOv2 y determinismo de la extracción | Nada los comprueba |
| Versión de NotebookLM y de Consensus | No hay versión visible registrada; el proveedor las controla |
| Hora de cada consulta de NotebookLM al banco | Solo consta la hora del commit |
| Versión de Zotero en la exportación | El RTF no la graba; 10.0.4 es una inferencia del historial |
| Versión de Claude Code en cada commit | Los commits graban solo el modelo |
| Versión de Graphify en la corrida de `graphify-out/` | `graph.json` no la graba; 0.9.63 es una inferencia |
| Versión de Chrome de los PDF anteriores | No se grabó |

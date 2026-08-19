# Procedencia de `chart.umd.min.js`

**Qué es:** Chart.js v4.4.1, la librería de gráficos que usa
`informe/demo.html`. Está versionada aquí, no cargada desde un CDN.

**Por qué está versionada.** La demo declaraba ser autocontenida y abrir
por doble clic desde una USB, pero cargaba la librería desde
`cdn.jsdelivr.net`. Sin conexión no fallaba de forma visible: lanzaba
`Uncaught ReferenceError: Chart is not defined`, lo que **detiene la
ejecución del script**, y con ella el llenado del resto de la página —
desaparecían los pAUC (0,1451 y 0,1331) y los paneles por skill, pero la
cabecera y el texto seguían viéndose. Un fallo silencioso justo en la
presentación en vivo. Comprobado empíricamente antes de decidir el
cambio, según la regla 5 del proyecto.

**Descarga y verificación (2026-08-18).**

Obtenido de **dos fuentes independientes**, que coinciden byte a byte:

| Fuente | SHA-256 |
|---|---|
| `https://registry.npmjs.org/chart.js/-/chart.js-4.4.1.tgz` → `package/dist/chart.umd.js` | `74401d738dd3e03ee5dfb3b6841210fe2c4ead8a960c4011ca4ba0b78a9fd8f3` |
| `https://unpkg.com/chart.js@4.4.1/dist/chart.umd.js` | `74401d738dd3e03ee5dfb3b6841210fe2c4ead8a960c4011ca4ba0b78a9fd8f3` |

Tamaño: 205.125 bytes.

**Sobre el nombre del archivo.** Se conserva `chart.umd.min.js` porque es
la ruta que pedía el CDN, pero **en el paquete npm ese archivo no
existe**: Chart.js v4 publica `dist/chart.umd.js`, ya minificado.
jsDelivr generaba el `.min.js` al vuelo y le anteponía un aviso propio de
274 bytes. Verificado: quitando ese aviso, lo que servía el CDN es
idéntico a lo que hay aquí — es el mismo código que la demo ya cargaba,
no una versión distinta.

**Licencia: MIT**, confirmada en dos sitios: el campo `license` de
`package/package.json` del paquete oficial, y el banner del propio
archivo:

```
/*!
 * Chart.js v4.4.1
 * https://www.chartjs.org
 * (c) 2023 Chart.js Contributors
 * Released under the MIT License
 */
```

Copia íntegra de la licencia en `chart.js-LICENSE.md`, extraída del mismo
paquete. La MIT exige conservar el aviso de copyright al redistribuir, y
este proyecto redistribuye la librería dentro de `informe/demo.html` y
`docs/index.html`.

**Por qué no se le añadió un comentario de licencia al archivo.** El
banner de arriba ya declara la MIT, así que un comentario nuestro sería
redundante — y tendría un coste: alterar un solo byte rompe la igualdad
con el original y haría imposible volver a verificar el hash contra npm.
El archivo se mantiene idéntico a la fuente y la anotación vive aquí.

**Cómo volver a verificarlo:**

```bash
curl -sSL https://unpkg.com/chart.js@4.4.1/dist/chart.umd.js \
  | shasum -a 256
# debe dar 74401d738dd3e03ee5dfb3b6841210fe2c4ead8a960c4011ca4ba0b78a9fd8f3
```

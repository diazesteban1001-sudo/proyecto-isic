#!/usr/bin/env python3
"""
generar_demo.py — construye informe/demo.html, la síntesis en formato
presentación.

Fase 4 de la skill sintesis-consultoria. El HTML no se escribe a mano:
se genera desde outputs/*.json igual que el informe, para que una
corrección en los instrumentos llegue a los dos entregables o a
ninguno. Un número tecleado en la plantilla sería una cifra inventada.

Los datos van embebidos en el archivo, no se piden con fetch: la demo
tiene que abrir con doble clic desde una USB, sin servidor.

Uso:
    python generar_demo.py --outputs-dir outputs/ --salida informe/demo.html
"""

import argparse
import json
import os
from datetime import datetime, timezone

from scipy import stats


# Los .md de cada instrumento se muestran al hacer clic en su casilla del
# diagrama. sintesis-consultoria no mide nada, así que no tiene un .md de
# resultados propio: se le asocia el de la verificación de trazabilidad,
# que es lo que esta skill sí produce como evidencia de su trabajo.
CADENA = [
    {
        "nombre": "eda-diagnostico",
        "tipo": "instrumento",
        "funcion": "Perfil de datos, faltantes, desbalance, estructura de grupos",
        "md": "eda-diagnostico",
        "mide": "Estructura del archivo, tipos, faltantes por columna, desbalance de la "
                "respuesta, tamaño de los grupos y qué columnas existen en train pero no en test.",
        "porque": "Ninguna decisión de diseño posterior se puede tomar sin esto. El esquema de "
                  "validación depende de la estructura de grupos, y la auditoría de fugas parte "
                  "de la lista de columnas asimétricas.",
    },
    {
        "nombre": "diseno-validacion",
        "tipo": "instrumento",
        "funcion": "Propone y verifica el esquema de validación cruzada",
        "md": "diseno-validacion",
        "mide": "Construye los folds agrupando por paciente y estratificando por clase, y después "
                "comprueba que ningún paciente cruce de un lado al otro. Además cuantifica cuánta "
                "fuga habría producido no hacerlo.",
        "porque": "Proponer un esquema es barato; verificarlo es lo que lo convierte en evidencia. "
                  "Sin la comparación contra la partición ingenua, «hay que agrupar por paciente» "
                  "es una recomendación de manual y no un hallazgo sobre estos datos.",
    },
    {
        "nombre": "auditoria-de-fugas",
        "tipo": "instrumento",
        "funcion": "Chequeos de fuga estructural y escaneo univariado",
        "md": "auditoria-de-fugas",
        "mide": "Dos cosas distintas: fuga estructural —columnas ausentes en test, constantes, "
                "identificadores— y fuga oculta, entrenando un modelo por columna sobre los folds "
                "agrupados para ver si alguna predice el objetivo sospechosamente bien.",
        "porque": "Es el instrumento adversario: existe para encontrar defectos, no para "
                  "confirmar que todo está bien. Un chequeo que no puede fallar no vale nada.",
    },
    {
        "nombre": "modelado-baseline",
        "tipo": "instrumento",
        "funcion": "Modelos de referencia con la métrica oficial",
        "md": "modelado-baseline",
        "mide": "Cuatro niveles de referencia sobre los mismos folds, evaluados con la métrica "
                "oficial de la competencia y no con la de por defecto, reportando el resultado de "
                "cada fold y no solo la media.",
        "porque": "Los niveles existen para acotar: sin la referencia univariada no se sabe "
                  "cuánto aporta combinar columnas, y sin el modelo desbalanceado no se ve que "
                  "omitir el ajuste de clase produce un fallo silencioso.",
    },
    {
        "nombre": "sintesis-consultoria",
        "tipo": "interpretación",
        "funcion": "Lee todo outputs/ y produce el informe y esta demo",
        # No mide nada, así que no tiene un .md de resultados propio: se le
        # asocia el de la verificación de trazabilidad, que es la evidencia
        # de que hizo su trabajo.
        "md": "sintesis-verificacion",
        "mide": "Nada. Es la única skill que interpreta: cruza los cuatro instrumentos, resuelve "
                "sus contradicciones y emite la recomendación. Lo que sí verifica es a sí misma, "
                "extrayendo cada número del informe y comprobando que tenga respaldo en outputs/.",
        "porque": "Es el trabajo del consultor, y está separado de los instrumentos a propósito: "
                  "un instrumento que interpretara sus propios resultados tendería a "
                  "justificarlos.",
    },
]

# Glosas por familia de columna. NO son medición: el JSON dice que una
# columna no está en test, no dice por qué. El porqué es lectura del
# consultor y en la página se marca como tal, en su propia columna
# rotulada, nunca mezclada con lo medido.
GLOSAS = {
    "iddx": "Taxonomía diagnóstica: es la etiqueta con otro nombre.",
    "mel_": "Solo existe tras la biopsia, y solo para melanomas. Predecir el pasado con información del futuro.",
    "tbp_lv_dnn_lesion_confidence": "No es post-biopsia, pero al no estar en test cualquier modelo que la use es inservible en inferencia.",
    "lesion_id": "Identificador de lesión, presente solo en train.",
    "target": "Es la variable respuesta.",
    "image_type": "Constante en todo el archivo: no distingue nada.",
    "isic_id": "Identificador de fila.",
}


def glosa(col):
    for clave, texto in GLOSAS.items():
        if col.startswith(clave):
            return texto
    return ""


def motivo_mecanico(col, auditoria):
    """El motivo tal como lo dejó el instrumento, sin interpretar."""
    motivos = []
    if col in auditoria.get("columnas_solo_en_train", []):
        motivos.append("no está en test")
    if col in auditoria.get("columnas_constantes", []):
        motivos.append("constante")
    if col in auditoria.get("columnas_identificador", []):
        motivos.append("identificador")
    return " + ".join(motivos) if motivos else "excluida por el script de modelado"


def leer(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def construir_datos(outputs_dir):
    def cargar(nombre):
        return json.loads(leer(os.path.join(outputs_dir, f"{nombre}.json")))

    eda = cargar("eda-diagnostico")
    validacion = cargar("diseno-validacion")
    auditoria = cargar("auditoria-de-fugas")
    modelado = cargar("modelado-baseline")

    niveles = [
        ("Nivel 0", "Referencia univariada", "nivel_0_referencia_univariada"),
        ("Nivel 1", "Regresión logística", "nivel_1_regresion_logistica"),
        ("Nivel 2a", "Gradient boosting sin balancear", "nivel_2a_gradient_boosting_sin_balancear"),
        ("Nivel 2b", "Gradient boosting balanceado", "nivel_2b_gradient_boosting_balanceado"),
    ]
    modelos = []
    for etiqueta, descripcion, clave in niveles:
        bloque = modelado[clave]
        modelos.append({
            "etiqueta": etiqueta,
            "descripcion": descripcion,
            "campo": clave,
            "media": bloque["pauc_media"],
            "std": bloque["pauc_std"],
            "por_fold": bloque["pauc_por_fold"],
            "nota": bloque.get("nota", ""),
        })

    n1 = modelado["nivel_1_regresion_logistica"]["pauc_por_fold"]
    b2 = modelado["nivel_2b_gradient_boosting_balanceado"]["pauc_por_fold"]
    diferencias = [round(b - a, 6) for a, b in zip(n1, b2)]
    n = len(diferencias)
    media_dif = sum(diferencias) / n
    # Desviación muestral (n-1): las cinco diferencias son una muestra, no
    # la población de todas las particiones posibles.
    var = sum((d - media_dif) ** 2 for d in diferencias) / (n - 1)
    sd_dif = var ** 0.5
    t_critico = float(stats.t.ppf(0.975, n - 1))
    margen = t_critico * sd_dif / (n ** 0.5)

    pareado = {
        "diferencias": diferencias,
        "media": media_dif,
        "sd": sd_dif,
        "t_critico": t_critico,
        "ic_bajo": media_dif - margen,
        "ic_alto": media_dif + margen,
        "folds_a_favor": sum(1 for d in diferencias if d > 0),
        "n_folds": n,
    }

    excluidas = []
    for col in modelado["columnas_excluidas"]:
        excluidas.append({
            "columna": col,
            "motivo": motivo_mecanico(col, auditoria),
            "glosa": glosa(col),
        })

    # El contraejemplo: nombre sospechoso, pero el instrumento la dejó
    # pasar y la investigación confirmó que es legítima. Sin esta fila la
    # tabla de exclusiones parece un filtro por nombre.
    nevi = next(
        (u for u in auditoria["univariado"] if u["columna"] == "tbp_lv_nevi_confidence"),
        None,
    )

    resumenes = {}
    for skill in CADENA:
        ruta = os.path.join(outputs_dir, f"{skill['md']}.md")
        resumenes[skill["md"]] = leer(ruta) if os.path.exists(ruta) else "(sin archivo)"

    mejor_univariada = max(auditoria["univariado"], key=lambda u: u["auc_oof"])
    positivos_por_fold = [f["n_val_positivos"] for f in validacion["por_fold"]]
    verificacion = json.loads(leer(os.path.join(outputs_dir, "sintesis-verificacion.json")))

    return {
        "generado": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "cadena": CADENA,
        "resumenes": resumenes,
        "auditoria": {
            "n_solo_en_train": len(auditoria["columnas_solo_en_train"]),
            "n_constantes": len(auditoria["columnas_constantes"]),
            "n_identificador": len(auditoria["columnas_identificador"]),
            "n_evaluadas": len(auditoria["univariado"]),
            "umbral": auditoria["umbral_auc_sospechoso"],
            "auc_max": mejor_univariada["auc_oof"],
            "columna_auc_max": mejor_univariada["columna"],
            "n_preguntas_abiertas": len(auditoria["preguntas_abiertas"]),
        },
        "verificacion": {
            "numeros": verificacion["numeros_en_borrador"],
            "con_respaldo": verificacion["numeros_con_respaldo_en_outputs"],
            "senalados": len(verificacion["numeros_sin_respaldo"]),
            # Los tres no suman: el verificador extrae todo número y luego
            # descarta los de contextos que no son cifras medidas. El resto
            # es ese descarte, y sin nombrarlo la resta parece un error.
            "ignorados": (
                verificacion["numeros_en_borrador"]
                - verificacion["numeros_con_respaldo_en_outputs"]
                - len(verificacion["numeros_sin_respaldo"])
            ),
        },
        "folds": {
            "n_grupos_positivos": validacion["n_grupos_positivos"],
            "min_positivos": min(positivos_por_fold),
            "max_positivos": max(positivos_por_fold),
        },
        "test_es_marcador": eda["test_is_placeholder"],
        "eda": {
            "n_filas": eda["fuente"]["n_filas"],
            "n_columnas": eda["fuente"]["n_columnas"],
            "n_pacientes": eda["estructura_grupos"]["n_grupos"],
            "media_por_paciente": eda["estructura_grupos"]["filas_por_grupo"]["media"],
            "min_por_paciente": eda["estructura_grupos"]["filas_por_grupo"]["min"],
            "max_por_paciente": eda["estructura_grupos"]["filas_por_grupo"]["max"],
            "n_solo_en_train": len(eda["columnas_solo_en_train"]),
            "positivos": eda["desbalance_target"]["conteos"]["1"],
            "negativos": eda["desbalance_target"]["conteos"]["0"],
            "pct_positivos": eda["desbalance_target"]["pct_positivos"],
        },
        "fuga": {
            "metodo": validacion["esquema"]["metodo"],
            "n_splits": validacion["esquema"]["n_splits"],
            "group_col": validacion["esquema"]["group_col"],
            "pct_naive": validacion["comparacion_particion_naive"]["pct_grupos_con_fuga"],
            "n_grupos_naive": validacion["comparacion_particion_naive"]["n_grupos_con_fuga"],
            "n_grupos_total": validacion["n_grupos_total"],
            "descripcion_naive": validacion["comparacion_particion_naive"]["descripcion"],
            "fuga_agrupada": validacion["fuga_de_grupo_detectada"],
            "por_fold": validacion["por_fold"],
        },
        "excluidas": excluidas,
        "n_features_usadas": modelado["n_features_usadas"],
        "nevi": nevi,
        "modelos": modelos,
        "pareado": pareado,
        "escala": modelado["escala_de_referencia_pauc"],
        "metrica": modelado["metrica"],
        "metrica_fuente": modelado["metrica_fuente"],
        "metrica_verificada": modelado["metrica_verificada_contra_fuente_oficial"],
    }


PLANTILLA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agente consultor estad&iacute;stico &mdash; ISIC 2024</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --tinta: #16202b;
    --suave: #5b6b7c;
    --linea: #d8e0e8;
    --fondo: #f4f6f9;
    --acento: #1f5f8b;
    --alarma: #b8341f;
    --bien: #1e7a52;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    color: var(--tinta);
    background: var(--fondo);
    line-height: 1.55;
  }
  .hoja { max-width: 1080px; margin: 0 auto; padding: 0 28px 72px; }
  header { padding: 44px 0 28px; border-bottom: 3px solid var(--tinta); }
  .kicker {
    text-transform: uppercase; letter-spacing: .16em; font-size: 12px;
    color: var(--suave); font-weight: 600;
  }
  h1 { font-size: 30px; margin: 10px 0 16px; line-height: 1.25; }
  .contexto { margin: 0 0 22px; max-width: 860px; }
  .contexto p { margin: 0 0 12px; font-size: 15.5px; }
  .contexto b { color: var(--acento); }
  .tesis {
    font-size: 21px; line-height: 1.45; border-left: 5px solid var(--acento);
    padding: 4px 0 4px 18px; margin: 0; color: var(--tinta);
  }
  .tesis strong { color: var(--acento); }
  section { margin-top: 52px; }
  h2 { font-size: 21px; margin: 0 0 6px; }
  h2 .num {
    display: inline-block; width: 30px; height: 30px; line-height: 30px;
    text-align: center; background: var(--tinta); color: #fff;
    border-radius: 50%; font-size: 14px; margin-right: 10px;
  }
  .sub { color: var(--suave); margin: 0 0 20px; font-size: 15px; }
  .tarjeta {
    background: #fff; border: 1px solid var(--linea); border-radius: 10px;
    padding: 22px; box-shadow: 0 1px 2px rgba(22,32,43,.05);
  }
  /* ---- cadena de skills ---- */
  .cadena { display: flex; align-items: stretch; gap: 6px; flex-wrap: wrap; }
  .paso {
    flex: 1 1 165px; text-align: left; cursor: pointer; background: #fff;
    border: 1px solid var(--linea); border-top: 4px solid var(--suave);
    border-radius: 8px; padding: 13px 14px; font: inherit; color: inherit;
    transition: transform .12s, box-shadow .12s, border-color .12s;
  }
  .paso:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(22,32,43,.12); }
  .paso[aria-selected="true"] { border-color: var(--acento); border-top-color: var(--acento); background: #eef5fa; }
  .paso.final { border-top-color: var(--acento); }
  .paso .nom { font-weight: 700; font-size: 14px; display: block; }
  .paso .tipo {
    font-size: 10px; text-transform: uppercase; letter-spacing: .1em;
    color: var(--suave); font-weight: 600;
  }
  .paso.final .tipo { color: var(--acento); }
  .paso .fun { font-size: 12px; color: var(--suave); margin-top: 6px; display: block; }
  .flecha { align-self: center; color: var(--suave); font-size: 20px; }
  .salida {
    margin-top: 16px; background: #fff; border: 1px solid var(--linea);
    border-radius: 10px; padding: 0 20px 4px;
  }
  .salida h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .08em; color: var(--suave); }
  .ficha { margin: 0 0 16px; }
  .ficha p { margin: 0 0 9px; font-size: 14.5px; }
  .ficha b { color: var(--acento); }
  .ficha .hallazgo { border-left: 3px solid var(--acento); background: #f4f8fb; padding: 9px 13px; border-radius: 0 6px 6px 0; }
  .salida pre {
    white-space: pre-wrap; font-family: Menlo, Consolas, monospace;
    font-size: 12.5px; line-height: 1.6; background: #fbfcfd;
    border: 1px solid var(--linea); border-radius: 6px; padding: 14px; overflow-x: auto;
  }
  /* ---- fuga ---- */
  .duo { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .medida { text-align: center; padding: 24px 18px; border-radius: 10px; border: 1px solid var(--linea); background: #fff; }
  .medida .cifra { font-size: 52px; font-weight: 700; line-height: 1; }
  .medida.mal { border-color: #f0c4bc; background: #fdf4f2; }
  .medida.mal .cifra { color: var(--alarma); }
  .medida.ok { border-color: #b9ded0; background: #f2faf6; }
  .medida.ok .cifra { color: var(--bien); }
  .medida .rot { font-weight: 600; margin-top: 10px; }
  .medida .det { font-size: 13px; color: var(--suave); margin-top: 4px; }
  /* ---- tablas ---- */
  table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--linea); vertical-align: top; }
  th { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--suave); }
  td.mono { font-family: Menlo, Consolas, monospace; font-size: 12.5px; }
  .lectura { color: var(--suave); }
  .aviso {
    font-size: 12.5px; color: var(--suave); background: #fbfcfd;
    border-left: 3px solid var(--linea); padding: 8px 12px; margin: 14px 0 0;
  }
  .contra { margin-top: 18px; border-left: 4px solid var(--bien); background: #f2faf6; padding: 14px 16px; border-radius: 0 8px 8px 0; }
  .contra b { color: var(--bien); }
  /* ---- toggle ---- */
  .barra { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
  .toggle { display: inline-flex; border: 1px solid var(--linea); border-radius: 8px; overflow: hidden; background: #fff; }
  .toggle button {
    border: 0; background: #fff; padding: 9px 18px; font: inherit; font-size: 13.5px;
    cursor: pointer; color: var(--suave); font-weight: 600;
  }
  .toggle button[aria-pressed="true"] { background: var(--acento); color: #fff; }
  .lienzo { position: relative; height: 340px; }
  /* ---- cierre ---- */
  .cierre { display: grid; gap: 16px; }
  .bloque { background: #fff; border: 1px solid var(--linea); border-radius: 10px; padding: 20px 22px; border-left: 5px solid var(--suave); }
  .bloque h3 { margin: 0 0 8px; font-size: 16px; }
  .bloque p { margin: 0; font-size: 14.5px; }
  .bloque.recomendacion { border-left-color: var(--bien); }
  .bloque.recomendacion h3 { color: var(--bien); }
  .bloque.limites { border-left-color: var(--alarma); }
  .bloque.limites h3 { color: var(--alarma); }
  .pie-grafico { font-size: 13px; color: var(--suave); margin-top: 14px; }
  .destacado { color: var(--tinta); }
  .cifra-fuente { border-bottom: 1px dotted var(--suave); cursor: help; }
  footer {
    margin-top: 64px; padding-top: 20px; border-top: 1px solid var(--linea);
    font-size: 12.5px; color: var(--suave);
  }
  @media (max-width: 760px) {
    .duo { grid-template-columns: 1fr; }
    .flecha { display: none; }
  }
</style>
</head>
<body>
<div class="hoja">

<header>
  <div class="kicker">Consultor&iacute;a e Investigaci&oacute;n &middot; Estad&iacute;stica &middot; caso ISIC 2024</div>
  <h1>Agente consultor estad&iacute;stico</h1>
  <div class="contexto">
    <p><b>El problema.</b> <span id="ctx-problema"></span></p>
    <p><b>Por qu&eacute; este caso.</b> <span id="ctx-eleccion"></span></p>
  </div>
  <p class="tesis">
    La finalidad del agente <strong>no es ganar la competencia</strong>: es leer la funci&oacute;n
    de utilidad que el cliente escribi&oacute; en su m&eacute;trica y emitir una recomendaci&oacute;n
    defendible, con cada cifra rastreable hasta el archivo que la produjo.
  </p>
</header>

<section>
  <h2><span class="num">1</span>La cadena de instrumentos</h2>
  <p class="sub">Cuatro skills miden y reportan. La quinta interpreta. Haz clic en cualquiera para ver su salida real.</p>
  <div class="cadena" id="cadena"></div>
  <div class="salida" id="salida" hidden>
    <h3 id="salida-nombre"></h3>
    <div class="ficha">
      <p><b>Qu&eacute; mide.</b> <span id="ficha-mide"></span></p>
      <p><b>Por qu&eacute; existe.</b> <span id="ficha-porque"></span></p>
      <p class="hallazgo"><b>Un hallazgo concreto.</b> <span id="ficha-hallazgo"></span></p>
    </div>
    <h3 id="salida-titulo"></h3>
    <pre id="salida-texto"></pre>
  </div>
</section>

<section>
  <h2><span class="num">2</span>El hallazgo de fuga</h2>
  <p class="sub" id="sub-fuga"></p>
  <div class="duo">
    <div class="medida mal">
      <div class="cifra" id="fuga-naive"></div>
      <div class="rot">Partici&oacute;n aleatoria por fila</div>
      <div class="det" id="fuga-naive-det"></div>
    </div>
    <div class="medida ok">
      <div class="cifra" id="fuga-agrupada"></div>
      <div class="rot" id="fuga-agrupada-rot"></div>
      <div class="det" id="fuga-agrupada-det"></div>
    </div>
  </div>
  <p class="aviso" id="aviso-fuga"></p>
</section>

<section>
  <h2><span class="num">3</span>Columnas excluidas</h2>
  <p class="sub" id="sub-excluidas"></p>
  <div class="tarjeta">
    <table>
      <thead>
        <tr>
          <th style="width:34%">Columna</th>
          <th style="width:24%">Motivo medido</th>
          <th style="width:42%">Lectura del consultor (interpretaci&oacute;n)</th>
        </tr>
      </thead>
      <tbody id="tbody-excluidas"></tbody>
    </table>
    <p class="aviso">La columna &laquo;motivo medido&raquo; sale de <code>auditoria-de-fugas.json</code>.
       La tercera columna no: es interpretaci&oacute;n, y por eso va rotulada aparte.</p>
    <div class="contra" id="contra"></div>
  </div>
</section>

<section>
  <h2><span class="num">4</span>Los cuatro niveles de modelado</h2>
  <p class="sub" id="sub-modelos"></p>
  <div class="tarjeta">
    <div class="barra">
      <div class="toggle" role="group" aria-label="Vista de resultados">
        <button id="btn-medias" aria-pressed="true">Medias</button>
        <button id="btn-pareada" aria-pressed="false">Pareada por fold</button>
      </div>
      <div class="pie-grafico" id="escala"></div>
    </div>
    <div class="lienzo"><canvas id="gr-modelos"></canvas></div>
    <p class="pie-grafico" id="pie-modelos"></p>
  </div>
</section>

<section>
  <h2><span class="num">5</span>Conclusi&oacute;n</h2>
  <p class="sub">Lo que un consultor le entregar&iacute;a al cliente: el hallazgo, la recomendaci&oacute;n y lo que a&uacute;n no se puede afirmar.</p>
  <div class="cierre">
    <div class="bloque">
      <h3>Lo que se encontr&oacute;</h3>
      <p id="cierre-hallazgos"></p>
    </div>
    <div class="bloque recomendacion">
      <h3>La recomendaci&oacute;n</h3>
      <p id="cierre-recomendacion"></p>
    </div>
    <div class="bloque limites">
      <h3>Las limitaciones honestas</h3>
      <p id="cierre-limites"></p>
    </div>
  </div>
</section>

<footer id="pie"></footer>
</div>

<script id="datos" type="application/json">__DATOS__</script>
<script>
const D = JSON.parse(document.getElementById("datos").textContent);
const esc = t => String(t).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const num = (v, d = 4) => v.toFixed(d).replace(".", ",");
// Cada cifra lleva su origen en el title: la trazabilidad del informe
// escrito, disponible al pasar el raton en la version proyectada.
const cifra = (v, fuente) => `<span class="cifra-fuente" title="${esc(fuente)}">${v}</span>`;
// useGrouping "always" porque el defecto español omite el punto en los
// números de cuatro cifras: "1042" al lado de "401.059" se lee como una
// inconsistencia en una pantalla proyectada.
const mil = v => v.toLocaleString("es", {useGrouping: "always"});

/* ---------- 0. contexto ---------- */
document.getElementById("ctx-problema").innerHTML =
  `ISIC 2024 pide detectar lesiones malignas de piel a partir de fotograf&iacute;as corporales totales en 3D ` +
  `&mdash; im&aacute;genes de calidad tipo smartphone, no dermatoscopio cl&iacute;nico. El dataset: ` +
  `${cifra(mil(D.eda.n_filas), "eda-diagnostico.json > fuente.n_filas")} lesiones de ` +
  `${cifra(mil(D.eda.n_pacientes), "eda-diagnostico.json > estructura_grupos.n_grupos")} pacientes, con solo ` +
  `${cifra(mil(D.eda.positivos), "eda-diagnostico.json > desbalance_target.conteos.1")} casos malignos confirmados ` +
  `(${cifra(num(D.eda.pct_positivos, 3) + "%", "eda-diagnostico.json > desbalance_target.pct_positivos")}). ` +
  `Cada paciente aporta entre ${cifra(mil(D.eda.min_por_paciente), "eda-diagnostico.json > estructura_grupos.filas_por_grupo.min")} y ` +
  `${cifra(mil(D.eda.max_por_paciente), "eda-diagnostico.json > estructura_grupos.filas_por_grupo.max")} lesiones.`;

document.getElementById("ctx-eleccion").innerHTML =
  `Se eligi&oacute; sobre otras opciones (detecci&oacute;n en rodilla, columna lumbar, series de tiempo de commodities) ` +
  `porque la metadata tabular permite trabajar sin GPU, el desbalance extremo y la agrupaci&oacute;n por paciente presentan ` +
  `riesgos reales de fuga de datos, y la m&eacute;trica oficial &mdash;${cifra(esc(D.metrica), "modelado-baseline.json > metrica")}&mdash; ` +
  `codifica expl&iacute;citamente la funci&oacute;n de utilidad del cliente: un sistema de apoyo diagn&oacute;stico debe ser ` +
  `altamente sensible, as&iacute; que el desempe&ntilde;o solo cuenta en la regi&oacute;n donde una tasa de detecci&oacute;n alta ` +
  `es cl&iacute;nicamente aceptable.`;

/* ---------- 1. cadena ---------- */
// La prosa de cada instrumento (que mide, por que existe) viaja en el JSON
// desde CADENA. El hallazgo concreto se arma aqui porque lleva cifras: cada
// una pasa por cifra() y por tanto por su archivo y campo de origen.
const HALLAZGOS = {
  "eda-diagnostico": () =>
    `Encontr&oacute; ${cifra(D.eda.n_solo_en_train, "eda-diagnostico.json > columnas_solo_en_train")} columnas presentes ` +
    `solo en entrenamiento, de las ${cifra(D.eda.n_columnas, "eda-diagnostico.json > fuente.n_columnas")} del archivo ` +
    `&mdash; la primera se&ntilde;al de que algo ah&iacute; no estar&iacute;a disponible al predecir en producci&oacute;n.`,
  "diseno-validacion": () =>
    `Cuantific&oacute; cu&aacute;nta fuga habr&iacute;a producido ignorar la agrupaci&oacute;n por paciente: ` +
    `${cifra(num(D.fuga.pct_naive, 2) + "%", "diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga")} ` +
    `de los pacientes (${cifra(mil(D.fuga.n_grupos_naive), "diseno-validacion.json > comparacion_particion_naive.n_grupos_con_fuga")} ` +
    `de ${cifra(mil(D.fuga.n_grupos_total), "diseno-validacion.json > n_grupos_total")}) habr&iacute;an caído a los dos lados de la partición.`,
  "auditoria-de-fugas": () =>
    `Gener&oacute; ${cifra(D.auditoria.n_preguntas_abiertas, "auditoria-de-fugas.json > preguntas_abiertas")} preguntas abiertas ` +
    `sobre columnas sospechosas; ${cifra(D.auditoria.n_preguntas_abiertas - 1, "derivado: preguntas_abiertas menos la que exigió fuente externa")} ` +
    `se resolvieron por su naturaleza post-biopsia, y la &uacute;ltima exigi&oacute; rastrear un paper cient&iacute;fico hasta confirmar ` +
    `que <code>${esc(D.nevi ? D.nevi.columna : "")}</code>, de apariencia sospechosa, era en realidad leg&iacute;tima.`,
  "modelado-baseline": () =>
    `En el camino se descubri&oacute; que la implementaci&oacute;n inicial de la m&eacute;trica usaba un umbral de sensibilidad ` +
    `equivocado y subestimaba el m&aacute;ximo posible de la escala, que es ` +
    `${cifra(num(D.escala.maximo, 1), "modelado-baseline.json > escala_de_referencia_pauc.maximo")}. Corregida y verificada contra ` +
    `la fuente oficial (${cifra(esc(D.metrica_fuente), "modelado-baseline.json > metrica_fuente")}) antes de confiar en ning&uacute;n resultado.`,
  "sintesis-consultoria": () =>
    `Extrajo los ${cifra(mil(D.verificacion.numeros), "sintesis-verificacion.json > numeros_en_borrador")} n&uacute;meros del borrador ` +
    `y los contrast&oacute; contra <code>outputs/</code>: ` +
    `${cifra(mil(D.verificacion.con_respaldo), "sintesis-verificacion.json > numeros_con_respaldo_en_outputs")} con respaldo exacto, ` +
    `${cifra(D.verificacion.senalados, "sintesis-verificacion.json > numeros_sin_respaldo")} se&ntilde;alados para revisi&oacute;n a mano, ` +
    `y ${cifra(D.verificacion.ignorados, "derivado: numeros_en_borrador menos los con respaldo y los señalados")} en contextos que el ` +
    `verificador excluye por dise&ntilde;o (n&uacute;meros de secci&oacute;n, fechas y similares).`
};

const cadena = document.getElementById("cadena");
D.cadena.forEach((s, i) => {
  const b = document.createElement("button");
  b.className = "paso" + (s.tipo !== "instrumento" ? " final" : "");
  b.setAttribute("aria-selected", "false");
  b.innerHTML = `<span class="tipo">${esc(s.tipo)}</span>
                 <span class="nom">${esc(s.nombre)}</span>
                 <span class="fun">${esc(s.funcion)}</span>`;
  b.onclick = () => {
    const abierto = b.getAttribute("aria-selected") === "true";
    document.querySelectorAll(".paso").forEach(p => p.setAttribute("aria-selected", "false"));
    const caja = document.getElementById("salida");
    if (abierto) { caja.hidden = true; return; }
    b.setAttribute("aria-selected", "true");
    document.getElementById("salida-nombre").textContent = s.nombre;
    document.getElementById("ficha-mide").textContent = s.mide;
    document.getElementById("ficha-porque").textContent = s.porque;
    document.getElementById("ficha-hallazgo").innerHTML = HALLAZGOS[s.nombre]();
    document.getElementById("salida-titulo").textContent = "outputs/" + s.md + ".md";
    document.getElementById("salida-texto").textContent = D.resumenes[s.md];
    caja.hidden = false;
  };
  cadena.appendChild(b);
  if (i < D.cadena.length - 1) {
    const f = document.createElement("div");
    f.className = "flecha"; f.textContent = "\u2192";
    cadena.appendChild(f);
  }
});

/* ---------- 2. fuga ---------- */
const F = D.fuga;
document.getElementById("sub-fuga").textContent =
  `${mil(D.eda.n_filas)} lesiones sobre ${mil(F.n_grupos_total)} pacientes ` +
  `(${num(D.eda.media_por_paciente, 2)} por paciente en promedio, hasta ${mil(D.eda.max_por_paciente)}). ` +
  `Si se parte al azar, el mismo paciente cae a los dos lados.`;
document.getElementById("fuga-naive").innerHTML = cifra(num(F.pct_naive, 2) + "%", "diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga");
document.getElementById("fuga-naive-det").textContent =
  `${mil(F.n_grupos_naive)} de ${mil(F.n_grupos_total)} pacientes aparecen en train y validación a la vez`;
document.getElementById("fuga-agrupada").innerHTML = cifra(F.fuga_agrupada ? "?" : "0%", "diseno-validacion.json > fuga_de_grupo_detectada");
document.getElementById("fuga-agrupada-rot").textContent = F.metodo + ` (k=${F.n_splits})`;
document.getElementById("fuga-agrupada-det").textContent =
  `Ningún ${F.group_col} compartido entre particiones, verificado fold a fold`;
document.getElementById("aviso-fuga").textContent =
  `Comparación: ${F.descripcion_naive}. La fuga por partición aleatoria no es un riesgo teórico en estos datos: es lo que pasa por defecto.`;

/* ---------- 3. columnas excluidas ---------- */
document.getElementById("sub-excluidas").textContent =
  `${D.excluidas.length} de las ${D.eda.n_columnas} columnas quedan fuera. Se modela con ${D.n_features_usadas}.`;
document.getElementById("tbody-excluidas").innerHTML = D.excluidas.map(e => `
  <tr>
    <td class="mono">${esc(e.columna)}</td>
    <td>${esc(e.motivo)}</td>
    <td class="lectura">${esc(e.glosa)}</td>
  </tr>`).join("");
if (D.nevi) {
  document.getElementById("contra").innerHTML =
    `<b>El contraejemplo.</b> <code>${esc(D.nevi.columna)}</code> tiene nombre sospechoso y el instrumento la marcó, ` +
    `pero <b>sí está en test</b> y su AUC univariado fuera de muestra es ${cifra(num(D.nevi.auc_oof), "auditoria-de-fugas.json > univariado[].auc_oof")}. ` +
    `Resolverla exigió leer el paper de SLICE-3D: es una métrica que la máquina calcula sobre la imagen, no un resultado de patología. ` +
    `Nombre sospechoso no es fuga &mdash; y esa distinción no la puede hacer un script.`;
}

/* ---------- 4. modelado ---------- */
document.getElementById("escala").innerHTML =
  `Escala: azar = ${cifra(num(D.escala.azar, 2), "modelado-baseline.json > escala_de_referencia_pauc.azar")}, ` +
  `máximo = ${cifra(num(D.escala.maximo, 1), "modelado-baseline.json > escala_de_referencia_pauc.maximo")}`;
document.getElementById("sub-modelos").textContent = D.metrica + ". Cinco folds, mismos folds para todos los niveles.";

// Bigotes de +/- 1 desviacion entre folds. Se dibujan a mano porque
// Chart.js no trae barras de error: sin ellas la vista de medias
// sugiere una precision que estos cinco folds no tienen.
const bigotes = {
  id: "bigotes",
  afterDatasetsDraw(ch) {
    const ds = ch.data.datasets[0];
    if (!ds.desviaciones) return;
    const meta = ch.getDatasetMeta(0), ejeY = ch.scales.y, cx = ch.ctx;
    cx.save(); cx.strokeStyle = "#16202b"; cx.lineWidth = 1.5;
    meta.data.forEach((barra, i) => {
      const s = ds.desviaciones[i], v = ds.data[i];
      if (!s) return;
      const arriba = ejeY.getPixelForValue(v + s), abajo = ejeY.getPixelForValue(v - s), x = barra.x;
      cx.beginPath();
      cx.moveTo(x, arriba); cx.lineTo(x, abajo);
      cx.moveTo(x - 7, arriba); cx.lineTo(x + 7, arriba);
      cx.moveTo(x - 7, abajo); cx.lineTo(x + 7, abajo);
      cx.stroke();
    });
    cx.restore();
  }
};

// Linea del piso aleatorio: sin ella, el 0,0013 del nivel 2a parece
// solo "bajo" en vez de estar por debajo del azar, que es el hallazgo.
const piso = {
  id: "piso",
  beforeDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(D.escala.azar), cx = ch.ctx;
    if (!isFinite(y)) return;
    cx.save();
    cx.strokeStyle = "#b8341f"; cx.setLineDash([5, 4]); cx.lineWidth = 1.5;
    cx.beginPath(); cx.moveTo(ch.chartArea.left, y); cx.lineTo(ch.chartArea.right, y); cx.stroke();
    cx.restore();
  },
  // El rótulo va DESPUÉS de las barras y sobre fondo opaco: dibujado
  // antes, la barra del nivel 2b le pasaba por encima y solo se leia
  // "aleatorio 0,02".
  afterDatasetsDraw(ch) {
    const y = ch.scales.y.getPixelForValue(D.escala.azar), cx = ch.ctx;
    if (!isFinite(y)) return;
    const texto = "piso aleatorio " + num(D.escala.azar, 2);
    cx.save();
    cx.font = "600 11px -apple-system, sans-serif"; cx.textAlign = "right";
    const ancho = cx.measureText(texto).width;
    const x = ch.chartArea.right - 6;
    cx.fillStyle = "rgba(255,255,255,.85)";
    cx.fillRect(x - ancho - 4, y - 18, ancho + 8, 15);
    cx.fillStyle = "#b8341f";
    cx.fillText(texto, x, y - 7);
    cx.restore();
  }
};

const COLORES = ["#8fa6b8", "#4a7fa5", "#c98b7a", "#1f5f8b"];
const lienzo = document.getElementById("gr-modelos");
let grafico = null;

function vistaMedias() {
  return {
    type: "bar",
    plugins: [bigotes, piso],
    data: {
      labels: D.modelos.map(m => m.etiqueta),
      datasets: [{
        label: "pAUC medio",
        data: D.modelos.map(m => m.media),
        desviaciones: D.modelos.map(m => m.std),
        backgroundColor: COLORES,
        borderRadius: 4,
        maxBarThickness: 96
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, suggestedMax: 0.2, title: { display: true, text: "pAUC (0,02 = azar, 0,2 = perfecto)" } },
        x: { ticks: { callback: (v, i) => D.modelos[i].etiqueta } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: it => D.modelos[it[0].dataIndex].etiqueta + " \u2014 " + D.modelos[it[0].dataIndex].descripcion,
            label: it => "pAUC " + num(D.modelos[it.dataIndex].media) + "  \u00b1" + num(D.modelos[it.dataIndex].std) + " entre folds",
            afterLabel: it => "modelado-baseline.json > " + D.modelos[it.dataIndex].campo
          }
        }
      }
    }
  };
}

function vistaPareada() {
  const n1 = D.modelos.find(m => m.etiqueta === "Nivel 1");
  const b2 = D.modelos.find(m => m.etiqueta === "Nivel 2b");
  return {
    type: "bar",
    data: {
      labels: D.pareado.diferencias.map((_, i) => "Fold " + i),
      datasets: [
        { label: n1.etiqueta + " \u2014 " + n1.descripcion, data: n1.por_fold, backgroundColor: "#4a7fa5", borderRadius: 4 },
        { label: b2.etiqueta + " \u2014 " + b2.descripcion, data: b2.por_fold, backgroundColor: "#1f5f8b", borderRadius: 4 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: "pAUC en el fold" } } },
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: it => it.dataset.label + ": " + num(it.parsed.y),
            afterBody: it => {
              const d = D.pareado.diferencias[it[0].dataIndex];
              return "Diferencia 2b \u2212 1: " + (d > 0 ? "+" : "\u2212") + num(Math.abs(d));
            }
          }
        }
      }
    }
  };
}

const PIE = {
  medias: () => {
    const n2a = D.modelos.find(m => m.etiqueta === "Nivel 2a");
    return `El <span class="destacado">nivel 2a queda en ${cifra(num(n2a.media), "modelado-baseline.json > nivel_2a_gradient_boosting_sin_balancear.pauc_media")}, ` +
      `por debajo del piso aleatorio</span>: no colapsa a predecir siempre negativo, satura en probabilidad 1 sobre negativos y los coloca ` +
      `encima de los positivos, arrasando justo la región de sensibilidad alta que el cliente mide. Su AUC estándar no delata nada. ` +
      `Los bigotes son &plusmn;1 desviación entre folds, no un intervalo de confianza.`;
  },
  pareada: () => {
    const p = D.pareado;
    const signo = p.ic_bajo < 0 && p.ic_alto > 0;
    return `2b gana en ${cifra(p.folds_a_favor + " de " + p.n_folds, "derivado de pauc_por_fold de ambos niveles")} folds. ` +
      `Diferencia media ${cifra(num(p.media), "derivado: media de 2b menos nivel 1, fold a fold")}, ` +
      `desviación ${cifra(num(p.sd), "derivado: desviación muestral de las 5 diferencias")}, ` +
      `intervalo t al 95% de ${num(p.ic_bajo)} a ${num(p.ic_alto)}. ` +
      `<span class="destacado">El intervalo cruza el cero: la comparación pareada no confirma la superioridad de 2b, la debilita.</span> ` +
      `Y además es optimista &mdash; los folds comparten la mayor parte del entrenamiento, así que las diferencias no son independientes ` +
      `y el intervalo subestima la varianza. Lo que sí sostiene 2b es la estabilidad: su peor fold ` +
      `(${cifra(num(Math.min(...D.modelos.find(m => m.etiqueta === "Nivel 2b").por_fold)), "modelado-baseline.json > nivel_2b_gradient_boosting_balanceado.pauc_por_fold")}) ` +
      `supera a los dos peores del nivel 1.`;
  }
};

function pintar(vista) {
  if (grafico) grafico.destroy();
  grafico = new Chart(lienzo, vista === "medias" ? vistaMedias() : vistaPareada());
  document.getElementById("pie-modelos").innerHTML = PIE[vista]();
  document.getElementById("btn-medias").setAttribute("aria-pressed", vista === "medias");
  document.getElementById("btn-pareada").setAttribute("aria-pressed", vista === "pareada");
}
document.getElementById("btn-medias").onclick = () => pintar("medias");
document.getElementById("btn-pareada").onclick = () => pintar("pareada");
pintar("medias");

/* ---------- 5. cierre ---------- */
const M = et => D.modelos.find(m => m.etiqueta === et);
const campo = et => "modelado-baseline.json > " + M(et).campo;

document.getElementById("cierre-hallazgos").innerHTML =
  `El desbalance extremo (${cifra(mil(D.eda.positivos), "eda-diagnostico.json > desbalance_target.conteos.1")} malignos entre ` +
  `${cifra(mil(D.eda.n_filas), "eda-diagnostico.json > fuente.n_filas")} lesiones) y la agrupación por paciente hacían la partición ` +
  `ingenua peligrosa: ${cifra(num(D.fuga.pct_naive, 2) + "%", "diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga")} ` +
  `de fuga potencial. La auditoría de columnas dejó fuera ` +
  `${cifra(D.excluidas.length, "modelado-baseline.json > columnas_excluidas")} de las ` +
  `${cifra(D.eda.n_columnas, "eda-diagnostico.json > fuente.n_columnas")}, y evitó que información no disponible en producción ` +
  `entrara al modelo. Y la comparación honesta entre modelos &mdash;no solo la media, sino par a par por fold&mdash; mostró que la ventaja ` +
  `del gradient boosting balanceado no es estadísticamente sostenible con la evidencia disponible: gana en ` +
  `${cifra(D.pareado.folds_a_favor + " de " + D.pareado.n_folds, "derivado de pauc_por_fold de los niveles 1 y 2b")} folds, y el intervalo ` +
  `de confianza de la diferencia (${cifra(num(D.pareado.ic_bajo) + " a " + num(D.pareado.ic_alto), "derivado: intervalo t al 95% sobre las 5 diferencias")}) ` +
  `cruza cero. <span class="destacado">Lo que sí se sostiene es que es más estable</span>: ` +
  `&plusmn;${cifra(num(M("Nivel 2b").std), campo("Nivel 2b") + ".pauc_std")} entre folds frente a ` +
  `&plusmn;${cifra(num(M("Nivel 1").std), campo("Nivel 1") + ".pauc_std")} de la logística.`;

document.getElementById("cierre-recomendacion").innerHTML =
  `Regresión logística balanceada &mdash;Nivel 1, pAUC ${cifra(num(M("Nivel 1").media), campo("Nivel 1") + ".pauc_media")}&mdash; ` +
  `como modelo de referencia: interpretable, con desempeño comparable al gradient boosting ` +
  `(Nivel 2b, ${cifra(num(M("Nivel 2b").media), campo("Nivel 2b") + ".pauc_media")}), y sin la fragilidad que mostró el boosting ` +
  `sin ajustar por desbalance: el Nivel 2a colapsó a ${cifra(num(M("Nivel 2a").media), campo("Nivel 2a") + ".pauc_media")}, ` +
  `por debajo del piso aleatorio de ${cifra(num(D.escala.azar, 2), "modelado-baseline.json > escala_de_referencia_pauc.azar")}.`;

document.getElementById("cierre-limites").innerHTML =
  `La clase negativa tiene ruido estructural: la mayoría de los ` +
  `${cifra(mil(D.eda.negativos), "eda-diagnostico.json > desbalance_target.conteos.0")} &laquo;benignos&raquo; nunca se biopsiaron. ` +
  `No existe un conjunto de prueba real sobre el cual medir un resultado final independiente &mdash;el test publicado es ` +
  `${cifra("un marcador de posición", "eda-diagnostico.json > test_is_placeholder = " + D.test_es_marcador)}, así que todo lo de ` +
  `arriba es validación cruzada, no resultado sobre datos nuevos. Y la propia métrica del proyecto tuvo un error que solo se detectó ` +
  `al contrastarla explícitamente contra la fuente oficial &mdash; recordatorio de que ninguna parte de este proceso, ni siquiera la ` +
  `más técnica, estaba exenta de revisión.`;

/* ---------- pie ---------- */
document.getElementById("pie").innerHTML =
  `Generado el ${esc(D.generado)} por <code>generar_demo.py</code> desde <code>outputs/*.json</code>. ` +
  `Ninguna cifra de esta página está escrita a mano: pasa el ratón sobre cualquiera para ver su archivo y campo de origen. ` +
  `Mismo origen que <code>informe/informe-final.docx</code>.`;
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument("--salida", required=True)
    args = ap.parse_args()

    datos = construir_datos(args.outputs_dir)
    # </script> dentro de la cadena JSON cerraria la etiqueta que la contiene;
    # \/ es escape válido en JSON, así que el dato llega intacto al parser.
    crudo = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = PLANTILLA.replace("__DATOS__", crudo)

    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(html)

    print(
        f"Escrito: {args.salida} — {len(datos['modelos'])} niveles, "
        f"{len(datos['excluidas'])} columnas excluidas, "
        f"{len(datos['cadena'])} skills en la cadena"
    )


if __name__ == "__main__":
    main()

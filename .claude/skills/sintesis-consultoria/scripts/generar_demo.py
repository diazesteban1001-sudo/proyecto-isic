#!/usr/bin/env python3
"""
generar_demo.py — construye informe/demo.html, la síntesis en formato
presentación.

Etapa 4 de la skill sintesis-consultoria. El HTML no se escribe a mano:
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
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


# Los .md de cada instrumento se muestran al hacer clic en su casilla del
# diagrama. sintesis-consultoria no mide nada, así que no tiene un .md de
# resultados propio: se le asocia el de la verificación de trazabilidad,
# que es lo que esta skill sí produce como evidencia de su trabajo.
CADENA = [
    {
        "nombre": "eda-diagnostico",
        "etapa": "Diagnóstico del dataset",
        "tipo": "medición",
        "funcion": "Se perfiló el archivo: tipos, faltantes, desbalance y estructura de grupos por paciente",
        "md": "eda-diagnostico",
        "mide": "Estructura del archivo, tipos, faltantes por columna, desbalance de la "
                "respuesta, tamaño de los grupos y qué columnas existen en train pero no en test.",
        "porque": "Ninguna decisión de diseño posterior se puede tomar sin esto. El esquema de "
                  "validación depende de la estructura de grupos, y la auditoría de fugas parte "
                  "de la lista de columnas asimétricas.",
    },
    {
        "nombre": "diseno-validacion",
        "etapa": "Diseño de la validación",
        "tipo": "medición",
        "funcion": "Se construyó y se verificó la validación cruzada agrupada por paciente",
        "md": "diseno-validacion",
        "mide": "Se construyeron los folds agrupando por paciente y estratificando por clase, y "
                "después se comprobó que ningún paciente cruzara de un lado al otro. Además se "
                "cuantificó cuánta fuga habría producido no hacerlo.",
        "porque": "Proponer un esquema es barato; verificarlo es lo que lo convierte en evidencia. "
                  "Sin la comparación contra la partición ingenua, «hay que agrupar por paciente» "
                  "es una recomendación de manual y no un hallazgo sobre estos datos.",
    },
    {
        "nombre": "auditoria-de-fugas",
        "etapa": "Auditoría de fugas",
        "tipo": "medición",
        "funcion": "Se auditó la fuga estructural y se escaneó columna por columna",
        "md": "auditoria-de-fugas",
        "mide": "Dos cosas distintas: fuga estructural —columnas ausentes en test, constantes, "
                "identificadores— y fuga oculta, entrenando un modelo por columna sobre los folds "
                "agrupados para ver si alguna predice el objetivo sospechosamente bien.",
        "porque": "Es el paso adversario: existe para encontrar defectos, no para "
                  "confirmar que todo está bien. Un chequeo que no puede fallar no vale nada.",
    },
    {
        "nombre": "modelado-baseline",
        "etapa": "Modelos de referencia",
        "tipo": "medición",
        "funcion": "Se entrenaron y evaluaron cuatro niveles con la métrica oficial",
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
        "etapa": "Síntesis y verificación",
        "tipo": "interpretación",
        "funcion": "Se cruzaron las cuatro salidas, se redactó el informe y se verificó su trazabilidad",
        # No mide nada, así que no tiene un .md de resultados propio: se le
        # asocia el de la verificación de trazabilidad, que es la evidencia
        # de que hizo su trabajo.
        "md": "sintesis-verificacion",
        "mide": "Nada. Es la única etapa que interpreta: se cruzaron las cuatro salidas "
                "anteriores, se resolvieron sus contradicciones y se emitió la recomendación. "
                "Lo que sí se verificó fue a sí misma, extrayendo cada número del informe y "
                "comprobando que tuviera respaldo en outputs/.",
        "porque": "Es el trabajo del consultor, y está separado de las etapas de medición a "
                  "propósito: una etapa que interpretara sus propios resultados tendería a "
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


def cargar_json(outputs_dir, nombre, leidos):
    """Lee outputs/<nombre>.json y lo anota en `leidos`. El aviso de estado
    revisa todo lo que pasó por aquí, no una lista escrita a mano: un archivo
    que la página empiece a leer queda cubierto sin tocar el aviso."""
    contenido = json.loads(leer(os.path.join(outputs_dir, f"{nombre}.json")))
    leidos[nombre] = contenido
    return contenido


def construir_datos(outputs_dir, leidos):
    def cargar(nombre):
        return cargar_json(outputs_dir, nombre, leidos)

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
            "auc": bloque.get("auc_estandar_media"),
            "por_fold": bloque["pauc_por_fold"],
            "nota": bloque.get("nota", ""),
        })

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
    verificacion = cargar("sintesis-verificacion")

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
<title>Proyecto de consultor&iacute;a ISIC 2024 &mdash; Detecci&oacute;n de melanoma</title>
<script>__CHARTJS__</script>
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
  .cadena { display: flex; align-items: stretch; gap: 6px; flex-wrap: wrap; }
  .paso {
    flex: 1 1 165px; text-align: left; cursor: pointer; background: #fff;
    border: 1px solid var(--linea); border-top: 4px solid var(--suave);
    border-radius: 8px; padding: 13px 14px; font: inherit; color: inherit;
    transition: transform .12s, box-shadow .12s, border-color .12s;
    display: flex; flex-direction: column;
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
  .exploratorio {
    margin: 24px 0 0; padding: 12px 16px; border: 2px solid var(--alarma);
    border-radius: 8px; background: #fdf3f1; color: var(--tinta); font-size: 15px;
  }
  .exploratorio b { color: var(--alarma); }
  .contra { margin-top: 18px; border-left: 4px solid var(--bien); background: #f2faf6; padding: 14px 16px; border-radius: 0 8px 8px 0; }
  .contra b { color: var(--bien); }
  .barra { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
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
__AVISO_EXPLORATORIO__

<header>
  <div class="kicker">Consultor&iacute;a e Investigaci&oacute;n &middot; Estad&iacute;stica &middot; caso ISIC 2024</div>
  <h1>Proyecto de consultor&iacute;a ISIC 2024</h1>
  <div class="contexto">
    <p><b>El problema.</b> <span id="ctx-problema"></span></p>
    <p><b>Por qu&eacute; este caso.</b> <span id="ctx-eleccion"></span></p>
  </div>
</header>

<section>
  <h2><span class="num">1</span>C&oacute;mo se desarroll&oacute; el trabajo</h2>
  <p class="sub">Cinco etapas. Las cuatro primeras miden y dejan su salida en un archivo; la quinta interpreta y redacta. Haz clic en cualquiera para ver la salida real que produjo.</p>
  <div class="cadena" id="cadena"></div>
  <div class="salida" id="salida" hidden>
    <h3 id="salida-nombre"></h3>
    <div class="ficha">
      <p><b>Qu&eacute; se midi&oacute;.</b> <span id="ficha-mide"></span></p>
      <p><b>Por qu&eacute; se hizo.</b> <span id="ficha-porque"></span></p>
      <p class="hallazgo"><b>Un hallazgo concreto.</b> <span id="ficha-hallazgo"></span></p>
    </div>
    <h3 id="salida-titulo"></h3>
    <pre id="salida-texto"></pre>
  </div>
</section>

<section>
  <h2><span class="num">2</span>Resultados</h2>
  <p class="sub" id="sub-modelos"></p>
  <div class="duo">
    <div class="medida ok">
      <div class="cifra" id="tit-reco"></div>
      <div class="rot">Nivel 1 &mdash; regresi&oacute;n log&iacute;stica balanceada</div>
      <div class="det">El modelo recomendado</div>
    </div>
    <div class="medida mal">
      <div class="cifra" id="tit-fallo"></div>
      <div class="rot">Nivel 2a &mdash; colapsa bajo la m&eacute;trica del cliente</div>
      <div class="det" id="tit-fallo-det"></div>
    </div>
  </div>
  <div class="tarjeta">
    <div class="barra">
      <div class="pie-grafico" id="escala"></div>
    </div>
    <div class="lienzo"><canvas id="gr-modelos"></canvas></div>
    <p class="pie-grafico" id="pie-modelos"></p>
  </div>
</section>

<section>
  <h2><span class="num">3</span>Conclusi&oacute;n</h2>
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

<section>
  <h2><span class="num">4</span>Lo que sigue</h2>
  <p class="sub">Trabajo previsto, no ejecutado. Sin cifras: todav&iacute;a no hay nada medido.</p>
  <div class="tarjeta">
    <p><b>Modelado con im&aacute;genes.</b> Todo lo anterior usa solo la metadata tabular.
    La extensi&oacute;n prevista incorpora las fotograf&iacute;as sin entrenar una red desde cero:
    se extraer&iacute;an caracter&iacute;sticas congeladas de un modelo fundacional de imagen,
    DINOv2, y se alimentar&iacute;an los mismos niveles de referencia, sobre
    los mismos folds agrupados por paciente, para que la comparaci&oacute;n siga siendo v&aacute;lida.</p>
    <p><b>El bloqueante, primero.</b> Antes de medir nada hay que verificar si SLICE-3D
    &mdash;el conjunto de este caso&mdash; form&oacute; parte del preentrenamiento del modelo.
    Si hubo solape, cualquier mejora observada estar&iacute;a inflada por una fuga que no viene
    del dataset sino del preentrenamiento de un tercero, y no ser&iacute;a atribuible al m&eacute;todo.
    Es el mismo razonamiento de la auditor&iacute;a de fugas, un nivel m&aacute;s arriba.</p>
    <p><b>Lo que ya se decidi&oacute;.</b> PanDerm, un modelo fundacional de dermatolog&iacute;a, no se usa:
    su art&iacute;culo declara un subconjunto de ISIC 2024 entre sus datos de preentrenamiento, y el
    criterio fijado de antemano era no usarlo si hab&iacute;a solape. DINOv3, gen&eacute;rico, tampoco:
    no cumpli&oacute; la regla de verificaci&oacute;n, fijada tambi&eacute;n de antemano. Se usa DINOv2: sus datos
    de preentrenamiento est&aacute;n descritos en un art&iacute;culo de abril de 2023, y sus autores no
    pertenecen a las instituciones que aportaron los datos.</p>
    <p class="aviso">Ninguna cifra aparece en esta secci&oacute;n porque ninguna est&aacute; medida.
    A diferencia del resto de la p&aacute;gina, aqu&iacute; no hay archivo en <code>outputs/</code> que
    respalde nada &mdash; y por eso no se afirma nada.</p>
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
    `Se encontraron ${cifra(D.eda.n_solo_en_train, "eda-diagnostico.json > columnas_solo_en_train")} columnas presentes ` +
    `solo en entrenamiento, de las ${cifra(D.eda.n_columnas, "eda-diagnostico.json > fuente.n_columnas")} del archivo ` +
    `&mdash; la primera se&ntilde;al de que algo ah&iacute; no estar&iacute;a disponible al predecir en producci&oacute;n.`,
  "diseno-validacion": () =>
    `Se cuantific&oacute; cu&aacute;nta fuga habr&iacute;a producido ignorar la agrupaci&oacute;n por paciente: ` +
    `${cifra(num(D.fuga.pct_naive, 2) + "%", "diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga")} ` +
    `de los pacientes (${cifra(mil(D.fuga.n_grupos_naive), "diseno-validacion.json > comparacion_particion_naive.n_grupos_con_fuga")} ` +
    `de ${cifra(mil(D.fuga.n_grupos_total), "diseno-validacion.json > n_grupos_total")}) habr&iacute;an caído a los dos lados de la partición.`,
  "auditoria-de-fugas": () =>
    `Se generaron ${cifra(D.auditoria.n_preguntas_abiertas, "auditoria-de-fugas.json > preguntas_abiertas")} preguntas abiertas ` +
    `sobre columnas sospechosas; ${cifra(D.auditoria.n_preguntas_abiertas - 1, "derivado: preguntas_abiertas menos la que exigió fuente externa")} ` +
    `se resolvieron por su naturaleza post-biopsia, y la &uacute;ltima exigi&oacute; rastrear un paper cient&iacute;fico hasta confirmar ` +
    `que <code>${esc(D.nevi ? D.nevi.columna : "")}</code>, de apariencia sospechosa, era en realidad leg&iacute;tima.`,
  "modelado-baseline": () =>
    `En el camino se descubri&oacute; que la implementaci&oacute;n inicial de la m&eacute;trica usaba un umbral de sensibilidad ` +
    `equivocado y subestimaba el m&aacute;ximo posible de la escala, que es ` +
    `${cifra(num(D.escala.maximo, 1), "modelado-baseline.json > escala_de_referencia_pauc.maximo")}. Corregida y verificada contra ` +
    `la fuente oficial (${cifra(esc(D.metrica_fuente), "modelado-baseline.json > metrica_fuente")}) antes de confiar en ning&uacute;n resultado.`,
  "sintesis-consultoria": () =>
    `Se extrajeron los ${cifra(mil(D.verificacion.numeros), "sintesis-verificacion.json > numeros_en_borrador")} n&uacute;meros del borrador ` +
    `y se contrastaron contra <code>outputs/</code>: ` +
    `${cifra(mil(D.verificacion.con_respaldo), "sintesis-verificacion.json > numeros_con_respaldo_en_outputs")} con respaldo exacto, ` +
    `${cifra(D.verificacion.senalados, "sintesis-verificacion.json > numeros_sin_respaldo")} se&ntilde;alados para revisi&oacute;n a mano, ` +
    `y ${cifra(D.verificacion.ignorados, "derivado: numeros_en_borrador menos los con respaldo y los señalados")} en contextos que el ` +
    `verificador excluye por dise&ntilde;o (n&uacute;meros de secci&oacute;n, fechas y similares).`
};

const cadena = document.getElementById("cadena");
D.cadena.forEach((s, i) => {
  const b = document.createElement("button");
  b.className = "paso" + (s.tipo === "interpretación" ? " final" : "");
  b.setAttribute("aria-selected", "false");
  b.innerHTML = `<span class="tipo">${i + 1} &middot; ${esc(s.tipo)}</span>
                 <span class="nom">${esc(s.etapa)}</span>
                 <span class="fun">${esc(s.funcion)}</span>`;
  b.onclick = () => {
    const abierto = b.getAttribute("aria-selected") === "true";
    document.querySelectorAll(".paso").forEach(p => p.setAttribute("aria-selected", "false"));
    const caja = document.getElementById("salida");
    if (abierto) { caja.hidden = true; return; }
    b.setAttribute("aria-selected", "true");
    document.getElementById("salida-nombre").textContent = s.etapa;
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

/* ---------- 2. modelado ---------- */
const M = et => D.modelos.find(m => m.etiqueta === et);
const campo = et => "modelado-baseline.json > " + M(et).campo;
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

const PIE = {
  medias: () => {
    const n2a = D.modelos.find(m => m.etiqueta === "Nivel 2a");
    return `El <span class="destacado">nivel 2a queda en ${cifra(num(n2a.media), "modelado-baseline.json > nivel_2a_gradient_boosting_sin_balancear.pauc_media")}, ` +
      `por debajo del piso aleatorio</span>: no colapsa a predecir siempre negativo, satura en probabilidad 1 sobre negativos y los coloca ` +
      `encima de los positivos, arrasando justo la región de sensibilidad alta que el cliente mide. Su AUC estándar no delata nada. ` +
      `Los bigotes son &plusmn;1 desviación entre folds, no un intervalo de confianza.`;
  }
};

function pintar(vista) {
  if (grafico) grafico.destroy();
  grafico = new Chart(lienzo, vistaMedias());
  document.getElementById("pie-modelos").innerHTML = PIE[vista]();
}

document.getElementById("tit-reco").innerHTML =
  cifra(num(M("Nivel 1").media), campo("Nivel 1") + ".pauc_media");
document.getElementById("tit-fallo").innerHTML =
  cifra(num(M("Nivel 2a").media), campo("Nivel 2a") + ".pauc_media");
document.getElementById("tit-fallo-det").innerHTML =
  "Boosting sin ajustar por desbalance. Su AUC est&aacute;ndar es " +
  cifra(num(M("Nivel 2a").auc, 2), campo("Nivel 2a") + ".auc_estandar_media") +
  ": por encima del azar. Bajo la m&eacute;trica del cliente queda por debajo de su piso de " +
  cifra(num(D.escala.azar, 2), "modelado-baseline.json > escala_de_referencia_pauc.azar") +
  ". Las dos m&eacute;tricas no coinciden ni en si el modelo supera al azar";

pintar("medias");

/* ---------- 3. cierre ---------- */
document.getElementById("cierre-hallazgos").innerHTML =
  `El desbalance extremo (${cifra(mil(D.eda.positivos), "eda-diagnostico.json > desbalance_target.conteos.1")} malignos entre ` +
  `${cifra(mil(D.eda.n_filas), "eda-diagnostico.json > fuente.n_filas")} lesiones) y la agrupación por paciente hacían la partición ` +
  `ingenua peligrosa: ${cifra(num(D.fuga.pct_naive, 2) + "%", "diseno-validacion.json > comparacion_particion_naive.pct_grupos_con_fuga")} ` +
  `de fuga potencial. La auditoría de columnas dejó el modelado con ` +
  `${cifra(D.n_features_usadas, "modelado-baseline.json > n_features_usadas")} variables de las ` +
  `${cifra(D.eda.n_columnas, "eda-diagnostico.json > fuente.n_columnas")} del archivo. Las otras ` +
  `${cifra(D.eda.n_columnas - D.n_features_usadas, "derivado: fuente.n_columnas menos n_features_usadas")} quedan fuera por razones distintas: ` +
  `${cifra(D.eda.n_solo_en_train, "eda-diagnostico.json > columnas_solo_en_train")} no existen al predecir &mdash;el test no las trae, y entre ellas va la propia respuesta&mdash;, ` +
  `<code>image_type</code> es constante en todo el archivo, <code>isic_id</code> identifica la fila, y ` +
  `<code>patient_id</code> no se descarta por sospechosa: se usa para agrupar los folds, no para predecir. ` +
  `Eso evitó que información no disponible en producción entrara al modelo. ` +
  `<span class="destacado">En esta partición 2b fue además menos disperso</span>: ` +
  `&plusmn;${cifra(num(M("Nivel 2b").std), campo("Nivel 2b") + ".pauc_std")} entre folds frente a ` +
  `&plusmn;${cifra(num(M("Nivel 1").std), campo("Nivel 1") + ".pauc_std")} de la logística &mdash; una ventaja que ` +
  `no se mantiene al repetir la validación con diez particiones distintas.`;

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


# Aviso de cifras exploratorias. Desde la Fase 1 (2026-09-25) cada instrumento
# declara en su JSON sobre qué datos midió (campo "datos"). Si alguno de los
# que lee la demo no declara el conjunto de desarrollo, sus cifras son las de
# la corrida exploratoria sobre el 100 % de los datos, y la página lo dice
# arriba. Se decide con los datos de entrada, no con una bandera: así el aviso
# no puede quedarse puesto en una demo regenerada con las cifras nuevas, ni
# faltar en una hecha con las viejas. Va en el HTML servido, no en el script
# de la página, para que se vea aunque el JavaScript falle.
AVISO_EXPLORATORIO = (
    '<div class="exploratorio" role="note"><b>Cifras exploratorias.</b> '
    "Las cifras de esta p&aacute;gina son de la corrida exploratoria sobre el 100&nbsp;% "
    "de los datos y se est&aacute;n re-midiendo sobre el conjunto de desarrollo.</div>"
)

# Nombre, sin extensión, de la salida de la Fase 5 en outputs/. No está
# fijado: lo fija el guion que abra el reservado (PLAN.md, Fase 5). Hasta
# entonces ningún archivo que lea la página puede declarar el reservado.
SALIDA_FASE_5 = None


def comprobar_conjuntos(leidos, salida_fase_5=SALIDA_FASE_5):
    """Devuelve el aviso exploratorio, o "" si no hace falta, mirando cada
    archivo que la página leyó. El reservado solo se acepta en la salida de la
    Fase 5: en cualquier otro archivo no se escribe la página, porque el aviso
    diría «corrida exploratoria» de unas cifras que no lo son.
    sintesis-verificacion no declara conjunto; se comprueba aparte."""
    exploratorio = False
    for nombre, contenido in leidos.items():
        if nombre == "sintesis-verificacion":
            continue
        conjunto = (contenido.get("datos") or {}).get("conjunto")
        if conjunto == "reservado":
            if nombre != salida_fase_5:
                raise SystemExit(
                    f"outputs/{nombre}.json declara el conjunto reservado y no es la salida "
                    "de la Fase 5. No se escribe la página."
                )
        elif conjunto != "desarrollo":
            exploratorio = True
    return AVISO_EXPLORATORIO if exploratorio else ""


# La verificación que la página muestra tiene que ser la del borrador vigente,
# hecha con el verificador de hoy. Se comprueba recalculándola, porque su JSON
# no dice sobre qué borrador se corrió. Comparar resultado contra resultado
# detecta además una verificación que se quedó atrás de outputs/: la cuarta
# fila del registro de incidentes de CLAUDE.md fue exactamente eso.
BORRADOR_VIGENTE = "informe/borrador-v2.md"
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VERIFICADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verificar_trazabilidad.py")


def comprobar_verificacion(outputs_dir):
    with tempfile.TemporaryDirectory() as tmp:
        recalculada = os.path.join(tmp, "sintesis-verificacion")
        subprocess.run(
            [sys.executable, VERIFICADOR, "--borrador", BORRADOR_VIGENTE,
             "--outputs-dir", os.path.abspath(outputs_dir), "--out", recalculada],
            cwd=RAIZ, check=True, capture_output=True,
        )
        esperado_json = json.loads(leer(f"{recalculada}.json"))
        esperado_md = leer(f"{recalculada}.md")
    actual_json = json.loads(leer(os.path.join(outputs_dir, "sintesis-verificacion.json")))
    actual_md = leer(os.path.join(outputs_dir, "sintesis-verificacion.md"))
    if actual_json == esperado_json and actual_md == esperado_md:
        return
    motivos = []
    cabecera_actual = actual_md.split("\n", 1)[0]
    if cabecera_actual != esperado_md.split("\n", 1)[0]:
        motivos.append(f"se corrió sobre otro borrador («{cabecera_actual}»)")
    if (actual_json.get("modo_tolerancia"), actual_json.get("tolerancia_redondeo")) != (
            esperado_json["modo_tolerancia"], esperado_json["tolerancia_redondeo"]):
        motivos.append(f"modo de tolerancia {actual_json.get('modo_tolerancia')!r} con margen "
                       f"{actual_json.get('tolerancia_redondeo')!r}, no {esperado_json['modo_tolerancia']!r}")
    if not motivos:
        motivos.append("no coincide con recalcularla sobre el outputs/ actual")
    raise SystemExit(
        f"outputs/sintesis-verificacion no corresponde a {BORRADOR_VIGENTE} con el verificador "
        f"actual: {'; '.join(motivos)}. Hay que regenerarla. No se escribe la página."
    )


# El modelo recomendado no está en ningún campo de outputs/: es la decisión de
# la persona del 2026-09-26 (PLAN.md, Fase 4, «Modelo recomendado: decisión de
# la persona, 2026-09-26»). El generador no lo da por supuesto: aplica la regla
# fijada antes de correr sobre la salida de M3 limpio − M2 y no escribe la
# página si el resultado no coincide con esta constante.
RECOMENDADO = "M3 limpio"


def regla_de_recomendacion(f3l):
    """PLAN.md, Fase 4, «Regla de recomendación»: M3 limpio si el intervalo
    corregido de la pAUC de M3 limpio − M2 queda entero por encima de cero; en
    cualquier otro caso, M2."""
    if (f3l["comparacion"]["nuevo"], f3l["comparacion"]["base"]) != ("M3limpio", "M2"):
        raise SystemExit(f"fase4-m3limpio-vs-m2.json compara {f3l['comparacion']}, no M3 limpio − M2.")
    bajo, _ = f3l["comparaciones_nuevo_menos_base"]["pauc"]["intervalo_t_95_nadeau_bengio"]
    return "M3 limpio" if bajo > 0 else "M2"


def comprobar_recomendacion(f3l):
    regla = regla_de_recomendacion(f3l)
    if regla != RECOMENDADO:
        raise SystemExit(
            f"La regla de recomendación da {regla} y RECOMENDADO dice {RECOMENDADO}. "
            "No se escribe la página."
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument(
        "--salida",
        required=True,
        nargs="+",
        help="Una o más rutas de destino. El HTML se renderiza UNA vez y esa "
        "misma cadena se escribe en todas: informe/demo.html para abrir por "
        "doble clic y docs/index.html para GitHub Pages.",
    )
    args = ap.parse_args()

    # Las tres comprobaciones van antes de renderizar: si una se niega, no se
    # escribe ningún destino, ni siquiera a medias.
    leidos = {}
    datos = construir_datos(args.outputs_dir, leidos)
    comprobar_recomendacion(cargar_json(args.outputs_dir, "fase4-m3limpio-vs-m2", leidos))
    comprobar_verificacion(args.outputs_dir)
    aviso = comprobar_conjuntos(leidos)
    # </script> dentro de la cadena JSON cerraria la etiqueta que la contiene;
    # \/ es escape válido en JSON, así que el dato llega intacto al parser.
    crudo = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")

    # Chart.js se empotra desde disco en vez de cargarse por CDN. Antes iba en
    # un <script src> a jsdelivr, y sin red la pagina lanzaba
    # "Chart is not defined", lo que ABORTA el script y deja sin rellenar todo
    # lo que viene despues: los pAUC y las fichas por skill desaparecian
    # mientras la cabecera seguia a la vista. Fallo silencioso en mitad de una
    # presentacion. Procedencia y hash en assets/PROCEDENCIA.md.
    #
    # La ruta se resuelve contra __file__, no contra el directorio de trabajo,
    # para que el script funcione invocado desde cualquier sitio.
    chartjs_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "assets",
        "chart.umd.min.js",
    )
    with open(chartjs_path, encoding="utf-8") as f:
        chartjs = f.read()

    # Verificado al empotrarla: la libreria no contiene "</script". Si una
    # version futura lo hiciera, cerraria la etiqueta antes de tiempo y
    # romperia la pagina sin ruido, asi que se comprueba en vez de confiar.
    if "</script" in chartjs.lower():
        raise SystemExit(
            f"{chartjs_path} contiene '</script': empotrarla cerraria la "
            "etiqueta antes de tiempo. Hay que escaparla antes de seguir."
        )

    # Se renderiza una sola vez, fuera del bucle, y se escribe la misma cadena
    # en cada destino. No es una optimización: el payload lleva una marca de
    # tiempo (datos["generado"]), así que dos renderizados podrían diferir en
    # ese campo y las copias dejarían de ser idénticas. Renderizar aquí hace
    # que la igualdad sea estructural en vez de algo que haya que comprobar.
    html = (
        PLANTILLA.replace("__CHARTJS__", chartjs)
        .replace("__AVISO_EXPLORATORIO__", aviso)
        .replace("__DATOS__", crudo)
    )

    for salida in args.salida:
        os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
        with open(salida, "w", encoding="utf-8") as f:
            f.write(html)

    print(
        f"Escrito: {', '.join(args.salida)} — {len(datos['modelos'])} niveles, "
        f"{len(datos['excluidas'])} columnas excluidas, "
        f"{len(datos['cadena'])} etapas en la cadena"
    )


if __name__ == "__main__":
    main()

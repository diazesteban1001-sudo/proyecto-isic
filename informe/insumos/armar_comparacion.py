"""Arma informe/insumos/estado-del-arte-comparacion.md desde los JSON de citas
de informe/insumos/citas/. Ninguna cita se teclea aquí: se toma del JSON por
clave, campo e índice, y se vuelve a comprobar contra su archivo.

Uso, desde cualquier directorio:
    python3 informe/insumos/armar_comparacion.py
Solo biblioteca estándar. Las citas de fichas con texto completo LOCAL se
comprueban contra referencias/_texto-completo/, que no se versiona: en un clon
nuevo hay que volver a obtener esos textos antes de correrlo."""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
SALIDA = os.path.join(RAIZ, "informe/insumos/estado-del-arte-comparacion.md")

ORDEN = ["kurtansky-2024", "kurtansky-2025", "marchetti-2023", "kaggle-2024", "mcclish-1989", "walter-2005",
         "yang-2019", "saeb-2017", "little-2017", "kapoor-2023", "cassidy-2022", "saenz-2018",
         "barrera-valencia-2024", "mejia-posada-2024", "rios-duarte-2024", "jojoa-acosta-2021", "jojoa-2022"]
J = {k: json.load(open(os.path.join(AQUI, "citas", f"{k}.json"), encoding="utf-8")) for k in ORDEN}
cache = {}


def lineas(ruta):
    if ruta not in cache:
        cache[ruta] = open(os.path.join(RAIZ, ruta), encoding="utf-8").read().split("\n")
    return cache[ruta]


def norm(t):
    t = re.sub(r"(^|\s)>\s", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def comprobar(archivo, ini, fin, texto):
    tramo = " ".join(lineas(archivo)[ini - 1:fin])
    if texto not in tramo and norm(texto) not in norm(tramo):
        raise SystemExit(f"CITA QUE NO ESTÁ: {archivo}:{ini}-{fin}: {texto[:80]}")


def loc(c):
    a = c["archivo"]
    ini, fin = int(c["linea_ini"]), int(c["linea_fin"])
    return f"`{a}`, l. {ini}" if ini == fin else f"`{a}`, l. {ini}–{fin}"


def mostrar(texto, tabla=False):
    t = norm(texto)
    if tabla:
        t = t.replace("|", "\\|")
    return t


def cita(c, tabla=False, campo="cita"):
    comprobar(c["archivo"], int(c["linea_ini"]), int(c["linea_fin"]), c[campo])
    return f"«{mostrar(c[campo], tabla)}» ({loc(c)})"


def q(clave, campo, i=0, tabla=False):
    return cita(J[clave]["celdas"][campo][i], tabla)


def qc(clave, i):
    return cita(J[clave]["contrastes"][i])


# --- citas del borrador y campos de outputs, comprobados igual ---
BORRADOR = "informe/borrador-v2.md"


def qb(ini, fin, texto):
    comprobar(BORRADOR, ini, fin, texto)
    return f"«{texto}» (`{BORRADOR}`, l. {ini}–{fin})" if ini != fin else f"«{texto}» (`{BORRADOR}`, l. {ini})"


def qo(archivo, ruta):
    d = json.load(open(os.path.join(RAIZ, "outputs", archivo), encoding="utf-8"))
    v = d
    for p in ruta.split("."):
        v = v[int(p)] if isinstance(v, list) else v[p]
    return f"`{archivo} > {ruta}` = {json.dumps(v, ensure_ascii=False)}"


# --- datos de cada fila ---
REF_ANTEPROYECTO = {
    "kurtansky-2024": "Kurtansky, N. R., D’Alessandro, B. M.",
    "kurtansky-2025": "Kurtansky, N. R., Gillis, M. C., Codella",
    "marchetti-2023": "Marchetti, M. A., Nazir, Z. H.",
    "kaggle-2024": "Kurtansky, N., Rotemberg, V., Gillis",
    "mcclish-1989": "McClish, D. K. (1989)",
    "walter-2005": "Walter, S. D. (2005)",
    "yang-2019": "Yang, H., Lu, K., Lyu, X., & Hu, F. (2019)",
    "saeb-2017": "Saeb, S., Lonini, L., Jayaraman",
    "little-2017": "Little, M. A., Varoquaux, G., Saeb",
    "kapoor-2023": "Kapoor, S., & Narayanan, A. (2023)",
    "cassidy-2022": "Cassidy, B., Kendrick, C., Brodzicki",
    "saenz-2018": "Sáenz, J. P., Novoa, M. P.",
    "barrera-valencia-2024": "Barrera-Valencia, C., & Perea-Flórez",
    "mejia-posada-2024": "Mejía Posada, M. I., Gutiérrez Gómez",
    "rios-duarte-2024": "Rios-Duarte, J. A., Diaz-Valencia",
    "jojoa-acosta-2021": "Jojoa Acosta, M. F., Caballero Tovar",
    "jojoa-2022": "Jojoa, M., Garcia-Zapirain, B., & Percybrooks",
}
NOMBRE = {
    "kurtansky-2024": "Kurtansky, D’Alessandro et al. (2024)", "kurtansky-2025": "Kurtansky et al. (2025)",
    "marchetti-2023": "Marchetti et al. (2023)", "kaggle-2024": "Kurtansky, Rotemberg et al. (2024), el reto en Kaggle",
    "mcclish-1989": "McClish (1989)", "walter-2005": "Walter (2005)", "yang-2019": "Yang et al. (2019)",
    "saeb-2017": "Saeb et al. (2017)", "little-2017": "Little et al. (2017)", "kapoor-2023": "Kapoor y Narayanan (2023)",
    "cassidy-2022": "Cassidy et al. (2022)", "saenz-2018": "Sáenz et al. (2018)",
    "barrera-valencia-2024": "Barrera-Valencia y Perea-Flórez (2024)", "mejia-posada-2024": "Mejía Posada et al. (2024)",
    "rios-duarte-2024": "Rios-Duarte et al. (2024)", "jojoa-acosta-2021": "Jojoa Acosta et al. (2021)",
    "jojoa-2022": "Jojoa et al. (2022)",
}
ARCHIVO = {
    "kurtansky-2024": ["referencias/kurtansky-2024-slice3d-descriptor.md"],
    "kurtansky-2025": ["referencias/kurtansky-2025-triaje-automatizado-tbp.md"],
    "marchetti-2023": ["referencias/marchetti-2023-modelo-morfologico-3dtbp.md"],
    "kaggle-2024": ["referencias/kaggle-evaluation.md", "referencias/kaggle-rules.md"],
    "mcclish-1989": ["referencias/mcclish-1989-pauc-original.md"],
    "walter-2005": ["referencias/walter-2005-pauc-sroc-en-metaanalisis.md"],
    "yang-2019": ["referencias/yang-2019-two-way-partial-auc.md"],
    "saeb-2017": ["referencias/saeb-2017-validacion-por-sujeto.md"],
    "little-2017": ["referencias/little-2017-perspectivas-sobre-saeb.md"],
    "kapoor-2023": ["referencias/kapoor-2023-fuga-y-reproducibilidad.md"],
    "cassidy-2022": ["referencias/cassidy-2022-duplicados-isic.md"],
    "saenz-2018": ["referencias/saenz-2018-app-teledermatologia-colombia.md"],
    "barrera-valencia-2024": ["referencias/barrera-valencia-2024-costos-teledermatologia.md"],
    "mejia-posada-2024": ["referencias/mejia-posada-2024-mapeo-corporal-medellin.md"],
    "rios-duarte-2024": ["referencias/rios-duarte-2024-cnn-melanoma-uniandes.md"],
    "jojoa-acosta-2021": ["referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md"],
    "jojoa-2022": ["referencias/jojoa-2022-redes-complejas-melanoma.md"],
}
# Acceso: (categoría, archivo, línea de la cabecera que lo declara, texto literal de esa línea a citar)
ACCESO = {
    "kurtansky-2024": ("texto completo versionado", "referencias/kurtansky-2024-slice3d-descriptor.md", 18, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "kurtansky-2025": ("texto completo versionado", "referencias/kurtansky-2025-triaje-automatizado-tbp.md", 16, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "marchetti-2023": ("solo resumen", "referencias/marchetti-2023-modelo-morfologico-3dtbp.md", 6, "Solo hay acceso al resumen"),
    "kaggle-2024": ("ficha + LOCAL", "referencias/kaggle-rules.md", 16, "**Texto completo:** en local, `referencias/_texto-completo/kaggle-rules.md`."),
    "mcclish-1989": ("solo resumen", "referencias/mcclish-1989-pauc-original.md", 13, "**Solo hay acceso al resumen**"),
    "walter-2005": ("solo resumen", "referencias/walter-2005-pauc-sroc-en-metaanalisis.md", 22, "**Solo hay acceso al resumen**"),
    "yang-2019": ("ficha + LOCAL", "referencias/yang-2019-two-way-partial-auc.md", 30, "**Texto completo:** en local, `referencias/_texto-completo/yang-arxiv-1508.00298v3.pdf`"),
    "saeb-2017": ("texto completo versionado", "referencias/saeb-2017-validacion-por-sujeto.md", 13, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "little-2017": ("texto completo versionado", "referencias/little-2017-perspectivas-sobre-saeb.md", 14, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "kapoor-2023": ("texto completo versionado", "referencias/kapoor-2023-fuga-y-reproducibilidad.md", 13, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "cassidy-2022": ("texto completo versionado", "referencias/cassidy-2022-duplicados-isic.md", 20, "**LICENCIA: CC BY-NC-ND 4.0 → TEXTO COMPLETO.**"),
    "saenz-2018": ("texto completo versionado", "referencias/saenz-2018-app-teledermatologia-colombia.md", 19, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "barrera-valencia-2024": ("solo resumen", "referencias/barrera-valencia-2024-costos-teledermatologia.md", 48, "resumen. No se leyeron el método de costeo, las tablas ni las limitaciones."),
    "mejia-posada-2024": ("texto completo versionado", "referencias/mejia-posada-2024-mapeo-corporal-medellin.md", 23, "**LICENCIA: CC BY-NC-ND 4.0 → TEXTO COMPLETO."),
    "rios-duarte-2024": ("texto completo versionado", "referencias/rios-duarte-2024-cnn-melanoma-uniandes.md", 19, "**LICENCIA: CC BY-NC-ND 4.0 → TEXTO COMPLETO.**"),
    "jojoa-acosta-2021": ("texto completo versionado", "referencias/jojoa-acosta-2021-aprendizaje-profundo-melanoma.md", 18, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
    "jojoa-2022": ("texto completo versionado", "referencias/jojoa-2022-redes-complejas-melanoma.md", 18, "**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.**"),
}
# Celdas donde la cita da la proporción de clases, no cómo se trata el desbalance.
SOLO_PROPORCION = {"kurtansky-2024"}
MAX_TABLA = 700


def linea_anteproyecto(prefijo):
    for i, l in enumerate(lineas("informe/anteproyecto.md"), 1):
        if l.startswith(prefijo) and i > 680:
            return i
    raise SystemExit(f"no está en la bibliografía del anteproyecto: {prefijo}")


def celda_tabla(clave, campos):
    partes = []
    for campo, etiqueta in campos:
        v = J[clave]["celdas"][campo]
        pre = f"*{etiqueta}:* " if etiqueta else ""
        if isinstance(v, dict):
            partes.append(f"{pre}**no lo dice**")
            continue
        elegida = next((c for c in v if len(norm(c["cita"])) <= MAX_TABLA), None)
        if elegida is None:
            partes.append(f"{pre}cita larga, en el anexo ({loc(v[0])})")
            continue
        texto = cita(elegida, tabla=True)
        if campo == "desbalance" and clave in SOLO_PROPORCION:
            texto = "no dice cómo lo trata; la proporción: " + texto
        partes.append(pre + texto)
    return "<br>".join(partes)


def fila(clave):
    n = linea_anteproyecto(REF_ANTEPROYECTO[clave])
    trabajo = (f"**{NOMBRE[clave]}**<br>" + ", ".join(f"`{a}`" for a in ARCHIVO[clave])
               + f"<br>bibliografía del anteproyecto, l. {n}")
    cat, arch, lin, txt = ACCESO[clave]
    comprobar(arch, lin, lin, txt)
    acceso = f"**{cat}**: «{txt.replace('|', chr(92) + '|')}» (`{arch}`, l. {lin})"
    cols = [
        trabajo,
        celda_tabla(clave, [("tipo", "")]),
        celda_tabla(clave, [("datos_origen", "origen"), ("datos_tamano", "tamaño"), ("datos_pais", "país"), ("datos_unidad", "unidad")]),
        celda_tabla(clave, [("validacion", "valida"), ("agrupa_por_paciente", "por paciente")]),
        celda_tabla(clave, [("metrica_principal", "")]),
        celda_tabla(clave, [("desbalance", "")]),
        celda_tabla(clave, [("resultado_principal", "")]),
        acceso,
    ]
    return "| " + " | ".join(cols) + " |"


def anexo(clave):
    out = [f"### {NOMBRE[clave]}", ""]
    etiquetas = {"tipo": "Tipo", "datos_origen": "Datos: origen", "datos_tamano": "Datos: tamaño",
                 "datos_pais": "Datos: país", "datos_unidad": "Datos: unidad", "validacion": "Cómo valida",
                 "agrupa_por_paciente": "Si agrupa por paciente", "metrica_principal": "Métrica principal",
                 "desbalance": "Desbalance", "resultado_principal": "Resultado principal"}
    for campo, et in etiquetas.items():
        v = J[clave]["celdas"][campo]
        if isinstance(v, dict):
            out.append(f"- **{et}: no lo dice.** Qué se buscó: {norm(v['buscado'])}")
        else:
            out.append(f"- **{et}:**")
            for c in v:
                out.append(f"  - {cita(c)}")
    out.append("")
    return out


def comprobar_todas():
    """Cada cita de cada extracción contra su rango de líneas, no solo las que
    usa este archivo. Devuelve (total, idénticas, iguales salvo espacios, las
    claves con citas de la segunda clase)."""
    total = identicas = normalizadas = 0
    claves_normalizadas = set()
    for k in ORDEN:
        d = J[k]
        items = [(c, c["cita"]) for v in d["celdas"].values() if isinstance(v, list) for c in v]
        items += [(c, c["cita"]) for c in d.get("contrastes", [])]
        items += [(c, c["referencia"]) for c in d.get("citados_comparables", [])]
        for c, texto in items:
            tramo = " ".join(lineas(c["archivo"])[int(c["linea_ini"]) - 1:int(c["linea_fin"])])
            total += 1
            if texto in tramo:
                identicas += 1
            elif norm(texto) in norm(tramo):
                normalizadas += 1
                claves_normalizadas.add(k)
            else:
                raise SystemExit(f"CITA QUE NO ESTÁ ({k}): {c['archivo']}:{c['linea_ini']}-{c['linea_fin']}")
    return total, identicas, normalizadas, claves_normalizadas


TOTAL, IDENTICAS, NORMALIZADAS, CLAVES_NORMALIZADAS = comprobar_todas()
# La frase de la cabecera explica las citas iguales salvo espacios por el PDF
# de Cassidy: si aparecen en otro trabajo, hay que rehacerla.
if CLAVES_NORMALIZADAS != {"cassidy-2022"}:
    raise SystemExit(f"Citas iguales salvo espacios en {sorted(CLAVES_NORMALIZADAS)}: rehacer la frase de la cabecera.")

# =========================== documento ===========================
L = []
L += [
    "# Insumos para el estado del arte: comparación con los trabajos citados",
    "",
    "*Insumo de trabajo, no texto del informe. Preparado el 2026-10-04 para lo que pidió el docente: comparar con otros",
    "trabajos académicos, darles reconocimiento y declarar qué suma este proyecto.*",
    "",
    "**Qué trabajos entran.** Los que cita la sección 2 del anteproyecto (`informe/anteproyecto.md`, «2. Estado del arte»),",
    "uno por fila: diecisiete. El contexto es la nota «Pendiente del estado del arte» de `PLAN.md`, Fase 0.",
    "",
    "**Cómo se lee cada celda.** Una o más citas literales entre comillas latinas, cada una con su archivo y su línea. Los",
    "saltos de línea, tabulaciones, espacios finos y espacios repetidos del original se muestran como un espacio, y en el resumen de",
    "Barrera-Valencia se quitan las marcas «> » del bloque de cita de la ficha. Si el texto no dice algo, la celda dice",
    "**no lo dice**, sin inferir; qué se buscó está en el anexo, por trabajo. En la tabla va una cita por dato, la primera de",
    "las extraídas; el anexo da todas.",
    "",
    "**Cómo se comprobó.** Las citas se extrajeron leyendo cada archivo entero y se comprobaron después, una por una y por",
    f"script, contra el rango de líneas que declaran: {TOTAL} citas, {IDENTICAS} idénticas carácter a carácter y {NORMALIZADAS}, todas de Cassidy",
    "et al. (2022), idénticas salvo espacios, porque su texto viene de un PDF con cortes de línea a mitad de frase. Ninguna",
    "sale de las secciones nuestras de las fichas («análisis nuestro», cabeceras); todas, de «Texto original», del resumen",
    "de PubMed o de la copia local de la página. El archivo lo arma `informe/insumos/armar_comparacion.py` desde las",
    "extracciones de `informe/insumos/citas/`, y en cada corrida vuelve a comprobar todas las citas de las extracciones,",
    "no solo las que usa.",
    "",
    "**Acceso.** «texto completo versionado»: el artículo entero está en `referencias/`. «ficha + LOCAL»: la ficha está en",
    "`referencias/` y el texto completo solo en `referencias/_texto-completo/`, que no se versiona. «solo resumen»: no hubo",
    "acceso al texto completo; lo que el resumen no dice figura como **no lo dice**, aunque el artículo pueda decirlo.",
    "",
    "## Tabla",
    "",
    "| Trabajo | Tipo | Datos | Cómo valida y si agrupa por paciente | Métrica principal | Desbalance | Resultado principal | Acceso |",
    "|---|---|---|---|---|---|---|---|",
]
L += [fila(k) for k in ORDEN]
L.append("")

# ---------- Tabla 3 y línea 248 de Kurtansky 2025 ----------
K25 = "referencias/kurtansky-2025-triaje-automatizado-tbp.md"
tabla3 = lineas(K25)[197:232]
L += [
    "## Kurtansky et al. (2025): la Tabla 3 y la ablación del ganador",
    "",
    f"Copia literal de la Tabla 3, tal como está en `{K25}`, líneas 198–232 (las columnas van separadas por",
    "tabulaciones; «x» marca las clases de variables que usa cada variante):",
    "",
    "```",
] + tabla3 + ["```", ""]
# Nota junto a la tabla, con la decisión de la persona (2026-10-04).
fr196 = "NNT80% SE = 51.57"
comprobar(K25, 196, 196, "The winning model realized " + fr196)
fr22 = "22 additional"
comprobar(K25, 248, 248, fr22)
assert any(l.startswith("\t\tx\tx\tx\tx\t0.173\t0.967\t50.57\t") for l in tabla3), "la fila del ganador no da 50.57"
L += [
    f"**Nota.** La línea 196 de Kurtansky 2025 da «{fr196}» (`{K25}`, l. 196) y la Tabla 3 y la línea 248 dan",
    f"50.57. Esta última cuadra con las «{fr22}» de la línea 248 (72,68 − 50,57 = 22,11; con 51,57 serían 21,11).",
    "Si se cita, se usa la de la tabla y se declara la discrepancia. *Decisión de la persona, 2026-10-04. El artículo",
    "no declara errata.*",
    "",
]
l248 = lineas(K25)[247]
comprobar(K25, 248, 248, l248)
L += [f"Línea 248, literal (`{K25}`, l. 248):", "", "> " + l248, ""]
# comprobación de cada comparación de la línea 248 contra las filas de la tabla
filas_t = {}
for l in tabla3:
    m = re.match(r"^\t\t(x?)\t(x?)\t(x?)\t(x?)\t([\d.]+)\t([\d.]+)\t([\d.]+)\t([\d.]+)\t([\d.]+)$", l)
    if m:
        clave = (bool(m.group(1)), bool(m.group(2)), bool(m.group(3)), bool(m.group(4)))
        filas_t.setdefault(clave, (float(m.group(6)), float(m.group(7))))  # la primera aparición: cáncer de piel
CLASES = ("Meta-basic", "Meta-WB360", "Tiles", "Patient context")


def var(*cl):
    return tuple(c in cl for c in CLASES)


COMPARACIONES_248 = [
    ("sin contexto de paciente frente al modelo completo", "AUC = 0.956 vs. AUC = 0.967",
     var("Meta-basic", "Meta-WB360", "Tiles"), var(*CLASES), "auc"),
    ("NNT80% SE sin contexto frente al completo", "NNT80% SE = 72.68 vs. NNT80% SE = 50.57",
     var("Meta-basic", "Meta-WB360", "Tiles"), var(*CLASES), "nnt"),
    ("solo WB360 frente a solo imágenes", "AUC = 0.939 vs. AUC = 0.922",
     var("Meta-WB360"), var("Tiles"), "auc"),
    ("sin imágenes frente a sin WB360", "AUC = 0.957 vs. AUC = 0.948",
     var("Meta-basic", "Meta-WB360", "Patient context"), var("Meta-basic", "Tiles", "Patient context"), "auc"),
    ("con datos demográficos frente a sin ellos, sobre WB360 y contexto", "AUC = 0.957 vs. AUC = 0.949",
     var("Meta-basic", "Meta-WB360", "Patient context"), var("Meta-WB360", "Patient context"), "auc"),
]
L += ["Cada comparación de la línea 248 contra la fila de la Tabla 3 (clasificación de cáncer de piel):", ""]
for desc, texto, a, b, met in COMPARACIONES_248:
    assert norm(texto) in norm(l248), texto
    va, vb = filas_t[a], filas_t[b]
    i = 0 if met == "auc" else 1
    L.append(f"- {desc}: la línea 248 dice «{texto}»; la tabla da {va[i]} y {vb[i]}.")
L.append("")

# ---------- (a) contrastes ----------
L += ["## (a) Contrastes que el texto permite", "",
      "Pares de trabajos que difieren en una misma dimensión, y solo donde los dos textos dicen algo sobre ella. Una",
      "ausencia («no lo dice») no cuenta como diferencia.", ""]
CONTRASTES = [
    ("Unidad de partición: por sujeto frente a estratificada por diagnóstico",
     [("Saeb et al. (2017) parten por sujeto", q("saeb-2017", "agrupa_por_paciente", 0)),
      ("Rios-Duarte et al. (2024) estratifican la partición por el diagnóstico", q("rios-duarte-2024", "validacion", 0))]),
    ("Validación: prueba con pacientes distintos frente a la partición fija de un reto",
     [("Kurtansky et al. (2025)", q("kurtansky-2025", "validacion", 0)),
      ("Jojoa Acosta et al. (2021) usan la partición del reto ISIC 2017", q("jojoa-acosta-2021", "validacion", 0))]),
    ("Comparación de modelos: prueba t sobre las medias de 10 pliegues frente a la prueba de DeLong",
     [("Jojoa et al. (2022)", q("jojoa-2022", "validacion", 0)),
      ("y comparan las medias con", q("jojoa-2022", "validacion", 2)),
      ("Kurtansky et al. (2025)", qc("kurtansky-2025", 4)),
      ("Rios-Duarte et al. (2024)", qc("rios-duarte-2024", 3))]),
    ("Métrica: área parcial frente a área completa",
     [("McClish (1989) propone", q("mcclish-1989", "metrica_principal", 0)),
      ("Walter (2005), en metaanálisis, concluye", q("walter-2005", "resultado_principal", 2)),
      ("y la competición la restringe a sensibilidad alta", q("kaggle-2024", "metrica_principal", 0))]),
    ("Métrica: restricción de una vía frente a dos vías",
     [("Yang et al. (2019) restringen los dos ejes", q("yang-2019", "metrica_principal", 0)),
      ("ISIC 2024 restringe solo la sensibilidad", q("kaggle-2024", "metrica_principal", 1))]),
    ("Métrica: el AUC solo frente al AUC con métricas de triaje",
     [("Marchetti et al. (2023)", q("marchetti-2023", "metrica_principal", 0)),
      ("Kurtansky et al. (2025)", q("kurtansky-2025", "metrica_principal", 2))]),
    ("Métrica: exactitud balanceada frente a F1 y otras cinco",
     [("Jojoa Acosta et al. (2021) añaden exactitud balanceada por el desbalance", q("jojoa-acosta-2021", "metrica_principal", 1)),
      ("Jojoa et al. (2022)", q("jojoa-2022", "metrica_principal", 0))]),
    ("Desbalance: pérdida ponderada, aumento de la clase maligna o un conjunto balanceado",
     [("Rios-Duarte et al. (2024)", q("rios-duarte-2024", "desbalance", 1)),
      ("Jojoa Acosta et al. (2021)", q("jojoa-acosta-2021", "desbalance", 1)),
      ("Cassidy et al. (2022)", q("cassidy-2022", "desbalance", 1))]),
    ("Desbalance: proporción del conjunto",
     [("SLICE-3D, en Kurtansky, D’Alessandro et al. (2024)", q("kurtansky-2024", "desbalance", 0)),
      ("Marchetti et al. (2023)", q("marchetti-2023", "datos_tamano", 1)),
      ("Saeb et al. (2017), en su simulación", q("saeb-2017", "desbalance", 1))]),
    ("Unidad de análisis: imagen, lesión, paciente, consulta",
     [("el reto pide una predicción por imagen", q("kaggle-2024", "datos_unidad", 0)),
      ("SLICE-3D: una imagen por lesión", q("kurtansky-2024", "datos_unidad", 1)),
      ("Mejía Posada et al. (2024): el paciente", q("mejia-posada-2024", "datos_unidad", 0)),
      ("Sáenz et al. (2018): la consulta", q("saenz-2018", "datos_unidad", 0))]),
    ("Datos: un centro y conveniencia frente a siete centros",
     [("Marchetti et al. (2023)", q("marchetti-2023", "datos_origen", 0)),
      ("SLICE-3D", q("kurtansky-2024", "datos_tamano", 1))]),
    ("Datos: fotografía corporal total frente a dermatoscopia",
     [("SLICE-3D", q("kurtansky-2024", "datos_origen", 1)),
      ("Cassidy et al. (2022)", q("cassidy-2022", "datos_origen", 0)),
      ("Rios-Duarte et al. (2024), sin metadatos", qc("rios-duarte-2024", 5))]),
    ("Fuga: no independencia frente a duplicados",
     [("Kapoor y Narayanan (2023), tipo L3.2", qc("kapoor-2023", 0)),
      ("Kapoor y Narayanan (2023), tipo L1.4", qc("kapoor-2023", 4)),
      ("Cassidy et al. (2022) los encuentran entre entrenamiento y prueba en ISIC", q("cassidy-2022", "resultado_principal", 0))]),
    ("Validación por sujeto: la prescripción y su réplica",
     [("Saeb et al. (2017)", q("saeb-2017", "agrupa_por_paciente", 1)),
      ("Little, en Little et al. (2017)", qc("little-2017", 0)),
      ("Varoquaux, en la misma revisión", qc("little-2017", 8))]),
]
for titulo, items in CONTRASTES:
    L.append(f"- **{titulo}.**")
    for quien, c in items:
        L.append(f"  - {quien}: {c}")
L.append("")

# ---------- (b) lo que suma este proyecto ----------
L += ["## (b) Qué hace este proyecto que cada trabajo no hace", "",
      "Solo donde lo sostienen una cita del trabajo y un campo de `outputs/` o una frase de `informe/borrador-v2.md`. Donde",
      "no hay las dos cosas, el trabajo no aparece aquí (ver al final).", ""]
B = [
    ("kurtansky-2024", [
        ("El descriptor deja la evaluación fuera de su alcance", q("kurtansky-2024", "validacion", 2)),
        ("y menciona que varias imágenes son del mismo paciente", q("kurtansky-2024", "datos_unidad", 2)),
        ("Este proyecto mide cuánto pesa eso en una partición", qo("diseno-validacion.json", "comparacion_particion_naive.pct_grupos_con_fuga")),
        ("", qb(307, 309, "Una partición aleatoria por filas, con la misma semilla, habría dejado a 824 pacientes, el 98,92%, con lesiones a los dos lados."))]),
    ("kurtansky-2025", [
        ("Compara las variantes de la ablación con la prueba de DeLong sobre el conjunto de evaluación", qc("kurtansky-2025", 4)),
        ("Este proyecto compara con diferencias pareadas por pliegue y un intervalo corregido por el solape", qb(76, 77, "Los dos modelos de cada comparación se evalúan sobre los mismos pliegues, así que cada comparación da 50 diferencias pareadas.")),
        ("", qb(80, 81, "El intervalo de la diferencia media se corrige por el solape entre los conjuntos de entrenamiento, con la corrección de Nadeau y Bengio (2003)"))]),
    ("marchetti-2023", [
        ("Su desenlace principal es el AUC", q("marchetti-2023", "metrica_principal", 0)),
        ("Este proyecto lee también la pAUC y las dos métricas de triaje, y muestra que pueden discrepar del AUC",
         qb(382, 385, "La métrica por defecto no es ciega a ese fallo, pero lo lee distinto. En la partición de la semilla 42, el AUC estándar del modelo sin balancear es 0,582, por encima del azar de su escala, 0,5; su pAUC queda por debajo del azar de la suya.")),
        ("", qo("fase4-m2-vs-m1.json", "comparaciones_nuevo_menos_base.setop15.intervalo_t_95_nadeau_bengio"))]),
    ("walter-2005", [
        ("Prefiere el AUC completo", q("walter-2005", "resultado_principal", 2)),
        ("Este proyecto reporta los dos sobre las mismas predicciones", qo("modelado-baseline.json", "nivel_2a_gradient_boosting_sin_balancear.auc_estandar_media")),
        ("", qo("validacion-repetida.json", "nivel_2a_gradient_boosting_sin_balancear.pauc_media_global"))]),
    ("yang-2019", [
        ("Sus datos se suponen independientes", qc("yang-2019", 5)),
        ("Este proyecto trabaja con lesiones agrupadas en pacientes, y lo mide", qo("eda-diagnostico.json", "estructura_grupos.filas_por_grupo.max")),
        ("", qb(300, 301, "La validación cruzada agrupa por paciente: cada paciente queda entero de un lado de cada pliegue."))]),
    ("saeb-2017", [
        ("Sus datos son de reconocimiento de actividad con un teléfono", qc("saeb-2017", 0)),
        ("Este proyecto aplica la partición por sujeto a lesiones de piel, con hasta miles de lesiones por paciente", qo("eda-diagnostico.json", "estructura_grupos.filas_por_grupo.max")),
        ("", qo("diseno-validacion.json", "comparacion_particion_naive.pct_grupos_con_fuga"))]),
    ("kapoor-2023", [
        ("Clasifican la no independencia como fuga", qc("kapoor-2023", 0)),
        ("Su estudio de caso es otro dominio", q("kapoor-2023", "datos_unidad", 0)),
        ("Este proyecto la mide en lesiones de piel", qo("diseno-validacion.json", "comparacion_particion_naive.n_grupos_con_fuga"))]),
    ("cassidy-2022", [
        ("Su partición es 80:20 sobre el conjunto curado", q("cassidy-2022", "validacion", 0)),
        ("y el paciente aparece como sugerencia de limpieza", ""),
        ("", qc("cassidy-2022", 7)),
        ("Este proyecto agrupa por paciente", qb(300, 301, "La validación cruzada agrupa por paciente: cada paciente queda entero de un lado de cada pliegue.")),
        ("Recomiendan un conjunto balanceado", q("cassidy-2022", "desbalance", 1)),
        ("este proyecto conserva el desbalance y pondera las clases", ""),
        ("", qb(108, 108, "Gradient boosting (`HistGradientBoostingClassifier`) con `class_weight=\"balanced\"`"))]),
    ("saenz-2018", [
        ("Excluyen valores según su efecto sobre la misma muestra que evalúan", qc("saenz-2018", 7)),
        ("Este proyecto fija la regla antes de correr la comparación", qb(189, 192, "Si el intervalo corregido de la pAUC de M3 limpio − M2 queda entero por encima de cero, el modelo recomendado es M3 limpio; en cualquier otro caso, es M2. Se fijó antes de correr esa comparación, que se corrió una sola vez."))]),
    ("barrera-valencia-2024", [
        ("Su análisis es descriptivo, de costos y tiempos de atención", q("barrera-valencia-2024", "tipo", 1)),
        ("Este proyecto mide el costo de predecir con cada modelo", qo("tiempo-inferencia.json", "tiempos.M3limpio.mediana_segundos_por_1000_lesiones"))]),
    ("mejia-posada-2024", [
        ("Su desenlace es el tiempo libre de melanoma", q("mejia-posada-2024", "metrica_principal", 0)),
        ("Este proyecto evalúa modelos de triaje", qo("fase4-m3limpio-vs-m2.json", "comparaciones_nuevo_menos_base.pauc.intervalo_t_95_nadeau_bengio"))]),
    ("rios-duarte-2024", [
        ("Solo imagen, sin metadatos", qc("rios-duarte-2024", 5)),
        ("Este proyecto usa los metadatos y el contexto de paciente", qo("fase4-m2-vs-m1.json", "comparaciones_nuevo_menos_base.setop15.intervalo_t_95_nadeau_bengio")),
        ("Y elige el mejor modelo con el AUC de validación", q("rios-duarte-2024", "metrica_principal", 0)),
        ("mientras que aquí la regla se fijó antes", qb(546, 546, "Se eligió con una regla fijada antes de correr la comparación"))]),
    ("jojoa-acosta-2021", [
        ("Reentrenan el mejor de los modelos que compararon sobre el conjunto de prueba", q("jojoa-acosta-2021", "validacion", 1)),
        ("", q("jojoa-acosta-2021", "validacion", 2)),
        ("Aquí la recomendación sale de una regla fijada antes de correr, y el conjunto reservado se abre una sola vez",
         qb(197, 199, "**El conjunto reservado se abre una sola vez**, al final, con el modelo recomendado fijado en un commit anterior, y su resultado se reporta sea cual sea."))]),
    ("jojoa-2022", [
        ("Comparan medias de pliegues con una prueba t", q("jojoa-2022", "validacion", 2)),
        ("Aquí el intervalo se corrige por el solape entre conjuntos de entrenamiento",
         qb(80, 81, "El intervalo de la diferencia media se corrige por el solape entre los conjuntos de entrenamiento, con la corrección de Nadeau y Bengio (2003)"))]),
]
for clave, items in B:
    L.append(f"- **{NOMBRE[clave]}.**")
    for quien, c in items:
        L.append(f"  - {quien}" if not c else f"  - {quien + ': ' if quien else ''}{c}")
L += ["",
      "**Sin entrada en (b).** Kurtansky, Rotemberg et al. (2024), el reto: lo que le faltaría a su evaluación sería una",
      "ausencia, y una ausencia no se sostiene con una cita. McClish (1989): solo hay resumen, y es un método.",
      "Little et al. (2017): Little propone probar las dos particiones, «" + norm(J["little-2017"]["celdas"]["validacion"][0]["cita"]) +
      "» (" + loc(J["little-2017"]["celdas"]["validacion"][0]) + "). En este proyecto la partición por filas solo aparece en",
      "`diseno-validacion.json > comparacion_particion_naive`, que cuenta pacientes: no se encontró ningún archivo de salida",
      "que evalúe un modelo con ella (se buscaron «naive», «ingenua», «por_fila» y «record» en `outputs/*.json`). Así que esa",
      "comparación no se hizo.",
      ""]

# ---------- (c) candidatos ----------
YA_CITADOS = ["3D Whole-body skin imaging for automated melanoma detection", "The SLICE-3D dataset",
              "Analysis of the ISIC image datasets", "Melanoma diagnosis using deep learning techniques on dermatoscopic",
              "Using and understanding cross-validation strategies", "The need to approximate the use-case",
              "Skinhealth, a mobile application"]
FUERA = ["Tsanas", "Kaliyadan", "Tran K.", "Ebner C.", "Maragoudakis", "Xiao L.", "Christodoulou", "CLAIM", "Checklist for evaluation of image",
         "Jeong, H. K.", "İsmailMendi", "Ferrante di Ruffano", "Rayner", "Koh, U.", "Navarrete-Dechent", "Javed R.", "Covalic", "Kaufman S"]
TEMAS = [
    ("Triaje o clasificación sobre fotografía corporal total y contexto de paciente",
     ["Cerminara", "Betz-Stablein", "Primiero", "patient-contextual", "patient-centric", "ugly duckling", "Rubegni", "Salerni", "Udrea", "Birkenfeld", "wide-field"]),
    ("Retos ISIC y conjuntos de imágenes de piel", ["International Skin Imaging Collaboration", "skin lesion analysis toward melanoma detection", "HAM10", "BCN20", "Ricci Lara", "Wen, D.", "Ha, Q.", "siim-isic", "SIIM‐ISIC", "Zhang Y"]),
    ("Validación agrupada, fuga por sujeto y fuga entre centros", ["Oner", "Roberts D.R.", "Valavi", "Zech", "Arlot", "Varoquaux G, Raamana", "Abraham A", "Xu G", "Wieczorek", "Obuchowski", "Roberts M."]),
    ("Clasificación de lesiones, comparación con dermatólogos y métricas clínicas", ["Number needed to biopsy", "Esteva", "Tschandl, P.", "Tschandl P", "Brinker", "Haenssle", "Marchetti, M. A. et al. Prospective", "PROVE-AI", "Heinlein", "human readers", "Human–computer", "James, O. T.", "Han SS", "Fujisawa", "Gessert", "Hekler", "Bissoto", "Harangi", "Schaefer", "Yilmaz", "Kawahara"]),
    ("Desbalance de clases", ["Vandewiele", "Blagus", "Le, D. N. T."]),
]
candidatos = {}
for clave in ORDEN:
    for c in J[clave].get("citados_comparables", []):
        ref = norm(c["referencia"])
        if any(y.lower() in ref.lower() for y in YA_CITADOS) or any(f in ref for f in FUERA):
            continue
        clave_ref = re.sub(r"\W+", "", re.sub(r"^\[?\d+\]?\.?\s*", "", ref).lower())[:60]
        candidatos.setdefault(clave_ref, []).append((clave, c))
asignados = {t: [] for t, _ in TEMAS}
otros = []
for k, usos in candidatos.items():
    ref = norm(usos[0][1]["referencia"])
    tema = next((t for t, pal in TEMAS if any(p.lower() in ref.lower() for p in pal)), None)
    (asignados[tema] if tema else otros).append(usos)
L += ["## (c) Candidatos: trabajos que estas fuentes citan y que serían comparables", "",
      "Con la referencia tal como la da la fuente, la línea donde está y quién la cita. No se buscaron ni se leyeron:",
      "son candidatos. Quedan fuera los que ya están en la sección 2 del anteproyecto y los que no tratan de lesiones de",
      "piel ni de validación (teledermatología de logística, Parkinson, sonidos cardíacos, resonancia magnética, guías",
      "de reporte y revisiones generales de IA en dermatología).", ""]
n_cand = 0
for tema, _ in TEMAS + [("Otros", None)]:
    grupo = asignados.get(tema, otros if tema == "Otros" else [])
    if not grupo:
        continue
    L.append(f"### {tema}")
    L.append("")
    for usos in grupo:
        clave0, c0 = usos[0]
        comprobar(c0["archivo"], int(c0["linea_ini"]), int(c0["linea_fin"]), c0["referencia"])
        citan = "; ".join(f"{NOMBRE[k]} ({loc(c)})" for k, c in usos)
        L.append(f"- «{norm(c0['referencia'])}». Lo citan: {citan}.")
        n_cand += 1
    L.append("")

# ---------- otras discrepancias ----------
L += ["## Otras discrepancias internas de las fuentes", "",
      f"- **Sáenz et al. (2018):** {q('saenz-2018', 'datos_tamano', 0)}; y entre las consultas de la brigada, «dermatology, 7.26% (n = 65)» "
      "(`referencias/saenz-2018-app-teledermatologia-colombia.md`, l. 321). El texto no explica la diferencia entre 65 consultas y 64 registradas.",
      "- **Mejía Posada et al. (2024):** los resultados dan «45 patients (12.2%) developed melanomas» "
      "(`referencias/mejia-posada-2024-mapeo-corporal-medellin.md`, l. 319) y la discusión, «10% of the population developed melanoma» "
      "(misma ficha, l. 377). La ficha ya lo anota y cita el 12,2 %.",
      ""]
comprobar("referencias/saenz-2018-app-teledermatologia-colombia.md", 321, 321, "dermatology, 7.26% (n = 65)")
comprobar("referencias/mejia-posada-2024-mapeo-corporal-medellin.md", 319, 319, "45 patients (12.2%) developed melanomas")
comprobar("referencias/mejia-posada-2024-mapeo-corporal-medellin.md", 377, 377, "10% of the population developed melanoma")

# ---------- anexo ----------
L += ["## Anexo: todas las citas, por trabajo", "",
      "Cada dato con todas sus citas, y en cada «no lo dice», qué se buscó y dónde.", ""]
for k in ORDEN:
    L += anexo(k)

os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(L).rstrip() + "\n")
print(f"Escrito {SALIDA}: {len(L)} líneas, {n_cand} candidatos.")

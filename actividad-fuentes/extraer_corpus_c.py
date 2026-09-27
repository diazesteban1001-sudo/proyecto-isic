#!/usr/bin/env python3
"""
extraer_corpus_c.py — extrae el corpus del tratamiento C: un .txt por
referencia, solo con el texto original, para subirlo a NotebookLM
(protocolo-experimento-v1.md; lista, regla y SHA-256 en corpus-c.md).

Qué toma de cada fuente, qué quita y qué añade está en corpus-c.md, «Qué se
quitó y qué se añadió». En corto:
- de los .md de referencias/ y de las copias locales, la sección «## Texto
  original», sin el encabezado;
- de las copias locales en texto plano, lo que va después de nuestras líneas de
  procedencia;
- quita los marcadores de página de Cassidy, el marcado Markdown puesto por
  quien copió (PanDerm, Kaggle) y los términos MeSH de McClish y Walter;
- añade, en los archivos que reúnen varias fuentes, una línea con el nombre de
  archivo o la URL delante de cada una.

Los archivos extraídos no se versionan. Nueve fuentes están en
referencias/_texto-completo/, que tampoco se versiona: en una máquina nueva
hay que volver a obtenerlas desde la URL de su ficha. El guion lo avisa antes
de escribir nada. Al terminar, compara el SHA-256 de cada archivo con la tabla
de corpus-c.md; si una fuente cambió, lo dice.

Uso:
    python actividad-fuentes/extraer_corpus_c.py [--salida DIR]
    python actividad-fuentes/extraer_corpus_c.py --comprobar DIR
La salida por defecto es ~/Downloads/corpus-c. No sobrescribe una carpeta que
ya existe. --comprobar solo compara una carpeta ya extraída con corpus-c.md.
Solo usa la biblioteca estándar.
"""

import argparse
import hashlib
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
REF = os.path.join(REPO, "referencias")
LOCAL = os.path.join(REF, "_texto-completo")
SALIDA = os.path.expanduser("~/Downloads/corpus-c")
CORPUS_C = os.path.join(AQUI, "corpus-c.md")

# Las fuentes que no viajan con el repositorio.
FUENTES_LOCALES = [
    "cac-melanoma-colombia-2026.md", "cac-melanoma-colombia-2025.md", "isic-licencia-y-cita-slice3d.md",
    "kaggle-overview-cita-2026-09-21.txt", "kaggle-evaluation.md", "upstream-README.md",
    "upstream-PrimaryMetric-pAUC.py", "upstream-SecondaryMetric-TopNSensitivity.py",
    "marchetti-2023-resumen-pubmed.txt", "mcclish-1989-pauc-original.md", "nadeau-bengio-2003.txt",
    "walter-2005-pauc-sroc-en-metaanalisis.md",
]


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def seccion_texto_original(ruta, hasta_separador=False):
    """Lo que va después del encabezado '## Texto original…', sin el encabezado.
    Con hasta_separador, se corta en la primera línea '---' (McClish, Walter:
    después vienen los términos MeSH, que no son del trabajo)."""
    lineas = leer(ruta).split("\n")
    inicio = [i for i, l in enumerate(lineas) if l.startswith("## Texto original")]
    assert len(inicio) == 1, ruta
    cuerpo = lineas[inicio[0] + 1:]
    if hasta_separador:
        cuerpo = cuerpo[:cuerpo.index("---")]
    return "\n".join(cuerpo)


def despues_de_separador(ruta):
    """Copias de Kaggle: cabecera nuestra, '---', y el texto."""
    lineas = leer(ruta).split("\n")
    return "\n".join(lineas[lineas.index("---") + 1:])


def limpiar_markdown(texto):
    """Quita el marcado Markdown puesto por quien copió: '#' de encabezado,
    '>' de bloque citado, la negrita al principio de línea y las vallas de
    código."""
    fuera = []
    for l in texto.split("\n"):
        if l.startswith("```"):
            continue
        l = re.sub(r"^#{1,6}\s+", "", l)
        l = re.sub(r"^>\s?", "", l)
        # Solo la negrita que abre la línea: "**Fig. 1 …**", "**A. Data Access and Use.**".
        # Un "**" en medio puede ser texto original: "***p<0.001" en PanDerm.
        l = re.sub(r"^\*\*([^*]+?)\*\*", r"\1", l)
        fuera.append(l)
    return "\n".join(fuera)


def compactar(texto):
    """Sin líneas en blanco al principio ni al final, y como mucho una seguida."""
    texto = re.sub(r"\n{3,}", "\n\n", texto.strip("\n"))
    return texto + "\n"


def notebook_a_texto(ruta):
    nb = json.loads(leer(ruta))
    celdas = []
    for c in nb["cells"]:
        if c["cell_type"] in ("code", "markdown"):
            fuente = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            if fuente.strip():
                celdas.append(fuente.rstrip("\n"))
    return "\n\n".join(celdas)


def partes(*pares):
    """Varias fuentes de una misma referencia: cada una precedida de una línea
    con su nombre de archivo o su URL."""
    return "\n\n".join(f"{nombre}\n\n{compactar(texto).rstrip()}" for nombre, texto in pares)


def construir():
    s = seccion_texto_original
    art = lambda nombre: os.path.join(REF, nombre + ".md")
    corpus = {}

    # 1. Texto original versionado
    cassidy = s(art("cassidy-2022-duplicados-isic"))
    corpus["cassidy-2022"] = "\n".join(l for l in cassidy.split("\n") if not re.fullmatch(r"=== \[p\. \d+\] ===", l))
    corpus["jojoa-2022"] = s(art("jojoa-2022-redes-complejas-melanoma"))
    corpus["jojoa-acosta-2021"] = s(art("jojoa-acosta-2021-aprendizaje-profundo-melanoma"))
    corpus["kapoor-narayanan-2023"] = s(art("kapoor-2023-fuga-y-reproducibilidad"))
    corpus["kurtansky-2024-slice3d"] = s(art("kurtansky-2024-slice3d-descriptor"))
    corpus["kurtansky-2025"] = s(art("kurtansky-2025-triaje-automatizado-tbp"))
    corpus["little-2017"] = s(art("little-2017-perspectivas-sobre-saeb"))
    corpus["mejia-posada-2024"] = s(art("mejia-posada-2024-mapeo-corporal-medellin"))
    corpus["rios-duarte-2024"] = s(art("rios-duarte-2024-cnn-melanoma-uniandes"))
    corpus["saeb-2017"] = s(art("saeb-2017-validacion-por-sujeto"))
    corpus["saenz-2018"] = s(art("saenz-2018-app-teledermatologia-colombia"))
    panderm = s(art("panderm-reduccion-examenes")).split("\n")
    assert panderm[1].startswith("*Contenido textual del XML"), panderm[:3]
    panderm = "\n".join(panderm[2:])
    # Encabezados que no están en el XML: los puso quien extrajo el texto.
    panderm = limpiar_markdown(panderm)
    panderm = "\n".join(l for l in panderm.split("\n") if l not in ("Abstract", "Abstract (web-summary)"))
    corpus["yan-2025"] = panderm
    nov = os.path.join(REF, "novoselskiy-2024-isic2024")
    corpus["novoselskiy-2024"] = partes(
        ("README.md", leer(os.path.join(nov, "README.md"))),
        ("notebooks/top-model.ipynb", notebook_a_texto(os.path.join(nov, "notebooks", "top-model.ipynb"))),
    )

    # 2. Copias locales
    corpus["contreras-2026"] = s(os.path.join(LOCAL, "cac-melanoma-colombia-2026.md"))
    corpus["cuenta-de-alto-costo-2025"] = s(os.path.join(LOCAL, "cac-melanoma-colombia-2025.md"))
    corpus["isic-2024"] = s(os.path.join(LOCAL, "isic-licencia-y-cita-slice3d.md"))
    # Las reglas (kaggle-rules.md) no entran: la copia se tomó a mano, ya era una
    # selección, y algún pasaje tiene forma de resumen. No se pueden certificar
    # como literales. Decisión de la persona, 2026-09-27.
    overview = leer(os.path.join(LOCAL, "kaggle-overview-cita-2026-09-21.txt")).split("\n")
    assert overview[0].startswith("Fuente:") and overview[1].startswith("Leido con"), overview[:2]
    corpus["kurtansky-2024-kaggle"] = partes(
        ("https://www.kaggle.com/competitions/isic-2024-challenge/overview", "\n".join(overview[2:])),
        ("https://www.kaggle.com/competitions/isic-2024-challenge/overview/evaluation",
         limpiar_markdown(despues_de_separador(os.path.join(LOCAL, "kaggle-evaluation.md")))),
    )
    corpus["kurtansky-2024-challenge-metrics"] = partes(
        ("README.md", leer(os.path.join(LOCAL, "upstream-README.md"))),
        ("PrimaryMetric-pAUC.py", leer(os.path.join(LOCAL, "upstream-PrimaryMetric-pAUC.py"))),
        ("SecondaryMetric-TopNSensitivity.py", leer(os.path.join(LOCAL, "upstream-SecondaryMetric-TopNSensitivity.py"))),
    )
    marchetti = leer(os.path.join(LOCAL, "marchetti-2023-resumen-pubmed.txt")).split("\n")
    assert marchetti[0].startswith("Fuente:") and marchetti[2].startswith("Copia LOCAL"), marchetti[:3]
    corpus["marchetti-2023"] = "\n".join(marchetti[3:])
    corpus["mcclish-1989"] = s(os.path.join(LOCAL, "mcclish-1989-pauc-original.md"), hasta_separador=True)
    corpus["nadeau-bengio-2003"] = leer(os.path.join(LOCAL, "nadeau-bengio-2003.txt"))
    corpus["walter-2005"] = s(os.path.join(LOCAL, "walter-2005-pauc-sroc-en-metaanalisis.md"), hasta_separador=True)
    return {k: compactar(v) for k, v in corpus.items()}


def sha256(ruta):
    with open(ruta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def comparar(directorio):
    """Compara los archivos de `directorio` con la tabla de corpus-c.md, por los
    16 primeros caracteres del SHA-256. Devuelve la lista de diferencias."""
    esperados = dict(re.findall(r"`([a-z0-9-]+\.txt)` \| `([0-9a-f]{16})`", leer(CORPUS_C)))
    presentes = {f for f in os.listdir(directorio) if f.endswith(".txt")}
    diferencias = [f"falta {f}" for f in sorted(set(esperados) - presentes)]
    diferencias += [f"sobra {f}" for f in sorted(presentes - set(esperados))]
    diferencias += [f"{f}: SHA-256 {sha256(os.path.join(directorio, f))[:16]}, corpus-c.md dice {esperados[f]}"
                    for f in sorted(presentes & set(esperados))
                    if sha256(os.path.join(directorio, f))[:16] != esperados[f]]
    return diferencias


def informar(directorio):
    diferencias = comparar(directorio)
    if diferencias:
        print("NO coincide con corpus-c.md:\n  " + "\n  ".join(diferencias))
        return 1
    print("Los SHA-256 coinciden con corpus-c.md, archivo por archivo.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--salida", default=SALIDA)
    grupo.add_argument("--comprobar", metavar="DIR")
    args = ap.parse_args()
    if args.comprobar:
        sys.exit(informar(args.comprobar))

    faltan = [f for f in FUENTES_LOCALES if not os.path.exists(os.path.join(LOCAL, f))]
    if faltan:
        sys.exit("ERROR: faltan copias locales en referencias/_texto-completo/ (se obtienen de nuevo "
                 "desde la URL de su ficha):\n  " + "\n  ".join(faltan))
    if os.path.exists(args.salida):
        sys.exit(f"ERROR: {args.salida} ya existe; no se sobrescribe.")
    corpus = construir()
    os.makedirs(args.salida)
    for nombre, texto in corpus.items():
        with open(os.path.join(args.salida, nombre + ".txt"), "x", encoding="utf-8", newline="") as f:
            f.write(texto)
    print(f"{len(corpus)} archivos en {args.salida}")
    sys.exit(informar(args.salida))


if __name__ == "__main__":
    main()

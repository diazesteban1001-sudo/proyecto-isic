#!/usr/bin/env python3
"""
md_a_pdf.py — convierte informe/anteproyecto.md en PDF: Markdown -> HTML con
la biblioteca estándar, y HTML -> PDF con Chrome sin interfaz.

Regenerar el PDF (Chrome sin interfaz, sin cabecera ni pie del navegador):
    python3 informe/md_a_pdf.py --entrada informe/anteproyecto.md --salida informe/anteproyecto.pdf

El PDF no se versiona (`informe/*.pdf` está en .gitignore): se regenera con
esta orden siempre que cambie el Markdown. El HTML intermedio va a un
directorio temporal y se borra; con --html se conserva para revisarlo.

Cubre solo lo que usa el anteproyecto: encabezados, párrafos, viñetas y listas
numeradas anidadas (con párrafos dentro de un ítem), tablas con barras, citas
en bloque con varios párrafos, **negrita**, *cursiva*, `código` y URL sueltas.
Lo que haya antes del primer `## ` es la portada: va centrada y en su página.

Tipografía (solo en el conversor; el Markdown no se toca):
- Times New Roman de 12 puntos, alineada a la izquierda y sin justificar, como
  pide APA 7, y sin división automática de palabras. Times no tiene los
  subíndices ₁ y ₂: los dibuja STIX Two Text, segunda en la lista de fuentes,
  así que el carácter Unicode se conserva y se ve como subíndice.
- Entre una cifra y el signo % va un espacio de no separación.
- Las URL y los DOI solo se parten después de «/» o antes de «.»: cada tramo
  va en un <span> sin cortes y entre tramos hay un <wbr>, que no es un
  carácter. El texto copiado del PDF es la URL exacta: no se meten caracteres
  invisibles ni se cambian guiones. El prefijo de un DOI («10.1038/») no se
  parte. «SLICE-3D» tampoco.
- Espacio de no separación en «et al.» y antes del guion de « - », para que
  ninguna línea empiece por él. Las palabras compuestas sí pueden partirse
  por su guion.
- Números de página abajo al centro, con las cajas de margen de @page, que
  Chrome dibuja; la portada no lleva número.
"""

import argparse
import html
import os
import re
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MARCA_LISTA = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
URL = re.compile(r"https?://[^\s<]+")

CSS = """
@page { size: A4; margin: 2.5cm;
        @bottom-center { content: counter(page);
                         font-family: "Times New Roman", serif; font-size: 11pt; } }
@page :first { @bottom-center { content: none; } }
html { font-family: "Times New Roman", "STIX Two Text", serif; font-size: 12pt;
       line-height: 1.5; color: #111; hyphens: manual;
       font-variant-numeric: lining-nums; }
body { margin: 0; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 1.2em; }
h2 { font-size: 15pt; margin: 1.6em 0 .5em; break-after: avoid; }
h3 { font-size: 13pt; margin: 1.2em 0 .4em; break-after: avoid; }
p { margin: 0 0 .7em; text-align: left; }
ul, ol { margin: 0 0 .7em; padding-left: 1.6em; }
li { margin: 0 0 .25em; }
li > p { margin: 0 0 .3em; }
li > ul, li > ol { margin: .2em 0 .3em; }
blockquote { margin: .6em 0 .9em 1.2em; padding: .2em 0 .2em .9em;
             border-left: 3px solid #999; font-size: 11pt; }
blockquote p { margin: 0 0 .5em; }
table { border-collapse: collapse; width: 100%; margin: .6em 0 1em;
        font-size: 10pt; }
th, td { border: 1px solid #888; padding: .3em .45em; vertical-align: top;
         text-align: left; }
th { background: #eee; }
tr { break-inside: avoid; }
code { font-family: "Menlo", "Courier New", monospace; font-size: .85em; }
a { color: inherit; text-decoration: none; }
.nb { white-space: nowrap; }
.portada { text-align: center; padding-top: 30%; break-after: page; }
.portada h1 { margin-bottom: 2em; }
.portada p { text-align: center; margin: 0 0 .6em; }
.referencias p { padding-left: 2em; text-indent: -2em; }
"""


def inline(texto):
    """Formato en línea: se protegen los trozos de código, se escapa el HTML y
    se aplican negrita, cursiva y URL. Las URL se enlazan para que el
    navegador pueda partirlas sin inventar guiones."""
    trozos = re.split(r"(`[^`]+`)", texto)
    salida = []
    for trozo in trozos:
        if trozo.startswith("`") and trozo.endswith("`") and len(trozo) > 1:
            salida.append("<code>" + html.escape(trozo[1:-1]) + "</code>")
            continue
        t = html.escape(trozo, quote=False)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<![*\w])\*(?!\s)([^*]+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", t)

        def enlazar(m):
            url = m.group(0)
            cola = ""
            while url and url[-1] in ".,;:)":
                cola = url[-1] + cola
                url = url[:-1]
            return f'<a href="{url}">{tramos_url(url)}</a>{cola}'

        t = URL.sub(enlazar, t)
        t = fuera_de_etiquetas(t, lambda s: re.sub(r"(\d) %", "\\1&nbsp;%", s))
        t = fuera_de_etiquetas(t, lambda s: s.replace("SLICE-3D", '<span class="nb">SLICE-3D</span>'))
        # «et al.» no se parte, y una línea no empieza por el guion de « - »
        # (el título de la competencia en Kaggle): espacio de no separación.
        t = fuera_de_etiquetas(t, lambda s: s.replace("et al.", "et&nbsp;al.").replace(" - ", "&nbsp;- "))
        salida.append(t)
    return "".join(salida)


def tramos_url(url):
    """La URL partida en tramos que no se cortan por dentro, con un punto de
    corte (<wbr>, que no es un carácter) después de cada «/» y antes de cada
    «.». El esquema «https://» no se parte."""
    esquema, resto = url.split("://", 1)
    tramos, actual = [], esquema + "://"
    for c in resto:
        # El prefijo de un DOI («10.1038/») no se parte por su punto.
        if c == "." and actual and not actual.endswith("://") and actual != "10":
            tramos.append(actual)
            actual = ""
        actual += c
        if c == "/":
            tramos.append(actual)
            actual = ""
    if actual:
        tramos.append(actual)
    return "<wbr>".join(f'<span class="nb">{tramo}</span>' for tramo in tramos)


def fuera_de_etiquetas(texto, funcion):
    """Aplica la función solo al texto, no a las etiquetas ni a sus atributos."""
    partes = re.split(r"(<[^>]+>)", texto)
    return "".join(p if p.startswith("<") else funcion(p) for p in partes)


def interrumpe(linea):
    """Si una línea corta el párrafo en curso para abrir una lista. Como en
    CommonMark, una lista numerada solo interrumpe un párrafo si empieza por
    «1.»: una referencia partida en «1496941. https://doi.org/…» sigue siendo
    párrafo, no un ítem número 1.496.941."""
    m = MARCA_LISTA.match(linea)
    return bool(m) and (not m.group(2)[0].isdigit() or m.group(2) == "1.")


def sangria(linea):
    return len(linea) - len(linea.lstrip(" "))


def bloques(lineas):
    """Convierte una lista de líneas en HTML. Se llama también sobre el
    contenido de cada ítem de lista, ya sin su sangría."""
    out = []
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        desnuda = linea.strip()
        if not desnuda:
            i += 1
            continue
        if desnuda.startswith("#"):
            nivel = len(desnuda) - len(desnuda.lstrip("#"))
            out.append(f"<h{nivel}>{inline(desnuda[nivel:].strip())}</h{nivel}>")
            i += 1
            continue
        if desnuda.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append(lineas[i].strip())
                i += 1
            out.append(tabla(filas))
            continue
        if desnuda.startswith(">"):
            parrafos, actual = [], []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                contenido = lineas[i].strip()[1:].strip()
                if contenido:
                    actual.append(contenido)
                elif actual:
                    parrafos.append(" ".join(actual))
                    actual = []
                i += 1
            if actual:
                parrafos.append(" ".join(actual))
            out.append("<blockquote>" + "".join(f"<p>{inline(p)}</p>" for p in parrafos)
                       + "</blockquote>")
            continue
        if MARCA_LISTA.match(linea):
            html_lista, i = lista(lineas, i)
            out.append(html_lista)
            continue
        partes = []
        while i < len(lineas):
            siguiente = lineas[i]
            s = siguiente.strip()
            if not s or s.startswith(("#", "|", ">")) or interrumpe(siguiente):
                break
            partes.append(s)
            i += 1
        out.append(f"<p>{inline(' '.join(partes))}</p>")
    return "\n".join(out)


def lista(lineas, i):
    """Una lista y sus ítems. Cada ítem reúne su primera línea y todo lo que
    venga con más sangría que su marca —continuaciones, sublistas y párrafos
    tras una línea en blanco—, y ese contenido se convierte recursivamente."""
    base = sangria(lineas[i])
    ordenada = MARCA_LISTA.match(lineas[i]).group(2)[0].isdigit()
    items = []
    while i < len(lineas):
        m = MARCA_LISTA.match(lineas[i])
        if not m or sangria(lineas[i]) != base:
            break
        if m.group(2)[0].isdigit() != ordenada:
            break
        desplazamiento = base + len(m.group(2)) + 1
        contenido = [m.group(3)]
        i += 1
        while i < len(lineas):
            l = lineas[i]
            if not l.strip():
                # Una línea en blanco sigue dentro del ítem solo si lo que viene
                # después está sangrado más que la marca.
                j = i
                while j < len(lineas) and not lineas[j].strip():
                    j += 1
                if j < len(lineas) and sangria(lineas[j]) > base:
                    contenido.extend([""] * (j - i))
                    i = j
                    continue
                break
            if sangria(l) <= base:
                break
            contenido.append(l[desplazamiento:] if sangria(l) >= desplazamiento else l.strip())
            i += 1
        items.append(contenido)
    etiqueta = "ol" if ordenada else "ul"
    cuerpo = []
    for contenido in items:
        interior = bloques(contenido)
        # Un ítem de un solo párrafo va sin <p>, como en una lista compacta.
        if interior.count("<p>") == 1 and interior.startswith("<p>") and interior.endswith("</p>"):
            interior = interior[3:-4]
        cuerpo.append(f"<li>{interior}</li>")
    return f"<{etiqueta}>" + "".join(cuerpo) + f"</{etiqueta}>", i


def tabla(filas):
    def celdas(fila):
        return [c.strip() for c in fila.strip("|").split("|")]
    cabecera = celdas(filas[0])
    cuerpo = [celdas(f) for f in filas[1:] if not re.fullmatch(r"\|?[\s:|-]+\|?", f)]
    th = "".join(f"<th>{inline(c)}</th>" for c in cabecera)
    tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in f) + "</tr>" for f in cuerpo)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


def documento(md):
    lineas = md.split("\n")
    corte = next((k for k, l in enumerate(lineas) if l.startswith("## ")), 0)
    portada, resto = lineas[:corte], lineas[corte:]
    titulo = next((l[2:].strip() for l in portada if l.startswith("# ")), "Anteproyecto")
    partes = []
    if portada:
        partes.append(f'<section class="portada">{bloques(portada)}</section>')
    texto = "\n".join(resto)
    if "\n## Referencias" in "\n" + texto:
        antes, despues = ("\n" + texto).split("\n## Referencias", 1)
        partes.append(bloques(antes.split("\n")))
        partes.append('<section class="referencias"><h2>Referencias</h2>'
                      + bloques(despues.split("\n")) + "</section>")
    else:
        partes.append(bloques(resto))
    return (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
            f"<title>{html.escape(titulo)}</title><style>{CSS}</style></head>"
            f"<body>{''.join(partes)}</body></html>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", required=True)
    ap.add_argument("--salida", required=True, help="ruta del PDF")
    ap.add_argument("--html", help="conservar el HTML intermedio en esta ruta")
    args = ap.parse_args()

    contenido = documento(open(args.entrada, encoding="utf-8").read())
    with tempfile.TemporaryDirectory() as tmp:
        ruta_html = args.html or os.path.join(tmp, "documento.html")
        with open(ruta_html, "w", encoding="utf-8") as f:
            f.write(contenido)
        if not os.path.exists(CHROME):
            sys.exit(f"No encuentro Chrome en {CHROME}.")
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={os.path.abspath(args.salida)}",
             "file://" + os.path.abspath(ruta_html)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    print(f"Escrito: {args.salida}")


if __name__ == "__main__":
    main()

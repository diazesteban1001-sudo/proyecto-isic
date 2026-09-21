# Línea base de la práctica clínica actual — cribado sobre TBP (PanDerm)

**Fuente:** *"A multimodal vision foundation model for clinical dermatology"*,
**Nature Medicine, volumen 31, número 8, páginas 2691-2702** (2025; en línea el
6 de junio de 2025). DOI 10.1038/s41591-025-03747-y.
https://www.nature.com/articles/s41591-025-03747-y
Copia de acceso abierto en PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12353815/

**Autores (25), según Crossref:** Siyuan Yan, Zhen Yu, Clare Primiero, Cristina Vico-Alonso, Zhonghua Wang, Litao Yang, Philipp Tschandl, Ming Hu, Lie Ju, Gin Tan, Vincent Tang, Aik Beng Ng, David Powell, Paul Bonnington, Simon See, Elisabetta Magnaterra, Peter Ferguson, Jennifer Nguyen, Pascale Guitera, Jose Banuls, Monika Janda, Victoria Mar, Harald Kittler, H. Peter Soyer, Zongyuan Ge.
*Verificado en `api.crossref.org` el 2026-09-21. Esta cabecera decía antes solo
"Yan S, Yu Z, Primiero C, Vico-Alonso C, et al." y no daba volumen ni páginas.*

**Fecha de consulta:** 2026-08-20

**LICENCIA: CC BY 4.0 → TEXTO COMPLETO.** *"Open Access This article is
licensed under a Creative Commons Attribution 4.0 International License"*
(https://creativecommons.org/licenses/by/4.0/). Verificado el 2026-09-21 en la
página del artículo en PMC y en el depósito de la editorial en Crossref.
Atribución: Yan S et al., *Nature Medicine* (2025), DOI 10.1038/s41591-025-03747-y. **Cambios** respecto del original, como pide la licencia:
aquí solo se reproduce la frase citada; el desglose, el contexto y las salvedades son nuestros.
**Consultado por:** el agente, vía WebFetch sobre la versión de PMC (acceso
abierto, legible sin sesión, a diferencia de Kaggle).

Este archivo existe para que la cifra de reducción de exámenes innecesarios sea
trazable a un archivo del repositorio y no a la memoria del agente ni a una
conversación previa, siguiendo la regla 3 de `CLAUDE.md`.

---

## La cita literal

Sección de resultados, *"Melanoma screening using TBP"* (figura 4j,k):

> "Significantly, it detected malignant lesions in 79 out of 80 patients while
> reducing unnecessary examinations by 60.8% compared with melanographers
> (3,498 versus 8,913 lesions recommended for detailed examination)"

Desglose de las cifras, todas de esa misma frase:

| Cifra | Qué es |
|---|---|
| 8.913 | Lesiones que **los melanógrafos** marcaron para examen detallado |
| 3.498 | Lesiones que **PanDerm** marcó para examen detallado |
| 60,8% | Reducción de exámenes innecesarios de la segunda cifra respecto a la primera |
| 79 de 80 | Pacientes en los que se detectó malignidad, sobre el mismo grupo |

**El alcance está resuelto, no supuesto:** las cifras 3.498 / 8.913 y el
79-de-80 corresponden **al mismo grupo de 80 pacientes**; la frase los enuncia
en una sola oración.

## Contexto del experimento

Cohortes de fotografía corporal total citadas para esta parte del estudio:

> "The HOP study is an in-house sequential dataset of high-risk melanoma
> individuals with 314 participants."

> "The MYM cohort is an in-house dataset studying the natural history of
> melanocytic nevi from 193 Australian participants."

Escala del problema de cribado en esa evaluación:

> "216 malignant versus 197,716 benign lesions"

Desempeño del modelo sobre esa tarea:

> "Using TBP images alone, PanDerm achieved a sensitivity of 0.893"

Ese desbalance —216 malignas contra 197.716 benignas— es del mismo orden que el
de SLICE-3D (393 sobre 401.059, `outputs/eda-diagnostico.json`), lo que hace la
comparación pertinente para este proyecto.

---

## Lo que el paper NO dice — cuatro límites de esta verificación

Van aquí porque la cifra se va a usar como línea base de la práctica clínica, y
una línea base mal entendida vale menos que ninguna.

1. **El paper dice *"melanographers"*, no "especialistas en melanoma".** La
   palabra aparece **una sola vez** en todo el artículo y **no se define**: no
   se describe su formación, su rol ni su protocolo. Decir "especialistas en
   melanoma" sería una sustitución nuestra, no una cita — y una que
   probablemente exagera la comparación, porque en las unidades de fotografía
   corporal total el melanógrafo suele ser personal técnico dedicado a la
   captura y al marcado, no el dermatólogo que diagnostica. **No lo afirmamos
   en ninguna dirección: el paper no da base para hacerlo.** Al citar la cifra,
   se cita la palabra del paper.

2. **No se declara si los datos son prospectivos o retrospectivos** para esta
   comparación.

3. **La sección de discusión y limitaciones no menciona esta comparación.** Ni
   el 79-de-80, ni los melanógrafos, ni el 60,8%. El resultado se presenta sin
   que los propios autores discutan sus factores de confusión ni las
   diferencias de protocolo entre el modelo y las personas.

4. **La cifra la publican los autores del modelo evaluado.** El 8.913 —el lado
   humano— es la parte útil como línea base independiente; el 3.498 es
   desempeño del propio PanDerm reportado por quienes lo construyeron. Para
   este proyecto sirve la primera; la segunda se cita como contexto de lo que
   el paper afirma, no como resultado verificado por nosotros.

## Advertencia de uso dentro de este proyecto

PanDerm es, a la vez, la fuente de esta cifra y el modelo cuya posible
contaminación con SLICE-3D es la sub-etapa **E1**, bloqueante, de la extensión
(última sección de `CLAUDE.md`). Son dos cosas independientes y conviene no
mezclarlas:

- Citar el **8.913 de los melanógrafos** como línea base de práctica clínica no
  depende en absoluto de si PanDerm está contaminado: es una medición sobre
  personas.
- Usar **pesos de PanDerm** para modelar sí depende de E1, y sigue bloqueado.

# Marchetti et al. (2023) — Modelo morfológico sobre imágenes 3D de cuerpo entero

> **FICHA** (regla 3 de `CLAUDE.md`): datos bibliográficos verificados, las
> **cifras** del resumen —son datos, no expresión—, una paráfrasis del diseño
> **marcada como paráfrasis**, y el cruce con lo que de este modelo mide la
> fuente del proyecto. Solo hay acceso al resumen; el texto completo está tras
> muro de pago.

**Autores:** M. A. Marchetti, Z. H. Nazir, J. K. Nanda, S. W. Dusza, B. M.
D'Alessandro, J. DeFazio, A. C. Halpern, V. M. Rotemberg, A. A. Marghoob.
**Título:** 3D Whole-body skin imaging for automated melanoma detection.
**Revista:** Journal of the European Academy of Dermatology and Venereology
(JEADV), volumen 37, número 5, páginas 945–950.
**Año:** 2023 (mayo).
**DOI:** 10.1111/jdv.18924
**PMID:** 36708077
**Tipo de publicación (PubMed):** Observational Study.

**LICENCIA: con copyright → FICHA.** El resumen lleva *"© 2023 European Academy
of Dermatology and Venereology"*; en Crossref, Wiley solo deposita sus términos y
condiciones (*vor*); no hay copia en PMC. Verificado en `api.crossref.org` el
2026-09-21.

**Texto completo:** no hay acceso. En local, el resumen de PubMed:
`referencias/_texto-completo/marchetti-2023-resumen-pubmed.txt`.
**Fecha de consulta:** 2026-09-21
**URL:** https://pubmed.ncbi.nlm.nih.gov/36708077/

**Cómo se verificó.** Contra el registro de PubMed, leyendo las etiquetas
`citation_*` de la página. La referencia que traía el proyecto —*J Eur Acad
Dermatol Venereol* 37, 945–950 (2023)— **coincide en todos los campos**.

**Dato de contexto, verificable en las dos listas de autores:** D'Alessandro,
Halpern y Rotemberg firman este artículo y también el de los organizadores de
ISIC 2024 (`referencias/kurtansky-2025-triaje-automatizado-tbp.md`). Es el mismo
grupo, MSKCC, evaluando su propio trabajo previo. No es un conflicto oculto
—está a la vista—, pero conviene saberlo antes de presentar la comparación
como externa.

---

## Qué dice el resumen — paráfrasis y cifras

**Diseño (paráfrasis).** Estudio piloto retrospectivo, observacional, de un
solo centro —un hospital oncológico terciario—, sobre una **muestra de
conveniencia** de pacientes diagnosticados de melanoma. Elegibles: quienes
tenían una imagen 3D de cuerpo entero (VECTRA WB360, Canfield Scientific)
tomada en los 90 días previos a la biopsia diagnóstica. Se exportaron las
medidas automáticas de cada lesión —tamaño, color, borde— y el resultado
principal fue el AUC.

**Cifras del resumen** (datos, reproducidos tal cual):

| Dato | Valor |
|---|---|
| Pacientes | 35 |
| Lesiones identificadas automáticamente (> 2 mm) | 23.538 |
| Lesiones por paciente | 102 a 3.021 |
| Melanomas | 49 |
| Lesiones no melanoma | 22.489 |
| Pacientes blancos | todos |
| Varones | 23 (66%) |
| Edad mediana (rango) | 64 años (26–89) |
| **AUC del modelo** | **0,94 (IC 95%: 0,92–0,96)** |
| Melanomas con el puntaje más alto o en el percentil 99 de su paciente | 14 (28%) |

**Conclusión de los autores (paráfrasis).** Lo presentan como prueba de
concepto piloto, y dicen que harían falta conjuntos de imágenes 3D más grandes,
de más calidad y más representativos para mejorar y validar el resultado.

---

## Cruce con la fuente del proyecto — y por qué importa

**El AUC que reporta el propio artículo no es el que se usa en el proyecto.**

| | AUC (melanoma) | Sobre qué datos |
|---|---|---|
| Marchetti et al. (2023), este artículo | 0,94 | sus 35 pacientes, un centro |
| El mismo modelo, reevaluado por Kurtansky et al. (2025) | 0,893 | leaderboard privado de ISIC 2024, multicéntrico |

La segunda cifra sale de `referencias/kurtansky-2025-triaje-automatizado-tbp.md`:
*"outperformed the preliminary model for WB-based melanoma detection published
by Marchetti et al. (AUC = 0.8927)"*. **La caída de 0,94 a 0,893 al cambiar de
datos es lo esperable en un piloto de 35 pacientes**, y es un argumento a favor
de que la referencia del proyecto sea la reevaluación y no el número original.

**Consecuencia directa para `PLAN.md`.** La referencia fijada para el SEtop-15
—**0,541**, Marchetti, objetivo melanoma— **no está en este artículo**: es la
medición que Kurtansky et al. hicieron del modelo de Marchetti sobre el
leaderboard privado (Tabla 3). Este resumen no reporta ningún SEtop-15, que es
una métrica definida después, para ISIC 2024. Al citarla en el informe, se
atribuye a Kurtansky et al. (2025), no a Marchetti et al. (2023).

**Lo que el resumen NO permite afirmar.**

- **El esquema de validación.** El resumen no dice cómo se obtuvo el AUC de
  0,94 —si con partición por paciente, validación cruzada, o sobre los mismos
  datos del ajuste—. Con 35 pacientes y 49 melanomas la diferencia importa
  mucho, y enlaza directamente con la línea 4 del estado del arte, la de fuga por sujeto
  (`PLAN.md`, Fase 0). **No se completa de memoria ni por inferencia.**
- **El "75% menos de lesiones a revisar con 95% de sensibilidad".**
  Kurtansky et al. (2025) atribuyen a este estudio esa reducción, pero **esa
  cifra no está en el resumen**. Puede estar en el texto completo; con lo
  versionado aquí no se puede comprobar, y citarla exigiría conseguirlo.
- **Las 11 medidas morfológicas del modelo.** Las enumera Kurtansky et al.
  (2025) en su sección de métodos; el resumen de este artículo solo habla de
  "tamaño, color, borde".

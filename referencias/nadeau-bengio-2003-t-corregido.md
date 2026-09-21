# Nadeau y Bengio (2003) — El t corregido por solape entre entrenamientos

> ⚠️ **NO CONTIENE EL TEXTO ORIGINAL, y es a propósito.** El artículo es
> © 2003 Kluwer Academic Publishers, sin licencia abierta, y este repositorio
> es público. Aquí hay: los datos bibliográficos verificados, **la fórmula en
> la notación del artículo** (contenido matemático, no expresión), localizadores
> exactos de página y sección, una sola cita breve, y paráfrasis **marcada como
> paráfrasis**. Quien quiera el texto lo obtiene del DOI. Es una desviación
> declarada de la regla 3 de `CLAUDE.md`; ver la última sección.

**Autores:** Claude Nadeau (Health Canada) y Yoshua Bengio (CIRANO y Dept. IRO,
Université de Montréal).
**Título:** Inference for the Generalization Error.
**Revista:** Machine Learning, volumen 52, número 3, páginas 239–281.
**Año:** 2003 (septiembre). Editora de la revista para este artículo: Lisa
Hellerstein.
**DOI:** 10.1023/A:1024068626366
**Fecha de consulta:** 2026-09-21
**URL:** https://link.springer.com/article/10.1023/A:1024068626366

**Cómo se verificó.** Datos bibliográficos contra **dos fuentes académicas
independientes**, que coinciden en todo: el registro de Crossref, que es el
registro oficial de DOIs (`api.crossref.org`), y la página del editor en
Springer. *Machine Learning* no está indexada en PubMed. La fórmula se leyó del
PDF del artículo servido por el editor (43 páginas), no de una fuente
secundaria.

---

## El escenario en que el artículo deriva la fórmula

**Sección 1, pp. 241–242 — paráfrasis nuestra, con la notación del artículo.**
Se toman `J` conjuntos de índices aleatorios `S_1, …, S_J`, cada uno de tamaño
fijo `n1`, **muestreados independientemente entre sí**. `S_j` es el
entrenamiento; su complemento `S_j^c`, de tamaño `n2 = n − n1`, es la prueba.
Para cada división,

    μ̂_j = (1/n2) · Σ_{i ∈ S_j^c} L(j, i)

es el error medio de prueba —o, según la ecuación (4) del artículo, la
**diferencia** de errores entre dos algoritmos—. El estimador es la media de
las `J`, ecuación (5), p. 242:

    ⁿ²ₙ₁μ̂_J = (1/J) · Σ_{j=1..J} μ̂_j

Los autores lo describen como *"close to the popular K-fold cross-validation
estimator"* (p. 242). **Cercano, no igual:** el escenario del artículo son
divisiones aleatorias independientes, no la partición en `K` bloques disjuntos
de la validación cruzada `K`-fold.

## La fórmula de la varianza corregida

**Sección 4 ("Inference about n1µ"), procedimiento 6, *"Corrected resampled
t-test statistic"*, p. 254** — en la notación del artículo:

    Estimador insesgado de ⁿ²ₙ₁σ²_J :   ( 1/J + ρ/(1−ρ) ) · S²_{μ̂_j}

donde `S²_{μ̂_j}` es la varianza muestral de las `μ̂_j` y `ρ` la correlación
entre ellas, desconocida. El t remuestreado ingenuo toma `ρ = 0`. La corrección
toma `ρ = ρ₀ = n2/(n1+n2)`, apoyándose en el argumento de la Sección 3, y como
`ρ₀/(1−ρ₀) = n2/n1` queda:

    σ̂² = ( 1/J + n2/n1 ) · S²_{μ̂_j}

con valor crítico

    c = t_{J−1, 1−α/2}

**La advertencia de los propios autores, en su única cita literal de este
archivo:** *"We must say again that this approximation is gross"* (p. 254).
La justifican porque es mejor que suponer `ρ = 0`, y porque, si `ρ` resulta
menor que `ρ₀`, la inferencia sale conservadora, que prefieren a liberal
(pp. 254–255, paráfrasis).

---

## Verificación contra la implementación del proyecto — COINCIDE

**Qué implementa** `.claude/skills/modelado-baseline/scripts/evaluar_repetido.py`,
función `_nadeau_bengio`, líneas 99–116: `varianza · (1/n + 1/(n_splits − 1))`
con `df = n − 1`.

**Correspondencia con el artículo:**

| Artículo | Implementación | Valor aquí |
|---|---|---|
| `J` | `n`, número de diferencias | 50 (10 semillas × 5 folds) |
| `n2/n1` | `1/(n_splits − 1)` | 0,25 (5-fold: prueba 1/5, entrenamiento 4/5) |
| `S²_{μ̂_j}` | `np.var(diffs, ddof=1)` | 0,00018595 |
| `t_{J−1, 1−α/2}` | `stats.t.ppf(0.975, df=n − 1)` | t(0,975; 49) = 2,009575 |

**No por lectura, por cálculo.** Se escribió la fórmula del artículo desde el
texto, sin importar la función del script, y se aplicó a las 50 diferencias de
`outputs/validacion-repetida.json > comparacion_pareada_2b_menos_1.diferencias`:

| | Intervalo 95% |
|---|---|
| Fórmula del artículo, sin redondear | [−0,001711; 0,026767] |
| Fórmula del artículo, a 4 decimales | **[−0,0017; 0,0268]** |
| `intervalo_t_95_nadeau_bengio` guardado | **[−0,0017; 0,0268]** |

**Y la comparación puede fallar** — se comprobó que distingue la fórmula
correcta de variantes plausibles pero equivocadas:

| Variante | Intervalo | ¿Coincide? |
|---|---|---|
| Artículo: `(1/J + n2/n1)`, `df = J−1` | [−0,0017; 0,0268] | **sí** |
| Ingenuo, `ρ = 0`: `(1/J)` | [0,0087; 0,0164] | no |
| `n2/n1` mal tomado como `1/k = 0,20` | [−0,0003; 0,0254] | no |
| `J = 5`, una sola semilla | [−0,0129; 0,0379] | no |
| Solo `n2/n1`, sin el `1/J` | [−0,0012; 0,0262] | no |
| `df = J` en vez de `J − 1` | [−0,0017; 0,0268] | **sí — indistinguible** |

**El único punto que el cálculo no puede decidir** es `df = J−1` frente a
`df = J`: a 4 decimales dan lo mismo. Ese se confirma **leyendo los dos
lados**, y coinciden: el artículo dice `t_{J−1}` y el código `df = n − 1`.

**Sensibilidad a `n2/n1`.** Con folds agrupados por paciente los tamaños no son
exactamente iguales. En `outputs/diseno-validacion.json > por_fold`, la razón
prueba/entrenamiento en **pacientes** va de 0,2479 a 0,2524 (en filas es
0,2500 en los cinco). Con el rango observado, el intervalo se mueve en el
cuarto decimal —[−0,0017; 0,0267] a [−0,0018; 0,0268]— y **sigue conteniendo
el cero**. La conclusión del proyecto no depende de usar el valor nominal.

---

## Salvedad de aplicabilidad — la implementación extiende el artículo

**El número coincide; el escenario no es exactamente el del artículo.** La
fórmula se deriva para `J` divisiones aleatorias **independientes** entre sí.
El proyecto la aplica a validación cruzada 5-fold **repetida con 10 semillas**:
entre semillas las particiones sí son independientes, pero **dentro** de cada
semilla los 5 conjuntos de prueba son disjuntos y complementarios, que es una
estructura de dependencia distinta de la que el artículo analiza. Los propios
autores solo llaman a su variante *cercana* al K-fold, y a su aproximación,
burda incluso en su propio escenario.

**Si esa extensión está justificada en la literatura, este archivo no lo
establece.** No se cita aquí ninguna fuente que la respalde, y no se va a
completar de memoria. Queda como pendiente: o se versiona una fuente que
justifique aplicar la corrección a K-fold repetido, o el informe declara que la
aplica fuera del escenario de derivación. Lo que **no** cambia: el intervalo
corregido contiene el cero, el ingenuo no, y es el corregido el que el proyecto
cita.

---

## Sobre la desviación de la regla 3

La regla 3 pide que un archivo de `referencias/` contenga el texto original.
Este no lo hace, porque reproducir un artículo con copyright y sin licencia
abierta en un repositorio público no es algo que el agente haga. Lo que sí
garantiza: cada afirmación lleva página y sección, la fórmula está en la
notación del artículo, la única cita literal está entrecomillada, todo lo demás
está marcado como paráfrasis, y la verificación numérica está entera aquí y es
reproducible desde `outputs/`. **Cómo debe tratar la regla 3 a las fuentes con
copyright es una decisión del proyecto, no del agente.**

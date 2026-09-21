# Yang, Lu, Lyu y Hu — "Two-Way Partial AUC and Its Properties" (FICHA)

**Autores:** Hanfang Yang (autor de correspondencia, School of Statistics,
Renmin University of China), Kun Lu, Xiang Lyu, Feifang Hu.

**Doble publicación — las dos referencias, porque no son la misma cosa:**

| | Preprint | Versión de revista |
|---|---|---|
| Dónde | arXiv:1508.00298 [stat.ME] | Statistical Methods in Medical Research |
| Año | enviado 3 ago 2015; v3 del 21 jun 2017 | 2019 ene; 28(1):184–195 |
| DOI | 10.48550/arXiv.1508.00298 | 10.1177/0962280217718866 |
| Otros | — | Epub 14 jul 2017 · PMID 28707503 |

La versión de revista se verificó en PubMed; la entrada de arXiv **no la
declara**. **La versión citable es la de 2019; las citas de abajo son del
preprint v3**, que es el texto accesible, y no se han cotejado con la
publicada. Se citan como del preprint.

**Fecha de consulta:** 2026-09-19.
**URL del preprint:** https://arxiv.org/abs/1508.00298

**LICENCIA: con copyright → FICHA.** Los autores publicaron el preprint bajo la
**licencia no exclusiva de distribución de arXiv 1.0**
(http://arxiv.org/licenses/nonexclusive-distrib/1.0/), que autoriza a arXiv a
distribuirlo y no a terceros; la versión de revista (SAGE) solo tiene
depositada en Crossref una licencia de minería de textos. Ninguna es abierta.
Verificado el 2026-09-21 en la página de arXiv y en `api.crossref.org`.

**Texto completo:** en local, `referencias/_texto-completo/yang-arxiv-1508.00298v3.pdf`
y su texto extraído, `yang-arxiv-1508.00298v3.txt`.

---

## Citas literales que el proyecto usa

Del preprint v3, página del PDF entre corchetes. **Las ligaduras `ﬁ` se
conservan tal como salen de la extracción del PDF**, para que cada cita case
carácter a carácter con el texto completo local.

**Resumen [p. 1]** — la tesis del artículo:

> However, its indirect control on TPR is conceptually and practically
> misleading.

**Introducción [p. 2]** — el límite inferior artificial:

> Unlike utilizing an artiﬁcial FPR lower bound to indirectly control
> acceptable TPR

**Escenario 1 de la Figura 2 [p. 4]** — el área sobrante distorsiona la
comparación:

> The redundant unethical area, S2, distorts the comparison of two classiﬁers.

**Remark 3.1 [p. 7]** — la crítica al *FPR pAUC*, formulada:

> Previous works, instead, utilize an synthetic approach, namely FPR pAUC here,
> to put an indirect lower restric-
> tion on TPR via artiﬁcially setting a corresponding FPR lower bound (6).

**Remark 3.2 [p. 7]** — el caso simétrico, el *TPR pAUC*:

> Similar to FPR pAUC, there exists another indirect synthetic approach, named
> as TPR pAUC (11).

> its philosophy is to indirectly prevent FPR from being too high via setting an
> artiﬁcial upper bound on TPR.

*"an synthetic" es así en el original.*

## Localizadores del resto — sin texto

- p. 2, Introducción: definición del *FPR pAUC* con límites `p1` y `p2`.
- p. 4, Figura 1: región A (two-way pAUC) frente a A + B (FPR pAUC).
- Sección 3: estimador no paramétrico del two-way pAUC y su normalidad
  asintótica.
- Sección 5: estudio numérico de eficiencia (potencia) frente al *FPR pAUC*.
- Aplicación: *Wisconsin Breast Cancer Data*; paquete de R `tpAUC`.

---

## Qué relación tiene con este proyecto — CORREGIDO el 2026-09-19

> **Una versión anterior de este archivo afirmaba que la métrica de ISIC 2024
> "es exactamente un *FPR pAUC* en el sentido de este artículo". Es falso.**
> La afirmación se escribió sin comprobarla contra el script oficial; al ir a
> buscar la línea que la respaldara, resultó que no existe. Se deja el error
> anotado en vez de borrarlo, porque el modo de fallo —una lectura plausible
> dada por buena sin abrir el código— es el que el proyecto registra.

### Qué hace realmente el script oficial

Líneas del script original `PrimaryMetric-pAUC.py`, cuya ficha es
`referencias/isic-primary-metric-pauc.py.md`. Entre paréntesis, el número que
tenían en la copia versionada hasta el 2026-09-21, que es el que usaban las
citas escritas antes de esa fecha:

| Línea | Código | Qué hace |
|---|---|---|
| 42–43 (54–55) | `v_gt = abs(np.asarray(v_gt)-1)` y lo mismo con `v_pred` | **invierte etiquetas y puntajes** |
| 44 (56) | `max_fpr = abs(1-min_tpr)` | deriva el tope del umbral de sensibilidad |
| 47 (59) | `fpr, tpr, _ = sklean.roc_curve(v_gt, v_pred, ...)` | ROC **sobre las etiquetas ya invertidas** |
| 54, 58 (66, 70) | `stop = np.searchsorted(fpr, max_fpr, "right")` … `fpr = np.append(fpr[:stop], max_fpr)` | trunca en el eje `fpr` |
| 59 (71) | `partial_auc = sklean.auc(fpr, tpr)` | integra con `fpr` como eje x |

**La línea 42 lo cambia todo.** Como las etiquetas están invertidas, la variable
que el código llama `fpr` **no es el FPR del problema original**: es
`1 − TPR_original`. Acotarla por arriba con `max_fpr = 1 − min_tpr` equivale
entonces a acotar `TPR_original ≥ min_tpr`, **directamente**. La métrica es una
restricción **vertical sobre el TPR**, y **no impone ninguna restricción sobre
el FPR**: la región integrada incluye cualquier FPR mientras el TPR supere el
umbral.

### Comprobación, no deducción

Se corrió el script oficial contra las dos hipótesis, con seis semillas
(n = 20.000, prevalencia 2%, `min_tpr = 0.80`):

| Semilla | Script oficial | (A) área con TPR ≥ 0,80 | (B) pAUC con FPR ≤ 0,20 |
|---|---|---|---|
| 0 | 0,080512 | **0,080512** | 0,081155 |
| 1 | 0,091335 | **0,091335** | 0,085318 |
| 2 | 0,089962 | **0,089962** | 0,093062 |
| 3 | 0,079038 | **0,079038** | 0,084093 |
| 4 | 0,083016 | **0,083016** | 0,083691 |
| 5 | 0,082145 | **0,082145** | 0,084461 |

Seis de seis coinciden con (A) al dígito y ninguna con (B). El máximo teórico de
(A) es `1 − 0,80 = 0,2`, que es el rango `[0.0, 0.2]` que documenta Kaggle
(`referencias/kaggle-evaluation.md`) — coincidencia que (B) no explica por sí
sola pero que junto a la tabla cierra el caso.

### Qué se sigue, y qué no

- **La crítica central de Yang et al. NO aplica a ISIC 2024.** Su objeto es el
  *FPR pAUC*: un límite **inferior artificial sobre el FPR** usado para
  controlar el TPR de forma indirecta. ISIC no hace eso — su restricción sobre
  el TPR es explícita y directa. Ninguna frase del informe puede decir que la
  métrica del cliente incurre en el defecto que este artículo describe.
- **Tampoco es el *TPR pAUC* del Remark 3.2**, que pone un límite **superior**
  artificial sobre el TPR para frenar el FPR. ISIC integra hasta TPR = 1 y no
  tiene ese segundo límite.
- **Lo que sí conecta — y es lectura nuestra, no del artículo.** El argumento
  general de fondo es que restringir un solo eje deja el otro sin controlar.
  ISIC fija el TPR y no acota el FPR en absoluto. Que eso sea un defecto
  depende de si al cliente le importa un techo de FPR, y por su propio artículo
  de 2025 parece que sí: definen `NNTx% SE`, una métrica de precisión
  (`referencias/kurtansky-2025-triaje-automatizado-tbp.md`). Esa conexión es
  defendible y es la que vale la pena desarrollar — pero se presenta como
  razonamiento propio apoyado en el marco de Yang et al., nunca como algo que
  el artículo diga sobre ISIC.

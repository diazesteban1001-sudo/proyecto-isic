# CatBoost — documentación de los parámetros de entrenamiento

**Fuente:** documentación oficial de CatBoost, tres páginas:
- *Common parameters*: https://catboost.ai/docs/en/references/training-parameters/common
- *Overfitting detection settings*: https://catboost.ai/docs/en/references/training-parameters/overfitting-detection
- *Output settings*: https://catboost.ai/docs/en/references/training-parameters/output

**Fecha de consulta:** 2026-09-26.
**Cómo se tomó:** con `curl`, que devolvió el HTML de cada página (código 200).
Las citas se comprobaron carácter a carácter en dos lecturas del HTML, una que
cambia cada etiqueta por un espacio y otra que la borra sin más. Se omiten las
etiquetas y los `<script>`, y los espacios seguidos quedan en uno. El HTML y el
texto están en local, en `referencias/_texto-completo/catboost-docs/`.
**Versión:** la página no dice a qué versión de CatBoost corresponde. Es la
documentación vigente el día de la consulta. El proyecto usa catboost 1.2.8, y
el ganador fijó la 1.2.5 (`requirements.txt` de su repositorio, copia local en
`referencias/_texto-completo/novoselskiy-2024-isic2024-repo/`).

**LICENCIA: DESCONOCIDA → FICHA.** Las páginas no declaran licencia para su
texto: no aparecen «License», «Copyright» ni «©». Buscado el 2026-09-26 en el
texto de *Common parameters*.

---

## Citas literales

**`bootstrap_type`**, valor por defecto (*Common parameters*):

> "Neither MultiClass nor MultiClassOneVsAll, task_type = CPU and sampling_unit = Object: MVS with the subsample parameter set to 0.8."

> "Otherwise: Bayesian."

**`bagging_temperature`** (*Common parameters*):

> "This parameter can be used if the selected bootstrap type is Bayesian."

**`use_best_model`** (*Common parameters*), descripción y valor por defecto:

> "No trees are saved after this iteration."

> "True if a validation set is input (the eval_set parameter is defined) and at least one of the label values of objects in this set differs from the others."

**`od_pval`** y **`od_wait`** (*Overfitting detection settings*):

> "0 (the overfitting detection is turned off)"

> "Iter — Consider the model overfitted and stop training after the specified number of iterations since the iteration with the optimal metric value."

**`metric_period`** (*Output settings*):

> "The frequency of iterations to calculate the values of objectives and metrics."

---

## Para qué la usa el proyecto *(nuestro)*

Especificación de M3, `PLAN.md`, Fase 4. El ganador entrena en GPU
(`top-model.ipynb`, celda 22: `task_type='GPU'`). Nosotros entrenamos en CPU.

- **El bootstrap.** En CPU, con `Logloss`, el valor por defecto es MVS, y
  `bagging_temperature` solo se aplica con el bayesiano. En GPU el valor por
  defecto es el bayesiano, por el «Otherwise». Por eso M3 fija
  `bootstrap_type="Bayesian"`: sin eso, el `bagging_temperature` publicado no
  tendría efecto. Comprobado con catboost 1.2.8 en CPU. Con los parámetros
  publicados y sin `bootstrap_type`, `get_all_params()` da
  `bootstrap_type='MVS'` y `bagging_temperature=None`.
- **El número de árboles del publicado depende del pliegue de validación.** La
  celda 22 pasa ese pliegue como `eval_set`. Con eso, `use_best_model` vale
  `True` y descarta los árboles posteriores a la mejor iteración en validación.
  *Observación nuestra, no de la documentación:* la página da `IncToDec` como
  valor por defecto de `od_type`, con `od_pval` en 0, es decir, sin detector.
  Pero con `od_wait=100` y sin `od_type`, catboost 1.2.8 en CPU activa el
  detector `Iter`: `get_all_params()` da `od_type='Iter'`, y en datos sintéticos
  el entrenamiento se detiene en la iteración 198 de 2000, con la mejor en la
  97. En GPU no se pudo comprobar.
- **`metric_period`.** En GPU el ganador evaluó el AUC cada 5 iteraciones: la
  salida de su celda 25 dice *"Default metric period is 5 because AUC is/are not
  implemented for GPU"*. En CPU, con el detector activo, catboost 1.2.8 avisa de
  que calcula la métrica de evaluación en cada iteración e ignora
  `metric_period`. Eso no se reproduce.

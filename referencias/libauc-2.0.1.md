# LibAUC 2.0.1 — la documentación de SOPA, `pAUC_CVaR_Loss` y `DualSampler`

**Qué es:** la librería de los autores de Zhu et al. 2022
(`referencias/zhu-2022-sopa-pauc-dro.md`) para optimizar el AUC y la pAUC en
aprendizaje profundo. Para este proyecto, su documentación son las docstrings
del código de la versión instalada; la web de la librería no se consultó.
**Paquete:** `libauc` 2.0.1, de PyPI, la rueda `libauc-2.0.1-py3-none-any.whl`,
SHA-256 `416039daded4a79e5a88b4cc843a7a18efc64b1e254512804984f4de058ba31f`
(publicada el 2026-06-24 según https://pypi.org/pypi/libauc/2.0.1/json), la
misma que está instalada en el `.venv/` (`pip install --no-deps
--require-hashes`). Repositorio declarado: https://github.com/Optimization-AI/LibAUC.
**Fecha de consulta:** 2026-11-01.

**LICENCIA: MIT → los originales se versionan intactos**, en
`referencias/libauc-2.0.1/`, con su `LICENSE` (*"MIT License"*, *"Copyright (c)
2023 OptMAI"*, el archivo `licenses/LICENSE` de la rueda). MIT autoriza copiar y
redistribuir con el aviso de copyright y de permiso, que es ese archivo. Como en
`referencias/novoselskiy-2024-isic2024.md`, la procedencia va en este `.md` y no
dentro de los archivos.

| Archivo en `referencias/libauc-2.0.1/` | SHA-256 |
|---|---|
| `LICENSE` | `efb8aef9961930702e18e29c2c370ca757b483cd909b9de7f606d0a58612173f` |
| `libauc/optimizers/sopa.py` | `35c1f2a74d8106346068a6d7a525cc9e517772e86fe05623586da161ab61d6ca` |
| `libauc/losses/auc.py` | `71b38dd8c6b9d6f25fa36ba3ee1abcde1862a9cd5661c81fe9523ee3690775ae` |
| `libauc/sampler/sampler.py` | `2feeae4e57aaf63ec4894423d16327ea920b9202032b93e634ff9637da7daae6` |

Cada uno coincide con el hash que registra el `RECORD` de la rueda instalada
(comprobado el 2026-11-01). Solo se versionan estos tres módulos: son los que
usa el proyecto.

---

## Lo que usa el proyecto *(sección nuestra)*

`PLAN.md`, Fase 4e, paso 2. Por la regla de la persona del 2026-11-01, lo que
Zhu et al. 2022 no fija se toma de esta documentación, y la documentación manda
sobre la firma de las funciones cuando no coinciden. Las líneas son las de los
archivos versionados.

**SOPA, la documentación** (`libauc/optimizers/sopa.py`, líneas 26 a 35):

```
            lr (float): learning rate (default: ``0.1``)
            mode (str): optimization mode, 'sgd' or 'adam' (default: ``'sgd'``)
            weight_decay (float, optional): weight decay (L2 penalty) (default: ``1e-5``)
            epoch_decay (float, optional): epoch decay (epoch-wise l2 penalty) (default: ``0.0``)
            momentum (float, optional): momentum factor for 'sgd' mode (default: ``0.9``)
            betas (Tuple[float, float], optional): coefficients used for computing
                running averages of gradient and its square for 'adam' mode (default: ``(0.9, 0.999)``)
            eps (float, optional): term added to the denominator to improve
                numerical stability for 'adam' mode (default: ``1e-8``)
            amsgrad (bool, optional): whether to use the AMSGrad variant of 'adam' mode
```

**SOPA, la firma, que no coincide** (líneas 56 a 60):

```
                 mode='adam', 
                 eta=1.0, 
                 lr=1e-3, 
                 clip_value=1.0,
                 weight_decay=0, 
```

El argumento `eta` no aparece en el código del resto del archivo, y
`clip_value` no está en la documentación: en el modo `'adam'`, el gradiente se recorta a ese valor, elemento
a elemento, antes de sumarle el decaimiento de pesos (línea 173):

```
                    grad = torch.clamp(p.grad.data , -clip_value, clip_value) + weight_decay*p.data
```

**`pAUC_CVaR_Loss`, la documentación** (`libauc/losses/auc.py`, líneas 392 a
397 y 425 a 429):

```
            data_len (int):  total number of samples in the training dataset.
            pos_len (int): total number of positive samples in the training dataset.
            margin (float, optional): margin term for squared-hinge surrogate loss (default: ``1.0``).
            beta (float): upper bound of False Positive Rate (FPR) used for optimizing pAUC (default: ``0.2``).
            eta (float): stepsize for update the dual variables for DRO-CVaR formulation (default: ``0.1``).
            surr_loss (string, optional): surrogate loss used in the problem formulation (default: ``'squared_hinge'``).
```

```
            Practical tips: 

            - ``margin`` can be tuned in ``{0.1, 0.3, 0.5, 0.7, 0.9, 1.0}`` for better performance.
            - ``beta`` can be tuned in the range (0.1, 0.9), ideally based on task requirement for FPR.
            - ``eta`` can be tuned in ``{10, 1.0, 0.1, 0.01}`` for better performance. 
```

**`pAUC_CVaR_Loss`, el código que importa para el muestreo.** Una variable dual
por caso, todas en 0 al empezar (línea 458); se detiene si un lote no trae casos
de las dos clases (líneas 474 y 478), y cada llamada actualiza la variable dual
de los positivos del lote, una vez, con el paso `eta` (línea 485):

```
        self.u_pos = torch.tensor([0.0]*data_len).reshape(-1, 1).to(self.device).detach()               
```

```
           assert self.num_neg > 0, 'There is no negative sample in the data!'
```

```
        assert sum(pos_mask) > 0, "Input data has no positive sample! Please use 'libauc.sampler.DualSampler' for data resampling!"
```

```
        self.u_pos[index] = self.u_pos[index]-self.eta*(1 - p.sum(dim=1, keepdim=True)/(self.beta*self.num_neg))
```

**`DualSampler`, la documentación** (`libauc/sampler/sampler.py`, líneas 171,
174, 176 y 189):

```
            sampling_rate (float): the ratio of number of positive samples to total number of samples per task in a mini-batch (default: ``0.5``).
```

```
            shuffle (bool): Whether to shuffle the data before sampling mini-batch data (default: ``True``).
```

```
            random_seed (int): random seed for reproducibility (default: ``2023``).
```

```
            - For ``sampling_rate``, we recommended to set a value slightly higher than the proportion of positive samples in your training dataset. For instance, if the ratio of positive sample in your dataset is 0.01, you might consider setting ``sampling_rate`` to 0.05, 0.1, or 0.2.
```

**`DualSampler`, cuánto dura su época** (línea 219): tantos lotes como haga
falta para recorrer la clase más larga una vez, repitiendo la otra.

```
        self.num_batches = max(self.pos_len//self.num_pos, self.neg_len//self.num_neg)
```

<!--
Fuente: https://raw.githubusercontent.com/ISIC-Research/Challenge-2024-Metrics/main/PrimaryMetric-pAUC.py
Copia literal tomada el 2026-08-11 por el agente (raw.githubusercontent.com sí es legible sin sesión).

Motivo: el notebook oficial de Kaggle (kaggle.com/code/metric/isic-pauc-abovetpr) NO es
legible por el agente — devuelve solo el shell de JavaScript, igual que el resto de Kaggle.
Este script del organizador (Nicholas R Kurtansky, MSKCC) es la implementación de
referencia del pAUC y sí es citable desde un archivo versionado, según la regla 3.
Kaggle y el organizador difieren solo en el valor de min_tpr (0.80 vs 0.88), que aquí
es un parámetro; el algoritmo es el mismo. Para este proyecto: min_tpr = 0.80.
-->

"""
pAUC_metric.py
-----------------

2024 ISIC Challenge primary prize scoring algorithm

Given a list of binary labels, an associated list of prediction 
scores ranging from [0,1], this function produces, as a single value, 
the partial area under the receiver operating characteristic (pAUC) 
above a given true positive rate (TPR).
https://en.wikipedia.org/wiki/Partial_Area_Under_the_ROC_Curve.

(c) 2024 Nicholas R Kurtansky, MSKCC
"""

#Primary scoring metric: pAUC

#IMPORTS 

import numpy as np
import sklearn.metrics as sklean


def p_auc_tpr(v_gt, v_pred, min_tpr=None, sample_weight=None):
    """Computes the area under the AUC above a minumum TPR.

    Args:
        v_gt: ground truth vector (1s and 0s)
        v_p: predictions vector of scores ranging [0, 1]
        min_tpr: minimum true positive threshold (sensitivity)

    Returns:
        Float value range [0, 1]
    """
    if len(np.unique(v_gt)) != 2:
        raise ValueError(
            "Only one class present in y_true. ROC AUC score "
            "is not defined in that case."
        )
    
    # redefine the target. set 0s to 1s and 1s to 0s
    v_gt = abs(np.asarray(v_gt)-1)
    v_pred = abs(np.asarray(v_pred)-1)
    max_fpr = abs(1-min_tpr)
    
    # using sklearn.metric functions: (1) roc_curve and (2) auc
    fpr, tpr, _ = sklean.roc_curve(v_gt, v_pred, sample_weight=sample_weight)
    if max_fpr is None or max_fpr == 1:
        return sklean.auc(fpr, tpr)
    if max_fpr <= 0 or max_fpr > 1:
        raise ValueError("Expected min_tpr in range [0, 1), got: %r" % min_tpr)

    # Add a single point at max_fpr by linear interpolation
    stop = np.searchsorted(fpr, max_fpr, "right")
    x_interp = [fpr[stop - 1], fpr[stop]]
    y_interp = [tpr[stop - 1], tpr[stop]]
    tpr = np.append(tpr[:stop], np.interp(max_fpr, x_interp, y_interp))
    fpr = np.append(fpr[:stop], max_fpr)
    partial_auc = sklean.auc(fpr, tpr)
    return(partial_auc)


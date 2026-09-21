# Anteproyecto

## 1. Problema y estado actual

## 2. Estado del arte

## 3. Objetivos

Objetivo general. Establecer un procedimiento de evaluación para modelos de triaje de melanoma sobre el conjunto SLICE-3D que priorice la función de utilidad declarada por el organizador, y determinar en qué medida las decisiones metodológicas por defecto —métrica, tratamiento del desbalance y esquema de partición— alteran el veredicto sobre un modelo.
Objetivos específicos.

1. Construir un esquema de evaluación libre de fuga: cuantificar la fuga de una partición por registro frente a una agrupada por paciente, identificar las variables no disponibles al momento de predecir y reservar un conjunto de pacientes que se evalúe una sola vez. Se declara cumplido con la proporción de pacientes presentes a ambos lados de cada partición, el listado de variables excluidas con su motivo y el conjunto reservado sellado antes de cualquier modelado.
2. Estimar el desempeño de cuatro niveles de referencia bajo la métrica oficial y bajo el AUC estándar, sobre los mismos pliegues. Se declara cumplido con las medias y las series por pliegue de ambas métricas, y con los casos donde las dos discrepan en el veredicto.
3. Contrastar los niveles mediante comparación pareada con validación cruzada repetida, corrigiendo la varianza por el solape entre conjuntos de entrenamiento. Se declara cumplido con el intervalo de confianza de la diferencia en sus versiones ingenua y corregida.
4. Evaluar los niveles bajo los ejes de triaje que definen los organizadores —sensibilidad en las quince lesiones de mayor riesgo por paciente y número de lesiones a derivar por maligna detectada— para determinar si el veredicto de la métrica principal se sostiene sobre la función de utilidad completa. Se declara cumplido con la tabla de los tres ejes por nivel y con la implementación contrastada contra el orden de magnitud publicado.
5. Incorporar características derivadas de imagen, previa verificación de que el conjunto no estuvo en el preentrenamiento del modelo fundacional empleado, y evaluar el modelo recomendado sobre el conjunto reservado. Se declara cumplido con el resultado de esa verificación y con las métricas del conjunto reservado reportadas con su intervalo.

## 4. Datos y método

## 5. Alcance y plan

## 6. Declaración de uso de IA y reparto del trabajo

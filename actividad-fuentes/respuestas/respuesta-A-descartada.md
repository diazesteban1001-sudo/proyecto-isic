Corrida descartada: la búsqueda web estaba activa, así que no cumple la definición del tratamiento A del protocolo. No se clasifica. Se conserva como desviación declarada.

Guardada el 2026-09-27 a las 18:47:07 (-0500).

---

Voy a buscar estudios que cuantifiquen ese efecto de fuga de datos (data leakage) en dermatología y a verificar cada DOI.Encontré pocos estudios en dermatología que midan directamente esa diferencia con el mismo modelo y los mismos datos. Varias de las referencias más citadas son auditorías de datos: cuantifican cuánta fuga hay, pero no cuánto se infla la métrica. Indico en cada caso qué tipo de evidencia aporta.
1. Medición directa de la inflación (partición por imagen aumentada frente a partición por lesión)
Artículo sobre clasificación híbrida cuántico-clásica en HAM10000, IEEE Access, 2026.

* Qué encontró: Al partir el conjunto de imágenes ya aumentadas, 1.095 de 4.810 lesiones (22,8 %) quedaban a ambos lados de la partición, lo que inflaba todas las métricas reportadas.
* Cuánto se sobreestimó: Con una partición verificada por lesión, la mejor configuración logra 78,41 % ± 0,74 de exactitud, frente al 94,57 % obtenido con el protocolo sin corregir. Son unos 16 puntos.
* DOI: 10.1109/ACCESS.2026.3707673. Lo tomé de la versión aceptada del autor, así que conviene confirmarlo en IEEE Xplore.

2. Auditoría de fuga por lesión en DermaMNIST/HAM10000 y de duplicados en Fitzpatrick17k
Abhishek, Jain y Hamarneh, Scientific Data, 2025.

* Fuga en DermaMNIST: 1.006 de las 7.470 lesiones únicas (~13,47 %) aparecen en más de una partición.
* Fitzpatrick17k: Tras la limpieza, el conjunto de prueba "Verified" se redujo en ~38 %. Los autores concluyen que 133 imágenes eran duplicados, lo que explica por qué los resultados de referencia estaban inflados.
* Matiz importante: Los autores advierten que los resultados de DermaMNIST y DermaMNIST-C no deben compararse, porque los modelos se entrenaron y evaluaron en particiones distintas. Por tanto, no cuantifican la inflación en HAM10000, solo la extensión de la fuga.
* DOI: 10.1038/s41597-025-04382-5

3. Partición por paciente frente a partición por lesión: evidencia de que la diferencia puede ser pequeña
"Skin Lesion Phenotyping via Nested Multi-modal Contrastive Learning" (SLIMP), preprint de arXiv.

* Qué comparó: Evaluó particiones disjuntas por paciente, con todas las lesiones de un mismo paciente en la misma partición.
* Qué encontró: Los resultados por paciente caen dentro del rango de variación de las particiones por lesión con varias semillas en PAD-UFES-20, HIBA y HAM10000. En algunos casos incluso superan el promedio por lesión.
* Por qué importa: Sugiere que la mayor parte de la inflación viene de separar imágenes de la misma lesión, más que de separar lesiones de un mismo paciente.
* DOI: 10.48550/arXiv.2505.23709. Es el DOI de arXiv; no verifiqué si ya tiene versión publicada.

4. Duplicados dentro y entre las ediciones de ISIC
Cassidy et al., Medical Image Analysis, 2022.

* Qué encontró: El trabajo busca señalar los sesgos que produce usar imágenes duplicadas de los conjuntos ISIC.
* Qué propone: Una estrategia para eliminar duplicados y dos conjuntos curados, para evitar sesgos en la evaluación de algoritmos.
* Limitación: Documenta el riesgo de solapamiento entre entrenamiento y prueba, pero no compara particiones por paciente.
* DOI: 10.1016/j.media.2021.102305

5. Casi-duplicados en benchmarks de evaluación dermatológica
Gröger et al., ML4H 2023 (PMLR 225).

* Qué encontró: Con confirmación de dermatólogos, el número de casi-duplicados crece con el tamaño del conjunto hasta un 2–3 %, incluso en conjuntos muy curados.
* Limitación: Cuantifica la contaminación, no la inflación del desempeño.
* DOI: PMLR no asigna DOI. El del preprint es 10.48550/arXiv.2309.06961.

En resumen: Solo la referencia 1 mide directamente la sobreestimación, y su fuga es un caso particular (aumentación de datos antes de partir). Si necesitas una cifra de inflación medida con rigor para citar, el trabajo de referencia más usado es de otro campo: en OCT, Tampu et al. hallaron que la partición incorrecta infla el desempeño entre 0,07 y 0,43 de MCC (5 % a 30 % de exactitud) (DOI 10.1038/s41597-022-01618-6).
Una auditoría en GitHub, no revisada por pares, estima que en HAM10000 una partición aleatoria por imagen deja en entrenamiento una imagen "hermana" de cerca del 40 % de las imágenes de prueba (70 % de los melanomas). No es citable como artículo, pero muestra la magnitud del problema.

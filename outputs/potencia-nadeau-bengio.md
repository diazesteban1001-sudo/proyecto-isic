# Potencia de la prueba de Nadeau y Bengio frente a M3 limpio (descriptivo)

Diferencias pliegue a pliegue de la pAUC de C4 a C7 − M3 limpio, cada una por separado. «A favor»: valor p bilateral < 0.05 y media > 0. Potencia con la t no central, bajo el modelo de varianza de la prueba (ρ = 1/5), con la s de cada comparación.

| Comparación | s | δ al 50 %, n = 25 | δ al 80 %, n = 25 | δ al 50 %, n = 50 | δ al 80 %, n = 50 |
|---|---|---|---|---|---|
| C4 (semillas 0 a 9) | 0.0081 | 0.0089 | 0.0127 | 0.0084 | 0.0120 |
| C5 (semillas 0 a 9) | 0.0085 | 0.0093 | 0.0133 | 0.0088 | 0.0126 |
| C6 (semillas 0 a 4) | 0.0073 | 0.0080 | 0.0115 | 0.0076 | 0.0109 |
| C7 (semillas 5 a 9) | 0.0101 | 0.0111 | 0.0159 | 0.0105 | 0.0150 |

Entre semillas, error estándar de la media frente al de la prueba: C4 0.0006 frente a 0.0042; C5 0.0008 frente a 0.0044; C6 0.0011 frente a 0.0039; C7 0.0010 frente a 0.0054.

Controles: 82 de 82 casos como se esperaba (41 deben fallar y fallan). Simulación con el generador de la 4d: 20000 juegos por comparación y n, semilla 2026. La curva completa está en outputs/potencia-nadeau-bengio-curva.json, fuera del corpus del verificador. No interpreta.

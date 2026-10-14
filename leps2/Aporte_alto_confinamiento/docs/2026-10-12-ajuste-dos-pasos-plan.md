# Ajuste en dos pasos: plan de implementación

**Objetivo:** calcular m, φ′1 por set, ω y φ′e=0 según `2026-10-12-ajuste-dos-pasos-design.md` y compararlos con la curva vigente.
**Arquitectura:** un script `analisis_antamina/a30_dos_pasos.py` (paso 1, paso 2, controles), JSON de salida y una figura.
**Herramientas:** Python con numpy, pandas, scipy (least_squares), matplotlib; `analisis/modelos.py` (sigma1, tau_leps2) y
`analisis/lepsp_r6.datos` (base mundial). Carpeta sin git: no hay commits.

## Restricciones globales
- Residuos de Antamina idénticos a a12 (ln q en TX con la tangencia de la Ec. 16; C_DS·ln τ en DS); m ≤ 1; ω = 20° solo si el criterio falla.
- Peso del mundo = 50 % del total (37/N_mundo por ensayo); sensibilidad 0, 25 % y 75 %.
- Normalización a e base con las Ecs. 27–29 (sobre φ′1).

### Tarea 1: paso 1 (m común, φ′1 por set)
- [ ] Control previo: con w = 0 y un φ′1 por set, la m debe acercarse a la de a18 (Antamina, nivel por set ≈ 1.00, límite 1).
- [ ] Implementar `paso1(w)` → dict(m, phi1_por_set, se); least_squares con parámetros [m, φ′1 de 13 sets de Antamina, φ′1 de cada set mundial].
- [ ] Bootstrap por sets estratificado (200 réplicas) para m.
- [ ] Imprimir m para w = 0, 0.25, 0.5, 0.75.

### Tarea 2: paso 2 (ω y φ′e=0)
- [ ] Regresión lineal φ′1_set = φ′e0 − ω·e₀_set (13 puntos); bootstrap por sets → intervalo 90 % de ω.
- [ ] Criterio de adopción (15–25°, ±10°); si falla, regresión conjunta con la base mundial (ordenadas por clase y Antamina, ω común, 50/50).
- [ ] Diagnóstico: ordenada por litología.

### Tarea 3: comparación y figura
- [ ] φ′s a 1, 4.6, 10 y 15 MPa frente a la curva vigente; cruces con las cotas; ensayos altos (a25) frente a la curva nueva.
- [ ] Figura φ′1–e (sets de Antamina, recta ajustada, clases de Leps 2.0) en `figuras_leps2/Fig_phi1_e.png`.
- [ ] Escribir `a30_dos_pasos.json`; informar al usuario antes de cambiar a12, la planilla y el memo.

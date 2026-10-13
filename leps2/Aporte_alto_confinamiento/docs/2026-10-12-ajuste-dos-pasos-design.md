# Ajuste de la curva Leps 2.0 de Antamina en dos pasos (diseño, 2026-10-12)

Pedido de WA: (1) ajustar m y φ′1 a la data de Antamina en el plano τ–σ′n, usando la data mundial con cierta ponderación
para el rango no cubierto por Antamina; (2) ajustar ω y φ′e=0 a la data de Antamina en el plano e–φ′1.

## Definiciones (verificadas en Cylwik et al. 2025)

| Símbolo | Definición en el paper | Dónde |
|---|---|---|
| φ′1 | Ángulo de fricción secante a σ′n = 10pa (≈ 1 MPa), «anchor stress»: ahí la resistencia no depende de m | Ec. 6, p. 2 |
| m | Coeficiente de curvatura de τ = tan φ′1 (10pa)^(1−m) σ′n^m | Ecs. 7–8, p. 2 |
| e | «Void ratio at start of test» (relación de vacíos inicial de la probeta; en el memo, e₀) | Tabla 2 y lista de símbolos, pp. 4 y 14 |
| ω | Pendiente de φ′1 frente a e (15–25° en la literatura; 20° propuesto) | Ec. 25, Fig. 10, p. 6 |
| φ′e=0 | Ordenada de φ′1 frente a e en e = 0 | Ec. 25, p. 6 |
| Ec. 26 | τ = tan(φ′e=0 − ω e) (10pa)^(1−m) σ′n^m | p. 8 |
| Ecs. 27–29 | Corrección por densidad sobre φ′1: φ′adj = −20°(e_obj − e); τ_cor = [tan(φ′1 + φ′adj) − tan φ′1](10pa)^0.1 σ′n^0.9 | p. 10 |
| Ec. 31 | φ′1 de un ensayo = atan[τ / ((10pa)^0.1 σ′n^0.9)] (con m = 0.9) | p. 10 |
| Conversión TX → σ′n, τ | Ecs. 13, 14 y 16, con la m del set; φ′1 y m por set con Solver (GRG), igualando σ′1 | pp. 3–4 |
| φ′1 por set (Figs. 8 y 10) | Ajuste de cada set con la Ec. 8 (φ′1 y m propios); cada set es un punto (φ′1, e) | p. 5 |
| Procedimiento propio | Set con varias presiones: φ′1 y m (Ec. 8); varias presiones y e: φ′e=0, m y ω (Ec. 26) | p. 8 |

Diferencia declarada con Cylwik: aquí los sets de Antamina comparten una m común (pedido de WA), en vez de una m por set.

## Paso 1: m común y φ′1 por set (plano τ–σ′n)

- Antamina: los 13 sets del ajuste (37 ensayos, con las mezclas); cada set con su φ′1 (a la e₀ del set).
- Mundo: sets de la base de Cylwik et al. con algún ensayo sobre 4.60 MPa (máximo σ′n de Antamina), con todos sus ensayos; cada
  set con su φ′1 libre (su nivel no se transfiere); aportan solo la curvatura.
- Una m común, m ≤ 1. Residuos: Antamina, ln q en triaxiales (tangencia, Ec. 16) y C_DS·ln τ en corte directo (como a12);
  mundo, ln τ con los pares σ′n–τ de la base.
- Peso: el conjunto mundial pesa lo mismo que el de Antamina (peso por ensayo mundial = 37/N_mundo). Sensibilidad: 0 (solo
  Antamina), 25 % y 75 %.
- Incertidumbre: bootstrap por sets, estratificado (Antamina y mundo por separado).

## Paso 2: ω y φ′e=0 (plano e–φ′1)

- Puntos: φ′1 de cada set de Antamina (paso 1) frente a la e₀ media del set (13 puntos), regresión lineal φ′1 = φ′e=0 − ω e.
- Criterio: si ω está entre 15° y 25° y su intervalo del 90 % (bootstrap por sets) es más estrecho que ±10°, se adopta.
- Si no: evaluar la data mundial con regresión conjunta en e–φ′1, ω común y ordenada propia para Antamina y para cada clase de la
  base (baja, moderada, alta), con peso 50/50; φ′1 de los sets mundiales con la m común del paso 1. Se informa antes de adoptar.
- Diagnóstico de confusión litología–densidad: regresión con ordenada por litología (mármol, hornfels, intrusivo, mezcla).

## Resultado

- Curva: τ = tan(φ′e=0 − ω e)(10pa)^(1−m) σ′n^m, e base 0.45.
- Comparación con la curva vigente (φ′e=0 = 48.10°, ω = 20°, m = 0.859): cotas de Indraratna y de Hawley y Cunning, ensayos altos
  (a25), φ′s a 1, 4.6, 10 y 15 MPa.
- Normalización de ensayos a e base con las Ecs. 27–29 (sobre φ′1), no con la regla simplificada sobre φ′s.
- Productos: script a30_dos_pasos.py y JSON; figura φ′1–e (como la Fig. 10); al aprobar los números: a12 y cadena, planilla
  (hoja Ajuste en dos pasos con fórmulas) y memo.

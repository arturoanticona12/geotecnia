# Análisis estadístico de la resistencia del desmonte de Antamina

Fuente de datos: `datos_antamina/base/` (verificada).

Programas, en este orden: `a1_sets.py`, `a2_densificacion.py`, `a3_efectos.py`, `a4_envolventes.py` y `figuras_antamina.py`.

## 1. Datos analizados

Se usaron 64 triaxiales drenados utilizables en 22 sets:

| Grupo | Ensayos |
|---|---|
| Gran escala, probetas de 0.6–1.0 m | 32 |
| Probetas de 6 in | 32 |

Se excluyeron:

- duplicados;
- ensayos detenidos antes de la falla;
- cíclicos;
- CU (análisis aparte);
- corte directo.

El máximo σ′3 es 2.45 MPa (hornfels). Falla: máximo desviador.

## 2. Resultados

### 2.1 Envolventes de gran escala casi lineales entre 0.5 y 2.5 MPa

El exponente m ajustado por set con probetas de 0.6–1.0 m va de 0.88 a 1.0. En la base mundial, la media es 0.86 (Figura A1). En el hornfels, la resistencia secante incluso aumenta con σ′3: de 41.4° a 1 MPa a 46.5° a 2.45 MPa.

### 2.2 Antamina frente a la población mundial

Mediana de φ′s en probetas de gran escala:

| σ′n (MPa) | Antamina | Base mundial |
|---|---|---|
| 0.5–1.5 | 40.2° | 41.9° |
| 1.5–3.0 | 41.1° | 40.3° |
| 3.0–6.0 | **39.9°** (P10 38.3°) | **37.8°** (P10 35.2°) |

A alta presión, el desmonte de Antamina ensayado es más resistente y menos disperso que la población mundial.

Frente a la previa de Leps 3.0, es decir, la clase de Cylwik et al. (2025) y e:

- el intrusivo puro (IDIEM 2025 y WSP 2024 C4) queda entre −0.1° y +0.8° de su clase tabulada («baja», pórfido de cuarzo-monzonita);
- las mezclas de intrusivo con 9–13 % de relave quedan entre +1.9° y +4.7° sobre esa clase;
- hornfels y mármol quedan entre −1.3° y +2.4° de lo previsto.

### 2.3 Densificación durante la consolidación (hipótesis respaldada en parte)

Dentro de cada set, el φ′1 implícito sigue a la relación de vacíos al inicio del corte (e_c) con R² = 0.63. Sin embargo:

- La pendiente es 72° por unidad de e (IC 90 %: 57–91°), 3.6 veces la de Cylwik et al. (2025), que es 20°.
- A la tasa mundial, la densificación explicaría cerca de un tercio del aplanamiento.
- e_c y σ′3 son colineales dentro de cada set, así que los datos no permiten separar las causas.

Las explicaciones compatibles con los datos son:

- densificación;
- granulometría muy bien gradada (Cu de 30 a 300);
- rotura que mejora el empaque.

### 2.4 Rotura: depende de la litología, no solo del esfuerzo

A igual σ′3, Antamina rompe en promedio menos que la base mundial: Bg de 17 % frente a 29 % a 1 MPa (Figura A2). Por litología:

| Litología | Bg | Efecto de la rotura sobre φ′ |
|---|---|---|
| Hornfels | 20–39 % en 1 m; 15 % en 6 in | φ′ aumenta |
| Mármol | 13–28 % en 1 m; 30 % en 6 in | φ′ disminuye (40° → 37°) |
| Intrusivo | 6–19 % | — |

Con densificación parecida (e_c de 0.31 a 0.20–0.22), el mármol pierde resistencia y el hornfels la gana. La diferencia apunta a la mineralogía: el clivaje de la calcita del mármol frente a los silicatos angulosos del hornfels. Además, el UCS directo de referencia del mármol es el más bajo del desmonte: 48 MPa.

### 2.5 Relave en co-disposición

| Ensayo | Contenido de relave | Efecto sobre φ′1 |
|---|---|---|
| WSP 2024 (0.6 m) | 9–13 % | Sube +1.8° respecto del intrusivo sin relave: el relave rellena vacíos |
| Golder 2021 (< 1 in, suelto) | 10 % → 50 % | Baja de 42.5° a 38.4° (unos −4°); la caída se concentra sobre 20 % |

Hasta unos 13 % de relave no hay pérdida de resistencia drenada. El efecto relevante del relave está en la permeabilidad y en la respuesta no drenada.

### 2.6 Escala

A σ′3 ≈ 1 MPa, el hornfels da 42.6° en probeta de 6 in y 41.5° en probeta de 1 m. El efecto es del orden de 1°.

## 3. Envolventes por litología (Leps 3.0 actualizado con Antamina, e = 0.42)

Ángulo secante φ′s (°) por σ′n, como P50 / P10, para un material nuevo de cada litología (Figura A3):

| Litología | % LE2 | 1 MPa | 3 MPa | 6 MPa | 10 MPa | 15 MPa |
|---|---|---|---|---|---|---|
| Hornfels | 19 | 42.2 / 38.2 | 40.2 / 36.3 | 39.0 / 34.8 | 38.2 / 33.5 | 37.5 / 32.4 |
| Intrusivo | 15 | 39.3 / 35.3 | 37.0 / 33.0 | 35.6 / 31.3 | 34.5 / 29.8 | 33.8 / 28.6 |
| Mármol | 39 | 39.1 / 35.0 | 35.6 / 31.7 | 33.5 / 29.2 | 32.0 / 27.2 | 30.8 / 25.6 |
| Caliza y margas (sin ensayos) | 27 | 38.9 / 34.0 | 34.5 / 29.9 | 31.9 / 26.9 | 30.1 / 24.6 | 28.7 / 22.8 |
| **Botadero LE2 (ponderado)** | 100 | 39.7 / 35.1 | 36.4 / 31.6 | 34.4 / 28.9 | 33.0 / 26.9 | 31.9 / 25.3 |

Los percentiles se calculan con la envolvente restringida a m ≤ 1, por muestreo exacto (`leps3.percentiles`). La versión anterior de esta tabla no aplicaba esa restricción. Las diferencias son de 0.4° o menos en el botadero y de hasta 1.5° en la mediana del hornfels a 15 MPa, que es la litología con m más cercano a 1.

Cómo leer la tabla:

- **Por encima de σ′n ≈ 4 MPa no hay ensayos de Antamina.** La envolvente se extrapola con el m posterior y su incertidumbre crece con el esfuerzo.
- **El P10 es para un punto.** La resistencia movilizada por una superficie de falla a escala de botadero promedia litologías y zonas, y es menos dispersa.
- **La varianza entre materiales** se tomó de la población mundial (Σ), lo cual es conservador para un solo yacimiento.

## 4. Implicancias para el diseño de botaderos de 700 m

1. **Mármol.** Es la litología dominante (39 %) y la que más pierde resistencia con el esfuerzo. Controla la resistencia en la base del botadero.
2. **Caliza y margas.** Son el 27 % del desmonte, sin ensayos. Su envolvente es la previa mundial, con la banda más ancha, y es el mayor aporte de incertidumbre.
3. **Hornfels e intrusivo.** A 3–6 MPa, los datos de gran escala son más resistentes que la mediana mundial. El hornfels es claramente más resistente. El intrusivo puro coincide con su clase tabulada de Leps, que para él es adecuada.
4. **Relave.** Hasta unos 13 % no reduce la resistencia drenada. Su efecto debe evaluarse en la permeabilidad y la respuesta no drenada.

## 5. Ensayos recomendados (de mayor a menor valor de información)

1. **Margas y limolitas:** triaxiales CD de gran escala a σ′3 de 0.5–4 MPa, durabilidad y desleimiento (slake).
2. **Mármol ROM:** triaxiales CD de gran escala a σ′3 de 2–4 MPa, con Bg y granulometría después del ensayo.
3. **Gs ensayado** en los lotes de gran escala.
4. **Ensayos CIU de gran escala** a alta presión sobre material triturado de mármol y margas, para el criterio de drenaje.

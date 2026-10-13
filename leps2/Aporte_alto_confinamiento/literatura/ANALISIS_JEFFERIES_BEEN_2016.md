# Análisis de Jefferies y Been (2016), *Soil Liquefaction: A Critical State Approach*, 2.ª ed.

**Referencia:** Jefferies, M., y Been, K. (2016). *Soil Liquefaction: A Critical State Approach* (2.ª ed.). CRC Press / Taylor & Francis. ISBN 978-1-4822-1367-6.

**Uso previsto:** sustento para (i) el artículo Leps-P (resistencia drenada de enrocados y estériles a alto confinamiento, envolvente acotada por el estado crítico) y (ii) el artículo complementario sobre presión de poros y licuación estática de capas basales saturadas, trituradas y contractivas en botaderos altos.

**Método de lectura.** Se extrajo el texto completo del PDF (713 páginas) con `pypdfium2` y se leyeron íntegros los capítulos 1 (casos), 2, 3, 5 y 6, el apéndice C (§C.1) y los pasajes pertinentes de los capítulos 4, 7, 9 y 10. Las ecuaciones y tablas que la extracción de texto deformó (ec. 4.6, C.8, 6.4, 6.16–6.17, tablas 5.4, 6.1, 6.3, 6.5, figura 6.48) se verificaron sobre la página renderizada. **Todas las páginas citadas son las páginas impresas del libro** (en el PDF completo, página PDF = página impresa + 23). Cuando algo es inferencia mía y no del libro, lo indico como tal.

---

## 1. Marco del libro

### 1.1 Parámetro de estado ψ

- Definición (ec. 2.6, p. 42; fig. 1.1, p. 4): **ψ = e − e_c**, con e la relación de vacíos actual y e_c la relación de vacíos crítica a la misma tensión media efectiva. ψ < 0 es denso (dilatante), ψ > 0 suelto (contractivo).
- Justificación física (p. 43): *"Because high confining stress levels tend to suppress dilatancy, the definition of state must take into account the stress level. It is the magnitude of dilation that determines strength, not the void ratio or density at which dilation occurs."* Es la frase más directa del libro para fundamentar que la dilatancia —y con ella el exceso de resistencia sobre el estado crítico— se suprime con la tensión.
- Argumento teórico (pp. 43–44): para una trayectoria idealizada a p′ constante desde el estado inicial hasta la CSL, ε_v = ψ/(1+e) (ec. 2.8) y, con ε_q ≈ 0,2–0,3 para movilizar el estado crítico en una banda de unas 10 partículas, la dilatancia media es **D_ave ≈ 4ψ/(1+e)** (ec. 2.9). Los autores advierten que el coeficiente 4 "is only a plausible estimate of likely magnitude" (p. 44); lo importante es la linealidad entre D y ψ y su independencia del nivel de tensión.
- ψ inicial frente a ψ actual (p. 45): ψ_o = e_o − e_c(p′_o) es cómodo para reducir ensayos; para la ley estado–dilatancia y la modelación se usa ψ al pico (actual). Con ψ_o la tendencia D–ψ no pasa por el origen por la densificación previa al pico (p. 44).
- Normalizaciones alternativas rechazadas (pp. 52–54): ψ/(e_max − e_min) no mejora la correlación (fig. 2.10); ψ/λ empeora la dispersión en estados densos (fig. 2.11, "a backward step"); ψ/(1+e) mejora poco (fig. 2.12). El índice de estado relativo de Boulanger (2003) y el índice de dilatancia relativa de Bolton (1986) se consideran inferiores porque suponen una CSL común no medida (p. 54).

### 1.2 Estado crítico: definición, unicidad y forma de la CSL

- Definición (Roscoe et al., 1958; p. 37–38): estado en que el suelo sigue deformándose a tensión y relación de vacíos constantes, **sin propensión a cambiar**. Formalmente, D = 0 y Ḋ = 0 (pp. 70, 109; ecs. 3.4–3.5, primer axioma). El segundo axioma es ψ → 0 cuando ε_q → ∞ (ec. 3.35, p. 123).
- Estado estacionario (Poulos, 1981) y estado crítico se tratan como equivalentes a efectos prácticos (pp. 39, 109). Las líneas S y F de Casagrande (1975) y Alarcon-Guzman et al. (1988) se explican por el límite de deformación del triaxial (~20 %), no por una CSL no única (pp. 79–81, 250–251, fig. 6.23).
- Unicidad: la CSL de Erksak 330/0.7 es independiente del método de preparación (fig. 2.32, p. 79–80) y de la trayectoria compresión/extensión dentro de Δe ≈ ±0,005 (fig. 6.7, p. 232). La confusión habitual es tomar el estado cuasi-estacionario (transformación de fase) por el crítico (pp. 71–72).
- **Forma semilogarítmica** (ec. 2.1, p. 39; ec. 3.6, p. 110): **e_c = Γ − λ ln(p′)**, con Γ definido a p′ = 1 kPa y λ en logaritmo natural (λ₁₀ = 2,303 λ).
- **CSL curva.** El libro insiste en que ψ no depende de la forma de la CSL:
  - *"the validity of the CSL as a frame of reference does not depend on a semi-log approximation – it is only a modelling detail"* (p. 39).
  - Toyoura (Verdugo, 1992): **e = 0,9325 − 0,019 (p′/p_ref)^0,7**, p_ref = 100 kPa (ec. 2.12, p. 76; fig. 2.29). Li y Wang (1998) proponen e vs (p′)^α con α = 0,7 (p. 110).
  - Fraser River sand (25 % cuarzo, partículas angulosas y triturables): semilog Γ = 1,22, λ₁₀ = 0,138 en 40–200 kPa, pero mejor ajuste potencial **e_c = 1,09 − 0,05 (p′)^0,25** para 10–1000 kPa (ec. 7.1, p. 340).
  - Guindon tailings B (67 % finos): la idealización semilog pierde ~0,02 en e respecto de la curva (p. 75–76, fig. 2.28).
  - **Erksak 330/0.7:** *"a distinct 'knee' or crushing point (for want of a better phrase) at a mean stress of about 1000 kPa"* (p. 110; fig. 2.26, p. 73). Por encima del codo la CSL se empina fuertemente (en la fig. 2.26 e_c baja de ≈0,73 a ≈0,57 entre ~1 y ~3 MPa; esta cifra es lectura mía de la figura, el libro no da un λ para el tramo alto). Interpretación del libro: la forma semilog surge cuando la rigidez es proporcional a p′; *"The knee in the Erksak sand CSL occurs when this is no longer the case and the stiffness becomes approximately constant"* (p. 110).
  - Rango de validez de la semilog: *"Equation 2.1 is a sufficient approximation for commonly encountered stress levels in engineering of about 10 kPa < p′ < 500 kPa"* (p. 110); *"the CSL is not necessarily linear on the semi-log plots used, in particular at stresses in the range of 1000 kPa or more"* (p. 82).
- Precisión: ±0,01 en e con buena práctica comercial (pp. 72, 75); la e debe conocerse a ±0,003 (p. 70).
- Rangos típicos (tabla 2.5, p. 82): Γ 0,9–1,4; λ₁₀ 0,02–0,07 (arenas cuarzosas uniformes), 0,10–0,25 (limos arenosos uniformes a limos), 0,04–0,07 (limos arenosos bien graduados). Arenas cuarzosas redondeadas λ₁₀ ≈ 0,03; *"angular, crushable silty sands will have greater values of λ10 (in the range 0.15–0.2…)"* (p. 84). La graduación pesa más que el contenido de finos (fig. 2.38, p. 85).

### 1.3 Razón de fricción crítica M y φ′c

- M = q/p′ en estado crítico; en compresión triaxial **M_tc = 6 sin φ_c /(3 − sin φ_c)** (ec. 2.13, p. 77).
- Independencia de la tensión: *"With quartz sands, M is essentially independent of pressure level to at least initial confining stresses in excess of 2.5 MPa (Vaid and Sasitharan, 1992)"* (p. 76). En la fig. C.1 (p. 484) los datos de Erksak llegan a p′ = 4,4 MPa con M_tc = 1,26 (φ_c = 31,4°) y tendencia lineal.
- Independencia de e: aceptada (ec. C.4), aunque *"there is a trend suggesting reduced M for very high void ratio"* (p. 484). En la calibración de Erksak, el mejor ajuste en ensayos sueltos fue M_tc = 1,18 frente a 1,26 en densos (p. 132).
- Dependencia del ángulo de Lode (pp. 90–94, 484–487): Brasted, M_tc = 1,27 (31,6°), M_te = 0,81 (27,9°), deformación plana M_ps = 1,08 con φ_c = 33,4° a θ ≈ 15°, *"an increase in frictional strength of about 2° over the triaxial compression conditions"* (p. 92). Erksak, M_te = 0,82 (28,3°) (p. 485). Función operativa M(θ) = M_tc − M_tc²/(3+M_tc)·cos(3θ/2 + π/4) (ec. 3.8, p. 111; C.7, p. 487).
- Valores reportados: tabla 2.5 (p. 82): **1,20–1,35 arenas cuarzosas; 1,15–1,25 arenas blandas; 1,30–1,60 arenas o limos de relave**. *"M is generally considered to increase with increasing angularity of soil grains, and we have seen values as large as Mtc ~ 1.7 for tailings materials and carbonate sands (compared to 1.2–1.3 for subrounded silica sands)"* (p. 86). *"Generally, ϕc ≈ 31° for sub-rounded hard quartz sands, but care is needed as ϕc can change markedly with mineralogy and grain shape"* (p. 49). Dogs Bay (carbonato) M_tc = 1,65; Fraser River M_tc = 1,45 (p. 341).
- Conversión (cálculo mío con ec. 2.13): M = 1,15 → 28,9°; 1,20 → 30,0°; 1,26 → 31,4°; 1,35 → 33,4°; 1,45 → 35,7°; 1,60 → 39,2°; 1,65 → 40,3°; 1,70 → 41,5°. Un φ′_c = 31° corresponde a M_tc ≈ 1,24.
- Determinación (pp. 77–78): (a) método de Bishop, η_max vs D_min extrapolado a D = 0 (preferido, ≥5 ensayos densos con D_r 40–100 %); (b) η final de ensayos sueltos llevados al estado crítico; (c) corte anular, criticado porque p′ es desconocido y supone φ_c invariante con el esfuerzo intermedio.

### 1.4 Tensión–dilatancia

- Rowe (1962): σ′₁/σ′₃ = K(1 − ε̇_v/ε̇₁) (ec. 2.2, p. 40). Dilatancia D = ε̇_v/ε̇_q (ec. 2.4, p. 41); por la convención compresión-positiva, la máxima dilatación es D_min (negativa).
- Cam Clay: Dᵖ = M − η (ec. 3.13, p. 113), consecuencia de suponer disipación de trabajo plástico constante (ec. 3.12).
- **Regla de Nova** (ec. 3.31, p. 122; ec. C.8, p. 487): **D_min = (M − η_max)/(1 − N)**, es decir, η_max = M − (1 − N)·D_min. *"Many natural sands tend to show N ≈ 0.3"* (p. 487); rango 0,2–0,5 (tabla 3.2, p. 127). N representa almacenamiento inelástico de energía (Jefferies, 1997).
- Razón imagen M_i (pp. 94–97, 122–123, 487–489): Dᵖ = M_i − η (ec. 3.32); M_i → M cuando ψ → 0. NorSand adopta M_i = M(θ)(1 − χ_i N |ψ_i|/M_tc) (tabla 3.1; ec. C.13). Alternativas en tabla 2.6 (p. 96): Manzari y Dafalias (1997) M_i = M + mψ; Li y Dafalias (2000) M_i = M exp(mψ), m ≈ 4 para Toyoura.

### 1.5 NorSand (lo esencial)

- Modelo de estado crítico generalizado (Jefferies, 1993) con **infinidad de líneas de compresión normal (NCL)** desacopladas de la CSL (pp. 118–122; evidencia experimental en Erksak, fig. 3.12; Jefferies y Been, 2000). Cam Clay es un caso particular (p. 109, apéndice H).
- Superficie de fluencia η/M_i = 1 − ln(p′/p′_i) (ec. 3.34); ley estado–dilatancia en la imagen **Dᵖ_min = χ_i ψ_i** (ec. 3.36), con χ_i = χ_tc/(1 − χ_tc λ/M_tc) (ec. 3.37; en la práctica 1,05χ_tc–1,10χ_tc); límite de endurecimiento (p′_i/p′)_max = exp(−χ_i ψ_i/M_i,tc) (ec. 3.38); ley de endurecimiento con módulo plástico H (ec. 3.40); elasticidad por I_r = G/p′ y ν.
- Parámetros (tabla 3.2, p. 127): Γ 0,9–1,4; λ 0,01–0,07; M_tc 1,2–1,5; N 0,2–0,5; H 25–500 (primer estimado H ≈ 4/λ₁₀, p. 139); χ_tc 2–5; I_r 100–600; ν 0,1–0,3.
- Calibración Erksak (tabla 3.3, p. 132): M_tc 1,26 (densos) y 1,18 (sueltos), N = 0,35, χ_tc = 4,0 ± 10 %, H = 103 − 980ψ_o; ensayos drenados con p′ de 60 a 1000 kPa (p. 130). Efecto de λ: *"the most compressible soils (large λ) showing the least dilatancy"* (p. 133).
- NorSand no reproduce el tramo post-pico de muestras densas porque la deformación se localiza (pp. 130, 135–136).
- Validación en deformación plana a partir de calibración triaxial (Brasted, Cornforth 1961; pp. 139–141).

---

## 2. Relaciones cuantitativas entre resistencia/dilatancia y ψ

| Relación | Ecuación / valores | Base de datos | Página |
|---|---|---|---|
| Dilatancia media (argumento teórico) | D_ave ≈ 4ψ/(1+e) | Experimento mental | 44 (ec. 2.9) |
| Dilatancia máxima vs ψ_o | D_min ≈ 3ψ_o, dentro de ±0,2 | 20 suelos (arenas cuarzosas limpias a arenas limosas, un relave de arenas petrolíferas, Hilton Mines), **p′ de 19 a 1200 kPa** | 49 (fig. 2.6) |
| φ′ pico triaxial vs ψ_o | Solo gráfica (φ′_tc ≈ 28–48° para ψ_o de 0 a −0,3) | Mismos 20 suelos | 50 (fig. 2.7) |
| (φ′_tc − φ′_c) vs ψ_o | Solo gráfica (0 a ~16°) | Mismos 20 suelos | 50 (fig. 2.8) |
| **φ′ pico vs ψ (ajuste explícito)** | **φ = φ_c(1 − 5ψ/3), φ_c = 32°** ⇒ φ ≈ 32° − 53ψ | "Based on the 20 sands tested… broadly applicable regardless of grain size and shape, fines content or mineralogy" | 153 (ec. 4.6) |
| Variante usada en el software | φ′ = 32 − 50ψ | Implícita en fig. 2.7 | 434 |
| Ley estado–dilatancia | **D_min = χ_tc ψ** (ψ actual al pico) | Drenados triaxiales; ver valores abajo | 55 (ec. 2.11), 56 (fig. 2.13) |
| Valores de χ_tc | Tabla 2.5: >4 bien graduados; ~4 arenas cuarzosas uniformes; ~3 arenas blandas uniformes. Tabla 2.1: Ottawa 4,8; Erksak 3,4–3,5; Nerlerk 5,2; Brasted 2,8; Hilton Mines 2,7; Toyoura 2,9 y 5,1; Northwest Brook Pit 5,3; Syncrude 5,3; Toromocho 5,9; Chek Lap Kok 4,0; Fraser River 3,2 | Arenas y relaves; en la tabla 2.1, D50 de 5,5 µm (limo de Endako) a 1000 µm | 46–48, 82, 341 |
| Equivalencia histórica | Been y Jefferies (1985) y NorSand original ≈ χ_tc ~ 4 implícito | — | 483 |
| Acoplamiento | En muchos suelos N·χ_tc ≈ 1, pero relaves y "paste" muestran que N y χ no son complementarios | — | 489 |
| Regla de flujo de Bolton (usada para CPT) | φ = φ_c + 0,8δ | Bolton (1986) | 151 (ec. 4.5) |
| Deformación volumétrica neta al pico | Dilatación neta al pico solo si ψ_o < ~−0,06 en promedio; ψ_o = 0 no separa | 20 arenas, triaxial drenado | 51 (fig. 2.9) |
| Distancia a la CSL vs dilatancia | D_min ∝ ψ al pico; la tendencia pasa cerca del origen (prueba de que drenados y no drenados comparten CSL) | 29 arenas (Been et al., 1992) | 81 (fig. 2.33) |
| Efecto de la fábrica | ±2° en φ′ (Arthur y Menzies 1972; Oda 1972; Tatsuoka 1987), comparable a la dispersión total | Arenas de laboratorio | 55–56, 59 (fig. 2.17) |
| Efecto de OCR | Con ψ referido a la fluencia (OCR = 4), efecto nulo; con e al inicio del corte, −1° aparente | Erksak | 59 (fig. 2.19) |
| Ejemplo NorSand | Base: Γ = 0,8, λ₁₀ = 0,05, M_tc = 1,25, N = 0,3, χ_tc = 3,5, H = 250, I_r = 600 | Simulación | 133 |

**Rango de los datos (respuesta explícita a la pregunta):**

- **Gravas:** ninguna. El D50 máximo de la tabla 2.1 es 1000 µm (Chek Lap Kok); el libro describe su base como *"broadly clean coarse sands to pure silts"* (p. 82, fig. 2.35).
- **Enrocados / estériles de mina gruesos:** ninguno. El único material de mina gruesa es el estéril de carbón de Aberfan, tratado solo como caso histórico (pp. 17–18), sin CSL ni parámetros.
- **Materiales triturables:** sí, pero arenosos: Fraser River (angulosa, 25 % cuarzo, posible trituración en los ensayos de mayor confinamiento, p. 341–343); Dogs Bay, arena carbonatada (Coop, 1990), con Γ = 3,35, **λ₁₀ = 0,77**, M_tc = 1,65 (tabla 2.1, p. 48); relaves (roca molida, sin trituración documentada en los ensayos).
- **Tensiones > 1 MPa:** escasas y casi todas para la CSL o para M, no para la relación φ–ψ: la fig. 2.6 llega a 1200 kPa; la CSL de Erksak incluye ensayos no drenados consolidados a 3–8 MPa con p′ final de 0,46–3,25 MPa (tabla 2.4, pp. 67–69); la fig. C.1 (M de Erksak) llega a 4,4 MPa; la CSL de Guindon se extiende con drenados a >1,5 MPa (p. 74); la tabla 6.1 (p. 237) recoge ensayos no drenados de Bishop et al. (1965) en arena de Ham River suelta a **990 psi (~6,8 MPa) y 1840 psi (~12,7 MPa)**.
- La relación φ–ψ (ec. 4.6) es, por tanto, una calibración en arenas a p′ ≤ 1,2 MPa; extrapolarla a enrocado a 1–15 MPa no tiene apoyo en el libro.

---

## 3. Trituración, alta tensión, curvatura de la CSL, tamaño de probeta y fábrica

### 3.1 Lo que el libro dice sobre trituración

El libro no desarrolla un modelo de rotura de partículas. Sus menciones son cualitativas pero útiles:

- Ensayos a alta presión para definir la CSL: *"it is necessary to consolidate the sample to p′ > 2 MPa prior to shear. Such high pressures are inconvenient for most commercial triaxial equipment as well as often involving grain crushing effects"* (p. 66; repetido en apéndice B, p. 460).
- *"even with high-pressure equipment, grain crushing often occurred which self-evidently changes the material being tested"* (p. 405). Por eso la práctica evolucionó a drenados sobre muestras sueltas para extender la CSL (pp. 74, 405–406).
- Codo de la CSL de Erksak ≈ 1000 kPa llamado "crushing point" (p. 110).
- Dilatancia: *"The minimum dilatancy plausibly depends on factors such as the crushability of the sand and grain size distribution, with uniformity of particle sizes and crushing both tending to reduce dilatancy. Well-graded, non-crushable sand grains should increase dilatancy. However, with the available database… we have not been able to establish any such relationship with index properties"* (p. 86; fig. 2.39: χ no correlaciona con D50 ni λ₁₀).
- Fraser River: M_tc = 1,45 y N = 0,43, mayores que en arenas cuarzosas, *"possibly caused by grain crushing in the higher confining stress tests and which is a further work dissipation mechanism"* (p. 341). Es la única afirmación del libro que vincula trituración con un aumento de M y N.
- CPT en cámara de calibración: sesgo de segundo orden a 450 kPa *"thought attributable to grain crushing, which is presently excluded from the NorSand model"* (p. 171).
- Russell y Khalili (2004), modelo de superficie límite para arenas con trituración, figura en la lista de referencias (p. 671); no localicé su cita en el cuerpo del texto.

### 3.2 Efecto de la tensión sobre ψ (relevante para la interacción e × σ)

- Factor K_σ (pp. 368–369): a relación de vacíos constante, aumentar la tensión hace ψ más positivo; la tasa la controla λ: *"the slope of the critical state line λ (which is the soil property that determines how ψ varies with stress level for constant density)"* (p. 369). *"if ψ is the chosen frame of reference then no stress-level correction factor Kσ is required"* (p. 369).
- Consolidación: *"Increasing stress also tends to increase (make more positive) the state parameter because the consolidation-related void ratio changes are less than the change in the critical void ratio for the same stress increase"* (p. 303). Es decir, aun considerando la compresión del material, ψ crece con la profundidad.
- Para carga no drenada, p′_c/p′_o = exp(−ψ_o/λ_e) (p. 52; ec. 6.16, p. 286). Para corte drenado a p′ constante, *"there is theoretically no role for λ"* (p. 52).

### 3.3 Tamaño de probeta (§2.2.9, pp. 60–62)

- Jefferies et al. (1990): arena de Ticino densa (e = 0,59 ± 0,02, D_r ≈ 100 %), p′ = 100 kPa, ocho ensayos con diámetros 36, 75, 154 y 289 mm (H/D ≈ 2).
- Lo que **no** cambió: *"The peak dilation rate is the same for all tests. Although there is some change in peak deviator stress, there is no systematic bias with sample size, and the variation (±5%) is within normal test repeatability"* (p. 61). Scott (1987) llegó a conclusiones similares.
- Lo que sí cambió: módulo inicial (menor al aumentar el tamaño, al revés que en Scott 1987), deformación volumétrica a 6 % de deformación axial (de 4,5 % a 3 %, *"a 30% reduction in the gross volume change"*) y fragilidad post-pico (las probetas grandes caen más rápido a la residual, con bandas de corte múltiples, fig. 2.21).
- Alcance: un solo material, una sola tensión, mismo tamaño de grano; es un efecto de escala probeta/banda de corte, no de escalado de granulometría (truncado o gradación paralela). El libro no trata el escalado de granulometrías gruesas.
- Localización a escala de campo: con bandas de corte, el agua migra hacia la banda a distancias del orden de 1 m (p. 277); por eso las resistencias no drenadas de suelos ligeramente dilatantes medidas en laboratorio no se mantienen en campo (pp. 276–277, 290–292).

### 3.4 Fábrica (§2.2.7, pp. 55–59; §2.5; §6.6.1; §10.5)

- Probetas de Kogyuk con igual ψ y distinta preparación: φ′ pico y D_min similares, curvas volumétricas muy distintas (fig. 2.15, p. 57).
- Efecto de ±2° en φ′ (p. 56); en carga cíclica la fábrica pesa tanto como ψ (Nemat-Nasser y Tobita, 1982; p. 58).
- La CSL no depende de la preparación (p. 79); la fábrica se representa en NorSand mediante H, I_r y en parte χ (p. 251–252; fig. 6.24).
- No hay método para medir la fábrica in situ: *"the best that can be done is to recognize that fabric is an important influence and to be conservative"* (p. 59).

---

## 4. Capítulo 5: variabilidad y estados característicos

### 4.1 Evidencia

1. **Bolsones sueltos (Rowe y Craig, 1976; pp. 203–208):** centrífuga del cajón de Oosterschelde. Con 4 % en volumen de material suelto en la zona superior de fundación (un tercio del ancho), las presiones de poros migraron a la arena densa y los desplazamientos se duplicaron (~0,4 % del ancho). Con 10 %, falla por licuación en la segunda etapa de carga. *"loose pockets have a disproportionate effect… High pore pressures generated in loose pockets dissipate into the surrounding denser material"* (p. 207).
2. **Tarsiut P-45 (Popescu, 1995; Popescu et al., 1997; pp. 209–216):** relleno hidráulico de Erksak, 32 + 5 CPT en 72 × 72 m. q_c ≈ log-normal; finos log-normales con media 1,5 % y percentil 90 de 2,5–3,0 %. Distancias de correlación: núcleo 0,95 m vertical y 12,1 m horizontal; berma 0,5 m y 5,4 m. Con simulaciones estocásticas, Δu/σ′_vo llegó a 0,8–1,0 frente a 0,6 en el depósito uniforme con la media. **El depósito uniforme con el percentil 80 reproduce la extensión de licuación de los campos estocásticos; los percentiles 70 y 90 la subestiman y sobrestiman** (p. 215). Las colas sueltas importan y la hipótesis normal subestima las presiones (p. 215).
3. **Berma de Nerlerk (Onisiphorou, 2000; Hicks y Onisiphorou, 2005; pp. 216–220):** análisis determinista con ψ uniforme: mecanismo de falla para ψ > −0,02; estable para ψ < −0,08. Campo aleatorio con μ_ψ = −0,08, σ_ψ = 0,05 (escalas ~1 m vertical, ~8 m horizontal): la respuesta más débil equivale al caso uniforme con ψ ≈ −0,02. En los CPT reales cerca del deslizamiento 3, mediana ψ ≈ −0,08 y percentil 80 ψ ≈ −0,03.

### 4.2 Recomendaciones

- Convención de percentiles del libro: *"the 80 percentile value, which means that 80% of the measurements will be 'stronger'"* (p. 220). Su "percentil 80" es el **fractil 20 % por la cola débil**; "percentil 90" es el fractil 10 %.
- Definición operativa: *"A characteristic value is simply the value to be used in a deterministic calculation to obtain the same outcome (performance prediction) as would be obtained with a full stochastic simulation and at a high level of confidence"* (p. 220).
- Requisitos: propiedad medible y bien definida (ψ sí; N_SPT no); respetar la forma de la distribución (log-normal, por eso percentiles y no media − k·σ); que el percentil sea estimable con el número de ensayos (p. 220).
- Precisión de ψ desde CPT: ±0,04; el percentil 90 suele ser errático en los perfiles CPT; el 99 no tiene sentido (p. 221).
- **Recomendación para licuación:** *"a reasonable characteristic value of state parameter lies between 80 percentile and 90 percentile values for liquefaction analyses. One should probably err closer to the 90 percentile value for cyclic loading cases, but can relax a little towards 80 percentile value for static design problems"* (p. 221). Para sistemas fuertemente estratificados como Nerlerk, esperar conexión de zonas sueltas (p. 221). En el cap. 6 se habla de "the loosest 15th percentile (85% denser)" (p. 273) y en Lower San Fernando se usa el percentil 90 (p. 303).
- **Resistencia para diseño de fundaciones (tabla 5.4, p. 222; Been y Jefferies, 1993):** para una estructura costa afuera con objetivo de resistencia factorada al 99 % de excedencia (631 MN):

| Percentil de resistencia | Resistencia calculada (MN) | Factor de resistencia |
|---|---|---|
| 95 | 741 | 1,17 |
| 90 | 764 | 1,21 |
| 80 | 793 | 1,26 |
| 70 | 814 | 1,29 |
| 60 | 832 | 1,32 |
| 50 | 849 | 1,34 |

  El percentil 80 con factor 1,26 coincide con ISO 19906 (factor ≥ 1,25) y con Meyerhof (1984, f_φ = 0,8) (p. 222). Eurocódigo 7: con métodos estadísticos, probabilidad ≤ 5 % de un valor peor que gobierne el estado límite (p. 223). Los autores creen que el trabajo de Popescu y Prevost apoya el EC7, *"although the basis for the clause is not defended even in the commentary"* (p. 223).

### 4.3 Comparación con el percentil 5 de una envolvente media

El libro no habla de envolventes ajustadas por regresión ni de incertidumbre epistémica del ajuste. Sus percentiles describen la **distribución espacial de valores puntuales** (variabilidad aleatoria del estado in situ) y se calibran contra simulaciones estocásticas del mecanismo. El percentil 5 inferior de la **envolvente media** de Leps-P cuantifica otra cosa: la incertidumbre sobre la media. Las dos ideas solo coinciden cuando la superficie de falla promedia muchas escalas de fluctuación, de modo que la variabilidad puntual se cancela y gobierna la incertidumbre de la media. Para mecanismos frágiles o de capa débil (bolsones sueltos, licuación) el libro muestra lo contrario: gobierna la cola débil de la distribución puntual (fractil 10–20 %), y la conectividad de las zonas sueltas puede hacer insuficiente incluso el fractil 20 % (Nerlerk). La tabla 5.4 muestra, además, que percentil y factor parcial son intercambiables: elegir el percentil sin fijar el factor (o al revés) no define la confiabilidad.

---

## 5. Capítulo 6: licuación estática y resistencia residual

### 5.1 Datos de laboratorio y tendencias

- Erksak en compresión no drenada, −0,07 < ψ_o < +0,07: con ψ_o > 0 la respuesta es frágil desde el desviador máximo; con 5–15 % de deformación se alcanza el estado crítico (pp. 227–228). Igual comportamiento en Ticino, en la arena limosa bien graduada de Bennett (31 % finos) y en el limo arenoso de Guindon (65 % finos) (pp. 228–230). *"The soil's state matters, not its fines fraction"* (p. 228).
- Resistencia pico: *"the data support a broad trend of strength ratio su/p′o > 0.15 even when the sample is rather loose (ψ = +0.05), rising to su/p′o ≈ 0.30 at the critical state (ψ = 0)"* (pp. 235–236; fig. 6.10). Kogyuk es anómalamente resistente.
- Analogía con arcillas normalmente consolidadas (Wroth, 1984): (s_u/p′_o)_nc ≈ 0,35 para M = 1,25; la espaciación r = 2 equivale a ψ_o = +0,69λ_e (≈ +0,015 en arenas limpias) (p. 237). A_f ≈ 0,9 a ese estado (p. 238).
- **Tabla 6.1 (p. 237; Bishop 1971):** incluye los únicos ensayos a muy alta presión del libro. Arena de Ham River suelta, compresión, **990 psi: (s_u/p′)_n = 0,249, φ′_f = 21,3°, φ′_r = 33°, I_B = 94 %**; **1840 psi: 0,251, 20,1°, 33°** (Bishop et al., 1965). Las razones son prácticamente iguales a las de Castro (1969) a 4 kg/cm² (0,206–0,333). Es evidencia, en arena, de que la fragilidad no drenada persiste a 7–13 MPa.
- **Resistencia residual (estado crítico, no drenada):** s_r/p′_o = (M/2) exp(−ψ_o/λ_e) (ec. 6.4bis, p. 286). En la p. 239 la ec. 6.4 aparece impresa con exp(ψ_o/λ), sin el signo menos; la curva de la fig. 6.13 y la ec. 6.4bis confirman que el signo correcto es negativo (errata del libro).
- Índice de fragilidad de Bishop: **I_B = (s_u − s_r)/s_u** (ec. 6.5, p. 240). *"Brittleness arises only if ψo/λe > 0.7"* y crece rápidamente con ψ_o/λ (p. 240, fig. 6.14).

### 5.2 Mecanismo y disparo

- No existe colapso de una estructura metaestable. Ensayo G609 (ψ_o = +0,068): caída de 80 % de resistencia y η_L = 0,62 en el "colapso", pero Δu y η se movilizan sin inflexión en el pico; el drenado D684 (e = 0,820 > e_max = 0,76) cruza η = 0,62 sin cambio alguno (pp. 242–243). *"Soil liquefaction is not the result of metastable arrangements of soil particles"* (p. 242).
- En NorSand, la licuación es endurecimiento limitado por el estado: con ψ > 0 el límite de endurecimiento (ec. 3.38) es menor que 1 y la contracción plástica reduce p′ más de lo que el endurecimiento aumenta q (p. 248).
- La resistencia no drenada pico y la "línea de inestabilidad" no son propiedades: dependen de I_r y H. Duplicar la rigidez elástica reduce ~30 % la resistencia al inicio de la licuación (p. 248); η_L varía de 0,75 a 1,0 con H/I_r para el mismo M_tc (pp. 255–256, fig. 6.27).
- Efecto de K_o (p. 254, fig. 6.25): partiendo de K_o más bajo (mayor corte inicial drenado) la resistencia no drenada pico sube, pero para K_o ≈ 0,55 la resistencia cae inmediatamente al pasar a no drenado, *"at far below the drained strength"*.
- **Trayectoria de corte constante con p′ decreciente (CSD), mecanismo de Aberfan** (pp. 259–263): en Fraser River densa (ψ_o ~ −0,13) la fluencia comienza a η = 1,08, por debajo de M, y la falla descontrolada a η = 1,84. Sasitharan et al. (1993) en Ottawa suelta: *"the axial strain … at initiation of collapse was only 0.4%"* (p. 259). Recomendación: *"be very, very careful with the observational method for an in-situ situation with anything near a CSD path. There will be very little, if any, observable movements before catastrophic failure – exactly what happened at Aberfan. By all means, measure pore pressure, but do not allow the stress path to extend past 'Point B' on the CSD path (which is readily computed from drained triaxial compression data)"* (pp. 262–263). Take y Beddoe (2014) reprodujeron el mecanismo en modelo físico.
- Estado cuasi-estacionario: depende de I_r; tomarlo por el crítico causa errores de factor 6–8 en p′_c (pp. 263–264).
- Corte simple vs triaxial: diferencia en s_u/p′ < ~5 % (p. 266); en términos de σ′_v y τ_xy la diferencia es mayor (fig. 6.38).

### 5.3 Escuela del estado estacionario y sus deficiencias (pp. 269–277)

s_r = (M/2)·p′_c (ec. 6.9). Deficiencias: mezcla de muestras de distinta graduación; reducción por cos φ_s (~30 %) "misguided"; M depende del esfuerzo intermedio (~5 %); la "resistencia mínima asegurada" es falsa para suelos ligeramente dilatantes (−0,1 < ψ < 0), y solo aplica a ψ > ~0,03; el drenaje no es despreciable (en un relleno de Erksak, 20 % de disipación en 2 min y total en ~8 min, p. 276); la localización acorta la longitud de drenaje a ~1 m (p. 277).

### 5.4 Casos históricos y resistencia residual por ψ

- Tabla 6.3 (pp. 280–281) incluye **Aberfan Tip (1966): "Coal tailings, about 10% silt sized", 67 m, 36°, "Mass movement liquefaction slide triggered by increasing pore pressure"**, además de Fort Peck, Calaveras, Wachusett, Lower San Fernando, Mochikoshi, Sullivan, Merriespruit, etc. Aberfan **no** figura en la tabla 6.5 de resistencias residuales retroanalizadas.
- Tabla 6.5 (p. 288): s_r/σ′_vo y ψ_k (característico = percentil 80–90) por caso. Ejemplos: Fort Peck s_r/σ′_vo 0,04–0,06 con ψ_k −0,05 a −0,01; Lower San Fernando 0,07–0,12 con ψ_k 0 a +0,07; Mochikoshi 1 ~0,08 y Mochikoshi 2 0,14–0,16 con ψ_k +0,13 a +0,25 (relaves, λ₁₀ 0,15–0,25); Nerlerk 0,09–0,15 con ψ_k −0,05 a −0,03.
- **Ec. 6.17 (p. 286):** s_r/σ′_vo = [(1 + 2K_o)/3]·(M/2)·exp(−ψ_o/λ_e), suponiendo no drenaje sin localización.
- Hipótesis de trabajo: la resistencia residual de campo corresponde a la resistencia no drenada en el instante de localización (criterio de Drucker, ec. 6.20: σ̇_q ε̇_q + σ̇_m ε̇_m < 0), porque el agua migra hacia la banda (pp. 290–292, 309–311). NorSand con H/I_r = 0,5 reproduce los casos; la resistencia crece poco con la densidad hasta ψ_o < ~−0,05, donde se vuelve asintóticamente grande (p. 292). *"There will never be a single trend line for post-liquefaction strength"* (p. 292).
- **Función recomendada (fig. 6.48, p. 292):** con k0_factor = (1 + 2K_o)/3 y λ = λ₁₀:
  - si ψ > λ₁₀: s_r/σ′_vo = k0_factor·0,5·M_tc·exp(−ψ/λ_e), λ_e = λ₁₀/2,3;
  - si no: s_r/σ′_vo = k0_factor·0,0501·M_tc + 0,8·(λ₁₀ − ψ).
  Es un ajuste conservador a los casos ("best practice trend", pendiente 0,8), validado en la fig. 6.49 como estimador prácticamente insesgado (p. 293).
- Lower San Fernando (pp. 293–304): con percentil 90 de ψ desde CPT y λ₁₀ = 0,10, s_r/σ′_vo ≈ 0,06–0,15 en capas limosas sueltas frente a 0,06–0,12 retroanalizado (p. 304). Los autores advierten de errores compensados.
- **¿Qué tan denso basta?** (pp. 304–308): no hay pérdida de resistencia si ψ < −0,08 en triaxial isotrópico y ψ < −0,05 en corte simple; el límite inferior no drenado intersecta la resistencia drenada (tan φ′ o M/2) en ψ ≈ −0,06 (p. 304). Con K_o in situ 0,5–0,8, *"A judgement criterion of ψ < −0.05 from laboratory testing should be conservative in practice"* (p. 305). Criterio final: *"we are not going to make progress beyond ψ > −0.05 as the criterion for flowslides"* (p. 308). Robertson (2010): Q_tn,cs = 70 como frontera conservadora (50 para los casos más fiables) (p. 305).
- Relaves y limos (pp. 308, 311–312): la depositación hidráulica deja estados susceptibles; la resistencia en la localización depende de λ, I_r y H; en materiales más finos la migración de agua es menor (c_v más bajo), lo que podría explicar las residuales más altas de Mochikoshi (p. 311).

### 5.5 Casos de residuos mineros

- **Aberfan** (pp. 1, 17–18, 32, 225, 242, 259, 263, 280): estéril de carbón volcado por la cara del botadero (Tip 7), 67 m de altura, ladera de 12,5°, ~107 000 m³, recorrido ~500 m hasta la escuela y ~100 m más, 144 muertos (116 niños). Disparo: presión artesiana en areniscas bajo depósitos glaciales tras lluvias intensas (Bishop, 1973). Densidades muy bajas en la parte no fallada a 13–28 m de profundidad (el libro escribe "1.5–1.7 kN/m3", unidad evidentemente errónea). ~10 % pasante #200, φ′ = 39,5° en triaxial drenado; el material del flujo pudo degradarse a un material cohesivo con IP 16 y φ′_r ≈ 18° tras ≥ 21 m de desplazamiento. Asentamiento de cresta de 3 m y luego 6 m antes de la falla rápida. Es el caso del libro más cercano a un botadero, pero no se le asigna ψ ni s_r.
- **Merriespruit** (pp. 18–20): relaves de oro, 1994, ~600 000 m³, 3 km de recorrido, disparo por rebalse y erosión; finos 40–100 %; estado muy suelto sobre la CSL (Fourie et al., 2001; Fourie y Papageorgiou, 2001). CSL en tabla 2.1 (p. 48).

### 5.6 Limitaciones para estéril grueso triturado

1. Ninguna calibración (CSL, M, N, χ, H, ni la función de s_r) corresponde a gravas o enrocados; la función de la fig. 6.48 está calibrada con arenas, limos y relaves con λ₁₀ ≲ 0,25.
2. El método de estado in situ es el CPT (cap. 4), inaplicable en estéril grueso. Sin CPT, ψ debe estimarse con e medida y CSL de laboratorio, que el libro considera imprecisas y sujetas a perturbación (pp. 63, 273–275).
3. La CSL única supone una gradación fija; la trituración cambia el material durante la carga (p. 405), algo que el marco no modela.
4. La migración de agua hacia bandas de corte y el drenaje parcial son mayores en materiales permeables (pp. 276–277, 311); en estériles gruesos el comportamiento no drenado a gran escala exige baja permeabilidad (capas con finos o degradadas) o carga muy rápida.
5. El libro no trata suelos parcialmente saturados más allá de mencionar B < 1 (p. 244–245).

---

## 6. Implicaciones para Leps-P

### 6.1 Justificación mecánica del piso de estado crítico y de la curvatura

Usos defendibles:

1. **El piso existe y es independiente de la tensión.** El primer axioma (ec. 3.4–3.5) y las evidencias de M constante con p′ hasta >2,5 MPa (p. 76) y 4,4 MPa (p. 484) en arena cuarzosa permiten afirmar que, cuando la dilatancia se anula, la resistencia tiende a M (φ′_c) y no sigue bajando. La forma acotada tan φ′_s = tan φ′_cs + (tan φ′₁ − tan φ′_cs)·(σ′_n/σ₀)^(−λ) es coherente con esto.
2. **La curvatura es supresión de dilatancia por aumento de ψ.** Cita textual de p. 43 (sección 1.1) más la regla de Nova y la ley estado–dilatancia: η_max − M = −(1 − N)·χ_tc·ψ. Con N = 0,3, χ_tc = 4 y M_tc = 1,26, ψ = −0,1 da η_max = 1,54 y φ′ ≈ 37,8° (cálculo mío), coherente con la ec. 4.6 (32 − 53·0,1 ≈ 37,3°).
3. **Por qué ψ aumenta con σ′.** A e constante, ψ sube con ln σ′ a la tasa de la CSL (p. 369); con consolidación, sube igual porque la compresión es menor que el desplazamiento de e_c (p. 303). Por encima de un "codo de trituración" la CSL se empina (Erksak, p. 110), así que ψ sube aún más rápido: esto da una vía mecánica para la curvatura fuerte a 1–10 MPa.

**Relación entre el λ de Leps-P y la CSL (inferencia mía, no está en el libro).** Combinando ec. 4.6 (Δφ ≈ 53|ψ|) con una CSL semilog a e fija, ψ(σ) = ψ_ref + λ_e ln(σ/σ_ref), el exceso decae **linealmente en ln σ** y se anula a una tensión finita σ* = σ_ref·exp(|ψ_ref|/λ_e). La forma de Leps-P decae como potencia y alcanza el piso solo asintóticamente. Localmente, la pendiente logarítmica de ambas coincide si

  λ_Leps-P = −d ln(Δ tan φ)/d ln σ ≈ λ_e,eff / |ψ|,

donde λ_e,eff es la tasa a la que crece ψ con ln σ (λ de la CSL menos la pendiente de compresión, por el argumento de la p. 303). Consecuencias contrastables con la base de 767 ensayos:

- λ_Leps-P debería ser mayor en materiales más compresibles o triturables (CSL más empinada) y en estados más sueltos (|ψ| pequeño), y menor en materiales densos de roca dura.
- Con CSL curva (potencial, ec. 2.12 o 7.1), dψ/d ln σ crece con σ, así que la caída del exceso se acelera a alta tensión; la potencia de Leps-P supone lo contrario (pendiente logarítmica constante). Conviene comprobar en los residuos si la curvatura observada a 5–15 MPa es más fuerte que la que admite una potencia simple.
- Recomiendo **no llamar λ al exponente de Leps-P** (choca con la notación universal de la pendiente de la CSL); usar, por ejemplo, β.
- Lo que no se puede afirmar: que λ_Leps-P "es" la pendiente de la CSL. Son magnitudes distintas (una es adimensional respecto de ln σ normalizada; la otra es Δe por unidad de ln p′), relacionadas a lo sumo por el cociente con |ψ|.

### 6.2 ¿Qué φ′_c es plausible para roca triturada frente a los 31° ajustados?

- El libro solo da rangos para arenas y relaves: cuarzosas 30–33,4° (M 1,20–1,35); relaves 32,3–39,2° (M 1,30–1,60); hasta ~41,5° (M ~1,7) en relaves y arenas carbonatadas; Fraser River (angulosa, triturable) 35,7°; Dogs Bay 40,3° (pp. 48, 82, 86, 341). La angulosidad sube M (p. 86) y la trituración puede subirlo como disipación adicional de trabajo (p. 341).
- Un φ′_cs = 31° queda en el extremo bajo de lo que el libro asocia a partículas angulosas. Hay tres lecturas posibles que el artículo debe discutir: (i) el piso estadístico está mal identificado porque pocos ensayos llegan a ψ ≈ 0 (el piso se infiere por extrapolación); (ii) el ajuste absorbe otros efectos (escala, fábrica, ensayos sueltos con M menor: 1,18 frente a 1,26 en Erksak, p. 132); (iii) es real para el conjunto mineralógico de la base. El libro no permite decidir.
- **Propuesta defendible con el libro:** estimar φ′_c de forma independiente en el subconjunto con medición de volumen, por el método de Bishop (η_max vs D_min extrapolado a D = 0; pp. 77–78, fig. 2.30) o con la η final de probetas contractivas. Si ese φ′_c independiente coincide con el piso ajustado, la forma acotada queda respaldada por dos caminos.
- Si Leps-P se aplica en análisis 2D (deformación plana), el φ′_c triaxial subestima ~2° (p. 92), lo que es conservador; conviene declararlo.
- La envolvente de Leps-P está en el plano τ–σ′_n y el libro trabaja en q–p′; el φ′ de la envolvente de Mohr derivada de triaxiales equivale a φ′_tc (ec. 2.13).

### 6.3 Interacción e × tensión expresada con ψ

- El libro da la base conceptual: el efecto de la relación de vacíos sobre la resistencia opera a través de ψ = e − e_c(σ′), no de e por separado (pp. 42–43; fig. 2.4 con Kogyuk: igual D_r y distinto comportamiento; igual ψ y comportamiento similar).
- Con la ec. 4.6 y CSL semilog: ∂φ/∂e ≈ −53° por unidad de e, y ∂φ/∂ ln σ ≈ −53·λ_e. Por década de tensión, a e fija, la caída sería de ~1,6° con λ₁₀ = 0,03 y ~10,6° con λ₁₀ = 0,2 (cálculo mío; extrapolar estos números a enrocado no tiene respaldo).
- **Por qué el efecto de e debe desvanecerse con la tensión:** dentro de ψ los efectos de e y de ln σ son aditivos, pero la respuesta no es lineal en ψ: el exceso dilatante es ~0 cuando ψ ≥ 0 (en probetas sueltas el pico drenado es ≈ M). Al subir σ′, una fracción creciente de probetas pasa a ψ ≥ 0, donde e ya no afecta el pico. En una regresión con e y ln σ como covariables, eso aparece como una interacción negativa e × ln σ. Además, si la CSL se empina con la trituración, la interacción se acentúa.
- Formas de implementarlo en el modelo jerárquico: (a) covariable ψ* = e − e_c(σ′) con e_c(σ′) = Γ* − c(σ′/p_a)^α (forma de Li y Wang, 1998) estimando Γ*, c y α por material o por grupo; (b) término e × ln σ con signo predicho; (c) exceso = f(max(0, −ψ*)). La opción (a) es la más fiel al libro; exige e de las probetas al corte, que en ensayos con roca escalpada y compactada es incierta. La fig. 2.9 (p. 51) da una verificación: si la base tiene ε_v al pico, las probetas con contracción neta deberían concentrarse donde ψ_o > ~−0,06.

### 6.4 Trituración y movimiento de la CSL

- El libro reconoce que la trituración cambia el material (p. 405), produce un codo en la CSL hacia ~1 MPa en arena cuarzosa (p. 110), aumenta λ en materiales angulosos y triturables (p. 84), reduce la dilatancia (p. 86) y puede elevar M y N (p. 341). No cuantifica ninguna de estas relaciones, no define un índice de rotura y su modelo excluye la trituración (p. 171).
- Para el manuscrito: el libro sirve para afirmar cualitativamente que la trituración desplaza la CSL hacia abajo y la empina, con lo cual a una e dada ψ aumenta más rápido con σ′. Para cualquier relación cuantitativa (rotura vs CSL, CSL de enrocados) hay que citar literatura externa; Russell y Khalili (2004) está en su lista de referencias.

### 6.5 Efecto de tamaño

- Apoyo limitado y útil: en arena densa a 100 kPa, el pico y la dilatancia máxima no tienen sesgo con el diámetro (36–289 mm, ±5 %), mientras la deformación volumétrica y la fragilidad sí cambian (pp. 60–62). Permite sostener que la magnitud que modela Leps-P (resistencia pico) es menos sensible a la escala que la respuesta volumétrica.
- No permite sostener nada sobre gradación paralela, escalpado, relación D/d_max ni efecto de tamaño en enrocados a alta tensión.

### 6.6 Valores característicos

- Lo que el libro respalda: (i) definir el valor característico como el que reproduce en un cálculo determinista el resultado de la simulación estocástica (p. 220); (ii) usar percentiles y no media − k·σ cuando la variable es log-normal (p. 220); (iii) percentil y factor parcial deben elegirse juntos (tabla 5.4); (iv) para mecanismos gobernados por zonas sueltas, el fractil débil 10–20 % del estado, más cerca del 10 % en carga cíclica (p. 221).
- Propuesta para Leps-P: reportar por separado (a) la cota inferior creíble de la envolvente **media** (incertidumbre epistémica) y (b) el cuantil inferior **predictivo** de un ensayo nuevo (incluye la variabilidad entre muestras y sitios del modelo jerárquico). Usar (a) cuando la superficie de falla promedia muchas escalas de fluctuación y (b), o un fractil del estado, cuando el mecanismo lo controlan zonas débiles. El libro da la lógica de (b), no la de (a).

### 6.7 Afirmaciones que el libro NO respalda para enrocado a 1–10 MPa

1. Cualquier valor numérico de φ′_c, χ, N, Γ o λ para gravas, enrocados o estériles.
2. La ec. 4.6 (φ = 32(1 − 5ψ/3)) o la ley D_min = χψ por encima de ~1,2 MPa ni para materiales gruesos.
3. Que M sea independiente de la tensión en materiales que se trituran (la evidencia es para arena cuarzosa; en Fraser River la trituración se asocia a M mayor).
4. Una forma funcional de la CSL a alta tensión (el libro solo muestra un codo cualitativo en Erksak y ajustes potenciales para arenas hasta ~1 MPa).
5. Una relación entre rotura de partículas y la posición de la CSL.
6. Efectos de escala de granulometría.
7. Que la envolvente acotada debe ser exponencial: la combinación ψ–CSL semilog predice decaimiento lineal en ln σ hasta un piso alcanzado a tensión finita.

---

## 7. Implicaciones para el artículo complementario (presión de poros y licuación estática en la base de botaderos altos)

1. **Marco:** la susceptibilidad depende de ψ, no del tipo de material ni del contenido de finos (p. 228). Una capa basal triturada y saturada puede ser contractiva aunque el material sea "denso" en términos de D_r, porque σ′ alta lleva ψ hacia valores positivos (pp. 303, 369).
2. **Umbral:** ψ > −0,05 como criterio de flujo (p. 308); en triaxial isotrópico no hay caída de resistencia con ψ < −0,08 y en corte simple con ψ < −0,05 (p. 304). Con λ grande (material triturable), un mismo Δe respecto de la CSL corresponde a menor ψ/λ y a menos fragilidad (p. 240; Rose Creek, p. 257), pero el material puede estar mucho más suelto en campo que en laboratorio (p. 257).
3. **Disparo por aumento de presión de poros a corte constante (CSD):** es el mecanismo de Aberfan y el más pertinente para una base que se satura por infiltración o por subida de nivel freático. La fluencia empieza por debajo de M (η = 1,08 en Fraser River densa) y la falla ocurre con muy poca deformación previa (0,4 % en Sasitharan et al., 1993). La recomendación del libro, no permitir que la trayectoria pase el punto B calculado con triaxiales drenados (p. 263), se traslada directamente a criterios de diseño o de monitoreo.
4. **Disparo por carga:** con K_o bajo (corte inicial alto por la geometría del botadero), la caída puede ser inmediata al pasar a condición no drenada (p. 254). La línea de inestabilidad no es una propiedad (pp. 253–256).
5. **Alta presión:** la tabla 6.1 (p. 237) muestra arena de Ham River suelta a ~6,8 y ~12,7 MPa con s_u/p′ ≈ 0,25 e I_B = 94 % a 990 psi: el comportamiento frágil persiste a tensiones del orden de las de la base de un botadero de 700 m. Es arena, no estéril.
6. **Resistencia residual:** usar ec. 6.17 solo como cota superior para estados muy sueltos (sin localización); para estados cerca de la CSL, la función de la fig. 6.48 o simulaciones con NorSand en el punto de localización (pp. 290–292, 309–311). Ninguna está calibrada para estéril grueso.
7. **Programa de ensayos:** ~10 triaxiales por gradación representativa: al menos tres no drenados sueltos (100–200 kPa), dos drenados sueltos (~400 kPa) para extender la CSL y tres drenados densos para N y χ (pp. 404–406). Para la CSL a alta tensión, el libro recomienda drenados sobre muestras sueltas en vez de no drenados consolidados a presiones extremas, y advierte que la trituración cambia el material (pp. 74, 405). Medir G_max con bender elements para I_r (p. 406).
8. **Variabilidad:** las zonas sueltas conectadas gobiernan (Rowe y Craig; Nerlerk). Para la capa basal, usar el fractil débil 10–20 % de ψ, más cerca del 10 % si la estratificación es marcada (p. 221), o simulación estocástica de ψ (p. 440).
9. **Drenaje:** evaluar el factor de tiempo; el libro muestra disipación casi completa en ~8 min en arena con 2–3 % de limo (p. 276). En estéril grueso la condición no drenada solo es creíble en capas basales con finos o degradadas, o con carga muy rápida. El caso de Aberfan sugiere degradación del material a algo cohesivo (IP 16) en la superficie de falla (p. 18).
10. **Limitaciones a declarar:** no hay método de estado in situ para estériles gruesos; la CSL cambia con la trituración durante la carga; NorSand no incluye trituración; los casos de flujo con residual retroanalizada son arenas, limos y relaves, no estériles.

---

## 8. Referencias primarias citadas por el libro que conviene leer o citar

✔ = vista con datos bibliográficos completos en la lista de referencias del libro (pp. 659–676).

**Estado crítico, ψ y CSL**
- ✔ Roscoe, K., Schofield, A.N., y Wroth, C.P. (1958). On the yielding of soils. *Géotechnique*, 8(1), 22–53.
- ✔ Schofield, A., y Wroth, C.P. (1968). *Critical State Soil Mechanics*. McGraw-Hill.
- ✔ Casagrande, A. (1936). Characteristics of cohesionless soils affecting the stability of earth fills. *J. Boston Soc. Civil Eng.*, 23, 257–276.
- ✔ Poulos, S.J. (1981). The steady state of deformation. *J. Geotech. Eng. Div., ASCE*, 107(5), 553–562.
- ✔ Been, K., y Jefferies, M.G. (1985). A state parameter for sands. *Géotechnique*, 35(2), 99–112.
- ✔ Been, K., Jefferies, M.G., y Hachey, J.E. (1991). The critical state of sands. *Géotechnique*, 41(3), 365–381.
- ✔ Verdugo, R. (1992). The critical state of sands: Discussion. *Géotechnique*, 42(4), 655–663.
- ✔ Li, X.-S., y Wang, Z.-L. (1998). Linear representation of steady state line for sand. *J. Geotech. Geoenviron. Eng., ASCE*, 124(12), 1215–1217.
- ✔ Jefferies, M.G., y Been, K. (2000). Implications for critical state theory from isotropic compression of sand. *Géotechnique*, 50(4), 419–429.
- ✔ Pestana, J.M., y Whittle, A.J. (1995). Compression model for cohesionless soils. *Géotechnique*, 45, 611–631.

**Tensión–dilatancia, M y φ′_c**
- ✔ Rowe, P.W. (1962). The stress dilatancy relation for static equilibrium of an assembly of particles in contact. *Proc. R. Soc. London A*, 269, 500–527.
- ✔ Bolton, M.D. (1986). Strength and dilatancy of sands. *Géotechnique*, 36(1), 65–78.
- ✔ Nova, R. (1982). A constitutive model under monotonic and cyclic loading. En Pande y Zienkiewicz (eds.), *Soil Mechanics – Transient and Cyclic Loads*, pp. 343–373. Wiley.
- ✔ Bishop, A.W. (1966). Strength of soils as engineering materials. Sixth Rankine Lecture. *Géotechnique*, 16, 89–130.
- ✔ Vaid, Y.P., y Sasitharan, S. (1992). The strength and dilatancy of sand. *Can. Geotech. J.*, 29, 522–526. (M de Erksak hasta 4,4 MPa.)
- ✔ Negussey, D., Wijewickreme, W.K.D., y Vaid, Y.P. (1988). Constant-volume friction angle of granular materials. *Can. Geotech. J.*, 25(1), 50–55.
- ✔ Cornforth, D.H. (1964). Some experiments on the effect of strain condition on the strength of sand. *Géotechnique*, 14, 143–167.
- ✔ Jefferies, M.G., y Shuttle, D.A. (2002). Dilatancy in general Cambridge-type models. *Géotechnique*, 52(9), 625–637.
- ✔ Jefferies, M.G., y Shuttle, D.A. (2011). On the operating critical friction ratio in general stress states. *Géotechnique*, 61(8), 709–713.
- ✔ Manzari, M.T., y Dafalias, Y.F. (1997). A critical state two-surface plasticity model for sands. *Géotechnique*, 47, 255–272.
- ✔ Li, X.-S., y Dafalias, Y.F. (2000). Dilatancy for cohesionless soils. *Géotechnique*, 50(4), 449–460.
- ✔ Jefferies, M.G. (1993). NorSand: A simple critical state model for sand. *Géotechnique*, 43, 91–103.
- ✔ Been, K., y Jefferies, M.G. (2004). Stress dilatancy in very loose sand. *Can. Geotech. J.*, 41(1), 972–989.

**Trituración y alta presión**
- ✔ Coop, M.R. (1990). The mechanics of uncemented carbonate sands. *Géotechnique*, 40(4), 607–626.
- ✔ Russell, A.R., y Khalili, N. (2004). A bounding surface plasticity model for sands exhibiting particle crushing. *Can. Geotech. J.*, 41(6), 1179–1192.
- ✔ Bishop, A.W., Webb, K.L., y Skinner, A.E. (1965). Triaxial tests on soil at elevated cell pressures. *Proc. 6th ICSMFE*, Montreal, Vol. 1, pp. 170–174.

**Tamaño de probeta, localización y fábrica**
- ✔ Jefferies, M.G., Been, K., y Hachey, J.E. (1990). The influence of scale on the constitutive behaviour of sand. *Proc. 43rd Canadian Geotechnical Conference*, Quebec, Vol. 1, pp. 263–273.
- ✔ Scott, R.F. (1987). Twenty seventh Rankine Lecture: Failure. *Géotechnique*, 37, 423–466.
- ✔ Desrues, J., Chambon, R., Mokni, M., y Mazerolle, F. (1996). Void ratio evolution inside shear bands in triaxial sand specimens studied by computed tomography. *Géotechnique*, 46(3), 529–546.
- ✔ Oda, M., y Kazama, H. (1998). Microstructure of shear bands and its relation to the mechanisms of dilatancy and failure of dense granular soils. *Géotechnique*, 48(4), 465–481.
- ✔ Arthur, J.R.F., y Menzies, B.K. (1972). Inherent anisotropy in sand. *Géotechnique*, 22(1), 115–128.
- ✔ Tatsuoka, F. (1987). Strength and dilatancy of sands: Discussion. *Géotechnique*, 37(2), 219–225.

**Variabilidad y valores característicos**
- ✔ Popescu, R., Prevost, J.H., y Deodatis, G. (1997). Effects of spatial variability on soil liquefaction: Some design recommendations. *Géotechnique*, 47, 1019–1036.
- ✔ Hicks, M.A., y Onisiphorou, C. (2005). Stochastic evaluation of static liquefaction in a predominantly dilative sand. *Géotechnique*, 55(2), 123–133.
- ✔ Rowe, P.W., y Craig, W.H. (1976). Studies of offshore caissons founded on Oosterschelde sand. En *Design and Construction of Offshore Structures*, ICE, pp. 49–55.
- ✔ Been, K., y Jefferies, M.G. (1993). Determination of sand strength for limit state design. *Proc. Int. Symp. on Limit State Design in Geotechnical Engineering*, Copenhague, Vol. 1, pp. 101–110.

**Licuación estática, residual y casos de residuos mineros**
- ✔ Bishop, A.W. (1971). Shear strength parameters for undisturbed and remoulded soil specimens. En Parry (ed.), *Stress–Strain Behaviour of Soils (Roscoe Memorial Symposium)*, pp. 3–58. Foulis.
- ✔ Bishop, A.W. (1973). The stability of tips and spoil heaps. *Q. J. Eng. Geol.*, 6, 335–376.
- ✔ Bishop, A.W., y Penman, A.D.M. (1969). Informal discussion. Aberfan disaster: Technical aspects. *Proc. ICE*, 42(2), 317–318.
- ✔ Castro, G. (1969). *Liquefaction of sands*. Tesis doctoral, Harvard University (Harvard Soil Mechanics Series 81).
- ✔ Sasitharan, S., Robertson, P.K., Sego, D.C., y Morgenstern, N.R. (1993). Collapse behaviour of sand. *Can. Geotech. J.*, 30(4), 569–577.
- ✔ Take, W.A., y Beddoe, R.A. (2014). Base liquefaction: A mechanism for shear-induced failure of loose granular slopes. *Can. Geotech. J.*, 51(5), 496–507.
- ✔ Junaideen, S.M., Tham, L.G., Law, K.T., Dai, F.C., y Lee, C.F. (2010). Behaviour of recompacted residual soils in a constant shear stress path. *Can. Geotech. J.*, 47(4), 648–661.
- ✔ Wanatowski, D., y Chu, J. (2007). Static liquefaction of sand in plane strain. *Can. Geotech. J.*, 44(3), 299–313.
- ✔ Hird, C.C., y Hassona, F. (1990). Some factors affecting the liquefaction and flow of saturated sands in laboratory tests. *Engineering Geology*, 28, 149–170.
- ✔ Konrad, J.-M. (1990b). Minimum undrained strength versus steady state strength of sands. *J. Geotech. Eng., ASCE*, 116(6), 948–963.
- ✔ Wroth, C.P. (1984). Twenty fourth Rankine Lecture: The interpretation of in situ soil tests. *Géotechnique*, 34(4), 449–489.
- ✔ Olson, S.M., y Stark, T.D. (2002). Liquefied strength ratio from liquefaction flow failure case histories. *Can. Geotech. J.*, 39, 629–647.
- ✔ Robertson, P.K. (2010). Evaluation of flow liquefaction and liquefied strength using the cone penetration test. *J. Geotech. Geoenviron. Eng., ASCE*, 136(6), 842–853.
- ✔ Shuttle, D.A., y Cunning, J. (2007). Liquefaction potential of silts from CPTu. *Can. Geotech. J.*, 44(1), 1–19.
- ✔ Fourie, A.B., Blight, G.E., y Papageorgiou, G. (2001). Soil liquefaction as a possible explanation for Merriespruit tailings dam failure. *Can. Geotech. J.*, 38(4), 707–719.
- ✔ Fourie, A.B., y Papageorgiou, G. (2001). Defining an appropriate steady state line for Merriespruit gold tailings. *Can. Geotech. J.*, 38(4), 695–706.
- ✔ Been, K., Obermeyer, J., Parks, J., y Quinonez, A. (2012). Post liquefaction undrained shear strength of sandy silt and silty sand tailings. *Proc. Tailings and Mine Waste '12*, Keystone, CO, pp. 325–335.

**Notas.** El libro no cita literatura de enrocados ni de estériles de mina gruesos (no aparecen Marsal, Leps, Indraratna ni Hardin, entre otros, en su lista de referencias), y tampoco Verdugo y Ishihara (1996).

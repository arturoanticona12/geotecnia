# Golder (2010): caracterización del material ROM para el proyecto IPCC (resumen de extracción)

**Fuente:** `2010_Golder_Caracterizacion ROM IPCC.pdf` (232 págs.). Es un memorando técnico de Golder Associates Perú, proyecto 099-4151017, del 25 de marzo de 2010, escrito por A. Bustamante y dirigido a J. Pottie (CMA). Las páginas citadas son las del PDF.

**Mapa del PDF:**
- Texto: págs. 1–5.
- Tablas 1–4: págs. 7–10.
- Figuras 1–7: págs. 12–17.
- Anexos:
  - granulometrías de terreno (19–34);
  - densidad in situ por reemplazo de agua (35–42);
  - densidad máxima y mínima (43–47);
  - Gs y absorción (48–49);
  - Los Ángeles (50–57);
  - durabilidad en sulfato (58–65);
  - compresión simple (66–73);
  - carga puntual (74–81);
  - triaxiales CU de Golder (82–156);
  - permeabilidad (157–160);
  - triaxiales CU de Vector de 6" (161–184);
  - carga directa en plataformas, CISMID (185–226);
  - fotos (227–232).

## Objetivo y materiales

- **Objetivo:** caracterización físico-mecánica del desmonte ROM de Antamina para un nuevo esquema de depositación: chancado en el tajo y transporte por faja (IPCC; pág. 1).
- **Litologías** (una muestra de cada una):

  | Muestra | `litologia_informe` | `litologia` | `litologia_detalle` |
  |---|---|---|---|
  | MAR-M-01 | Mármol Negro | Mármol | mármol negro |
  | HOR-M-01 | Hornfels Gris | Hornfels | hornfels gris |
  | INT-M-01 | Intrusivo | Intrusivo | sin subtipo en el informe |
  | EXO-M-01 | Exoskarn Diopsido | Skarn | exoskarn diópsido |

- **Fases** (clase de material para `tipo_material`):
  - **Fase A** = material original del tajo → **ROM**. Muestreo julio–agosto 2009.
  - **Fase B** = el mismo material después del chancado → **Chancado**. Septiembre 2009.
- El informe no indica alteración ni clase de desmonte A/B/C; esas columnas quedan vacías.

## Ensayos de resistencia (CSV `Golder_2010_ROM.csv`: 57 probetas, 19 sets)

Todos los ensayos son **triaxiales CU** (ASTM D4767) sobre la **fracción fina truncada** de la matriz: < 3/8", < 5/8" o < 1". **No son ensayos de gran escala.** La σ′3c va de **125 a 1577 kPa**. Todas las probetas son remoldeadas y saturadas (S ≈ 100 %).

| Set | Fase / clase | Litología | Ø probeta | Dmax | Densidad objetivo | σ′3c (kPa) | Pág. |
|---|---|---|---|---|---|---|---|
| G2010-A-MN-2.8in | A / ROM | Mármol negro | 2.8" (71 mm) | 3/8" | campo 2.135 | 324, 788, 1570 | 82–86 |
| G2010-A-HG-2.8in | A / ROM | Hornfels gris | 2.8" | 3/8" | campo 2.026 | 393, 786, 1577 | 87–91 |
| G2010-A-INT-2.8in | A / ROM | Intrusivo | 2.8" | 3/8" | campo 1.863 | 394, 788, 1570 | 92–96 |
| G2010-A-EXO-2.8in | A / ROM | Exoskarn diópsido | 2.8" | 3/8" | campo 2.273 | 394, 787, 1573 | 97–101 |
| G2010-A-HG-4in | A / ROM | Hornfels gris | 4" (102 mm) | 5/8" | campo 2.026 | 392, 591, 785 | 102–106 |
| G2010-A-INT-4in | A / ROM | Intrusivo | 4" | 5/8" | campo 1.863 | 393, 590, 786 | 107–111 |
| G2010-A-EXO-4in | A / ROM | Exoskarn diópsido | 4" | 5/8" | mínima 2.180 | 392, 588, 783 | 112–116 |
| G2010-B-MN-2.8in | B / Chancado | Mármol negro | 2.8" | 3/8" | campo 2.151 | 391, 788, 1577 | 117–121 |
| G2010-B-HG-2.8in | B / Chancado | Hornfels gris | 2.8" | 3/8" | campo 2.137 | 387, 786, 1576 | 122–126 |
| G2010-B-INT-2.8in | B / Chancado | Intrusivo | 2.8" | 3/8" | campo 2.019 | 390, 785, 1568 | 127–131 |
| G2010-B-EXO-2.8in | B / Chancado | Exoskarn diópsido | 2.8" | 3/8" | campo 2.357 | 393, 784, 1568 | 132–136 |
| G2010-B-MN-4in | B / Chancado | Mármol negro | 4" | 5/8" | mínima 1.821 | 392, 550, 785 | 137–141 |
| G2010-B-HG-4in | B / Chancado | Hornfels gris | 4" | 5/8" | mínima 1.861 | 393, 580, 783 | 142–146 |
| G2010-B-INT-4in | B / Chancado | Intrusivo | 4" | 5/8" | mínima 1.833 | 392, 589, 780 | 147–151 |
| G2010-B-EXO-4in | B / Chancado | Exoskarn diópsido | 4" | 5/8" | mínima 2.161 | 391, 589, 784 | 152–156 |
| G2010-B-MN-6in | B / Chancado | Mármol negro | 6" (151 mm) | 1" | γd 2.024–2.027 | 125, 250, 500 | 161–166 |
| G2010-B-HG-6in | B / Chancado | Hornfels gris | 6" | 1" | γd 2.135–2.139 | 125, 250, 500 | 167–172 |
| G2010-B-INT-6in | B / Chancado | Intrusivo | 6" | 1" | γd 2.023–2.027 | 125, 250, 500 | 173–178 |
| G2010-B-EXO-6in | B / Chancado | Exoskarn diópsido | 6" | 1" | γd 2.332–2.354 | 125, 250, 500 | 179–184 |

**Laboratorios:**
- Sets de 2.8" y 4": laboratorio de Golder Associates Perú (informes GL-481-09 a GL-484-09).
- Sets de 6": Vector Perú S.A.C. (informe VP-209-09E).

**Criterio de falla:**
- Golder: «esfuerzo desviador máximo» de la hoja.
- Vector: pico (primer máximo) del desviador, que es el que usa Vector para su envolvente «pico». Si después hay endurecimiento, los valores al 14 % van en `notas`.

**Cómo se llenaron las columnas:**
- `sigma3_kPa` = σ′3 de consolidación.
- `sigma1_kPa` = σ′1 en la falla.
- `u_falla_kPa` = exceso de presión de poros en la falla.
- `p_falla_kPa` = (σ′1+2σ′3)/3, calculado.
- `q_falla_und_kPa` = σ′1−σ′3.
- e0: tomado del informe en Golder. En Vector se calculó con el Gs de finos de Golder.

**Verificación:** todas las hojas resumen se verificaron en la imagen. Las de Exoskarn de Vector (págs. 179–181) no tienen capa de texto y se transcribieron de la imagen.

## Envolventes ajustadas por el informe (c en kPa, φ en °)

**Tabla 3, Fase A (pág. 9), y hojas Mohr de Golder:**

| Material | 2.8": c / φ / c′ / φ′ en Tabla 3 | 2.8": hoja Golder (pág.) | 4": Tabla 3 = hoja |
|---|---|---|---|
| Mármol negro | 9 / 10 / 3 / 31 | **871 / 10 / 259 / 31** (84) | sin ensayo |
| Hornfels gris | 2 / 15 / 0 / 35 | **149 / 15 / 33 / 35** (89) | 376 / 3 / 272 / 14 (104) |
| Intrusivo | 3 / 10 / 1 / 30 | **313 / 10 / 103 / 30** (94) | 0 / 17 / 0 / 36 (109) |
| Exoskarn diópsido | 1 / 11 / 0 / 29 | **80 / 11 / 0 / 29** (99) | 4 / 17 / 29 / 26 (114) |

**Tabla 4, Fase B (pág. 10)** (coincide con las hojas, págs. 119–154, 165–183):

| Material | 2.8" Golder | 4" Golder | 6" Vector (pico) |
|---|---|---|---|
| Mármol negro | 927 / 15 / 188 / 35 | 47 / 11 / 67 / 16 | 60 / 30 / 25 / 36 |
| Hornfels gris | 23 / 18 / 0 / 40 | 0 / 15 / 22 / 21 | 0 / 26 / 6 / 29 |
| Intrusivo | 162 / 15 / 42 / 34 | 7 / 12 / 0 / 23 | 0 / 12 / 0 / 28 |
| Exoskarn diópsido | 102 / 16 / 0 / 37 | 0 / 14 / 14 / 26 | 0 / 24 / 0 / 34 |

**Envolvente al 12 % de deformación (Vector):** c′/φ′ = 10/38 (mármol negro), 5/39.2 (hornfels gris), 0/38.1 (intrusivo) y 0/42 (exoskarn).

**Resumen del propio informe** (pág. 4–5):
- A densidad mínima: c′ = 0–67 kPa y φ′ = 16–26°.
- A densidades mayores: c′ = 0–25 kPa y φ′ = 28–36°.
- La resistencia del mármol negro y del exoskarn crece con la densidad (Fig. 6).

El informe no hace ajustes de Leps ni de ley de potencia.

## Granulometría de terreno por litología (Tabla 1, pág. 7, verificada)

| Litología | Fase | w nat. (%) | TM | % < 3" | Grava (%) | Arena (%) | Finos (%) | Cu / Cc del informe (Fig. 1–4) | D10 / D30 / D50 / D60 calc. (mm) |
|---|---|---|---|---|---|---|---|---|---|
| Mármol negro | A (ROM) | 2.2 | 35" | 34.7 | 88.9 | 8.3 | 2.8 | 88.3 / 4.5 | 2.5 / 61 / 195 / 256 |
| Mármol negro | B (Chancado) | 2.9 | 12" | 66.0 | 77.4 | 15.4 | 7.2 | 485.3 / 26.6 | 0.11 / 11.3 / 35.8 / 52.4 |
| Hornfels gris | A (ROM) | 2.4 | > 35" (94.9 % pasa 35") | 28.6 | 96.3 | 2.8 | 0.88 | 10.3 / 1.5 | 20.7 / 80 / 157 / 207 |
| Hornfels gris | B (Chancado) | 2.3 | 12" | 64.4 | 91.9 | 5.4 | 2.7 | 7.9 / 1.0 | 6.8 / 24.4 / 44.8 / 64.6 |
| Intrusivo | A (ROM) | 3.8 | 30" | 39.4 | 92.0 | 6.4 | 1.6 | 30.3 / 1.8 | 8.0 / 56 / 126 / 185 |
| Intrusivo | B (Chancado) | 2.7 | 12" | 65.3 | 75.4 | 17.6 | 7.0 | 400 / 10 | 0.15 / 8.6 / 33.7 / 58.6 |
| Exoskarn diópsido | A (ROM) | 3.1 | 19" | 79.8 | 78.2 | 19.1 | 2.7 | 41.3 / 2.7 | 0.78 / 8.1 / 22.2 / 33.2 |
| Exoskarn diópsido | B (Chancado) | 3.0 | 12" | 89.3 | 71.6 | 23.0 | 5.4 | 76.2 / 6.4 | 0.24 / 5.2 / 13.0 / 18.6 |

- Grava, arena y finos son de la muestra global, con cortes en #4 y #200; coinciden con la Tabla 2.
- D10–D60 se calcularon por interpolación log-lineal (script `paginas/Golder2010/gradacion_terreno.py`).
- **Matriz < 3" (Tabla 2), % grava / arena / finos:**

  | Litología | Fase A | Fase B |
  |---|---|---|
  | Mármol negro | 71.4 / 22.8 / 5.8 | 68.9 / 23.6 / 7.5 |
  | Hornfels gris | 86.2 / 11.2 / 2.6 | 85.6 / 10.8 / 3.6 |
  | Intrusivo | 80.4 / 16.3 / 3.3 | 67.4 / 25.4 / 7.2 |
  | Exoskarn diópsido | 76.5 / 20.9 / 2.6 | 72.5 / 23.1 / 4.4 |

- **La granulometría de la fracción ensayada en los triaxiales no se informa.**

## Ensayos índice por litología (Tabla 2, pág. 8, verificada, y anexos)

| Litología | Fase | γ in situ / γd terreno (g/cm³) | Gs grueso (Tabla 2) | Gs fino D854 | Absorción C127 (%) | Durabilidad (%) | LA (%) | σc carga puntual (MPa) | UCS lab. (MPa; valores) | k (m/s) | Asent. carga directa (cm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mármol negro | A | 2.185 / 2.135 | 2.696 | 2.763 | 0.34 | 43.4 | 62.1 | 32.24 | 44.7 (41.0; 48.3) | — | — |
| Mármol negro | B | 2.200 / 2.151 | 2.725 | 2.747 | 0.33 | 49.8 | 62.4 | 24.56 | 49.6 (41.5; 57.7) | — | 4.8 |
| Hornfels gris | A | 2.055 / 2.026 | 2.733 | 2.791 | 0.24 | 0.7 | 23.7 | 72.99 | 49.2 (46.8; 51.6) | 3.2E-06 | — |
| Hornfels gris | B | 2.162 / 2.137 | 2.740 | 2.802 | 0.12 | 0.6 | 20.3 | 100.42 | 65.5 (62.6; 68.3) | 2.6E-06 | 5.6 |
| Intrusivo | A | 1.931 / 1.865 | 2.451 | 2.674 | 1.66 | 33.4 | 49.8 | 80.56 | 46.8 (48.4; 45.1) | 2.5E-06 | — |
| Intrusivo | B | 2.060 / 2.019 | 2.647 | 2.742 | 2.17 | 18.6 | 32.2 | 78.06 | 54.0 (56.1; 51.8) | 2.2E-06 | 3.6 |
| Exoskarn diópsido | A | 2.350 / 2.273 | 3.172 | 3.484 | 1.44 | 5.9 | 37.0 | 67.79 | 73.3 (79.3; 67.3) | — | — |
| Exoskarn diópsido | B | 2.418 / 2.357 | 3.102 | 3.338 | 1.30 | 6.7 | 27.6 | 124.78 | 97.4 (101.7; 93.1) | — | 5.1 |

**Notas a la tabla:**
- **Densidad in situ:** por reemplazo de agua (págs. 35–42).
- **Gs:**
  - Gs grueso según la Tabla 2. En Fase A no coincide exactamente con el Gs bulk de C127 de la pág. 48 (2.717 / 2.737 / 2.461 / 3.212); en Fase B sí coincide.
  - Gs fino: pág. 49.
- **Absorción:** pág. 48.
- **Durabilidad:** pérdida corregida en sulfato de **magnesio** según las hojas de las págs. 58–65. El texto de la pág. 2 dice «sulfato de sodio».
- **Los Ángeles:** ASTM C535 (págs. 50–57).
- **Carga puntual:** 4 a 8 probetas (págs. 74–81). Is(50) promedio:

  | Litología | Fase A (kg/cm²) | Fase B (kg/cm²) |
  |---|---|---|
  | Mármol negro | ≈13.7 | ≈10.4 |
  | Hornfels gris | ≈31 | ≈42 |
  | Intrusivo | ≈34 | ≈33 |
  | Exoskarn diópsido | ≈29 | ≈53 |

  La σc estimada de las hojas está en kg/cm². Ejemplo: mármol negro A, 321–367 kg/cm², con promedio de 32.2 MPa.
- **UCS de laboratorio:** ASTM D2938, dos probetas por caso, estandarizada según Protodyakonov (págs. 66–73).
- **Permeabilidad:** pared flexible, ASTM D5084, sobre material < 5/8" (págs. 157–160). La columna de la Fase B en la Tabla 2 dice «cm/s», pero las hojas dan m/s.
- **Carga directa estática:** CISMID, en plataformas de 1 m de material chancado, con carga máxima de 6 kg/cm² (págs. 185–226).
- **Densidad máxima/mínima** (ASTM D4253/4254, fracción < 5/8"; págs. 43–47):

  | Material | γd mín | γd máx (g/cm³) |
  |---|---|---|
  | Exoskarn A | 2.175 | 2.621 |
  | Mármol negro B | 1.821 | 2.236 |
  | Hornfels gris B | 1.861 | 2.308 |
  | Intrusivo B | 1.833 | 2.237 |
  | Exoskarn B | 2.161 | 2.647 |

  No hay datos de la Fase A para mármol negro, hornfels e intrusivo. Las probetas de 4" de «densidad mínima» se armaron a esos valores, por lo que su Dr ≈ 0 %. No se calculó Dr en el CSV.

**Lectura del informe** (pág. 3): el mármol negro es el material más débil y degradable (LA ≈ 62 %, durabilidad 43–50 %, σc PL 25–32 MPa) y el que más finos tiene. El hornfels gris es el más competente (LA 20–24 %, durabilidad < 1 %).

## Dudas y datos ilegibles

1. **Escala:** los triaxiales son de pequeña escala, con fracción < 3/8" a < 1" de un ROM con TM de 19" a 35". Su utilidad para una base de datos de desmonte a gran confinamiento es limitada. σ′3 máx = 1577 kPa.
2. **Tabla 3, Fase A, 2.8":** c y c′ figuran como kPa pero parecen estar en kg/cm² (871 → 9; 259 → 3; 149 → 2; 33 → 0; 313 → 3; 103 → 1; 80 → 1). Los φ coinciden. Las hojas de laboratorio (págs. 84–99) son la referencia.
3. **Tamaño máximo en Fase B:** la Tabla 2 repite el TM de la Fase A (35/35/30/19"), pero el texto (pág. 2), la Tabla 1 y las figuras indican TM de 9–12" después del chancado.
4. **Densidad promedio en la Tabla 4:** para mármol negro 4" de Fase B, la tabla da 1.722, que es solo el valor de la probeta 3. Las probetas 1 y 2 tienen 1.825 y 1.824. En la Tabla 3, exoskarn 4" de Fase A da 2.094: el promedio de 2.180, 2.056 y 2.046 es 2.094, así que coincide, aunque las probetas difieren de la «densidad mínima» de 2.180 declarada.
5. **Plantilla posiblemente copiada en Vector:** las cabeceras iniciales de mármol negro e intrusivo de 6" son idénticas (H, Ø, w = 4.5 %, γd 2.027 / 2.025 / 2.024–2.023); los valores finales difieren. Además, B = 0.86–0.93 en todas las probetas Vector, menos que el 0.95 habitual.
6. **Punto de falla en Vector:** su punto «pico» de intrusivo a 500 kPa parece estar en ε ≈ 2.5 %, no en el máximo del desviador (1.75 %). En exoskarn a 125 kPa no hay pico (endurecimiento hasta el 14 %) y Vector marcó ε = 1.0 %. Yo usé esos mismos puntos y dejé los valores finales en `notas`.
7. **Exoskarn de Vector (págs. 179–181):** solo es imagen; se transcribió a mano.
8. **Fecha del exoskarn 4" de Fase B:** la hoja dice «07 de Enero de 2009» (pág. 152). Es probable que sea 2010.
9. **Gs grueso de Fase A:** difiere entre la Tabla 2 y la hoja C127. No se resolvió.
10. **Granulometrías de detalle:** las de terreno de las págs. 19–34 no se transcribieron. Se usó la Tabla 1, que las resume. Las curvas de las Fig. 1–4 confirman las mismas formas.

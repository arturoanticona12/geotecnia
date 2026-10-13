# Ensayos de laboratorio Anddes Geolab, desmonte de Antamina (solicitud EPE-23.10.141)

Carpeta de origen: `Data Antamina\ensayos\` (25 PDF, 60 páginas). Todos los informes son de **Anddes Geolab SAC** para Antamina (proyecto «Perforaciones Geotécnicas e Hidrogeológicas 2023», solicitado por Gary Olivo) y se emitieron entre mayo y octubre de 2024. Cada número se extrajo con PyMuPDF y se comprobó en la imagen renderizada de la página (`paginas\ensayos\*.png`). Las tablas triaxiales se leyeron con un parser por coordenadas (`parse_tx.py`, `tx_parsed.json`), y los CSV se generan con `construir_csv.py`.

Salidas:

- `ensayos_triaxial_CU.csv`: 15 probetas (5 series × 3 σ′3).
- `ensayos_corte_directo.csv`: 15 puntos (5 series × 3 σn).
- `ensayos_indices.csv`: 5 muestras compuestas.

## 1. Materiales

No son 13 + 12 + 12 muestras ensayadas por separado. Cada PDF corresponde a **una muestra compuesta** (una «ruma» o «pila»), y la lista M-x, H-x o I-x enumera las submuestras que se mezclaron.

| Clave | Muestra (informe) | Litología informe → normalizada | Zona / profundidad | Clase de desmonte |
|---|---|---|---|---|
| M | 01 (Ruma 01), M-1 al M-13 | Marmol → Mármol | Patio de servicios / Botadero Este, 40–90 m | no indicada |
| H | 02 (Ruma 02), H-1 al H-12 | HORNFELS → Hornfels | Patio de servicios / Botadero Este, 40–90 m | no indicada |
| I | 03 (Ruma 03) / Fase 10 A, I-1 al I-12 (I-1 al I-11 en SUCS, Proctor, CA y LSDS) | Intrusivo → Intrusivo | Botadero Este, 20–60 m | no indicada |
| P1 | Pila 01: MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B | Mármol + Hornfels → Mezcla (proporción no indicada) | Pilas Experimentales Medio Ambiente | «Material B» → B (inferido) |
| P2 | Pila 02: MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A | Intrusivo → Intrusivo | Pilas Experimentales Medio Ambiente | «Material A» → A (inferido) |

- **litologia_detalle y alteracion**: ningún informe da subtipo (mármol blanco o negro, tipo de intrusivo, etc.) ni alteración o meteorización. Esas columnas quedan vacías.
- **tipo_material (ROM / Chancado / Enrocado)**: ningún informe lo indica, así que la columna queda vacía. M, H e I provienen de perforaciones en el Botadero Este a 20–90 m de profundidad, es decir, son desmonte ya depositado en el botadero y por su origen serían **probablemente ROM**, pero el documento no lo dice. Para las pilas experimentales (P1, P2) no hay ningún indicio.
- **Pila 01**: «Mármol + Hornfels» sin proporciones. Los códigos MP1-B-M-1/M2/M3 y MP1-H podrían significar 3 submuestras + 1, pero «M» puede ser «muestra»; no se infiere ninguna proporción.
- **Preparación común**: todas las probetas (TX y LSDS) se **reconstituyeron al 90 % de la MDS del Proctor estándar** y al contenido de agua óptimo. Las densidades iniciales cuadran con 0,9 × MDS: 2,182; 2,100; 1,921; 2,094 y 1,831 g/cm³.

## 2. Ensayos índice (por muestra)

| | Mármol (M) | Hornfels (H) | Intrusivo (I) | Pila 01 M+H (P1) | Pila 02 Intrusivo (P2) |
|---|---|---|---|---|---|
| Dmax terreno (100 % pasa) | 75 mm (3 in) | 75 mm | 75 mm | 75 mm | 75 mm |
| Grava / arena / finos (%) | 65 / 25 / 10 | 68 / 21 / 11 | 63 / 29 / 8 | 59 / 30 / 11 | 57 / 34 / 9 (+1 % bolonería) |
| D10 / D30 / D60 informados (mm) | 1,54 / 2,76 / 22,04 | 1,54 / 3,55 / 19,45 | 0,13 / 3,03 / 15,35 | 1,54 / 1,47 / 12,51 | 0,08 / 1,45 / 11,49 |
| Cu / Cc informados | 14,29 / 0,22 | 12,61 / 0,42 | 121,26 / 4,74 | 8,11 / 0,11 | 138,86 / 2,21 |
| D10 / D30 / D50 / D60 interpolados (mm) | 0,075 / 2,77 / 13,4 / 22,2 | <0,075 / 3,56 / 12,9 / 19,6 | 0,126 / 2,98 / 9,9 / 15,3 | <0,075 / 1,50 / 8,0 / 12,6 | 0,084 / 1,50 / 7,1 / 11,5 |
| LL / LP / IP | NP / NP / NP | 16 / NP / NP | 17 / NP / NP | NP / NP / NP | NP / NP / NP |
| SUCS | GP-GM | GP-GM | GP-GM | GP-GM | GW-GM |
| Proctor estándar: γd máx (kN/m³) / ρd máx (g/cm³) / w óptimo (%) | 23,780 / 2,425 / 6,8 | 22,876 / 2,333 / 7,7 (*) | 20,930 / 2,134 / 9,8 (*) | 22,819 / 2,327 / 7,4 | 19,951 / 2,034 / 11,1 |
| Proctor corregido por sobretamaño: γd (kN/m³) / w (%) | 25,754 / 3,9 | 24,533 / 4,7 | 22,230 / 6,7 | 24,012 / 5,4 | 20,797 / 8,6 |
| Sobretamaño: Gs bulk / w (%) | 2,94 / 0,1 | 2,80 / 0,3 | 2,56 / 1,0 | 2,79 / 0,8 | 2,39 / 2,0 |
| Gs (curva de 100 % saturación del Proctor) | 3,06 | 2,94 | 2,75 | 2,90 | 2,74 |
| Método Proctor | fuera de método | fuera de método | fuera de método | Método C | Método C |
| w natural (CA, informado / calculado) | 3 / 2,94 % | 3 / 3,28 % | 5 / 5,11 % | 3 / 2,81 % | 6 / 5,52 % |

(*) **Discrepancia en el w óptimo**: la hoja Proctor de H da 7,7 %, pero el TX dice «óptimo 6,0 %» y las probetas TX se moldearon al 6,0 %; el LSDS usa 7,7 %. Lo mismo ocurre en I: el Proctor da 9,8 %, el TX dice 8,0 % y moldea al 8,0 %, y el LSDS usa 9,8 %. En M, P1 y P2 los tres documentos coinciden. Las MDS sí coinciden en todos los casos.

Páginas: granulometría en SUCS p.1; límites y SUCS en SUCS p.2; Proctor p.1; CA p.1.

## 3. Triaxial CU de 6 in (ASTM D4767-11(2020))

- **Probetas**: Ø 152 mm × 310 mm, consolidación isotrópica con contrapresión de 187 kPa, B = 0,95–0,98, velocidad 0,025 cm/min y σ′3 = 500, 1000 y 2000 kPa. Son 15 probetas en total.
- **Dmax de la probeta**: el informe no lo indica. La muestra de terreno tiene TM 3 in, y con el criterio D/6 correspondería ≤ 25 mm (como el TM 1 in del LSDS), pero no consta.
- **Convenciones**: el informe usa p y q del MIT, con q = (σ1 − σ3)/2. En el CSV, `q_kPa` es el desviador completo, `p_falla_kPa` es p′ (MIT) y `q_falla_und_kPa` es q′ (MIT). σ′1 se calculó como σ3 − u + desviador y cuadra con el p′ del informe (± 0,2 kPa).
- **Criterio de falla del informe**: 15 % de deformación axial, usado para la envolvente efectiva y para Su. El CSV añade el estado de desviador máximo (`q_dev_max_kPa`, `eps_q_dev_max_pct`, `u_q_dev_max_kPa`) y el de la razón σ′1/σ′3 máxima.
- **Su**: es q′ (MIT) al 15 %.

| Serie | c′ (kPa) | φ′ (°) | a′ (kPa) / α′ (°) | Total: c / φ (criterio) | Su / σ′3 | Página |
|---|---|---|---|---|---|---|
| Mármol (M) | 40,0 | 44,0 | 28,9 / 34,7 | 29,0 kPa / 19,0° (2 %) | 0,49 | 1, 7 |
| Hornfels (H) | 72,0 | 40,5 | 55 / 33,0 | 72,0 kPa / 16,5° (2 %) | 0,44 | 1, 7 |
| Intrusivo (I) | 82,0 | 44,0 | 59,3 / 34,7 | 163,0 kPa / 16,0° (2 %) | 0,72 (500 kPa), 0,45 (1000–2000 kPa) | 1, 7 |
| Pila 01 M+H | 61,0 | 42,0 | 45,3 / 33,9 | 0 / 25,0° (15 %) | 0,73 | 1, 7 |
| Pila 02 Intrusivo | 57,0 | 42,0 | 42,7 / 33,8 | 0 / 24,0° (15 %) | 0,69 | 1, 7 |

La página 7 lleva la nota: «La interpretación presentada en la presente página ha sido un requerimiento explícito del solicitante», por lo que el laboratorio se exime de responsabilidad sobre ella.

Valores al 15 % (desviador / u, en kPa; detalle en el CSV):

| σ′3 (kPa) | Mármol | Hornfels | Intrusivo | Pila 01 | Pila 02 |
|---|---|---|---|---|---|
| 500 | 375,7 / 420,8 | 555,4 / 428,1 | 718,8 / 377,2 | 584,1 / 401,8 | 599,0 / 385,9 |
| 1000 | 893,7 / 893,1 | 982,1 / 905,1 | 983,8 / 868,0 | 1213,9 / 801,6 | 1368,6 / 771,1 |
| 2000 | 2018,3 / 1581,2 | 1674,4 / 1663,4 | 1680,0 / 1714,2 | 3064,8 / 1313,8 | 2782,7 / 1365,7 |

**Comportamiento.** En M, H e I el desviador alcanza un máximo a ε ≈ 1,75–2,5 %, cae con el aumento de u (contractivo) y luego se recupera parcialmente. Hay excepciones dilatantes en las que el máximo está al 14–15 %: M a 2000 kPa y H a 500 kPa. Las pilas son más resistentes a 2000 kPa: P1 llega a 3065 kPa de desviador y P2 a 2783 kPa, frente a 1674–2018 kPa en M, H e I.

## 4. Corte directo de gran escala (LSDS, ASTM D3080/D3080M-23)

- **Equipo y condiciones**: caja de 30,5 × 30,5 cm y 17,8 cm de altura, TM 1 in, separación de cajas 1,0 mm, velocidad 0,5 mm/min y consolidación de 16 h.
- **Saturación**: el informe dice «saturados durante el ensayo, salvo excepciones».
- **Esfuerzos normales**: σn = 300, 600 y 1200 kPa (P1: 300, 600 y 1000 kPa). Son 15 puntos en total.
- **Valores informados**: τ pico y τ a 6,6 cm de desplazamiento. No hay residual verdadero.

| Serie | τ pico a σn 300 / 600 / 1200 (kPa) | Pico: c (kPa) / φ (°) / μ | 6,6 cm: c (kPa) / φ (°) | ρd / w inicial |
|---|---|---|---|---|
| Mármol | 219,5 / 469,5 / 984,3 | 0 / 39,0 / 0,68 | 0 / 38,7 | 2,183 / 6,80 % |
| Hornfels | 255,7 / 476,1 / 998,1 | 0 / 39,5 / 0,69 | 0 / 39,5 | 2,100 / 7,70 % |
| Intrusivo | 228,1 / 468,1 / 945,1 | 0 / 38,1 / 0,67 | 0 / 36,5 | 1,921 / 9,80 % |
| Pila 01 M+H | 356,3 / 625,3 / 947,3 (σn = 1000) | 109,6 / 40,1 / 0,70 | 100,0 / 40,0 | 2,094 / 7,40 % |
| Pila 02 Intrusivo | 353,9 / 633,7 / 1019,2 | 161,1 / 36,0 / 0,63 | 169,2 / 34,9 | 1,831 / 11,10 % |

Las pilas muestran φ secantes de 50° a 300 kPa que bajan a 40–43° a 1000–1200 kPa. Es una envolvente curva, y la «cohesión» de 100–169 kPa es un artefacto del ajuste lineal. M, H e I tienen φ secante prácticamente constante (36–40°). Todos los especímenes se comprimen durante el corte, con un desplazamiento vertical de 3 a 10 mm según el gráfico; el informe no tabula esos valores.

Páginas: envolventes en p.1; densidades, w y gráficos en p.2.

## 5. Resumen por litología

- **Mármol (M, Ruma 01)**
  - Grava limosa pobremente gradada (GP-GM, NP), con 10 % de finos y la MDS más alta (2,425 g/cm³; Gs 3,06).
  - TX CU al 15 %: c′ = 40 kPa y φ′ = 44,0°.
  - LSDS: φ pico = 39,0° con c = 0; a 6,6 cm, φ = 38,7°.
  - Su/σ′3 = 0,49.
- **Hornfels (H, Ruma 02)**
  - GP-GM con LL 16 NP y 11 % de finos; MDS 2,333 g/cm³ (Gs 2,94).
  - TX CU: c′ = 72 kPa y φ′ = 40,5°, el φ′ más bajo de las cinco series.
  - LSDS: φ = 39,5° (pico y a 6,6 cm), el más alto de las tres litologías puras.
  - Su/σ′3 = 0,44.
- **Intrusivo**: tiene dos muestras.
  - **Ruma 03 / Fase 10 A**: GP-GM con LL 17 NP y 8 % de finos; MDS 2,134 g/cm³ (Gs 2,75). TX CU: c′ = 82 kPa y φ′ = 44,0°. LSDS: φ pico = 38,1° y φ a 6,6 cm = 36,5°, con la mayor caída posterior al pico.
  - **Pila 02**: GW-GM NP con 9 % de finos y la MDS más baja (2,034 g/cm³; Gs 2,74; w natural 6 %). TX CU: c′ = 57 kPa y φ′ = 42,0°. LSDS: c = 161 kPa y φ = 36,0° (envolvente curva).
- **Mezcla Mármol + Hornfels (Pila 01)**
  - GP-GM NP con 11 % de finos; MDS 2,327 g/cm³ (Gs 2,90).
  - TX CU: c′ = 61 kPa y φ′ = 42,0°.
  - LSDS: c = 109,6 kPa y φ = 40,1°, con φ secante de 50° a 43°.
  - Es la mayor resistencia no drenada a 2000 kPa (Su/σ′3 = 0,73).

**Rango de esfuerzos.** En el TX, σ′3 va de 500 a 2000 kPa y σ′1 en la falla al 15 % va de 455 a 3751 kPa, con p′ entre 267 y 2219 kPa. En el LSDS, σn va de 300 a 1200 kPa. **No hay datos por encima de 2 MPa de confinamiento.**

## 6. Dudas y datos ilegibles

No hay datos ilegibles: todas las tablas son nítidas.

1. **D10 informados incoherentes.** Es el caso de M, H y P1 (D10 = 1,54 mm con 10–11 % pasando 0,075 mm) y de P1 además D30 (1,47) < D10 (1,54). Los Cu y Cc informados de esas muestras no son fiables. En el CSV se añadieron D-valores interpolados (`*_interp`). Cuando pasa ≥ 10 % por el N° 200, el D10 real es < 0,075 mm y no se puede obtener por tamizado.
2. **Dmax de las probetas triaxiales no informado.** El LSDS usa TM 1 in; la muestra de terreno es de 3 in. El triaxial no declara escalamiento ni tamizado previo.
3. **Gs**: no hay ensayo de gravedad específica. El Gs usado (3,06 / 2,94 / 2,75 / 2,90 / 2,74) es el rótulo de la curva de saturación del Proctor, y no se indica a qué fracción corresponde. Las páginas 4 del TX contienen además un texto oculto «2,70» que no se ve en la imagen y no se usó. Los e0 del CSV están calculados con el Gs del Proctor.
4. **w de moldeo TX vs Proctor y LSDS** en H (6,0 vs 7,7 %) e I (8,0 vs 9,8 %), con la misma ρd.
5. **Submuestras**: el triaxial dice I-1 al I-12, mientras que SUCS, Proctor, CA y LSDS dicen I-1 al I-11.
6. **Clase de desmonte A/B de las pilas**: se infiere de «Material A» y «Material B» en el N° de muestra; el informe no lo define como clase de desmonte.
7. **tipo_material (ROM / Chancado / Enrocado)**: no se indica en ningún informe.
8. El N° de informe del LSDS de la Pila 02 termina en «_SUCS», probablemente una errata.
9. Pila 02 a 2000 kPa: w final (10,5 %) menor que el inicial (11,1 %), tal cual en el informe.
10. Pila 02 SUCS: 1 % de bolonería, aunque pasa 100 % por 3 in y grava + arena + finos = 100 %.
11. El Proctor de M, H e I está marcado «Fuera de método», sin explicación (probablemente por exceso de sobretamaño).
12. Las envolventes totales (p.7) usan un criterio distinto del de las efectivas (2 % en M, H e I; 15 % en las pilas) y son una interpretación pedida por el cliente.

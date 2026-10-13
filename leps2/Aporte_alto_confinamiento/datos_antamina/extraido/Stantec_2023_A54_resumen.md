# Stantec 2023, Apéndice A.5.4: propiedades índice del desmonte chancado

**Fuente:** `2023_Stantec_A.5.4_Propiedades Desmonte Chancado.pdf` (1 lámina A3, L-01, fecha 9/14/2023)
**Proyecto:** Ingeniería de Prefactibilidad Gate 2A del depósito de Relaves Site 3 y Depósito de desmonte EE4BE-S3 (Stantec).
**Tipo de material:** Chancado.
**CSV de ensayos:** no se generó. La lámina no presenta ensayos individuales identificables: los puntos del gráfico τ–σn no tienen identificación de probeta ni σ3. Es una compilación de Golder (2010), Golder (2021) y WSP (2023), que se extraen de sus informes originales.

## Contenido y objetivo

La lámina resume las propiedades índice y de resistencia que sirven de base al diseño del desmonte chancado. Contiene:

1. Granulometrías de terreno por litología (Mármol Negro, Hornfels Gris, Intrusivo, Exoskarn Diópsido y Tipo A, B y C), las muestras escaladas para laboratorio (Golder 2021 y WSP 2023) y las bandas de Golder (1987): A = rango de enrocado, B = enrocado en triaxiales, C = enrocado grueso.
2. La tabla «% de Material Presente».
3. El gráfico de resistencia τ–σn con la envolvente adoptada.
4. Gs, UCS, abrasión y durabilidad por litología.
5. La densidad seca vs p′ con su envolvente propuesta (base: Hawley y Cunning, 2017).
6. Un recuadro con edómetros de pared flexible (asentamiento vs carga).

## Clasificación litológica (tipo_material = Chancado)

| litologia_informe | litologia | litologia_detalle | alteracion | Datos de la lámina para esta litología |
|---|---|---|---|---|
| Mármol Negro | Mármol | mármol negro | no indicada | granulometría, tabla de %, Gs, UCS, abrasión, durabilidad, edómetro |
| Hornfels Gris | Hornfels | hornfels gris | no indicada | ídem; pared flexible Golder (2010): w 5 %, k 2,6×10⁻⁶ m/s |
| Intrusivo | Intrusivo | (no indicado) | no indicada | ídem; pared flexible Golder (2010): w 5,3 %, k 2,2×10⁻⁶ m/s |
| Exoskarn Diposido / Diopsido (escrito así en la leyenda y en la tabla) | Skarn | exoskarn diopsídico | no indicada | ídem |
| Mármol Negro (WSP, 2023) | Mármol | mármol negro | no indicada | solo % de la matriz <3" |
| Tipo A, B y C (curvas moradas) | Otra (bandas granulométricas de Golder 1987, sin litología) | — | — | solo granulometría |

La lámina no describe la mineralogía ni el origen (tajo, banco o fase), y no da carga puntual ni absorción. No hay mezclas de litologías. Las propiedades por litología están en las tablas de granulometría e índices que siguen.

## Envolvente de resistencia (gráfico superior derecho)

- Leyenda:
  - Puntos: «(WSP, 2023)», «(Golder, 2021)» e «IPCC Study (Golder, 2010)».
  - Envolvente continua azul: **«Baja Calidad (Piteau, 2019)»**.
  - Referencias segmentadas: Leps Low, Average y High.
- Es la única envolvente continua, así que se interpreta como la envolvente de diseño del chancado. La lámina **no da parámetros numéricos** (ni φ, ni c, ni A y b).
- Los valores se extrajeron de la polilínea vectorial del PDF, calibrada con las etiquetas de los ejes (0-5000 kPa). La precisión estimada es de ±15 kPa.

| σn (kPa) | 100 | 250 | 500 | 1000 | 1500 | 2000 | 2500 | 3000 | 3500 | 4000 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| τ (kPa) | 76 | 184 | 356 | 696 | 1004 | 1307 | 1602 | 1897 | 2194 | 2496 | 2799 | 3120 |
| φ_sec (°) | 37,2 | 36,4 | 35,5 | 34,8 | 33,8 | 33,2 | 32,7 | 32,3 | 32,1 | 32,0 | 31,9 | 32,0 |

Ajuste potencial propio (no del informe): τ ≈ 0,931·σn^0,954 (kPa). Los valores por debajo de ~100 kPa están limitados por la resolución del dibujo.

## Granulometría: tabla «% de Material Presente» (verificada en la imagen)

| Tipo de desmonte | 12"–36" | 3"–12" | Gravas | Arenas | Finos | Matriz <3": Gravas | Arenas | Finos |
|---|---|---|---|---|---|---|---|---|
| Mármol Negro | – | 34 | 43,4 | 15,4 | 7,2 | 68,9 | 23,6 | 7,5 |
| Hornfels Gris | – | 35,6 | 56,3 | 5,4 | 2,7 | 85,6 | 10,8 | 3,6 |
| Intrusivo | – | 34,7 | 40,7 | 17,6 | 7 | 67,4 | 25,4 | 7,2 |
| Exoskarn Diópsido | – | 10,7 | 60,9 | 23 | 5,4 | 72,5 | 23,1 | 4,4 |
| Mármol Negro (WSP, 2023) | – | – | – | – | – | 80,2–99,4 | 0,6–14,6 | 1,2–5,8 |

Fuente de la granulometría: Golder (2010), Golder (2021) y WSP (2023). Las curvas de las muestras escaladas para laboratorio aparecen solo en el gráfico; no las digitalicé.

## Ensayos índice (leídos de gráfico raster, precisión aproximada ±0,02 en Gs, ±2 MPa y ±1 %)

Colores: dorado = Mármol Negro, azul = Hornfels Gris, verde = Intrusivo y rojo = Exoskarn Diópsido.

| Litología | Gs grueso | Gs fino | UCS mín / Q1 / mediana / Q3 / máx (MPa) | UCS promedio (MPa) | Abrasión (%) | Durabilidad (%) |
|---|---|---|---|---|---|---|
| Mármol Negro | 2,73 | 2,75 | 21 / 23 / 26 / 32 / 41 | 30 | 63 | 50 |
| Hornfels Gris | 2,74 | 2,80 | 63 / 81 / 96 / 110 / 116 | 94 | 20 | 0,6 |
| Intrusivo | 2,65 | 2,74 | 52 / 60 / 80 / 82 / 83 | 72 | 32 | 19 |
| Exoskarn Diópsido | 3,10 | 3,34 | 81 / 100 / 122 / 142 / 148 | 120 | 28 | 7 |

La lámina no define «Abrasión» ni «Durabilidad» (presumiblemente Los Ángeles y algún índice de durabilidad o slake), ni el ensayo de UCS.

## Densidad seca vs p′ (gráfico inferior derecho)

- Puntos de Hawley y Cunning (2017): triaxiales y edómetros de ROM, lixiviado y chancado. También aparecen puntos coloreados por litología y dos ensayos de pared flexible de Golder (2010):
  - Intrusivo: w = 5,3 %, k = 2,2×10⁻⁶ m/s.
  - Hornfels: w = 5 %, k = 2,6×10⁻⁶ m/s.
- La «Envolvente Propuesto» (roja) se extrajo del vector. ρd ≈ 2,08 t/m³ a p′ = 0; 2,22 a 2 MPa; 2,37 a 4 MPa; 2,54 a 6 MPa y 2,62 a 7 MPa. Ajuste propio: ρd ≈ 2,079·e^(0,0033·p′), con p′ en ×0,1 MPa. La lámina no muestra la ecuación.

## Edómetro de pared flexible (recuadro)

Asentamiento acumulado por unidad de altura vs carga, hasta ~590-600 kPa. Valores máximos aproximados, tomados del borde inferior de cada polilínea vectorial: Hornfels ≈ 11 %, Exoskarn ≈ 10 %, Mármol Negro ≈ 9,5 % e Intrusivo ≈ 7 %. Las curvas incluyen descarga. La lámina no da etiquetas numéricas.

## Ensayos no drenados

No hay.

## Dudas

1. La lámina no da parámetros de resistencia numéricos. La envolvente «Baja Calidad (Piteau, 2019)» se tabuló desde el vector.
2. No se puede asignar cada punto τ–σn a un ensayo ni a un σ3. Se recomienda usar los informes originales (Golder 2010, Golder 2021 y WSP 2023).
3. Los índices son lecturas de un gráfico raster y no tienen el número de muestras.
4. La relación entre la clasificación A/B/C de la lámina (bandas de Golder, 1987) y la «clase de desmonte» de Antamina no es explícita. Aquí A, B y C son rangos granulométricos, no clases geoquímicas.

# Caracterización del desmonte LE2 (Antamina): resumen de extracción

Carpeta de origen: `Data Antamina\250903 Waste Charact\` y el RFI `Data Antamina\102-24213-CW18321-RFI-115-G-0047_0.pdf`.
Scripts e imágenes en `datos_antamina\paginas\caracterizacion\` (`dump_pptx.py`, `extraer.py`, `geo_stats.py`, láminas exportadas `WSC\WSC_laminaNN.png`, `PGR\PGR_laminaNN.png` e imágenes internas `WSC_sNN_*.png`, páginas `RFI_pNN.png`).
No se revisaron `SIMULACIONES_MR2024_V3.csv` ni `Merged_Table_Assay_lito_12JUNIO2025_ult.csv`, que revisa otro agente.

Salidas:

| Archivo | Contenido | Filas |
|---|---|---|
| `caracterizacion_muestras.csv` | Una fila por registro de ensayo (xlsx) o por unidad o estadístico (pptx), en formato semiancho: una columna por parámetro | 66 465 (66 372 registros de ensayo + 93 filas de unidad) |
| `parametros_RMU.csv` | Estadísticos por RMU y parámetro: valor del Resumen del xlsx y valor recalculado desde los datos crudos (media, P50, P35, P16, P84, desviación estándar, mínimo, máximo), n, base y fuente | 434 |
| `fragmentacion.csv` | Una fila por análisis de fragmentación de voladura (P10…P90, Xmax, Rosin-Rammler y parámetros de voladura), con D10, D50, D80, D90 y Dmax en mm | 319 |

Las columnas que pidió el usuario (`litologia_informe`, `litologia` normalizada, `litologia_detalle`, `alteracion`, `correspondencia_rmu_litologias`) están en `caracterizacion_muestras.csv` y `parametros_RMU.csv`. Las columnas `LA_pct`, `durabilidad`, `absorcion_pct`, `Gs` y `granulometria` existen pero **están vacías**, porque ninguno de los cinco archivos tiene esos ensayos.

---

## 1. Qué contiene cada archivo

### 1.1 `Waste Sample Characterization Rev C.pptx` (WSC): "LE2 Waste Characterization", 29 ago 2025, 17 láminas

Objetivo: caracterizar la dureza del desmonte LE2 para dimensionar la **chancadora giratoria de desmonte W2-Hybrid**, es decir, el desmonte **Chancado** que va a la faja. No es un estudio geotécnico de botaderos. Metodología: correlaciones UCS → Bond Crusher Work Index (CBWI), aplicadas al modelo de bloques geológico (MR24, unos 310 000 bloques) y a los testigos de sondaje (unos 248 000 registros), por litología y por año del plan minero.

| Lámina | Contenido |
|---|---|
| 1 | Portada |
| 2 | Tabla "Caracterización de la Roca – Análisis de Resistencia" (Mine-to-mill 2007/2009, Fase 3): UCS, Bond CWI, crushability, Bond BWI, abrasividad Macon, Bond Ai y DWT A·b para M1, M2A y M4B (mineral) y para **Waste-C/Std, Waste-Fine y Waste-Hard** (desmonte). Incluye el gráfico CWI vs crushability |
| 3 | Modelo: CWI = 8.02·ln(UCS) − 22.10; Crushability = 286.06/√UCS − 0.012. Validación contra 4 materiales y 4 modelos empíricos |
| 4 | Estructura de las bases: testigos (holeid, xyz, ROCKCODE_NUMEQ, UCS_MPa, ABRASION_pc, Litología, CBWI) y bloques (MR24_ABRA, MR24_AXB, MR24_BD [densidad], MR24_BWI, MR24_RT [litología], MR24_UCS, LOM25_AMIN_LE2 [año]) |
| 5 | Boxplots de UCS y CBWI por litología del modelo de bloques |
| 6 | Boxplots de UCS y CBWI por año, 2025–2049 (LE1 + LE2) |
| 7 | CBWI por año y litología para LE2 (2035 a 2046–49) |
| 8 | Histogramas de UCS, abrasión y densidad en testigos y en bloques |
| 9, 15 | Mapas del plan de minado (PLP, LOM, fases 8 a 14) |
| 10 | Mapas de sondajes por litología (Intrusivo, Mármol, Mármol Diopsida, Horfel Diopsida, Hornfels, Caliza) |
| 11, 16 | Representatividad: sondajes en celdas de 200 m × 200 m (número de taladros por celda) |
| 12 | **Muestras Core Geotecnia**: criterio secuencial de selección de testigos (LE2; HQ válido, NQ no; litologías Limestone, Hornfel, Marble, Endoskarn, Intrusive, Exoskarn, Exo Diopsídico y material diopsídico; rangos de UCS 0–25, 25–50, 50–100 y >100 MPa); tabla resumen de parámetros geotécnicos por RMU (copia de PGR lámina 4, sin RMR/RQD/FF); tabla de MR24_UCS por litología (n, media, desviación estándar, mínimo, P25, P50, P75, máximo); nota "LMH Calizas Desmonte (limestone Hornfels) / XDP Exoskarn mayor desmonte" |
| 13 | Recomendación DRA: ensayos CWi/LEIT, índice de abrasión de Bond, DRX, CEC (arcillas) y microscopía óptica |
| 14 | Cierre ("¡Gracias!") |
| 17 | Toneladas acumuladas por litología en el modelo de bloques (anexo) |

### 1.2 `Parametros Geotecnicos Vs RMU LE2 03092025.pptx` (PGR): "Ensayos Geotécnicos LE2", Geotecnia e Hidrogeología PDN, 5 láminas

- Lámina 2: ubicación de los ensayos UCS, BT (brasileño), CD (corte directo) y PLI (carga puntual) en el tajo LE2. Nota: "Solo ensayos desde la configuración del plan minero 2036 hacia abajo".
- Lámina 3: ubicación de los tramos con RMR, RQD y FF (con la misma nota).
- Lámina 4: **tabla resumen de parámetros geotécnicos por RMU** (END, EXO, HRN, INT, LMH, XDP): UCS, Is(50) axial y diametral, tracción brasileña, φ y c de corte directo, RMR, RQD y FF, con promedio, "promedio ponderado" (vacío) y percentiles 50 y 35. La tabla es un metarchivo WMF; se verificó en la exportación `PGR_lamina04.png`.
- Láminas 1 y 5: portada y cierre.

### 1.3 `Resultados Parametros  Geotecnicos LE2 (03092025).xlsx`: los datos que respaldan PGR lámina 4

| Hoja | Contenido | Registros |
|---|---|---|
| Resumen | Tabla de PGR lámina 4. UCS, PLT, BT y corte se enlazan por fórmula a las hojas de datos; RMR, RQD y FF son valores pegados | 6 RMU × 4 filas |
| UCS | E, N, cota (UTM), RMU, UCS (MPa), año (1997–2024) y estadísticos por bloque de RMU | 2464 |
| UCS_rev | Copia con percentiles 16, 50 y 84 por RMU (fórmulas matriciales) | — |
| PLTA / plta_rev | Carga puntual axial Is(50), años 2008–2024; 8 registros con RMU = "N/D" | 4658 |
| PLTD / pldt_rev | Carga puntual diametral Is(50), años 1997–2024; 2 con RMU "N/D"; 17 sin valor numérico | 13 988 |
| Brazilian / Sheet7 | Tracción indirecta (MPa), 2010–2024 | 1872 |
| Corte / Sheet8 | φ (°) y c (MPa) de corte directo, 2010–2024. Solo hay 261 combinaciones únicas de (RMU, φ, c, año): muchas filas se repiten con coordenadas casi iguales | 890 |
| RMR_RQD_FF | Tramos de logueo (xyz del punto medio, UG, RQD corregido, FF/m, RMR) y percentiles 16/50/84 por UG | 42 500 |

Ninguna hoja tiene litología detallada, alteración, clase de desmonte, densidad, Gs, absorción, Los Ángeles, durabilidad ni granulometría. La unidad es siempre la RMU.

### 1.4 `Fragmentación Desmonte 2025.xlsx`: una hoja, "ANÁLISIS DE FRAGMENTACIÓN"

Tiene 319 análisis de fragmentación por fotos en el frente de pala, de enero a agosto de 2025. Todas las filas son "Clasificación = Desmonte", con objetivo de 30 cm. Cubren las fases 8 (cotas 3713–3773), 9 (3893–3983) y 10 (4388–4448), y las zonas Producción (262) y Trim (52, más mixtas). La columna "Tipo de material" vale A (147), B (30), C (115) o C1 (27); es la **clase de desmonte de Antamina**, que el archivo no define.

Columnas: fechas, pala, fase, proyecto/polígono, cota, número de fotos, Rosin-Rammler (Xc, b, n), fracción pasante de 1 y 2 cm, P10 a P90, Xmax (cm), dig rate, toneladas, kg de explosivo, FP (kg/t), FE (MJ/t), malla (altura, taco, diámetro de 9 7/8" a 12 1/4", burden, espaciamiento, sobreperforación), secuencia de salida y explosivo. Hay además un bloque "MODELO ROSIN-RAMMLER" con fracciones teóricas pasantes de ½", 1", 2", 4" y 6" y P10–P90 y Xmax del modelo. Son valores pegados, sin fórmulas.

No hay litología en el archivo, por lo que la fragmentación no se puede separar por litología con este archivo. Habría que cruzar proyecto/polígono y cota con el modelo de bloques.

### 1.5 `102-24213-CW18321-RFI-115-G-0047_0.pdf`: RFI, 3 páginas (paginado "de 4"), 25/03/2026

- Proyecto 24213 LE2, contrato CW18321 (MSA LE2), etapa de prefactibilidad (102), agrupador **24213EXB-115 Botaderos Este E0-E1-E2-E9-E10**.
- Antecedente: en enero de 2026 el IRB recomendó (i) **evaluar el efecto de la lixiviación ácida en la degradación de la resistencia del desmonte** y (ii) diseñar drenes con redundancia ante la obstrucción por precipitados.
- Stantec pidió: (1) resultados de ensayos geotécnicos (índice, resistencia y rigidez) en desmonte degradado de pilas de lixiviación a escala de campo, con litología, clase geoquímica y años de degradación; (2) el instructivo de construcción de drenes en botaderos; (3) muestras de desmonte degradado de barrel tests.
- Respuesta de Antamina (p. 3): Ítem 1, se adjunta "Resultados de Laboratorio.zip" en el SPF, con ensayos índice y especiales. Ítem 2, no hay instructivo. Ítem 3, no hay muestras degradadas.
- Relevancia: es la única fuente de este grupo que trata la **degradación del desmonte en el tiempo**, que reduce la resistencia de las partículas y aumenta la rotura bajo 700 m de altura. El zip no viene en el PDF. **Hipótesis no verificada:** podría corresponder a la carpeta `Data Antamina\ensayos\` (Hornfels H-1…H-12, Intrusivo I-1…I-12, Mármol M-1…M-13, Pila 01 Mármol + Hornfels, Pila 02 Intrusivo; SUCS, humedad, Proctor, corte directo de gran escala y triaxial CU de 6"). No abrí esos archivos.

---

## 2. Relación entre RMU, litología y clase de desmonte

| RMU | litologia (normalizada) | litologia_detalle | Base de la correspondencia |
|---|---|---|---|
| END | Skarn | Endoskarn | Sigla y lista de litologías de WSC lámina 12 (no definida en el xlsx) |
| EXO | Skarn | Exoskarn | Ídem |
| XDP | Skarn | Exoskarn "mayor desmonte"; la sigla sugiere exoskarn diopsídico | WSC lámina 12: "XDP Exoskarn mayor desmonte" |
| HRN | Hornfels | Hornfels | Sigla |
| INT | Intrusivo | Intrusivo sin subtipo (no separa monzonita cuarcífera ni pórfidos) | Sigla |
| LMH | Caliza | "Calizas Desmonte (limestone Hornfels)"; probablemente incluye mármol | WSC lámina 12. **Ambiguo**: ninguna RMU es de mármol, aunque el mármol es la mayor litología en toneladas |

El modelo de bloques (MR24_RT) usa otras litologías: Intrusivo, Intrus-Estruct-Tab, Brechas-Intrus, Mármol, Mármol Diopsida, Horfels, Horfel Diopsida, Caliza y Margas-Limonitas. No hay una tabla de equivalencia RMU ↔ MR24_RT en estos archivos.

**Clase de desmonte (ROM, Chancado, Enrocado).** Ningún archivo asigna muestras ni RMU a una de estas clases.

- WSC está orientado al desmonte **Chancado**: chancadora W2-Hybrid y faja.
- Las 319 fragmentaciones son de desmonte **ROM** recién volado, en el frente de pala.
- Los ensayos de PGR y del xlsx son de **roca in situ** (testigos), válidos para cualquier clase.
- No hay datos de **Enrocado**.

La clasificación A/B/C/C1 del archivo de fragmentación es otra variable: la clase de material de Antamina, probablemente geoquímica. No equivale a ROM, Chancado ni Enrocado.

---

## 3. Fichas por litología

Valores de núcleos por RMU, recalculados desde los datos crudos. Coinciden con el Resumen salvo en **XDP UCS P35**: el Resumen dice 2021 MPa porque la fórmula toma la columna del año; el valor correcto es 70.8 MPa.
Formato: mediana (P35; media; n). UCS de bloques = MR24_UCS (WSC lámina 12). Las toneladas se leyeron del gráfico de WSC lámina 17 y son aproximadas.

### Intrusivo (RMU INT; bloques Intrusivo, Intrus-Estruct-Tab, Brechas-Intrus)
- UCS en núcleo: 50.6 MPa (P35 39.5; media 57.7; n = 379; P16–P84 25.8–89.2).
- Is50 axial: 3.48 (P35 2.15; n = 486). Is50 diametral: 4.87 (P35 3.67; n = 2077). Tracción BT: 7.25 MPa (P35 5.93; n = 206).
- Corte directo: φ = 33.4° (P35 30.3; media 31.1; n = 66) y c = 0.10 MPa (media 0.49).
- RMR 71 (media 67.9; n = 6720); RQD 100 (media 91.7); FF 0.33/m (media 1.29).
- UCS de bloques (P50): Intrusivo 63.2 MPa (n = 46 813), Intrus-Estruct-Tab 103.3 MPa, Brechas-Intrus 56.7 MPa. CBWI ≈ 11.1 / 15.1 / 10.3 kWh/t (lectura del gráfico).
- Toneladas (aprox.): Intrusivo 0.69 Gt, Intrus-Estruct-Tab 0.05 Gt, Brechas unos 0.003 Gt.
- Subtipos (monzonita, pórfido) y alteración: no disponibles.

### Hornfels (RMU HRN; bloques Horfels y Horfel Diopsida)
- UCS en núcleo: 75.2 MPa (P35 58.2; media 96.8; n = 275; P16–P84 39.2–163.9).
- Is50 axial: 4.87 (n = 530). Is50 diametral: 4.96 (n = 1118). BT: 9.71 MPa (n = 304), el más alto.
- Corte: φ = 28.2° (P35 27.4; media 29.1; n = 113) y c = 0 (media 0.42 MPa).
- RMR 72 (media 69.2; n = 4197); RQD 100; FF 0.67/m (media 1.19).
- UCS de bloques: Horfels 104.9 MPa (n = 48 510) y Horfel Diopsida 115.0 MPa (n = 9983). CBWI ≈ 15.2 y 16.0.
- Toneladas: Horfels unos 0.79 Gt y Horfel Diopsida unos 0.17 Gt.

### Mármol (sin RMU propia; bloques Marmol y Marmol Diopsida)
- No hay ensayos de núcleo identificados como mármol en el xlsx. Puede estar incluido en LMH (ver Caliza), pero no está confirmado.
- UCS de bloques: Mármol 74.1 MPa (media 74.0; P25–P75 65.8–80.9; n = 110 698 bloques) y Mármol Diopsida 94.7 MPa (n = 8020). CBWI ≈ 12.4 y 14.4.
- Toneladas: Mármol unos **1.80 Gt (la mayor litología del desmonte)** y Mármol Diopsida unos 0.13 Gt.
- No separa mármol negro y blanco.

### Skarn (RMU END, EXO, XDP)
- **Endoskarn (END)**: UCS 28.1 MPa (P35 22.0; media 39.3; n = 312) es **el más débil**. Is50 axial 1.97; diametral 2.65; BT 3.39. φ corte 31.4° (P35 27.9); c 0.10. RMR 65 (media 60.7), RQD 98 (media 78.0) y FF medio 2.55/m: el más fracturado.
- **Exoskarn (EXO)**: UCS 66.7 MPa (P35 49.6; media 72.7; n = 309). Is50 axial 4.71; diametral 5.92; BT 7.15. φ 31.6° (P35 29.7); c 0.11. RMR 66.5 (media 62.5); RQD 100 (media 81.6); FF medio 1.79/m.
- **XDP (exoskarn "mayor desmonte")**: UCS 98.0 MPa (P35 70.8 recalculado; media 98.7; n = 78). Is50 axial 6.85; diametral 7.18; BT 8.52. φ 32.6° (P35 27.7); c 0.02. RMR 68; RQD 100; FF 0.62/m.
- Los skarns no aparecen como litología en el modelo de bloques MR24_RT de WSC.

### Caliza (RMU LMH; bloques Caliza)
- **LMH**: UCS 56.3 MPa (P35 44.3; media 68.0; n = 1111, la RMU con más datos). Is50 axial 3.49 (n = 2469); diametral 3.55 (n = 7409); BT 6.39 (n = 834). φ corte 28.7° (P35 28.0; media 31.0; n = 507); c 0.10. RMR 70 (n = 19 868); RQD 100; FF 0.56/m.
- UCS de bloques Caliza: 82.5 MPa (n = 24 434); CBWI ≈ 13.1. Toneladas: unos 0.40 Gt.

### Otra (bloques Margas-Limonitas)
- UCS de bloques: 69.2 MPa (n = 58 104); CBWI ≈ 12.0. Toneladas: unos 0.95 Gt (la segunda mayor).
- No hay ensayos de núcleo asociados.

### Desmonte genérico (WSC lámina 2, programa Mine-to-mill 2007/2009, sin litología)
| Material | UCS (MPa) | Bond CWI (kWh/t) | Crushability (%) | Macon (g/t) | Bond Ai | DWT A·b |
|---|---|---|---|---|---|---|
| Waste-C/Std | 54 | 12.6 | 36.50 | 39.4 | 0.0261 | 43.9 |
| Waste-Fine | 83 | 17.1 | 28.72 | 50.0 | 0.0202 | 35.6 |
| Waste-Hard | 155 | 16.0 | 25.02 | 778.0 | 0.4810 | 38.8 |

### Propiedades comunes (WSC lámina 8, lectura de histogramas, todas las litologías)
- Densidad (MR24_BD y testigos; unidad no indicada, presumiblemente t/m³): moda 2.70–2.72, con un grupo secundario de 2.40–2.55 y uno menor de unos 2.88. Puede tomarse como densidad de partícula del orden de 2.7, pero **no hay Gs ni absorción medidos**.
- Abrasión: moda de unos 22 en testigos y bimodal (≈26 y ≈41) en bloques.
- UCS en testigos: moda de 50–65 MPa y cola hasta 300 MPa.

### Fragmentación ROM (todas las litologías; no hay separación por litología)
| Estadístico (319 voladuras) | P10 | P50 | P80 | P90 | Xmax | n (RR) | % < 1 cm |
|---|---|---|---|---|---|---|---|
| Mediana | 8 mm | 98 mm | 234 mm | 326 mm | 853 mm | 0.99 | 11 % |
| Percentiles 10–90 | 3–19 mm | 53–163 mm | 136–361 mm | 191–485 mm | 541–1340 mm | 0.73–1.23 | 6–19 % |

- Por clase A/B/C/C1, la mediana de P80 es 234, 270, 245 y 181 mm. Por fase: F8 113 mm, F9 262 mm y F10 192 mm. El Trim es más grueso que la producción (P80 de unos 288 vs 225 mm).
- El Cu aproximado con medianas es P60/P10 ≈ 13.2/0.8 ≈ 16, con granulometría de banda ancha. Ojo: el análisis por fotos subestima los finos.

---

## 4. Datos útiles para estimar φ′1 (con Δφ por confinamiento) y la rotura

**Calidad y resistencia de partícula** (sirven para elegir la curva de Leps, escoger entre roca "débil", "media" o "fuerte" y estimar la rotura):
- UCS de núcleo por RMU, con distribución completa (2464 ensayos), más Is50 (18 600) y BT (1870). Una correlación local UCS–Is50 sale de las propias medianas: UCS/Is50 diametral ≈ 10.6 (END), 11.3 (EXO), 15.2 (HRN), 10.4 (INT), 15.9 (LMH) y 13.6 (XDP). Son cálculos míos con medianas, no del informe.
- Los P35 (que Antamina usa como valor característico) dan una UCS de 22 a 71 MPa. El END (P35 ≈ 22 MPa) y el INT (P35 ≈ 40 MPa) serían los materiales más rompibles.
- La UCS de bloques MR24 es mayor que la de núcleos en la misma litología (por ejemplo, hornfels 105 vs 75 MPa e intrusivo 63 vs 51 MPa). Antes de usarla hay que definir cuál se adopta.
- Las toneladas por litología permiten ponderar la mezcla del botadero: mármol unos 36 % (más 3 % de mármol diopsídico), margas unos 19 %, hornfels unos 16 % (más 3 % de hornfels diopsídico), intrusivo unos 15 % (incluye el tabular) y caliza unos 8 % del total leído (unos 5.0 Gt).

**Tamaño de partícula** (escalamiento y efecto de tamaño en la rotura): la fragmentación ROM da D50 ≈ 10 cm, D80 ≈ 23 cm y Dmax ≈ 85 cm, con la curva Rosin-Rammler completa por voladura. No hay granulometría de desmonte Chancado ni de Enrocado.

**Relación de vacíos o densidad**: **no hay datos** de densidad seca colocada, de relación de vacíos del botadero, de Gs ni de absorción. Solo hay densidad de roca (moda ≈ 2.71) para usar como densidad de sólidos aproximada.

**Corte directo (φ ≈ 28–34°, c ≈ 0–0.1 MPa)**: no es la resistencia del desmonte granular. Probablemente se ensayaron discontinuidades en núcleo; el archivo no lo indica. Sirve a lo sumo como cota de fricción básica o de la roca alterada, y **no debe usarse como φ′ del desmonte**.

**Durabilidad y degradación**: no hay Los Ángeles, slake ni ensayos de sanidad. El RFI muestra que el IRB pide evaluar la pérdida de resistencia por lixiviación ácida. Los datos de Antamina sobre eso estarían en el zip "Resultados de Laboratorio", que no está en este grupo de archivos.

---

## 5. Dudas y observaciones de calidad

1. **Error en el Resumen del xlsx (y en PGR lámina 4 y WSC lámina 12)**: el P35 de UCS de XDP aparece como 2021 MPa. La fórmula `PERCENTILE.INC(F2394:F2471,0.35)` toma la columna del año. El valor correcto es **70.8 MPa**.
2. En PLTA, la media de HRN usa C950:C1478 y los percentiles usan C950:C1479. La diferencia es mínima.
3. La fila "Promedio Ponderado" está vacía en todo el Resumen (solo "--"), aunque hay una fórmula de SUMPRODUCT sin sentido en UCS!H2.
4. Hay 10 registros de PLT con RMU = "N/D" (8 en PLTA y 2 en PLTD). Sin valor numérico de Is50 quedaron 1 registro de PLTA ("N/D") y 17 de PLTD (2 "N/D" y 15 celdas vacías con RMU asignada). Quedaron vacíos en el CSV.
5. En la hoja Corte, de 890 filas solo 261 son combinaciones únicas. Parece que el valor de cada ensayo se repite en tramos contiguos, lo que sesga media y percentiles hacia los ensayos repetidos. El tipo de ensayo (discontinuidad o roca, pico o residual) no se indica.
6. Las siglas RMU no se definen en el xlsx. Las expansiones (END = endoskarn, EXO = exoskarn, XDP ≈ exoskarn "mayor desmonte" o diopsídico, LMH = calizas con hornfels) vienen de la nota de WSC lámina 12 y de la lista de litologías de la misma lámina. **No hay RMU de mármol**, pese a que es la litología dominante del desmonte. No está claro si queda dentro de LMH.
7. En fragmentación, una fila (Excel 241) tiene b = 99.5 y n = 34.8, y otra (Excel 86) tiene P30 = 68.1 cm > P40 = 11.1 cm. Ambas son errores evidentes y se conservaron sin corregir. Las columnas del "MODELO ROSIN-RAMMLER" (fracción pasante de ½" ≈ 0.65 con P10 medido ≈ 0.8 cm) **no son coherentes** con la curva medida. No las usaría.
8. Las lecturas gráficas (medianas de los boxplots de la lámina 5, toneladas de la lámina 17 y modas de la lámina 8) son aproximadas y van marcadas así en `estadistico`.
9. La nota de PGR dice "solo ensayos desde la configuración del plan minero 2036 hacia abajo": la estadística representa la roca bajo el pit 2036, no todo el desmonte LE2.
10. La clase A/B/C/C1 del archivo de fragmentación no se define. Que sea la clasificación geoquímica de Antamina es una suposición mía.

# Resumen: WSP Golder (2022). Pruebas de enrocado 3B a gran escala, hornfels y alta presión, para el modelamiento de deformación

- **Fuente:** `2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf` (396 p.)
- **Documento:** Memorando técnico Golder/WSP 20377053-001-TM-Rev1-401001, 1 de septiembre de 2022 (Doc. Antamina 105-18028-MTE00420-MEM-430-G-0007 Rev. 1, «Tailing Dam Raise Phase 7»). Autores: M. V. Sanín y H. Puebla.
- **Archivos generados:** `WSP_2022_hornfels3B.csv` (25 filas: 19 probetas triaxiales y 6 edómetros) y `WSP_2022_edometro.csv` (253 puntos σv–εv–e de 6 edómetros).
- **Scripts e imágenes de verificación:** `paginas/WSP2022/` (`build.py`, `parse_tx.py`, `parse_edo.py`, `grad.py`, `cal35.py`, PNG de las páginas).

## 1. Objetivo y materiales

El memorando resume el programa de laboratorio sobre el **enrocado 3B** de la presa de relaves de Antamina. El enrocado se usa en el recrecimiento del espaldón y de la cresta. El objetivo es calibrar los modelos numéricos de deformación y desempeño sísmico de la presa.

Hay dos litologías:

| Litología normalizada | Nombre en el informe | Origen | Clase (`tipo_material`) |
|---|---|---|---|
| Hornfels | «H6 Hornfel Gris», «HG (Hornfels Gris)», «Hornfels (HR)» | Tajo, Fase 8, Norte, Pala 11, polígono 8-NP-4193-46-03, cota 4193 m s. n. m. (macrogranulometría M-001, p47); material llevado al Acopio G | Enrocado (3B) |
| Mármol | «Mármol Negro (MN/MR)»; muestra IDIEM «MARMOL (REG 41061)» | Acopio Punto G (p8). Hay dos campañas: 2011 (Golder 2012) y 2021–2022 | Enrocado (3B) |

Cantidades enviadas: 39 t de hornfels y 7 t de mármol a IDIEM (tamaño menor que 7"), y 200 kg de cada litología a Golder Burnaby y a USC (tamaño menor que 1").

Las muestras se describen como perturbadas y remoldeadas. El informe no da mineralogía. En los núcleos de UCS de IDIEM se describe: «Fracturas/vetillas: calcita; Alteraciones: no presenta».

## 2. Programa de ensayos (Tabla 3, p10; Tabla 4, p31)

| Tipo | Hornfels | Mármol negro |
|---|---|---|
| CID monótono, Ø1.0 × 1.8 m (IDIEM) | 3 (σ′c = 980, 1,960 y 2,450 kPa) | 2, de 2011 (490 y 1,961 kPa) |
| CID carga-descarga, Ø1.0 m (IDIEM) | 3 (980, 1,960 y 2,450 kPa) | 3, de 2011 (490, 981 y 1,961 kPa) |
| CID carga-descarga, Ø0.15 m (Golder) | 1 (980 kPa) | 1 (981 kPa) |
| Cíclico drenado más carga monótona post-cíclica, Ø0.10 y 0.15 m (USC) | 3 (350 kPa) | 3 (350 kPa) |
| Edómetro Ø1.0 m (IDIEM) | 1 (hasta 6,865 kPa) | 2 (2011 hasta 5,884 kPa; 2021 hasta 6,865 kPa) |
| Edómetro Ø0.24 m (Golder) | 2 (ρd 2.1 y 1.8 t/m³, hasta 4,800 kPa) | 2 (2.3 y 1.8 t/m³; solo hay hoja de la de 1.8) |

Los ensayos de mármol de 2011 (IDIEM 708.397-A) son los mismos que publicó **Golder (2012)**. En el CSV se marcan como «DUPLICADO» en `notas`, para no contarlos dos veces.

**Rango de σ′3 en los triaxiales:** 350 a 2,452 kPa. La alta presión corresponde al hornfels de Ø1.0 m: 981, 1,961 y 2,452 kPa.
**Rango de σv en los edómetros:** hasta 6,865 kPa (70 kg/cm²) en Ø1.0 m y 4,799 kPa en Ø0.24 m.

## 3. Resultados triaxiales de hornfels a gran escala (IDIEM, Ø1.0 m, hojas p106–250)

IDIEM entrega las tablas en kg/cm², con q = (σ1−σ3)/2. Los valores se convirtieron con el factor 98.0665. Se tomó el máximo de la tabla; todos los valores se verificaron en la imagen de la página.

| Tabla 3 | Ensayo | σ′3 (kPa) | q máx (kPa) | εa (%) | εv (%) | φsec calc. (°) | Bg (%) |
|---|---|---|---|---|---|---|---|
| 1 | Monótono | 981 | 3,897 | 13.13 | −5.05 | 41.7 | 20 |
| 2 | Monótono | 1,961 | 9,059 | 19.04 (fin del ensayo) | −7.14 | 44.2 | 29 |
| 3 | Monótono | 2,452 | 11,931 | 17.83 | −8.64 | 45.1 | 37 |
| 4 | Carga-descarga | 981 | 3,821 | 19.15 (fin) | −6.35 | 41.4 | 24 |
| 5 | Carga-descarga | 1,961 | 9,703 | 18.80 | −7.03 | 45.4 | 36 |
| 6 | Carga-descarga | 2,452 | 12,929 | 18.98 | −8.34 | 46.5 | 39 |
| 7 | Carga-descarga, Ø0.15 m (Golder) | 977 | 4,100 (hoja) | 11.44 | −5.31 | 42.6 | 15 |

Convención de signos: εv negativa es compresión. Todas las probetas son contractivas.

- **Envolvente del informe:** el informe no ajusta c–φ, Leps ni ley potencial. Solo da φ′ máx por probeta en un gráfico (Fig. 16, p20): φ crece de 42° a 1 MPa hasta 45–46° a 2.5 MPa. En la Fig. 17 los compara con Leps (1970) y quedan en el rango superior o por encima, con tendencia creciente con σ3, contraria a Leps. El φsec del CSV lo calculé yo, porque no viene tabulado.
- **Módulo secante** Es a σ1/σ3 = 2 (Fig. 18, solo gráfico): de 70 a 300 MPa entre 1 y 2.5 MPa (p41). Para el mármol: de 40 a 100 MPa.
- **t/σ′c último normalizado:** de 2.0 a 2.5 para el hornfels y de 1.5 a 2 para el mármol.
- **Consolidación:** ΔV drenado de 2.1 % a 6.6 % de V0 (anotado en `notas`).
- **Mármol de 2011** (recálculo propio): φsec de 40.2° a 490 kPa y de 36.7° a 1,961 kPa (el informe da 40° y 36°).

## 4. Ensayos índice por litología

| Propiedad | Hornfels | Mármol negro |
|---|---|---|
| UCS, Tabla 1/2 (Golder 2021a) | 65 y 64 MPa (M-1 y M-2, p7) | 2021: 44 y 42 MPa. 2011: 53, 108, 106, 129, 54, 61, 136 y 132 MPa (p8) |
| UCS, IDIEM 1.555.677-D (2022, p72–83) | 26.3, 40.8 y 24.5 MPa (D50). Falla mixta B2 por vetillas de calcita. ρd de la roca 2.66, 2.71 y 2.69 g/cm³ | REG 41061: 96.6, 66.9 y 103.5 MPa. Falla por matriz (tipo A). ρd de la roca 2.74–2.75 g/cm³ |
| Los Ángeles | 17 % (promedio) | 43 % (2011); 45–50 % (2021) (p36) |
| Gs | 2.75 «calculated» (Golder 6"); 2.71 «estimated» (USC); 2.60 «estimado» (IDIEM, edómetro). Inconsistente con ρd de la roca ≥ 2.66 | 2.70 (Golder 6"; Golder edómetro «assumed»; IDIEM 2011 «peso específico integral»); 2.71 (USC); 2.60 (IDIEM 2021) |
| ρmáx/ρmín índice, ASTM D4253/4254, material de 1" (p85–86) | 2232 (seco) / 2308 (húmedo) / 1852 kg/m³ | 2297 / 2398 / 1905 kg/m³ |
| Especificación 3B | UCS ≥ 40 MPa; Los Ángeles < 60 % | Igual |

Absorción, durabilidad y carga puntual no se informan.

**Duda:** la UCS de IDIEM 2022 para el hornfels (24–41 MPa) es menor que la mínima especificada de 40 MPa y que la de la Tabla 1 (64–65 MPa). El texto principal no la menciona. Para el mármol 2021 pasa lo contrario: IDIEM da 67–104 MPa y el texto da 42–44 MPa. El texto atribuye la mayor compresibilidad y rotura del mármol 2021 a su menor UCS; los datos de IDIEM contradicen ese argumento.

## 5. Granulometrías

- **Hornfels en terreno** (M-001, p47): Dmax ≈ 914 mm (36"), 2.49 % pasa el #200, GW-GM, Cu 33, Cc 2.5 (calculados con el material menor que 3").
- **Hornfels inicial Ø1.0 m** (IDIEM, p62): Dmax 177.8 mm. Con interpolación log-lineal propia: D10 2.61 mm, D30 13.3, D50 28.0 y D60 35.0 mm; Cu 13.4, Cc 1.93; grava 87.3 %, arena 10.1 % y finos 2.6 %.
- **Hornfels y mármol Ø0.15 y 0.10 m:** no hay tabla. Leí la curva de los marcadores vectoriales de las Fig. 3 y 4 (p6–7), y es idéntica para ambas litologías: Dmax 25.4 mm, D10 ≈ 0.19, D30 ≈ 1.73, D50 ≈ 4.55 y D60 ≈ 6.4 mm, con ≈ 8.9 % pasando 0.15 mm. Es aproximadamente paralela a la curva de 1.0 m, con un factor cercano a 7. El informe no declara el método de escalamiento.
- **Mármol 2011 inicial** (p66): Dmax 178 mm, D10 1.39, D30 17.6, D50 39.5 y D60 51.9 mm; Cu 37.4; finos 4.9 %.
- **Mármol 2021 inicial** (p61): 10.9 % pasa el #200; después del edómetro, 25.7 %.
- **Granulometrías posteriores** (p62–63, 66–67): finos del hornfels después del triaxial de 5.6 % a 13.5 %, y 9.5 % después del edómetro.

**Rotura (Bg de Marsal, Tabla 7, p41).**
- Hornfels: triaxiales Ø1.0 m de 20 a 39 %, que aumentan con σ3; 15 % en Ø0.15 m; 8 % en los cíclicos (valor único); edómetros 23 % (1.0 m), 12 % y 8 % (0.24 m).
- Mármol: 13–28 % (2011), 30 % (6"), 6 % (cíclicos); edómetros 14 % (2011), 45 % (2021) y 21 %.

Recalculé Bg desde las granulometrías y reproduce exactamente la Tabla 7. Eso además resolvió qué columna «20 kgf/cm²» de la p63 corresponde al ensayo monótono: la primera, con Bg 29.

El informe no da Br de Hardin.

## 6. Edómetros (curvas completas en `WSP_2022_edometro.csv`)

| Ensayo | ρd (t/m³) | e0 | σv máx (kPa) | εv a σv máx (%) | M tangente 500–4500 kPa* | M secante a σmáx* | Cc* | Origen |
|---|---|---|---|---|---|---|---|---|
| Hornfels Ø1.0 m (IDIEM) | 2.10 | 0.238 (Gs 2.60) | 6,865 | 5.01 | ≈136 MPa | ≈126 MPa a 5,884 kPa | ≈0.053 (981–5,884 kPa) | Tabla, p300–302 |
| Hornfels Ø0.24 m | 2.1 | – | 4,799 | ≈6.1 | ≈92 MPa | ≈82 MPa | – | Leído de gráfico (Fig. 33c) |
| Hornfels Ø0.24 m | 1.8 | – | 4,799 | ≈17.5 | ≈59 MPa | ≈28 MPa | – | Leído de gráfico (Fig. 33d) |
| Mármol 2021 Ø1.0 m (IDIEM) | 2.10 | 0.238 | 6,865 | 6.39 | ≈127 MPa | ≈96 MPa | ≈0.045 | Tabla, p324 |
| Mármol 2011 Ø1.0 m (IDIEM; duplicado de Golder 2012) | 2.10 | 0.284 | 5,884 | 9.03 | ≈63 MPa | ≈65 MPa | ≈0.107 | Tabla, p295 |
| Mármol Ø0.24 m (Golder Test 1) | 1.856 | 0.455 | 4,799 | 15.63 | ≈61 MPa | ≈31 MPa | ≈0.112 (1000–4799) | Tabla, p359 |

\* Cálculos propios. El informe solo define M = σ′v/εv y lo muestra en gráficos (Fig. 33–34). No da valores ni Cc.

Los ensayos de Ø1.0 m incluyen un ciclo de descarga y recarga a 60 kg/cm². La altura de las probetas de Ø1.0 m de 2021–2022 es 0.70 m, aunque la p4 dice 0.9 m. El Ø0.24 m de Golder tiene 0.20 m de altura.

**Permeabilidad (carga constante en el edómetro de 1.0 m, Tablas 5–6, p35):**
- Hornfels: 3.5×10⁻² cm/s a 588 kPa, hasta 3.5×10⁻³ cm/s a 6,865 kPa.
- Mármol 2021: 1.2×10⁻² a 2.7×10⁻³ cm/s.
- Mármol 2011: 1.4×10⁻¹ a 8.2×10⁻² cm/s.

## 7. Ensayos cíclicos (USC) y no drenados

Las seis probetas cíclicas son drenadas, a σ′c = 350 kPa, y terminan con una carga monótona drenada. Su q máximo post-cíclico va de 1,210 a 1,576 kPa (φsec ≈ 40.6°–46.2°) y quedó en el CSV. El informe no extrae deformaciones por ciclo como tabla, solo en gráficos (Fig. 27–30). No hay ensayos no drenados.

## 8. Dudas e inconsistencias

1. **Probeta 7 de hornfels (Golder 6").** La hoja da q_f = 4,100 kPa a 11.44 %, pero la curva llega a ≈4,600 kPa a ≈17.5 %. Con ese valor φ ≈ 44.6°, que coincide con el 45° del texto. En el CSV se dejó el valor de la hoja y se anotó la diferencia.
2. **Mármol 6".** Con la hoja, φ = 41.3°; el texto dice 45°. Además, la hoja trae w post 27.4 % y saturación 319 %, que son erratas.
3. **Convención de εv.** La leyenda de las hojas Golder dice «−ve = dilation», pero las curvas son de compresión negativa.
4. **Ensayos cíclicos.** La Tabla 3 no coincide con los anexos USC en diámetros ni CSR. Por eso se usaron los ID de laboratorio (HR-LCTX2, HR-CTX1, HR-CTX4, MN-CTX3, MN-LCTX1 y MN-LCTX2). El Bg de los cíclicos es un solo valor por material.
5. **Hornfels edómetro Ø0.24 m n.° 2.** La Tabla 7 dice 2.3 t/m³; la Tabla 4 y el texto dicen 2.1 t/m³. Además, sus curvas solo están en gráficos: los valores del CSV se leyeron de los marcadores vectoriales, con un error aproximado de ±30 kPa y ±0.05 %.
6. **Edómetros de mármol 2011.** La Tabla 7 da un σmáx de 6,800 kPa, pero la hoja llega a 5,884 kPa.
7. **Numeración de las probetas 3 y 4 de mármol.** El texto (p31) la invierte respecto de la Tabla 4 y cita 17 %; la hoja da 15.63 %. El edómetro de mármol de 2.3 t/m³ no tiene hoja.
8. **Gs no informado para los triaxiales IDIEM.** El e0 se calculó con Gs = 2.75 (Golder), por lo que es 0.310 para 2.10 t/m³ y 0.335 para 2.06 t/m³. Con el Gs = 2.60 de IDIEM sería 0.238 y 0.262.
9. **Densidades de los triaxiales carga-descarga IDIEM (1.555.677-E).** Son 2.06 g/cm³ con w = 5 %, menores que los 2.10 g/cm³ del objetivo y de los monótonos.
10. **Fechas erróneas.** Las hojas B.2 dicen «17-12-2022» y el edómetro B.1 dice «05-11-2022».
11. **UCS contradictoria.** Ver la sección 4.
12. **Escalamiento.** No se declara el método: ni para pasar de terreno (Dmax 914 mm) a laboratorio (178 mm) ni de 178 a 25.4 mm.

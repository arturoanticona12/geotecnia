# Verificación independiente: WSP 2022 (hornfels y mármol 3B) y Golder 2012 (mármol negro)

**Fecha:** 2026-10-06. **Alcance:** propiedades índice y condiciones de campo y laboratorio, según `VERIFICACION.md`.
**Fuentes:** `2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf` (396 p.) y `2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf` (79 p.). Las páginas citadas son las del PDF; «W p» indica WSP 2022 y «G p», Golder 2012.
**Evidencia:** imágenes PNG y scripts en `paginas/verificacion/WSP2022_Golder2012/`:
- `render.py`: renderiza las páginas.
- `parse_idiem.py` y `compara_duplicados.py`: leen las tablas IDIEM por coordenadas y comparan los duplicados.
- `verif_edometro.py`: compara las curvas edométricas.
- `bg_golder.py`, `bg_hornfels.py` y `bg_mn2021.py`: recalculan Bg.
- `build_verificado.py` y `build_condiciones.py`: generan los entregables.
- `discrepancias_filas.csv`: lista de discrepancias fila por fila.

Cada número de este documento se comprobó en la imagen de la página. Los valores que se recalcularon aquí se señalan como «recalculado».

## 1. Resumen

- **Discrepancias encontradas:** 27 temas distintos. Al aplicarlos fila por fila son 82 cambios de celda (anexo A).
  - **Graves (6):** cambian números que se usan en análisis. Ver la sección 2.
  - **Moderadas (9):** contradicciones de origen, de UCS o de Los Ángeles, y ensayos truncados.
  - **Menores (12):** rótulos, redondeos, erratas y notas mal asignadas.
- **Duplicados de mármol 2011:** los 5 triaxiales y el edómetro IDIEM 708.397-A son exactamente los mismos en ambos informes. La comparación automática de las tablas da 16, 346, 402, 54 y 504 filas q–εa–εv, todas idénticas. El edómetro tiene 45 filas numéricas, también idénticas. Las granulometrías son iguales celda a celda (G p27–28 = W p66–67; las dos copias dejan vacía la celda de 7" de la probeta 4).
  - **Registro primario:** Golder (2012), Doc. 446, con su anexo IDIEM 708.397-A (emitido el 05-09-2011). WSP (2022) reproduce esas hojas en su Anexo B (W p252–p295).
- **Bases de cálculo:** el criterio de falla (máximo t = (σ1−σ3)/2) y los esfuerzos σ′3, σ′1 y q de los 30 ensayos triaxiales y edómetros se confirmaron en las tablas. La conversión es 1 kg/cm² = 98.0665 kPa.

## 2. Discrepancias graves

| # | Archivo / filas | Columna | Valor anterior | Valor correcto | Página | Razón |
|---|---|---|---|---|---|---|
| G1 | Golder_2012_marmol.csv, las 6 filas | Bg_pct | 26.8; 28.6; 40.8; 50.2; 55.4; 28.8 | **13.4; 14.3; 20.4; 25.1; 27.7; 14.4** (recalculado) | G p17, p27–28; W p41 | La Tabla 5 de Golder 2012 da Σ\|ΔW\|, que es 2×Bg. El propio texto define Bg como «sum of the positive differences». Con las granulometrías IDIEM el Bg de Marsal es exactamente la mitad. WSP 2022 (Tabla 7) ya lo corrigió: 13, 14, 20, 25, 28 y 14. Golder 2012 destaca «Bg > 50 not common»: esa conclusión se apoya en el error. |
| G2 | WSP_2022_hornfels3B.csv, fila MN-edo-1.0m-2021 | Bg_pct | 45 | **37.8** (recalculado) | W p41, p61, p66 | Con la granulometría inicial y la post-edómetro del mismo ensayo (IDIEM p61) el Bg es 37.8. El 45 de la Tabla 7 se reproduce (45.6) solo si la curva post-2021 se compara con la inicial de 2011 (p66). Es un error probable de WSP, y debilita su argumento de que el mármol 2021 «rompe más». |
| G3 | WSP, mármol 2011 (5 triaxiales y edómetro) | saturado | «no indicado en la hoja» | **sí**: CO2 24 h + agua desaireada, B > 0.95, contrapresión 2 kg/cm² | G p7; W p252 | El registro primario describe la saturación. La hoja reproducida muestra contrapresión de 2.00 kg/cm². |
| G4 | Ensayos USC HR-CTX1, HR-CTX4 y MN-CTX3 | criterio_falla | «máximo desviador en la carga post-cíclica» | **Ensayo detenido antes de la falla:** q es una cota inferior | W p361, p367, p379 | La hoja da «Max. Axial Strain» de 1.68 %, 7.37 % y 4.89 %, y el desviador a esa deformación es igual al máximo. Los valores 1280, 1210.5 y 1245.3 kPa no son resistencia en falla y no deben usarse como puntos de envolvente. |
| G5 | Gs 2.60 de los edómetros IDIEM 2021–22 (hornfels y mármol) | Gs y e0 | 2.60 → e0 0.238 | Se mantiene (es lo que informa IDIEM), pero **es físicamente incompatible** | W p300, p324, p72–82 | IDIEM lo declara «estimado». Las densidades secas de los núcleos del mismo lote son 2.66–2.71 g/cm³ en hornfels y 2.74–2.75 g/cm³ en mármol (REG 41061), y el Gs no puede ser menor que la densidad seca de la roca. Con Gs 2.75, e0 = 0.310. |
| G6 | Hornfels Ø1.0 m (6 probetas) | UCS_MPa | 64.5 (sin matiz) | 64.5 según la Tabla 1, pero **el lote ensayado en IDIEM dio 24.5–40.8 MPa** | W p7, p49, p51, p72–76 | Ver la sección 4. El CSV atribuía a las probetas una UCS medida sobre otras muestras. Se agregó en notas. |

## 3. Discrepancias moderadas

| # | Archivo / alcance | Columna | Valor anterior | Valor correcto | Página | Razón |
|---|---|---|---|---|---|---|
| M1 | WSP, filas de mármol 2011 | Cu / Cc | 37.4 / 4.3 | 34.4 / 4.1 (informe primario) | G p2 | Para que coincida con el registro primario. El 37.4 / 4.3 de la interpolación log-lineal queda en notas. |
| M2 | WSP, filas de mármol 2011 | escalamiento | «método no declarado» | **Truncado (scalping) a 178 mm** | G p2 | Golder 2012: «scalped at 178 mm». |
| M3 | WSP, filas de mármol 2011 | e0_origen / UCS_MPa / clase | calculado / vacío / vacío | informe (Tabla 3) / 97.3 / C | G p1, p3, p7 | Para que coincida con el registro primario. |
| M4 | Resumen WSP: origen del mármol 2011 | origen | «Acopio Punto G» | **Fase 5, polígono 12022607, cota 4478** | G p1 | El Acopio G corresponde solo al lote 2020–21. |
| M5 | Resumen WSP: origen del mármol 2021 | origen | «Acopio Punto G» | **Tajo Mina Fase 8 Sur (Pala 10), polígono 8-NP-4133-25-04, Acopio punto G; 23–24/11/2020** | W p52–56 | Faltaba el polígono y la fase. |
| M6 | Resumen WSP: muestras UCS/LA de hornfels | origen | Acopio G | «**Acopio punto F** / M-01, M-02», Tajo Mina Fase 8, 31/10/2020 | W p48–51 | El texto (p4) dice Acopio G; las hojas dicen Acopio F. |
| M7 | Resumen WSP: Los Ángeles del mármol 2021 | LA | 45–50 % | **55.8 % y 45.2 %** (ASTM C535, gradación 2) | W p53, p55 | El texto del memo (p38) dice «entre 45 % y 50 %», y la hoja lo contradice. 55.8 % sigue cumpliendo el límite de < 60 %. |
| M8 | Hornfels Golder Ø6" | hay_pico / q | 4100 kPa a 11.44 % | Se mantiene, con alerta | W p350–351 | La curva llega a ≈4600 kPa a ≈17.5 %: la hoja es inconsistente con su propio gráfico. |
| M9 | WSP, USC MN-LCTX1 y MN-LCTX2 | e0 | 0.205 | Se mantiene, con alerta | W p385, p391 | La hoja da e tras consolidación 0.21 y 0.25, mayores que e0. Además, LCTX1 y LCTX2 (y también HR-CTX1 y HR-CTX4) tienen masas idénticas, así que no son mediciones independientes. |

## 4. Contradicciones de UCS: qué dice cada página y por qué difieren

No es un problema de unidades: todo está en MPa, y un error kg/cm²–MPa daría un factor de 10. Son ensayos distintos, hechos por laboratorios distintos, sobre probetas distintas.

**Hornfels**

| Fuente | Página | Probetas | Norma / diámetro | Resultados (MPa) | Muestra |
|---|---|---|---|---|---|
| Golder 2021a (CQA Antamina), en W Tabla 1 | W p7; hojas p49, p51 | 2 muestras × 2 núcleos | ASTM D7012 Método C; Ø 74–74.6 mm; L/D 1.9 | M-001/M-01: 66.0 y 64.5 (prom. 65.3); M-001/M-02: 65.1 y 62.5 (prom. 63.8). La Tabla 1 los redondea a 65 y 64 | «Tajo Mina Fase 8», Acopio punto F, 31/10/2020 |
| IDIEM 1.555.677-D | W p72, p74, p76 | 3 núcleos | ASTM D7012-14e1; Ø 54 mm; 0.5 MPa/s | 26.3, 40.8 y 24.5 (corregidos a D50); 25.9, 40.2 y 24.1 (D54). ρd 2.66, 2.71 y 2.69. Falla «Mixta (Tipo B2)»; vetillas de calcita; sin alteración | Lote «H6 HORNFEL GRIS» enviado a IDIEM, recibido el 12/04/2021: **el mismo material de los triaxiales y del edómetro** |

**Por qué difieren:** son muestras distintas (dos puntos de muestreo y dos campañas), dos laboratorios y dos diámetros. Las tres probetas IDIEM tienen vetillas de calcita y falla mixta (B2), que suele indicar rotura a lo largo de la vetilla. La hoja no dice expresamente que la vetilla controle la falla; eso es una inferencia. El memo cita solo los valores de Golder 2021a, y dos de las tres probetas IDIEM están por debajo del mínimo especificado de 40 MPa.

**Corrección menor:** en la Tabla 1, la carga de M-2 (27,259 kg) es una errata. El promedio de la hoja es 28,258.5 kg, y con ese valor se obtienen los 64 MPa informados.

**Mármol negro**

| Fuente | Página | Probetas | Resultados (MPa) | Muestra |
|---|---|---|---|---|
| Informe 379 (Golder 2011), en G Tabla 1 y W Tabla 2 | G p3; W p8 | 8 núcleos, Ø 45–45.5 mm, L/D 2 | 540–1380 kg/cm² = 53–135 MPa (prom. 97.3). WSP los recalcula desde la carga: 53, 108, 106, 129, 54, 61, 136 y 132. Son los mismos ensayos y solo difieren en el redondeo | Campaña 2011 (Fase 5). El Informe 379 no está incluido |
| Golder 2021a (CQA) | W p54, p56; W Tabla 2 | 2 muestras × 2 núcleos, Ø 68.5–69 mm, ASTM D7012 C | M-001: 45.6 y 42.9 (prom. 44.3); M-002: 42.6 y 40.5 (prom. 41.5). La Tabla 2 da 44 y 42 | Fase 8 Sur, Acopio G, 23/11/2020 |
| IDIEM 1.555.677-D | W p78, p80, p82 | 3 núcleos, Ø 54 mm | 96.6, 66.9 y 103.5 (D50). ρd 2.74–2.75. Falla por matriz (Tipo A) | «REG 41061»: **el mismo lote del edómetro IDIEM 2021** (W p322) |

**Por qué difieren:** las cifras de 2011 y de 2021 corresponden a campañas y frentes de mina distintos. Para el material 2021 hay dos juegos de ensayos sobre muestras distintas:
- Golder 2021a, en el sitio, dio 42–44 MPa.
- IDIEM, sobre el lote que realmente se ensayó, dio 67–104 MPa.

El memo usa solo los 42–44 MPa para explicar la mayor compresibilidad y rotura del mármol 2021 (p33, p42). Hay dos problemas con ese argumento:
- Los datos IDIEM del mismo lote lo contradicen.
- El Bg de 45 % que lo sostiene no se reproduce: con las curvas del mismo ensayo es 37.8 % (ver G2).

Hay además otra errata: el texto de p33 dice «UCS entre 53 y 108 MPa en 2011», pero su propia Tabla 2 llega a 136 MPa.

## 5. Gs y e0 por set

| Set | γd montaje (kN/m³) | Gs del informe y su origen | e0 recalculado | e0 con otro Gs (sensibilidad) |
|---|---|---|---|---|
| Hornfels Ø1.0 m monótono (IDIEM B.2) | 20.60 | **no informado**; se adopta 2.75 («calculated», Golder Burnaby, mismo lote <1"; método no descrito) | **0.310** | 2.71 → 0.290; 2.60 → 0.238 |
| Hornfels Ø1.0 m carga-descarga (IDIEM E) | 20.21 (ρd 2.06, no 2.10) | ídem, 2.75 | **0.335** | 2.71 → 0.316; 2.60 → 0.262 |
| Hornfels Ø6" Golder | 20.58 | 2.75 «calculated» (W p350) | **0.311** | 2.71 → 0.292 |
| Hornfels USC | 21.46 | 2.71 «Estimated» (W p373) | **0.239** | 2.75 → 0.257 |
| Hornfels edómetro Ø1.0 m | 20.60 | 2.60 «estimado» (W p300), **incompatible** con ρd de la roca | 0.238 | 2.75 → 0.310 |
| Hornfels edómetros Ø0.24 m (2.1 y 1.8) | 20.60 / 17.66 | no informado (sin hoja) | no calculable | 2.75 → 0.310 / 0.528 |
| Mármol 2011, triaxiales y edómetro (primario Golder 2012) | 20.60 | 2.70 **supuesto** («not determined», G p3, p7, p13) | **0.286** (el edómetro da 0.284 tras el asiento a 0.18 kg/cm²) | sin densidad de roca para acotarlo |
| Mármol Ø6" Golder | 20.37 | 2.70 «calculated» (W p354) | **0.300** | 2.75 → 0.324 |
| Mármol USC | 22.07 | 2.71 «Estimated» | **0.205** | 2.75 → 0.222 |
| Mármol edómetro Ø1.0 m 2021 | 20.60 | 2.60 «estimado», **incompatible** (núcleos 2.74–2.75) | 0.238 | 2.70 → 0.286; 2.75 → 0.310 |
| Mármol edómetro Ø0.24 m | 18.21 | 2.70 «Assumed» (W p359) | **0.455** | 2.75 → 0.482 |

**Conclusión:** ningún informe mide Gs. En el hornfels, el valor de 2.75 es el único compatible con la densidad seca de los núcleos (≤ 2.71) que aparece asociado al mismo lote. En el mármol 2021, todos los Gs informados (2.60, 2.70 y 2.71) quedan por debajo de la densidad seca de sus núcleos (2.74–2.75), así que los e0 de ese material están subestimados. En el mármol 2011, Gs 2.70 es un supuesto sin verificar.

## 6. Condiciones clave (detalle en `condiciones_*.csv`)

**Origen de las muestras**
- Hornfels: Tajo Fase 8 Norte, Pala 11, polígono 8-NP-4193-46-03, cota 4193 (W p47); las muestras UCS/LA son del Acopio punto F.
- Mármol 2021: Tajo Fase 8 Sur, polígono 8-NP-4133-25-04, Acopio G.
- Mármol 2011: Fase 5, polígono 12022607, cota 4478 («Type C rockfill», angular ROM).
- Los rótulos de las fotos de hornfels y de mármol 2021 dicen «MATERIAL TIPO C».
- IDIEM no registra la fecha ni el lugar de muestreo.

**Granulometría de campo**
- Hornfels: 100 % pasa 36"; 11.8 % retenido en 16"; 2.49 % de finos; Cu 33 y Cc 2.5 (calculados con el material <3").
- Mármol 2020: 4.9 % retenido en 16"; 4.07 % de finos; Cu 113.1 y Cc 7.0; w 4.2 %.
- Mármol 2011: solo gráfico, con Dmax 558.8 mm, Cu 35 y Cc 2.5.
- Ningún informe da densidad de campo.

**Escalamiento**
- Golder 2012: truncado (scalping) a 178 mm.
- WSP: «ajustadas a <178 mm» y «<1"», sin método declarado.
- WSP 0.15 m y 0.24 m: densidad corregida por tamaño según Dorador et al. (2018).

**Relación D/Dmax:** 5.6 (Ø1.0 m), 6.0 (Ø6"), 5.8 y 3.9 (USC), 9.4–9.5 (Ø0.24 m), 5.3 (edómetro 2011).

**Preparación de las probetas**
- Ø1.0 m: material seco, 6 capas de 0.3 m, pisón vibratorio, ρd objetivo 2.1 t/m³ (≈97 % del Proctor estándar estimado por correlación, no medido). Las probetas IDIEM E quedaron en 2.06 t/m³ con w 5 %; las B.2, en 2.10 t/m³ con w 3 %; las de 2011, en 2.10 t/m³ con w 0.09 %.
- USC: «Moist Tamping» con w 5 %. El texto dice que se prepararon en seco.

**Saturación, contrapresión y consolidación**
- Saturación: CO2 seguido de agua desaireada. El criterio es B > 0.95 en IDIEM (sin valor por probeta). En Golder Ø6" B = 0.99 y en USC B = 0.95–0.97.
- Contrapresión:
  - IDIEM 2022: 196 / 98 / 196 kPa (B.2) y 98 kPa (E).
  - IDIEM 2011: 196 kPa.
  - Golder Ø6": 688 kPa (hornfels) y 1104 kPa (mármol).
  - USC: ≈431–451 kPa.
- Consolidación isotrópica, sin duración informada. El γd post-consolidación aparece solo en Golder 2012 (Tabla 3) y en Golder Ø6". Para IDIEM 2022 se recalculó con ΔV.

**Velocidad de carga**
- IDIEM: «--» (controlado por carga). El texto da ≈98 kPa/min.
- Golder Ø6": 1 %/h.
- USC post-cíclico: 5 %/h.

**Deformación final y pico**
- Deformación final: ≈18.7–20.4 % en Ø1.0 m.
- No hay pico marcado. La caída posterior al máximo es ≤ 5.3 %, y en varias probetas el máximo coincide con el último punto (hornfels P2 y P4).

**Criterio de falla:** máximo de t = (σ1−σ3)/2. Todos los ensayos son drenados, así que la sección B de `VERIFICACION.md` (no drenados) no aplica. Con σ′3 constante, el máximo desviador coincide con la máxima oblicuidad.

**Bg:** se usa el de Marsal sobre 18 tamices (7" a #200) y el fondo. Se reprodujeron todos los valores de la Tabla 7 del hornfels Ø1.0 m (20.3, 29.3, 36.5, 24.2, 35.5, 38.9 y 23.0). Los Bg de las probetas de 0.15 y 0.24 m y de los cíclicos no se pueden verificar, porque solo hay gráficos.

**Propiedades índice de la roca**
- Los Ángeles (ASTM C535, gradación 2, 1000 revoluciones):
  - Hornfels: 15.5 y 17.3 % (promedio 16.4; el texto dice 17 %).
  - Mármol 2021: 55.8 y 45.2 %.
  - Mármol 2011: 44 y 41 % (Informe 379, norma no indicada).
- Durabilidad, absorción e Is50: no informadas en ningún informe.
- Densidades índice ASTM D4253/D4254 (material de 1"):
  - Hornfels: 2232 (seco) / 2308 (húmedo) / 1852 kg/m³.
  - Mármol: 2297 / 2398 / 1905 kg/m³.

## 7. Discrepancias menores

1. **Hornfels, Dmax de campo.** El CSV decía «≈914 mm», pero 914 mm es el primer tamiz, por el que pasa el 100 %. El Dmax real está entre 406 y 914 mm (W p47).
2. **Golder 2012, e0 del edómetro.** e0_origen pasa de «informe» a «calculado»: el informe no tabula e0. En la hoja aparece 0.284 a 0.18 kg/cm² (G p13, p72).
3. **Golder 2012, notas del edómetro.** Le asignaban CO2, contrapresión y 6 capas. El edómetro se armó en 3 capas, se inundó y no tuvo contrapresión (G p13).
4. **Ensayos USC de 4".** Gs estaba vacío aunque el e0 se había calculado con 2.71. Se completó con 2.71, tomado de las hojas de 6".
5. **USC, preparación.** El texto (p15) dice «estado seco», pero las hojas dicen «Moist Tamping» con w = 5 %.
6. **Hoja de hornfels Ø6".** Rotula la muestra como «MR» (W p350–351).
7. **Mármol Ø6".** La hoja trae w post de 27.4 % y saturación de 319 %, que son erratas (W p354).
8. **Fechas IDIEM.** La hoja B.2 dice «17-12-2022» y el edómetro de hornfels, «05-11-2022»: son erratas de 2021 (W p233, p298, p300).
9. **Altura del edómetro Ø1.0 m.** Es 0.70 m en las hojas y en p32; p4 y p37 dicen 0.9 m.
10. **Tabla 7.** Da 6800 kPa para el edómetro de mármol 2011, pero la hoja llega a 5884 kPa. Además, rotula el edómetro de hornfels n.° 2 con 2.3 t/m³, cuando se ensayó a 2.1 t/m³.
11. **Mármol Ø0.24 m.** El texto (p33) invierte la numeración de las probetas 3 y 4 y cita 17 % de deformación; la hoja da 15.63 %.
12. **Cc del hornfels inicial.** El recalculado es 1.935, que redondea a 1.94 y no a 1.93. Es despreciable y no se cambió.

## 8. Confirmado como correcto

- **Hornfels IDIEM (6 probetas).** Coinciden con las tablas (W p106–p250) σ′3 (981, 1961 y 2452 kPa), q (3897, 9059, 11931, 3821, 9703 y 12929 kPa), σ′1, εa y εv en la falla. También coinciden γd (2.10 y 2.06), w (3 y 5 %), Bg (20, 29, 37, 24, 36 y 39, recalculados) y los finos post-ensayo (5.6, 8.0, 10.4, 6.8, 9.8 y 13.5).
- **Granulometría inicial del hornfels Ø1.0 m.** D10 2.61, D30 13.3, D50 28.0 y D60 35.0 mm; Cu 13.4; grava, arena y finos 87.3 / 10.1 / 2.6 %.
- **Mármol 2011 (Golder CSV).** Coinciden σ′3, σ′1, q, εa, εv, φsec (40.2, 39.4, 36.7, 36.7 y 38.1°), γd 2.10, w 0.09 %, e0 0.286, e después de la consolidación, Dmax 177.8 y 558.8 mm, Cu 34.4 y Cc 4.1 (informe), finos post-ensayo, UCS promedio 97.3 MPa y Los Ángeles 44 y 41 %. También la permeabilidad y los datos del edómetro (ρd 2.100, w 0.088 %, εv 9.03 % a 60 kg/cm²).
- **Golder Ø6" y edómetro MR Test 1.** Coinciden todos los valores de las hojas: D, H, Gs, w, γd, e0, B, q, εa y εv. La curva σv–εv–e del Test 1 coincide en sus 26 filas.
- **USC.** Coinciden D, H, γd (21.46 y 22.07), w 5 %, q máximo (1420.4, 1280, 1210.54, 1245.3, 1575.9 y 1550.5) y Gs 2.71 en las hojas de 6".
- **`WSP_2022_edometro.csv`.** Hay coincidencia fila a fila con las tablas: hornfels Ø1.0 m (69 filas, p300–302), mármol 2021 (69 filas, p324), mármol 2011 (38 filas, p295) y mármol Golder Ø0.24 m (26 filas, p359). Las curvas de hornfels Ø0.24 m son digitalizadas de las Fig. 33c y 33d y no se pueden verificar con precisión de tabla.
- **Granulometría Ø0.15 m.** Los valores leídos de la Fig. 3 (D50 ≈4.6 mm, D10 ≈0.19 mm y 49 % de grava) concuerdan con lo extraído.

## Anexo A. Cambios celda por celda aplicados a los CSV verificados

Además de estos cambios, se agregaron notas marcadas con `[VERIF 2026-10-06]` en la columna `notas`. Ninguna fila se borró.

# Verificación independiente: ensayos Anddes Geolab 2024 y propiedades de roca LE2

Fecha: 2026-10-06. Revisión hecha por un agente distinto del extractor, según `VERIFICACION.md`.

**Fuentes revisadas**

- Los 25 PDF de `Data Antamina\ensayos\` (60 páginas). Todas se renderizaron (`paginas\verificacion\Anddes_LE2\*.png`) y cada número usado se comparó con la imagen.
- `Resultados Parametros  Geotecnicos LE2 (03092025).xlsx`, leído con openpyxl en fórmulas y en valores.
- Las dos pptx de `250903 Waste Charact\`: texto e imágenes incrustadas de WSC láminas 8 y 12.
- Como apoyo para la densidad: `SIMULACIONES_MR2024_V3.csv` (MR24_BD, MR24_RT).

Scripts en `paginas\verificacion\Anddes_LE2\`: `render.py`, `parse_tx_verif.py`, `criterios_tx.py`, `comparar_*.py`, `proctor_gs_linea.py`, `le2_stats.py`, `bd_por_rt.py`, `construir_verificado.py`, `construir_condiciones_y_roca.py`.

## 1. Resultado global

- **Valores numéricos extraídos: sin errores.** Se compararon contra la imagen o contra un parser independiente:
  - las 15 probetas TX (28 filas tabuladas cada una; celda, contrapresión, B, H, D, w y ρd antes y después de consolidar; Su, envolventes c′, φ′, a′, α′ y totales);
  - los 15 puntos LSDS;
  - las 5 fichas índice (granulometría completa, LL, SUCS, Proctor, corrección por sobretamaño, Gs rotulado y CA);
  - los 192 estadísticos de UCS, Is50 y BT de `parametros_RMU.csv`.

  En la tabla TX, los controles internos p = σ3c + q/2, p′ = p − u y σ′1/σ′3 dan 0 fallos en 420 filas.
- **Discrepancias: 12.** Ninguna es un número mal transcrito. Son errores de semántica (columnas que mezclan estados), banderas indebidas (saturado = «sí»), clasificaciones no verificables y explicaciones que faltaban. Las importantes son D1, D4, D6 y D8.

## 2. Discrepancias

| N° | Archivo / columna | Valor anterior | Valor correcto | Página / hoja | Razón |
|---|---|---|---|---|---|
| D1 | `ensayos_triaxial_CU.csv`: `sigma3_kPa` y `sigma1_kPa` (15 filas) | p. ej. M-500: sigma3 = 500, sigma1 = 454,9, q = 375,7 | `sigma3c_kPa` = 500 (consolidación). Al 15 %: `sigma3f_e15_kPa` = 79,2, `sigma1f_e15_kPa` = 454,9 y q = 375,7. Se añaden los tres estados (qmax, oblmax, e15) | TX p.3-5 | La columna sigma3 es σ′3c y la columna sigma1 es σ′1 en la falla, por lo que q ≠ σ1 − σ3 (454,9 − 500 = −45). Viola ESQUEMA y VERIFICACION B. Se conservan los valores y se agregan columnas explícitas |
| D2 | `ensayos_triaxial_CU.csv`: `Dmax_mm` (15) | vacío | «no informado» | TX p.1-7 | Regla de VERIFICACION: el dato no existe |
| D3 | `ensayos_triaxial_CU.csv`: `tipo_material` (15) | vacío | «no indicada» | todas | Ídem. La inferencia «probablemente ROM» queda solo en notas |
| D4 | `ensayos_corte_directo.csv`: `saturado` (15) | «sí» | «no confirmado» y nueva columna `Sr_final_calc` | LSDS p.2 | El informe dice «saturados durante el ensayo, **salvo excepciones**». Con la w y la ρd finales informadas y el Gs rotulado, Sr final da 0,73-0,81 en P1 y P2 y 0,88-0,96 en I. En P1 a 1000 kPa, w final = w inicial = 7,40 % |
| D5 | `ensayos_corte_directo.csv`: `escalamiento` (15) | «no indicado; TM de ensayo 1 in» | se añade que la MDS de referencia es de la fracción < 19 mm | Proctor p.1 | La probeta TM 1 in se compacta al 90 % de una MDS obtenida sobre material < 3/4 in (ver D7) |
| D6 | `ensayos_indices.csv` y `ensayos_resumen.md`: SUCS de P1 | GP-GM, sin reserva | GP-GM informado pero **no verificable**; podría ser GW-GM | SUCS P1 p.1-2 | Cc = 0,11 sale del D10 erróneo (1,54 mm). Con D30 = 1,50 y D60 = 12,6 mm, si 0,059 ≤ D10 < 0,075 mm resulta Cc = 2,4-3,0 (GW-GM). En M (D10 = 0,075 mm, Cc ≈ 4,6) y H (Cc > 8) la clase GP sí se sostiene |
| D7 | `ensayos_resumen.md` §6.11 | «Fuera de método sin explicación (probablemente por sobretamaño)» | Retenido en 3/4 in: M 44 %, H 41 % e I 35 %, por encima del 30 % que admite el Método C; P1 30 % y P2 27 %, que sí son «Método C». La corrección por sobretamaño del propio informe implica Pc = 43,7 / 40,4 / 35,1 / 29,9 / 27,3 %, igual al retenido en 3/4 in | SUCS p.1; Proctor p.1 | Con esto se confirma que el Proctor (y la MDS del 90 %) es de la fracción **< 19 mm** |
| D8 | `set_id` de I y `ensayos_resumen.md` §1 y §6.5 | «I-1 al I-12 (I-1 al I-11 en SUCS, Proctor, CA y LSDS)» | **I-1 al I-11 (11 submuestras)**. El N° de informe TX lista 11 ítems (28, 27, 26, 43, 34, 35, 41, 39, 40, 38, 36), mientras que M lista 13 y H lista 12 | TX p.1; SUCS, PR, CA, LSDS p.1 | El «I-12» del encabezado TX y de los nombres de archivo es un error probable. `set_id` se dejó igual para no romper uniones y se añadió `submuestras_verificadas` en `condiciones_Anddes2024.csv` |
| D9 | `ensayos_resumen.md` §6.3 | «Gs: no se indica a qué fracción corresponde» | Es el Gs de la curva de saturación del Proctor, sobre la fracción < 19 mm (D7). La línea dibujada responde a Gs = 3,05 / 2,93 / 2,74 / 2,89 / 2,73 (a 0,01 del rótulo) | Proctor p.1 (geometría vectorial) | Se comprobó que el rótulo y la curva dibujada son coherentes |
| D10 | Notas del TX (5 probetas con «comportamiento dilatante») y `ensayos_resumen.md` §3 (excepciones: «M 2000 y H 500») | M-2000, H-500, P1-2000, P2-1000 y P2-2000 marcadas como dilatantes; el resumen solo cita M-2000 y H-500 | En 5 probetas el máximo q global está al 14-15 %, pero cuatro tienen antes un **pico local**: M-2000 1996,2 a 2 %; H-500 538,5 a 1,75 %; P1-2000 3057,5 a 3 %; P2-1000 1355,3 a 3 %; P2-2000 2565,3 a 3 % | TX p.3-5 | Es ablandamiento seguido de endurecimiento, no dilatancia monótona. Se añade la columna `pico_local_previo` |
| D11 | `ensayos_resumen.md` §3, «Dmax de la probeta TX» | «correspondería ≤ 25 mm (D/6)» | «no informado» | TX | Era una especulación. Lo único documentado es que la MDS de referencia es de la fracción < 19 mm |
| D12 | `caracterizacion_resumen.md` §4 («no hay densidad por litología») y `csv_grandes_resumen.md` («no hay leyenda de RT») | sin densidad por litología | Densidad del modelo de bloques por litología: Mármol 2,70; Mármol diopsídico 2,85; Horfels 2,70; Horfel diopsida 2,87; Intrusivo 2,45; Caliza 2,71 t/m³ (P50) | `SIMULACIONES_MR2024_V3.csv`; WSC lámina 12 | Las litologías se asignaron a los códigos RT (16, 19, 13, 14, 1, 10…) porque el n, la media y la desviación de MR24_UCS coinciden exactamente con la tabla de WSC lámina 12. Son valores del modelo, no ensayos |

## 3. Confirmaciones (verificado en la imagen)

- **TX** (p.1, 3-5 y 7):
  - Probetas de Ø 15,20 cm × 31,00 cm, contrapresión de 187 kPa, celda de 687/1187/2187 kPa, B = 0,95-0,98 y velocidad de 0,025 cm/min.
  - Los 28 puntos por probeta coinciden.
  - Envolventes efectivas al 15 %: M 40,0 kPa / 44,0° (a′ 28,9; α′ 34,7); H 72,0 / 40,5 (55 / 33,0); I 82,0 / 44,0 (59,3 / 34,7); P1 61,0 / 42,0 (45,3 / 33,9); P2 57,0 / 42,0 (42,7 / 33,8). Son coherentes entre sí (sen φ′ = tan α′).
  - Su/σ′3: 0,49; 0,44; 0,72 y 0,45; 0,73; 0,69.
  - Totales en p.7: M 29 / 19° y H 72 / 16,5° (al 2 %); I 163 / 16° (al 2 %); P1 0 / 25° y P2 0 / 24° (al 15 %).
  - El «2,70» de la p.4 es texto blanco de 5,9 pt, invisible en la imagen; no se usa.
- **LSDS**: todos los τ pico, τ a 6,6 cm, ángulos secantes, c, φ, μ, alturas, w y ρd. Caja de 30,5 × 30,5 × 17,8 cm, TM 1 in, 0,5 mm/min, consolidación de 16 h. El N° de informe de P2 termina en «_SUCS» (errata del informe).
- **Índices**:
  - Las cinco curvas granulométricas (14 tamices), los porcentajes grava/arena/finos y los D, Cu y Cc informados.
  - LL: M NP, H 16, I 17, P1 NP, P2 NP.
  - Clases SUCS informadas, Proctor (puntos, MDS, w óptimo, corregidos y Gs bulk del sobretamaño) y CA (w = 2,94 / 3,28 / 5,11 / 2,81 / 5,52 %, recalculados desde las masas).
  - Los D interpolados del CSV (D10 0,075 / 0,126 / 0,084; D30, D50 y D60) son correctos.
- **parametros_RMU.csv**: los 192 estadísticos de UCS, Is50 axial, Is50 diametral y BT recalculados coinciden. Se confirma el error de XDP P35.

## 4. Puntos abiertos (a)-(g)

**(a) Gs.**

- El rótulo de la curva de saturación del Proctor dice Gs = 3,06 (M), 2,94 (H), 2,75 (I), 2,90 (P1) y 2,74 (P2). Se verificó en la imagen ampliada y en la geometría de la línea, que da 3,05 / 2,93 / 2,74 / 2,89 / 2,73.
- No hay ensayo ASTM D854. El valor corresponde a la fracción < 19 mm.
- Los datos del propio laboratorio exigen esos valores. Para que el punto Proctor más húmedo tenga Sr ≤ 1 hace falta Gs ≥ 3,03 (M), 2,88 (H), 2,69 (I), 2,87 (P1) y 2,68 (P2). Con Gs = 2,70, M, H y P1 tendrían Sr > 1.
- El estado final del TX (w final y ρd consolidada, suponiendo Sr = 1) da un Gs implícito de 3,06-3,10 (M), 2,87-2,96 (H), 2,67-2,87 (I), 2,83-2,88 (P1) y 2,64-2,67 (P2).
- **El 3,06 de M es internamente coherente, pero alto para mármol**:
  - calcita = 2,71;
  - densidad de bloque LE2 del Mármol: P50 2,70 (P84 2,73); Mármol diopsídico: 2,85;
  - el propio sobretamaño de M tiene Gs bulk 2,94.

  La muestra compuesta M probablemente contiene minerales densos (skarn o sulfuros). No hay petrografía que lo confirme. Recomendación: ensayar Gs (D854/C127) antes de usar e0.

**(b) D10.**

- D10 = 1,54 mm aparece idéntico en M, H y P1. Es un artefacto del formato: los Cu y Cc informados se calcularon con él (22,04/1,54 = 14,3).
- Valores reales:
  - M: D10 = 0,075 mm (pasa 10 % exacto por N° 200);
  - H y P1: D10 < 0,075 mm, que no se puede medir por tamizado (una extrapolación log-lineal da ≈ 0,063, pero no es dato);
  - I: 0,126 mm y P2: 0,084 mm, que coinciden con lo informado.
- En P1 además D30 informado (1,47) < D10, y la clase SUCS no es verificable (D6).

**(c) Humedad de moldeo y submuestras.**

- **H**: el TX moldea a 6,0 % (rotulado «óptimo»). El Proctor da 7,7 % y el LSDS usa 7,70 %.
- **I**: el TX moldea a 8,0 %. El Proctor da 9,8 % y el LSDS usa 9,80 %.
- La MDS es la misma en los tres documentos. Los documentos no permiten resolver la diferencia.
- Dato nuevo: **el TX de H se ensayó el 2024-01-25/29, antes que el Proctor de H (2024-04-12/15) y que la granulometría (2024-04-10/15)**. En I el TX (2024-04-24/29) es posterior al Proctor (2024-04-10/12).
- Las probetas TX de H e I quedaron 1,7-1,8 puntos del lado seco del óptimo del Proctor documentado.
- Submuestras de I: son I-1 a I-11 (D8).

**(d) Esfuerzos TX.** Los valores están en kPa. En cada criterio se da ε (%) / σ′3f / σ′1f / u / q, salvo al 15 %, donde ε = 15. Están completos, con p′ y t′ del MIT y la razón σ′1/σ′3, en `ensayos_triaxial_CU_verificado.csv`.

| Set | σ′3c | Máx. desviador: ε / σ′3f / σ′1f / u / q | Máx. oblicuidad: ε / σ′3f / σ′1f / u / q | 15 % (informe): σ′3f / σ′1f / u / q |
|---|---|---|---|---|
| M | 500 | 1,75 / 252,8 / 769,6 / 247,2 / 516,8 | 15,0 / 79,2 / 454,9 / 420,8 / 375,7 | 79,2 / 454,9 / 420,8 / 375,7 |
| M | 1000 | 2,0 / 517,4 / 1665,6 / 482,6 / 1148,2 | 15,0 / 106,9 / 1000,6 / 893,1 / 893,7 | 106,9 / 1000,6 / 893,1 / 893,7 |
| M | 2000 | 15,0 / 418,8 / 2437,1 / 1581,2 / 2018,3 (pico local 1996,2 a 2 %) | 15,0 / 418,8 / 2437,1 / 1581,2 / 2018,3 | 418,8 / 2437,1 / 1581,2 / 2018,3 |
| H | 500 | 15,0 / 71,9 / 627,3 / 428,1 / 555,4 (pico local 538,5 a 1,75 %) | 15,0 / 71,9 / 627,3 / 428,1 / 555,4 | 71,9 / 627,3 / 428,1 / 555,4 |
| H | 1000 | 2,0 / 439,9 / 1530,5 / 560,1 / 1090,6 | 15,0 / 94,9 / 1077,0 / 905,1 / 982,1 | 94,9 / 1077,0 / 905,1 / 982,1 |
| H | 2000 | 2,0 / 713,1 / 2469,7 / 1286,9 / 1756,6 | 6,0 / 311,0 / 1895,6 / 1689,0 / 1584,6 | 336,6 / 2011,0 / 1663,4 / 1674,4 |
| I | 500 | 1,75 / 282,9 / 1145,6 / 217,1 / 862,7 | 15,0 / 122,8 / 841,6 / 377,2 / 718,8 | 122,8 / 841,6 / 377,2 / 718,8 |
| I | 1000 | 1,75 / 445,8 / 1678,4 / 554,2 / 1232,6 | 15,0 / 132,0 / 1115,8 / 868,0 / 983,8 | 132,0 / 1115,8 / 868,0 / 983,8 |
| I | 2000 | 2,5 / 805,8 / 2811,3 / 1194,2 / 2005,5 | 15,0 / 285,8 / 1965,8 / 1714,2 / 1680,0 | 285,8 / 1965,8 / 1714,2 / 1680,0 |
| P1 | 500 | 2,0 / 242,1 / 908,6 / 257,9 / 666,5 | 15,0 / 98,2 / 682,3 / 401,8 / 584,1 | 98,2 / 682,3 / 401,8 / 584,1 |
| P1 | 1000 | 2,5 / 548,5 / 1914,0 / 451,5 / 1365,5 | 15,0 / 198,4 / 1412,3 / 801,6 / 1213,9 | 198,4 / 1412,3 / 801,6 / 1213,9 |
| P1 | 2000 | 14,0 / 685,7 / 3753,5 / 1314,3 / 3067,8 (pico local 3057,5 a 3 %) | 14,0 / 685,7 / 3753,5 / 1314,3 / 3067,8 | 686,2 / 3751,0 / 1313,8 / 3064,8 |
| P2 | 500 | 2,5 / 253,1 / 911,4 / 246,9 / 658,3 | 15,0 / 114,1 / 713,1 / 385,9 / 599,0 | 114,1 / 713,1 / 385,9 / 599,0 |
| P2 | 1000 | 15,0 / 228,9 / 1597,5 / 771,1 / 1368,6 (pico local 1355,3 a 3 %) | 15,0 / 228,9 / 1597,5 / 771,1 / 1368,6 | 228,9 / 1597,5 / 771,1 / 1368,6 |
| P2 | 2000 | 15,0 / 634,3 / 3417,0 / 1365,7 / 2782,7 (pico local 2565,3 a 3 %) | 15,0 / 634,3 / 3417,0 / 1365,7 / 2782,7 | 634,3 / 3417,0 / 1365,7 / 2782,7 |

**(e) Probeta TX y preparación.**

- Ø 152 × 310 mm.
- **Dmax de la probeta: no informado.** Tampoco se informan el método de compactación (pisón o vibración), el número de capas, la fracción usada ni la granulometría de la probeta. El TX no declara escalamiento.
- Lo que sí consta:
  - «Reconstituido al 90 % de la MDS … y óptimo contenido de agua» (MDS de la fracción < 19 mm), con ρd de 2,182 / 2,100 / 1,921 / 2,094 / 1,831 g/cm³;
  - w de moldeo de 6,8 / 6,0 / 8,0 / 7,4 / 11,1 %;
  - en el formato, «Grado de compactación: Medio».
- La consolidación isotrópica reduce el volumen entre 6 y 14 % (recalculado con H y D inicial y final; cuadra con la ρd informada ± 0,002).
- El LSDS usa TM 1 in (lado/TM = 12).

**(f) Origen.**

- **M y H**: perforación del proyecto «Perforaciones Geotécnicas e Hidrogeológicas 2023», zona «Patio de servicios / Botadero Este», 40-90 m.
- **I**: «Botadero Este», 20-60 m, código «03 (Ruma 03) / Fase 10 A».
- **P1 y P2**: «Pilas Experimentales Medio Ambiente», sin profundidad, con «Material B» y «Material A» en el N° de muestra.
- Las muestras fueron recibidas el 2023-11-23 (M, H, I) y el 2024-09-03 (P1, P2). La fecha de muestreo no se informa.
- **ROM, Chancado o Enrocado: el texto no lo indica en ningún caso.** Solo se puede inferir, sin confirmación, que M, H e I son desmonte ya depositado en el Botadero Este (ROM por definición).
- La granulometría recibida (100 % < 75 mm) está limitada por el muestreo: no es la de terreno.
- «Material A» y «Material B» parecen la clase de material de Antamina (A/B/C), que no equivale a ROM, Chancado ni Enrocado.

**(g) parametros_RMU.**

- **Siglas.** Solo dos están definidas en texto, en WSC lámina 12: «LMH Calizas Desmonte (limestone Hornfels)» y «XDP Exoskarn mayor desmonte». END, EXO, HRN e INT no se definen en ningún archivo; endoskarn, exoskarn, hornfels e intrusivo son lecturas de la sigla, apoyadas en la lista de litologías de la misma lámina. No hay RMU de mármol.
- **Error del P35 de XDP, confirmado.** La fórmula `UCS!J2394 = PERCENTILE.INC(F2394:F2471, 0.35)` toma la columna Año y devuelve 2021. El valor correcto es **70,84 MPa**. El error se repite en PGR lámina 4 y en la tabla de WSC lámina 12, verificada en la imagen incrustada.
- **Otros hallazgos menores:**
  - la media PLTA de HRN usa C950:C1478 (5,437 frente a 5,435);
  - hay 6 UCS con RMU «N/A» fuera de toda fórmula.
- **Medianas de UCS recalculadas desde la hoja cruda** (n entre paréntesis): END 28,10 (312), EXO 66,68 (309), HRN 75,20 (275), INT 50,60 (379), LMH 56,27 (1111) y XDP 97,99 (78) MPa. Coinciden con el Resumen.
- **P35 de UCS**: 21,97 / 49,57 / 58,16 / 39,53 / 44,32 / 70,84 MPa, en el mismo orden.
- Is50, BT y los demás estadísticos están en `indices_roca_LE2.csv`.

## 5. Condiciones clave para el uso de los datos

1. Son probetas **reconstituidas, densas (90 % de la MDS del Proctor estándar sobre la fracción < 19 mm)**, de muestras recibidas que pasan 100 % por 75 mm. No representan la granulometría ni la densidad de colocación de terreno, que no se informan.
2. TX CU: confinamiento máximo σ′3c = 2 MPa, con σ′1f de hasta unos 3,75 MPa. La consolidación reduce el volumen entre 6 y 14 %, y la e0 recalculada (con el Gs rotulado) es 0,385-0,496. El criterio del informe (15 %) suele coincidir con la máxima oblicuidad, no con el máximo desviador, que se da a 1,75-2,5 %. Para comparar con bases drenadas, usar los estados de la tabla (d).
3. LSDS: la saturación no está demostrada, sobre todo en las pilas. Las envolventes de P1 y P2 son curvas (φ secante de 50° a 300 kPa).
4. Gs no ensayado; la e0 depende de él. El valor de M (3,06) es atípico para mármol.
5. Hay propiedades índice de roca solo por RMU (testigos LE2) y no por muestra Anddes. No hay Los Ángeles, durabilidad, absorción ni rotura (Bg) en ninguna fuente.

# WSP (2024) – Ensayos geotécnicos a gran escala para mezclas de co-disposición de desmonte y relave, Fase 1

- **Fuente:** `2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf` (366 pp.). Informe final IFF de WSP Perú, octubre de 2024, proyecto 2094151472, código 101-20110-LTE01220-IFF-420-G-0003 Rev.0 (Eco Estable Co-Disposal, Pre-Pilot Plant).
- **Laboratorios:** IDIEM (Universidad de Chile) ejecutó los triaxiales, edómetros, permeabilidad, densidades máxima y mínima, Proctor y granulometrías (Anexo B: informes IDIEM 1.914.482-A, B, C, D, E y F; la carga puntual figura como 1.914.482-G dentro del F). WSP Lima hizo Gs, UCS y Los Ángeles (Anexo A).
- **CSV:** `WSP_2024_codisposicion.csv`, 18 filas (una por probeta triaxial), todas verificadas en la imagen de la página.
- **Scripts y páginas renderizadas:** `paginas/WSP2024/` (`parse_tx.py`, `gran_digit.py`, `gran_calc.py`, `pl_stats.py`, `build_csv.py`).

## 1. Objetivo y materiales

El objetivo fue evaluar resistencia, esfuerzo-deformación, compresibilidad y conductividad hidráulica de cuatro mezclas de desmonte tipo intrusivo y relave (p. 7-8). Las proporciones son en masa:

| Mezcla | Intrusivo : relave | % desmonte / % relave (nominal) | ρd de montaje (g/cm³) | Gs global (Tabla 5, p.12) |
|---|---|---|---|---|
| Codisposal 1 | 3.5 : 1 | 78 / 22 | 2.07 | 2.93 |
| Codisposal 2 | 4.5 : 1 | 82 / 18 | 2.03 | 2.90 |
| Codisposal 3 | 5.5 : 1 | 85 / 15 | 2.05 | 2.89 |
| Codisposal 4 | solo intrusivo | 100 / 0 | 2.00 | 2.85 |

- **Clase de desmonte (ROM, Chancado o Enrocado):** el informe no la indica. La muestra llegó en 5 maxisacos de «Desmonte de Mina (Intrusivo)», 46 191 kg, con Dmax de terreno de 10″ (p.89, 93). Por eso `tipo_material` dice «desmonte (clase no indicada)» y `clase_desmonte` queda vacía.
- **Origen:** las fichas de WSP Lima indican «Tajo Mina» / «Material Intrusivo / Tajo» y los sondajes de referencia CD-EGS-001, CD-ECU-001 y CD-ERD-001 (pp. 45-82), con muestreo de Antamina en febrero y marzo de 2024. No se indican banco ni fase. No está demostrado que las muestras de WSP Lima y las de IDIEM sean el mismo lote.
- **Relave:** 10 630 kg. Granulometría IDIEM-F (p.355): 100 % pasa 3/8″, 99.9 % pasa N°4, 57.5 % pasa N°60 y 12.4 % pasa N°200 (SM, sin hidrómetro). Gs = 3.42–3.50 (promedio 3.46, WSP Lima, Tabla 4 p.11); IDIEM obtuvo 3.48 (p.97). Proctor modificado: ρd máx 2.20 g/cm³ con w óptima de 12.1 % (p.97).

## 2. Litología (detalle por litología)

| Litología | Origen / identificación | Mineralización y alteración | Propiedades de la roca |
|---|---|---|---|
| **Intrusivo – tonalita** (nombre del informe: «Desmonte de Mina (Intrusivo)», «100% Intrusivo») | Tajo Mina; 31 de los 38 fragmentos de carga puntual (82 % por conteo) | Vetillas de pirita, sulfuros de cobre, cuarzo, calcita y epidota. Alteración por sericitización y cloritización, y localmente epidotización, oxidación, arcillas y zeolitización | Is50 de fragmentos válidos: media 5.0 MPa, mediana 4.95 MPa, rango 1.1–8.8 MPa (n = 26 válidos de 31) |
| **Caliza** (incluida dentro del «100% Intrusivo») | 7 de los 38 fragmentos (18 % por conteo) | Vetillas de calcita y, en un fragmento, de calcita con sulfuros de cobre. Sin alteración | Is50: media 5.3 MPa, rango 4.3–6.6 MPa (n = 7, todos válidos) |
| Intrusivo, sin subtipo (WSP Lima) | «Material Intrusivo / Tajo Mina» | — | UCS de 64.0 a 143.1 MPa, promedio 95.2 MPa (7 probetas, ASTM D7012, w = 0.17–0.34 %; R4–R5 según ISRM, Tabla 6 p.12). Los Ángeles (ASTM C535 gradación 1 según las fichas; el texto dice C131): 21.2–39.9 %, promedio 30.4 % (Tabla 7 p.13). Gs aparente 2.83–2.93, promedio 2.87; Gs base seca 2.71–2.86; absorción 0.8–1.6 %, promedio 1.08 % (Tabla 3 p.11) |

- **Is50 por set según IDIEM-F (Tabla 6 p.364):** 5.48, 4.36, 4.11 y 6.16 MPa (clase «muy alta»), con w de 0.09–0.43 %.
- **Promedios recalculados:** con solo los fragmentos válidos salen 5.49, 4.90, 3.27 y 6.12 MPa. Los promedios de IDIEM incluyen fragmentos marcados «no válida».
- **Normalización en el CSV:** `litologia` = Intrusivo, con subtipo tonalita en `litologia_detalle`. La fracción de caliza (~18 % por número de fragmentos, no por masa) va en `litologia_proporcion`. El informe nunca trata el material como mezcla de litologías.

## 3. Programa y resultados triaxiales (CID, 0.6 m × 1.2 m)

- **Sets:** 6 sets y 18 probetas. Son 4 sets monótonos (C1, C2, C3 y C4) y 2 sets de carga-descarga drenados sin extensión (C1 y C2). En cada set, σ′3 = 5, 10 y 20 kgf/cm², es decir 490, 980 y 1960 kPa según el informe (Tabla 9 p.15).
- **Montaje y saturación:** probetas con w = 3 %, saturadas con B ≥ 0.95 y contrapresión de 1 kgf/cm².
- **Corte:** a carga controlada hasta εa ≈ 20 %, controlando que no hubiera exceso de presión de poros.
- **Ciclos de carga-descarga:** a εa = 2, 5 y 8 % (Tabla 10 p.18).
- **Origen de los valores de pico:** las hojas IDIEM tabulan εa, εv, p = (σ1+σ3)/2 y q = (σ1−σ3)/2 en kgf/cm². El pico es el máximo de q. Desviador = 2q × 98.0665 kPa.
- **Verificación del texto extraído:** p − q = σ′3 se cumple en todas las filas.

| Set | σ′3 (kPa) | σ1−σ3 (kPa) | φ′sec (°) | εa pico (%) | εv pico (%) | Bg (%) |
|---|---|---|---|---|---|---|
| C1 mon | 490 / 981 / 1961 | 1895 / 4166 / 7628 | 41.2 / 42.8 / 41.3 | 15.6 / 18.8 / 13.4 | −4.4 / −6.6 / −6.7 | 9.6 / 18.3 / 16.9 |
| C1 C/D | 490 / 981 / 1961 | 1732 / 3815 / 7755 | 39.7 / 41.3 / 41.6 | 11.1 / 13.6 / 11.7 | −3.7 / −4.7 / −5.1 | 6.0 / 11.8 / 16.9 |
| C2 mon | 490 / 981 / 1961 | 1905 / 3564 / 6596 | 41.3 / 40.2 / 38.8 | 14.7 / 15.7 / 13.9 | −3.1 / −3.8 / −4.2 | 7.8 / 8.6 / 13.5 |
| C2 C/D | 490 / 981 / 1961 | 2267 / 3703 / 6973 | 44.3 / 40.8 / 39.8 | 7.9 / 12.7 / 13.5 | −3.6 / −4.5 / −5.1 | 13.0 / 15.8 / 15.2 |
| C3 mon | 490 / 981 / 1961 | 1930 / 3813 / 6900 | 41.5 / 41.3 / 39.6 | 15.1 / 13.2 / 19.6 | −3.5 / −4.8 / −5.1 | 6.3 / 15.2 / 19.4 |
| C4 mon | 490 / 981 / 1961 | 1638 / 3389 / 7024 | 38.7 / 39.3 / 39.9 | 12.4 / 20.7 / 19.4 | −4.3 / −4.8 / −5.1 | 8.3 / 8.5 / 17.6 |

- **Convención de εv:** IDIEM usa negativo = contracción. Todas las probetas monótonas son contractivas. En carga-descarga a 490 kPa hay una ligera dilatancia tras la 2.ª etapa de ciclos (C1) o la 3.ª (C2) (p.20).
- **Envolventes:** el informe **no ajusta envolventes** (ni c-φ, ni Leps, ni ley de potencia). Solo presenta φ′pico por probeta frente a σ′c (Fig. 13 p.27) y frente a σ′n en el plano de falla, comparado con las curvas de Leps (1970) (Fig. 14 p.28):
  - C2, C3 y C4 caen cerca de la curva de enrocado promedio.
  - C1 tiende a la curva de mayor resistencia.
- **φ′ calculado:** asin(q/p) con los datos IDIEM reproduce la Fig. 13 con una diferencia de ±0.1°.
- **Tendencias que describe el informe:** φ′ crece con σ′c en C1 y C4 y decrece en C2 y C3. C1 muestra la mayor resistencia a 980 y 1960 kPa.
- **No drenados:** el informe no tiene ensayos no drenados.

### Densidad, e0 y Dr

- **e0 del CSV:** calculado como Gs global / ρd − 1, con valores 0.415, 0.429, 0.410 y 0.425.
- **e0 de los edómetros (Tabla 12):** 0.418, 0.431, 0.408 y 0.425, para la misma ρd de montaje.
- **ρd post-consolidación:** se anotó en `notas` (IDIEM, pp.130, 217, 219, 255, 339 y 341).
- **Densidades mínima y máxima (Tabla 8, p.13; material < 3″):**

| Mezcla | ρd mín (g/cm³) | ρd máx (g/cm³) |
|---|---|---|
| C1 | 1.945 | 2.169 |
| C2 | 1.914 | 2.158 |
| C3 | 1.865 | 2.187 |
| C4 | 1.825 | 2.212 |

- **Dr:** el informe no la indica. Calculada a partir de estos valores, quedaría en ≈58 % (C1), 51 % (C2), 61 % (C3) y 50 % (C4). No la puse en el CSV porque el ensayo de densidades se hizo sobre material < 3″, no < 4″.

## 4. Granulometrías

- **Desmonte de terreno (IDIEM-A, p.93):** Dmax 10″. Pasante: 96.2 % en 4″, 57.4 % en 3/4″, 25.7 % en N°4 y 6.6 % en N°200. Hay 6.8 % retenido sobre 3″.
- **Probetas:** truncadas (scalping) a 4″, y el material integral se trabaja bajo 3/4″ (p.108).
- **Codisposal 4:** se calculó exacto (pasante / 0.962). D10 = 0.20 mm, D50 = 13.3 mm, D60 = 19.2 mm, Cu = 96, Cc = 8.1, finos 6.9 %.
- **C1–C3:** solo aparecen como gráfico (Gráfico 1 de cada informe IDIEM). Los digitalicé calibrando con los marcadores del desmonte, que tienen valores conocidos; los residuos de calibración son < 1.5 % de pasante.

| Mezcla | D10 (mm) | D30 (mm) | D50 (mm) | D60 (mm) | Cu | Cc | Pasante N°4 (%) | Finos (%) |
|---|---|---|---|---|---|---|---|---|
| C1 | 0.13 | 2.1 | 12.0 | 19.2 | 148 | 1.8 | 34.0 | 7.1 |
| C2 | 0.135 | 2.8 | 12.2 | 19.0 | 141 | 3.1 | 32.8 | 7.1 |
| C3 | 0.14 | 3.4 | 12.4 | 19.0 | 137 | 4.5 | 31.8 | 7.1 |

- **Post-ensayo:** las tablas IDIEM dan % retenido en N°4 y % de finos por probeta (pp.132, 221-222, 257, 344). Bg de Marsal en la Tabla 15 (pp.35-36). Según el informe, la rotura se concentra entre 3″ y 3/8″.

## 5. Edómetros y permeabilidad (0.6 m de diámetro, pared rígida)

- **Edómetros:** cargas de 392, 784, 1568, 3136 y 5880 kPa con descarga, 1 día por escalón (1 a 3 días en C4).

| Mezcla | e0 | ρd (g/cm³) | εv final a 5880 kPa (%) | Bg (%) |
|---|---|---|---|---|
| C1 | 0.418 | 2.07 | 8.2 | 10.5 |
| C2 | 0.431 | 2.03 | 10.4 | 8.3 |
| C3 | 0.408 | 2.05 | 11.1 | 7.7 |
| C4 | 0.425 | 2.00 | 17.4 | 9.2 |

- **Datos de C4 (p.121):** e pasa de 0.425 a 0.363 tras la saturación y llega a 0.187 a 60 kgf/cm². Hay colapso por saturación de 4.3 % bajo 0.1 kgf/cm². Las curvas e–log σ′v están en la Fig. 16 y la Fig. 17 (módulo edométrico M).
- **Conductividad hidráulica (Tabla 14, p.27; m/s, a 392 / 784 / 1568 / 3136 / 5880 kPa):**

| Mezcla | 392 kPa | 784 kPa | 1568 kPa | 3136 kPa | 5880 kPa |
|---|---|---|---|---|---|
| C1 | 1.3e-3 | 1.0e-3 | 8.4e-4 | 7.6e-4 | 6.6e-4 |
| C2 | 4.7e-4 | 3.8e-4 | 3.2e-4 | 2.7e-4 | 2.5e-4 |
| C3 | 7.0e-4 | 6.2e-4 | 5.8e-4 | 4.5e-4 | 4.2e-4 |
| C4 | 2.9e-4 | 2.8e-4 | 2.3e-4 | 2.3e-4 | 2.0e-4 |

- **Fiabilidad de k:** el molde vacío da ≈1e-4 m/s, así que todos los valores están en ese orden o por encima. El propio informe los considera **no representativos** (posible flujo preferencial por las paredes) y su tendencia es inversa a la esperada. IDIEM los reporta en cm/s (factor 100).

## 6. Dudas y observaciones

1. **Contenido real de relave.** La curva «teórica» de ensayo de C1–C3 coincide con el desmonte bajo 4″ en todos los tamaños ≥ 3/4″. Los puntos digitalizados se reproducen bien si el % de relave se aplica **solo a la fracción bajo 3/4″** (C1: 59.7 × (0.447 + 0.553 × 0.22) = 34.0 % pasante N°4, igual al gráfico). Una mezcla de 22 % en masa total daría ≈43 %. Eso equivale a ≈13 %, 11 % y 9 % de relave en masa total para C1, C2 y C3. Dos datos apoyan esta lectura:
   - El Gs global de WSP (Tabla 5) solo se reproduce con pasante N°4 = 34 / 33 / 32 %.
   - Las granulometrías post-ensayo (C1 a 490 kPa: 37 % pasante N°4) son compatibles con 34 % inicial y no con 43 %.

   El informe no lo explica. En el CSV dejé el % nominal (22, 18 y 15 %) y lo advertí en `notas`. Conviene confirmarlo con WSP o Antamina.
2. **Fechas y códigos de IDIEM:**
   - Las hojas de Codisposal 4 tienen fechas de enero de 2023, aunque las muestras se recibieron en noviembre de 2023; probable error de año (debería ser 2024).
   - En la hoja de C2 C/D probeta 1 la fecha de término (08-04-2024) es anterior a la de inicio (06-05-2024).
   - El proyecto aparece como «Estudio conceptual commingling» en todas las hojas.
3. **C2 C/D a 490 kPa:** IDIEM pide usar con precaución los resultados posteriores al 8 % por la deformación acumulada en los ciclos. El máximo q se registró justo al inicio de la etapa de 8 % (εa = 7.93 %), por lo que su φ′ de 44.3° es atípico.
4. **C4 a 980 kPa:** q seguía creciendo al terminar el ensayo (εa = 20.7 %), así que el valor es un límite inferior.
5. **Probetas de carga-descarga:** el máximo q puede coincidir con un punto de inicio de ciclo. El criterio de falla es el máximo desviador de toda la curva, el mismo que reproduce la Fig. 13.
6. **Granulometrías de C1–C3:** salen de digitalizar un gráfico (precisión de ±1 % de pasante), por lo que D10, Cu y Cc son aproximados. Tampoco hay hidrómetro: los finos < 0.074 mm no están caracterizados.
7. **Norma de Los Ángeles:** el texto dice ASTM C131 (sección 4.4) y las fichas y la Tabla 2 dicen C535.
8. **Clase de desmonte y fracción de caliza:** la clase (ROM / Chancado / Enrocado / A-B-C) no se indica. La fracción de caliza dentro del «100% Intrusivo» solo se conoce por el conteo de fragmentos de carga puntual.
